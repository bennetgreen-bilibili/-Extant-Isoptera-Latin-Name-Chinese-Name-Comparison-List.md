
# -*- coding: utf-8 -*-
import json, sys
sys.stdout.reconfigure(encoding='utf-8')
d = json.load(open('_data/phylogeny.json', encoding='utf-8'))
print(type(d).__name__, len(d))
print(json.dumps(d, ensure_ascii=False)[:1200])
