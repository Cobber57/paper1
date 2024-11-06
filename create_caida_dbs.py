import json
import jsonpickle # used for sets for Caida data
import csv
import os
os.chdir('/home/paul/Documents/UK')
del os 
import sqlite3

def insintotable(node,town,lat,lon,source):
    try:
        sqliteConnection = sqlite3.connect('/home/paul/Documents/UK/data/CAIDA/caida.db')
        cursor = sqliteConnection.cursor()
        #print("Connected to SQLite")

        sqlite_insert_with_param = """INSERT INTO geo
                        (node,town,lat,lon,source) 
                        VALUES (?, ?, ?,?,?);"""

        data_tuple = (node,town,lat,lon,source)
        cursor.execute(sqlite_insert_with_param, data_tuple)
        sqliteConnection.commit()
        #print("Python Variables inserted successfully into ips table")

        cursor.close()

    except sqlite3.Error as error:
        print("Failed to insert Python variable into sqlite table", error)
    finally:
        if sqliteConnection:
            sqliteConnection.close()
            #print("The SQLite connection is closed")
        
def insintotablenode(ip,node):
    try:
        sqliteConnection = sqlite3.connect('/home/paul/Documents/UK/data/CAIDA/caida.db')
        cursor = sqliteConnection.cursor()
        #print("Connected to SQLite")

        sqlite_insert_with_param = """INSERT INTO ips
                        (ip,node) 
                        VALUES (?, ?);"""

        data_tuple = (ip,node)
        cursor.execute(sqlite_insert_with_param, data_tuple)
        sqliteConnection.commit()
        #print("Python Variables inserted successfully into ips table")

        cursor.close()

    except sqlite3.Error as error:
        print("Failed to insert Python variable into sqlite table", error)
    finally:
        if sqliteConnection:
            sqliteConnection.close()
            #print("The SQLite connection is closed")

def drop_tables(): 
    # set double_check to True below if you definitely want to drop both tables
    # else rem out whichever table you dont want to drop
    double_check = False
    if double_check:
        # example of sql cmd cursor.execute("""CREATE TABLE ips (id INTEGER PRIMARY KEY AUTOINCREMENT, ip varchar(15), node varchar(15))""")
        #create CAIDA table
        con = sqlite3.connect("/home/paul/Documents/UK/data/CAIDA/caida.db")
        cursor = con.cursor()
        sqliteDropTable     = "DROP TABLE IF EXISTS geo"
        cursor.execute(sqliteDropTable) 
        sqliteDropTable     = "DROP TABLE IF EXISTS ips"
        cursor.execute(sqliteDropTable)  

def create_tables():
    # latitude Decimal(8,6), and longitudes use: Decimal(9,6)
    # node,town,lat,lon,source
    con = sqlite3.connect("/home/paul/Documents/UK/data/CAIDA/caida.db")
    cursor = con.cursor()
    #cursor.execute("""CREATE TABLE geo (node varchar(15) PRIMARY KEY , town varchar(20), lat Decimal(8,6), lon Decimal(9,6), source varchar(20) )""")
    #con.commit()
    cursor.execute("""CREATE TABLE ips (ips varchar(15) PRIMARY KEY , node varchar(15))""")
    con.commit()
    print('database created')

def test_db():
    # test with a select
    con = sqlite3.connect("/home/paul/Documents/UK/data/CAIDA/caida.db")
    cursor = con.cursor()
    sqlselect = "SELECT * FROM geo"
    cursor.execute(sqlselect)

    print("All the data")
    output = cursor.fetchall()
    for row in output:
        print(row)

    con.commit()

    # Close the connection
    con.close()

def build_geo_table():
    # reads in each node from CAIDA geo file, checks if they are GB
    # and inserts them into the CAIDA geo table
    # creates a node set and saves it in a file for later use
    # returns the node set and the name of the node set file
    node_set = set()
    with open('data/CAIDA/midar-iff.nodes.geo', mode = 'r') as csv_file:
        csvreader = csv.reader(csv_file)
        # extracting field names through first row
        for i in range(0,6):
            fields = next(csvreader)
        # extracting each data row one by one
        for row in csvreader:
            #print('rows are',row)
            nodea = row[0].split(':')[0]
            node = nodea.split(' ')[1]
            #print('node is',node)
            countrya = row[0].split(':')[1]
            country = countrya.split('\t')[2]
            #print('country is',country)
            if country == 'GB':
                town = countrya.split('\t')[4]
                lat = countrya.split('\t')[5]
                lon = countrya.split('\t')[6]
                source = countrya.split('\t')[9]
                #print(town,lat,lon,source)
                insintotable(node,town,lat,lon,source)
                node_set.add(node)
                #print(node_set)
                #input('wait')
                
    gb_nodes_json = jsonpickle.encode(node_set)
    print('GBNODESJSON IS',gb_nodes_json)
    out_file = 'data/CAIDA/gb_nodes.json'
    with open(out_file, 'w') as f:
        json.dump(gb_nodes_json, f)                   
    print('gb_nodes WRITTEN TO data/CAIDA/gb_nodes.json')
    return node_set, out_file
'''
def build_ips_table():
    # reads in each node from CAIDA db and inserts them into the ips table
    # NOTE DIDNT WORK see ver2
    with open('data/CAIDA/midar-iff.nodes', mode = 'r') as csv_file:
        
        csvreader = csv.reader(csv_file)
        # extracting field names through first row
        for i in range(0,4735):
            fields = next(csvreader)
        # extracting each data row one by one
        row_count= 0
        ip_count = 0
        ip_total = 0

        for row in csvreader:
            #print('rows are',row_count)
            
            #ips_list = row.split(':  ')[1]
            ips = (row[0].split(':  ')[1])
            nodea = (row[0].split(':  ')[0])
            print(nodea)
            node  = nodea.split(' ')[1]
            print('node is',node)
            if node in node_set:
            #print(ips)
                insintotablenode(node,ips)
'''            
def build_ips_table():
    # version2
    # reads in each node from CAIDA db and inserts them into the ips table  
    # the ips insertions above didnt work overnight so will use the 'data/CAIDA/gb_nodes.json' file
    # to create the ips table instead
    '''
    # this didnt work because the file is too big
    with open('data/CAIDA/gb_nodes.json') as f:
        nodes_uk = json.load(f)
    for node in nodes_uk:
        print('node is', node)
        input('wait')
    '''
    con = sqlite3.connect("/home/paul/Documents/UK/data/CAIDA/caida.db")
    cursor = con.cursor()
    sqlselect = "SELECT * FROM geo"
    cursor.execute(sqlselect)
    
    print(type(records))
    
    with open('data/CAIDA/midar-iff.nodes', mode = 'r') as csv_file:
        csvreader = csv.reader(csv_file)
        # extracting field names through first row
        for i in range(0,4735):
            fields = next(csvreader)
        # extracting each data row one by one
        row_count= 0
        ip_count = 0
        ip_total = 0

        
        nodes={}
        
        for row in csvreader:
            #print('rows are',row_count)
            
            #ips_list = row.split(':  ')[1]
            ips = (row[0].split(':  ')[1])
            nodea = (row[0].split(':  ')[0])
            #print(nodea)
            node  = nodea.split(' ')[1]
            #print('Node is', node)
            ips_list = ips.split(' ')
            #print('IPS lISt is',ips_list)
            #nodes[node] = {}
            nodes[node] = ips_list


            #print('nodes is',nodes)
            #input('WAIT')

        for record in records:
            
            node = record(0)
            if node in nodes:
                print('RECORD is', record)
                print('Node is',node)
                print(nodes[node])
            #for node in records
            input('wait')
        
        '''
        for this_ip in ips_list:
            #print(this_ip,node)
            insintotablenode(this_ip,node)  
            #input('wait')  
        '''
            
def count_records():
    con = sqlite3.connect("/home/paul/Documents/UK/data/CAIDA/caida.db")
    cursor = con.cursor()
    rowsQuery = "SELECT Count() FROM geo" 
    cursor.execute(rowsQuery)
    numberOfRows = cursor.fetchone()[0]
    print('rows are',numberOfRows)



if __name__ == "__main__":  
    #build_ips_table() 
    #count_records()
    test_db() 
    