
import numpy as np
from scipy.spatial import cKDTree
B='C:/PR/worktrees/sfs/328-juglet-wall-side-cure/artifacts/pota328/jobA'
def load_ply6(p):
    rows=[];hdr=True;n=0
    for ln in open(p):
        if hdr:
            t=ln.split()
            if t and t[0]=='element' and t[1]=='vertex': n=int(t[2])
            if t and t[0]=='end_header': hdr=False
            continue
        if len(rows)<n: rows.append([float(x) for x in ln.split()[:6]])
    return np.array(rows)
def load_pcd(p):
    L=open(p).read().splitlines()
    i=[n for n,l in enumerate(L) if l.startswith('DATA')][0]
    rows=[l.split() for l in L[i+1:] if l.strip() and len(l.split())>=6]
    return np.array([[float(x) for x in r[:6]] for r in rows])
for pot,pcs in (('pota',['Pot_A_Piece_01','Pot_A_Piece_02','Pot_A_Piece_03']),('potc',['Pot_C_Piece_01'])):
  for pc in pcs:
    print('==',pc)
    for face in ('S0','S1','Bl0','Bl1'):
        try:
            if face[0]=='S':
                a=load_ply6(f'{B}/outnew_{pot}/geom/{pc}.{face}'); b=load_ply6(f'{B}/outold_{pot}/geom/{pc}.{face}')
            else:
                a=load_pcd(f'{B}/outnew_{pot}/geom/{pc}.{face}'); b=load_pcd(f'{B}/outold_{pot}/geom/{pc}.{face}')
        except Exception as ex:
            print('  ',face,'ERR',ex); continue
        if len(a)!=len(b):
            print('  %-4s n new=%d old=%d'%(face,len(a),len(b))); continue
        d=np.linalg.norm(a[:,:3]-b[:,:3],axis=1)
        dots=np.sum(a[:,3:6]*b[:,3:6],axis=1)
        print('  %-4s n=%5d  pos median=%.6f max=%.6f  normal dot median=%.4f  frac|d|>1e-6=%.3f'%(
            face,len(a),np.median(d),d.max(),np.median(dots),float((d>1e-6).mean())))
