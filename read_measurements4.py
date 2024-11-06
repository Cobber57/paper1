import pprint
import os
import time
import collections
import sys
# from decimal import Decimal
from geopy.distance import geodesic
import xlsxwriter


if __name__ == "__main__":
    import json 
    from ripe.atlas.cousteau import Measurement, AtlasResultsRequest
    os.chdir('/home/paul/Documents/UK')
    #open testfile
    
    # with open("measurements/ukfull1_measurements.json") as file:
    with open("latest_measures.json") as file:
        measurements =json.load(file)
   
   
    # html = Html_Create(probes)
    targets = {}
    #print(measurements)
    for target_probe in measurements:
        print('Target probe is', target_probe)
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
            print('The source info is ', traceroute,'\n\n')
            source_probe = int(traceroute['prb_id'])
            targets[this_measurement_id]['results'][source_probe] = {}
            targets[this_measurement_id]['results'][source_probe]['source_address'] = traceroute['src_addr']
            targets[this_measurement_id]['results'][source_probe]['source_coordinates'] = measurements[str(source_probe)]['coordinates']
            print('TARGETS ARE',targets)
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
            targets[this_measurement_id]['results'][source_probe]['max_hops'] = h
            fibre_max_length = (rtt/2) * ((.6*300000)/1000) # in kilometres
            targets[this_measurement_id]['results'][source_probe]['fibre_length'] = fibre_max_length
            # Work out max geographical distance between source and destination
            source_coords = targets[this_measurement_id]['results'][source_probe]['source_coordinates']
            dest_coords = targets[this_measurement_id]['target_coordinates']
            distance = float(str(geodesic(source_coords, dest_coords)).split(' ')[0])
            targets[this_measurement_id]['results'][source_probe]['geodistance_to_target'] = distance
            print(rtt,fibre_max_length,source_coords,dest_coords,distance)
            print ('Actual distance is from source probe',source_probe,' to target probe',target_probe ,'is ',distance)
            print ('Distance according to RTT values is within a',fibre_max_length, 'km radius of the source probe,',source_probe,'at',source_coords)
            
      
            # input('test')
            
        
            
          

            
    # with open("results/targetsfull.json", 'w') as outfile:
    with open("results/targetslatest.json", 'w') as outfile:
        json.dump(targets, outfile)
    outfile.close()
      
    
    #workbook = xlsxwriter.Workbook('results/resultsfull'+ '.xlsx')
    workbook = xlsxwriter.Workbook('results/resultslatest'+ '.xlsx')
    worksheet = workbook.add_worksheet()

    # Add a bold format to use to highlight cells.
    bold = workbook.add_format({'bold': 1})

 
    worksheet.set_column(1, 1, 15)

    # Write some data headers.
    worksheet.write('A1', 'Target Probe', bold)
    worksheet.write('B1', 'Source Probe', bold)
    worksheet.write('C1', 'RTT (ms)', bold)
    worksheet.write('D1', 'Hops', bold)
    worksheet.write('E1', 'Fibre_max_length (km)', bold)
    worksheet.write('F1', 'Geo Distance (km)', bold)
    worksheet.write('G1', 'Error Margin', bold)
    worksheet.write('H1', 'Avg_ms_Hop', bold)
    worksheet.write('I1', 'Avg_km_ms', bold)
    # Write out the opposites
    worksheet.write('K1', 'Target Probe', bold)
    worksheet.write('L1', 'Source Probe', bold)
    worksheet.write('M1', 'RTT (ms)', bold)
    worksheet.write('N1', 'Hops', bold)
    worksheet.write('O1', 'Fibre_max_length (km)', bold)
    worksheet.write('P1', 'Geo Distance (km)', bold)
    worksheet.write('Q1', 'Error Margin', bold)
    worksheet.write('R1', 'Avg_ms_Hop', bold)
    worksheet.write('S1', 'Avg_km_ms', bold)
    
    probe_list = []
    for measurement in targets:
        probe_list.append(targets[measurement]['target_probe'])
        # print (probe_list)
    
    
    
    # Start from the first cell below the headers.
    
    
    row = 1
    col = 0

    
    count = 0 
    for measurement in targets:
    
        worksheet.write_string  (row, col, targets[measurement]['target_probe'])
        target_probe = targets[measurement]['target_probe']
        for source_probe in targets[measurement]['results']:
            
            print(targets[measurement]['results'][source_probe]['fibre_length'])
            f_length = float("{:.2f}".format(targets[measurement]['results'][source_probe]['fibre_length']))
            
            dist = float("{:.2f}".format(targets[measurement]['results'][source_probe]['geodistance_to_target']))
            worksheet.write_string  (row, col + 1, str(source_probe)) 
            rtt = float("{:.2f}".format(targets[measurement]['results'][source_probe]['final_rtt']))
            hops = float("{:.2f}".format(targets[measurement]['results'][source_probe]['max_hops']))
            worksheet.write_number  (row, col + 2, rtt)
            worksheet.write_number  (row, col + 3, hops)
            worksheet.write_number  (row, col + 4, f_length)
            worksheet.write_number  (row, col + 5, dist)
            error = f_length/dist
            worksheet.write_number  (row, col + 6, error)
            avg_time_per_hop = rtt/hops
            worksheet.write_number  (row, col + 7, avg_time_per_hop)
            avg_km_per_ms = dist/rtt
            worksheet.write_number  (row, col + 8, avg_km_per_ms)

            # Now write the opposite traceroutes
            col = 10
            for m in targets:
                # print('the target will be', targets[m]['target_probe'])
                if targets[m]['target_probe'] != target_probe:
                    # print(type(targets[m]['target_probe']), type(target_probe) )
                    # print(targets[m]['target_probe'],target_probe )
                    if targets[m]['target_probe'] == str(source_probe):
                        
                        for t in targets[m]['results']:
                            # print(type(t), type(target_probe))
                            if str(t) == target_probe:
                                source = target_probe
                                worksheet.write_string  (row, col, targets[m]['target_probe'])
                                worksheet.write_string  (row, col + 1, str(t))
                                f_length = float("{:.2f}".format(targets[m]['results'][t]['fibre_length']))

                                dist = float("{:.2f}".format(targets[m]['results'][t]['geodistance_to_target']))
                                rtt = float("{:.2f}".format(targets[m]['results'][t]['final_rtt']))
                                hops = float("{:.2f}".format(targets[m]['results'][t]['max_hops']))
                                worksheet.write_number  (row, col + 2, rtt)
                                worksheet.write_number  (row, col + 3, hops)
                                worksheet.write_number  (row, col + 4, f_length)
                                worksheet.write_number  (row, col + 5, dist)
                                error = f_length/dist
                                worksheet.write_number  (row, col + 6, error)
                                avg_time_per_hop = rtt/hops
                                worksheet.write_number  (row, col + 7, avg_time_per_hop)
                                avg_km_per_ms = dist/rtt
                                worksheet.write_number  (row, col + 8, avg_km_per_ms)
            count += 1
            row += 1
            col = 0





            # work way around opposites     
            
            
            
            
            



    print(count)
    count = 0
    row = 1
    col = 10
    


    '''
    for source_probe in probe_list:
        # print ('Source probe is ', source_probe)
        for measurement in targets:
            target_probe = targets[measurement]['target_probe']
            # print('target is ', target_probe)
            if source_probe != target_probe:
                
                for target in targets[measurement]['results']:
                    #print('s',source_probe, 'targets_source',target)
                    if int(source_probe) == target:
                        #print('WOOT s',source_probe, 't',target)
                        worksheet.write_string  (row, col, str(source_probe))
                        worksheet.write_string  (row, col + 1, str(target_probe))
                        rtt = targets[measurement]['results'][target]['final_rtt']
                        worksheet.write_string  (row, col + 2, str(rtt))
                        

                    # rtt = float("{:.2f}".format(targets[measurement]['results'][source_probe]['final_rtt']))
                    # hops = float("{:.2f}".format(targets[measurement]['results'][source_probe]['max_hops']))


                        count += 1
                        row += 1
                        col = 10
    
    count = 0
    row = 1
    col = 10

    for measurement in targets:
        target_probe = targets[measurement]['target_probe']
        print(target_probe)
        for source_probe in targets[measurement]['results']:
            for m in targets:
                if targets[m]['target_probe'] == str(source_probe):
                    print (target_probe,source_probe)
                    for t in targets[m]['results']:
                        print('t is',t, 's is', source_probe)
                        if t == source_probe:
                            print (t,source_probe)
                            print('woot')
                            worksheet.write_string  (row, col, str(source_probe))
                            worksheet.write_string  (row, col + 1, str(target_probe))
                            print(measurement, target_probe)
                            rtt = targets[measurement]['results'][target_probe]['final_rtt']
                            worksheet.write_string  (row, col + 2, str(rtt))
                            count += 1
                            row += 1
                            col = 10
    '''
    print(count)           
    workbook.close()
    


           

       


        

        

