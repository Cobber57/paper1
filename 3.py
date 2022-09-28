import prsw


import ipaddress
import json
from ipwhois.net import Net
from ipwhois.asn import ASNOrigin,IPASN

#from ixp_create_test_rectangle import create_ixp
# PRSW, the Python RIPE Stat Wrapper, is a python package that simplifies access to the RIPE Stat public data API.
import prsw
    
ripe = prsw.RIPEstat()


from peeringdb import PeeringDB, resource, config
pdb = PeeringDB()
# pdb.update_all() # update my local database
n = '37.143.136.250'

response = ripe.network_info(n)
print(response.prefix)
input('wait')
net = Net(n)

obj = IPASN(net)
results = obj.lookup()

print(results)


print('w is',w)  # print values of all found attributes

this_ip = '37.143.136.250'


# https://team-cymru.com/community-services/ip-asn-mapping/
f = open("team-cymru/list02", "r")
#print(f.read())

for line in f:
    print(line)
    
    prefix = [x.split() for x in line.split('|')]
    print(this_ip,prefix[2][0])

    if ipaddress.ip_address(this_ip) in ipaddress.ip_network(prefix[2][0]):
        print('asn  is')
        print(line.split('|')[0])
        break   
'''


# Workout location of Hop

#response = ripe.network_info('37.143.136.0')
#print(dir(response))
#print(response.asns)
'''