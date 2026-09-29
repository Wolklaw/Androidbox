import ctypes
import os
import shutil
import socket
import subprocess
import tempfile
import time
import zipfile
from pathlib import Path

from . import instances, paths

AD_BLOCKING_DNS = "dns.adguard-dns.com"
QUICK_BOOT_LIMIT = 45
APP_PACKAGES = {".apk", ".apks", ".xapk", ".apkm"}


def environment():
    return {
        **os.environ,
        "ANDROID_HOME": str(paths.SDK),
        "ANDROID_SDK_ROOT": str(paths.SDK),
        "ANDROID_USER_HOME": str(paths.DATA),
        "ANDROID_AVD_HOME": str(paths.AVD_HOME),
    }


def run(args, timeout=30):
    try:
        result = subprocess.run(args, capture_output=True, text=True, timeout=timeout, env=environment(),
                                creationflags=subprocess.CREATE_NO_WINDOW, encoding="utf-8", errors="replace")
    except subprocess.TimeoutExpired:
        return -1, f"No answer after {timeout} seconds"
    return result.returncode, (result.stdout + result.stderr).strip()


def hardware_acceleration():
    code, output = run([str(paths.EMULATOR), "-accel-check"])
    lines = output.splitlines()
    return code == 0, lines[-2] if len(lines) > 1 else output


class Emulator:
    def __init__(self, instance):
        self.instance = instance
        self.process = None
        self.quick_boot = False
        self.started = 0.0

    @property
    def lock(self):
        return self.instance.folder / "hardware-qemu.ini.lock"

    def start(self, wipe=False, fresh=False):
        fresh = instances.write_avd(self.instance) or fresh
        args = [str(paths.EMULATOR), "-avd", self.instance.id, "-port", str(self.instance.console_port),
                "-grpc", str(self.instance.grpc_port), "-grpc-use-token", "-no-window", "-gpu", "host",
                "-no-boot-anim", "-no-metrics"]
        if wipe:
            args.append("-wipe-data")
        if fresh:
            args.append("-no-snapshot-load")
        self.quick_boot = (self.instance.folder / "snapshots" / "default_boot").exists() and not (wipe or fresh)
        self.started = time.monotonic()
        paths.LOGS.mkdir(parents=True, exist_ok=True)
        with open(self.instance.log, "w") as log:
            self.process = subprocess.Popen(args, env=environment(), stdout=log, stderr=subprocess.STDOUT,
                                            creationflags=subprocess.CREATE_NO_WINDOW)

    def running(self):
        if self.process and self.process.poll() is None:
            return True
        try:
            with socket.create_connection(("127.0.0.1", self.instance.console_port), timeout=0.2):
                return True
        except OSError:
            return False

    def fully_stopped(self):
        return not self.running() and not self.lock.exists()

    def crashed(self):
        return self.process is not None and self.process.poll() not in (None, 0)

    def booted(self):
        code, output = self.adb("shell", "getprop", "sys.boot_completed", timeout=5)
        return code == 0 and output == "1"

    def stuck(self):
        return self.quick_boot and time.monotonic() - self.started > QUICK_BOOT_LIMIT

    def grpc_token(self):
        found = []
        for ini in (file for folder in paths.DISCOVERY for file in folder.glob("pid_*.ini")):
            try:
                pid = int(ini.stem.removeprefix("pid_"))
                values = dict(line.split("=", 1) for line in ini.read_text().splitlines() if "=" in line)
                modified = ini.stat().st_mtime
            except (OSError, ValueError):
                continue
            if values.get("port.serial") == str(self.instance.console_port) and "grpc.token" in values \
                    and process_alive(pid):
                found.append((modified, values["grpc.token"]))
        return max(found)[1] if found else None

    def stop(self):
        try:
            self.console("kill")
        except OSError:
            pass
        deadline = time.monotonic() + 40
        while not self.fully_stopped() and time.monotonic() < deadline:
            time.sleep(0.5)
        if not self.fully_stopped():
            self.force_stop()
        self.process = None

    def force_stop(self):
        pids = [self.process.pid] if self.process else []
        pid = self.qemu_pid()
        if pid:
            pids.append(pid)
        for pid in pids:
            run(["taskkill", "/F", "/T", "/PID", str(pid)])

    def qemu_pid(self):
        try:
            return int((self.lock / "pid").read_text())
        except (OSError, ValueError):
            return None

    def console(self, command):
        token = paths.CONSOLE_TOKEN.read_text().strip()
        with socket.create_connection(("127.0.0.1", self.instance.console_port), timeout=5) as connection:
            connection.sendall(f"auth {token}\r\n{command}\r\nquit\r\n".encode())
            reply = b""
            try:
                while chunk := connection.recv(4096):
                    reply += chunk
            except OSError:
                pass
        return reply.decode(errors="replace")

    def adb(self, *args, timeout=30):
        return run([str(paths.ADB), "-s", self.instance.serial, *args], timeout)

    def install(self, package):
        path = Path(package)
        if path.suffix.lower() == ".apk":
            code, output = self.adb("install", "-r", str(path), timeout=600)
            return code == 0 and "Success" in output, last_line(output)
        with tempfile.TemporaryDirectory() as folder:
            with zipfile.ZipFile(path) as bundle:
                bundle.extractall(folder)
            apks = sorted(str(apk) for apk in Path(folder).rglob("*.apk"))
            if not apks:
                return False, "No APK files inside this package"
            code, output = self.adb("install-multiple", "-r", *apks, timeout=900)
            if code != 0 or "Success" not in output:
                return False, last_line(output)
            for obb in Path(folder).rglob("*.obb"):
                target = f"/sdcard/Android/obb/{obb.parent.name}/{obb.name}"
                self.adb("shell", f"mkdir -p /sdcard/Android/obb/{obb.parent.name}")
                self.adb("push", str(obb), target, timeout=1800)
        return True, ""

    def push(self, file):
        target = f"/sdcard/Download/{Path(file).name}"
        code, output = self.adb("push", str(file), target, timeout=1800)
        if code == 0:
            quoted = target.replace("'", "'\\''")
            self.adb("shell", f"am broadcast -a android.intent.action.MEDIA_SCANNER_SCAN_FILE -d 'file://{quoted}'")
        return code == 0, last_line(output)

    def block_ads(self, enabled):
        if enabled:
            self.adb("shell", f"settings put global private_dns_specifier {AD_BLOCKING_DNS}"
                              " && settings put global private_dns_mode hostname")
        else:
            self.adb("shell", "settings put global private_dns_mode opportunistic")

    def keep_awake(self):
        self.adb("shell", "svc power stayon true && input keyevent KEYCODE_WAKEUP")

    def set_frame_rate(self, fps):
        self.adb("shell", f"settings put system peak_refresh_rate {fps}.0"
                          f" && settings put system min_refresh_rate {fps}.0")

    def foreground_app(self):
        code, output = self.adb("shell", "dumpsys window | grep mCurrentFocus", timeout=5)
        if code != 0 or "/" not in output:
            return None
        return output.split("/")[0].split()[-1]

    def set_priority(self, eco):
        pid = self.qemu_pid()
        if not pid:
            return
        handle = ctypes.windll.kernel32.OpenProcess(0x0200, False, pid)
        if handle:
            ctypes.windll.kernel32.SetPriorityClass(handle, 0x4000 if eco else 0x20)
            ctypes.windll.kernel32.CloseHandle(handle)

    @property
    def recording(self):
        paths.DATA.mkdir(parents=True, exist_ok=True)
        return Path(short_path(paths.DATA)) / f"{self.instance.id}.webm"

    def start_recording(self):
        self.recording.unlink(missing_ok=True)
        return "KO" not in self.console(f"screenrecord start --time-limit 180 {self.recording}")

    def stop_recording(self, destination):
        self.console("screenrecord stop")
        deadline = time.monotonic() + 15
        size = -1
        while time.monotonic() < deadline:
            current = self.recording.stat().st_size if self.recording.exists() else -1
            if current > 0 and current == size:
                break
            size = current
            time.sleep(0.5)
        if not self.recording.exists():
            return False
        shutil.move(self.recording, destination)
        return True


def process_alive(pid):
    handle = ctypes.windll.kernel32.OpenProcess(0x1000, False, pid)
    if not handle:
        return False
    code = ctypes.c_ulong()
    ctypes.windll.kernel32.GetExitCodeProcess(handle, ctypes.byref(code))
    ctypes.windll.kernel32.CloseHandle(handle)
    return code.value == 259


def short_path(path):
    buffer = ctypes.create_unicode_buffer(1024)
    ctypes.windll.kernel32.GetShortPathNameW(str(path), buffer, len(buffer))
    return buffer.value or str(path)


def last_line(output):
    return output.strip().splitlines()[-1] if output.strip() else ""


def is_app_package(file):
    return Path(file).suffix.lower() in APP_PACKAGES
