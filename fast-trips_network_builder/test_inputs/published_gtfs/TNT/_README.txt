changes:

fare_id: operatorname_servicetype(_zoneindex, optional)
	ex1. tntransit_local_bus
	ex2. tntransit_express_bus_Z1
fare_class: fair_id_timeindicator
	ex1. tntransit_local_bus_allday
	ex2. tntransit_local_bus_pm

price: in Dollars, with two decimal-places
	ex. 2.00

fare start_time and end_time:
	default to blank rather than 000001, 235959
	because we generally don't have time of day info for fares, and blanks indicate a base fare
	that would be overridden by time-specific fares
	
stop_ids:
	R1 = 185
	R2 = 186
	R3 = 183
	B1 = 144
	B2 = 137
	B3 = 128

stop_id in stop_times_ft: bug fix, stop_id was concatenation of line name and stop sequence, should just be the regular ol' stop_id

PNRs:
	P1 = 200
	P2 = 201
	
Zones:
	Z1 = 7
	Z2 = 5
	Z3 = 14
	Z4 = 12
	Z5 = 3