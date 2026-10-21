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
print('Bl0 n=%d bad=%d (%.1f%%)' % (len(L0), len(bad), 100.0 * len(bad) / len(L0)))
print('bad idx range: %d..%d' % (bad.min(), bad.max()))
print('bad median dist: %.2f max: %.2f' % (np.median(d[bad]), d[bad].max()))
print('bad centroid: [%.1f, %.1f, %.1f]' % tuple(L0[bad].mean(0)))
print('bad bbox x[%.1f,%.1f] y[%.1f,%.1f] z[%.1f,%.1f]' % (L0[bad][:,0].min(), L0[bad][:,0].max(), L0[bad][:,1].min(), L0[bad][:,1].max(), L0[bad][:,2].min(), L0[bad][:,2].max()))
print('bad xyz head:')
for i in bad[:8]:
    print('  idx %d [%.1f, %.1f, %.1f] d=%.2f' % (i, L0[i][0], L0[i][1], L0[i][2], d[i]))
# walk-order jumps
seg = np.sqrt(((L0[1:] - L0[:-1]) ** 2).sum(-1))
j = np.nonzero(seg > 10)[0]
print('jumps>10 at:', [(int(i), round(float(seg[i]), 1)) for i in j])
# where is the jump located
for i in j:
    print('  jump after idx %d at [%.1f, %.1f, %.1f]' % (int(i), L0[int(i)][0], L0[int(i)][1], L0[int(i)][2]))
