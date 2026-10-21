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
            if len(p) >= 6:
                rows.append([float(p[0]), float(p[1]), float(p[2]), float(p[3]), float(p[4]), float(p[5])])
    return np.array(rows)

def load_ply_xyz(path):
    with open(path, errors='ignore') as f: txt = f.read()
    i = txt.find('end_header')
    arr = np.fromstring(txt[i+10:], sep=' ')
    # assume x y z first of stride; detect stride by vertex count
    head = txt[:i]
    nv = int([l for l in head.splitlines() if l.startswith('element vertex')][0].split()[2])
    stride = (arr.size // nv)
    return arr[:nv*stride].reshape(nv, stride)[:, :3]

A = 'C:/PR/SfSpp_preprocessing/.scratch/pota221/pota221f/author/'
L = 'C:/PR/SfSpp_preprocessing/.scratch/pota221/pota221f/lanes/'
F = 'C:/PR/SfSpp_preprocessing/artifacts/pota232/'
o0 = load_pcd_xyz(A+'Pot_D_Piece_22_Breakline_0.pcd')[:, :3]
o1 = load_pcd_xyz(A+'Pot_D_Piece_22_Breakline_1.pcd')[:, :3]
b0 = load_pcd_xyz(L+'Pot_D_Piece_22_Breakline_0.pcd')[:, :3]
b1 = load_pcd_xyz(L+'Pot_D_Piece_22_Breakline_1.pcd')[:, :3]
cloud = load_pcd_xyz(F+'Pot_D_Piece_22_Point.pcd')
C, N = cloud[:, :3], cloud[:, 3:6]
print('cloud', C.shape, 'normals ok')
S0 = load_xyz(F+'P22_S0_thr12.xyz'); S1 = load_xyz(F+'P22_S1_thr12.xyz')
print('S0', S0.shape, 'S1', S1.shape)
UN12 = load_ply_xyz(F+'P22_UN_thr12.ply'); print('UN12', UN12.shape)

tree = cKDTree(C)
# baseline: cloud pts >6mm from any lane dot
lanes = np.vstack([o0, o1, b0, b1])
dmin, _ = cKDTree(lanes).query(C, k=1)
face_idx = np.where(dmin > 6.0)[0]
print('face-interior candidates:', face_idx.size)
rng = np.random.default_rng(0)
sel = rng.choice(face_idx, size=min(600, face_idx.size), replace=False)

def sharpness(pts, r=2.0):
    out = []
    for p in pts:
        idx = tree.query_ball_point(p, r)
        if len(idx) < 3:
            out.append(np.nan); continue
        m = N[idx].mean(axis=0)
        out.append(float(np.degrees(np.arccos(min(1.0, abs(np.linalg.norm(m)))))))
    return np.array(out)

Sb = sharpness(C[sel])
Sb = Sb[~np.isnan(Sb)]
print(f'BASELINE med {np.median(Sb):.2f} n={Sb.size}')
# control: b1 idx35-46 (on-rim) vs nearest author dots
ctrl_ours = b1[35:47]
d_auth = np.linalg.norm(ctrl_ours[:,None,:]-o1[None,:,:], axis=2)
ctrl_auth = o1[d_auth.argmin(axis=1)]
# unique author dots
ctrl_auth = np.unique(ctrl_auth, axis=0)
So = sharpness(ctrl_ours); Sa = sharpness(ctrl_auth)
print(f'CONTROL ours med {np.median(So):.2f} n={So.size} | auth med {np.median(Sa):.2f} n={Sa.size}')
line = max(0.0, float(np.median(Sb))) + 15.0
print(f'DECISION LINE baseline+15 = {line:.2f}; control pass: {np.median(So)>=line and np.median(Sa)>=line}')
# Q1: author line dots
S_o0 = sharpness(o0); S_o1 = sharpness(o1)
print(f'AUTHOR o0 med {np.nanmedian(S_o0):.2f} (n={len(S_o0)}) frac>=line {(S_o0>=line).mean()*100:.1f}%')
print(f'AUTHOR o1 med {np.nanmedian(S_o1):.2f} (n={len(S_o1)}) frac>=line {(S_o1>=line).mean()*100:.1f}%')
S_b0 = sharpness(b0); S_b1 = sharpness(b1)
print(f'OURS b0 med {np.nanmedian(S_b0):.2f} | b1 med {np.nanmedian(S_b1):.2f}')
# Q2a: global S0<->S1 min + near turn
t0, t1 = cKDTree(S0[:,:3]), cKDTree(S1[:,:3])
d01, _ = t0.query(S1[:,:3], k=1); d10, ii10 = t1.query(S0[:,:3], k=1)
print(f'GAP12 global: S1->S0 min {d01.min():.3f} p1 {np.percentile(d01,1):.2f} p50 {np.median(d01):.2f}; S0->S1 min {d10.min():.3f}')
turn = b1[48]
for name, S in [('S0', S0), ('S1', S1)]:
    dd, _ = cKDTree(S[:, :3]).query(turn, k=5)
    print(f'  turn->nearest {name}: {dd[:5].round(2)}')
# near-turn gap: S0 dots within 10mm of turn, their dist to S1
near0 = S0[np.linalg.norm(S0[:,:3]-turn, axis=1) < 10.0]
near1 = S1[np.linalg.norm(S1[:,:3]-turn, axis=1) < 10.0]
print(f'  S0 dots within 10mm of turn: {len(near0)}; S1 dots within 10mm: {len(near1)}')
if len(near0): print('   near0->S1 min', cKDTree(S1[:,:3]).query(near0[:,:3], k=1)[0].min().round(3))
if len(near1): print('   near1->S0 min', cKDTree(S0[:,:3]).query(near1[:,:3], k=1)[0].min().round(3))
# excursion dots b1[48:53]: counts in cloud/S0/S1/UN within 2 and 5mm
UN = UN12
for r in (2.0, 5.0):
    cc = sum(tree.query_ball_point(p, r).__len__() for p in b1[48:53])
    c0 = sum(t0.query_ball_point(p, r).__len__() for p in b1[48:53])
    c1 = sum(t1.query_ball_point(p, r).__len__() for p in b1[48:53])
    tu = cKDTree(UN)
    cu = sum(tu.query_ball_point(p, r).__len__() for p in b1[48:53])
    print(f'  r={r}: cloud {cc} S0 {c0} S1 {c1} UN12 {cu} (5 excursion dots)')
# turn dot sharpness
print('TURN S:', sharpness(turn[None,:]))
