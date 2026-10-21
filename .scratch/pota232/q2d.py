import numpy as np
from scipy.spatial import cKDTree
def load_pcd_xyz(path):
    with open(path) as f: txt = f.read()
    head, data = txt.split('DATA ascii')
    npts = int([l for l in head.splitlines() if l.startswith('WIDTH')][0].split()[1])
    nf = len([l for l in head.splitlines() if l.startswith('FIELDS')][0].split())-1
    arr = np.fromstring(data, sep=' ')
    return arr[:npts*nf].reshape(npts, nf)[:, :3]
F = 'C:/PR/SfSpp_preprocessing/artifacts/pota232/'
L = 'C:/PR/SfSpp_preprocessing/.scratch/pota221/pota221f/lanes/'
A = 'C:/PR/SfSpp_preprocessing/.scratch/pota221/pota221f/author/'
b1 = load_pcd_xyz(L+'Pot_D_Piece_22_Breakline_1.pcd')
b0 = load_pcd_xyz(L+'Pot_D_Piece_22_Breakline_0.pcd')
o0 = load_pcd_xyz(A+'Pot_D_Piece_22_Breakline_0.pcd')
o1 = load_pcd_xyz(A+'Pot_D_Piece_22_Breakline_1.pcd')
B = load_pcd_xyz(F+'S1_boundary.pcd')
np.set_printoptions(precision=2, suppress=True)
# nearest o1 to b1[52] and to b1[47]
for i in [47, 48, 52]:
    j = int(np.linalg.norm(o1-b1[i],axis=1).argmin())
    print(f'b1[{i}] {b1[i]} nearest o1[{j}] {o1[j]} d={np.linalg.norm(o1[j]-b1[i]):.2f}')
# author o1 direction past idx134: o1[134] -> o1[148]
print('o1[130..148]:')
for i in range(130, 149):
    d = np.linalg.norm(o1[i]-b1[52])
    print(f'  o1[{i}] {o1[i]} d-to-b1end {d:.1f}')
# boundary dots nearest to o1[134]..o1[140] (where boundary ends)
t = cKDTree(B)
for i in [134, 135, 136, 140, 145]:
    dd, ii = t.query(o1[i], k=3)
    print(f'o1[{i}] boundary dists {dd.round(2)}')
# where are the last boundary dots in the tab direction? boundary dots with x < -8
far = B[B[:,0] < -8.0]
print(f'boundary dots x<-8: n={len(far)}', far.round(2) if len(far)<12 else far[:12].round(2))
# b0 turn? b0 first>2mm-never-return check reversed walk (39->0): 
auth = np.vstack([o0,o1])
d = np.linalg.norm(b0[:,None,:]-auth[None,:,:],axis=2).min(axis=1)
print('b0 dist-to-either:', ' '.join(f'{i}:{v:.1f}' for i,v in enumerate(d)))
