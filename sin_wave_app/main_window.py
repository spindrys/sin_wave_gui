"""Main PyQt5 Window for Sin Wave App."""

import datetime

from PyQt5.QtWidgets import (QVBoxLayout, QWidget, QPushButton, 
                             QMainWindow, QLineEdit, QHBoxLayout, QVBoxLayout)
from PyQt5.QtCore import QThreadPool

from sin_wave_app.utils import IsRunning
from sin_wave_app.figure_class.ani_sin_figure import AnimatedSinFigure
from sin_wave_app.data_class.sin_data import SinData
from sin_wave_app.runnables.log_runner import DataLogRunnable
from sin_wave_app.runnables.sin_data_fetcher import SinDataFetcher



class MainWindow(QMainWindow):
    """Main Window for Sin Wave App."""

    def __init__(self, is_running_obj: IsRunning):
        """Initializes Main Window, necessary widgets and layouts."""
        super().__init__()

        self.setWindowTitle("A Sin Wave")

        self.is_running_class = is_running_obj
        self.sin_data = SinData()
        self.ani_sin_fig = AnimatedSinFigure(self.sin_data)

        self.amp_input_widget = self.set_up_input_widget(self.amp_update, "Amplitude")
        self.offset_input_widget = self.set_up_input_widget(self.offset_update, "Vertical Offset")
        self.freq_input_widget = self.set_up_input_widget(self.freq_update, "Frequency")

        self.start_btn=QPushButton('Start')
        self.start_btn.clicked.connect(self.start_sin_ani)
  

        vertical_layout = QVBoxLayout()
        vertical_layout.addWidget(self.start_btn)
        vertical_layout.addWidget(self.amp_input_widget)
        vertical_layout.addWidget(self.offset_input_widget)
        vertical_layout.addWidget(self.freq_input_widget)
        
        vertical_widget = QWidget()
        vertical_widget.setLayout(vertical_layout)
        
        horizontal_layout = QHBoxLayout()
     

        horizontal_layout.addWidget(vertical_widget)
        horizontal_layout.addWidget(self.ani_sin_fig)

        widget = QWidget()
        widget.setLayout(horizontal_layout)
        self.setCentralWidget(widget)
        

    def start_sin_ani(self):
        """Starts sin wave animation once start button is pushed."""
        self.is_running_class.is_running = True

        pool = QThreadPool.globalInstance()
        sin_data_fetcher = SinDataFetcher(self.sin_data, self.is_running_class)

        current_time = datetime.datetime.now(datetime.UTC)
        date_time_format = "%Y_%m_%d-%H-%M-%S-%f%Z"
        current_time_str = current_time.strftime(date_time_format)

        file_name = f"sin_log_{current_time_str}.npy"
        
        data_log_runnable = DataLogRunnable(self.sin_data, file_name, self.is_running_class)
        

        pool.start(sin_data_fetcher)
        pool.start(data_log_runnable)

        self.ani_sin_fig.start_pushed = True
        
        self.start_btn.setEnabled(False)

    def set_up_input_widget(self, update_func: callable, init_text: str ) -> QLineEdit:
        """Sets up a QLineEdit input widget for sin function params.

            i.e.: Sets up input widget for frequency, amplitude or vertical offset params.

        Args:
            update_func (callable): Function that updates param once input is changed.
            init_text (str): Initially text displayed in input box.

        Returns:
            QLineEdit: An input widget.
        """
        input_widget = QLineEdit()
        input_widget.setText(init_text)
        input_widget.textChanged.connect(update_func)
        return input_widget
    
    def amp_update(self, text: str):
        """Updates amplitude param in the sin data class.

        Args:
            text (str): Passed in input text from amp input widget.
        """
        
        try: 
            amp = float(text)
            self.sin_data.amp = amp
        except ValueError:
            self.amp_input_widget.setText("Enter a valid real number")

    def offset_update(self, text: str):
        """Updates vertical offset param in the sin data class.

        Args:
            text (str): Passed in input text from offset input widget.
        """
        
        try: 
            offset = float(text)
            
            self.sin_data.offset = offset
        except ValueError:
            self.offset_input_widget.setText("Enter a valid real number")

    def freq_update(self, text: str):
        """Updates frequency param in sin data class.

        Args:
            text (str): Passed in input text from frequency input widget.
        """
        
        try: 
            freq = float(text)
            
            self.sin_data.frequency = freq
        except ValueError:
            self.freq_input_widget.setText("Enter a valid real number")