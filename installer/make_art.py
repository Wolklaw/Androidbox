"""Draws the artwork for the Androidbox setup wizard into this folder.

    python installer/make_art.py

The PNGs it writes are committed, so setup.iss compiles without running this.
"""
import sys
from pathlib import Path

from PySide6.QtCore import QPointF, QRectF, Qt
from PySide6.QtGui import (QColor, QFont, QGuiApplication, QIcon, QImage, QLinearGradient, QPainter, QPainterPath, QPen,
                           QRadialGradient)

HERE = Path(__file__).resolve().parent
ICON = HERE.parent / "assets" / "androidbox.ico"

ACCENT = QColor("#3ddc84")
TOP, BOTTOM = QColor("#1f2227"), QColor("#121417")
WIDTH, HEIGHT = 164, 314  # the wizard image keeps this ratio at every DPI; everything below is in these units
WELCOME_WIDTHS = (202, 336, 534)
ICON_SIZES = (58, 77, 97, 124, 159)


def alpha(color, value):
    result = QColor(color)
    result.setAlpha(value)
    return result


def stroke(painter, color, width):
    pen = QPen(color, width)
    pen.setCapStyle(Qt.PenCapStyle.RoundCap)
    pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
    painter.setPen(pen)


def background(painter):
    fill = QLinearGradient(0, 0, 0, HEIGHT)
    fill.setColorAt(0, TOP)
    fill.setColorAt(1, BOTTOM)
    painter.fillRect(QRectF(0, 0, WIDTH, HEIGHT), fill)
    glow = QRadialGradient(QPointF(86, 128), 118)
    glow.setColorAt(0, alpha(ACCENT, 46))
    glow.setColorAt(1, alpha(ACCENT, 0))
    painter.fillRect(QRectF(0, 0, WIDTH, HEIGHT), glow)
    painter.setPen(Qt.PenStyle.NoPen)
    painter.setBrush(alpha("#ffffff", 14))
    for x in range(8, WIDTH, 10):
        for y in range(8, HEIGHT, 10):
            painter.drawEllipse(QPointF(x, y), 0.55, 0.55)


def monitor(painter):
    window = QRectF(16, 64, 132, 96)
    painter.setBrush(QColor("#1a1c20"))
    stroke(painter, QColor("#30343a"), 1.2)
    painter.drawRoundedRect(window, 8, 8)
    stroke(painter, ACCENT, 1.5)
    painter.drawPath(corner(window))
    stroke(painter, QColor("#6b7178"), 1)
    painter.drawLine(QPointF(118, 74), QPointF(123, 74))
    painter.drawRect(QRectF(128, 71.5, 5, 5))
    painter.drawLine(QPointF(138, 71.5), QPointF(143, 76.5))
    painter.drawLine(QPointF(143, 71.5), QPointF(138, 76.5))
    robot(painter, window)


def corner(window):
    path = QPainterPath()
    path.moveTo(window.left(), window.top() + 38)
    path.lineTo(window.left(), window.top() + 8)
    path.quadTo(window.left(), window.top(), window.left() + 8, window.top())
    path.lineTo(window.left() + 62, window.top())
    return path


def robot(painter, window):
    painter.save()
    painter.setClipRect(window.adjusted(1, 1, -1, -1))
    painter.setPen(Qt.PenStyle.NoPen)
    painter.setBrush(alpha(ACCENT, 78))
    painter.drawEllipse(QPointF(46, window.bottom()), 23, 23)
    painter.setBrush(QColor("#1a1c20"))
    painter.drawEllipse(QPointF(38, window.bottom() - 10), 2.4, 2.4)
    painter.drawEllipse(QPointF(54, window.bottom() - 10), 2.4, 2.4)
    stroke(painter, alpha(ACCENT, 78), 2)
    painter.drawLine(QPointF(35, window.bottom() - 20), QPointF(30, window.bottom() - 28))
    painter.drawLine(QPointF(57, window.bottom() - 20), QPointF(62, window.bottom() - 28))
    painter.restore()


def phone(painter):
    body = QRectF(78, 98, 62, 126)
    fill = QLinearGradient(0, body.top(), 0, body.bottom())
    fill.setColorAt(0, QColor("#1d2024"))
    fill.setColorAt(1, QColor("#15171a"))
    painter.setBrush(fill)
    stroke(painter, QColor("#41464d"), 1.8)
    painter.drawRoundedRect(body, 11, 11)
    painter.setBrush(Qt.BrushStyle.NoBrush)
    stroke(painter, QColor("#555b63"), 1)
    painter.drawEllipse(QPointF(body.center().x(), body.top() + 8), 1.5, 1.5)
    painter.setPen(Qt.PenStyle.NoPen)
    for row in range(4):
        for column in range(3):
            tile = QRectF(body.left() + 8 + column * 17, body.top() + 20 + row * 17, 12, 12)
            painter.setBrush(alpha(ACCENT, 235) if (row, column) == (1, 1) else QColor("#2a2d32"))
            painter.drawRoundedRect(tile, 3, 3)
    painter.setBrush(Qt.BrushStyle.NoBrush)
    stroke(painter, ACCENT, 1.3)
    nav = body.bottom() - 11
    triangle = QPainterPath()
    triangle.moveTo(body.left() + 18, nav - 3)
    triangle.lineTo(body.left() + 14, nav)
    triangle.lineTo(body.left() + 18, nav + 3)
    painter.drawPath(triangle)
    painter.drawEllipse(QPointF(body.center().x(), nav), 3, 3)
    painter.drawRect(QRectF(body.right() - 18, nav - 2.8, 5.6, 5.6))
    painter.setPen(Qt.PenStyle.NoPen)
    painter.setBrush(ACCENT)
    painter.drawRoundedRect(QRectF(body.right() - 0.6, 138, 2, 18), 1, 1)


def words(painter):
    heading = QFont("Segoe UI Semibold")
    heading.setPixelSize(22)
    painter.setFont(heading)
    painter.setPen(QColor("#f5f6f7"))
    painter.drawText(QPointF(14, 262), "Androidbox")
    body = QFont("Segoe UI")
    body.setPixelSize(10)
    painter.setFont(body)
    painter.setPen(QColor("#a3a9b0"))
    painter.drawText(QPointF(14, 280), "Android on your PC.")
    painter.setPen(ACCENT)
    painter.drawText(QPointF(14, 294), "No ads.")
    stroke(painter, alpha(ACCENT, 140), 1)
    painter.drawLine(QPointF(14, 304), QPointF(150, 304))


def welcome(width):
    height = round(width * HEIGHT / WIDTH)
    image = QImage(width, height, QImage.Format.Format_ARGB32_Premultiplied)
    image.fill(Qt.GlobalColor.transparent)
    painter = QPainter(image)
    painter.setRenderHints(QPainter.RenderHint.Antialiasing | QPainter.RenderHint.TextAntialiasing
                           | QPainter.RenderHint.SmoothPixmapTransform)
    painter.scale(width / WIDTH, height / HEIGHT)
    background(painter)
    monitor(painter)
    phone(painter)
    words(painter)
    painter.end()
    return image


def badge(size):
    image = QImage(size, size, QImage.Format.Format_ARGB32_Premultiplied)
    image.fill(Qt.GlobalColor.transparent)
    painter = QPainter(image)
    painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
    painter.drawPixmap(0, 0, QIcon(str(ICON)).pixmap(size, size))
    painter.end()
    return image


def main():
    app = QGuiApplication(sys.argv)
    for width in WELCOME_WIDTHS:
        welcome(width).save(str(HERE / f"welcome-{width}.png"))
    for size in ICON_SIZES:
        badge(size).save(str(HERE / f"badge-{size}.png"))
    del app


if __name__ == "__main__":
    main()
