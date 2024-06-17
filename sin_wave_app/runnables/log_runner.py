"""Runnable that logs data chunks on an interval."""

import time

import numpy as np
from PyQt5.QtCore import QRunnable

from sin_wave_app.data_class.sin_data import SinData
from sin_wave_app.constants import LOG_INTERNAL_SECONDS

class DataLogRunnable(QRunnable):
    """Data log runner."""
    def __init__(self, sin_data: SinData, file_name: str):
        """Initializes data log runner.

        Args:
            sin_data (SinData): Sin data class
            file_name (str): File to save data to. Time stamped.
        """
        super().__init__()
        self.sin_data = sin_data
        self.save_start_index = 0
        self.file_name = file_name

    def run(self):
        """Data log runner.
        
            Logs a chunk of sin wave data on an interval.
            Saved data index is kept track of. 
            New indexes are append to file.
        
        """
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
    
      
