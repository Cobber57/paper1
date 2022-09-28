from datetime import datetime
import time
import json 
import os

# Gets the required measuremnt from RIPE ATLAS and creates the initial dictionary file 

# info from https://ripe-atlas-cousteau.readthedocs.io/_/downloads/en/latest/pdf/
from ripe.atlas.cousteau import Ping, Traceroute, AtlasSource, AtlasRequest, AtlasCreateRequest, AtlasLatestRequest, Probe, Measurement, ProbeRequest
# Sagans sole purpose is to make RIPE Atlas measurements manageable from within Python.
# https://ripe-atlas-sagan.readthedocs.io/en/latest/use.html#how-to-use-this-library
# Attributes and Methods at https://ripe-atlas-sagan.readthedocs.io/en/latest/types.html

from ripe.atlas.sagan import Result, TracerouteResult
# Opensource Geocoder
from geopy.geocoders import Nominatim
geolocator = Nominatim(user_agent="aswindow")      
ATLAS_API_KEY = "6f0e691d-056c-497d-9f5b-2297e970ec60"
traceroute_dict = {}                                        # initialise the measuretments dictionary

#from html_create import Html_Create 

from ipwhois.net import Net
from ipwhois.asn import ASNOrigin,IPASN
from peeringdb import PeeringDB, resource

pdb = PeeringDB()


# get targets
targets_dict = {}
f = open("data/globalEpisodes50-1.csv", "r")
i = 0
# a good thing about using a dictionary is it gets rid of duplicate entries.
for t in f:
    i += 1
    if i == 1: # avoid reading first line
        continue
    # Get Prefix and ASNs and alert type that are involved
    target = t.split(",")
    
    prefix = target[0]
    new_asn = target[1]
    old_asn = target[2]
    score = target[5]
    alert_type = target[13]

    targets_dict[prefix] = {}
    targets_dict[prefix][new_asn] = {}
    targets_dict[prefix][old_asn] = {}
    
    targets_dict[prefix][old_asn]['in_whois'] = False
    targets_dict[prefix][new_asn]['in_whois'] = False
    targets_dict[prefix][old_asn]['country'] = ''
    targets_dict[prefix][new_asn]['country'] = ''
    targets_dict[prefix][new_asn]['new_old_neither'] = 'new'
    targets_dict[prefix][old_asn]['new_old_neither'] = 'old'
    targets_dict[prefix][new_asn]['registry'] = ''
    targets_dict[prefix][new_asn]['country'] = ''
    targets_dict[prefix][new_asn]['description'] = ''
    targets_dict[prefix][old_asn]['registry'] = ''
    targets_dict[prefix][old_asn]['country'] = ''
    targets_dict[prefix][old_asn]['description'] = ''
   
    targets_dict[prefix]['country_total'] = 0
    targets_dict[prefix]['alert'] = alert_type
    targets_dict[prefix]['score'] = score

    # lookup what whois says about the Ip address.
    
    n = prefix.split('/')[0]
    net = Net(n)
    obj = IPASN(net)
    results = obj.lookup()
    targets_dict[prefix][old_asn]['in_whois'] = False
    targets_dict[prefix][new_asn]['in_whois'] = False
    targets_dict[prefix][old_asn]['country'] = ''
    targets_dict[prefix][new_asn]['country'] = ''
    targets_dict[prefix][new_asn]['new_old_neither'] = 'new'
    targets_dict[prefix][old_asn]['new_old_neither'] = 'old'
    targets_dict[prefix][new_asn]['registry'] = ''
    targets_dict[prefix][new_asn]['country'] = ''
    targets_dict[prefix][new_asn]['description'] = ''
    targets_dict[prefix][old_asn]['registry'] = ''
    targets_dict[prefix][old_asn]['country'] = ''
    targets_dict[prefix][old_asn]['description'] = ''   
    print(targets_dict)