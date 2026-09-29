from PySide6.QtCore import Qt
from PySide6.QtWidgets import QFrame, QScrollArea, QVBoxLayout, QWidget

from .theme import COLORS, ICONS
from .widgets import ToolButton

ALWAYS_ON = {"fullscreen", "popout", "game", "install", "folder", "eco", "sync"}


class ToolRail(QWidget):
    def __init__(self, host):
        super().__init__()
        self.setObjectName("Tools")
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground)
        self.setFixedWidth(56)
        self.buttons = {}
        groups = [
            [("back", "Back", lambda: host.send_key("GoBack")),
             ("home", "Home", lambda: host.send_key("GoHome")),
             ("recents", "Recent apps", lambda: host.send_key("AppSwitch"))],
            [("volume_up", "Volume up", lambda: host.send_key("AudioVolumeUp")),
             ("volume_down", "Volume down", lambda: host.send_key("AudioVolumeDown"))],
            [("rotate", "Rotate  (Ctrl+Shift+O)", host.rotate),
             ("fullscreen", "Full screen  (F11)", host.toggle_fullscreen),
             ("popout", "Open in its own window  (Ctrl+Shift+W)", host.toggle_popout, True)],
            [("game", "Game controls on/off  (Ctrl+Shift+K)", host.toggle_game_controls, True),
             ("keyboard", "Edit game controls  (Ctrl+Shift+E)", host.edit_controls, True),
             ("macro", "Record a macro  (Ctrl+Shift+M)", host.toggle_macro, True)],
            [("camera", "Screenshot  (Ctrl+Shift+S)", host.screenshot),
             ("record", "Record the screen  (Ctrl+Shift+R)", host.toggle_video, True)],
            [("install", "Install apps", host.choose_apps),
             ("folder", "Add files to Downloads", host.choose_files),
             ("location", "Set location", host.choose_location),
             ("shake", "Shake", host.shake)],
            [("eco", "Eco mode: lower FPS and CPU use", host.toggle_eco, True),
             ("sync", "Sync input to every running instance", host.toggle_sync, True)],
        ]
        column = QWidget()
        layout = QVBoxLayout(column)
        layout.setContentsMargins(8, 10, 8, 10)
        layout.setSpacing(4)
        for number, group in enumerate(groups):
            if number:
                line = QFrame()
                line.setFixedSize(24, 1)
                line.setStyleSheet(f"background: {COLORS['line']};")
                layout.addWidget(line, alignment=Qt.AlignmentFlag.AlignHCenter)
            for name, tooltip, action, *checkable in group:
                tool = ToolButton(ICONS[name], tooltip, action, checkable=bool(checkable))
                self.buttons[name] = tool
                layout.addWidget(tool, alignment=Qt.AlignmentFlag.AlignHCenter)
        layout.addStretch(1)
        scroll = QScrollArea()
        scroll.setWidget(column)
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.addWidget(scroll)
        self.host = host

    def refresh(self, controller, prefs, editing):
        live = controller is not None and controller.on
        for name, tool in self.buttons.items():
            tool.setEnabled(live or name in ALWAYS_ON)
        states = {
            "popout": self.host.popped,
            "game": prefs["game_controls"],
            "keyboard": editing,
            "macro": bool(controller and controller.recording_macro),
            "record": bool(controller and controller.recording_video),
            "eco": bool(controller and controller.instance.eco),
            "sync": prefs["sync_input"],
        }
        for name, checked in states.items():
            self.buttons[name].setChecked(checked)
        self.buttons["record"].setText(ICONS["stop"] if states["record"] else ICONS["record"])
        self.buttons["popout"].setToolTip("Put back in the main window  (Ctrl+Shift+W)" if self.host.popped
                                          else "Open in its own window  (Ctrl+Shift+W)")
