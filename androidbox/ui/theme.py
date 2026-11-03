from PySide6.QtGui import QFontDatabase

COLORS = {
    "sidebar": "#10131a",
    "main": "#151921",
    "surface": "#1c212b",
    "raised": "#262c38",
    "hover": "#212733",
    "selected": "#2a3142",
    "input": "#0d1016",
    "line": "#252b38",
    "text": "#e6e9f0",
    "bright": "#fafbfe",
    "muted": "#a7aebd",
    "faint": "#7f8799",
    "dim": "#596073",
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
    "person": "",
    "chevron": "",
    "mute": "",
    "pin": "",
    "download": "",
    "library": "",
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
    #Sidebar, #Tools, #Inspector {{
        background: {c["sidebar"]};
    }}
    #Inspector {{
        border-left: 1px solid {c["line"]};
    }}
    #Header {{
        border-bottom: 1px solid {c["line"]};
    }}
    #Dock {{
        background: {c["raised"]};
        border: 1px solid {c["line"]};
        border-radius: 20px;
    }}
    #Chip {{
        background: {c["surface"]};
        color: {c["muted"]};
        border-radius: 12px;
        padding: 4px 10px;
        font-size: 9pt;
    }}
    #HeaderTitle {{
        color: {c["bright"]};
        font-family: "{Fonts.strong}";
        font-size: 14pt;
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
        font-size: 18pt;
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
        border-radius: 16px;
    }}
    #Divider {{
        background: {c["line"]};
        max-height: 1px;
        min-height: 1px;
    }}
    QPushButton {{
        border: none;
        border-radius: 10px;
        padding: 0 18px;
        min-height: 36px;
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
        background: #323a4b;
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
    QPushButton[kind="chip"] {{
        background: {c["surface"]};
        color: {c["muted"]};
        border-radius: 14px;
        min-height: 28px;
        padding: 0 12px;
    }}
    QPushButton[kind="chip"]:hover {{
        background: {c["raised"]};
        color: {c["bright"]};
    }}
    QPushButton[size="large"] {{
        min-height: 40px;
        padding: 0 24px;
    }}
    QLineEdit, QComboBox, QAbstractSpinBox {{
        background: {c["input"]};
        border: 1px solid {c["line"]};
        border-radius: 10px;
        padding: 0 12px;
        min-height: 36px;
        color: {c["text"]};
        selection-background-color: {c["accent"]};
        selection-color: {c["on_accent"]};
    }}
    QLineEdit:focus, QComboBox:focus, QAbstractSpinBox:focus {{
        border: 1px solid {c["accent"]};
    }}
    QListWidget {{
        background: {c["input"]};
        border: 1px solid {c["line"]};
        border-radius: 8px;
        padding: 4px;
        outline: none;
    }}
    QListWidget::item {{
        padding: 7px 10px;
        border-radius: 6px;
    }}
    QListWidget::item:hover {{
        background: {c["hover"]};
    }}
    QListWidget::item:selected {{
        background: {c["selected"]};
        color: {c["bright"]};
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
        border-radius: 12px;
        padding: 6px;
    }}
    QMenu::item {{
        padding: 8px 16px;
        border-radius: 8px;
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
        border-radius: 18px;
    }}
    """
