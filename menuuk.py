# Uk Menu
import os
import json

from peeringdb import PeeringDB, resource, config
pdb = PeeringDB()
from ripe.atlas.cousteau import ProbeRequest, Traceroute, AtlasSource, AtlasRequest, AtlasCreateRequest

menu = {}
menu['1']="Create world measurements towards a specific target" 
menu['2']="Create IP prefixes file"
menu['3']="create Networks file"
menu['4']="Create Source probes file"
menu['9']="Exit"
while True: 
    options=menu.keys()
    
    for entry in options: 
        print(entry, menu[entry])

    selection=input("Please Select:") 
    if selection =='1': 
        prefix = input('What is Target prefix , must be a /24 and only enter first 3 octets, (ie 100.0.0.0) ')
        country = input('What is country of hijacking AS ')
        filesaved = input('What is filename to save measurement info to ')
        print (' prefix is ', prefix)
        print ('Country to select source probes is ',country)
        print ('filename to save measurement info is ',filesaved)
        answer = input('is this correct y/n 1')
        if answer == 'y':
            textfile = 'python create_world_measurements.py '+prefix+' '+country+' '+ filesaved
            os.system(textfile)


    elif selection == '2': 
        networks = pdb.fetch_all(resource.Network)

        with open('peeringdb_test_results/networks_all.json', 'w') as outfile:
            json.dump(networks, outfile)
        outfile.close()
    elif selection == '3':
        ipprefixes = pdb.fetch_all(resource.InternetExchangeLanPrefix) 
        with open('peeringdb_test_results/ipprefixes_all.json', 'w') as outfile:
            json.dump(networks, outfile)
    
    elif selection == '9': 
        break
    else: 
        print("Unknown Option Selected!")