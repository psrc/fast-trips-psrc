__copyright__ = "Copyright 2015 Contributing Entities"
__license__   = """
    Licensed under the Apache License, Version 2.0 (the "License");
    you may not use this file except in compliance with the License.
    You may obtain a copy of the License at
        http://www.apache.org/licenses/LICENSE-2.0
    Unless required by applicable law or agreed to in writing, software
    distributed under the License is distributed on an "AS IS" BASIS,
    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
    See the License for the specific language governing permissions and
    limitations under the License.
"""
import os
import pandas as pd
#import numpy
#import time

#from .Logger import FastTripsLogger

class GTFS_Utilities(object):
    """
    Route class.  Documentation forthcoming.
    """

    #: File with routes.
    #: TODO document format
    
    def __init__(self, gtfs_dir, start_time, end_time, service_id = 'WEEKDAY'):
        """
        Constructor from dictionary mapping attribute to value.
        """
        #: Trips_stop_times DataFrame
        self.dir = gtfs_dir
        self.df_trips_stop_times = self._get_trips_stop_times(start_time, end_time, service_id)
        self.departure_times = self._get_departure_times()
        # A dictionary where key is stop_id and value is a list of route_ids that serve the stop: 
        self.routes_by_stop = {k: list(set(g["route_id"].tolist())) 
                               for k,g in self.df_trips_stop_times.groupby("stop_id")}
        
    def _get_trips_stop_times(self, start, end, service_id):
        """
        Creates a merged dataframe consisting of trips & stop_ids for the start time, end time and service_id (from GTFS Calender.txt).
        This can include partial itineraries as only stops within the start and end time are included.  
        """
        trips_df = pd.DataFrame.from_csv(self.dir + '/trips.txt', index_col=False)
        stop_times_df = pd.DataFrame.from_csv(self.dir + '/stop_times.txt', index_col=False)
        
        # Detect whether there is any missing departure and arrival time in data
        if stop_times_df[['arrival_time', 'departure_time']].isnull().values.any():
            # If there are missing time, calculate the missing stops' departure and arrival time by distributing the travel time euqally
            stop_times_df['arrival_time'].fillna('00:00:00', inplace=True)  
            stop_times_df['departure_time'].fillna('00:00:00', inplace=True)
            stop_times_df = self._make_sequence_col(stop_times_df, ['trip_id', 'stop_sequence'], 'trip_id', 'stop_sequence')   
            # Add columns for arrival/departure in seconds
            stop_times_df['arrival_time_mins'] = stop_times_df.apply(self._convert_to_decimal_minutes, axis=1, args=('arrival_time',))
            stop_times_df['departure_time_mins'] = stop_times_df.apply(self._convert_to_decimal_minutes, axis=1,args=('departure_time',))
            stop_times_df['arrival_time_secs'] = (stop_times_df['arrival_time_mins']*60).astype(int)
            stop_times_df['departure_time_secs'] = (stop_times_df['departure_time_mins']*60).astype(int)
            import numpy as np
            import time
            for id in np.unique(stop_times_df['trip_id']):
                this_trip = stop_times_df[stop_times_df['trip_id']==id]
                cap_diff = (this_trip['departure_time_secs'].iloc[len(this_trip)-1] - this_trip['departure_time_secs'].iloc[0])/len(this_trip)
                #stop_times_df.loc[stop_times_df['trip_id'] == id, 'departure_time_secs'] = this_trip['departure_time_secs'].iloc[0] + cap_diff* (this_trip['stop_sequence']-1) 
                stop_times_df.loc[stop_times_df['trip_id'] == id, 'departure_time_secs'] = this_trip['departure_time_secs'].iloc[0] + cap_diff* (this_trip['stop_sequence']-1) 
            stop_times_df['departure_time'] = stop_times_df.apply(lambda row: time.strftime('%H:%M:%S', time.gmtime(row['departure_time_secs'])), axis=1)
            stop_times_df['arrival_time'] = stop_times_df.apply(lambda row: time.strftime('%H:%M:%S', time.gmtime(row['arrival_time_secs'])), axis=1)
        else: 
            stop_times_df = self._make_sequence_col(stop_times_df, ['trip_id', 'stop_sequence'], 'trip_id', 'stop_sequence')

        # Add columns for arrival/departure in decimal minutes and hours:
        stop_times_df['arrival_time_mins'] = stop_times_df.apply(self._convert_to_decimal_minutes, axis=1, args=('arrival_time',))
        stop_times_df['departure_time_mins'] = stop_times_df.apply(self._convert_to_decimal_minutes, axis=1,args=('departure_time',))
        stop_times_df['departure_time_hrs'] = stop_times_df['departure_time_mins']/60
        stop_times_df['departure_time_hrs'] = stop_times_df['departure_time_hrs'].astype(int)

        # Merge stop_times and trips on trip_id, so we can have shape_id
        trips_stop_times_df = stop_times_df.merge(trips_df, 'left', left_on = ["trip_id"], right_on = ["trip_id"])
        # Get trips/stop times for this service_id, start and end:
        trips_stop_times_df = trips_stop_times_df.loc[(trips_stop_times_df.service_id == service_id)]
        trips_stop_times_df = trips_stop_times_df.loc[(trips_stop_times_df.arrival_time_mins >= start) & (trips_stop_times_df.arrival_time_mins < end)]
        return trips_stop_times_df   
    
    def _get_departure_times(self):
        """
        Returns a dictionayr where the key is shape_id and the value is a list of departure times at the first stop for the time window 
        specified in the constructor. 
        """
        first_departure = self.df_trips_stop_times.sort('stop_sequence', ascending=True).groupby('trip_id', as_index=False).first()
        first_departure = first_departure.loc[(first_departure.stop_sequence == 1)]
        departure_times = {k: g["departure_time_mins"].tolist() for k,g in first_departure.groupby("shape_id")}
        return departure_times

    def get_departure_times_by_ids(self, list_of_shape_ids):
        """
        Using the list_of_shape_ids parameter, returns a list of combined departure times at the first stop for the time window 
        specified in the constructor. This can be used to get departure times for indivudal TDM routes that represents more than 
        one shape_id. 
        """
        
        departure_time_dict = dict((k, self.departure_times[k]) for k in (list_of_shape_ids))
        departure_times = []
        # We are getting the departure times for one or more shape_ids so put them all 
        # in one list:
        for departure_time in departure_time_dict.values():    
            departure_times.extend(departure_time)
        return departure_times
       
    def get_trips_per_hour(self):
        """
        Returns a dictionary where key is shape_id and value is the number of departures from the first stop. Does this only for
        the time window specified in the constructor.  
        """
        # get unique trips:
        first_departure = self.df_trips_stop_times.sort('stop_sequence', ascending=True).groupby('trip_id', as_index=False).first()
        first_departure = first_departure.loc[(first_departure.stop_sequence == 1)]
        first_departure = first_departure.groupby(['shape_id', 'departure_time_hrs'])['departure_time_hrs'].count()
        first_departure_df = pd.DataFrame(first_departure)
        first_departure_df.reset_index(level=0, inplace=True)
        first_departure_df = first_departure_df.rename(columns = {'departure_time_hrs' : 'frequency'})
        first_departure_df.reset_index(level=0, inplace=True)
        t = pd.pivot_table(first_departure_df, values='frequency', index=['shape_id'], columns=['departure_time_hrs'])
        t = t.fillna(0)
        return t

    def _make_sequence_col(self, data_frame, sort_list, group_by_col, seq_col):

        """
        Sorts a pandas dataframe using sort_list, then creates a column of sequential integers (1,2,3, etc.) for
        groups, using the group_by_col. Then drops the existing sequence column and re-names the new sequence column.
        """
        #sort on tripId, sequence
        data_frame = data_frame.sort(sort_list, ascending=[1,1])
        #create a new field, set = to the position of each record in a group, grouped by tripId
        data_frame['temp'] = data_frame.groupby(group_by_col).cumcount() + 1
        #drop the old sequence column
        data_frame = data_frame.drop(seq_col, axis=1)
        #rename new column:
        data_frame = data_frame.rename(columns = {'temp':seq_col})
        return data_frame

    def _convert_to_decimal_minutes(self, row, field):
        '''Convert HH:MM:SS to seconds since midnight, for comparison purposes.'''
        H, M, S = row[field].split(':')
        seconds = float(((float(H) * 3600) + (float(M) * 60) + float(S))/60)
        return seconds

#test = GTFS_Utilities(r'W:\gis\projects\CentersTransit2015\walkscore\GTFS\Metro', 0, 1440, 'WEEKDAY')