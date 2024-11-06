import csv
import re
import os
os.chdir('/home/paul/Documents/UK')
del os 
import sqlite3

# import request so can access the RIPE database REST API 
import requests
ripe_url = 'https://rest.db.ripe.net/search.json'

import json

import ipaddress    

# create_ixinfo isnt needed now as the complete file has been created
# ix_detail_dict now has a cross reference between Ip addresses and facilities.
    # These only include the LINX networks but more can be added to this
    #print('40',ix_detail_dict['185.1.101.28'])
    #print('#######')
    #print('42',ix_detail_dict['195.66.244.42'])
    #input('wait')
    
    
def create_ixinfo():

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
    facilitys_uk['8628']["networks"] = [3744, 56595, 2354, 12703, 10507, 202793]

    facilitys_uk['4463'] = {}
    facilitys_uk['4463']["org_id"] = 2103
    facilitys_uk['4463']["name"] = 'Netnorth Ltd'
    facilitys_uk['4463']["address1"] = "Unit 7 Queensbrook" 
    facilitys_uk['4463']["address2" ] = "Bolton Technology Exchange, Spa Rd"
    facilitys_uk['4463']["city"] =  "Bolton"
    facilitys_uk['4463']["country"] = "GB"
    facilitys_uk['4463']["postcode"] = "BL1 4AY"
    facilitys_uk['4463']["latitude"] = 50.681852 
    facilitys_uk['4463']["longitude"] = -2.256535
    facilitys_uk['4463']["networks"] = [14737, 205402, 2356, 25376]


    facilitys_uk['1793']["latitude"] = 51.24771 
    facilitys_uk['1793']["longitude"] = -0.15714
    

    facilitys_uk['34']["latitude"] = 51.51171
    facilitys_uk['34']["longitude"] = -0.00294

    facilitys_uk['39']["latitude"] = 51.51171
    facilitys_uk['39']["longitude"] = -0.00294

    facilitys_uk['51']["latitude"] = 51.499
    facilitys_uk['51']["longitude"] = -0.01446

    facilitys_uk['244']["latitude"] = 53.47941
    facilitys_uk['244']["longitude"] = -2.23815

    facilitys_uk['428']["latitude"] = 51.52334
    facilitys_uk['428']["longitude"] = -0.08549

    facilitys_uk['438']["latitude"] = 53.46371
    facilitys_uk['438']["longitude"] = -2.23677

    facilitys_uk['632']["latitude"] = 51.44526
    facilitys_uk['632']["longitude"] = -0.97596

    facilitys_uk['677']["latitude"] = 52.64077
    facilitys_uk['677']["longitude"] = -1.14055

    facilitys_uk['734']["latitude"] = 52.05523
    facilitys_uk['734']["longitude"] = -0.75594   

    facilitys_uk['835']["latitude"] = 51.51171
    facilitys_uk['835']["longitude"] = -0.00294

    facilitys_uk['840']["latitude"] = 51.46199
    facilitys_uk['840']["longitude"] = -1.00587

    facilitys_uk['1027']["latitude"] = 51.65227
    facilitys_uk['1027']["longitude"] = -0.05508

    facilitys_uk['1140']["latitude"] = 52.04248
    facilitys_uk['1140']["longitude"] = -0.81931

    facilitys_uk['1311']["latitude"] = 52.27884
    facilitys_uk['1311']["longitude"] = -1.89576

    facilitys_uk['1312']["latitude"] = 52.27884
    facilitys_uk['1312']["longitude"] = -1.89576

    facilitys_uk['1548']["latitude"] = 51.55309
    facilitys_uk['1548']["longitude"] = -3.03672

    facilitys_uk['1683']["latitude"] = 53.46080
    facilitys_uk['1683']["longitude"] = -2.32357

    facilitys_uk['1684']["latitude"] = 53.46083
    facilitys_uk['1684']["longitude"] = -2.32346

    facilitys_uk['1848']["latitude"] = 53.37906
    facilitys_uk['1848']["longitude"] = -1.47971

    facilitys_uk['2116']["latitude"] = 51.49293
    facilitys_uk['2116']["longitude"] = -0.03064

    facilitys_uk['2384']["latitude"] = 53.79256
    facilitys_uk['2384']["longitude"] = -1.54054
    
    facilitys_uk['2417']["latitude"] = 57.15251
    facilitys_uk['2417']["longitude"] = -2.16024

    facilitys_uk['3144']["latitude"] = 50.83371
    facilitys_uk['3144']["longitude"] = -0.13445

    facilitys_uk['3213']["latitude"] = 52.47811
    facilitys_uk['3213']["longitude"] = -1.87830

    facilitys_uk['3884']["latitude"] = 52.92833
    facilitys_uk['3884']["longitude"] = -1.21246

    facilitys_uk['4060']["latitude"] = 53.47468
    facilitys_uk['4060']["longitude"] = -2.17468

    facilitys_uk['4088']["latitude"] = 51.50870
    facilitys_uk['4088']["longitude"] = -0.05794
    
    facilitys_uk['4360']["latitude"] = 51.51171
    facilitys_uk['4360']["longitude"] = -0.00294

    facilitys_uk['5441']["latitude"] = 51.44679
    facilitys_uk['5441']["longitude"] = -0.45422

    facilitys_uk['6433']["latitude"] = 52.35817
    facilitys_uk['6433']["longitude"] = -1.33147

    facilitys_uk['7042']["latitude"] = 51.76947
    facilitys_uk['7042']["longitude"] = -0.12977

    facilitys_uk['7425']["latitude"] = 51.54706
    facilitys_uk['7425']["longitude"] = -0.17404

    facilitys_uk['8078']["latitude"] = 51.28160
    facilitys_uk['8078']["longitude"] = -0.79469

    facilitys_uk['8078']["latitude"] = 53.585077, -2.526218
    
    fac ='bt faraday London'
    facilitys_uk[fac] ={}                                              
    facilitys_uk[fac]['latitude'] = 51.511950
    facilitys_uk[fac]['longitude'] = -0.101645
    facilitys_uk[fac]['city'] = 'London'
    facilitys_uk[fac]['org_id'] = 384
    facilitys_uk[fac]['networks'] = [281]

    fac ='bt colindale London'
    facilitys_uk[fac] ={}                                              
    facilitys_uk[fac]['latitude'] = 51.58378
    facilitys_uk[fac]['longitude'] = -0.24646
    facilitys_uk[fac]['city'] = 'London'
    facilitys_uk[fac]['org_id'] = 384
    facilitys_uk[fac]['networks'] = [281]

    fac ='bt southbank London'
    facilitys_uk[fac] ={}                                              
    facilitys_uk[fac]['latitude'] = 51.50547 
    facilitys_uk[fac]['longitude'] = -0.105219
    facilitys_uk[fac]['city'] = 'London'
    facilitys_uk[fac]['org_id'] = 384
    facilitys_uk[fac]['networks'] = [281]

    fac ='bt kingston'
    facilitys_uk[fac] ={}                                              
    facilitys_uk[fac]['latitude'] = 51.41249999999999 
    facilitys_uk[fac]['longitude'] = -0.29127
    facilitys_uk[fac]['city'] = 'Kingston'
    facilitys_uk[fac]['org_id'] = 384
    facilitys_uk[fac]['networks'] = [281]

    fac ='bt birmingham'
    facilitys_uk[fac] ={}                                              
    facilitys_uk[fac]['latitude'] = 52.483079 
    facilitys_uk[fac]['longitude'] = -1.90519 
    facilitys_uk[fac]['city'] = 'Birmingham'
    facilitys_uk[fac]['org_id'] = 384
    facilitys_uk[fac]['networks'] = [281]



    #read in the IXp LINX detailed info downloaded from 
    # https://portal.linx.net/members/members-ip-asn
    
    with open('ix_info/members_export.csv', mode = 'r') as csv_file:
        csvreader = csv.reader(csv_file)
        # extracting field names through first row
        fields = next(csvreader)
        # extracting each data row one by one
        row_count= 0
        for row in csvreader:
            row_count += 1
            # print(row_count)
            i = 0
            
            ix_detail_dict[row[4]] = {}
            ix_detail_dict[row[4]]['facility_number'] = 0
            #print(ix_detail_dict)
            for field in fields:
                if field != 'IPv4 Address':
                    ix_detail_dict[row[4]][field] = row[i]
                i += 1 
            mysearch1 = ix_detail_dict[row[4]]['Location'].split(' (')[0]
            mysearch = mysearch1.split(' ')
            # print(mysearch)
            word_count = len(mysearch)
            # print(mysearch)
            
            # Now add the facility number that cooresponds with the Facility name from linx
            # to the ix_detail_dictionary 

            for facility in facilitys_uk:
                #print ('Facility',facility)
                #print('Word count is', word_count)            
                count = 0
                for this_word in mysearch:
                    
                    # print('This Word',this_word, 'Search in ',facilitys_uk[facility]["name"])
                    count += 1
                    
                    if this_word == 'MENA':
                        ix_detail_dict[row[4]]['facility_number'] = 7082
                        break
                    if this_word == 'MA1':
                        ix_detail_dict[row[4]]['facility_number'] = 76
                        break
                    
                    '''
                    "668": {
                    "org_id": 34,
                    "name": "Coresite Reston",
                    "address1": "12100 Sunrise Valley Drive",
                    "address2": "Greenham Business Park",
                    "city": "Reston",
                    "country": "VA",
                    "postcode": "20191",
                    "latitude": -77.364541,
                    "longitude": 38.950631,
                    "networks": [
                    20189,20940,22925,198167,29838,21949,58453,36692,203391,174,205994,
                    2734,30456,23420,208,393,397071,61317,47328,54113,26863,36459,63023,3257,
                    7489,919,6939,213122,16876,62947,32478,20144,397770,3290,53292,40138,8075,
                    8069,10886,34553,56038,62597,2914,31898,16276,4556,40676,33353,32035,26459,
                    1299,13414,3223,5662,62874,53636,10310,21859,399114],
                    '''
                    if this_word.casefold() == 'Reston'.casefold() or this_word == 'Coresite' :
                        #input('Reston wait')
                        ix_detail_dict[row[4]]['facility_number'] = 668
                        break                   
                    if this_word == 'North2':
                        ix_detail_dict[row[4]]['facility_number'] = 4360
                        break
                    if this_word == 'Newport(NGD)':
                        ix_detail_dict[row[4]]['facility_number'] = 1548
                        break
                    if this_word == 'LD8':
                        ix_detail_dict[row[4]]['facility_number'] = 45
                        break
                    if this_word == 'Digital':
                        # print(ix_detail_dict[row[4]]['Location'].split(' (')[1])
                        if ix_detail_dict[row[4]]['Location'].split(' (')[1].split(' ')[0] == '44521':
                            ix_detail_dict[row[4]]['facility_number'] = 1380
                            # print(mysearch)
                            break
                        elif ix_detail_dict[row[4]]['Location'].split(' (')[1].split(' ')[0] == 'RBS)':
                            ix_detail_dict[row[4]]['facility_number'] = 40
                            # print(ix_detail_dict[row[4]]['facility_number'])
                            #input('wait')
                            break
                        elif ix_detail_dict[row[4]]['Location'].split(' (')[1].split(' ')[0] == 'TCM)':
                            ix_detail_dict[row[4]]['facility_number'] = 43
                            # print(ix_detail_dict[row[4]]['facility_number'])
                            #input('wait')
                            break
                        else:
                            ix_detail_dict[row[4]]['facility_number'] = 0
                            break
                    if this_word == 'Iron':
                        ix_detail_dict[row[4]]['facility_number'] = 5373
                        break
                    if this_word == 'Newport(NGD)':
                        ix_detail_dict[row[4]]['facility_number'] = 1548
                        break
                    if this_word == 'Quality':
                        #Not sure if this is correct facility
                        ix_detail_dict[row[4]]['facility_number'] = 350
                        break
                    
                    #print('Count', count)
                    if this_word.casefold() in facilitys_uk[facility]["name"].casefold():
                        #print(this_word,count, word_count,facilitys_uk[facility]["name"])
                        
                        if  count == word_count:
                            
                            ix_detail_dict[row[4]]['facility_number'] = facility

                    else:
                        break
                #print('Facility number', facility)
                if ix_detail_dict[row[4]]['facility_number'] != 0:
                    break
    
    # Now Add the LONAP IXP information to the ix_details list at https://portal.lonap.net/api/v4/member-export/ixf/.
    # in the same format as the LINX IXP details
    # example : "195.66.224.74": {
    #"facility_number": "34",
    #"Organisation Name": "Zzoomm PLC",
    #"Website": "http://",
    #"ASN": "42611",
    #"Peering Policy": "No data",
    #"IPv6 Address": "2001:7f8:4::a673:1",
    #"MAC Address": "a4e1.1a6e.ce0b",
    #"Location": "Telehouse North (THN)",
    #"Switch Port and VLAN": "edge1-thn xe-2/3/0",
    #"Port Type": "10G",
    #"Service Speed": "10G",
    #"Service Type": "Regular",
    #"Peering LAN": "lon1",
    #"Membership Type": "full",
    #"Route Servers": "rs1.lon1, rs2.lon2, rs3.lon1, rs4.lon2"
    # }

    

    with open('ix_info/lonap_data.json') as f:
        lonap_measurements = json.load(f)
    # example IXP and switch entry, note only one ixp and vlan, (LONAP), but multiple switches situated at different facilities
    #
    lonap_switches = {}
    for switch in lonap_measurements['ixp_list'][0]['switch']:
        # print(switch)
        id = switch['id']
        lonap_switches[id] = {}
        lonap_switches[id]["name"] = switch['name'],
        lonap_switches[id]["location"] = switch["colo"]
        lonap_switches[id]["city"] = switch['city']
        lonap_switches[id]["country"]: switch['country']
        lonap_switches[id]['pdb fac'] = switch['pdb_facility_id']
        lonap_switches[id]['manufacturer'] = switch['manufacturer']
        lonap_switches[id]['model'] = switch['model']
        lonap_switches[id]['software'] = switch['software']
        
        
    for member in lonap_measurements["member_list"]:
        #print(member)
        
        for connection in member["connection_list"]:
            #print('CCCCCCCCCCCCCCC')
            #print(connection) 
            for vlan in connection['vlan_list']:
                #print('VVVVVVVVVVVVV')
                #print(vlan)
                if 'ipv4' in vlan.keys():
                    ipaddress = vlan['ipv4']['address']
                    ix_detail_dict[ipaddress]= {}
                    print(ipaddress,vlan)
                    #input('ip,vlan')
                    
                    ix_detail_dict[ipaddress]["Organisation Name"] = member['name']
                    ix_detail_dict[ipaddress]["Website"] = member['url']
                    ix_detail_dict[ipaddress]['ASN'] = member['asnum']
                    ix_detail_dict[ipaddress]["Peering Policy"] = member['peering_policy']
                    if 'ipv6' in vlan.keys():
                        ix_detail_dict[ipaddress]["IPv6 Address"] = vlan['ipv6']['address']
                    else:
                        ix_detail_dict[ipaddress]["IPv6 Address"] = ''
                    ix_detail_dict[ipaddress]["MAC Address"] = vlan['ipv4']['mac_addresses']
                    ix_detail_dict[ipaddress]['Port Type'] = ''
                    ix_detail_dict[ipaddress]["Service Speed"] = connection['if_list'][0]['if_speed']      

                    ix_detail_dict[ipaddress]["Service Type"] = ''
                    ix_detail_dict[ipaddress]["Peering LAN"] = "LONAP Peering LAN #1"
                    ix_detail_dict[ipaddress]["Membership Type"] = member['member_type']
                    ix_detail_dict[ipaddress]["Route Servers"]  = '' 
           
                    # sometimes there are multiple switches listed however in every case analysed they are duplicates
                    # so only need first one
                    
                    id = connection['if_list'][0]['switch_id']

                    #print(lonap_measurements['ixp_list']['switch'])
                    ix_detail_dict[ipaddress]["Location"] = lonap_switches[id]['location']
                    ix_detail_dict[ipaddress]["Switch Port and VLAN"] = lonap_switches[id]['name']
                    ix_detail_dict[ipaddress]["facility_number"] =  str(lonap_switches[id]['pdb fac'])

                    #print('HERE',ix_detail_dict[ipaddress])  
                    #input('wait')

    #Add any IXs that have been manually found that do not appear on a members list
    # Equinxi Manchester IX does not seem to have a public members list
    ix_detail_dict["185.1.101.28"] ={}
    ix_detail_dict["185.1.101.28"]["facility_number"] = "76"
    ix_detail_dict["185.1.101.28"]["Organisation Name"] = "Equinix Inc"
    ix_detail_dict["185.1.101.28"]["Website"] = "http://www.equinix.com/"
    ix_detail_dict["185.1.101.28"]["ASN"] ="42611"
    ix_detail_dict["185.1.101.28"]["Peering Policy"] = "No data"
    ix_detail_dict["185.1.101.28"]["IPv6 Address"] = ""
    ix_detail_dict["185.1.101.28"]["MAC Address"] = ""
    ix_detail_dict["185.1.101.28"]["Location"] = "Equinix Internet Exchange, manchester"
    ix_detail_dict["185.1.101.28"]["Switch Port and VLAN"] = ""
    ix_detail_dict["185.1.101.28"]["Port Type"] = ""
    ix_detail_dict["185.1.101.28"]["Service Speed"] = ""
    ix_detail_dict["185.1.101.28"]["Service Type"] = ""
    ix_detail_dict["185.1.101.28"]["Peering LAN"] =""
    ix_detail_dict["185.1.101.28"]["Membership Type"] =""
    ix_detail_dict["185.1.101.28"]["Route Servers"] = ""

    # Linx london. for some reason this is not on their list
    ip = '195.66.226.35' 
    ix_detail_dict[ip] ={}
    ix_detail_dict[ip]["facility_number"] = "34"
    ix_detail_dict[ip]["Organisation Name"] = "London Internet Exchange Ltd."
    ix_detail_dict[ip]["Website"] = "http://www.linx.net/"
    ix_detail_dict[ip]["ASN"] ="5459"
    ix_detail_dict[ip]["Peering Policy"] = "No data"
    ix_detail_dict[ip]["IPv6 Address"] = ""
    ix_detail_dict[ip]["MAC Address"] = ""
    ix_detail_dict[ip]["Location"] = "London Internet Exchange (LINX)"
    ix_detail_dict[ip]["Switch Port and VLAN"] = ""
    ix_detail_dict[ip]["Port Type"] = ""
    ix_detail_dict[ip]["Service Speed"] = ""
    ix_detail_dict[ip]["Service Type"] = ""
    ix_detail_dict[ip]["Peering LAN"] =""
    ix_detail_dict[ip]["Membership Type"] =""
    ix_detail_dict[ip]["Route Servers"] = ""

    # Linx lon2. for some reason this is not on their list
    ip = '195.66.238.35' 
    ix_detail_dict[ip] ={}
    ix_detail_dict[ip]["facility_number"] = "34"
    ix_detail_dict[ip]["Organisation Name"] = "Avensys."
    ix_detail_dict[ip]["Website"] = "https://www.avensys.net/"
    ix_detail_dict[ip]["ASN"] ="8553"
    ix_detail_dict[ip]["Peering Policy"] = "No data"
    ix_detail_dict[ip]["IPv6 Address"] = ""
    ix_detail_dict[ip]["MAC Address"] = ""
    ix_detail_dict[ip]["Location"] = "London Internet Exchange (LINX)"
    ix_detail_dict[ip]["Switch Port and VLAN"] = ""
    ix_detail_dict[ip]["Port Type"] = ""
    ix_detail_dict[ip]["Service Speed"] = ""
    ix_detail_dict[ip]["Service Type"] = ""
    ix_detail_dict[ip]["Peering LAN"] =""
    ix_detail_dict[ip]["Membership Type"] =""
    ix_detail_dict[ip]["Route Servers"] = ""


if __name__ == "__main__":

    global ix_detail_dict
    ix_detail_dict = {}

    global facilitys_uk
    # Read in the UK Facilities records
    with open('peeringdb_test_results/uk_facilities_to_networks_good.json') as f:
        facilitys_uk = json.load(f)

    create_ixinfo()


    # ix_detail_dict now has a cross reference between Ip addresses and facilities.
    # These only include the LINX and LONAP networks but more can be added to this
    #print('40',ix_detail_dict['185.1.101.28'])
    #print('#######')
    #print('42',ix_detail_dict['195.66.244.42'])
    #input('wait')
    ix_details_file = 'results/ix_details.json'
    with open(ix_details_file, 'r') as f:
        ix_detail_dict = json.load(f)  
    
    #print (ix_detail_dict)
    
    #print('40',ix_detail_dict['185.1.101.28'])
    print('#######')
    print('42',ix_detail_dict['195.66.244.42'])
    print (facilitys_uk['1403'])

    # test with a select
    con = sqlite3.connect("/home/paul/Documents/UK/data/CAIDA/midar.db")
    cursor = con.cursor()
    sqlselect = "SELECT * FROM ips"
    cursor.execute(sqlselect)
  
    print("All the data")
    output = cursor.fetchall()
    for row in output:
        print(row)
    
    con.commit()
    
    # Close the connection
    con.close()
    input('wait')
    input('wait')
    


    