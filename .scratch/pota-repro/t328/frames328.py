
import numpy as np
IN='artifacts/pota328/in'
def load_ply(p):
    rows=[];hdr=True
    for ln in open(p):
        if hdr:
            if ln.strip()=='end_header': hdr=False
            continue
        t=ln.split()
        if len(t)>=6: rows.append([float(x) for x in t[:6]])
    return np.array(rows)
for k in (1,2,9):
    a=load_ply(f'{IN}/geom/Juglet_Piece_{k}.S0'); b=load_ply(f'{IN}/geom/Juglet_Piece_{k}.S1')
    ax=[float(x) for x in open(f'{IN}/gt/Juglet_Piece_{k}_Axis.xyz').read().split()]
    T=np.loadtxt(f'{IN}/gt/Juglet_Piece_{k}_T.txt')
    P=np.vstack([a[:,:3],b[:,:3]])
    print(k,'centroid',np.round(P.mean(0),3),'axisline pt',np.round(ax[:3],3),'dir',np.round(ax[3:],3))
    print('   T trans',np.round(T[:3,3],3),'det',round(np.linalg.det(T[:3,:3]),4))
    print('   centroid via T',np.round((T[:3,:3]@P.mean(0)+T[:3,3]),3))
