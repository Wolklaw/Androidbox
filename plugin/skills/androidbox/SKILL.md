---
name: androidbox
description: Use for anything on an Android phone, emulator or app on this PC - testing or debugging an app, taking screenshots, tapping, typing, installing an APK, reading logcat. Androidbox runs the phones; use its MCP tools, not raw adb.
---

Androidbox runs Android instances on this PC with a private adb server (port 5137), so plain `adb devices`
shows nothing. Use the `androidbox` MCP tools (mcp__androidbox__*): list_instances, read_screen, screenshot,
tap_text, tap, swipe, type_text, key, wait_for_text, install_apk, launch_app, stop_app, logcat, screen_record.
Prefer read_screen over screenshot, and tap_text over tapping coordinates. If the tools are missing, check
`/mcp`; if the user's instance is off, ask them to start it from the Androidbox window. From a shell, the same
helper works: `python "${CLAUDE_PLUGIN_ROOT}/server/androidbox.py" list`.
