import json

from . import paths

DEFAULTS = {
    "selected": None,
    "game_controls": True,
    "show_hints": True,
    "show_fps": False,
    "sync_input": False,
}


def load():
    try:
        return {**DEFAULTS, **json.loads(paths.SETTINGS.read_text())}
    except (OSError, ValueError):
        return dict(DEFAULTS)


def save(values):
    paths.SETTINGS.parent.mkdir(parents=True, exist_ok=True)
    paths.SETTINGS.write_text(json.dumps(values, indent=2))
