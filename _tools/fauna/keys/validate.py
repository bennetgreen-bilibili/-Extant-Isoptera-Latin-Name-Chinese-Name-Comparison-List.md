
import json, pathlib
root = pathlib.Path('.')
j = json.load(open('_data/fauna_keys.json', encoding='utf-8'))

def exists(url, kind):
    u = url.strip().strip('/')
    if kind == 'species':
        return (root/'_species'/(u.split('/')[-1]+'.md')).exists() or (root/(u+'.md')).exists()
    return (root/(u+'.md')).exists() or (root/u/'index.md').exists()

bad = []
for pg, v in j.items():
    for k in v['keys']:
        for c in k['couplets']:
            for l in c['leads']:
                lf = l.get('leaf')
                if not lf:
                    continue
                for row in [lf] + (lf.get('also') or []):
                    if row.get('kind') == 'fossil' or not row.get('url'):
                        continue
                    if not exists(row['url'], row['kind']):
                        bad.append((pg, row['kind'], row['url'], row.get('latin', '')))
print('strict missing', len(bad))
for b in bad[:40]: print(b)
