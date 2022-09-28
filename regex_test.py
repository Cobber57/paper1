import re
from peeringdb import PeeringDB, resource, config
import json
pdb = PeeringDB()

# Read in the UK Facilities records
townset = set(())
with open('Documents/UK/peeringdb_test_results/uk_facilities.json') as f:
     facilitys_uk = json.load(f)
# with open('uk_facilities_no_coords.json') as f:
   
towns = []
for fac in facilitys_uk:
    townset.add(facilitys_uk[fac]['city'])
print(townset)

rname = 'be-1-ibr01-drt-red.uk.cdw.com.'
rdns_parts_list =rname.split('.')
for this_rdns_partial_name in rdns_parts_list:
    rdns_partial_list = re.findall("[a-zA-Z]{3,}", this_rdns_partial_name)
    print(rdns_parts_list,this_rdns_partial_name,rdns_partial_list)

    for this_part in rdns_partial_list:
        print('this part is', this_part)
        for town in townset:
            print(town,this_part)
            town_lower = town.casefold()
            this_part_lower = this_part.casefold()
            if town_lower.startswith(this_part_lower):
                print(town, this_part,)
                input('WOOT, wait')


input('booowait')



coords = (51.2477342160338, -0.15708547962421623)
    
for fac in facilitys_uk:
    this_facility = facilitys_uk[fac]
    print(fac,facilitys_uk[fac])
    if this_facility["city"] == 'Redhill':
        print ('YES')
        input('wait')
    