'''
This file is to create the gtfs_shapeID_to_lineID.csv
'''

import pandas as pd 
import numpy as np 
path = r'C:\Temp\fast-trips_network_builder\input'
line_attributes = pd.read_csv(path + '\line_attributes.csv') 
hourly_trips = pd.read_csv(path + '\hourly_trips33.txt')
headway = pd.read_csv(path + '\sc_headways.csv')
hourly_trips['operator']
hourly_trips['LineID']
line_attributes['LineID']
line_attributes['shape_id']

test = pd.DataFrame()
line_attributes['LineID2'] = line_attributes['LineID'] + 110000

shapeid_to_lineid = pd.read_csv(path + '\gtfs_shapeID_to_lineID.csv')

test['model_shape_id'] = line_attributes['LineID'] + 110000
test['gtfs_shape_id'] = line_attributes['shape_id']
test['LineID'] = test['model_shape_id']
hourly_trips = hourly_trips[['LineID', 'operator']]

gtfs_file = pd.merge(left = test, right = hourly_trips, on = 'LineID')

lost_lines = pd.DataFrame([['115125', '19_T03', '115125', 'ct'],['115362', '11096502', '115362', 'metro'], ['115363', '11098503', '115363', 'metro']], columns = (['model_shape_id', 'gtfs_shape_id', 'LineID','operator']))

new_gtfs_file = pd.concat([gtfs_file, lost_lines], ignore_index=True)

new_gtfs_file['feed'] = new_gtfs_file['operator']
feed_dict = {1: 'metro', 2: 'pt', 3: 'ct', 4: 'kt', 5: 'wsf', 6:'st', 7: 'Everett'}
new_gtfs_file = new_gtfs_file.replace({"feed": feed_dict})
new_gtfs_file['service_id'] = 'WEEKDAY'

new_gtfs_file.to_csv(path + '\gtfs_shapeID_to_lineID.csv')




