import ctypes
import os
import subprocess
import sys
import winreg
from ctypes import wintypes
from pathlib import Path

from . import paths

RUN_KEY = r"Software\Microsoft\Windows\CurrentVersion\Run"
RUN_NAME = "Androidbox"
RESERVED_MEMORY = 4096


class MemoryStatus(ctypes.Structure):
    _fields_ = [("length", wintypes.DWORD), ("load", wintypes.DWORD), ("total", ctypes.c_ulonglong),
                ("free", ctypes.c_ulonglong), ("page_total", ctypes.c_ulonglong), ("page_free", ctypes.c_ulonglong),
                ("virtual_total", ctypes.c_ulonglong), ("virtual_free", ctypes.c_ulonglong),
                ("extended", ctypes.c_ulonglong)]


class ProcessMemory(ctypes.Structure):
    _fields_ = [("size", wintypes.DWORD), ("faults", wintypes.DWORD), ("peak", ctypes.c_size_t),
                ("working_set", ctypes.c_size_t), ("pool_peak", ctypes.c_size_t), ("pool", ctypes.c_size_t),
                ("nonpaged_peak", ctypes.c_size_t), ("nonpaged", ctypes.c_size_t), ("pagefile", ctypes.c_size_t),
                ("pagefile_peak", ctypes.c_size_t)]


def host_cores():
    return os.cpu_count() or 4


def host_memory():
    status = MemoryStatus()
    status.length = ctypes.sizeof(status)
    ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(status))
    return status.total // (1 << 20)


def suggested_hardware():
    # Half the PC's threads and a quarter of its memory leaves Windows plenty
    cores = max(2, min(8, host_cores() // 2 // 2 * 2))
    memory = host_memory()
    ram = 8192 if memory >= 24576 else 6144 if memory >= 16384 else 4096 if memory >= 8192 else 3072 if memory >= 6144 \
        else 2048
    return cores, ram


def core_options(current):
    options = {count for count in (1, 2, 3, 4, 6, 8, 10, 12, 16, 24, 32) if count <= host_cores()}
    return sorted(options | {current})


def memory_options(current):
    limit = max(host_memory() - RESERVED_MEMORY, 2048)
    options = {size for size in (2048, 3072, 4096, 6144, 8192, 12288, 16384, 24576, 32768) if size <= limit}
    return sorted(options | {current})


def process_handle(pid, access):
    return ctypes.windll.kernel32.OpenProcess(access, False, pid)


def process_times(pid):
    handle = process_handle(pid, 0x1000)
    if not handle:
        return None
    created, exited, kernel, user = (wintypes.FILETIME() for _ in range(4))
    try:
        ok = ctypes.windll.kernel32.GetProcessTimes(handle, ctypes.byref(created), ctypes.byref(exited),
                                                    ctypes.byref(kernel), ctypes.byref(user))
    finally:
        ctypes.windll.kernel32.CloseHandle(handle)
    if not ok:
        return None
    ticks = lambda value: (value.dwHighDateTime << 32 | value.dwLowDateTime) / 1e7
    return ticks(kernel) + ticks(user)


def process_memory(pid):
    handle = process_handle(pid, 0x1000 | 0x0010)
    if not handle:
        return None
    counters = ProcessMemory()
    counters.size = ctypes.sizeof(counters)
    try:
        ok = ctypes.windll.psapi.GetProcessMemoryInfo(handle, ctypes.byref(counters), counters.size)
    finally:
        ctypes.windll.kernel32.CloseHandle(handle)
    return counters.working_set if ok else None


def launcher():
    # What starts Androidbox: its exe once installed, or pythonw and the script when run from source
    if getattr(sys, "frozen", False):
        return sys.executable, ""
    python = Path(sys.executable).with_name("pythonw.exe")
    script = paths.BUNDLE / "Androidbox.pyw"
    return str(python if python.exists() else sys.executable), f'"{script}"'


def command(*arguments):
    target, prefix = launcher()
    return " ".join([f'"{target}"', *([prefix] if prefix else []), *arguments])


def starts_with_windows():
    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, RUN_KEY) as key:
            winreg.QueryValueEx(key, RUN_NAME)
        return True
    except OSError:
        return False


def start_with_windows(enabled):
    with winreg.OpenKey(winreg.HKEY_CURRENT_USER, RUN_KEY, 0, winreg.KEY_SET_VALUE) as key:
        if enabled:
            winreg.SetValueEx(key, RUN_NAME, 0, winreg.REG_SZ, command("--background"))
        else:
            try:
                winreg.DeleteValue(key, RUN_NAME)
            except FileNotFoundError:
                pass


def shortcut(file, arguments, description):
    target, prefix = launcher()
    script = ("$link = (New-Object -ComObject WScript.Shell).CreateShortcut($env:SHORTCUT_FILE); "
              "$link.TargetPath = $env:SHORTCUT_TARGET; $link.Arguments = $env:SHORTCUT_ARGUMENTS; "
              "$link.Description = $env:SHORTCUT_TEXT; $link.IconLocation = $env:SHORTCUT_ICON; "
              "$link.WorkingDirectory = $env:SHORTCUT_FOLDER; $link.Save()")
    # Passed as environment variables so that no quoting can break a path or a game's name
    settings = {"SHORTCUT_FILE": str(file), "SHORTCUT_TARGET": target,
                "SHORTCUT_ARGUMENTS": " ".join([prefix, *arguments]).strip(), "SHORTCUT_TEXT": description,
                "SHORTCUT_ICON": str(paths.ICON), "SHORTCUT_FOLDER": str(Path(target).parent)}
    result = subprocess.run(["powershell", "-NoProfile", "-NonInteractive", "-Command", script], capture_output=True,
                            text=True, env={**os.environ, **settings}, creationflags=subprocess.CREATE_NO_WINDOW)
    if result.returncode:
        raise OSError(result.stderr.strip() or "Windows couldn't create the shortcut")


def restart():
    # The new copy has to wait until this one has let go of the single-instance lock
    subprocess.Popen(["cmd", "/c", f'timeout /t 2 /nobreak >nul & start "" {command()}'],
                     creationflags=subprocess.CREATE_NO_WINDOW | subprocess.DETACHED_PROCESS, close_fds=True)
