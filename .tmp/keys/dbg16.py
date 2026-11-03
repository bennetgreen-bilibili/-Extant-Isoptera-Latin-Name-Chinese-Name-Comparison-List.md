import json,re
sbg=json.load(open('_data/species_by_genus.json',encoding='utf-8'))
def find(epi):
    out=[]
    for gid,lst in sbg.items():
        if gid=='_meta': continue
        for sp in lst:
            e=re.sub(r'[^a-z]','',sp['latin'].split()[-1].lower())
            if e==epi: out.append((gid,sp['zh'],sp['latin']))
    return out
probes={
 '蔡白蚁属':['huanensis','yingdeensis','ampliceps','oreophilus','mangshanensis','oocephalus'],
 '奇象白蚁属':['xingshanensis','heterodon','huangshanensis','machengensis','bashanensis','longwanshanensis','qimenensis','changningensis','shangchengensis'],
 '歧颚白蚁属':['communis','orthonasus'],
 '近瓢白蚁属':['parafulvus','dinghuensis'],
 '壤白蚁属':['suomatrensis','yingjiangensis','ruiliensis'],
 '华白蚁属':['hainanensis','luxiensis','yunnanensis'],
 '马扭白蚁属':['huananensis','huannanensis'],
}
for k,eps in probes.items():
    print('==',k)
    for e in eps:
        print('  ',e,'->',find(e)[:6])
