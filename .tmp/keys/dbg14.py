import json,re
ni=json.load(open('_data/name_issues.json',encoding='utf-8'))
print(list(ni.keys()))
print(json.dumps(ni.get('meta'),ensure_ascii=False)[:800])
print('issues',len(ni.get('issues',[])),'syn_pairs',len(ni.get('synonym_pairs',[])))
lats=['sinotermes','parahypotermes','peribulbitermes','mironasutitermes','havilanditermes','tsaitermes','malaysiocapritermes']
blob=json.dumps(ni,ensure_ascii=False).lower()
for l in lats:
    idx=[m.start() for m in re.finditer(l,blob)]
    print(l,len(idx))
    for i in idx[:3]:
        print('   ...',blob[max(0,i-120):i+120].replace('\n',' '))
