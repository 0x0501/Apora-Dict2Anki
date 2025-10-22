# Set system path for external packages
from . import setup  # noqa: F401

import os
import requests

from aqt import mw, qconnect

# import the "show info" tool from utils.py
from aqt.utils import showInfo

# import all of Qt GUI library
from aqt.qt import QAction
from .addon.addonWindow import Windows

HOME = os.path.expanduser("~")
BASHRC_FILE = HOME + "/.bashrc"

print("__init__.py")


def disable_ssl_check():
    original_req = requests.Session.request

    def request(*args, **kwargs):
        kwargs["verify"] = False
        return original_req(*args, **kwargs)

    requests.Session.request = request


check_debug = True
DEBUG = False


def disable_ssl_check_if_debug():
    global check_debug, DEBUG
    if not check_debug:
        return
    if not os.path.exists(BASHRC_FILE):
        return
    try:
        rc = os.system(f'source {BASHRC_FILE} && test "$DICT2ANKI_SSL_VERIFY" = "0"')
        if rc == 0:
            DEBUG = True
            showInfo("[Dict2Anki] DEBUG=True, SSL Check is DISABLED!")
            disable_ssl_check()
        check_debug = False  # check and prompt once
    except Exception:
        pass


print("__try__")

try:
    from aqt import mw, qconnect

    # import the "show info" tool from utils.py
    from aqt.utils import showInfo

    # import all of Qt GUI library
    from aqt.qt import QAction
    from .addon.addonWindow import Windows

    def show_window():
        disable_ssl_check_if_debug()
        w = Windows()
        w.exec()

    print("Add Dict2Anki-Apora to menuTools.")

    action = QAction("Dict2Anki...", mw)
    qconnect(action.triggered, show_window)
    mw.form.menuTools.addAction(action)

except Exception as ex:
    err = ex
    import os

    print("Cannot import Qt GUI Library.")
    print(ex)

    if os.environ.get("DEVDICT2ANKI"):
        import sys
        from .addon.addonWindow import Windows
        from aqt import QApplication

        app = QApplication(sys.argv)
        window = Windows()
        window.exec()
        sys.exit(app.exec())

print("__END__")
