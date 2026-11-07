import os, sys, numpy as np
sys.path.insert(0, "/data/gpfs/projects/punim2657/sfs_preprocessing/work_314")
CORPUS = "/data/gpfs/projects/punim2657/sfs_main/original_samples/SfS_pp"

from sfs_axes.potsac import run_potsac_union
from sfs_axes.normalized import centroid_distance
from sfs_axes.io_axes import read_axes, direction_angle_deg

def canonicalize(vt):
    vt = np.asarray(vt, dtype=float).copy()
    if vt[2] < 0: vt[:3] = -vt[:3]
    return vt

failing = [3, 23, 24, 25, 26, 28, 31]

print("=== VERIFYING CLEAN POTSAC ON 7 FAILING PIECES OF POT E ===")
all_pass_top2 = True
for p in failing:
    stem = f"Pot_E_Piece_{p:02d}"
    s0 = np.loadtxt(f"{CORPUS}/Surfaces/{stem}_Surface_0.xyz", usecols=range(6)).T
    s1 = np.loadtxt(f"{CORPUS}/Surfaces/{stem}_Surface_1.xyz", usecols=range(6)).T
    C = np.concatenate([s0, s1], axis=1)

    rel_ax = read_axes(f"{CORPUS}/Axes/{stem}_Axis.xyz")
    gt_path = f"{CORPUS}/Ground Truth Axes/{stem}_Axis.xyz"
    gt_ax = read_axes(gt_path) if os.path.isfile(gt_path) else rel_ax
    v_gt = canonicalize(gt_ax[:, 0])

    # Run potsac union
    axes = run_potsac_union(s0, s1, max_candidates=6, normalized=True)

    print(f"\nPiece {p:02d}: returned {axes.shape[1]} lines")
    min_top2 = 999.0
    for k in range(axes.shape[1]):
        cand = axes[:, k]
        d = centroid_distance(cand, C)
        a = cand[:3] / np.linalg.norm(cand[:3])
        mean_ax = np.mean(np.abs(a @ C[3:6, :]))

        min_ang = direction_angle_deg(cand[:3], v_gt[:3])
        for r_idx in range(rel_ax.shape[1]):
            v_rel_k = canonicalize(rel_ax[:, r_idx])
            ang_k = direction_angle_deg(cand[:3], v_rel_k[:3])
            if ang_k < min_ang: min_ang = ang_k

        if k < 2 and min_ang < min_top2:
            min_top2 = min_ang

        status = "TRUE (<10deg)" if min_ang <= 10.0 else "DECOY"
        print(f"  Rank {k}: ang={min_ang:5.2f}deg | d={d:5.1f}mm | mean_ax={mean_ax:.3f} [{status}]")

    passed = min_top2 <= 10.0
    if not passed: all_pass_top2 = False
    print(f"--> Piece {p:02d} Top 2 Status: {'PASS' if passed else 'FAIL'} (best top2: {min_top2:.2f}deg)")

print(f"\n=======================================================")
print(f"ALL 7 PIECES PASS TOP 2 (<10 deg)? = {all_pass_top2}")
print(f"=======================================================")
