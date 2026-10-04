import time
from pathlib import Path

from PySide6.QtCore import QPoint, QStandardPaths, Qt, QTimer, QUrl
from PySide6.QtGui import QDesktopServices, QIcon
from PySide6.QtWidgets import (QApplication, QComboBox, QFileDialog, QFrame, QHBoxLayout, QLineEdit, QMainWindow,
                               QMenu, QScrollArea, QStackedWidget, QVBoxLayout, QWidget)

from .. import VERSION, browser, claude, emulator, installer, instances, keymap, macros, paths, profiles, settings, updates
from . import tasks
from .controller import Controller, plural
from .host import ScreenActions
from .pages import (ControlsPage, InstancesPage, MacrosPage, NoAccelerationPage, ProfilePage, Progress, ScreenPage,
                    SettingsPage, SetupPage, show_text)
from .popout import PopoutWindow
from .theme import COLORS, ICONS
from .widgets import (STATUS_COLORS, InstanceButton, Modal, NavButton, ProfileButton, Toast, ToolButton, button, column,
                      confirm, divider, glyph_css, label, row, style_title_bar)

PAGES = {
    "screen": ("screen", "Screen"),
    "controls": ("game", "Game controls"),
    "macros": ("macro", "Macros"),
    "settings": ("settings", "Settings"),
    "instances": ("apps", "All instances"),
    "profile": ("person", "Profile"),
}

GLOBAL_PAGES = ("instances", "profile")

STATES = {"on": "Running", "booting": "Starting…", "stopping": "Shutting down…", "crashed": "Stopped unexpectedly"}
BACKUP_FILTER = "Androidbox backup (*.androidbox)"
LAYOUT_FILTER = "Game controls (*.json)"
PROFILE_FILTER = f"Androidbox profile (*{profiles.EXTENSION})"


def documents():
    return Path(QStandardPaths.writableLocation(QStandardPaths.StandardLocation.DocumentsLocation))


class MainWindow(QMainWindow, ScreenActions):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Androidbox")
        self.setWindowIcon(QIcon(str(paths.ICON)))
        self.resize(1280, 840)
        self.setMinimumSize(980, 660)
        profiles.start()
        self.prefs = settings.load()
        if self.prefs["claude_access"]:
            claude.enable()
        self.instances = instances.load()
        self.controllers = {}
        self.instance_buttons = {}
        self.popouts = {}
        self.current = None
        self.page = "instances"
        self.closing = False
        self.was_maximized = False
        tasks.relay.on_error = self.report

        central = QWidget()
        self.setCentralWidget(central)
        root = QHBoxLayout(central)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)
        root.addWidget(self.build_sidebar())
        main = QWidget()
        main.setObjectName("Main")
        main.setAttribute(Qt.WidgetAttribute.WA_StyledBackground)
        main_layout = QVBoxLayout(main)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        main_layout.addWidget(self.build_header())
        self.stack = QStackedWidget()
        main_layout.addWidget(self.stack, 1)
        root.addWidget(main, 1)
        self.toaster = Toast(central)

        self.screen = ScreenPage(self)
        self.pages = {
            "screen": self.screen,
            "controls": ControlsPage(self),
            "macros": MacrosPage(self),
            "settings": SettingsPage(self),
            "instances": InstancesPage(self),
            "profile": ProfilePage(self),
        }
        self.setup = SetupPage(self)
        self.no_acceleration = NoAccelerationPage(self)
        for page in (*self.pages.values(), self.setup, self.no_acceleration):
            self.stack.addWidget(page)
        self.install_shortcuts()
        self.profile_timer = QTimer(self, interval=3000, timeout=self.watch_profile)
        self.profile_timer.start()

        if installer.is_installed():
            self.open_instances()
        else:
            self.show_onboarding(self.setup)
            self.setup.begin()

    def showEvent(self, event):
        style_title_bar(self)

    def build_sidebar(self):
        self.sidebar = QWidget()
        self.sidebar.setObjectName("Sidebar")
        self.sidebar.setAttribute(Qt.WidgetAttribute.WA_StyledBackground)
        self.sidebar.setFixedWidth(248)
        layout = QVBoxLayout(self.sidebar)
        layout.setContentsMargins(10, 0, 10, 12)
        layout.setSpacing(2)

        logo = label()
        logo.setPixmap(QIcon(str(paths.ICON)).pixmap(22, 22))
        brand = row(logo, label("Androidbox", "Brand"), None, spacing=10, margins=(8, 0, 0, 0))
        brand.setFixedHeight(56)
        layout.addWidget(brand)

        add = ToolButton(ICONS["add"], "Create an instance", self.new_instance)
        add.setFixedSize(26, 26)
        layout.addWidget(row(label("Instances", "Section"), None, add, margins=(8, 4, 2, 2)))
        self.instance_list = QVBoxLayout()
        self.instance_list.setContentsMargins(0, 0, 0, 0)
        self.instance_list.setSpacing(2)
        list_holder = QWidget()
        list_holder.setLayout(self.instance_list)
        self.instance_scroll = QScrollArea()
        self.instance_scroll.setWidget(list_holder)
        self.instance_scroll.setWidgetResizable(True)
        self.instance_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        layout.addWidget(self.instance_scroll)
        self.overview = NavButton(ICONS["apps"], "All instances")
        self.overview.clicked.connect(lambda: self.select(None))
        layout.addWidget(self.overview)

        self.page_section = QWidget()
        pages_layout = QVBoxLayout(self.page_section)
        pages_layout.setContentsMargins(0, 10, 0, 0)
        pages_layout.setSpacing(2)
        pages_layout.addWidget(divider())
        pages_layout.addSpacing(8)
        self.page_title = label("", "Section")
        self.page_title.setContentsMargins(8, 0, 0, 4)
        pages_layout.addWidget(self.page_title)
        self.nav_buttons = {}
        for name in ("screen", "controls", "macros", "settings"):
            glyph, text = PAGES[name]
            nav = NavButton(ICONS[glyph], text)
            nav.clicked.connect(lambda _=False, page=name: self.show_page(page))
            self.nav_buttons[name] = nav
            pages_layout.addWidget(nav)
        layout.addWidget(self.page_section)
        layout.addStretch(1)

        self.status = label("", "Small")
        self.status.setContentsMargins(8, 0, 0, 6)
        self.power = button("Start Android", self.toggle_power)
        self.power_area = column(self.status, self.power, spacing=0)
        layout.addWidget(self.power_area)
        return self.sidebar

    def build_header(self):
        self.header = QFrame()
        self.header.setObjectName("Header")
        self.header.setFixedHeight(52)
        layout = QHBoxLayout(self.header)
        layout.setContentsMargins(20, 0, 20, 0)
        layout.setSpacing(10)
        self.header_icon = label("")
        self.header_icon.setStyleSheet(f"color: {COLORS['faint']}; {glyph_css(17)}")
        self.header_title = label("", "Title")
        self.header_detail = label("", "Small")
        layout.addWidget(self.header_icon)
        layout.addWidget(self.header_title)
        layout.addWidget(self.header_detail)
        layout.addStretch(1)
        self.profile_chip = ProfileButton()
        self.profile_chip.setToolTip("Your profile: game controls, macros, presets and preferences")
        self.profile_chip.clicked.connect(self.open_profile_menu)
        self.show_profile_name()
        layout.addWidget(self.profile_chip)
        return self.header

    def run(self, work, then=None, failed=None):
        tasks.background(work, then, failed)

    def later(self, callback):
        tasks.on_main_thread(callback)

    def toast(self, text, tone="text"):
        self.toaster.show_message(text, tone)

    def dialog_parent(self):
        return self.centralWidget()

    def report(self, details):
        paths.DATA.mkdir(parents=True, exist_ok=True)
        paths.CRASH_LOG.write_text(details)
        modal = Modal(self.dialog_parent(), "Something went wrong", details.strip().splitlines()[-1])
        modal.action("OK")
        modal.open()

    def active(self):
        return self.controllers.get(self.current)

    def show_onboarding(self, page):
        self.sidebar.hide()
        self.header.hide()
        self.stack.setCurrentWidget(page)

    def open_instances(self):
        self.sidebar.show()
        self.header.show()
        if not self.instances:
            instances.create(self.instances, "Main")
        for instance in self.instances:
            self.add_controller(instance)
        selected = self.prefs["selected"]
        self.select(selected if selected in self.controllers else self.instances[0].id)
        self.check_acceleration()
        self.check_for_updates()
        if profiles.sync_missing():
            self.toast("Your sync folder isn't available. Using this PC's copy of your profiles for now", "bad")

    def setup_finished(self):
        self.open_instances()
        if self.active():
            self.active().start()

    def check_acceleration(self):
        def checked(result):
            ok, reason = result
            if not ok:
                self.show_onboarding(self.no_acceleration)
            elif self.stack.currentWidget() is self.no_acceleration:
                self.sidebar.show()
                self.header.show()
                self.select(self.current)

        self.run(emulator.hardware_acceleration, checked)

    def add_controller(self, instance):
        controller = Controller(instance, self.instances)
        self.controllers[instance.id] = controller
        controller.changed.connect(lambda: self.controller_changed(controller))
        controller.app_changed.connect(lambda: self.app_changed(controller))
        controller.macros_changed.connect(lambda: self.macros_changed(controller))
        controller.image_missing.connect(lambda: self.get_image(controller))
        controller.notify.connect(self.toast)
        item = InstanceButton(instance)
        item.clicked.connect(lambda: self.select(instance.id))
        self.instance_buttons[instance.id] = item
        self.instance_list.addWidget(item)
        self.fit_instance_list()
        return controller

    def remove_controller(self, controller):
        controller.timer.stop()
        controller.detach()
        del self.controllers[controller.instance.id]
        self.instance_buttons.pop(controller.instance.id).deleteLater()
        self.fit_instance_list()

    def fit_instance_list(self):
        rows = min(len(self.instance_buttons), 6)
        self.instance_scroll.setFixedHeight(rows * 44 + max(rows - 1, 0) * 2)

    def select(self, instance_id):
        if instance_id not in self.controllers:
            instance_id = None
        if instance_id != self.current:
            target = self.controllers.get(instance_id)
            self.screen.phone.show_controller(None if instance_id in self.popouts else target)
        self.current = instance_id
        self.prefs["selected"] = instance_id
        settings.save(self.prefs, "selected")
        self.overview.setChecked(instance_id is None)
        for key, item in self.instance_buttons.items():
            item.setChecked(key == instance_id)
        self.page_section.setVisible(instance_id is not None)
        self.power_area.setVisible(instance_id is not None)
        if instance_id:
            self.page_title.setText(self.active().instance.name)
        self.update_power()
        self.show_page("screen" if instance_id else "instances")
        self.update_mirrors()

    def update_power(self):
        controller = self.active()
        if not controller:
            return
        state = controller.state
        color = STATUS_COLORS.get(state, COLORS["dim"])
        self.status.setText(f"<span style='color:{color}'>●</span>&nbsp; {STATES.get(state, 'Off')} · "
                            f"{controller.instance.android}")
        off = state in ("off", "crashed")
        self.power.setText("Start Android" if off else "Stop Android")
        self.power.setProperty("kind", None if off else "secondary")
        self.power.setEnabled(state != "stopping")
        self.power.style().unpolish(self.power)
        self.power.style().polish(self.power)

    def show_page(self, name):
        controller = self.active()
        if not controller and name not in GLOBAL_PAGES:
            name = "instances"
        if self.screen.phone.editing and name != "screen":
            self.screen.phone.finish_editing()
        self.page = name
        page = self.pages[name]
        if name in GLOBAL_PAGES:
            page.refresh()
        elif name == "screen":
            page.refresh(controller, controller.instance.id in self.popouts)
        else:
            page.refresh(controller)
        self.stack.setCurrentWidget(page)
        for key, nav in self.nav_buttons.items():
            nav.setChecked(key == name)
        self.overview.setChecked(self.current is None and name == "instances")
        self.update_header()

    def show_screen(self):
        if self.page != "screen":
            self.show_page("screen")

    def update_header(self):
        glyph, title = PAGES[self.page]
        controller = self.active()
        detail = ""
        if self.page == "screen" and controller and controller.on:
            detail = controller.package or ""
        elif self.page == "instances":
            running = sum(1 for c in self.controllers.values() if c.state == "on")
            detail = f"{running} of {len(self.controllers)} running"
        self.header_icon.setText(ICONS[glyph])
        self.header_title.setText(title)
        self.header_detail.setText(detail)

    def controller_changed(self, controller):
        item = self.instance_buttons.get(controller.instance.id)
        if item:
            item.set_state(controller.state)
        popout = self.popouts.get(controller.instance.id)
        if popout:
            popout.refresh()
        if self.page == "instances":
            self.pages["instances"].refresh()
            self.update_header()
        if controller is self.active():
            self.update_power()
            self.update_header()
            if self.page in ("screen", "settings", "macros", "controls"):
                self.show_page(self.page)
        self.update_mirrors()

    def app_changed(self, controller):
        if controller is self.active():
            self.update_header()
            if self.page == "controls":
                self.pages["controls"].refresh(controller)

    def macros_changed(self, controller):
        if controller is self.active():
            if self.page == "macros":
                self.pages["macros"].refresh(controller)
            self.refresh_tools()
        popout = self.popouts.get(controller.instance.id)
        if popout:
            popout.refresh_tools()

    def controls_changed(self):
        if self.page == "controls" and self.active():
            self.pages["controls"].refresh(self.active())
        self.screen.phone.update()
        for popout in self.popouts.values():
            popout.screen.phone.update()

    def set_pref(self, key, value):
        self.prefs[key] = value
        settings.save(self.prefs, key)
        if key == "claude_access":
            claude.enable() if value else claude.disable()
        if key == "sync_input":
            self.update_mirrors()
        self.refresh_tools()
        self.screen.phone.update()
        for popout in self.popouts.values():
            popout.refresh_tools()
            popout.screen.phone.update()

    def update_mirrors(self):
        active = self.active()
        for controller in self.controllers.values():
            if controller.bridge:
                controller.bridge.mirrors = []
        if active and active.bridge and self.prefs["sync_input"]:
            active.bridge.mirrors = [c.bridge for c in self.controllers.values() if c is not active and c.bridge]

    def toggle_power(self):
        controller = self.active()
        if controller:
            if controller.state in ("off", "crashed"):
                controller.start()
            else:
                controller.stop()

    def pop_out(self, controller):
        key = controller.instance.id
        if key in self.popouts:
            self.popouts[key].raise_()
            self.popouts[key].activateWindow()
            return
        if key == self.current:
            self.screen.phone.show_controller(None)
        window = PopoutWindow(self, controller)
        self.popouts[key] = window
        window.show()
        if key == self.current:
            self.show_page(self.page)
        self.refresh_tools()

    def toggle_popout(self):
        controller = self.active()
        if not controller:
            return
        popout = self.popouts.get(controller.instance.id)
        if popout:
            popout.close()
        else:
            self.pop_out(controller)

    def docked(self, controller):
        self.popouts.pop(controller.instance.id, None)
        if controller is self.active() and not self.closing:
            self.screen.phone.show_controller(controller)
            self.show_page(self.page)

    def set_up_browser(self, controller):
        if not controller.on:
            self.toast("Start Android first")
            return
        progress = Progress(self.dialog_parent(), "Ad-free browser",
                            "Getting Firefox from Mozilla, then opening uBlock Origin in it.")
        last = [0.0]

        def report(stage, done, total):
            now = time.monotonic()
            if stage == "download" and now - last[0] < 0.1 and done < total:
                return
            last[0] = now
            if stage == "download":
                text, fraction = f"Downloading Firefox · {done / 1e6:,.0f} of {total / 1e6:,.0f} MB", done / total
            else:
                text, fraction = "Installing Firefox…", 1.0
            self.later(lambda: progress.update_progress(text, fraction))

        def finished(_):
            progress.done("One more tap", "Firefox is now your browser and it's open on uBlock Origin. Tap "
                          "Add to Firefox, then Add. After that, ads are blocked on every website, YouTube included.")
            if controller is self.active():
                self.show_page("screen")

        self.run(lambda: browser.set_up(controller.emulator, report), finished,
                 lambda error: progress.done("Couldn't set up Firefox", str(error)))

    def check_for_updates(self):
        if not self.prefs["check_updates"]:
            return

        def found(result):
            version, url = result
            if not updates.newer(version) or self.prefs["skipped_version"] == version:
                return
            modal = Modal(self.dialog_parent(), f"Androidbox {version} is out",
                          f"You have {VERSION}. The new version is on GitHub, ready to download.")
            modal.action("Skip this version", lambda: self.set_pref("skipped_version", version), kind="secondary")
            modal.action("Download", lambda: QDesktopServices.openUrl(QUrl(url)))
            modal.open()

        self.run(updates.latest, found, lambda _: None)

    def export_controls(self, package):
        file, _ = QFileDialog.getSaveFileName(self, "Export game controls", str(documents() / f"{package}.json"),
                                              LAYOUT_FILTER)
        if file:
            keymap.export(package, file)
            self.toast(f"Saved the layout to {Path(file).name}", "good")

    def import_controls(self, package):
        file, _ = QFileDialog.getOpenFileName(self, "Import game controls", str(documents()), LAYOUT_FILTER)
        if not file:
            return
        try:
            count = keymap.import_layout(package, file)
        except (OSError, ValueError, TypeError, KeyError):
            self.toast("That file isn't a game controls layout", "bad")
            return
        for phone in [self.screen.phone, *(popout.screen.phone for popout in self.popouts.values())]:
            if phone.package == package:
                phone.load_controls()
        self.controls_changed()
        self.toast(f"Imported {count} controls for {package}", "good")

    def arrange(self):
        running = [controller for controller in self.controllers.values() if controller.on]
        if not running:
            return
        for controller in running:
            self.pop_out(controller)
        area = self.windowHandle().screen().availableGeometry()
        width = area.width() // len(running)
        for index, controller in enumerate(running):
            window = self.popouts[controller.instance.id]
            window.showNormal()
            extra_width = window.frameGeometry().width() - window.width()
            extra_height = window.frameGeometry().height() - window.height()
            window.resize(width - extra_width, area.height() - extra_height)
            window.move(area.left() + index * width, area.top())

    def get_image(self, controller):
        instance = controller.instance

        def resolved(result):
            packages, licenses = result
            size = sum(package.size for package in packages if not package.installed) / 1e9
            modal = Modal(self.dialog_parent(), f"Download {instance.android}",
                          f"{instance.name} runs {instance.android}, which isn't on this PC yet. It's a {size:.1f} GB "
                          "download from Google, and you only need it once.")
            terms = "\n\n".join(licenses.values())
            modal.add(button("Read the license", lambda: show_text(self.dialog_parent(), "License", terms),
                             kind="link"))
            modal.cancel()
            modal.action("Agree and download", lambda: self.download_image(controller, packages))
            modal.open()

        self.run(lambda: installer.resolve(instance.api, tools=False), resolved,
                 lambda _: self.toast("Couldn't reach Google. Check your internet connection", "bad"))

    def download_image(self, controller, packages):
        name = controller.instance.android
        progress = Progress(self.dialog_parent(), f"Getting {name}", "Straight from Google. This happens once.")
        last = [0.0]

        def report(package, done, total, stage):
            now = time.monotonic()
            if now - last[0] < 0.1 and done < total:
                return
            last[0] = now
            verb = {"download": "Downloading", "verify": "Verifying", "unpack": "Unpacking"}[stage]
            amount = f" · {done / 1e6:,.0f} of {total / 1e6:,.0f} MB" if stage == "download" else ""
            self.later(lambda: progress.update_progress(f"{verb} {name}{amount}", done / max(total, 1)))

        def installed(_):
            progress.close_modal()
            controller.start()

        self.run(lambda: installer.install(packages, report), installed,
                 lambda error: progress.done("Download stopped", f"{error}. Start the instance again to resume."))

    def back_up(self, controller):
        instance = controller.instance
        if controller.state not in ("off", "crashed"):
            self.toast(f"Stop {instance.name} before backing it up")
            return
        file, _ = QFileDialog.getSaveFileName(self, "Back up instance",
                                              str(documents() / f"{instance.name} backup.androidbox"), BACKUP_FILTER)
        if not file:
            return
        progress = Progress(self.dialog_parent(), "Backing up", f"Saving {instance.name} to {Path(file).name}.")
        self.run(lambda: instances.backup(instance, file, self.byte_progress(progress)),
                 lambda _: progress.done("Backup saved", f"{instance.name} is saved in {file}. Restore it any time "
                                                         "from All instances."),
                 lambda error: progress.done("Backup failed", str(error)))

    def restore_backup(self):
        file, _ = QFileDialog.getOpenFileName(self, "Restore a backup", str(documents()), BACKUP_FILTER)
        if not file:
            return
        try:
            slot = instances.free_slot(self.instances)
        except RuntimeError as error:
            self.toast(str(error), "bad")
            return
        progress = Progress(self.dialog_parent(), "Restoring", f"Unpacking {Path(file).name}.")

        def restored(instance):
            if any(existing.name == instance.name for existing in self.instances):
                instance.name = f"{instance.name} (restored)"
            instances.adopt(self.instances, instance)
            self.add_controller(instance)
            progress.done("Restored", f"{instance.name} is back, with its apps and data.")
            self.select(instance.id)

        self.run(lambda: instances.restore(file, slot, self.byte_progress(progress)), restored,
                 lambda error: progress.done("Restore failed", str(error)))

    def byte_progress(self, progress):
        last = [0.0]

        def report(done, total):
            now = time.monotonic()
            if now - last[0] >= 0.1 or done >= total:
                last[0] = now
                self.later(lambda: progress.update_progress(f"{done / 1e9:.1f} of {total / 1e9:.1f} GB",
                                                            done / total))

        return report

    def new_instance(self):
        try:
            instances.free_slot(self.instances)
        except RuntimeError as error:
            self.toast(str(error), "bad")
            return
        modal = Modal(self.dialog_parent(), "New instance",
                      "A separate Android with its own apps, accounts and settings.")
        name = QLineEdit(f"Android {len(self.instances) + 1}")
        name.setMaxLength(32)
        display = QComboBox()
        for preset, (width, height, _) in instances.RESOLUTIONS.items():
            display.addItem(f"{preset}  ·  {width}×{height}", preset)
        android = QComboBox()
        android.addItem("Android 15 (recommended)", "35")
        android.addItem("Android 11 (runs older 32-bit games)", "30")
        modal.add(label("Name", "Section"))
        modal.add(name)
        saved = profiles.presets()
        start = QComboBox()
        start.addItem("Standard settings", None)
        for values in saved:
            start.addItem(values["name"], values)
        custom = [label("Display", "Section"), display, label("Android version", "Section"), android]
        if saved:
            modal.add(label("Start from", "Section"))
            modal.add(start)

            def pick():
                for widget in custom:
                    widget.setVisible(start.currentData() is None)

            start.currentIndexChanged.connect(pick)
        for widget in custom:
            modal.add(widget)
        modal.cancel()
        modal.action("Create", lambda: self.create_instance(name.text(), display.currentData(), android.currentData(),
                                                            start.currentData()))
        modal.open()
        name.setFocus()
        name.selectAll()

    def create_instance(self, name, display="Phone", api=installer.DEFAULT_API, preset=None):
        if preset:
            hardware = {key: preset[key] for key in profiles.PRESET_FIELDS if key in preset}
            if hardware.get("api") not in installer.ANDROID_VERSIONS:
                hardware.pop("api", None)
        else:
            width, height, density = instances.RESOLUTIONS[display]
            hardware = {"width": width, "height": height, "density": density, "api": api}
        instance = instances.create(self.instances, name.strip() or "Android", **hardware)
        self.add_controller(instance)
        self.select(instance.id)
        self.toast(f"Created {instance.name}. Its first start takes a little longer.", "good")

    def clone_instance(self, controller):
        if controller.state not in ("off", "crashed"):
            self.toast(f"Stop {controller.instance.name} before cloning it")
            return
        try:
            slot = instances.free_slot(self.instances)
        except RuntimeError as error:
            self.toast(str(error), "bad")
            return
        self.toast(f"Cloning {controller.instance.name}…")

        def cloned(copy):
            instances.adopt(self.instances, copy)
            self.add_controller(copy)
            self.pages["instances"].refresh()
            self.toast(f"Created {copy.name}", "good")

        self.run(lambda: instances.clone(controller.instance, slot), cloned)

    def delete_instance(self, controller):
        instance = controller.instance

        def delete():
            def removed(_=None):
                self.remove_controller(controller)
                self.select(None)
                self.toast(f"Deleted {instance.name}", "good")

            popout = self.popouts.get(instance.id)
            if popout:
                popout.close()
            controller.stop(then=lambda: self.run(lambda: instances.delete(self.instances, instance), removed))

        confirm(self.dialog_parent(), f"Delete {instance.name}?", "This removes the instance with all of its apps "
                "and data. This can't be undone.", "Delete", delete, danger=True)

    def rename(self, controller, text):
        text = text.strip()
        if not text or text == controller.instance.name:
            return
        controller.instance.name = text
        controller.save()
        self.instance_buttons[controller.instance.id].update()
        self.page_title.setText(text)
        popout = self.popouts.get(controller.instance.id)
        if popout:
            popout.refresh()

    def set_hardware(self, controller, **changes):
        for key, value in changes.items():
            setattr(controller.instance, key, value)
        controller.save()
        if controller.state in ("on", "booting"):
            self.toast("Saved. Restart Android to use it")

    def set_resolution(self, controller, preset):
        width, height, density = instances.RESOLUTIONS[preset]
        self.set_hardware(controller, width=width, height=height, density=density)

    def ask(self, title, text, default, action, submit):
        modal = Modal(self.dialog_parent(), title, text)
        field = QLineEdit(default)
        field.setMaxLength(profiles.NAME_LIMIT)
        modal.add(field)
        modal.cancel()
        confirm_button = modal.action(action, lambda: submit(field.text()))
        field.returnPressed.connect(confirm_button.click)
        modal.open()
        field.setFocus()
        field.selectAll()

    def show_profile_name(self):
        name = profiles.active()
        self.profile_chip.show_profile(name, instances.initials(name))

    def open_profile_menu(self):
        menu = QMenu(self)
        current = profiles.active()
        for name in profiles.names():
            action = menu.addAction(name)
            action.setCheckable(True)
            action.setChecked(name == current)
            action.triggered.connect(lambda _=False, target=name: self.switch_profile(target))
        menu.addSeparator()
        menu.addAction("Manage profiles…", lambda: self.show_page("profile"))
        menu.exec(self.profile_chip.mapToGlobal(QPoint(0, self.profile_chip.height() + 4)))

    def phones(self):
        return [self.screen.phone, *(popout.screen.phone for popout in self.popouts.values())]

    def reload_profile(self):
        for phone in self.phones():
            phone.finish_editing()
        self.prefs = settings.load()
        macros.forget()
        for phone in self.phones():
            phone.load_controls()
        for controller in self.controllers.values():
            controller.macros_changed.emit()
        self.update_mirrors()
        self.show_profile_name()
        self.refresh_tools()
        for popout in self.popouts.values():
            popout.refresh_tools()
        if self.page in GLOBAL_PAGES or self.active():
            self.show_page(self.page)

    def watch_profile(self):
        if any(phone.editing for phone in self.phones()):
            return
        if profiles.changed_outside():
            self.reload_profile()
            self.toast("Your profile was updated from another PC")

    def switch_profile(self, name):
        if name == profiles.active():
            return
        profiles.activate(name)
        self.reload_profile()
        self.toast(f"Switched to {name}", "good")

    def new_profile(self):
        def submit(text):
            try:
                name = profiles.create(text)
            except (OSError, ValueError) as error:
                self.toast(str(error), "bad")
                return False
            self.switch_profile(name)

        self.ask("New profile", "Start fresh with your own game controls, macros and presets.", "", "Create", submit)

    def rename_profile(self, name):
        def submit(text):
            try:
                profiles.rename(name, text)
            except (OSError, ValueError) as error:
                self.toast(str(error), "bad")
                return False
            self.reload_profile()

        self.ask("Rename profile", f"A new name for {name}.", name, "Rename", submit)

    def duplicate_profile(self, name):
        def submit(text):
            try:
                profiles.duplicate(name, text)
            except (OSError, ValueError) as error:
                self.toast(str(error), "bad")
                return False
            self.pages["profile"].refresh()
            self.toast(f"Created {text.strip()}", "good")

        self.ask("Duplicate profile", f"Copy {name} with all of its layouts, macros and presets.",
                 profiles.unique(f"{name} copy"), "Duplicate", submit)

    def delete_profile(self, name):
        if len(profiles.names()) < 2:
            self.toast("Keep at least one profile", "bad")
            return
        layouts, saved, presets = profiles.summary(name)
        note = " It is deleted on every PC that syncs it." if profiles.syncing() else ""

        def delete():
            if name == profiles.active():
                profiles.activate(next(other for other in profiles.names() if other != name))
                self.reload_profile()
            try:
                profiles.delete(name)
            except (OSError, ValueError) as error:
                self.toast(str(error), "bad")
                return
            self.pages["profile"].refresh()
            self.toast(f"Deleted {name}", "good")

        confirm(self.dialog_parent(), f"Delete {name}?", f"This removes its {layouts} game layouts, {saved} macros "
                f"and {presets} presets. This can't be undone.{note}", "Delete", delete, danger=True)

    def export_profile(self, name):
        file, _ = QFileDialog.getSaveFileName(self, "Export profile", str(documents() / f"{name}{profiles.EXTENSION}"),
                                              PROFILE_FILTER)
        if file:
            profiles.export(name, file)
            self.toast(f"Saved {name} to {Path(file).name}", "good")

    def import_profile(self):
        file, _ = QFileDialog.getOpenFileName(self, "Import a profile", str(documents()), PROFILE_FILTER)
        if not file:
            return
        try:
            name = profiles.import_profile(file)
        except (OSError, ValueError) as error:
            self.toast(str(error), "bad")
            return
        self.pages["profile"].refresh()
        self.toast(f"Imported {name}. Switch to it whenever you like", "good")

    def choose_sync_folder(self):
        start = profiles.sync_folder() or str(Path.home())
        folder = QFileDialog.getExistingDirectory(self, "Choose a sync folder", start)
        if not folder or Path(folder) == Path(profiles.sync_folder() or "."):
            return
        try:
            uploaded, found = profiles.start_sync(folder)
        except OSError as error:
            self.toast(f"Couldn't use that folder: {error}", "bad")
            return
        self.reload_profile()
        parts = []
        if uploaded:
            parts.append(f"added {plural(uploaded, 'profile')} from this PC")
        if found:
            parts.append(f"found {plural(found, 'profile')} already there")
        self.toast(f"Syncing through {Path(folder).name}" + (f": {', '.join(parts)}" if parts else ""), "good")

    def stop_syncing(self):
        try:
            profiles.stop_sync()
        except OSError as error:
            self.toast(f"Couldn't copy your profiles back: {error}", "bad")
            return
        self.reload_profile()
        self.toast("Sync is off. This PC keeps its own copy of your profiles", "good")

    def save_preset(self, controller):
        instance = controller.instance

        def submit(text):
            try:
                name = profiles.save_preset(text, instance)
            except (OSError, ValueError) as error:
                self.toast(str(error), "bad")
                return False
            self.toast(f"Saved the preset {name} to {profiles.active()}", "good")

        self.ask("Save as a preset", "Name it, and it shows up when you create an instance.", instance.name, "Save",
                 submit)

    def delete_preset(self, name):
        profiles.delete_preset(name)
        self.pages["profile"].refresh()

    def stop_all(self):
        for controller in self.controllers.values():
            controller.stop()

    def toggle_fullscreen(self):
        chrome = (self.sidebar, self.header, self.screen.tools)
        if self.isFullScreen():
            for part in chrome:
                part.show()
            if self.was_maximized:
                self.showMaximized()
            else:
                self.showNormal()
            return
        if not self.active():
            return
        self.show_page("screen")
        self.was_maximized = self.isMaximized()
        for part in chrome:
            part.hide()
        self.showFullScreen()
        self.toast("Press F11 to leave full screen")

    def closeEvent(self, event):
        self.closing = True
        for popout in list(self.popouts.values()):
            popout.close()
        running = [c for c in self.controllers.values() if c.state not in ("off", "crashed")]
        if not running:
            event.accept()
            QApplication.quit()
            return
        event.ignore()
        self.hide()
        remaining = [len(running)]

        def stopped():
            remaining[0] -= 1
            if remaining[0] == 0:
                QApplication.quit()

        for controller in running:
            controller.stop(then=stopped)
        QTimer.singleShot(90_000, QApplication.quit)
