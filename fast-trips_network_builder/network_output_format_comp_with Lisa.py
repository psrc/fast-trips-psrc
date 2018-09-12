import pandas as pd 
import numpy as np 

import os

input_path = 'D:/fast_trips/fast_trips_re_run_04172017/fast-trips_network_builder/outputs/5v'
file_dict = {}
for file in os.listdir(input_path):
    print file
    file_key = file[:-4]
    print file_key 
    file_dict[file_key] = pd.read_csv(input_path + '/'+ file) 


lisa_path = 'D:/fast_trips/fast_trips_re_run_04172017/network_format_latest/network'
lisa_dict = {}
for file in os.listdir(input_path):
    print file
    file_key = file[:-4]
    print file_key 
    lisa_dict[file_key] = pd.read_csv(lisa_path + '/'+ file) 


a = file_dict
b = lisa_dict 
for keys in a.keys():
     print keys
     print a[keys].columns  
     print b[keys].columns 
     print a[keys].head(3)
     print b[keys].head(3)
     print '****************************'


# below part is to fix the 2014 network format
# after fixed, put result into FT run at first, hopefully the run would go well 
# while model run, coming back debug the network builder.

######################################################
## update line attributes file 
#line_attributes = pd.read_csv(r'D:\fast_trips\fast_trips_re_run_04172017\fast-trips_network_builder\inputs\line_attributes.csv')
#line_attributes['Mode'] = line_attributes['Mode'].map({'b': 'local_bus', 
#                                                     'c':'commuter_rail', 
#                                                     'f':'ferry', 
#                                                     'p':'premium_bus', 
#                                                     'r':'light_rail'})

#line_attributes['ft_mode'] = line_attributes['ft_mode'].map({'b': 'local_bus', 
#                                                     'c':'commuter_rail', 
#                                                     'f':'ferry', 
#                                                     'p':'premium_bus', 
#                                                     'r':'light_rail'})

#line_attributes['vehicle_name'] = line_attributes['vehicle_name'].map({'b1': 'local_bus1', 
#                                                     'c1':'commuter_rail1', 
#                                                     'f1':'ferry1', 
#                                                     'p1':'premium_bus1', 
#                                                     'r1':'light_rail1'})

#line_attributes.to_csv(r'D:\fast_trips\fast_trips_re_run_04172017\fast-trips_network_builder\inputs\line_attributes.csv')

##################################################

## route_ft
#'''
#a_routes_mode
#array(['b', 'c', 'f', 'p', 'r'], dtype=object)
#b_routes_mode
#array(['commuter_rail', 'ferry', 'light_rail', 'local_bus', 'premium_bus'], dtype=object)
#'''

a['routes_ft']['mode'] = a['routes_ft']['mode'].map({'b': 'local_bus', 
                                                     'c':'commuter_rail', 
                                                     'f':'ferry', 
                                                     'p':'premium_bus', 
                                                     'r':'light_rail'})

# fare_rules
#'''
#a['fare_rules']['route_id'].head(2)
#0    1672.0
#1    1673.0
#Name: route_id, dtype: float64
#b['fare_rules']['route_id'].head(2)
#0    1_1001
#1    1_1002

#['route_id', 'origin_id', 'destination_id'] all has this issue
#'''

a['fare_rules'][['route_id', 'origin_id', 'destination_id']] = a['fare_rules'][['route_id', 'origin_id', 'destination_id']].astype(object)


# agency
#'''
#a['agency']['agency_name']
#0   NaN
#Name: agency_name, dtype: float64
#b['agency']['agency_name']
#0    PSRC
#Name: agency_name, dtype: object
#'''

a['agency']['agency_name'] = b['agency']['agency_name']

# stops
#'''
#np.unique(a['stops']['stop_name'])
#array(['King', 'Kitsap', 'NorthEastSnohomish', 'Pierce', 'Snohomish'], dtype=object)
#np.unique(b['stops']['stop_name'])
#array([  5135,   5259,   5282, ..., 199719, 199720, 199733], dtype=int64)
#'''


## trips_ft
#'''
#np.unique(a['trips_ft']['vehicle_name'])
#array(['b1', 'c1', 'f1', 'p1', 'r1'], dtype=object)
#np.unique(b['trips_ft']['vehicle_name'])
#array(['commuter_rail1', 'ferry1', 'light_rail1', 'local_bus1',
#       'premium_bus1'], dtype=object)
#'''

a['trips_ft']['vehicle_name'] = a['trips_ft']['vehicle_name'].map({'b1': 'local_bus1', 
                                                     'c1':'commuter_rail1', 
                                                     'f1':'ferry1', 
                                                     'p1':'premium_bus1', 
                                                     'r1':'light_rail1'})



# transfers_ft
a['transfers_ft'][['to_route_id', 'to_route_id', 'schedule_precedence']] = np.nan

# calendar 
a['calendar']['service_id'] = b['calendar']['service_id']

# trips
a['trips'] = a['trips'].drop('LineID', 1)



#####################################################
for keys in a.keys():
     print keys
     a[keys].to
out_path = 'D:/fast_trips/fast_trips_re_run_04172017/fast-trips_network_builder/outputs/4v'
for file in os.listdir(input_path):
    print file
    file_key = file[:-4]
    print file_key 
    a[file_key].to_csv(out_path + '/'+ file) 