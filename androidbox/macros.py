import base64
import json
import re
import threading
import time

from . import profiles
from .proto import emulator_controller_pb2 as pb

SPEEDS = (0.5, 1.0, 2.0, 4.0)
LOOPS = ((1, "Once"), (2, "2 times"), (5, "5 times"), (10, "10 times"), (25, "25 times"), (50, "50 times"),
         (100, "100 times"), (0, "Until I stop it"))
GAPS = (0.0, 0.3, 1.0, 2.0, 5.0, 10.0, 30.0, 60.0)
TAP_SECONDS = 0.35
TAP_TRAVEL = 40

cache = {}


def file(name):
    return profiles.macro_folder() / f"{name}.json"


def forget():
    cache.clear()


def load():
    folder = profiles.macro_folder()
    if cache.get("folder") != folder:
        macros = []
        for path in sorted(folder.glob("*.json")):
            try:
                macros.append(json.loads(path.read_text()))
            except (OSError, ValueError):
                continue
        cache["folder"] = folder
        cache["all"] = macros
    return cache["all"]


def next_name():
    taken = {macro["name"] for macro in load()}
    return next(f"Macro {n}" for n in range(1, 1000) if f"Macro {n}" not in taken)


def write(macro):
    profiles.write_json(file(macro["name"]), macro, indent=None)
    forget()


def save(name, recording, display):
    if not recording:
        return None
    start = recording[0][0]
    macro = {
        "name": name,
        "duration": round(recording[-1][0] - start, 2),
        "speed": 1.0,
        "hotkey": "",
        "display": list(display),
        "events": [[round(at - start, 4), base64.b64encode(payload).decode()] for at, payload in recording],
    }
    write(macro)
    return macro


def update(current, **changes):
    macro = json.loads(file(current).read_text())
    if "name" in changes:
        changes["name"] = re.sub(r'[\/:*?"<>|]', "", changes["name"]).strip() or current
        if changes["name"] != current and file(changes["name"]).exists():
            raise ValueError(f"A macro called {changes['name']} already exists")
    macro.update(changes)
    write(macro)
    if macro["name"] != current:
        delete(current)
    return macro


def delete(name):
    file(name).unlink(missing_ok=True)
    profiles.stamp()
    forget()


def decode(payload):
    event = pb.InputEvent()
    event.ParseFromString(base64.b64decode(payload))
    return event


def actions(macro):
    """The raw events grouped into what a person did: a tap, a swipe, a hold or a key press"""
    found = []
    touching = set()
    current = None
    keys = {}
    for number, (offset, payload) in enumerate(macro["events"]):
        event = decode(payload)
        kind = event.WhichOneof("type")
        if kind == "touch_event":
            touches = event.touch_event.touches
            if current is None:
                current = {"start": offset, "end": offset, "events": [], "points": []}
                found.append(current)
            current["events"].append(number)
            current["end"] = offset
            for touch in touches:
                current["points"].append((touch.x, touch.y))
                (touching.add if touch.pressure else touching.discard)(touch.identifier)
            if not touching:
                current = None
        elif kind == "key_event":
            key = event.key_event.key or event.key_event.text
            held = keys.get(key)
            if held and event.key_event.eventType == pb.KeyboardEvent.keyup:
                held["events"].append(number)
                held["end"] = offset
                keys.pop(key)
                continue
            action = {"start": offset, "end": offset, "events": [number], "key": key}
            found.append(action)
            if event.key_event.eventType == pb.KeyboardEvent.keydown:
                keys[key] = action
        else:
            found.append({"start": offset, "end": offset, "events": [number], "other": True})
    previous = 0.0
    for action in found:
        action["wait"] = round(max(0.0, action["start"] - previous), 2)
        previous = max(previous, action["end"])
        action["label"] = describe(action)
    return found


def describe(action):
    if "key" in action:
        return f"Key {action['key'] or '?'}"
    if "points" not in action:
        return "Other input"
    points = action["points"]
    (x1, y1), (x2, y2) = points[0], points[-1]
    seconds = action["end"] - action["start"]
    if max(abs(x2 - x1), abs(y2 - y1)) > TAP_TRAVEL:
        return f"Swipe from {x1}, {y1} to {x2}, {y2} in {seconds:.1f}s"
    if seconds >= TAP_SECONDS:
        return f"Hold at {x1}, {y1} for {seconds:.1f}s"
    return f"Tap at {x1}, {y1}"


def finish(macro):
    events = macro["events"]
    macro["duration"] = round(events[-1][0] - events[0][0], 2) if events else 0.0
    return macro


def remove_action(macro, number):
    # Later actions move up by the time this one and the wait before it took, so their own waits stay as they were
    found = actions(macro)
    action = found[number]
    earlier = max((other["end"] for other in found[:number]), default=0.0)
    shift = max(0.0, action["end"] - earlier)
    gone = set(action["events"])
    macro["events"] = [[round(offset - (shift if offset > action["end"] else 0.0), 4), payload]
                       for index, (offset, payload) in enumerate(macro["events"]) if index not in gone]
    return finish(macro)


def set_wait(macro, number, seconds):
    action = actions(macro)[number]
    delta = seconds - action["wait"]
    macro["events"] = [[round(max(0.0, offset + (delta if offset >= action["start"] else 0.0)), 4), payload]
                       for offset, payload in macro["events"]]
    return finish(macro)


class Player:
    def __init__(self, bridge, macro, loops=1, on_done=None):
        self.bridge = bridge
        speed = macro.get("speed") or 1.0
        self.events = [(offset / speed, base64.b64decode(payload)) for offset, payload in macro["events"]]
        self.gap = macro.get("gap", 0.3)
        self.loops = loops
        self.on_done = on_done
        self.stopped = threading.Event()
        threading.Thread(target=self.play, daemon=True).start()

    def play(self):
        played = 0
        while not self.stopped.is_set() and (self.loops == 0 or played < self.loops):
            start = time.monotonic()
            for offset, payload in self.events:
                if self.stopped.wait(max(0.0, start + offset - time.monotonic())):
                    break
                self.bridge.replay(payload)
            played += 1
            self.stopped.wait(self.gap)
        if self.on_done:
            self.on_done()

    def stop(self):
        self.stopped.set()
