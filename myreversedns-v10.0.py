#!/usr/bin/env python
# take results and discover the hops locations
from dns import resolver,reversename
import csv
import codecs
import sys,getopt
sys.path.append("/home/paul/.local/lib/python3.7/site-packages/prsw")
import re
import os
os.chdir('/home/paul/Documents/UK')
del os 
import sqlite3

# https://pypi.org/project/prsw/
# Check RPKI validation status TODO: this not currently implemented
# print(ripe.rpki_validation_status(3333, '193.0.0.0/21').status)
# Find all announced prefixes for a Autonomous System
# prefixes = ripe.announced_prefixes(3333)
# however this returns multiple ASNs for a given prefix, prbably best using the RIPE database for this
# PRSW, the Python RIPE Stat Wrapper, is a python package that simplifies access to the RIPE Stat public data API.
import prsw

global ripe
ripe = prsw.RIPEstat()




# Interact with the looking glass
'''
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


# Table Names
#peeringdb_network         
#peeringdb_facility          peeringdb_network_contact 
#peeringdb_ix                peeringdb_network_facility
#peeringdb_ix_facility       peeringdb_network_ixlan   
#peeringdb_ixlan             peeringdb_organization    
#peeringdb_ixlan_prefix    


# import request so can access the RIPE database REST API 
import requests
ripe_url = 'https://rest.db.ripe.net/search.json'

import json
import ipaddress
import great_circle_calculator.great_circle_calculator as gcc
from ripe.atlas.cousteau import ProbeRequest, Traceroute, AtlasSource, AtlasRequest, AtlasCreateRequest
from dns import resolver,reversename


from peeringdb import PeeringDB, resource, config

def append_vptable_dict(code,ip,lat,lon,rdns,fac,port,speed):
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
        telehouse_list = [34,39,45,835]
        equinix_list = [832, 3152]
        if all(x in telehouse_list for x in possible_entry_facility):
            ixp_entry_point = possible_entry_facility[0]
            print('all telehouse',ixp_entry_point) 
            results[probe_id]['status'] = False
            results[probe_id]['status_reason'].append(probe_id+' All Entry points are Telehouse in london Docklands')
            results[probe_id]['status_code'].append(7)
            this_hop['hop_latitude'] = facilitys_uk[str(ixp_entry_point)]['latitude']
            this_hop['hop_longitude'] = facilitys_uk[str(ixp_entry_point)]['longitude']
            this_hop['facility'].append(ixp_entry_point)
        # if list of possible entry facilities are all equinix in slough then just chose the initial one   
        elif all(x in equinix_list for x in possible_entry_facility):
                ixp_entry_point = possible_entry_facility[0]
                print('all equinix',ixp_entry_point)
                results[probe_id]['status'] = False 
                results[probe_id]['status_reason'].append(probe_id+' All Entry points are Equinix in Slough')
                results[probe_id]['status_code'].append(8)
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
        results[probe_id]['status_code'].append(0) 
        
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


def get_hop_location(ixp_pre_hops,ixp_in_hops,ixp_post_hops,facilities_used,this_target,probe_id,prev_hop,hop,hop_details,ixp_entered_flag):
    
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
    
    #input('Wait')

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

    print('This  hops ip address is',this_hop['ip_from'])

    # Check to see if this hops ip address is in a IX prefix list and set flag if true
    # TODO This could actually do with going at end of rules as it slows down the processing
    # but then how would i get a flag set for rules 5 and 6 ?
    ix_prefix_flag = False
    local_subnet_flag = False
    this_hop['local_subnet_flag'] = False
    target_flag = False
    gateway_flag = False

    # PRELIMINARY CHECKS
    #########################################################################################################

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
    
    #Check to see if this ip address is in the local subnets
    
    for prefix in local_subnets:
        '''
        # TODO temporary fix as cant seem to get this working - FIXED
        if this_hop['ip_from'] == '10.255.255.2':
            local_subnet_flag = True
            this_hop['local_subnet_flag'] = True  
            print('Local Subnet flag is', local_subnet_flag)
            print( '10.255.255.2; local subnet_flag is ', local_subnet_flag)
            #input('WAIT')
            break
        '''
        
       
      
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
                    this_hop['asn'] = [int(re.split('AS|as', ripedb_asn)[1])][0]
                    print('RIPE GOT THIS Hop ASN = ', this_hop['asn'])
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
                print(x)
                #input('hopefully got infor from ARIn wait')
                print(r.text)
                try:
                    this_hop['asn']  = r.text.split('<originAS>AS')[1].split('</originAS>')[0]
                except:
                    # if arin cant find the ASN lets try a looking glass server
                    response = ripe.network_info(this_hop['ip_from'])
                    print('Arin got a ok status but couldnt find an AS so tried prsw, ASN = ', this_hop['asn'])
                    
                    this_hop['asn'] = response.asns[0]
                        
                else:
                    print(' this hop is', this_hop['asn'])
                    print('ARIN GOT THIS Hop ASN = ', this_hop['asn'])
                    #input('wait')
            else:
                # if arin cant find the ASN lets try a looking glass server
                response = ripe.network_info(this_hop['ip_from'])
                print('Arin got a not ok status but PRSW GOT THIS ASN = ', this_hop['asn'])
                    
                this_hop['asn'] = response.asns[0]        
                #input('wait')
                 

    # if this ip address is used by an IX get the ASN of the IX
    if ix_prefix_flag:
        con = sqlite3.connect("/home/paul/peeringdb.sqlite3")
        cur = con.cursor()
        print('IXPS UK', this_ixp,ixps_uk[this_ixp])
        ixp_ip = (this_hop['ip_from'],)
        this_hop['asn'] = 0
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

     
    # END OF PRELIMINARY CHECKS
    # ###############################################################################################################           
    


    # Find Location Logic
    ##############################################################################################################

    rule_flag = False

    # First of all start with the obvious, We dont need to run REGEX on every hop because some hops will not have ReverseDNS
    # Addresses.

    
    
    # rule1 if hop is 1 and subnet is same as probe ip the location is still where the probe is located. 
    # This is probably the local gateway that the probe is connected to.  
    if this_hop['id'] == '1': 
        rname  = port = speed = ''
        rule_flag = True
        gateway_flag = True
        # lets try rdns but it is likely it wont work
        addr=reversename.from_address(this_hop['ip_from'])
        try:
            rname = str(resolver.resolve(addr,"PTR")[0])
        except:
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
                this_hop['asn'] = prev_hop['asn']
                # this_hop['facility'] = []
                print('PROBEID is' ,probe_id)
                this_hop['rdns'] = 'local'
                print('SUBENET = ' , this_subnet, prev_subnet,this_hop['hop_latitude'] )
                print('Coords are',  this_hop['ip_from'], this_hop['hop_latitude'], this_hop['hop_longitude'] )
                append_vptable_dict(2, this_hop['ip_from'],this_hop['hop_latitude'], this_hop['hop_longitude'],rname,this_hop['facility'],port,speed)
                stats['2'] += 1
            else:
                print ('hmm hop is 1 but subnets dont match - see the find location logic rules 1 - may need a new rule')
                print('HOp1s info is',this_hop, ' probe info is ', probe_id, prev_hop)
                print('SUBNET = ' , this_subnet, prev_subnet)
                append_vptable_dict(5, this_hop['ip_from'],this_hop['hop_latitude'], this_hop['hop_longitude'],rname,this_hop['facility'],port,speed)
                stats['5'] += 1
                input('Wait')
            
            print('RULE1')
           
            print(vptable_dict)
            # input('wait')
        else:
            
            this_facility, coords = get_coords(this_hop,rname)
            
            if this_facility:
                lon = coords[0]
                lat = coords[1]
                print(this_hop['facility'],this_facility)
                this_hop['facility'] = this_facility
                print(this_hop['facility'])
                input('wait')
                this_hop['hop_longitude'] = lon
                this_hop['hop_latitude'] = lat
                append_vptable_dict(2, this_hop['ip_from'],this_hop['hop_latitude'], this_hop['hop_longitude'],rname,this_facility,port,speed)
                stats['2'] += 1
            else:
                # I shouldnt repeat code but if i cannot find the facility then this is same as if the try failed above
                
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
                    this_hop['asn'] = prev_hop['asn']
                    this_hop['facility'] = []
                    print('PROBEID is' ,probe_id)
                    this_hop['rdns'] = 'local'
                    print('SUBENET = ' , this_subnet, prev_subnet,this_hop['hop_latitude'] )
                    print('Coords are',  this_hop['ip_from'], this_hop['hop_latitude'], this_hop['hop_longitude'] )
                    append_vptable_dict(2, this_hop['ip_from'],this_hop['hop_latitude'], this_hop['hop_longitude'],rname,this_hop['facility'],port,speed)
                    stats['2'] += 1
                else:
                    print ('hmm hop is 1 but subnets dont match - see the find location logic rules 1 - may need a new rule')
                    print('HOp1s info is',this_hop, ' probe info is ', probe_id, prev_hop)
                    append_vptable_dict(5, this_hop['ip_from'],this_hop['hop_latitude'], this_hop['hop_longitude'],rname,this_hop['facility'],port,speed)
                    stats['5'] += 1
                    input('Wait')
                    
                print('RULE1')
                
                #input('wait')


    # rule2 if using a local subnet and previous wasnt then it is likely that this IP_address is now at the remote site (ie the next hop address) 
    # so we need to fill in the coordinets of this IP address by using the next hops coordinates.
    # but this network will still belong to the last ASN
    if local_subnet_flag:
        if not prev_hop['local_subnet_flag']:
            rule_flag = True
            print('remote end of VPN')
            this_hop['use_next_hop_loc'] = True # Setting a flag so that next hop knows to set prev hop to same location
            this_hop['hop_latitude'] =  0
            this_hop['hop_longitude'] = 0
            this_hop['rdns'] = 'local'
            this_hop['asn'] = prev_hop['asn']
        else:
            print ('hmm prev_hop prefix is in local subnets and so is this (is this a multi hop local network ?) - see the find location logic rules 2')
            rule_flag = True
            print('remote end of VPN')
            this_hop['use_next_hop_loc'] = True # Setting a flag so that next hop knows to set prev hop to same location
            this_hop['hop_latitude'] =  0
            this_hop['hop_longitude'] = 0
            this_hop['rdns'] = 'local'
            this_hop['asn'] = prev_hop['asn']
            
            #input('Wait')
        print('RULE2')
        #input('wait')
        
    # rule3 if the last hops 'use_next_hop_loc' is true then we need to fill in the last ones coordiantes as well as this one
    # as it likely that the two are in the same location. (this may go back a few hops)
    if prev_hop['use_next_hop_loc'] == True:
        rule_flag = True
        rname = port = speed = ''
        addr=reversename.from_address(this_hop['ip_from'])
        try:
            rname = str(resolver.resolve(addr,"PTR")[0])
        except:
            # if we cant get the location of this hop using dns then try comparing last asn to this asn and finding
            # what network facilities the two jointly peer at.
            print('Probe ', probe_id)
            print('THIS HOP ********************',hop,this_hop)
            print('Previous HOP ********************',prev_hop)
            
            if this_hop['asn'] != prev_hop['asn']:
                
                print('ASNS are different - RULE3 perhaps maybe use this fact, deferring locating for now')
                print(results[probe_id])
                this_hop['use_next_hop_loc'] == True
                
            else:
                # if the two asns are the same then we are going to have to defer locating this hop and use the next hops location
                
                this_hop['use_next_hop_loc'] == True
                print(' RULE3 USE NEXT HOPs location for the previous hop and this hop')
                # input('wait Continue if you want to see how far you get')
        # if resolver was able to get a reverse dns name then continue as normal.
        #         
        else:
            this_facility,coords = get_coords(this_hop,rname)
            this_hop['rdns'] = rname
            print('RULE 3 This hops Reversedns name is',rname)
            if this_facility:
                this_facility, coords = get_coords(this_hop,rname)
                lon = coords[0]
                lat = coords[1]
                this_hop['facility'].append(this_facility)
                this_hop['hop_longitude'] = lon
                this_hop['hop_latitude'] = lat
                append_vptable_dict(2, this_hop['ip_from'],this_hop['hop_latitude'], this_hop['hop_longitude'],rname,this_facility,port,speed)
                stats['2'] += 1
                # Now go back and set the last hops that had their use next hop location to true
                for h in range(int(hop)-1,0,-1):
                    print('hop is', h)
                    print(results[probe_id][str(h)])
                    if results[probe_id][str(h)]['use_next_hop_loc'] == True:
                        
                        results[probe_id][str(h)]['hop_latitude'] =  lat # fill in longitude of last hop
                        results[probe_id][str(h)]['hop_longitude'] =  lon # fill in longitude of last hop
                        results[probe_id][str(h)]['facility'].append(this_facility)
                        print('hop',h,results[probe_id][str(h)])
                        # if this hop is not a local subnet then add to vptable
                        if not results[probe_id][str(h)]['local_subnet_flag']:
                            append_vptable_dict(4, results[probe_id][str(h)]['ip_from'],this_hop['hop_latitude'], this_hop['hop_longitude'],rname,this_facility,port,speed)
                            stats['4'] += 1
                        
                    else:
                        print('use next hop loc at hop',h,'is no longer true')
                        break
            else:
                print ('RULE 3 got the rname', rname,' but couldnt get the facility',this_hop)
                append_vptable_dict(5, results[probe_id][str(h)]['ip_from'],this_hop['hop_latitude'], this_hop['hop_longitude'],rname,this_facility,port,speed)
                stats['5'] += 1
                input('wait')
            print('RESULTS ARE ',results[probe_id])
        print('RULE3')
        # input('wait')
        
    # rule 4 if this hop is the target ip address
    if this_hop['ip_from'] == measurement[this_target] ["probe_ip"]:
        rule_flag = True
        target_flag = True
        rname = port = speed = ''
        this_hop['hop_longitude'] = measurement[this_target] ["probe_y"] 
        this_hop['hop_latitude'] = measurement[this_target] ["probe_x"]
        this_hop['facility'] = []
        this_hop['rdns'] = 'PROBE'+this_target   
        print('this hop is', this_hop)
        append_vptable_dict(2, this_hop['ip_from'],this_hop['hop_latitude'], this_hop['hop_longitude'],this_hop['rdns'],this_hop['facility'],port,speed)
        stats['2'] += 1
        print('RULE4')
        #input('wait')
        
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
        input('wait')
    '''    
    #RULE 5A
    # Now we need the exit point if we are now inside the IXP
    if ix_prefix_flag:
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
            hop_asn = prev_hop['asn']
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

        # try first of all getting the correct facility using the new facilities to ip address table
        this_fac = {}
        this_fac = ix_detail_dict[this_hop['ip_from']]
        print( 'FACILITY =',this_fac)

        if this_fac:
            ixp_exit_point = this_fac['facility_number']

            results[probe_id]['status'] = True 
            results[probe_id]['status_reason'].append(probe_id+' Exit Facility is'+ixp_exit_point)
            results[probe_id]['status_code'].append(0)
            this_hop['hop_latitude'] = facilitys_uk[str(ixp_exit_point)]['latitude']
            this_hop['hop_longitude'] = facilitys_uk[str(ixp_exit_point)]['longitude']
            this_hop['facility'].append(ixp_exit_point)
            this_hop['port'] = this_fac['Switch Port and VLAN']
            this_hop['speed'] = this_fac['Port Type']
            
            append_vptable_dict(2, this_hop['ip_from'],this_hop['hop_latitude'], this_hop['hop_longitude'],'',this_hop['facility'],this_hop['port'],this_hop['speed'])
            stats['2'] += 1
        else:
            # try Getting the facilities where the network succeding the IXP peers by comparing the previous ASN peering points with 
            # this ASNs peering points and selecting the common facility
            if this_network['netfac_set']:
                exit_netfac_ids = []
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

                ixp_exit_point = []
                #Choose the exit facility which is shared between the exit network and the IXP
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

            # Lets see if we can figure out the facility by the hops ip address
            # This really should be one of the first checks
                print(this_hop['ip_from'])
            '''
            for ip_address in ix_detail_dict:
                if ip_address == this_hop['ip_from']:
                    print(ix_detail_dict[ip_address]['facility_number'])
                    this_fac = ix_detail_dict[ip_address]['facility_number']
                    this_ip = ip_address
                    ixp_exit_point = this_fac
                    results[probe_id]['status'] = True 
                    results[probe_id]['status_reason'].append(probe_id+' Exit Facility is'+ixp_exit_point)
                    results[probe_id]['status_code'].append(0)
                    this_hop['hop_latitude'] = facilitys_uk[str(ixp_exit_point)]['latitude']
                    this_hop['hop_longitude'] = facilitys_uk[str(ixp_exit_point)]['longitude']
                    this_hop['facility'].append(ixp_exit_point)
                    break
            '''
            print('the correct fac is', this_fac, 'and is confirmed with', ixp_fac, ' and the correct ip is', this_hop['ip_from'])
        
        # These are possibly all redundant rules now due to being found by the IP to facility table
        if results[probe_id]['status'] != True:
            ixp_exit_point = 0
            for fac in possible_exit_facility:
                if fac == this_fac:
                    # yes we did figure it out
                    ixp_exit_point = fac
                    results[probe_id]['status'] = True 
                    results[probe_id]['status_reason'].append(probe_id+' Exit Facility is'+ixp_exit_point_)
                    results[probe_id]['status_code'].append(0)
                    this_hop['hop_latitude'] = facilitys_uk[str(ixp_exit_point)]['latitude']
                    this_hop['hop_longitude'] = facilitys_uk[str(ixp_exit_point)]['longitude']
                    this_hop['facility'].append(ixp_exit_point)
                    append_vptable_dict(2, this_hop['ip_from'],this_hop['hop_latitude'], this_hop['hop_longitude'])
                    stats['2'] += 1
                    break
            if len(possible_exit_facility) > 1:
                print('greater than 1')
                telehouse_list = [34,39,45,835]
                equinix_list = [832, 3152]
                if all(x in telehouse_list for x in possible_exit_facility):
                    ixp_exit_point = possible_exit_facility[0]
                    print('all telehouse',ixp_exit_point) 
                    this_hop['facility'].append(ixp_exit_point)
                    this_hop['hop_latitude'] = facilitys_uk[str(ixp_exit_point)]['latitude']
                    this_hop['hop_longitude'] = facilitys_uk[str(ixp_exit_point)]['longitude']
                    results[probe_id]['status'] = True 
                    results[probe_id]['status_reason'].append(probe_id+' All Telehouse so chose first one'+ixp_exit_point_)
                    results[probe_id]['status_code'].append(0)
                    append_vptable_dict(3, this_hop['ip_from'],this_hop['hop_latitude'], this_hop['hop_longitude'])
                    stats['3'] += 1
                # if list of possible exit facilities are all equinix in slough then just chose the initial one   
                elif all(x in equinix_list for x in possible_exit_facility):
                    ixp_exit_point = possible_exit_facility[0]
                    print('all equinix',ixp_exit_point) 
                    this_hop['facility'].append(ixp_exit_point)
                    this_hop['hop_latitude'] = facilitys_uk[str(ixp_exit_point)]['latitude']
                    this_hop['hop_longitude'] = facilitys_uk[str(ixp_exit_point)]['longitude']
                    results[probe_id]['status'] = True 
                    results[probe_id]['status_reason'].append(probe_id+' All Equinix so chose first one'+ixp_exit_point_)
                    results[probe_id]['status_code'].append(0)
                    append_vptable_dict(3, this_hop['ip_from'],this_hop['hop_latitude'], this_hop['hop_longitude'])
                    stats['3'] += 1
                    # if there are multiple shared facilities for the AS and the IX
                    # exit RULE 2
                    # if the exit and entrance are same 
                elif ixp_entry_point in possible_exit_facility:
                        # there is no entry point anymore so this will fail 
                        ixp_exit_point = ixp_entry_point
                        this_hop['facility'].append(ixp_exit_point)
                        this_hop['hop_latitude'] = facilitys_uk[str(ixp_exit_point)]['latitude']
                        this_hop['hop_longitude'] = facilitys_uk[str(ixp_exit_point)]['longitude']
                        results[probe_id]['status'] = True 
                        results[probe_id]['status_reason'].append(probe_id+'Input and output are same'+ixp_exit_point_)
                        results[probe_id]['status_code'].append(7)
                        append_vptable_dict(3, this_hop['ip_from'],this_hop['hop_latitude'], this_hop['hop_longitude'])
                        stats['3'] += 1
                        input('input and exit are the same')
                else:
                    # if the list doesnt have all telehouse facilities then we need a rule here
                    print('ohoh no valid rule for this posissible exit list', possible_exit_facility) 
                    results[probe_id]['status'] = False
                    results[probe_id]['status_reason'].append('initial Facility used as no valid rule for the Facility EXIT list ' + str(possible_exit_facility))
                    results[probe_id]['status_code'].append(5)
                    ixp_exit_point = possible_exit_facility[0]
                    this_hop['facility'].append(ixp_exit_point)
                    this_hop['hop_latitude'] = facilitys_uk[str(ixp_exit_point)]['latitude']
                    this_hop['hop_longitude'] = facilitys_uk[str(ixp_exit_point)]['longitude']
                    append_vptable_dict(5, this_hop['ip_from'],this_hop['hop_latitude'], this_hop['hop_longitude'])
                    stats['5'] += 1
            elif len(possible_exit_facility) == 1:
                # If there is only one shared facility between the IX and the ASN then all is good
                # RULE 3
                results[probe_id]['status'] = False
                results[probe_id]['status_reason'].append('All is good with the exit facility ' + str(possible_exit_facility))
                results[probe_id]['status_code'].append(0)
                ixp_exit_point =  possible_exit_facility[0]
                this_hop['facility'].append(ixp_exit_point) 
                this_hop['hop_latitude'] = facilitys_uk[str(ixp_exit_point)]['latitude']
                this_hop['hop_longitude'] = facilitys_uk[str(ixp_exit_point)]['longitude']
                append_vptable_dict(2, this_hop['ip_from'],this_hop['hop_latitude'], this_hop['hop_longitude'])
                stats['2'] += 1
            else:
                # If there are no shared facilities then we have a problem
                # RULE 4
                print ('exit list must be 0, this needs a human', possible_exit_facility)
                results[probe_id]['status'] = False
                results[probe_id]['status_reason'].append(probe_id+' does not have an EXIT POINT')
                results[probe_id]['status_code'].append(4)
                append_vptable_dict(5, this_hop['ip_from'],this_hop['hop_latitude'], this_hop['hop_longitude'])
                stats['5'] += 1
                
        '''
        facilities_used[probe_id].append(str(ixp_exit_point))
        facilities_used[probe_id].append(hop)
        print('facilities-used',facilities_used[probe_id])
        print('FLAG********************************************************************',ixp_entered_flag)
        # html.create_ixp(ixp_entered_id, ixps_uk[ixp_entered_id],facilities_used[probe_id],facilitys_uk,probe_id)
        #ixp_entered_flag = False
        #this_ixp = []
        



        lat2 = this_hop['hop_latitude']
        lon2 = this_hop['hop_longitude']                   
                            
                        
                                
        current_ip = prev_hop['ip_from']
        # if only 2 entries then we have worked out facility entering the ixp but not the one exiting
        if len(facilities_used[probe_id])  == 2:
            print('hop, entry facilities',hop, facilities_used[probe_id][0],facilities_used[probe_id][1])
            
            if str(int(hop)-1) == facilities_used[probe_id][1]:
                # if we have worked out the entry facility
                if facilities_used[probe_id][0] != '0':
                    print('FAC USED',facilities_used)
                    fac_entry_hop = True 
                    print('only 2/4 RESULTS SO FAR ARE', results)
                    input('waiting on results')
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
                source_coords = (lon1,lat1)
                hop_coords = (lon2,lat2)
                hop_distance = gcc.distance_between_points(source_coords, hop_coords, unit='kilometers',haversine=True)
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
        '''
        


        
        # html.create_hop(probe_id,hop,this_hop,this_rtt,fac_entry_hop,fac_exit_hop)
        
        # html.create_lines_var(probe_id,hop,lat1,lon1,lat2,lon2,hop_distance,this_rtt,current_ip,this_hop['from'],fac_entry_hop,fac_exit_hop)                   
        # record the state of the last hop in case it is needed to detect the IXP entry point
        prev_hop = this_hop
        fac_exit_hop = False
        fac_entry_hop = False 
        ixp_entered_flag = False
        
        '''
        current_lat = lat2
        current_lon = lon2
        source_coords = (lon2,lat2)
        '''

        last_rtt = this_rtt

    
        # try to get the reverse DNS name, if none then just use the IX Number   
        # 
        if results[probe_id]['status'] != True: 
            try:
                    
                addr=reversename.from_address(this_hop['ip_from'])
                rname = str(resolver.resolve(addr,"PTR")[0])
            except:
                rname = 'IX:'+this_ixp
                this_hop['rdns'] = rname
                results[probe_id]['status'] = False
                results[probe_id]['status_reason'].append('RULE 5 RDNS was Unable to find the  exit facility ' )
                results[probe_id]['status_code'].append(7)
                
            else:
                this_facility,coords = get_coords(this_hop,rname)

                if this_facility:
                    lon = coords[0]
                    lat = coords[1]
                    this_hop['facility'].append(this_facility)
                    this_hop['network'] = 0
                    this_hop['hop_longitude'] = lon
                    this_hop['hop_latitude'] = lat
                    results[probe_id]['status'] = True
                    results[probe_id]['status_reason'].append('RULE 5 RDNS found the  exit facility ' )
                    results[probe_id]['status_code'].append(0)
                    append_vptable_dict(2, this_hop['ip_from'],this_hop['hop_latitude'], this_hop['hop_longitude'],rname,this_facility,port,speed)
                    stats['2'] += 1
                else:
                    print(' RULE 5 found a rdns name but not a facility',rname,this_hop)
                    results[probe_id]['status'] = False
                    results[probe_id]['status_reason'].append('RULE 5 RDNS found a rdns name but Unable to find the  exit facility ' )
                    results[probe_id]['status_code'].append(7)
                    append_vptable_dict(5, this_hop['ip_from'],this_hop['hop_latitude'], this_hop['hop_longitude'],rname,'',port,speed)
                    stats['5'] += 1

        print('RULE 5(IXP) This hops Reversedns name is',rname)
        # input('wait')
        print(results)

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
        #input('wait')
        
    # rule 6 if this ip address hasnt been picked up by any of the above rules then it probably just needs locating via its rdns
    if not rule_flag:
        rule_flag = True
        rname = port = speed = ''
        print('ix_prefix_flag',hop,this_hop['ip_from'],ix_prefix_flag)
        addr=reversename.from_address(this_hop['ip_from'])
        try:
            rname = str(resolver.resolve(addr,"PTR")[0])
        except:
            print('RULE 6 didnt find a rname, this_hop',this_hop)
        this_hop['rdns'] = rname
        print('RULE 6 This hops Reversedns name is',rname)
        this_facility, coords = get_coords(this_hop,rname)

        if this_facility:
            lon = coords[0]
            lat = coords[1]
            print('RULE 6 before',this_hop['facility'],this_facility)
            this_hop['facility'].append(this_facility)
            print('RULE 6 after',this_hop['facility'],this_facility)
            this_hop['network'] = 0
            this_hop['hop_longitude'] = lon
            this_hop['hop_latitude'] = lat
            append_vptable_dict(2, this_hop['ip_from'],this_hop['hop_latitude'], this_hop['hop_longitude'],rname,this_facility,port,speed)
            stats['2'] += 1
        else:
            print(' RULE 6 found a rdns name but not a facility',rname,this_hop)
            append_vptable_dict(5, this_hop['ip_from'],this_hop['hop_latitude'], this_hop['hop_longitude'],rname,[],port,speed)
            stats['5'] += 1
        print('RULE6')

        #input('wait')
        
    # Rule 7 there is no rule 7
    if rule_flag == False:
        print('ohoh new rule required')
        input('Doh wait')
    print('END OF RULES')
    print('This Hop INFO', this_hop)
    print('prev_hop INFO', prev_hop)
    
   
    return this_hop, facilities_used, ixp_pre_hops,ixp_in_hops,ixp_post_hops

def get_coords(this_hop,rname):
    
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
    f= ''
    possible_facilitys = {}
    last_part = ''
    for this_rdns_partial_name in rdns_parts_list:
        '''
        be-1-ibr01-drt-red
        uk
        cdw
        com
        '''
        rdns_partial_list = re.findall("[a-zA-Z]{3,}", this_rdns_partial_name)
        print(rdns_parts_list,this_rdns_partial_name,rdns_partial_list)
        
        for this_part in rdns_partial_list:
            print('this part is', this_part)
            if this_part == 'com':
                break
            if this_part == 'net':
                break
            if this_part == 'anycast':
                break
            if this_part == 'ptr':
                break
            if this_part == 'unassigned':
                break
            #AQL are only in Leeds so 
            if last_part != 'lon' and this_part == 'aql':
                this_part = 'leeds'
            possible_facilitys[this_part] = {}
            for town in townset:
                print(town,this_part)
                town_lower = town.casefold()
                this_part_lower = this_part.casefold()
                if town_lower.startswith(this_part_lower):
                    
                    print(town, this_part,coords)
                    
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
            # this is mainly for AQLs benefit, if the interface is in LON then need to stop it being set to leeds
            last_part = this_part
    # now we have to work out which is the correct facility and what the coords of theme are
    # we do this by comparing which of the possible facilitys in the relevant town peer with the last ASNs network
    f=[]
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
                    print('ASN is',asn, this_hop['asn'])
                    #print(type(asn),type(this_hop['asn']))
                    if asn == this_hop['asn']:
                        print('WOOT', possible_facilitys[part])
                        # input('wait')
                        coords = (possible_facilitys[part][facil]['lon'],possible_facilitys[part][facil]['lat'])
                        f.append(facil) 
                        
                        # break
    if len(f) > 1:
        print(' We need to figure out which of these facilities is the correct one', f)
        # if both are in Leeds then we can select the Salem Church one (896) as they are failrly close together geographically
        # TODO: this may be a problem later as fac 2384 (aql DC5, Leeds) is mainly used by JISC, perhaps we can check for the JISC ASN
        # and then select 2384 instead
        if f[0] == '896' and f[1] == '2384':
            print('Both in leeds so removing 2384')
            f.remove('2384')
            #f= f[0]
            print('F is',f)
            coords = (possible_facilitys[part]['896']['lon'],possible_facilitys[part]['896']['lat'])
        input('wait')



    print('facilities are ',f,'and coords are',coords)
    # input('WOOT, wait')
                    
    return f,coords  


def main(argv):
    in_file = ''
    out_file = ''
    final_vptable_dict = {}
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
        out_file = 'results/tables/'+'results.json'
    else:
        out_file = 'results/tables/'+out_file
    if in_file == '':
        in_file = 'results/target_6087.json'
    else:
        in_file= 'results/'+in_file
    
    
    print('Input file is ?', in_file)
    print('Output file is ?', out_file)
    # Create the Vantage Point table
    # 
    
    global vptable_dict
    vptable_dict = {}
    
    
    #input('wait')
    
    
    
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
                    # BE CAREFUL IF RESETTING the 'uk_facilities to networks file' 
                    # because the reston data has been input manually
                    # ie
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
      
    


    ix_details_file = 'results/ix_details.json'
    # Make up a backup file of the dictionary in case we want to use it
    # but the dictionary can now be used.
    # ix_detail_dict now has a cross reference between Ip addresses and facilities.
    # These only include the LINX networks but more can be added to this
    # print(ix_detail_dict['195.66.224.74'])
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
    local_subnets = ['10.0.0.0/8', '172.16.0.0/16', '172.17.0.0/16', '172.18.0.0/16', '172.19.0.0/16', '172.20.0.0/16', '172.21.0.0/16', '172.22.0.0/16',
    '172.23.0.0/16', '172.24.0.0/16', '172.25.0.0/16', '172.26.0.0/16', '172.27.0.0/16', '172.28.0.0/16', '172.29.0.0/16', '172.30.0.0/16', '172.31.0.0/16', '192.168.0.0/24',
    '100.64.0.0/10']

    # Read in the UK Internet Exchange info
    #with open('peeringdb_test_results/uk_ixps.json') as f:
        #ixps_uk = json.load(f)

     
    
    #Create a list of Towns where facilities are located
    global townset
    townset = set(())
    towns = []
    for fac in facilitys_uk:
        townset.add(facilitys_uk[fac]['city'])
    # print(townset)

    # create a list of ipv4 prefixes for later use (ipv6 can wait for now)
        
    global ix_prefix_list 
    ix_prefix_list = []
    key = 'ipv4_prefix'
    for ix in ixps_uk:
        # print(ix)
        if key in ixps_uk[ix]:
            ix_prefix_list.append(ixps_uk[ix]['ipv4_prefix'])
        else:
            ixps_uk[ix]['ipv4_prefix']= []

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
    # test reverse dns
    #addr=reversename.from_address("185.74.25.250")
    #reversedns = str(resolver.resolve(addr,"PTR")[0])
    # print(reversedns)
    ResultsFile = "target_6087.json"
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
    stats['total'] = 0
    global measurement
    measurement =  {}
    for measurement_id in measurements:
        print(measurement_id)
        #('wait')

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
            global results
            results = {}
            probe_number = 0
            ixp_entry_point = ''
            #
            #Create the Source Probes
            for probe_id in measurements[measurement_id]['results']:
                print(probe_id)
                # Tests a single source probe
                #if probe_id != '6562':
                #    continue
                probe_number += 1
                print('PPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPP')
                print (probe_number,'Start of new Source Probe',probe_id,)
                print('PPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPP')
                # ixp_entered_id = 0
                ixp_entered_flag = False
                
                facilities_used[probe_id] = []
                # Only iterate through source probe's not the target probe
                if probe_id != this_target:
                    results[probe_id] = {}
                    results[probe_id]['status'] = False
                    results[probe_id]['status_reason'] = []
                    results[probe_id]['status_code'] = []



                    source_lon = measurements[measurement_id]['results'][probe_id]['source_coordinates'][0]
                    source_lat = measurements[measurement_id]['results'][probe_id]['source_coordinates'][1]
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



                    for hop in measurements[measurement_id]['results'][probe_id]['hops']:
                        stats['total'] += 1
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
                        this_hop, facilities_used, ixp_pre_hops,ixp_in_hops,ixp_post_hops = get_hop_location(ixp_pre_hops,ixp_in_hops,ixp_post_hops,facilities_used,this_target,probe_id,prev_hop, hop, this_hop_results,ixp_entered_flag)

                        print(this_hop)
                        
                        prev_hop = this_hop
                        results[probe_id][hop] = this_hop
                        print('%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%')
                    print(results[probe_id])
                    results_file = 'results/tables/'+probe_id+'_'+this_target+'.json'
                    print ('WRITING FILE',results_file)
                    with open(results_file, 'w') as f:
                        json.dump(results[probe_id], f)  
                                      
                    
                    vptable_filename = 'results/vptables/'+probe_id+'_'+this_target+'.json'
                    write_vptable_file(vptable_filename)
                    #lets clear the vptable each source probe for now, can always remove this when we are happy with results
                    final_vptable_dict.update(vptable_dict)
                    vptable_dict = {}
    final_vptable_filename = 'results/vptables/'+this_target+'.json'
    final_vptable_dict['stats'] = {}
    final_vptable_dict['stats'].update(stats)
    with open(final_vptable_filename, 'w') as f:
        json.dump(final_vptable_dict, f) 
    print(final_vptable_dict)
    print('FINAL VPTABLE WRITTEN TO ', final_vptable_filename)
    with open(out_file, 'w') as f:
        json.dump(results, f)                   
    print('RESULTS WRITTEN TO ', out_file)
    #input('wait')
if __name__ == "__main__":
    main(sys.argv[1:])
