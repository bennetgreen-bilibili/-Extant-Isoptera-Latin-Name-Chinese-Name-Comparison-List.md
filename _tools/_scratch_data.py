
# -*- coding: utf-8 -*-
import json, sys
sys.stdout.reconfigure(encoding='utf-8')
for name in ('species_by_genus','fauna_genera','taxonomy_images','subfamily_maps'):
    d = json.load(open('_data/%s.json' % name, encoding='utf-8'))
    print('==', name, type(d).__name__, len(d))
    if isinstance(d, dict):
        k = list(d)[0]
        print('  key0:', k)
        v = d[k]
        print('  val0:', json.dumps(v, ensure_ascii=False)[:600])
    else:
        print('  first:', json.dumps(d[0], ensure_ascii=False)[:600])
