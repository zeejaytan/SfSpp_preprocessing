import numpy as np
from scipy.spatial import cKDTree
def load_pcd_xyz(path):
    with open(path) as f: txt = f.read()
    head, data = txt.split('DATA ascii')
    npts = int([l for l in head.splitlines() if l.startswith('WIDTH')][0].split()[1])
    nf = len([l for l in head.splitlines() if l.startswith('FIELDS')][0].split())-1
    arr = np.fromstring(data, sep=' ')
    return arr[:npts*nf].reshape(npts, nf)[:, :3]
def load_seg(path):
    return np.loadtxt(path)[:, :3]
F = 'C:/PR/SfSpp_preprocessing/artifacts/pota232/'
L = 'C:/PR/SfSpp_preprocessing/.scratch/pota221/pota221f/lanes/'
A = 'C:/PR/SfSpp_preprocessing/.scratch/pota221/pota221f/author/'
b1 = load_pcd_xyz(L+'Pot_D_Piece_22_Breakline_1.pcd')
o1 = load_pcd_xyz(A+'Pot_D_Piece_22_Breakline_1.pcd')
B = load_pcd_xyz(F+'S1_boundary.pcd'); print('boundary n=', B.shape)
s1 = load_seg(F+'S1_seg1.xyz'); s2 = load_seg(F+'S1_seg2.xyz')
print('seg shapes:', s1.shape, s2.shape)
# which seg is b1's? nearest seg endpoints to b1 ends
for nm, s in [('seg1',s1),('seg2',s2)]:
    print(nm, 'start', s[0].round(2), 'end', s[-1].round(2), 'd to b1[52]:', round(float(np.linalg.norm(s-b1[52],axis=1).min()),2), 'd to b1[0]:', round(float(np.linalg.norm(s-b1[0],axis=1).min()),2))
# turn angle multi-step along b1 at corner
for w in (1,2,4):
    a = b1[47]-b1[47-w]; d = b1[47+w]-b1[47]
    ang = float(np.degrees(np.arccos(np.clip(a@d/np.linalg.norm(a)/np.linalg.norm(d),-1,1))))
    print(f'w={w}: arrival {a.round(2)} departure {d.round(2)} angle {ang:.1f}')
# author o1 corner: max turn along o1 near b1[47]
d = np.linalg.norm(o1-b1[47],axis=1)
near = np.where(d < 12.0)[0]
print('o1 dots within 12mm of b1[47]:', near.min(), '..', near.max(), 'n=', len(near))
best = (0,0)
for i in range(near.min()+2, near.max()-2):
    a = o1[i]-o1[i-2]; dd = o1[i+2]-o1[i]
    ang = float(np.degrees(np.arccos(np.clip(a@dd/np.linalg.norm(a)/np.linalg.norm(dd),-1,1))))
    if ang > best[1]: best = (i, ang)
print(f'o1 max corner in window: idx {best[0]} angle {best[1]:.1f} coord {o1[best[0]].round(2)}')
# gap test: boundary spacing near turn
t = cKDTree(B)
d216, _ = t.query(B, k=2)
sp = d216[:,1]
nearB = np.linalg.norm(B-b1[47],axis=1) < 12.0
print(f'boundary spacing near corner (<12mm, n={nearB.sum()}): med {np.median(sp[nearB]):.2f} max {sp[nearB].max():.2f}')
print(f'boundary spacing global: med {np.median(sp):.2f} max {sp.max():.2f} (idx {int(np.argmax(sp))} {B[int(np.argmax(sp))].round(2)})')
# does boundary continue past b1[52] toward author? o1 dots within 15mm of b1[52], their dist to boundary
m = np.linalg.norm(o1-b1[52],axis=1)
q = np.where(m < 15.0)[0]
print(f'o1 dots within 15mm of b1[52]: idx {q.min()}..{q.max()} n={len(q)}')
db, _ = t.query(o1[q], k=1)
print('  their dist to boundary: ' + ' '.join(f'{i}:{v:.1f}' for i,v in zip(q, db)))
# boundary dots past the lane end: boundary within 8mm of b1[52] count, and beyond (farther along o1 dir)
print('boundary within 8mm of b1[52]:', int((np.linalg.norm(B-b1[52],axis=1)<8.0).sum()))
print('boundary within 8mm of b1[47]:', int((np.linalg.norm(B-b1[47],axis=1)<8.0).sum()))
