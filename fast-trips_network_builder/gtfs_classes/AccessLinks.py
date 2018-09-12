import os
import pandas as pd

class AccessLinks(object):
    
    """
    Access Links. 
    """
    columns = ['taz', 'stop_id', 'dist'] 
    def __init__(self, data):
        """
        Constructor to populate DataFrame from list of dictionaries where each dictionary holds 
        row data for GTFS stop.txt. 
        """
        #: Trips_stop_times DataFrame
        
        self.data_frame = pd.DataFrame(data, columns = self.columns)