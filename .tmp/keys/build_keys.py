import re, json, sys
sys.path.insert(0,'.tmp/keys')
import kparse
from kparse import *

tax=json.load(open('_data/taxonomy.json',encoding='utf-8'))
sbg=json.load(open('_data/species_by_genus.json',encoding='utf-8'))

genus_rec={g['id']:g for g in tax['genera']}
zh2genus={}
for g in tax['genera']:
    zh2genus[g['zh']]=g['id']
lat2genus={}
for g in tax['genera']:
    lat2genus[g['latin'].lower()]=g['id']

sp_index={}   # (genus_id, epi) -> species
sp_zh={}
for g,lst in sbg.items():
    if g=='_meta': continue
    for sp in lst:
        parts=sp['latin'].split()
        epi=re.sub(r'[^a-z]','',parts[-1].lower()) if len(parts)>1 else ''
        sp_index[(g,epi)]=sp
        sp_zh.setdefault(re.sub(r'\s','',sp['zh']),[]).append((g,sp))

def fix_keygenus(title):
    for zh,gid in zh2genus.items():
        if zh in title: return gid
    return None

def resolve_taxon(term, keygenus):
    g = term['genus']
    # genus-level terminal (分属 keys)
    if not term['epi_raw']:
        gid = lat2genus.get(g.lower()) or lat2genus.get(term['genus_raw'].lower())
        if gid: return ('genus', gid, genus_rec[gid])
        return ('unresolved', None, {'latin':term['latin'],'zh':term['zh']})
    gid = None
    if len(g)==1:
        gid = keygenus
    else:
        gid = lat2genus.get(g.lower())
        if not gid:
            gm=genus_match(g)
            if gm: gid=lat2genus.get(gm.lower())
    epi = re.sub(r'[^a-z]','',term['epi_raw'].lower())
    if gid and (gid,epi) in sp_index:
        return ('species', gid, sp_index[(gid,epi)])
    # fuzzy epi in gid
    if gid:
        best=None;bd=3
        for (gg,e2),sp in sp_index.items():
            if gg!=gid: continue
            d=lev(epi,e2)
            if d<bd: bd=d;best=sp
        if best and bd<=2: return ('species', gid, best)
    zh=re.sub(r'\s','',term['zh'])
    if zh and zh in sp_zh:
        cands=sp_zh[zh]
        return ('species', cands[0][0], cands[0][1])
    return ('unresolved', gid, {'latin':term['latin'],'zh':term['zh'],'epi':epi})

if __name__=='__main__':
    for (h,e) in blocks():
        title=lines[h].strip()
        kg=fix_keygenus(title)
        ks=parse_key(h,e)
        nterm=0; unres=[]
        for sec in ks:
            cs=sec['couplets']
            maxn=max([c['n'] for c in cs],default=0)
            for c in cs:
                for l in c['leads']:
                    typ,val=classify(l,maxn)
                    if typ=='taxon':
                        nterm+=1
                        kind,gid,obj=resolve_taxon(val,kg)
                        if kind!='species': unres.append((kind,val['latin'],val['zh']))
        print('%-32s %s terms=%d unres=%s' % (title[:32], kg, nterm, unres[:8]))
