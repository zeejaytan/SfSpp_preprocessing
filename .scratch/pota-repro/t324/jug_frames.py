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
for i in (1,2,9):
    A=load(os.path.join(G,'Juglet_Piece_%d.S0'%i)); B=load(os.path.join(G,'Juglet_Piece_%d.S1'%i))
    C=np.hstack([A,B])
    cen=C.mean(axis=1)
    T=np.loadtxt(os.path.join(K,'Juglet_Piece_%d_T.txt'%i))
    ka=np.loadtxt(os.path.join(K,'Juglet_Piece_%d_Axis.xyz'%i)).reshape(-1,6)[0]
    print('piece',i)
    print('  centroid      ', np.round(cen,2))
    print('  GT T 4x4 tr  ', np.round(T[0:3,3],2) if T.shape==(4,4) else np.round(T.reshape(-1)[:3],2))
    print('  key p0        ', np.round(ka[3:6],2))
    print('  bbox min/max  ', np.round(C.min(axis=1),1), np.round(C.max(axis=1),1))
