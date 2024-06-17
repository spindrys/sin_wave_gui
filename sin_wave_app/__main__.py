"""Main Entry for Sin Wave App."""

import sys

from PyQt5.QtWidgets import QApplication

from sin_wave_app.main_window import MainWindow
from sin_wave_app.utils import IsRunning



is_running_obj = IsRunning()
app = QApplication(sys.argv)
window = MainWindow(is_running_obj)
window.show()
app.exec()

# update running bool to break out of QRunnables at end of application.
is_running_obj.is_running = False
