#!/usr/bin/python
# Creates the measurements between RUSSIAN anchors and a target  adds the measurment info to a file in the measurments folder
# for use in a application to read that info and make use of it.

# put ip range in target ips
# need to fix the number of probes , currently uses all 726 anchors as sources



import sys

print('Number of arguments:', len(sys.argv), 'arguments.')
print('Argument List:', str(sys.argv))
prefix = sys.argv[1]
country = sys.argv[2]
filesaved = sys.argv[3]
print(prefix,country,filesaved)
input('wait')


from ripe.atlas.cousteau import ProbeRequest, Traceroute, AtlasSource, AtlasRequest, AtlasCreateRequest
from datetime import datetime
import time
import json 
import os

ATLAS_API_KEY = "6f0e691d-056c-497d-9f5b-2297e970ec60"

filename = 'measurements/world_measurements.json'



# filters = {"tags": "NAT", "country_code": "gb", "asn_v4": "3333"}
filters = {"tags": "system-Anchor", "status": "1", "country_code": country,}
probes = ProbeRequest(**filters)
probe_list = []
measurements = {}
world_probes ={}
for source_probe in probes:
    probe_list.append(str(source_probe["id"]))
    world_probes[source_probe["id"]] = {}
    world_probes[source_probe["id"]] ["address"] = source_probe["address_v4"]
    world_probes[source_probe["id"]] ["coordinates"] = source_probe["geometry"]["coordinates"]
    
    # print(world_probes[source_probe["id"]])
print(world_probes)
target_ips =[]
for r in range(1,5):
    target_ips.append(prefix+str(r))

for r in range(250,255):
    target_ips.append(prefix+str(r))

print(target_ips)

my_measurements= {}

for target in target_ips:
    my_measurements[target] ={}
    print(probes.total_count)
    print(target)
    source_list = probe_list
    source_string = ','.join(source_list)
  
    print(source_string)
    input('wait')
    
    
    # , probe["address_v4"], probe["geometry"])
    # input("a key")

    # Create Measurement Specification Object
    # https://github.com/RIPE-NCC/ripe-atlas-cousteau/blob/master/docs/use.rst
    print('target is ', target)
    traceroute = Traceroute(
    af=4,
    target=target,
    description="Traceroute to "+target,
    protocol="ICMP",
    )

    source = AtlasSource(
    type="probes",
    value= source_string,
    requested= 10
    )
    
    print('tp',source_probe)
    print ('m', source_string)
    
    atlas_request = AtlasCreateRequest(
                
                key=ATLAS_API_KEY,
                measurements=[traceroute],
                sources=[source],
                is_oneoff=True)
                
    (is_success, response) = atlas_request.create()
    print(is_success, response)
    print(response,dir(response))
    # world_probes[target]['measurement'] = response['measurements'][0]
    my_measurements[target]['measurement']= response['measurements'][0]
    my_measurements[target]['success'] = is_success
    





    
              
    
    
    





                


    # targets_dict[prefix][target] = {}
    # targets_dict[prefix][target] = response['measurements'][0]
# create file of measurement,targesource_probe_id,......,..........
with open(filesaved, 'w') as outfile:
    json.dump(my_measurements, outfile)
outfile.close()
