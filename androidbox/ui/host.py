from PySide6.QtGui import QKeySequence, QShortcut
from PySide6.QtWidgets import QComboBox, QFileDialog, QLineEdit

from .widgets import Modal, label, row

PLACES = {
    "New York": (40.7128, -74.0060),
    "San Francisco": (37.7749, -122.4194),
    "Toronto": (43.6532, -79.3832),
    "London": (51.5074, -0.1278),
    "Paris": (48.8566, 2.3522),
    "Berlin": (52.5200, 13.4050),
    "Tokyo": (35.6762, 139.6503),
    "Seoul": (37.5665, 126.9780),
    "Sydney": (-33.8688, 151.2093),
    "São Paulo": (-23.5505, -46.6333),
}


class ScreenActions:
    popped = False

    def install_shortcuts(self):
        for keys, action in (("F11", self.toggle_fullscreen), ("Ctrl+Shift+S", self.screenshot),
                             ("Ctrl+Shift+R", self.toggle_video), ("Ctrl+Shift+K", self.toggle_game_controls),
                             ("Ctrl+Shift+E", self.edit_controls), ("Ctrl+Shift+M", self.toggle_macro),
                             ("Ctrl+Shift+O", self.rotate), ("Ctrl+Shift+W", self.toggle_popout)):
            QShortcut(QKeySequence(keys), self, action)

    def live(self):
        controller = self.active()
        return controller if controller and controller.on else None

    def refresh_tools(self):
        self.screen.tools.refresh(self.active(), self.prefs, self.screen.phone.editing)

    def send_key(self, key):
        if self.live():
            self.live().key(key)

    def rotate(self):
        if self.live():
            self.live().rotate()

    def shake(self):
        if self.live():
            self.live().shake()
            self.toast("Shaking the device")

    def screenshot(self):
        if self.live():
            self.live().screenshot()

    def toggle_video(self):
        if self.active():
            self.active().toggle_video()
        self.refresh_tools()

    def toggle_macro(self):
        if self.live():
            self.live().toggle_macro()
        self.refresh_tools()

    def record_macro(self):
        if not self.live():
            self.toast("Start Android first")
            return
        self.show_screen()
        if not self.live().recording_macro:
            self.live().toggle_macro()
        self.refresh_tools()

    def toggle_eco(self):
        controller = self.active()
        if controller:
            controller.set_eco(not controller.instance.eco)
            self.toast("Eco mode on: fewer frames, lower CPU use" if controller.instance.eco else "Eco mode off")
        self.refresh_tools()

    def toggle_sync(self):
        self.set_pref("sync_input", not self.prefs["sync_input"])
        self.toast("Input now goes to every running instance" if self.prefs["sync_input"] else "Input sync off")

    def toggle_game_controls(self):
        self.set_pref("game_controls", not self.prefs["game_controls"])
        self.toast("Game controls on" if self.prefs["game_controls"] else "Game controls off")

    def edit_controls(self):
        self.show_screen()
        phone = self.screen.phone
        if phone.editing:
            phone.finish_editing()
        else:
            phone.start_editing()
        self.refresh_tools()

    def choose_apps(self):
        files, _ = QFileDialog.getOpenFileNames(self, "Install apps", "",
                                                "Android apps (*.apk *.apks *.xapk *.apkm);;All files (*.*)")
        if files and self.active():
            self.active().open_files(files)

    def choose_files(self):
        files, _ = QFileDialog.getOpenFileNames(self, "Add files to Android", "", "All files (*.*)")
        if files and self.active():
            self.active().open_files(files)

    def choose_location(self):
        controller = self.live()
        if not controller:
            return
        modal = Modal(self.dialog_parent(), "Set location", "Apps will see this as the device's GPS position.")
        place = QComboBox()
        place.addItem("Custom", None)
        for name, spot in PLACES.items():
            place.addItem(name, spot)
        latitude = QLineEdit("40.7128")
        longitude = QLineEdit("-74.0060")

        def pick_place():
            spot = place.currentData()
            if spot:
                latitude.setText(str(spot[0]))
                longitude.setText(str(spot[1]))

        def apply():
            try:
                lat, lng = float(latitude.text()), float(longitude.text())
            except ValueError:
                self.toast("Enter numbers like 40.7128 and -74.0060", "bad")
                return False
            if not (-90 <= lat <= 90 and -180 <= lng <= 180):
                self.toast("That spot is off the map", "bad")
                return False
            controller.locate(lat, lng)

        place.currentIndexChanged.connect(pick_place)
        modal.add(label("Place", "Section"))
        modal.add(place)
        modal.add(label("Latitude and longitude", "Section"))
        modal.add(row(latitude, longitude))
        modal.cancel()
        modal.action("Set location", apply)
        modal.open()
