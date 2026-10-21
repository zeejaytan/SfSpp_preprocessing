import numpy as np
def load_pcd_xyz(path):
    with open(path) as f: txt = f.read()
    head, data = txt.split('DATA ascii')
    npts = int([l for l in head.splitlines() if l.startswith('WIDTH')][0].split()[1])
    nf = len([l for l in head.splitlines() if l.startswith('FIELDS')][0].split())-1
    arr = np.fromstring(data, sep=' ')
    return arr[:npts*nf].reshape(npts, nf)[:, :3]
L = 'C:/PR/SfSpp_preprocessing/.scratch/pota221/pota221f/lanes/'
A = 'C:/PR/SfSpp_preprocessing/.scratch/pota221/pota221f/author/'
b0 = load_pcd_xyz(L+'Pot_D_Piece_22_Breakline_0.pcd')
np.set_printoptions(precision=2, suppress=True)
print('b0 excursion idx20-30:')
for i in range(20, 31): print(f'  b0[{i}]: {b0[i]}')
print('b0[0..3]:')
for i in range(4): print(f'  b0[{i}]: {b0[i]}')
