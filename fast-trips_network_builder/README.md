# fast-trips network builder 
This repository contains scripts and sample input files needed to build the supply-side network input files for [fast-trips](http://fast-trips.mtc.ca.gov/) based on the [Soundcast](https://github.com/psrc/soundcast/wiki) travel demand model.  It uses [transit assignment data files](https://github.com/psrc/soundcast/blob/5ce7547a8384df367c92d3e48c54eea86228f47e/scripts/summarize/standard/daily_bank.py) from Soundcast to build a set of files that together describe a network of transit service according to the [GTFS-PLUS standard](https://github.com/osplanning-data-standards/GTFS-PLUS). 


**version**: 0.0.1  
**updated**: 14 August 2017  
**created**: 09 september 2015  
**authors**:  

 * Stefan Coe  (Puget Sound Regional Council) 
 * Angela Yang (Puget Sound Regional Council) 

# Full Documentation
Fast-Trips Transit Network Design Specification v0.2, [technical memo](http://fast-trips.mtc.ca.gov/library/T2-NetworkDesign-StaticCopy-Sept2015V0.2.pdf). 

# Related Projects
[fast-trips](https://github.com/BayAreaMetro/fast-trips)

[Soundcast](https://github.com/psrc/soundcast)

[GTFS-PLUS](https://github.com/osplanning-data-standards/GTFS-PLUS)

[fast-trips Demand Converter](https://github.com/psrc/fast-trips_demand_converter)

# Getting Started
Follow the steps below to prepare to run the network builder: 
 * Download and install [Anaconda python 2.7 package](https://www.anaconda.com/download/)
 * If you need run Soundcast to get transit assignment data files, follow the [Soundcast setup steps](https://github.com/psrc/soundcast/wiki/Soundcast-Install)
 
# Input
The inputs to the network builder consist of: 
* [Soundcast transit bank](https://github.com/psrc/soundcast/blob/5ce7547a8384df367c92d3e48c54eea86228f47e/scripts/summarize/standard/daily_bank.py) for transit assignment. The files are generated from a Soundcast model run. Please make sure you use hourly transit banks. 

* A network builder MUST include the following input files:

Filename 			| Description										
----------			| -------------										
[`fare_id.csv`](https://github.com/psrc/fast-trips_network_builder/blob/master/inputs/fares/fare_id.csv)	| fare id									
[`stop_zones.csv`](https://github.com/psrc/fast-trips_network_builder/blob/master/inputs/fares/stop_zones.csv)		| stop zones		
[`fare_rules_ft.csv`](https://github.com/psrc/fast-trips_network_builder/blob/master/inputs/fares/fare_rules_ft.csv)| fare rules					
[`fare_attributes.csv`](https://github.com/psrc/fast-trips_network_builder/blob/master/inputs/fares/fare_attributes.csv)				| fare attributes								
[`fare_attributes_ft.csv`](https://github.com/psrc/fast-trips_network_builder/blob/master/inputs/fares/fare_attributes_ft.csv)		| fare attributes for fast trips		
[`fare_transfer_rules.csv`](https://github.com/psrc/fast-trips_network_builder/blob/master/inputs/fares/fare_transfer_rules.csvd)			| fare transfer rules									
[`vehicles.csv`](https://github.com/psrc/fast-trips_network_builder/blob/master/inputs/vehicles.csv)		| type of vehicles				
[`timed_transfers.csv`](https://github.com/psrc/fast-trips_network_builder/blob/master/inputs/timed_transfers.csv)				| transfer time								
[`line_attributes.csv`](https://github.com/psrc/fast-trips_network_builder/blob/master/inputs/line_attributes.csv)		| Get TAZ Nodes for walk access				
[`gtfs_shapeID_to_lineID.csv`](https://github.com/psrc/fast-trips_network_builder/blob/master/inputs/gtfs_shapeID_to_lineID.csv)	| Shape ID to model route crosswalk  		

*Note: the first six files in this list should be in a sub-folder named `fares`*

* The file [gtfs_shapeID_to_lineID.csv](https://github.com/psrc/fast-trips_network_builder/blob/master/inputs/gtfs_shapeID_to_lineID.csv) is not a Soundcast output.  It is created from a separate script, [reformat_GTFS_file.py](https://github.com/psrc/fast-trips_network_builder/blob/master/reformat_GTFS_file.py), which requires these two files as inputs:

Filename 			| Description										
----------			| -------------										
[`sc_headways.csv`](https://github.com/psrc/fast-trips_network_builder/blob/master/inputs/sc_headways.csv)	| 				headway information for transit lines		
[`hourly_trips33.txt`](https://github.com/psrc/fast-trips_network_builder/blob/master/inputs/hourly_trips33.txt)			| transit operator information	for transit lines 	

# Building the Network
1. If needed, edit and run [reformat_GTFS_file.py](https://github.com/psrc/fast-trips_network_builder/blob/master/reformat_GTFS_file.py) to create [gtfs_shapeID_to_lineID.csv](https://github.com/psrc/fast-trips_network_builder/blob/master/inputs/gtfs_shapeID_to_lineID.csv).

   *NOTE: This step is making sure Soudncast line id is consisted with GTFS shapeid.* 

2. Edit and run the [configuration file](https://github.com/psrc/fast-trips_network_builder/blob/master/config/input_configuration.py) under python 2.7 environment to set global variables and defaults.

   *NOTE: Please keep the transit network time of day bank setting consistent with your selection for the [transit demand converter](https://github.com/psrc/fast-trips_demand_converter). This will avoid transit time conflicts between network inputs and demand inputs during the fast-trips model run.* 

3. Run the [builder file](https://github.com/psrc/fast-trips_network_builder/blob/master/config/build_network.py) to generate the GTFS-PLUS .txt files.

4. If desired, run the [validation script](https://github.com/psrc/fast-trips_network_builder/blob/master/config/trip_validation.py).

# Output
* The output from the network builder is organized as a [GTFS-PLUS transit network](https://github.com/osplanning-data-standards/GTFS-PLUS) with data files including schedules, access, egress, and transfer information.

NOTE: [GTFS-Plus Data Standards Repository](https://github.com/osplanning-data-standards/GTFS-PLUS) is a draft specification and still under development.

# License
This project is licensed under [Apache 2.0](https://github.com/psrc/fast-trips_network_builder/blob/Angela/LICENSE.md)



