# -*- coding: utf-8 -*-
import sys, json
sys.path.insert(0,'.tmp/keys')
import res
q=['yaxianensis','obliqu','cochear','hekouensis','changtaiensis','suzhouensis','guizhou','qingdaoensis','liarchensis','dichrous','wuyishan','mengpeng','manzhuang','semarangi','jangtsekiang','latinotus','annandalei','mediocris','tianmuensis','sichuanensis','communis','orthonasus','luzonensis','tiantaiensis','jinghongensis']
for w in q:
    hits=[(s['slug'],s['zh'],s['latin']) for (g,e),s in res.SP.items() if w in e or w in s['latin'].lower()]
    print(w,'->',hits[:6])
