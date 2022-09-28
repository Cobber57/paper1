import pprint
import os
import time
import collections
import sys
from decimal import Decimal
from geopy.distance import geodesic


if __name__ == "__main__":
    import json 
    from ripe.atlas.cousteau import Measurement, AtlasResultsRequest
    os.chdir('/home/paul/Documents/UK')
    #open testfile
    with open("measurements/uk_measurements_1.json") as file:
        measurements =json.load(file)
   
   
    # html = Html_Create(probes)
    targets = {}
    #print(measurements)
    for target_probe in measurements:
        this_measurement_id = measurements[target_probe]['measurement']
        kwargs = {
            "msm_id": this_measurement_id
            
        }

        is_success, results = AtlasResultsRequest(**kwargs).create()

        
        targets[this_measurement_id] = {}
        targets[this_measurement_id]['target_probe'] = target_probe
        targets[this_measurement_id]['target_address'] = measurements[target_probe]['address']
        targets[this_measurement_id]['target_coordinates'] = measurements[target_probe]['coordinates']
        targets[this_measurement_id]['results'] = {}
        for traceroute in results:
            #print('The source info is ', traceroute)
            source_probe = int(traceroute['prb_id'])
            targets[this_measurement_id]['results'][source_probe] = {}
            targets[this_measurement_id]['results'][source_probe]['source_address'] = traceroute['src_addr']
            targets[this_measurement_id]['results'][source_probe]['source_coordinates'] = measurements[str(source_probe)]['coordinates']
            #print(targets)
            #print(traceroute['result'])
            targets[this_measurement_id]['results'][source_probe]['hops'] = {}
            
            for hop in traceroute['result']:
                #print(hop)
                h = hop['hop']
                targets[this_measurement_id]['results'][source_probe]['hops'][h] = {}
                
                # 3 traceroutes are taken but we only need the quickest rtt time
                rtt = 100
                for tr in hop['result']:
                    #print(tr)
                    try:
                        if tr['rtt'] < rtt:
                            rtt = tr['rtt']
                            ip_from = tr['from']

                    except:
                        print('this traceroute doesnt have have an rtt value')
                targets[this_measurement_id]['results'][source_probe]['hops'][h]['rtt'] = rtt
                targets[this_measurement_id]['results'][source_probe]['hops'][h]['ip_from'] = ip_from
            # Work out max length of fibre from source to destination   
            targets[this_measurement_id]['results'][source_probe]['final_rtt'] = rtt
            fibre_max_length = (rtt/2) * ((.66*300000)/1000) 
            targets[this_measurement_id]['results'][source_probe]['fibre_length'] = fibre_max_length
            # Work out max geographical distance between source and destination
            source_coords = targets[this_measurement_id]['results'][source_probe]['source_coordinates']
            dest_coords = targets[this_measurement_id]['target_coordinates']
            distance = geodesic(source_coords, dest_coords)
            print(rtt,fibre_max_length,source_coords,dest_coords,distance)
            print ('Actual distance is from source probe',source_probe,' to target probe',target_probe ,'is ',distance)
            print ('Distance according to RTT values is within a',fibre_max_length, 'km radius of the source probe,',source_probe,'at',source_coords)
            
      
            input('test')
            
        
            


            
    with open("results/targets.json", 'w') as outfile:
        json.dump(targets, outfile)
    outfile.close()


           

       


        

        

