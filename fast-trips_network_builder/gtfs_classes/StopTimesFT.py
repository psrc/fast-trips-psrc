import os
import pandas as pd

#from .Logger import FastTripsLogger

class StopTimesFT(object):
    
    """
    Stop Times
    """
    columns = ['trip_id', 'stop_id']
    
    def __init__(self, data):
        """
        Constructor to populate DataFrame from list of dictionaries where each dictionary holds 
        row data for GTFS stop_times_ft. 
        """
        #: Trips_stop_times DataFrame
        
        self.data_frame = pd.DataFrame(data, columns = self.columns)