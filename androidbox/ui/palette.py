from PySide6.QtCore import QEvent, Qt, QTimer
from PySide6.QtWidgets import QLineEdit, QListWidget, QListWidgetItem

from .widgets import Modal

RESULT_LIMIT = 12


class Palette(Modal):
    """One search box for everything: pages, instances, actions, settings, saved states and macros. Each
    command is (title, what kind of thing it is, what to do)."""

    def __init__(self, parent, commands, secret=None, on_secret=None):
        super().__init__(parent, "Search everything", width=580)
        self.commands = commands
        self.secret = secret
        self.on_secret = on_secret
        self.field = QLineEdit()
        self.field.setPlaceholderText("Try: screenshot, proxy, start, saved state")
        self.field.textChanged.connect(self.narrow)
        self.field.installEventFilter(self)
        self.results = QListWidget()
        self.results.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.results.itemActivated.connect(self.run)
        self.results.itemClicked.connect(self.run)
        self.add(self.field)
        self.add(self.results)
        self.narrow("")

    def open(self):
        super().open()
        self.field.setFocus()
        return self

    def narrow(self, text):
        words = text.lower().split()
        ranked = []
        for index, (title, kind, action) in enumerate(self.commands):
            haystack = f"{title} {kind}".lower()
            if all(word in haystack for word in words):
                # Titles that start with what was typed come first, then the order they were listed in
                ranked.append((not (words and title.lower().startswith(words[0])), index, title, kind, action))
        self.results.clear()
        key = self.secret(text) if self.secret else None
        if key:
            item = QListWidgetItem(f"{text.strip()}    ·    Easter egg")
            item.setData(Qt.ItemDataRole.UserRole, lambda key=key: self.on_secret(key))
            self.results.addItem(item)
        for _, _, title, kind, action in sorted(ranked, key=lambda found: found[:2])[:RESULT_LIMIT]:
            item = QListWidgetItem(f"{title}    ·    {kind}")
            item.setData(Qt.ItemDataRole.UserRole, action)
            self.results.addItem(item)
        # As tall as what was found, so a short list isn't a big empty box
        self.results.setFixedHeight(max(1, min(self.results.count(), 8)) * 40 + 12)
        if self.results.count():
            self.results.setCurrentRow(0)

    def run(self, item=None):
        item = item or self.results.currentItem()
        if not item:
            return
        action = item.data(Qt.ItemDataRole.UserRole)
        self.close_modal()
        # After the palette has gone, so a dialog the command opens isn't covered by it
        QTimer.singleShot(0, action)

    def eventFilter(self, watched, event):
        if watched is not self.field:
            return super().eventFilter(watched, event)
        if event.type() == QEvent.Type.KeyPress:
            key = event.key()
            if key in (Qt.Key.Key_Down, Qt.Key.Key_Up):
                step = 1 if key == Qt.Key.Key_Down else -1
                row = max(0, min(self.results.count() - 1, self.results.currentRow() + step))
                self.results.setCurrentRow(row)
                return True
            if key in (Qt.Key.Key_Return, Qt.Key.Key_Enter):
                self.run()
                return True
            if key == Qt.Key.Key_Escape:
                self.close_modal()
                return True
        # Everything else from the field is none of the modal's business: its own filter resizes it to
        # whatever sent the event, and that is only right for the window it covers
        return False
