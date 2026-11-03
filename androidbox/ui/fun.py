import random

from PySide6.QtCore import QPointF, QRectF, Qt, QTimer
from PySide6.QtGui import QColor, QPainter
from PySide6.QtWidgets import QWidget


# Up, up, down, down, left, right, left, right, B, A
KONAMI = [Qt.Key.Key_Up, Qt.Key.Key_Up, Qt.Key.Key_Down, Qt.Key.Key_Down, Qt.Key.Key_Left, Qt.Key.Key_Right,
          Qt.Key.Key_Left, Qt.Key.Key_Right, Qt.Key.Key_B, Qt.Key.Key_A]

LOGO_CLICKS = 7
LOGO_QUIPS = [
    "Androidbox: now with 100% more green robot.",
    "You found the logo. It does nothing. It's very proud of that.",
    "Fun fact: this is a phone pretending to be a window pretending to be a phone.",
    "Seven clicks. Your mouse is fine. Your commitment is noted.",
    "No ads were harmed in the making of this app.",
]

# Typed into the Ctrl+K search: phrase, then what it says. A few of them do something as well, below
SECRETS = {
    "xyzzy": "Nothing happens.",
    "sudo": "Nice try. You're already root, in a way that matters to nobody.",
    "42": "The answer. Now, what was the question?",
    "hello there": "General Kenobi. Shall we start Android?",
    "matrix": "There is no spoon, only an emulator.",
    "beep": "Boop.",
    "rickroll": "Never gonna give you up. Never gonna let your instance down.",
    "do a barrel roll": "Hold on.",
    "konami": "+30 lives. Cheat codes work here, never in your games.",
    "confetti": "Congratulations on nothing in particular.",
}
CONFETTI = {"konami", "confetti"}
COLORS_FOR_CONFETTI = ["#3ddc84", "#e8b64c", "#f2766f", "#6ea8fe", "#c792ea", "#5ae497", "#f5f6f7"]


class Confetti(QWidget):
    """Paper falling over the window for a few seconds. It ignores the mouse, so nothing underneath is blocked."""

    def __init__(self, parent, count=110, seconds=3.6):
        super().__init__(parent)
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        self.setAttribute(Qt.WidgetAttribute.WA_NoSystemBackground)
        self.setGeometry(parent.rect())
        width = max(parent.width(), 1)
        self.pieces = [{
            "x": random.uniform(0, width), "y": random.uniform(-parent.height() * 0.6, 0),
            "vx": random.uniform(-1.2, 1.2), "vy": random.uniform(2.5, 6.0), "size": random.uniform(6, 12),
            "turn": random.uniform(0, 360), "spin": random.uniform(-9, 9),
            "color": QColor(random.choice(COLORS_FOR_CONFETTI))} for _ in range(count)]
        self.timer = QTimer(self, interval=16, timeout=self.step)
        self.timer.start()
        QTimer.singleShot(int(seconds * 1000), self.finish)
        self.show()
        self.raise_()

    def step(self):
        for piece in self.pieces:
            piece["x"] += piece["vx"]
            piece["y"] += piece["vy"]
            piece["vx"] += random.uniform(-0.05, 0.05)
            piece["turn"] += piece["spin"]
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setPen(Qt.PenStyle.NoPen)
        for piece in self.pieces:
            if piece["y"] > self.height() + 20:
                continue
            painter.save()
            painter.translate(QPointF(piece["x"], piece["y"]))
            painter.rotate(piece["turn"])
            painter.setBrush(piece["color"])
            size = piece["size"]
            painter.drawRoundedRect(QRectF(-size / 2, -size / 4, size, size / 2), 1.5, 1.5)
            painter.restore()

    def finish(self):
        self.timer.stop()
        self.deleteLater()


def rain(window):
    Confetti(window)


def secret_key(text):
    key = " ".join(text.lower().split())
    return key if key in SECRETS else None
