import ctypes
import warnings
from ctypes import wintypes

DEADZONE = 0.22
TRIGGER = 0.25
RESCAN_TICKS = 60

XINPUT_BUTTONS = {
    0x0001: "Pad Up", 0x0002: "Pad Down", 0x0004: "Pad Left", 0x0008: "Pad Right",
    0x0010: "Pad Start", 0x0020: "Pad Back", 0x0040: "Pad LS", 0x0080: "Pad RS",
    0x0100: "Pad LB", 0x0200: "Pad RB", 0x1000: "Pad A", 0x2000: "Pad B", 0x4000: "Pad X", 0x8000: "Pad Y",
}


def stick(x, y):
    fx, fy = max(-1.0, x / 32767), max(-1.0, y / 32767)
    magnitude = (fx * fx + fy * fy) ** 0.5
    if magnitude < DEADZONE:
        return 0.0, 0.0
    scale = (min(magnitude, 1.0) - DEADZONE) / (1 - DEADZONE) / magnitude
    return fx * scale, fy * scale


def merged(states):
    # Every connected controller counts: buttons add up, and the stick pushed furthest wins
    pressed, left, right = set(), (0.0, 0.0), (0.0, 0.0)
    for buttons, state_left, state_right in states:
        pressed |= buttons
        left = max(left, state_left, key=lambda point: point[0] ** 2 + point[1] ** 2)
        right = max(right, state_right, key=lambda point: point[0] ** 2 + point[1] ** 2)
    return pressed, left, right


class SdlPads:
    def __init__(self):
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            import sdl2
        self.sdl = sdl2
        sdl2.SDL_SetHint(sdl2.SDL_HINT_JOYSTICK_ALLOW_BACKGROUND_EVENTS, b"1")
        if sdl2.SDL_Init(sdl2.SDL_INIT_GAMECONTROLLER) != 0:
            raise OSError("SDL could not start its controller support")
        self.pads = {}
        self.event = sdl2.SDL_Event()
        self.buttons = {
            sdl2.SDL_CONTROLLER_BUTTON_A: "Pad A", sdl2.SDL_CONTROLLER_BUTTON_B: "Pad B",
            sdl2.SDL_CONTROLLER_BUTTON_X: "Pad X", sdl2.SDL_CONTROLLER_BUTTON_Y: "Pad Y",
            sdl2.SDL_CONTROLLER_BUTTON_BACK: "Pad Back", sdl2.SDL_CONTROLLER_BUTTON_START: "Pad Start",
            sdl2.SDL_CONTROLLER_BUTTON_LEFTSTICK: "Pad LS", sdl2.SDL_CONTROLLER_BUTTON_RIGHTSTICK: "Pad RS",
            sdl2.SDL_CONTROLLER_BUTTON_LEFTSHOULDER: "Pad LB", sdl2.SDL_CONTROLLER_BUTTON_RIGHTSHOULDER: "Pad RB",
            sdl2.SDL_CONTROLLER_BUTTON_DPAD_UP: "Pad Up", sdl2.SDL_CONTROLLER_BUTTON_DPAD_DOWN: "Pad Down",
            sdl2.SDL_CONTROLLER_BUTTON_DPAD_LEFT: "Pad Left", sdl2.SDL_CONTROLLER_BUTTON_DPAD_RIGHT: "Pad Right",
        }
        for index in range(sdl2.SDL_NumJoysticks()):
            self.open(index)

    def open(self, index):
        sdl = self.sdl
        if not sdl.SDL_IsGameController(index):
            return
        pad = sdl.SDL_GameControllerOpen(index)
        if not pad:
            return
        identity = sdl.SDL_JoystickInstanceID(sdl.SDL_GameControllerGetJoystick(pad))
        if identity in self.pads:
            sdl.SDL_GameControllerClose(pad)
        else:
            self.pads[identity] = pad

    def unplug(self, identity):
        pad = self.pads.pop(identity, None)
        if pad:
            self.sdl.SDL_GameControllerClose(pad)

    def read(self, pad):
        sdl = self.sdl
        axis = lambda which: sdl.SDL_GameControllerGetAxis(pad, which)
        pressed = {name for button, name in self.buttons.items() if sdl.SDL_GameControllerGetButton(pad, button)}
        if axis(sdl.SDL_CONTROLLER_AXIS_TRIGGERLEFT) / 32767 > TRIGGER:
            pressed.add("Pad LT")
        if axis(sdl.SDL_CONTROLLER_AXIS_TRIGGERRIGHT) / 32767 > TRIGGER:
            pressed.add("Pad RT")
        left = stick(axis(sdl.SDL_CONTROLLER_AXIS_LEFTX), axis(sdl.SDL_CONTROLLER_AXIS_LEFTY))
        right = stick(axis(sdl.SDL_CONTROLLER_AXIS_RIGHTX), axis(sdl.SDL_CONTROLLER_AXIS_RIGHTY))
        return pressed, left, right

    def poll(self):
        sdl = self.sdl
        while sdl.SDL_PollEvent(ctypes.byref(self.event)):
            if self.event.type == sdl.SDL_CONTROLLERDEVICEADDED:
                self.open(self.event.cdevice.which)
            elif self.event.type == sdl.SDL_CONTROLLERDEVICEREMOVED:
                self.unplug(self.event.cdevice.which)
        if not self.pads:
            return None
        return merged(self.read(pad) for pad in self.pads.values())


class XInputPad(ctypes.Structure):
    _fields_ = [("buttons", wintypes.WORD), ("left_trigger", ctypes.c_ubyte), ("right_trigger", ctypes.c_ubyte),
                ("lx", ctypes.c_short), ("ly", ctypes.c_short), ("rx", ctypes.c_short), ("ry", ctypes.c_short)]


class XInputState(ctypes.Structure):
    _fields_ = [("packet", wintypes.DWORD), ("pad", XInputPad)]


class XInputPads:
    def __init__(self):
        self.read = None
        for name in ("xinput1_4", "xinput1_3", "xinput9_1_0"):
            try:
                self.read = ctypes.WinDLL(name).XInputGetState
                break
            except OSError:
                continue
        self.connected = set()
        self.ticks = 0
        self.state = XInputState()

    def scan(self):
        # Asking for a controller that isn't plugged in is slow, so look for new ones only now and then
        self.ticks += 1
        if self.ticks % RESCAN_TICKS == 1:
            self.connected |= {index for index in range(4) if self.read(index, ctypes.byref(self.state)) == 0}

    def poll(self):
        if not self.read:
            return None
        self.scan()
        states = []
        for index in sorted(self.connected):
            if self.read(index, ctypes.byref(self.state)) != 0:
                self.connected.discard(index)
                continue
            pad = self.state.pad
            pressed = {name for bit, name in XINPUT_BUTTONS.items() if pad.buttons & bit}
            if pad.left_trigger / 255 > TRIGGER:
                pressed.add("Pad LT")
            if pad.right_trigger / 255 > TRIGGER:
                pressed.add("Pad RT")
            states.append((pressed, stick(pad.lx, -pad.ly), stick(pad.rx, -pad.ry)))
        return merged(states) if states else None


def open_gamepads():
    try:
        return SdlPads()
    except (ImportError, OSError):
        return XInputPads()
