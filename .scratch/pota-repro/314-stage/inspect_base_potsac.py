import os, sys, numpy as np
CORPUS = "/data/gpfs/projects/punim2657/sfs_main/original_samples/SfS_pp"
sys.path.insert(0, "/data/gpfs/projects/punim2657/sfs_preprocessing/work_314")

from sfs_axes.pottmann import compute_pottmann_axis
from sfs_axes.potsac import _cluster_union, effective_step
from sfs_axes.normalized import centroid_distance
from sfs_axes.io_axes import read_axes, direction_angle_deg

base_pieces = [
    ("Pot_A_Piece_01", 0),
    ("Pot_B_Piece_01", 0),
    ("Pot_C_Piece_03", 0),
    ("Pot_D_Piece_22", 0),
    ("Pot_D_Piece_28", 1),
    ("Pot_D_Piece_32", 0),
    ("Pot_G_Piece_07", 0),
    ("Pot_I_Piece_25", 0),
]

for stem, l_idx in base_pieces:
    s0 = np.loadtxt(f"{CORPUS}/Surfaces/{stem}_Surface_0.xyz", usecols=range(6)).T
    s1 = np.loadtxt(f"{CORPUS}/Surfaces/{stem}_Surface_1.xyz", usecols=range(6)).T
    C = np.concatenate([s0, s1], axis=1)
    
    gt_ax = read_axes(f"{CORPUS}/Axes/{stem}_Axis.xyz")[:, l_idx]
    
    Cd = C[:, ::effective_step(C.shape[1], 10)]
    nd = Cd.shape[1]

    all_cands = []
    for seed in range(5):
        rng = np.random.default_rng(seed)
        for _ in range(500):
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
    
    print(f"\n{stem} (GT d={centroid_distance(gt_ax, C):.1f}mm): {len(all_cands)} draws -> {reps.shape[1]} basins")
    # Find basins close to GT
    for j in range(reps.shape[1]):
        cand = reps[:, j]
        d = centroid_distance(cand, C)
        ang = direction_angle_deg(cand[:3], gt_ax[:3])
        if ang < 15.0 or sizes[j] > 100:
            a = cand[:3] / np.linalg.norm(cand[:3])
            mean_ax = np.mean(np.abs(a @ C[3:6, :]))
            print(f"  Basin {j:2d}: size={sizes[j]:4d}, d={d:5.1f}mm, ang={ang:5.2f}deg, mean_ax={mean_ax:.3f}")
