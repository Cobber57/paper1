# Test file which will need to be copied into create_html file once it is fully working
# this maps an ixp within leaflet

import peeringdb

def create_ixp(ixp_id, ixp_info,facilitys_uk,html):
        pdb = peeringdb.PeeringDB()
        # ip = open('peeringdb_test_results/ixp_test.html', 'w')
        ip = open(html.filename, 'a')


        # show all the facilities where the IXP peers on the map
        string6 = 'var bounds_' # = [[ # 37.767202, -122.456709], [37.766560, -122.455316]]; 
        stringa = 'var rectangle_'
        stringb = ' = L.rectangle(bounds_'
        stringc = ', {color: "black", weight: 4}).addTo(map);\n'
        
        string3 = '        ]).addTo(map);\n'
        string4 = 'rectangle_'
        string4a= '.bindPopup("<b>IXP '
        
        string5 = '</b><br /> ");\n'

        string7 = 'var polylinePoints = [['
        string8 = 'var polyline_' 
        string9 = ' = L.polyline(polylinePoints, {color: "black", weight: 1}).addTo(map);\n'   
        

        spacer1 = "        ["
        spacer2 = "],\n"

        first_facility = str(ixp_info['fac_set'][0][0])
        first_facility_lat = str(facilitys_uk[first_facility]['latitude'])
        first_facility_lon = str(facilitys_uk[first_facility]['longitude'] )

        for fac in ixp_info['fac_set'][0]:
            
            f = pdb.fetch(peeringdb.resource.Facility, fac)
            fac_organisation = f[0]['org']['name']
            fac_address = f[0]['org']['address1']
            fac_city = f[0]['org']['city']
            fac_country = f[0]['org']['country']
            fac_website = f[0]['org']['website']
            
            

            fac_str = str(fac)
            # print(fac_str, ixp_info['fac_set'][0][0])
            
            rec_lat1 = str(facilitys_uk[fac_str]['latitude'] + .001)
            rec_lat2 = str(facilitys_uk[fac_str]['latitude'] - .001)
            rec_lon1 = str(facilitys_uk[fac_str]['longitude'] - .001)
            rec_lon2 = str(facilitys_uk[fac_str]['longitude'] + .001)
            # print ( 'FIRST FAC =',first_facility, first_facility_lat,first_facility_lon)
            #create the IXP Rectangle at the first facilties location
            ip.write ('      // IXP '+str(ixp_id)+' Facility '+fac_str+'\n')
            ip.write(string6 +fac_str+' = [['+rec_lat1 +',' +rec_lon1 +'],[' +rec_lat2+',' +rec_lon2 +']];\n')
            ip.write(stringa + fac_str+stringb+fac_str+stringc)  
            ip.write(string4 
            + fac_str
            + string4a
            + str(ixp_id)
            + "<br />"
            + ixp_info['name'][0]
            + "<br />"
            + ixp_info['ipv4_prefix']
            +"<br />"
            + ixp_info['ipv6_prefix']
            +"<br />"
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

            # Dont bother drawing a line from the first facility
            if fac_str != str(ixp_info['fac_set'][0][0]):
                
                ip.write('      // Draw Line_'+str(fac_str)+'\n')
                ip.write(string7 
                    +first_facility_lat
                    +', '
                    +first_facility_lon
                    +'],['
                    +str(facilitys_uk[fac_str]['latitude'])
                    +', '
                    +str(facilitys_uk[fac_str]['longitude'])
                    +']];\n')
                ip.write(string8+fac_str+string9)


            '''

        i = 0
        j = 0 

        
        for lon in sorted_fac_lons:
            # popup[lon] = ""
            print(lon)
            j = 0
            for fac in pop[lon]:
                print('facilities at longitude', j,'=',i)
                print ("LON IS ",lon,'Fac is',fac)
                print(pop[lon][fac]['latitude'])
                i = i+1
                #print (info['popup'])
                #popup[lon] = popup[lon]+info['popup']+"<br />"
                #print (popup[lon])
                
                
                ip.write(spacer1+str(pop[lon][fac]['latitude'])+ ','+str(lon)+spacer2)
                 #print ("POPUP for ",lon," is ",popup[lon])

            j = j+1
            print('longitudes', j)
        '''
        
        #keys_list = list(ixp.keys())
        #ixp_name = ixp[ixp_id]['name']
        
        





        


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
    

    import ipaddress
    import json
    with open('peeringdb_test_results/uk_facilities.json') as f:
        facilitys_uk = json.load(f)
    
        

    this_ixp = {}
    this_ixp['18'] = {}
    this_ixp['name'] = ["LINX LON1"]
    this_ixp["org_id"] = [791]
    this_ixp["fac_set"] = [[34, 39, 40, 43, 45, 46, 79, 399, 534, 832, 2262, 835, 4404, 4360, 4089, 3152, 6535, 3399]]
    this_ixp["ixlan_set"] = [[18]]
    this_ixp["ipv4_prefix"] = "195.66.224.0/22"
    this_ixp["ipv6_prefix"] = "2001:7f8:4::/64"

    #print(this_ixp)
    create_ixp('18', this_ixp,facilitys_uk) # pass the IXP Id, the IXP info, all the UK facilities