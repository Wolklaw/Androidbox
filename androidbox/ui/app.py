import ctypes
import json
import sys

from PySide6.QtGui import QIcon
from PySide6.QtNetwork import QLocalServer, QLocalSocket
from PySide6.QtWidgets import QApplication, QMessageBox

from .. import paths, system
from .theme import Fonts, stylesheet
from .window import MainWindow

TITLE = "Androidbox"
REQUESTS = "Androidbox-requests"


def parse(arguments):
    # Done by hand: the windowed exe has no console, and argparse reports mistakes by printing to one
    request = {"instance": None, "launch": None, "background": False, "fullscreen": False}
    items = iter(arguments)
    for item in items:
        if item == "--background":
            request["background"] = True
        elif item == "--fullscreen":
            request["fullscreen"] = True
        elif item in ("--instance", "--launch"):
            request[item[2:]] = next(items, None)
    return request


def another_copy_running():
    kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
    kernel32.CreateMutexW(None, False, "Local\\Androidbox")
    return ctypes.get_last_error() == 183


def hand_over(request):
    # The copy that is already running does what this one was asked to, such as opening a game
    socket = QLocalSocket()
    socket.connectToServer(REQUESTS)
    if socket.waitForConnected(2000):
        socket.write(json.dumps(request).encode())
        socket.waitForBytesWritten(2000)
        socket.disconnectFromServer()
        return True
    window = ctypes.windll.user32.FindWindowW(None, TITLE)
    if window:
        ctypes.windll.user32.ShowWindow(window, 9)
        ctypes.windll.user32.SetForegroundWindow(window)
    return False


def listen(window):
    server = QLocalServer()
    server.setSocketOptions(QLocalServer.SocketOption.UserAccessOption)
    QLocalServer.removeServer(REQUESTS)
    server.listen(REQUESTS)

    def received():
        while connection := server.nextPendingConnection():
            connection.waitForReadyRead(500)
            try:
                window.handle_request(json.loads(bytes(connection.readAll()).decode()))
            except ValueError:
                pass
            connection.disconnectFromServer()

    server.newConnection.connect(received)
    return server


def files_missing():
    box = QMessageBox()
    box.setWindowTitle(TITLE)
    box.setIcon(QMessageBox.Icon.Warning)
    box.setText("Androidbox's files aren't there")
    box.setInformativeText(f"Androidbox keeps its files in {paths.HOME}, and that folder isn't available. If it's on a "
                           "drive that's unplugged, connect it and open Androidbox again. Or start fresh in the "
                           "default folder.")
    fresh = box.addButton("Use the default folder", QMessageBox.ButtonRole.AcceptRole)
    box.addButton("Quit", QMessageBox.ButtonRole.RejectRole)
    box.exec()
    if box.clickedButton() is fresh:
        paths.LOCATION.unlink(missing_ok=True)
        system.restart()


def main():
    app = QApplication(sys.argv)
    request = parse(sys.argv[1:])
    if another_copy_running():
        hand_over(request)
        return
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(TITLE)
    app.setApplicationName(TITLE)
    app.setWindowIcon(QIcon(str(paths.ICON)))
    app.setQuitOnLastWindowClosed(False)
    Fonts.load()
    app.setStyleSheet(stylesheet())
    if paths.home_missing():
        files_missing()
        return
    window = MainWindow(background=request["background"], request=request)
    server = listen(window)
    if not (request["background"] and window.tray_active()):
        window.show()
    code = app.exec()
    server.close()
    sys.exit(code)
