
# -*- coding: utf-8 -*-
import re, sys, io
sys.stdout.reconfigure(encoding='utf-8')
p = sys.argv[1]
lines = open(p, encoding='utf-8').read().split('\n')
H = re.compile(r'^<(h2|h3|h4|h5)\s+id="([^"]+)"[^>]*>(.*?)</\1>\s*$')
heads = []
for i,l in enumerate(lines):
    m = H.match(l.strip())
    if m: heads.append((i, m.group(1), m.group(2), re.sub('<[^>]+>','',m.group(3))))
# family h3 content until next heading
for idx,(i,tag,hid,txt) in enumerate(heads):
    if tag=='h3':
        nxt = heads[idx+1][0] if idx+1 < len(heads) else len(lines)
        body = lines[i+1:nxt]
        print('=== ', hid, '('+str(nxt-i-1)+' lines)')
        for b in body[:8]:
            print('   ', b[:160])
        break
print('counts', {k: sum(1 for h in heads if h[1]==k) for k in ('h2','h3','h4','h5')})
