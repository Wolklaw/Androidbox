import ctypes
import sys

from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QApplication

from .. import paths
from .theme import Fonts, stylesheet
from .window import MainWindow

TITLE = "Androidbox"


def focus_running_copy():
    kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
    kernel32.CreateMutexW(None, False, "Local\\Androidbox")
    if ctypes.get_last_error() != 183:
        return False
    window = ctypes.windll.user32.FindWindowW(None, TITLE)
    if window:
        ctypes.windll.user32.ShowWindow(window, 9)
        ctypes.windll.user32.SetForegroundWindow(window)
    return True


def main():
    if focus_running_copy():
        return
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(TITLE)
    app = QApplication(sys.argv)
    app.setApplicationName(TITLE)
    app.setWindowIcon(QIcon(str(paths.ICON)))
    app.setQuitOnLastWindowClosed(False)
    Fonts.load()
    app.setStyleSheet(stylesheet())
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
