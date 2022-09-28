# Creates the measurements between 34 anchors in the UK and adds the measurment info to a file in the measurments folder
# for use in a application to read that info and make use of it.

from ripe.atlas.cousteau import ProbeRequest, Traceroute, AtlasSource, AtlasRequest, AtlasCreateRequest
from datetime import datetime
import time
import json 
import os

ATLAS_API_KEY = "6f0e691d-056c-497d-9f5b-2297e970ec60"

filename = 'measurements/ukfull1_measurements.json'

# filters = {"tags": "NAT", "country_code": "gb", "asn_v4": "3333"}
filters = {"tags": "system-Anchor", "country_code": "gb", "status": "1"}
probes = ProbeRequest(**filters)
probe_list = []
measurements = {}
i = 0
uk_probes ={}
for t_probe in probes:
    probe_list.append(str(t_probe["id"]))
    uk_probes[t_probe["id"]] = {}
    uk_probes[t_probe["id"]] ["address"] = t_probe["address_v4"]
    uk_probes[t_probe["id"]] ["coordinates"] = t_probe["geometry"]["coordinates"]
    i= i+1
    # print(uk_probes[t_probe["id"]])

print(uk_probes)
print(i)

for target_probe in uk_probes:
    print(probes.total_count)
    print(target_probe)
    source_list = probe_list.copy()
    print(probe_list)
    source_list.remove(str(target_probe))
    print(source_list)
    source_string = ','.join(source_list)
    '''
    source_string = "" 
    for i in source_list:
        print(i)
        source_string += str(i)
        source_string += ","
    '''    
    print(source_string)
    # input('wait')
    print (uk_probes[target_probe]) 
    target = uk_probes[target_probe]['address']
    # , probe["address_v4"], probe["geometry"])
    # input("a key")

    # Create Measurement Specification Object
    # https://github.com/RIPE-NCC/ripe-atlas-cousteau/blob/master/docs/use.rst
    # https://ripe-atlas-cousteau.readthedocs.io/en/latest/use.html#creating-measurements
    print('target is ', target)
    traceroute = Traceroute(
    af=4,
    target=target,
    description="Traceroute Anchors UK FULL",
    protocol="ICMP",
    )

    source = AtlasSource(
    type="probes",
    value= source_string,
    requested= 5
    )
    
    print('tp',target_probe)
    print ('m', source_string)
    
    atlas_request = AtlasCreateRequest(
                
                key=ATLAS_API_KEY,
                measurements=[traceroute],
                sources=[source],
                interval=3600,
                tags=["uk_anchors_tr"],

                is_oneoff=False)
                
    (is_success, response) = atlas_request.create()
    print(is_success, response)
    uk_probes[target_probe]['measurement'] = response['measurements'][0]
    





    
              
    
    
    





                


    # targets_dict[prefix][target] = {}
    # targets_dict[prefix][target] = response['measurements'][0]
# create file of measurement,target_probe_id,......,..........
with open(filename, 'w') as outfile:
    json.dump(uk_probes, outfile)
outfile.close()
