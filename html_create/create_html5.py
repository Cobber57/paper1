# Creates the measurements between 34 anchors in the UK and adds the measurment info to a file in the measurments folder
# for use in a application to read that info and make use of it.

from ripe.atlas.cousteau import ProbeRequest, Traceroute, AtlasSource, AtlasRequest, AtlasCreateRequest
from datetime import datetime
import time
import json 
import os
from geopy.geocoders import Nominatim
from geopy.distance import geodesic
# from haversine import haversine
import great_circle_calculator.great_circle_calculator as gcc


class Html_Create:
    def create_header_html(self):           
            # Choose centre of map
            central_lon = -2.23                                  # central lon coordiantes
            central_lat = 52.369                                  # central lat coordiantes

            # write default head info to new file
            
            cmd2 = 'chmod ' +'766 '+ self.filename
            cmd = 'cp html/head.html '+ self.filename
                    
            os.system(cmd)
            # Fix File Permisssions
            os.system(cmd2)
                    
            # Write latitude and longitude to html file for zoom location
            # open file 
            
            ip = open(self.filename, 'a')
            
            print(central_lat,central_lon)
            
            ip.write(str(central_lat)+", "+str(central_lon)+'], 7);\n')
            ip.close()
            

            # write tilelayer information to html file
            cmd = 'cat html/tilelayer.html >> '+ self.filename
            os.system(cmd)

    def create_probes(self, probe_id, probe_dict):

        

        asn             = probe_dict[probe_id]['probe_asn']
        ip_address      = probe_dict[probe_id]['probe_ip']
        lon             = probe_dict[probe_id]['probe_x']
        lat             = probe_dict[probe_id]['probe_y']
        #hops            = probe_dict[probe_id]['Hops']

        group_name = "group" + str(probe_id)
        target_name = "target_" + str(probe_id)
        ip = open(self.filename, 'a')
        

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
    def create_hop(self,probe_id,h,hop,rtt):
        group_name = "group" + probe_id
        target_name = "target_" + probe_id

        stringa = "      var circle_"
        stringb = " = L.circle(["
        string22 = "], { color: 'blue', fillColor: '#8000000', fillOpacity: 0.5, radius: "
        string2a = " });"
        string5 = '</b><br />'
        string7a ='      circle_'
        string7b ='.bindPopup("<b>Hop '
        string8a = ' ");\n\n'

        ip = open(self.filename, 'a')
        # Create Blue hop location 
        name = str(probe_id)+'_' + h
        print('HOP',hop)
        ip.write ('      // Probe '+probe_id+ ' Hop '+h+'\n')
        ip.write(stringa + name +stringb+str(hop['hop_latitude'])+ ','+str(hop['hop_longitude'])+string22+str(300)+string2a+'\n')  
        # Create hop Popup
        ip.write(string7a +name+string7b+ name + string5 + 'AS '+hop['asn']+"<br />" + str(hop['from']) + "<br />" + "Address: "+hop['address']+ "<br />" + "stt : " + str(rtt/2)+string8a+"\n")   
        # add to Featuregroup
        ip.write("      circle_" + name + ".addTo(" + group_name +");\n")

    def create_lines_var(self,probe_id,h,current_lon,current_lat,new_lon,new_lat,distance,rtt,current_ip,new_ip):
        group_name = "group" + probe_id
        name = str(probe_id)+'_' + h
        string1 = "      var latlng_"
        string1a = " = [ ["
        string2 = "],["
        string3 = "] ] ;"
        string4 = "      var pline_"
        string5 = " = L.polyline(latlng_"
        string6 = ", {color: '"
        string6a = "'});\n"

        string7a ='        pline_'
        string7b ='.bindPopup("<b>Hop '
        string7c = '</b><br />'
        string8a = ' ");\n\n'
        ip = open(self.filename, 'a')
        
        # Work out speed of link (ie Congestion plus Packet processing overhead)
        # Average Speed of packet though fibre cable 2/3C  = 200 km per millisecond
        average_speed_fraction = .66          # Average speed of a packet in optical fibre
        packet_speed = (distance*1000) / (rtt/2)         # speed of packet in km per sec
        sol_fraction = packet_speed/ 300000   # Compared against speed of light

        if sol_fraction < .2:
            colour = "red"
        if sol_fraction >= .2 and sol_fraction < .3:
            colour = "orange"
        if sol_fraction >= .3 and sol_fraction < .5:
            colour = "yellow"
        if sol_fraction >= .5:
            colour = "green"
        
        ip.write ('      // Probe '+probe_id+ ' Line '+h+'\n')
        #Create the line lat and lon variable
        ip.write(string1+name+string1a+str(current_lat)+', '+str(current_lon)+string2+str(new_lat)+', '+str(new_lon)+string3+'\n')
        # Create and add the line to the map
        ip.write(string4+name+string5+name+string6+colour+string6a+'\n')
        # Create Line Popup
        ip.write("      pline_"+name+string7b+ name + string7c + 'From: ' + str(current_ip)+ ' To: '+str(new_ip)+"<br />"'Distance: '+ str(distance)+" Km<br />" + "Stt: "+str(rtt/2)  + "<br />" +"Average Speed of packet in fibre: .66 Speed of light"+"<br />"+"Packet Speed Over This Hop: " +str(sol_fraction)  +string8a+"\n")
        
        # add to Featuregroup
        ip.write("      pline_"+name+".addTo("+group_name+");\n")


    def close_file(self):
        ip = open(self.filename, 'a')
        # Complete Script and write to file
        #ip.write(string7 +'asnumber'+string5+'owner'+string8)
        string9 = "    </script>\n  </body>\n</html>"
        ip.write (string9)
        ip.close() 
    
    def __init__(self, probe_id, probe_dict):
        # print(probe_dict)
        probe_list = list(probe_dict.keys())  
        # print (probe_list)
        print(probe_dict)

                        # gets destination address 
        self.target_ip = str(probe_dict[probe_id]['probe_ip'])                # gets destination address 
        self.target_lat = probe_dict[probe_id]['probe_x']
        self.target_lon = probe_dict[probe_id]['probe_y']
        self.target_address = 'Not Applicable'

       
        self.filename = 'web/targets/target_tr_'+str(self.target_ip)+'.html'

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



with open("results/targets.json") as file:
        measurements =json.load(file)
measurement =  {}
# print('measurement', measurements)
for measurement_id in measurements:
    this_target = measurements[measurement_id]['target_probe']
    print("TARGET",this_target)
    measurement[this_target] = {}
    measurement[this_target] ["probe_ip"] = measurements[measurement_id]["target_address"]
    measurement[this_target] ["probe_x"] = measurements[measurement_id]["target_coordinates"][1]
    measurement[this_target] ["probe_y"] = measurements[measurement_id]["target_coordinates"][0]
    measurement[this_target] ["probe_asn"] = uk_probes[int(this_target)] ["probe_asn"]

    
    html = Html_Create(this_target,measurement)     
    html.create_header_html()          # create the file (named after the target IP and centralise the map )
    target_lon = measurement[this_target] ["probe_y"]
    target_lat = measurement[this_target] ["probe_x"]
    target_coords = (target_lon,target_lat)
    #Create the Source Probes
    for probe_id in uk_probes:
        # Only iterate through source probe's not the target probe
        # print('Source Probe is', probe_id, 'target probe is ', this_target)
        # input('wait')
        if str(probe_id) != this_target:
            # Now create the probes 
            html.create_probes(probe_id,uk_probes) 
            source_lon = measurements[measurement_id]['results'][str(probe_id)]['source_coordinates'][0]
            source_lat = measurements[measurement_id]['results'][str(probe_id)]['source_coordinates'][1]
            source_coords = (source_lon,source_lat) 
            max_distance = gcc.distance_between_points(source_coords, target_coords, unit='kilometers',haversine=True)
            
            print (source_coords, target_coords)
            print('Distance is', max_distance)
            
            if measurement[this_target] ["probe_ip"] != None:
                current_ip = measurement[this_target] ["probe_ip"] 
            else:
                current_ip = 'unknown'
            # now create the hops between the source and target
            print(measurements[measurement_id]['results'][str(probe_id)])
            
            # try:
                
            hops = measurements[measurement_id]['results'][str(probe_id)]['max_hops']
            rtt = measurements[measurement_id]['results'][str(probe_id)]['final_rtt']
            print('HOPS', hops)
            current_lat = source_lat
            current_lon = source_lon
            
            for hop in range(hops):
                print('target is ',this_target, 'source is ', probe_id, 'HOP',hop)
                h = str(hop+1)
                print(h)
                # print(measurements[measurement_id]['results'][str(probe_id)]['hops'][h])
                # Create location of where to place this hop
                if h in measurements[measurement_id]['results'][str(probe_id)]['hops']:
                    this_rtt = measurements[measurement_id]['results'][str(probe_id)]['hops'][h]['rtt']
                elif '255' in measurements[measurement_id]['results'][str(probe_id)]['hops']:
                        this_rtt = measurements[measurement_id]['results'][str(probe_id)]['hops']['255']['rtt']
                        
                
                count = 0
                next_h = h
                while this_rtt == 100:
                    next_h = str(int(next_h)+1)
                    if next_h in measurements[measurement_id]['results'][str(probe_id)]['hops']: 
                        this_rtt = measurements[measurement_id]['results'][str(probe_id)]['hops'][next_h]['rtt']
                        count += 1
                    elif '255' in measurements[measurement_id]['results'][str(probe_id)]['hops']:
                        this_rtt = measurements[measurement_id]['results'][str(probe_id)]['hops']['255']['rtt']
                        count += 1
                    else:
                        this_rtt = measurements[measurement_id]['results'][str(probe_id)]['hops'][h]['rtt']
                        count += 1
                if count == 0:
                    this_fraction = this_rtt/rtt
                else:
                    # calculate the difference in time between the original rtt and the next hop (that is not 100); 
                    this_time_taken = this_rtt - measurements[measurement_id]['results'][str(probe_id)]['hops'][h]['rtt']
                    # now add this differnce to the original time but divide it by the number of times had to skip due to 100
                    this_rtt = measurements[measurement_id]['results'][str(probe_id)]['hops'][h]['rtt'] + (this_time_taken/count) 
                    this_fraction = this_rtt/rtt 
                print('total rtt is ',rtt,'this rtt is', this_rtt,'FRACTION', this_fraction)
                hop_coords = gcc.intermediate_point(source_coords, target_coords,fraction=this_fraction)
                this_hop = {}
                this_hop['hop_latitude'] = hop_coords[0]
                this_hop['hop_longitude'] = hop_coords[1]
                lat1 = current_lat
                lon1 = current_lon
                lat2 = this_hop['hop_latitude']
                lon2 = this_hop['hop_longitude']
                
                this_hop['asn'] = 'Not coded yet'
                if h in measurements[measurement_id]['results'][str(probe_id)]['hops']:
                    this_hop['from'] = measurements[measurement_id]['results'][str(probe_id)]['hops'][h]['ip_from']
                elif '255' in measurements[measurement_id]['results'][str(probe_id)]['hops']:
                    this_hop['from'] = measurements[measurement_id]['results'][str(probe_id)]['hops']['255']['ip_from']   
                this_hop['address'] = 'no address'
                # print('HOP COORDS are', hop_coords)
                # input('wait')
                # html.create_hop(probe_id,h,this_hop,rtt)
                current_lat = this_hop['hop_latitude']
                current_lon = this_hop['hop_longitude']
                
        # add to Featuregroup
            #except:
                # do nothing
                #print('No Source ', probe_id, 'For ', this_target)
html.close_file() 
