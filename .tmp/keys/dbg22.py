import json
tax=json.load(open('_data/taxonomy.json',encoding='utf-8'))
subs=tax['subfamilies']
for s in subs: print(s)
print('---- termitidae page front matter')
