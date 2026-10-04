import shutil

from . import paths

FOLDER = paths.HOME / "claude"
TOOL = FOLDER / "androidbox.py"
GUIDE = FOLDER / "README.md"

GUIDE_TEXT = """# Androidbox for Claude Code

Androidbox's "Let Claude Code control Android" switch is on. Use the helper in this folder to drive the
running instances:

    python "{tool}" list
    python "{tool}" shot [instance] [file.png]
    python "{tool}" ui [instance]
    python "{tool}" tap [instance] X Y
    python "{tool}" tap-text [instance] "Sign in"
    python "{tool}" swipe [instance] X1 Y1 X2 Y2 [ms]
    python "{tool}" text [instance] "hello"
    python "{tool}" key [instance] BACK|HOME|ENTER|<KEYCODE_...>
    python "{tool}" install [instance] app.apk
    python "{tool}" launch [instance] com.example.app
    python "{tool}" stop-app [instance] com.example.app
    python "{tool}" logcat [instance] [lines]
    python "{tool}" adb [instance] -- <any adb arguments>

`instance` is a name or id from `list`, and can be left out when only one instance is running. Start
instances from the Androidbox window. The helper refuses to run while the switch is off.
"""

TOOL_TEXT = r'''import json
import os
import re
import subprocess
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

HOME = Path(os.environ["LOCALAPPDATA"]) / "Androidbox"
ADB = HOME / "sdk" / "platform-tools" / "adb.exe"
CONSOLE_PORTS = {CONSOLE_PORTS}
KEYS = {"BACK": "KEYCODE_BACK", "HOME": "KEYCODE_HOME", "ENTER": "KEYCODE_ENTER", "MENU": "KEYCODE_MENU",
        "RECENTS": "KEYCODE_APP_SWITCH", "POWER": "KEYCODE_POWER", "DELETE": "KEYCODE_DEL"}


def fail(message):
    sys.exit(f"androidbox: {message}")


def read(path, default):
    try:
        return json.loads(Path(path).read_text())
    except (OSError, ValueError):
        return default


def allowed():
    return read(HOME / "data" / "settings.json", {}).get("claude_access") is True


def adb(serial, *args, binary=False, check=True):
    result = subprocess.run([str(ADB), "-s", serial, *args], capture_output=True, timeout=600)
    if check and result.returncode:
        fail((result.stdout + result.stderr).decode(errors="replace").strip() or "adb failed")
    return result.stdout if binary else result.stdout.decode(errors="replace")


def online():
    out = subprocess.run([str(ADB), "devices"], capture_output=True, text=True, timeout=30).stdout
    return {line.split()[0] for line in out.splitlines()[1:] if line.strip().endswith("device")}


def instances():
    found = []
    for entry in read(HOME / "data" / "instances.json", []):
        port = CONSOLE_PORTS[entry["slot"]]
        found.append({"id": entry["id"], "name": entry["name"], "serial": f"emulator-{port}"})
    return found


def pick(arguments):
    running = online()
    live = [item for item in instances() if item["serial"] in running]
    if arguments:
        wanted = arguments[0].lower()
        for item in instances():
            if wanted in (item["id"].lower(), item["name"].lower()):
                arguments.pop(0)
                if item["serial"] not in running:
                    fail(f"{item['name']} isn't running. Start it from the Androidbox window")
                return item["serial"]
    if len(live) == 1:
        return live[0]["serial"]
    fail("no instance running" if not live else "several instances are running, name one: "
         + ", ".join(item["name"] for item in live))


def screen_nodes(serial):
    adb(serial, "shell", "uiautomator", "dump", "/sdcard/androidbox-ui.xml")
    xml = adb(serial, "exec-out", "cat", "/sdcard/androidbox-ui.xml")
    nodes = []
    for node in ET.fromstring(xml).iter("node"):
        box = re.findall(r"\d+", node.get("bounds", ""))
        if len(box) == 4:
            x1, y1, x2, y2 = map(int, box)
            nodes.append({"text": node.get("text", ""), "desc": node.get("content-desc", ""),
                          "id": node.get("resource-id", ""), "class": node.get("class", "").split(".")[-1],
                          "clickable": node.get("clickable") == "true", "center": [(x1 + x2) // 2, (y1 + y2) // 2],
                          "bounds": [x1, y1, x2, y2]})
    return nodes


def main():
    if len(sys.argv) < 2:
        fail("commands: list shot ui tap tap-text swipe text key install launch stop-app logcat adb")
    command, arguments = sys.argv[1], sys.argv[2:]
    if not allowed():
        fail("Claude Code access is off. Turn on 'Let Claude Code control Android' in Androidbox")
    if not ADB.exists():
        fail("Androidbox hasn't set up its Android tools yet. Open Androidbox first")
    if command == "list":
        running = online()
        for item in instances():
            print(f"{item['name']}\t{item['id']}\t{item['serial']}\t{'running' if item['serial'] in running else 'off'}")
        return
    serial = pick(arguments)
    if command == "shot":
        target = Path(arguments[0] if arguments else "androidbox-shot.png").resolve()
        target.write_bytes(adb(serial, "exec-out", "screencap", "-p", binary=True))
        print(target)
    elif command == "ui":
        for node in screen_nodes(serial):
            if node["text"] or node["desc"] or node["clickable"]:
                label = node["text"] or node["desc"] or node["id"]
                print(f"{'*' if node['clickable'] else ' '} {node['class']:<14} {label!r:<40} {node['center']}")
    elif command == "tap" and len(arguments) == 2:
        adb(serial, "shell", "input", "tap", *arguments)
    elif command == "tap-text" and arguments:
        wanted = arguments[0].lower()
        matches = [n for n in screen_nodes(serial) if wanted in (n["text"] + " " + n["desc"]).lower()]
        if not matches:
            fail(f"nothing on screen says {arguments[0]!r}")
        adb(serial, "shell", "input", "tap", *map(str, matches[0]["center"]))
    elif command == "swipe" and len(arguments) in (4, 5):
        adb(serial, "shell", "input", "swipe", *arguments)
    elif command == "text" and arguments:
        adb(serial, "shell", "input", "text", arguments[0].replace(" ", "%s"))
    elif command == "key" and arguments:
        adb(serial, "shell", "input", "keyevent", KEYS.get(arguments[0].upper(), arguments[0]))
    elif command == "install" and arguments:
        print(adb(serial, "install", "-r", arguments[0]).strip())
    elif command == "launch" and arguments:
        adb(serial, "shell", "monkey", "-p", arguments[0], "-c", "android.intent.category.LAUNCHER", "1")
    elif command == "stop-app" and arguments:
        adb(serial, "shell", "am", "force-stop", arguments[0])
    elif command == "logcat":
        print(adb(serial, "logcat", "-d", "-t", arguments[0] if arguments else "200"))
    elif command == "adb":
        print(adb(serial, *(arguments[1:] if arguments[:1] == ["--"] else arguments)).strip())
    else:
        fail(f"unknown or incomplete command: {command}")


main()
'''


def enable():
    from . import instances
    FOLDER.mkdir(parents=True, exist_ok=True)
    TOOL.write_text(TOOL_TEXT.replace("{CONSOLE_PORTS}", repr(list(instances.CONSOLE_PORTS))), encoding="utf-8")
    GUIDE.write_text(GUIDE_TEXT.format(tool=TOOL), encoding="utf-8")


def disable():
    shutil.rmtree(FOLDER, ignore_errors=True)
