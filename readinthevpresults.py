import json
# Read in the networks info
with open('results/vptables/backup1/7094.json') as f:
    vpresults = json.load(f)

count = 0
for ip in vpresults:
    count +=1 
    print(ip,count)