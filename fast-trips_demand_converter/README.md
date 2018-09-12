# PSRC-SoundCast to Fast-Trips Demand Data Converter
This project converts disaggregate SoundCast Activity-Based Travel Model demand to [Fast-Trips](https://github.com/MetropolitanTransportationCommission/fast-trips) input demand, using output from [PSRC Daysim Model] (https://github.com/psrc/daysim-old). 

# Full Documents
[Dyno-Demand technical memo](https://github.com/osplanning-data-standards/dyno-demand)

The demand data is reformatted to the Dyno-Demand format to be able to be read by Fast-Trips. 
The Dyno-demand format has one mandatory file (trip_list.txt) and two optional files [ household.txt and person.txt ].

# Related Projects
The parallel project [SF-CHAMP to Fast-Trips Demand Data Converter](https://github.com/sfcta/fast-trips_demand_converter) completed by [Bhargava Sana](https://github.com/bhargavasana) 

# Getting started

 `Convert_demand.py` is tested by Python 2.7.11 | Anaconda 2.2.0 (64-bit) | [MSC v1500 64 bit (AMD64)] on win32, and requests following library: h5py, numpy, pandas, datetime. 

The script reads:     `daysim_outputs_2014.h5` (PSRC Daysim trip file in HDF5 format)  
The script writes:    Input demand to [Fast-Trips](https://github.com/MetropolitanTransportationCommission/fast-trips) in [Dyno-Demand](https://github.com/osplanning-data-standards/dyno-demand) format:  
 - [`household.txt`](https://github.com/osplanning-data-standards/dyno-demand/blob/master/files/household.md)
 - [`person.txt`](https://github.com/osplanning-data-standards/dyno-demand/blob/master/files/person.md)
 - [`trip_list.txt`](https://github.com/osplanning-data-standards/dyno-demand/blob/master/files/trip_list.md) 

# Running 
The outcome saved at [Soundcast_fasttrips_demand_version0.1.zip](https://app.box.com/files/0/f/8524509565/3-Transit_Demand)

# Credits
This is based on a script originally written by [Lisa Zorn](https://github.com/lmz) and [Alireza Khani](https://github.com/akhani) in 2012:
`Q:\Model Development\FastTrips\Demand.CHAMP\ft_CHAMPdemandGenerator.py` - this is an internal reference

# License
This project is licensed under the [Apache 2.0] (https://github.com/psrc/fast-trips_demand_converter/blob/master/LICENSE.md)
