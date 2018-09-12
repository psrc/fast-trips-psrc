import os
import pandas as pd

class TripsFT(object):
    
    """
    Trips. 
    """
    columns = ['trip_id', 'vehicle_name'] 
    def __init__(self, data):
        """
        Constructor to populate DataFrame from list of dictionaries where each dictionary holds 
        row data for GTFS Trips.txt. 
        """
        #: Trips_stop_times DataFrame
        
        df = pd.DataFrame(data, columns = self.columns)
        df['vehicle_name'] = df['vehicle_name'].map({'b1': 'local_bus1', 
                                                     'c1':'commuter_rail1', 
                                                     'f1':'ferry1', 
                                                     'p1':'premium_bus1', 
                                                     'r1':'light_rail1'})
        self.data_frame = df