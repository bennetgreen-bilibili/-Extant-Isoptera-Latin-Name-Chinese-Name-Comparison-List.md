
import json,re
j=json.load(open('_data/fauna_keys.json',encoding='utf-8'))
bad=[]
for pg,v in j.items():
    for k in v['keys']:
        for c in k['couplets']:
            for l in c['leads']:
                t=l['t']; lf=l.get('leaf')
                if lf and lf.get('kind') in ('genus','family'):
                    if re.search(r'[屬属腐嵩羁科]$',t) or re.search(r'[A-Za-z]',t) or re.search(r'[①-⑩]',t):
                        bad.append((pg,k['title'],c['n'],lf['zh'],t))
print(len(bad))
for b in bad: print(b[1],b[2],b[3],'|',b[4][-30:])
print('---- open/unres text flags')
for pg,v in j.items():
    for k in v['keys']:
        for c in k['couplets']:
            for l in c['leads']:
                if re.search(r'[A-Za-z]',l['t']) or re.search(r'[①②③④⑤⑥⑦⑧⑨⑩]',l['t']):
                    print(pg,k['title'],c['n'],repr(l['t'])[:120])
