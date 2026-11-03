import json
tax=json.load(open('_data/taxonomy.json',encoding='utf-8'))
sbg=json.load(open('_data/species_by_genus.json',encoding='utf-8'))
from collections import Counter,defaultdict
gc=Counter(); sc=Counter()
for g in tax['genera']:
    gc[g['family']]+=1
    sc[g['family']]+=len(sbg.get(g['id'],[]))
for f in tax['families']:
    fid=f['id'] if isinstance(f,dict) else f
    print(fid, gc[fid], sc[fid])
print('---- clades/families type', type(tax['families'][0]))
for g in tax['genera']:
    if g['id'] in ('coptotermes','reticulitermes','glyptotermes','neotermes','stylotermes','prorhinotermes','kalotermes','schedorhinotermes','macrotermes','hypotermes','indotermes','procapritermes','ahmaditermes','nasutitermes'):
        print(g['id'],g['latin'],g['zh'],g['family'],g['subfamily'])
