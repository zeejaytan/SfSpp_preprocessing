import glob, os, sys, numpy as np
CORPUS = "/data/gpfs/projects/punim2657/sfs_main/original_samples/SfS_pp"
sys.path.insert(0, "/data/gpfs/projects/punim2657/sfs_preprocessing/work_314")
from sfs_axes.io_axes import read_axes
from sfs_axes.pottmann import compute_pottmann_axis
from sfs_axes.potsac import _cluster_union, effective_step
from sfs_axes.normalized import centroid_distance

# Check all pieces across all pots
results = []
for pdir in sorted(glob.glob(f"{CORPUS}/Axes/*_Axis.xyz")):
    stem = os.path.basename(pdir).replace("_Axis.xyz", "")
    s0_p = f"{CORPUS}/Surfaces/{stem}_Surface_0.xyz"
    s1_p = f"{CORPUS}/Surfaces/{stem}_Surface_1.xyz"
    if not os.path.exists(s0_p): continue
    s0 = np.loadtxt(s0_p, usecols=range(6)).T
    s1 = np.loadtxt(s1_p, usecols=range(6)).T
    C = np.concatenate([s0, s1], axis=1)
    c_pt = C[:3].mean(axis=1)
    
    axes = read_axes(pdir)
    gt_min_d = min(np.linalg.norm(np.cross(c_pt - axes[3:6, k], axes[:3, k]/np.linalg.norm(axes[:3, k]))) for k in range(axes.shape[1]))
    gt_is_base = (gt_min_d < 25.0)

    # Run quick Pottmann SAC: 3 seeds * 300 draws = 900 draws
    Cd = C[:, ::effective_step(C.shape[1], 10)]
    nd = Cd.shape[1]
    all_cands = []
    for seed in range(3):
        rng = np.random.default_rng(seed)
        for _ in range(300):
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
    
    # Check if there is ANY basin with d >= 25.0 and mean_ax <= 0.50 and size >= 10
    has_cylinder_basin = False
    best_cyl_size = 0
    for j in range(reps.shape[1]):
        cand = reps[:, j]
        d = centroid_distance(cand, C)
        a = cand[:3] / np.linalg.norm(cand[:3])
        mean_ax = np.mean(np.abs(a @ C[3:6, :]))
        if d >= 25.0 and mean_ax <= 0.50 and sizes[j] >= 10:
            has_cylinder_basin = True
            if sizes[j] > best_cyl_size: best_cyl_size = sizes[j]
            
    results.append((stem, gt_is_base, gt_min_d, has_cylinder_basin, best_cyl_size))

print(f"Total pieces evaluated: {len(results)}")
print("\n--- BASE PIECES (gt_min_d < 25mm) ---")
for r in results:
    if r[1]:
        print(f"{r[0]:18s} [BASE] gt_d={r[2]:4.1f} | has_cyl={r[3]} (best_size={r[4]})")

print("\n--- FAILING POT E PIECES ---")
for r in results:
    if r[0] in [f"Pot_E_Piece_{p:02d}" for p in [3, 23, 24, 25, 26, 28, 31]]:
        print(f"{r[0]:18s} [WALL] gt_d={r[2]:4.1f} | has_cyl={r[3]} (best_size={r[4]})")
