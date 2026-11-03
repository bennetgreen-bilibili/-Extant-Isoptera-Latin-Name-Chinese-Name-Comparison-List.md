
# -*- coding: utf-8 -*-
import re, sys
sys.stdout.reconfigure(encoding='utf-8')
p = sys.argv[1]
lines = open(p, encoding='utf-8').read().split('\n')
H = re.compile(r'^<(h2|h3|h4|h5)\s+id="([^"]+)"[^>]*>(.*?)</\1>\s*$')
heads = []
for i,l in enumerate(lines):
    m = H.match(l.strip())
    if m: heads.append((i, m.group(1), m.group(2)))
print('HEAD')
print('\n'.join(lines[:40]))
for idx,(i,tag,hid) in enumerate(heads):
    if tag=='h3' and hid=='termitidae':
        nxt = heads[idx+1][0]
        print('=== termitidae body lines', i+1, nxt)
        print('\n'.join(lines[i+1:nxt])[:2500])
        break
