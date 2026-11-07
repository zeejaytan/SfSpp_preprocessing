import os
import glob
import numpy as np

CORPUS = "/data/gpfs/projects/punim2657/sfs_main/original_samples/SfS_pp"
AXES313 = "/data/gpfs/projects/punim2657/SfSpp/runs/20261106-1316_fe906ab_t313a-axes/out/axes313"

def read_axis(path):
    lines = [l.strip().split() for l in open(path) if l.strip()]
    axes = []
    for l in lines:
        axes.append(np.r_[[float(x) for x in l[3:6]], [float(x) for x in l[:3]]])
    return np.column_stack(axes)

def canonicalize(vt):
    vt = np.asarray(vt, dtype=float).copy()
    if vt[2] < 0:
        vt[:3] = -vt[:3]
    return vt

def angle_deg(v1, v2):
    a1 = v1[:3] / np.linalg.norm(v1[:3])
    a2 = v2[:3] / np.linalg.norm(v2[:3])
    cos = np.clip(abs(float(np.dot(a1, a2))), 0.0, 1.0)
    return float(np.degrees(np.arccos(cos)))

files = sorted(glob.glob(f"{CORPUS}/Surfaces/Pot_E_Piece_*_Surface_0.xyz"))
print(f"Total Pot E pieces: {len(files)}")
for f in files:
    stem = os.path.basename(f)[:-len("_Surface_0.xyz")]
    s0 = np.loadtxt(f, usecols=range(6)).T
    s1 = np.loadtxt(f"{CORPUS}/Surfaces/{stem}_Surface_1.xyz", usecols=range(6)).T
    C = np.concatenate([s0, s1], axis=1)
    C_centroid = np.mean(C[:3, :], axis=1)

    gt_path = f"{CORPUS}/Ground Truth Axes/{stem}_Axis.xyz"
    if not os.path.isfile(gt_path):
        gt_path = f"{CORPUS}/Axes/{stem}_Axis.xyz"
    rel_path = f"{CORPUS}/Axes/{stem}_Axis.xyz"

    gt_ax = read_axis(gt_path)
    rel_ax = read_axis(rel_path)
    v_gt = canonicalize(gt_ax[:, 0])
    v_rel = canonicalize(rel_ax[:, 0])

    d_gt = np.linalg.norm(np.cross(C_centroid - v_gt[3:6], v_gt[:3]))
    
    # Check what axes313 generated
    ax313_path = f"{AXES313}/{stem}_Axis.xyz"
    if os.path.isfile(ax313_path):
        ax313 = read_axis(ax313_path)
        k_count = ax313.shape[1]
        top_v = canonicalize(ax313[:, 0])
        ang_top = angle_deg(top_v, v_gt)
        d_top = np.linalg.norm(np.cross(C_centroid - top_v[3:6], top_v[:3]))
        
        # also find min angle across all candidates in axes313
        min_ang = min(angle_deg(canonicalize(ax313[:, k]), v_gt) for k in range(k_count))
        # check mean axial normal for top_v
        a_top = top_v[:3]
        mean_ax = np.mean(np.abs(a_top @ C[3:6, :]))
    else:
        k_count = 0
        ang_top, d_top, min_ang, mean_ax = -1, -1, -1, -1

    p_num = stem.split("_")[-1]
    if int(p_num) in [3, 23, 24, 25, 26, 28, 31]:
        marker = " <--- FAILING IN 313"
    else:
        marker = ""
    print(f"{stem}: d_gt={d_gt:5.1f} | 313 K={k_count} top_ang={ang_top:5.1f} d_top={d_top:5.1f} mean_ax={mean_ax:.2f} min_ang={min_ang:5.1f}{marker}")
