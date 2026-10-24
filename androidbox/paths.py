import os
import sys
import tempfile
from pathlib import Path

LOCAL = Path(os.environ["LOCALAPPDATA"])
DEFAULT_HOME = LOCAL / "Androidbox"
# The folder Androidbox keeps its files in can be moved to another drive. Where it went is written here,
# and this one file always stays in the default folder
LOCATION = DEFAULT_HOME / "location.txt"
CLEANUP = DEFAULT_HOME / "cleanup.txt"


def chosen_home():
    # ANDROIDBOX_HOME is for development and tests
    override = os.environ.get("ANDROIDBOX_HOME")
    if override:
        return Path(override)
    try:
        text = LOCATION.read_text(encoding="utf-8").strip()
    except OSError:
        return DEFAULT_HOME
    return Path(text) if text else DEFAULT_HOME


HOME = chosen_home()
SDK = HOME / "sdk"
DATA = HOME / "data"
DOWNLOADS = HOME / "downloads"

AVD_HOME = DATA / "avd"
LOGS = DATA / "logs"
PROFILES = DATA / "profiles"
PROFILE_STATE = DATA / "profile.json"
LEGACY_KEYMAPS = DATA / "keymaps"
LEGACY_MACROS = DATA / "macros"
INSTANCES = DATA / "instances.json"
SETTINGS = DATA / "settings.json"
CRASH_LOG = DATA / "crash.log"

EMULATOR = SDK / "emulator" / "emulator.exe"
ADB = SDK / "platform-tools" / "adb.exe"
DISCOVERY = {LOCAL / "Temp" / "avd" / "running", Path(tempfile.gettempdir()) / "avd" / "running"}
CONSOLE_TOKEN = Path.home() / ".emulator_console_auth_token"

BUNDLE = Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parent.parent))
ICON = BUNDLE / "assets" / "androidbox.ico"


def moved():
    return HOME != DEFAULT_HOME


def home_missing():
    return moved() and not HOME.is_dir()
