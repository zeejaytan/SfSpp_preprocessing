import numpy as np, sys, os, glob, argparse
from scipy.spatial import cKDTree

# ticket 51 pair quality -- the paircheck45.py protocol (t50-theta45 run), parameterised over
# this run's cell directories: every <PIECE>_arm{C,U}/surfaces/<PIECE>_Surface_{0,1}.ply pair.
# med_nn     median nearest-neighbour distance B->A (surface 1 points to surface 0 tree)
# med_across median |dist - d_par| : the perpendicular residual of B off A's local tangent
# med_angle  median angle between normals at the nearest-neighbour pairs
def read_ply(p):
    with open(p,'rb') as f:
        hdr=[]
        while True:
            l=f.readline(); hdr.append(l)
            if l.startswith(b'end_header'): break
    txt=b''.join(hdr).decode('ascii','replace').split('element camera')[0]
    n=int([l for l in txt.split('\n') if l.startswith('element vertex')][0].split()[-1])
    props=[l.split()[2] for l in txt.split('\n') if l.startswith('property')]
    rows=[]
    with open(p,'rb') as f:
        f.seek(0)
        for _ in range(len(hdr)): f.readline()
        for i in range(n): rows.append(f.readline().split())
    d=np.array(rows,dtype=np.float64)
    return {k:d[:,i] for i,k in enumerate(props)}

ap=argparse.ArgumentParser()
ap.add_argument('--cells',required=True)
ap.add_argument('--out',required=True)
a=ap.parse_args()
lines=['piece\tarm\tn0\tn1\tmed_nn\tmed_across\tmed_angle']
ncell=0; npair=0
for cd in sorted(glob.glob(a.cells+'/*_arm?')):
    cell=os.path.basename(cd)
    if cell.endswith('_armC'): arm='C'
    elif cell.endswith('_armU'): arm='U'
    else: continue
    piece=cell[:-5]
    ncell+=1
    f0=glob.glob(cd+'/surfaces/*_Surface_0.ply'); f1=glob.glob(cd+'/surfaces/*_Surface_1.ply')
    if not f0 or not f1:
        lines.append('%s\t%s\tNO-SURFACE-FILE'%(piece,arm)); continue
    A_=read_ply(f0[0]); B_=read_ply(f1[0])
    A=np.stack([A_['x'],A_['y'],A_['z']],1); B=np.stack([B_['x'],B_['y'],B_['z']],1)
    na=np.stack([A_['nx'],A_['ny'],A_['nz']],1) if 'nx' in A_ else None
    nb=np.stack([B_['nx'],B_['ny'],B_['nz']],1) if 'nx' in B_ else None
    t=cKDTree(A); dist,idx=t.query(B,k=1)
    nn=float(np.median(dist))
    if na is not None and nb is not None:
        na/=np.maximum(np.linalg.norm(na,axis=1,keepdims=True),1e-12)
        nb/=np.maximum(np.linalg.norm(nb,axis=1,keepdims=True),1e-12)
        dvec=B-A[idx]; dpar=np.abs(np.einsum('ij,ij->i',dvec,na[idx]))
        across=float(np.median(np.abs(dist-dpar)))
        ang=float(np.degrees(np.median(np.arccos(np.clip(np.abs(np.einsum('ij,ij->i',nb,na[idx])),-1,1)))))
    else:
        across=float('nan'); ang=float('nan')
    npair+=1
    lines.append('%s\t%s\t%d\t%d\t%.3f\t%.3f\t%.2f'%(piece,arm,len(A),len(B),nn,across,ang))
open(a.out,'w').write('\n'.join(lines)+'\n')
print('\n'.join(lines))
print('cells=%d pairs_scored=%d -> %s'%(ncell,npair,a.out))
