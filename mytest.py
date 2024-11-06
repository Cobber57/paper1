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

# provide IX id and get IXLAN id
#cur.execute("select * from peeringdb_ixlan where id = 18")
#data = cur.fetchall()
#ixlan_id = (data[0][12],)

#======================================
# How to get the ASn given an Ip address

cur.execute("select * from peeringdb_network_ixlan where ipaddr4 = '195.66.224.253'")
data = cur.fetchone()
colnames = cur.description
print(colnames)
print('Network is',data[12])
x = (data[12],)

cur.execute("select * from peeringdb_network where id = ?",x )

data = cur.fetchone()
colnames = cur.description
print(colnames)
print('asn is',data[5])
'''
#============================================

cur.execute("select * from peeringdb_ix where id = 18")
data = cur.fetchall()
colnames = cur.description
print(colnames)
print(data)

'''


# provide ixlan_id and get  prefix (ensure status is ok and protocol is IPv4)
#cur.execute("select * from peeringdb_ixlan_prefix where Ixlan_id = 18")
# data = cur.fetchall()

# provide ixlan_id and get LAN id's
'''
cur.execute("select * from peeringdb_network_ixlan where Ixlan_id = 18")
data = cur.fetchall()
for i in data:
    if i[13] == 1:
        print(colnames[6][0],colnames[10][0],colnames[12][0])
        print(i[6],i[10],i[12])
        input('wait')
'''
#cur.execute("select * from peeringdb_network")
#data = cur.fetchone()



# print(ixlan_id)
con.close()