import json
ff=json.load(open('_data/fauna_families.json',encoding='utf-8'))
for k,v in ff.items():
    print('==',k)
    for kk,vv in v.items():
        s=str(vv)
        print('   ',kk,':',s[:200])
