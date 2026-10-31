import contextlib
import json
import os
import shutil
import stat
import time
import uuid
import zipfile
from dataclasses import asdict, dataclass, fields
from pathlib import Path

from . import installer, paths

CONSOLE_PORTS = [5580, 5582, 5584, 5578, 5576, 5574, 5572, 5570, 5568, 5566, 5564, 5562, 5560, 5558, 5556, 5554]
GRPC_BASE = 8554
FRAME_RATES = (60, 90, 120, 144, 240)
DISK_SIZES = (16, 32, 64, 128)
# What the emulator's -gpu option takes. Hardware is the fast one, the others are there for GPUs that crash it
GPU_MODES = {"host": "Graphics card", "auto": "Automatic", "swangle": "Software (slow)"}
DEFAULT_GPU = "host"
BACKUP_SKIPS = {"snapshots", "hardware-qemu.ini.lock", "multiinstance.lock", "hardware-qemu.ini",
                "emu-launch-params.txt"}
CHUNK = 1 << 22

RESOLUTIONS = {
    "Phone": (1080, 1920, 420),
    "Phone (light)": (720, 1280, 320),
    "Phone (tall)": (1080, 2400, 420),
    "Tablet": (1920, 1080, 240),
    "Tablet (light)": (1600, 900, 240),
    "Tablet (QHD)": (2560, 1440, 320),
    "OUYA": (1920, 1080, 320),
    "GameStick": (1280, 720, 213),
}
SIZE_LIMITS = {"width": (320, 3840), "height": (320, 3840), "density": (120, 640)}

HARDWARE = {
    "avd.ini.encoding": "UTF-8",
    "hw.gpu.enabled": "yes",
    "hw.keyboard": "yes",
    "hw.mainKeys": "no",
    "hw.sdCard": "no",
    "hw.audioInput": "yes",
    "fastboot.forceColdBoot": "no",
    "showDeviceFrame": "no",
    "skin.path": "_no_skin",
}


@dataclass
class Instance:
    id: str
    name: str
    slot: int
    cores: int = 4
    ram: int = 4096
    width: int = 1080
    height: int = 1920
    density: int = 420
    fps: int = 60
    api: str = installer.DEFAULT_API
    camera: bool = False
    block_ads: bool = True
    eco: bool = False
    disk: int = 16
    gpu: str = DEFAULT_GPU
    muted: bool = False
    autostart: bool = False
    # A change to storage only takes effect on a fresh data partition, so the next start erases the old one
    wipe_next: bool = False
    # Where this instance's files live. Empty means the default folder, inside Androidbox's own data
    storage_path: str = ""

    @property
    def android(self):
        return installer.ANDROID_VERSIONS.get(self.api, f"Android API {self.api}")

    @property
    def console_port(self):
        return CONSOLE_PORTS[self.slot]

    @property
    def grpc_port(self):
        return GRPC_BASE + self.slot

    @property
    def serial(self):
        return f"emulator-{self.console_port}"

    @property
    def folder(self):
        base = Path(self.storage_path) if self.storage_path else paths.AVD_HOME
        return base / f"{self.id}.avd"

    @property
    def log(self):
        return paths.LOGS / f"{self.id}.log"

    @property
    def resolution(self):
        return next((name for name, size in RESOLUTIONS.items()
                     if size == (self.width, self.height, self.density)), "Custom")

    @property
    def initials(self):
        return initials(self.name)

    @property
    def gpu_mode(self):
        return self.gpu if self.gpu in GPU_MODES else DEFAULT_GPU

    @property
    def graphics(self):
        return GPU_MODES[self.gpu_mode]


def initials(name):
    letters = [next(char for char in word if char.isalnum())
               for word in name.split() if any(char.isalnum() for char in word)]
    return "".join(letters[:2]).upper() or "A"


def from_dict(values, **overrides):
    known = {field.name for field in fields(Instance)}
    return Instance(**{**{k: v for k, v in values.items() if k in known}, **overrides})


def load():
    try:
        instances = [from_dict(entry) for entry in json.loads(paths.INSTANCES.read_text())]
    except (OSError, ValueError):
        instances = []
    if recover(instances):
        save(instances)
    return instances


def number(values, key, default):
    value = values.get(key, "").strip()
    return int(value) if value.isdigit() else default


def marker_folder(marker):
    # The marker's own "path=" line is the source of truth: a custom-storage instance's data
    # doesn't sit next to its marker, the way the default folder always does
    for line in marker.read_text().splitlines():
        key, _, value = line.partition("=")
        if key.strip() == "path" and value.strip():
            return Path(value.strip())
    return paths.AVD_HOME / f"{marker.stem}.avd"


def recover(instances):
    known = {instance.id for instance in instances}
    found = False
    for marker in sorted(paths.AVD_HOME.glob("*.ini")):
        if marker.stem in known or len(instances) >= len(CONSOLE_PORTS):
            continue
        folder = marker_folder(marker)
        config = folder / "config.ini"
        if not config.exists():
            continue
        values = dict(line.split("=", 1) for line in config.read_text().splitlines() if "=" in line)
        name = values.get("avd.ini.displayname", "Android").strip() or "Android"
        if any(instance.name == name for instance in instances):
            name = f"{name} (recovered)"
        api = values.get("image.sysdir.1", "").split("android-")[-1].split("\\")[0]
        storage_path = str(folder.parent) if folder.parent != paths.AVD_HOME else ""
        instances.append(Instance(
            id=marker.stem, name=name, slot=free_slot(instances), storage_path=storage_path,
            cores=number(values, "hw.cpu.ncore", 4), ram=number(values, "hw.ramSize", 4096),
            width=number(values, "hw.lcd.width", 1080), height=number(values, "hw.lcd.height", 1920),
            density=number(values, "hw.lcd.density", 420), fps=number(values, "hw.lcd.vsync", 60),
            disk=number({"size": values.get("disk.dataPartition.size", "").rstrip("Gg")}, "size", 16),
            gpu=values.get("hw.gpu.mode", DEFAULT_GPU),
            api=api if api in installer.ANDROID_VERSIONS else installer.DEFAULT_API,
            camera=values.get("hw.camera.front") == "webcam0"))
        known.add(marker.stem)
        found = True
    return found


def save(instances):
    paths.INSTANCES.parent.mkdir(parents=True, exist_ok=True)
    paths.INSTANCES.write_text(json.dumps([asdict(instance) for instance in instances], indent=2))


def free_slot(instances):
    used = {instance.slot for instance in instances}
    slot = next((slot for slot in range(len(CONSOLE_PORTS)) if slot not in used), None)
    if slot is None:
        raise RuntimeError(f"Androidbox supports up to {len(CONSOLE_PORTS)} instances")
    return slot


def new_id():
    return f"box{uuid.uuid4().hex[:8]}"


def adopt(instances, instance):
    write_avd(instance)
    instances.append(instance)
    save(instances)
    return instance


def create(instances, name, **hardware):
    return adopt(instances, Instance(id=new_id(), name=name, slot=free_slot(instances), **hardware))


def clone(source, slot):
    copy = from_dict(asdict(source), id=new_id(), name=f"{source.name} copy", slot=slot)
    shutil.copytree(source.folder, copy.folder, ignore=shutil.ignore_patterns(*BACKUP_SKIPS))
    return copy


def forget(instances, instance):
    # Drop it from the list before touching its files, so a folder that can't be removed yet
    # never leaves a half-deleted instance behind
    (paths.AVD_HOME / f"{instance.id}.ini").unlink(missing_ok=True)
    instances[:] = [kept for kept in instances if kept.id != instance.id]
    save(instances)


def writable_then_retry(remove, path, error):
    # The emulator marks some files read-only (pstore.bin), which Windows refuses to delete
    with contextlib.suppress(OSError):
        os.chmod(path, stat.S_IWRITE)
        remove(path)


def erase(instance):
    for _ in range(20):
        with contextlib.suppress(OSError):
            shutil.rmtree(instance.folder, onexc=writable_then_retry)
        if not instance.folder.exists():
            break
        time.sleep(0.5)
    for frames in paths.DATA.glob(f"{instance.id}-*.frame"):
        with contextlib.suppress(OSError):
            frames.unlink()


def backup(instance, file, progress):
    root = instance.folder
    files = [path for path in root.rglob("*")
             if path.is_file() and not BACKUP_SKIPS.intersection(path.relative_to(root).parts)]
    total = sum(path.stat().st_size for path in files) or 1
    done = 0
    with zipfile.ZipFile(file, "w", zipfile.ZIP_DEFLATED, compresslevel=1) as archive:
        archive.writestr("instance.json", json.dumps(asdict(instance)))
        for path in files:
            name = f"avd/{path.relative_to(root).as_posix()}"
            with open(path, "rb") as source, archive.open(name, "w", force_zip64=True) as target:
                while chunk := source.read(CHUNK):
                    target.write(chunk)
                    done += len(chunk)
                    progress(done, total)


def restore(file, slot, progress):
    with zipfile.ZipFile(file) as archive:
        try:
            saved = json.loads(archive.read("instance.json"))
        except KeyError:
            raise RuntimeError("This file isn't an Androidbox backup") from None
        # The backup's original storage location may not exist on this PC, so restore to the default
        # folder; the instance can be moved to a custom one again afterwards
        instance = from_dict(saved, id=new_id(), slot=slot, storage_path="")
        root = instance.folder.resolve()
        members = [member for member in archive.infolist()
                   if member.filename.startswith("avd/") and not member.is_dir()]
        total = sum(member.file_size for member in members) or 1
        done = 0
        try:
            for member in members:
                target = (root / member.filename[4:]).resolve()
                if not target.is_relative_to(root):
                    raise RuntimeError("This backup contains unsafe file paths")
                target.parent.mkdir(parents=True, exist_ok=True)
                with archive.open(member) as source, open(target, "wb") as output:
                    while chunk := source.read(CHUNK):
                        output.write(chunk)
                        done += len(chunk)
                        progress(done, total)
        except Exception:
            shutil.rmtree(root, ignore_errors=True)
            raise
    return instance


def write_avd(instance):
    instance.folder.mkdir(parents=True, exist_ok=True)
    (paths.AVD_HOME / f"{instance.id}.ini").write_text(
        "avd.ini.encoding=UTF-8\n"
        f"path={instance.folder}\n"
        f"path.rel=avd\\{instance.id}.avd\n"
        f"target=android-{instance.api}\n"
    )
    config_path = instance.folder / "config.ini"
    config = {}
    if config_path.exists():
        for line in config_path.read_text().splitlines():
            key, _, value = line.partition("=")
            if key:
                config[key.strip()] = value.strip()
    before = {key: value for key, value in config.items() if key != "avd.ini.displayname"}
    tag = installer.image_tag(instance.api)
    abi = installer.image_abi(instance.api)
    config.update(HARDWARE)
    config.update({
        "AvdId": instance.id,
        "avd.ini.displayname": instance.name,
        "image.sysdir.1": f"{installer.image_dir(instance.api)}\\",
        "tag.id": tag,
        "tag.display": installer.TAG_LABELS.get(tag, tag),
        "abi.type": abi,
        "hw.cpu.arch": installer.ARCH_FAMILY[abi],
        "PlayStore.enabled": "true" if installer.has_playstore(instance.api) else "false",
        "hw.camera.front": "webcam0" if instance.camera else "none",
        "hw.camera.back": "webcam0" if instance.camera else "none",
        "disk.dataPartition.size": f"{instance.disk}G",
        "hw.gpu.mode": instance.gpu_mode,
        "hw.cpu.ncore": str(instance.cores),
        "hw.ramSize": str(instance.ram),
        "hw.lcd.width": str(instance.width),
        "hw.lcd.height": str(instance.height),
        "hw.lcd.density": str(instance.density),
        "hw.lcd.vsync": str(instance.fps),
        "hw.initialOrientation": "portrait" if instance.height >= instance.width else "landscape",
        "skin.name": f"{instance.width}x{instance.height}",
    })
    config_path.write_text("".join(f"{key}={value}\n" for key, value in config.items()))
    return before != {key: value for key, value in config.items() if key != "avd.ini.displayname"}
