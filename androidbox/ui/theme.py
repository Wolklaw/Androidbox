from PySide6.QtGui import QFontDatabase

COLORS = {
    "sidebar": "#17191c",
    "main": "#1d1f23",
    "surface": "#24272b",
    "raised": "#2e3136",
    "hover": "#272a2f",
    "selected": "#2f3338",
    "input": "#141619",
    "line": "#2b2e33",
    "text": "#e4e6e9",
    "bright": "#f5f6f7",
    "muted": "#a3a9b0",
    "faint": "#7b8189",
    "dim": "#5c6269",
    "accent": "#3ddc84",
    "accent_hover": "#5ae497",
    "on_accent": "#0a1f12",
    "green": "#3ddc84",
    "red": "#f2766f",
    "danger": "#d9534c",
    "danger_hover": "#bf433d",
    "yellow": "#e8b64c",
}

ICONS = {
    "back": "",
    "home": "",
    "recents": "",
    "volume_up": "",
    "volume_down": "",
    "rotate": "",
    "camera": "",
    "record": "",
    "stop": "",
    "fullscreen": "",
    "keyboard": "",
    "game": "",
    "location": "",
    "install": "",
    "folder": "",
    "settings": "",
    "power": "",
    "add": "",
    "macro": "",
    "shake": "",
    "eco": "",
    "apps": "",
    "screen": "",
    "info": "",
    "sync": "",
    "more": "",
    "popout": "",
}


class Fonts:
    text = "Segoe UI"
    strong = "Segoe UI Semibold"
    icons = "Segoe MDL2 Assets"

    @classmethod
    def load(cls):
        available = set(QFontDatabase.families())

        def pick(*names):
            return next((name for name in names if name in available), names[-1])

        cls.text = pick("Segoe UI Variable Text", "Segoe UI")
        cls.strong = pick("Segoe UI Semibold", "Segoe UI")
        cls.icons = pick("Segoe Fluent Icons", "Segoe MDL2 Assets")


def stylesheet():
    c = COLORS
    return f"""
    QWidget {{
        color: {c["text"]};
        font-family: "{Fonts.text}";
        font-size: 10pt;
    }}
    QMainWindow, #Main, #Page, QStackedWidget {{
        background: {c["main"]};
    }}
    #Sidebar, #Tools {{
        background: {c["sidebar"]};
    }}
    #Header {{
        border-bottom: 1px solid {c["line"]};
    }}
    #Brand {{
        color: {c["bright"]};
        font-family: "{Fonts.strong}";
        font-size: 12pt;
    }}
    #Title {{
        color: {c["bright"]};
        font-family: "{Fonts.strong}";
        font-size: 11pt;
    }}
    #Heading {{
        color: {c["bright"]};
        font-family: "{Fonts.strong}";
        font-size: 16pt;
    }}
    #Subheading {{
        color: {c["bright"]};
        font-family: "{Fonts.strong}";
        font-size: 10.5pt;
    }}
    #Section {{
        color: {c["faint"]};
        font-family: "{Fonts.strong}";
        font-size: 9pt;
    }}
    #Muted {{
        color: {c["muted"]};
    }}
    #Small {{
        color: {c["faint"]};
        font-size: 9pt;
    }}
    #Card {{
        background: {c["surface"]};
        border-radius: 10px;
    }}
    #Divider {{
        background: {c["line"]};
        max-height: 1px;
        min-height: 1px;
    }}
    QPushButton {{
        border: none;
        border-radius: 8px;
        padding: 0 16px;
        min-height: 34px;
        font-family: "{Fonts.strong}";
        font-size: 10pt;
        color: {c["on_accent"]};
        background: {c["accent"]};
    }}
    QPushButton:hover {{
        background: {c["accent_hover"]};
    }}
    QPushButton:disabled {{
        background: {c["raised"]};
        color: {c["dim"]};
    }}
    QPushButton[kind="secondary"] {{
        background: {c["raised"]};
        color: {c["text"]};
    }}
    QPushButton[kind="secondary"]:hover {{
        background: #383c42;
    }}
    QPushButton[kind="danger"] {{
        background: {c["danger"]};
        color: #ffffff;
    }}
    QPushButton[kind="danger"]:hover {{
        background: {c["danger_hover"]};
    }}
    QPushButton[kind="link"] {{
        background: transparent;
        color: {c["accent"]};
        font-family: "{Fonts.text}";
        padding: 0 8px;
    }}
    QPushButton[kind="link"]:hover {{
        text-decoration: underline;
    }}
    QPushButton[size="large"] {{
        min-height: 40px;
        padding: 0 24px;
    }}
    QLineEdit, QComboBox {{
        background: {c["input"]};
        border: 1px solid {c["line"]};
        border-radius: 8px;
        padding: 0 10px;
        min-height: 34px;
        color: {c["text"]};
        selection-background-color: {c["accent"]};
        selection-color: {c["on_accent"]};
    }}
    QLineEdit:focus, QComboBox:focus {{
        border: 1px solid {c["accent"]};
    }}
    QComboBox::drop-down {{
        border: none;
        width: 24px;
    }}
    QComboBox::down-arrow {{
        image: none;
        width: 0;
    }}
    QComboBox QAbstractItemView {{
        background: {c["surface"]};
        border: 1px solid {c["line"]};
        padding: 4px;
        outline: none;
        selection-background-color: {c["selected"]};
    }}
    QScrollArea, QScrollArea > QWidget > QWidget {{
        background: transparent;
        border: none;
    }}
    QScrollBar:vertical {{
        background: transparent;
        width: 8px;
        margin: 2px;
    }}
    QScrollBar::handle:vertical {{
        background: {c["raised"]};
        border-radius: 4px;
        min-height: 32px;
    }}
    QScrollBar::add-line, QScrollBar::sub-line, QScrollBar::add-page, QScrollBar::sub-page {{
        height: 0;
        background: transparent;
    }}
    QToolTip {{
        background: {c["raised"]};
        color: {c["bright"]};
        border: 1px solid {c["line"]};
        padding: 5px 8px;
        font-size: 9pt;
    }}
    QMenu {{
        background: {c["surface"]};
        border: 1px solid {c["line"]};
        border-radius: 8px;
        padding: 4px;
    }}
    QMenu::item {{
        padding: 7px 14px;
        border-radius: 6px;
        color: {c["text"]};
    }}
    QMenu::item:selected {{
        background: {c["selected"]};
        color: {c["bright"]};
    }}
    QMenu::separator {{
        height: 1px;
        background: {c["line"]};
        margin: 4px 6px;
    }}
    #Toast {{
        background: {c["raised"]};
        color: {c["bright"]};
        border-radius: 8px;
        padding: 10px 16px;
    }}
    #Dialog {{
        background: {c["surface"]};
        border: 1px solid {c["line"]};
        border-radius: 12px;
    }}
    """
