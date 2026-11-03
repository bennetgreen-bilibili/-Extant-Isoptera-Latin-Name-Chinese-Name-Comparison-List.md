import re, json, sys
sys.path.insert(0,'.tmp/keys')
import kp
from kp import _find_end

tax=json.load(open('_data/taxonomy.json',encoding='utf-8'))
sbg=json.load(open('_data/species_by_genus.json',encoding='utf-8'))
GEN={g['id']:g for g in tax['genera']}
LAT2G={g['latin'].lower():g['id'] for g in tax['genera']}
ZH2G={re.sub(r'\s','',g['zh']).replace('蚊','蚁'):g['id'] for g in tax['genera']}
FAM={}
for f in tax['families']:
    FAM[f['id']]=f
FAMLAT={f['latin'].lower():f['id'] for f in tax['families']}
FAMZH={f['zh']:f['id'] for f in tax['families']}
SUB={s['id']:s for s in tax['subfamilies']}
SP={}; SPZH={}
for gid,lst in sbg.items():
    if gid=='_meta': continue
    for sp in lst:
        e=sp.get('epithet') or re.sub(r'[^a-z]','',sp['latin'].split()[-1].lower())
        SP[(gid,e)]=sp
        SPZH.setdefault(re.sub(r'\s','',sp['zh']).replace('蚊','蚁'),[]).append((gid,sp))

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

def res_species(pay, kg):
    g=pay.get('genus_raw'); epi=pay.get('epi') or ''
    cands=[]
    if g:
        if len(g)==1: cands=[kg] if kg else []
        elif g.lower() in LAT2G: cands=[LAT2G[g.lower()]]
        else:
            cands=[v for k,v in LAT2G.items() if lev(k,g.lower())<=1]
    for gid in cands:
        if (gid,epi) in SP: return SP[(gid,epi)]
    for gid in cands:
        best=None;bd=3
        for (gg,e2),sp in SP.items():
            if gg!=gid: continue
            d=lev(epi,e2)
            if d<bd: bd=d;best=sp
        if best and bd<=1: return best
    zh=pay.get('zh')
    if zh:
        key=re.sub(r'\s','',zh).replace('蚊','蚁')
        c=SPZH.get(key)
        if c:
            c=sorted(c,key=lambda x:0 if x[0]==(kg or '') else 1)
            if len(c)==1 or (c[0][0]==kg): return c[0][1]
            return c[0][1]
    return None

def res_genus(pay, kg):
    g=pay.get('genus_raw')
    if g and len(g)>1:
        if g.lower() in LAT2G: return GEN[LAT2G[g.lower()]]
        for k,v in LAT2G.items():
            if lev(k,g.lower())<=1: return GEN[v]
        # try stripping trailing 属 char
    zh=pay.get('zh')
    if zh:
        z=re.sub(r'\s','',zh).replace('蚊','蚁')
        for suf in ('属','腐','嵩','羁','羈'):
            if z.endswith(suf) and z[:-1]+'属' in ZH2G: return GEN[ZH2G[z[:-1]+'属']]
        if z in ZH2G: return GEN[ZH2G[z]]
    return None

TAIL_LAT=re.compile(r"[\s.．,，]*[A-Z]\s*[.,．]?\s*(?:[(（〔\[]{1,2}\s*[A-Za-z0-9]{1,3}\s*[.．]?\s*[)）〕\]}]{1,2}\s*)?[a-zà-ÿ]{2,}(?:\s+[a-zà-ÿ]+)*\s*[.。]?\s*$")
def strip_taxon(t, pay):
    s=t
    zh=pay.get('zh')
    if zh:
        z=re.sub(r'\s','',zh)
        s2=s.rstrip()
        if s2.replace(' ','').endswith(z):
            # cut by characters from end
            k=len(z)
            i=len(s2); cnt=0
            while i>0 and cnt<k:
                i-=1
                if s2[i].strip(): cnt+=1
            s=s[:i]
    s=TAIL_LAT.sub('',s)
    s=re.sub(r'[\s.．,，、·…—…\-]+$','',s)
    return s.strip()

def clean_text(s):
    s=re.sub(r'[（(]\s*图\s*\d+\s*[)）]','',s)
    s=s.replace('\u3000',' ')
    s=re.sub(r'[.．·…]{2,}',' ',s)
    s=s.replace('蚊','蚁')
    s=re.sub(r'(?<=[\u4e00-\u9fa5])\s+(?=[\u4e00-\u9fa5])','',s)
    s=re.sub(r'\s+([，。、；：])',r'\1',s)
    s=re.sub(r'(\d)\s*\.\s*(\d)',r'\1.\2',s)
    s=re.sub(r'\s+',' ',s).strip()
    return s

if __name__=='__main__':
    print('modules ok')
