"""Main Entry for Sin Wave App."""

import sys

from PyQt5.QtWidgets import QApplication

from sin_wave_app.main_window import MainWindow


app = QApplication(sys.argv)
window = MainWindow()
window.show()
app.exec()