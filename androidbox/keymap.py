import json
import math
from dataclasses import asdict, dataclass, field, fields
from pathlib import Path

from . import paths

FIRST_TOUCH = 10
AIM_REACH = 0.22
DIRECTIONS = [(0, -1), (-1, 0), (0, 1), (1, 0)]
PAD_DIRECTIONS = ["Pad Up", "Pad Left", "Pad Down", "Pad Right"]
SHORT_NAMES = {"Mouse Left": "LMB", "Mouse Right": "RMB"}


@dataclass
class Control:
    kind: str
    x: float
    y: float
    key: str = ""
    keys: list = field(default_factory=lambda: ["W", "A", "S", "D"])
    size: float = 0.12
    speed: float = 1.0
    x2: float = None
    y2: float = None

    def label(self):
        if self.kind == "joystick":
            return " ".join(self.keys)
        return SHORT_NAMES.get(self.key, self.key)

    def end(self):
        return (self.x if self.x2 is None else self.x2), (max(0.0, self.y - 0.2) if self.y2 is None else self.y2)

    def describe(self):
        if self.kind == "joystick":
            return f"Joystick on {'/'.join(self.keys)}, the D-pad and the left stick"
        if self.kind == "aim":
            return f"Aim: {self.key} locks the mouse to look around. The right stick works too"
        if self.kind == "look":
            return f"Look: hold {self.key} and move the mouse to look around"
        if self.kind == "skill":
            return f"Skill: hold {self.key}, point with the mouse, release to cast"
        if self.kind == "turbo":
            return f"Turbo: hold {self.key} to tap rapidly at {self.x:.0%} across, {self.y:.0%} down"
        if self.kind == "swipe":
            return f"Swipe: {self.key} drags along the arrow"
        return f"Tap at {self.x:.0%} across, {self.y:.0%} down"


def profile(package):
    return paths.KEYMAPS / f"{package}.json"


def parse(entries):
    known = {item.name for item in fields(Control)}
    return [Control(**{k: v for k, v in entry.items() if k in known}) for entry in entries]


def load(package):
    try:
        return parse(json.loads(profile(package).read_text()))
    except (OSError, ValueError, TypeError):
        return []


def export(package, file):
    layout = {"package": package, "controls": [asdict(control) for control in load(package)]}
    Path(file).write_text(json.dumps(layout, indent=2))


def import_layout(package, file):
    data = json.loads(Path(file).read_text())
    controls = parse(data["controls"] if isinstance(data, dict) else data)
    save(package, controls)
    return len(controls)


def save(package, controls):
    paths.KEYMAPS.mkdir(parents=True, exist_ok=True)
    kept = [control for control in controls if control.kind == "joystick" or control.key]
    if kept:
        profile(package).write_text(json.dumps([asdict(control) for control in kept], indent=2))
    else:
        profile(package).unlink(missing_ok=True)


class Engine:
    def __init__(self):
        self.use([])

    def use(self, controls):
        self.controls = controls
        self.pressed = {}
        self.analog = {}
        self.touching = {}
        self.aiming = None
        self.cursor = (0.5, 0.5)

    def identifier(self, control):
        return FIRST_TOUCH + self.controls.index(control)

    def touch(self, identifier, u, v, down):
        if down:
            self.touching[identifier] = (u, v)
        else:
            self.touching.pop(identifier, None)
        return identifier, u, v, down

    def aim_control(self):
        return next((control for control in self.controls if control.kind in ("aim", "look")), None)

    def swipes(self, key):
        return [control for control in self.controls if control.kind == "swipe" and control.key == key]

    def pulse(self):
        touches = []
        for control in self.controls:
            identifier = self.identifier(control)
            if control.kind == "turbo" and identifier in self.pressed:
                touches.append(self.touch(identifier, control.x, control.y, identifier not in self.touching))
        return touches

    def handles(self, key):
        for control in self.controls:
            if control.kind == "joystick" and (key in control.keys or key in PAD_DIRECTIONS):
                return True
            if control.kind != "joystick" and control.key == key:
                return True
        return False

    def press(self, key, down, width, height):
        touches = []
        for control in self.controls:
            identifier = self.identifier(control)
            if control.kind == "tap" and control.key == key:
                touches.append(self.touch(identifier, control.x, control.y, down))
            elif control.kind == "turbo" and control.key == key:
                if down:
                    self.pressed[identifier] = {key}
                    touches.append(self.touch(identifier, control.x, control.y, True))
                else:
                    self.pressed.pop(identifier, None)
                    if identifier in self.touching:
                        touches.append(self.touch(identifier, control.x, control.y, False))
            elif control.kind == "skill" and control.key == key:
                touches.extend(self.cast(control, down, width, height))
            elif control.kind == "joystick" and (key in control.keys or key in PAD_DIRECTIONS):
                held = self.pressed.setdefault(identifier, set())
                if down:
                    held.add(key)
                else:
                    held.discard(key)
                touches.extend(self.steer(control, width, height))
        return touches

    def stick(self, x, y, width, height):
        for control in self.controls:
            if control.kind == "joystick":
                self.analog[self.identifier(control)] = (x, y)
                return self.steer(control, width, height)
        return []

    def steer(self, control, width, height):
        identifier = self.identifier(control)
        held = self.pressed.get(identifier, set())
        dx = dy = 0.0
        for index, (step_x, step_y) in enumerate(DIRECTIONS):
            if control.keys[index] in held or PAD_DIRECTIONS[index] in held:
                dx += step_x
                dy += step_y
        if not dx and not dy:
            dx, dy = self.analog.get(identifier, (0.0, 0.0))
        active = identifier in self.touching
        length = math.hypot(dx, dy)
        if length < 0.05:
            return [self.touch(identifier, control.x, control.y, False)] if active else []
        scale = min(length, 1.0) / length
        reach = control.size * min(width, height)
        target = (control.x + dx * scale * reach / width, control.y + dy * scale * reach / height)
        start = [] if active else [self.touch(identifier, control.x, control.y, True)]
        return start + [self.touch(identifier, *target, True)]

    def cast(self, control, down, width, height):
        identifier = self.identifier(control)
        if not down:
            u, v = self.touching.get(identifier, (control.x, control.y))
            return [self.touch(identifier, u, v, False)]
        return [self.touch(identifier, control.x, control.y, True),
                self.touch(identifier, *self.skill_target(control, width, height), True)]

    def skill_target(self, control, width, height):
        dx = (self.cursor[0] - 0.5) * width
        dy = (self.cursor[1] - 0.5) * height
        length = math.hypot(dx, dy)
        if length < 8:
            return control.x, control.y
        reach = control.size * min(width, height)
        return control.x + dx / length * reach / width, control.y + dy / length * reach / height

    def point(self, u, v, width, height):
        self.cursor = (u, v)
        return [self.touch(self.identifier(control), *self.skill_target(control, width, height), True)
                for control in self.controls
                if control.kind == "skill" and self.identifier(control) in self.touching]

    def look(self, dx, dy, width, height):
        control = self.aim_control()
        if not control:
            return []
        identifier = self.identifier(control)
        touches = []
        if self.aiming is None:
            self.aiming = (0.0, 0.0)
            touches.append(self.touch(identifier, control.x, control.y, True))
        offset_x = self.aiming[0] + dx * control.speed / width
        offset_y = self.aiming[1] + dy * control.speed / height
        if math.hypot(offset_x * width, offset_y * height) > AIM_REACH * min(width, height):
            touches.append(self.touch(identifier, control.x + self.aiming[0], control.y + self.aiming[1], False))
            touches.append(self.touch(identifier, control.x, control.y, True))
            offset_x, offset_y = dx * control.speed / width, dy * control.speed / height
        self.aiming = (offset_x, offset_y)
        touches.append(self.touch(identifier, control.x + offset_x, control.y + offset_y, True))
        return touches

    def stop_looking(self):
        control = self.aim_control()
        self.aiming = None
        if not control or self.identifier(control) not in self.touching:
            return []
        return [self.touch(self.identifier(control), *self.touching[self.identifier(control)], False)]

    def release_all(self):
        touches = [(identifier, u, v, False) for identifier, (u, v) in self.touching.items()]
        self.pressed = {}
        self.analog = {}
        self.touching = {}
        self.aiming = None
        return touches
