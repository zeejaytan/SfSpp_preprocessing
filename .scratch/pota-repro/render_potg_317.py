"""
render_potg_317.py -- Render multi-arm assembly comparison for Ticket 317.
Compares:
1. MO Released Control (7/7 sherds, 10/10 joins)
2. axes315 K=3 (4/7 sherds, 1/10 joins - truncated conical axis)
3. axes315 K=6 (Stage A unconfound)
4. axes317 K=1 (Stage B - conical promoted to Rank 0)
5. axes317 K=2 (Stage B)
6. axes317 K=3 (Stage B)
"""
import os
import sys
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

CORPUS = "/data/gpfs/projects/punim2657/sfs_main/original_samples/SfS_pp"
NPIECES = 7
POT = "G"

PALETTE = [
    "#4e79a7", "#f28e2b", "#e15759", "#76b7b2", "#59a14f",
    "#edc948", "#b07aa1", "#ff9da7", "#9c755f", "#bab0ac"
]

def load_piece_points(step=6):
    clouds = []
    for p in range(1, NPIECES + 1):
        pts = []
        for s in (0, 1):
            path = os.path.join(CORPUS, "Surfaces", f"Pot_{POT}_Piece_{p:02d}_Surface_{s}.xyz")
            if os.path.isfile(path):
                arr = np.loadtxt(path)
                if arr.ndim == 2 and arr.shape[1] >= 3:
                    pts.append(arr[::step, :3])
        if pts:
            clouds.append(np.vstack(pts))
        else:
            clouds.append(np.zeros((0, 3)))
    return clouds

def load_transforms(arm_dir):
    Ts = []
    for k in range(NPIECES):
        tpath = os.path.join(arm_dir, f"T_{k}to_{k}.txt")
        if os.path.isfile(tpath):
            T = np.loadtxt(tpath)
            Ts.append(T)
        else:
            Ts.append(np.eye(4))
    return Ts

def load_acc_label(arm_dir, default_label):
    acc_path = os.path.join(arm_dir, "1. Acc.txt")
    if os.path.isfile(acc_path):
        try:
            with open(acc_path) as f:
                lines = [line.strip() for line in f if "Sherd accuracy" in line]
            if len(lines) >= 2:
                # e.g. "Sherd accuracy : 7 / 7 (100 %)" and "Sherd accuracy : 10 / 10 (100 %)"
                p_sherd = lines[0].split(":")[-1].strip().split("(")[0].strip()
                p_join = lines[1].split(":")[-1].strip().split("(")[0].strip()
                return f"{default_label}\n({p_sherd} sherds, {p_join} joins)"
        except Exception:
            pass
    return default_label

def transform_pts(pts, T):
    if len(pts) == 0:
        return pts
    R, t = T[:3, :3], T[:3, 3]
    return pts @ R.T + t

def main():
    out_path = sys.argv[1] if len(sys.argv) > 1 else "/tmp/potg_kladder_assembly.png"

    arms = [
        ("MO Control", "/data/gpfs/projects/punim2657/SfSpp/runs/20261108-0958_5044a41_t317b-kladder-G/out/G_MOR1"),
        ("axes315 K=3", "/data/gpfs/projects/punim2657/SfSpp/runs/20261108-0430_c1fed82_t315c-potg/out/MMR1"),
        ("axes315 K=6", "/data/gpfs/projects/punim2657/SfSpp/runs/20261108-0931_5044a41_t317a-potg-315k6/out/MMR1"),
        ("axes317 K=1", "/data/gpfs/projects/punim2657/SfSpp/runs/20261108-0958_5044a41_t317b-kladder-G/out/G_K1R1"),
        ("axes317 K=2", "/data/gpfs/projects/punim2657/SfSpp/runs/20261108-0958_5044a41_t317b-kladder-G/out/G_K2R1"),
        ("axes317 K=3", "/data/gpfs/projects/punim2657/SfSpp/runs/20261108-0958_5044a41_t317b-kladder-G/out/G_K3R1"),
    ]

    clouds = load_piece_points(step=6)
    n_arms = len(arms)

    # Compute unified bounding box across all arms
    all_transformed = []
    for label, arm_dir in arms:
        if os.path.isdir(arm_dir):
            Ts = load_transforms(arm_dir)
            for k in range(NPIECES):
                if len(clouds[k]) > 0:
                    all_transformed.append(transform_pts(clouds[k], Ts[k]))

    if all_transformed:
        big_pts = np.vstack(all_transformed)
        mid = 0.5 * (big_pts.max(axis=0) + big_pts.min(axis=0))
        span = 0.55 * (big_pts.max(axis=0) - big_pts.min(axis=0)).max()
    else:
        mid = np.zeros(3)
        span = 100.0

    views = [
        (90, 0, "Top View (along vessel axis)"),
        (25, 45, "Perspective View")
    ]

    fig = plt.figure(figsize=(4.8 * n_arms, 9.5), dpi=160)

    for c_idx, (default_lbl, arm_dir) in enumerate(arms):
        full_lbl = load_acc_label(arm_dir, default_lbl) if os.path.isdir(arm_dir) else f"{default_lbl}\n(missing)"
        Ts = load_transforms(arm_dir) if os.path.isdir(arm_dir) else [np.eye(4)] * NPIECES

        for r_idx, (elev, azim, view_name) in enumerate(views):
            ax = fig.add_subplot(2, n_arms, r_idx * n_arms + c_idx + 1, projection="3d")
            for k in range(NPIECES):
                if len(clouds[k]) > 0:
                    q = transform_pts(clouds[k], Ts[k])
                    col = PALETTE[k % len(PALETTE)]
                    lbl = f"P{k+1:02d}" if (c_idx == 0 and r_idx == 0) else None
                    ax.scatter(q[:, 0], q[:, 1], q[:, 2], s=1.2, c=col, alpha=0.75, label=lbl)

            ax.set_xlim(mid[0] - span, mid[0] + span)
            ax.set_ylim(mid[1] - span, mid[1] + span)
            ax.set_zlim(mid[2] - span, mid[2] + span)
            ax.view_init(elev=elev, azim=azim)
            ax.set_title(f"{full_lbl}\n{view_name}", fontsize=10, fontweight="bold")
            ax.set_xlabel("X (mm)", fontsize=8)
            ax.set_ylabel("Y (mm)", fontsize=8)
            ax.set_zlabel("Z (mm)", fontsize=8)
            if c_idx == 0 and r_idx == 0:
                ax.legend(loc="upper right", markerscale=2.5, fontsize=7, ncol=2)

    fig.suptitle(
        "Pot G (Conical Bowl, 7 pieces): Reassembly Under Normalized Axes Ladder\n"
        "Unconfounding axes315 (truncated conical axis) vs axes317 (true conical axis promoted to Rank 0 / K=1)",
        fontsize=13, fontweight="bold", y=0.98
    )
    fig.tight_layout(rect=[0, 0, 1, 0.95])
    os.makedirs(os.path.dirname(os.path.abspath(out_path)), exist_ok=True)
    fig.savefig(out_path)
    plt.close(fig)
    print(f"Saved render to {out_path}")

if __name__ == "__main__":
    main()
