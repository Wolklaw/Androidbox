from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QVBoxLayout, QWidget

from .. import paths
from .host import ScreenActions
from .pages import ScreenPage
from .widgets import Toast, style_title_bar


class PopoutWindow(QWidget, ScreenActions):
    popped = True

    def __init__(self, main, controller):
        super().__init__()
        self.main = main
        self.controller = controller
        self.setObjectName("Main")
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)
        self.setWindowIcon(QIcon(str(paths.ICON)))
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        self.screen = ScreenPage(self)
        layout.addWidget(self.screen)
        self.toaster = Toast(self)
        self.install_shortcuts()
        instance = controller.instance
        height = 880
        self.resize(round((height - 32) * instance.width / instance.height) + 32 + 56, height)
        self.setMinimumSize(360, 480)
        self.refresh()

    @property
    def prefs(self):
        return self.main.prefs

    def set_pref(self, key, value):
        self.main.set_pref(key, value)

    def active(self):
        return self.controller

    def toast(self, text, tone="text"):
        self.toaster.show_message(text, tone)

    def controls_changed(self):
        self.main.controls_changed()

    def dialog_parent(self):
        return self

    def show_screen(self):
        pass

    def show_page(self, name):
        pass

    def toggle_popout(self):
        self.close()

    def toggle_fullscreen(self):
        if self.isFullScreen():
            self.screen.tools.show()
            self.showNormal()
            return
        self.screen.tools.hide()
        self.showFullScreen()
        self.toast("Press F11 to leave full screen")

    def refresh(self):
        self.setWindowTitle(f"{self.controller.instance.name} · Androidbox")
        self.screen.refresh(self.controller)

    def showEvent(self, event):
        style_title_bar(self)
        if self.screen.phone.controller is not self.controller:
            self.screen.phone.show_controller(self.controller)
        self.refresh()

    def closeEvent(self, event):
        self.screen.phone.show_controller(None)
        self.main.docked(self.controller)
