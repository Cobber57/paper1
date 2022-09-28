#!/usr/bin/env python
#
# Program:      $Id: $ 
# Author:       Paul McCherry <p.mccherry@lancaster.ac.uk>
# Description:  Creates Leaflet based HTML file map of probes, hops and targets.  
#               
#


class Html_Create:
    def create_header_html(self):           
        # Choose centre of map is now focused on target lat and lon
        # central_lon = -2.23                                  # central lon coordiantes
        # central_lat = 52.369                                  # central lat coordiantes

        # write default head info to new file
        
        cmd2 = 'chmod ' +'766 '+ self.filename
        cmd = 'cp html/head.html '+ self.filename
                
        os.system(cmd)
        # Fix File Permisssions
        os.system(cmd2)
                
        # Write latitude and longitude to html file for zoom location
        # open file 
        
        ip = open(self.filename, 'a')
        
        # centre of map is focused on target lat and lon       
        ip.write(str(self.target_lat)+", "+str(self.target_lon)+'], 12);\n')
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

        # Create Red Probe location - These are probes used in the calculation
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
    
    def create_greater(self, probe_id, probe_dict, rtt,target):

        

        asn             = probe_dict[probe_id]['probe_asn']
        ip_address      = probe_dict[probe_id]['probe_ip']
        lon             = probe_dict[probe_id]['probe_x']
        lat             = probe_dict[probe_id]['probe_y']
        #hops            = probe_dict[probe_id]['Hops']
        # Avg Speed of a packet in a fibre optic medium
        packet_speed = 0.66 * 300000 # METRES PER MILLISECCOND
        radius          = (rtt/2) * packet_speed 



        group_name = "group" + str(probe_id)
        target_group_name = "group" + str(target)
        
        ip = open(self.filename, 'a')
        

        # create ipaddress points on map in green circles
        stringa = "      var gcircle_"
        stringb = " = L.circle(["
        string1 = "      // show the area of operation of the AS on the map\n      var polygon = L.polygon([\n"
        string2 = "], { color: 'red', fillColor: '#00', interactive: false, fillOpacity: 0.0, radius: "
        string21 = "], { color: 'red', fillColor: '#8000000', fillOpacity: 0.5, radius: "
        string22 = "], { color: 'blue', fillColor: '#8000000', fillOpacity: 0.5, radius: "
        string23 = "], { color: 'red', fillColor: '#00', interactive: false, fillOpacity: 0.0, radius: "
        string24 = "], { color: 'green', fillColor: '#00', interactive: false, fillOpacity: 0, radius: "
        string25 = "], { color: 'yellow', fillColor: '#8000000', fillOpacity: 0.5, radius: "
        string2a = " }).addTo(map);"


        string3 = "        ]).addTo(map);\n"
        string4 = '      polygon.bindPopup("<b>AS'
        string5 = '</b><br />'
        string6 = '<br />Area of Operation");\n'
        string6a = "});\n"
        string7 = '      circle.bindPopup("<b>Probe '
        string7a ='      circle'
        string7b ='.bindPopup("<b>Probe '
        string7c ='.bindPopup("<b>Target '
        string8 = ' ").openPopup();\n\n'
        string8a = ' ");\n\n'
        spacer1 = "        ["
        spacer2 = "],\n"
        
     
            
            
        ip.write ('      // greater Circle '+str(probe_id)+'\n')

        # Create Green greater circle 
        ip.write(stringa + str(probe_id)+stringb+str(lat)+ ','+str(lon)+string24+str(radius)+string6a+'\n')  
        
                
        # add to Featuregroup
        ip.write("      gcircle_"+str(probe_id)+".addTo("+group_name+");\n")
        ip.write("      gcircle_"+str(probe_id)+".addTo("+target_group_name+");\n")

        #ip.write("     "+group_name+".bindPopup('"+group_name+"');\n")
        '''
        ip.write("      circle"+str(probe_id)+".on('click', function(e) {if(map.hasLayer("+group_name+")){\n")
        ip.write("        map.removeLayer("+group_name+"); ")
        ip.write("        map.removeLayer("+target_name+"); }\n")
        ip.write("      else {\n")
        ip.write("        map.addLayer("+group_name+"); };} )\n")
        '''



    def create_target(self, probe_id, probe_dict):

        

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
            
            
        ip.write ('      // Target '+str(probe_id)+'\n')

        # Create yellow Target location 
        ip.write(stringa + str(probe_id)+stringb+str(lat)+ ','+str(lon)+string25+str(1000)+string2a+'\n')  
        # Create Probe Popup
        ip.write(string7a +str(probe_id)+string7c+str(probe_id) + string5 + 'AS '+str(asn)+"<br />" + str(ip_address) + "<br />" +string8a)

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
        ip.write(string1+name+string1a+str(current_lon)+', '+str(current_lat)+string2+str(new_lon)+', '+str(new_lat)+string3+'\n')
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
        
        probe_list = list(probe_dict.keys())  
        
        

        # gets destination address 
        self.target_ip = str(probe_dict[probe_id]['probe_ip'])                # gets destination address 
        self.target_lat = probe_dict[probe_id]['probe_x']
        self.target_lon = probe_dict[probe_id]['probe_y']
        self.target_address = 'Not Applicable'

       
        self.filename = 'web/targets/target_tr_'+str(self.target_ip)+'.html'


if __name__ == "__main__":
    # Creates a list of UK anchors, reads in a measurements file and creates the html files for each

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
    # https://pypi.org/project/prsw/
    my_ripe = prsw.RIPEstat()

    from peeringdb import PeeringDB, resource, config
    pdb = peeringdb.PeeringDB()

    geolocator = Nominatim(user_agent="aswindow")

    ATLAS_API_KEY = "6f0e691d-056c-497d-9f5b-2297e970ec60"

    filename2 = 'measurements/uk_measurements.json'

    # filters = {"tags": "NAT", "country_code": "gb", "asn_v4": "3333"}
    filters = {"tags": "system-Anchor", "country_code": "gb"}
    probes = ProbeRequest(**filters)
    probe_list = []
    measurements = {}
    uk_probes ={}
    asn_list = []
    addresses_list =[]
    count = 0
    add_count = 0
    numberoffiles = 0

    # Create a Dictionary of the UK probes to be used 
    for t_probe in probes:
        
        probe_list.append(str(t_probe["id"]))
        uk_probes[t_probe["id"]] = {}
        uk_probes[t_probe["id"]] ["probe_ip"] = t_probe["address_v4"]
        uk_probes[t_probe["id"]] ["probe_x"] = t_probe["geometry"]["coordinates"][0]
        uk_probes[t_probe["id"]] ["probe_y"] = t_probe["geometry"]["coordinates"][1]
        uk_probes[t_probe["id"]] ["probe_asn"] = t_probe["asn_v4"]

    # Create the IXPs in their relevant locations


    # Create a web based menu to provide easy access to Target maps
    menu_file = 'web/targets/menu.html'
    cmd = 'rm ' + menu_file
    os.system(cmd)
    menu = open(menu_file,'a')
    menu.write('<!DOCTYPE html>\n<html>\n<body>\n\n<h1>UK target Links</h1>\n')
    link1_string = '<p><a href="'
    link2_string = '">'
    link3_string = '</a></p>'

    # Open the measurements file created previously

    with open("results/targets.json") as file:
            measurements =json.load(file)
    measurement =  {}


    # Read in measurements

    for measurement_id in measurements:
        
        this_target = measurements[measurement_id]['target_probe']
        
        print("TARGET",this_target)

        measurement[this_target] = {}
        measurement[this_target] ["probe_ip"] = measurements[measurement_id]["target_address"]
        measurement[this_target] ["probe_x"] = measurements[measurement_id]["target_coordinates"][1]
        measurement[this_target] ["probe_y"] = measurements[measurement_id]["target_coordinates"][0]
        measurement[this_target] ["probe_asn"] = measurements[measurement_id] ["target_probe"]

        
        html = Html_Create(this_target,measurement)     
        html.create_header_html()          # create the file (named after the target IP and centralise the map )
        target_lon = measurement[this_target] ["probe_y"]
        target_lat = measurement[this_target] ["probe_x"]
        target_coords = (target_lon,target_lat)
        # Create the target probe          
        html.create_target(int(this_target),uk_probes) 

        # Add target to web based menu
        menu = open(menu_file,'a')
        menu.write(link1_string + 'http://icloud9.co.uk/phd/uk/target_tr_'+measurement[this_target]["probe_ip"] +'.html' +link2_string +'Probe : '+this_target+ ' Target IP : ' +measurement[this_target]["probe_ip"]+' '  + link3_string+'\n')
        menu.close()
        
        #Create the Source Probes
        for probe_id in measurements[measurement_id]['results']:

            # Only iterate through source probe's not the target probe

            if probe_id != this_target:

                # Now create the probes 
                html.create_probes(int(probe_id),uk_probes) 
                source_lon = measurements[measurement_id]['results'][probe_id]['source_coordinates'][0]
                source_lat = measurements[measurement_id]['results'][probe_id]['source_coordinates'][1]
                source_coords = (source_lon,source_lat) 
                max_distance = gcc.distance_between_points(source_coords, target_coords, unit='kilometers',haversine=True)
                

                
                if measurement[this_target] ["probe_ip"] != None:
                    current_ip = measurement[this_target] ["probe_ip"] 
                else:
                    current_ip = 'unknown'
                # Now create the Greater Circle around the probe using the RTT value
                html.create_greater(int(probe_id),uk_probes,measurements[measurement_id]['results'][probe_id]['final_rtt'], this_target) 
                
                # now create the hops between the source and target
                
                hops = measurements[measurement_id]['results'][probe_id]['max_hops']
                rtt = measurements[measurement_id]['results'][probe_id]['final_rtt']

                current_lat = source_lat
                current_lon = source_lon
                last_rtt = 0
                # amount to add where rtt has failed, .01 = 1km from last hop
                default_rtt = .01

                # create forward path
                for hop in measurements[measurement_id]['results'][probe_id]['hops']:

                    # Create location of where to place this hop
                    this_rtt = measurements[measurement_id]['results'][probe_id]['hops'][hop]['rtt']
                    
                    this_ip = measurements[measurement_id]['results'][probe_id]['hops'][hop]['ip_from']
                    # Workout location of Hop
                    
                    response = my_ripe.network_info(this_ip)

                    # if location cannot be worked out then just use rtt value                    
                    if this_rtt > rtt:
                        # Note : possible problem if this default rtt gove over the max_rtt
                        this_rtt = last_rtt + default_rtt
                    
                    
                    this_fraction = this_rtt/rtt 
                    if source_coords >= target_coords:
                        hop_coords =  target_coords
                        
                    else:
                        hop_coords = gcc.intermediate_point(source_coords, target_coords,fraction=this_fraction)
                        
                    this_hop = {}
                    this_hop['hop_latitude'] = hop_coords[1]
                    this_hop['hop_longitude'] = hop_coords[0]
                    lat1 = current_lat
                    lon1 = current_lon
                    lat2 = this_hop['hop_latitude']
                    lon2 = this_hop['hop_longitude']
                    hop_distance = gcc.distance_between_points(source_coords, hop_coords, unit='kilometers',haversine=True)
                    this_hop['asn'] = 'Not coded yet'
                    
                    this_hop['from'] = measurements[measurement_id]['results'][str(probe_id)]['hops'][hop]['ip_from']
                    
                    this_hop['address'] = 'no address'

                    html.create_hop(probe_id,hop,this_hop,this_rtt)
                    html.create_lines_var(probe_id,hop,lat1,lon1,lat2,lon2,hop_distance,this_rtt,current_ip,this_hop['from'])
                    current_lat = lat2
                    current_lon = lon2
                    source_coords = (lon2,lat2)

                    last_rtt = this_rtt

                # Create the Reverse Path
                '''
                reverse_target_probe = probe_id
                reverse_source_probe = this_target
                for reverse_measurement_id in measurements:
                    if measurements[reverse_measurement_id]["target_probe"] == reverse_target_probe:
                        for reverse_hop in measurements[reverse_measurement]["results"][reverse_source_probe]['hops']
                            html.create_lines_var(reverse_probe_id,hop,lat2,lon2,lat1,lon1,hop_distance,this_rtt,current_ip,this_hop['from'])

                        # break out of loop as we found the reverse path, no need to keep checking
                        break
                measurement_id = 
                for hop in measurements[measurement_id]['results'][probe_id]['hops']:
                '''
        

        
        html.close_file()     
        numberoffiles += 1
        print ('Copy ', html.filename ,' upto web server', numberoffiles)

                
    # Complete and close web based menu
    menu = open(menu_file,'a')            
    menu.write('</body>\n</html>')
    menu.close()