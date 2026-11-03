# -*- coding: utf-8 -*-
import sys
sys.path.insert(0,'.tmp/keys')
import emit, res
pays=[{'genus_raw':'Cryptotermes','epi':'','zh':'属'},
      {'genus_raw':'Glyprotermes','epi':'','zh':'属'},
      {'genus_raw':'Prorhinotermes','epi':'','zh':'原鼻白蚁漏'},
      {'genus_raw':'Tsaitermes','epi':'','zh':'蔡白蚁属'},
      {'genus_raw':'Parahypotermes','epi':'','zh':'壤白蚁腐'},
      {'genus_raw':'Malaysiotermes','epi':'','zh':'马扭白蚁属'},
      {'genus_raw':'Pseudocapriternes','epi':'','zh':'钩歪白蚊属'},
      {'genus_raw':'Pseudocapritermes','epi':'','zh':'钩扭白蚊属'},
      {'genus_raw':'Peribulbitermes','epi':'','zh':'近瓢白蚁属'},
      {'genus_raw':'Havilanditermes','epi':'','zh':'歧颚白蚊属'},
      {'genus_raw':'Mironasutitermes','epi':'','zh':'奇象白蚁属'},
      {'genus_raw':'Dicuspiditermes','epi':'','zh':'突歪白蚁属'},
      {'genus_raw':'Ahmaditermes','epi':'','zh':'钝频白蚁属'}]
for p in pays:
    g=emit.res_genus(p,None)
    print(p['genus_raw'], p['zh'], '->', (g['id'] if g else None))
print('LAT2G sample', list(res.LAT2G.items())[:3], len(res.LAT2G))
print('keys with cryptotermes?', [k for k in res.LAT2G if 'crypto' in k])
print('dicuspiditermes in site?', [k for k in res.LAT2G if 'dicusp' in k], [k for k in res.LAT2G if 'malaysi' in k])
