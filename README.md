# Thesis

Advanced Geolocation Techniques and Geopolitical Integration for a Resilient Internet Infrastructure his script reads UK facilities, extracts location and metadata, and creates an interactive HTML map.

create_measurements.py Creates the initial trace route measurements between 32 anchors in the UK
and adds the measurment info to a file in the measurments folder
for use in a application to read that info and make use of it.
1. Run create_measurements.py
read_measurements.py reads in the uk_measurments file created in step 1
and access's the RIPE ATLAS measurments to create a spreadsheet of distances vs RTT times results/results.xlsx
also saves all this infomation to results/targets.json file
2. Run read_measurements.py
Create_html reads in the file created in step2 and creates a html page showing
the geolocations of the probes
3. run create_html.py
