import base64
import json
import threading
import time

from . import paths


def folder(instance):
    return paths.MACROS / instance.id


def load(instance):
    macros = []
    for file in sorted(folder(instance).glob("*.json")):
        try:
            macros.append(json.loads(file.read_text()))
        except (OSError, ValueError):
            continue
    return macros


def next_name(instance):
    taken = {macro["name"] for macro in load(instance)}
    return next(f"Macro {n}" for n in range(1, 1000) if f"Macro {n}" not in taken)


def save(instance, name, recording):
    if not recording:
        return None
    start = recording[0][0]
    macro = {
        "name": name,
        "duration": round(recording[-1][0] - start, 2),
        "events": [[round(at - start, 4), base64.b64encode(payload).decode()] for at, payload in recording],
    }
    folder(instance).mkdir(parents=True, exist_ok=True)
    (folder(instance) / f"{name}.json").write_text(json.dumps(macro))
    return macro


def delete(instance, name):
    (folder(instance) / f"{name}.json").unlink(missing_ok=True)


class Player:
    def __init__(self, bridge, macro, loops=1, on_done=None):
        self.bridge = bridge
        self.events = [(offset, base64.b64decode(payload)) for offset, payload in macro["events"]]
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
