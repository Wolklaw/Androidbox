import subprocess
import time

from PySide6.QtCore import QRectF, Qt, QTimer
from PySide6.QtGui import QColor, QPainter, QPainterPath
from PySide6.QtWidgets import (QComboBox, QFrame, QHBoxLayout, QLineEdit, QMenu, QPlainTextEdit, QScrollArea,
                               QStackedWidget, QToolButton, QVBoxLayout, QWidget)

from .. import installer, instances, keymap, macros
from .phone import PhoneView
from .theme import COLORS, ICONS
from .tools import ToolRail
from .widgets import Modal, Toggle, avatar, button, column, confirm, divider, glyph_css, label, recolor, row

STATES = {"on": "Running", "booting": "Starting…", "stopping": "Shutting down…", "crashed": "Stopped unexpectedly"}


class Bar(QWidget):
    def __init__(self, height=6, busy=False):
        super().__init__()
        self.setFixedHeight(height)
        self.fraction = 0.0
        self.busy = busy
        self.timer = QTimer(self, interval=16, timeout=self.update)
        if busy:
            self.timer.start()

    def set_fraction(self, fraction):
        self.fraction = min(max(fraction, 0.0), 1.0)
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        radius = self.height() / 2
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QColor(COLORS["raised"]))
        painter.drawRoundedRect(QRectF(self.rect()), radius, radius)
        painter.setBrush(QColor(COLORS["accent"]))
        if self.busy:
            clip = QPainterPath()
            clip.addRoundedRect(QRectF(self.rect()), radius, radius)
            painter.setClipPath(clip)
            cycle = (time.monotonic() % 1.4) / 1.4
            width = self.width() * 0.35
            painter.drawRoundedRect(QRectF(-width + cycle * (self.width() + width), 0, width, self.height()),
                                    radius, radius)
        elif self.fraction > 0:
            painter.drawRoundedRect(QRectF(0, 0, max(self.height(), self.width() * self.fraction), self.height()),
                                    radius, radius)


class Progress(Modal):
    def __init__(self, parent, title, text):
        super().__init__(parent, title, text)
        self.status = self.add(label("", "Small"))
        self.bar = self.add(Bar(8))
        self.finished = False
        self.open()

    def update_progress(self, text, fraction):
        self.status.setText(text)
        self.bar.set_fraction(fraction)

    def done(self, title, text):
        self.finished = True
        self.close_modal()
        modal = Modal(self.parentWidget(), title, text)
        modal.action("OK")
        modal.open()

    def keyPressEvent(self, event):
        if self.finished:
            super().keyPressEvent(event)

    def mousePressEvent(self, event):
        if self.finished:
            super().mousePressEvent(event)


class Page(QScrollArea):
    def __init__(self, width=720):
        super().__init__()
        self.setWidgetResizable(True)
        holder = QWidget()
        holder.setObjectName("Page")
        outer = QHBoxLayout(holder)
        outer.setContentsMargins(24, 24, 24, 32)
        self.content = QWidget()
        self.content.setMaximumWidth(width)
        self.body = QVBoxLayout(self.content)
        self.body.setContentsMargins(0, 0, 0, 0)
        self.body.setSpacing(16)
        self.body.setAlignment(Qt.AlignmentFlag.AlignTop)
        outer.addWidget(self.content)
        outer.addStretch(1)
        self.setWidget(holder)

    def clear(self):
        while self.body.count():
            item = self.body.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

    def add(self, *widgets):
        for widget in widgets:
            self.body.addWidget(widget)

    def intro(self, title, text):
        self.add(label(title, "Heading"), label(text, "Muted", wrap=True))


def card(*widgets, spacing=12):
    frame = QFrame()
    frame.setObjectName("Card")
    layout = QVBoxLayout(frame)
    layout.setContentsMargins(16, 16, 16, 16)
    layout.setSpacing(spacing)
    for widget in widgets:
        layout.addWidget(widget)
    return frame


def setting(title, text, control):
    words = column(label(title, "Subheading"), label(text, "Small", wrap=True), spacing=2)
    line = QWidget()
    layout = QHBoxLayout(line)
    layout.setContentsMargins(0, 0, 0, 0)
    layout.setSpacing(24)
    layout.addWidget(words, 1)
    layout.addWidget(control, 0, Qt.AlignmentFlag.AlignVCenter)
    return line


def choice(options, current):
    combo = QComboBox()
    for text, value in options:
        combo.addItem(text, value)
    combo.setCurrentIndex(max(0, combo.findData(current)))
    combo.setMinimumWidth(220)
    combo.setCursor(Qt.CursorShape.PointingHandCursor)
    return combo


def menu_button(actions):
    more = QToolButton()
    more.setText(ICONS["more"])
    more.setFixedSize(34, 34)
    more.setCursor(Qt.CursorShape.PointingHandCursor)
    more.setPopupMode(QToolButton.ToolButtonPopupMode.InstantPopup)
    more.setStyleSheet(f"""
        QToolButton {{ border: none; border-radius: 8px; background: {COLORS["raised"]}; color: {COLORS["text"]};
                       {glyph_css(14)} }}
        QToolButton:hover {{ background: #383c42; }}
        QToolButton::menu-indicator {{ image: none; width: 0; }}
    """)
    menu = QMenu(more)
    for text, action in actions:
        if text is None:
            menu.addSeparator()
        else:
            menu.addAction(text, action)
    more.setMenu(menu)
    return more


class StateView(QWidget):
    def __init__(self, host):
        super().__init__()
        self.host = host
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setSpacing(10)
        self.badge = avatar(ICONS["screen"], COLORS["surface"], 88, glyph=True)
        self.title = label("", "Heading")
        self.text = label("", "Muted", wrap=True)
        self.text.setFixedWidth(420)
        self.text.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.bar = Bar(busy=True)
        self.bar.setFixedWidth(280)
        self.actions = QHBoxLayout()
        self.actions.setSpacing(10)
        for widget in (self.badge, self.title, self.text, self.bar):
            layout.addWidget(widget, alignment=Qt.AlignmentFlag.AlignHCenter)
        layout.addSpacing(8)
        layout.addLayout(self.actions)

    def show_state(self, controller, popped=False):
        while self.actions.count():
            self.actions.takeAt(0).widget().deleteLater()
        state = controller.state
        if popped:
            title, text = "Open in its own window", f"{controller.instance.name} is showing in a separate window."
        elif state == "booting":
            title, text = "Starting Android…", "This takes a few seconds, or up to a minute on the very first start."
        elif state == "stopping":
            title, text = "Shutting down…", "Android is saving its state so it resumes quickly next time."
        elif state == "crashed":
            title, text = "Android stopped unexpectedly", "The log may say why. Starting again usually fixes it."
        elif state == "on":
            title, text = "Connecting…", "Android is running. Connecting to its screen."
        else:
            title, text = "Android is off", "Start it to use your apps and games. Drop APK files here to install them."
        self.title.setText(title)
        self.text.setText(text)
        busy = state in ("booting", "stopping", "on") and not popped
        self.bar.setVisible(busy)
        if busy:
            self.bar.timer.start()
        else:
            self.bar.timer.stop()
        recolor(self.badge, COLORS["danger"] if state == "crashed" and not popped else COLORS["surface"])
        if popped:
            self.actions.addWidget(button("Bring it back", self.host.toggle_popout, size="large"))
        elif state in ("off", "crashed"):
            self.actions.addWidget(button("Start Android", controller.start, size="large"))
        if state == "crashed" and not popped:
            self.actions.addWidget(button("Open log", controller.open_log, kind="secondary", size="large"))


class ScreenPage(QWidget):
    def __init__(self, host):
        super().__init__()
        self.host = host
        self.stack = QStackedWidget()
        self.state = StateView(host)
        self.phone = PhoneView(host)
        self.stack.addWidget(self.state)
        self.stack.addWidget(self.phone)
        self.tools = ToolRail(host)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        self.holder = QWidget()
        self.holder.setObjectName("Page")
        inner = QVBoxLayout(self.holder)
        inner.setContentsMargins(16, 16, 16, 16)
        inner.addWidget(self.stack)
        layout.addWidget(self.holder, 1)
        layout.addWidget(self.tools)
        self.phone.editing_changed.connect(lambda _: host.refresh_tools())

    def refresh(self, controller, popped=False):
        if controller.on and not popped:
            if self.stack.currentWidget() is not self.phone:
                self.stack.setCurrentWidget(self.phone)
                self.phone.setFocus()
        else:
            self.stack.setCurrentWidget(self.state)
            self.state.show_state(controller, popped)
        self.tools.refresh(controller, self.host.prefs, self.phone.editing)


class ControlsPage(Page):
    def __init__(self, host):
        super().__init__()
        self.host = host

    def refresh(self, controller):
        self.clear()
        prefs = self.host.prefs
        self.intro("Game controls", "Play with a keyboard, mouse or controller. Place controls on the screen and "
                                    "Androidbox touches there for you. Every game keeps its own layout.")
        package = controller.package if controller.on else None
        controls = keymap.load(package) if package else []
        current = label(package or "Start Android and open a game to set up its controls.",
                        "Subheading" if package else "Muted", wrap=True)
        edit = button("Edit on screen", self.host.edit_controls)
        edit.setEnabled(bool(package))
        clear = button("Clear", lambda: self.clear_controls(package), kind="secondary")
        clear.setEnabled(bool(controls))
        self.add(card(label("Current app", "Section"), current, row(edit, clear, None)))

        enabled = Toggle(prefs["game_controls"])
        enabled.toggled.connect(lambda on: self.host.set_pref("game_controls", on))
        hints = Toggle(prefs["show_hints"])
        hints.toggled.connect(lambda on: self.host.set_pref("show_hints", on))
        self.add(card(setting("Use game controls", "Turn this off to type normally in games that have controls.",
                              enabled), divider(),
                      setting("Show key hints", "Draw your controls on top of the game.", hints)))

        if controls:
            rows = [label("This game", "Section")]
            for control in controls:
                chip = label(control.label(), "Subheading")
                chip.setMinimumWidth(96)
                rows.append(row(chip, label(control.describe(), "Muted"), None))
            self.add(card(*rows, spacing=8))

        kinds = [("Tap", "Click the screen while editing, then press a key or controller button"),
                 ("Joystick", "Moves with WASD, the D-pad or the left stick. Select it and press four keys to "
                              "rebind"),
                 ("Aim", "Shooter mode: its key locks the mouse, and moving the mouse turns the camera"),
                 ("Fire and Scope", "Taps for the left and right mouse buttons while aiming"),
                 ("Skill", "MOBA casting: hold the key, point with the mouse, release to cast")]
        rows = [label("Controls you can add", "Section")]
        for name, what in kinds:
            title = label(name, "Subheading")
            title.setMinimumWidth(96)
            rows.append(row(title, label(what, "Muted", wrap=True), spacing=8))
        self.add(card(*rows, spacing=8))

        tips = ["Left-click taps, drag swipes, the scroll wheel scrolls",
                "Right-click goes Back, middle-click goes Home",
                "Controllers navigate Android too: A is Enter, B is Back, Start is Home",
                "Drop APK or XAPK files on the screen to install them"]
        self.add(card(label("Mouse, keyboard and controller", "Section"),
                      *[label(f"•  {tip}", "Muted") for tip in tips], spacing=6))

    def clear_controls(self, package):
        keymap.save(package, [])
        self.host.controls_changed()


class MacrosPage(Page):
    def __init__(self, host):
        super().__init__()
        self.host = host

    def refresh(self, controller):
        self.clear()
        self.intro("Macros", "Record taps, swipes and key presses once, then replay them as often as you like. "
                             "Handy for repetitive game tasks.")
        if controller.recording_macro:
            record = button("Stop recording", self.host.toggle_macro, kind="danger")
        else:
            record = button("Record a macro", self.host.record_macro)
        self.add(row(record, None))
        saved = macros.load(controller.instance)
        if not saved:
            self.add(card(label("No macros yet. Record one, and it shows up here.", "Muted")))
            return
        rows = []
        for macro in saved:
            name = macro["name"]
            details = column(label(name, "Subheading"),
                             label(f"{macro['duration']:.1f} seconds · {len(macro['events'])} actions", "Small"),
                             spacing=2)
            if controller.playing == name:
                actions = [button("Stop", controller.stop_macro, kind="danger")]
            else:
                actions = [button("Play", lambda m=macro: self.play(controller, m, 1)),
                           button("Loop", lambda m=macro: self.play(controller, m, 0), kind="secondary")]
            actions.append(button("Delete", lambda n=name: self.delete(controller, n), kind="secondary"))
            rows.append(row(details, None, *actions))
        self.add(card(label("Saved", "Section"), *rows, spacing=10))

    def play(self, controller, macro, loops):
        controller.play_macro(macro, loops)
        self.host.show_page("screen")

    def delete(self, controller, name):
        macros.delete(controller.instance, name)
        controller.macros_changed.emit()


class SettingsPage(Page):
    def __init__(self, host):
        super().__init__()
        self.host = host

    def refresh(self, controller):
        self.clear()
        host = self.host
        instance = controller.instance
        self.intro("Settings", f"Settings for {instance.name}. Hardware changes apply the next time it starts.")

        name = QLineEdit(instance.name)
        name.setMaxLength(32)
        name.editingFinished.connect(lambda: host.rename(controller, name.text()))
        self.add(card(label("Name", "Section"), name))

        cores = choice([(f"{count} cores", count) for count in (2, 4, 6, 8)], instance.cores)
        memory = choice([(f"{size // 1024} GB", size) for size in (2048, 3072, 4096, 6144, 8192)], instance.ram)
        display = choice([(f"{preset}  ·  {width}×{height}", preset)
                          for preset, (width, height, _) in instances.RESOLUTIONS.items()], instance.resolution)
        rate = choice([(f"{fps} FPS", fps) for fps in instances.FRAME_RATES], instance.fps)
        cores.currentIndexChanged.connect(lambda: host.set_hardware(controller, cores=cores.currentData()))
        memory.currentIndexChanged.connect(lambda: host.set_hardware(controller, ram=memory.currentData()))
        display.currentIndexChanged.connect(lambda: host.set_resolution(controller, display.currentData()))
        rate.currentIndexChanged.connect(lambda: host.set_hardware(controller, fps=rate.currentData()))
        restart = []
        if controller.state in ("on", "booting"):
            restart = [divider(), row(label("Restart Android to use new hardware settings.", "Muted"), None,
                                      button("Restart", controller.restart, kind="secondary"))]
        self.add(card(label("Performance", "Section"),
                      setting("Processor", "More cores help heavy games.", cores), divider(),
                      setting("Memory", "4 GB suits most apps and games.", memory), divider(),
                      setting("Display", "Tablet runs in landscape, which most games prefer.", display), divider(),
                      setting("Frame rate", "Higher is smoother in games that support it, and uses more power.",
                              rate), *restart))

        eco = Toggle(instance.eco)
        eco.toggled.connect(controller.set_eco)
        ads = Toggle(instance.block_ads)
        ads.toggled.connect(controller.set_block_ads)
        browser = button("Set up", lambda: host.set_up_browser(controller), kind="secondary")
        self.add(card(label("Extras", "Section"),
                      setting("Eco mode", "Draws fewer frames and lowers Android's CPU priority. Good for "
                                          "idle games running in the background.", eco), divider(),
                      setting("Block ads", "Blocks ad networks inside apps and games. It can't remove ads that "
                                           "come from the same servers as the content, like YouTube's.", ads),
                      divider(),
                      setting("Ad-free browser", "Installs Firefox and uBlock Origin, which blocks ads on every "
                                                 "website, YouTube included.", browser)))

        backup = button("Back up", lambda: host.back_up(controller), kind="secondary")
        self.add(card(label("Backup", "Section"),
                      setting("Back up this instance", "Saves its apps, data and settings to one file you can "
                                                       "restore from All instances.", backup)))

        reset = button("Factory reset", lambda: confirm(
            host.dialog_parent(), "Factory reset", f"Erase every app and all data on {instance.name}? "
            "This can't be undone.", "Erase everything", controller.factory_reset, danger=True), kind="danger")
        delete = button("Delete instance", lambda: host.delete_instance(controller), kind="danger")
        self.add(card(label("Danger zone", "Section"),
                      setting("Factory reset", "Erase all apps and data, like a new phone.", reset), divider(),
                      setting("Delete instance", "Remove this instance and everything in it.", delete)))


class InstancesPage(Page):
    def __init__(self, host):
        super().__init__(width=820)
        self.host = host

    def refresh(self):
        self.clear()
        host = self.host
        self.intro("Instances", "Run several Androids side by side. Each has its own apps, accounts and settings.")
        running = any(c.state not in ("off", "crashed") for c in host.controllers.values())
        stop_all = button("Stop all", host.stop_all, kind="secondary")
        stop_all.setEnabled(running)
        self.add(row(button("New instance", host.new_instance),
                     button("Restore a backup", host.restore_backup, kind="secondary"), stop_all, None))
        rows = []
        for controller in host.controllers.values():
            instance = controller.instance
            color = COLORS["green"] if controller.state == "on" else COLORS["faint"]
            words = column(label(instance.name, "Subheading"),
                           label(f"<span style='color:{color}'>●</span>  {STATES.get(controller.state, 'Off')}  ·  "
                                 f"{instance.resolution}  ·  {instance.cores} cores  ·  {instance.ram // 1024} GB  ·  "
                                 f"{instance.fps} FPS", "Small"), spacing=2)
            if controller.state in ("off", "crashed"):
                power = button("Start", controller.start)
            else:
                power = button("Stop", controller.stop, kind="secondary")
                power.setEnabled(controller.state != "stopping")
            more = menu_button([
                ("Open in its own window", lambda c=controller: host.pop_out(c)),
                ("Clone", lambda c=controller: host.clone_instance(c)),
                ("Back up", lambda c=controller: host.back_up(c)),
                (None, None),
                ("Delete", lambda c=controller: host.delete_instance(c)),
            ])
            rows.append(row(avatar(instance.initials, COLORS["raised"]), words, None, power,
                            button("Open", lambda c=controller: host.select(c.instance.id), kind="secondary"),
                            more, spacing=10))
        if rows:
            self.add(card(label(f"Your instances · {len(rows)}", "Section"), *rows, spacing=12))

        sync = Toggle(host.prefs["sync_input"])
        sync.toggled.connect(lambda on: host.set_pref("sync_input", on))
        fps = Toggle(host.prefs["show_fps"])
        fps.toggled.connect(lambda on: host.set_pref("show_fps", on))
        self.add(card(label("Everywhere", "Section"),
                      setting("Sync input", "Mirror taps and keys from the instance you're using to every other "
                                            "running instance. Best when they use the same display setting.", sync),
                      divider(),
                      setting("Show FPS", "Show frames per second in the corner of the screen.", fps)))

        shortcuts = [("F11", "Full screen"), ("Ctrl+Shift+S", "Screenshot"), ("Ctrl+Shift+R", "Record the screen"),
                     ("Ctrl+Shift+K", "Game controls on or off"), ("Ctrl+Shift+E", "Edit game controls"),
                     ("Ctrl+Shift+M", "Record a macro"), ("Ctrl+Shift+O", "Rotate"),
                     ("Ctrl+Shift+W", "Open in its own window"), ("Esc", "Back in Android")]
        lines = [row(label(keys, "Subheading"), label(what, "Muted"), None, spacing=16) for keys, what in shortcuts]
        for line in lines:
            line.layout().itemAt(0).widget().setFixedWidth(140)
        self.add(card(label("Keyboard shortcuts", "Section"), *lines, spacing=6))


class SetupPage(QWidget):
    def __init__(self, host):
        super().__init__()
        self.setObjectName("Page")
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground)
        self.host = host
        self.packages = []
        self.licenses = {}
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        box = QFrame()
        box.setObjectName("Card")
        box.setFixedWidth(480)
        layout.addWidget(box)
        inner = QVBoxLayout(box)
        inner.setContentsMargins(32, 32, 32, 28)
        inner.setSpacing(12)
        inner.addWidget(avatar(ICONS["screen"], COLORS["accent"], 64, glyph=True),
                        alignment=Qt.AlignmentFlag.AlignHCenter)
        self.title = label("Welcome to Androidbox", "Heading")
        self.title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.text = label(f"Androidbox downloads the official Android emulator and {installer.IMAGE_NAME} with "
                          "Google Play, straight from Google.", "Muted", wrap=True)
        self.text.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.detail = label("Checking download size…", "Small")
        self.detail.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.bar = Bar(8)
        self.bar.hide()
        self.action = button("Download and install", self.install, size="large")
        self.action.setEnabled(False)
        self.legal = button("Android SDK License", self.show_license, kind="link")
        self.legal.hide()
        for widget in (self.title, self.text, self.detail, self.bar):
            inner.addWidget(widget)
        inner.addSpacing(8)
        inner.addWidget(self.action)
        inner.addWidget(self.legal, alignment=Qt.AlignmentFlag.AlignHCenter)

    def begin(self, error=None):
        self.bar.hide()
        self.action.setText("Download and install")
        self.action.setEnabled(False)
        self.detail.setText(error or "Checking download size…")
        self.detail.setStyleSheet(f"color: {COLORS['red']};" if error else "")
        self.host.run(installer.resolve, self.ready, self.offline)

    def ready(self, result):
        self.packages, self.licenses = result
        missing = [package for package in self.packages if not package.installed]
        size = sum(package.size for package in missing) / 1e9
        if self.detail.styleSheet() == "":
            self.detail.setText(f"{size:.1f} GB, one-time download. By continuing you accept the license below.")
        self.action.setEnabled(True)
        self.legal.show()

    def offline(self, error):
        self.detail.setText("Couldn't reach Google. Check your internet connection.")
        self.detail.setStyleSheet(f"color: {COLORS['red']};")
        self.action.setText("Try again")
        self.action.setEnabled(True)
        self.action.clicked.disconnect()
        self.action.clicked.connect(self.retry)

    def retry(self):
        self.action.clicked.disconnect()
        self.action.clicked.connect(self.install)
        self.begin()

    def show_license(self):
        modal = Modal(self.host.dialog_parent(), "Android SDK License", width=640)
        terms = QPlainTextEdit("\n\n".join(self.licenses.values()))
        terms.setReadOnly(True)
        terms.setMinimumHeight(380)
        terms.setStyleSheet(f"background: {COLORS['input']}; border: none; border-radius: 8px; padding: 8px;")
        modal.add(terms)
        modal.action("Close")
        modal.open()

    def install(self):
        missing = [package for package in self.packages if not package.installed]
        self.title.setText("Installing Android")
        self.action.hide()
        self.legal.hide()
        self.bar.show()
        self.detail.setStyleSheet("")
        last = [0.0]

        def progress(package, done, total, stage):
            now = time.monotonic()
            if now - last[0] >= 0.1 or done >= total:
                last[0] = now
                self.host.later(lambda: self.show_progress(missing.index(package), len(missing), package.label,
                                                           done, total, stage))

        self.host.run(lambda: installer.install(missing, progress), self.installed, self.failed)

    def show_progress(self, index, count, name, done, total, stage):
        verb = {"download": "Downloading", "verify": "Verifying", "unpack": "Unpacking"}[stage]
        amount = f"  ·  {done / 1e6:,.0f} of {total / 1e6:,.0f} MB" if stage == "download" else ""
        self.text.setText(f"{verb} {name}…")
        self.detail.setText(f"Step {index + 1} of {count}{amount}")
        self.bar.set_fraction(done / max(total, 1))

    def installed(self, _):
        self.host.setup_finished()

    def failed(self, error):
        self.title.setText("Welcome to Androidbox")
        self.action.show()
        self.begin(f"Setup stopped: {error}")


class NoAccelerationPage(QWidget):
    def __init__(self, host):
        super().__init__()
        self.setObjectName("Page")
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground)
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        box = card(avatar(ICONS["info"], COLORS["yellow"], 64, glyph=True),
                   label("Turn on virtualization", "Heading"),
                   label("Android needs Windows Hypervisor Platform. Turn it on in Windows Features, restart your "
                         "PC, then open Androidbox again.", "Muted", wrap=True),
                   button("Open Windows Features", lambda: subprocess.Popen(["OptionalFeatures.exe"]), size="large"),
                   button("Check again", host.check_acceleration, kind="secondary", size="large"))
        box.setFixedWidth(460)
        layout.addWidget(box)
