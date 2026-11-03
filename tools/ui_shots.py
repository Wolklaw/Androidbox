"""Renders Androidbox's pages to PNG files, for looking at a change to the UI without starting Android.

    python tools/ui_shots.py OUTPUT_FOLDER [--scale 1.5]

It runs the real window against a throwaway Androidbox folder, parked off-screen so it never gets in the
way, with the real Windows fonts. Nothing in your own Androidbox folder is read or changed.
"""
import os
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
os.environ["ANDROIDBOX_HOME"] = tempfile.mkdtemp(prefix="androidbox-shots-")

from PySide6.QtCore import QEvent  # noqa: E402
from PySide6.QtWidgets import QApplication, QWidget  # noqa: E402

from androidbox import emulator, installer, instances  # noqa: E402

# The throwaway folder has no Android tools in it, so pretend the PC is ready for them
installer.is_installed = lambda: True
emulator.hardware_acceleration = lambda: (True, "")

from androidbox.ui import tasks  # noqa: E402
from androidbox.ui.inspector import Inspector  # noqa: E402
from androidbox.ui.palette import Palette  # noqa: E402
from androidbox.ui.theme import Fonts, stylesheet  # noqa: E402
from androidbox.ui.window import MainWindow  # noqa: E402

PAGES = ("instances", "screen", "controls", "macros", "library", "settings")


def settle(app, window):
    # The window is parked off-screen, where Qt is slow to lay out what was just shown, so do it by hand
    for _ in range(3):
        app.processEvents()
        # Widgets that were deleted later have to be gone, or they are still in the picture
        app.sendPostedEvents(None, QEvent.Type.DeferredDelete)
        for widget in window.findChildren(QWidget):
            if widget.layout() and widget.isVisible():
                widget.layout().activate()
    app.processEvents()


def main():
    arguments = sys.argv[1:]
    if not arguments:
        sys.exit(__doc__)
    folder = Path(arguments[0])
    folder.mkdir(parents=True, exist_ok=True)
    app = QApplication([])
    Fonts.load()
    app.setStyleSheet(stylesheet())
    window = MainWindow()
    # Problems go to the console, not into a dialog that would end up in the picture
    tasks.relay.on_error = lambda details: print(details, file=sys.stderr, flush=True)
    window.resize(1280, 840)
    window.move(-4000, 0)
    window.show()
    app.processEvents()
    # A second instance, so the instance grid has more than one card
    window.add_controller(instances.create(window.instances, "Second", cores=4, ram=4096))
    first = next(iter(window.controllers), None)
    for name in PAGES:
        if name == "instances":
            window.select(None)
        else:
            window.select(first)
            window.show_page(name)
        settle(app, window)
        window.grab().save(str(folder / f"{name}.png"))
        print("saved", folder / f"{name}.png", flush=True)
    window.select(first)
    window.show_page("screen")
    inspector = Inspector(window)
    inspector.refresh(window.controllers[first])
    inspector.resize(272, 760)
    inspector.show()
    app.processEvents()
    inspector.grab().save(str(folder / "inspector.png"))
    inspector.hide()
    window.open_palette()
    settle(app, window)
    window.grab().save(str(folder / "palette.png"))
    field = window.findChild(Palette).field
    field.setText("prox")
    settle(app, window)
    window.grab().save(str(folder / "palette_search.png"))
    print("palette results for 'prox':", [window.findChild(Palette).results.item(i).text()
                                           for i in range(window.findChild(Palette).results.count())], flush=True)
    window.closing = True
    os._exit(0)


main()
