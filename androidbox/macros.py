import base64
import json
import re
import threading
import time

from . import profiles

SPEEDS = (0.5, 1.0, 2.0, 4.0)

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


class Player:
    def __init__(self, bridge, macro, loops=1, on_done=None):
        self.bridge = bridge
        speed = macro.get("speed") or 1.0
        self.events = [(offset / speed, base64.b64decode(payload)) for offset, payload in macro["events"]]
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
            self.stopped.wait(0.3)
        if self.on_done:
            self.on_done()

    def stop(self):
        self.stopped.set()
