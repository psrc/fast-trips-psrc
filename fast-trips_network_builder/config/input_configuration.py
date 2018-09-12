import collections
# This file contains input parameters imported by Fast-Trips Network Building scripts.   

# Default dwell time in decimal minutes
DWELL_TIME = .25

#Service ID Field 
SERVICE_ID = 'PSRC'
use_published_departure_times = True
test_network = False
# Location of assingment banks
banks_path = 'Z:/Stefan/Soundcast_feb_twg/Banks'

agency_list = [{'agency_id' : 'PSRC', 'agency_name' : 'PSRC', 'agency_url' : "http://www.psrc.org", 'agency_timezone' : 'US/Pacific'}]
calender_list = [{'service_id' : 'PSRC', 'monday' : 1 ,'tuesday' : 1,'wednesday' : 1, 'thursday' : 1,'friday' : 1,'saturday' : 1, 'sunday' : 1, 
            'start_date' : '20160101', 'end_date' : '20161231'}]
##### Network Dictionaries:
# We currently have two disctinct transit networks- AM and MD - and we use them for multiple assignment periods. 
# 'transit_bank'- The transit network to use for a given time period (AM or MD). We use the same am transit network for 6to7, 7to8, and 8to9 assignments, 
#                 so we only need to use one. Same for MD (9to10, 10to14, 14to15). This will change for 2014 when we will have one network with headways 
#                 for each time period, like SFCTA currently does. 

# 'start_time'-   The mininum time a route can leave its first stop. Our transit demand starts at 6:00 and ends at 15:00, but we can not 
#                 have a hard start of the schedule at 6 because we would be missing service from routes that begin before 6:00 and 
#                 have stops that occur after 6:00. For now, lets start the schedule building at 5 using am peak service levels.

# "end_time'-     The max time a route can leave it's first stop. Note that all stops will be completed even if they occur after end_time. 

transit_network_tod = collections.OrderedDict()
# please keep this setting consistent with demand
#transit_network_tod['5to6'] = {'transit_bank' : '5to6', 'start_time' : 300, 'end_time' : 359}
#transit_network_tod['6to7'] = {'transit_bank' : '6to7', 'start_time' : 360, 'end_time' : 419}
#transit_network_tod['7to8'] = {'transit_bank' : '7to8', 'start_time' : 420, 'end_time' : 479}
transit_network_tod['8to9'] = {'transit_bank' : '8to9', 'start_time' : 480, 'end_time' : 539}
transit_network_tod['9to10'] = {'transit_bank' : '9to10', 'start_time' : 540, 'end_time' : 599}
transit_network_tod['10to14'] = {'transit_bank' : '10to14', 'start_time' : 600, 'end_time' : 839}
#transit_network_tod['14to15'] = {'transit_bank' : '14to15', 'start_time' : 840, 'end_time' : 899}
#transit_network_tod['15to16'] = {'transit_bank' : '15to16', 'start_time' : 900, 'end_time' : 959}
#transit_network_tod['16to17'] = {'transit_bank' : '16to17', 'start_time' : 960, 'end_time' : 1019}
#transit_network_tod['17to18'] = {'transit_bank' : '17to18', 'start_time' : 1020, 'end_time' : 1079}
#transit_network_tod['18to20'] = {'transit_bank' : '18to20', 'start_time' : 1080, 'end_time' : 1199}

#transit_networl_tod['20to5'] = {'transit_bank' : '20to5', 'start_time' : 1200, 'end_time' : }
#transit_network_tod['md'] = {'transit_bank' :'9to10', 'start_time' : 540, 'end_time' : 900, 'tod_int': 20000 }


# The highway asssignment bank that is used to get link speed/time. 
highway_assignment_tod = {5: '5to6', 6: '6to7', 7: '7to8', 8: '8to9', 9: '9to10', 10: '10to14', 11 : '10to14',
                          12: '10to14', 13 : '10to14', 14 : '14to15', 15 : '15to16', 16 : '16to17', 17: '17to18', 
                          18: '18to20', 19: '18to20', 20: '20to5', 21: '20to5', 22: '20to5', 23: '20to5', 24: '20to5'}

# Sometimes we need to get travel times from road networks that are not part of our static transit network time periods (6-9, 9-15). It's possible that a link
# belonging to a given transit route does not exist in these networks so we must have a fall back network. For example, a route departs it's first stop at 8:55 
# and continues make stops past 9. Any such stop should get it's stop to stop travel time from the 9to10 auto assignment bank, but it's possible that the link does 
# not exist (e.g. bus only lane that reverts back to GP during non-peak) for this network. In these cases, get the travel time from the '8to9' highway assignment bank.
# key = auto_assignment bank that does not contain the link, value = auto_assignment  bank that should be used instead. 
fall_back_dict = {'5to6' : '6to7', '9to10' : '8to9', '10to14' : '8to9', '15to16' : '14to15', '16to17' : '15to16', '17to18' : '16to17', '18to20' : '17to18', '20to5': '18to20'}

route_type_dict = {'r' : 0, 'c' : 2, 'b' : 3, 'p' : 3, 'f' : 4}