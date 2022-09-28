#!/usr/bin/env python
# fully working upto finding the correct IXP entry and exit points
# and creates the map
# now need to
#  1. Most important, calculate the distances from ixp exit point to target 
#  2. compare results with result from CBG, and RIPEMAP 
#  3. force the route to go via the xp
#  4. display the additional colocation facilities
#  5. route via the colocation facilities
#  6. test method on unkown targets
#  7. test method on bgpstream hijack results 
# Creates a list of UK anchors, reads in a measurements file and creates the html files for each
# requries my Htmlcreate13.py 
def convert(lst):
    my_dict = {}
    for l in lst:
        id = l['id']
        my_dict[id] = {}
        for key,value in l.items():
            my_dict[id][key] = value
    
    return my_dict

def get_hop_location(prev_hop,hop):

    # Create location of where to place this hop
    this_rtt = measurements[measurement_id]['results'][probe_id]['hops'][hop]['rtt']
    
    this_ip = measurements[measurement_id]['results'][probe_id]['hops'][hop]['ip_from']

    # if location cannot be worked out then just use last rtt value plus default of .1 ms                   
    if this_rtt > rtt:
        # TODO: possible problem if this default rtt goes over the max_rtt
        this_rtt = last_rtt + default_rtt
    
    
    this_fraction = this_rtt/rtt 
    if source_coords >= target_coords:
        hop_coords =  target_coords
    
    else:
        hop_coords = gcc.intermediate_point(source_coords, target_coords,fraction=this_fraction)

    this_hop = {}
    this_hop['id'] = hop
    this_hop['hop_latitude'] = hop_coords[1]
    this_hop['hop_longitude'] = hop_coords[0]
    lat1 = current_lat
    lon1 = current_lon
    lat2 = this_hop['hop_latitude']
    lon2 = this_hop['hop_longitude']
    hop_distance = gcc.distance_between_points(source_coords, hop_coords, unit='kilometers',haversine=True)
    
    this_hop['from'] = measurements[measurement_id]['results'][str(probe_id)]['hops'][hop]['ip_from']
    this_hop['rtt'] =  measurements[measurement_id]['results'][str(probe_id)]['hops'][hop]['rtt']
    this_hop['address'] = 'no address'
    this_hop['asn'] = []
    
    print('************* the ip address of this hop is',this_ip, 'and the rtt is', this_rtt)
    asns = []
    # Check to see if ipaddress belongs to ASN 196745 as there seems to be some anomaly that it doesnt report it at 
    # https://stat.ripe.net/data/network-info/data.json?resource=37.143.136.250
    # 
    print(measurements[measurement_id]['results'][str(probe_id)]['hops'][hop])
    print(this_hop['from'],this_hop['asn'] )
    if ipaddress.ip_address(this_hop['from']) in ipaddress.ip_network('37.143.136.0/24'):
        # DigitalOcean on RIPE
        this_hop['asn'] = ['196745']
        asns = this_hop['asn']
    elif ipaddress.ip_address(this_hop['from']) in ipaddress.ip_network('138.197.0.0/16'):
        # TODO: add a search on the arin database
        this_hop['asn'] = ['14061']
        asns=this_hop['asn']
    

    else:
        for ippre in local_subnets:


            print(this_hop['from'], ippre)
            # input('wait')
            if this_hop['from'].startswith(ippre):
                # have set initial asn to be that of the probe to ensure there is always a prev_asn (see prev_hop definition)
                print(prev_hop)
                this_hop['asn'] = prev_hop
                asns = this_hop['asn']
                print('this hop asn is now prev hop asn',this_hop['asn'])
                # if still no asn because all the hops have been local from the probe then use the probe asn
                if not this_hop['asn']:
                    this_hop['asn'] = uk_probes[probe_id]["probe_asn"] 
                    asns = this_hop['asn']    
                    print('this hop asn is now the probes hop asn',this_hop['asn'])
                break

    
    if not asns:
    
        # Workout location of Hop
        response = ripe.network_info(this_ip)
        
        options = {
            'query-string' : this_ip,
            'type-filter' : 'route',
            'flags' : ['no-irt','no-referenced'],
            'source' : 'RIPE'
            }
        r = requests.get(ripe_url, params=options)
        print (r.status_code)
        
        
        if r.status_code == 200:
            x = r.json()
            attributes = x['objects']['object'][0]['attributes']['attribute']
            for attrib in attributes:
                if attrib['name'] == 'origin':
                    ripedb_asn = attrib['value']
                    # had to make this overly complex change because i  swapped from using RIPE stat to RIPE database
                    asns = [int(re.split('AS|as', ripedb_asn)[1])]
                    print(ripedb_asn, 'compare ripe db with ripe stat ',response.asns,asns )
        else:
            # if RIPE database fails to return a ASN try ripetsat
            asns = response.asns
            # if ripestat fails then default to previous
            if not response.asns:
                print('requests isnt working and even response isnt',response.asns)
                print('print this is requests text',r.text)
                print ('defaulting to previous asn')
                asns = prev_hop
                input('wait')
    
    
    
    
    
    #used to use ripestat but moved to RIPE db
    #this_hop['asn'] = response.asns
    this_hop['asn'] = asns
    
    print('THis HOP ASN',this_hop['asn'])
    
    
    return this_ip, this_hop, this_rtt, lat1, lon1, lat2, lon2, hop_distance

if __name__ == "__main__":
    
    from Htmlcreate3 import Html_Create # my htmlcreate module
    from ripe.atlas.cousteau import ProbeRequest, Traceroute, AtlasSource, AtlasRequest, AtlasCreateRequest
    from datetime import datetime
    import time
    import json 
    import os
    from geopy.geocoders import Nominatim
    from geopy.distance import geodesic
    # from haversine import haversine
    import great_circle_calculator.great_circle_calculator as gcc
    # PRSW, the Python RIPE Stat Wrapper, is a python package that simplifies access to the RIPE Stat public data API.
    import prsw
    import ipwhois
    import re

    import ipaddress
    import json

    #from ixp_create_test_rectangle import create_ixp


    from peeringdb import PeeringDB, resource, config
    pdb = PeeringDB()
    # pdb.update_all() # update my local database



    # https://pypi.org/project/prsw/
    # Check RPKI validation status
    # print(ripe.rpki_validation_status(3333, '193.0.0.0/21').status)
    # Find all announced prefixes for a Autonomous System
    # prefixes = ripe.announced_prefixes(3333)
    # however this returns multiple ASNs for a given prefix, prbably best using the RIPE database for this
    ripe = prsw.RIPEstat()
    # import request so can access the RIPE database REST API 
    import requests
    ripe_url = 'https://rest.db.ripe.net/search.json'


    local_subnets = ['10.', '172.16.', '172.17.', '172.18.', '172.19.', '172.20.', '172.21.', '172.22.',
'172.23.', '172.24.', '172.25.', '172.26.', '172.27.', '172.28.', '172.29.', '172.30.', '172.31.', '192.168.',
'100.64.', '100.65.', '100.66.', '100.67.', '100.68.', '100.69.',
'100.70.', '100.71.', '100.72.', '100.73.', '100.74.', '100.75.', '100.76.', '100.77.', '100.78.',
'100.79.', '100.80.', '100.81.', '100.82.', '100.83.', '100.84.', '100.85.', '100.86.', '100.87.',
'100.88.', '100.89.', '100.90.', '100.91.', '100.92.', '100.93.', '100.94.', '100.95.', '100.96.',
'100.97.', '100.98.', '100.99.', '100.100.', '100.101.', '100.102.', '100.103.', '100.104.', '100.105.',
'100.106.', '100.107.', '100.108.', '100.109.', '100.110.', '100.111.', '100.112.', '100.113.', '100.114.',
'100.115.', '100.116.', '100.117.', '100.118.', '100.119.', '100.120.', '100.121.', '100.122.', '100.123.',
'100.124.', '100.125.', '100.126.', '100.127.']


    # If need to refresh  prefixes and networks run the 2 commands below instead of open
    # dont forget to remove the open statements. Could also create these files from menuuk.py
    # ipprefixes = pdb.fetch_all(resource.InternetExchangeLanPrefix)
    # nets = pdb.fetch_all(resource.Network)

    # Read in the prefixes info
    with open('peeringdb_test_results/ipprefixes_all.json') as f:
        ipprefixes = json.load(f)

    
    # Read in the networks info
    with open('peeringdb_test_results/networks_all.json') as f:
        nets = json.load(f)
    
    # Convert the networks file to a dictionary
    networks = convert(nets)

    # Read in the UK Internet Exchange info
    with open('peeringdb_test_results/uk_ixps.json') as f:
        ixps_uk = json.load(f)

    # Read in the UK Facilities records
    with open('peeringdb_test_results/uk_facilities.json') as f:
        facilitys_uk = json.load(f)

    # Open the measurements file created previously
    # filename2 = 'measurements/uk_measurements.json' # for full uk_measurements
    
    with open("results/target_6087.json") as f:
        measurements =json.load(f)

    
    
    # filters = {"tags": "NAT", "country_code": "gb", "asn_v4": "3333"}
    filters = {"tags": "system-Anchor", "country_code": "gb"}
    probes = ProbeRequest(**filters)




    ATLAS_API_KEY = "6f0e691d-056c-497d-9f5b-2297e970ec60"



    
    probe_list = []
    uk_probes ={}
    asn_list = []
    addresses_list =[]
    count = 0
    add_count = 0
    numberoffiles = 0

    # Create a Dictionary of the UK probes to be used 
    for t_probe in probes:
        
        probe_list.append(str(t_probe["id"]))
        uk_probes[t_probe["id"]] = {}
        uk_probes[t_probe["id"]] ["probe_ip"] = t_probe["address_v4"]
        uk_probes[t_probe["id"]] ["probe_x"] = t_probe["geometry"]["coordinates"][0]
        uk_probes[t_probe["id"]] ["probe_y"] = t_probe["geometry"]["coordinates"][1]
        uk_probes[t_probe["id"]] ["probe_asn"] = t_probe["asn_v4"]


    print(ixps_uk)
    # input('wait')
    
    # create a list of ipv4 prefixes for later use (ipv6 can wait for now)
    
    ix_prefix_list = []
    key = 'ipv4_prefix'
    for ix in ixps_uk:

        if key in ixps_uk[ix]:
            ix_prefix_list.append(ixps_uk[ix]['ipv4_prefix'])
        #create a list of probes that use this ixp
        ixps_uk[ix]['probes'] = []
    
    
    
        


    # Add any facilities that may have been discovered manually
    facilitys_uk['8628'] = {}
    facilitys_uk['8628']["org_id"] = 26163
    facilitys_uk['8628']["name"] = 'Datacenta Hosting'
    facilitys_uk['8628']["address1"] = "Dorset Innovation Park" 
    facilitys_uk['8628']["address2" ] = ""
    facilitys_uk['8628']["city"] =  "Winfrith Newburgh"
    facilitys_uk['8628']["country"] = "GB"
    facilitys_uk['8628']["postcode"] = "DT2 8ZB"
    facilitys_uk['8628']["latitude"] = 50.681852 
    facilitys_uk['8628']["longitude"] = -2.256535


    
    # Create a web based menu to provide easy access to Target maps
    menu_file = 'web/targets/menu.html'
    cmd = 'rm ' + menu_file
    os.system(cmd)
    menu = open(menu_file,'a')
    menu.write('<!DOCTYPE html>\n<html>\n<body>\n\n<h1>UK target Links</h1>\n')
    link1_string = '<p><a href="'
    link2_string = '">'
    link3_string = '</a></p>'

    
    measurement =  {}
    
    print(measurements)

    # Read in measurements

    for measurement_id in measurements:
        
        this_target = measurements[measurement_id]['target_probe']
        
        print("TARGET ***************************************************",this_target)

        measurement[this_target] = {}
        measurement[this_target] ["probe_ip"] = measurements[measurement_id]["target_address"]
        measurement[this_target] ["probe_x"] = measurements[measurement_id]["target_coordinates"][1]
        measurement[this_target] ["probe_y"] = measurements[measurement_id]["target_coordinates"][0]
        measurement[this_target] ["probe_asn"] = measurements[measurement_id] ["target_probe"]

        
        html = Html_Create(this_target,measurement)     
        html.create_header_html()          # create the file (named after the target IP and centralise the map )
        target_lon = measurement[this_target] ["probe_y"]
        target_lat = measurement[this_target] ["probe_x"]
        target_coords = (target_lon,target_lat)
        # Create the target probe          
        html.create_target(int(this_target),uk_probes) 

        # Add target to web based menu
        menu = open(menu_file,'a')
        menu.write(link1_string + 'http://icloud9.co.uk/phd/uk/target_tr_'+measurement[this_target]["probe_ip"] +'.html' +link2_string +'Probe : '+this_target+ ' Target IP : ' +measurement[this_target]["probe_ip"]+' '  + link3_string+'\n')
        menu.close()
        
        #Create the Source Probes
        for probe_id in measurements[measurement_id]['results']:
            print (probe_id,'*************************************************')
            ixp_entered_id = 0
            ixp_entered_flag = False
            facilities_used = []
            # Only iterate through source probe's not the target probe

            if probe_id != this_target:

                # Now create the probes 
                html.create_probes(int(probe_id),uk_probes) 
                source_lon = measurements[measurement_id]['results'][probe_id]['source_coordinates'][0]
                source_lat = measurements[measurement_id]['results'][probe_id]['source_coordinates'][1]
                source_coords = (source_lon,source_lat) 
                max_distance = gcc.distance_between_points(source_coords, target_coords, unit='kilometers',haversine=True)
                

                
                if measurement[this_target] ["probe_ip"] != None:
                    current_ip = measurement[this_target] ["probe_ip"] 
                else:
                    current_ip = 'unknown'
                # Now create the Greater Circle around the probe using the RTT value
                html.create_greater(int(probe_id),uk_probes,measurements[measurement_id]['results'][probe_id]['final_rtt'], this_target) 
                
                # now create the hops between the source and target
                
                hops = measurements[measurement_id]['results'][probe_id]['max_hops']
                rtt = measurements[measurement_id]['results'][probe_id]['final_rtt']

                current_lat = source_lat
                current_lon = source_lon
                last_rtt = 0
                # amount to add where rtt has failed, .01 = 1km from last hop
                default_rtt = .01

                # create forward path
                
                prev_hop ={}
                print(uk_probes[int(probe_id)])
                prev_hop['asn'] = uk_probes[int(probe_id)]["probe_asn"]
                for hop in measurements[measurement_id]['results'][probe_id]['hops']:
                    
                    fac_exit_hop = False
                    fac_entry_hop = False 
                    print('previous hop',prev_hop, 'ip address', measurements[measurement_id]['results'][probe_id]['hops'][hop])
                    this_ip, this_hop, this_rtt, lat1, lon1, lat2, lon2, hop_distance = get_hop_location(prev_hop['asn'],hop)

                    # check for Internet Exchange
                    this_ixp = 0
                    
                    
                    
                    # Group the probes by the IXP they pass through
                    for prefix in ix_prefix_list:
                        if ipaddress.ip_address(this_ip) in ipaddress.ip_network(prefix):
                            for ixp in ixps_uk:
                                if ixps_uk[ixp]['ipv4_prefix'] == prefix:
                                    # this ip address belongs to an IXP
                                    this_ixp = ixp
                                    
                                    # print('Target is ', this_target, 'Source probe is ', probe_id, 'Hop is ', hop, )
                                    # print ('Hop info is', this_hop)
                                    #print('Ixp is ', ixp)
                                    # This probe_id is added to the IXP list so that it can be grouped on the html page later
                                    if probe_id not in ixps_uk[ixp]['probes']:
                                        ixps_uk[ixp]['probes'].append(probe_id)
                                    # print(ixps_uk[ixp])
                                    
                                    break
                            break
                    
                    
                    # create an ixp on the map 
                    # Need to discover the ASn of the hop preceding the IXP so that we can compare which facilities
                    # it has in common with the IXP in order to map where the route enters the IXP.
                    
                    if this_ixp and not ixp_entered_flag:
                        # Get the ASN of the network Preceding the IXP hop
                        print('Probe ', probe_id)
                        print('THIS HOP ********************',hop,this_hop)
                        print('Previous HOP ********************',prev_hop)
                        prev_hop_asn = prev_hop['asn'][0]
                        print('PREV HOP ASN = ',prev_hop_asn)
                        '''
                        hop_asn = this_hop['asn'][0]
                        print('HOP ASN = ',hop_asn) 
                        hop_ip = this_hop['from']
                        print('this ip =', hop_ip)
                        print('this ixp = ', this_ixp) 
                        ''' 
                        ixp_facilities = ixps_uk[this_ixp]['fac_set'][0]
                        # networks has been defined at start of code, is entire list of networks
                        
                        
                        for network,values in networks.items():
                            # print(network,values['asn'])
                            # print('a'+prev_hop_asn+'a')
                            if values['asn'] == prev_hop_asn:
                                    print('The network entering the IXP  is', network)
                                    this_network = networks[network]
                                    break
                            # very strange anomaly doesnt work properly with 14061 so had to do this
                            elif values['asn'] == 14061:
                                    print('The network entering the IXP (asn 14061) is', network)
                                    this_network = networks[network]
                                    break

                        
                        
                        print('probe_id is',probe_id)
                        print('Network',this_network['id'],'facilities are',this_network['netfac_set'])
                        # Get the facilities where the network preceding the IXP peers
                        if this_network['netfac_set']:
                            entry_netfac_ids = []
                            for netfac in this_network['netfac_set']:
                                
                                print('Network',this_network['id'],'facilities are',this_network['netfac_set'])
                                print('this one is',netfac)
                                netfac_info = pdb.fetch(resource.NetworkFacility, netfac)
                                # print('NETFAC INFO is', netfac_info[0])
                                entry_netfac_ids.append(netfac_info[0]['fac_id'])  
                            print('The ASN preceding the IXP is', prev_hop_asn, ' and its facilites are', entry_netfac_ids)
                            ixp_entered_flag = True
                            ixp_entered_id = this_ixp
                        print('IXPs', this_ixp,'facilities are', ixp_facilities)

                        #Choose the entry Facility- which is shared between the entry network and the IXP
                        possible_entry_facility = [] 
                        for network_fac in entry_netfac_ids:
                            for ixp_fac in ixp_facilities:
                                if network_fac == ixp_fac:
                                    print ('this is the one', network_fac)
                                    possible_entry_facility.append(network_fac)
                                    break
                                
                        print(possible_entry_facility)
                        # CREATE THE IXP ENTRY RULES HERE
                        # if there are multiple shared facilities for the AS and the IX
                        # Entry Rule 1
                        # if list of possible entry facilities are all telehouse in london then just chose the initial one
                        if len(possible_entry_facility) > 1:
                            print('greater than 1')
                            telehouse_list = [34,39,45,835]
                            equinix_list = [832, 3152]
                            if all(x in telehouse_list for x in possible_entry_facility):
                                ixp_entry_point = possible_entry_facility[0]
                                print('all telehouse',ixp_entry_point) 
                            # if list of possible entry facilities are all equinix in slough then just chose the initial one   
                            elif all(x in equinix_list for x in possible_entry_facility):
                                    ixp_entry_point = possible_entry_facility[0]
                                    print('all equinix',ixp_entry_point) 
                            else:
                                print('ohoh no valid rule for this posissible entry list', possible_entry_facility) 
                                input('wait')
                        elif len(possible_entry_facility) == 1:
                            ixp_entry_point =  possible_entry_facility[0]
                        
                        else:
                            print ('entry list must be 0', possible_entry_facility)
                        facilities_used.append(str(ixp_entry_point))
                        facilities_used.append(hop)
                        print('facilities-used',facilities_used)
                        # input('wait')
                        

                    # Now we need the exit point
                    
                    print ('hop IP address',this_hop['from'])
                    
                    
                    if ixp_entered_flag:
                        if ipaddress.ip_address(this_hop['from']) not in ipaddress.ip_network(ixps_uk[ixp_entered_id]['ipv4_prefix']):
                            print ('ixp prefix',ixp_entered_id, ixps_uk[ixp_entered_id]['ipv4_prefix'])

                            print('HOP is ', hop)
                            # If we are not still in the IXP then we can now get the exiting ASN
                            print(this_hop)
                            if not this_hop['asn']:
                                hop_asn = prev_hop['asn'][0]
                            else:
                                hop_asn = this_hop['asn'][0]

                            print('HOP ASN = ',hop_asn)
                            '''
                            hop_asn = this_hop['asn'][0]
                            print('HOP ASN = ',hop_asn) 
                            hop_ip = this_hop['from']
                            print('this ip =', hop_ip)
                            print('this ixp = ', this_ixp) 
                            ''' 
                            ixp_facilities = ixps_uk[ixp_entered_id]['fac_set'][0]
                            # networks = pdb.fetch_all(resource.Network)
                            for network,values in networks.items():
                                if values['asn'] == hop_asn:
                                        print('The network exiting the IXP  is', network)
                                        this_network = networks[network]
                                        # input('wait')
                                        break
                                # very strange anomaly doesnt work properly with 14061 so had to do this
                                elif values['asn'] == 14061:
                                    print('The network entering the IXP (asn 14061) is', network)
                                    this_network = networks[network]
                                    break
                            
                            print('probe_id is',probe_id)
                            print('Network',this_network['id'],'facilities are',this_network['netfac_set'])
                            # input('wait')


                            # Get the facilities where the network succeding the IXP peers
                            if this_network['netfac_set']:
                                exit_netfac_ids = []
                                for netfac in this_network['netfac_set']:
                                    
                                    print('Network',this_network['id'],'facilities are',this_network['netfac_set'])
                                    print('this one is',netfac)
                                    netfac_info = pdb.fetch(resource.NetworkFacility, netfac)
                                    # print('NETFAC INFO is', netfac_info[0])
                                    exit_netfac_ids.append(netfac_info[0]['fac_id'])  
                                print('The ASN succeding the IXP is', hop_asn, ' and its facilites are', exit_netfac_ids)
                                
                            print('IXPs', ixp_entered_id,'facilities are', ixp_facilities)

                            ixp_exit_point = []
                            #Choose the exit IXP which is shared between the exit network and the IXP
                            possible_exit_facility = [] 
                            for network_fac in exit_netfac_ids:
                                for ixp_fac in ixp_facilities:
                                    if network_fac == ixp_fac:
                                        print ('this is the one', network_fac)
                                        possible_exit_facility.append(network_fac)
                                        break
                                    
                            print(possible_exit_facility)
                            # CREATE THE EXIT RULES HERE
                            # if there are multiple shared facilities for the AS and the IX
                            # Exit Rule 1
                            # if list of possible exit facilities are all telehouse in london then just chose the initial one

                            if len(possible_exit_facility) > 1:
                                print('greater than 1')
                                telehouse_list = [34,39,45,835]
                                equinix_list = [832, 3152]
                                if all(x in telehouse_list for x in possible_exit_facility):
                                    ixp_exit_point = possible_exit_facility[0]
                                    print('all telehouse',ixp_exit_point) 
                                
                                # if list of possible entry facilities are all equinix in slough then just chose the initial one   
                                elif all(x in equinix_list for x in possible_exit_facility):
                                    ixp_exit_point = possible_exit_facility[0]
                                    print('all equinix',ixp_exit_point) 
                                    # if there are multiple shared facilities for the AS and the IX
                                    # exit RULE 2
                                    # if the exit and entrance are same 
                                elif ixp_entry_point in possible_exit_facility:
                                        ixp_exit_point = ixp_entry_point
                                else:
                                    # if the list doesnt have all telehouse facilities then we need a rule here
                                    print('ohoh no valid rule for this posissible exit list', possible_exit_facility) 
                                    input('wait')
                            elif len(possible_exit_facility) == 1:
                                # If there is only one shared facility between the IX and the ASN then all is good
                                # RULE 3
                                ixp_exit_point =  possible_exit_facility[0]
                            
                            else:
                                # If there are no shared facilities the we have a problem
                                # RULE 4
                                print ('exit list must be 0, this needs a human', possible_exit_facility)
                                
                                input('wait')
                            facilities_used.append(str(ixp_exit_point))
                            facilities_used.append(hop)
                            print('facilities-used',facilities_used)
                            
                            ixp_entered_flag = False
                            this_ixp = []
                            



                                
                                
                            html.create_ixp(ixp_entered_id, ixps_uk[ixp_entered_id],facilities_used,facilitys_uk,probe_id)
                    # record the state of the last hop in case it is needed to detect the IXP entry point
                    if len(facilities_used)  == 2:
                        print('hop, entry facilities',hop, facilities_used[1])
                        if hop == facilities_used[1]:
                            fac_entry_hop = True 
                            this_hop['hop_latitude'] = facilitys_uk[facilities_used[0]]["latitude"]
                            this_hop['hop_longitude'] = facilitys_uk[facilities_used[0]]["longitude"]
                            #lat2 = this_hop['hop_latitude']
                            #lon2 = this_hop['hop_longitude']
                            #print('entry fac')
                           
                    if len(facilities_used)  == 4:
                        print('hop, entry facilities',hop, facilities_used[3])
                        
                        if hop == facilities_used[3]:
                            fac_entry_hop = False 
                            fac_exit_hop = True 
                            this_hop['hop_latitude'] = facilitys_uk[facilities_used[2]]["latitude"]
                            this_hop['hop_longitude'] = facilitys_uk[facilities_used[2]]["longitude"]
                            #lat2 = this_hop['hop_latitude']
                            #lon2 = this_hop['hop_longitude']
                            #print('exit fac')
                            
                    html.create_hop(probe_id,hop,this_hop,this_rtt,fac_entry_hop,fac_exit_hop)
                    html.create_lines_var(probe_id,hop,lat1,lon1,lat2,lon2,hop_distance,this_rtt,current_ip,this_hop['from'],fac_entry_hop,fac_exit_hop)                   
                    prev_hop = this_hop
                    fac_exit_hop = False
                    fac_entry_hop = False 
                  
                    
                    current_lat = lat2
                    current_lon = lon2
                    source_coords = (lon2,lat2)


                    last_rtt = this_rtt


                # Create the Reverse Path
                '''
                reverse_target_probe = probe_id
                reverse_source_probe = this_target
                for reverse_measurement_id in measurements:
                    if measurements[reverse_measurement_id]["target_probe"] == reverse_target_probe:
                        for reverse_hop in measurements[reverse_measurement]["results"][reverse_source_probe]['hops']
                            html.create_lines_var(reverse_probe_id,hop,lat2,lon2,lat1,lon1,hop_distance,this_rtt,current_ip,this_hop['from'])

                        # break out of loop as we found the reverse path, no need to keep checking
                        break
                measurement_id = 
                for hop in measurements[measurement_id]['results'][probe_id]['hops']:
                '''

        # create the layer checkers
        
        for probe_id  in measurements[measurement_id]['results']:
            ixp_flag = False
            for ixp in ixps_uk:
                if probe_id in ixps_uk[ixp]['probes']:
                    html.create_layer_checker(ixp,probe_id,ixps_uk)
                    ixp_flag = True
            #   IF IXP_FLAG  IS fALSE THEN THERE IS NO IXP SO NO NEED TO ADD TO A IXP GROUP but still need to create the route lines and hops
            if ixp_flag == False:
                ixp = 0
                html.create_layer_checker(ixp,probe_id,ixps_uk)

                


                
        

        
        html.close_file()     
        numberoffiles += 1
        print ('Copy ', html.filename ,' upto web server', numberoffiles)

                
    # Complete and close web based menu
    menu = open(menu_file,'a')            
    menu.write('</body>\n</html>')
    menu.close()