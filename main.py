import os
import sys
from Engine.core import SamplerCore
from ui_files.main_window import MainWindow
from PyQt5 import QtWidgets


# ── Working Directory ──────────────────────────────────────────────────────

def set_working_directory():
    """Point the working directory at the bundled files (works for source and .exe)."""
    base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    os.chdir(base_path)


if __name__ == "__main__":
    set_working_directory()
    app = QtWidgets.QApplication([])
    core = SamplerCore()
    window = MainWindow(core)

    core.bank.main_window = window
    core.recorder.main_window = window

    window.show()
    app.exec_()