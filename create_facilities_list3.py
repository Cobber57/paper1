# this one works but too many read requests
# Reads in each network. checks the facilities if it peers at ang GB facilities,
# and creates a list of networks organised by facility
# however this causes many read requests and eventually peeringdb stops providing results.
# Have sent an email to support@peeringdb.com



from pprint import pprint

from peeringdb import config, resource
from peeringdb.client import Client
from geopy.geocoders import Nominatim
import ipaddress
import json
geolocator = Nominatim(user_agent="aswindow")
pdb = Client()
pdb.update_all()
#pdb = peeringdb.PeeringDB()

# Area under analysis
area = 'UK'


#facilities = pdb.fetch_all(resource.Facility)
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

with open('peeringdb_test_results/uk_facilities_all_new.json', 'w') as outfile:
        json.dump(facilitys, outfile)
outfile.close()
            
'''

    

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
        facilitys_uk[fac] = {}
        facilitys_uk[fac]['org_id'] = f['org_id']
        facilitys_uk[fac]['name'] = f['name']
        facilitys_uk[fac]['address1'] = f['address1']
        facilitys_uk[fac]['address2'] = f['address2']
        facilitys_uk[fac]['city'] = f['city']
        facilitys_uk[fac]['country'] = f['country']
        facilitys_uk[fac]['postcode'] = f['zipcode']
        facilitys_uk[fac]['latitude'] = f['latitude']
        facilitys_uk[fac]['longitude'] = f['longitude']
        
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
        json.dump(facilitys_uk, outfile)
    outfile.close()
'''