import json, re, unicodedata
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
TREATISE=ROOT/'_unpublished/文库/treatise-on-the-isoptera/_full.txt'
tax=json.load(open(ROOT/'_data/taxonomy.json',encoding='utf-8'))
genera=tax['genera']
s=TREATISE.read_text(encoding='utf-8',errors='replace')

def clean(x):
    return re.sub(r'\s+',' ',x).strip()

def entry_end(pos):
    tail=s[pos:pos+20000]
    m=re.search(r'(?m)^\s*(?:▲\s*\d+\s+species|\uf0fd\s*Distribution:|Distribution:)',tail)
    if m: return pos+m.start()
    # next genus-like centered heading
    m=re.search(r'(?m)^\s{10,}([A-Z][A-Za-z]+)\s+[A-Z][^\n]{2,60}?,\s*\d{4}',tail[50:])
    if m: return pos+50+m.start()
    return min(len(s),pos+20000)

def find_entry(latin):
    pat=re.compile(r'(?m)^[ \t]{0,50}'+re.escape(latin)+r'[ \t]+([A-Z][^\n]{0,70}?),?[ \t]*(\d{4}[a-z]?)(?:[ \t]*:.*)?[ \t]*$')
    best=None
    for m in pat.finditer(s):
        pos=m.start(); end=entry_end(pos)
        win=s[pos:end]
        if 'Type species:' not in win: continue
        # reject if another genus heading intervenes before the type-species line
        head=s[pos:m.end()].strip()
        score=0
        lead=len(s[pos:m.start()])-len(s[pos:m.start()].lstrip(' 	')) if False else len(m.group(0))-len(m.group(0).lstrip(' 	'))
        if lead>=8: score+=10
        if re.search(r'(?m)^\s*Type species:',win): score+=2
        if re.search(r'(?m)^\s*Type species:',win[:1200]): score+=3
        if ':' in head: score-=2
        score-=min(5,len(head)//80)
        if best is None or score>best[0]: best=(score,pos,end,head)
    return best

def parse_entry(pos,end,head):
    win=s[pos:end]
    tm=re.search(r'(?m)^\s*Type species:\s*(.+?)(?=\n\s*\n|\n\s*—|\n\s*\uf0fe)',win,re.S)
    type_species=clean(tm.group(1)) if tm else ''
    # citation: heading line if it has pages, else following line starting with genus
    cit=head
    if not re.search(r':\s*[0-9]',cit):
        after=s[pos+len(head):pos+1200]
        for line in after.splitlines():
            line=clean(line)
            if not line: continue
            if line.startswith(head.split()[0]):
                cit=line; break
            break
    # join citation continuation if it ends mid-sentence
    if cit and not cit.endswith('.'):
        idx=s.find(cit,pos)
        more=s[idx+len(cit):idx+len(cit)+400]
        nxt=''
        for line in more.splitlines()[1:]:
            line=clean(line)
            if not line: break
            nxt+=' '+line
            if line.endswith('.'): break
        cit=clean(cit+nxt)
    refs=[]
    for line in win.splitlines():
        line=line.strip()
        mm=re.match(r'^[—–-]\s*(.+?)\s*[•·]\s*(.*)$', line)
        if mm:
            refs.append((clean(mm.group(1)), clean(mm.group(2))))
    keep=[]
    for who,note in refs:
        low=note.lower()
        if ('character' in low or 'diagnos' in low or 'key' in low or
            ('described' in low and ('soldier' in low or 'imago' in low or 'worker' in low or 'alate' in low))):
            keep.append({'ref':who,'note':note})
    return type_species, keep[:12], len(refs)

out={}; missing=[]
for g in genera:
    latin=g['latin']
    b=find_entry(latin)
    if not b:
        missing.append(latin); continue
    score,pos,end,head=b
    ts,refs,nrefs=parse_entry(pos,end,head)
    out[g['id']]={'latin':latin,'zh':g['zh'],'family':g['family'],'citation':head,'type_species':ts,'references':refs,'nrefs':nrefs,'score':score}

json.dump(out,open(ROOT/'_tmp/genus_sources_probe.json','w',encoding='utf-8'),ensure_ascii=False,indent=1)
print('found',len(out),'missing',len(missing))
print('missing:',','.join(missing))
for k in ['hypotermes','anacanthotermes','isognathotermes','mastotermes']:
    if k in out: print(k, json.dumps(out[k],ensure_ascii=False)[:700])
