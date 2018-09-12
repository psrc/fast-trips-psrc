import inro.emme.matrix as ematrix
import inro.emme.database.matrix
import inro.emme.database.emmebank as _eb
import numpy as np
import time
from config.input_configuration import *
import itertools
from itertools import groupby
from itertools import combinations
from gtfs_classes.Trips import *
from gtfs_classes.TripsFT import *
from gtfs_classes.StopTimes import *
from gtfs_classes.FareRules import *
from gtfs_classes.Shapes import *
from gtfs_classes.Stops import *
from gtfs_classes.Routes import *
from gtfs_classes.RoutesFT import *
from pyproj import Proj, transform
import random 
import geocoder
import pyproj


def get_emme_stop_sequence(emme_transit_line):
    
    record_list = []
# Loop through the segments of each route
    for segment in emme_transit_line.segments():
            last_segment_number = max(enumerate(emme_transit_line.segments()))[1].number
            #segment_time = calc_transit_time(segment)
            
            # A one segment line (ferry):
            if segment.number == 0 and last_segment_number == 0:
                record_list.append(int(segment.i_node.id))
                record_list.append(int(segment.j_node.id))
                
            elif segment.number == 0:
                record_list.append(int(segment.i_node.id))

            elif segment.number == last_segment_number:
            # Last stop, need time of last segment
                if segment.allow_alightings:
                    record_list.append(int(segment.i_node.id))
                record_list.append(int(segment.j_node.id))

            else:
                if segment.allow_alightings:
                    record_list.append(int(segment.i_node.id))

    return record_list

def configure_transit_line_attributes(transit_line, df_network_atts):
    '''
    Add attributes that are not stored in emme to each transit line.  
    '''

    row = df_network_atts.loc[(df_network_atts.id == int(transit_line.id))]
    transit_line.route_id = row['route_id'].iloc[0]
    transit_line.shape_id = row['shape_id'].iloc[0]
    #Angela's edit - below one line
    #transit_line.LineID = row['LineID'].iloc[0]
    transit_line.short_name = row['short_name'].iloc[0]
    transit_line.long_name = row['long_name'].iloc[0]
    transit_line.ft_mode = row['ft_mode'].iloc[0]
    transit_line.proof_of_payment = row['proof_of_payment'].iloc[0]
    transit_line.vehicle_name = row['vehicle_name'].iloc[0]


def reproject_to_wgs84(longitude, latitude, ESPG = "+init=EPSG:2926", conversion = 0.3048006096012192):
    '''
    Converts the passed in coordinates from their native projection (default is state plane WA North-EPSG:2926)
    to wgs84. Returns a two item tuple containing the longitude (x) and latitude (y) in wgs84. Coordinates
    must be in meters hence the default conversion factor- PSRC's are in state plane feet.  
    '''
    #print longitude, latitude
    # Remember long is x and lat is y!
    prj_wgs = Proj(init='epsg:4326')
    prj_sp = Proj(ESPG)
    
    # Need to convert feet to meters:
    longitude = longitude * conversion
    latitude = latitude * conversion
    x, y = transform(prj_sp, prj_wgs, longitude, latitude)
    
    return x, y


def get_fare_id(operator, origin, destination):
    '''
    Returns fare_id from df_fares using origin, destination, operator
    '''
    
    row = df_fares.loc[(df_fares.operator == operator) & (df_fares.origin_zone == origin) & (df_fares.destination_zone == destination)]
    
    return row['fare_id'].iloc[0]

def get_zone_combos(list_of_zones, mode):
    '''
    Returns a list of tuples containing the feasible zone combos from a list of zones. The zone list must be in
    sequence- the zones encountered along the path
    '''

    # Check to see if only one zone for entire route:
    if len(set(list_of_zones)) <=1:
        return[(list_of_zones[0], list_of_zones[0])]
    
    # Ferries- only want origin, destination combo. 
    elif mode == 'f':
        return[(list_of_zones[0], list_of_zones[1])]
    
    else:
        # Creates a list of tuples of possible zone pairs for a sequence of zones.  
        zone_combos = []
        x = 0
        for zone in list_of_zones:
            for i in range(x, len(list_of_zones)):
                combo = (zone, list_of_zones[i])
                zone_combos.append(combo)
            x = x + 1
        
        return list(set(zone_combos))

def get_random_departure_time(time_period_start, headway, min_start_time = 0):
    '''
    Using a log normal distribution, computes a pseudo random departure time in number of minutes based on a time window. The
    time window ranges from a default of 0 to half the headway. From this range, the mean and standard deviation are 
    calculated and then used as paramaters in the random.lognormvariate function. This result is added to time_period_start, 
    and result is the departure time in number of minutes past midnight. The idea behind this methodology is that first 
    departures 1) should not all happen at the same time, 2) Indviudal routes should have a first departure time well less than 
    their headway so that their hourly frequencies are met at most stops, and 3) longer headways (less fequent service) should 
    have start times farther away from the begining of the time period compared to routes with more frequent service. Item 3
    is not guaranteed but highly probable.    
    '''
    # Assume max start time is half the headway for now:
    max_start_time = headway * .5
    start_time = max_start_time
    # Make sure start_time is < max_start_time
    while start_time >= max_start_time or start_time < 0:
        mean = (max_start_time + min_start_time)/2
        # Using 3 because 3 Standard deviatons should account for 99.7% of a population in a normal distribution. 
        sd = mean/3
        start_time = random.lognormvariate(mean, sd)
    start_time = start_time + time_period_start 
    return start_time

def get_zone_combos_contains_id(list_of_zones):
    '''
    Not fully implemented but contains the logic to be used when using the list_of_zones convention in fare_rules.txt
    '''
    
    # Check to see if only one zone for entire route:
    if len(set(list_of_zones)) <=1:
        
        return[(list_of_zones[0], list_of_zones[0])]
    
    else:
        # Creates a list of tuples of possible zone pairs for a sequence of zones.  
        zone_combos = []
        x = 0
        for zone in list_of_zones:
            combos = []
            for i in range(x, len(list_of_zones)):
                combos.append(list_of_zones[i])
                zone_combos.append(tuple(combos))  
            x = x + 1
        
        return list(set(zone_combos))
                   
def get_zones_from_stops(list_of_stops, df_stops_zones):
    '''
    Returns a list of zones using list_of_stops and the stop_zone look up, df_stops_zones
    '''

    df = pd.DataFrame(np.asarray(list_of_stops),index=None,columns=['NODE_ID'])
    df = df.merge(df_stops_zones, 'left', left_on = ["NODE_ID"], right_on = ["ID"])

    zone_list = df['ZoneID'].tolist()

    return zone_list

def popualate_stops(network, stops, df_stop_zones):
    '''
    Creates records for stops.txt
    '''
    stops_list = []
    for stop in stops:
        node = network.node(stop)
        #location = geolocator.reverse(node.x, node.y)
        #print location.address
        wgs84tuple = reproject_to_wgs84(node.x, node.y)
        #geocode = geocoder.google([wgs84tuple[1], wgs84tuple[0]], method="reverse")
        #try:
        #    stop_name = geocode.content['results'][1]['address_components'][0]['short_name']
        #except:
        #    stop_name = geocode.street_long

        row = df_stop_zones.loc[(df_stop_zones.ID == int(node.id))]
        if len(row['ZoneName']) == 1:
            stop_name = row['ZoneName'].iloc[0]
        #print stop_name
            zone_id = row['ZoneID'].iloc[0]
        #print zone_id
        stops_record = [node.id, stop_name, wgs84tuple[1], wgs84tuple[0], zone_id]
        stops_list.append(dict(zip(Stops.columns, stops_record)))

    return stops_list

def populate_fare_rule(zone_pairs, df_fare_rules, emme_transit_line, df_fares):
    '''
    Updates dataframe on instance of Fare_Rules with all possible rules for a given route
    '''
    for pair in zone_pairs:
        origin = pair[0]
        destination = pair[1]
        # .data3 refers to operator
        row = df_fares.loc[(df_fares.operator == emme_transit_line.data3) 
                           & (df_fares.origin_zone == origin) & (df_fares.destination_zone == destination)]
        if len(row) == 0:
            #print origin, destination
            break 
        fare_id = row['fare_id'].iloc[0]
        #fare_id = get_fare_id(emme_transit_line.data3, origin, destination)

        df_fare_rules.loc[len(df_fare_rules)] = [fare_id, emme_transit_line.route_id, origin, destination, ""]
 

def test_fare_rules(route_stops, df_fare_rules, route_id):
    """
       This is a unit test that checks every route to see if all feasible stop combinations have valid records in fare_rules. 
    """
    x = 0
    zones = get_zones_from_stops(route_stops)
    for o_zone in zones:
        for i in range(x+1, len(zones)):
            d_zone = zones[i]
            row = df_fare_rules.loc[(df_fare_rules.route_id == route_id) & (df_fare_rules.origin_id == o_zone) & (df_fare_rules.destination_id == d_zone)]
            x = x + 1
            return len(row)

def generate_unique_id(seq):
    """
    Generator that yields a number from a passed in sequence
    """
    
    for x in seq:
        yield x
  
def dec_mins_to_HHMMSS(time_in_decimal_minutes):
    """ 
    Convertes Decimal minutes to HHMMSS
    """
    return time.strftime("%H:%M:%S", time.gmtime(time_in_decimal_minutes * 60))

def get_route_record(transit_line, agency_id):
    '''
    Creates a transit record for routes.txt
    '''
    route_list = []
    route_record = [transit_line.route_id, agency_id, transit_line.short_name, transit_line.long_name, transit_line.description,  
                    route_type_dict[transit_line.mode.id]]
    route_list.append(dict(zip(Routes.columns, route_record)))
    return route_list

def get_route_ft_record(transit_line):
    '''
    Creates a transit record for routes.txt
    '''
    route_ft_list = []
    route_ft_record = [transit_line.route_id, transit_line.ft_mode, transit_line.proof_of_payment]
    route_ft_list.append(dict(zip(RoutesFT.columns, route_ft_record)))
    return route_ft_list

def get_transit_line_shape(transit_line):
    """
    Returns a list of dictionaries that hold the records for shape.txt for an individual transit line. 
    Coordinates (for PSRC) are stored in state plane so this includes a call to the reproject_to_wgs84 
    function.  
    """
    x = 1
    shape_list = []
    for segment in transit_line.segments():
        # Get all vertices except for the last one (JNode):
        for coord in segment.link.shape[:-1]:
            # Remember, X=long and Y=lat
            wgs84tuple = reproject_to_wgs84(coord[0], coord[1])
            shape_record = [transit_line.shape_id, wgs84tuple[1], wgs84tuple[0], x]
            #shape_record = [transit_line.shape_id, coord[1], coord[0], x]
            shape_list.append(dict(zip(Shapes.columns, shape_record)))
            x = x + 1
    
    # Get the JNode of the last link
    coord = segment.link.shape[-1] 
    wgs84tuple = reproject_to_wgs84(coord[0], coord[1])
    shape_record = [transit_line.shape_id, wgs84tuple[1], wgs84tuple[0], x]
    #shape_record = [transit_line.shape_id, coord[1], coord[0], x]
    
    shape_list.append(dict(zip(Shapes.columns, shape_record)))
    return shape_list

def schedule_route(start_time, end_time, transit_line, trip_id_generator, stop_times_list, trips_list, trips_ft_list, network_dictionary, prev_last_departure_dict, departure_times):
    '''
    Builds a schedule for a given route, for a given time window using stop to stop travel times. First Stop departure times can be passed in as a list (departure_times) 
    otherwise they will be determined using the get_random_departure_time function. Creates a record for each trip and all stop_times for each trip, which are stored in 
    dictionaries and appended to stops_times_list and trips_list.
    '''
    # Get first stop departure times if not provided by departure_times argument: 
    if not departure_times:

        # Has this line already been scheduled for a previous time period?
        if transit_line.shape_id in prev_last_departure_dict.values():

            # Get the final departure time from the last time period
            last_departure = prev_last_departure_dict.values[transit_line.shape_id]
            # Does the last departure + the new headway happen before the begining of this time period? If yes, 
            # set the first departure time to the begining of the time period. 
            if last_departure + transit_line.headway < start_time:
                departure_times = range(int(start_time), end_time, int(transit_line.headway))

            # Otherwise make the first departure equal to the last departure + the new headway
            else:
                departure_times = range(int(last_departure + start_time), end_time, int(transit_line.headway))

        # Otherwise, schedule this route for the first time:
        else:
            random_start_time = get_random_departure_time(start_time, transit_line.headway)
 
            departure_times = range(int(random_start_time), end_time, int(transit_line.headway))

      

    prev_last_departure_dict[transit_line.shape_id] = departure_times[-1]
    for departure_time in departure_times:

       # Create a record for trips (GTFS File)
       trip_id = trip_id_generator.next()
 
       # To Do: need a route_id attribute- using transit_line.id for now
       # Populate trips record

       trips_record = [transit_line.route_id, SERVICE_ID, trip_id, transit_line.shape_id]
       # Above original code was edited into blow to test the headway trip frequency - Angela 
       #trips_record = [transit_line.route_id, SERVICE_ID, trip_id, transit_line.shape_id, transit_line.LineID]
       trips_list.append(dict(zip(Trips.columns, trips_record)))

       
       # Populate trips_ft record
       trips_ft_record = [trip_id, transit_line.vehicle_name]
       trips_ft_list.append(dict(zip(TripsFT.columns, trips_ft_record)))
     
       order = 1
       for segment in transit_line.segments():
          
        
           last_segment_number = max(enumerate(transit_line.segments()))[1].number
           tod = highway_assignment_tod[int(departure_time)/60]
      
       
           # Get segment time in decmial minutes
         
           segment_time = calc_transit_time(segment, segment.link.i_node.id, segment.link.j_node.id, tod, segment.transit_time_func, network_dictionary)
           
           # A one segment line (ferry):
           if segment.number == 0 and last_segment_number == 0:
                
                stop_times_record = [trip_id, dec_mins_to_HHMMSS(departure_time), dec_mins_to_HHMMSS(departure_time), 
                                     int(segment.i_node.id), order]
                stop_times_list.append(dict(zip(StopTimes.columns, stop_times_record)))
                
                stop_times_record = [trip_id, dec_mins_to_HHMMSS(departure_time + segment_time), 
                                     dec_mins_to_HHMMSS(departure_time + segment_time), int(segment.j_node.id), order + 1]
                stop_times_list.append(dict(zip(StopTimes.columns, stop_times_record)))
                
           # First Stop:
           elif segment.number == 0:
                stop_times_record = [trip_id, dec_mins_to_HHMMSS(departure_time), 
                                     dec_mins_to_HHMMSS(departure_time), int(segment.i_node.id), order]
                stop_times_list.append(dict(zip(StopTimes.columns, stop_times_record)))
                
                # Update departure time for next stop
                departure_time =  departure_time + segment_time
                order = order + 1
           
           elif segment.number == last_segment_number:
            # Last stop, need time of last segment
                # Check to see if there is a stop on the I-node:
                if segment.allow_alightings:
                    stop_times_record = [trip_id, dec_mins_to_HHMMSS(departure_time), 
                                        dec_mins_to_HHMMSS(departure_time + DWELL_TIME), int(segment.i_node.id), order]
                    stop_times_list.append(dict(zip(StopTimes.columns, stop_times_record)))
                    order = order + 1
                
                # Add final stop, update segment time
                departure_time = departure_time + segment_time + DWELL_TIME
                stop_times_record = [trip_id, dec_mins_to_HHMMSS(departure_time), 
                                     dec_mins_to_HHMMSS(departure_time), int(segment.j_node.id), order]
                stop_times_list.append(dict(zip(StopTimes.columns, stop_times_record)))
                
           
           else:
                if segment.allow_alightings:
                    # Its a stop
                    stop_times_record = [trip_id, dec_mins_to_HHMMSS(departure_time), 
                                         dec_mins_to_HHMMSS(departure_time + DWELL_TIME), int(segment.i_node.id), order]
                    stop_times_list.append(dict(zip(StopTimes.columns, stop_times_record)))
                    departure_time = departure_time + segment_time + DWELL_TIME
                    order = order + 1
                else:
                    # Not a stop, add time for this link
                    departure_time = departure_time + segment_time

def calc_transit_time(segment, link_i, link_j, tod, ttf, network_dictionary):
    '''
    Returns the transit time for a passed in segment in decimal minutes using the same factors we use for static assignment. ttf is a transit network input and is based
    on facility type and when the last stop was made.
    '''
    
    network = network_dictionary[tod]
  
    link = network.link(link_i, link_j)

    new_tod = ''
 
    # Check to see if link exists:
    if not link:
        # Get it from fall back dict:
        new_tod = fall_back_dict[tod]
        network = network_dictionary[new_tod]
        link = network.link(link_i, link_j)
        
    # Factors below would be stored in a config file. 
    # Bus Only, assume max speed
    if ttf == 4:
        transit_time = link.length * (60 / link.data2)
        
    # Rail time is stored in data2
    elif ttf == 5:
        transit_time = link.data2
       
    # Weave links- do not get a time
    elif link.data2 == 0:
        transit_time = 0
       
    # Local
    elif ttf == 11:
        if link.auto_time <= 0:
            transit_time = 1.037034 * (link.length * (60 / link.data2))
        else:
            transit_time = min(1.037034 * link.auto_time, link.length * 12)
        
    # Local, recent stop
    elif ttf == 12:
        if link.auto_time <= 0:
            transit_time = 1.285566 * (link.length * (60 / link.data2))
        else:
            transit_time = min(1.285566 * link.auto_time, link.length * 12)
      
    # Facility type is highway and last stop is greater than 2640 feet behind
    elif ttf == 13:
        if link.auto_time <= 0:
            transit_time = 1.265774 * (link.length * (60 / link.data2))
        else:
            transit_time = min(1.265774 * link.auto_time, link.length * 12)
      
    # Last stop is greater than 7920 feet behind
    elif ttf == 14:
        if link.auto_time <= 0:
            transit_time = 1.00584 * (link.length * (60 / link.data2))
        else:
            transit_time = 1.00584 * link.auto_time
    
            # TTF should not be 0- only here because of a transit coding error. Remove once fixed. 
    elif ttf == 0:
        if link.auto_time <= 0:
            transit_time = 1.00584 * (link.length * (60 / link.data2))
        else:
            transit_time = 1.00584 * link.auto_time
    else: 
        raise ValueError('Transit ID ' + str(segment.line) + ' and segment number ' + str(segment.number) + 'does not have a valid TTF')
      
    if transit_time < 0:
        # Speed's of 0 are allowed on weave links, but let's make sure there are no negative values. 
        raise ValueError('Transit ID ' + str(segment.line) + ' and segment number ' + str(segment.number) + 'has a speed lower than 0')
        
    return transit_time

def get_access_links(taz_list, stops_df, max_distance_in_feet):
    geod = pyproj.Geod(ellps='WGS84')
    buffer = max_distance_in_feet * 0.3048
    #taz_points = taz_df.as_matrix(columns=['lon', 'stop_lat', 'taz'])
    bus_stop_points = stops_df.as_matrix(columns=['stop_lon', 'stop_lat', 'stop_id'])
    access_links_list = []
    for row in taz_list:
        x = [[geod.inv(row[2], row[1], y[0], y[1])[2], row[0], y[2]] for y in bus_stop_points if geod.inv(row[2], row[1], y[0], y[1])[2] <= buffer]
        #x = [[geod.inv(row[2], row[1], y[0], y[1])[2], row[0], y[2]] for y in bus_stop_points]

        for record in x:
            distance = record[0]
            distance = distance * 3.28084/5280.0
            distance = float("{0:.2f}".format(distance))
            access_links_list.append({'taz' : record[1], 'stop_id' : record[2], 'dist' : distance}) 
    return access_links_list

def get_taz_nodes(network):
    taz_list = []
    #build tuple: (taz_id, lat, long)
    for node in network.nodes():
        if node.is_centroid:
            wgs84tuple = reproject_to_wgs84(node.x, node.y)
            taz_list.append((int(node.id), wgs84tuple[1], wgs84tuple[0]))
    return taz_list

def stop_to_stop_transfers(stops_df, routes_by_stop, max_distance_in_feet):
    '''
    Creates stop to stop transfers DataFrame for transfers.txt. Limits stops pairs by applying max_distance_in_feet.  
    '''
    
    # convert buffer to meters becayse pyproj.Geod.inv operates in meters:
    buffer = max_distance_in_feet * 0.3048
    points = stops_df.as_matrix(columns=['stop_lon', 'stop_lat', 'stop_id'])
    geod = pyproj.Geod(ellps='WGS84')
    
    # get all stop to stop combos and distances:
    x = [[geod.inv(x[0], x[1], y[0], y[1])[2], x[2], y[2]] for x, y in combinations(points, 2) if geod.inv(x[0], x[1], y[0], y[1])[2] <= buffer] 
    # fill list (data) with records that are within distance buffer. convert distance back to feet:
    data = []
    for record in x:
        stop1_routes = routes_by_stop[int(record[1])]
        stop2_routes = routes_by_stop[int(record[2])]
        distance = record[0]
        distance = distance * 3.28084/5280.0
        distance = float("{0:.2f}".format(distance))
        # check to see if there are routes in the first stop that are not at the second stop (of the pair)
        if [i for i in stop1_routes if i not in stop2_routes]:
            data.append({'dist' : distance, 'from_stop_id' : record[1], 'to_stop_id' : record[2], 'transfer_type' : 0})
        # check the other way
        if [i for i in stop2_routes if i not in stop1_routes]:
            data.append({'dist' : distance, 'from_stop_id' : record[2], 'to_stop_id' : record[1], 'transfer_type' : 0})
    return data

def stop_to_stop_transfersFT(transfer_list,timed_transfers_df):
    '''
    Creates stop to stop transfers DataFrame for transfers.txt. Limits stops pairs by applying max_distance_in_feet.  
    '''
    transfer_list_ft = []
    # add fields to transfer_list
    for record in transfer_list:
        record.update({'from_route_id' : " ", 'to_route_id' : " ", 'schedule_precedence' : " "})
        transfer_list_ft.append(record)
    for row in timed_transfers_df.itertuples():
        row = row[1: len(row)]
        #print (zip(timed_transfers_df.columns.tolist(), row))
        transfer_list_ft.append(zip(timed_transfers_df.columns.tolist(), row))

    return transfer_list_ft
