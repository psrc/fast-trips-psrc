import sys
import os 
import inro.emme.matrix as ematrix
import inro.emme.database.matrix
import inro.emme.database.emmebank as _eb
import numpy as np
import pandas as pd
import itertools
from itertools import groupby
from itertools import chain
os.chdir(r"D:\fast_trips\fast_trips_re_run_04172017\fast-trips_network_builder")
from collections import defaultdict
import collections
from config.input_configuration import *
from functions.general_functions import *
from gtfs_classes.FareRules import *
from gtfs_classes.Trips import *
from gtfs_classes.TripsFT import *
from gtfs_classes.StopTimes import *
from gtfs_classes.StopTimesFT import *
from gtfs_classes.Shapes import *
from gtfs_classes.Stops import *
from gtfs_classes.StopsFT import *
from gtfs_classes.Routes import *
from gtfs_classes.RoutesFT import *
from gtfs_classes.Transfers import *
from gtfs_classes.Calendar import *
from gtfs_classes.Agency import *
from gtfs_classes.TransfersFT import *
from gtfs_classes.GTFS_Utilities import *
from gtfs_classes.AccessLinks import *

walk_links_built = False  

if test_network:
    inputs_path = 'test_inputs/'
else:
    inputs_path = 'inputs/'

banks_path = 'Z:/Stefan/Soundcast_feb_twg/Banks/'

# Fare Files
#if not test_network:
df_fares = pd.DataFrame.from_csv(inputs_path + 'fares/fare_id.csv', index_col=False)
df_stops_zones = pd.DataFrame.from_csv(inputs_path + 'fares/stop_zones.csv', index_col=False)
df_fare_rules_ft = pd.DataFrame.from_csv(inputs_path + 'fares/fare_rules_ft.csv', index_col=False)
df_fare_attributes = pd.DataFrame.from_csv(inputs_path + 'fares/fare_attributes.csv', index_col=False)
df_fare_attributes_ft = pd.DataFrame.from_csv(inputs_path + 'fares/fare_attributes_ft.csv', index_col=False)
df_fare_transfer_rules = pd.DataFrame.from_csv(inputs_path + 'fares/fare_transfer_rules.csv', index_col=False)
df_fare_transfer_rules_ft = pd.DataFrame.from_csv(inputs_path + 'fares/fare_transfer_rules_ft.csv', index_col=False)
df_vehicles = pd.DataFrame.from_csv(inputs_path + 'vehicles.csv', index_col=False)
df_timed_transfers = pd.DataFrame.from_csv(inputs_path + 'timed_transfers.csv', index_col=False)

# Shape ID to model route crosswalk: 
df_shape_id_crosswalk = pd.DataFrame.from_csv(inputs_path + 'gtfs_shapeID_to_lineID.csv', index_col = False)

# Model routes to shape_id can be one to many; create a list of shape_ids for each model route
shapes = {k: list(v) for k,v in df_shape_id_crosswalk.groupby("model_shape_id")["gtfs_shape_id"]}

# Get unique rows using id (which is also model route shape_id) and name of feed 
#(also the directory where the gtfs data is stored)
unique_rows = df_shape_id_crosswalk.drop_duplicates(['model_shape_id', 'feed'])

# Populate a dictionary where key is model route shape_id, and value is a dictionary withe feed name and list(gtfs_shape_id)
# of published gtfs shape_ids (shapes).  
shape_id_dict = {}
for row in unique_rows.iterrows():
    shape_id_dict[row[1].model_shape_id] = {'shape_ids' : shapes[row[1].model_shape_id], 'feed' : row[1].feed}

# Now get a list of tuples that include unique feed and service id's.
unique_rows = df_shape_id_crosswalk.drop_duplicates(['feed'])
subset = unique_rows[['feed', 'service_id']]
schedule_tuples = [tuple(x) for x in subset.values]


#def main():
#global walk_links_built

# Creat outputs dir if one does not exist
if not os.path.exists('outputs'):
    os.makedirs('outputs')

network_dict = {}
last_departure_dict = {}
# Lists to hold stop_times and trips records
stop_times_list = []
stops = []
stops_list = []
trips_list = []
trips_ft_list = []
shapes_list = []
routes_list = []
routes_ft_list = []
fare_rules = FareRules()

# Generates a unique ID 
id_generator = generate_unique_id(range(1,999999))

# Load all the networks into the network_dict
# Highway_assignment_tod = {6: '6to7'}   

for tod in highway_assignment_tod.itervalues():
    with _eb.Emmebank(banks_path + tod + '/emmebank') as emmebank:
        current_scenario = emmebank.scenario(1002)
        network = current_scenario.get_network()
        network_dict[tod] = network

for tod, my_dict in transit_network_tod.iteritems():
    # A dictionary to hold an instance of GTFS_Utilities for each feed
    gtfs_dict = {}  
    # Populate gtfs_dict
    for feed in schedule_tuples:
        gtfs_utils = GTFS_Utilities(inputs_path + 'published_gtfs/' + feed[0], my_dict['start_time'], my_dict['end_time'], feed[1])
        gtfs_dict[feed[0]] = gtfs_utils
     
    # Get the am or md transit network: 
    transit_network = network_dict[my_dict['transit_bank']]

    # Get TAZ Nodes for walk access, only need to do once:
    if not walk_links_built:
        taz_list = get_taz_nodes(network)
        walk_links_built = True  
    transit_attributes_df = pd.DataFrame.from_csv(inputs_path + 'line_attributes.csv', index_col=False)
 

    # To Do: Store in a dict and turn this into a loop
    transit_network.create_attribute('TRANSIT_LINE', 'shape_id')
    transit_network.create_attribute('TRANSIT_LINE', 'route_id')
    transit_network.create_attribute('TRANSIT_LINE', 'short_name')
    transit_network.create_attribute('TRANSIT_LINE', 'long_name')
    transit_network.create_attribute('TRANSIT_LINE', 'ft_mode')
    transit_network.create_attribute('TRANSIT_LINE', 'proof_of_payment')
    transit_network.create_attribute('TRANSIT_LINE', 'vehicle_name') 
   
    
    # Schedule each route and create data structure (list of dictionaries) for trips and stop_times. 
    i = 0
    for transit_line in transit_network.transit_lines():
        i += 1
        configure_transit_line_attributes(transit_line, transit_attributes_df)
        departure_times = [] 
        # Check if departure times for this route come from published GTFS shape_ids:
        if transit_line.shape_id in shape_id_dict.keys():
            feed = shape_id_dict[transit_line.shape_id]['feed']
            ids = shape_id_dict[transit_line.shape_id]['shape_ids']
            departure_times = gtfs_dict[feed].get_departure_times_by_ids(ids)    
        ###### ROUTES ######
        routes_list.extend(get_route_record(transit_line, agency_list[0]['agency_id']))
        routes_ft_list.extend(get_route_ft_record(transit_line)) 
        ###### SHAPES ######
        shapes_list.extend(get_transit_line_shape(transit_line))
        ###### FARES ######
        # Get a list of ordered stops for this route
        list_of_stops = get_emme_stop_sequence(transit_line)
        # Add to stops_list for writing out stops.txt later
        stops.extend(list_of_stops)
        # Fare logic specific to PSRC. Don't do following on test network:
        # Get the zones
        #if not test_network:
        zone_list = get_zones_from_stops(list_of_stops, df_stops_zones)
        # Remove duplicates in sequence. [1,2,2,1] becomes [1,2,1]
        zone_list = [x[0] for x in groupby(zone_list)]
        # Get zone combos. Note: mode 'f' for ferry gets special treatment for PSRC. See function def.
        zone_combos = get_zone_combos(zone_list, transit_line.mode.id)
        # Return instance of fare_rules with populated dataframe
        no_match_dict = {}
        populate_fare_rule(zone_combos, fare_rules.data_frame, transit_line, df_fares)
        ###### Schedule ######
        schedule_route(my_dict['start_time'], my_dict['end_time'], transit_line, id_generator, stop_times_list, trips_list, 
                       trips_ft_list, network_dict, last_departure_dict, departure_times)

stops = list(set(stops))
stops_list = popualate_stops(transit_network, stops, df_stops_zones)
            
# Instantiate classes
shapes = Shapes(shapes_list)
stop_times = StopTimes(stop_times_list)
stop_times_ft = StopTimesFT(stop_times_list)
trips = Trips(trips_list)
trips_ft = TripsFT(trips_ft_list)
stops = Stops(stops_list)
stops_ft = StopsFT(stops_list)
routes = Routes(routes_list)
routes_ft = RoutesFT(routes_ft_list)
agency = Agency(agency_list)
calendar = Calendar(calender_list)
    
# Access links:
access_links = AccessLinks(get_access_links(taz_list, stops.data_frame, 14000))
access_links.data_frame.to_csv('outputs/walk_access.txt', index = False)
        
# Drop duplicate records
fare_rules.data_frame.drop_duplicates(inplace = True)
fare_rules = fare_rules.data_frame.astype(object)
fare_rules[['route_id', 'origin_id', 'destination_id']] = fare_rules[['route_id', 'origin_id', 'destination_id']].astype(object)
print fare_rules.dtypes
fare_rules.to_csv('outputs/fare_rules.txt', index = False)
df_fare_rules_ft.to_csv('outputs/fare_rules_ft.txt', index = False)
df_fare_attributes.to_csv('outputs/fare_attributes.txt', index = False, float_format='%.2f')
df_fare_attributes_ft.to_csv('outputs/fare_attributes_ft.txt', index = False, float_format='%.2f')
df_fare_transfer_rules.to_csv('outputs/fare_transfer_rules.txt', index = False, float_format='%.2f')
df_fare_transfer_rules_ft.to_csv('outputs/fare_transfer_rules_ft.txt', index = False, float_format='%.2f')
df_fare_periods_ft.to_csv('outputs/fare_periods_ft.txt', index = False, float_format='%.2f')
df_fare_periods_ft.to_csv('outputs/fare_periods_ft.txt', index = False, float_format='%.2f')
df_vehicles.to_csv('outputs/vehicles.txt', index = False)
df_vehicles.to_csv('outputs/vehicles_ft.txt', index = False)
routes.data_frame.drop_duplicates(inplace = True)
routes.data_frame = routes.data_frame.groupby('route_id').first().reset_index()
routes_ft.data_frame.drop_duplicates(inplace = True)
routes_ft.data_frame = routes_ft.data_frame.groupby('route_id').first().reset_index()

# Write out text files
shapes.data_frame.to_csv('outputs/shapes.txt', index = False)
stop_times.data_frame.to_csv('outputs/stop_times.txt', index = False)
stop_times_ft.data_frame.to_csv('outputs/stop_times_ft.txt', index = False)
stops.data_frame.to_csv('outputs/stops.txt', index = False)
stops_ft.data_frame.to_csv('outputs/stops_ft.txt', index = False)
trips.data_frame.to_csv('outputs/trips.txt', index = False)
trips_ft.data_frame.to_csv('outputs/trips_ft.txt', index = False) 
routes.data_frame.to_csv('outputs/routes.txt', index = False)
routes_ft.data_frame.to_csv('outputs/routes_ft.txt', index = False)
agency.data_frame.to_csv('outputs/agency.txt', index = False)
calendar.data_frame.to_csv('outputs/calendar.txt', index = False)

# Create transfers, depdendent on stops class:
print "create transfers, depdendent on stops class:"
synth_gtfs = GTFS_Utilities('outputs', 0, 1440, SERVICE_ID)
transfer_list = stop_to_stop_transfers(stops.data_frame, synth_gtfs.routes_by_stop, 2640)
transfers = Transfers(transfer_list)
transfer_list_ft = stop_to_stop_transfersFT(transfer_list, df_timed_transfers)
transfers_ft = TransfersFT(transfer_list_ft)
# Write out transfers:
transfers.data_frame.to_csv('outputs/transfers.txt', index = False)
transfers_ft.data_frame.to_csv('outputs/transfers_ft.txt', index = False)
#if __name__ == "__main__":
#    main()

print 'congrats! done.'