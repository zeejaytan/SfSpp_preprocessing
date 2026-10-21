import numpy as np
from scipy.spatial import cKDTree
def load_xyz3(path):
    return np.loadtxt(path)[:, :3]
F = 'C:/PR/SfSpp_preprocessing/artifacts/pota232/'
S0 = load_xyz3(F+'P22_S0_thr12.xyz'); S1 = load_xyz3(F+'P22_S1_thr12.xyz')
t1 = cKDTree(S1)
d, j = t1.query(S0, k=1)
mask = d < 2.0
print(f'S0 dots within 2mm of S1: {mask.sum()} / {len(S0)}')
pts = S0[mask]
mates = S1[j[mask]]
mid = (pts + mates) / 2
print(f'contact mids bbox x[{mid[:,0].min():.1f},{mid[:,0].max():.1f}] y[{mid[:,1].min():.1f},{mid[:,1].max():.1f}] z[{mid[:,2].min():.1f},{mid[:,2].max():.1f}]')
turn = np.array([-4.15, 18.58, 439.21])
fork = np.array([-2.77, 18.05, 438.19])
dm = np.linalg.norm(mid - turn, axis=1)
print(f'contact mids dist to turn: min {dm.min():.2f} med {np.median(dm):.2f} max {dm.max():.2f}')
df = np.linalg.norm(mid - fork, axis=1)
print(f'contact mids dist to fork b1[47]: min {df.min():.2f} med {np.median(df):.2f}')
# histogram of distances: one patch or several?
h, e = np.histogram(dm, bins=[0,2,5,10,15,20,50])
print(f'dist-to-turn hist {h} edges {e}')
# closest 5 mids
idx = np.argsort(dm)[:5]
for i in idx:
    print(f'  mid {mid[i].round(2)} d-to-turn {dm[i]:.2f} gap {d[mask][i]:.3f}')
# reverse direction too
t0 = cKDTree(S0)
d2, j2 = t0.query(S1, k=1)
mask2 = d2 < 2.0
print(f'S1 dots within 2mm of S0: {mask2.sum()} / {len(S1)}')
mid2 = (S1[mask2] + S0[j2[mask2]]) / 2
print(f'reverse mids bbox x[{mid2[:,0].min():.1f},{mid2[:,0].max():.1f}] y[{mid2[:,1].min():.1f},{mid2[:,1].max():.1f}] z[{mid2[:,2].min():.1f},{mid2[:,2].max():.1f}]')
