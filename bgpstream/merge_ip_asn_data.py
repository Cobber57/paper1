
#!/usr/bin/env python

import pybgpstream
import ipaddress
import requests
import gzip

# see if asn to ip list is already created (list02 in default dir)
file_already_created = True

if file_already_created == False:

    prefixes=[]

    # UK Prefixes provided by  https://team-cymru.com/community-services/ip-asn-mapping/ 
    # download this input file from ftp.ripe.net/ripe/stats/delegated-ripencc-latest
    # Once file is created run it through the following commnad to create list02
    # netcat whois.cymru.com 43 < prefix_list | sort -n > list02
    # this will create asn to Ip lookup table
    prefixes_file =''
    with open('uk_prefixes', 'r')  as myfile:
        for line in myfile:
            print(line)
            prefix = line.split('|')[3]
            subnet = line.split('|')[4]
            if subnet == '256':
                cidr = '24'
            elif subnet == '512':
                cidr = '23'
            elif subnet == '1024':
                cidr = '22'
            elif subnet == '2048':
                cidr = '21'
            elif subnet == '4096':
                cidr = '20'
            elif subnet == '8192':
                cidr = '19'
            elif subnet == '16384':
                cidr = '18'
            elif subnet == '32768':
                cidr = '17'
            elif subnet == '65536':
                cidr = '16'
            elif subnet == '131072':
                cidr = '15'
            elif subnet == '262144':
                cidr = '14'
            elif subnet == '524288':
                cidr = '13'
            elif subnet == '1048576':
                cidr = '12'
            else:
                print(subnet,cidr) 
            prefixes.append(prefix + '/' +cidr)
            prefixes_file = prefixes_file+prefix+'/'+cidr+'\n'
    f = open('prefix_list', 'w')
    f.write('begin\n')
    f.write('verbose\n')
    f.write(prefixes_file)
    f.write('end\n')
    f.close()
prefixes = []
with open('prefix_list', 'r') as prefile:
    for line in prefile:
        
        # print(line)
        line = line.split('\n')[0]
        print('LINE IS ', line)
        prefixes.append(line)

prefixes.remove('begin')
prefixes.remove('verbose')
prefixes.remove('end')
#print('PREFIXES ARE', prefixes)
#input('wait')

filter_string="collector rrc00 and type updates"
for p in prefixes:
    filter_string = filter_string + ' and more '+ str(p)

# filter_string = "collector rrc00"
print('FILTER STRING IS',filter_string)
'''
stream = pybgpstream.BGPStream(
    # accessing ris-live
    project="routeviews-stream",
    # filter to show only stream from rrc00
    filter="router amsix",
)

for elem in stream:
    print(elem)
'''
# tried doing it through a live stream but wouldnt work
'''
stream = pybgpstream.BGPStream(
    # accessing ris-live
    project="ris-live",
    # filter to show only stream from rrc00
    filter="collector rrc00",
)
for element in stream:

elem = str(element)
print(elem)
asn = elem.split('|')[7]
this_ip = elem.split('|')[8]
ipprefix = elem.split('|')[9]
aspath = elem.split('|')[10]
communities = elem.split('|')[11]
print(asn)
for this_prefix in prefixes:
    print(this_ip, this_prefix)
    if ipaddress.ip_address(str(this_ip)) in ipaddress.ip_network(this_prefix):
        print(this_ip,this_prefix)
        print(elem)
'''
url = 'https://data.ris.ripe.net/rrc00/latest-update.gz'
r = requests.get(url, allow_redirects=True)

open()

        


