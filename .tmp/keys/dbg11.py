# -*- coding: utf-8 -*-
import json,io
d=json.load(io.open('_data/name_issues.json',encoding='utf-8'))
print(list(d.keys()))
issues=d['issues']
print('n issues',len(issues),'syn pairs',len(d.get('synonym_pairs') or []),'syn_of',len(d.get('synonym_of_slug') or {}))
for q in ['崖县','斜孔','匙颏','长泰','苏州','贵州乳白蚁','河口','吕宋','天台','景洪近瓢','扬子江','双色散白蚁','青岛散白蚁','宽胸','三宝']:
    hits=[i for i in issues if q in (i.get('latin') or '')+ (i.get('accepted_latin') or '') + (i.get('kind') or '')]
    print(q, len(hits))
print('---sample issue---')
print(json.dumps(issues[0],ensure_ascii=False,indent=1)[:600])
print('---kinds---')
from collections import Counter
print(Counter(i.get('kind') for i in issues))
print('groups',Counter(i.get('group') for i in issues))
