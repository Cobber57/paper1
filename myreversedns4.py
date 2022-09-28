#!/usr/bin/env python
# take results and discover the hops locations
from dns import resolver,reversename
import csv
import codecs
import re
import os
os.chdir('/home/paul/Documents/UK')
del os 

# https://pypi.org/project/prsw/
# Check RPKI validation status TODO: this not currently implemented
# print(ripe.rpki_validation_status(3333, '193.0.0.0/21').status)
# Find all announced prefixes for a Autonomous System
# prefixes = ripe.announced_prefixes(3333)
# however this returns multiple ASNs for a given prefix, prbably best using the RIPE database for this
# PRSW, the Python RIPE Stat Wrapper, is a python package that simplifies access to the RIPE Stat public data API.
import prsw
ripe = prsw.RIPEstat()

# Table Names
#peeringdb_network         
#peeringdb_facility          peeringdb_network_contact 
#peeringdb_ix                peeringdb_network_facility
#peeringdb_ix_facility       peeringdb_network_ixlan   
#peeringdb_ixlan             peeringdb_organization    
#peeringdb_ixlan_prefix    
        if this_ixp and ixp_entered_flag:
            print('Now we are in the IX and this hop must be exiting the IX')
            print ('hop IP address',this_hop['ip_from'])
            print('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
            print('IXP ENTEREDRED FLAG', ixp_entered_flag)
                
            print ('ixp prefix',ixp_entered_id, ixps_uk[ixp_entered_id]['ipv4_prefix'])

            print('HOP is ', hop)
            input('wait')
                
            if ipaddress.ip_address(this_hop['ip_from']) not in ipaddress.ip_network(ixps_uk[ixp_entered_id]['ipv4_prefix']):
                print ('NOW OUT OF THE IXP, ixp prefix',ixp_entered_id, ixps_uk[ixp_entered_id]['ipv4_prefix'])

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
                hop_ip = this_hop['ip_from']
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
                # print('Network',this_network['id'],'facilities are',this_network['netfac_set'])
                # input('wait')


                # Get the facilities where the network succeding the IXP peers
                if this_network['netfac_set']:
                    exit_netfac_ids = []
                    for netfac in this_network['netfac_set']:
                        
                        # print('Network',this_network['id'],'facilities are',this_network['netfac_set'])
                        # print('this one is',netfac)
                        netfac_info = pdb.fetch(resource.NetworkFacility, netfac)
                        # print('NETFAC INFO is', netfac_info[0])
                        exit_netfac_ids.append(netfac_info[0]['fac_id'])  
                        # add JANET additional manually found facilities TODO why arnt these found ?
                        # print(exit_netfac_ids)
                        # input('wait')
                    
                        if hop_asn == 786:
                            exit_netfac_ids.append(896) 
                            exit_netfac_ids.append(76)
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
                    
                    # if list of possible exit facilities are all equinix in slough then just chose the initial one   
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
                        results[probe_id]['status'] = False
                        results[probe_id]['status_reason'].append('initial Facility used as no valid rule for the Facility EXIT list ' + str(possible_exit_facility))
                        results[probe_id]['status_code'].append(5)
                        ixp_exit_point = possible_exit_facility[0]
                        #input('wait')
                elif len(possible_exit_facility) == 1:
                    # If there is only one shared facility between the IX and the ASN then all is good
                    # RULE 3
                    ixp_exit_point =  possible_exit_facility[0]
                
                else:
                    # If there are no shared facilities then we have a problem
                    # RULE 4
                    print ('exit list must be 0, this needs a human', possible_exit_facility)
                    results[probe_id]['status'] = False
                    results[probe_id]['status_reason'].append(probe_id+' does not have an EXIT POINT')
                    results[probe_id]['status_code'].append(4)
                    #input('wait')
                facilities_used[probe_id].append(str(ixp_exit_point))
                facilities_used[probe_id].append(hop)
                print('facilities-used',facilities_used[probe_id])
                print('FLAG********************************************************************',ixp_entered_flag)
                # html.create_ixp(ixp_entered_id, ixps_uk[ixp_entered_id],facilities_used[probe_id],facilitys_uk,probe_id)
                #ixp_entered_flag = False
                #this_ixp = []
                



                                
                             
                            
                                   
            current_ip = prev_hop['ip_from']
            # if only 2 entries then we have worked out facility entering the ixp but not the one exiting
            if len(facilities_used[probe_id])  == 2:
                print('hop, entry facilities',hop, facilities_used[probe_id][0],facilities_used[probe_id][1])
                
                if hop == facilities_used[probe_id][1]:
                    # if we have worked out the entry facility
                    if facilities_used[probe_id][0] != '0':
                        print('FAC USED',facilities_used)
                        fac_entry_hop = True 
                        this_hop['hop_latitude'] = facilitys_uk[facilities_used[probe_id][0]]["latitude"]
                        this_hop['hop_longitude'] = facilitys_uk[facilities_used[probe_id][0]]["longitude"]
                        lat2 = this_hop['hop_latitude']
                        lon2 = this_hop['hop_longitude']
                        source_coords = (lon1,lat1)
                        hop_coords = (lon2,lat2)
                        hop_distance = gcc.distance_between_points(source_coords, hop_coords, unit='kilometers',haversine=True)
                        print('entry fac')

                        ixp_in_hops[hop] = {}
                        ixp_in_hops[hop]['info'] = this_hop
                        ixp_in_hops[hop]['lat1'] = lat1
                        ixp_in_hops[hop]['lon1'] = lon1
                        ixp_in_hops[hop]['lat2'] = lat2
                        ixp_in_hops[hop]['lon2'] = lon2
                        ixp_in_hops[hop]['rtt'] = this_rtt
                        ixp_in_hops[hop]['ip'] = current_ip
                        ixp_in_hops[hop]['distance'] = hop_distance
                    else:
                        # If we couldnt work out the entry facility
                        fac_entry_hop = False
                        this_hop['hop_latitude'] = prev_hop['hop_latitude']
                        this_hop['hop_longitude'] = prev_hop['hop_longitude']
                        lat2 = this_hop['hop_latitude']
                        lon2 = this_hop['hop_longitude']
                        print('NO entry fac')

                        ixp_in_hops[hop] = {}
                        ixp_in_hops[hop]['info'] = this_hop
                        ixp_in_hops[hop]['lat1'] = lat1
                        ixp_in_hops[hop]['lon1'] = lon1
                        ixp_in_hops[hop]['lat2'] = lat1
                        ixp_in_hops[hop]['lon2'] = lon1
                        ixp_in_hops[hop]['rtt'] = this_rtt
                        ixp_in_hops[hop]['ip'] = current_ip
                        ixp_in_hops[hop]['distance'] = hop_distance
                    
            if len(facilities_used[probe_id])  == 4:
                # if we have 4 entries then we must have worked out entry
                print('hop, entry facilities',hop, facilities_used[probe_id][3])
                
                if hop == facilities_used[probe_id][3]:
                    fac_entry_hop = False 
                    fac_exit_hop = True 
                    this_hop['hop_latitude'] = facilitys_uk[facilities_used[probe_id][2]]["latitude"]
                    this_hop['hop_longitude'] = facilitys_uk[facilities_used[probe_id][2]]["longitude"]
                    lat2 = this_hop['hop_latitude']
                    lon2 = this_hop['hop_longitude']
                    print('exit fac')
                    ixp_post_hops[hop] = {}
            
                    ixp_post_hops[hop]['info'] = this_hop
                    ixp_post_hops[hop]['lat1'] = lat1
                    ixp_post_hops[hop]['lon1'] = lon1
                    ixp_post_hops[hop]['lat2'] = lat2
                    ixp_post_hops[hop]['lon2'] = lon2
                    ixp_post_hops[hop]['rtt'] = this_rtt
                    ixp_post_hops[hop]['ip'] = current_ip
                    ixp_post_hops[hop]['distance'] = hop_distance
                
                    
                
            if len(facilities_used[probe_id]) == 0:
                print('HAs it got an IXP ',probe_id,this_ixp)
                
                ixp_pre_hops[hop] = {}
            
                ixp_pre_hops[hop]['info'] = this_hop
                ixp_pre_hops[hop]['lat1'] = lat1
                ixp_pre_hops[hop]['lon1'] = lon1
                ixp_pre_hops[hop]['lat2'] = lat2
                ixp_pre_hops[hop]['lon2'] = lon2
                ixp_pre_hops[hop]['rtt'] = this_rtt
                ixp_pre_hops[hop]['ip'] = current_ip
                ixp_pre_hops[hop]['distance'] = hop_distance
                

            
            print('*********************')
            print('PRE',ixp_pre_hops)
            print('*********************')
            print('IN', ixp_in_hops)
            print('*********************')
            print('POST',ixp_post_hops)
            


            
            # html.create_hop(probe_id,hop,this_hop,this_rtt,fac_entry_hop,fac_exit_hop)
            
            # html.create_lines_var(probe_id,hop,lat1,lon1,lat2,lon2,hop_distance,this_rtt,current_ip,this_hop['from'],fac_entry_hop,fac_exit_hop)                   
            # record the state of the last hop in case it is needed to detect the IXP entry point
            prev_hop = this_hop
            fac_exit_hop = False
            fac_entry_hop = False 
            
            
            current_lat = lat2
            current_lon = lon2
            source_coords = (lon2,lat2)


            last_rtt = this_rtt
    

# import request so can access the RIPE database REST API 
import requests
ripe_url = 'https://rest.db.ripe.net/search.json'

import json
import ipaddress
import great_circle_calculator.great_circle_calculator as gcc
from ripe.atlas.cousteau import ProbeRequest, Traceroute, AtlasSource, AtlasRequest, AtlasCreateRequest
from dns import resolver,reversename


from peeringdb import PeeringDB, resource, config


        

def convert(lst):
    my_dict = {}
    for l in lst:
        id = l['id']
        my_dict[id] = {}
        for key,value in l.items():
            my_dict[id][key] = value
    
    return my_dict

def get_hop_location(prev_hop,hop,hop_details,ixp_entered_flag):
    print('The ixp entered flag is set to' , ixp_entered_flag)
    print ('Previous Hop was ', prev_hop)
    lat1 = prev_hop['hop_latitude']
    lon1 = prev_hop['hop_longitude']
    this_rtt = hop_details['rtt']
    print ('This hop is',hop) 
    print('Probe id is', probe_id)
    #print('probe ids source coordinates are',source_coords)
    #old_prefix = ripe.announced_prefixes(prev_hop['asn'])
    #new_prefix = ripe.announced_prefixes(hop['asn'])
    # Create location of where to place this hop

    this_hop = {}
    this_hop['id'] = hop  
    this_hop['ip_from'] = hop_details['ip_from']
    this_hop['rdns'] = ''
    this_hop['rtt'] =  hop_details['rtt']
    this_hop['address'] = 'no address'
    this_hop['asn'] = 0
    this_hop['hop_latitude'] = 0
    this_hop['hop_longitude'] = 0
    this_hop['use_next_hop_loc'] = False

    print('This  hops ip address is',this_hop['ip_from'])

    # Check to see if this hops ip address is in a IX prefix list and set flag if true
    # TODO This could actually do with going at end of rules as it slows down the processing
    # but then how would i get a flag set for rules 5 and 6 ?
    ix_prefix_flag = False
    
    for prefix in ix_prefix_list:
        
        # print (type(ipaddress.ip_address(this_hop['ip_from'])),type(ipaddress.ip_network(prefix)))
        # print(ipaddress.ip_address(this_hop['ip_from']),ipaddress.ip_network(prefix))
        if ipaddress.ip_address(this_hop['ip_from']) in ipaddress.ip_network(prefix): 
            # print('Checking', this_hop['ip_from'])
            ix_prefix_flag = True
            # print('IX prefix flag is true', this_hop['ip_from'], prefix,hop )
            # input('wait')
            for ixp in ixps_uk:
                if ixps_uk[ixp]['ipv4_prefix'] == prefix:
                    # this ip address belongs to an IXP
                    this_ixp = ixp  
                    # print('Target is ', this_target, 'Source probe is ', probe_id, 'Hop is ', hop, )
                    # print ('Hop info is', this_hop)
                    #print('Ixp is ', ixp)
                    # This probe_id is added to the IXP list so that it can be grouped on the html page later
                    # print('ixps_uk', ixps_uk[ixp])
                    if probe_id not in ixps_uk[ixp]['probes']:
                        ixps_uk[ixp]['probes'].append(probe_id)
                    
                    break
            break

    
    # Get this hops ASN

    
    
    options = {
            'query-string' : this_hop['ip_from'],
            'type-filter' : 'route',
            'flags' : ['no-irt','no-referenced'],
            'source' : 'RIPE'
            }
    r = requests.get(ripe_url, params=options)
    print ('Status code 200 means its ok', r.status_code)
    
    # status code 200 is ok then get the ASN of this IP address
    if r.status_code == 200:
        x = r.json()
        print(x)

        attributes = x['objects']['object'][0]['attributes']['attribute']
        for attrib in attributes:
            if attrib['name'] == 'origin':
                ripedb_asn = attrib['value']
                # had to make this overly complex change because i  swapped from using RIPE stat to RIPE database
                print ('RIPEDB_ASN',ripedb_asn)
                this_hop['asn'] = [int(re.split('AS|as', ripedb_asn)[1])]
    else:
        # if Ripe DB cant find the ASN try RIPE stat
        print('trying RIPE STAT')
        if this_hop['ip_from'] != '10.255.255.2': # ripestat doesnt like local subnets 
            # TODO: SHOULDnt THIS BE all the local subnets ?
            # if this_hop['ip_from'] != '195.66.224.253': # This prefix has been hijacked by AS25577
                
            print('trying RIPE STAT')
            response = ripe.network_info(this_hop['ip_from'])
            print('ASNS are', response.asns, response.prefix)
            for asn in response.asns:
                print(asn)
            this_hop['asn'] = [asn]
            
            #else:
                # This prefix has been hijacked by AS25577 so having to manually set it
                # TODO: reported this to RIPE, looks like they have fixed it now so this may no longer be neccessary
                #this_hop['asn'] = [43996]
        print(this_hop)
    input('wait')            
                
    


    # find location Logic

    # First of all start with the obvious, We dont need to run REGEX on every hop because some hops will not have ReverseDNS
    # Addresses.

    

    # rule1 if hop is 1 and subnet is same as probe ip the location is still where the probe is located. 
    # This is probably the local gateway that the probe is connected to.
    

    if this_hop['id'] == '1': 

        # TODO: We actually need to get the prefix downloaded from the probe so we can test against their correct subnets
        #  This will mean editing the
        # createmeasurments file or perhaps just creating a program to interrogate each probe in the uk-measurements file and 
        # recreate the uk-measurements file with the prefix field added. 
        # But for the time being we will test as if every probe is on a 255.255.255.0 prefix.
        this_subnet = this_hop['ip_from'].split('.')[0]+'.'+this_hop['ip_from'].split('.')[1]+'.'+this_hop['ip_from'].split('.')[2]
        prev_subnet = prev_hop['ip_from'].split('.')[0]+'.'+prev_hop['ip_from'].split('.')[1]+'.'+prev_hop['ip_from'].split('.')[2]
        if this_subnet == prev_subnet:
            this_hop['hop_latitude'] =  prev_hop['hop_latitude']
            this_hop['hop_longitude'] = prev_hop['hop_longitude']
            this_hop['rdns'] = 'local'
            print('SUBENET = ' , this_subnet, prev_subnet)
        else:
            print ('hmm hop is 1 but subnets dont match - see the find location logic rules 1')
            input('Wait')

    # rule2 if using a local subnet and previous wasnt then it is likely that this IP_address is now at the remote site (ie the next hop address) 
    # so we need to fill in the coordinets of this IP address by using the next hops coordinates.
    # but this network will still belong to the last ASN

    elif this_hop['ip_from'].split('.')[0]+'.' in local_subnets or this_hop['ip_from'].split('.')[0]+'.'+this_hop['ip_from'].split('.')[1]+'.' in local_subnets:
        if prev_hop['ip_from'].split('.')[0]+'.' not in local_subnets or prev_hop['ip_from'].split('.')[0]+'.'+prev_hop['ip_from'].split('.')[1]+'.' not in local_subnets:
            print('remote end of VPN')
            this_hop['use_next_hop_loc'] = True # Setting a flag so that next hop knows to set prev hop to same location
            this_hop['hop_latitude'] =  0
            this_hop['hop_longitude'] = 0
            this_hop['rdns'] = 'local'
            this_hop['asn'] = prev_hop['asn']
        else:
            print ('hmm prev_hop prefix is in local subnets and sio is this (is this a multi hop local network ?) - see the find location logic rules 2')
            input('Wait')
    # rule3 if this hops IP address is not in the local subnets and the last one was then we need to fill in the last ones coordiantes as well as this one
    # as it likely that the two are in the same location.
    elif prev_hop['use_next_hop_loc'] == True:
        

        addr=reversename.from_address(this_hop['ip_from'])
        rname = str(resolver.resolve(addr,"PTR")[0])
        this_hop['rdns'] = rname
        print('RULE 3 This hops Reversedns name is',rname)
        lon, lat = get_coords(rname)
        this_hop['hop_longitude'] = lon
        this_hop['hop_latitude'] = lat
        results[probe_id][str(int(hop)-1)]['hop_latitude'] =  lat # fill in longitude of last hop
        results[probe_id][str(int(hop)-1)]['hop_longitude'] =  lon # fill in longitude of last hop
    # rule 4 if this hop is the target ip address
    elif this_hop['ip_from'] == measurement[this_target] ["probe_ip"]:
        this_hop['hop_longitude'] = measurement[this_target] ["probe_x"] 
        this_hop['hop_latitude'] = measurement[this_target] ["probe_y"]
        this_hop['rdns'] = this_target   

    # rule5 if ip address is part of an IXP then the facility needs to be worked out and then the coordinates of that facility
    elif ix_prefix_flag:
        
        # check for Internet Exchange
        #this_ixp = 0
        #ixp_entered_flag = False
        #ixp_entered_id = 0
        # if source probe does use an ixp create an ixp on the map 
        # Need to discover the ASn of the hop preceding the IXP so that we can compare which facilities
        # it has in common with the IXP in order to map where the route enters the IXP.
                

        if this_ixp and not ixp_entered_flag:
            # Get the ASN of the network Preceeding the IXP hop
            print('Probe ', probe_id)
            print('THIS HOP ********************',hop,this_hop)
            print('Previous HOP ********************',prev_hop)
            print('IXP',this_ixp)
            prev_hop_asn = prev_hop['asn'][0]
            print('PREV HOP ASN = ',prev_hop_asn)
            
            hop_asn = this_hop['asn'][0]
            print('HOP ASN = ',hop_asn) 
            hop_ip = this_hop['ip_from']
            print('this ip =', hop_ip)
            print('this ixp = ', this_ixp) 
            print(ixps_uk[this_ixp])
            
            ixp_facilities = ixps_uk[this_ixp]['fac_set'][0]

            print('IXP facilities is', ixp_facilities)
            # networks has been defined at start of code, is entire list of networks
            input('wait')        
            #print(networks[14061])
            for network,values in networks.items():
                # print(network,values['asn'])
                # print('a'+prev_hop_asn+'a')
                if values['asn'] == prev_hop_asn:
                        print('The network entering the IXP  is', network)
                        this_network = networks[network]
                        break
                # very strange anomaly doesnt work properly with 14061 so had to do this
                elif prev_hop_asn == 14061:
                        print('The network entering the IXP (asn 14061) is', network)
                        this_network = networks[network]
                        break

                    
                    
                    
            print('probe_id is',probe_id)
            # print('Network',this_network['id'],'facilities are',this_network['netfac_set'])
            # Get the facilities where the network preceding the IXP peers
            if this_network['netfac_set']:
                entry_netfac_ids = []
                for netfac in this_network['netfac_set']:
                    
                    #print('Network',this_network['id'],'facilities are',this_network['netfac_set'])
                    # print('this one is',netfac)
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
                    results[probe_id]['status'] = False
                    results[probe_id]['status_reason'].append(probe_id+' All Entry points are Telehouse in london Docklands')
                    results[probe_id]['status_code'].append(7)
                # if list of possible entry facilities are all equinix in slough then just chose the initial one   
                elif all(x in equinix_list for x in possible_entry_facility):
                        ixp_entry_point = possible_entry_facility[0]
                        print('all equinix',ixp_entry_point)
                        results[probe_id]['status'] = False 
                        results[probe_id]['status_reason'].append(probe_id+' All Entry points are Equinix in Slough')
                        results[probe_id]['status_code'].append(8)
                else:
                    print('ohoh no valid rule for this posissible entry list', possible_entry_facility) 
                    input('wait')
                    results[probe_id]['status'] = False
                    results[probe_id]['status_reason'].append('initial Facility used as no valid rule for the Facility entry list ' + str(possible_entry_facility))
                    results[probe_id]['status_code'].append(2)
                    ixp_entry_point = possible_entry_facility[0]
            elif len(possible_entry_facility) == 1:
                ixp_entry_point =  possible_entry_facility[0]
            
            else:
                # shared entry facilities must be zero 
                # this can happen where a ISp uses remote peering see https://www.linx.net/about/our-partners/connexions-reseller-partners/
                print ('entry list must be 0', possible_entry_facility)
                results[probe_id]['status'] = False
                results[probe_id]['status_reason'].append(probe_id+' NO IXP Entry Point')
                results[probe_id]['status_code'].append(6)
                ixp_entry_point = '0' # TODO set it to the exit facility for now, but this is wrong
            facilities_used[probe_id].append(str(ixp_entry_point))
            facilities_used[probe_id].append(hop)
            print('facilities-used',facilities_used[probe_id])

        # Now we need the exit point if we are now inside the IXP
        if this_ixp and ixp_entered_flag:
            print('Now we are in the IX and this hop must be outside the IX')
            print ('hop IP address',this_hop['ip_from'])
            print('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
            print('IXP ENTEREDRED FLAG', ixp_entered_flag)
                
            print ('ixp prefix',ixp_entered_id, ixps_uk[ixp_entered_id]['ipv4_prefix'])

            print('HOP is ', hop)
            input('wait')
                
            if ipaddress.ip_address(this_hop['ip_from']) not in ipaddress.ip_network(ixps_uk[ixp_entered_id]['ipv4_prefix']):
                print ('NOW OUT OF THE IXP, ixp prefix',ixp_entered_id, ixps_uk[ixp_entered_id]['ipv4_prefix'])

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
                hop_ip = this_hop['ip_from']
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
                # print('Network',this_network['id'],'facilities are',this_network['netfac_set'])
                # input('wait')


                # Get the facilities where the network succeding the IXP peers
                if this_network['netfac_set']:
                    exit_netfac_ids = []
                    for netfac in this_network['netfac_set']:
                        
                        # print('Network',this_network['id'],'facilities are',this_network['netfac_set'])
                        # print('this one is',netfac)
                        netfac_info = pdb.fetch(resource.NetworkFacility, netfac)
                        # print('NETFAC INFO is', netfac_info[0])
                        exit_netfac_ids.append(netfac_info[0]['fac_id'])  
                        # add JANET additional manually found facilities TODO why arnt these found ?
                        # print(exit_netfac_ids)
                        # input('wait')
                    
                        if hop_asn == 786:
                            exit_netfac_ids.append(896) 
                            exit_netfac_ids.append(76)
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
                    
                    # if list of possible exit facilities are all equinix in slough then just chose the initial one   
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
                        results[probe_id]['status'] = False
                        results[probe_id]['status_reason'].append('initial Facility used as no valid rule for the Facility EXIT list ' + str(possible_exit_facility))
                        results[probe_id]['status_code'].append(5)
                        ixp_exit_point = possible_exit_facility[0]
                        #input('wait')
                elif len(possible_exit_facility) == 1:
                    # If there is only one shared facility between the IX and the ASN then all is good
                    # RULE 3
                    ixp_exit_point =  possible_exit_facility[0]
                
                else:
                    # If there are no shared facilities then we have a problem
                    # RULE 4
                    print ('exit list must be 0, this needs a human', possible_exit_facility)
                    results[probe_id]['status'] = False
                    results[probe_id]['status_reason'].append(probe_id+' does not have an EXIT POINT')
                    results[probe_id]['status_code'].append(4)
                    #input('wait')
                facilities_used[probe_id].append(str(ixp_exit_point))
                facilities_used[probe_id].append(hop)
                print('facilities-used',facilities_used[probe_id])
                print('FLAG********************************************************************',ixp_entered_flag)
                # html.create_ixp(ixp_entered_id, ixps_uk[ixp_entered_id],facilities_used[probe_id],facilitys_uk,probe_id)
                #ixp_entered_flag = False
                #this_ixp = []
                



                                
                             
                            
                                   
            current_ip = prev_hop['ip_from']
            
            if len(facilities_used[probe_id])  == 2:
                print('hop, entry facilities',hop, facilities_used[probe_id][0],facilities_used[probe_id][1])
                
                if hop == facilities_used[probe_id][1]:
                    if facilities_used[probe_id][0] != '0':
                        print('FAC USED',facilities_used)
                        fac_entry_hop = True 
                        this_hop['hop_latitude'] = facilitys_uk[facilities_used[probe_id][0]]["latitude"]
                        this_hop['hop_longitude'] = facilitys_uk[facilities_used[probe_id][0]]["longitude"]
                        lat2 = this_hop['hop_latitude']
                        lon2 = this_hop['hop_longitude']
                        source_coords = (lon1,lat1)
                        hop_coords = (lon2,lat2)
                        hop_distance = gcc.distance_between_points(source_coords, hop_coords, unit='kilometers',haversine=True)
                        print('entry fac')

                        ixp_in_hops[hop] = {}
                        ixp_in_hops[hop]['info'] = this_hop
                        ixp_in_hops[hop]['lat1'] = lat1
                        ixp_in_hops[hop]['lon1'] = lon1
                        ixp_in_hops[hop]['lat2'] = lat2
                        ixp_in_hops[hop]['lon2'] = lon2
                        ixp_in_hops[hop]['rtt'] = this_rtt
                        ixp_in_hops[hop]['ip'] = current_ip
                        ixp_in_hops[hop]['distance'] = hop_distance
                    else:
                        fac_entry_hop = False
                        this_hop['hop_latitude'] = prev_hop['hop_latitude']
                        this_hop['hop_longitude'] = prev_hop['hop_longitude']
                        lat2 = this_hop['hop_latitude']
                        lon2 = this_hop['hop_longitude']
                        print('NO entry fac')

                        ixp_in_hops[hop] = {}
                        ixp_in_hops[hop]['info'] = this_hop
                        ixp_in_hops[hop]['lat1'] = lat1
                        ixp_in_hops[hop]['lon1'] = lon1
                        ixp_in_hops[hop]['lat2'] = lat1
                        ixp_in_hops[hop]['lon2'] = lon1
                        ixp_in_hops[hop]['rtt'] = this_rtt
                        ixp_in_hops[hop]['ip'] = current_ip
                        ixp_in_hops[hop]['distance'] = hop_distance
                    
            if len(facilities_used[probe_id])  == 4:
                print('hop, entry facilities',hop, facilities_used[probe_id][3])
                
                if hop == facilities_used[probe_id][3]:
                    fac_entry_hop = False 
                    fac_exit_hop = True 
                    this_hop['hop_latitude'] = facilitys_uk[facilities_used[probe_id][2]]["latitude"]
                    this_hop['hop_longitude'] = facilitys_uk[facilities_used[probe_id][2]]["longitude"]
                    lat2 = this_hop['hop_latitude']
                    lon2 = this_hop['hop_longitude']
                    print('exit fac')
                    ixp_post_hops[hop] = {}
            
                    ixp_post_hops[hop]['info'] = this_hop
                    ixp_post_hops[hop]['lat1'] = lat1
                    ixp_post_hops[hop]['lon1'] = lon1
                    ixp_post_hops[hop]['lat2'] = lat2
                    ixp_post_hops[hop]['lon2'] = lon2
                    ixp_post_hops[hop]['rtt'] = this_rtt
                    ixp_post_hops[hop]['ip'] = current_ip
                    ixp_post_hops[hop]['distance'] = hop_distance
                
                    
                
            if len(facilities_used[probe_id]) == 0:
                print('HAs it got an IXP ',probe_id,this_ixp)
                
                ixp_pre_hops[hop] = {}
            
                ixp_pre_hops[hop]['info'] = this_hop
                ixp_pre_hops[hop]['lat1'] = lat1
                ixp_pre_hops[hop]['lon1'] = lon1
                ixp_pre_hops[hop]['lat2'] = lat2
                ixp_pre_hops[hop]['lon2'] = lon2
                ixp_pre_hops[hop]['rtt'] = this_rtt
                ixp_pre_hops[hop]['ip'] = current_ip
                ixp_pre_hops[hop]['distance'] = hop_distance
                

            
            print('*********************')
            print('PRE',ixp_pre_hops)
            print('*********************')
            print('IN', ixp_in_hops)
            print('*********************')
            print('POST',ixp_post_hops)
            


            
            # html.create_hop(probe_id,hop,this_hop,this_rtt,fac_entry_hop,fac_exit_hop)
            
            # html.create_lines_var(probe_id,hop,lat1,lon1,lat2,lon2,hop_distance,this_rtt,current_ip,this_hop['from'],fac_entry_hop,fac_exit_hop)                   
            # record the state of the last hop in case it is needed to detect the IXP entry point
            prev_hop = this_hop
            fac_exit_hop = False
            fac_entry_hop = False 
            
            
            current_lat = lat2
            current_lon = lon2
            source_coords = (lon2,lat2)


            last_rtt = this_rtt
    
        
        # try to get the reverse DNS name, if none then just use the IX Number    
            try:
                    
                addr=reversename.from_address(this_hop['ip_from'])
                rname = str(resolver.resolve(addr,"PTR")[0])
            except:
                rname = 'IX'+this_ixp
                this_hop['rdns'] = rname
            else:
                
                this_hop['rdns'] = rname
            print('RULE 5(IXP) This hops Reversedns name is',rname)
            input('WAIT')
        print(results)

        input('wait')
        # this_hop['hop_longitude'] = 500
        # this_hop['hop_latitude'] = 500
        
        
        
        
        # Rule 6 if all other rules are false then this is a valid ip to use REGEX to extract the town from the reverse DNS address
        # and find the location of that Ip address.
        if ix_prefix_flag == False and this_hop['ip_from'] != measurement[this_target] ["probe_ip"] :
            addr=reversename.from_address(this_hop['ip_from'])
            rname = str(resolver.resolve(addr,"PTR")[0])
            this_hop['rdns'] = rname
            print('Rule 6 This hops Reversedns name is',rname)
            lon, lat = get_coords(rname)
            this_hop['hop_longitude'] = lon
            this_hop['hop_latitude'] =  lat

    
    # rule 6 if this ip address hasnt been picked up by any of the above rules then it probably just needs locating via its rdns
    
    elif this_hop['ip_from'] not in local_subnets and not ix_prefix_flag:
        print('ix_prefix_flag',hop,this_hop['ip_from'],ix_prefix_flag)
        addr=reversename.from_address(this_hop['ip_from'])
        rname = str(resolver.resolve(addr,"PTR")[0])
        this_hop['rdns'] = rname
        print('RULE 3 This hops Reversedns name is',rname)
        lon, lat = get_coords(rname)
        this_hop['hop_longitude'] = lon
        this_hop['hop_latitude'] = lat
    
    
  
    # Rule 7 there is no rule 7
    else:
        print('oh heck a new rule is required')
        input('wait')
                
    print('This Hop', this_hop)
    print('prev_hop', prev_hop)
    
    return this_hop

def get_coords(rname):
    coords = []
    ''' 
    if rname == 'be-1-ibr01-drt-red.uk.cdw.com.':
        coords = (51.2477342160338, -0.15708547962421623)
    if rname == 'fo-4-0-5-core01-drt-red.uk.cdw.com.':
        coords = (51.2477342160338, -0.15708547962421623)
    if rname == 'te-2-0-1-core01-drt-lon.uk.cdw.com.':
        coords = (51.4998, -0.0107 )
    if rname == 'fo-0-0-0-20-ibr01-drt-lon.uk.cdw.com.':
        coords = (51.4998, -0.0107)
    if rname == 'fo-4-0-5-core01-drt-lon.uk.cdw.com.':
        coords = (51.4998, -0.0107)
    if rname == 'te-2-0-1-core01-drt-red.uk.cdw.com.':
        coords = (51.2476, -0.1571)
    if rname == 'fo-0-0-0-20-ibr01-drt-red.uk.cdw.com.':
        coords = (51.2476, -0.1571)
    if rname == 'external-dcfw-cluster.uk.cdw.com.':
        coords = (51.2476, -0.1571 )
    '''
    
    # Read in the UK Facilities records

    
    # rname = 'be-1-ibr01-drt-red.uk.cdw.com.'
    rdns_parts_list =rname.split('.')
    coords = (0,0)
    print(facilitys_uk)
    possible_facilitys = {}
    for this_rdns_partial_name in rdns_parts_list:
        rdns_partial_list = re.findall("[a-zA-Z]{3,}", this_rdns_partial_name)
        print(rdns_parts_list,this_rdns_partial_name,rdns_partial_list)

        for this_part in rdns_partial_list:
            print('this part is', this_part)
            possible_facilitys[this_part] = {}
            for town in townset:
                print(town,this_part)
                town_lower = town.casefold()
                this_part_lower = this_part.casefold()
                if town_lower.startswith(this_part_lower):
                    
                    print(town, this_part,coords)
                    
                    for fac in facilitys_uk:
                        
                        if facilitys_uk[fac]['city'] == town:
                            
                            print(fac)
                            print(facilitys_uk[fac]['latitude'])
                            print(facilitys_uk[fac]['longitude'])
                            possible_facilitys[this_part][fac] ={}
                            possible_facilitys[this_part][fac]['lat'] = facilitys_uk[fac]['latitude']
                            possible_facilitys[this_part][fac]['lon'] = facilitys_uk[fac]['longitude']
                            possible_facilitys[this_part][fac]['town'] = town
                            possible_facilitys[this_part][fac]['org_id'] = facilitys_uk[fac]['org_id']
                            possible_facilitys[this_part][fac]['networks'] = []
                            possible_facilitys[this_part][fac]['networks'] = facilitys_uk[fac]['networks']
                    # now we have to work out which is the correct facility and what the coords of theme are
                    # we do this by comparing which of the possible facilitys in the relevant town peer with the last ASNs network
                    print(possible_facilitys) 
                    for part in possible_facilitys:
                        # if this part is not empty
                        if possible_facilitys[part]: 
                            # find the network
                            for facil in possible_facilitys[part]:
                                i = 1
                                for asn in possible_facilitys[part][facil]['networks']:
                                    # facilitys_uk[fac]['networks'] consists of a network,asn tuple, we are only intereted in the asn
                                    i += 1
                                    if i ==2:
                                        i = 0
                                        continue
                                    print('ASN is',asn, this_hop['asn'][0])
                                    print(type(asn),type(this_hop['asn'][0]))
                                    if asn == this_hop['asn'][0]:
                                        #print('WOOT', possible_facilitys[part])
                                        #input('DONE')
                                        coords = (possible_facilitys[part][facil]['lon'],possible_facilitys[part][facil]['lat'])

                    # input('WOOT, wait')
    return coords   

if __name__ == "__main__":
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
    with open('peeringdb_test_results/uk_facilities_to_networks_good.json') as f:
        facilitys_uk = json.load(f)

    pdb = PeeringDB()
    # pdb.update_all() # update my local database
    # local subnets
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

    # Read in the UK Internet Exchange info
    with open('peeringdb_test_results/uk_ixps.json') as f:
        ixps_uk = json.load(f)


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
    facilitys_uk['8628']["networks"] = [3744, 56595, 2354, 12703, 10507, 202793]

    facilitys_uk['1793']["latitude"] = 51.24771 
    facilitys_uk['1793']["longitude"] = -0.15714
    

    facilitys_uk['34']["latitude"] = 51.51171
    facilitys_uk['34']["longitude"] = -0.00294

    facilitys_uk['39']["latitude"] = 51.51171
    facilitys_uk['39']["longitude"] = -0.00294

    facilitys_uk['51']["latitude"] = 51.499
    facilitys_uk['51']["longitude"] = -0.01446

    facilitys_uk['244']["latitude"] = 53.47941
    facilitys_uk['244']["longitude"] = -2.23815

    facilitys_uk['428']["latitude"] = 51.52334
    facilitys_uk['428']["longitude"] = -0.08549

    facilitys_uk['438']["latitude"] = 53.46371
    facilitys_uk['438']["longitude"] = -2.23677

    facilitys_uk['632']["latitude"] = 51.44526
    facilitys_uk['632']["longitude"] = -0.97596

    facilitys_uk['677']["latitude"] = 52.64077
    facilitys_uk['677']["longitude"] = -1.14055

    facilitys_uk['734']["latitude"] = 52.05523
    facilitys_uk['734']["longitude"] = -0.75594   

    facilitys_uk['835']["latitude"] = 51.51171
    facilitys_uk['835']["longitude"] = -0.00294

    facilitys_uk['840']["latitude"] = 51.46199
    facilitys_uk['840']["longitude"] = -1.00587

    facilitys_uk['1027']["latitude"] = 51.65227
    facilitys_uk['1027']["longitude"] = -0.05508

    facilitys_uk['1140']["latitude"] = 52.04248
    facilitys_uk['1140']["longitude"] = -0.81931

    facilitys_uk['1311']["latitude"] = 52.27884
    facilitys_uk['1311']["longitude"] = -1.89576

    facilitys_uk['1312']["latitude"] = 52.27884
    facilitys_uk['1312']["longitude"] = -1.89576

    facilitys_uk['1548']["latitude"] = 51.55309
    facilitys_uk['1548']["longitude"] = -3.03672

    facilitys_uk['1683']["latitude"] = 53.46080
    facilitys_uk['1683']["longitude"] = -2.32357

    facilitys_uk['1684']["latitude"] = 53.46083
    facilitys_uk['1684']["longitude"] = -2.32346

    facilitys_uk['1848']["latitude"] = 53.37906
    facilitys_uk['1848']["longitude"] = -1.47971

    facilitys_uk['2116']["latitude"] = 51.49293
    facilitys_uk['2116']["longitude"] = -0.03064

    facilitys_uk['2384']["latitude"] = 53.79256
    facilitys_uk['2384']["longitude"] = -1.54054
    
    facilitys_uk['2417']["latitude"] = 57.15251
    facilitys_uk['2417']["longitude"] = -2.16024

    facilitys_uk['3144']["latitude"] = 50.83371
    facilitys_uk['3144']["longitude"] = -0.13445

    facilitys_uk['3213']["latitude"] = 52.47811
    facilitys_uk['3213']["longitude"] = -1.87830

    facilitys_uk['3884']["latitude"] = 52.92833
    facilitys_uk['3884']["longitude"] = -1.21246

    facilitys_uk['4060']["latitude"] = 53.47468
    facilitys_uk['4060']["longitude"] = -2.17468

    facilitys_uk['4088']["latitude"] = 51.50870
    facilitys_uk['4088']["longitude"] = -0.05794
    
    facilitys_uk['4360']["latitude"] = 51.51171
    facilitys_uk['4360']["longitude"] = -0.00294

    facilitys_uk['5441']["latitude"] = 51.44679
    facilitys_uk['5441']["longitude"] = -0.45422

    facilitys_uk['6433']["latitude"] = 52.35817
    facilitys_uk['6433']["longitude"] = -1.33147

    facilitys_uk['7042']["latitude"] = 51.76947
    facilitys_uk['7042']["longitude"] = -0.12977

    facilitys_uk['7425']["latitude"] = 51.54706
    facilitys_uk['7425']["longitude"] = -0.17404

    facilitys_uk['8078']["latitude"] = 51.28160
    facilitys_uk['8078']["longitude"] = -0.79469

    





    




    #Create a list of Towns where facilities are located
    townset = set(())
    towns = []
    for fac in facilitys_uk:
        townset.add(facilitys_uk[fac]['city'])
    # print(townset)

    # create a list of ipv4 prefixes for later use (ipv6 can wait for now)
        
    ix_prefix_list = []
    key = 'ipv4_prefix'
    for ix in ixps_uk:
        # print(ix)
        if key in ixps_uk[ix]:
            ix_prefix_list.append(ixps_uk[ix]['ipv4_prefix'])
        #create a list of probes that use this ixp
        ixps_uk[ix]['probes'] = []






    

    # Open the measurements file created previously
    # filename2 = 'measurements/uk_measurements.json' # for full uk_measurements
        

    # filters = {"tags": "NAT", "country_code": "gb", "asn_v4": "3333"}
    filters = {"tags": "system-Anchor", "country_code": "gb"}
    probes = ProbeRequest(**filters)
    probe_list = []
    uk_probes ={}


    # Create a Dictionary of the UK probes to be used 
    for t_probe in probes:
        
        probe_list.append(str(t_probe["id"]))
        uk_probes[t_probe["id"]] = {}
        uk_probes[t_probe["id"]] ["probe_ip"] = t_probe["address_v4"]
        uk_probes[t_probe["id"]] ["probe_x"] = t_probe["geometry"]["coordinates"][0]
        uk_probes[t_probe["id"]] ["probe_y"] = t_probe["geometry"]["coordinates"][1]
        uk_probes[t_probe["id"]] ["probe_asn"] = t_probe["asn_v4"]



        

    probes_uk_file = 'peeringdb_test_results/uk_probes.json'
    # write list of Uk probes to file in case needed later
    with open(probes_uk_file, "w") as outfile:
        json.dump(uk_probes, outfile)






    addr=reversename.from_address("185.74.25.250")
    reversedns = str(resolver.resolve(addr,"PTR")[0])
    # print(reversedns)
    ResultsFile = "target_6087.json"
    UKTownFile = "IPN_GB_2021.csv"

    # UK Towns file is a utf-8 encoded file, ignore any errors
    with codecs.open(UKTownFile,'r', encoding='utf-8',
                 errors='ignore') as file:
        content = file.readlines()
    header = content[:1]
    rows = content[1:]
    # print(header)
    # print(rows[0])
    length=len(rows)
    print (length)
    towns = {}
    for row in rows:
        
        name = row.split(',')[12].replace('"','')
        # name = name.replace('\r\n', '')
        id = row.split(',')[0]
        if name not in towns:
            towns[name] = {}
        towns[name][id] ={}
        towns[name][id]["lat"] = lat = row.split(',')[41]
        towns[name][id]["lon"] = lat = row.split(',')[42].replace('\r\n', '')
            
# Towns is our dictionary of UK towns and relevant coordinates
# Facilities have coordinates and ip ranges, if a routers ip address is in a facilities ??????? 

# Open the measurments 
with open("results/target_6087_source_6515.json") as f:
        measurements =json.load(f)

measurement =  {}
for measurement_id in measurements:
    print(measurement_id)
    input('wait')

    # Read in measurements

    for measurement_id in measurements:
        
        this_target = measurements[measurement_id]['target_probe']
        
        print("TARGET ***************************************************",this_target)

        measurement[this_target] = {}
        measurement[this_target] ["probe_ip"] = measurements[measurement_id]["target_address"]
        measurement[this_target] ["probe_x"] = measurements[measurement_id]["target_coordinates"][1]
        measurement[this_target] ["probe_y"] = measurements[measurement_id]["target_coordinates"][0]
        measurement[this_target] ["probe_asn"] = uk_probes[int(this_target)] ["probe_asn"]

        facilities_used = {}
        results = {}
        probe_number = 0
        

        #Create the Source Probes
        for probe_id in measurements[measurement_id]['results']:
            
            probe_number += 1
            print('PPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPP')
            print (probe_number,'Start of new Source Probe',probe_id,)
            print('PPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPP')
            ixp_entered_id = 0
            ixp_entered_flag = False
            facilities_used[probe_id] = []
            # Only iterate through source probe's not the target probe
            if probe_id != this_target:
                results[probe_id] = {}
                source_lon = measurements[measurement_id]['results'][probe_id]['source_coordinates'][0]
                source_lat = measurements[measurement_id]['results'][probe_id]['source_coordinates'][1]
                source_coords = (source_lon,source_lat)
                prev_hop ={}
                ixp_pre_hops = {}
                ixp_post_hops = {}
                ixp_in_hops = {}
                print(uk_probes[int(probe_id)])
                prev_hop['id'] = '0'
                prev_hop['ip_from'] =uk_probes[int(probe_id)]['probe_ip']
                prev_hop['rdns'] = ''
                prev_hop['rtt'] = 0
                prev_hop['address'] = 'street, town, postcode'
                prev_hop['asn'] = uk_probes[int(probe_id)]["probe_asn"]
                prev_hop['hop_latitude'] = source_lon
                prev_hop['hop_longitude'] = source_lat     
                prev_hop['use_next_hop_loc'] = False                           
                for hop in measurements[measurement_id]['results'][probe_id]['hops']:
                    results[probe_id][hop] = {}
                    #print('HOp IS', hop)
                   
                    #input('wait')
                    fac_exit_hop = False
                    fac_entry_hop = False
                    
                    
                    print('HHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHH') 
                    print(' START of NEW HOP',hop)
                    print ('for source probe', probe_number,'Probe ',probe_id,)
                    # print('previous hop',prev_hop, 'ip address', measurements[measurement_id]['results'][probe_id]['hops'][hop])
                   
                    this_hop_results = measurements[measurement_id]['results'][probe_id]['hops'][hop] # rtt value and IP address for this address
                    print('HHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHH') 
                    this_hop = get_hop_location(prev_hop, hop, this_hop_results,ixp_entered_flag)


                    print(this_hop)
                    

                    prev_hop = this_hop
                    results[probe_id][hop] = this_hop
                    print('%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%')
                    print(results[probe_id])
           
