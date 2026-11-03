import re, json
lines=open('.tmp/keys/raw.txt',encoding='utf-8').read().split('\n')
pat = re.compile(r'^\s*(\d{1,3})\s*[.．、]\s*([\u4e00-\u9fa5]{2,13})\s*([A-Z][a-zA-Z]{3,})\s+([a-z][a-zA-Z\-]{2,})')
book=[]
for l in lines:
    m=pat.match(l)
    if m: book.append({'n':int(m.group(1)),'zh':m.group(2),'genus':m.group(3),'epi':m.group(4)})
sbg=json.load(open('_data/species_by_genus.json',encoding='utf-8'))
gen={}
for g,lst in sbg.items():
    if g=='_meta': continue
    gen[g]=(lst[0]['latin'].split()[0] if lst else g, lst)
def norm(s): return re.sub(r'[^a-z]','',s.lower())
def lev(a,b):
    if a==b: return 0
    if abs(len(a)-len(b))>3: return 9
    prev=list(range(len(b)+1))
    for i,ca in enumerate(a,1):
        cur=[i]
        for j,cb in enumerate(b,1):
            cur.append(min(prev[j]+1,cur[j-1]+1,prev[j-1]+(ca!=cb)))
        prev=cur
    return prev[-1]
# genus fuzzy
gkeys=list(gen.keys())
def find_genus(gname):
    n=norm(gname)
    for k,(lat,lst) in gen.items():
        if norm(lat)==n: return k
    best=None;bd=9
    for k,(lat,lst) in gen.items():
        d=lev(n,norm(lat))
        if d<bd: bd=d;best=k
    return best if bd<=3 else None
unmatched=[]
resolved=[]
used_genus={}
for b in book:
    gk=find_genus(b['genus'])
    used_genus.setdefault(b['genus'],gk)
    if not gk: unmatched.append((b,'no-genus')); continue
    lst=gen[gk][1]; ne=norm(b['epi'])
    cands=[(lev(ne,norm(s['latin'].split()[-1])),s) for s in lst]
    cands.sort(key=lambda x:x[0])
    if cands and cands[0][0]<=2:
        resolved.append((b,gk,cands[0][1],cands[0][0]))
    else:
        unmatched.append((b,gk))
print('resolved',len(resolved),'unmatched',len(unmatched))
for b,info in unmatched: print(' UNM', b['n'], b['zh'], b['genus'], b['epi'], info if isinstance(info,str) else '')
print('--- genus map issues ---')
for g,gk in used_genus.items():
    if gk is None: print(' nogenus', g)
