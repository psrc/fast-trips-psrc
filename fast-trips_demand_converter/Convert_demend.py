import h5py
import numpy as np
import pandas as pd
import datetime

SOUNDCAST_DEMAND = r'C:/Users/Angela/Documents/Daysim/daysim_outputs_2014.h5'
OUTPUT_PATH = r'H:/FastTrips/'
HOUSEHOLD_OUTFILE = os.path.join(OUTPUT_PATH, 'household.txt')
PERSON_OUTFILE =  os.path.join(OUTPUT_PATH, 'person.txt')
TRIPLIST_OUTFILE= os.path.join(OUTPUT_PATH, 'trip_list.txt')
transit_mode = 6
trip_begin_time = 360
trip_end_time = 540
time_zone = 'AM'

#Daysim outputs:
my_store = h5py.File(SOUNDCAST_DEMAND, "r+")
#Build the dataframe
def build_df(set_name, set_fields_dict):
     daysim_set = my_store[set_name]
     #Populate trip_array_dict, key is new field name, value are numpy arrays:
     arrays_dict = {}
     for FTs_field_name, field_name in set_fields_dict.iteritems():
         print field_name
         arrays_dict[FTs_field_name] = np.asarray(daysim_set[field_name], dtype = "int")
     #Create a DataFrame from the individual arrays 
     set_table = pd.DataFrame(arrays_dict)
     return set_table

#Get the fields we need from the trip table, create new field names for FAST-TrIPs
trip_fields_dict = {'pno' : 'pno', 
                    'hh_id' : 'hhno', 
                    'o_taz': 'otaz', 
                    'd_taz' : 'dtaz', 
                    'Mode' : 'mode',
                    'purpose' : 'dpurp', 
                    'deptm': 'deptm', 
                    'arrtm' : 'arrtm', 
                    'vot' : 'vot'}
person_fields_dict = {'pno': 'pno', 
                      'hh_id' : 'hhno', 
                      'age' : 'pagey', 
                      'pgend' : 'pgend', 
                      'pwtyp': 'pwtyp', 
                      'wpcl' : 'pwpcl', 
                      'transit_pass' : 'ptpass'}
household_fields_dict = {'hh_id' : 'hhno', 
                         'hh_vehicles' : 'hhvehs', 
                         'hh_income' : 'hhincome', 
                         'hh_size': 'hhsize', 
                         'hpcl' : 'hhparcel'}
trip_table = build_df('Trip', trip_fields_dict)
print trip_table.head()
person_table = build_df('Person', person_fields_dict)
print person_table.head()
household_table = build_df('Household', household_fields_dict)
print household_table.head()
my_store.close

#######################Prepare for trip_list.txt#######################

#Transfer departure and arrive time into HH:MM:SS form
def time(seconds):
    m, s = divmod(seconds, 60)
    h, m = divmod(m, 60)
    time_frame = "%d:%02d:%02d" % (h, m, s)
    return time_frame

def mode_id(id, eligible_zones_list): 
    mode_id = {}
    for ele in range(0,4001): 
        if ele in eligible_zones_list: 
            mode_id[ele] = id
        else: 
            mode_id[ele] = 0
    return mode_id 

zones = list(range(3751, 4001))

def trip_list(transit_mode_id, eligible_zones_list, min_depart_time, max_depart_time, time_period):

    #only focus on transit trips
    transit_table = trip_table[trip_table['Mode'] == transit_mode_id]
    print '1',  transit_table.shape

    #Transfer departure and arrive time into HH:MM:SS form
    dep_time_arr = []
    arr_time_arr = []
    for ele in transit_table['deptm']: 
        ele = ele*60
        dep_time_arr.append(time(ele))
    for ele in transit_table['arrtm']: 
        ele = ele*60
        arr_time_arr.append(time(ele))
    transit_table['departure_time'] = dep_time_arr
    transit_table['arrival_time'] = arr_time_arr
    print '2', transit_table.shape

    #PNR for Only Os and Ds that are eligible:
    mode_id_o = mode_id(1,eligible_zones_list)
    mode_id_d = mode_id(2,eligible_zones_list)
    transit_table['mode_Orig'] = transit_table['o_taz'].map(mode_id_o)
    transit_table['mode_Dest'] = transit_table['d_taz'].map(mode_id_d)
    transit_table['mode_id'] = transit_table.apply(lambda row: (row['mode_Orig'] + row['mode_Dest']), axis=1)
    transit_table['mode'] = transit_table['mode_id'].map({0: 'walk-transit-walk', 1:'PNR-transit-walk', 2:'walk-transit-PNR'})
    transit_table.drop(['mode_Orig','mode_Dest', 'mode_id'], axis=1)
    print '3', transit_table.shape

    #Query for time of day and mode
    qstring = 'deptm >= ' + str(min_depart_time) + ' and deptm <= ' + str(max_depart_time) + ' and Mode == ' + str(transit_mode_id)
    transit_table = transit_table.query(qstring)
    print '4', transit_table.shape

    #Add some columns that are required for FAST-TrIPs
    transit_table['timePeriod'] = time_period
    transit_table['time_target'] = 'arrival'

    # Add person_trip_id
    transit_table['person_trip_id'] = trip_table.groupby(['hh_id', 'pno']).cumcount()+1

    #trip_table['person_id'] = np.arange(1, len(trip_table) + 1)
    transit_table['person_id'] = transit_table.hh_id.astype(str) + '_' + transit_table.pno.astype(str)
    print '5', transit_table.shape
    return transit_table


transit_trips = trip_list(transit_mode, zones, trip_begin_time, trip_end_time, time_zone)
transit_trips_cols = ['person_id', 'person_trip_id', 'o_taz', 'd_taz', 'mode', 'purpose', 'departure_time', 'arrival_time', 'timePeriod', 'time_target', 'vot']
transit_trips.to_csv(TRIPLIST_OUTFILE, 
                     columns = transit_trips_cols, 
                     index = False, sep=',') 
print len(transit_trips)

################Prepare for person.txt################

#Create the unique id for identifing travellers
person_table['person_id'] = person_table.hh_id.astype(str) + '_' + person_table.pno.astype(str) 
#worker status
person_table['work_status'] = person_table['pwtyp'].map({0: 'unemployed', 1:'full-time', 2:'full-time'})
#gender
person_table['gender'] = person_table['pgend'].map({1: 'male', 2:'female', 9:'none'})
#work at home: if work pacel = home pacel
left = person_table
right = household_table.loc[:, ['hh_id', 'hpcl']]
result = pd.merge(left, right, on='hh_id')
work_at_home = []

for ele in result.index:
     if result['wpcl'][ele] == result['hpcl'][ele]:
         work_at_home.append(1)
     else: 
         work_at_home.append(0)
person_table['work_at_home'] = work_at_home

#Add some columns that are required for FAST-TrIPs
person_table['multiple_jobs'] = 'none'
person_table['disability'] = 'none'

person_table_cols = ['person_id', 'hh_id', 'age', 'gender', 'work_status', 'work_at_home', 'multiple_jobs', 'transit_pass', 'disability']
person_table.to_csv(PERSON_OUTFILE, 
                    columns = person_table_cols, 
                    index = False, sep=',') 
print len(person_table)

###################Prepare for hosuehold.txt##################

#find out that [hh_grdsch], [hh_highsch], [hh_presch], [hh_workers] are all with '-1' value 
def person_type(condition, typle):
    global household_table
    left = household_table
    person_type = person_table.loc[condition]
    person_type_no = person_type.loc[:, ['hh_id']]

    right = pd.DataFrame((person_type_no.groupby('hh_id').size()), columns = [typle])
    right['hh_id'] = right.index
    household_table = pd.merge(left, right, on='hh_id', how='outer').fillna(0)
    household_table[typle] = household_table[typle].astype(int)
    #return household_table
    print np.unique(np.array(household_table[typle]))

person_type_condi = {'hh_presch': (person_table['age'] <= 4), 
                     'hh_grdsch': ((person_table['age'] > 4) & (person_table['age'] <= 15)), 
                     'hh_hghsch': ((person_table['age'] > 15) & (person_table['age'] <= 17)),  
                     'hh_workers': (person_table['work_status'] > 0), 
                     'hh_elders': (person_table['age'] >= 65)}
for type_key in person_type_condi: 
    houshold_table = person_type(person_type_condi[type_key], type_key)

household_table_cols = ['hh_id', 'hh_vehicles', 'hh_income', 'hh_size', 'hh_workers', 'hh_presch', 'hh_grdsch', 'hh_hghsch', 'hh_elders']
household_table.to_csv(HOUSEHOLD_OUTFILE, 
                       columns = household_table_cols, 
                       index = False, sep=',')
print len(household_table)

print 'done'

