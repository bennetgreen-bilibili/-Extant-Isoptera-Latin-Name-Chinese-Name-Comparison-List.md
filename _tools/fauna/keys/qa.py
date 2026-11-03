
import json, re, sys
j = json.load(open('_data/fauna_keys.json', encoding='utf-8'))
out = []
bad = 0
for pg, v in sorted(j.items()):
    out.append('== %s  keys=%d couplets=%d leaves=%d omitted=%d' % (pg, v['n_keys'], v['n_couplets'], v['n_leaves'], len(v.get('omitted') or [])))
    for k in v['keys']:
        ns = [c['n'] for c in k['couplets']]
        consec = ns == list(range(1, len(ns)+1))
        targets = set()
        dangling = []
        empty = []
        nleaf = 0
        for c in k['couplets']:
            for l in c['leads']:
                if 'leaf' in l:
                    nleaf += 1
                elif 'to' in l:
                    targets.add(l['to'])
                else:
                    empty.append('%d:%r' % (c['n'], l.get('t','')[:40]))
        for t in targets:
            if t not in ns: dangling.append(t)
        dmax = max([c['d'] for c in k['couplets']] or [0])
        flag = ''
        if not consec: flag += ' NONSEQ'
        if dangling: flag += ' DANGLE=%s' % dangling
        if empty: flag += ' NODEST=%d' % len(empty)
        if len(k['couplets']) < 2: flag += ' TINY'
        if flag: bad += 1
        out.append('   - %-38s %-8s cp=%-3d lf=%-3d drop=%-2d dmax=%-2d%s' % (k['title'][:38], k.get('caste',''), len(k['couplets']), nleaf, len(k.get('dropped') or []), dmax, flag))
        for e in empty[:3]: out.append('       NODEST %s' % e)
out.append('flagged keys: %d' % bad)
open('.tmp/keys/qa.txt','w',encoding='utf-8').write('\n'.join(out))
print('ok', bad)
