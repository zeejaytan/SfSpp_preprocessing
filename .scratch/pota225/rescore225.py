"""POTA-225 local re-verification: slot matrix + med/cov/jumps/gapmax (209 pattern)."""
import numpy as np, os, sys
from scipy.spatial import cKDTree
B = 'C:/PR/SfSpp_preprocessing/.scratch/'

def load_xyz(p):
    pts = []
    with open(p) as f:
        for ln in f:
            s = ln.split()
            if len(s) >= 3:
                try: pts.append([float(x) for x in s[:3]])
                except ValueError: pass
    return np.array(pts)

def load_pcd(p):
    with open(p, 'rb') as f: data = f.read()
    head, _, body = data.partition(b'DATA ascii\n')
    if not body: head, _, body = data.partition(b'DATA ascii\r\n')
    nf = 3
    for ln in head.decode('ascii', errors='replace').splitlines():
        if ln.startswith('FIELDS'): nf = len(ln.split()) - 1
    return np.fromstring(body.decode('ascii', errors='replace'), sep=' ').reshape(-1, nf)[:, :3]

def stats(our, auth):
    dd, _ = cKDTree(auth).query(our)
    gaps = np.linalg.norm(np.diff(our, axis=0), axis=1)
    return (round(float(np.median(dd)), 2), round(float((dd < 2.0).mean() * 100), 1),
            round(float(dd.max()), 1), int((gaps > 10.0).sum()),
            round(float(gaps.max()) if gaps.size else 0.0, 1), len(our))

JOBS = [
    ('P12@3', B + 'pota224/lanes/Pot_D_Piece_12_Breakline_0.pcd',
              B + 'pota224/lanes/Pot_D_Piece_12_Breakline_1.pcd',
              B + 'pota222/p12/auth_Bl0.pcd', B + 'pota222/p12/auth_Bl1.pcd', 'pcd', 'pcd'),
    ('P15@8', B + 'pota222/lanes/Pot_D_Piece_15_Breakline_0.xyz',
              B + 'pota222/lanes/Pot_D_Piece_15_Breakline_1.xyz',
              B + 'pota221/pota221f/author/Pot_D_Piece_15_Breakline_0.pcd',
              B + 'pota221/pota221f/author/Pot_D_Piece_15_Breakline_1.pcd', 'xyz', 'pcd'),
    ('P16@10', B + 'pota222/lanes/Pot_D_Piece_16_Breakline_0.xyz',
               B + 'pota222/lanes/Pot_D_Piece_16_Breakline_1.xyz',
               B + 'pota221/pota221f/author/Pot_D_Piece_16_Breakline_0.pcd',
               B + 'pota221/pota221f/author/Pot_D_Piece_16_Breakline_1.pcd', 'xyz', 'pcd'),
    ('P01@8', B + '.wt-220/artifacts/pota220/p01_8_Bl0.pcd',
              B + '.wt-220/artifacts/pota220/p01_8_Bl1.pcd',
              B + '.wt-220/artifacts/pota220/p01_author_Bl0.pcd',
              B + '.wt-220/artifacts/pota220/p01_author_Bl1.pcd', 'pcd', 'pcd'),
]
for tag, l0p, l1p, a0p, a1p, lf, af in JOBS:
    ll = load_xyz if lf == 'xyz' else load_pcd
    la = load_xyz if af == 'xyz' else load_pcd
    L = [ll(l0p), ll(l1p)]; A = [la(a0p), la(a1p)]
    print('%s refs o0=%d o1=%d n0=%d n1=%d' % (tag, len(A[0]), len(A[1]), len(L[0]), len(L[1])))
    for i in [0, 1]:
        for j in [0, 1]:
            m, c, mx, jmp, gm, n = stats(L[i], A[j])
            print('  SLOT o%d->a%d med=%.2f cov=%.1f max=%.1f jumps=%d gapmax=%.1f n=%d' % (i, j, m, c, mx, jmp, gm, n))
print('RESCORE225-OK')
