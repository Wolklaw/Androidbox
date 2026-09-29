import ctypes
from ctypes import wintypes

BUTTONS = {
    0x0001: "Pad Up", 0x0002: "Pad Down", 0x0004: "Pad Left", 0x0008: "Pad Right",
    0x0010: "Pad Start", 0x0020: "Pad Back", 0x0040: "Pad LS", 0x0080: "Pad RS",
    0x0100: "Pad LB", 0x0200: "Pad RB", 0x1000: "Pad A", 0x2000: "Pad B", 0x4000: "Pad X", 0x8000: "Pad Y",
}
DEADZONE = 0.22
TRIGGER = 60
RESCAN_TICKS = 60


class Pad(ctypes.Structure):
    _fields_ = [("buttons", wintypes.WORD), ("left_trigger", ctypes.c_ubyte), ("right_trigger", ctypes.c_ubyte),
                ("lx", ctypes.c_short), ("ly", ctypes.c_short), ("rx", ctypes.c_short), ("ry", ctypes.c_short)]


class State(ctypes.Structure):
    _fields_ = [("packet", wintypes.DWORD), ("pad", Pad)]


def load_xinput():
    for name in ("xinput1_4", "xinput1_3", "xinput9_1_0"):
        try:
            return ctypes.WinDLL(name).XInputGetState
        except OSError:
            continue
    return None


def axis(x, y):
    fx, fy = max(-1.0, x / 32767), max(-1.0, -y / 32767)
    magnitude = (fx * fx + fy * fy) ** 0.5
    if magnitude < DEADZONE:
        return 0.0, 0.0
    scale = (min(magnitude, 1.0) - DEADZONE) / (1 - DEADZONE) / magnitude
    return fx * scale, fy * scale


class Gamepads:
    def __init__(self):
        self.read = load_xinput()
        self.index = None
        self.ticks = 0
        self.state = State()

    def poll(self):
        if not self.read:
            return None
        if self.index is None:
            self.ticks += 1
            if self.ticks % RESCAN_TICKS != 1:
                return None
            self.index = next((i for i in range(4) if self.read(i, ctypes.byref(self.state)) == 0), None)
            if self.index is None:
                return None
        if self.read(self.index, ctypes.byref(self.state)) != 0:
            self.index = None
            return None
        pad = self.state.pad
        pressed = {name for bit, name in BUTTONS.items() if pad.buttons & bit}
        if pad.left_trigger > TRIGGER:
            pressed.add("Pad LT")
        if pad.right_trigger > TRIGGER:
            pressed.add("Pad RT")
        return pressed, axis(pad.lx, pad.ly), axis(pad.rx, pad.ry)
