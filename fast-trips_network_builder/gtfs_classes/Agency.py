import os
import pandas as pd

class Agency(object):
    
    """
    Trips. 
    """
    columns = ['agency_id', 'agency_name', 'agency_url', 'agency_timezone'] 
    def __init__(self, data):
        """
        Constructor to populate DataFrame from list of dictionaries where each dictionary holds 
        row data for GTFS Trips.txt. 
        """
        #: Trips_stop_times DataFrame
        
        df = pd.DataFrame(data, columns = self.columns)

        self.data_frame = df