import posixpath
from pathlib import Path

from PySide6.QtWidgets import QAbstractItemView, QComboBox, QFileDialog, QListWidget, QListWidgetItem, QSizePolicy

from .tasks import background
from .widgets import Modal, label, row

ROOT = "/sdcard"
PLACES = [("Internal storage", ROOT), ("Pictures", f"{ROOT}/Pictures"), ("Screenshots", f"{ROOT}/Pictures/Screenshots"),
          ("Camera photos", f"{ROOT}/DCIM"), ("Downloads", f"{ROOT}/Download"), ("Movies", f"{ROOT}/Movies"),
          ("Documents", f"{ROOT}/Documents")]
UP = ".."


class FileBrowser(Modal):
    """Looks through Android's shared storage and copies what you pick to a folder on the PC"""

    def __init__(self, parent, controller, notify):
        super().__init__(parent, "Save files from Android",
                         "Browse Android's storage, then copy files or whole folders to your PC.", width=580)
        self.controller = controller
        self.notify = notify
        self.path = ROOT
        places = QComboBox()
        for name, folder in PLACES:
            places.addItem(name, folder)
        places.activated.connect(lambda _: self.go(places.currentData()))
        self.where = label(ROOT, "Small")
        self.names = QListWidget()
        self.names.setFixedHeight(300)
        self.names.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.names.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
        self.names.itemDoubleClicked.connect(self.enter)
        self.add(row(places, None))
        self.add(self.where)
        self.add(self.names)
        self.add(label("Double-click a folder to open it. Select several files with Ctrl or Shift. With nothing "
                       "selected, Save copies the whole folder you're in.", "Small", wrap=True))
        self.cancel("Close")
        self.action("Save to PC…", self.save)
        self.go(ROOT)

    def go(self, folder):
        background(lambda: self.controller.emulator.listing(folder), lambda names: self.show_folder(folder, names))

    def show_folder(self, folder, names):
        if names is None:
            self.notify("Couldn't open that folder", "bad")
            return
        self.path = folder
        self.where.setText(folder)
        self.names.clear()
        if folder.rstrip("/"):
            self.add_item("⬑  Up one folder", UP)
        for name in names:
            self.add_item(("▸  " if name.endswith("/") else "     ") + name.rstrip("/"), name)
        if not names:
            self.add_item("This folder is empty", None)

    def add_item(self, text, name):
        item = QListWidgetItem(text)
        item.setData(256, name)
        self.names.addItem(item)

    def remote(self, name):
        return posixpath.join(self.path, name.rstrip("/"))

    def enter(self, item):
        name = item.data(256)
        if name == UP:
            self.go(posixpath.dirname(self.path.rstrip("/")) or "/")
        elif name and name.endswith("/"):
            self.go(self.remote(name))

    def save(self):
        chosen = [self.remote(item.data(256)) for item in self.names.selectedItems()
                  if item.data(256) not in (UP, None)]
        sources = chosen or [self.path]
        destination = QFileDialog.getExistingDirectory(self, "Save to", str(Path.home() / "Downloads"))
        if not destination:
            return False
        emulator = self.controller.emulator

        def work():
            return [emulator.pull(source, destination) for source in sources]

        def finished(results):
            failed = [reason for ok, reason in results if not ok]
            if failed:
                self.notify(f"Couldn't copy everything: {failed[0]}", "bad")
            else:
                self.notify(f"Saved {len(sources)} {'item' if len(sources) == 1 else 'items'} to {destination}", "good")

        self.notify(f"Copying to {destination}…", "text")
        background(work, finished)
        return False
