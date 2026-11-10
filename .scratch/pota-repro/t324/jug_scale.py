import numpy as np, os
G='/data/gpfs/projects/punim2657/SfSpp/runs/20261103-1332_fab76f5_t66-admitsign-default/outU_jug/geom'
K='/data/gpfs/projects/punim2657/Dataset/Juglet_GT'
def load(p):
    rows=[]
    with open(p) as f:
        nv=0
        for ln in f:
            if ln.startswith('element vertex'):
                nv=int(ln.split()[-1]); break
        hdr_left=True
        for ln in f:
            if ln.startswith('end_header'):
                break
        for _ in range(nv):
            ln=f.readline()
            if not ln: break
            v=ln.split()
            if len(v)>=6: rows.append([float(v[0]),float(v[1]),float(v[2])])
    a=np.array(rows); return a.T
print('piece  npts   diag_mm  d_c_key_mm  r_max_mm')
res=[]
for i in range(1,10):
    A=load(os.path.join(G,'Juglet_Piece_%d.S0'%i)); B=load(os.path.join(G,'Juglet_Piece_%d.S1'%i))
    C=np.hstack([A,B]); n=C.shape[1]
    diag=float(np.linalg.norm(C.max(axis=1)-C.min(axis=1)))
    cen=C.mean(axis=1)
    ka=np.loadtxt(os.path.join(K,'Juglet_Piece_%d_Axis.xyz'%i)).reshape(-1,6)[0]
    a=ka[:3]/np.linalg.norm(ka[:3]); p0=ka[3:6]
    d=float(np.linalg.norm(np.cross(cen-p0,a)))
    rmax=float(np.max(np.linalg.norm(np.cross(C.T-p0,a),axis=1)))
    res.append((i,n,diag,d,rmax))
    print('%5d %6d %8.2f %10.2f %8.2f' % (i,n,diag,d,rmax))
print('diag %.1f-%.1f mm | d_c(key) %.2f-%.2f mm | all d_c < 25mm? %s' % (min(r[2] for r in res), max(r[2] for r in res), min(r[3] for r in res), max(r[3] for r in res), all(r[3]<25.0 for r in res)))
