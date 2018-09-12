import os
import pandas as pd

class RoutesFT(object):
    
    """
    Routes. 
    """
    columns = ['route_id', 'mode', 'proof_of_payment'] 
    def __init__(self, data):
        """
        Constructor to populate DataFrame from list of dictionaries where each dictionary holds 
        row data for GTFS routes.txt. 
        """
        #: Trips_stop_times DataFrame
        
        df = pd.DataFrame(data, columns = self.columns)
        df['mode'] = df['mode'].map({'b': 'local_bus', 
                                     'c':'commuter_rail', 
                                     'f':'ferry', 
                                     'p':'premium_bus', 
                                     'r':'light_rail'})
        self.data_frame = df
    
