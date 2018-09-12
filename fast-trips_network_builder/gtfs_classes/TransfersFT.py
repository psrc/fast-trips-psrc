import os
import pandas as pd
import numpy as np 

class TransfersFT(object):
    
    """
    Routes. 
    """
    columns = ['from_stop_id', 'to_stop_id', 'dist', 'from_route_id', 'to_route_id', 'schedule_precedence'] 
    def __init__(self, data):
        """
        Constructor to populate DataFrame from list of dictionaries where each dictionary holds 
        row data for GTFS transfers.txt. 
        """
        #: Trips_stop_times DataFrame
        
        df = pd.DataFrame(data, columns = self.columns)
        self.data_frame = df

    