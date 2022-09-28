#!/usr/bin/env python
#
# Program:      $Id: $ 
# Author:       Paul McCherry <p.mccherry@lancaster.ac.uk>
# Description:  create a file from the measurements that shows both forward and return paths 
#
class Create_Path_File:
    def __init__(self, forward_target_id, reverse_target_id, probe_dict, filename):
        
        probe_list = list(probe_dict.keys())  

        # gets target addresses
        self.forward_target_ip = str(probe_dict[forward_target_id]['probe_ip'])  # gets forward address 
        self.forward_target_lat = probe_dict[forward_target_id]['probe_x']
        self.forward_target_lon = probe_dict[forward_target_id]['probe_y']
        self.forward_target_address = 'Not Applicable'

        self.reverse_target_ip = str(probe_dict[reverse_target_id]['probe_ip'])  # gets reverse address 
        self.reverse_target_lat = probe_dict[reverse_target_id]['probe_x']
        self.reverse_target_lon = probe_dict[reverse_target_id]['probe_y']
        self.reverse_target_address = 'Not Applicable'
        
        self.filename = filename      
        # self.filename = 'web/targets/target_tr_'+str(self.target_ip)+'.html'   

        



if __name__ == "__main__":
    # Creates a list of UK anchors, reads in a measurements file and creates the html files for each


    from ripe.atlas.cousteau import ProbeRequest, Traceroute, AtlasSource, AtlasRequest, AtlasCreateRequest
    from datetime import datetime
    import time
    import json 
    import sys
    import os
    from geopy.geocoders import Nominatim
    from geopy.distance import geodesic
    # from haversine import haversine
    import great_circle_calculator.great_circle_calculator as gcc
    # PRSW, the Python RIPE Stat Wrapper, is a python package that simplifies access to the RIPE Stat public data API.
    import prsw
    # https://pypi.org/project/prsw/
    my_ripe = prsw.RIPEstat()

    geolocator = Nominatim(user_agent="aswindow")

    ATLAS_API_KEY = "6f0e691d-056c-497d-9f5b-2297e970ec60"

    filename2 = 'measurements/uk_measurements.json'

    # filters = {"tags": "NAT", "country_code": "gb", "asn_v4": "3333"}
    filters = {"tags": "system-Anchor", "country_code": "gb"}
    probes = ProbeRequest(**filters)
    probe_list = []
    measurements = {}
    uk_probes ={}
    asn_list = []
    addresses_list =[]
    count = 0
    add_count = 0
    numberoffiles = 0

    with open(sys.argv[1]) as file:
            measurements =json.load(file)
        measurement =  {}
        # Read in measurements

        measurement[this_target] = {}
        mself.foward = measurements[measurement_id]["target_address"]
        measurement[this_target] ["probe_x"] = measurements[measurement_id]["target_coordinates"][1]
        measurement[this_target] ["probe_y"] = measurements[measurement_id]["target_coordinates"][0]
        measurement[this_target] ["probe_asn"] = measurements[measurement_id] ["target_probe"]
        for measurement_id in measurements: