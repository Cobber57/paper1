
# now redundant as this software been moved to peeringdb_test
from peeringdb import PeeringDB, resource, config
import json
pdb = PeeringDB()
ipprefixes = pdb.fetch_all(resource.InternetExchangeLanPrefix)



with open('peeringdb_test_results/uk_ixps.json') as f:
        ixps_uk = json.load(f)
ixlans = []

for ixp in ixps_uk:
    
    print(ixp)
    print(ixps_uk[ixp])
    ixlans.append(ixp)
    for prefix in ipprefixes:
        print(prefix)
        print(ixp)
        print (prefix['ixlan_id'], prefix)
        
        if prefix['ixlan_id'] == int(ixp):
            if prefix['protocol'] == 'IPv4':
                ixps_uk[ixp]['ipv4_prefix'] = prefix['prefix']
            elif prefix['protocol'] == 'IPv6':
                ixps_uk[ixp]['ipv6_prefix'] = prefix['prefix']
    if 'ipv4_prefix' not in ixps_uk[ixp]:
        ixps_uk[ixp]['ipv4_prefix'] = ""
    if 'ipv6_prefix' not in ixps_uk[ixp]:
        ixps_uk[ixp]['ipv6_prefix'] = ""
            

with open('peeringdb_test_results/uk_ixps.json', 'w') as outfile:
    json.dump(ixps_uk, outfile)
outfile.close()


    

