# RIPE test of ripe anchor lcoations


from datetime import datetime
import json 
import os

# Gets the required measuremnt from RIPE ATLAS and creates the initial dictionary file 

# info from https://ripe-atlas-cousteau.readthedocs.io/_/downloads/en/latest/pdf/
# from ripe.atlas.cousteau import Ping, Traceroute, AtlasSource, AtlasRequest, AtlasCreateRequest, AtlasLatestRequest, Probe, Measurement, ProbeRequest
from ripe.atlas.cousteau import ProbeRequest, Traceroute, AtlasSource, AtlasRequest, AtlasCreateRequest
from datetime import datetime

print(dir(AtlasRequest()))
# print(dir(AtlasCreateRequest()))

# Opensource Geocoder
from geopy.geocoders import Nominatim
geolocator = Nominatim(user_agent="aswindow")      
ATLAS_API_KEY = "6f0e691d-056c-497d-9f5b-2297e970ec60"
traceroute_dict = {}                                        # initialise the measuretments dictionary


from peeringdb import PeeringDB, resource
pdb = PeeringDB()

# PRSW, the Python RIPE Stat Wrapper, is a python package that simplifies access to the RIPE Stat public data API.
import prsw



# get targets

filters = {"tags": "system-Anchor", "country_code": "gb"}
probes = ProbeRequest(**filters)
probe_list = []
uk_probes = {}
# Create a Dictionary of the UK probes to be used 
for t_probe in probes:
    
    probe_list.append(str(t_probe["address_v4"]))
    uk_probes[t_probe["id"]] = {}
    uk_probes[t_probe["id"]] ["probe_ip"] = t_probe["address_v4"]
    uk_probes[t_probe["id"]] ["probe_x"] = t_probe["geometry"]["coordinates"][0]
    uk_probes[t_probe["id"]] ["probe_y"] = t_probe["geometry"]["coordinates"][1]
    uk_probes[t_probe["id"]] ["probe_asn"] = t_probe["asn_v4"]

print(probe_list)


url_prefix_path = "/api/v1/locate/"
url_suffix_path = "/best"
server =  'ipmap.ripe.net'



for ip in probe_list:
    url_path = url_prefix_path+ip+url_suffix_path
    print(url_path)
    request = AtlasRequest(**{"url_path": url_path, "server" : server})
    
    (is_success, response) = request.get()
    
    print(is_success)
    print (response)

    
    
    