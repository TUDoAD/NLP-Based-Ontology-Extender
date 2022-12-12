import json
with open('FoundClasses.json', 'r') as f:
    data = json.load(f)

for key in data:
    print("{}: {} classes found".format(key,len(data[key])))

unique_dict = {}
for keys in data.keys():
    for i in data[keys]:
        temp = dict.fromkeys(i,"")
        unique_dict.update(temp)    

print("unique keys: ", len(unique_dict.keys()))