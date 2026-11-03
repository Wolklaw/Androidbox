from PySide6.QtCore import QPoint, Qt
from PySide6.QtWidgets import QFrame, QHBoxLayout, QMenu, QScrollArea, QSizePolicy, QVBoxLayout, QWidget

from .theme import COLORS, ICONS
from .widgets import ToolButton

ALWAYS_ON = {"fullscreen", "popout", "game", "more", "inspector"}
# The rest of the tools, in the More menu: label, host method, the state it shows (if it is a switch), and
# whether it needs a running Android
MORE = [
    ("Volume up", "volume_up", None, True), ("Volume down", "volume_down", None, True), None,
    ("Install apps…", "choose_apps", None, False), ("Add files to Downloads…", "choose_files", None, False),
    ("Save files from Android to your PC…", "pull_files", None, True), None,
    ("Set location…", "choose_location", None, True), ("Shake", "shake", None, True), None,
    ("Eco mode: lower FPS and CPU use", "toggle_eco", "eco", False),
    ("Sync input to every running instance", "toggle_sync", "sync", False),
    ("Mute this instance", "toggle_mute", "mute", True),
    ("Keep Androidbox on top of other windows", "toggle_pin", "pin", False), None,
    ("Search everything…    Ctrl+K", "open_palette", None, False),
]


class ToolRail(QWidget):
    def __init__(self, host, horizontal=False):
        super().__init__()
        self.horizontal = horizontal
        self.setObjectName("Dock" if horizontal else "Tools")
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground)
        self.compact = False
        self.buttons = {}
        self.live = False
        self.states = {}
        groups = [
            [("back", "Back", lambda: host.send_key("GoBack")),
             ("home", "Home", lambda: host.send_key("GoHome")),
             ("recents", "Recent apps", lambda: host.send_key("AppSwitch"))],
            [("rotate", "Rotate  (Ctrl+Shift+O)", host.rotate),
             ("fullscreen", "Full screen  (F11)", host.toggle_fullscreen),
             ("popout", "Open in its own window  (Ctrl+Shift+W)", host.toggle_popout, True)],
            [("game", "Game controls on/off  (Ctrl+Shift+K)", host.toggle_game_controls, True),
             ("keyboard", "Edit game controls  (Ctrl+Shift+E)", host.edit_controls, True),
             ("macro", "Record a macro  (Ctrl+Shift+M)", host.toggle_macro, True)],
            [("camera", "Screenshot  (Ctrl+Shift+S)", host.screenshot),
             ("record", "Record the screen  (Ctrl+Shift+R)", host.toggle_video, True)],
            [("info", "Inspector: saved states, automation, network  (Ctrl+I)", host.toggle_inspector, True),
             ("more", "More tools", self.show_more)],
        ]
        column = QWidget()
        layout = QHBoxLayout(column) if horizontal else QVBoxLayout(column)
        layout.setContentsMargins(8, 10, 8, 10)
        layout.setSpacing(2 if horizontal else 4)
        middle = Qt.AlignmentFlag.AlignVCenter if horizontal else Qt.AlignmentFlag.AlignHCenter
        for number, group in enumerate(groups):
            if number:
                line = QFrame()
                line.setFixedSize(*((1, 22) if horizontal else (24, 1)))
                line.setStyleSheet(f"background: {COLORS['line']};")
                layout.addWidget(line, alignment=middle)
            for name, tooltip, action, *checkable in group:
                tool = ToolButton(ICONS[name], tooltip, action, checkable=bool(checkable))
                self.buttons[name] = tool
                layout.addWidget(tool, alignment=middle)
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        if horizontal:
            outer.addWidget(column)
            self.setSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Fixed)
        else:
            layout.addStretch(1)
            scroll = QScrollArea()
            scroll.setWidget(column)
            scroll.setWidgetResizable(True)
            scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
            scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
            outer.addWidget(scroll)
        self.host = host
        self.layout_margins = layout
        self.apply_compact(False)

    def apply_compact(self, compact):
        self.compact = compact
        margin = 4 if compact else 8
        if self.horizontal:
            self.setFixedHeight(44 if compact else 54)
            self.layout_margins.setContentsMargins(10, margin - 2, 10, margin - 2)
        else:
            self.setFixedWidth(40 if compact else 56)
            self.layout_margins.setContentsMargins(margin, 10, margin, 10)
        for tool in self.buttons.values():
            tool.set_compact(compact)

    def refresh(self, controller, prefs, editing):
        if prefs["compact_tools"] != self.compact:
            self.apply_compact(prefs["compact_tools"])
        self.live = controller is not None and controller.on
        for name, tool in self.buttons.items():
            tool.setEnabled(self.live or name in ALWAYS_ON)
        self.states = {
            "popout": self.host.popped,
            "game": prefs["game_controls"],
            "keyboard": editing,
            "macro": bool(controller and controller.recording_macro),
            "record": bool(controller and controller.recording_video),
            "eco": bool(controller and controller.instance.eco),
            "sync": prefs["sync_input"],
            "mute": bool(controller and controller.instance.muted),
            "pin": prefs["always_on_top"],
            "info": prefs["inspector"],
        }
        for name, checked in self.states.items():
            if name in self.buttons:
                self.buttons[name].setChecked(checked)
        self.buttons["record"].setText(ICONS["stop"] if self.states["record"] else ICONS["record"])
        self.buttons["popout"].setToolTip("Put back in the main window  (Ctrl+Shift+W)" if self.host.popped
                                          else "Open in its own window  (Ctrl+Shift+W)")

    def more_menu(self):
        menu = QMenu(self)
        for item in MORE:
            if item is None:
                menu.addSeparator()
                continue
            text, method, state, needs_live = item
            action = menu.addAction(text, getattr(self.host, method))
            action.setEnabled(self.live or not needs_live)
            if state:
                action.setCheckable(True)
                action.setChecked(self.states.get(state, False))
        return menu

    def show_more(self):
        menu = self.more_menu()
        button = self.buttons["more"]
        menu.exec(button.mapToGlobal(QPoint(-menu.sizeHint().width() - 4, button.height() - menu.sizeHint().height())))
