import glob, os, sys, numpy as np
CORPUS = "/data/gpfs/projects/punim2657/sfs_main/original_samples/SfS_pp"
sys.path.insert(0, "/data/gpfs/projects/punim2657/sfs_preprocessing/work_314")
from sfs_axes.io_axes import read_axes
from sfs_axes.potsac import patch_gap_deg

true_bases = [
    ("Pot_A_Piece_01", 0),
    ("Pot_B_Piece_01", 0),
    ("Pot_C_Piece_03", 0),
    ("Pot_D_Piece_22", 0),
    ("Pot_D_Piece_28", 1),
    ("Pot_D_Piece_29", 0),
    ("Pot_D_Piece_30", 0),
    ("Pot_D_Piece_31", 0),
    ("Pot_D_Piece_32", 0),
    ("Pot_G_Piece_07", 0),
    ("Pot_I_Piece_25", 0),
    ("Pot_I_Piece_29", 0),
    ("Pot_I_Piece_30", 0),
    ("Pot_E_Piece_34", 2),
]

print("=== TRUE BASE PIECES ===")
for stem, line_idx in true_bases:
    s0 = np.loadtxt(f"{CORPUS}/Surfaces/{stem}_Surface_0.xyz", usecols=range(6)).T
    s1 = np.loadtxt(f"{CORPUS}/Surfaces/{stem}_Surface_1.xyz", usecols=range(6)).T
    C = np.concatenate([s0, s1], axis=1)
    axes = read_axes(f"{CORPUS}/Axes/{stem}_Axis.xyz")
    vt = axes[:, line_idx]
    gap = patch_gap_deg(vt, C)
    span = 360.0 - gap
    print(f"{stem} line {line_idx}: gap={gap:.1f}deg, span={span:.1f}deg")

print("\n=== PERPENDICULAR DECOYS ON POT E WALL PIECES ===")
AXES313 = "/data/gpfs/projects/punim2657/SfSpp/runs/20261106-1316_fe906ab_t313a-axes/out/axes313"
for p in [3, 23, 24, 25, 26, 28, 31]:
    stem = f"Pot_E_Piece_{p:02d}"
    s0 = np.loadtxt(f"{CORPUS}/Surfaces/{stem}_Surface_0.xyz", usecols=range(6)).T
    s1 = np.loadtxt(f"{CORPUS}/Surfaces/{stem}_Surface_1.xyz", usecols=range(6)).T
    C = np.concatenate([s0, s1], axis=1)
    ax_p = f"{AXES313}/{stem}_Axis.xyz"
    if not os.path.exists(ax_p): continue
    axes = read_axes(ax_p)
    c_pt = C[:3].mean(axis=1)
    for k in range(axes.shape[1]):
        vt = axes[:, k]
        a = vt[:3] / np.linalg.norm(vt[:3])
        d = np.linalg.norm(np.cross(c_pt - vt[3:6], a))
        if d < 25.0:
            gap = patch_gap_deg(vt, C)
            span = 360.0 - gap
            mean_ax = np.mean(np.abs(a @ C[3:6, :]))
            print(f"{stem} decoy {k} (d={d:.1f}mm): gap={gap:.1f}deg, span={span:.1f}deg, mean_ax={mean_ax:.3f}")
