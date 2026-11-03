import json
sbg=json.load(open('_data/species_by_genus.json',encoding='utf-8'))
zhs=['奇象','近瓢','歧颚','华白蚁','壤白蚁','马扭','蔡白蚁','钩扭','华象','钝颚']
for k,v in sbg.items():
    if k=='_meta': continue
    for sp in v:
        for z in zhs:
            if z in sp['zh']:
                print(z,'|',k,'|',sp['latin'],'|',sp['zh'],'|',sp['url'])
