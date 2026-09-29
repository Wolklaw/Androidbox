import os
import sys
import tempfile
from pathlib import Path

LOCAL = Path(os.environ["LOCALAPPDATA"])
HOME = LOCAL / "Androidbox"
SDK = HOME / "sdk"
DATA = HOME / "data"
DOWNLOADS = HOME / "downloads"

AVD_HOME = DATA / "avd"
LOGS = DATA / "logs"
KEYMAPS = DATA / "keymaps"
MACROS = DATA / "macros"
INSTANCES = DATA / "instances.json"
SETTINGS = DATA / "settings.json"
CRASH_LOG = DATA / "crash.log"

EMULATOR = SDK / "emulator" / "emulator.exe"
ADB = SDK / "platform-tools" / "adb.exe"
DISCOVERY = {LOCAL / "Temp" / "avd" / "running", Path(tempfile.gettempdir()) / "avd" / "running"}
CONSOLE_TOKEN = Path.home() / ".emulator_console_auth_token"

BUNDLE = Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parent.parent))
ICON = BUNDLE / "assets" / "androidbox.ico"
