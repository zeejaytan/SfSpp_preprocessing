import numpy as np
from scipy.spatial import cKDTree
def load_pcd_xyz(path):
    with open(path) as f: txt = f.read()
    head, data = txt.split('DATA ascii')
    npts = int([l for l in head.splitlines() if l.startswith('WIDTH')][0].split()[1])
    nf = len([l for l in head.splitlines() if l.startswith('FIELDS')][0].split())-1
    arr = np.fromstring(data, sep=' ')
    return arr[:npts*nf].reshape(npts, nf)
def load_xyz(path):
    rows = []
    with open(path) as f:
        for line in f:
            p = line.split()
            if len(p) >= 6: rows.append([float(x) for x in p[:6]])
    return np.array(rows)
def load_ply_xyz(path):
    with open(path, errors='ignore') as f: txt = f.read()
    i = txt.find('end_header')
    arr = np.fromstring(txt[i+10:], sep=' ')
    head = txt[:i]
    nv = int([l for l in head.splitlines() if l.startswith('element vertex')][0].split()[2])
    return arr[:nv*(arr.size//nv)].reshape(nv, arr.size//nv)[:, :3]
F = 'C:/PR/SfSpp_preprocessing/artifacts/pota232/'
L = 'C:/PR/SfSpp_preprocessing/.scratch/pota221/pota221f/lanes/'
b1 = load_pcd_xyz(L+'Pot_D_Piece_22_Breakline_1.pcd')[:, :3]
S0 = load_xyz(F+'P22_S0_thr12.xyz')[:, :3]; S1 = load_xyz(F+'P22_S1_thr12.xyz')[:, :3]
UN12 = load_ply_xyz(F+'P22_UN_thr12.ply')
cloud = load_pcd_xyz(F+'Pot_D_Piece_22_Point.pcd')
C, N = cloud[:, :3], cloud[:, 3:6]
tree = cKDTree(C)
S0_14 = load_xyz(F+'P22_S0_thr14.xyz')[:, :3]; S1_14 = load_xyz(F+'P22_S1_thr14.xyz')[:, :3]
S0_10 = load_xyz(F+'P22_S0_thr10.xyz')[:, :3]; S1_10 = load_xyz(F+'P22_S1_thr10.xyz')[:, :3]
UN14 = load_ply_xyz(F+'P22_UN_thr14.ply'); UN10 = load_ply_xyz(F+'P22_UN_thr10.ply')
print('shapes:', S0_14.shape, S1_14.shape, UN14.shape, S0_10.shape, S1_10.shape, UN10.shape)
t0, t1, tu = cKDTree(S0), cKDTree(S1), cKDTree(UN12)
print('per excursion dot: nearest S0/S1/UN12/cloud + S:')
for i in range(46, 53):
    p = b1[i]
    d0 = t0.query(p, k=1)[0]; d1 = t1.query(p, k=1)[0]; du = tu.query(p, k=1)[0]
    idx = tree.query_ball_point(p, 2.0)
    m = N[idx].mean(axis=0) if len(idx) >= 3 else np.array([np.nan]*3)
    S = float(np.degrees(np.arccos(min(1.0, abs(np.linalg.norm(m)))))) if len(idx)>=3 else float('nan')
    print(f'  b1[{i}] {p.round(2)} dS0 {d0:.2f} dS1 {d1:.2f} dUN {du:.2f} ncloud2mm {len(idx)} S {S:.1f}')
# bridge pair location: find argmin S0->S1
print('bridge search...')
d, j = t1.query(S0, k=1)
k = int(np.argmin(d))
print(f'  min S0->S1: {d[k]:.4f} S0dot {S0[k].round(2)} S1mate {S1[j[k]].round(2)}')
d2, j2 = t0.query(S1, k=1)
k2 = int(np.argmin(d2))
print(f'  min S1->S0: {d2[k2]:.4f} S1dot {S1[k2].round(2)} S0mate {S0[j2[k2]].round(2)}')
turn = b1[48]
print(f'  turn {turn.round(2)} dist to bridge S0dot {np.linalg.norm(S0[k]-turn):.2f}, to bridge S1dot {np.linalg.norm(S1[k2]-turn):.2f}')
# (e): tab-region census at @14/@12/@10: dots of S0/S1/UN within 5mm of each excursion dot
for nm, a0, a1, uu in [('@14',S0_14,S1_14,UN14),('@12',S0,S1,UN12),('@10',S0_10,S1_10,UN10)]:
    A0, A1, UU = cKDTree(a0), cKDTree(a1), cKDTree(uu)
    row = []
    for i in range(48, 53):
        p = b1[i]
        row.append((len(A0.query_ball_point(p,5.0)), len(A1.query_ball_point(p,5.0)), len(UU.query_ball_point(p,5.0))))
    print(f'  {nm} per-dot (S0,S1,UN) within 5mm: ' + ' '.join(str(r) for r in row))
