import re, json, sys
sys.path.insert(0,'.tmp/keys')
import kparse
from kparse import lines as LINES, blocks, clean_line

def norm(s):
    s = s.replace('蚊','蚁')
    s = re.sub(r'[\s　]+','',s)
    return s

tax=json.load(open('_data/taxonomy.json',encoding='utf-8'))
sbg=json.load(open('_data/species_by_genus.json',encoding='utf-8'))
genus_rec={g['id']:g for g in tax['genera']}

SP={}   # norm zh -> list of dict(genus,slug,latin,zh)
GEN={}  # norm zh genus name -> genus id
for gid,g in genus_rec.items():
    GEN.setdefault(norm(g['zh']),[]).append(gid)
for gid,lst in sbg.items():
    if gid=='_meta': continue
    for sp in lst:
        SP.setdefault(norm(sp['zh']),[]).append(dict(genus=gid,slug=sp['slug'],latin=sp['latin'],zh=sp['zh'],url=sp['url']))

# term lengths for greedy longest match at a position
SP_KEYS=sorted(SP.keys(), key=len, reverse=True)
GEN_KEYS=sorted(GEN.keys(), key=len, reverse=True)

def find_terms(s, keygenus=None):
    """return list of (start,end,kind,zh,payload) hits, longest-match, non-overlapping (scan left->right)."""
    hits=[]
    i=0; n=len(s)
    while i<n:
        hit=None
        for k in SP_KEYS:
            if s.startswith(k,i):
                cands=SP[k]
                pick=None
                for c in cands:
                    if keygenus and c['genus']==keygenus: pick=c;break
                pick=pick or cands[0]
                hit=(i,i+len(k),'species',k,pick); break
        if hit is None:
            for k in GEN_KEYS:
                if s.startswith(k,i):
                    hit=(i,i+len(k),'genus',k,GEN[k][0]); break
        if hit: hits.append(hit); i=hit[1]
        else: i+=1
    return hits

if __name__=='__main__':
    bad=0
    for (h,e) in blocks():
        title=LINES[h].strip()
        ks=kparse.parse_key(h,e)
        for sec in ks:
            cs=sec['couplets']
            ln=[len(c['leads']) for c in cs]
            nl=[x for x in ln if x!=2]
            if nl: print('NON2', title[:20], sec['caste'], nl)
