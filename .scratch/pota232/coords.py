import numpy as np
def load_pcd(path):
    with open(path) as f: txt = f.read()
    head, data = txt.split('DATA ascii')
    npts = int([l for l in head.splitlines() if l.startswith('WIDTH')][0].split()[1])
    nf = len([l for l in head.splitlines() if l.startswith('FIELDS')][0].split())-1
    arr = np.fromstring(data, sep=' ')
    return arr[:npts*nf].reshape(npts, nf)[:, :3]
A = 'C:/PR/SfSpp_preprocessing/.scratch/pota221/pota221f/author/'
L = 'C:/PR/SfSpp_preprocessing/.scratch/pota221/pota221f/lanes/'
o0 = load_pcd(A+'Pot_D_Piece_22_Breakline_0.pcd')
o1 = load_pcd(A+'Pot_D_Piece_22_Breakline_1.pcd')
b0 = load_pcd(L+'Pot_D_Piece_22_Breakline_0.pcd')
b1 = load_pcd(L+'Pot_D_Piece_22_Breakline_1.pcd')
np.set_printoptions(precision=2, suppress=True)
print('b1 idx46-52:')
for i in range(46, 53): print(f'  {i}: {b1[i]}')
print('b0 idx0-3 + idx28-32:')
for i in [0,1,2,3,28,29,30,31,32]: print(f'  b0[{i}]: {b0[i]}')
# nearest author lane per dot for b1 on-rim stretch and b0 tail
for name, lane, idxs in [('b1',b1,range(33,53)), ('b0',b0,range(28,40))]:
    d0 = np.linalg.norm(lane[None,:,:]-o0[:,None,:] if False else lane[:,None,:]-o0[None,:,:], axis=2).min(axis=1)
    d1 = np.linalg.norm(lane[:,None,:]-o1[None,:,:], axis=2).min(axis=1)
    print(f'{name}: idx d_o0 d_o1 nearer')
    for i in idxs: print(f'  {i}: {d0[i]:.2f} {d1[i]:.2f} {"o0" if d0[i]<d1[i] else "o1"}')
