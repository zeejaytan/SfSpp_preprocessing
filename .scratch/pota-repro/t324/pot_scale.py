import numpy as np, os, glob, re
LANES={'B':'/data/gpfs/projects/punim2657/SfSpp/runs/20261105-0445_9c5eec2_t305-lane-b2/out/geom',
       'E':'/data/gpfs/projects/punim2657/SfSpp/runs/20261105-0445_9c5eec2_t305-lane-e2/out/geom'}
AX='/data/gpfs/projects/punim2657/sfs_main/original_samples/SfS_pp/Axes'
def load(p):
    rows=[]
    with open(p) as f:
        nv=0
        for ln in f:
            if ln.startswith('element vertex'):
                nv=int(ln.split()[-1]); break
        for ln in f:
            if ln.startswith('end_header'): break
        for _ in range(nv):
            ln=f.readline()
            if not ln: break
            v=ln.split()
            if len(v)>=6: rows.append([float(v[0]),float(v[1]),float(v[2])])
    return np.array(rows).T
print('pot piece  diag_mm  d_c_released_mm  ratio')
for pot,dirn in LANES.items():
    stems=sorted(set(re.sub(r'\.(S0|S1)$','',os.path.basename(p)) for p in glob.glob(dirn+'/*.S0')))
    for st in stems[:8]:
        A=load(os.path.join(dirn,st+'.S0')); B=load(os.path.join(dirn,st+'.S1'))
        C=np.hstack([A,B]); cen=C.mean(axis=1)
        diag=float(np.linalg.norm(C.max(axis=1)-C.min(axis=1)))
        ap=os.path.join(AX,st+'_Axis.xyz')
        if not os.path.exists(ap): continue
        ka=np.loadtxt(ap).reshape(-1,6)[0]; p0=ka[0:3]; a=ka[3:6]/np.linalg.norm(ka[3:6])
        d=float(np.linalg.norm(np.cross(cen-p0,a)))
        print('%-3s %-14s %7.1f %12.1f %10.2f' % (pot,st,diag,d,d/diag))
