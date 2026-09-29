import threading
import time

from PySide6.QtCore import QPointF, QRectF, Qt, QTimer, Signal
from PySide6.QtGui import QColor, QCursor, QImage, QKeySequence, QPainter, QPainterPath, QPen
from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QWidget

from .. import gamepad, keymap
from ..bridge import KEYDOWN, KEYUP
from .theme import COLORS
from .widgets import button, text_font

MOUSE_TOUCH = 0
SCROLL_TOUCH = 9
SCROLL_STEP = 0.12
SCROLL_LIMIT = 0.6
ECO_INTERVAL = 1 / 20
PAD_INTERVAL = 16
LOOK_SPEED = 14
DIRECTION_NAMES = ["up", "left", "down", "right"]

ANDROID_KEYS = {
    Qt.Key.Key_Return: "Enter", Qt.Key.Key_Enter: "Enter", Qt.Key.Key_Backspace: "Backspace",
    Qt.Key.Key_Tab: "Tab", Qt.Key.Key_Escape: "Escape", Qt.Key.Key_Delete: "Delete",
    Qt.Key.Key_Left: "ArrowLeft", Qt.Key.Key_Right: "ArrowRight", Qt.Key.Key_Up: "ArrowUp",
    Qt.Key.Key_Down: "ArrowDown", Qt.Key.Key_Home: "Home", Qt.Key.Key_End: "End",
    Qt.Key.Key_PageUp: "PageUp", Qt.Key.Key_PageDown: "PageDown", Qt.Key.Key_Shift: "Shift",
    Qt.Key.Key_Control: "Control", Qt.Key.Key_Alt: "Alt", Qt.Key.Key_Space: " ",
}

PAD_KEYS = {
    "Pad A": "Enter", "Pad B": "GoBack", "Pad Start": "GoHome", "Pad Back": "AppSwitch",
    "Pad Up": "ArrowUp", "Pad Down": "ArrowDown", "Pad Left": "ArrowLeft", "Pad Right": "ArrowRight",
}

MOUSE_BUTTONS = {Qt.MouseButton.LeftButton: "Mouse Left", Qt.MouseButton.RightButton: "Mouse Right"}


def key_name(event):
    modifiers = {Qt.Key.Key_Shift: "Shift", Qt.Key.Key_Control: "Ctrl", Qt.Key.Key_Alt: "Alt"}
    return modifiers.get(event.key()) or QKeySequence(event.key()).toString()


class Scroller:
    def __init__(self, phone):
        self.phone = phone
        self.lock = threading.Lock()
        self.origin = (0.5, 0.5)
        self.pending = (0.0, 0.0)
        self.busy = False

    def push(self, u, v, du, dv):
        with self.lock:
            self.origin = (u, v)
            self.pending = (self.pending[0] + du, self.pending[1] + dv)
            if self.busy:
                return
            self.busy = True
        threading.Thread(target=self.drain, daemon=True).start()

    def drain(self):
        while True:
            with self.lock:
                du, dv = self.pending
                if not du and not dv:
                    self.busy = False
                    return
                take = (max(-SCROLL_LIMIT, min(SCROLL_LIMIT, du)), max(-SCROLL_LIMIT, min(SCROLL_LIMIT, dv)))
                self.pending = (du - take[0], dv - take[1])
                u, v = self.origin
            self.drag(u, v, *take)

    def drag(self, u, v, du, dv):
        u = min(max(u, 0.05 - min(du, 0)), 0.95 - max(du, 0))
        v = min(max(v, 0.05 - min(dv, 0)), 0.95 - max(dv, 0))
        steps = 8
        self.touch(u, v, True)
        for step in range(1, steps + 1):
            time.sleep(0.01)
            self.touch(u + du * step / steps, v + dv * step / steps, True)
        time.sleep(0.05)
        self.touch(u + du, v + dv, False)

    def touch(self, u, v, down):
        bridge = self.phone.bridge
        if bridge and self.phone.controller:
            bridge.touch((SCROLL_TOUCH, *self.phone.device_point(u, v), down))


class EditBar(QFrame):
    def __init__(self, phone):
        super().__init__(phone)
        self.setStyleSheet(f"EditBar {{ background: {COLORS['surface']}; border-radius: 10px; }}")
        layout = QHBoxLayout(self)
        layout.setContentsMargins(14, 8, 8, 8)
        layout.setSpacing(6)
        self.hint = QLabel()
        self.hint.setStyleSheet(f"color: {COLORS['text']}; background: transparent;")
        self.hint.setMinimumWidth(300)
        layout.addWidget(self.hint)
        for text, action in (("Joystick", phone.add_joystick), ("Aim", phone.add_aim), ("Fire", phone.add_fire),
                             ("Scope", phone.add_scope), ("Skill", phone.add_skill),
                             ("Clear", phone.clear_controls)):
            layout.addWidget(button(text, action, kind="secondary"))
        layout.addWidget(button("Done", phone.finish_editing))
        self.hide()


class PhoneView(QWidget):
    frame_ready = Signal()
    editing_changed = Signal(bool)

    def __init__(self, host):
        super().__init__()
        self.host = host
        self.controller = None
        self.bridge = None
        self.image = None
        self.buffer = None
        self.rotation = 0
        self.latest = None
        self.scheduled = False
        self.last_frame = 0.0
        self.frames = 0
        self.fps = 0
        self.touching = False
        self.held = {}
        self.engine = keymap.Engine()
        self.controls = []
        self.package = None
        self.editing = False
        self.selected = None
        self.dragging = False
        self.bind_step = 0
        self.shooting = False
        self.lock_point = None
        self.gamepads = gamepad.Gamepads()
        self.pad_pressed = set()
        self.pad_left = (0.0, 0.0)
        self.pad_looking = False

        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.setAcceptDrops(True)
        self.setMouseTracking(True)
        self.setAttribute(Qt.WidgetAttribute.WA_OpaquePaintEvent)
        self.frame_ready.connect(self.take_frame, Qt.ConnectionType.QueuedConnection)
        self.restream_timer = QTimer(self, singleShot=True, interval=120, timeout=self.restream)
        self.fps_timer = QTimer(self, interval=1000, timeout=self.count_fps)
        self.fps_timer.start()
        self.pad_timer = QTimer(self, interval=PAD_INTERVAL, timeout=self.poll_pad)
        self.edit_bar = EditBar(self)
        self.scroller = Scroller(self)

    def show_controller(self, controller):
        if self.controller:
            self.controller.attached.disconnect(self.restream)
            self.controller.app_changed.disconnect(self.load_controls)
        self.stop_stream()
        self.release_input()
        self.finish_editing()
        self.controller = controller
        self.image = None
        if controller:
            controller.attached.connect(self.restream)
            controller.app_changed.connect(self.load_controls)
        self.load_controls()
        self.restream()

    def restream(self):
        self.stop_stream()
        if not (self.controller and self.controller.bridge and self.isVisible()):
            return
        self.bridge = self.controller.bridge
        ratio = self.devicePixelRatioF()
        self.bridge.watch(max(1, int(self.width() * ratio)), max(1, int(self.height() * ratio)), self.receive)

    def stop_stream(self):
        if self.bridge:
            self.bridge.unwatch()
        self.bridge = None

    def receive(self, data, width, height, rotation):
        now = time.monotonic()
        if self.controller and self.controller.instance.eco and now - self.last_frame < ECO_INTERVAL:
            return
        self.last_frame = now
        self.latest = (data, width, height, rotation)
        if not self.scheduled:
            self.scheduled = True
            self.frame_ready.emit()

    def take_frame(self):
        self.scheduled = False
        if not self.latest:
            return
        self.buffer, width, height, self.rotation = self.latest
        self.image = QImage(self.buffer, width, height, width * 3, QImage.Format.Format_RGB888)
        self.image.setDevicePixelRatio(self.devicePixelRatioF())
        self.frames += 1
        self.update()

    def count_fps(self):
        self.fps, self.frames = self.frames, 0
        if self.host.prefs["show_fps"]:
            self.update()

    def frame_rect(self):
        if not self.image:
            return QRectF(self.rect())
        size = self.image.deviceIndependentSize()
        return QRectF((self.width() - size.width()) / 2, (self.height() - size.height()) / 2,
                      size.width(), size.height())

    def frame_size(self):
        frame = self.frame_rect()
        return frame.width(), frame.height()

    def showEvent(self, event):
        self.restream()
        self.pad_timer.start()

    def hideEvent(self, event):
        self.pad_timer.stop()
        self.stop_stream()
        self.release_input()

    def resizeEvent(self, event):
        self.restream_timer.start()
        self.place_edit_bar()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
        painter.fillRect(self.rect(), QColor(COLORS["main"]))
        if not self.image:
            return
        rect = self.frame_rect()
        clip = QPainterPath()
        clip.addRoundedRect(rect, 10, 10)
        painter.save()
        painter.setClipPath(clip)
        painter.drawImage(rect, self.image)
        if self.editing:
            painter.fillRect(rect, QColor(0, 0, 0, 90))
        painter.restore()
        prefs = self.host.prefs
        if self.controls and (self.editing or prefs["show_hints"] and prefs["game_controls"]):
            self.paint_controls(painter, rect)
        if prefs["show_fps"]:
            painter.setFont(text_font(12, strong=True))
            painter.setPen(QColor(COLORS["green"]))
            painter.drawText(rect.adjusted(12, 0, 0, -10), Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignBottom,
                             f"{self.fps} FPS")
        if self.controller and (self.controller.video or self.controller.recording_macro):
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(QColor(COLORS["red"]))
            painter.drawEllipse(QPointF(rect.right() - 18, rect.top() + 18), 6, 6)

    def paint_controls(self, painter, rect):
        painter.setFont(text_font(12, strong=True))
        span = min(rect.width(), rect.height())
        for index, control in enumerate(self.controls):
            center = QPointF(rect.left() + control.x * rect.width(), rect.top() + control.y * rect.height())
            selected = self.editing and index == self.selected
            color = QColor(COLORS["accent"]) if selected else QColor(255, 255, 255, 150)
            painter.setPen(QPen(color, 2 if selected else 1.2))
            if control.kind == "joystick":
                radius = control.size * span
                painter.setBrush(QColor(0, 0, 0, 80))
                painter.drawEllipse(center, radius, radius)
                painter.setPen(QColor("#ffffff"))
                for step, (dx, dy) in enumerate(keymap.DIRECTIONS):
                    text = control.keys[step]
                    width = max(28, painter.fontMetrics().horizontalAdvance(text) + 8)
                    spot = QRectF(center.x() + dx * radius * 0.66 - width / 2, center.y() + dy * radius * 0.66 - 12,
                                  width, 24)
                    if selected and step == self.bind_step:
                        painter.setPen(QColor(COLORS["accent"]))
                    painter.drawText(spot, Qt.AlignmentFlag.AlignCenter, text)
                    painter.setPen(QColor("#ffffff"))
                continue
            if control.kind == "aim":
                painter.setBrush(QColor(0, 0, 0, 90))
                painter.drawEllipse(center, 22, 22)
                for dx, dy in keymap.DIRECTIONS:
                    painter.drawLine(QPointF(center.x() + dx * 8, center.y() + dy * 8),
                                     QPointF(center.x() + dx * 18, center.y() + dy * 18))
                painter.setPen(QColor("#ffffff"))
                painter.drawText(QRectF(center.x() - 40, center.y() + 24, 80, 20), Qt.AlignmentFlag.AlignCenter,
                                 control.label() or "?")
                continue
            if control.kind == "skill" and self.editing:
                reach = control.size * span
                dashed = QPen(color, 1.2, Qt.PenStyle.DashLine)
                painter.setPen(dashed)
                painter.setBrush(Qt.BrushStyle.NoBrush)
                painter.drawEllipse(center, reach, reach)
                painter.setPen(QPen(color, 2 if selected else 1.2))
            text = control.label() or "?"
            width = max(30, painter.fontMetrics().horizontalAdvance(text) + 16)
            chip = QRectF(center.x() - width / 2, center.y() - 15, width, 30)
            painter.setBrush(QColor(0, 0, 0, 150))
            painter.drawRoundedRect(chip, 15 if control.kind == "skill" else 8, 15 if control.kind == "skill" else 8)
            painter.setPen(QColor("#ffffff"))
            painter.drawText(chip, Qt.AlignmentFlag.AlignCenter, text)

    def normalized(self, position):
        rect = self.frame_rect()
        u = (position.x() - rect.left()) / rect.width()
        v = (position.y() - rect.top()) / rect.height()
        return min(max(u, 0.0), 1.0), min(max(v, 0.0), 1.0)

    def inside(self, position):
        return self.image is not None and self.frame_rect().contains(position)

    def device_point(self, u, v):
        width, height = self.controller.instance.width, self.controller.instance.height
        if self.rotation == 1:
            return (1 - v) * width, u * height
        if self.rotation == 2:
            return (1 - u) * width, (1 - v) * height
        if self.rotation == 3:
            return v * width, (1 - u) * height
        return u * width, v * height

    def send_touches(self, touches):
        if not self.bridge:
            return
        for identifier, u, v, down in touches:
            self.bridge.touch((identifier, *self.device_point(u, v), down))

    def game_controls_active(self):
        return self.host.prefs["game_controls"] and bool(self.controls)

    def handle(self, name, down):
        if not (self.game_controls_active() and self.engine.handles(name)):
            return False
        aim = self.engine.aim_control()
        if aim and name == aim.key:
            if down:
                self.toggle_shooting()
            return True
        self.send_touches(self.engine.press(name, down, *self.frame_size()))
        return True

    def toggle_shooting(self):
        if self.shooting:
            self.stop_shooting()
            return
        self.shooting = True
        self.lock_point = self.mapToGlobal(self.frame_rect().center().toPoint())
        self.grabMouse()
        self.setCursor(Qt.CursorShape.BlankCursor)
        QCursor.setPos(self.lock_point)
        self.host.toast(f"Shooting mode: move the mouse to aim. Press {self.engine.aim_control().key} to "
                        "get your cursor back")

    def stop_shooting(self):
        if not self.shooting:
            return
        self.shooting = False
        self.releaseMouse()
        self.unsetCursor()
        self.send_touches(self.engine.stop_looking())

    def mousePressEvent(self, event):
        self.setFocus()
        if self.shooting:
            name = MOUSE_BUTTONS.get(event.button())
            if name:
                self.handle(name, True)
            return
        if self.bridge and self.image is None:
            self.controller.wake()
            return
        if not self.bridge or not self.inside(event.position()):
            return
        if self.editing:
            self.edit_press(event)
            return
        if event.button() == Qt.MouseButton.LeftButton:
            self.touching = True
            self.send_touches([(MOUSE_TOUCH, *self.normalized(event.position()), True)])
        elif event.button() == Qt.MouseButton.RightButton:
            self.bridge.key("GoBack")
        elif event.button() == Qt.MouseButton.MiddleButton:
            self.bridge.key("GoHome")

    def mouseMoveEvent(self, event):
        if self.editing:
            if self.dragging and self.selected is not None:
                control = self.controls[self.selected]
                control.x, control.y = self.normalized(event.position())
                self.update()
        elif self.shooting:
            delta = event.globalPosition().toPoint() - self.lock_point
            if delta.manhattanLength():
                self.send_touches(self.engine.look(delta.x(), delta.y(), *self.frame_size()))
                QCursor.setPos(self.lock_point)
        elif self.touching and self.bridge:
            self.send_touches([(MOUSE_TOUCH, *self.normalized(event.position()), True)])
        elif self.game_controls_active():
            self.send_touches(self.engine.point(*self.normalized(event.position()), *self.frame_size()))

    def mouseReleaseEvent(self, event):
        if self.editing:
            if self.dragging:
                self.dragging = False
                self.save_controls()
            return
        if self.shooting:
            name = MOUSE_BUTTONS.get(event.button())
            if name:
                self.handle(name, False)
            return
        if self.touching and event.button() == Qt.MouseButton.LeftButton and self.bridge:
            self.touching = False
            self.send_touches([(MOUSE_TOUCH, *self.normalized(event.position()), False)])

    def wheelEvent(self, event):
        if self.editing:
            if self.selected is not None:
                self.resize_control(self.controls[self.selected], event.angleDelta().y() / 120)
            return
        if not self.bridge:
            return
        frame = self.frame_rect()
        du = event.angleDelta().x() / 120 * SCROLL_STEP * frame.height() / frame.width()
        dv = event.angleDelta().y() / 120 * SCROLL_STEP
        self.scroller.push(*self.normalized(event.position()), du, dv)

    def keyPressEvent(self, event):
        if self.editing:
            self.edit_key(event)
            return
        if not self.bridge:
            return
        name = key_name(event)
        if event.isAutoRepeat() and self.game_controls_active() and self.engine.handles(name):
            return
        if self.handle(name, True):
            return
        key = ANDROID_KEYS.get(event.key()) or (event.text() if event.text().isprintable() else "")
        if key:
            self.held[event.key()] = key
            self.bridge.key(key, KEYDOWN)

    def keyReleaseEvent(self, event):
        if self.editing or not self.bridge or event.isAutoRepeat():
            return
        if self.handle(key_name(event), False):
            return
        key = self.held.pop(event.key(), None)
        if key:
            self.bridge.key(key, KEYUP)

    def poll_pad(self):
        state = self.gamepads.poll() if self.window().isActiveWindow() else None
        pressed, left, right = state or (set(), (0.0, 0.0), (0.0, 0.0))
        for name in sorted(pressed - self.pad_pressed):
            self.pad_button(name, True)
        for name in sorted(self.pad_pressed - pressed):
            self.pad_button(name, False)
        self.pad_pressed = pressed
        if self.editing or not self.bridge or not self.game_controls_active():
            return
        width, height = self.frame_size()
        if left != self.pad_left:
            self.pad_left = left
            self.send_touches(self.engine.stick(*left, width, height))
        if any(right) and self.engine.aim_control():
            self.pad_looking = True
            self.send_touches(self.engine.look(right[0] * LOOK_SPEED, right[1] * LOOK_SPEED, width, height))
        elif self.pad_looking and not self.shooting:
            self.pad_looking = False
            self.send_touches(self.engine.stop_looking())

    def pad_button(self, name, down):
        if self.editing:
            if down:
                self.bind(name)
            return
        if not self.bridge or self.handle(name, down):
            return
        key = PAD_KEYS.get(name)
        if key:
            self.bridge.key(key, KEYDOWN if down else KEYUP)

    def focusNextPrevChild(self, forward):
        return False

    def focusOutEvent(self, event):
        self.release_input()

    def release_input(self):
        self.stop_shooting()
        if not self.bridge:
            self.held.clear()
            self.engine.release_all()
            return
        self.send_touches(self.engine.release_all())
        for key in self.held.values():
            self.bridge.key(key, KEYUP)
        self.held.clear()
        self.pad_left = (0.0, 0.0)
        self.pad_looking = False
        if self.touching:
            self.touching = False
            self.bridge.touch((MOUSE_TOUCH, 0, 0, False))

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event):
        files = [url.toLocalFile() for url in event.mimeData().urls() if url.isLocalFile()]
        if files and self.controller:
            self.controller.open_files(files)

    def load_controls(self):
        self.stop_shooting()
        self.package = self.controller.package if self.controller else None
        self.controls = keymap.load(self.package) if self.package else []
        self.engine.use(self.controls)
        self.selected = None
        self.update()

    def save_controls(self):
        if self.package:
            keymap.save(self.package, self.controls)
        self.engine.use(self.controls)
        self.host.controls_changed()

    def start_editing(self):
        if not self.controller or not self.controller.on:
            self.host.toast("Start Android and open a game first")
            return
        if not self.package:
            self.host.toast("Open the game you want to set up first")
            return
        self.release_input()
        self.editing = True
        self.select(None)
        self.edit_bar.show()
        self.place_edit_bar()
        self.setFocus()
        self.editing_changed.emit(True)

    def finish_editing(self):
        if not self.editing:
            return
        self.editing = False
        self.controls[:] = [control for control in self.controls if control.kind == "joystick" or control.key]
        self.save_controls()
        self.edit_bar.hide()
        self.editing_changed.emit(False)
        self.update()

    def place_edit_bar(self):
        self.edit_bar.adjustSize()
        self.edit_bar.move(max(0, (self.width() - self.edit_bar.width()) // 2), 12)

    def select(self, index):
        self.selected = index
        self.bind_step = 0
        control = self.controls[index] if index is not None else None
        if control is None:
            hint = "Click to place a key. Drag to move, right-click to remove, scroll to resize."
        elif control.kind == "joystick":
            hint = f"Press the key for {DIRECTION_NAMES[self.bind_step]}"
        elif control.kind == "aim":
            hint = "Press the key that turns shooting mode on and off. Scroll to change sensitivity."
        else:
            hint = "Press a key or controller button for this spot"
        self.edit_bar.hint.setText(hint)
        self.place_edit_bar()
        self.update()

    def control_at(self, position):
        rect = self.frame_rect()
        span = min(rect.width(), rect.height())
        for index in reversed(range(len(self.controls))):
            control = self.controls[index]
            center = QPointF(rect.left() + control.x * rect.width(), rect.top() + control.y * rect.height())
            reach = control.size * span if control.kind == "joystick" else 24
            if (position - center).manhattanLength() <= reach * 1.3:
                return index
        return None

    def edit_press(self, event):
        index = self.control_at(event.position())
        if event.button() == Qt.MouseButton.RightButton:
            if index is not None:
                del self.controls[index]
                self.select(None)
                self.save_controls()
            return
        if index is None:
            self.controls[:] = [control for control in self.controls if control.kind == "joystick" or control.key]
            self.controls.append(keymap.Control("tap", *self.normalized(event.position())))
            index = len(self.controls) - 1
        self.select(index)
        self.dragging = True

    def edit_key(self, event):
        if event.key() == Qt.Key.Key_Escape:
            self.finish_editing()
        elif event.key() in (Qt.Key.Key_Delete, Qt.Key.Key_Backspace) and self.selected is not None:
            del self.controls[self.selected]
            self.select(None)
            self.save_controls()
        elif not event.isAutoRepeat():
            self.bind(key_name(event))

    def bind(self, name):
        if self.selected is None:
            return
        control = self.controls[self.selected]
        if control.kind == "joystick":
            control.keys[self.bind_step] = name
            self.bind_step = (self.bind_step + 1) % 4
            self.edit_bar.hint.setText(f"Press the key for {DIRECTION_NAMES[self.bind_step]}")
        else:
            control.key = name
        self.save_controls()
        self.update()

    def resize_control(self, control, steps):
        if control.kind == "aim":
            control.speed = round(min(4.0, max(0.2, control.speed + steps * 0.1)), 2)
            self.host.toast(f"Aim sensitivity {control.speed:.1f}")
        else:
            control.size = min(0.3, max(0.04, control.size + steps * 0.01))
        self.save_controls()
        self.update()

    def add(self, control):
        self.controls.append(control)
        self.select(len(self.controls) - 1)
        self.save_controls()
        self.setFocus()

    def add_joystick(self):
        self.add(keymap.Control("joystick", 0.18, 0.72))

    def add_aim(self):
        self.add(keymap.Control("aim", 0.68, 0.42, key="F1"))

    def add_fire(self):
        self.add(keymap.Control("tap", 0.86, 0.72, key="Mouse Left"))

    def add_scope(self):
        self.add(keymap.Control("tap", 0.86, 0.52, key="Mouse Right"))

    def add_skill(self):
        self.add(keymap.Control("skill", 0.8, 0.62, size=0.1))

    def clear_controls(self):
        self.controls.clear()
        self.select(None)
        self.save_controls()
        self.setFocus()
