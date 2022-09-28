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

n1 = pdb.get(resource.Network, 25376)
out_file = open("as2856.json", "w")
  
json.dump(n1, out_file)
  
out_file.close()