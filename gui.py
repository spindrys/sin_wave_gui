from PyQt5.QtWidgets import (QApplication, 
                             QVBoxLayout, QWidget, QLabel, QPushButton, 
                             QMainWindow, QLineEdit, QHBoxLayout, QVBoxLayout
)
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
# Only needed for access to command line arguments
import sys
import matplotlib.pyplot as plt # For ploting
import numpy as np # to work with numerical data efficiently\
from matplotlib.figure import Figure
from typing import *
import sys
import os
from matplotlib.backends.qt_compat import QtCore, QtWidgets
# from PyQt5 import QtWidgets, QtCore
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
import matplotlib as mpl
import matplotlib.figure as mpl_fig
import matplotlib.animation as anim
import numpy as np

from PyQt5.QtCore import QObject, pyqtSignal, pyqtSlot, QThreadPool, QRunnable

X_LEN = 5 

class FileSavers(QRunnable):
    def __init__(self, worker_id: UUID, files: list[str]) -> None:
        super().__init__()
        # Allow for signals to be used
        self.worker_id = worker_id
        self.files_to_process = files
        self.signals: WorkerSignals = WorkerSignals()

    def run(self):
        """
        This is where the work is done. This actually has to be a method called run() for QRunnable to work.
        """
        self.signals.signal_started.emit(self.files_to_process)
        for i in range(1, 100, 10):
            sleep(0.1)
            self.signals.signal_progress.emit(i)
        self.signals.signal_finished.emit(self.worker_id)

class MyFigureCanvas(anim.FuncAnimation, FigureCanvasQTAgg):
    '''
    This is the FigureCanvas in which the live plot is drawn.

    '''
    def __init__(self) -> None:
        '''
        :param x_len:       The nr of data points shown in one plot.
        :param y_range:     Range on y-axis.
        :param interval:    Get a new datapoint every .. milliseconds.

        '''
        FigureCanvasQTAgg.__init__(self, mpl_fig.Figure())

        self.index = 0
        self.x_data = []
        self.y_data = []
        self.amp = 1
        self.offset = 0 
        self.frequency = 1 


        self._ax_  = self.figure.subplots()
        self.ln, = self._ax_.plot([], [])

        self._ax_.set_ylim(-1, 1)
        frames=np.linspace(0, 2 * np.pi)
        # Call superclass constructors
        anim.FuncAnimation.__init__(self, fig = self.figure, func=self._update_canvas_, frames=frames, repeat=True,
                                    blit=False)

        return
    
    def _update_canvas_(self, frames) -> None:
        '''
        This function gets called regularly by the timer.

        '''
        if self.index > 0 and frames == 0:
            # on repeat, we want to skip first frame 
            return self.ln
        
        x_val = frames + (self.index * 2 * np.pi)
        y_val= self.amp * np.sin(frames* self.frequency) + self.offset
    

        self.x_data.append(x_val)
        self.y_data.append(y_val)
        self.ln.set_data(self.x_data,self.y_data)

        # move plot to follow sin wave 
        self._ax_.set_xlim(x_val-X_LEN, x_val+X_LEN )
        
        if frames == 2 * np.pi:
            # we have just finished a loop, next iteration starts over
            self.index += 1
        
        return self.ln
    
    def log_data(self):

    


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        
        self.setWindowTitle("A Sin Wave")

        self.figure_canvas = MyFigureCanvas()
    

        amp_input_widget = self.set_amp_widget()
        offset_input_widget = self.set_offset_widget()
        freq_input_widget = self.set_freq_widget()
        
        
  


        vertical_layout = QVBoxLayout()
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

app = QApplication(sys.argv)
window = MainWindow()
window.show()
app.exec()

# Your application won't reach here until you exit and the event
# loop has stopped.
