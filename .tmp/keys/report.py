import re, json, sys
sys.path.insert(0,'.tmp/keys')
from kparse import *

sbg=json.load(open('_data/species_by_genus.json',encoding='utf-8'))
byname={}   # (genus_slug, epi_norm) -> species dict
by_zh={}
allsp=[]
for g,lst in sbg.items():
    if g=='_meta': continue
    for sp in lst:
        lat=sp['latin'].split()
        epi=re.sub(r'[^a-z]','',lat[-1].lower()) if len(lat)>1 else ''
        byname[(g,epi)]=sp
        by_zh.setdefault(re.sub(r'\s','',sp['zh']),[]).append((g,sp))
        allsp.append((g,epi,sp))

def resolve(term):
    g=re.sub(r'[^a-z]','',term['genus'].lower())
    epi=re.sub(r'[^a-z]','',term['epi_raw'].lower())
    if not epi:
        return ('genus', g, None)
    if (g,epi) in byname: return ('species', g, byname[(g,epi)])
    # fuzzy epithet within genus
    best=None;bd=3
    for (gg,e2),sp in byname.items():
        if gg!=g: continue
        d=lev(epi,e2)
        if d<bd: bd=d;best=sp
    if best and bd<=2: return ('species', g, best)
    # zh name
    zh=re.sub(r'\s','',term['zh'])
    if zh and zh in by_zh:
        cands=by_zh[zh]
        for gg,sp in cands:
            if gg==g: return ('species',g,sp)
        return ('species', cands[0][0], cands[0][1])
    return ('missing', g, {'epi':epi,'zh':term['zh']})

def report():
    for (h,e) in blocks():
        ks=parse_key(h,e)
        title=lines[h].strip()
        for sec in ks:
            cs=sec['couplets']
            maxn=max([c['n'] for c in cs],default=0)
            nums={c['n'] for c in cs}
            bad=[]
            for c in cs:
                if len(c['leads'])!=2: bad.append('len%d'%c['n'])
                for l in c['leads']:
                    typ,val=classify(l,maxn)
                    if typ=='open': bad.append('open%d'%c['n'])
                    if typ=='target' and val['next'] not in nums: bad.append('dangling%d->%d'%(c['n'],val['next']))
                    if typ=='taxon':
                        r=resolve(val)
                        if r[0]=='missing': bad.append('miss%d:%s/%s'%(c['n'],val['latin'],val['zh']))
            print('%-34s %-4d %-4d cp=%2d %s' % (title[:34], h, e, len(cs), ' '.join(bad[:10])))
report()
