import dataclasses
import platform
import re
import zipfile

from . import VERSION

# What to look for in the device log, in order of how likely it is to explain a game that crashes or closes
FINDINGS = [
    ("ARM translator crash",
     ("Cannot process signal 11", "libndk_translation_proxy_libc", "libproxy_arm64_to_x86_64_libc",
      "Forwarding signal 11"),
     "An ARM game crashed inside Android's ARM-to-x86 translator, usually while copying memory it had just "
     "protected. No newer Android image fixes this, so the game itself has to avoid it."),
    ("App crash", ("FATAL EXCEPTION", "AndroidRuntime: Shutting down VM"),
     "An app threw an error it didn't handle and closed. The lines around it name the app and the error."),
    ("App not responding", ("ANR in ",), "An app froze for several seconds and Android offered to close it."),
    ("Out of memory", ("OutOfMemoryError", "lowmemorykiller", "Out of memory: Kill"),
     "Android ran out of memory and closed an app. Give this instance more memory in its Settings."),
    ("Graphics trouble", ("EGL_BAD_", "GLES: Failed", "Failed to create GL", "eglMakeCurrent"),
     "Something went wrong with the graphics. Try Automatic or Software graphics in this instance's Settings."),
    ("Missing Play certification", ("not Play Protect certified", "DEVICE_NOT_CERTIFIED"),
     "Google doesn't consider this image certified. Redownloading the image in Settings sometimes fixes it."),
]
LOG_COMMANDS = {
    "logcat.txt": ("logcat", "-d", "-b", "all", "-v", "threadtime"),
    "properties.txt": ("shell", "getprop"),
    "memory.txt": ("shell", "dumpsys", "meminfo"),
    "crashes.txt": ("shell", "dumpsys", "dropbox", "--print", "data_app_crash"),
}


def findings(logcat):
    found = []
    for title, needles, advice in FINDINGS:
        lines = [line.strip() for line in logcat.splitlines() if any(needle in line for needle in needles)]
        if lines:
            found.append((title, advice, lines))
    return found


def summary(instance, running, logcat):
    lines = [f"Androidbox {VERSION} on {platform.platform()}", f"Instance: {instance.name} ({instance.id}), "
             f"{instance.android}, {'running' if running else 'not running'}", ""]
    found = findings(logcat) if logcat else []
    if not logcat:
        lines.append("No device log: Android wasn't running when this was collected.")
    elif not found:
        lines.append("No known problem signatures in the device log.")
    for title, advice, matches in found:
        lines += [f"== {title} ({len(matches)} lines)", advice, *(f"   {line[:240]}" for line in matches[:5]), ""]
    return "\n".join(lines)


def collect(emulator, destination):
    """Zips the device log, the emulator's own log and this instance's settings, plus a plain summary of what
    looks wrong. Returns the number of problems it recognised."""
    instance = emulator.instance
    running = emulator.running()
    outputs = {}
    if running:
        for name, command in LOG_COMMANDS.items():
            code, output = emulator.adb(*command, timeout=90)
            if code == 0 or output:
                outputs[name] = output
    logcat = outputs.get("logcat.txt", "")
    with zipfile.ZipFile(destination, "w", zipfile.ZIP_DEFLATED) as bundle:
        bundle.writestr("summary.txt", summary(instance, running, logcat))
        for name, text in outputs.items():
            bundle.writestr(name, text)
        # A proxy address can carry a login, and this file is meant to be shared
        settings = {**dataclasses.asdict(instance), "proxy": re.sub(r"//[^@/]*@", "//***@", instance.proxy)}
        bundle.writestr("instance.txt", "\n".join(f"{key}={value}" for key, value in settings.items()))
        for name, path in (("emulator.log", instance.log), ("config.ini", instance.folder / "config.ini")):
            try:
                bundle.write(path, name)
            except OSError:
                pass
    return len(findings(logcat))
