#from peeringdb.client import PeeringDB, resource
import peeringdb

from pprint import pprint

import django
from peeringdb import PeeringDB, resource, config
from geopy.geocoders import Nominatim
import ipaddress
import json
geolocator = Nominatim(user_agent="aswindow")

pdb = peeringdb.PeeringDB()

# Area under analysis
area = 'UK'
'''
# Ip addresses listed by IXPs in this area on PCH.net
ixp_ips = ['196.223.14', '196.223.30', '196.10.140', '196.223.22',
    '196.10.141', '196.60.8', '196.60.9', '196.60.10', '196.60.11']
# Additional Ip Addresses being used by IXP's
ixp_unknown_ips = ['105.22.46', ]
'''


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



#print(ipaddress.ip_address('206.126.240.1') in ipaddress.ip_network('206.126.236.0/22'))

# pprint(dir(peeringdb))

# https://github.com/grizz/pdb-examples
# EXAMPLE SCRIPT lookup network by ASN
#pdb.update_all()
#print ("TAGS")
#pprint(dir(pdb.tags.ix.all))

# pprint(dir(geolocator))

'''

'Class',
 'Facility',
 'InternetExchange',
 'InternetExchangeFacility',
 'InternetExchangeLan',
 'InternetExchangeLanPrefix',
 'Meta',
 'Network',
 'NetworkContact',
 'NetworkFacility',
 'NetworkIXLan',
 'OrderedDict',
 'Organization',
 'RESOURCES_BY_TAG',

 '''
ixes = 0
exc = pdb.fetch_all(resource.InternetExchange)
fac_id = pdb.fetch_all(resource.InternetExchangeFacility)
facility = pdb.fetch_all(resource.Facility)
ipprefixes = pdb.fetch_all(resource.InternetExchangeLanPrefix)
#networks = pdb.fetch_all(resource.Network)
# Convert the networks file to a dictionary
# networks = convert(nets)

#print(networks[0])
input('wait')
ixps_uk = {}

facilitys_uk = {}
fac_list =[]




# Do we want to read directly from Peeringdb or from files that have been created
# set to False to read from files
read_from_pdb = True

# do we want to write results to new set of files, only works when read_from_dpb is = true
write_to_files = True

# Start
if read_from_pdb == True:


    # Create a dictionary of UK IXPS and the facilities they use
    for ix in exc:
        
        if ix['country'] == 'GB':
            
            
            print('===========================================')
            print(ixes,ix['name'], ix['org_id'])

            #print(ix)
            ixps_uk[ix['id']] = {}
            ixps_uk[ix['id']]['name'] = [ix['name']]
            ixps_uk[ix['id']]['org_id'] = [ix['org_id']]
            ixps_uk[ix['id']]['fac_set'] = [ix['fac_set']]
            ixps_uk[ix['id']]['ixlan_set'] = [ix['ixlan_set']]

            #print(ixps_uk)
            #print(ixps_uk[ix['name']]['fac_set'][0])

            #print('===========================================')
            #exchanges[ixes] = ix
            ixes += 1
            facs = 0
            
            # Create a dictionary of Uk Facilities and their locations
            for fac in ix['fac_set']:
                print(fac)
                # input("wait")
                if fac not in facilitys_uk:
                    print('facility wasnt in facilitys_uk') 
                    f = pdb.fetch(resource.Facility, fac)
                    print('Facility',facs,f)
                    
                    print(f[0]['id'], f[0]['org_id'])
                    facilitys_uk[fac] = {}
                    facilitys_uk[fac]['org_id'] = f[0]['org_id']
                    facilitys_uk[fac]['name'] = f[0]['name']
                    facilitys_uk[fac]['address1'] = f[0]['address1']
                    facilitys_uk[fac]['address2'] = f[0]['address2']
                    facilitys_uk[fac]['city'] = f[0]['city']
                    facilitys_uk[fac]['country'] = f[0]['country']
                    facilitys_uk[fac]['postcode'] = f[0]['zipcode']
                    facilitys_uk[fac]['latitude'] = f[0]['latitude']
                    facilitys_uk[fac]['longitude'] = f[0]['longitude']
                    fac_list.append(fac)
                    print(len(fac_list),fac_list)
                    facs += 1
                

                    # check if facility has coordinates
                    
                    if facilitys_uk[fac]['latitude'] == None:
                        full_address = facilitys_uk[fac]['address1']+','+facilitys_uk[fac]['address2']+','+facilitys_uk[fac]['city']
                        location = geolocator.geocode(full_address)
                        if location != None:
                            facilitys_uk[fac]['latitude'] = location.latitude
                            facilitys_uk[fac]['longitude'] = location.longitude
                            print(location,location.latitude, location.longitude)
                            
                        
                        else:
                            #list of facilities that didnt manage to get location from Nominatum
                            if fac == 1548:
                                facilitys_uk[fac]['latitude'] = 51.5548
                                facilitys_uk[fac]['longitude'] = -3.0382 
                            # if facility isnt in list then need to do some manual location finding and
                            # add it to the list above
                            else: 
                                print ('OOps no coordinates')
                                print(facilitys_uk[fac])
                                input('wait')
                    

            ixs = 1
            # print(facilitys_uk)
            print('Number of facilities = ',facs)
            print('Number of ixes = ', ixes)
            input('wait')
    
    # Now we can add the IP prefixes to the IX records to make life simpler
    ixlans = []
    for ixp in ixps_uk:
    
        # ixlans.append(ixp)
        for prefix in ipprefixes:
            #print(prefix)
            #print(ixp)
            #print (prefix['ixlan_id'], prefix)
            
            if prefix['ixlan_id'] == int(ixp):
                if prefix['protocol'] == 'IPv4':
                    ixps_uk[ixp]['ipv4_prefix'] = prefix['prefix']
                elif prefix['protocol'] == 'IPv6':
                    ixps_uk[ixp]['ipv6_prefix'] = prefix['prefix']
                


    if write_to_files == True:
        with open('peeringdb_test_results/uk_ixps_new.json', 'w') as outfile:
            json.dump(ixps_uk, outfile)
        outfile.close()

        with open('peeringdb_test_results/uk_facilities_new.json', 'w') as outfile:
            json.dump(facilitys_uk, outfile)
        outfile.close()

else:
    with open('peeringdb_test_results/uk_ixps.json') as f:
        ixps_uk = json.load(f)
        

    with open('peeringdb_test_results/uk_facilities.json') as f:
        facilitys_uk = json.load(f)

    # Below is an example of a search of the uk prefixes
    num = 0
    num1 = 0
    for facility in facilitys_uk:
        num += 1
        print(num,facility)
    for ixp in ixps_uk:
        num1 +=1
        print(num1,ixp)
    
    '''
    for ippre in ipprefixes:
        if ipaddress.ip_address('195.66.225.234') in ipaddress.ip_network(ippre['prefix']):
            print(ippre)
            print (ippre['ixlan_id'])
            print (ixps_uk[str(ippre['ixlan_id'])]['fac_set'])
            print(fac_list)
            for facility in ixps_uk[str(ippre['ixlan_id'])]['fac_set'][0]:
                print(facility)
                print(facilitys_uk[str(facility)])
                input('wait')
    
    '''


# ignore from here onwards as its all to do with the networks
# maybe work for later on when looking at the ASes and their networks
'''
        for ix_lan in ix['ixlan_set']:
            print('++++++++++++++++++++++++++++++++++++++++++++++++++++')
            print(ix_lan)
            i = pdb.fetch(resource.InternetExchangeLan, ix_lan)
            print('Ix Lan',ixs,i)
            nets = 1
            print(i[0]['net_set'])
            input("wait")
            
            
           
            
            for net in i[0]['net_set']:
    
                print('---------------------------------------------------------')
                print(net)
                n = pdb.fetch(resource.Network, net)
                print('Network',nets,n)
                print('---------------------------------------------------------')
                nfacs = 1
                input("wait")
                for nf in n[0]['netfac_set']: # ties the facility into the netset
                    print('fffffffffffffffffffffffffffffffffffffffffffffff')
                    print(nf)
                    nfac = pdb.fetch(resource.NetworkFacility, nf)
                    print('Network Facilities',nfacs,nfac)
                    print('ffffffffffffffffffffffffffffffffffffffffffffffff')
                    nfacs += 1
                    
                ixlans = 1
                
                for ixl in n[0]['netixlan_set']: 
                    print('nnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnn')
                    print(ixl)
                    ixlan = pdb.fetch(resource.NetworkIXLan, ixl)
                    print('Network IXLAN',ixlans,ixlan)
                    print('nnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnn')
                    ixlans += 1
                    input("wait")
                nets += 1
            print('++++++++++++++++++++++++++++++++++++++++++++++++++++')
            ixs += 1

#print(exc[287])
print(fac[0])
'''
