from peeringdb import PeeringDB, resource, config
# Table Names
#peeringdb_network         
#peeringdb_facility          peeringdb_network_contact 
#peeringdb_ix                peeringdb_network_facility
#peeringdb_ix_facility       peeringdb_network_ixlan   
#peeringdb_ixlan             peeringdb_organization    
#peeringdb_ixlan_prefix    

import django
import peeringdb

# couldnt get django working (config.yaml, peeringdb.django, virtualenv)and PDB keeps aacessing the online database which then creates too many requests and 
# I am stopped from accessing the database so have had to resort to using sqlite3 module to access the local sqlite3 file.
#import pandas as pd
import sqlite3

pdb = PeeringDB()
#pdb.update_all()
from pprint import pprint

con = sqlite3.connect("/home/paul/peeringdb.sqlite3")
cur = con.cursor()

#cur.execute("select * from peeringdb_ix where status = 'deleted'")
#uk_ixs = cur.fetchone()

#print(uk_ixs)
#input('wait')

cur.execute("select * from peeringdb_ix where country = 'GB'")
uk_ixs = cur.fetchall()
colnames = cur.description
#print(colnames)
con.close()

uk_ix_dict ={}

for ix in uk_ixs:
    print('\n')
    print('********* ix', ix,'**************************************\n')
    j= 0
    uk_ix_dict[ix[0]] = {}
    for column in colnames:
        print (ix[0],ix[j],column[0])
        uk_ix_dict[ix[0]][column[0]] = ix[j]
        print('this column is',column[0],'and its value is',ix[j])
        
        print('this part of the dict is',uk_ix_dict[ix[0]])
     
        j += 1
        input('wait')
    print('\n*******************************************')
    print('Entire dictionary is',uk_ix_dict)
    print('\n*******************************************')
      
        
# Return first result of query
#cur.fetchone()

#df = pd.read_sql_query("select * from peeringdb_facility where country = 'GB'", con)
#print(df.head())

#print(peeringdb.get_backend_info()[1])
#n1 = pdb.get(resource.Network, 1)
#print(n1)




input('wait')
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

for ix in exc:
    
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



        
