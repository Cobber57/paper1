import json
import jsonpickle # used for sets for Caida data
import csv
import os
os.chdir('/home/paul/Documents/UK')
del os 
#import sqlite3


def read_file(r):
    
    file2name = "results/targetslatest.json"
    #results/targetslatest.json
    with open(file2name,'r') as in2file:
        targets = json.load(in2file)

    filename ="results/vptables/final_vptable.json"
    #results/vptables/final_vptable.json
    with open(filename,'r') as infile:
        results = json.load(infile)
    
    #print(type(results))

    
    
    
    i = 0
    ips ={}
    
    for ip in results:
        
        lat = results[ip]['lat']
        rdns = results[ip]['rdns']
        facility = results[ip]['facility']
        #print('RESULTS is',results[ip], 'IP is',ip)
        code =  results[ip]['code']

       
        # determine how many records were found without a rDNS lookup and no facility.
        # basically Rule 1 checking for hop1 RTT value
        if r == 1 and lat != 0 and rdns == '' and facility =='':
            print(ip,results[ip])
            i +=1
            ips[ip] =[]
            
            for measurement in targets:
                for source_probe in targets[measurement]['results']:
                    for hop in targets[measurement]['results'][source_probe]['hops']:
                        if targets[measurement]['results'][source_probe]['hops'][hop]['ip_from'] == ip:
                            rtt = targets[measurement]['results'][source_probe]['hops'][hop]['rtt']
                            ips[ip].append(source_probe)
                            ips[ip].append(hop)
                            ips[ip].append(rtt)
            #print(ips[ip])
            #input('wait')
        
        # how many are located that are actually private IP addresses
        elif r == 2 and code == 2  and ip[:3] == '10.' :
            print(ip,results[ip])
            i +=1
            ips[ip] =[]
            
            for measurement in targets:
                for source_probe in targets[measurement]['results']:
                    for hop in targets[measurement]['results'][source_probe]['hops']:
                        if targets[measurement]['results'][source_probe]['hops'][hop]['ip_from'] == ip:
                            rtt = targets[measurement]['results'][source_probe]['hops'][hop]['rtt']
                            ips[ip].append(source_probe)
                            ips[ip].append(hop)
                            ips[ip].append(rtt)
            print(ips[ip])
        
        
        # how many are target ip addresses RULE 3
        elif r == 3 and code == 2  and rdns[:5] == 'PROBE' :
            print(ip,results[ip])
            i +=1
            ips[ip] =[]
            
            for measurement in targets:
                for source_probe in targets[measurement]['results']:
                    for hop in targets[measurement]['results'][source_probe]['hops']:
                        if targets[measurement]['results'][source_probe]['hops'][hop]['ip_from'] == ip:
                            rtt = targets[measurement]['results'][source_probe]['hops'][hop]['rtt']
                            ips[ip].append(source_probe)
                            ips[ip].append(hop)
                            ips[ip].append(rtt)
            print(ips[ip])
            #input('wait')
        
        
        # determine how many records were found without a rDNS lookup but had a facility.
        # basically Rule 4 checking using facility location
        elif r == 4 and lat != 0 and rdns == '' and facility !='':
            print(ip,results[ip])
            i +=1
            ips[ip] =[]
            
            for measurement in targets:
                for source_probe in targets[measurement]['results']:
                    for hop in targets[measurement]['results'][source_probe]['hops']:
                        if targets[measurement]['results'][source_probe]['hops'][hop]['ip_from'] == ip:
                            rtt = targets[measurement]['results'][source_probe]['hops'][hop]['rtt']
                            ips[ip].append(source_probe)
                            ips[ip].append(hop)
                            ips[ip].append(rtt)
            print(ips[ip])
            #input('wait')
        
        # how many are located using regex or other method RULE 5
        elif r == 5 and code == 2 and rdns != '' and rdns[:5] != 'PROBE' :
            print(ip,results[ip])
            i +=1
            ips[ip] =[]
            if ip == "185.40.232.21":
                print('HERE')
                input('wait')
            
            for measurement in targets:
                for source_probe in targets[measurement]['results']:
                    for hop in targets[measurement]['results'][source_probe]['hops']:
                        if targets[measurement]['results'][source_probe]['hops'][hop]['ip_from'] == ip:
                            rtt = targets[measurement]['results'][source_probe]['hops'][hop]['rtt']
                            ips[ip].append(source_probe)
                            ips[ip].append(hop)
                            ips[ip].append(rtt)
            print(ips[ip])
            #input('wait')
        
        

    print('I IS',i )



if __name__ == "__main__":  
    # r =1 test for how many records were found without a rDNS lookup and no facility.
    # r = 2 how many records were found without a rDNS lookup but had a facility.
    # r = 3 how many were succesfully looked up using Rule 5
    read_file(5) 
    