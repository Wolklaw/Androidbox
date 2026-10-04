import json

from . import paths, profiles

LOCAL = {
    "selected": None,
    "check_updates": True,
    "skipped_version": "",
    "claude_access": False,
}

PROFILE = {
    "game_controls": True,
    "show_hints": True,
    "show_fps": False,
    "sync_input": False,
}


def profile_file():
    return profiles.folder() / "settings.json"


def read(path):
    values = profiles.read_json(path, {})
    return values if isinstance(values, dict) else {}


def load():
    local, shared = read(paths.SETTINGS), read(profile_file())
    return {**LOCAL, **PROFILE,
            **{key: value for key, value in local.items() if key in LOCAL},
            **{key: value for key, value in shared.items() if key in PROFILE}}


def save(values, key):
    if key in PROFILE:
        profiles.write_json(profile_file(), {name: values[name] for name in PROFILE})
    else:
        paths.SETTINGS.parent.mkdir(parents=True, exist_ok=True)
        paths.SETTINGS.write_text(json.dumps({name: values[name] for name in LOCAL}, indent=2))
