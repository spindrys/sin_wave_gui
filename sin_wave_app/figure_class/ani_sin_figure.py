
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
import matplotlib.figure as mpl_fig
import matplotlib.animation as anim

from sin_wave_app.data_class.sin_data import SinData
from sin_wave_app.constants import Y_RANGE, X_LEN, TIME_INTERVAL_MILLISECONDS

class AnimatedSinFigure(FigureCanvasQTAgg):
    """Animated Sin Figure."""
    
    def __init__(self, sin_data: SinData,) -> None:
        """Initializes the figure and animation for the sin wave.

        Args:
            sin_data (SinData): Sin data class. 
        """

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
        """Starts animation once start button in main window is pressed."""
        
        self.animation.resume()
    
   
    def update_sin_line(self, _) -> None:
        """Update the animation with sin data.

        Args:
            _ (IteratableArtist): A frame from animation class that is not in use. (Errors out if not included)
        """

        if not self.start_pushed:
            # do not start updating sin line till start button is pushed
            return 
  

        self.sin_line.set_data(self.sin_data.x_data,self.sin_data.y_data)

        x_val = self.sin_data.x_data[-1]
        # move plot to follow sin wave 
        self._ax_.set_xlim(x_val-X_LEN, x_val+X_LEN )
        