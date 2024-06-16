from PyQt5.QtWidgets import (QApplication, 
                             QVBoxLayout, QWidget, QLabel, QPushButton, 
                             QMainWindow, QLineEdit, QHBoxLayout, QVBoxLayout, 
)
# Only needed for access to command line arguments
import sys
import matplotlib.pyplot as plt # For ploting
import numpy as np # to work with numerical data efficiently\
from matplotlib.figure import Figure
from typing import *
import sys
import os
import time
from matplotlib.backends.qt_compat import QtCore, QtWidgets
from numpy.typing import ArrayLike
# from PyQt5 import QtWidgets, QtCore
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
import matplotlib as mpl
import matplotlib.figure as mpl_fig
import matplotlib.animation as anim
import numpy as np

from PyQt5.QtCore import QObject, pyqtSignal, pyqtSlot, QThreadPool, QRunnable, QTimer

X_LEN = 5 

FRAME_INTERVAL = 2 * np.pi 

TIME_INTERVAL_SECONDS = .25

TIME_INTERVAL_MILLISECONDS = TIME_INTERVAL_SECONDS * 1000

class SinData:

    def __init__(self):
        self.x_data = []
        self.y_data = []
        self.amp = 1
        self.offset = 0 
        self.frequency = 1 

class SinDataFetcher(QRunnable):
    def __init__(self, sin_data: SinData):
        super().__init__()
        self.frames=np.linspace(0, FRAME_INTERVAL)
        self.sin_data = sin_data
        self.current_frame_index = 0
        self.loops = 0 

    def run(self):
        while True:

            if self.current_frame_index == len(self.frames):
                self.current_frame_index = 1
                self.loops += 1
                

            current_frame = self.frames[self.current_frame_index]

            x_val = current_frame + (self.loops * FRAME_INTERVAL)
                
            
            
            y_val= self.sin_data.amp * np.sin(current_frame * self.sin_data.frequency) + self.sin_data.offset

            self.sin_data.x_data.append(x_val)
            self.sin_data.y_data.append(y_val)

            self.current_frame_index += 1 
            time.sleep(TIME_INTERVAL_SECONDS)



class MyFigureCanvas(FigureCanvasQTAgg):
    '''
    This is the FigureCanvas in which the live plot is drawn.

    '''
    def __init__(self, sin_data: SinData,) -> None:

        FigureCanvasQTAgg.__init__(self, mpl_fig.Figure())

        self.index = 0
        self.sin_data = sin_data

        self.amp = 1
        self.offset = 0 
        self.frequency = 1 

        self.start_pushed = False

        self.last_saved_index = 0


        self._ax_  = self.figure.subplots()
        self.ln, = self._ax_.plot([], [])

        self._ax_.set_ylim(-1, 1)
        self._ax_.set_xlim(-X_LEN, X_LEN )

    
        
        
        self.animation = anim.FuncAnimation(fig = self.figure, func=self.sin_func,
                                    blit=False, interval=TIME_INTERVAL_MILLISECONDS)
        
        

    def start_animation(self):
        self.animation.resume()
    
   
    def sin_func(self, _) -> None:

        if not self.start_pushed:
            return 
  

        self.ln.set_data(self.sin_data.x_data,self.sin_data.y_data)

        x_val = self.sin_data.x_data[-1]
        # move plot to follow sin wave 
        self._ax_.set_xlim(x_val-X_LEN, x_val+X_LEN )
        
    
    


class DataLogRunnable(QRunnable):
    def __init__(self, data_to_save: ArrayLike, save_start_index:int):
        super().__init__()
        self.data_to_save = data_to_save
        self.save_start_index = save_start_index

    def run(self):
        print("logging data")
        
        
        
        save_data = self.data_to_save[self.save_start_index:]
        time.sleep(10)
        print("logged")
    
      


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        
        self.setWindowTitle("A Sin Wave")

        self.sin_data = SinData()
        self.figure_canvas = MyFigureCanvas(self.sin_data)
        
    

        amp_input_widget = self.set_amp_widget()
        offset_input_widget = self.set_offset_widget()
        freq_input_widget = self.set_freq_widget()
        
        self.start_btn=QPushButton('Start')
        self.start_btn.clicked.connect(self.start_sin_ani)

        self.log_timer=QTimer()
        self.log_timer.timeout.connect(self.start_log_runnable)

        self.save_start_index = 0 
        self.save_data = []
  


        vertical_layout = QVBoxLayout()
        vertical_layout.addWidget(self.start_btn)
        vertical_layout.addWidget(amp_input_widget)
        vertical_layout.addWidget(offset_input_widget)
        vertical_layout.addWidget(freq_input_widget)
        
        vertical_widget = QWidget()
        vertical_widget.setLayout(vertical_layout)
        
        horizontal_layout = QHBoxLayout()
     

        horizontal_layout.addWidget(vertical_widget)
        horizontal_layout.addWidget(self.figure_canvas)

        widget = QWidget()
        widget.setLayout(horizontal_layout)
        self.setCentralWidget(widget)
    
    def start_log_runnable(self):
        pool = QThreadPool.globalInstance()
    
        data_chunk = self.figure_canvas.ln.get_xydata()
        runnable = DataLogRunnable(data_chunk, self.save_start_index)
        self.save_start_index=len(data_chunk)
        
        pool.start(runnable)

    def start_sin_ani(self):
        pool = QThreadPool.globalInstance()
        sin_data_fetcher = SinDataFetcher(self.sin_data)
        pool.start(sin_data_fetcher)
        self.figure_canvas.start_pushed = True
        self.log_timer.start(3000) # in milliseconds
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
            self.figure_canvas.amp = amp
        except ValueError:
            # somehow get message to app 
            # use label next to it ? 
            print("fix")
            #self.amp_input_widget.setText("Enter a valid real number")
            # #sleep maybe
            # self.amp_input_widget.setText(str(self.amp))


    def offset_update(self, text: str):
        
        try: 
            offset = float(text)
            
            self.figure_canvas.offset = offset
        except ValueError:
            # somehow get message to app 
            # use label next to it ? 
            print("fix")
            #self.amp_input_widget.setText("Enter a valid real number")
            # #sleep maybe
            # self.amp_input_widget.setText(str(self.amp))

    def freq_update(self, text: str):
        
        try: 
            freq = float(text)
            
            self.figure_canvas.frequency = freq
        except ValueError:
            # somehow get message to app 
            # use label next to it ? 
            print("fix")
            #self.amp_input_widget.setText("Enter a valid real number")
            # #sleep maybe
            # self.amp_input_widget.setText(str(self.amp))

# 1. Subclass QRunnable
class DataLogRunnable(QRunnable):
    def __init__(self, data_to_save: ArrayLike, save_start_index:int):
        super().__init__()
        self.data_to_save = data_to_save
        self.save_start_index = save_start_index

    def run(self):
        print("logging data")
        
        
        
        save_data = self.data_to_save[self.save_start_index:]
        time.sleep(10)
        print("logged")
    
      


app = QApplication(sys.argv)
window = MainWindow()
window.show()
app.exec()

# Your application won't reach here until you exit and the event
# loop has stopped.
