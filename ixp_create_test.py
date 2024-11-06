def create_ixp(ixp_id, ixp):
        with open('peeringdb_test_results/uk_facilities.json') as f:
            facilitys_uk = json.load(f)
        ip = open('peeringdb_test_results/ipx_test.html', 'w')
        
        # Sort facilties via Latitude to tidy up area of operation
        
        pop = {}
        for fac in facilitys_uk:
            print(fac)

            # create a point of prescence for the IXP at this facility
            lon = facilitys_uk[fac]['longitude']
            # if this pop lonitude doesnt already have a point of presence
            if lon not in pop:
                pop[lon] = {}
            # otherwise just add another facilty here (but also add all the relevant info even when it doesnt)
            pop[lon][fac] = {}
            pop[lon][fac]['org_id']     = facilitys_uk[fac]['org_id']
            pop[lon][fac]['name']       = facilitys_uk[fac]['name']
            pop[lon][fac]['address1']   = facilitys_uk[fac]['address1']
            pop[lon][fac]['address2']   = facilitys_uk[fac]['address2']
            pop[lon][fac]['city']       = facilitys_uk[fac]['city']
            pop[lon][fac]["country"]    = facilitys_uk[fac]['country']
            pop[lon][fac]["postcode"]   = facilitys_uk[fac]['postcode']
            pop[lon][fac]['latitude']  = facilitys_uk[fac]['latitude']
            

        #print(pop)
        
        sorted_fac_lons = sorted(pop)
        print('SORTED ##########################################')
        print(sorted_fac_lons)

        ''' NOT SURE IF THE FOLLOWING IS NEEDED ATM but will leave just in case
        # Negative strings are not orderd correctly so need to fix
        #print (sorted_fac_lons)
        sorted_facs = collections.OrderedDict(sorted_fac_lons)
        #print (sorted_facs)
        #input('wait')
        '''

        # show the area of operation of the IXP on the map
        stringa = "      var polygon"
        stringb = " = L.polygon([\n"

        string3 = "        ]).addTo(map);\n"
        string4 = '      polygon.bindPopup("<b>IXP '
        string5 = '</b><br /> ");'

        spacer1 = "        ["
        spacer2 = "],\n"

        #create the IXP Polygon
        ip.write ('      // IXP '+str(ixp_id)+'\n')
        ip.write(stringa + str(ixp_id)+stringb)  

        for lon in sorted_fac_lons:
            # popup[lon] = ""
            print(lon)
            for fac in pop[lon]:
                print ("LAT IS ",lon,'Fac is',fac)
                print(pop[lon][fac]['latitude'])
                
                #print (info['popup'])
                #popup[lon] = popup[lon]+info['popup']+"<br />"
                #print (popup[lon])
                
                
                ip.write(spacer1+str(pop[lon][fac]['latitude'])+ ','+str(lon)+spacer2)
                 #print ("POPUP for ",lon," is ",popup[lon])

        
        
        # add polygon ending   
        ip.write(string3)
        
        #keys_list = list(ixp.keys())
        #ixp_name = ixp[ixp_id]['name']
        
        ip.write(string4 +ixp_id+string5)





        


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
    this_ixp = {}
    this_ixp['18'] = {}
    this_ixp['name'] = ["LINX LON1"]
    this_ixp["org_id"] = [791]
    this_ixp["fac_set"] = [[34, 39, 40, 43, 45, 46, 79, 399, 534, 832, 2262, 835, 4404, 4360, 4089, 3152, 6535, 3399]]
    this_ixp["ixlan_set"] = [[18]]
    this_ixp["ipv4_prefix"] = "195.66.224.0/22"
    this_ixp["ipv6_prefix"] = "2001:7f8:4::/64"

    #print(this_ixp)
    create_ixp('18', this_ixp)