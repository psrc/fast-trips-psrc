import pandas as pd
import numpy as np
path = 'D:/fast_trips/last_working_copy/fast_trips_repo_121415/fast-trips_network_builder'
trip = pd.read_csv(path + '/outputs/trips.txt')
line_attr = pd.read_csv(path + '/inputs/line_attributes.csv')
headway = pd.read_csv(path + '/inputs/sc_headways.csv')
stop_time = pd.read_csv(path + '/outputs/stop_times.txt')

# clean up the line attribute table a bit
line_attr = line_attr.dropna()
line_attr = line_attr[line_attr['shape_id'] != 'Adds new to terminus in lakewood']
# get stop time to my trip
my_stop_time = stop_time[stop_time['stop_sequence'] == 1]

my_trip = pd.merge(left = trip, right = line_attr, on = 'shape_id', how = 'left')
my_trip['LineID'] = (my_trip['LineID_y']).astype(str)
my_col = ['trip_id', 'shape_id', 'LineID', 'Mode', 'Description', 'route_id_x']
my_trip = my_trip[my_col]

my_trip_time = pd.merge(left = my_trip, right = my_stop_time, on = 'trip_id')
my_trip_time['hour'] = my_trip_time['departure_time'].apply(lambda x: x[:2])
# sort trips
trip_sorted = my_trip_time.groupby(['LineID', 'hour']).count()
trip_sorted['trip_est'] = trip_sorted['trip_id']
trip_sorted['hour'] = trip_sorted.index.get_level_values('hour')
trip_sorted['LineID'] = trip_sorted.index.get_level_values('LineID')
trip_sorted = trip_sorted.reset_index(drop = True)[['LineID', 'hour', 'trip_est']]
trip_sorted['hdw'] = 60/ trip_sorted['trip_est'] # get headway 
# get headway info
my_headway = headway
my_headway['LineID'] = my_headway['LineID'] - 110000
my_headway['LineID'] = my_headway['LineID'].astype('float')
trip_sorted['LineID'] = trip_sorted['LineID'].astype('float')

# MERGE AND CHECK 
test = pd.merge(left = my_headway, right = trip_sorted, on = 'LineID', how = 'inner')
hdw_dict = {'05' : 'hdw_5to6', 
            '06' : 'hdw_6to7', 
            '07' : 'hdw_7to8', 
            '08' : 'hdw_8to9',
            '09' : 'hdw_9to10', 
            '10' : 'hdw_10to14', 
            '11' : 'hdw_10to14',
            '12' : 'hdw_10to14', 
            '13' : 'hdw_10to14', 
            '14' : 'hdw_14to15', 
            '15' : 'hdw_15to16', 
            '16' : 'hdw_16to17', 
            '17' : 'hdw_17to18', 
            '18' : 'hdw_18to20', 
            '19' : 'hdw_18to20', 
            '20': 'hdw_18to20'}

test['new_hour'] = test['hour'].map(hdw_dict)
test.reset_index(inplace=True, drop=True)
test['hdw_observed'] = test.apply(lambda row: row[row['new_hour']], axis=1)
test['diff'] = test['hdw_observed'] - test['hdw']
diff = pd.DataFrame()
for i in range(len(test)): 
    if test.iloc[i]['diff'] != 0: 
        diff = diff.append(test.iloc[i][['LineID', 'hdw', 'hdw_observed', 'hour', 'new_hour', 'trip_est', 'diff']])
diff['trip_obs'] = 60 /diff['hdw']
diff.to_csv(r'T:\2016December\Angela\headway_diff_full.csv')

# check diff 
test2 = diff

test2 = test2.groupby('LineID').apply(lambda row: row[['trip_est', 'trip_obs']].sum())
test2['trip_diff'] = test2.trip_est - test2.trip_obs
test3 = test2[test2['trip_diff'] != 0]
if len(test3) == 0: 
    print 'so far so good'
    test2 = diff
    test4 = test2.groupby(['LineID', 'new_hour']).apply(lambda row: row[['trip_est', 'trip_obs']].sum())
    test4['trip_diff'] = test4.trip_est - test4.trip_obs
    test5 = test4[test4['trip_diff'] != 0]
    if len(test5) == 0: 
    print 'Finally, good to go'

else: 
    print 'something wrong, do whatever you need to do'

