
import json
j=json.load(open('_data/fauna_keys.json',encoding='utf-8'))
for pg in ['/family/termitidae/','/family/kalotermitidae/','/family/rhinotermitidae/','/list/']:
    print('===',pg)
    for k in j[pg]['keys']:
        print('--',k['title'],'|',k['caste'],'| couples',len(k['couplets']))
        for c in k['couplets']:
            for l in c['leads']:
                tgt=l['leaf']['zh'] if 'leaf' in l else '->%s'%l['to']
                print('  %-2d d%d %-40s %s'%(c['n'],c['d'],l['t'][:40],tgt))
