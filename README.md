<p align="center">
  <img src="docs/banner.png" alt="Androidbox: Android on your PC. No ads." width="720">
</p>

<p align="center">
  <b>An ad-free Android emulator for Windows.</b><br>
  Google Play, game controls, multiple instances, and nothing trying to sell you anything.
</p>

<p align="center">
  <a href="https://github.com/Wolklaw/Androidbox/releases/latest"><b>Download the Androidbox installer</b></a><br>
  Windows 10 or 11 · free · MIT license
</p>

---

Androidbox runs **Google's official Android Emulator**, the same engine inside Android Studio, on your
graphics card, and shows Android in one clean window. There are no ads, no accounts to create, no
bundled apps and no telemetry. Everything it needs downloads straight from Google, and everything it
stores stays in one folder you can delete.

<p align="center"><img src="docs/screen.png" alt="Androidbox running Android 15" width="820"></p>

## Getting started

**You need:**
- Windows 10 or 11, 64-bit
- **Windows Hypervisor Platform** turned on. Androidbox tells you if it's off and opens the right
  settings page
- A graphics card with current drivers
- About 4 GB of disk space for Android, plus up to 10 GB per instance

**Then:**
1. Download `Androidbox-Setup-<version>.exe` from the
   [latest release](https://github.com/Wolklaw/Androidbox/releases/latest).
2. Run it. Windows may warn that the app is from an unknown publisher, because it isn't code-signed.
   Choose **More info**, then **Run anyway**.
3. Follow the setup wizard. It installs Androidbox in `Program Files` for everyone on the PC and asks
   Windows for permission once. No admin rights? Choose **Install for me only** on the first page and it
   installs in your own folder instead. If Windows Hypervisor Platform is off, the wizard offers to turn
   it on for you.
4. Open Androidbox and choose **Download and install**. This happens once.
5. Press **Start Android**.

Closing Androidbox saves and shuts down every running Android, unless you choose to keep it running in
the tray. Androidbox keeps itself up to date (see [Updates](#updates)), and you can also run a newer
installer over the old one. Your instances and settings stay where they are, and an older per-user install
is replaced.

## Features

### Android 16 with Google Play

Runs on your GPU at 60, 90, 120, 144 or 240 FPS, with ARM apps and games supported. For older games
that only ship 32-bit ARM code, create an instance with **Android 11**, which runs both 32-bit and
64-bit ARM apps.

Each instance has its own hardware, set in its Settings:

- **Processor and memory** up to what your PC has, and new instances start with a sensible share of it.
- **Display** from six presets, or any size from 320 to 3840 pixels with your own density.
- **Storage** of 16, 32, 64 or 128 GB, which only takes the space Android actually uses. Big games need
  64 GB or more.
- **Graphics**: your graphics card, Automatic, or Software when a GPU crashes the emulator.

### Game controls

Saved separately for every game:

| Control | What it does |
|---|---|
| Tap | A key or controller button taps a spot on the screen |
| Joystick | WASD (rebindable), the D-pad or the left stick moves |
| Aim | Shooter mode: press its key (F1) and the mouse turns the camera. The right stick aims too |
| Look | Free look: the mouse turns the camera only while you hold its key (Alt) |
| Fire and Scope | The left and right mouse buttons while aiming |
| Skill | MOBA casting: hold the key, point with the mouse, release to cast |
| Turbo | Hold the key to tap the same spot rapidly |
| Hold | Press once to hold a spot down and again to let go, for sprint and auto-run |
| Swipe | One key performs a drag along an arrow you place, for dodges and lane changes |
| Tilt | Keys, or the left stick, tip the device like a steering wheel, for racing games |
| Macro | One key plays a macro you recorded, and stops it if you press it again |
| Zoom | Ctrl and the mouse wheel pinch in and out, with no setup |

**Starter layouts** give a game a head start: Shooter, MOBA, Racing, Action platformer and Endless runner
place the usual controls, and you move each one onto the game's real button. Layouts export to a file, so
you can share them or move them to another instance or PC.

<p align="center"><img src="docs/controls.png" alt="Placing game controls on the screen" width="820"></p>

### Controllers

Xbox, PlayStation and Switch Pro controllers, 8BitDo pads and most other gamepads work straight away,
wired or over Bluetooth. Bind their buttons and triggers like keys. Plug in two and both work at once,
which is handy for couch co-op. Without game controls they navigate Android: A is Enter, B is Back,
Start is Home.

### Macros

Record taps, swipes and key presses once, then play them back at half, normal, double or four times
the speed. Repeat a macro a set number of times or until you stop it, with a wait of your choice between
rounds, which suits idle and farming games. **Edit steps** shows each tap, swipe, hold and key press so
you can change how long it waits or remove it. Give a macro a hotkey, and turn on **Works in any
program** to fire it while another program has the keyboard.

### Profiles and sync

A profile keeps your game control layouts, macros, instance presets and preferences together. Make one
for yourself, one for streaming, one for the family PC, and switch from the menu at the top right.

- Save an instance's hardware as a **preset** and start new instances from it.
- Profiles export to a single file.
- Profiles **sync between PCs** through any folder that OneDrive, Dropbox, Google Drive or Syncthing
  already keeps up to date. Pick the folder once on each PC and your layouts, macros and presets follow
  you. There is no server and no login, and Androidbox uploads nothing itself.

### Several Androids at once

Every instance has its own apps, accounts and settings. Create, clone, back up to a single file,
restore, start them all at once, open any instance in its own window, tile them side by side, and
mirror your input to all of them at the same time.

### Apps and games

The **Apps** page lists what's installed on an instance. Open a game, give it its own frame rate that
applies while it's in front, uninstall it, or put a shortcut to it on your desktop. A shortcut starts the
instance if it's off and opens that game, even when Androidbox is already running.

### Updates

Androidbox checks GitHub for a newer release when it starts and every few hours while it runs. When one
is out, it downloads the installer in the background and checks it against the checksum GitHub published
for it. It then asks whether to restart and install: Androidbox saves your Androids first, Windows asks
for permission if it's installed in `Program Files`, and Androidbox opens again afterwards. It never
restarts on its own. Turn the checks or the automatic download off on the **All instances** page, where
**Look for an update now** also checks on demand.

Every push to `main` that raises the version publishes a new release, which is how an update gets to
you.

### Stays out of the way

- **Tray**: keep Android running when you close the window, so idle games keep going. Quit from the
  tray icon.
- **Start with Windows**: Androidbox opens in the tray and starts the instances you marked to start
  with it.
- **Boss key**: one shortcut that works in any program hides every Androidbox window and mutes Android.
  Press it again to bring everything back.
- **Mute** one instance, and **keep Androidbox on top** of other windows.

<p align="center"><img src="docs/instances.png" alt="The instance manager" width="820"></p>

### No ads, two ways

- **Block ads** filters ad networks inside every app and game through AdGuard DNS.
- **Ad-free browser** installs Firefox from Mozilla, makes it the default browser and opens uBlock
  Origin for you. One tap later, websites are ad-free, YouTube included.

### Let Claude Code test your apps

Off by default. Turn on **Let Claude Code control Android** in Settings and Androidbox writes a helper
script to `%LOCALAPPDATA%\Androidbox\claude`. Claude Code on your PC can then take screenshots, read
what's on screen, tap, swipe, type, install and launch apps, and read logs on your running instances.
Turn the switch off and the helper is deleted, and it refuses to run while the switch is off.

### Everything else

- Screenshots, and screen recording with no time limit (saved in 3-minute parts)
- Drag and drop to install `.apk`, `.apks` and `.xapk` files, game data included
- File import and export: add files to Android, or browse its storage and save files and folders to your PC
- A clipboard shared with Windows
- Your webcam as Android's camera
- Rotate, shake, volume and GPS location
- Full screen, an FPS counter that also shows how much processor and memory the emulator uses, and eco
  mode for idle games
- Move everything Androidbox stores to another drive when your C: drive runs short
- Automatic updates, with a check for new releases that you can turn off

<p align="center"><img src="docs/settings.png" alt="Per-instance settings" width="820"></p>

## How it works

<p align="center">
  <img src="docs/how-it-works.png" alt="The Androidbox window gets screen frames from the Android Emulator through shared memory. It sends touch, keys and sensors over gRPC, installs and settings over adb, and recording and shutdown over the emulator console. On the first run, the emulator is downloaded from dl.google.com." width="520">
</p>

1. **First run.** Androidbox reads Google's SDK package index, downloads the emulator, adb and the
   Android 16 system image (about 1.9 GB), checks every file's checksum, and unpacks them into
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

## Using it

- **Mouse:** left-click taps, drag swipes, the wheel scrolls, right-click is Back, middle-click is Home.
- **Keyboard:** typing goes straight to Android, and Esc is Back.
- **Files:** drop them on the screen.

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

### Set up a game

Open the game, press Ctrl+Shift+E, click where a button is and press the key you want for it.
**Add control** at the top adds a joystick, aim, look, fire, scope, skill, turbo or swipe control. Drag
controls to move them (drag the tip of a swipe arrow to aim it), scroll over one to resize it, and
right-click to remove it. Press Done, and the layout is saved for that game.

### Record a macro

Press Ctrl+Shift+M, play, and press it again. On the Macros page you can rename a macro, change its
speed and click the hotkey box to give it a shortcut such as Ctrl+1. Macros belong to your profile and
remember the display they were recorded on, so they only play on instances with the same one.

### Pick a hotkey that works anywhere

Open **Macros**, click a macro's hotkey box and press something like Ctrl+1, then turn on **Works in any
program**. Windows only lets a program claim a shortcut that includes Ctrl, Alt, Shift or Win, and not
one another program already has.

### Share a profile between PCs

Open the profile menu at the top right, or Manage profiles for the full page. Choose **Choose a folder**
under Sync between PCs, on each PC, and pick a folder your cloud storage syncs. Instances, apps and
accounts inside Android are not part of a profile, use Back up for those.

## Tips

- **Google Play needs a Google account** to install or update apps, and some Google apps that come with
  Android ask for an update before they open. If you'd rather not sign in, install apps from `.apk`
  files and use the ad-free browser for YouTube.
- **Games need more?** Give the instance more cores and memory in Settings, or switch it to the Tablet
  display for landscape games. A game that won't install for lack of room needs more **Storage**, which
  is chosen when an instance is created, and changing it erases that instance.
- **Android crashes as it starts?** In Settings, set Graphics to Automatic, then Software.
- **Idle game in the background?** Turn on eco mode for that instance.
- **A game won't install or says the device isn't supported?** It probably ships 32-bit ARM code only.
  Create a new instance, pick Android 11, and install it there.
- **High refresh rate monitor?** Set the instance's frame rate to 144 or 240 FPS in Settings. Games
  that cap their own frame rate stay capped.

## FAQ

<details>
<summary><b>Is it really ad-free?</b></summary>

Androidbox itself has no ads and never will. Inside Android, Block ads stops ad networks in apps and
games, and the ad-free browser handles websites and YouTube. Ads that apps serve from their own servers
can't be filtered by any DNS blocker.

</details>

<details>
<summary><b>Does it support root?</b></summary>

No. The Google Play images can't be rooted. The upside is that banking apps and games with root
detection keep working.

</details>

<details>
<summary><b>Do I need an account?</b></summary>

No. A profile is just a name on your PC, with no password and no sign-in, and nothing about it leaves
your PC unless you pick a sync folder. Anyone who can open that folder can read the profile, so don't
share it with people you wouldn't hand your game layouts to.

</details>

<details>
<summary><b>Where is my data, and how do I remove it?</b></summary>

Everything lives in `%LOCALAPPDATA%\Androidbox`, apart from the program itself, which is in
`Program Files`. To keep it somewhere else, open **All instances** and use **Where Androidbox keeps its
files**: it copies everything to a drive you pick, restarts, and then removes the old copy. Uninstall
Androidbox from **Settings > Apps** and it asks whether to delete that folder too, with all its
instances. It keeps the folder unless you say yes, because the Android images take a while to download
again. If you turned on sync, a copy of your profiles also sits in the folder you chose, in
`Androidbox Profiles`.

</details>

<details>
<summary><b>Can I run it without Google Play?</b></summary>

Yes. Skip signing in and install apps from `.apk` files.

</details>

<details>
<summary><b>Does Pokémon GO work?</b></summary>

No, and it won't. Niantic blocks emulators on purpose: the game checks Play Integrity and its own
anti-cheat, and refuses to run on any emulator, BlueStacks included. Getting around that means breaking
their terms of service and risking a ban, so Androidbox doesn't try. The GPS location tool is meant for
testing apps and games that allow it.

</details>

<details>
<summary><b>Why Android 16, and not the newest Android?</b></summary>

Google publishes Play Store images for new versions long before they are stable enough for games.
Android 16 is the newest stable one, and its ARM translator runs games that crash on Android 15, such
as BitLife. Android 11 stays available because it's the last one that runs 32-bit ARM apps.

</details>

<details>
<summary><b>An ARM game crashes on my Android 15 instance</b></summary>

On a PC, Android runs ARM-only games through Google's ARM translator, and the one in Android 15 crashes
some Unity games a few seconds after they start. Create an Android 16 instance and install the game
there. Apps and accounts don't carry over between Android versions, so you sign in to Google Play
again on the new instance.

</details>

## Building

```powershell
.\build.ps1
```

This creates a virtual environment, installs the packages in `requirements.txt` plus PyInstaller, bundles
the app with PyInstaller, and wraps it in a setup wizard with [Inno Setup 6](https://jrsoftware.org/isinfo.php)
(`winget install JRSoftware.InnoSetup`). The installer lands in `dist\Androidbox-Setup-<version>.exe`, and
the version comes from `androidbox/__init__.py`. The wizard's artwork is drawn by `installer/make_art.py`,
and the PNGs it writes are committed. Raise `VERSION` and push to `main`, and
`.github/workflows/release.yml` builds the installer the same way and publishes it as release `v<version>`,
which installed copies then offer to download. Dependencies are pinned in `requirements.txt` so that
release builds match what was tested. To run from source instead:

```powershell
python -m venv .venv
.venv\Scripts\pip install -r requirements.txt
.venv\Scripts\pythonw Androidbox.pyw
```

<details>
<summary><b>What's in the source</b></summary>

- `androidbox/installer.py`: downloads and verifies the emulator, adb and the system image
- `androidbox/instances.py`: instances, ports, virtual hardware, backup and restore
- `androidbox/emulator.py`: starts and stops the emulator, adb and console commands
- `androidbox/bridge.py`: the gRPC link, with the screen stream, touch and key input, and sensors
- `androidbox/keymap.py`, `gamepad.py`: game controls and controller input
- `androidbox/profiles.py`, `settings.py`: profiles, presets, per-game settings and the sync folder, plus
  preferences
- `androidbox/macros.py`, `browser.py`: macros, with their editing, and the ad-free browser
- `androidbox/system.py`, `relocate.py`, `hotkeys.py`: what the PC has, shortcuts and Windows startup,
  moving the files to another drive, and shortcuts that work in any program
- `androidbox/claude.py`: the Claude Code helper script
- `androidbox/updates.py`: asks GitHub for the newest release, then downloads and verifies its installer
- `androidbox/ui/`: the windows. `window.py`, `popout.py` and `host.py` lay them out, `phone.py` draws
  Android, and `files.py` browses Android's storage
- `androidbox/proto/`: bindings generated from the emulator's gRPC definition
- `build.ps1`, `setup.iss`, `installer/`: build the app and its Windows installer, and the wizard's art

</details>

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
