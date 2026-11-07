import glob, os, sys, numpy as np
CORPUS = "/data/gpfs/projects/punim2657/sfs_main/original_samples/SfS_pp"
sys.path.insert(0, "/data/gpfs/projects/punim2657/sfs_preprocessing/work_314")

from sfs_axes.pottmann import compute_pottmann_axis
from sfs_axes.potsac import _cluster_union, effective_step
from sfs_axes.normalized import centroid_distance, is_base_fragment
from sfs_axes.io_axes import read_axes, direction_angle_deg

def run_potsac_basins(C, total_seeds=10, iters_per_seed=1000):
    Cd = C[:, ::effective_step(C.shape[1], 10)]
    nd = Cd.shape[1]
    all_cands = []
    for seed in range(total_seeds):
        rng = np.random.default_rng(seed)
        for _ in range(iters_per_seed):
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
    return reps, sizes, len(all_cands)

print("=== CHECKING POT E FAILING PIECES (Decoys should be PURGED) ===")
for p in [3, 23, 24, 25, 26, 28, 31]:
    stem = f"Pot_E_Piece_{p:02d}"
    s0 = np.loadtxt(f"{CORPUS}/Surfaces/{stem}_Surface_0.xyz", usecols=range(6)).T
    s1 = np.loadtxt(f"{CORPUS}/Surfaces/{stem}_Surface_1.xyz", usecols=range(6)).T
    C = np.concatenate([s0, s1], axis=1)
    
    reps, sizes, n_draws = run_potsac_basins(C, 5, 500)
    
    # Check if any decoy with d < 25 has size > 0.05 * n_draws
    decoys_surviving = 0
    max_decoy_size = 0
    for j in range(reps.shape[1]):
        cand = reps[:, j]
        d = centroid_distance(cand, C)
        a = cand[:3] / np.linalg.norm(cand[:3])
        mean_ax = np.mean(np.abs(a @ C[3:6, :]))
        if d < 25.0 or mean_ax > 0.50:
            if sizes[j] > max_decoy_size:
                max_decoy_size = sizes[j]
            if sizes[j] >= 0.05 * n_draws:
                decoys_surviving += 1
    print(f"Piece {p:02d}: {n_draws} draws | max decoy size={max_decoy_size} ({max_decoy_size/n_draws*100:.1f}%) | decoys surviving threshold={decoys_surviving}")

print("\n=== CHECKING GENUINE BASE PIECES (True bases should SURVIVE) ===")
for stem, l_idx in [("Pot_A_Piece_01", 0), ("Pot_B_Piece_01", 0), ("Pot_C_Piece_03", 0), ("Pot_D_Piece_22", 0), ("Pot_D_Piece_28", 1), ("Pot_I_Piece_25", 0)]:
    s0 = np.loadtxt(f"{CORPUS}/Surfaces/{stem}_Surface_0.xyz", usecols=range(6)).T
    s1 = np.loadtxt(f"{CORPUS}/Surfaces/{stem}_Surface_1.xyz", usecols=range(6)).T
    C = np.concatenate([s0, s1], axis=1)
    gt_ax = read_axes(f"{CORPUS}/Axes/{stem}_Axis.xyz")[:, l_idx]
    
    reps, sizes, n_draws = run_potsac_basins(C, 5, 500)
    
    # Find true base basin
    true_base_survives = False
    best_size = 0
    for j in range(reps.shape[1]):
        cand = reps[:, j]
        ang = direction_angle_deg(cand[:3], gt_ax[:3])
        d = centroid_distance(cand, C)
        if ang <= 10.0 and d < 25.0:
            if sizes[j] > best_size:
                best_size = sizes[j]
            if sizes[j] >= 0.05 * n_draws:
                true_base_survives = True
    print(f"{stem}: {n_draws} draws | true base size={best_size} ({best_size/n_draws*100:.1f}%) | true base survives={true_base_survives}")
