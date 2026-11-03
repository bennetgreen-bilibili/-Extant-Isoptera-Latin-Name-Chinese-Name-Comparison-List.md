import sys, io
sys.path.insert(0,'.tmp/keys')
import kp
lines=kp.lines
out=io.StringIO()
def tag(l):
    f=kp._find_end(l,200)
    if not f: return 'OPEN'
    if f[0]=='target': return '>%s'%f[1]['next']
    return 'L:%s|%s'%(f[1].get('zh'),f[1].get('epi'))
for (h,e) in kp.blocks():
    t=lines[h].strip()
    out.write('\n===== %s  [%d-%d]\n'%(t,h,e))
    for sec in kp.parse_block(h,e):
        if sec['caste']: out.write('  ## caste %s\n'%sec['caste'])
        for c in sec['couplets']:
            tags=[tag(l) for l in c['leads']]
            t0=c['leads'][0][:42].replace('\n',' ')
            out.write('  c%-3s %-28s %s\n'%(c['n'], ' / '.join(tags), t0))
open('.tmp/keys/overview.txt','w',encoding='utf-8').write(out.getvalue())
print(len(out.getvalue()))
