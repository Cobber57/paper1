from peeringdb import config, resource
from peeringdb.client import Client
import inspect

pdb = Client()
# sync database with remote data
# unauthenticated to default URL unless configured
# since this is relatively slow, normally this would be done from cron - see CLI doc for example
#pdb.update_all()

# search by ix and name

ix = pdb.all(resource.Network)
print(ix)
input('wait')

# get a single record
n1 = pdb.get(resource.Network, 1)

net = pdb.tags.net              # type wrap

# both are equal
assert net.get(1) == n1

print(n1)

# query by parameter
print(pdb.all(resource.Network).filter(asn=2906))
# or
print(net.all().filter(asn=2906))

networks = pdb.fetch_all(resource.Network)
uk_facilities = {}
nets ={}
facilitys = {}
for n in networks:
    
    print(n)
    print(n['netfac_set'])
    facil = n['netfac_set']
    input('wait')