from peeringdb import PeeringDB, resource, config
# Table Names
#peeringdb_network         
#peeringdb_facility          peeringdb_network_contact 
#peeringdb_ix                peeringdb_network_facility
#peeringdb_ix_facility       peeringdb_network_ixlan   
#peeringdb_ixlan             peeringdb_organization    
#peeringdb_ixlan_prefix    

# 
# import django
import peeringdb
import json

# couldnt get django working (config.yaml, peeringdb.django, virtualenv)and when i use  peeringdb.pythons PDB keeps aacessing the online database which then creates too many requests and 
# I am stopped from accessing the database so have had to resort to using sqlite3 module to access the local sqlite3 file.
# which complicates things but  i can create dictionaries from the sqlite3 databases and just work with them

import sqlite3

pdb = PeeringDB()
#pdb.update_all() # unmark this to update the sqllite3 database with changes
from pprint import pprint

 # read from SQLlite3 database and create UK Internet Exchange Dictionary

def get_ixps():
    con = sqlite3.connect("/home/paul/peeringdb.sqlite3")
    cur = con.cursor()

    #cur.execute("select * from peeringdb_ix where status = 'deleted'")
    #uk_ixs = cur.fetchone()

    

    # get Internet Exchange info
    cur.execute("select * from peeringdb_ix where country = 'GB'")
    uk_ixs = cur.fetchall()
    colnames = cur.description
    #print(colnames)

   



    # con.close()

    uk_ix_dict ={}
    ixp_dict ={}
    number = 0
   
    for ix in uk_ixs:
        number += 1
        # print('\n')
        # print('********* ix', ix,'**************************************\n')
        i = 0
        uk_ix_dict[ix[0]] = {}
        ixp_dict [ix[0]] = {} # this will be the dictionary that is returned and is similar to how pdb formats the dictionary
        ix_id = (ix[0],)
        # get facilities that this ixp is peered at info
        cur.execute('select * from peeringdb_ix_facility where ix_id =?',ix_id) 
        facilities = cur.fetchall()
        ixp_dict[ix[0]]["fac_set"] = []
        for fac in facilities:
            ixp_dict[ix[0]]["fac_set"].append(fac[5])
        # print(ixp_dict[ix[0]]["fac_set"])

        cur.execute('select * from peeringdb_ixlan where ix_id =?',ix_id) 
        ix_lan = cur.fetchall() 
        
        # get lans that belong to this ixp ( I think theres usually only one ixlan but to keep it consistent with PDB I have tuned it into a list of lists)
        ixp_dict[ix[0]]["ixlan_set"] = []       
        for lan in ix_lan:
            lan_list = [lan[0]]
            ixp_dict[ix[0]]["ixlan_set"].append(lan_list)
        
        print(ixp_dict[ix[0]])
        print (ix_lan)
        
        
        for column in colnames:
            print (ix[0],ix[i],column[0])
            uk_ix_dict[ix[0]][column[0]] = ix[i]
            i += 1

            '''
            print('this column is',column[0],'and its value is',ix[j])           
            print('this part of the dict is',uk_ix_dict[ix[0]])         
            input('wait')
            '''
        print('\n*******************************************')
        print('Entire dictionary is',uk_ix_dict)
        print('\n*******************************************')
        ixp_dict[ix[0]]["name"] = [uk_ix_dict[ix[0]]["name"]]
        ixp_dict[ix[0]]["org-id"] = [uk_ix_dict[ix[0]]["org_id"]]
       
        
        # get prefixes that belong to this
        cur.execute('select * from peeringdb_ixlan_prefix where ixlan_id =?',ix_id) 
        ix_prefix = cur.fetchall() 
        for prefix in ix_prefix:
            if prefix[1] == 'ok':
                if prefix[6] == 'IPv4':
                    ixp_dict[ix[0]]["ipv4_prefix"] = prefix[7]
                if prefix[6] == 'IPv6':
                    ixp_dict[ix[0]]["ipv6_prefix"] = prefix[7]
        
        # print(ix_prefix) 
        # colnames = cur.description
        # print(colnames)
        
        print('ipx-dict is',ixp_dict)

        
        #input('wait')
    con.close()
    with open('Documents/UK/peeringdb_test_results/uk_ixps.json', 'w') as outfile:
            json.dump(ixp_dict, outfile)
    outfile.close()
    
    print(number)
    input('wait')
    return ixp_dict

def get_facilities():
    con = sqlite3.connect("/home/paul/peeringdb.sqlite3")
    cur = con.cursor()

    #cur.execute("select * from peeringdb_ix where status = 'deleted'")
    #uk_ixs = cur.fetchone()

    

    # get Internet Exchange info
    cur.execute("select * from peeringdb_facility where country = 'GB'")
    uk_fac = cur.fetchall()

    uk_fac_dict ={}
    for fac in uk_fac:
        uk_fac_dict[fac[0]] = {}
        uk_fac_dict[fac[0]]['org_id'] = fac[19]
        uk_fac_dict[fac[0]]['name'] = fac[13]
        uk_fac_dict[fac[0]]['address1'] = fac[5]
        uk_fac_dict[fac[0]]['address2'] = fac[6]
        uk_fac_dict[fac[0]]['city'] = fac[7]
        uk_fac_dict[fac[0]]['country'] = fac[10]
        uk_fac_dict[fac[0]]['postcode'] = fac[9]
        uk_fac_dict[fac[0]]['latitude'] = fac[11]
        uk_fac_dict[fac[0]]['longitude'] = fac[12]


        
    
   
    with open('Documents/UK/peeringdb_test_results/uk_facilities.json', 'w') as outfile:
            json.dump(uk_fac_dict, outfile)
    outfile.close()



    con.close()
    print(uk_fac_dict)
    input('wait')

# Return first result of query
#cur.fetchone()

#df = pd.read_sql_query("select * from peeringdb_facility where country = 'GB'", con)
#print(df.head())

#print(peeringdb.get_backend_info()[1])
#n1 = pdb.get(resource.Network, 1)
#print(n1)


ix_dict = get_ixps()
# get_facilities()


input('wait and done')
pprint(dir(peeringdb))
'''
• ixlan
• Describes the LAN of an IX
• One IX may have multiple ixlan
• May go away with PeeringDB 3.0
• ixpfx
• Describes the IP range (IPv4 and IPv6) for an ixlan
• One ixlan may have multiple ixpfx, both for IPv4 and IPv6
• netixlan
• Describes the presence of a network at an IX
• netfac
• Describes the presence of a network at a facility
'''
# https://github.com/grizz/pdb-examples
# EXAMPLE SCRIPT lookup network by ASN
#pdb.update_all()
#print ("TAGS")
#pprint(dir(pdb.tags.ix.all))


'''

'Class',
 'Facility',
 'InternetExchange',
 'InternetExchangeFacility',
 'InternetExchangeLan',
 'InternetExchangeLanPrefix',
 'Meta',
 'Network',
 'NetworkContact',
 'NetworkFacility',
 'NetworkIXLan',
 'OrderedDict',
 'Organization',
 'RESOURCES_BY_TAG',

 '''
ixes = 1
exc = pdb.fetch_all(resource.InternetExchange)
fac_id = pdb.fetch_all(resource.InternetExchangeFacility)
facility = pdb.fetch_all(resource.Facility)
number = 0
for ix in exc:
    number += 1
    if ix['country'] == 'GB':
        
        
        print('===========================================')
        print(ixes,ix['name'], ix['org_id'])

        print(ix)
        print('===========================================')
        #exchanges[ixes] = ix
        ixes += 1
        facs = 1
        input("wait")

        # Print each of the facilities info that belongs to this IX
        for fac in ix['fac_set']:
            print(fac)
            f = pdb.fetch(resource.Facility, fac)
            print('Facility',facs,f)
            
            facs += 1
        ixs = 1

        # print a list of networks that peer at this IX
        for ix_lan in ix['ixlan_set']:
            print('++++++++++++++++++++++++++++++++++++++++++++++++++++')
            print(ix_lan)
            i = pdb.fetch(resource.InternetExchangeLan, ix_lan)
            print('Ix Lan',ixs,i)
            nets = 1
            print(i[0]['net_set'])
            input("wait")

            # Print each networks detailed info at this IX
            for net in i[0]['net_set']:
    
                print('---------------------------------------------------------')
                print(net)
                n = pdb.fetch(resource.Network, net)
                print('Network',nets,n)
                print('---------------------------------------------------------')
                nfacs = 1
                input("wait")
                # print each facility where this network peers
                for nf in n[0]['netfac_set']: # ties the facility into the network
                    print('fffffffffffffffffffffffffffffffffffffffffffffff')
                    print(nf)
                    nfac = pdb.fetch(resource.NetworkFacility, nf)
                    print('Network Facilities',nfacs,nfac)
                    print('ffffffffffffffffffffffffffffffffffffffffffffffff')
                    nfacs += 1
                    
                ixlans = 1
                
                for ixl in n[0]['netixlan_set']: 
                    print('nnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnn')
                    print(ixl)
                    ixlan = pdb.fetch(resource.NetworkIXLan, ixl)
                    print('Network IXLAN',ixlans,ixlan)
                    print('nnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnn')
                    ixlans += 1
                    input("wait")
                nets += 1
            print('++++++++++++++++++++++++++++++++++++++++++++++++++++')
            ixs += 1
'''
#print(exc[287])
print(fac[0])
'''



        
