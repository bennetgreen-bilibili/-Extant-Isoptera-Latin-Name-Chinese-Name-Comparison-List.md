import json,re
fs=json.load(open('_data/fauna_species.json',encoding='utf-8'))
words=['奇象','近瓢','歧颚','壤白蚁','华白蚁','马扭','钩扭','Havilanditermes','Mironasutitermes','Peribulbitermes','Parahypotermes','Sinotermes','Malaysiocapritermes']
seen=set()
for url,v in fs.items():
    for k,vv in v.items():
        if not isinstance(vv,str): continue
        for w in words:
            if w in vv:
                key=(w,k)
                if key in seen: continue
                seen.add(key)
                i=vv.find(w)
                print('[%s|%s] %s' % (w,url, vv[max(0,i-90):i+90].replace('\n',' ')))
