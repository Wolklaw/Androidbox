from PySide6.QtCore import Qt
from PySide6.QtWidgets import QComboBox, QLineEdit, QScrollArea, QVBoxLayout, QWidget

from .. import instances, macros
from .widgets import Toggle, button, card, column, divider, label, row

WIDTH = 272
MACRO_LIMIT = 5


def combo(options, current):
    box = QComboBox()
    for text, value in options:
        box.addItem(text, value)
    box.setCurrentIndex(max(0, box.findData(current)))
    box.setCursor(Qt.CursorShape.PointingHandCursor)
    return box


def short(package):
    return package.rsplit(".", 1)[-1] if package else ""


class Inspector(QWidget):
    """The things you reach for while a game is running, beside it instead of a page away: saved states,
    keeping the game running, a daily schedule, network conditions and macros."""

    def __init__(self, host):
        super().__init__()
        self.host = host
        self.setObjectName("Inspector")
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground)
        self.setFixedWidth(WIDTH)
        self.signature = None
        self.stats = None
        self.holder = QWidget()
        self.layout_ = QVBoxLayout(self.holder)
        self.layout_.setContentsMargins(12, 12, 12, 16)
        self.layout_.setSpacing(12)
        self.layout_.setAlignment(Qt.AlignmentFlag.AlignTop)
        scroll = QScrollArea()
        scroll.setWidget(self.holder)
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.addWidget(scroll)

    def refresh(self, controller):
        if controller is None:
            return
        instance = controller.instance
        states = controller.emulator.snapshots()
        shown = [macro["name"] for macro in macros.load()][:MACRO_LIMIT]
        signature = (instance.id, tuple(states), instance.keep_running, instance.network, instance.start_at,
                     instance.stop_at, controller.package, tuple(shown))
        if signature != self.signature:
            self.signature = signature
            self.build(controller, states, shown)
        usage = controller.usage
        self.stats.setText(f"{usage[0]:.0f}% CPU  ·  {usage[1]:.1f} GB" if usage else "")

    def build(self, controller, states, macro_names):
        host = self.host
        instance = controller.instance
        while self.layout_.count():
            item = self.layout_.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        self.stats = label("", "Small")
        self.layout_.addWidget(column(label(instance.name, "Subheading"), self.stats, spacing=2))

        chosen = combo([(name, name) for name in states] or [("None saved yet", "")], states[0] if states else "")
        chosen.setEnabled(bool(states))
        load = button("Load", lambda: host.load_snapshot(controller, chosen.currentData()), kind="secondary")
        load.setEnabled(bool(states))
        remove = button("Delete", lambda: host.delete_snapshot(controller, chosen.currentData()), kind="secondary")
        remove.setEnabled(bool(states))
        self.layout_.addWidget(card(
            label("Saved states", "Section"), chosen, row(load, remove, None),
            button("Save current state", lambda: host.save_snapshot(controller)), spacing=10))

        game = controller.package
        keep = Toggle(bool(instance.keep_running))
        keep.setEnabled(bool(game or instance.keep_running))
        keep.toggled.connect(lambda on: host.set_automation(controller, keep_running=(controller.package or "")
                                                            if on else ""))
        what = short(instance.keep_running or game) or "the game"
        times = []
        for key, text in (("start_at", "Start"), ("stop_at", "Stop")):
            field = QLineEdit(getattr(instance, key))
            field.setPlaceholderText("08:30")
            field.editingFinished.connect(lambda key=key, field=field: host.set_time(controller, key, field.text()))
            times.append(row(label(text, "Small"), field, spacing=6))
        self.layout_.addWidget(card(
            label("Automation", "Section"),
            row(label(f"Keep {what} running", "Muted", wrap=True), None, keep),
            divider(), label("Start and stop every day", "Small"), row(*times, spacing=10), spacing=10))

        network = combo([(name, key) for key, (name, _, _) in instances.NETWORK_PROFILES.items()], instance.network)
        network.currentIndexChanged.connect(lambda: controller.set_network(network.currentData()))
        self.layout_.addWidget(card(label("Network", "Section"), network, spacing=10))

        if macro_names:
            plays = [row(label(name, "Muted"), None,
                         button("Play", lambda name=name: controller.run_macro_named(name), kind="secondary"))
                     for name in macro_names]
            self.layout_.addWidget(card(label("Macros", "Section"), *plays, spacing=10))
        else:
            self.layout_.addWidget(card(label("Macros", "Section"),
                                        label("Record one with Ctrl+Shift+M and it shows up here.", "Small",
                                              wrap=True), spacing=10))
