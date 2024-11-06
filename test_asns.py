import json 
from peeringdb import PeeringDB, resource, config
pdb = PeeringDB()

def convert(lst):
    my_dict = {}
    for l in lst:
        id = l['id']
        my_dict[id] = {}
        for key,value in l.items():
            my_dict[id][key] = value
    
    return my_dict

# Read in the prefixes info
with open('peeringdb_test_results/ipprefixes_all.json') as f:
    ipprefixes = json.load(f)


# Read in the networks info
with open('peeringdb_test_results/networks_all.json') as f:
    nets = json.load(f)

# Convert the networks file to a dictionary
networks = convert(nets)

# Read in the UK Internet Exchange info
with open('peeringdb_test_results/uk_ixps.json') as f:
    ixps_uk = json.load(f)

# Read in the UK Facilities records
with open('peeringdb_test_results/uk_facilities.json') as f:
    facilitys_uk = json.load(f)

# Open the measurements file created previously
# filename2 = 'measurements/uk_measurements.json' # for full uk_measurements

# with open("results/target_6087_source_6716.json") as f:
with open("results/target_6716_source_6087.json") as f:
    measurements =json.load(f)

#report_file= "results/6087_report.json"
report_file= "results/6716_report.json"

# filters = {"tags": "NAT", "country_code": "gb", "asn_v4": "3333"}
#filters = {"tags": "system-Anchor", "country_code": "gb"}
#probes = ProbeRequest(**filters)




ATLAS_API_KEY = "6f0e691d-056c-497d-9f5b-2297e970ec60"

# Add any facilities that may have been discovered manually
facilitys_uk['8628'] = {}
facilitys_uk['8628']["org_id"] = 26163
facilitys_uk['8628']["name"] = 'Datacenta Hosting'
facilitys_uk['8628']["address1"] = "Dorset Innovation Park" 
facilitys_uk['8628']["address2" ] = ""
facilitys_uk['8628']["city"] =  "Winfrith Newburgh"
facilitys_uk['8628']["country"] = "GB"
facilitys_uk['8628']["postcode"] = "DT2 8ZB"
facilitys_uk['8628']["latitude"] = 50.681852 
facilitys_uk['8628']["longitude"] = -2.256535




probe_list = []
uk_probes ={}
asn_list = []
addresses_list =[]
count = 0
add_count = 0
numberoffiles = 0

ASN1 = 43996
ASN2 = 25376

for network,values in networks.items():
    
    if values['asn'] == ASN1:
        print('The ASN1 network ', network)
        ASN1_network = networks[network]
        break
for network,values in networks.items():   
    if values['asn'] == ASN2:
        print('The ASN2 network ', network)
        ASN2_network = networks[network]
        break
if ASN1_network['netfac_set']:
    ASN1_netfac_ids = []
    print('ASN1',ASN1_network['netfac_set'])
    input('wait')
    for netfac in ASN1_network['netfac_set']:
        print('Network',ASN1_network['id'],'facilities are',ASN1_network['netfac_set'])
        print('this one is',netfac)
        netfac_info = pdb.fetch(resource.NetworkFacility, netfac)
        print('NETFAC INFO is', netfac_info[0])
        ASN1_netfac_ids.append(netfac_info[0]['fac_id'])

    

if ASN2_network['netfac_set']:
    ASN2_netfac_ids = []
    for netfac in ASN2_network['netfac_set']:
        
        print('Network',ASN2_network['id'],'facilities are',ASN2_network['netfac_set'])
        print('this one is',netfac)
        netfac_info = pdb.fetch(resource.NetworkFacility, netfac)
        print('NETFAC INFO is', netfac_info[0])
        ASN2_netfac_ids.append(netfac_info[0]['fac_id'])
print('ASN1 in SLOUGH is', ASN1, ' and its facilites are', ASN1_netfac_ids)
print('ASN2 in MANCHESTER is', ASN2, ' and its facilites are', ASN2_netfac_ids)
