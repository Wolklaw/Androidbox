import hashlib
import shutil
import urllib.request
import xml.etree.ElementTree as ET
import zipfile
from dataclasses import dataclass
from pathlib import Path

from . import paths

REPOSITORY = "https://dl.google.com/android/repository/"
STABLE = "channel-0"

IMAGE_API = "35"
IMAGE_TAG = "google_apis_playstore"
IMAGE_ABI = "x86_64"
IMAGE_NAME = "Android 15"
IMAGE_REPOSITORY = f"{REPOSITORY}sys-img/{IMAGE_TAG}/"
IMAGE_DIR = Path("system-images", f"android-{IMAGE_API}", IMAGE_TAG, IMAGE_ABI)

REQUIRED = [Path("platform-tools"), Path("emulator"), IMAGE_DIR]


@dataclass
class Package:
    label: str
    url: str
    size: int
    sha1: str
    license: str
    folder: Path

    @property
    def installed(self):
        return (paths.SDK / self.folder).is_dir()


def is_installed():
    return all((paths.SDK / folder).is_dir() for folder in REQUIRED)


def resolve():
    repository = fetch_xml(REPOSITORY + "repository2-3.xml")
    images = fetch_xml(IMAGE_REPOSITORY + "sys-img2-3.xml")
    packages = [
        newest(repository, "platform-tools", REPOSITORY, "adb", REQUIRED[0]),
        newest(repository, "emulator", REPOSITORY, "the emulator", REQUIRED[1]),
        newest(images, f"system-images;android-{IMAGE_API};{IMAGE_TAG};{IMAGE_ABI}",
               IMAGE_REPOSITORY, IMAGE_NAME, IMAGE_DIR),
    ]
    texts = {**licenses(images), **licenses(repository)}
    return packages, {p.license: texts.get(p.license, "") for p in packages}


def install(packages, progress):
    paths.DOWNLOADS.mkdir(parents=True, exist_ok=True)
    for package in packages:
        if package.installed:
            continue
        archive = download(package, progress)
        extract(archive, paths.SDK / package.folder,
                lambda done, total: progress(package, done, total, "unpack"))
        archive.unlink()
    shutil.rmtree(paths.DOWNLOADS, ignore_errors=True)


def fetch_xml(url):
    with urllib.request.urlopen(url, timeout=30) as response:
        return ET.fromstring(response.read())


def local(element):
    return element.tag.rsplit("}", 1)[-1]


def first(element, name):
    return next((child for child in element.iter() if local(child) == name), None)


def licenses(root):
    return {element.get("id"): element.text.strip() for element in root if local(element) == "license"}


def newest(root, sdk_path, base_url, label, folder):
    best = None
    for package in root:
        if local(package) != "remotePackage" or package.get("path") != sdk_path:
            continue
        channel = first(package, "channelRef")
        if channel is None or channel.get("ref") != STABLE:
            continue
        revision = tuple(int(part.text) for part in first(package, "revision") if part.text.isdigit())
        for archive in package.iter():
            if local(archive) != "archive" or not runs_on_windows(archive):
                continue
            if best is None or revision > best[0]:
                complete = first(archive, "complete")
                best = revision, Package(
                    label=label,
                    url=base_url + first(complete, "url").text,
                    size=int(first(complete, "size").text),
                    sha1=first(complete, "checksum").text,
                    license=first(package, "uses-license").get("ref"),
                    folder=folder,
                )
    if best is None:
        raise RuntimeError(f"Google's repository has no Windows build of {sdk_path}")
    return best[1]


def runs_on_windows(archive):
    host = first(archive, "host-os")
    arch = first(archive, "host-arch")
    return (host is None or host.text == "windows") and (arch is None or arch.text == "x64")


def download(package, progress):
    final = paths.DOWNLOADS / Path(package.url).name
    if final.exists():
        return final
    partial = final.with_suffix(".part")
    have = partial.stat().st_size if partial.exists() else 0

    if have < package.size:
        headers = {"Range": f"bytes={have}-"} if have else {}
        with urllib.request.urlopen(urllib.request.Request(package.url, headers=headers), timeout=60) as response:
            if have and response.status != 206:
                have = 0
            with open(partial, "ab" if have else "wb") as file:
                while chunk := response.read(1 << 20):
                    file.write(chunk)
                    have += len(chunk)
                    progress(package, have, package.size, "download")

    progress(package, package.size, package.size, "verify")
    digest = hashlib.sha1()
    with open(partial, "rb") as file:
        while chunk := file.read(1 << 22):
            digest.update(chunk)
    if digest.hexdigest() != package.sha1:
        partial.unlink()
        raise RuntimeError(f"The download of {package.label} was damaged. Try again.")
    partial.rename(final)
    return final


def extract(archive, destination, progress):
    staging = destination.parent / ".unpacking"
    shutil.rmtree(staging, ignore_errors=True)
    with zipfile.ZipFile(archive) as zipped:
        members = zipped.infolist()
        total = sum(member.file_size for member in members) or 1
        done = 0
        for member in members:
            zipped.extract(member, staging)
            done += member.file_size
            progress(done, total)
    contents = list(staging.iterdir())
    source = contents[0] if len(contents) == 1 and contents[0].is_dir() else staging
    shutil.rmtree(destination, ignore_errors=True)
    destination.parent.mkdir(parents=True, exist_ok=True)
    source.rename(destination)
    shutil.rmtree(staging, ignore_errors=True)
