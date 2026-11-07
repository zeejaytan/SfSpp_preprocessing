import os, sys, numpy as np
CORPUS = "/data/gpfs/projects/punim2657/sfs_main/original_samples/SfS_pp"
sys.path.insert(0, "/data/gpfs/projects/punim2657/sfs_preprocessing/work_314")
from test_pipeline_clean_7pieces import run_clean_potsac
from sfs_axes.normalized import compute_normalized_residual
from sfs_axes.robust import apply_robustifier, robustifier_huber

stem = "Pot_E_Piece_03"
s0 = np.loadtxt(f"{CORPUS}/Surfaces/{stem}_Surface_0.xyz", usecols=range(6)).T
s1 = np.loadtxt(f"{CORPUS}/Surfaces/{stem}_Surface_1.xyz", usecols=range(6)).T

axes = run_clean_potsac(s0, s1, max_candidates=6)
for k in [0, 1, 2]:
    cand = axes[:, k]
    err0 = compute_normalized_residual(cand, s0)[0, :]
    err1 = compute_normalized_residual(cand, s1)[0, :]
    c0 = float(np.mean(apply_robustifier(robustifier_huber, err0, None)))
    c1 = float(np.mean(apply_robustifier(robustifier_huber, err1, None)))
    diff = abs(c0 - c1)
    ratio = max(c0, c1) / (min(c0, c1) + 1e-8)
    print(f"Rank {k}: c0={c0:.6f}, c1={c1:.6f}, worst={max(c0, c1):.6f}, diff={diff:.6f}, ratio={ratio:.2f}")
