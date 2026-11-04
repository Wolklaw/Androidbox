"""Renders the Claude Code plugin's MCP server from androidbox/claude.py, so the plugin and the in-app helper
never drift apart. Run from the repo root: python tools/build_plugin.py"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from androidbox import claude, emulator, instances  # noqa: E402

PLUGIN_HOME = '''# Installed as a Claude Code plugin, so Androidbox's folder isn't next to this script: find it
HOME = Path(os.environ.get("ANDROIDBOX_HOME") or Path(os.environ.get("LOCALAPPDATA", Path.home())) / "Androidbox")'''

text = (claude.TOOL_TEXT.replace("{CONSOLE_PORTS}", repr(list(instances.CONSOLE_PORTS)))
        .replace("{ADB_SERVER_PORT}", emulator.ADB_SERVER_PORT).replace("{HOME_LINE}", PLUGIN_HOME))
(ROOT / "plugin" / "server" / "androidbox.py").write_text(text, encoding="utf-8")
skill = claude.SKILL_TEXT.format(port=emulator.ADB_SERVER_PORT, tool="${CLAUDE_PLUGIN_ROOT}/server/androidbox.py")
(ROOT / "plugin" / "skills" / "androidbox" / "SKILL.md").write_text(skill, encoding="utf-8")
print("plugin rebuilt")
