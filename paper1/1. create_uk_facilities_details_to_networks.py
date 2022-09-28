# Reads in each network. checks the facilities if it peers at any GB facilities,
# and creates a list of networks organised by facility
# however this causes many read requests and eventually peeringdb stops providing results.
# This one also adds the details of each fac to keep all info in one place

# Have sent an email to support@peeringdb.com

# NOTE: Dont forget to do a #peeringdb sync at the command line first to update the tables

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
area = 'GB'

networks = pdb.fetch_all(resource.Network)
facility = pdb.fetch_all(resource.Facility)
netfac = pdb.fetch_all(resource.NetworkFacility)
uk_facilitys = {}
uk_asns = []
fac_list =[]
nets ={}
net_n = 0
facs_n = 0
# try:
for n in netfac:
    
    if n['country'] == 'GB':
        net_n += 1
        
        fac = n['fac_id']
        asn = n['local_asn']
        net = n['net_id']

        if fac not in uk_facilitys:
            f = pdb.fetch(resource.Facility, fac)
            uk_facilitys[fac] = {}
            nets[fac] = []
            facs_n += 1

            uk_facilitys[fac] = {}
            uk_facilitys[fac]['org_id'] = f[0]['org_id']
            uk_facilitys[fac]['name'] = f[0]['name']
            uk_facilitys[fac]['address1'] = f[0]['address1']
            uk_facilitys[fac]['address2'] = f[0]['address2']
            uk_facilitys[fac]['city'] = f[0]['city']
            uk_facilitys[fac]['country'] = f[0]['country']
            uk_facilitys[fac]['postcode'] = f[0]['zipcode']
            uk_facilitys[fac]['latitude'] = f[0]['latitude']
            uk_facilitys[fac]['longitude'] = f[0]['longitude']
            fac_list.append(fac)
            if uk_facilitys[fac]['latitude'] == None:
                full_address = uk_facilitys[fac]['address1']+','+uk_facilitys[fac]['address2']+','+uk_facilitys[fac]['city']
                location = geolocator.geocode(full_address)
                if location != None:
                    uk_facilitys[fac]['latitude'] = location.latitude
                    uk_facilitys[fac]['longitude'] = location.longitude
                    print(location,location.latitude, location.longitude)
                    
                
                else:
                    #list of facilities that didnt manage to get location from Nominatum
                    if fac == 1548:
                        uk_facilitys[fac]['latitude'] = 51.5548
                        uk_facilitys[fac]['longitude'] = -3.0382 
                    if fac == 438:
                        uk_facilitys[fac]['latitude'] = 53.46173930900856
                        uk_facilitys[fac]['longitude'] = -2.238477402437006
                    if fac == 1027:
                        uk_facilitys[fac]['latitude'] = 51.65233068848927
                        uk_facilitys[fac]['longitude'] = -0.05506174363571605
                    if fac == 1684:
                        uk_facilitys[fac]['latitude'] = 53.46079870865286
                        uk_facilitys[fac]['longitude'] = -2.3238013877644064
                    if fac == 1793:
                        uk_facilitys[fac]['latitude'] = 51.24768870880858
                        uk_facilitys[fac]['longitude'] = -0.15714624340282543
                    if fac == 2384:
                        uk_facilitys[fac]['latitude'] = 53.79241801187366
                        uk_facilitys[fac]['longitude'] = -1.540471925077685
                    if fac == 3213:
                        uk_facilitys[fac]['latitude'] = 52.47729951633814
                        uk_facilitys[fac]['longitude'] = -1.8771037589558874
                    if fac == 5441:
                        uk_facilitys[fac]['latitude'] = 51.44679783988321
                        uk_facilitys[fac]['longitude'] = -0.4541687124105929
                    

                    # if facility isnt in list then need to do some manual location finding and
                    # add it to the list above
                    else: 
                        print ('OOps no coordinates')
                        print(fac, uk_facilitys[fac])
                        input('wait')
        
        
        if asn not in uk_asns:
            uk_asns.append(asn)

        nets[fac].append(net)
        nets[fac].append(asn)
        uk_facilitys[fac]['networks'] = nets[fac]

        
         





        # print(uk_facilitys)
        print('number of facilities = ', len(uk_facilitys),facs_n)
        print('length',len(fac_list),fac_list)
        print('number of asns/networks = ', len(uk_asns))
# with open('peeringdb_test_results/uk_facilities_and_details_to_networks_and_asns_new.json', 'w') as outfile:
    #json.dump(uk_facilitys, outfile)
    
#outfile.close()
            
'''            
except:
    print('an error occurred')   
    print(n)
    input('wait')
finally:
    print('number of facilities = ', len(uk_facilitys))
    print('number of asns/networks = ', len(uk_asns))
    
    with open('peeringdb_test_results/uk_facilities_all3.json', 'w') as outfile:
        json.dump(uk_facilitys, outfile)
        print(net_n)
    outfile.close()
'''
'''
facilities = pdb.fetch_all(resource.Facility)
uk_facilities = {}
fac_num = 0
for fac in facilities:
    if fac['country'] == 'GB':
        fac_num += 1
        print(fac_num,fac)
        
        
print(fac_num)



networks = pdb.fetch_all(resource.Network)
uk_facilities = {}
nets ={}
facilitys = {}
for n in networks:
    #print(n['netfac_set'])
    facil = n['netfac_set']
    fac_id = [] 
    
    print (n['id'],n)
    for fac in facil:
        print(fac)
        netfac_info = pdb.fetch(resource.NetworkFacility, fac)
        print(netfac_info[0]['country'])
        if netfac_info[0]['country'] == 'GB':
            fac_id = netfac_info[0]['fac_id']
            asn = netfac_info[0]['net']['asn']
            print(netfac_info)
            #input('wait')
            if fac_id not in facilitys:
                facilitys[fac_id] = {}
                nets[fac_id] = []
            print(fac_id)
            print(nets[fac_id])
            nets[fac_id].append(n['id'])
            nets[fac_id].append(asn)
            facilitys[fac_id] = nets[fac_id] 


            print(facilitys)

with open('peeringdb_test_results/uk_facilities_all.json', 'w') as outfile:
        json.dump(facilitys, outfile)
outfile.close()
            
# This is where old program ended 

    

# nets = {349: {}, 916: {}, 1282: {}, 1466: {}, 1554: {}, 1555: {}, 1556: {}, 1557: {}, 2314: {}, 2963: {}, 3658: {}, 3719: {123}, 4246: {}, 5040: {}, 5086: {}, 5230: [6535,123,345]}
final_nets = {}
for x in nets:
    
    if nets[x] == {}:
        print(x,'nothing')
    else:

        final_nets[x] = nets[x] 
        print(x,nets[x])
print(final_nets)

with open('peeringdb_test_results/networks_to_uk_facilities_all.json', 'w') as outfile:
    json.dump(final_nets, outfile)
outfile.close()
input('stop')
facilities_uk = {}
fac_list =[]

facs = 0
            
           
# Create a dictionary of Uk Facilities and their locations
for f in facilities:
    print(f)
    if f['country'] == 'GB' or fac['country'] == 'UK':
        print('GB)')
        input("wait")
        # f = pdb.fetch(resource.Facility, fac)
        fac = f[0]['id']
        print('Facility',facs,fac)
        uk_facilitys[fac] = {}
        uk_facilitys[fac]['org_id'] = f['org_id']
        uk_facilitys[fac]['name'] = f['name']
        uk_facilitys[fac]['address1'] = f['address1']
        uk_facilitys[fac]['address2'] = f['address2']
        uk_facilitys[fac]['city'] = f['city']
        uk_facilitys[fac]['country'] = f['country']
        uk_facilitys[fac]['postcode'] = f['zipcode']
        uk_facilitys[fac]['latitude'] = f['latitude']
        uk_facilitys[fac]['longitude'] = f['longitude']
        
        facs += 1

        # check if facility has coordinates

        if uk_facilitys[fac]['latitude'] == None:
            full_address = uk_facilitys[fac]['address1']+','+uk_facilitys[fac]['address2']+','+uk_facilitys[fac]['city']
            location = geolocator.geocode(full_address)
            if location != None:
                uk_facilitys[fac]['latitude'] = location.latitude
                uk_facilitys[fac]['longitude'] = location.longitude
                print(location,location.latitude, location.longitude)
                
            
            else:
                #list of facilities that didnt manage to get location from Nominatum
                if fac == 1548:
                    uk_facilitys[fac]['latitude'] = 51.5548
                    uk_facilitys[fac]['longitude'] = -3.0382 
                # if facility isnt in list then need to do some manual location finding and
                # add it to the list above
                else: 
                    print ('OOps no coordinates')
                    print(uk_facilitys[fac])
                    input('wait')
    

ixs = 1
# print(uk_facilitys)
print('Number of facilities = ',facs)

# Now we can add the IP prefixes to the IX records to make life simpler
ixlans = []
for ixp in ixps_uk:

    # ixlans.append(ixp)
    for prefix in ipprefixes:
        print(prefix)
        print(ixp)
        print (prefix['ixlan_id'], prefix)
        
        if prefix['ixlan_id'] == int(ixp):
            if prefix['protocol'] == 'IPv4':
                ixps_uk[ixp]['ipv4_prefix'] = prefix['prefix']
            elif prefix['protocol'] == 'IPv6':
                ixps_uk[ixp]['ipv6_prefix'] = prefix['prefix']
            

    with open('peeringdb_test_results/uk_facilities_all.json', 'w') as outfile:
        json.dump(uk_facilitys, outfile)
    outfile.close()
'''