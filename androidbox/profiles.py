import contextlib
import json
import re
import shutil
import zipfile
from pathlib import Path

from . import paths

DEFAULT = "Default"
SYNC_FOLDER = "Androidbox Profiles"
EXTENSION = ".androidbox-profile"
NAME_LIMIT = 32
PRESET_FIELDS = ("cores", "ram", "width", "height", "density", "fps", "api", "camera", "block_ads", "eco")

cache = {}


def state():
    if "state" not in cache:
        try:
            cache["state"] = json.loads(paths.PROFILE_STATE.read_text())
        except (OSError, ValueError):
            cache["state"] = {}
    return cache["state"]


def remember(**changes):
    state().update(changes)
    paths.PROFILE_STATE.parent.mkdir(parents=True, exist_ok=True)
    paths.PROFILE_STATE.write_text(json.dumps(state(), indent=2))


def read_json(path, default):
    try:
        return json.loads(path.read_text())
    except (OSError, ValueError):
        return default


def write_json(path, value, indent=2):
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f"{path.name}.tmp")
    temporary.write_text(json.dumps(value, indent=indent))
    temporary.replace(path)
    stamp()


def sync_folder():
    return state().get("sync", "")


def syncing():
    folder = sync_folder()
    return bool(folder) and Path(folder).is_dir()


def sync_missing():
    return bool(sync_folder()) and not syncing()


def root():
    return Path(sync_folder()) / SYNC_FOLDER if syncing() else paths.PROFILES


def names():
    base = root()
    if not base.is_dir():
        return []
    return sorted((path.name for path in base.iterdir() if path.is_dir() and not path.name.startswith(".")),
                  key=str.lower)


def active():
    wanted = state().get("profile", DEFAULT)
    found = names()
    match = next((name for name in found if name.lower() == wanted.lower()), None)
    return match or (found[0] if found else DEFAULT)


def folder(name=None):
    return root() / (name or active())


def keymaps():
    return folder() / "keymaps"


def macro_folder():
    return folder() / "macros"


def signature():
    newest, count = 0, 0
    for path in folder().rglob("*.json"):
        with contextlib.suppress(OSError):
            newest = max(newest, path.stat().st_mtime_ns)
            count += 1
    return newest, count


def stamp():
    cache["seen"] = signature()


def changed_outside():
    if not syncing():
        return False
    current = signature()
    if current == cache.get("seen"):
        return False
    cache["seen"] = current
    return True


def clean(name):
    return re.sub(r'[\\/:*?"<>|]', "", name).strip().strip(".").strip()[:NAME_LIMIT].strip()


def taken(name):
    return name.lower() in {existing.lower() for existing in names()}


def unique(name):
    base = clean(name) or "Profile"
    candidate, number = base, 2
    while taken(candidate):
        candidate = f"{base} {number}"
        number += 1
    return candidate


def valid(name, ignoring=None):
    name = clean(name)
    if not name:
        raise ValueError("Give the profile a name")
    if taken(name) and name.lower() != (ignoring or "").lower():
        raise ValueError(f"A profile called {name} already exists")
    return name


def create(name):
    name = valid(name)
    folder(name).mkdir(parents=True)
    return name


def duplicate(source, name):
    name = valid(name)
    shutil.copytree(folder(source), folder(name))
    return name


def rename(old, new):
    new = valid(new, ignoring=old)
    if new == old:
        return old
    was_active = active() == old
    folder(old).rename(folder(new))
    if was_active:
        remember(profile=new)
    return new


def delete(name):
    if len(names()) < 2:
        raise ValueError("Keep at least one profile")
    was_active = active() == name
    shutil.rmtree(folder(name))
    if was_active:
        remember(profile=names()[0])
        stamp()


def activate(name):
    remember(profile=name)
    stamp()


def summary(name):
    base = folder(name)
    return (len(list((base / "keymaps").glob("*.json"))), len(list((base / "macros").glob("*.json"))),
            len(presets(name)))


def presets(name=None):
    entries = read_json(folder(name) / "presets.json", [])
    return [entry for entry in entries if isinstance(entry, dict) and entry.get("name")] \
        if isinstance(entries, list) else []


def save_preset(name, instance):
    name = name.strip()[:NAME_LIMIT].strip()
    if not name:
        raise ValueError("Give the preset a name")
    values = {"name": name, **{key: getattr(instance, key) for key in PRESET_FIELDS}}
    kept = [preset for preset in presets() if preset["name"].lower() != name.lower()]
    write_json(folder() / "presets.json", [*kept, values])
    return name


def delete_preset(name):
    write_json(folder() / "presets.json", [preset for preset in presets() if preset["name"] != name])


def export(name, file):
    base = folder(name)
    with zipfile.ZipFile(file, "w", zipfile.ZIP_DEFLATED) as archive:
        archive.writestr("profile.json", json.dumps({"name": name, "format": 1}))
        for path in base.rglob("*"):
            if path.is_file():
                archive.write(path, f"profile/{path.relative_to(base).as_posix()}")


def import_profile(file):
    try:
        archive = zipfile.ZipFile(file)
    except (zipfile.BadZipFile, OSError):
        raise ValueError("This file isn't an Androidbox profile") from None
    with archive:
        try:
            header = json.loads(archive.read("profile.json"))
            name = unique(str(header.get("name", "")) or Path(file).stem)
        except (KeyError, ValueError, AttributeError):
            raise ValueError("This file isn't an Androidbox profile") from None
        target = folder(name)
        target.mkdir(parents=True)
        base = target.resolve()
        try:
            for member in archive.infolist():
                if not member.filename.startswith("profile/") or member.is_dir():
                    continue
                destination = (base / member.filename[len("profile/"):]).resolve()
                if not destination.is_relative_to(base):
                    raise ValueError("This profile contains unsafe file paths")
                destination.parent.mkdir(parents=True, exist_ok=True)
                destination.write_bytes(archive.read(member))
        except Exception:
            shutil.rmtree(target, ignore_errors=True)
            raise
    return name


def files(base):
    return {path.relative_to(base): path for path in base.rglob("*") if path.is_file()}


def identical(first, second):
    left, right = files(first), files(second)
    return left.keys() == right.keys() and all(left[key].read_bytes() == right[key].read_bytes() for key in left)


def free_name(parent, base):
    candidate, number = base, 2
    while (parent / candidate).exists():
        candidate = f"{base} {number}"
        number += 1
    return parent / candidate


def start_sync(chosen):
    parent = Path(chosen)
    target = parent / SYNC_FOLDER
    target.mkdir(parents=True, exist_ok=True)
    current = active()
    uploaded, found = 0, len([path for path in target.iterdir() if path.is_dir()])
    if paths.PROFILES.is_dir():
        for source in sorted(path for path in paths.PROFILES.iterdir() if path.is_dir()):
            destination = target / source.name
            if destination.exists():
                if not files(source) or identical(source, destination):
                    continue
                destination = free_name(target, f"{source.name} (this PC)")
            shutil.copytree(source, destination)
            uploaded += 1
            if source.name == current:
                current = destination.name
    remember(sync=str(parent), profile=current)
    if not names():
        folder(DEFAULT).mkdir(parents=True)
    stamp()
    return uploaded, found


def stop_sync():
    if syncing():
        staging = paths.PROFILES.with_name("profiles.new")
        shutil.rmtree(staging, ignore_errors=True)
        shutil.copytree(root(), staging, ignore=shutil.ignore_patterns(".*"))
        shutil.rmtree(paths.PROFILES, ignore_errors=True)
        staging.rename(paths.PROFILES)
    remember(sync="")
    stamp()


def migrate():
    base = paths.PROFILES / DEFAULT
    base.mkdir(parents=True, exist_ok=True)
    if paths.LEGACY_KEYMAPS.is_dir():
        shutil.copytree(paths.LEGACY_KEYMAPS, base / "keymaps", dirs_exist_ok=True)
    if paths.LEGACY_MACROS.is_dir():
        owners = {entry.get("id"): entry.get("name", "") for entry in read_json(paths.INSTANCES, [])
                  if isinstance(entry, dict)}
        for source in sorted(path for path in paths.LEGACY_MACROS.iterdir() if path.is_dir()):
            for file in sorted(source.glob("*.json")):
                macro = read_json(file, None)
                if not isinstance(macro, dict) or "name" not in macro:
                    continue
                if (base / "macros" / f"{macro['name']}.json").exists():
                    macro["name"] = f"{macro['name']} ({clean(owners.get(source.name) or '') or source.name})"
                (base / "macros").mkdir(parents=True, exist_ok=True)
                (base / "macros" / f"{macro['name']}.json").write_text(json.dumps(macro))
    saved = read_json(paths.SETTINGS, {})
    shared = {key: saved[key] for key in ("game_controls", "show_hints", "show_fps", "sync_input") if key in saved}
    if shared:
        (base / "settings.json").write_text(json.dumps(shared, indent=2))
    remember(profile=DEFAULT)
    for legacy in (paths.LEGACY_KEYMAPS, paths.LEGACY_MACROS):
        shutil.rmtree(legacy, ignore_errors=True)


def start():
    cache.clear()
    if not paths.PROFILE_STATE.exists():
        migrate()
    if not names():
        folder(DEFAULT).mkdir(parents=True, exist_ok=True)
    remember(profile=active())
    stamp()
