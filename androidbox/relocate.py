import contextlib
import os
import re
import shutil
import stat
from pathlib import Path

from . import paths

CHUNK = 1 << 22
# Snapshots and locks belong to the folder they were made in, and Android rebuilds them on the next start
SKIPS = {"snapshots", "hardware-qemu.ini.lock", "multiinstance.lock", "hardware-qemu.ini", "emu-launch-params.txt"}
KEPT_IN_DEFAULT = {paths.LOCATION.name, paths.CLEANUP.name}


def skipped(relative):
    return bool(SKIPS.intersection(relative.parts)) or relative.suffix in (".frame", ".lock")


def files_to_move(source):
    return [path for path in source.rglob("*")
            if path.is_file() and path.name not in KEPT_IN_DEFAULT and not skipped(path.relative_to(source))]


def target_for(parent):
    return Path(parent) / "Androidbox" if Path(parent).name.lower() != "androidbox" else Path(parent)


def point_avds_at(target):
    avds = target / "data" / "avd"
    for marker in avds.glob("*.ini"):
        text = marker.read_text(encoding="utf-8")
        folder = avds / f"{marker.stem}.avd"
        marker.write_text(re.sub(r"(?m)^path=.*$", lambda _: f"path={folder}", text), encoding="utf-8")


def move(parent, progress):
    source = paths.HOME
    target = target_for(parent)
    if target == source:
        raise RuntimeError("Androidbox already keeps its files there")
    if target.is_relative_to(source):
        raise RuntimeError("Pick a folder outside the current Androidbox folder")
    if target.exists() and any(child.name not in KEPT_IN_DEFAULT for child in target.iterdir()):
        raise RuntimeError(f"{target} already has files in it. Pick an empty folder")
    files = files_to_move(source)
    total = sum(path.stat().st_size for path in files) or 1
    free = shutil.disk_usage(target.parent if target.parent.exists() else Path(target.anchor)).free
    if free < total * 1.02:
        raise RuntimeError(f"That drive has {free / 1e9:.1f} GB free and Androidbox needs {total / 1e9:.1f} GB")
    done = 0
    try:
        for path in files:
            destination = target / path.relative_to(source)
            destination.parent.mkdir(parents=True, exist_ok=True)
            with open(path, "rb") as reader, open(destination, "wb") as writer:
                while chunk := reader.read(CHUNK):
                    writer.write(chunk)
                    done += len(chunk)
                    progress(done, total)
        point_avds_at(target)
    except BaseException:
        shutil.rmtree(target, ignore_errors=True)
        raise
    paths.DEFAULT_HOME.mkdir(parents=True, exist_ok=True)
    if target == paths.DEFAULT_HOME:
        paths.LOCATION.unlink(missing_ok=True)
    else:
        paths.LOCATION.write_text(str(target), encoding="utf-8")
    paths.CLEANUP.write_text(str(source), encoding="utf-8")
    return target


def writable_then_retry(remove, path, error):
    # The emulator marks some files read-only, which Windows refuses to delete
    with contextlib.suppress(OSError):
        os.chmod(path, stat.S_IWRITE)
        remove(path)


def clean_up_old_location():
    # Runs after the restart, once nothing holds the old folder open
    try:
        old = Path(paths.CLEANUP.read_text(encoding="utf-8").strip())
    except OSError:
        return
    if old == paths.HOME or not old.exists():
        paths.CLEANUP.unlink(missing_ok=True)
        return
    for child in old.iterdir():
        if old == paths.DEFAULT_HOME and child.name in KEPT_IN_DEFAULT:
            continue
        if child.is_dir():
            shutil.rmtree(child, onexc=writable_then_retry)
        else:
            with contextlib.suppress(OSError):
                child.unlink()
    if old != paths.DEFAULT_HOME:
        with contextlib.suppress(OSError):
            old.rmdir()
    paths.CLEANUP.unlink(missing_ok=True)
