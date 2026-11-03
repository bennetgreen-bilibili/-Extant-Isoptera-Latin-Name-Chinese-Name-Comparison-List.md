
# -*- coding: utf-8 -*-
import re, sys, json
p = sys.argv[1]
lines = open(p, encoding='utf-8').read().split('\n')
H = re.compile(r'^<(h2|h3|h4|h5)\s+id="([^"]+)"[^>]*>(.*?)</\1>\s*$')
heads = []
for i, l in enumerate(lines):
    m = H.match(l.strip())
    if m:
        heads.append((i+1, m.group(1), m.group(2), re.sub('<[^>]+>','',m.group(3))[:60]))
print("total lines", len(lines), "headings", len(heads))
for h in heads:
    print(h[0], h[1], h[2], "|", h[3])
