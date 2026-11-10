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
        for ln in f:
            if ln.startswith('end_header'): break
        for _ in range(nv):
            ln=f.readline()
            if not ln: break
            v=ln.split()
            if len(v)>=6: rows.append([float(v[0]),float(v[1]),float(v[2])])
    return np.array(rows).T
print('piece diag_mm  d_c_key_mm  r_max_mm  |d| %.4f')
out=[]
for i in range(1,10):
    C=np.hstack([load(os.path.join(G,'Juglet_Piece_%d.S0'%i)), load(os.path.join(G,'Juglet_Piece_%d.S1'%i))])
    cen=C.mean(axis=1); diag=float(np.linalg.norm(C.max(axis=1)-C.min(axis=1)))
    ka=np.loadtxt(os.path.join(K,'Juglet_Piece_%d_Axis.xyz'%i)).reshape(-1,6)[0]
    p0=ka[0:3]; a=ka[3:6]; an=np.linalg.norm(a)
    a=a/an
    d=float(np.linalg.norm(np.cross(cen-p0,a)))
    rmax=float(np.max(np.linalg.norm(np.cross(C.T-p0,a),axis=1)))
    out.append((i,diag,d,rmax,an))
    print('%5d %7.2f %10.2f %8.2f %8.4f' % (i,diag,d,rmax,an))
print('diag %.1f-%.1f | d_c %.1f-%.1f | any d_c<25: %s' % (min(r[1] for r in out),max(r[1] for r in out),min(r[2] for r in out),max(r[2] for r in out),sum(1 for r in out if r[2]<25.0)))
