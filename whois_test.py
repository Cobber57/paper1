from ipwhois import IPWhois
from ipwhois.asn import IPASN
obj = IPWhois('37.143.136.250')
# obj = IPWhois('164.39.242.16')
results = obj.lookup_rdap()

print(results)