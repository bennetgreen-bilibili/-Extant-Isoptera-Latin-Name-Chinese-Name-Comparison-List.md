import json, sys
sys.path.insert(0,'.tmp/keys')
import res
print(json.dumps(res.SP[('glyptotermes','daweishanensis')],ensure_ascii=False))
print(json.dumps(res.SUB['nasutitermitinae'],ensure_ascii=False)[:300])
print(json.dumps({k:v for k,v in res.FAM['termitidae'].items()},ensure_ascii=False)[:400])
