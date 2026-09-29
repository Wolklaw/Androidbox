<p align="center">
  <img src="docs/banner.png" alt="Androidbox: Android on your PC. No ads." width="720">
</p>

<p align="center">
  <b>An ad-free Android emulator for Windows.</b><br>
  Google Play, game controls, multiple instances, and nothing trying to sell you anything.
</p>

<p align="center">
  <a href="https://github.com/Wolklaw/Androidbox/releases/latest"><b>Download Androidbox.exe</b></a>
</p>

---

Androidbox runs **Google's official Android Emulator**, the same engine inside Android Studio, on your
graphics card, and shows Android in one clean window. There are no ads, no accounts to create, no
bundled apps and no telemetry. Everything it needs downloads straight from Google, and everything it
stores stays in one folder you can delete.

<p align="center"><img src="docs/screen.png" alt="Androidbox running Android 15" width="820"></p>

## What you get

**Android 15 with Google Play**, running on your GPU at 60, 90, 120, 144 or 240 FPS, with ARM apps and
games supported. For older games that only ship 32-bit ARM code, create an instance with
**Android 11**, which runs both 32-bit and 64-bit ARM apps.

**Game controls**, saved separately for every game:

| Control | What it does |
|---|---|
| Tap | A key or controller button taps a spot on the screen |
| Joystick | WASD (rebindable), the D-pad or the left stick moves |
| Aim | Shooter mode: press its key (F1) and the mouse turns the camera. The right stick aims too |
| Look | Free look: the mouse turns the camera only while you hold its key (Alt) |
| Fire and Scope | The left and right mouse buttons while aiming |
| Skill | MOBA casting: hold the key, point with the mouse, release to cast |
| Turbo | Hold the key to tap the same spot rapidly |
| Swipe | One key performs a drag along an arrow you place, for dodges and lane changes |
| Zoom | Ctrl and the mouse wheel pinch in and out, with no setup |

Layouts export to a file, so you can share them or move them to another instance or PC.

<p align="center"><img src="docs/controls.png" alt="Placing game controls on the screen" width="820"></p>

**Controllers.** Xbox, PlayStation and Switch Pro controllers, 8BitDo pads and most other gamepads work
straight away, wired or over Bluetooth. Bind their buttons and triggers like keys. Without game
controls they navigate Android: A is Enter, B is Back, Start is Home.

**Macros.** Record taps, swipes and key presses once, then play them back once or on a loop, at half,
normal, double or four times the speed. Name a macro and give it a hotkey to fire it in the middle of a
game.

**Several Androids at once.** Every instance has its own apps, accounts and settings. Create, clone,
back up to a single file, restore, open any instance in its own window, tile them side by side, and
mirror your input to all of them at the same time.

<p align="center"><img src="docs/instances.png" alt="The instance manager" width="820"></p>

**No ads, two ways.**
- **Block ads** filters ad networks inside every app and game through AdGuard DNS.
- **Ad-free browser** installs Firefox from Mozilla, makes it the default browser and opens uBlock
  Origin for you. One tap later, websites are ad-free, YouTube included.

**Everything else you'd expect:** screenshots, screen recording with no time limit (saved in 3-minute parts), drag and drop to
install `.apk`, `.apks` and `.xapk` files (game data included), file import, your webcam as Android's
camera, rotate, shake, volume, GPS location, a clipboard shared with Windows, full screen, eco mode for
idle games, an FPS counter, and a quiet check for new Androidbox releases that you can turn off.

<p align="center"><img src="docs/settings.png" alt="Per-instance settings" width="820"></p>

## How it works

```mermaid
flowchart LR
    A["Androidbox window<br/>Qt"] -- "screen frames" --> B
    B["Android Emulator<br/>headless, on your GPU"] -- "shared memory<br/>60 to 240 FPS" --> A
    A -- "touch, keys, sensors<br/>gRPC" --> B
    A -- "installs, settings<br/>adb" --> B
    A -- "recording, shutdown<br/>console" --> B
    C["dl.google.com"] -. "first run" .-> B
```

1. **First run.** Androidbox reads Google's SDK package index, downloads the emulator, adb and the
   Android 15 system image (about 2.2 GB), checks every file's checksum, and unpacks them into
   `%LOCALAPPDATA%\Androidbox`. The Android 11 image (about 1.4 GB) only downloads the first time you
   start an instance that uses it.
2. **Starting Android.** Each instance is a standard Android virtual device. The emulator runs without
   a window of its own, uses your GPU, and resumes from a snapshot in a few seconds.
3. **Showing it.** Androidbox asks the emulator over gRPC to draw each frame, at the size of your window,
   straight into memory the two share, so frames arrive without being copied through a socket. Mouse,
   keyboard and controller input go back as multi-touch and key events.
4. **Game controls** turn keys, mouse movement and controller sticks into touches at the spots you
   placed, so they work in any game, even ones that were never built for a keyboard.
5. **Shutting down** saves a snapshot, so the next start picks up where you left off.

## Getting started

**You need:**
- Windows 10 or 11, 64-bit
- **Windows Hypervisor Platform** turned on. Androidbox tells you if it's off and opens the right
  settings page
- A graphics card with current drivers
- About 4 GB of disk space for Android, plus up to 10 GB per instance

**Then:**
1. Download `Androidbox.exe` from the [latest release](https://github.com/Wolklaw/Androidbox/releases/latest).
   It's a single file, so put it anywhere.
2. Open it. Windows may warn that the app is from an unknown publisher, because it isn't code-signed.
   Choose **More info**, then **Run anyway**.
3. Choose **Download and install**. This happens once.
4. Press **Start Android**.

Closing Androidbox saves and shuts down every running Android.

## Using it

**Mouse:** left-click taps, drag swipes, the wheel scrolls, right-click is Back, middle-click is Home.
**Keyboard:** typing goes straight to Android, and Esc is Back. **Files:** drop them on the screen.

| Shortcut | Action |
|---|---|
| F11 | Full screen |
| Ctrl+Shift+S | Screenshot, saved to `Pictures\Androidbox` |
| Ctrl+Shift+R | Record the screen, saved to `Videos\Androidbox` |
| Ctrl+Shift+K | Game controls on or off |
| Ctrl+Shift+E | Edit game controls |
| Ctrl+Shift+M | Record a macro |
| Ctrl+Shift+O | Rotate |
| Ctrl+Shift+W | Open in its own window |
| Ctrl+wheel | Pinch to zoom |

**Setting up a game:** open the game, press Ctrl+Shift+E, click where a button is and press the key you
want for it. **Add control** at the top adds a joystick, aim, look, fire, scope, skill, turbo or swipe
control. Drag controls to move them (drag the tip of a swipe arrow to aim it), scroll over one to
resize it, and right-click to remove it. Press Done, and the layout is saved for that game.

**Macros:** press Ctrl+Shift+M, play, and press it again. On the Macros page you can rename a macro,
change its speed and click the hotkey box to give it a shortcut such as Ctrl+1.

## Tips

- **Google Play needs a Google account** to install or update apps, and some Google apps that come with
  Android ask for an update before they open. If you'd rather not sign in, install apps from `.apk`
  files and use the ad-free browser for YouTube.
- **Games need more?** Give the instance more cores and memory in Settings, or switch it to the Tablet
  display for landscape games.
- **Idle game in the background?** Turn on eco mode for that instance.
- **A game won't install or says the device isn't supported?** It probably ships 32-bit ARM code only.
  Create a new instance, pick Android 11, and install it there.
- **High refresh rate monitor?** Set the instance's frame rate to 144 or 240 FPS in Settings. Games
  that cap their own frame rate stay capped.

## FAQ

**Is it really ad-free?** Androidbox itself has no ads and never will. Inside Android, Block ads stops
ad networks in apps and games, and the ad-free browser handles websites and YouTube. Ads that apps
serve from their own servers can't be filtered by any DNS blocker.

**Does it support root?** No. The Google Play images can't be rooted. The upside is that banking apps
and games with root detection keep working.

**Where is my data, and how do I remove it?** Everything lives in `%LOCALAPPDATA%\Androidbox`. Delete
that folder, and Androidbox with all its instances is gone.

**Can I run it without Google Play?** Yes. Skip signing in and install apps from `.apk` files.

**Does Pokémon GO work?** No, and it won't. Niantic blocks emulators on purpose: the game checks
Play Integrity and its own anti-cheat, and refuses to run on any emulator, BlueStacks included.
Getting around that means breaking their terms of service and risking a ban, so Androidbox doesn't try.
The GPS location tool is meant for testing apps and games that allow it.

**Why Android 15 and 11, and not the newest Android?** Google publishes Play Store images for new
versions long before they are stable enough for games. Android 15 is the newest one that runs games
reliably, and Android 11 is the last one that runs 32-bit ARM apps.

## Building

```powershell
.\build.ps1
```

This creates a virtual environment, installs the packages in `requirements.txt` plus PyInstaller, and
writes a single `dist\Androidbox.exe`. To run from source instead:

```powershell
python -m venv .venv
.venv\Scripts\pip install -r requirements.txt
.venv\Scripts\pythonw Androidbox.pyw
```

| Path | Role |
|---|---|
| `androidbox/installer.py` | Downloads and verifies the emulator, adb and the system image |
| `androidbox/instances.py` | Instances, ports, virtual hardware, backup and restore |
| `androidbox/emulator.py` | Starts and stops the emulator, adb and console commands |
| `androidbox/bridge.py` | The gRPC link: screen stream, touch and key input, sensors |
| `androidbox/keymap.py`, `gamepad.py` | Game controls and controller input |
| `androidbox/macros.py`, `browser.py` | Macros and the ad-free browser |
| `androidbox/updates.py` | Asks GitHub whether a newer release is out |
| `androidbox/ui/` | The windows: `window.py`, `popout.py` and `host.py` lay them out, `phone.py` draws Android |
| `androidbox/proto/` | Bindings generated from the emulator's gRPC definition |

## Credits

- The **Android Emulator**, its system images and its gRPC definition (`emulator_controller.proto`) are
  made by the Android Open Source Project and Google. The bindings in `androidbox/proto` are generated
  from that definition, which is licensed under the Apache License 2.0. The emulator and system images
  are downloaded from Google under the Android SDK License, which you accept on first run.
- The Android robot is reproduced or modified from work created and shared by Google and used according
  to terms described in the Creative Commons 3.0 Attribution License.
- **Firefox** is made by Mozilla, **uBlock Origin** by Raymond Hill and contributors, and **AdGuard DNS**
  by AdGuard. Androidbox only helps you install or use them.
- Built with **Qt for Python (PySide6)** and **gRPC**. Controller support comes from **SDL**, through
  PySDL2.

## License

Androidbox is released under the [MIT License](LICENSE).
