import requests
import re
import json
#164.39.242.16 works
#138.197.249.118' latest error from code ARIN

# https://stat.ripe.net/data/network-info/data.json?resource=37.143.136.250 last error RIPE
# get('https://rest.db.ripe.net/search.json?query-string=138.197.249.118&flags=no-referenced&flags=no-irt&source=RIPE')
#x = requests.get('https://rest.db.ripe.net/search.json?query-string=37.143.136.250&type-filter=route&flags=no-referenced&flags=no-irt&source=RIPE')
ripe_url = 'https://rest.db.ripe.net/search.json'
options = {
    'query-string' : '164.39.242.17',
    'type-filter' : 'route',
    'flags' : ['no-irt','no-referenced'],
    'source' : 'RIPE'
    }

r = requests.get(ripe_url, params=options)
print (r.status_code)
                    

if r.status_code == 200:
    x = r.json()
    print(x)
    attributes = x['objects']['object'][0]['attributes']['attribute']
    for attrib in attributes:
        print(attrib)
        if attrib['name'] == 'origin':
            ripedb_asn = attrib['value']
            print(ripedb_asn)
            # had to make this overly complex change because i  swapped from using RIPE stat to RIPE database
            asns = [int(re.split('AS|as',ripedb_asn)[1])]
            print(ripedb_asn,asns )
'''
url = 'https://rest.db.ripe.net/search'
options = {
    'query-string' : '138.197.249.118',
    'type-filter' : 'route',
    'flags' : ['no-irt','no-referenced'],
    'source' : 'APNIC-GRS'
    }

x = requests.get(url, params=options).json()

attributes = x['objects']['object'][0]['attributes']['attribute']



for attrib in attributes:
    if attrib['name'] == 'origin':
        asn = attrib['value']

print(asn)
'''

