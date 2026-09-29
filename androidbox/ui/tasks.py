import threading
import traceback

from PySide6.QtCore import QObject, Signal


class Relay(QObject):
    delivered = Signal(object)

    def __init__(self):
        super().__init__()
        self.delivered.connect(lambda callback: callback())
        self.on_error = print


relay = Relay()


def on_main_thread(callback):
    relay.delivered.emit(callback)


def background(work, then=None, failed=None):
    def run():
        try:
            result = work()
        except Exception as error:
            problem, details = error, traceback.format_exc()
            on_main_thread(lambda: failed(problem) if failed else relay.on_error(details))
            return
        if then:
            on_main_thread(lambda: then(result))

    threading.Thread(target=run, daemon=True).start()
