import numpy as np
from scipy.spatial import cKDTree
def load_pcd_xyz(path):
    with open(path) as f: txt = f.read()
    head, data = txt.split('DATA ascii')
    npts = int([l for l in head.splitlines() if l.startswith('WIDTH')][0].split()[1])
    nf = len([l for l in head.splitlines() if l.startswith('FIELDS')][0].split())-1
    arr = np.fromstring(data, sep=' ')
    return arr[:npts*nf].reshape(npts, nf)[:, :3]
def load_xyz3(path):
    return np.loadtxt(path)[:, :3]
def load_ply3(path):
    import re
    with open(path, errors='ignore') as f: txt = f.read()
    i = txt.find('end_header')
    arr = np.fromstring(txt[i+10:], sep=' ')
    nv = int(re.search(r'element vertex (\d+)', txt[:i]).group(1))
    return arr[:nv*(arr.size//nv)].reshape(nv, arr.size//nv)[:, :3]
F = 'C:/PR/SfSpp_preprocessing/artifacts/pota232/'
L = 'C:/PR/SfSpp_preprocessing/.scratch/pota221/pota221f/lanes/'
A = 'C:/PR/SfSpp_preprocessing/.scratch/pota221/pota221f/author/'
b1 = load_pcd_xyz(L+'Pot_D_Piece_22_Breakline_1.pcd')
o1 = load_pcd_xyz(A+'Pot_D_Piece_22_Breakline_1.pcd')
B = load_pcd_xyz(F+'S1_boundary.pcd')
S1 = load_xyz3(F+'P22_S1_thr12.xyz'); S0 = load_xyz3(F+'P22_S0_thr12.xyz'); UN = load_ply3(F+'P22_UN_thr12.ply')
tB, t1, t0, tU = cKDTree(B), cKDTree(S1), cKDTree(S0), cKDTree(UN)
np.set_printoptions(precision=2, suppress=True)
# 1. directions + angle
rim = o1[136]-o1[132]; brk = b1[52]-b1[48]
rim_u = rim/np.linalg.norm(rim); brk_u = brk/np.linalg.norm(brk)
ang = float(np.degrees(np.arccos(np.clip(rim_u@brk_u,-1,1))))
print(f'rim dir (o1 132->136): {rim.round(2)} |len {np.linalg.norm(rim):.2f}|')
print(f'break dir (b1 48->52): {brk.round(2)} |len {np.linalg.norm(brk):.2f}|')
print(f'ANGLE rim-vs-break: {ang:.1f} deg')
# arrival dir for reference
arr = b1[47]-b1[43]
print(f'arrival dir (b1 43->47): {arr.round(2)}; angle arrival-vs-break: {float(np.degrees(np.arccos(np.clip(arr/np.linalg.norm(arr)@brk_u,-1,1)))):.1f}')
# 2. membership table: rim continuation o1[128..140] vs break b1[48..52]
print('idx | dBnd dS1 dS0 dUN | nearest')
for tag, i, p in [('rim', i, o1[i]) for i in range(128, 141)] + [('brk', i, b1[i]) for i in range(48, 53)]:
    dB = tB.query(p,k=1)[0]; d1 = t1.query(p,k=1)[0]; d0 = t0.query(p,k=1)[0]; dU = tU.query(p,k=1)[0]
    m = min((dB,'BND'),(d1,'S1'),(d0,'S0'),(dU,'UN'))
    print(f'  {tag}{i}: {dB:.2f} {d1:.2f} {d0:.2f} {dU:.2f} -> {m[1]}')
# 3. fork branch structure: boundary dots within 4mm of b1[47]
near = B[np.linalg.norm(B-b1[47],axis=1) < 4.0]
print(f'boundary dots within 4mm of fork b1[47]: n={len(near)}')
if len(near) >= 3:
    c = near.mean(axis=0); u, s, vt = np.linalg.svd(near-c, full_matrices=False)
    print(f'  centroid {c.round(2)} PCA var ratio: {(s**2/(s**2).sum()).round(3)}')
    print(f'  PC1 {vt[0].round(3)} PC2 {vt[1].round(3)}')
    # project onto PC1: bimodal (two branches) or uniform?
    pr = (near-c)@vt[0]
    print(f'  PC1 spread: min {pr.min():.2f} max {pr.max():.2f}')
    hist, edges = np.histogram(pr, bins=6)
    print(f'  PC1 hist: {hist} edges {edges.round(2)}')
