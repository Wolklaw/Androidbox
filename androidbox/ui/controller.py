import os
import re
from datetime import datetime
from pathlib import Path

from PySide6.QtCore import QObject, QStandardPaths, QTimer, Signal
from PySide6.QtGui import QGuiApplication

from .. import emulator, installer, instances, macros, paths, profiles, system
from ..bridge import Bridge
from .tasks import background, on_main_thread

RECORDING_LIMIT = 180


def media_folder(kind):
    location = QStandardPaths.StandardLocation.PicturesLocation if kind == "image" \
        else QStandardPaths.StandardLocation.MoviesLocation
    folder = Path(QStandardPaths.writableLocation(location)) / "Androidbox"
    folder.mkdir(parents=True, exist_ok=True)
    return folder


def file_stamp(name):
    return f"{re.sub(r'[^A-Za-z0-9 _-]', '', name) or 'Android'} {datetime.now():%Y-%m-%d %H-%M-%S}"


def plural(count, word):
    return f"{count} {word}" if count == 1 else f"{count} {word}s"


class Controller(QObject):
    changed = Signal()
    attached = Signal()
    app_changed = Signal()
    macros_changed = Signal()
    image_missing = Signal()
    notify = Signal(str, str)

    def __init__(self, instance, all_instances):
        super().__init__()
        self.instance = instance
        self.all_instances = all_instances
        self.emulator = emulator.Emulator(instance)
        self.bridge = None
        self.token = None
        self.phase = "off"
        self.stopping = False
        self.epoch = 0
        self.checking = False
        self.ticks = 0
        self.pending = []
        self.package = None
        self.video = None
        self.video_part = 0
        self.video_stamp = ""
        self.player = None
        self.playing = None
        self.last_clip = None
        self.skip_clip = True
        self.apps = None
        self.pending_launch = None
        self.applied_fps = None
        self.usage = None
        self.sample = None
        self.timer = QTimer(self, interval=1500, timeout=self.poll)
        self.timer.start()
        self.video_timer = QTimer(self, singleShot=True, timeout=self.video_finished)
        self.poll()

    @property
    def state(self):
        return "stopping" if self.stopping else self.phase

    @property
    def on(self):
        return self.state == "on" and self.bridge is not None

    @property
    def recording_video(self):
        return bool(self.video or self.video_part)

    @property
    def recording_macro(self):
        return self.bridge is not None and self.bridge.recording is not None

    def save(self):
        instances.save(self.all_instances)

    def poll(self):
        if self.checking:
            return
        self.checking = True
        self.ticks += 1
        epoch = self.epoch
        wants_package = self.ticks % 2 == 0
        background(lambda: self.check(wants_package), lambda result: self.apply(*result, epoch))

    def check(self, wants_package):
        try:
            if self.emulator.running():
                if self.phase == "on" or self.emulator.booted():
                    phase = "on"
                else:
                    phase = "stuck" if self.emulator.stuck() else "booting"
            else:
                phase = "crashed" if self.emulator.crashed() else "off"
            package = self.package
            if phase == "on" and wants_package:
                package = self.emulator.foreground_app() or package
            token = self.emulator.grpc_token() if phase in ("booting", "on") else None
            return phase, package, token, self.emulator.usage() if phase == "on" else None
        except OSError:
            return self.phase, self.package, None, None
        finally:
            self.checking = False

    def measure(self, sample):
        # Processor use as a share of the whole PC, like Task Manager's, from the emulator's time between two checks
        previous, self.sample = self.sample, sample
        if not sample:
            self.usage = None
        elif previous:
            busy = (sample[1] - previous[1]) / max(sample[0] - previous[0], 0.001) / system.host_cores()
            self.usage = (max(0.0, min(100.0, busy * 100)), sample[2] / (1 << 30))

    def apply(self, phase, package, token, sample, epoch):
        if epoch != self.epoch or self.stopping:
            return
        self.measure(sample)
        if phase == "stuck":
            self.notify.emit(f"{self.instance.name}: Quick Boot stalled, doing a full restart", "text")
            self.stop(then=lambda: self.start(fresh=True))
            return
        ready = phase == "on" and self.phase != "on"
        moved = phase != self.phase
        self.phase = phase
        if token and token != self.token:
            self.detach()
            self.attach(token)
            moved = True
        if phase in ("off", "crashed") and self.bridge:
            self.detach()
            moved = True
        if package != self.package:
            self.package = package
            self.app_changed.emit()
            self.refresh_frame_rate()
        if moved:
            self.changed.emit()
        if ready:
            self.ready()

    def attach(self, token):
        self.token = token
        self.bridge = Bridge(self.instance.grpc_port, token, frames=paths.DATA / f"{self.instance.id}.frame")
        self.skip_clip = True
        self.bridge.watch_clipboard(lambda text: on_main_thread(lambda: self.clip_from_android(text)))
        QGuiApplication.clipboard().dataChanged.connect(self.clip_from_windows)
        self.attached.emit()

    def detach(self):
        self.token = None
        if not self.bridge:
            return
        QGuiApplication.clipboard().dataChanged.disconnect(self.clip_from_windows)
        self.stop_macro()
        self.bridge.close()
        self.bridge = None
        self.apps = None
        self.attached.emit()

    def ready(self):
        self.applied_fps = None
        self.refresh_frame_rate()
        background(self.emulator.keep_awake)
        if self.instance.block_ads:
            background(lambda: self.emulator.block_ads(True))
        if self.instance.eco:
            background(lambda: self.emulator.set_priority(True))
        if self.instance.muted:
            background(lambda: self.apply_mute(True))
        files, self.pending = self.pending, []
        if files:
            self.open_files(files)
        if self.pending_launch:
            package, self.pending_launch = self.pending_launch, None
            # The launcher needs a moment after Android reports it has booted
            QTimer.singleShot(3000, lambda: self.on and background(lambda: self.emulator.launch(package)))

    def refresh_frame_rate(self):
        # A game can have its own frame rate, which applies while it is in front
        own = profiles.game(self.package).get("fps") if self.package else None
        fps = own or self.instance.fps
        if self.state == "on" and fps != self.applied_fps:
            self.applied_fps = fps
            background(lambda: self.emulator.set_frame_rate(fps))

    def launch(self, package):
        if self.on:
            background(lambda: self.emulator.launch(package))
            return
        self.pending_launch = package
        if self.state in ("off", "crashed"):
            self.start()

    def start(self, wipe=False, fresh=False):
        if self.state not in ("off", "crashed"):
            return
        if not installer.image_installed(self.instance.api):
            self.image_missing.emit()
            return
        self.epoch += 1
        if self.instance.wipe_next:
            wipe = True
            self.instance.wipe_next = False
            self.save()
        self.emulator.start(wipe, fresh)
        self.phase = "booting"
        self.changed.emit()

    def stop(self, then=None):
        if self.stopping or self.state in ("off", "crashed"):
            if then:
                then()
            return
        self.epoch += 1
        self.stopping = True
        if self.recording_video:
            self.stop_video()
        self.detach()
        self.changed.emit()

        def finished(_=None):
            self.stopping = False
            self.epoch += 1
            self.phase = "off"
            self.changed.emit()
            if then:
                then()

        background(self.emulator.stop, finished, finished)

    def restart(self):
        self.stop(then=self.start)

    def factory_reset(self):
        self.stop(then=lambda: self.start(wipe=True))

    def open_files(self, files):
        files = [str(file) for file in files]
        if not self.on:
            self.pending.extend(files)
            if self.state in ("off", "crashed"):
                self.start()
            self.notify.emit(f"{plural(len(self.pending), 'file')} will be added once Android is ready", "text")
            return
        first = Path(files[0]).name
        self.notify.emit(f"Adding {first}…" if len(files) == 1 else f"Adding {len(files)} files…", "text")

        def work():
            results = []
            for file in files:
                if emulator.is_app_package(file):
                    ok, reason = self.emulator.install(file)
                else:
                    ok, reason = self.emulator.push(file)
                results.append((Path(file).name, emulator.is_app_package(file), ok, reason))
            return results

        background(work, self.files_added)

    def files_added(self, results):
        failed = [(name, reason) for name, _, ok, reason in results if not ok]
        apps = sum(1 for _, is_app, ok, _ in results if ok and is_app)
        files = sum(1 for _, is_app, ok, _ in results if ok and not is_app)
        if apps:
            self.apps = None
        for name, reason in failed:
            self.notify.emit(f"Couldn't add {name}: {reason}", "bad")
        done = []
        if apps:
            done.append(f"installed {plural(apps, 'app')}")
        if files:
            done.append(f"copied {plural(files, 'file')} to Downloads")
        if done:
            self.notify.emit(" and ".join(done).capitalize(), "good")

    def key(self, name):
        if self.bridge:
            self.bridge.key(name)

    def wake(self):
        if self.on:
            background(self.emulator.keep_awake)

    def rotate(self):
        if self.bridge:
            bridge = self.bridge
            background(lambda: bridge.rotate(0 if bridge.rotation() else 90))

    def shake(self):
        if self.bridge:
            background(self.bridge.shake)

    def locate(self, latitude, longitude):
        if self.bridge:
            bridge = self.bridge
            background(lambda: bridge.locate(latitude, longitude),
                       lambda _: self.notify.emit(f"Location set to {latitude:.4f}, {longitude:.4f}", "good"))

    def screenshot(self):
        if not self.bridge:
            return
        bridge = self.bridge

        def work():
            file = media_folder("image") / f"{file_stamp(self.instance.name)}.png"
            file.write_bytes(bridge.screenshot())
            return file

        background(work, lambda file: self.notify.emit(f"Screenshot saved to Pictures\\Androidbox\\{file.name}", "good"))

    def toggle_video(self):
        if self.recording_video:
            self.stop_video()
            return
        if not self.on:
            return
        self.video_stamp = file_stamp(self.instance.name)
        self.video_part = 1
        self.record_part()

    def record_part(self):
        suffix = f" part {self.video_part}" if self.video_part > 1 else ""
        self.video = media_folder("video") / f"{self.video_stamp}{suffix}.webm"
        self.changed.emit()

        def started(ok):
            if ok:
                self.video_timer.start(RECORDING_LIMIT * 1000)
                if self.video_part == 1:
                    self.notify.emit("Recording the screen. Click record again to stop", "text")
            else:
                self.video = None
                self.video_part = 0
                self.changed.emit()
                self.notify.emit("Couldn't start recording", "bad")

        background(self.emulator.start_recording, started, lambda _: started(False))

    def stop_video(self):
        file, self.video = self.video, None
        parts = self.video_part
        self.video_part = 0
        self.video_timer.stop()
        self.changed.emit()
        if not file:
            return

        def saved(ok):
            if not ok:
                self.notify.emit("The recording couldn't be saved", "bad")
            elif parts > 1:
                self.notify.emit(f"Recording saved to Videos\\Androidbox in {parts} parts", "good")
            else:
                self.notify.emit(f"Recording saved to Videos\\Androidbox\\{file.name}", "good")

        background(lambda: self.emulator.stop_recording(file), saved, lambda _: saved(False))

    def video_finished(self):
        if not self.video:
            return
        file, self.video = self.video, None
        self.video_part += 1

        def next_part(_=None):
            if self.video_part and self.on:
                self.record_part()

        background(lambda: self.emulator.stop_recording(file), next_part, next_part)

    def trigger_macro(self, key):
        if not self.bridge:
            return False
        macro = next((macro for macro in macros.load() if macro.get("hotkey") == key), None)
        if not macro:
            return False
        self.toggle_macro_playback(macro)
        return True

    def run_macro_named(self, name):
        macro = next((macro for macro in macros.load() if macro["name"] == name), None)
        if macro:
            self.toggle_macro_playback(macro)
        else:
            self.notify.emit(f"The macro {name} isn't in this profile", "bad")

    def toggle_macro_playback(self, macro):
        if self.playing == macro["name"]:
            self.stop_macro()
        else:
            self.play_macro(macro)

    def update_macro(self, current, **changes):
        try:
            macros.update(current, **changes)
        except (OSError, ValueError) as error:
            self.notify.emit(str(error), "bad")
        self.macros_changed.emit()

    def toggle_macro(self):
        if not self.bridge:
            return
        if self.bridge.recording is None:
            self.stop_macro()
            self.bridge.recording = []
            self.notify.emit("Recording a macro. Use Android, then click the macro button again", "text")
        else:
            recording, self.bridge.recording = self.bridge.recording, None
            macro = macros.save(macros.next_name(), recording, (self.instance.width, self.instance.height))
            if macro:
                self.notify.emit(f"Saved {macro['name']} ({macro['duration']:.1f}s)", "good")
            else:
                self.notify.emit("Nothing was recorded", "text")
            self.macros_changed.emit()
        self.changed.emit()

    def play_macro(self, macro, loops=None):
        loops = macro.get("loops", 1) if loops is None else loops
        if not self.bridge:
            self.notify.emit("Start Android to play macros", "text")
            return
        display = macro.get("display")
        if display and list(display) != [self.instance.width, self.instance.height]:
            self.notify.emit(f"{macro['name']} was recorded on a {display[0]}×{display[1]} display, so it only "
                             "plays on an instance with the same one", "bad")
            return
        self.stop_macro()
        self.playing = macro["name"]
        self.player = macros.Player(self.bridge, macro, loops, on_done=lambda: on_main_thread(self.macro_done))
        self.macros_changed.emit()

    def stop_macro(self):
        if self.player:
            self.player.stop()

    def macro_done(self):
        self.player = None
        self.playing = None
        self.macros_changed.emit()

    def set_eco(self, enabled):
        self.instance.eco = enabled
        self.save()
        if self.on:
            background(lambda: self.emulator.set_priority(enabled))
        self.changed.emit()

    def apply_mute(self, muted):
        # Runs off the main thread, since it waits on adb
        self.emulator.set_music_muted(muted)

    def set_autostart(self, enabled):
        self.instance.autostart = enabled
        self.save()

    def set_muted(self, muted):
        self.instance.muted = muted
        self.save()
        if self.on:
            background(lambda: self.apply_mute(muted))
        self.changed.emit()

    def hush(self, quiet):
        # The boss key silences every instance without changing which of them are muted for good
        if self.on and not self.instance.muted:
            background(lambda: self.apply_mute(quiet))

    def set_block_ads(self, enabled):
        self.instance.block_ads = enabled
        self.save()
        if self.on:
            background(lambda: self.emulator.block_ads(enabled))

    def clip_from_android(self, text):
        if self.skip_clip:
            self.skip_clip = False
            self.last_clip = text
            return
        if text and text != self.last_clip:
            self.last_clip = text
            QGuiApplication.clipboard().setText(text)

    def clip_from_windows(self):
        text = QGuiApplication.clipboard().text()
        if self.bridge and text and text != self.last_clip:
            self.last_clip = text
            bridge = self.bridge
            background(lambda: bridge.set_clipboard(text))

    def open_log(self):
        if self.instance.log.exists():
            os.startfile(self.instance.log)
