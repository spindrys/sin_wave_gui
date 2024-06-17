# Set up

1. Navigate to root project foler
1. run `python -m venv venv`
1. activate venv `source venv/bin/activate` or `venv/Scripts/activate` depending on platform
1. `pip install -r requirements.txt`
1. modify constants in sin_wave_app/constants.py if need be
1. `python -m sin_wave_app.main` or use launch.json config (if using vscode)

# Notes on project structure 

## MainWindow Class

This is where the window for the application is built up. 
It initiallizes necessary classes, widgets and layouts:
1. AnimatedSinFigure
    1. The class where the matplotlib figure and animation class is initialized.
1. Sin Data class
    1. A data class that holds th x and y values of the sin function as well as the params; freq, amplitude, offset.
1. Start button
    1. Starts animation when pressed by connecting to a start function
    1. Start function starts the animation as well as two runnables; data logger and data fetcher.
1. QLineEdit - Input widgets for sin function params
    1. Three boxes in the window can take real number inputs
        1. Frequency
        1. Amplitude
        1. Vertical Offset
    1. A connection to update param functions is triggered whenever these boxes are edited
    1. The update param functions modify the sin data class param values so that the changes are reflected in the animation

## SinDataFetcher Class

This class is a QRunnable that updates the SinDataClass with new sin values. 
It is initialized in the MainWindow class and runs once the start button is pushed.
Its run function is a loop that sleeps for a specific interval (the same interval the animation is updated).
At each interval, the y value is computed using the sin function, input params and the given time in seconds that has passed since the start button was pushed. 

Since this run function runs in its own thread, separate from the main, the y values can be calculated without interrupting the animation.
It updates the sin data class at the same interval that the animation pulls data from the same sin data class instance, allowing a smooth transition of data.

Once the main application is closed, a bool, is running, is updated to false.
SinDataFetcher will break once this bool is false to end the thread. 

## DataLogRunner Class

This is QRunnable that logs data according to the log interval constant in the constants.py file (current set at 60 seconds).
It is intialized ini the MainWindow class and runs once the start button is pushed.
Its run function is a loop that sleeps for the given interval and then appends data chunks to a timestamped npy file. 
The timestamp is the time the start button was pressed. 

The DataLogRunner class keeps track of the index of the last saved sin data so that it can extract the next data chunk.
This is important so that the entire sin data is not saved to file each time (can result in data loss/slow process).
Instead of overwriting the file, the new chunks are appended to the end of the file. 

Once the main application is closed, a bool, is running, is updated to false.
DataLogRunner will break once this bool is false to end the thread. 

