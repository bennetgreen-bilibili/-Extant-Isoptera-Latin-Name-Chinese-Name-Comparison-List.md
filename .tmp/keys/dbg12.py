# -*- coding: utf-8 -*-
import json,io
d=json.load(io.open('_data/fauna_keys.json',encoding='utf-8'))
print('pages:',list(d.keys()))
for pg in ['/family/termitidae/','/family/kalotermitidae/']:
    v=d[pg]; print('##',pg,v['n_keys'],v['n_couplets'],v['n_leaves'])
    for k in v['keys'][:1]:
        print('KEY',k['title'],k['caste'],'site',k['site_genus'],'book',k['book_genus'],'dropped',k['dropped'])
        for c in k['couplets'][:8]:
            for l in c['leads']:
                print('  %2d d%d %s | %s'%(c['n'],c['d'],l['t'][:52],(l.get('leaf') or {}).get('latin') or ('->%s'%l.get('to'))))
v=d['/family/heterotermitidae/']
print('## hetero',v['n_keys'],v['n_couplets'],v['n_leaves'])
for k in v['keys']:
    print('KEY',k['title'],k['caste'],'c=',len(k['couplets']),'drop=',k['dropped'])
