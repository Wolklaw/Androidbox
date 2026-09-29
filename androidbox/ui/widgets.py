import ctypes

from PySide6.QtCore import QRectF, QSize, Qt, QTimer, QVariantAnimation, Signal
from PySide6.QtGui import QColor, QFont, QPainter
from PySide6.QtWidgets import (QAbstractButton, QFrame, QGraphicsOpacityEffect, QHBoxLayout, QLabel, QPushButton,
                               QSizePolicy, QToolButton, QVBoxLayout, QWidget)

from .theme import COLORS, Fonts

STATUS_COLORS = {"on": COLORS["green"], "booting": COLORS["yellow"], "stopping": COLORS["yellow"],
                 "crashed": COLORS["red"]}


def style_title_bar(window):
    handle = int(window.winId())
    color = QColor(COLORS["sidebar"])
    for attribute, value in ((20, 1), (35, color.red() | color.green() << 8 | color.blue() << 16)):
        data = ctypes.c_int(value)
        ctypes.windll.dwmapi.DwmSetWindowAttribute(handle, attribute, ctypes.byref(data), ctypes.sizeof(data))


def icon_font(size):
    font = QFont(Fonts.icons)
    font.setPixelSize(size)
    return font


def text_font(size, strong=False):
    font = QFont(Fonts.strong if strong else Fonts.text)
    font.setPixelSize(size)
    return font


def glyph_css(size):
    return f'font-family: "{Fonts.icons}"; font-size: {size}px;'


def avatar(text, color, size=40, glyph=False):
    badge = QLabel(text)
    badge.setFixedSize(size, size)
    badge.setAlignment(Qt.AlignmentFlag.AlignCenter)
    badge.setProperty("glyph", glyph)
    recolor(badge, color)
    return badge


def recolor(badge, color, ink=None):
    size = badge.width()
    font = glyph_css(size // 2) if badge.property("glyph") else \
        f'font-family: "{Fonts.strong}"; font-size: {size * 2 // 5}px;'
    ink = ink or (COLORS["on_accent"] if color == COLORS["accent"] else COLORS["bright"])
    badge.setStyleSheet(f"background: {color}; color: {ink}; border-radius: {size // 4}px; {font}")


def label(text="", name=None, wrap=False):
    widget = QLabel(text)
    if name:
        widget.setObjectName(name)
    widget.setWordWrap(wrap)
    return widget


def button(text, on_click=None, kind=None, size=None):
    widget = QPushButton(text)
    widget.setCursor(Qt.CursorShape.PointingHandCursor)
    if kind:
        widget.setProperty("kind", kind)
    if size:
        widget.setProperty("size", size)
    if on_click:
        widget.clicked.connect(on_click)
    return widget


def divider():
    line = QFrame()
    line.setObjectName("Divider")
    return line


def row(*widgets, spacing=8, margins=(0, 0, 0, 0)):
    container = QWidget()
    layout = QHBoxLayout(container)
    layout.setContentsMargins(*margins)
    layout.setSpacing(spacing)
    for widget in widgets:
        if widget is None:
            layout.addStretch(1)
        else:
            layout.addWidget(widget)
    return container


def column(*widgets, spacing=8, margins=(0, 0, 0, 0)):
    container = QWidget()
    layout = QVBoxLayout(container)
    layout.setContentsMargins(*margins)
    layout.setSpacing(spacing)
    for widget in widgets:
        if widget is None:
            layout.addStretch(1)
        else:
            layout.addWidget(widget)
    return container


class SidebarButton(QAbstractButton):
    def __init__(self, text):
        super().__init__()
        self.setText(text)
        self.setCheckable(True)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.hovered = False

    def enterEvent(self, event):
        self.hovered = True
        self.update()

    def leaveEvent(self, event):
        self.hovered = False
        self.update()

    def paint_background(self, painter):
        if self.isChecked() or self.hovered:
            painter.setBrush(QColor(COLORS["selected" if self.isChecked() else "hover"]))
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawRoundedRect(QRectF(self.rect()), 8, 8)

    def ink(self):
        return QColor(COLORS["bright"] if self.isChecked() else COLORS["text"] if self.hovered else COLORS["muted"])


class NavButton(SidebarButton):
    def __init__(self, glyph, text):
        super().__init__(text)
        self.setFixedHeight(36)
        self.glyph = glyph

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.paint_background(painter)
        painter.setPen(QColor(COLORS["accent"]) if self.isChecked() else self.ink())
        painter.setFont(icon_font(16))
        painter.drawText(QRectF(10, 0, 22, self.height()), Qt.AlignmentFlag.AlignCenter, self.glyph)
        painter.setPen(self.ink())
        painter.setFont(text_font(14, strong=self.isChecked()))
        painter.drawText(QRectF(42, 0, self.width() - 46, self.height()),
                         Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft, self.text())


class InstanceButton(SidebarButton):
    def __init__(self, instance):
        super().__init__(instance.name)
        self.setFixedHeight(44)
        self.instance = instance
        self.state = "off"

    def set_state(self, state):
        self.state = state
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.paint_background(painter)
        tile = QRectF(8, 8, 28, 28)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QColor(COLORS["accent"] if self.isChecked() else COLORS["raised"]))
        painter.drawRoundedRect(tile, 7, 7)
        painter.setPen(QColor(COLORS["on_accent"] if self.isChecked() else COLORS["text"]))
        painter.setFont(text_font(12, strong=True))
        painter.drawText(tile, Qt.AlignmentFlag.AlignCenter, self.instance.initials)
        painter.setPen(self.ink())
        painter.setFont(text_font(14, strong=self.isChecked()))
        painter.drawText(QRectF(46, 0, self.width() - 72, self.height()),
                         Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft,
                         painter.fontMetrics().elidedText(self.instance.name, Qt.TextElideMode.ElideRight,
                                                          self.width() - 76))
        color = STATUS_COLORS.get(self.state)
        if color:
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(QColor(color))
            painter.drawEllipse(QRectF(self.width() - 20, self.height() / 2 - 4, 8, 8))


class Toggle(QAbstractButton):
    def __init__(self, checked=False):
        super().__init__()
        self.setCheckable(True)
        self.setChecked(checked)
        self.setFixedSize(40, 22)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.position = 1.0 if checked else 0.0
        self.animation = QVariantAnimation(self, duration=120)
        self.animation.valueChanged.connect(self.move_knob)
        self.toggled.connect(self.slide)

    def move_knob(self, value):
        self.position = value
        self.update()

    def slide(self, checked):
        self.animation.stop()
        self.animation.setStartValue(self.position)
        self.animation.setEndValue(1.0 if checked else 0.0)
        self.animation.start()

    def sizeHint(self):
        return QSize(40, 22)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QColor(COLORS["accent"] if self.isChecked() else COLORS["raised"]))
        painter.drawRoundedRect(QRectF(0, 0, 40, 22), 11, 11)
        painter.setBrush(QColor(COLORS["on_accent"] if self.isChecked() else COLORS["muted"]))
        painter.drawEllipse(QRectF(4 + 18 * self.position, 4, 14, 14))


class ToolButton(QToolButton):
    def __init__(self, glyph, tooltip, on_click=None, checkable=False):
        super().__init__()
        self.setText(glyph)
        self.setToolTip(tooltip)
        self.setCheckable(checkable)
        self.setFixedSize(40, 40)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setStyleSheet(f"""
            QToolButton {{ border: none; border-radius: 8px; color: {COLORS["muted"]}; background: transparent;
                           {glyph_css(17)} }}
            QToolButton:hover {{ background: {COLORS["hover"]}; color: {COLORS["bright"]}; }}
            QToolButton:checked {{ background: {COLORS["selected"]}; color: {COLORS["accent"]}; }}
            QToolButton:disabled {{ color: {COLORS["dim"]}; }}
        """)
        if on_click:
            self.clicked.connect(on_click)


class Toast(QLabel):
    def __init__(self, parent):
        super().__init__(parent)
        self.setObjectName("Toast")
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        self.opacity = QGraphicsOpacityEffect(self)
        self.setGraphicsEffect(self.opacity)
        self.fade = QVariantAnimation(self, duration=200)
        self.fade.valueChanged.connect(self.opacity.setOpacity)
        self.fade.finished.connect(lambda: self.opacity.opacity() == 0 and self.hide())
        self.timer = QTimer(self, singleShot=True, timeout=self.fade_out)
        self.hide()

    def show_message(self, text, tone="text", seconds=3.5):
        self.setText(text)
        color = {"good": COLORS["green"], "bad": COLORS["red"]}.get(tone)
        self.setStyleSheet(f"border-left: 3px solid {color};" if color else "")
        self.adjustSize()
        parent = self.parentWidget()
        self.move((parent.width() - self.width()) // 2, parent.height() - self.height() - 24)
        self.raise_()
        self.show()
        self.fade.stop()
        self.fade.setStartValue(self.opacity.opacity())
        self.fade.setEndValue(1.0)
        self.fade.start()
        self.timer.start(int(seconds * 1000))

    def fade_out(self):
        self.fade.stop()
        self.fade.setStartValue(1.0)
        self.fade.setEndValue(0.0)
        self.fade.start()


class Modal(QWidget):
    closed = Signal()

    def __init__(self, parent, title, body=None, width=440):
        super().__init__(parent)
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground)
        self.setStyleSheet("Modal { background: rgba(0, 0, 0, 150); }")
        self.setGeometry(parent.rect())
        outer = QVBoxLayout(self)
        outer.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.card = QFrame()
        self.card.setObjectName("Dialog")
        self.card.setFixedWidth(width)
        outer.addWidget(self.card)
        self.body = QVBoxLayout(self.card)
        self.body.setContentsMargins(20, 20, 20, 16)
        self.body.setSpacing(10)
        self.body.addWidget(label(title, "Heading"))
        if body:
            self.body.addWidget(label(body, "Muted", wrap=True))
        self.footer = QHBoxLayout()
        self.footer.setSpacing(8)
        self.footer.addStretch(1)
        self.footer_added = False
        parent.installEventFilter(self)

    def eventFilter(self, watched, event):
        if event.type() == event.Type.Resize:
            self.setGeometry(watched.rect())
        return False

    def add(self, widget):
        self.body.addWidget(widget)
        return widget

    def action(self, text, on_click=None, kind=None):
        if not self.footer_added:
            self.body.addSpacing(8)
            self.body.addLayout(self.footer)
            self.footer_added = True
        widget = button(text, kind=kind)

        def clicked():
            if on_click and on_click() is False:
                return
            self.close_modal()

        widget.clicked.connect(clicked)
        self.footer.addWidget(widget)
        return widget

    def cancel(self, text="Cancel"):
        return self.action(text, kind="secondary")

    def open(self):
        self.show()
        self.raise_()
        self.setFocus()
        return self

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Escape:
            self.close_modal()

    def mousePressEvent(self, event):
        if not self.card.geometry().contains(event.position().toPoint()):
            self.close_modal()

    def close_modal(self):
        self.parentWidget().removeEventFilter(self)
        self.closed.emit()
        self.deleteLater()


def confirm(parent, title, text, action, on_confirm, danger=False):
    modal = Modal(parent, title, text)
    modal.cancel()
    modal.action(action, on_confirm, kind="danger" if danger else None)
    return modal.open()
