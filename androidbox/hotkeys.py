import ctypes
from ctypes import wintypes

from PySide6.QtCore import QAbstractNativeEventFilter, Qt
from PySide6.QtGui import QKeySequence

WM_HOTKEY = 0x0312
NO_REPEAT = 0x4000
FIRST_ID = 0x4A00
MODIFIERS = {Qt.KeyboardModifier.AltModifier: 0x1, Qt.KeyboardModifier.ControlModifier: 0x2,
             Qt.KeyboardModifier.ShiftModifier: 0x4, Qt.KeyboardModifier.MetaModifier: 0x8}
SPECIAL_KEYS = {Qt.Key.Key_Backspace: 0x08, Qt.Key.Key_Tab: 0x09, Qt.Key.Key_Return: 0x0D, Qt.Key.Key_Enter: 0x0D,
                Qt.Key.Key_Escape: 0x1B, Qt.Key.Key_Space: 0x20, Qt.Key.Key_PageUp: 0x21, Qt.Key.Key_PageDown: 0x22,
                Qt.Key.Key_End: 0x23, Qt.Key.Key_Home: 0x24, Qt.Key.Key_Left: 0x25, Qt.Key.Key_Up: 0x26,
                Qt.Key.Key_Right: 0x27, Qt.Key.Key_Down: 0x28, Qt.Key.Key_Insert: 0x2D, Qt.Key.Key_Delete: 0x2E}


def virtual_key(key):
    code = int(key)
    if 0x30 <= code <= 0x39 or 0x41 <= code <= 0x5A:
        return code
    if int(Qt.Key.Key_F1) <= code <= int(Qt.Key.Key_F24):
        return 0x70 + code - int(Qt.Key.Key_F1)
    return SPECIAL_KEYS.get(key, 0)


def parse(text):
    """A shortcut such as Ctrl+Alt+B as Windows' modifiers and virtual key, or None if Windows can't take it"""
    sequence = QKeySequence(text)
    if sequence.isEmpty():
        return None
    combo = sequence[0]
    modifiers = sum(flag for modifier, flag in MODIFIERS.items() if combo.keyboardModifiers() & modifier)
    code = virtual_key(combo.key())
    return (modifiers, code) if code and modifiers else None


class Hotkeys(QAbstractNativeEventFilter):
    """Shortcuts that work while another program has the keyboard"""

    def __init__(self, app):
        super().__init__()
        self.actions = {}
        app.installNativeEventFilter(self)

    def set(self, wanted):
        """Registers {shortcut: callback}, and returns the shortcuts Windows refused, usually because they're taken"""
        for identifier in self.actions:
            ctypes.windll.user32.UnregisterHotKey(None, identifier)
        self.actions = {}
        refused = []
        for number, (text, callback) in enumerate(wanted.items()):
            parsed = parse(text)
            identifier = FIRST_ID + number
            if parsed and ctypes.windll.user32.RegisterHotKey(None, identifier, parsed[0] | NO_REPEAT, parsed[1]):
                self.actions[identifier] = callback
            else:
                refused.append(text)
        return refused

    def nativeEventFilter(self, event_type, message):
        if event_type == b"windows_generic_MSG":
            event = wintypes.MSG.from_address(int(message))
            if event.message == WM_HOTKEY and event.wParam in self.actions:
                self.actions[event.wParam]()
                return True, 0
        return False, 0
