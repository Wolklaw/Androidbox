import json
import os
import shutil
import subprocess
import sys
import threading
from pathlib import Path

from . import paths

FOLDER = paths.HOME / "claude"
TOOL = FOLDER / "androidbox.py"
GUIDE = FOLDER / "README.md"

GUIDE_TEXT = """# Androidbox for Claude Code

Androidbox's "Let Claude Code control Android" switch is on.

## As an MCP server (recommended)

Androidbox registers this for you by adding it to Claude Code's user config (~/.claude.json). Restart Claude
Code afterwards. To do it by hand instead, from any folder:

    claude mcp add --scope user androidbox -- python "{tool}" mcp

Claude Code then gets tools for your running instances: list_instances, screenshot (returned inline, no
file to save and read back), read_screen, ui_tree, wait_for_text, screen_record, tap, tap_text, swipe, type_text, key, install_apk, launch_app,
stop_app, logcat and adb. Run `/mcp` in Claude Code to check it connected.

## As a command line

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
instances from the Androidbox window. Either way, the helper refuses to run while the switch is off.
"""

HOME_LINE = ("# This script lives in the claude folder inside Androidbox's own folder, wherever that has been moved to\n"
             "HOME =Path(__file__).resolve().parent.parent")

TOOL_TEXT = r'''import base64
import json
import os
import re
import subprocess
import sys
import tempfile
import time
import xml.etree.ElementTree as ET
from pathlib import Path

{HOME_LINE}
ADB = HOME / "sdk" / "platform-tools" / "adb.exe"
ENVIRONMENT = {**os.environ, "ANDROID_ADB_SERVER_PORT": "{ADB_SERVER_PORT}"}
CONSOLE_PORTS = {CONSOLE_PORTS}
KEYS = {"BACK": "KEYCODE_BACK", "HOME": "KEYCODE_HOME", "ENTER": "KEYCODE_ENTER", "MENU": "KEYCODE_MENU",
        "RECENTS": "KEYCODE_APP_SWITCH", "POWER": "KEYCODE_POWER", "DELETE": "KEYCODE_DEL"}


class Problem(Exception):
    """Something the caller did wrong, as opposed to a bug here: reported, never a crash."""


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
    result = subprocess.run([str(ADB), "-s", serial, *args], capture_output=True, timeout=600, env=ENVIRONMENT)
    if check and result.returncode:
        raise Problem((result.stdout + result.stderr).decode(errors="replace").strip() or "adb failed")
    return result.stdout if binary else result.stdout.decode(errors="replace")


def online():
    out = subprocess.run([str(ADB), "devices"], capture_output=True, text=True, timeout=30, env=ENVIRONMENT).stdout
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
                    raise Problem(f"{item['name']} isn't running. Start it from the Androidbox window")
                return item["serial"]
    if len(live) == 1:
        return live[0]["serial"]
    raise Problem("no instance running" if not live else "several instances are running, name one: "
                  + ", ".join(item["name"] for item in live))


def resolve(name):
    """Same matching as pick(), but for the MCP tools, where the instance is a named argument, not a
    positional one a command might also want."""
    running = online()
    live = [item for item in instances() if item["serial"] in running]
    if name:
        wanted = name.lower()
        for item in instances():
            if wanted in (item["id"].lower(), item["name"].lower()):
                if item["serial"] not in running:
                    raise Problem(f"{item['name']} isn't running. Start it from the Androidbox window")
                return item["serial"]
        raise Problem(f"no instance named {name!r}")
    if len(live) == 1:
        return live[0]["serial"]
    raise Problem("no instance running" if not live else "several instances are running, name one: "
                  + ", ".join(item["name"] for item in live))


def screen_xml(serial):
    adb(serial, "shell", "uiautomator", "dump", "/sdcard/androidbox-ui.xml")
    return adb(serial, "exec-out", "cat", "/sdcard/androidbox-ui.xml")


def screen_nodes(serial):
    nodes = []
    for node in ET.fromstring(screen_xml(serial)).iter("node"):
        box = re.findall(r"\d+", node.get("bounds", ""))
        if len(box) == 4:
            x1, y1, x2, y2 = map(int, box)
            nodes.append({"text": node.get("text", ""), "desc": node.get("content-desc", ""),
                          "id": node.get("resource-id", ""), "class": node.get("class", "").split(".")[-1],
                          "clickable": node.get("clickable") == "true", "center": [(x1 + x2) // 2, (y1 + y2) // 2],
                          "bounds": [x1, y1, x2, y2]})
    return nodes


def text_content(text):
    return {"type": "text", "text": text}


def tool_list_instances(arguments):
    running = online()
    lines = [f"{item['name']}\t{item['id']}\t{item['serial']}\t{'running' if item['serial'] in running else 'off'}"
             for item in instances()]
    return [text_content("\n".join(lines) or "no instances")]


def tool_screenshot(arguments):
    serial = resolve(arguments.get("instance"))
    png = adb(serial, "exec-out", "screencap", "-p", binary=True)
    return [{"type": "image", "data": base64.b64encode(png).decode(), "mimeType": "image/png"}]


def tool_read_screen(arguments):
    serial = resolve(arguments.get("instance"))
    lines = [f"{'*' if n['clickable'] else ' '} {n['class']:<14} {(n['text'] or n['desc'] or n['id'])!r:<40} "
             f"{n['center']}" for n in screen_nodes(serial) if n["text"] or n["desc"] or n["clickable"]]
    return [text_content("\n".join(lines) or "nothing on screen")]


def tool_ui_tree(arguments):
    xml = screen_xml(resolve(arguments.get("instance")))
    return [text_content(xml if len(xml) <= 60000 else xml[:60000] + "\n... cut off, use read_screen for a summary")]


def tool_wait_for_text(arguments):
    serial = resolve(arguments.get("instance"))
    wanted, gone = arguments["text"].lower(), bool(arguments.get("gone"))
    deadline = time.monotonic() + min(max(arguments.get("timeout", 20), 1), 120)
    while True:
        try:
            matches = [n for n in screen_nodes(serial) if wanted in (n["text"] + " " + n["desc"]).lower()]
        except (Problem, ET.ParseError):
            # uiautomator can't dump while the screen is animating, so try again
            matches = None
        if matches is not None and bool(matches) != gone:
            return [text_content("gone" if gone else f"found at {matches[0]['center']}")]
        if time.monotonic() > deadline:
            raise Problem(f"timed out waiting for {arguments['text']!r} to " + ("go away" if gone else "show up"))
        time.sleep(1)


def tool_screen_record(arguments):
    serial = resolve(arguments.get("instance"))
    seconds = min(max(arguments.get("seconds", 10), 1), 60)
    path = arguments.get("path") or os.path.join(tempfile.gettempdir(), f"androidbox-{int(time.time())}.mp4")
    adb(serial, "shell", "screenrecord", "--time-limit", str(seconds), "/sdcard/androidbox-clip.mp4")
    adb(serial, "pull", "/sdcard/androidbox-clip.mp4", path)
    adb(serial, "shell", "rm", "/sdcard/androidbox-clip.mp4", check=False)
    return [text_content(f"saved {seconds} seconds to {path}")]


def tool_tap(arguments):
    serial = resolve(arguments.get("instance"))
    adb(serial, "shell", "input", "tap", str(arguments["x"]), str(arguments["y"]))
    return [text_content("tapped")]


def tool_tap_text(arguments):
    serial = resolve(arguments.get("instance"))
    wanted = arguments["text"].lower()
    matches = [n for n in screen_nodes(serial) if wanted in (n["text"] + " " + n["desc"]).lower()]
    if not matches:
        raise Problem(f"nothing on screen says {arguments['text']!r}")
    adb(serial, "shell", "input", "tap", *map(str, matches[0]["center"]))
    return [text_content(f"tapped {matches[0]['center']}")]


def tool_swipe(arguments):
    serial = resolve(arguments.get("instance"))
    points = [str(arguments["x1"]), str(arguments["y1"]), str(arguments["x2"]), str(arguments["y2"])]
    if "ms" in arguments:
        points.append(str(arguments["ms"]))
    adb(serial, "shell", "input", "swipe", *points)
    return [text_content("swiped")]


def tool_type_text(arguments):
    serial = resolve(arguments.get("instance"))
    adb(serial, "shell", "input", "text", arguments["text"].replace(" ", "%s"))
    return [text_content("typed")]


def tool_key(arguments):
    serial = resolve(arguments.get("instance"))
    key = arguments["key"]
    adb(serial, "shell", "input", "keyevent", KEYS.get(key.upper(), key))
    return [text_content("sent")]


def tool_install_apk(arguments):
    serial = resolve(arguments.get("instance"))
    return [text_content(adb(serial, "install", "-r", arguments["path"]).strip())]


def tool_launch_app(arguments):
    serial = resolve(arguments.get("instance"))
    adb(serial, "shell", "monkey", "-p", arguments["package"], "-c", "android.intent.category.LAUNCHER", "1")
    return [text_content("launched")]


def tool_stop_app(arguments):
    serial = resolve(arguments.get("instance"))
    adb(serial, "shell", "am", "force-stop", arguments["package"])
    return [text_content("stopped")]


def tool_logcat(arguments):
    serial = resolve(arguments.get("instance"))
    return [text_content(adb(serial, "logcat", "-d", "-t", str(arguments.get("lines", 200))))]


def tool_adb(arguments):
    serial = resolve(arguments.get("instance"))
    return [text_content(adb(serial, *arguments["args"]).strip())]


INSTANCE_PROPERTY = {"instance": {"type": "string", "description": "A name or id from list_instances. "
                                                                    "Leave out when only one is running."}}
TOOLS = [
    {"name": "list_instances", "description": "List Androidbox instances and whether each is running.",
     "inputSchema": {"type": "object", "properties": {}}},
    {"name": "screenshot", "description": "Take a screenshot of an instance's screen.",
     "inputSchema": {"type": "object", "properties": INSTANCE_PROPERTY}},
    {"name": "read_screen", "description": "List the text, labels and tap targets currently on screen.",
     "inputSchema": {"type": "object", "properties": INSTANCE_PROPERTY}},
    {"name": "ui_tree", "description": "The raw accessibility tree of the screen as XML, for when read_screen "
                                       "leaves something out.",
     "inputSchema": {"type": "object", "properties": INSTANCE_PROPERTY}},
    {"name": "wait_for_text", "description": "Wait until text shows up on screen, or with gone set, until it "
                                             "disappears. Fails when the timeout runs out.",
     "inputSchema": {"type": "object", "required": ["text"], "properties": {
         **INSTANCE_PROPERTY, "text": {"type": "string"}, "gone": {"type": "boolean"},
         "timeout": {"type": "integer", "description": "Seconds to wait, up to 120. Defaults to 20."}}}},
    {"name": "screen_record", "description": "Record the screen as an MP4 for a few seconds and save it on "
                                             "this PC. Returns where.",
     "inputSchema": {"type": "object", "properties": {
         **INSTANCE_PROPERTY, "seconds": {"type": "integer", "description": "Up to 60. Defaults to 10."},
         "path": {"type": "string", "description": "Where to save it. Defaults to the temp folder."}}}},
    {"name": "tap", "description": "Tap a point on the screen.",
     "inputSchema": {"type": "object", "required": ["x", "y"], "properties": {
         **INSTANCE_PROPERTY, "x": {"type": "integer"}, "y": {"type": "integer"}}}},
    {"name": "tap_text", "description": "Tap whatever on screen contains this text or accessibility label.",
     "inputSchema": {"type": "object", "required": ["text"], "properties": {
         **INSTANCE_PROPERTY, "text": {"type": "string"}}}},
    {"name": "swipe", "description": "Swipe from one point to another.",
     "inputSchema": {"type": "object", "required": ["x1", "y1", "x2", "y2"], "properties": {
         **INSTANCE_PROPERTY, "x1": {"type": "integer"}, "y1": {"type": "integer"}, "x2": {"type": "integer"},
         "y2": {"type": "integer"}, "ms": {"type": "integer", "description": "How long the swipe takes."}}}},
    {"name": "type_text", "description": "Type text into the focused field.",
     "inputSchema": {"type": "object", "required": ["text"], "properties": {
         **INSTANCE_PROPERTY, "text": {"type": "string"}}}},
    {"name": "key", "description": "Send a key: BACK, HOME, ENTER, MENU, RECENTS, POWER, DELETE, or any "
                                   "KEYCODE_* name.",
     "inputSchema": {"type": "object", "required": ["key"], "properties": {
         **INSTANCE_PROPERTY, "key": {"type": "string"}}}},
    {"name": "install_apk", "description": "Install an APK file.",
     "inputSchema": {"type": "object", "required": ["path"], "properties": {
         **INSTANCE_PROPERTY, "path": {"type": "string"}}}},
    {"name": "launch_app", "description": "Launch an app by its package name.",
     "inputSchema": {"type": "object", "required": ["package"], "properties": {
         **INSTANCE_PROPERTY, "package": {"type": "string"}}}},
    {"name": "stop_app", "description": "Force-stop an app by its package name.",
     "inputSchema": {"type": "object", "required": ["package"], "properties": {
         **INSTANCE_PROPERTY, "package": {"type": "string"}}}},
    {"name": "logcat", "description": "Read the last lines of the device log.",
     "inputSchema": {"type": "object", "properties": {
         **INSTANCE_PROPERTY, "lines": {"type": "integer"}}}},
    {"name": "adb", "description": "Last resort: a raw adb command against the instance, for what the other "
                                   "tools don't cover. Already pointed at Androidbox's adb server.",
     "inputSchema": {"type": "object", "required": ["args"], "properties": {
         **INSTANCE_PROPERTY, "args": {"type": "array", "items": {"type": "string"}}}}},
]
DISPATCH = {
    "list_instances": tool_list_instances, "screenshot": tool_screenshot, "read_screen": tool_read_screen,
    "ui_tree": tool_ui_tree, "wait_for_text": tool_wait_for_text, "screen_record": tool_screen_record,
    "tap": tool_tap, "tap_text": tool_tap_text, "swipe": tool_swipe, "type_text": tool_type_text, "key": tool_key,
    "install_apk": tool_install_apk, "launch_app": tool_launch_app, "stop_app": tool_stop_app,
    "logcat": tool_logcat, "adb": tool_adb,
}


INSTRUCTIONS = ("These tools drive the Android phones that Androidbox runs on this PC. Use them instead of running adb "
                "yourself: Androidbox keeps its own adb server on port {ADB_SERVER_PORT}, so a plain `adb devices` "
                "shows none of its instances. Start with list_instances, then read_screen (text and tap targets) "
                "before falling back to screenshot, and use tap_text, wait_for_text and install_apk/launch_app "
                "rather than guessing coordinates or shelling out. The adb tool is only for what the others don't "
                "cover. If an instance is off, ask the user to start it from the Androidbox window.")


def respond(id_, result):
    print(json.dumps({"jsonrpc": "2.0", "id": id_, "result": result}), flush=True)


def mcp_server():
    # Line-delimited JSON-RPC 2.0, per the MCP stdio transport: no response to a notification (no "id")
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            request = json.loads(line)
        except ValueError:
            continue
        method, has_id, id_ = request.get("method"), "id" in request, request.get("id")
        params = request.get("params") or {}
        if method == "initialize":
            respond(id_, {"protocolVersion": params.get("protocolVersion", "2024-11-05"),
                          "capabilities": {"tools": {}}, "serverInfo": {"name": "androidbox", "version": "1.0"},
                          "instructions": INSTRUCTIONS})
        elif method == "tools/list":
            respond(id_, {"tools": TOOLS})
        elif method == "tools/call":
            handler = DISPATCH.get(params.get("name"))
            try:
                if not handler:
                    raise Problem(f"unknown tool: {params.get('name')}")
                if not allowed():
                    raise Problem("Claude Code access is off. Turn on 'Let Claude Code control Android' "
                                  "in Androidbox")
                if not ADB.exists():
                    raise Problem("Androidbox hasn't set up its Android tools yet. Open Androidbox first")
                respond(id_, {"content": handler(params.get("arguments") or {}), "isError": False})
            except Problem as exc:
                respond(id_, {"content": [text_content(str(exc))], "isError": True})
            except Exception as exc:
                respond(id_, {"content": [text_content(f"error: {exc}")], "isError": True})
        elif method == "ping" and has_id:
            respond(id_, {})
        elif has_id and method != "notifications/initialized":
            print(json.dumps({"jsonrpc": "2.0", "id": id_,
                              "error": {"code": -32601, "message": f"method not found: {method}"}}), flush=True)


def run(command, arguments):
    if not allowed():
        raise Problem("Claude Code access is off. Turn on 'Let Claude Code control Android' in Androidbox")
    if not ADB.exists():
        raise Problem("Androidbox hasn't set up its Android tools yet. Open Androidbox first")
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
            raise Problem(f"nothing on screen says {arguments[0]!r}")
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
        raise Problem(f"unknown or incomplete command: {command}")


def main():
    if len(sys.argv) < 2:
        fail("commands: list shot ui tap tap-text swipe text key install launch stop-app logcat adb mcp")
    command, arguments = sys.argv[1], sys.argv[2:]
    if command == "mcp":
        mcp_server()
        return
    try:
        run(command, arguments)
    except Problem as exc:
        fail(str(exc))


main()
'''


def enable():
    from . import emulator, instances
    FOLDER.mkdir(parents=True, exist_ok=True)
    TOOL.write_text(TOOL_TEXT.replace("{CONSOLE_PORTS}", repr(list(instances.CONSOLE_PORTS)))
                    .replace("{ADB_SERVER_PORT}", emulator.ADB_SERVER_PORT)
                    .replace("{HOME_LINE}", HOME_LINE), encoding="utf-8")
    GUIDE.write_text(GUIDE_TEXT.format(tool=TOOL), encoding="utf-8")
    threading.Thread(target=register, daemon=True).start()


def disable():
    shutil.rmtree(FOLDER, ignore_errors=True)
    threading.Thread(target=unregister, daemon=True).start()


CONFIG = Path.home() / ".claude.json"
DESKTOP_CONFIG = Path(os.environ.get("APPDATA", str(Path.home()))) / "Claude" / "claude_desktop_config.json"
SKILL = Path.home() / ".claude" / "skills" / "androidbox" / "SKILL.md"
SKILL_TEXT = """---
name: androidbox
description: Use for anything on an Android phone, emulator or app on this PC - testing or debugging an app, taking screenshots, tapping, typing, installing an APK, reading logcat. Androidbox runs the phones; use its MCP tools, not raw adb.
---

Androidbox runs Android instances on this PC with a private adb server (port {port}), so plain `adb devices`
shows nothing. Use the `androidbox` MCP tools (mcp__androidbox__*): list_instances, read_screen, screenshot,
tap_text, tap, swipe, type_text, key, wait_for_text, install_apk, launch_app, stop_app, logcat, screen_record.
Prefer read_screen over screenshot, and tap_text over tapping coordinates. If the tools are missing, check
`/mcp`; if the user's instance is off, ask them to start it from the Androidbox window. From a shell, the same
helper works: `python "{tool}" list`.
"""


def python_command():
    """A python that can run the helper: the one Androidbox runs on from source, else whatever is on PATH.
    A bare `python` is no good, it can be the Microsoft Store stub that opens a store page instead of running."""
    if not getattr(sys, "frozen", False):
        console = Path(sys.executable).with_name("python.exe")
        return str(console if console.exists() else sys.executable)
    for name in ("python", "py"):
        found = shutil.which(name)
        if found and "WindowsApps" not in found:
            return found
    return "python"


def edit_config(change, path=None):
    """Claude Code keeps user-scope MCP servers in ~/.claude.json. Editing it directly is the fallback for when
    the `claude` command isn't on PATH, as with the desktop app, so registration doesn't depend on it."""
    try:
        path = path or CONFIG
        data = json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}
        servers = data.setdefault("mcpServers", {})
        change(servers)
        path.parent.mkdir(parents=True, exist_ok=True)
        temporary = path.with_suffix(".androidbox.tmp")
        temporary.write_text(json.dumps(data, indent=2), encoding="utf-8")
        temporary.replace(path)
        return True
    except (OSError, ValueError, AttributeError):
        return False


def mcp_command(*arguments):
    """Runs `claude mcp ...`; False when Claude Code isn't installed or the command failed, in which case the
    guide still shows how to register by hand."""
    claude = shutil.which("claude")
    if not claude:
        return False
    try:
        return subprocess.run([claude, "mcp", *arguments], capture_output=True, timeout=60,
                              creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0)).returncode == 0
    except (OSError, subprocess.SubprocessError):
        return False


def plugin_installed():
    """The Androidbox plugin brings its own server and skill, so registering ours as well would double them."""
    try:
        return "androidbox@" in (Path.home() / ".claude" / "plugins" / "installed_plugins.json").read_text(encoding="utf-8")
    except OSError:
        return False


def register():
    if plugin_installed():
        unregister()
        return True
    entry = {"type": "stdio", "command": python_command(), "args": [str(TOOL), "mcp"], "env": {}}
    # Written either way, so it lands even when the claude command is missing or fails
    done = edit_config(lambda servers: servers.__setitem__("androidbox", entry))
    if DESKTOP_CONFIG.parent.exists():
        edit_config(lambda servers: servers.__setitem__("androidbox", {k: v for k, v in entry.items() if k != "type"}),
                    DESKTOP_CONFIG)
    try:
        SKILL.parent.mkdir(parents=True, exist_ok=True)
        from . import emulator
        SKILL.write_text(SKILL_TEXT.format(port=emulator.ADB_SERVER_PORT, tool=TOOL), encoding="utf-8")
    except OSError:
        pass
    return done or (mcp_command("remove", "--scope", "user", "androidbox")
                    and mcp_command("add", "--scope", "user", "androidbox", "--", python_command(), str(TOOL), "mcp"))


def registered():
    try:
        return "androidbox" in json.loads(CONFIG.read_text(encoding="utf-8")).get("mcpServers", {})
    except (OSError, ValueError, AttributeError):
        return False


def unregister():
    edit_config(lambda servers: servers.pop("androidbox", None), DESKTOP_CONFIG) if DESKTOP_CONFIG.exists() else None
    shutil.rmtree(SKILL.parent, ignore_errors=True)
    edit_config(lambda servers: servers.pop("androidbox", None))
    return mcp_command("remove", "--scope", "user", "androidbox")
