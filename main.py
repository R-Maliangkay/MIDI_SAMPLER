from Engine.core import SamplerCore
from ui_files.main_window import MainWindow
from PyQt5 import QtWidgets

if __name__ == "__main__":
    app = QtWidgets.QApplication([])
    core = SamplerCore()
    window = MainWindow(core)

    core.bank.main_window = window
    core.recorder.main_window = window

    window.show()
    app.exec_()