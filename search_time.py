import numpy as np
from scipy import signal 

class search_subclip:
    """
    Search for the subclip in the full audio file
    methods:
        find_offset(y_within,sr_within, y_find, window):Find the precise time point of the short audio in the long audio
    """
    def find_offset(y_within,sr_within, y_find, window):

        c = signal.correlate(y_within, y_find[:sr_within*window], mode='valid', method='fft')
        peak = np.argmax(c)
        offset = round(peak / sr_within, 2)

        return offset
    
    