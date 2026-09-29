import ctypes
import traceback

from androidbox import paths

try:
    from androidbox.ui.app import main
    main()
except Exception:
    paths.DATA.mkdir(parents=True, exist_ok=True)
    paths.CRASH_LOG.write_text(traceback.format_exc())
    ctypes.windll.user32.MessageBoxW(None, f"Androidbox crashed. Details are in {paths.CRASH_LOG}", "Androidbox", 0x10)
