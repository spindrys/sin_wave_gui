from PyQt5.QtWidgets import (QApplication, 
                             QVBoxLayout, QWidget, QPushButton, 
                             QMainWindow, QLineEdit, QHBoxLayout, QVBoxLayout, 
)
# Only needed for access to command line arguments
import sys
from typing import *
import sys
import time
from numpy.typing import ArrayLike
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
import matplotlib.figure as mpl_fig
import matplotlib.animation as anim
import datetime
import numpy as np



from PyQt5.QtCore import QThreadPool, QRunnable

X_LEN = 5
# x axis +- domain 

Y_RANGE = 10 
# y axis +- range

TIME_INTERVAL_SECONDS = .1
# fetch data and update figure interval

TIME_INTERVAL_MILLISECONDS = TIME_INTERVAL_SECONDS * 1000

LOG_INTERNAL_SECONDS = 3
# log data to file interval

Y_ROUND = 4
# decimal places to round y value to 

class SinData:

    def __init__(self):
        self.x_data = []
        self.y_data = []
        self.amp = 1
        self.offset = 0 
        self.frequency = 1 

        self.save_start_index = 0 

class SinDataFetcher(QRunnable):
    def __init__(self, sin_data: SinData):
        super().__init__()
        self.sin_data = sin_data

    def run(self):
        t0 = time.time()
        while True:

  
            time_value = time.time() - t0
            
            y_val= round(self.sin_data.amp * np.sin(time_value * self.sin_data.frequency) + self.sin_data.offset, Y_ROUND)


            self.sin_data.x_data.append(time_value)
            self.sin_data.y_data.append(y_val)

            time.sleep(TIME_INTERVAL_SECONDS)


class MyFigureCanvas(FigureCanvasQTAgg):
    '''
    This is the FigureCanvas in which the live plot is drawn.

    '''
    def __init__(self, sin_data: SinData,) -> None:

        FigureCanvasQTAgg.__init__(self, mpl_fig.Figure())

        
        self.sin_data = sin_data


        self.start_pushed = False

        self._ax_  = self.figure.subplots()
        self.sin_line, = self._ax_.plot([], [])

        self._ax_.set_ylim(-Y_RANGE, Y_RANGE)
        self._ax_.set_xlim(-X_LEN, X_LEN )

        self._ax_.set_ylabel(str("Data"))
        self._ax_.set_xlabel(str("Seconds"))
        
        
        self.animation = anim.FuncAnimation(fig = self.figure, func=self.update_sin_line,
                                    blit=False, interval=TIME_INTERVAL_MILLISECONDS)
        
        

    def start_animation(self):
        self.animation.resume()
    
   
    def update_sin_line(self, _) -> None:

        if not self.start_pushed:
            # do not start updating sin line till start button is pushed
            return 
  

        self.sin_line.set_data(self.sin_data.x_data,self.sin_data.y_data)

        x_val = self.sin_data.x_data[-1]
        # move plot to follow sin wave 
        self._ax_.set_xlim(x_val-X_LEN, x_val+X_LEN )
        
  

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        
        self.setWindowTitle("A Sin Wave")

        self.sin_data = SinData()
        self.figure_canvas = MyFigureCanvas(self.sin_data)
        
    

        self.amp_input_widget = self.set_amp_widget()
        self.offset_input_widget = self.set_offset_widget()
        self.freq_input_widget = self.set_freq_widget()
        
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
        horizontal_layout.addWidget(self.figure_canvas)

        widget = QWidget()
        widget.setLayout(horizontal_layout)
        self.setCentralWidget(widget)
    

    def start_sin_ani(self):
        pool = QThreadPool.globalInstance()
        sin_data_fetcher = SinDataFetcher(self.sin_data)

        current_time = datetime.datetime.now(datetime.UTC)
        date_time_format = "%Y_%m_%d-%H-%M-%S-%f%Z"
        current_time_str = current_time.strftime(date_time_format)

        file_name = f"sin_log_{current_time_str}.npy"
        
        data_log_runnable = DataLogRunnable(self.sin_data, file_name)
        

        pool.start(sin_data_fetcher)
        pool.start(data_log_runnable)

        self.figure_canvas.start_pushed = True
        
        self.start_btn.setEnabled(False)

    def set_amp_widget(self):
        amp_input_widget = QLineEdit()
        
        amp_input_widget.setText("Amplitude")
        amp_input_widget.textChanged.connect(self.amp_update)

        return amp_input_widget
    
    def set_offset_widget(self):
        offset_input_widget = QLineEdit()
        offset_input_widget.setText("Vertical Offset")
        offset_input_widget.textChanged.connect(self.offset_update)

        return offset_input_widget

    def set_freq_widget(self):
        freq_input_widget = QLineEdit()
        freq_input_widget.setText("Frequency")
        freq_input_widget.textChanged.connect(self.freq_update)

        return freq_input_widget

    
    def amp_update(self, text: str):
        
        try: 
            amp = float(text)
            self.sin_data.amp = amp
        except ValueError:
            self.amp_input_widget.setText("Enter a valid real number")
          


    def offset_update(self, text: str):
        
        try: 
            offset = float(text)
            
            self.sin_data.offset = offset
        except ValueError:
            self.offset_input_widget.setText("Enter a valid real number")

    def freq_update(self, text: str):
        
        try: 
            freq = float(text)
            
            self.sin_data.frequency = freq
        except ValueError:
            self.freq_input_widget.setText("Enter a valid real number")


class DataLogRunnable(QRunnable):
    def __init__(self, sin_data: SinData, file_name: str):
        super().__init__()
        self.sin_data = sin_data
        self.save_start_index = 0
        self.file_name = file_name

        

    def run(self):
        while True:
            time.sleep(LOG_INTERNAL_SECONDS)
            print("logging data")
            x_data_chunk = self.sin_data.x_data[self.save_start_index:]
            y_data_chunk = self.sin_data.y_data[self.save_start_index:]
            save_data = [[x,y] for x, y in zip(x_data_chunk,y_data_chunk)]

            with open(self.file_name, 'ab') as f:
                np.savetxt(f,save_data)
    
            # for testing/ viewing data : 
            with open(self.file_name, 'rb') as f:
                a = np.loadtxt(f)
                print(a)

            self.save_start_index = len(self.sin_data.x_data)
    
      


app = QApplication(sys.argv)
window = MainWindow()
window.show()
app.exec()

