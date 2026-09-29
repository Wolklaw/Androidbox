import json
import time
import urllib.request
import zipfile

from . import paths

FIRST_LAUNCH = 6

VERSIONS = "https://product-details.mozilla.org/1.0/mobile_versions.json"
ARCHIVE = ("https://archive.mozilla.org/pub/fenix/releases/{version}/android/fenix-{version}-android-x86_64/"
           "fenix-{version}.multi.android-x86_64.apk")
PACKAGE = "org.mozilla.firefox"
UBLOCK = "https://addons.mozilla.org/android/addon/ublock-origin/"
CACHE = paths.DATA / "cache"


def installed(emulator):
    code, output = emulator.adb("shell", f"pm path {PACKAGE}")
    return code == 0 and "package:" in output


def download(progress):
    with urllib.request.urlopen(VERSIONS, timeout=20) as response:
        version = json.loads(response.read())["version"]
    target = CACHE / f"firefox-{version}.apk"
    if target.exists():
        return target
    CACHE.mkdir(parents=True, exist_ok=True)
    for old in CACHE.glob("firefox-*"):
        old.unlink()
    partial = target.with_suffix(".part")
    with urllib.request.urlopen(ARCHIVE.format(version=version), timeout=60) as response:
        total = int(response.headers.get("Content-Length", 0)) or 1
        done = 0
        with open(partial, "wb") as file:
            while chunk := response.read(1 << 20):
                file.write(chunk)
                done += len(chunk)
                progress("download", done, total)
    with zipfile.ZipFile(partial) as apk:
        if "AndroidManifest.xml" not in apk.namelist():
            partial.unlink()
            raise RuntimeError("The Firefox download was damaged. Try again.")
    partial.rename(target)
    return target


def set_up(emulator, progress):
    fresh = not installed(emulator)
    if fresh:
        apk = download(progress)
        progress("install", 0, 1)
        ok, reason = emulator.install(apk)
        if not ok:
            raise RuntimeError(f"Firefox didn't install: {reason}")
    emulator.adb("shell", f"cmd role add-role-holder android.app.role.BROWSER {PACKAGE}")
    if fresh:
        emulator.adb("shell", f"monkey -p {PACKAGE} -c android.intent.category.LAUNCHER 1")
        time.sleep(FIRST_LAUNCH)
    emulator.adb("shell", f"am start -a android.intent.action.VIEW -d {UBLOCK} {PACKAGE}")
