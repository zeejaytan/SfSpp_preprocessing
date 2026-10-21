import numpy as np
from scipy.spatial import cKDTree
def load(p):
    d = []
    f = open(p)
    data = p.endswith('.pcd') and False
    for ln in f:
        if p.endswith('.pcd'):
            if not data:
                if ln.startswith('DATA'): data = True
                continue
        s = ln.split()
        if len(s) >= 3:
            try: d.append([float(x) for x in s[:3]])
            except ValueError: pass
    return np.array(d)
D = 'C:/PR/SfSpp_preprocessing/.scratch/pota222/p12/'
a0 = load(D+'auth_Bl0.pcd'); a1 = load(D+'auth_Bl1.pcd')
for tag in ['at8','at4p5']:
    s0 = load(D+'p12_S0_%s.xyz'%tag); s1 = load(D+'p12_S1_%s.xyz'%tag)
    allp = np.vstack([s0,s1])
    t = cKDTree(allp)
    for nm, a in [('Bl0',a0),('Bl1',a1)]:
        dd,_ = t.query(a)
        print(tag, nm, 'n=%d med=%.2f cov2mm=%.1f%%'%(len(a), float(np.median(dd)), 100*float((dd<2).mean())), flush=True)
