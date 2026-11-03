
# -*- coding: utf-8 -*-
import json, sys
sys.stdout.reconfigure(encoding='utf-8')
d = json.load(open('_data/species_by_genus.json', encoding='utf-8'))
ks = [k for k in d if k != '_meta']
print('genera keys', len(ks), ks[:3], ks[-3:])
print(json.dumps(d[ks[0]], ensure_ascii=False)[:900])
