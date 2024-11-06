#!/usr/bin/env python
# takes measurements saved from RIPE ATLAS and discovers each hops geographical locations
# Uses the results/targetsfull.json file created by read_measurments4.py, can use the entire file but to limit
# how much to use whilst testing, copy and paste just the target and source probe_ids into a new file,
# ie target_6087.json for one target and multiple sources
# or, target_6087_source_6515.json for just a single source and target.
import gc
gc.collect()
from dns import resolver,reversename
from decimal import Decimal

import csv
import codecs
import sys,getopt
sys.path.append("/home/paul/.local/lib/python3.7/site-packages/prsw")
import re
import os
os.chdir('/home/paul/Documents/UK')
del os 
import sqlite3

# import request so can access the RIPE database REST API 
import requests
ripe_url = 'https://rest.db.ripe.net/search.json'

import json
import jsonpickle # used for sets for Caida data
import ipaddress
import great_circle_calculator.great_circle_calculator as gcc
from ripe.atlas.cousteau import ProbeRequest, Traceroute, AtlasSource, AtlasRequest, AtlasCreateRequest
from dns import resolver,reversename


from peeringdb import PeeringDB, resource, config


# https://pypi.org/project/prsw/
# Check RPKI validation status TODO: this not currently implemented
# print(ripe.rpki_validation_status(3333, '193.0.0.0/21').status)
# Find all announced prefixes for a Autonomous System
# prefixes = ripe.announced_prefixes(3333)
# however this returns multiple ASNs for a given prefix, prbably best using the RIPE database for this

# PRSW, the Python RIPE Stat Wrapper, is a python package that simplifies access to the RIPE Stat public data API.
import prsw


# Interact with the looking glass
'''
example:-
for collector in ripe.looking_glass('185.40.232.0/24'):
    print(collector.location)

    for peer in collector.peers:
        print (peer)
        input('wait')
        print(
            peer.asn_origin,
            peer.as_path,
            peer.community,
            peer.last_updated,
            peer.prefix,
            peer.peer,
            peer.origin,
            peer.next_hop,
            peer.latest_time
        )
        input('wait')
# print(ripe.rpki_validation_status(3333, '185.40.232.0/24 ').status
input('wait')
'''
# Check RPKI validation status
# print(ripe.rpki_validation_status(3333, '193.0.0.0/21').status)


# Table Names for quering Peeringdb
#peeringdb_network         
#peeringdb_facility          peeringdb_network_contact 
#peeringdb_ix                peeringdb_network_facility
#peeringdb_ix_facility       peeringdb_network_ixlan   
#peeringdb_ixlan             peeringdb_organization    
#peeringdb_ixlan_prefix   
# 
# 
# create an ip to asn lookup file which will store succesful lookups from arin and RIPE 
# so that we do  not use all the permitted number of enquiries in one day.
    
asn_to_ip_file = 'asn_to_ip.json'
def read_asn_to_ip_json(filename = asn_to_ip_file):
    with open(filename) as f:
        asn_to_ip_data = json.load(f)
    return asn_to_ip_data

def write_asn_to_ip_json(new_data, filename=asn_to_ip_file):
    with open(filename,'r+') as file:
         # First we load existing data into a dict.
        
        file_data = json.load(file)
        # Join new_data with file_data inside emp_details
        file_data.update(new_data)
        # Sets file's current position at offset.
        file.seek(0)
        # convert back to json.
        json.dump(file_data, file, indent = 4)
 


def reverse_traceroute(rules,source,target,forward_measurement,rdns,rule,forward_hop,max_hop):
        
    reverse_measurement = measurement[source]['reverse_measurement_id']
    print('The reverse_measurment is ', reverse_measurement)
    print ('Source',source)
    print('target',target)
    print('measurement is',forward_measurement)
    print('rdns', rdns)
    print('forward_hop',forward_hop)
    print('max_hop',max_hop)
    #input('wait 113')
    this_ixp= ''
    reverse_hop =''
    facility = None
    ix_prefix_flag = False
    # this wont always work on asymetric forward and reverse traceroutes, will need to think about this.
    print(max_hop)

    if rule == 1:
        # first of all check if the ip addresses are in the same /24 subnet 
        # ie the first hop of the forward traceroute and the last hop of the
        # reverse tracroute.
        #  if this is the case then get the reverse dns name of the preceding hops
        # ip address on the reverse traceroute and return a rdns name
        # now put this rdns name through REGEX to see if we can locate it
        
        
        final_rev_hop = str(measurements[reverse_measurement]['results'][source]['max_hops'])
        pre_final_rev_hop = str(measurements[reverse_measurement]['results'][source]['max_hops']-1)
        # pre_final_rev_hop is the ip address of the penultimate hop on the return leg
        pre_final_rev_hop_ip = measurements[reverse_measurement]['results'][source]['hops'][pre_final_rev_hop]['ip_from']
        forw_ip = measurements[forward_measurement]['results'][target]['hops']['1']['ip_from']
        print(forw_ip)
        rev_ip  = measurements[reverse_measurement]['results'][source]['hops'][final_rev_hop]['ip_from']

        print('forward ip',forw_ip)
        print('reverse ip',rev_ip)
        rev_ip_cidr1 = rev_ip.split('.')
        rev_ip_prefix = rev_ip_cidr1[0]+'.'+rev_ip_cidr1[1]+'.'+rev_ip_cidr1[2]+'.0/24'
        if ipaddress.ip_address(forw_ip) in ipaddress.ip_network(rev_ip_prefix): 
            addr=reversename.from_address(pre_final_rev_hop_ip)
            rname = str(resolver.resolve(addr,"PTR")[0])
            print('rname is',rname)
            #input('wait 145')
            

        
        #this_ip = measurement['hops'][reverse_hop]['ip_from']
        
    if rule == 5 and reverse_hop != '':
        ix_prefix_flag,ix_hop,this_ixp = ix_prefix_check(source,measurement[reverse_hop]['ip_from'],hop) 
        reverse_hop = ix_hop
        this_ip = measurement['hops'][reverse_hop]['ip_from']
        ixinfo = ix_detail_dict[this_ip]
        print('ixinfo is' , this_ip, ixinfo)
        facility = ixinfo['facility_number']
        rdns = 'LINX '+ ixinfo['Peering LAN']
        rules.append('reverse_tr')
    if rule == 6:
        reverse_hop = '0'
        # TODO LETS CHECK FOR hops with IP addresses in the same /24 range
        # then do a reverse dns to see if they have  one
    print('rule is',rule)
    print('reverse-hop is',reverse_hop)
    

    #input('WAIT 168')
    '''  
    finally:
        print('IXINFO is',this_ip, facility)
        if facility != None:
            break
    '''
    return facility, rdns, rules, ix_prefix_flag,forward_hop,this_ixp
    

    
    


def append_vptable_dict(code,ip,lat,lon,rdns,fac,port,speed):
    if ip not in vptable_dict:
        stats['total_ips'] += 1
        stats[str(code)] += 1
        vptable_dict[ip] = {}
        vptable_dict[ip]['lat'] = lat
        vptable_dict[ip]['lon'] = lon
        vptable_dict[ip]['code'] = code
        vptable_dict[ip]['rdns'] = rdns
        vptable_dict[ip]['facility'] = fac
        vptable_dict[ip]['port'] = port
        vptable_dict[ip]['speed'] = speed

        print('VPTABLE IS',vptable_dict)

def write_vptable_file(vptable_filename):
    with open(vptable_filename, 'w') as f:
        json.dump(vptable_dict, f) 
    print('VPTABLE WRITTEN TO ', vptable_filename)
    


    

def convert(lst):
    my_dict = {}
    for l in lst:
        id = l['id']
        my_dict[id] = {}
        for key,value in l.items():
            my_dict[id][key] = value
    
    return my_dict

# Note redundant finction
def get_ixp_entry_fac(probe_id, hop, this_hop, prev_hop, this_ixp, facilities_used):
    # Get the ASN of the network Preceeding the IXP hop
    print('Probe ', probe_id)
    print('THIS HOP ********************',hop,this_hop)
    print('Previous HOP ********************',prev_hop)
    print('IXP',this_ixp)
    prev_hop_asn = prev_hop['asn']
    print('PREV HOP ASN = ',prev_hop_asn)
    
    hop_asn = this_hop['asn']
    print('HOP ASN = ',hop_asn) 
    hop_ip = this_hop['ip_from']
    print('this ip =', hop_ip)
    print('this ixp = ', this_ixp) 
    print(ixps_uk[this_ixp])
    
    ixp_facilities = ixps_uk[this_ixp]['fac_set'][0]
    
    print('IXP facilities is', ixp_facilities)
    # networks has been defined at start of code, is entire list of networks
    #input('wait')        
    #print(networks[14061])
    for network,values in networks.items():
        # print(network,values['asn'])
        # print('a'+prev_hop_asn+'a')
        if values['asn'] == prev_hop_asn:
                
                this_network = networks[network]
                print ('This network',this_network)
                #input('wait')
                break
        # very strange anomaly doesnt work properly with 14061 so had to do this
        elif prev_hop_asn == 14061:
                
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
            #netfac_info = pdb.fetch(resource.NetworkFacility, netfac)
    
            con = sqlite3.connect("/home/paul/peeringdb.sqlite3")
            cur = con.cursor()
            print('NETFAC', netfac)
            fac_id = (netfac,)
            cur.execute("select * from peeringdb_network_facility where id = ?", fac_id)
            data = cur.fetchone()
            colnames = cur.description
            print(colnames)
            print('facility info is',data)
            print('NETFAC INFO is', data[9])
            # input('wait')
            entry_netfac_ids.append(data[9])  
        print('The ASN preceding the IXP is', prev_hop_asn, ' and its facilites are', entry_netfac_ids)
        ixp_entered_flag = True
        # ixp_entered_id = this_ixp
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
        telehouse_list = ['34','39','45','835']
        equinix_list = ['832', '3152']
        if all(x in telehouse_list for x in possible_entry_facility):
            ixp_entry_point = possible_entry_facility[0]
            print('all telehouse',ixp_entry_point) 
            results[probe_id]['status'] = False
            results[probe_id]['status_reason'].append(probe_id+' All Entry points are Telehouse in london Docklands')
            results[probe_id]['status_code'].append(0)
            this_hop['hop_latitude'] = facilitys_uk[str(ixp_entry_point)]['latitude']
            this_hop['hop_longitude'] = facilitys_uk[str(ixp_entry_point)]['longitude']
            this_hop['facility'].append(ixp_entry_point)
        # if list of possible entry facilities are all equinix in slough then just chose the initial one   
        elif all(x in equinix_list for x in possible_entry_facility):
                ixp_entry_point = possible_entry_facility[0]
                print('all equinix',ixp_entry_point)
                results[probe_id]['status'] = False 
                results[probe_id]['status_reason'].append(probe_id+' All Entry points are Equinix in Slough')
                results[probe_id]['status_code'].append(0)
                this_hop['hop_latitude'] = facilitys_uk[str(ixp_entry_point)]['latitude']
                this_hop['hop_longitude'] = facilitys_uk[str(ixp_entry_point)]['longitude']
                this_hop['facility'].append(ixp_entry_point)
    
        else:
            # Lets see if we can figure out the facility by the hops ip address
            # This really should be one of the first checks
            print(this_hop['ip_from'])
            for ip_address in ix_detail_dict:
                if ip_address == this_hop['ip_from']:
                    print(ix_detail_dict[ip_address]['facility_number'])
                    this_fac = ix_detail_dict[ip_address]['facility_number']
                    this_ip = ip_address
                    break
            print('the correct fac is', this_fac, ' and the correct ip is', this_ip)
            ixp_entry_point = 0
            for fac in possible_entry_facility:
                if fac == this_fac:
                    # yes we did figure it out
                    ixp_entry_point = fac
                    results[probe_id]['status'] = True 
                    results[probe_id]['status_reason'].append(probe_id+' Entry Facility is'+ixp_entry_point)
                    results[probe_id]['status_code'].append(0)
                    this_hop['hop_latitude'] = facilitys_uk[str(ixp_entry_point)]['latitude']
                    this_hop['hop_longitude'] = facilitys_uk[str(ixp_entry_point)]['longitude']
                    this_hop['facility'].append(ixp_entry_point)
    
            if results[probe_id]['status'] != True:
                print('ohoh no valid rule for this posissible entry list', possible_entry_facility) 
                results[probe_id]['status'] = False
                results[probe_id]['status_reason'].append('initial Facility used as no valid rule for the Facility entry list ' + str(possible_entry_facility))
                results[probe_id]['status_code'].append(2)
                ixp_entry_point = possible_entry_facility[0]
                this_hop['hop_latitude'] = facilitys_uk[str(ixp_entry_point)]['latitude']
                this_hop['hop_longitude'] = facilitys_uk[str(ixp_entry_point)]['longitude']
                this_hop['facility'].append(ixp_entry_point)
    
    elif len(possible_entry_facility) == 1:
        ixp_entry_point =  possible_entry_facility[0]
        results[probe_id]['status'] = True 
        results[probe_id]['status_reason'].append(probe_id+' Entry Facility is'+str(ixp_entry_point))
        results[probe_id]['status_code'] = 0
        
        this_hop['facility'].append(ixp_entry_point)
          
        this_hop['hop_latitude'] = facilitys_uk[str(ixp_entry_point)]['latitude']
        this_hop['hop_longitude'] = facilitys_uk[str(ixp_entry_point)]['longitude']
    
    
    else:
        # shared entry facilities must be zero 
        # this can happen where a ISp uses remote peering see https://www.linx.net/about/our-partners/connexions-reseller-partners/
        print ('entry list must be 0', possible_entry_facility)
        results[probe_id]['status'] = False
        results[probe_id]['status_reason'].append(probe_id+' NO IXP Entry Point')
        results[probe_id]['status_code'].append(6)
        ixp_entry_point = '0' # TODO set it to the exit facility for now, but this is wrong
        this_hop['facility'].append(ixp_entry_point)
    facilities_used[probe_id].append(str(ixp_entry_point))
    # Note the entry point was the previous hop
    facilities_used[probe_id].append(str(int(hop)-1))
    print('facilities-used',facilities_used[probe_id])
    return ixp_entry_point

def ix_prefix_check(probe_id,this_ip,hop):
    ix_prefix_flag = False
    ix_hop = '0'
    this_ixp='0'
    for prefix in ix_prefix_list:
        
        # print (type(ipaddress.ip_address(this_hop['ip_from'])),type(ipaddress.ip_network(prefix)))
        # print(ipaddress.ip_address(this_hop['ip_from']),ipaddress.ip_network(prefix))
        if ipaddress.ip_address(this_ip) in ipaddress.ip_network(prefix): 
            # print('Checking', this_hop['ip_from'])
            ix_prefix_flag = True
            ix_hop = hop
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
        
    return ix_prefix_flag,ix_hop,this_ixp

def get_hop_location(ixp_pre_hops,ixp_in_hops,ixp_post_hops,facilities_used,this_target,probe_id,prev_hop,hop,hop_details,ixp_entered_flag, ix_hop,max_hop):
    
    print('hop details', hop_details)
    print ('max hop, hop',max_hop,hop)
    #print ('thismeasurement is', measurement_id, measurements[measurement_id]['results'][probe_id])
    print ('this target is',this_target)
    print('probe is is', probe_id)


    #input('wait')
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
    this_hop['network'] = 0
    this_hop['hop_latitude'] = 0
    this_hop['hop_longitude'] = 0
    this_hop['use_next_hop_loc'] = False
    this_hop['facility'] = []
    rname = port = speed = ''
    ix_hop = '0'

    print('This  hops ip address is',this_hop['ip_from'])

    # Check to see if this hops ip address is in a IX prefix list and set flag if true
    # TODO This could actually do with going at end of rules as it slows down the processing
    # but then how would i get a flag set for rules 5 and 6 ?
    
    local_subnet_flag = False
    this_hop['local_subnet_flag'] = False
    target_flag = False
    gateway_flag = False

    # PRELIMINARY CHECKS
    #########################################################################################################
    ix_prefix_flag,ix_hop,this_ixp = ix_prefix_check(probe_id,this_hop['ip_from'],hop)
    
   

    
    #Check to see if this ip address is in the local subnets
    if not ix_prefix_flag:
        for prefix in local_subnets:
           
            print(this_hop['ip_from'],prefix)
            if ipaddress.ip_address(this_hop['ip_from']) in ipaddress.ip_network(prefix): 
                local_subnet_flag = True
                this_hop['local_subnet_flag'] = True
                print('Local Subnet flag is', local_subnet_flag)
                #input('WAIT')
            break

    print('local subnet flag is Prev,this' , prev_hop['local_subnet_flag'],this_hop['local_subnet_flag'])   
    
    # Get this hops ASN
    # SET ASN TO null as fallback
    this_hop['asn'] = 0
    # if a local subnet flag is set then no point in searching for an ASN
    # otherwise search for the ASN wwhere this IP address is used 

    


    if not local_subnet_flag and not ix_prefix_flag:   
    
        #first of all lets check the ip to asn file thats been precreated to avoid keep making enquiries at RIPE
        
        # print(asn_to_ip_data)
        #input('asn_to_ip_data is above')
        if this_hop['ip_from'] in asn_to_ip_data:
            this_hop['asn'] = asn_to_ip_data[this_hop['ip_from']]
            #input('wait')
        else:
            options = {
                    'query-string' : this_hop['ip_from'],
                    'type-filter' : 'route',
                    'flags' : ['no-irt','no-referenced'],
                    'source' : 'RIPE'
                    }
            try:
                r = requests.get(ripe_url, params=options)
                print ('Status code 200 means its ok', r.status_code)
                
                # status code 200 is ok then get the ASN of this IP address
                if r.status_code == 200:
                    x = r.json()
                    #print(x)

                    attributes = x['objects']['object'][0]['attributes']['attribute']
                    for attrib in attributes:
                        if attrib['name'] == 'origin':
                            ripedb_asn = attrib['value']
                            # had to make this overly complex change because i  swapped from using RIPE stat to RIPE database
                            print ('RIPEDB_ASN',ripedb_asn)
                            this_hop['asn'] = [int(re.split('AS|as', ripedb_asn)[1])][0]
                            print('RIPE GOT THIS Hop ASN = ', this_hop['asn'])
                            # python object to be appended                            
                            y = { this_hop['ip_from'] : this_hop['asn']}

                            #print('Y is',y )
                            #input('wait')
                            write_asn_to_ip_json(y)
                            #input('wait')
                # if there was no result from Ripedatabase 
                # then set this_hops ASN to null for now, a later rulle may set it to the same as the next_hops asn
                else:
                    print(r.json())
                    arin_url = 'https://whois.arin.net/rest/ip/'
                    search_string = arin_url+this_hop['ip_from']
                    r = requests.get(search_string)
                    if r.status_code == 200:
                        x = r.json
                        
                        # print(x)
                        #input('hopefully got infor from ARIn wait')
                        # print(r.text)                   
                        this_hop['asn']  = r.text.split('<originAS>AS')[1].split('</originAS>')[0]
                        # print(' this hop is', this_hop['asn'])
                        print('ARIN GOT THIS Hop ASN = ', this_hop['asn'])
                        # python object to be appended                            
                        y = { this_hop['ip_from'] : this_hop['asn']}
                        #print('Y is',y )
                        #input('wait')
                        write_asn_to_ip_json(y)
                    else:
                        # if arin cant find the ASN lets try a looking glass server
                        response = ripe.network_info(this_hop['ip_from'])
                        this_hop['asn'] = response.asns[0]
                        # TODO: this needs checking
                        print('Arin got a not ok status but PRSW GOT THIS ASN = ', this_hop['asn'])       
                        # python object to be appended                            
                        y = { this_hop['ip_from'] : this_hop['asn']}
                        #print('Y is',y )
                        #input('wait')
                        write_asn_to_ip_json(y)
                        #input('wait')
                        #this_hop['asn'] = 0
            except:
                    this_hop['asn'] = 0
             
    # if this ip address is used by an IX get the ASN of the IX
    if ix_prefix_flag:
        # added this if statement at a later stage, perhaps better to do it this way than rely on a file of ip address to asns
        # would need the addresses of all Uk based IXs
        if ipaddress.ip_address(this_hop['ip_from']) in ipaddress.ip_network('195.66.236.0/22'):
            this_hop['asn'] = '5459'
        else:
            #try getting it from asn_to_ip file 
            try:
                
                this_hop['asn'] = asn_to_ip_data[this_hop['ip_from']]
            except:
                con = sqlite3.connect("/home/paul/peeringdb.sqlite3")
                cur = con.cursor()
                print('IXPS UK', this_ixp,ixps_uk[this_ixp])
                ixp_ip = (this_hop['ip_from'],)
                this_hop['asn'] = 0
                try:
                    cur.execute("select * from peeringdb_network_ixlan where ipaddr4 = ?", ixp_ip)
                    data = cur.fetchone()
                    #colnames = cur.description
                    #print(colnames)
                
                    this_hop['network'] = data[12]
                    print('Network is',data[12])
                    x = (data[12],)

                    cur.execute("select * from peeringdb_network where id = ?",x )

                    data = cur.fetchone()
                    #colnames = cur.description
                    #print(colnames)
                    print('ASN is',data[5])
                    this_hop['asn'] = data[5]
                except:
                    this_hop['asn'] = 0
                    print('line 614')
                    print('this ip is an ix prefix but couldnt get an asn',ixp_ip)
                    
            
                    
        
    

    '''
    # I was also going to try RIPESTAT but it doesnt seem to be any improvement on RIPE DATABASe
    # RIPESTAT appears to add no further info than RIPE DB can add so have commenetd this out.
    # else:
        # if Ripe DB cant find the ASN try RIPE stat
        print('trying RIPE STAT')
        if this_hop['ip_from'] != '10.255.255.2': # ripestat doesnt like local subnets 
            # TODO: SHOULDnt THIS BE all the local subnets ?
            # if this_hop['ip_from'] != '195.66.224.253': # This prefix has been hijacked by AS25577
            print('trying RIPE STAT')
            response = ripe.network_info(this_hop['ip_from'])
            print('Response', response)
            print('ASNS are', response.asns, response.prefix)
            for asn in response.asns:
                print(asn)
            this_hop['asn'] = [asn]
            
            #else:
                # This prefix has been hijacked by AS25577 so having to manually set it
                # TODO: reported this to RIPE, looks like they have fixed it now so this may no longer be neccessary
                #this_hop['asn'] = [43996]
        print(this_hop)
    '''
    rule_flag = False
    rules = []

    # individual ip addresess range lookups  
    print(this_hop['ip_from'])
      
    if ipaddress.ip_address(this_hop['ip_from']) in ipaddress.ip_network('185.40.232.0/24'):
        results['prelim'] +=1
        try:
            addr=reversename.from_address(this_hop['ip_from'])
            rname = str(resolver.resolve(addr,"PTR")[0]) 
        except:
            rname = 'Anycast'
        fac = '34'
        lon = -0.0031222276903634526
        lat = 51.511827346720686 
        coords = (lon,lat)
        port = speed = ''
        rule_flag = True
        this_hop['hop_latitude'] =  lat
        this_hop['hop_longitude'] = lon
        this_hop['asn'] = 36236
        this_hop['rdns'] = 'Anycast'
        this_hop['facility'].append(fac)
        
        append_vptable_dict(2, this_hop['ip_from'],this_hop['hop_latitude'], this_hop['hop_longitude'],this_hop['rdns'],this_hop['facility'],"","")
        results[probe_id]['status'] = True
        rules.append(10)
        print('the ip address was in the anycast range')
        
        if rname.casefold() in results['successes']['prelim']:
            results['successes']['prelim'][rname.casefold()] +=1 
            results['successes']['prelim']['total'] +=1 
        else:
            results['successes']['prelim'][rname.casefold()] = 1
            results['successes']['prelim']['total'] +=1 
    
    if ipaddress.ip_address(this_hop['ip_from']) in ipaddress.ip_network('195.50.90.128/25'):
        results['prelim'] +=1
        try:
            addr=reversename.from_address(this_hop['ip_from'])
            rname = str(resolver.resolve(addr,"PTR")[0]) + ' telehouse north-LONDON-CAR3-CUSTOMER-SERIAL-LINKS1'
        except:
            rname = 'telehouse north-LONDON-CAR3-CUSTOMER-SERIAL-LINKS1'
        fac = '34'
        lon = -0.0031222276903634526
        lat = 51.511827346720686 
        coords = (lon,lat)
        port = speed = ''
        rule_flag = True
        this_hop['hop_latitude'] =  lat
        this_hop['hop_longitude'] = lon
        this_hop['asn'] = 36236
        this_hop['rdns'] = rname 
        this_hop['facility'].append(fac)

        append_vptable_dict(2, this_hop['ip_from'],this_hop['hop_latitude'], this_hop['hop_longitude'],this_hop['rdns'],this_hop['facility'],"","")
        results[probe_id]['status'] = True
        rules.append(11)
        if rname.casefold() in results['successes']['prelim']:
            results['successes']['prelim'][rname.casefold()] +=1 
            results['successes']['prelim']['total'] +=1 
        else:
            results['successes']['prelim'][rname.casefold()] = 1
            results['successes']['prelim']['total'] +=1 
    
    if this_hop['ip_from'] == '31.217.132.101':
        results['prelim'] +=1
        fac = '896'
        lon = -1.54109
        lat = 53.793329 
        coords = (lon,lat)
        rname = port = speed = ''
        rule_flag = True
        this_hop['hop_latitude'] =  lat
        this_hop['hop_longitude'] = lon
        this_hop['asn'] = 33920
        this_hop['rdns'] = 'IX Reach - AS43531 - at AQL Salem Church Leeds'
        this_hop['facility'].append(fac)

        append_vptable_dict(2, this_hop['ip_from'],this_hop['hop_latitude'], this_hop['hop_longitude'],this_hop['rdns'],this_hop['facility'],"","")
        results[probe_id]['status'] = True
        rules.append(12)
        if rname.casefold() in results['successes']['prelim']:
            results['successes']['prelim'][rname.casefold()] +=1 
            results['successes']['prelim']['total'] +=1 
        else:
            results['successes']['prelim'][rname.casefold()] = 1
            results['successes']['prelim']['total'] +=1 
    
    if this_hop['ip_from'] == '195.66.226.35':
        rname = 'ge-0-0-0-border1-thn.linx.net'
        fac = '34'
        lon = -0.0031222276903634526
        lat = 51.511827346720686 
        coords = (lon,lat)
        port = speed = ''
        rule_flag = True
        this_hop['hop_latitude'] =  lat
        this_hop['hop_longitude'] = lon
        this_hop['asn'] = 5459            ### 8553
        this_hop['rdns'] = rname 
        this_hop['facility'].append(fac)


        append_vptable_dict(2, this_hop['ip_from'],this_hop['hop_latitude'], this_hop['hop_longitude'],this_hop['rdns'],this_hop['facility'],"","")
        results[probe_id]['status'] = True
        rules.append(12)
        if rname.casefold() in results['successes']['prelim']:
            results['successes']['prelim'][rname.casefold()] +=1 
            results['successes']['prelim']['total'] +=1 
        else:
            results['successes']['prelim'][rname.casefold()] = 1
            results['successes']['prelim']['total'] +=1 
        

        


     
    # END OF PRELIMINARY CHECKS
    # ###############################################################################################################           
    


    # Find Location Logic
    ##############################################################################################################

    

    # First of all start with the obvious, We dont need to run REGEX on every hop because some hops will not have ReverseDNS
    # Addresses.

    
    
    # rule1 if hop is 1 and no prelim rules have taken place
    # This is  the  gateway that the probe is connected to.  
    

    
    #if hop rtt is relatively small gateway is probably in same location
    if this_hop['id'] == '1' and not rule_flag:
        rule = 1
        hop_result =this_hop['rtt']
        if hop_result < .1:
            results['rtt']['.0'] += 1
        if hop_result >= .1 and hop_result < .2:
            results['rtt']['.1'] += 1
        if hop_result >= .2 and hop_result < .3:
            results['rtt']['.2'] += 1
        if hop_result >= .3 and hop_result < .4:
            results['rtt']['.3'] += 1
        if hop_result >= .4 and hop_result < .5:
            results['rtt']['.4'] += 1
        if hop_result >= .5 and hop_result < .6:
            results['rtt']['.5'] += 1
        if hop_result >= .6 and hop_result < .7:
            results['rtt']['.6'] += 1
        if hop_result >= .7 and hop_result < .8:
            results['rtt']['.7'] += 1
        if hop_result >= .8 and hop_result < .9:
            results['rtt']['.8'] += 1
        if hop_result >= .9 and hop_result < 1:
            results['rtt']['.9'] += 1
        if hop_result >= 1:
            results['rtt']['1'] += 1
        results['rule1'] += 1
        #print(results['rule1'],this_target, probe_id,this_hop)
        #input('in wait')
        # TODO ### done####we need to ensure the gateway is close to the source probe , any RTTs from source to 
        # gateway should realistically be under 1 ms
        rname = port = speed = ''
        rule_flag = True
        gateway_flag = True
        this_hop['facility'] = []
    
        
        if this_hop['rtt'] < 1:

            
           
            #print(this_target, probe_id,this_hop)
            
            #input('out wait')
            
            

            #print(results['rtt'],results['rule1'],this_target, probe_id,this_hop)
            #input('in wait')
            
            
            
            
            
            
            
            
            
        
            

            
            if not this_hop['ip_from'] == measurement[this_target] ["probe_ip"]: #make sure this isnt the target ip address
                
                
                # lets try rdns but it is likely it wont work
                
                try:
                    addr=reversename.from_address(this_hop['ip_from'])
                    rname = str(resolver.resolve(addr,"PTR")[0])
                    this_hop['rdns'] = rname
                    #print(vptable_dict)
                except:  
                    print(' failed to get rname')
                    print('however the hop is relatively close to the source probe so choosing the coords of the probe')
                    this_hop['hop_longitude'] = prev_hop['hop_longitude']
                    this_hop['hop_latitude'] = prev_hop['hop_latitude']
                    this_facility = ''
                    append_vptable_dict(2, this_hop['ip_from'],this_hop['hop_latitude'], this_hop['hop_longitude'],rname,this_facility,port,speed)
                    results[probe_id]['status'] = True
                    if rname.casefold() in results['successes']['rule1']:
                        results['successes']['rule1'][rname.casefold()] +=1 
                        results['successes']['rule1']['total'] +=1 
                    else:
                        results['successes']['rule1'][rname.casefold()] = 1
                        results['successes']['rule1']['total'] +=1 
                    # input('wait')
                    #print('RNAME is ', rname)
                    #input('wait')
                else:
                    print('got rname',rname)
                    # this needs to now do a regex on the rname

                    # input('wait')
                    #a=0
                    try:
                        this_facility, rules = get_facilitys(rules,rname,this_hop)
                        if len(this_facility) == 0:
                            coords =(0,0)
                            print('do a reverse traceroute because facilities are 0')
                            print('Trying reverse measurement')
                            print('this measurement id is ', measurement[this_target]['measurement_id'])
                            print('max hop is',max_hop,'ix_hop is',ix_hop)
                            print('trying a reverse traceroute where facilities = 0 line 858')
                            this_fac,reverse_dns,rules,ix_prefix_flag,ix_hop,this_ixp = reverse_traceroute(rules,this_target,probe_id,measurement[this_target]['measurement_id'],this_hop['rdns'],rule,1,max_hop)
                            print('reverse_dns',reverse_dns)
                            print(this_fac)
                            # Now we do a REGEX on the reverse traceroute rdns to see if that has a location
                            
                            this_facility, rules = get_facilitys(rules,reverse_dns,this_hop)
                            print(this_facility)
                            print('wait 896')
                            #post_regex(rname,this_facility)
                            
                            
                            
                            if rname.casefold() in results['failures']['rule1']:
                                results['failures']['rule1'][rname.casefold()] +=1 
                                results['failures']['rule1']['total'] +=1 
                            else:
                                results['failures']['rule1'][rname.casefold()] = 1
                                results['failures']['rule1']['total'] +=1 
                            append_vptable_dict(5, this_hop['ip_from'],0, 0,rname,'',port,speed)
                
                        if len(this_facility) == 1:
                            coords= (facilitys_uk[this_facility[0]]['longitude'],facilitys_uk[this_facility[0]]['latitude'])
                            lon = coords[0]
                            lat = coords[1]
                            print(this_hop['facility'],this_facility)
                            this_hop['facility'].append(this_facility)
                            print('*************************************************************************')
                            print(this_hop['facility'])
                            #input('wait')
                            this_hop['hop_longitude'] = lon
                            this_hop['hop_latitude'] = lat
                            append_vptable_dict(2, this_hop['ip_from'],this_hop['hop_latitude'], this_hop['hop_longitude'],rname,this_facility,port,speed)
                            results[probe_id]['status'] = True
                            if rname.casefold() in results['successes']['rule1']:
                                results['successes']['rule1'][rname.casefold()] +=1 
                                results['successes']['rule1']['total'] +=1 
                            else:
                                results['successes']['rule1'][rname.casefold()] = 1
                                results['successes']['rule1']['total'] +=1 
                        if len(this_facility) > 1:
                            print ('Do a reverse_traceroute because faciltities are more than 1')
                            coords=(0,0)
                            #input('wait')
                        
                        
                        
                    except:

                        print('got rname but failed to get coords',rname)
                        print('however the hop is relatively close to the source probe so choosing the coords of the probe')
                        this_hop['hop_longitude'] = prev_hop['hop_longitude']
                        this_hop['hop_latitude'] = prev_hop['hop_latitude']
                        this_facility = ''
                        append_vptable_dict(2, this_hop['ip_from'],this_hop['hop_latitude'], this_hop['hop_longitude'],rname,this_facility,port,speed)
                        results[probe_id]['status'] = True
                        if rname.casefold() in results['successes']['rule1']:
                            results['successes']['rule1'][rname.casefold()] +=1 
                            results['successes']['rule1']['total'] +=1 
                        else:
                            results['successes']['rule1'][rname.casefold()] = 1
                            results['successes']['rule1']['total'] +=1 
            else:
                print('was target address so ignore')
                this_hop['hop_latitude'] =  ''
                this_hop['hop_longitude'] = ''
                this_hop['asn'] = prev_hop['asn']
                results[probe_id]['status'] = False
                print('HOp1s info is',this_hop, ' probe info is ', probe_id, prev_hop)
                this_hop['rdns'] = 'local'
                if rname.casefold() in results['failures']['rule1']:
                    results['failures']['rule1'][rname.casefold()] +=1 
                    results['failures']['rule1']['total'] +=1 
                else:
                    results['failures']['rule1'][rname.casefold()] = 1
                    results['failures']['rule1']['total'] +=1 
                append_vptable_dict(5, this_hop['ip_from'],0, 0,rname,'',port,speed)
        
        else:
            print('RTT is over 1ms so most likely not local')
            this_hop['hop_latitude'] =  ''
            this_hop['hop_longitude'] = ''
            this_hop['asn'] = prev_hop['asn']
            results[probe_id]['status'] = False
            print('HOp1s info is',this_hop, ' probe info is ', probe_id, prev_hop)
            try:
                addr=reversename.from_address(this_hop['ip_from'])
                rname = str(resolver.resolve(addr,"PTR")[0])
                this_hop['rdns'] = rname
            except:
                print('failed to get rname')
                #input('wait')
                if rname.casefold() in results['failures']['rule1']:
                    results['failures']['rule1'][rname.casefold()] +=1 
                    results['failures']['rule1']['total'] +=1 
                else:
                    results['failures']['rule1'][rname.casefold()] = 1
                    results['failures']['rule1']['total'] +=1 
                append_vptable_dict(5, this_hop['ip_from'],0, 0,rname,'',port,speed)
                
            else:
                print('got rname',rname)
                #input('wait')
                try:
                    this_facility, rules = get_facilitys(rules,rname,this_hop)
                    if len(this_facility) == 0:
                        coords =(0,0)
                        print('do a reverse traceroute because facilities are 0')
                        if rname.casefold() in results['failures']['reverse_tr']:
                            results['failures']['reverse_tr'][rname.casefold()] +=1 
                            results['failures']['reverse_tr']['total'] +=1 
                        else:
                            results['failures']['reverse_tr'][rname.casefold()] = 1
                            results['failures']['reverse_tr']['total'] +=1 
              
                            append_vptable_dict(5, this_hop['ip_from'],0, 0,rname,'',port,speed)

                        
                    if len(this_facility) == 1:
                        coords= (facilitys_uk[this_facility[0]]['longitude'],facilitys_uk[this_facility[0]]['latitude'])
                        lon = coords[0]
                        lat = coords[1]
                        print(this_hop['facility'],this_facility)
                        this_hop['facility'].append(this_facility)
                        print('*************************************************************************')
                        print(this_hop['facility'])
                        # input('wait')
                        this_hop['hop_longitude'] = lon
                        this_hop['hop_latitude'] = lat
                        append_vptable_dict(2, this_hop['ip_from'],this_hop['hop_latitude'], this_hop['hop_longitude'],rname,this_facility,port,speed)
                        results[probe_id]['status'] = True
                        if rname.casefold() in results['successes']['rule1']:
                            results['successes']['rule1'][rname.casefold()] +=1 
                            results['successes']['rule1']['total'] +=1 
                        else:
                            results['successes']['rule1'][rname.casefold()] = 1
                            results['successes']['rule1']['total'] +=1 
                    if len(this_facility) > 1:
                        coords=(0,0)
                        print ('Do a reverse_traceroute because faciltities are more than 1')   
                        if rname.casefold() in results['failures']['reverse_tr']:
                            results['failures']['reverse_tr'][rname.casefold()] +=1 
                            results['failures']['reverse_tr']['total'] +=1 
                        else:
                            results['failures']['reverse_tr'][rname.casefold()] = 1
                            results['failures']['reverse_tr']['total'] +=1 
                except:
                    #print('got rname but failed to get coords',rname)
                    #input('wait')
                    if rname.casefold() in results['failures']['rule1']:
                        results['failures']['rule1'][rname.casefold()] +=1 
                        results['failures']['rule1']['total'] +=1 
                    else:
                        results['failures']['rule1'][rname.casefold()] = 1
                        results['failures']['rule1']['total'] +=1 
                    append_vptable_dict(5, this_hop['ip_from'],0, 0,rname,'',port,speed)
        #print(results)
        #input('wait')
        rules.append(1)
        #input('wait')


    # rule2 
    # if using a private subnet and last hop wasnt then check RTT value to see if this router is local to previous router
    # using a latency threshold of 1 ms to denote whether it is local or remote
    
    if local_subnet_flag and not rule_flag:
        rule = 2
        results['rule2'] +=1
        rname = port = speed = ''
        if not prev_hop['local_subnet_flag']:
            rule_flag = True
            if this_hop['rtt'] < 1:
                print('local to previous router')
                this_hop['hop_latitude'] =  prev_hop['hop_latitude']
                this_hop['hop_longitude'] = prev_hop['hop_longitude']
                this_hop['rdns'] = 'private'
                this_hop['asn'] = prev_hop['asn']
                results[probe_id]['status'] = True
            else:
                print('possibly remote end of site to site link')
                this_hop['use_next_hop_loc'] = True # Setting a flag so that next hop knows to set prev hop to same location
                this_hop['rdns'] = 'private'
                results[probe_id]['status'] = False
            
            
            if rname.casefold() in results['successes']['rule2']:
                results['successes']['rule2'][rname.casefold()] +=1 
                results['successes']['rule2']['total'] +=1 
            else:
                results['successes']['rule2'][rname.casefold()] = 1
                results['successes']['rule2']['total'] +=1 
            append_vptable_dict(2, this_hop['ip_from'],0, 0,rname,'',port,speed)

        else:
            print ('hmm prev_hop prefix is in private subnets and so is this (is this a multi hop local network ?) - see the find location logic rules 2')
            rule_flag = True
            print('remote end of connection')
            this_hop['use_next_hop_loc'] = True # Setting a flag so that next hop knows to set prev hop to same location
            this_hop['hop_latitude'] =  0
            this_hop['hop_longitude'] = 0
            this_hop['rdns'] = 'local'
            this_hop['asn'] = prev_hop['asn']
            results[probe_id]['status'] = True
            if rname.casefold() in results['failures']['rule2']:
                results['failures']['rule2'][rname.casefold()] +=1 
                results['failures']['rule2']['total'] +=1 
            else:
                results['failures']['rule2'][rname.casefold()] = 1
                results['failures']['rule2']['total'] +=1 
            append_vptable_dict(5, this_hop['ip_from'],0, 0,rname,'',port,speed)
            
            #input('Wait')
        print('RULE2')
        rules.append(2)
        # NOte: not easy to know whether this will be a success or failure until later in the process so a success here
        #  just indicates that Rule 2 was invoked (this will cause a duplicate entry perhaps at rule3/4/5 )
               
        
        #input('wait')
        
    # rule3 if the last hops 'use_next_hop_loc' is true then we need to fill in the last ones coordiantes as well as this one
    # as it likely that the two are in the same location. (this may go back a few hops)
    if prev_hop['use_next_hop_loc'] == True and not ix_prefix_flag: # make sure this hop isnt the IX hop as that is at the far end of the link
        rule = 3
        results['rule3'] +=1
        rule_flag = True
        rname = port = speed = ''
        
        addr=reversename.from_address(this_hop['ip_from'])
        try:
            rname = str(resolver.resolve(addr,"PTR")[0])
        except:
            #except:
            # if we cant get the location of this hop using dns then try comparing last asn to this asn and finding
            # what network facilities the two jointly peer at.
            print('Probe ', probe_id)
            print('THIS HOP ********************',hop,this_hop)
            print('Previous HOP ********************',prev_hop)
            
            if this_hop['asn'] != prev_hop['asn']:
                #TODO this needs more investigation if asns are different could look this up to see the
                # where what facilities they both peer at.
                
                print('ASNS are different - RULE3 perhaps maybe use this fact, deferring locating for now')
                print(results[probe_id])
                this_hop['use_next_hop_loc'] = True

                # input('wait')
            else:
                # if the two asns are the same then we are going to have to defer locating this hop and use the next hops location
                
                this_hop['use_next_hop_loc'] = True
                print(' RULE3 USE NEXT HOPs location for the previous hop and this hop')
                # input('wait Continue if you want to see how far you get')
            # either way this is a rule3 failure
            if rname.casefold() in results['failures']['rule3']:
                results['failures']['rule3'][rname.casefold()] +=1 
                results['failures']['rule3']['total'] +=1 
            else:
                results['failures']['rule3'][rname.casefold()] = 1
                results['failures']['rule3']['total'] +=1 
            append_vptable_dict(5, this_hop['ip_from'],0, 0,rname,'',port,speed)

        else:
            this_hop['rdns'] = rname
            print('RULE 3 This hops Reversedns name is',rname)
            this_facility, rules = get_facilitys(rules,rname,this_hop)
            if len(this_facility) == 0:
                coords =(0,0)
                print('do a reverse traceroute because facilities are 0')
                if rname.casefold() in results['failures']['reverse_tr']:
                    results['failures']['reverse_tr'][rname.casefold()] +=1 
                    results['failures']['reverse_tr']['total'] +=1 
                else:
                    results['failures']['reverse_tr'][rname.casefold()] = 1
                    results['failures']['reverse_tr']['total'] +=1 

                append_vptable_dict(5, this_hop['ip_from'],0, 0,rname,'',port,speed)
                
            if len(this_facility) == 1:
                coords= (facilitys_uk[this_facility[0]]['longitude'],facilitys_uk[this_facility[0]]['latitude'])
                lon = coords[0]
                lat = coords[1]
                print(this_hop['facility'],this_facility)
                this_hop['facility'].append(this_facility)
                print('*************************************************************************')
                print(this_hop['facility'])
                # input('wait')
                this_hop['hop_longitude'] = lon
                this_hop['hop_latitude'] = lat
                append_vptable_dict(2, this_hop['ip_from'],this_hop['hop_latitude'], this_hop['hop_longitude'],rname,this_facility,port,speed)
                results[probe_id]['status'] = True
                if rname.casefold() in results['successes']['rule1']:
                    results['successes']['rule1'][rname.casefold()] +=1 
                    results['successes']['rule1']['total'] +=1 
                else:
                    results['successes']['rule1'][rname.casefold()] = 1
                    results['successes']['rule1']['total'] +=1 
            if len(this_facility) > 1:
                coords=(0,0)
                print ('Do a reverse_traceroute because faciltities are more than 1')
                if rname.casefold() in results['failures']['reverse_tr']:
                    results['failures']['reverse_tr'][rname.casefold()] +=1 
                    results['failures']['reverse_tr']['total'] +=1 
                else:
                    results['failures']['reverse_tr'][rname.casefold()] = 1
                    results['failures']['reverse_tr']['total'] +=1 
                append_vptable_dict(5, this_hop['ip_from'],0, 0,rname,'',port,speed)
    
                # Now go back and set the last hops that had their use next hop location to true
            if len(this_facility) == 1:
                for h in range(int(hop)-1,0,-1):
                    print('hop is', h)
                    lon = coords[0]
                    lat = coords[1]
                    if h in results[probe_id]:
                        print(results[probe_id][str(h)])
                        if results[probe_id][str(h)]['use_next_hop_loc'] == True:
                            
                            results[probe_id][str(h)]['hop_latitude'] =  lat # fill in longitude of last hop
                            results[probe_id][str(h)]['hop_longitude'] =  lon # fill in longitude of last hop
                            results[probe_id][str(h)]['facility'].append(this_facility)
                            append_vptable_dict(2, this_hop['ip_from'],this_hop['hop_latitude'], this_hop['hop_longitude'],rname,this_hop['facility'],"","")
                            
                            print('hop',h,results[probe_id][str(h)])
                            # if this hop is not a local subnet then add to vptable
                            if not results[probe_id][str(h)]['local_subnet_flag']:
                                # TODO: i think the below doesnt need results[probe_id] test when get chance see line 744
                                append_vptable_dict(2, results[probe_id][str(h)]['ip_from'],this_hop['hop_latitude'], this_hop['hop_longitude'],rname,this_hop['facility'], "","")
                                
                            
                        else:
                            print('use next hop loc at hop',h,'is no longer true')
                            break
                    else:
                        print ('RULE 3 got the rname', rname,' got the facility',this_facility)
                        print('But failed to locate the previous hop possibly due to a RTT failure')
                        print('PROBE id is',probe_id,this_hop)
                        append_vptable_dict(5, this_hop['ip_from'],this_hop['hop_latitude'], this_hop['hop_longitude'],rname,this_facility,port,speed)
                        
                        results[probe_id]['status'] = False
                        if rname.casefold() in results['failures']['rule3']:
                            results['failures']['rule3'][rname.casefold()] +=1 
                            results['failures']['rule3']['total'] +=1 
                        else:
                            results['failures']['rule3'][rname.casefold()] = 1
                            results['failures']['rule3']['total'] +=1 
            else:
                print ('RULE 3 got the rname', rname,' but couldnt get the facility',this_hop)
                print('PROBE id is',probe_id,this_hop)
                append_vptable_dict(5, this_hop['ip_from'],this_hop['hop_latitude'], this_hop['hop_longitude'],rname,this_facility,port,speed)
                
                results[probe_id]['status'] = False
                if rname.casefold() in results['failures']['rule3']:
                    results['failures']['rule3'][rname.casefold()] +=1 
                    results['failures']['rule3']['total'] +=1 
                else:
                    results['failures']['rule3'][rname.casefold()] = 1
                    results['failures']['rule3']['total'] +=1 
                # input('wait')
            print('RESULTS ARE ',results[probe_id])
            
        
        # if resolver was able to get a reverse dns name then continue as normal.
        #         
        
            
        print('RULE3')
        rules.append(3)
        #input('wait')
        
    # rule 4 if this hop is the target ip address
    if not rule_flag:
        if this_hop['ip_from'] == measurement[this_target] ["probe_ip"]:
            rule = 4
            results['rule4'] +=1
            rule_flag = True
            target_flag = True
            rname = port = speed = ''
            this_hop['hop_longitude'] = measurement[this_target] ["probe_y"] 
            this_hop['hop_latitude'] = measurement[this_target] ["probe_x"]
            this_hop['facility'] = []
            this_hop['rdns'] = 'PROBE'+this_target   
            print('this hop is', this_hop)
            append_vptable_dict(2, this_hop['ip_from'],this_hop['hop_latitude'], this_hop['hop_longitude'],this_hop['rdns'],this_hop['facility'],port,speed)
            
            results[probe_id]['status'] = True
            print('RULE4')
            if rname.casefold() in results['successes']['rule4']:
                results['successes']['rule4'][rname.casefold()] +=1 
                results['successes']['rule4']['total'] +=1 
            else:
                results['successes']['rule4'][rname.casefold()] = 1
                results['successes']['rule4']['total'] +=1 
            rules.append(4)
            
    # rule5 if ip address is part of an IXP then the facility needs to be worked out and then the coordinates of that facility
    # NOTE: The following check finds the Entry facility of the IX however RULE 6 will already have found the entry point
    # if the previous hop had a valid RDNS name so this rule just verifies that and therefore this rule may no longer be required.
    
    # MADE THIS REDUNDANT SO NOW RELYING ON RULE 6 TO FIND THE ENTRY FACILITY
    # So now this rule (5A) simply finds the IX exit facility and coords
    '''
    if ix_prefix_flag:
        rule_flag = True
        # check for Internet Exchange
        #this_ixp = 0
        #ixp_entered_flag = False
        #ixp_entered_id = 0
        
        if this_ixp and not ixp_entered_flag:
            ixp_entered_flag = True
            prev_fac = {}
            prev_fac = ix_detail_dict[prev_hop['ip_from']]
            print( 'FACILITY =',prev_fac)
            if prev_fac:
                ixp_entry_point = prev_fac['facility_number']
                results[probe_id]['status'] = True 
                results[probe_id]['status_reason'].append(probe_id+' Entry Facility is'+ixp_entry_point)
                results[probe_id]['status_code'].append(0)
                prev_hop['hop_latitude'] = facilitys_uk[str(ixp_entry_point)]['latitude']
                prev_hop['hop_longitude'] = facilitys_uk[str(ixp_entry_point)]['longitude']
                prev_hop['facility'] = ixp_entry_point
            else:
                # Need to discover the ASn of the hop preceding the IXP so that we can compare which facilities
                # it has in common with the IXP in order to map where the route enters the IXP ie waht facility.
            
                # the ixp facility entry code has been Moved to its own function (yet to do the exit function)
                ixp_entry_point = get_ixp_entry_fac(probe_id, hop, this_hop, prev_hop, this_ixp, facilities_used)
            
            print(ixp_entry_point)
        print(ix_detail_dict[this_hop['ip_from']])
        print('RULE5',ixp_entered_flag)
        #input('wait')
    '''    
    #RULE 5A
    # GET IX_EXIT_FACILITY PROCESS
    # Now we need the exit point if we are now inside the IXP
    if ix_prefix_flag:
        rule = 5
        results['rule5'] +=1
        this_hop['use_next_hop_loc'] = False 
        rule_flag = True
        rname = port = speed = ''
        print('Now we are in the IX and this hop must be exiting the IX')
        print ('hop IP address',this_hop['ip_from'])
        print('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
        print('IXP ENTEREDRED FLAG', ixp_entered_flag)
            
        print ('ixp prefix',this_ixp, ixps_uk[this_ixp]['ipv4_prefix'])

        print('HOP is ', hop)
        #input('wait')
            
        # if ipaddress.ip_address(this_hop['ip_from']) not in ipaddress.ip_network(ixps_uk[ixp_entered_id]['ipv4_prefix']):
        print ('NOW OUT OF THE IXP, ixp prefix',this_ixp, ixps_uk[this_ixp]['ipv4_prefix'])

        print('HOP is ', hop)
        # If we are not still in the IXP then we can now get the exiting ASN
        print(this_hop)
        if not this_hop['asn']:
            hop_asn = ix_detail_dict[this_hop['ip_from']]['ASN']
        else:
            hop_asn = this_hop['asn']
        print('HOP ASN = ',hop_asn)
        '''
        hop_asn = this_hop['asn'][0]
        print('HOP ASN = ',hop_asn) 
        hop_ip = this_hop['ip_from']
        print('this ip =', hop_ip)
        print('this ixp = ', this_ixp) 
        ''' 
        ixp_facilities = ixps_uk[this_ixp]['fac_set'][0]
        # networks = pdb.fetch_all(resource.Network)
        
        # compares the current hop_asn with the networks list to discover the network number
        # using a file to stop interrogating RIPE too much, this then provides much info such as the netfac set
        
        if not this_hop['network']:
            
            
            for network,values in networks.items():
                if values['asn'] == hop_asn:
                        print(network,values,hop_asn)
                
                        print('The network exiting the IXP  is', network)
                        this_network = this_hop['network'] = networks[network]
                        #print('this_network,hop_asn',this_network,hop_asn)
                        #input('wait')
                        break
                # very strange anomaly doesnt work properly with 14061 so had to do this
                #elif values['asn'] == 14061:
                    #print('The network entering the IXP (asn 14061) is', network)
                    #this_network = this_hop[network] = networks[network]
                    #break
            
        else:
            this_network = networks[this_hop['network']]
        #print(this_network)
        #input('this')
        # this_network is now equal to example:-
        # {'id': 5320, 'org_id': 8217, 'name': 'Booking.com', 'aka': '', 'name_long': '', 
        # 'website': 'https://www.booking.com', 'asn': 43996, 'looking_glass': '', 'route_server': '',
        #  'irr_as_set': 'AS-BOOKING', 'info_type': 'Content', 'info_prefixes4': 100, 'info_prefixes6': 100,
        #  'info_traffic': '', 'info_ratio': 'Mostly Outbound', 'info_scope': 'Global', 'info_unicast': True, 
        # 'info_multicast': False, 'info_ipv6': True, 'info_never_via_route_servers': False, 'ix_count': 15, 
        # 'fac_count': 6, 'notes': 'A member of Booking Holdings www.bookingholdings.com.\n\nBooking.com also 
        # provides connectivity for www.rentalcars.com.', 'netixlan_updated': '2021-09-22T00:07:35.357068Z', 
        # 'netfac_updated': '2018-04-17T14:24:51Z', 'poc_updated': '2019-11-18T11:00:59Z', 'policy_url': '', 
        # 'policy_general': 'Open', 'policy_locations': 'Not Required', 'policy_ratio': False, 
        # 'policy_contracts': 'Not Required', 'netfac_set': [12836, 12837, 13600, 14890, 28000, 29000], 
        # 'netixlan_set': [15672, 17654, 17822, 20272, 23086, 23842, 23952, 23981, 27427, 42738, 42939, 43695, 
        # 45995, 45996, 47467], 'poc_set': [8906, 8907, 8988], 'allow_ixp_update': False, 'created': 
        # '2013-02-21T02:54:04Z', 'updated': '2018-06-25T13:15:29Z', 'status': 'ok'}

        print('probe_id is',probe_id)
        # print('Network',this_network['id'],'facilities are',this_network['netfac_set'])
        # input('wait')

        # try first of all getting the correct facility using the new facilities to ip address table
        this_fac = {}
        ixp_exit_point = []
        '''
        if this_hop['ip_from'] == '5.57.81.128':
            # this_fac = ix_detail_dict[this_hop['ip_from']]
            print(this_network['netfac_set'])
            input('wait')
        '''
        possible_exit_facility = [] 
        exit_netfac_ids = []
        ixp_exit_point = []
        ix_fac_flag = False
        

        
        try:
            print(this_hop)
            # if ipaddress belongs to Linx manchester theres only 3 facs and they are close together so
            # choose first fac
            if ipaddress.ip_address(this_hop['ip_from']) in ipaddress.ip_network('185.1.101.0/24'):
                this_fac = ix_detail_dict['185.1.101.28']
            else:
                this_fac = ix_detail_dict[this_hop['ip_from']]
            
            if this_fac:
        
                ix_fac_flag = True
                results['rule5.fac_to_ip_table']+=1
                if rname.casefold() in results['successes']['rule5.fac_to_ip_table']:
                    results['successes']['rule5.fac_to_ip_table'][this_hop['ip_from']] +=1 
                    results['successes']['rule5.fac_to_ip_table']['total'] +=1 
                else:
                    results['successes']['rule5.fac_to_ip_table'][this_hop['ip_from']] = 1
                    results['successes']['rule5.fac_to_ip_table']['total'] +=1 
            
        #print('FAC IS',this_fac)
            #input('wait')
        except:
            print('couldnt find a this_fac excepted',this_hop['ip_from'])
            results['rule5.fac_to_ip_table']+=1
            if rname.casefold() in results['failures']['rule5.fac_to_ip_table']:
                results['failures']['rule5.fac_to_ip_table'][this_hop['ip_from']] +=1 
                results['failures']['rule5.fac_to_ip_table']['total'] +=1 
            else:
                results['failures']['rule5.fac_to_ip_table'][this_hop['ip_from']] = 1
                results['failures']['rule5.fac_to_ip_table']['total'] +=1 
            # ok so its not in the ix_detail dict
            # try Getting the facilities where the network succeding the IXP peers by comparing the previous ASN peering points with 
            # this ASNs peering points and selecting the common facility

            #Note: dont forget the netfac_set is an intermediate number for the real facility codes
            print(this_network['netfac_set'])
            #input('wait this fac set')
            if this_network['netfac_set']:
                exit_netfac_ids = []
                
                # netfac is an intermediate number which points at the facitly and it is this facility number that we need
                # so lets search for all the facilities that the network peers at.
                for netfac in this_network['netfac_set']:
                    
                    # print('Network',this_network['id'],'facilities are',this_network['netfac_set'])
                    # print('this one is',netfac)
                    # netfac_info = pdb.fetch(resource.NetworkFacility, netfac)
                    # print('NETFAC INFO is', netfac_info[0])

                    con = sqlite3.connect("/home/paul/peeringdb.sqlite3")
                    cur = con.cursor()
                    print('NETFAC', netfac)
                    fac_id = (netfac,)
                    cur.execute("select * from peeringdb_network_facility where id = ?", fac_id)
                    data = cur.fetchone()
                    colnames = cur.description
                    #print(colnames)
                    #print('facility info is',data)
                    #print('NETFAC INFO is', data[9])
                    # input('wait')
                    exit_netfac_ids.append(data[9])  
                    # exit_netfac_ids.append(netfac_info[0]['fac_id'])  

                    # add JANET additional manually found facilities TODO why arnt these found ?
                    # print(exit_netfac_ids)
                    # input('wait')
                
                    if hop_asn == 786:
                        exit_netfac_ids.append(896) 
                        exit_netfac_ids.append(76)
                print('The ASN succeding the IXP is', hop_asn, ' and its facilites are', exit_netfac_ids)
                
                print('IXPs', this_ixp,'facilities are', ixp_facilities)

                
                #Choose the exit possible facilities which is shared between the exit network and the IXP
                
            for network_fac in exit_netfac_ids:
                for ixp_fac in ixp_facilities:
                    if network_fac == ixp_fac:
                        print ('this is the one', network_fac)
                        possible_exit_facility.append(network_fac)
                        print('possible exit facility is',possible_exit_facility)

                        
                        break
            print('POSSIBLE EXT FACILITY',possible_exit_facility)
            print('wait on exit facilities 1442')        
            if len(possible_exit_facility) == 1:
                this_fac['facility_number'] = possible_exit_facility[0]
                this_fac['Switch Port and VLAN'] =''
                this_fac['Port Type'] =''
                ix_fac_flag = True
                print('the exit facilility is',possible_exit_facility[0])
                results['rule5.common_fac']+=1
                if rname.casefold() in results['successes']['rule5.common_fac']:
                    results['successes']['rule5.common_fac'][rname.casefold()] +=1 
                    results['successes']['rule5.common_fac']['total'] +=1 
                else:
                    results['successes']['rule5.common_fac'][rname.casefold()] = 1
                    results['successes']['rule5.common_fac']['total'] +=1 
            
            # CREATE additional EXIT RULES HERE
            # if there are multiple shared facilities for the AS and the IX
            # Exit Rule 1
            # if list of possible exit facilities are all telehouse in london then just chose the initial one
            
            elif len(possible_exit_facility) > 1:
                print('greater than 1')
                telehouse_list = ['34','39','45','835']
                equinix_list = ['832', '3152']
                if all(x in telehouse_list for x in possible_exit_facility):
                    ixp_exit_point.append(telehouse_list[0])
                    print('all telehouse',ixp_exit_point) 
                    this_hop['facility'].append(ixp_exit_point)
                    this_hop['hop_latitude'] = facilitys_uk[str(telehouse_list[0])]['latitude']
                    this_hop['hop_longitude'] = facilitys_uk[str(telehouse_list[0])]['longitude']
                    this_fac['facility_number'] = telehouse_list[0]
                    this_fac['Switch Port and VLAN'] =''
                    this_fac['Port Type'] =''
                    ix_fac_flag = True
                    results[probe_id]['status'] = True 
                    results[probe_id]['status_reason'].append(probe_id+' All Telehouse so chose first one'+str(ixp_exit_point[0]))
                    results[probe_id]['status_code'] = 0
                    append_vptable_dict(2, this_hop['ip_from'],this_hop['hop_latitude'], this_hop['hop_longitude'],rname,this_hop['facility'],"","")
                    results['rule5']+=1
                    if rname.casefold() in results['successes']['rule5.common_fac']:
                        results['successes']['rule5.common_fac'][rname.casefold()] +=1 
                        results['successes']['rule5.common_fac']['total'] +=1 
                    else:
                        results['successes']['rule5.common_fac'][rname.casefold()] = 1
                        results['successes']['rule5.common_fac']['total'] +=1 
                # if list of possible exit facilities are all equinix in slough then just chose the initial one   
                elif all(x in equinix_list for x in possible_exit_facility):
                    ixp_exit_point.append(equinix_list[0])
                    print('all equinix',ixp_exit_point) 
                    this_hop['facility'].append(ixp_exit_point[0])
                    this_hop['hop_latitude'] = facilitys_uk[str(equinix_list[0])]['latitude']
                    this_hop['hop_longitude'] = facilitys_uk[str(equinix_list[0])]['longitude']
                    this_fac['facility_number'] = equinix_list[0]
                    this_fac['Switch Port and VLAN'] =''
                    this_fac['Port Type'] =''
                    ix_fac_flag = True
                    results[probe_id]['status'] = True 
                    results[probe_id]['status_reason'].append(probe_id+' All Equinix so chose first one'+ str(ixp_exit_point[0]))
                    results[probe_id]['status_code'] = 0
                    append_vptable_dict(2, this_hop['ip_from'],this_hop['hop_latitude'], this_hop['hop_longitude'],rname,this_hop['facility'],"","")
                    results['rule5']+=1
                    if rname.casefold() in results['successes']['rule5.common_fac']:
                        results['successes']['rule5.common_fac'][rname.casefold()] +=1 
                        results['successes']['rule5.common_fac']['total'] +=1 
                    else:
                        results['successes']['rule5.common_fac'][rname.casefold()] = 1
                        results['successes']['rule5.common_fac']['total'] +=1 
                    # if there are multiple shared facilities for the AS and the IX
                    # exit IX RULE 2
                    # if the exit and entrance are same 
                    '''
                    elif ixp_exit_point in possible_exit_facility:
                            # there is no entry point anymore so this will fail 
                            #ixp_exit_point = ixp_entry_point
                            this_hop['facility'].append(ixp_exit_point[0])
                            this_hop['hop_latitude'] = facilitys_uk[str(ixp_exit_point)]['latitude']
                            this_hop['hop_longitude'] = facilitys_uk[str(ixp_exit_point)]['longitude']
                            results[probe_id]['status'] = True 
                            results[probe_id]['status_reason'].append(probe_id+'Input and output are same'+str(ixp_exit_point[0]))
                            results[probe_id]['status_code'] = 7
                            append_vptable_dict(3, this_hop['ip_from'],this_hop['hop_latitude'], this_hop['hop_longitude'],rname,this_hop['facility'],this_hop['port'],this_hop['speed'])
                            
                            input('input and exit are the same')
                    '''
                else:
                    # if the list doesnt have all telehouse facilities then we need a rule here
                    print('ohoh no valid rule for this posissible exit list', possible_exit_facility) 
                    results[probe_id]['status'] = False
                    results[probe_id]['status_reason'].append('initial Facility used as no valid rule for the Facility EXIT list ' + str(possible_exit_facility))
                    results[probe_id]['status_code'] = 5
                    ixp_exit_point.append(possible_exit_facility[0])
                    this_hop['facility'].append(ixp_exit_point)
                    this_hop['hop_latitude'] = facilitys_uk[str(ixp_exit_point[0])]['latitude']
                    this_hop['hop_longitude'] = facilitys_uk[str(ixp_exit_point[0])]['longitude']
                    append_vptable_dict(5, this_hop['ip_from'],this_hop['hop_latitude'], this_hop['hop_longitude'],rname,this_hop['facility'],"","")
                    results['rule5.common_fac']+=1
                    if rname.casefold() in results['failures']['rule5.common_fac']:
                        results['failures']['rule5.common_fac'][rname.casefold()] +=1 
                        results['failures']['rule5.common_fac']['total'] +=1 
                    else:
                        results['failures']['rule5.common_fac'][rname.casefold()] = 1
                        results['failures']['rule5.common_fac']['total'] +=1 
                    #input('wait')
            
            
               
            else:
                #For some reason this one network (AVENSYS) does not have facilities listed on peeringdb
                if this_hop['ip_from'] == '195.66.226.35':
                    this_fac['facility_number'] = '34'
                    this_fac['Switch Port and VLAN'] =''
                    this_fac['Port Type'] =''
                    ix_fac_flag = True
                    print('ip was 195.66.226.35 belonging to avensys who do not seem to have any networks')
                    # input('wait')
                    results['rule5.common_fac']+=1
                    if rname.casefold() in results['successes']['rule5.common_fac']:
                        results['successes']['rule5.common_fac'][rname.casefold()] +=1 
                        results['successes']['rule5.common_fac']['total'] +=1 
                    else:
                        results['successes']['rule5.common_fac'][rname.casefold()] = 1
                        results['successes']['rule5.common_fac']['total'] +=1 
                else:
                    print(' didnt manager to get a facility from the ixp facility list')
                    print(' and this network has no facilities, unlikely but it may get here')
                    results['rule5.common_fac']+=1
                    if rname.casefold() in results['failures']['rule5.common_fac']:
                        results['failures']['rule5.common_fac'][rname.casefold()] +=1 
                        results['failures']['rule5.common_fac']['total'] +=1 
                    else:
                        results['failures']['rule5.common_fac'][rname.casefold()] = 1
                        results['failures']['rule5.common_fac']['total'] +=1 
                    print('wait 1644')
        
        # CONTINUE HERE IF WE MANAGE TO GET A Facility

        if ix_fac_flag == True:
            print( 'FACILITY =',str(this_fac))
        
            ixp_exit_point.append(this_fac['facility_number'])

            results[probe_id]['status'] = True 
            results[probe_id]['status_reason'].append(probe_id+' Exit Facility is '+str(ixp_exit_point[0]))
            results[probe_id]['status_code'] = 0
            this_hop['hop_latitude'] = facilitys_uk[str(ixp_exit_point[0])]['latitude']
            this_hop['hop_longitude'] = facilitys_uk[str(ixp_exit_point[0])]['longitude']
            this_hop['facility'].append(ixp_exit_point)
            this_hop['port'] = this_fac['Switch Port and VLAN']
            this_hop['speed'] = this_fac['Port Type']
            
            
            append_vptable_dict(2, this_hop['ip_from'],this_hop['hop_latitude'], this_hop['hop_longitude'],'',this_hop['facility'],this_hop['port'],this_hop['speed'])
            

        else: 
            print('ix fac flag is false')
            results[probe_id]['status'] = False
            results[probe_id]['status_reason'].append('common fac and fac-to ip table were both unable to find a exit facility ' )
            results[probe_id]['status_code']= 5
            
               
            ####################################################################
            #TODO NOW TRY Reverse DNS HERE
            # #############################################################

            ##############################################################################################

            # try to get the reverse DNS name, if none then just use the IX Number   
       
            try:
                    
                addr=reversename.from_address(this_hop['ip_from'])
                rname = str(resolver.resolve(addr,"PTR")[0])
            except:
                rname = 'IX:'+this_ixp
                this_hop['rdns'] = rname
               
                results['rule5.reverse_dns']+=1
                if rname.casefold() in results['failures']['rule5.reverse_dns']:
                    results['failures']['rule5.reverse_dns'][rname.casefold()] +=1 
                    results['failures']['rule5.reverse_dns']['total'] +=1 
                else:
                    results['failures']['rule5.reverse_dns'][rname.casefold()] = 1
                    results['failures']['rule5.reverse_dns']['total'] +=1
                append_vptable_dict(5, this_hop['ip_from'],0, 0,rname,'',port,speed) 
                
            else:
                print('RULE 5 This hops Reversedns name is',rname)
                try:
                    this_facility, rules = get_facilitys(rules,rname,this_hop)
                except:
                    coords =(0,0)
                    print('do a reverse traceroute because facilities are 0')
                    results['rule5.reverse_dns']+=1
                    
                    if rname.casefold() in results['failures']['rule5.reverse_dns']:
                        results['failures']['rule5.reverse_dns'][rname.casefold()] +=1 
                        results['failures']['rule5.reverse_dns']['total'] +=1 
                    else:
                        results['failures']['rule5.reverse_dns'][rname.casefold()] = 1
                        results['failures']['rule5.reverse_dns']['total'] +=1 
                    
                    append_vptable_dict(5, this_hop['ip_from'],0, 0,rname,'',port,speed)
                else:

                    if len(this_facility) == 0:
                        coords =(0,0)
                        print('do a reverse traceroute because facilities are 0')
                        results['rule5.reverse_dns']+=1
                        
                        if rname.casefold() in results['failures']['rule5.reverse_dns']:
                            results['failures']['rule5.reverse_dns'][rname.casefold()] +=1 
                            results['failures']['rule5.reverse_dns']['total'] +=1 
                        else:
                            results['failures']['rule5.reverse_dns'][rname.casefold()] = 1
                            results['failures']['rule5.reverse_dns']['total'] +=1 
                        
                        append_vptable_dict(5, this_hop['ip_from'],0, 0,rname,'',port,speed)
                        
                    if len(this_facility) == 1:
                        coords= (facilitys_uk[this_facility[0]]['longitude'],facilitys_uk[this_facility[0]]['latitude'])
                        lon = coords[0]
                        lat = coords[1]
                        print(this_hop['facility'],this_facility)
                        this_hop['facility'].append(this_facility)
                        print('*************************************************************************')
                        print(this_hop['facility'])
                        # input('wait')
                        this_hop['hop_longitude'] = lon
                        this_hop['hop_latitude'] = lat
                        append_vptable_dict(2, this_hop['ip_from'],this_hop['hop_latitude'], this_hop['hop_longitude'],rname,this_facility,port,speed)
                        
                        results['rule5.reverse_dns']+=1
                    
                        if rname.casefold() in results['successes']['rule5.reverse_dns']:
                            results['successes']['rule5.reverse_dns'][rname.casefold()] +=1 
                            results['successes']['rule5.reverse_dns']['total'] +=1 
                        else:
                            results['successes']['rule5.reverse_dns'][rname.casefold()] = 1
                            results['successes']['rule5.reverse_dns']['total'] +=1 
                    if len(this_facility) > 1:
                        coords=(0,0)
                        print ('Do a reverse_traceroute because faciltities are more than 1')
                        results['rule5.reverse_dns']+=1
                        if rname.casefold() in results['failures']['rule5.reverse_dns']:
                            results['failures']['rule5.reverse_dns'][rname.casefold()] +=1 
                            results['failures']['rule5.reverse_dns']['total'] +=1 
                        else:
                            results['failures']['rule5.reverse_dns'][rname.casefold()] = 1
                            results['failures']['rule5.reverse_dns']['total'] +=1 
                        append_vptable_dict(5, this_hop['ip_from'],0, 0,rname,'',port,speed)
                    ##############################################################################################

                    if len(this_facility) == 1:
                        lon = coords[0]
                        lat = coords[1]
                        this_hop['facility'].append(this_facility)
                        this_hop['network'] = 0
                        this_hop['hop_longitude'] = lon
                        this_hop['hop_latitude'] = lat
                        results[probe_id]['status'] = True
                        results[probe_id]['status_reason'].append('RULE 5 RDNS found the  exit facility ' )
                        results[probe_id]['status_code'] = 0
                        
                    else:
                        print(' RULE 5 found a rdns name but not a facility',rname,this_hop)
                        results[probe_id]['status'] = False
                        results[probe_id]['status_reason'].append('RULE 5 RDNS found a rdns name but Unable to find the  exit facility ' )
                        results[probe_id]['status_code'] = 5
                        append_vptable_dict(5, this_hop['ip_from'],this_hop['hop_latitude'], this_hop['hop_longitude'],rname,'',port,speed)
                        
                        
        print('RULE 5(IX) This hops Reversedns name is',rname)
        # input('wait')
        #print(results)

        #input('wait')
        # this_hop['hop_longitude'] = 500
        # this_hop['hop_latitude'] = 500
        
        
        '''
        # NOT SURE WHY I ADDED THIS
        
        # Rule 6 (for ixp) if all other rules are false then this is a valid ip to use REGEX to extract the town from the reverse DNS address
        # and find the location of that Ip address.
        if ix_prefix_flag == False and this_hop['ip_from'] != measurement[this_target] ["probe_ip"] :
            addr=reversename.from_address(this_hop['ip_from'])
            rname = str(resolver.resolve(addr,"PTR")[0])
            this_hop['rdns'] = rname
            print('Rule 6 for ixp This hops Reversedns name is',rname)
            lon, lat = get_coords(rname)
            this_hop['hop_longitude'] = lon
            this_hop['hop_latitude'] =  lat
        '''
        print('RULE5A')
        
        rules.append(5)


        #input('wait')
        
    # rule 6 if this ip address hasnt been picked up by any of the above rules then it probably just needs locating via its rdns
    if not rule_flag:
        rule = 6
        results['rule6'] +=1
        rule_flag = True
        rname = port = speed = ''
        print('ix_prefix_flag',hop,this_hop['ip_from'],ix_prefix_flag)
        


        
        #try:   
        addr=reversename.from_address(this_hop['ip_from'])
        
        try: 
            rname = str(resolver.resolve(addr,"PTR")[0])
        except:
            print(' RULE 6 couldnt find a  rdns name ',rname,this_hop)
            append_vptable_dict(5, this_hop['ip_from'],this_hop['hop_latitude'], this_hop['hop_longitude'],rname,this_hop['facility'],"","")
        
            results[probe_id]['status_code'] = 5
            results[probe_id]['status'] = False
            
            if rname.casefold() in results['failures']['rule6']:
                results['failures']['rule6'][rname.casefold()] +=1 
                results['failures']['rule6']['total'] +=1 
            else:
                results['failures']['rule6'][rname.casefold()] = 1
                results['failures']['rule6']['total'] +=1 
            
        else:
            print('rname passed',rname)
            print('Address, rname',addr,rname)
            print('RULE 6 This hops Reversedns name is',rname)
            this_facility, rules = get_facilitys(rules,rname,this_hop)
            if len(this_facility) == 0:
                coords =(0,0)
                print('do a reverse traceroute because facilities are 0')
                if rname.casefold() in results['failures']['reverse_tr']:
                    results['failures']['reverse_tr'][rname.casefold()] +=1 
                    results['failures']['reverse_tr']['total'] +=1 
                else:
                    results['failures']['reverse_tr'][rname.casefold()] = 1
                    results['failures']['reverse_tr']['total'] +=1 
                
                append_vptable_dict(5, this_hop['ip_from'],0, 0,rname,'',port,speed)
                
            if len(this_facility) == 1:
                coords= (facilitys_uk[this_facility[0]]['longitude'],facilitys_uk[this_facility[0]]['latitude'])
                lon = coords[0]
                lat = coords[1]
                print(this_hop['facility'],this_facility)
                this_hop['facility'].append(this_facility)
                print('*************************************************************************')
                print(this_hop['facility'])
                # input('wait')
                this_hop['hop_longitude'] = lon
                this_hop['hop_latitude'] = lat
                append_vptable_dict(2, this_hop['ip_from'],this_hop['hop_latitude'], this_hop['hop_longitude'],rname,this_facility,port,speed)
                results[probe_id]['status'] = True
                if rname.casefold() in results['successes']['rule1']:
                    results['successes']['rule1'][rname.casefold()] +=1 
                    results['successes']['rule1']['total'] +=1 
                else:
                    results['successes']['rule1'][rname.casefold()] = 1
                    results['successes']['rule1']['total'] +=1 
            if len(this_facility) > 1:
                coords=(0,0)
                print ('Do a reverse_traceroute because faciltities are more than 1')
                if rname.casefold() in results['failures']['reverse_tr']:
                    results['failures']['reverse_tr'][rname.casefold()] +=1 
                    results['failures']['reverse_tr']['total'] +=1 
                else:
                    results['failures']['reverse_tr'][rname.casefold()] = 1
                    results['failures']['reverse_tr']['total'] +=1 
                append_vptable_dict(5, this_hop['ip_from'],0, 0,rname,'',port,speed)
            
            '''
            print('this_facility passed',this_facility,coords,rule)
            if this_facility:
                lon = coords[0]
                lat = coords[1]
                this_hop['facility'].append(this_facility)
                print('RULE 6 ',this_hop['facility'])
                this_hop['network'] = 0
                this_hop['hop_longitude'] = lon
                this_hop['hop_latitude'] = lat
                append_vptable_dict(2, this_hop['ip_from'],this_hop['hop_latitude'], this_hop['hop_longitude'],rname,this_hop['facility'],"","")
                results[probe_id]['status_code'] = 2
                this_hop['rdns'] = rname
                if rname.casefold() in results['successes']['rule6']:
                    results['successes']['rule6'][rname.casefold()] +=1 
                    results['successes']['rule6']['total'] +=1 
                else:
                    results['successes']['rule6'][rname.casefold()] = 1
                    results['successes']['rule6']['total'] +=1 
                
                results[probe_id]['status'] = True
            else:
                this_hop['rdns'] = rname
                print('RULE 6 This hops Reversedns name is',rname)
                print(' RULE 6 found a rdns name but not a facility',rname,this_hop)
                append_vptable_dict(5, this_hop['ip_from'],this_hop['hop_latitude'], this_hop['hop_longitude'],rname,this_hop['facility'],"","")
                if rname.casefold() in results['failures']['rule6']:
                    results['failures']['rule6'][rname.casefold()] +=1 
                    results['failures']['rule6']['total'] +=1 
                else:
                    results['failures']['rule6'][rname.casefold()] = 1
                    results['failures']['rule6']['total'] +=1 
                    results[probe_id]['status_code'] = 5
                    results[probe_id]['status'] = False
            '''
        print('RULE6')
        
        
        
        
        rules.append(6)
        #input('wait')
        
    # Rule 7 there is no rule 7
    if rule_flag == False:
        print('ohoh new rule required')
        input('Doh wait')
        results[probe_id]['status'] = False
    print('END OF RULES')
    print('This Hop INFO', this_hop)
    print('prev_hop INFO', prev_hop)
    
   
    return this_hop, facilities_used, ixp_pre_hops,ixp_in_hops,ixp_post_hops,rules,ix_hop



def get_facilitys(rules,rname,this_hop):
    #takes a reverse DNS name and breaks it down to attempt to find a town name
    # it then finds the facilities in that town and returns a list of those facilities
    
    # coords = []
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
    #f= ''
    possible_facilitys = {}
    last_part = ''
    prev_last_part = ''
    skip_town_check = False # if this_part turns out to be only one possible facility then skip town check
    already_have_possible_facility = False # if we can work out from rdns what the facility is then no need to check towns
    skip_regex_check = False
    f=[]

    #scripts for publicinternet 
    if rname.casefold() == "gi2-0-1.lon-core-01.ip.pblin.net." or rname.casefold() == "gi0-0-0.lon-core-02.ip.pblin.net.":
        this_part= 'lon'
        fac ='34'
        f.append(fac) 
        possible_facilitys[this_part] = {}
        possible_facilitys[this_part][fac] ={}                                              
        possible_facilitys[this_part][fac]['lat'] = facilitys_uk[fac]['latitude']
        possible_facilitys[this_part][fac]['lon'] = facilitys_uk[fac]['longitude']
        possible_facilitys[this_part][fac]['town'] = 'London'
        possible_facilitys[this_part][fac]['org_id'] = facilitys_uk[fac]['org_id']
        possible_facilitys[this_part][fac]['networks'] = []
        possible_facilitys[this_part][fac]['networks'] = facilitys_uk[fac]['networks']
        coords = (possible_facilitys[this_part][fac]['lon'],possible_facilitys[this_part][fac]['lat'])
        skip_town_check = True
        skip_regex_check = True
        already_have_possible_facility = True
        print(possible_facilitys) 
        rules.append('get_coords pblin')
        results['regex'] +=1
        if rname.casefold() in results['successes']['regex']:
            results['successes']['regex'][rname.casefold()] +=1 
            results['successes']['regex']['total'] +=1 
        else:
            results['successes']['regex'][rname.casefold()] = 1
            results['successes']['regex']['total'] +=1 
        # end scripts for publicinternet

    #scripts for faelix.net
    if 'faelix.net.' in rname.casefold():
        rules.append('get_coords faelix')
            
        if 'dekker' in rname.casefold():
            this_part= 'lon'
            fac ='835'
            f.append(fac) 
            possible_facilitys[this_part] = {}
            possible_facilitys[this_part][fac] ={}                                              
            possible_facilitys[this_part][fac]['lat'] = facilitys_uk[fac]['latitude']
            possible_facilitys[this_part][fac]['lon'] = facilitys_uk[fac]['longitude']
            possible_facilitys[this_part][fac]['town'] = 'London'
            possible_facilitys[this_part][fac]['org_id'] = facilitys_uk[fac]['org_id']
            possible_facilitys[this_part][fac]['networks'] = []
            possible_facilitys[this_part][fac]['networks'] = facilitys_uk[fac]['networks']
            coords = (possible_facilitys[this_part][fac]['lon'],possible_facilitys[this_part][fac]['lat'])
            skip_town_check = True
            skip_regex_check = True
            already_have_possible_facility = True
            results['regex'] +=1
            if rname.casefold() in results['successes']['regex']:
                results['successes']['regex'][rname.casefold()] +=1 
                results['successes']['regex']['total'] +=1 
            else:
                results['successes']['regex'][rname.casefold()] = 1
                results['successes']['regex']['total'] +=1 
             
        if 'gunn' in rname.casefold():
            this_part= 'lon'
            fac ='46'
            f.append(fac) 
            possible_facilitys[this_part] = {}
            possible_facilitys[this_part][fac] ={}                                              
            possible_facilitys[this_part][fac]['lat'] = facilitys_uk[fac]['latitude']
            possible_facilitys[this_part][fac]['lon'] = facilitys_uk[fac]['longitude']
            possible_facilitys[this_part][fac]['town'] = 'London'
            possible_facilitys[this_part][fac]['org_id'] = facilitys_uk[fac]['org_id']
            possible_facilitys[this_part][fac]['networks'] = []
            possible_facilitys[this_part][fac]['networks'] = facilitys_uk[fac]['networks']
            coords = (possible_facilitys[this_part][fac]['lon'],possible_facilitys[this_part][fac]['lat'])
            skip_town_check = True
            skip_regex_check = True
            already_have_possible_facility = True
            results['regex'] +=1
            if rname.casefold() in results['successes']['regex']:
                results['successes']['regex'][rname.casefold()] +=1 
                results['successes']['regex']['total'] +=1 
            else:
                results['successes']['regex'][rname.casefold()] = 1
                results['successes']['regex']['total'] +=1 
            
        
        if 'aebi' in rname.casefold():
            this_part= 'man'
            fac ='78'
            f.append(fac) 
            possible_facilitys[this_part] = {}
            possible_facilitys[this_part][fac] ={}                                              
            possible_facilitys[this_part][fac]['lat'] = facilitys_uk[fac]['latitude']
            possible_facilitys[this_part][fac]['lon'] = facilitys_uk[fac]['longitude']
            possible_facilitys[this_part][fac]['town'] = 'Manchester'
            possible_facilitys[this_part][fac]['org_id'] = facilitys_uk[fac]['org_id']
            possible_facilitys[this_part][fac]['networks'] = []
            possible_facilitys[this_part][fac]['networks'] = facilitys_uk[fac]['networks']
            coords = (possible_facilitys[this_part][fac]['lon'],possible_facilitys[this_part][fac]['lat'])
            skip_town_check = True
            skip_regex_check = True
            already_have_possible_facility = True
            results['regex'] +=1
            if rname.casefold() in results['successes']['regex']:
                results['successes']['regex'][rname.casefold()] +=1 
                results['successes']['regex']['total'] +=1 
            else:
                results['successes']['regex'][rname.casefold()] = 1
                results['successes']['regex']['total'] +=1 

        
        if 'earhart' in rname.casefold():
            this_part= 'lon'
            fac ='34'
            f.append(fac) 
            possible_facilitys[this_part] = {}
            possible_facilitys[this_part][fac] ={}                                              
            possible_facilitys[this_part][fac]['lat'] = facilitys_uk[fac]['latitude']
            possible_facilitys[this_part][fac]['lon'] = facilitys_uk[fac]['longitude']
            possible_facilitys[this_part][fac]['town'] = 'London'
            possible_facilitys[this_part][fac]['org_id'] = facilitys_uk[fac]['org_id']
            possible_facilitys[this_part][fac]['networks'] = []
            possible_facilitys[this_part][fac]['networks'] = facilitys_uk[fac]['networks']
            coords = (possible_facilitys[this_part][fac]['lon'],possible_facilitys[this_part][fac]['lat'])
            skip_town_check = True
            skip_regex_check = True
            already_have_possible_facility = True
            results['regex'] +=1
            if rname.casefold() in results['successes']['regex']:
                results['successes']['regex'][rname.casefold()] +=1 
                results['successes']['regex']['total'] +=1 
            else:
                results['successes']['regex'][rname.casefold()] = 1
                results['successes']['regex']['total'] +=1 
        
        if 'coudreau' in rname.casefold():
            this_part= 'lon'
            fac ='46'
            f.append(fac) 
            possible_facilitys[this_part] = {}
            possible_facilitys[this_part][fac] ={}                                              
            possible_facilitys[this_part][fac]['lat'] = facilitys_uk[fac]['latitude']
            possible_facilitys[this_part][fac]['lon'] = facilitys_uk[fac]['longitude']
            possible_facilitys[this_part][fac]['town'] = 'London'
            possible_facilitys[this_part][fac]['org_id'] = facilitys_uk[fac]['org_id']
            possible_facilitys[this_part][fac]['networks'] = []
            possible_facilitys[this_part][fac]['networks'] = facilitys_uk[fac]['networks']
            coords = (possible_facilitys[this_part][fac]['lon'],possible_facilitys[this_part][fac]['lat'])
            skip_town_check = True
            skip_regex_check = True
            already_have_possible_facility = True
            results['regex'] +=1
            if rname.casefold() in results['successes']['regex']:
                results['successes']['regex'][rname.casefold()] +=1 
                results['successes']['regex']['total'] +=1 
            else:
                results['successes']['regex'][rname.casefold()] = 1
                results['successes']['regex']['total'] +=1 
        
        print(possible_facilitys)
        # end scripts for Faelix.net


    #Scripts for hurricane Electric  
    # HE only use 2 letters, setting all HE locations in London to same geocoordinates
    #  as there is not much difference between them, can split betwwen lon6 and lon2 etc
    # if ever find out where these are exactly

    if 'he.net.' in rname.casefold():
        if 'lon' in rname.casefold():
            this_part= 'lon'          
            fac = '45'
            f.append(fac) 
            possible_facilitys[this_part] = {}
            possible_facilitys[this_part][fac] ={}                                              
            possible_facilitys[this_part][fac]['lat'] = facilitys_uk[fac]['latitude']
            possible_facilitys[this_part][fac]['lon'] = facilitys_uk[fac]['longitude']
            possible_facilitys[this_part][fac]['town'] = 'London'
            possible_facilitys[this_part][fac]['org_id'] = facilitys_uk[fac]['org_id']
            possible_facilitys[this_part][fac]['networks'] = []
            possible_facilitys[this_part][fac]['networks'] = facilitys_uk[fac]['networks']
            coords = (possible_facilitys[this_part][fac]['lon'],possible_facilitys[this_part][fac]['lat'])
            skip_town_check = True
            skip_regex_check = True
            already_have_possible_facility = True
            rules.append('get_coords Hurricane Electric Equinix LD8 London)')
            results['regex'] +=1
            if rname.casefold() in results['successes']['regex']:
                results['successes']['regex'][rname.casefold()] +=1 
                results['successes']['regex']['total'] +=1 
            else:
                results['successes']['regex'][rname.casefold()] = 1
                results['successes']['regex']['total'] +=1 
    
    #Scripts for BT Telehouse
    if 'telehouse' in rname.casefold():
        this_part= 'lon'          
        fac = '34'
        f.append(fac) 
        possible_facilitys[this_part] = {}
        possible_facilitys[this_part][fac] ={}                                              
        possible_facilitys[this_part][fac]['lat'] = facilitys_uk[fac]['latitude']
        possible_facilitys[this_part][fac]['lon'] = facilitys_uk[fac]['longitude']
        possible_facilitys[this_part][fac]['town'] = 'London'
        possible_facilitys[this_part][fac]['org_id'] = facilitys_uk[fac]['org_id']
        possible_facilitys[this_part][fac]['networks'] = []
        possible_facilitys[this_part][fac]['networks'] = facilitys_uk[fac]['networks']
        coords = (possible_facilitys[this_part][fac]['lon'],possible_facilitys[this_part][fac]['lat'])
        skip_town_check = True
        skip_regex_check = True
        already_have_possible_facility = True
        rules.append('get_coords Bt at Telehouse)')
        results['regex'] +=1
        if rname.casefold() in results['successes']['regex']:
            results['successes']['regex'][rname.casefold()] +=1 
            results['successes']['regex']['total'] +=1 
        else:
            results['successes']['regex'][rname.casefold()] = 1
            results['successes']['regex']['total'] +=1 


    #Scripts for CDW 
    #  
    if rname.casefold() == "external-dcfw-cluster.uk.cdw.com.":
        this_part= 'lon'
        fac ='1793'
        f.append(fac) 
        possible_facilitys[this_part] = {}
        possible_facilitys[this_part][fac] ={}                                              
        possible_facilitys[this_part][fac]['lat'] = facilitys_uk[fac]['latitude']
        possible_facilitys[this_part][fac]['lon'] = facilitys_uk[fac]['longitude']
        possible_facilitys[this_part][fac]['town'] = 'London'
        possible_facilitys[this_part][fac]['org_id'] = facilitys_uk[fac]['org_id']
        possible_facilitys[this_part][fac]['networks'] = []
        possible_facilitys[this_part][fac]['networks'] = facilitys_uk[fac]['networks']
        coords = (possible_facilitys[this_part][fac]['lon'],possible_facilitys[this_part][fac]['lat'])
        skip_town_check = True
        skip_regex_check = True
        already_have_possible_facility = True
        print(possible_facilitys) 
        rules.append('get_coords cdw')
        results['regex'] +=1
        if rname.casefold() in results['successes']['regex']:
            results['successes']['regex'][rname.casefold()] +=1 
            results['successes']['regex']['total'] +=1 
        else:
            results['successes']['regex'][rname.casefold()] = 1
            results['successes']['regex']['total'] +=1 
        # end scripts for publicinternet


    '''
    f.append('34')
    this_hop['asn'] = 36236
    lon = -0.0031222276903634526
    lat = 51.511827346720686 
    #this_hop['facility'].append('34')
    this_hop['network'] = 0
    this_hop['hop_longitude'] = lon
    this_hop['hop_latitude'] = lat
    append_vptable_dict(2, this_hop['ip_from'],this_hop['hop_latitude'], this_hop['hop_longitude'],rname,this_hop['facility'],"","")
    results[probe_id]['status_code'] = 2
    
    results[probe_id]['status'] = True
    skip_town_check = True
    already_have_possible_facility = True
    '''
    if not skip_regex_check: 
        for this_rdns_partial_name in rdns_parts_list:
            '''
            example:-
            be-1-ibr01-drt-red
            uk
            cdw
            com
            '''
            
            
            rdns_partial_list = re.findall("[a-zA-Z]{3,}", this_rdns_partial_name)
            print(rdns_parts_list,this_rdns_partial_name,rdns_partial_list)

            


            
            for this_part in rdns_partial_list:
                ''' 
                example:-
                red
                '''
                this_part = this_part.casefold()
                print('this part is and rdns partial list is', this_part, rdns_partial_list)

                #insert REGEX PRE-RULES here
                if this_part == 'com':
                    continue
                if this_part == 'net':
                    continue
                if this_part == 'anycast':
                    continue
                if this_part == 'ptr':
                    continue
                if this_part == 'unassigned':
                    continue
                if this_part == 'compute':
                    continue
                if this_part == 'amazonaws':
                    continue
                '''
                if this_part == 'east':
                    break
                if this_part == 'north':
                    break
                if this_part == 'south':
                    break
                '''
                
                if this_part == 'twelve':
                    continue
                if this_part == 'drt':
                    continue
                if this_part == 'ibr':
                    continue
                if this_part == 'cust':
                    continue
                if this_part == 'cdw':
                    print('this was cdw',this_rdns_partial_name)
                    #input('wait')
                    continue
                #AQL are only in Leeds so 
                if last_part != 'lon' and this_part == 'aql':
                    this_part = 'leeds'

                #scripts for BT

                if this_part == 'faraday' or this_part== 'gia':
                    # TODO: im not completely happy with geolocating GIA here as it can appear
                    #  at both ends of the connection from faraday to the Internet Exchange facility (Interxion fac 46)
                    # but as they are so close together this geocoordiante will do for now. 
                    this_part= 'lon'
                    fac ='bt faraday London'
                    f.append(fac) 
                    possible_facilitys[this_part] = {}
                    possible_facilitys[this_part][fac] ={}                                              
                    possible_facilitys[this_part][fac]['lat'] = 51.511950
                    possible_facilitys[this_part][fac]['lon'] = -0.101645
                    possible_facilitys[this_part][fac]['town'] = 'London'
                    possible_facilitys[this_part][fac]['org_id'] = 384
                    possible_facilitys[this_part][fac]['networks'] = []
                    possible_facilitys[this_part][fac]['networks'] = 281
                    coords = (possible_facilitys[this_part][fac]['lon'],possible_facilitys[this_part][fac]['lat'])
                    skip_town_check = True
                    already_have_possible_facility = True
                    print(possible_facilitys)
                    rules.append('get_coords BT Faraday')
                    results['regex'] +=1
                    if rname.casefold() in results['successes']['regex']:
                        results['successes']['regex'][rname.casefold()] +=1 
                        results['successes']['regex']['total'] +=1 
                    else:
                        results['successes']['regex'][rname.casefold()] = 1
                        results['successes']['regex']['total'] +=1 
                    break  
                if this_part == 'colindale':
                    this_part= 'lon'
                    fac ='bt colindale London'
                    f.append(fac) 
                    possible_facilitys[this_part] = {}
                    possible_facilitys[this_part][fac] ={}                                              
                    possible_facilitys[this_part][fac]['lat'] = 51.58378
                    possible_facilitys[this_part][fac]['lon'] = -0.24646
                    possible_facilitys[this_part][fac]['town'] = 'London'
                    possible_facilitys[this_part][fac]['org_id'] = 384
                    possible_facilitys[this_part][fac]['networks'] = []
                    possible_facilitys[this_part][fac]['networks'] = 281
                    coords = (possible_facilitys[this_part][fac]['lon'],possible_facilitys[this_part][fac]['lat'])
                    skip_town_check = True
                    already_have_possible_facility = True
                    print(possible_facilitys)
                    rules.append('get_coords BT colindale')
                    results['regex'] +=1
                    if rname.casefold() in results['successes']['regex']:
                        results['successes']['regex'][rname.casefold()] +=1 
                        results['successes']['regex']['total'] +=1 
                    else:
                        results['successes']['regex'][rname.casefold()] = 1
                        results['successes']['regex']['total'] +=1
                if this_part == 'southbank':
                    this_part= 'lon'
                    fac ='bt southbank London'
                    f.append(fac) 
                    possible_facilitys[this_part] = {}
                    possible_facilitys[this_part][fac] ={}                                              
                    possible_facilitys[this_part][fac]['lat'] = 51.50547
                    possible_facilitys[this_part][fac]['lon'] = -0.105219
                    possible_facilitys[this_part][fac]['town'] = 'London'
                    possible_facilitys[this_part][fac]['org_id'] = 384
                    possible_facilitys[this_part][fac]['networks'] = []
                    possible_facilitys[this_part][fac]['networks'] = 281
                    coords = (possible_facilitys[this_part][fac]['lon'],possible_facilitys[this_part][fac]['lat'])
                    skip_town_check = True
                    already_have_possible_facility = True
                    print(possible_facilitys)
                    rules.append('get_coords BT Southbank')
                    results['regex'] +=1
                    if rname.casefold() in results['successes']['regex']:
                        results['successes']['regex'][rname.casefold()] +=1 
                        results['successes']['regex']['total'] +=1 
                    else:
                        results['successes']['regex'][rname.casefold()] = 1
                        results['successes']['regex']['total'] +=1
                if this_part == 'kingston':
                    fac ='bt kingston'
                    f.append(fac) 
                    possible_facilitys[this_part] = {}
                    possible_facilitys[this_part][fac] ={}                                              
                    possible_facilitys[this_part][fac]['lat'] = 51.41249999999999
                    possible_facilitys[this_part][fac]['lon'] = -0.29127
                    possible_facilitys[this_part][fac]['town'] = 'kingston'
                    possible_facilitys[this_part][fac]['org_id'] = 384
                    possible_facilitys[this_part][fac]['networks'] = []
                    possible_facilitys[this_part][fac]['networks'] = 281
                    coords = (possible_facilitys[this_part][fac]['lon'],possible_facilitys[this_part][fac]['lat'])
                    skip_town_check = True
                    already_have_possible_facility = True
                    print(possible_facilitys)
                    rules.append('get_coords BT Kingston')
                    results['regex'] +=1
                    if rname.casefold() in results['successes']['regex']:
                        results['successes']['regex'][rname.casefold()] +=1 
                        results['successes']['regex']['total'] +=1 
                    else:
                        results['successes']['regex'][rname.casefold()] = 1
                        results['successes']['regex']['total'] +=1
                # BT label some of their customer end points with the name of wherever the remote end is
                # so to avoid false positives we need to be very specific about whether this is a interface in Birmingham
                if this_part == 'ukcore':
                    if last_part == 'birmingham':
                        fac ='bt birmingham'
                        f.append(fac) 
                        possible_facilitys[this_part] = {}
                        possible_facilitys[this_part][fac] ={}                                              
                        possible_facilitys[this_part][fac]['lat'] = 52.483079
                        possible_facilitys[this_part][fac]['lon'] = -1.90519
                        possible_facilitys[this_part][fac]['town'] = 'birmingham'
                        possible_facilitys[this_part][fac]['org_id'] = 384
                        possible_facilitys[this_part][fac]['networks'] = []
                        possible_facilitys[this_part][fac]['networks'] = 281
                        coords = (possible_facilitys[this_part][fac]['lon'],possible_facilitys[this_part][fac]['lat'])
                        skip_town_check = True
                        already_have_possible_facility = True
                        print(possible_facilitys)
                        rules.append('get_coords BT Birmingham')
                        results['regex'] +=1
                        if rname.casefold() in results['successes']['regex']:
                            results['successes']['regex'][rname.casefold()] +=1 
                            results['successes']['regex']['total'] +=1 
                        else:
                            results['successes']['regex'][rname.casefold()] = 1
                            results['successes']['regex']['total'] +=1
                    
                if this_part == 'telehouse':
                    fac ='34'
                    f.append(fac) 
                    possible_facilitys[this_part] = {}
                    possible_facilitys[this_part][fac] ={}                                              
                    possible_facilitys[this_part][fac]['lat'] = 52.483079
                    possible_facilitys[this_part][fac]['lon'] = -1.90519
                    possible_facilitys[this_part][fac]['town'] = 'London'
                    possible_facilitys[this_part][fac]['org_id'] = 384
                    possible_facilitys[this_part][fac]['networks'] = []
                    possible_facilitys[this_part][fac]['networks'] = 281
                    coords = (possible_facilitys[this_part][fac]['lon'],possible_facilitys[this_part][fac]['lat'])
                    skip_town_check = True  
                    already_have_possible_facility = True
                    print(possible_facilitys)
                    rules.append('get_coords BT telehouse lon fac 34')
                    results['regex'] +=1
                    if rname.casefold() in results['successes']['regex']:
                        results['successes']['regex'][rname.casefold()] +=1 
                        results['successes']['regex']['total'] +=1 
                    else:
                        results['successes']['regex'][rname.casefold()] = 1
                        results['successes']['regex']['total'] +=1
                # Scripts for Amazon AWS locations
                if this_part == 'west':
                    print(this_part,this_rdns_partial_name)
                    print(possible_facilitys)
                    # input('wait')
                    if this_rdns_partial_name == 'eu-west-2':
                        # input('wait written purely for amazon aws if any other need to rethink')
                        this_part= 'lon'
                        fac ='40'
                        f.append(fac) 
                        possible_facilitys[this_part] = {}
                        possible_facilitys[this_part][fac] ={}                                              
                        possible_facilitys[this_part][fac]['lat'] = facilitys_uk[fac]['latitude']
                        possible_facilitys[this_part][fac]['lon'] = facilitys_uk[fac]['longitude']
                        possible_facilitys[this_part][fac]['town'] = 'London'
                        possible_facilitys[this_part][fac]['org_id'] = facilitys_uk[fac]['org_id']
                        possible_facilitys[this_part][fac]['networks'] = []
                        possible_facilitys[this_part][fac]['networks'] = facilitys_uk[fac]['networks']
                        coords = (possible_facilitys[this_part][fac]['lon'],possible_facilitys[this_part][fac]['lat'])
                        skip_town_check = True
                        already_have_possible_facility = True
                        print(possible_facilitys)
                        rules.append('get_coords AWS')
                        results['regex'] +=1
                        if rname.casefold() in results['successes']['regex']:
                            results['successes']['regex'][rname.casefold()] +=1 
                            results['successes']['regex']['total'] +=1 
                        else:
                            results['successes']['regex'][rname.casefold()] = 1
                            results['successes']['regex']['total'] +=1 
                             
            
                        # input('wait')
                        break           
                if this_part == 'compute':
                    continue; 
                if this_part == 'amazonaws':
                    continue;
                # end scripts for amazonaws

                #script for level3.net now aka Lumen (they have a manchester in the USA)
                # Lumen in london used EQUINIX LD1 but that is no longer operational
                # looks like they are using telehouse north now 
                # lumen in Manchester  uses Equinix MA1 MA2 MA3 and all are also very close
                print('This part is', this_part,'prev_part is',last_part)
                if this_part == 'manchesteruk':
                    # Lumen have a manchester in the USA
                    this_part = 'manchester'
                print('This part is', this_part,'prev_part is',last_part)
                if this_part == 'level':
                    if last_part == 'london':
                        fac = '34'
                        f.append(fac) 
                        possible_facilitys[this_part] = {}
                        possible_facilitys[this_part][fac] ={}                                              
                        possible_facilitys[this_part][fac]['lat'] = facilitys_uk[fac]['latitude']
                        possible_facilitys[this_part][fac]['lon'] = facilitys_uk[fac]['longitude']
                        possible_facilitys[this_part][fac]['town'] = 'London'
                        possible_facilitys[this_part][fac]['org_id'] = facilitys_uk[fac]['org_id']
                        possible_facilitys[this_part][fac]['networks'] = []
                        possible_facilitys[this_part][fac]['networks'] = facilitys_uk[fac]['networks']
                        coords = (possible_facilitys[this_part][fac]['lon'],possible_facilitys[this_part][fac]['lat'])
                        skip_town_check = True
                        already_have_possible_facility = True
                        print(possible_facilitys)
                        rules.append('get_coords Lumen London (level3)')
                        results['regex'] +=1
                        if rname.casefold() in results['successes']['regex']:
                            results['successes']['regex'][rname.casefold()] +=1 
                            results['successes']['regex']['total'] +=1 
                        else:
                            results['successes']['regex'][rname.casefold()] = 1
                            results['successes']['regex']['total'] +=1 
                             
                        break
                    if last_part == 'manchester':
                        fac = '76'
                        f.append(fac) 
                        possible_facilitys[this_part] = {}
                        possible_facilitys[this_part][fac] ={}                                              
                        possible_facilitys[this_part][fac]['lat'] = facilitys_uk[fac]['latitude']
                        possible_facilitys[this_part][fac]['lon'] = facilitys_uk[fac]['longitude']
                        possible_facilitys[this_part][fac]['town'] = 'Manchester'
                        possible_facilitys[this_part][fac]['org_id'] = facilitys_uk[fac]['org_id']
                        possible_facilitys[this_part][fac]['networks'] = []
                        possible_facilitys[this_part][fac]['networks'] = facilitys_uk[fac]['networks']
                        coords = (possible_facilitys[this_part][fac]['lon'],possible_facilitys[this_part][fac]['lat'])
                        skip_town_check = True
                        already_have_possible_facility = True
                        print(possible_facilitys)
                        rules.append('get_coords Lumen Manchester (level3)')
                        results['regex'] +=1
                        if rname.casefold() in results['successes']['regex']:
                            results['successes']['regex'][rname.casefold()] +=1 
                            results['successes']['regex']['total'] +=1 
                        else:
                            results['successes']['regex'][rname.casefold()] = 1
                            results['successes']['regex']['total'] +=1 
                        break

                







                
                # print(possible_facilitys)
                # input('wait')

                    

                # now lets search each town to see if it starts with 'this_part' 
                print(skip_town_check)
                #input('skip town')
                if skip_town_check == False:
                    print('the part to be checked by the town is', this_part)
                    #list of possible facilities
                    possible_facilitys[this_part] = {}
                
                    for town in townset:
                        print(town,this_part)
                        town_lower = town.casefold()
                        this_part_lower = this_part.casefold()
                        if town_lower.startswith(this_part_lower):
                            
                            print(town, this_part,coords)
                            # if town does start with 'this_part' get a list of facilities in that town
                            for fac in facilitys_uk:
                                    
                                
                                if facilitys_uk[fac]['city'] == town:
                                    
                                    print(fac,town)
                                    print(facilitys_uk[fac]['latitude'])
                                    print(facilitys_uk[fac]['longitude'])
                                    possible_facilitys[this_part][fac] ={}
                                    
                                    
                                    possible_facilitys[this_part][fac]['lat'] = facilitys_uk[fac]['latitude']
                                    possible_facilitys[this_part][fac]['lon'] = facilitys_uk[fac]['longitude']
                                    possible_facilitys[this_part][fac]['town'] = town
                                    possible_facilitys[this_part][fac]['org_id'] = facilitys_uk[fac]['org_id']
                                    possible_facilitys[this_part][fac]['networks'] = []
                                    possible_facilitys[this_part][fac]['networks'] = facilitys_uk[fac]['networks']
        
                    
                    prev_last_part = last_part
                    last_part = this_part

    # now we have to work out which is the correct facility and what the coords of them are
    # we do this by comparing which of the possible facilitys in the relevant town peer with the last ASNs network
    
    if not already_have_possible_facility:
        print ('possible facilities are',possible_facilitys)
        
        for part in possible_facilitys:
            
            # if part is not empty
            if possible_facilitys[part]: 
                # find the network
                if len(possible_facilitys[part]) == 1:
                    
                    facil = list(possible_facilitys[part].keys())[0]
                    #print('Length of possible facilitties =1',facil)
                    f.append(facil)
                    #input('wait 2560')
                else:
                    for facil in possible_facilitys[part]:
                        i = 1
                        for asn in possible_facilitys[part][facil]['networks']:
                            # facilitys_uk[fac]['networks'] consists of a network,asn tuple, we are only intereted in the asn
                            i += 1
                            if i ==2:
                                i = 0
                                continue
                            print('ASN is',asn, this_hop['asn'])
                            
                            #input('wait')
                            
                            
                            if asn == this_hop['asn']:
                                print('Possible Facility is', possible_facilitys[part])
                                #input('wait')
                                coords = (possible_facilitys[part][facil]['lon'],possible_facilitys[part][facil]['lat'])
                                f.append(facil) 
                                rules.append('get_coords REGEX')
                            
                
                                
                                break
                        
    # POST processing REGEX, 
    
    if len(f) > 1:
        print(' We need to figure out which of these facilities is the correct one', f)
        #*******************************************************************
        # This is where a reverse traceroute will come in handy
        #*********************************************************************

        # if both are in Leeds then we can select the Salem Church one (896) as they are failrly close together geographically
        # TODO: this may be a problem later as fac 2384 (aql DC5, Leeds) is mainly used by JISC, perhaps we can check for the JISC ASN
        # and then select 2384 instead

        leeds_list = ['896','2384']
        manchester_list = ['601','1054']
        london_list = ['34', '39', '45', '835']
        london2_list = ['39', '45', '46']
        london3_list = ['34','418']

        equinix_list = ['832', '3152']
        ext_london_list = ['34', '45', '46', '254', '352', '398', '534', '1934']
        ext_manchester_list = ['76','78','601']
        large_london_ger_list =['34','39','40','43','45','46','47','48','79','352','354','398','534','835','1547']
        small_london_list =['34','79']
        iomart_list=['34','45','428']

        if all(x in large_london_ger_list for x in f):
            f= f[0]
            print('F is',f)
            #input('wait 2606')
            results['regex'] +=1
            if rname.casefold() in results['successes']['regex']:
                results['successes']['regex'][rname.casefold()] +=1 
                results['successes']['regex']['total'] +=1 
            else:
                results['successes']['regex'][rname.casefold()] = 1
                results['successes']['regex']['total'] +=1 
        elif all(x in small_london_list for x in f):
            f= f[0]
            print('F is',f)
            #input('wait 2606')
            results['regex'] +=1
            if rname.casefold() in results['successes']['regex']:
                results['successes']['regex'][rname.casefold()] +=1 
                results['successes']['regex']['total'] +=1 
            else:
                results['successes']['regex'][rname.casefold()] = 1
                results['successes']['regex']['total'] +=1 
        elif all(x in iomart_list for x in f):
            f= f[0]
            print('F is',f)
            #input('wait 2606')
            results['regex'] +=1
            if rname.casefold() in results['successes']['regex']:
                results['successes']['regex'][rname.casefold()] +=1 
                results['successes']['regex']['total'] +=1 
            else:
                results['successes']['regex'][rname.casefold()] = 1
                results['successes']['regex']['total'] +=1 

        elif all(x in leeds_list for x in f):
       
            print('Both in leeds so removing 2384')
            #f.clear()
            #f = [x]

            #f.remove('2384')
            f= f[0]
            print('F is',f)
            #input('wait 2606')
            results['regex'] +=1
            if rname.casefold() in results['successes']['regex']:
                results['successes']['regex'][rname.casefold()] +=1 
                results['successes']['regex']['total'] +=1 
            else:
                results['successes']['regex'][rname.casefold()] = 1
                results['successes']['regex']['total'] +=1 
        elif all(x in manchester_list for x in f):
            print('Both in manchester so removing 1054')
            #f.clear()
            #f = [x]
            '''
            f.remove('1054')
            '''
            f= f[0]
            print('F is',f)
            #input('wait 2636')
            
            results['regex'] +=1
            if rname.casefold() in results['successes']['regex']:
                results['successes']['regex'][rname.casefold()] +=1 
                results['successes']['regex']['total'] +=1 
            else:
                results['successes']['regex'][rname.casefold()] = 1
                results['successes']['regex']['total'] +=1 
        elif all(x in london_list for x in f):
            #f.clear()
            #f = [x]
            print('all in london so removing 39,45,835')
            '''
            f.remove('39')
            f.remove('45')
            f.remove('835')
            '''
            f= f[0]
            print('F is',f)
            #input('wait 2606')
            results['regex'] +=1
            if rname.casefold() in results['successes']['regex']:
                results['successes']['regex'][rname.casefold()] +=1 
                results['successes']['regex']['total'] +=1 
            else:
                results['successes']['regex'][rname.casefold()] = 1
                results['successes']['regex']['total'] +=1 
        elif all(x in london2_list for x in f):
            #f.clear()
            #f = [x]
            '''
            print('all in london2 so removing 46,45')
            f.remove('46')
            f.remove('45')
            '''
            
            f= f[0]
            print('F is',f)
            #input('wait 2606')
            results['regex'] +=1
            if rname.casefold() in results['successes']['regex']:
                results['successes']['regex'][rname.casefold()] +=1 
                results['successes']['regex']['total'] +=1 
            else:
                results['successes']['regex'][rname.casefold()] = 1
                results['successes']['regex']['total'] +=1 
        elif all(x in london3_list for x in f):
            print('all in london3 so removing 418')
            
          
            
            f= f[0]
            print('F is',f)
            #input('wait 2606')
            results['regex'] +=1
            if rname.casefold() in results['successes']['regex']:
                results['successes']['regex'][rname.casefold()] +=1 
                results['successes']['regex']['total'] +=1 
            else:
                results['successes']['regex'][rname.casefold()] = 1
                results['successes']['regex']['total'] +=1 
        elif all(x in equinix_list for x in f):
            # print('all in slough so removing 3152')
            
            
            f= f[0]
            print('F is',f)
            #input('wait 2606')
            results['regex'] +=1
            if rname.casefold() in results['successes']['regex']:
                results['successes']['regex'][rname.casefold()] +=1 
                results['successes']['regex']['total'] +=1 
            else:
                results['successes']['regex'][rname.casefold()] = 1
                results['successes']['regex']['total'] +=1 
        elif all(x in ext_london_list for x in f):
            print('all in extended london so removing all the others to just leave 34')
            #f.clear()
            #f = [x]
            '''
            f.remove('254')
            f.remove('45')
            f.remove('46')
            f.remove('398')
            f.remove('352')
            f.remove('534')
            f.remove('1934')
            '''
            f= f[0]
            print('F is',f)
            #input('wait 2606')
            results['regex'] +=1
            if rname.casefold() in results['successes']['regex']:
                results['successes']['regex'][rname.casefold()] +=1 
                results['successes']['regex']['total'] +=1 
            else:
                results['successes']['regex'][rname.casefold()] = 1
                results['successes']['regex']['total'] +=1 
        elif all(x in ext_london_list for x in f):
            print('all in extended london so removing all the others to just leave 34')
            #f.clear()
            #f = [x]
            '''
            f.remove('254')
            f.remove('45')
            f.remove('46')
            f.remove('398')
            f.remove('352')
            f.remove('534')
            f.remove('1934')
            '''
            f= f[0]
            print('F is',f)
            #input('wait 2606')
            results['regex'] +=1
            if rname.casefold() in results['successes']['regex']:
                results['successes']['regex'][rname.casefold()] +=1 
                results['successes']['regex']['total'] +=1 
            else:
                results['successes']['regex'][rname.casefold()] = 1
                results['successes']['regex']['total'] +=1 
        elif all(x in ext_manchester_list for x in f):
       
            print('all in manchester so removing 78,601 ')
            #f.clear()
            #f = [x]
            '''
            f.remove('78')
            f.remove('601')
            '''
            f= f[0]
            print('F is',f)
            #input('wait 2606')
            results['regex'] +=1
            if rname.casefold() in results['successes']['regex']:
                results['successes']['regex'][rname.casefold()] +=1 
                results['successes']['regex']['total'] +=1 
            else:
                results['successes']['regex'][rname.casefold()] = 1
                results['successes']['regex']['total'] +=1
        else:
            results['regex'] +=1
            # even though it found multiple facilities, REGEX was a success in that it found some
            if rname.casefold() in results['successes']['regex']:
                results['successes']['regex'][rname.casefold()] +=1 
                results['successes']['regex']['total'] +=1 
            else:
                results['successes']['regex'][rname.casefold()] = 1
                results['successes']['regex']['total'] +=1 
            
            print ('Facilities are',f )
            print('multiple facilities found')
    elif len(f) == 0:
        
        results['regex'] +=1
        if rname.casefold() in results['failures']['regex']:
            results['failures']['regex'][rname.casefold()] +=1 
            results['failures']['regex']['total'] +=1 
        else:
            results['failures']['regex'][rname.casefold()] = 1
            results['failures']['regex']['total'] +=1 
        # input('No facilities found')
    else:
        
        print('facilities are ',f)
    
        results['regex'] +=1
        if rname.casefold() in results['successes']['regex']:
            results['successes']['regex'][rname.casefold()] +=1 
            results['successes']['regex']['total'] +=1 
        else:
            results['successes']['regex'][rname.casefold()] = 1
            results['successes']['regex']['total'] +=1 
        
        #input('WOOT, wait')


        
                            
    return f,rules


def post_regex(rname,f):
   
                        
    # input('REVERSE Traceroute required here to discover which of the facilities is the correct one')
    # TODO: DONE ...... reverse_traceroute(target, probe_id)
    print('Trying reverse measurement') 
    this_measurement= my_measurements[probe_id]['measurement']
    print('The measurement is', this_target,probe_id,this_measurement)
    print('my_measurements is',my_measurements)
    
    #===============================================================================
    # TODO: whilst testing individual targets I need full access to all emasurments in case I need
    # todo a reverse dns but this will not be required later so can change it back to just measurements
    reverse_measurment = full_measurements[str(this_measurement)]['results'][this_target]
    print('The reverse_measurment is ', reverse_measurment)
    #==================================================================================
    print('trying a reverse traceroute where facilities > 1 line 2200')
    this_fac,this_hop['rdns'],rules,ix_prefix_flag,ix_hop,this_ixp = reverse_traceroute(rules,this_target,probe_id,reverse_measurment,this_hop['rdns'],rule,1,max_hop)
    print(this_fac)
    print('reverse traceroute where there are multiple facilitiesin the get_coords')
    
    if this_fac:
        print('F is currently,',f)
        
        # f.append(this_fac)
        print(facilitys_uk[f[0]])
        # input('wait')
        coords = (facilitys_uk[f[0]]['longitude'],facilitys_uk[f[0]]['latitude'])
        print('coords are',f[0],coords)
        results[probe_id]['status'] = True 
        results[probe_id]['status_reason'] =[]
        results[probe_id]['status_reason'].append(probe_id+' Exit Facility is '+f[0])
        results[probe_id]['status_code'] = 0
        results['reverse_tr'] +=1
        if rname.casefold() in results['successes']['reverse_tr']:
            results['successes']['reverse_tr'][rname.casefold()] +=1 
            results['successes']['reverse_tr']['total'] +=1 
        else:
            results['successes']['reverse_tr'][rname.casefold()] = 1
            results['successes']['reverse_tr']['total'] +=1 


        # input('wait')
    else:
        results[probe_id]['status'] = False
        print('even with reverse traceroute, still cant find the correct fac')
        results['reverse_tr'] +=1
        if rname.casefold() in results['failures']['reverse_tr']:
            results['failures']['reverse_tr'][rname.casefold()] +=1 
            results['failures']['reverse_tr']['total'] +=1 
        else:
            results['failures']['reverse_tr'][rname.casefold()] = 1
            results['failures']['reverse_tr']['total'] +=1 

        
        # input('wait')


    if this_hop['id'] == '1':
        #input('couldnt get it via regex or reverse_tr but this is hop1 . .')
        # TODO might be worth carrying out a RTT check less than .5 to ensure gateway is local
        print(' facility not found but this is hop 1 so set to same location as probe')
        #will be set by the get_location function
        
        this_hop['hop_latitude']= prev_hop['hop_latitude']
        this_hop['hop_longitude']= prev_hop['hop_longitude']
        coords = (this_hop['hop_longitude'],this_hop['hop_latitude'])
        '''
        if rname.casefold() in results['successes']['regex']:
            results['successes']['regex'][rname.casefold()] +=1 
            results['successes']['regex']['total'] +=1 
        else:
            results['successes']['regex'][rname.casefold()] = 1
                results['successes']['regex']['total'] +=1 
        '''
    else:
        #===============================================================================
        # TODO: whilst testing individual targets I need full access to all emasurments in case I need
        # todo a reverse dns but this will not be required later so can change it back to just measurements
        print('Trying reverse measurement')
        this_measurement= my_measurements[probe_id]['measurement']
        print(probe_id, this_target, this_measurement)
        reverse_measurment = full_measurements[str(this_measurement)]['results'][this_target]
        print('The source_measurment is ', reverse_measurment)
        #==================================================================================
        print('max hop is',max_hop,'ix_hop is',ix_hop)
        print('trying a reverse traceroute where facilities = 0 line 2278')
        this_fac,this_hop['rdns'],rules,ix_prefix_flag,ix_hop,this_ixp = reverse_traceroute(rules,this_target,probe_id,reverse_measurment,this_hop['rdns'],rule,1,max_hop)
        print(this_fac)
        print('wait 3017')
    
    if this_fac:
        print('F is currently,',f)
        
        f.append(str(this_fac))
        print(facilitys_uk[f[0]])
        # input('wait')
        coords = (facilitys_uk[f[0]]['longitude'],facilitys_uk[f[0]]['latitude'])
        print('coords are',f[0],coords)
        results[probe_id]['status'] = True 
        results[probe_id]['status_reason'] =[]
        results[probe_id]['status_reason'].append(probe_id+' Exit Facility is '+f[0])
        results[probe_id]['status_code'] = 0
        results['reverse_tr'] +=1
        if rname.casefold() in results['successes']['reverse_tr']:
            results['successes']['reverse_tr'][rname.casefold()] +=1 
            results['successes']['reverse_tr']['total'] +=1 
        else:
            results['successes']['reverse_tr'][rname.casefold()] = 1
            results['successes']['reverse_tr']['total'] +=1 
    else:
        print('No possible facilities even after regex and reverse traceroute need to look at this')
        results[probe_id]['status'] = False
        print(probe_id,this_hop)
        results['reverse_tr'] +=1
        if rname.casefold() in results['failures']['reverse_tr']:
            results['failures']['reverse_tr'][rname.casefold()] +=1 
            results['failures']['reverse_tr']['total'] +=1 
        else:
            results['failures']['reverse_tr'][rname.casefold()] = 1
            results['failures']['reverse_tr']['total'] +=1
        
        # input('wait')
        

def main(argv):
    in_file = ''
    out_file = ''
    
    try:
        opts, args = getopt.getopt(argv,"hi:o:",["ifile=","ofile="])
    except getopt.GetoptError:
        print('test.py -i <inputfile> -o <outputfile>')
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print('test.py -i <inputfile> -o <outputfile>')
            sys.exit()
        elif opt in ("-i", "--ifile"):
            in_file = arg
        elif opt in ("-o", "--ofile"):
            out_file = arg
    if out_file == '':
        out_file = 'results/tables/'+'resultslatest.json'
        #out_file = 'results/tables/'+'results.json'
    else:
        out_file = 'results/tables/'+out_file
    if in_file == '':
        # in_file = 'results/targetsfull.json'
        #in_file = 'results/target_6087.json'
        #in_file = 'results/targetsfull.json'
        in_file = 'results/targetslatest.json'
        #in_file = 'bttest_reverse.json'
    else:
        in_file= 'results/'+in_file

    #===================================================================================
    # whilst testing individual target probes I need access to the full list of measurments
    # in case I need to do reverse dns but this can be removed eventually
    global full_measurements
    with open('results/targetslatest.json') as f:
        full_measurements = json.load(f)
    #====================================================================
    print('Input file is ?', in_file)
    print('Output file is ?', out_file)
    input('wait')


    # create an ip to asn lookup file which will store succesful lookups from arin and RIPE 
    # so that we do  not use all the permitted number of enquiries in one day.
    global asn_to_ip_data
    asn_to_ip_data = read_asn_to_ip_json()

    # load the list of measurments that were created on RIPE for use when a reverse traceroute is needed
    global my_measurements   #, my_targets
    # with open('measurements/ukfull1_measurements.json') as f:
    with open('latest_measures.json') as f:
        #with open('measurements/uk_measurements_1.json') as f:
        my_measurements = json.load(f)
    # load the list of targets that were created on RIPE for use when a reverse traceroute is needed   
    #with open('results/targets.json') as f:
        #my_targets = json.load(f)
    


    # Create the Vantage Point table
    # 
    
    global vptable_dict
    vptable_dict = {}
    
    
    #input('wait')
    global ripe
    ripe = prsw.RIPEstat()

    
    #read in the validation data from CAIDA
    '''
    valid_domains = {}
    with open('caida.jsonl','r') as json_file:
        json_list = list(json_file)
    i = 0
    for json_str in json_list:
        result = json.loads(json_str)
        #print(f"result: {result}")
        #print(isinstance(result, dict))
        
        for locations in [result['geohints']]:
            #print('locations are',i,locations)
            for n in locations:
                #this_location = locations[0]
                #print('this is',n)
                if 'location' in n:
                    #print('cc is', n['location']['cc'])
                    cc = n['location']['cc']
                    if cc == 'GB':
                        valid_domains[result['domain']] ={}
                        valid_domains[result['domain']]['lat'] = n['lat']
                        valid_domains[result['domain']]['lon'] = n['lng']
                        valid_domains[result['domain']]['city'] = n['location']['place']
                        #print('VALID DOMAINS ARE', valid_domains)
                        i+=1
                       
    with open('validation.json','w') as f:
        json.dump(valid_domains, f) 
    print('I is',i)    
    input('wait')
            
    '''

    

        




    
    global facilitys_uk
    # Read in the UK Facilities records
    with open('peeringdb_test_results/uk_facilities_to_networks_good.json') as f:
        facilitys_uk = json.load(f)

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

    facilitys_uk['4463'] = {}
    facilitys_uk['4463']["org_id"] = 2103
    facilitys_uk['4463']["name"] = 'Netnorth Ltd'
    facilitys_uk['4463']["address1"] = "Unit 7 Queensbrook" 
    facilitys_uk['4463']["address2" ] = "Bolton Technology Exchange, Spa Rd"
    facilitys_uk['4463']["city"] =  "Bolton"
    facilitys_uk['4463']["country"] = "GB"
    facilitys_uk['4463']["postcode"] = "BL1 4AY"
    facilitys_uk['4463']["latitude"] = 50.681852 
    facilitys_uk['4463']["longitude"] = -2.256535
    facilitys_uk['4463']["networks"] = [14737, 205402, 2356, 25376]


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

    facilitys_uk['8078']["latitude"] = 53.585077, -2.526218
    
    fac ='bt faraday London'
    facilitys_uk[fac] ={}                                              
    facilitys_uk[fac]['latitude'] = 51.511950
    facilitys_uk[fac]['longitude'] = -0.101645
    facilitys_uk[fac]['city'] = 'London'
    facilitys_uk[fac]['org_id'] = 384
    facilitys_uk[fac]['networks'] = [281]

    fac ='bt colindale London'
    facilitys_uk[fac] ={}                                              
    facilitys_uk[fac]['latitude'] = 51.58378
    facilitys_uk[fac]['longitude'] = -0.24646
    facilitys_uk[fac]['city'] = 'London'
    facilitys_uk[fac]['org_id'] = 384
    facilitys_uk[fac]['networks'] = [281]

    fac ='bt southbank London'
    facilitys_uk[fac] ={}                                              
    facilitys_uk[fac]['latitude'] = 51.50547 
    facilitys_uk[fac]['longitude'] = -0.105219
    facilitys_uk[fac]['city'] = 'London'
    facilitys_uk[fac]['org_id'] = 384
    facilitys_uk[fac]['networks'] = [281]

    fac ='bt kingston'
    facilitys_uk[fac] ={}                                              
    facilitys_uk[fac]['latitude'] = 51.41249999999999 
    facilitys_uk[fac]['longitude'] = -0.29127
    facilitys_uk[fac]['city'] = 'Kingston'
    facilitys_uk[fac]['org_id'] = 384
    facilitys_uk[fac]['networks'] = [281]

    fac ='bt birmingham'
    facilitys_uk[fac] ={}                                              
    facilitys_uk[fac]['latitude'] = 52.483079 
    facilitys_uk[fac]['longitude'] = -1.90519 
    facilitys_uk[fac]['city'] = 'Birmingham'
    facilitys_uk[fac]['org_id'] = 384
    facilitys_uk[fac]['networks'] = [281]
    

    #create the Vantage point dictionary
    final_vptable_dict = {}
   

    
    
    # results/vptables/final_vptable.json
    

    
    #read in the IXp LINX detailed info downloaded from 
    # https://portal.linx.net/members/members-ip-asn
    global ix_detail_dict
    ix_detail_dict = {}
    with open('ix_info/members_export.csv', mode = 'r') as csv_file:
        csvreader = csv.reader(csv_file)
        # extracting field names through first row
        fields = next(csvreader)
        # extracting each data row one by one
        row_count= 0
        for row in csvreader:
            row_count += 1
            # print(row_count)
            i = 0
            
            ix_detail_dict[row[4]] = {}
            ix_detail_dict[row[4]]['facility_number'] = 0
            #print(ix_detail_dict)
            for field in fields:
                if field != 'IPv4 Address':
                    ix_detail_dict[row[4]][field] = row[i]
                i += 1 
            mysearch1 = ix_detail_dict[row[4]]['Location'].split(' (')[0]
            mysearch = mysearch1.split(' ')
            # print(mysearch)
            word_count = len(mysearch)
            # print(mysearch)
            
            # Now add the facility number that cooresponds with the Facility name from linx
            # to the ix_detail_dictionary 

            for facility in facilitys_uk:
                #print ('Facility',facility)
                #print('Word count is', word_count)            
                count = 0
                for this_word in mysearch:
                    
                    # print('This Word',this_word, 'Search in ',facilitys_uk[facility]["name"])
                    count += 1
                    
                    if this_word == 'MENA':
                        ix_detail_dict[row[4]]['facility_number'] = 7082
                        break
                    if this_word == 'MA1':
                        ix_detail_dict[row[4]]['facility_number'] = 76
                        break
                    
                    '''
                    "668": {
                    "org_id": 34,
                    "name": "Coresite Reston",
                    "address1": "12100 Sunrise Valley Drive",
                    "address2": "Greenham Business Park",
                    "city": "Reston",
                    "country": "VA",
                    "postcode": "20191",
                    "latitude": -77.364541,
                    "longitude": 38.950631,
                    "networks": [
                    20189,20940,22925,198167,29838,21949,58453,36692,203391,174,205994,
                    2734,30456,23420,208,393,397071,61317,47328,54113,26863,36459,63023,3257,
                    7489,919,6939,213122,16876,62947,32478,20144,397770,3290,53292,40138,8075,
                    8069,10886,34553,56038,62597,2914,31898,16276,4556,40676,33353,32035,26459,
                    1299,13414,3223,5662,62874,53636,10310,21859,399114],
                    '''
                    if this_word.casefold() == 'Reston'.casefold() or this_word == 'Coresite' :
                        #input('Reston wait')
                        ix_detail_dict[row[4]]['facility_number'] = 668
                        break                   
                    if this_word == 'North2':
                        ix_detail_dict[row[4]]['facility_number'] = 4360
                        break
                    if this_word == 'Newport(NGD)':
                        ix_detail_dict[row[4]]['facility_number'] = 1548
                        break
                    if this_word == 'LD8':
                        ix_detail_dict[row[4]]['facility_number'] = 45
                        break
                    if this_word == 'Digital':
                        # print(ix_detail_dict[row[4]]['Location'].split(' (')[1])
                        if ix_detail_dict[row[4]]['Location'].split(' (')[1].split(' ')[0] == '44521':
                            ix_detail_dict[row[4]]['facility_number'] = 1380
                            # print(mysearch)
                            break
                        elif ix_detail_dict[row[4]]['Location'].split(' (')[1].split(' ')[0] == 'RBS)':
                            ix_detail_dict[row[4]]['facility_number'] = 40
                            # print(ix_detail_dict[row[4]]['facility_number'])
                            #input('wait')
                            break
                        elif ix_detail_dict[row[4]]['Location'].split(' (')[1].split(' ')[0] == 'TCM)':
                            ix_detail_dict[row[4]]['facility_number'] = 43
                            # print(ix_detail_dict[row[4]]['facility_number'])
                            #input('wait')
                            break
                        else:
                            ix_detail_dict[row[4]]['facility_number'] = 0
                            break
                    if this_word == 'Iron':
                        ix_detail_dict[row[4]]['facility_number'] = 5373
                        break
                    if this_word == 'Newport(NGD)':
                        ix_detail_dict[row[4]]['facility_number'] = 1548
                        break
                    if this_word == 'Quality':
                        #Not sure if this is correct facility
                        ix_detail_dict[row[4]]['facility_number'] = 350
                        break
                    
                    #print('Count', count)
                    if this_word.casefold() in facilitys_uk[facility]["name"].casefold():
                        #print(this_word,count, word_count,facilitys_uk[facility]["name"])
                        
                        if  count == word_count:
                            
                            ix_detail_dict[row[4]]['facility_number'] = facility

                    else:
                        break
                #print('Facility number', facility)
                if ix_detail_dict[row[4]]['facility_number'] != 0:
                    break
    
    # Now Add the LONAP IXP information to the ix_details list at https://portal.lonap.net/api/v4/member-export/ixf/.
    # in the same format as the LINX IXP details
    # example : "195.66.224.74": {
    #"facility_number": "34",
    #"Organisation Name": "Zzoomm PLC",
    #"Website": "http://",
    #"ASN": "42611",
    #"Peering Policy": "No data",
    #"IPv6 Address": "2001:7f8:4::a673:1",
    #"MAC Address": "a4e1.1a6e.ce0b",
    #"Location": "Telehouse North (THN)",
    #"Switch Port and VLAN": "edge1-thn xe-2/3/0",
    #"Port Type": "10G",
    #"Service Speed": "10G",
    #"Service Type": "Regular",
    #"Peering LAN": "lon1",
    #"Membership Type": "full",
    #"Route Servers": "rs1.lon1, rs2.lon2, rs3.lon1, rs4.lon2"
    # }

    

    with open('ix_info/lonap_data.json') as f:
        lonap_measurements = json.load(f)
    # example IXP and switch entry, note only one ixp and vlan, (LONAP), but multiple switches situated at different facilities
    #
    lonap_switches = {}
    for switch in lonap_measurements['ixp_list'][0]['switch']:
        print(switch)
        id = switch['id']
        lonap_switches[id] = {}
        lonap_switches[id]["name"] = switch['name'],
        lonap_switches[id]["location"] = switch["colo"]
        lonap_switches[id]["city"] = switch['city']
        lonap_switches[id]["country"]: switch['country']
        lonap_switches[id]['pdb fac'] = switch['pdb_facility_id']
        lonap_switches[id]['manufacturer'] = switch['manufacturer']
        lonap_switches[id]['model'] = switch['model']
        lonap_switches[id]['software'] = switch['software']
        
        
    for member in lonap_measurements["member_list"]:
        #print(member)
        
        for connection in member["connection_list"]:
            #print('CCCCCCCCCCCCCCC')
            #print(connection) 
            for vlan in connection['vlan_list']:
                #print('VVVVVVVVVVVVV')
                #print(vlan)
                if 'ipv4' in vlan.keys():
                    ipaddress = vlan['ipv4']['address']
                    ix_detail_dict[ipaddress]= {}
                    print(ipaddress,vlan)
                    #input('ip,vlan')
                    
                    ix_detail_dict[ipaddress]["Organisation Name"] = member['name']
                    ix_detail_dict[ipaddress]["Website"] = member['url']
                    ix_detail_dict[ipaddress]['ASN'] = member['asnum']
                    ix_detail_dict[ipaddress]["Peering Policy"] = member['peering_policy']
                    if 'ipv6' in vlan.keys():
                        ix_detail_dict[ipaddress]["IPv6 Address"] = vlan['ipv6']['address']
                    else:
                        ix_detail_dict[ipaddress]["IPv6 Address"] = ''
                    ix_detail_dict[ipaddress]["MAC Address"] = vlan['ipv4']['mac_addresses']
                    ix_detail_dict[ipaddress]['Port Type'] = ''
                    ix_detail_dict[ipaddress]["Service Speed"] = connection['if_list'][0]['if_speed']      

                    ix_detail_dict[ipaddress]["Service Type"] = ''
                    ix_detail_dict[ipaddress]["Peering LAN"] = "LONAP Peering LAN #1"
                    ix_detail_dict[ipaddress]["Membership Type"] = member['member_type']
                    ix_detail_dict[ipaddress]["Route Servers"]  = '' 
           
                    # sometimes there are multiple switches listed however in every case analysed they are duplicates
                    # so only need first one
                    
                    id = connection['if_list'][0]['switch_id']

                    #print(lonap_measurements['ixp_list']['switch'])
                    ix_detail_dict[ipaddress]["Location"] = lonap_switches[id]['location']
                    ix_detail_dict[ipaddress]["Switch Port and VLAN"] = lonap_switches[id]['name']
                    ix_detail_dict[ipaddress]["facility_number"] =  str(lonap_switches[id]['pdb fac'])

                    #print('HERE',ix_detail_dict[ipaddress])  
                    #input('wait')

    #Add any IXs that have been manually found that do not appear on a members list
    # Equinxi Manchester IX does not seem to have a public members list
    ix_detail_dict["185.1.101.28"] ={}
    ix_detail_dict["185.1.101.28"]["facility_number"] = "76"
    ix_detail_dict["185.1.101.28"]["Organisation Name"] = "Equinix Inc"
    ix_detail_dict["185.1.101.28"]["Website"] = "http://www.equinix.com/"
    ix_detail_dict["185.1.101.28"]["ASN"] ="42611"
    ix_detail_dict["185.1.101.28"]["Peering Policy"] = "No data"
    ix_detail_dict["185.1.101.28"]["IPv6 Address"] = ""
    ix_detail_dict["185.1.101.28"]["MAC Address"] = ""
    ix_detail_dict["185.1.101.28"]["Location"] = "Equinix Internet Exchange, manchester"
    ix_detail_dict["185.1.101.28"]["Switch Port and VLAN"] = ""
    ix_detail_dict["185.1.101.28"]["Port Type"] = ""
    ix_detail_dict["185.1.101.28"]["Service Speed"] = ""
    ix_detail_dict["185.1.101.28"]["Service Type"] = ""
    ix_detail_dict["185.1.101.28"]["Peering LAN"] =""
    ix_detail_dict["185.1.101.28"]["Membership Type"] =""
    ix_detail_dict["185.1.101.28"]["Route Servers"] = ""

    # Linx london. for some reason this is not on their list
    ip = '195.66.226.35' 
    ix_detail_dict[ip] ={}
    ix_detail_dict[ip]["facility_number"] = "34"
    ix_detail_dict[ip]["Organisation Name"] = "London Internet Exchange Ltd."
    ix_detail_dict[ip]["Website"] = "http://www.linx.net/"
    ix_detail_dict[ip]["ASN"] ="5459"
    ix_detail_dict[ip]["Peering Policy"] = "No data"
    ix_detail_dict[ip]["IPv6 Address"] = ""
    ix_detail_dict[ip]["MAC Address"] = ""
    ix_detail_dict[ip]["Location"] = "London Internet Exchange (LINX)"
    ix_detail_dict[ip]["Switch Port and VLAN"] = ""
    ix_detail_dict[ip]["Port Type"] = ""
    ix_detail_dict[ip]["Service Speed"] = ""
    ix_detail_dict[ip]["Service Type"] = ""
    ix_detail_dict[ip]["Peering LAN"] =""
    ix_detail_dict[ip]["Membership Type"] =""
    ix_detail_dict[ip]["Route Servers"] = ""

    # Linx lon2. for some reason this is not on their list
    ip = '195.66.238.35' 
    ix_detail_dict[ip] ={}
    ix_detail_dict[ip]["facility_number"] = "34"
    ix_detail_dict[ip]["Organisation Name"] = "Avensys."
    ix_detail_dict[ip]["Website"] = "https://www.avensys.net/"
    ix_detail_dict[ip]["ASN"] ="8553"
    ix_detail_dict[ip]["Peering Policy"] = "No data"
    ix_detail_dict[ip]["IPv6 Address"] = ""
    ix_detail_dict[ip]["MAC Address"] = ""
    ix_detail_dict[ip]["Location"] = "London Internet Exchange (LINX)"
    ix_detail_dict[ip]["Switch Port and VLAN"] = ""
    ix_detail_dict[ip]["Port Type"] = ""
    ix_detail_dict[ip]["Service Speed"] = ""
    ix_detail_dict[ip]["Service Type"] = ""
    ix_detail_dict[ip]["Peering LAN"] =""
    ix_detail_dict[ip]["Membership Type"] =""
    ix_detail_dict[ip]["Route Servers"] = ""



    ix_details_file = 'results/ix_details.json'
    # Make up a backup file of the dictionary in case we want to use it
    # but the dictionary can now be used.
    # ix_detail_dict now has a cross reference between Ip addresses and facilities.
    # These only include the LINX networks but more can be added to this
    #print('40',ix_detail_dict['185.1.101.28'])
    #print('#######')
    #print('42',ix_detail_dict['195.66.244.42'])
    #input('wait')
    
    with open(ix_details_file, 'w') as f:
        json.dump(ix_detail_dict, f)  
    
    
    # Read in the prefixes info
    with open('peeringdb_test_results/ipprefixes_all.json') as f:
        ipprefixes = json.load(f)


    # Read in the networks info
    with open('peeringdb_test_results/networks_all.json') as f:
        nets = json.load(f)

    # Convert the networks file to a dictionary
    global networks
    networks = convert(nets)
    
    



    # Read in the UK Internet Exchange info
    global ixps_uk
    with open('peeringdb_test_results/uk_ixps.json') as f:
        ixps_uk = json.load(f)
    
    
    

    
    global pdb
    pdb = PeeringDB()
    # pdb.update_all() # update my local database
    # local subnets
    global local_subnets
    local_subnets = ['10.0.0.0/8', '172.16.0.0/12', '192.168.0.0/16','100.64.0.0/10']

    # Read in the UK Internet Exchange info
    #with open('peeringdb_test_results/uk_ixps.json') as f:
        #ixps_uk = json.load(f)

     
    
    #Create a list of Towns where facilities are located
    global townset
    townset = set()
    towns = []
    for fac in facilitys_uk:
        print(fac,facilitys_uk[fac])
        townset.add(facilitys_uk[fac]['city'])
    ''' print(townset)
    c = 0
    for t in townset:
        c +=1
        print(t,c)
    input('number of towns')
    '''
    # create a list of ipv4 prefixes for later use (ipv6 can wait for now)
        
    global ix_prefix_list 
    ix_prefix_list = []
    key = 'ipv4_prefix'
    i = 0
    for ix in ixps_uk:
        i +=1
        print(ix,i)
        
        if key in ixps_uk[ix]:
            ix_prefix_list.append(ixps_uk[ix]['ipv4_prefix'])
        else:
            ixps_uk[ix]['ipv4_prefix']= []

        #create a list of probes that use this ixp
        ixps_uk[ix]['probes'] = []
    print(ix_prefix_list)
    
    # Open the measurements file created previously
    # filename2 = 'measurements/uk_measurements.json' # for full uk_measurements
        

    # filters = {"tags": "NAT", "country_code": "gb", "asn_v4": "3333"}
    
    filters = {"country_code": "gb", "status": "1"} # all uk connected probes
    #filters = {"tags": "system-Anchor", "country_code": "gb"}
    # print(dir(ProbeRequest)) 
    probes = ProbeRequest(**filters)
    probe_list = []
    global uk_probes
    uk_probes ={}
    uk_probes['asn_v4'] = {}
    uk_probes['asn_v4']['total'] = 0
    uk_probes['total_probes'] = 0

    # Create a Dictionary of the UK probes to be used 
    for t_probe in probes:
        #print(str(t_probe["id"]),t_probe)
        # input('wait on probe')
        probe_list.append(str(t_probe["id"]))
        uk_probes[t_probe["id"]] = {}
        uk_probes[t_probe["id"]] ["probe_ip"] = t_probe["address_v4"]
        uk_probes[t_probe["id"]] ["probe_x"] = t_probe["geometry"]["coordinates"][0]
        uk_probes[t_probe["id"]] ["probe_y"] = t_probe["geometry"]["coordinates"][1]
        uk_probes[t_probe["id"]] ["probe_asn"] = t_probe["asn_v4"]
        uk_probes[t_probe["id"]] ["prefix"] = t_probe["prefix_v4"]
        uk_probes[t_probe["id"]] ["status"] = t_probe["status"]['id']
        uk_probes[t_probe["id"]] ["status_description"] = t_probe["status"]['name']
        uk_probes['total_probes'] += 1
        if t_probe['asn_v4'] not in uk_probes['asn_v4']:
            uk_probes['asn_v4'][t_probe['asn_v4']] = 1
            uk_probes['asn_v4']['total'] += 1
        else:
            uk_probes['asn_v4'][t_probe['asn_v4']] +=1
            uk_probes['asn_v4']['total'] +=1

    probes_uk_file = 'peeringdb_test_results/all_uk_anchors.json'
    # write list of Uk probes to file in case needed later
    with open(probes_uk_file, "w") as outfile:
        json.dump(uk_probes, outfile)
    
    
    # test reverse dns
    #addr=reversename.from_address("185.74.25.250")
    #reversedns = str(resolver.resolve(addr,"PTR")[0])
    # print(reversedns)
    # ResultsFile = "target_6087.json"
    UKTownFile = "IPN_GB_2021.csv"

    # UK Towns file is a utf-8 encoded file, ignore any errors
    # https://geoportal.statistics.gov.uk/
    with codecs.open(UKTownFile,'r', encoding='utf-8',
                 errors='ignore') as file:
        content = file.readlines()
    header = content[:1]
    rows = content[1:]
    # print(header)
    # print(rows[0])
    length=len(rows)
    #print (length)
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
    global measurements
    with open(in_file) as measurements_in:
            measurements =json.load(measurements_in)
    # counts for statitics, stored in vptable
    global stats 
    stats = {}
    stats['1'] = 0  # 
    stats['2'] = 0
    stats['3'] = 0
    stats['4'] = 0
    stats['5'] = 0
    stats['total_ips'] = 0
    stats['total_hops'] = 0
    global measurement
    measurement =  {}
    

    # Read in measurements

    # Analysis 
    global results

    results = {}
    results['failures'] = {}
    results['successes']= {}
    
    results['failures']['regex'] = {}
    results['failures']['regex']['total'] = 0
    results['successes']['regex'] = {}
    results['successes']['regex']['total'] = 0

    results['failures']['reverse_tr'] = {}
    results['failures']['reverse_tr']['total'] = 0
    results['successes']['reverse_tr'] = {}
    results['successes']['reverse_tr']['total'] = 0

    results['failures']['rule1'] = {}
    results['failures']['rule1']['total'] = 0
    results['successes']['rule1'] = {}
    results['successes']['rule1']['total'] = 0

    results['failures']['rule2'] = {}
    results['failures']['rule2']['total'] = 0
    results['successes']['rule2'] = {}
    results['successes']['rule2']['total'] = 0
    
    results['failures']['rule3'] = {}
    results['failures']['rule3']['total'] = 0
    results['successes']['rule3'] = {}
    results['successes']['rule3']['total'] = 0

    results['failures']['rule4'] = {}
    results['failures']['rule4']['total'] = 0
    results['successes']['rule4'] = {}
    results['successes']['rule4']['total'] = 0


    results['failures']['rule5'] = {}
    results['failures']['rule5']['total'] = 0
    results['successes']['rule5'] = {}
    results['successes']['rule5']['total'] = 0

    results['failures']['rule5.reverse_dns'] = {}
    results['failures']['rule5.reverse_dns']['total'] = 0
    results['successes']['rule5.reverse_dns'] = {}
    results['successes']['rule5.reverse_dns']['total'] = 0

    results['failures']['rule5.common_fac'] = {}
    results['failures']['rule5.common_fac']['total'] = 0
    results['successes']['rule5.common_fac'] = {}
    results['successes']['rule5.common_fac']['total'] = 0

    results['failures']['rule5.fac_to_ip_table'] = {}
    results['failures']['rule5.fac_to_ip_table']['total'] = 0
    results['successes']['rule5.fac_to_ip_table'] = {}
    results['successes']['rule5.fac_to_ip_table']['total'] = 0

    results['failures']['rule6'] = {}
    results['failures']['rule6']['total'] = 0
    results['successes']['rule6'] = {}
    results['successes']['rule6']['total'] = 0

    results['failures']['rule6'] = {}
    results['failures']['rule6']['total'] = 0
    results['successes']['rule6'] = {}
    results['successes']['rule6']['total'] = 0

    results['failures']['prelim'] = {}
    results['failures']['prelim']['total'] = 0
    results['successes']['prelim'] = {}
    results['successes']['prelim']['total'] = 0

    results['rule1'] = 0
    results['rule2'] = 0
    results['rule3'] = 0
    results['rule4'] = 0
    results['rule5'] = 0
    results['rule5.fac_to_ip_table'] = 0
    results['rule5.common_fac'] = 0
    results['rule5.reverse_dns'] = 0
    results['rule5.reverse_tr'] = 0

    results['rule6'] = 0
    results['prelim'] = 0
    results['reverse_dns'] = 0
    results['regex'] = 0

    results['rtt'] ={}
    results['rtt']['.0'] = 0
    results['rtt']['.1'] = 0
    results['rtt']['.2'] = 0
    results['rtt']['.3'] = 0
    results['rtt']['.4'] = 0
    results['rtt']['.5'] = 0
    results['rtt']['.6'] = 0
    results['rtt']['.7'] = 0
    results['rtt']['.8'] = 0
    results['rtt']['.9'] = 0
    results['rtt']['1'] = 0


        
    final_results_dict ={} 
    

    for measurement_id in measurements:
        print('Measurement Id is',measurement_id)
        print('Measurement is',measurements[measurement_id])

        this_target = measurements[measurement_id]['target_probe']
        
        
        print("TARGET ***************************************************",this_target)
        
        
        measurement[this_target] = {}
        measurement[this_target] ["measurement_id"] = measurement_id
        measurement[this_target] ["probe_ip"] = measurements[measurement_id]["target_address"]
        measurement[this_target] ["probe_x"] = measurements[measurement_id]["target_coordinates"][1]
        measurement[this_target] ["probe_y"] = measurements[measurement_id]["target_coordinates"][0]
        measurement[this_target] ["probe_asn"] = uk_probes[int(this_target)] ["probe_asn"]
        measurement[this_target] ["probe_asn"] = uk_probes[int(this_target)] ["probe_asn"]
        facilities_used = {}
        
            
        probe_number = 0
        ixp_entry_point = ''
        final_results_dict[this_target]={}
        #
        #Create the Source Probes
        for probe_id in measurements[measurement_id]['results']:
            # get reveerse measurment in case it is needed later
            measurement[this_target]['reverse_measurement_id'] = ''
            for m in measurements:
                if measurements[m]['target_probe'] == probe_id:
                    measurement[this_target]['reverse_measurement_id'] = m
                    break;
            print('forward_measurement is',measurement_id)
            print('source is',probe_id)
            print('target is',measurements[measurement_id]['target_probe'])
            if measurement[this_target]['reverse_measurement_id'] =='':
                input('reverse measurment id has not been set, are you sure you have got all the measurments, forward and reverse')
            print('reverse measurement is',m)
            print('sources are',measurements[m]['results'])
            print('target is',measurements[m]['target_probe'])
            


            print(probe_id)
            # Tests a single source probe
            #if probe_id != '6562':
            #    continue
            probe_number += 1
            print('PPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPP')
            print (probe_number,'Start of new Source Probe',probe_id,)
            print('PPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPP')
            #input('wait')
            # ixp_entered_id = 0
            ixp_entered_flag = False
            ix_hop = 0
            facilities_used[probe_id] = []
            # Only iterate through source probe's not the target probe
            if probe_id != this_target:
                results[probe_id] = {}
                results[probe_id]['status'] = False
                results[probe_id]['status_reason'] = []
                results[probe_id]['status_code'] = []



                source_lon = measurements[measurement_id]['results'][probe_id]['source_coordinates'][0]
                source_lat = measurements[measurement_id]['results'][probe_id]['source_coordinates'][1]
                max_hop = measurements[measurement_id]['results'][probe_id]['max_hops']
                source_coords = (source_lat,source_lon)
                prev_hop ={}
                ixp_pre_hops = {}
                ixp_post_hops = {}
                ixp_in_hops = {}
                #facilities_used={}
                print(uk_probes[int(probe_id)])
                prev_hop['id'] = '0'
                prev_hop['ip_from'] =uk_probes[int(probe_id)]['probe_ip']
                prev_hop['rdns'] = ''
                prev_hop['rtt'] = 0
                prev_hop['address'] = 'street, town, postcode'
                print('UK PROBES',uk_probes[int(probe_id)]["probe_asn"])
                # input('wait')
                prev_hop['asn'] = uk_probes[int(probe_id)]["probe_asn"]
                prev_hop['hop_latitude'] = source_lat
                prev_hop['hop_longitude'] = source_lon     
                prev_hop['use_next_hop_loc'] = False     
                prev_hop['local_subnet_flag'] = False  
                prev_hop['facility'] = []
                prev_hop['network'] = 0
                

                print('lat,lon', prev_hop['hop_latitude'],prev_hop['hop_longitude'] )   
                
                final_results_dict[this_target][probe_id] ={}
                for hop in measurements[measurement_id]['results'][probe_id]['hops']:
                    stats['total_hops'] += 1
                    
                    results[probe_id][hop] = {}
                    #print('HOp IS', hop)
                
                    #input('wait')
                    fac_exit_hop = False
                    fac_entry_hop = False
                    
                    
                    print('HHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHH') 
                    print(' START of NEW HOP',hop)
                    print ('for source probe', probe_number,'Probe ',probe_id,)
                    print('target is',this_target)
                    print('previous hop',prev_hop, 'ip address', measurements[measurement_id]['results'][probe_id]['hops'][hop])
                    
                    this_hop_results = measurements[measurement_id]['results'][probe_id]['hops'][hop] # rtt value and IP address for this address
                    
                    print('HHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHH') 
                    
                    # we could only check if this ip address is not already in the final VP table but
                    # is it possible that we found some extra info ? not sure if this is possible
                    # but leaving it as a TODO for now.
                    #  
                    this_hop, facilities_used, ixp_pre_hops,ixp_in_hops,ixp_post_hops,rules,ix_hop = get_hop_location(ixp_pre_hops,ixp_in_hops,ixp_post_hops,facilities_used,this_target,probe_id,prev_hop, hop, this_hop_results,ixp_entered_flag,ix_hop,max_hop)

                    print(this_hop)
                    
                    
                    prev_hop = this_hop
                    fac_exit_hop = False
                    fac_entry_hop = False 
                    ixp_entered_flag = False
                    #last_rtt = this_rtt


                    results[probe_id][hop] = this_hop
                    results[probe_id][hop]['rule_use'] = rules
                    print('%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%')
                    ipaddress = this_hop['ip_from']
                    #print('IP ADDRESS is',ipaddress)
                    #print(final_vptable_dict)
                    #print('#####################')
                    #print (vptable_dict)


                    # try to update the Vptable with any new information found regarding that IPADDRESS
                    # else: otherwise create a new vptable entry
                    if ipaddress in final_vptable_dict.keys():
                        
                        #print(final_vptable_dict)
                        #print('ipaddress is',ipaddress)
                        #print('this_hop is',this_hop)
                        #print
                        
                        #print('Vptable is ',vptable_dict)
                        
                        #print('Rules are',rules)
                        if final_vptable_dict[ipaddress]['lat'] == 0:
                            final_vptable_dict[ipaddress]['lat'] = vptable_dict[ipaddress]['lat']
                            final_vptable_dict[ipaddress]['lon'] = vptable_dict[ipaddress]['lon']
                            final_vptable_dict[ipaddress]['facility']=vptable_dict[ipaddress]['facility']
                            print('change lat,lon,fac')
                        if final_vptable_dict[ipaddress]['rdns'] != '':
                            final_vptable_dict[ipaddress]['rdns'] =vptable_dict[ipaddress]['rdns']
                            print('rdns')
                        if vptable_dict[ipaddress]['code'] == 2:
                            final_vptable_dict[ipaddress]['code'] =2 
                            print('code')
                        if vptable_dict[ipaddress]['port'] != '':
                            final_vptable_dict[ipaddress]['port'] = vptable_dict[ipaddress]['port']  
                            print('port')
                        if vptable_dict[ipaddress]['speed'] != '':
                            final_vptable_dict[ipaddress]['speed'] = vptable_dict[ipaddress]['speed'] 
                            print('speed')

                        
                        #print(final_vptable_dict)  
                        #input('wait')

                    else:
                        final_vptable_dict[ipaddress] ={}
                        
                        final_vptable_dict[ipaddress]['lat'] = vptable_dict[ipaddress]['lat']
                        final_vptable_dict[ipaddress]['lon'] = vptable_dict[ipaddress]['lon']
                        final_vptable_dict[ipaddress]['facility']=vptable_dict[ipaddress]['facility']
                        final_vptable_dict[ipaddress]['rdns'] =vptable_dict[ipaddress]['rdns']
                        final_vptable_dict[ipaddress]['code'] = vptable_dict[ipaddress]['code'] 
                        final_vptable_dict[ipaddress]['port'] = vptable_dict[ipaddress]['port']  
                        final_vptable_dict[ipaddress]['speed'] = vptable_dict[ipaddress]['speed'] 

                #print(results[probe_id])
                results_file = 'results/tables/latest/'+probe_id+'_'+this_target+'.json'
                print ('WRITING FILE',results_file)
                with open(results_file, 'w') as f:
                    json.dump(results[probe_id], f)  
                                    
                final_results_dict[this_target][probe_id].update(results[probe_id])
                vptable_filename = 'results/vptables/latest/'+probe_id+'_'+this_target+'.json'
                #write_vptable_file(vptable_filename)
                
                
                final_vptable_dict.update(vptable_dict)

                
                # vptable_dict = {}
                    
    final_vptable_filename = 'results/vptables/latest_vptable.json'
    final_vptable_dict['stats'] = {}
    final_vptable_dict['stats'].update(stats)
    with open(final_vptable_filename, 'w') as f:
        json.dump(final_vptable_dict, f) 
    print(final_vptable_dict)
    print('FINAL VPTABLE WRITTEN TO ', final_vptable_filename)

    final_results_dict['successes']={}
    final_results_dict['failures']={}
    final_results_dict['failures'].update(results['failures'])
    final_results_dict['successes'].update(results['successes'])

    with open(out_file, 'w') as f:
        json.dump(final_results_dict, f)                   
    print('Final RESULTS WRITTEN TO ', out_file)
    #input('wait')
if __name__ == "__main__":
    main(sys.argv[1:])
