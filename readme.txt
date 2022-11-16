# myipgeolocator-v12.0.py is a standalone module which will read measurments from a file created by the create_measurements4.py
# it will then attempt to geolocate each of the hops of the traceroutes and create a Vantage Point table which is
# an ip address to geolocation coordinates.

# create_measurements4.py Creates the initial traceromeasurements between 32 anchors in the UK
# and adds the measurment info to a file in the measurments folder
# for use in a application to read that info and make use of it.
# 1. Run create_measurements4.py

# read_measurements4.py reads in the uk_measurments file created in step 1
# and acceesss the RIPE ATLAS measurments to create a spreadsheet of distances vs RTT times results/results.xlsx
# also saves all this infomation to results/targets.json file
# 2. Run read_measurements4.py

# Create_html reads in the file created in step2 and creates a html page showing
# the geolocations of the probes
# 3. run create_html.py
 
