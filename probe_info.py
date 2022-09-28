# Creates the measurements between 34 anchors in the UK and adds the measurment info to a file in the measurments folder
# for use in a application to read that info and make use of it.

from ripe.atlas.cousteau import ProbeRequest, Traceroute, AtlasSource, AtlasRequest, AtlasCreateRequest
from datetime import datetime
import time
import json 
import os
from geopy.geocoders import Nominatim

def create_header_html(probe_dict):
        
        filename = 'web/probes.html'
        
        
        central_lon = -1.23                                  # central lon coordiantes
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
        
        print(central_lat,central_lon)
        
        ip.write(str(central_lat)+", "+str(central_lon)+'], 12);\n')
        ip.close()
        

        # write tilelayer information to html file
        cmd = 'cat html/tilelayer.html >> '+ filename
        os.system(cmd)

def create_probes(probe_id, probe_dict):

    filename = 'web/probes.html'

    asn             = probe_dict[probe_id]['probe_asn']
    ip_address      = probe_dict[probe_id]['probe_ip']
    lon             = probe_dict[probe_id]['probe_x']
    lat             = probe_dict[probe_id]['probe_y']
    #hops            = probe_dict[probe_id]['Hops']

    group_name = "group" + str(probe_id)
    target_name = "target_" + str(probe_id)
    ip = open(filename, 'a')
    

    # create ipaddress points on map in green circles
    stringa = "      var circle"
    stringb = " = L.circle(["
    string1 = "      // show the area of operation of the AS on the map\n      var polygon = L.polygon([\n"
    string2 = "], { color: 'red', fillColor: '#00', interactive: false, fillOpacity: 0.0, radius: "
    string21 = "], { color: 'red', fillColor: '#8000000', fillOpacity: 0.5, radius: "
    string22 = "], { color: 'blue', fillColor: '#8000000', fillOpacity: 0.5, radius: "
    string23 = "], { color: 'red', fillColor: '#00', interactive: false, fillOpacity: 0.0, radius: "
    string24 = "], { color: 'red', fillColor: '#8000000', fillOpacity: 0.5, radius: "
    string25 = "], { color: 'yellow', fillColor: '#8000000', fillOpacity: 0.5, radius: "
    string2a = " }).addTo(map);"


    string3 = "        ]).addTo(map);\n"
    string4 = '      polygon.bindPopup("<b>AS'
    string5 = '</b><br />'
    string6 = '<br />Area of Operation");\n'
    string7 = '      circle.bindPopup("<b>Probe '
    string7a ='      circle'
    string7b ='.bindPopup("<b>Probe '
    string7c ='.bindPopup("<b>Target '
    string8 = ' ").openPopup();\n\n'
    string8a = ' ");\n\n'
    spacer1 = "        ["
    spacer2 = "],\n"
    
    # show all landmarks on map
        
        
    ip = open(filename, 'a') 

    ip.write ('      // Probe '+str(probe_id)+'\n')

    # Create Green Probe location - These are probes used in the calculation
    ip.write(stringa + str(probe_id)+stringb+str(lat)+ ','+str(lon)+string21+str(500)+string2a+'\n')  
    # Create Probe Popup
    ip.write(string7a +str(probe_id)+string7b+str(probe_id) + string5 + 'AS '+str(asn)+"<br />" + str(ip_address) + "<br />" +string8a)

    # Create Feature group Layer and Checker

    ip.write("      var "+group_name+" = L.featureGroup();\n")
    #ip.write("     "+group_name+".bindPopup('"+group_name+"');\n")
    ip.write("      circle"+str(probe_id)+".on('click', function(e) {if(map.hasLayer("+group_name+")){\n")
    ip.write("        map.removeLayer("+group_name+"); ")
    ip.write("        map.removeLayer("+target_name+"); }\n")
    ip.write("      else {\n")
    ip.write("        map.addLayer("+group_name+"); };} )\n")

def close_file():
    filename = 'web/probes.html'
    ip = open(filename, 'a')
    # Complete Script and write to file
    #ip.write(string7 +'asnumber'+string5+'owner'+string8)
    string9 = "    </script>\n  </body>\n</html>"
    ip.write (string9)
    ip.close() 

geolocator = Nominatim(user_agent="aswindow")

ATLAS_API_KEY = "6f0e691d-056c-497d-9f5b-2297e970ec60"

filename2 = 'measurements/uk_measurements.json'

# filters = {"tags": "NAT", "country_code": "gb", "asn_v4": "3333"}
filters = {"tags": "system-Anchor", "country_code": "gb", "status": "1"}
probes = ProbeRequest(**filters)
probe_list = []
measurements = {}
uk_probes ={}
# print(probes)
asn_list = []
addresses_list =[]
count = 0
add_count = 0
for t_probe in probes:
    #print (t_probe)
    probe_list.append(str(t_probe["id"]))
    uk_probes[t_probe["id"]] = {}
    uk_probes[t_probe["id"]] ["probe_ip"] = t_probe["address_v4"]
    uk_probes[t_probe["id"]] ["probe_x"] = t_probe["geometry"]["coordinates"][0]
    uk_probes[t_probe["id"]] ["probe_y"] = t_probe["geometry"]["coordinates"][1]
    uk_probes[t_probe["id"]] ["probe_asn"] = t_probe["asn_v4"]
    
    '''
    ['probe_asn']
        ip_address      = probe_dict[probe_id]['probe_ip']
        lon             = probe_dict[probe_id]['probe_x']
        lat             = probe_dict[probe_id]['probe_y']
        hops            = probe_dict[probe_id]['Hops']


    if t_probe['asn_v4'] not in asn_list:
        asn_list.append(t_probe['asn_v4'])
        count += 1
        print(t_probe["geometry"]["coordinates"])
        latitude = t_probe["geometry"]["coordinates"][0]
        longitude = t_probe["geometry"]["coordinates"][1]
        print ("lat is ", latitude)
        print ("lon is ", longitude)
        coordinates = str(longitude)+','+str(latitude)
        if t_probe["geometry"]["coordinates"] != None:
            location = geolocator.reverse(coordinates)
            print(location.address)
            if location.address not in addresses_list:
                addresses_list.append(location.address)
                add_count += 1
   

print(asn_list)
print(count)
print(addresses_list)
print (add_count)
'''
# print(uk_probes)


# target_address = "90 Oxford Street, Randburg"   # sample target address

     
create_header_html(uk_probes)          # create the file (named after the target IP and centralise the map )

#Create the Probes
for probe_id in uk_probes:
    # Only iterate through probe ID's not other information
    
    # Now create the probes 
    create_probes(probe_id,uk_probes) 
close_file() 
