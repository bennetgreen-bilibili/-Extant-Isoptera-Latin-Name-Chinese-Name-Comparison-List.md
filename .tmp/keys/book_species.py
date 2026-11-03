import re, json, unicodedata
lines=open('.tmp/keys/raw.txt',encoding='utf-8').read().split('\n')
# species treatments: number + chinese name + Latin
pat = re.compile(r'^\s*(\d{1,3})\s*[.．、]\s*([\u4e00-\u9fa5]{2,13})\s*([A-Z][a-zA-Z]{3,})\s+([a-z][a-zA-Z\-]{2,})')
book=[]
for l in lines:
    m=pat.match(l)
    if m:
        book.append((int(m.group(1)), m.group(2), m.group(3), m.group(4), l.strip()[:80]))
print('treatment lines:', len(book))
nums=[b[0] for b in book]
print('max num', max(nums), 'unique', len(set(nums)))
# genus from site
sbg=json.load(open('_data/species_by_genus.json',encoding='utf-8'))
site=[]
genus_latin={}
for g, lst in sbg.items():
    if g=='_meta': continue
    for sp in lst:
        site.append((g, sp['latin'], sp['zh'], sp['url']))
print('site species', len(site))
def norm(s):
    return re.sub(r'[^a-z]','',s.lower())
site_by_epi={}
for g,lat,zh,url in site:
    parts=lat.split()
    epi=norm(parts[-1]) if len(parts)>1 else norm(lat)
    site_by_epi.setdefault((g,epi),[]).append((lat,zh,url))
missing=[]
for n,zh,g,epi,raw in book:
    key=(g.lower(), norm(epi))
    if key not in site_by_epi:
        missing.append((n,zh,g,epi))
print('book species not found in site:', len(missing))
for m in missing[:40]: print('  ',m)
