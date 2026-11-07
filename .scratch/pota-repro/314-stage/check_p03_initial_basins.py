import os, sys, numpy as np
sys.path.insert(0, "/data/gpfs/projects/punim2657/sfs_preprocessing/work_314")
CORPUS = "/data/gpfs/projects/punim2657/sfs_main/original_samples/SfS_pp"

from sfs_axes.normalized import centroid_distance, is_base_fragment
from sfs_axes.pottmann import compute_pottmann_axis
from sfs_axes.potsac import _cluster_union, effective_step

stem = "Pot_E_Piece_03"
s0 = np.loadtxt(f"{CORPUS}/Surfaces/{stem}_Surface_0.xyz", usecols=range(6)).T
s1 = np.loadtxt(f"{CORPUS}/Surfaces/{stem}_Surface_1.xyz", usecols=range(6)).T
C = np.concatenate([s0, s1], axis=1)

Cd = C[:, ::effective_step(C.shape[1], 10)]
nd = Cd.shape[1]

all_cands = []
for seed in range(10):
    rng = np.random.default_rng(seed)
    for _ in range(1000):
        kidx = rng.choice(nd, 6, replace=False)
        Cs = Cd[:, kidx].copy()
        mCs = Cs[:3, :].mean(axis=1)
        Cs[:3, :] -= mCs[:, None]
        scale = float(np.mean(np.abs(Cs)))
        if scale < 1e-8: continue
        Cs[:3, :] /= scale
        try:
            vt = compute_pottmann_axis(Cs)
            vt[3:6] = vt[3:6] * scale + mCs
            vt[3:6] -= (vt[:3] @ vt[3:6]) * vt[:3]
            all_cands.append(vt)
        except Exception: pass

V = np.column_stack(all_cands)
reps, sizes = _cluster_union(V)

print(f"Total basins on Piece 03: {reps.shape[1]}")
for j in range(reps.shape[1]):
    cand = reps[:, j]
    d_c = centroid_distance(cand, C)
    if d_c < 25.0:
        base = is_base_fragment(C, cand)
        a = cand[:3] / np.linalg.norm(cand[:3])
        mean_ax = np.mean(np.abs(a @ C[3:6, :]))
        print(f"  Basin {j}: d_c={d_c:.1f}mm, mean_ax={mean_ax:.3f}, is_base={base}")
