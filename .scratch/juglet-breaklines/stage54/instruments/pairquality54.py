import numpy as np, sys, os, glob, argparse, json
from scipy.spatial import cKDTree

# ticket 54 pair quality -- the paircheck45.py protocol, parameterised over this run's cell
# directories: every <PIECE>_arm{D,X,W,W7}/surfaces/<PIECE>_Surface_{0,1}.ply pair.
# med_nn     median nearest-neighbour distance B->A (surface 1 points to surface 0 tree)
# med_across median |dist - d_par| : the perpendicular residual of B off A's local tangent
# med_angle  median angle between normals at the nearest-neighbour pairs
# wall_mm / med_nn_pct_wall: the piece's OWN wall thickness (ticket 40's 800-ray method,
# wall40.py run on the arm-W Surface_0 against the corpus mesh) and med_nn as a % of it.
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
ap.add_argument('--walls',default=None,help='dir of wall40 <PIECE>_wall.json (optional)')
ap.add_argument('--out',required=True)
a=ap.parse_args()

walls={}
wdir=a.walls
if wdir and os.path.isdir(wdir):
    for j in glob.glob(os.path.join(wdir,'*.json')):
        try:
            r=json.load(open(j,encoding='utf-8'))
            if r.get('thick_med_mm') is not None: walls[r.get('piece',os.path.basename(j))]=float(r['thick_med_mm'])
        except Exception: pass

lines=['piece\tarm\tn0\tn1\tmed_nn\tmed_across\tmed_angle\twall_mm\tmed_nn_pct_wall']
ncell=0; npair=0
for cd in sorted(glob.glob(a.cells+'/*_arm*')):
    cell=os.path.basename(cd)
    import re
    m=re.match(r'^(.*)_arm(D|X|W7|W)$',cell)
    if not m: continue
    piece,arm=m.group(1),m.group(2)
    piece=cell[:-5]
    ncell+=1
    f0=glob.glob(cd+'/surfaces/*_Surface_0.ply'); f1=glob.glob(cd+'/surfaces/*_Surface_1.ply')
    if not f0 or not f1:
        lines.append('%s\t%s\tNO-SURFACE-FILE\t\t\t\t\t\t'%(piece,arm)); continue
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
    w=walls.get(piece)
    pct=('%.1f'%(100.0*nn/w)) if w else '-'
    lines.append('%s\t%s\t%d\t%d\t%.3f\t%.3f\t%.2f\t%s\t%s'%(piece,arm,len(A),len(B),nn,across,ang,('%.3f'%w) if w else '-',pct))
open(a.out,'w').write('\n'.join(lines)+'\n')
print('\n'.join(lines))
print('cells=%d pairs_scored=%d walls=%d -> %s'%(ncell,npair,len(walls),a.out))
