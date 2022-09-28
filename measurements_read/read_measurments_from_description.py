import pprint
import os
import time
import collections
import sys
import json 
from ripe.atlas.cousteau import Measurement, AtlasResultsRequest, MeasurementRequest, AtlasCreateRequest
from geopy.geocoders import Nominatim
import ipinfo
from decimal import Decimal


if __name__ == "__main__":
    
    os.chdir('/home/paul/Documents/UK')
    #open testfile
    # with open("measurements/uk_measurements_1.json") as file:
        # measurements =json.load(file)
    # html = Html_Create(probes)
    targets = {}
    kwargs = { "description": 'Traceroute UK 3'}


    # is_success, results = AtlasResultsRequest(**kwargs).create()
    # filters = {"status": 1}
    measurements = MeasurementRequest(**kwargs)
        
    for msm in measurements:
        print(msm['id'])
    
    
    print (measurements.total_count)
    print(dir(AtlasCreateRequest.get_headers))
    
    '''
    for target_probe in measurements:
        this_measurement_id = measurements[target_probe]['measurement']
        
        kwargs = {
            "msm_id": this_measurement_id
            
        }

        is_success, results = AtlasResultsRequest(**kwargs).create()

        if is_success:
            print(this_measurement_id)
            print(target_probe)

            print(results)
        
        targets[this_measurement_id] = {}
        targets[this_measurement_id]['target_probe'] = target_probe
        targets[this_measurement_id]['target_address'] = measurements[target_probe]['address']
        targets[this_measurement_id]['target_coordinates'] = measurements[target_probe]['coordinates']
        for target in results:
            print('The target is ', target)
            for source in target:
                print('The source is ', source)
                source_probe = int(source['prb_id'])

                targets[this_measurement_id][source_probe] = {}
                targets[this_measurement_id][source_probe]['source_address'] = source['src_addr']
                print(targets)
            input("wait")
    '''