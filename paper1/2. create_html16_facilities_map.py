#!/usr/bin/env python
# takes all the facilities
# fully working upto finding the correct IXP entry and exit points
# and creates the map
# now need to
#  1. Most important, calculate the distances from ixp exit point to target 
#  2. compare results with result from CBG, and RIPEMAP 
#  3. force the route to go via the xp
#  4. display the additional colocation facilities
#  5. route via the colocation facilities
#  6. test method on unkown targets
#  7. test method on bgpstream hijack results 
# Creates a list of UK anchors, reads in a measurements file and creates the html files for each
# requries my Htmlcreate13.py 

def create_header_html(filename):           
       
        central_lon = -2.23                                  # central lon coordiantes
        central_lat = 52.369                                  # central lat coordiantes

        # write default head info to new file
        
        cmd2 = 'chmod ' +'766 '+ filename
        cmd = 'cp html/head.html '+ filename
                
        os.system(cmd)
        # Fix File Permisssions
        os.system(cmd2)
                
        # Write latitude and longitude to html file for zoom location
        # open file 
        
        ip = open(filename, 'a')
        
        # centre of map is focused on target lat and lon       
        ip.write(str(central_lat)+", "+str(central_lon)+'], 12);\n')
        ip.close()
        

        # write tilelayer information to html file
        cmd = 'cat html/tilelayer.html >> '+ filename
        os.system(cmd)
        

def close_file(filename):
        ip = open(filename, 'a')
        # Complete Script and write to file
        #ip.write(string7 +'asnumber'+string5+'owner'+string8)
        string9 = "    </script>\n  </body>\n</html>"
        ip.write (string9)
        ip.close() 
    
def create_facility(filename, fac, facility, organisation):
    ip = open(filename, 'a')
    
    string6 = 'var bounds_' # = [[ # 37.767202, -122.456709], [37.766560, -122.455316]]; 
    stringa = 'var rectangle_'
    stringb = ' = L.rectangle(bounds_'
    stringc = ', {color: "black", fillColor: 0, fillOpacity: 0, weight: 4 }).addTo(map);\n'
    stringd = ', {color: "blue", fillColor: 0, fillOpacity: 0, weight: 4 });\n'
    string3 = '        ]).addTo(map);\n'
    string4 = 'rectangle_'
    string4a= '.bindPopup("<b>IXP '
    
    string5 = '</b><br /> ");\n'

    string7 = 'var polylinePoints = [['
    string8 = 'var polyline_' 
    string8a = 'polyline_'   
    string9 = ' = L.polyline(polylinePoints, {color: "black", weight: 2});\n'

    spacer1 = "        ["
    spacer2 = "],\n"

    fac_str = str(fac)

    
    fac_organisation = organisation['name']
    fac_address = organisation['address']
    fac_city = organisation['city']
    fac_country = organisation['country']
    fac_website = organisation['website']
    
    

    
    # print(fac_str, ixp_info['fac_set'][0][0])
    
    rec_lat1 = str(facilitys_uk[fac_str]['latitude'] + .001)
    rec_lat2 = str(facilitys_uk[fac_str]['latitude'] - .001)
    rec_lon1 = str(facilitys_uk[fac_str]['longitude'] - .001)
    rec_lon2 = str(facilitys_uk[fac_str]['longitude'] + .001)

    # print ( 'FIRST FAC =',first_facility, first_facility_lat,first_facility_lon)
    #create the IXP Rectangle at the first facilties location
    ip.write ('      //  Facility '+fac_str+'\n')
    ip.write(string6 +fac_str+' = [['+rec_lat1 +',' +rec_lon1 +'],[' +rec_lat2+',' +rec_lon2 +']];\n')
    ip.write(stringa + fac_str+stringb+fac_str+stringc)  
    ip.write(string4 
    + fac_str
    + string4a
    +' Facility '+fac_str
    +"<br />"
    + facilitys_uk[fac_str]['name']
    +"<br />"
    + facilitys_uk[fac_str]['address1']
    +"<br />"
    +' Administration by:- <br />'
    + fac_organisation+'<br />'
    +fac_address +'<br />'
    +fac_city +'<br />'
    +fac_country+'<br />'
    +fac_website
    +string5)



def convert(lst):
    my_dict = {}
    for l in lst:
        id = l['id']
        my_dict[id] = {}
        for key,value in l.items():
            my_dict[id][key] = value
    
    return my_dict



if __name__ == "__main__":
    
    from Htmlcreate15 import Html_Create # my htmlcreate module
    from ripe.atlas.cousteau import ProbeRequest, Traceroute, AtlasSource, AtlasRequest, AtlasCreateRequest
    from datetime import datetime
    import time
    import json 
    import os
    from geopy.geocoders import Nominatim
    from geopy.distance import geodesic
    # from haversine import haversine
    import great_circle_calculator.great_circle_calculator as gcc
    # PRSW, the Python RIPE Stat Wrapper, is a python package that simplifies access to the RIPE Stat public data API.
    import prsw
    import ipwhois
    import re

    import ipaddress
    import json

    #from ixp_create_test_rectangle import create_ixp


    from peeringdb import PeeringDB, resource, config
    pdb = PeeringDB()
    pdb.update_all() # update my local database

    filename = 'web_files_results/uk_facilities.html'

    # https://pypi.org/project/prsw/
    # Check RPKI validation status TODO: this not currently implemented
    # print(ripe.rpki_validation_status(3333, '193.0.0.0/21').status)
    # Find all announced prefixes for a Autonomous System
    # prefixes = ripe.announced_prefixes(3333)
    # however this returns multiple ASNs for a given prefix, prbably best using the RIPE database for this
    ripe = prsw.RIPEstat()
    # import request so can access the RIPE database REST API 
    import requests
    ripe_url = 'https://rest.db.ripe.net/search.json'

    #remote peering facilities
    #bso.co, bics
    colocation = { 'bso1': 'manchester', 'bso2':'edinburgh', 'bso3': 'london', 'bics1' : 'london', 'epsilon1' : 'london', 'telia1' : 'manchester', 'telia2': 'london', 'telia3' : 'slough'}


    

    local_subnets = ['10.', '172.16.', '172.17.', '172.18.', '172.19.', '172.20.', '172.21.', '172.22.',
'172.23.', '172.24.', '172.25.', '172.26.', '172.27.', '172.28.', '172.29.', '172.30.', '172.31.', '192.168.',
'100.64.', '100.65.', '100.66.', '100.67.', '100.68.', '100.69.',
'100.70.', '100.71.', '100.72.', '100.73.', '100.74.', '100.75.', '100.76.', '100.77.', '100.78.',
'100.79.', '100.80.', '100.81.', '100.82.', '100.83.', '100.84.', '100.85.', '100.86.', '100.87.',
'100.88.', '100.89.', '100.90.', '100.91.', '100.92.', '100.93.', '100.94.', '100.95.', '100.96.',
'100.97.', '100.98.', '100.99.', '100.100.', '100.101.', '100.102.', '100.103.', '100.104.', '100.105.',
'100.106.', '100.107.', '100.108.', '100.109.', '100.110.', '100.111.', '100.112.', '100.113.', '100.114.',
'100.115.', '100.116.', '100.117.', '100.118.', '100.119.', '100.120.', '100.121.', '100.122.', '100.123.',
'100.124.', '100.125.', '100.126.', '100.127.']


    # If need to refresh  prefixes and networks run the 2 commands below instead of open
    # dont forget to remove the open statements. Could also create these files from menuuk.py
    # ipprefixes = pdb.fetch_all(resource.InternetExchangeLanPrefix)
    # nets = pdb.fetch_all(resource.Network)

    
    # Read in the UK Facilities records
    with open('peeringdb_test_results/uk_facilities_and_details_to_networks_and_asns.json') as f:
        facilitys_uk = json.load(f)

    # Open the measurements file created previously
    # filename2 = 'measurements/uk_measurements.json' # for full uk_measurements
 


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
    facilitys_uk['8628']["networks"] = []

    organisation = {}



    # Read in facilities
    create_header_html(filename)          # create the file 
    for facility in facilitys_uk:  
        f = pdb.fetch(resource.Facility, facility)
        
        organisation['name'] = f[0]['org']['name']
        organisation['address'] = f[0]['org']['address1']
        organisation['city'] = f[0]['org']['city']
        organisation['country'] = f[0]['org']['country']
        organisation['website'] = f[0]['org']['website']  
         
        create_facility(filename,facility,facilitys_uk[facility],organisation)
        
            

    close_file(filename) 
    print ('Copy ', filename ,' upto web server')

   