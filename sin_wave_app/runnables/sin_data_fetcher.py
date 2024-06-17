"""Runnable that updates data for the sin wave figure."""
import time

import numpy as np
from PyQt5.QtCore import QRunnable

from sin_wave_app.data_class.sin_data import SinData
from sin_wave_app.constants import TIME_INTERVAL_SECONDS, Y_ROUND
from sin_wave_app.utils import IsRunning


class SinDataFetcher(QRunnable):
    """Runnable that updates sin data class on an interval."""
    def __init__(self, sin_data: SinData, is_running_obj: IsRunning):
        """Initializes runner with sin data.

        Args:
            sin_data (SinData): Sin data class to update.
        """
        super().__init__()
        self.sin_data = sin_data
        self.is_running_obj = is_running_obj

    def run(self):
        """Sin data fetcher.
         
           Runs in separate thread. Calculates sin data based on time passed in seconds.
           
        """
        t0 = time.time()
        while self.is_running_obj.is_running:

  
            time_value = time.time() - t0
            
            y_val= round(self.sin_data.amp * np.sin(time_value * self.sin_data.frequency) + self.sin_data.offset, Y_ROUND)


            self.sin_data.x_data.append(time_value)
            self.sin_data.y_data.append(y_val)

            time.sleep(TIME_INTERVAL_SECONDS)
