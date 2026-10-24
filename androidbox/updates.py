import hashlib
import json
import re
import urllib.request
from dataclasses import dataclass

from . import REPOSITORY, VERSION, paths

RELEASES = f"https://api.github.com/repos/{REPOSITORY}/releases/latest"
# Only an installer that GitHub itself serves from this project's releases is ever downloaded
DOWNLOADS = f"https://github.com/{REPOSITORY}/releases/download/"
INSTALLER = re.compile(r"^Androidbox-Setup-\d+(\.\d+)*\.exe$")
NOTES_LIMIT = 600
CHUNK = 1 << 18


@dataclass
class Release:
    version: str
    page: str
    notes: str = ""
    name: str = ""
    url: str = ""
    size: int = 0
    sha256: str = ""

    @property
    def installable(self):
        # Without GitHub's checksum there is nothing to verify the download against, so it stays a manual download
        return bool(self.url and self.size and self.sha256)


def parse(version):
    return tuple(int(part) for part in version.split(".") if part.isdigit())


def request(url):
    return urllib.request.Request(url, headers={"Accept": "application/vnd.github+json", "User-Agent": "Androidbox"})


def latest():
    with urllib.request.urlopen(request(RELEASES), timeout=15) as response:
        release = json.loads(response.read())
    assets = [asset for asset in release.get("assets", []) if INSTALLER.match(asset.get("name", ""))
              and asset.get("browser_download_url", "").startswith(DOWNLOADS)]
    asset = assets[0] if assets else {}
    digest = asset.get("digest") or ""
    return Release(version=release["tag_name"].lstrip("v"), page=release["html_url"],
                   notes=(release.get("body") or "").strip()[:NOTES_LIMIT], name=asset.get("name", ""),
                   url=asset.get("browser_download_url", ""), size=asset.get("size", 0),
                   sha256=digest.removeprefix("sha256:") if digest.startswith("sha256:") else "")


def newer(version):
    return parse(version) > parse(VERSION)


def folder():
    return paths.DOWNLOADS / "update"


def checksum(file):
    digest = hashlib.sha256()
    with open(file, "rb") as source:
        while chunk := source.read(CHUNK):
            digest.update(chunk)
    return digest.hexdigest()


def downloaded(release):
    """The installer for this release if it was already fetched and is still intact, else None"""
    file = folder() / release.name
    return file if release.installable and file.is_file() and file.stat().st_size == release.size \
        and checksum(file) == release.sha256 else None


def download(release, progress):
    """Fetches the installer, checks it against GitHub's checksum, and returns where it is. Raises if it's wrong"""
    kept = downloaded(release)
    if kept:
        return kept
    folder().mkdir(parents=True, exist_ok=True)
    for old in folder().glob("*"):
        old.unlink(missing_ok=True)
    partial = folder() / f"{release.name}.part"
    digest = hashlib.sha256()
    done = 0
    with urllib.request.urlopen(urllib.request.Request(release.url, headers={"User-Agent": "Androidbox"}),
                                timeout=30) as response, open(partial, "wb") as target:
        while chunk := response.read(CHUNK):
            target.write(chunk)
            digest.update(chunk)
            done += len(chunk)
            progress(done, release.size)
    if done != release.size or digest.hexdigest() != release.sha256:
        partial.unlink(missing_ok=True)
        raise RuntimeError("The download didn't match what GitHub published, so it was thrown away")
    file = folder() / release.name
    partial.replace(file)
    return file
