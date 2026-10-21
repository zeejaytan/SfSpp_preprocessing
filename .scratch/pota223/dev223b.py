import numpy as np
def load(p):
    d = open(p, 'rb').read()
    h, _, b = d.partition(b'DATA ascii\n')
    if not b:
        h, _, b = d.partition(b'DATA ascii\r\n')
    nf = 3
    for line in h.decode('ascii', errors='replace').splitlines():
        if line.startswith('FIELDS'):
            nf = len(line.split()) - 1
    return np.fromstring(b.decode('ascii', errors='replace'), sep=' ').reshape(-1, nf)[:, :3]
L0 = load('C:/PR/SfSpp_preprocessing/.scratch/pota223/lanes/Pot_D_Piece_12_Breakline_0.pcd')
O1 = load('C:/PR/SfSpp_preprocessing/.scratch/pota221/pota221f/author/Pot_D_Piece_12_Breakline_1.pcd')
d = np.sqrt(((L0[:, None, :] - O1[None, :, :]) ** 2).sum(-1)).min(1)
bad = np.nonzero(d >= 2.0)[0]
runs = np.split(bad, np.nonzero(np.diff(bad) > 1)[0] + 1)
for r in runs:
    print('run idx %d..%d (n=%d) centroid [%.1f, %.1f, %.1f] maxd=%.2f' % (r.min(), r.max(), len(r), L0[r].mean(0)[0], L0[r].mean(0)[1], L0[r].mean(0)[2], d[r].max()))
