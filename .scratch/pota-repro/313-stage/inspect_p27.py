#!/usr/bin/env python3
import os, sys, numpy as np

CORPUS = "/data/gpfs/projects/punim2657/sfs_main/original_samples/SfS_pp"
sys.path.insert(0, ".")
from sfs_axes.pottmann import compute_pottmann_axis
from sfs_axes.normalized import centroid_distance, worst_wall_normalized_cost, DEFAULT_CLEARANCE_MM
from sfs_axes.potsac import _cluster_union, effective_step
from sfs_axes.io_axes import direction_angle_deg
from check_ref_drift import load_surface, read_axis

def canonicalize(vt):
    vt = np.asarray(vt, dtype=float).copy()
    if vt[2] < 0: vt[:3] = -vt[:3]
    return vt

p = 27
stem = f"Pot_E_Piece_{p:02d}"
s0_path = os.path.join(CORPUS, "Surfaces", f"{stem}_Surface_0.xyz")
s1_path = os.path.join(CORPUS, "Surfaces", f"{stem}_Surface_1.xyz")
gt_path = os.path.join(CORPUS, "Ground Truth Axes", f"{stem}_Axis.xyz")
rel_path = os.path.join(CORPUS, "Axes", f"{stem}_Axis.xyz")

C0 = load_surface(s0_path)
C1 = load_surface(s1_path)
C = np.concatenate([C0, C1], axis=1)
N = C[3:6, :]
gt_axes = read_axis(gt_path)
vt_gt = canonicalize(gt_axes[:, 0])

Cd = C[:, ::1]
nd = Cd.shape[1]

all_cands = []
for seed in range(10):
    rng = np.random.default_rng(seed)
    for _ in range(1000):
        kidx = rng.choice(nd, 6, replace=False)
        Cs = Cd[:, kidx].copy()
        mCs = Cs[0:3, :].mean(axis=1)
        Cs[0:3, :] -= mCs[:, None]
        scale = float(np.mean(np.abs(Cs)))
        if scale < 1e-8: continue
        Cs[0:3, :] /= scale
        try:
            vt = compute_pottmann_axis(Cs)
            vt[3:6] = vt[3:6] * scale + mCs
            vt[3:6] -= (vt[0:3] @ vt[3:6]) * vt[0:3]
            all_cands.append(vt)
        except Exception:
            pass

V = np.column_stack(all_cands)
print(f"Total Pottmann draws: {V.shape[1]}")

# Sort draws by distance to GT to see what costs they have
angs = [direction_angle_deg(canonicalize(V[:, i])[:3], vt_gt[:3]) for i in range(V.shape[1])]
costs = [worst_wall_normalized_cost(V[:, i], C0, C1, min_clearance_mm=0.0) for i in range(V.shape[1])]
dists = [centroid_distance(V[:, i], C) for i in range(V.shape[1])]

close_idx = np.where(np.array(angs) < 10.0)[0]
print(f"Number of draws within 10 deg of GT: {len(close_idx)}")
for idx in close_idx[:10]:
    print(f"  Draw {idx}: ang={angs[idx]:.2f} deg, d={dists[idx]:.2f} mm, cost={costs[idx]:.5f}")

cost_gt = worst_wall_normalized_cost(vt_gt, C0, C1, min_clearance_mm=0.0)
print(f"GT axis cost: {cost_gt:.5f}, d={centroid_distance(vt_gt, C):.2f}")
