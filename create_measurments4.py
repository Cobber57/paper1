# Creates the measurements between ALLcat anchors in the UK and adds the measurment info to a file in the measurments folder
# for use in a application to read that info and make use of it.

# Costeau is the official python wrapper around RIPE Atlas API allowing easier interaction
from ripe.atlas.cousteau import ProbeRequest, Traceroute, AtlasSource, AtlasRequest, AtlasCreateRequest
from datetime import datetime
import time
import json 
import os
import csv

ATLAS_API_KEY = "6f0e691d-056c-497d-9f5b-2297e970ec60"

filename = 'measurements/all_uk_probes.json'
target_list = 'target_list.txt'
f =  open (target_list,'r')  
ip_list = []
for ip in f:
    ip_list.append(ip.split('\n')[0])
    print('ip is', ip)
f.close()
print(ip_list)
input('wait')

# filters = {"tags": "NAT", "country_code": "gb", "asn_v4": "3333"}
# if you just want anchors ####### filters = {"tags": "system-Anchor", "country_code": "gb", "status": "1"}
filters = {"country_code": "gb", "status": "1"}
probes = ProbeRequest(**filters)
probe_list = []
measurements = {}
uk_probes ={}
for t_probe in probes:
    probe_list.append(str(t_probe["id"]))
    uk_probes[t_probe["id"]] = {}
    uk_probes[t_probe["id"]] ["address"] = t_probe["address_v4"]
    uk_probes[t_probe["id"]] ["coordinates"] = t_probe["geometry"]["coordinates"]
    
    # print(uk_probes[t_probe["id"]])
#print(uk_probes)
not_work =0
done = 0
for target_probe in uk_probes:
    if done == 31:
        break
    print(probes.total_count)
    print(target_probe)
    source_list = probe_list.copy()
    #print(probe_list)
    source_list.remove(str(target_probe))
    #print(source_list)
    source_string = ','.join(source_list)
    '''
    source_string = "" 
    for i in source_list:
        print(i)
        source_string += str(i)
        source_string += ","
    '''    
    #print(source_string)
    #input('wait')
    #print (uk_probes[target_probe]) 
    target = uk_probes[target_probe]['address']
    # , probe["address_v4"], probe["geometry"])
    # input("a key")

    # Create Measurement Specification Object
    # https://github.com/RIPE-NCC/ripe-atlas-cousteau/blob/master/docs/use.rst
    if target_probe == 55:
        continue
   
    if target in ip_list:
        print ('target is in already done list', target)
        #input('wait')
        continue
    try:
        print('target is ', target_probe, target)
        traceroute = Traceroute(
        af=4,
        target=target,
        description="FULL UK PROBE traceroute",
        protocol="ICMP",
        )

        source = AtlasSource(
        type="probes",
        value= source_string,
        requested= 650
        )
        
        print('tp',target_probe)
        #print ('m', source_string)
        
        atlas_request = AtlasCreateRequest(
                    
                    key=ATLAS_API_KEY,
                    measurements=[traceroute],
                    sources=[source],
                    is_oneoff=True)
                    
        (is_success, response) = atlas_request.create()
        print(is_success, response)
        ## you need to add this target to the already done list and write it to file
        uk_probes[target_probe]['measurement'] = response['measurements'][0]
        # create file of measurement,target_probe_id,......,..........
        with open(filename, 'a') as outfile:
            json.dump(uk_probes[target_probe], outfile)
        
        f = open(target_list, "a")
        f.write('\n'+str(target))
        f.close()
        
        done +=1
        input('wait', done)

    except:
        not_work +=1
        print('target is but didnt work', target_probe,target, not_work)
        f = open('target_list_not_work.txt', "a")
        f.write('\n'+str(target_probe))
        f.close()

    
              
    
    
    





                


    # targets_dict[prefix][target] = {}
    # targets_dict[prefix][target] = response['measurements'][0]

outfile.close()
