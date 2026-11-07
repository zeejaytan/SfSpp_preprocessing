"""
render_assemblies.py -- Render reconstructed ceramic vessel assemblies before/after.

Usage:
    python render_assemblies.py --pot B --run-dir <DIR> --arm-left MOR1 --label-left "Author released (MO: 9/9)" \
                                --arm-right MMR1 --label-right "Ticket 313 (MM: 9/9)" --out potb_assembly.png
"""
import os
import sys
import argparse
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

CORPUS = "/data/gpfs/projects/punim2657/sfs_main/original_samples/SfS_pp"

PALETTE = [
    "#4e79a7", "#f28e2b", "#e15759", "#76b7b2", "#59a14f",
    "#edc948", "#b07aa1", "#ff9da7", "#9c755f", "#bab0ac",
    "#1f77b4", "#ff7f0e", "#2ca02c", "#d62728", "#9467bd",
    "#8c564b", "#e377c2", "#7f7f7f", "#bcbd22", "#17becf",
    "#393b79", "#5254a3", "#6b6ecf", "#9c9ede", "#637939",
    "#8ca252", "#b5cf6b", "#cedb9c", "#8c6d31", "#bd9e39",
    "#e7ba52", "#e7cb94", "#843c39", "#ad494a", "#d6616b"
]

def load_piece_points(pot, npieces, step=8):
    clouds = []
    for p in range(1, npieces + 1):
        pts = []
        for s in (0, 1):
            path = os.path.join(CORPUS, "Surfaces", f"Pot_{pot}_Piece_{p:02d}_Surface_{s}.xyz")
            if os.path.isfile(path):
                arr = np.loadtxt(path)
                if arr.ndim == 2 and arr.shape[1] >= 3:
                    pts.append(arr[::step, :3])
        if pts:
            clouds.append(np.vstack(pts))
        else:
            clouds.append(np.zeros((0, 3)))
    return clouds

def load_transforms(arm_dir, npieces):
    Ts = []
    for k in range(npieces):
        tpath = os.path.join(arm_dir, f"T_{k}to_{k}.txt")
        if os.path.isfile(tpath):
            T = np.loadtxt(tpath)
            Ts.append(T)
        else:
            Ts.append(np.eye(4))
    return Ts

def transform_pts(pts, T):
    if len(pts) == 0:
        return pts
    R, t = T[:3, :3], T[:3, 3]
    return pts @ R.T + t

def render_comparison(pot, run_dir, arm_left, label_left, arm_right, label_right, npieces, out_path, title=""):
    clouds = load_piece_points(pot, npieces)
    dir_left = os.path.join(run_dir, "out", arm_left)
    dir_right = os.path.join(run_dir, "out", arm_right)
    
    Ts_left = load_transforms(dir_left, npieces)
    Ts_right = load_transforms(dir_right, npieces)
    
    fig = plt.figure(figsize=(16, 12), dpi=160)
    
    views = [
        (90, 0, "Top View (along vessel axis)"),
        (20, 45, "Side / Perspective View")
    ]
    
    panels = [
        (arm_left, label_left, Ts_left, 0),
        (arm_right, label_right, Ts_right, 1)
    ]
    
    # Calculate global bounding box across both arms to use identical scale
    all_transformed = []
    for _, _, Ts, _ in panels:
        for k in range(npieces):
            if len(clouds[k]) > 0:
                all_transformed.append(transform_pts(clouds[k], Ts[k]))
    if all_transformed:
        big_pts = np.vstack(all_transformed)
        mid = 0.5 * (big_pts.max(axis=0) + big_pts.min(axis=0))
        span = 0.55 * (big_pts.max(axis=0) - big_pts.min(axis=0)).max()
    else:
        mid = np.zeros(3)
        span = 100.0

    for col_idx, (arm_name, arm_label, Ts, _) in enumerate(panels):
        for row_idx, (elev, azim, view_name) in enumerate(views):
            subplot_idx = row_idx * 2 + col_idx + 1
            ax = fig.add_subplot(2, 2, subplot_idx, projection="3d")
            
            for k in range(npieces):
                if len(clouds[k]) > 0:
                    q = transform_pts(clouds[k], Ts[k])
                    col = PALETTE[k % len(PALETTE)]
                    lbl = f"P{k+1:02d}" if (col_idx == 0 and row_idx == 0) else None
                    ax.scatter(q[:, 0], q[:, 1], q[:, 2], s=2.0, c=col, alpha=0.75, label=lbl)
            
            ax.set_xlim(mid[0] - span, mid[0] + span)
            ax.set_ylim(mid[1] - span, mid[1] + span)
            ax.set_zlim(mid[2] - span, mid[2] + span)
            ax.view_init(elev=elev, azim=azim)
            ax.set_title(f"{arm_label}\n{view_name}", fontsize=11, fontweight="bold")
            ax.set_xlabel("X (mm)", fontsize=9)
            ax.set_ylabel("Y (mm)", fontsize=9)
            ax.set_zlabel("Z (mm)", fontsize=9)
            
            if col_idx == 0 and row_idx == 0:
                ax.legend(loc="upper right", markerscale=2.5, fontsize=7, ncol=2)
                
    if title:
        fig.suptitle(title, fontsize=14, fontweight="bold", y=0.98)
    fig.tight_layout(rect=[0, 0, 1, 0.96])
    os.makedirs(os.path.dirname(os.path.abspath(out_path)), exist_ok=True)
    fig.savefig(out_path)
    plt.close(fig)
    print(f"Saved render to {out_path}")

def render_multi_k(pot, run_dir, arm_specs, npieces, out_path, title=""):
    """
    Renders multiple arms (e.g. MO, BASE, K1, K2, K3, K6) in a grid.
    arm_specs: list of tuples (arm_dir_name, display_label)
    """
    clouds = load_piece_points(pot, npieces, step=10)
    n_arms = len(arm_specs)
    
    fig = plt.figure(figsize=(5.5 * n_arms, 10), dpi=150)
    
    # Calculate bounding box
    all_transformed = []
    for arm_name, _ in arm_specs:
        Ts = load_transforms(os.path.join(run_dir, "out", arm_name), npieces)
        for k in range(npieces):
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
        (90, 0, "Top View (XY)"),
        (25, 45, "Perspective View")
    ]
    
    for c_idx, (arm_name, display_label) in enumerate(arm_specs):
        Ts = load_transforms(os.path.join(run_dir, "out", arm_name), npieces)
        for r_idx, (elev, azim, view_name) in enumerate(views):
            ax = fig.add_subplot(2, n_arms, r_idx * n_arms + c_idx + 1, projection="3d")
            for k in range(npieces):
                if len(clouds[k]) > 0:
                    q = transform_pts(clouds[k], Ts[k])
                    col = PALETTE[k % len(PALETTE)]
                    lbl = f"P{k+1:02d}" if (c_idx == 0 and r_idx == 0) else None
                    ax.scatter(q[:, 0], q[:, 1], q[:, 2], s=1.5, c=col, alpha=0.7, label=lbl)
            ax.set_xlim(mid[0] - span, mid[0] + span)
            ax.set_ylim(mid[1] - span, mid[1] + span)
            ax.set_zlim(mid[2] - span, mid[2] + span)
            ax.view_init(elev=elev, azim=azim)
            ax.set_title(f"{display_label}\n{view_name}", fontsize=10, fontweight="bold")
            ax.set_xlabel("X (mm)", fontsize=8)
            ax.set_ylabel("Y (mm)", fontsize=8)
            ax.set_zlabel("Z (mm)", fontsize=8)
            if c_idx == 0 and r_idx == 0 and npieces <= 10:
                ax.legend(loc="upper right", markerscale=2, fontsize=6)
                
    if title:
        fig.suptitle(title, fontsize=13, fontweight="bold", y=0.98)
    fig.tight_layout(rect=[0, 0, 1, 0.96])
    os.makedirs(os.path.dirname(os.path.abspath(out_path)), exist_ok=True)
    fig.savefig(out_path)
    plt.close(fig)
    print(f"Saved multi-arm render to {out_path}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", default="compare", choices=["compare", "multi"])
    parser.add_argument("--pot", required=True)
    parser.add_argument("--run-dir", required=True)
    parser.add_argument("--arm-left", default="MOR1")
    parser.add_argument("--label-left", default="Author Released (MO)")
    parser.add_argument("--arm-right", default="MMR1")
    parser.add_argument("--label-right", default="Normalized Axes (MM)")
    parser.add_argument("--npieces", type=int, required=True)
    parser.add_argument("--out", required=True)
    parser.add_argument("--title", default="")
    parser.add_argument("--multi-arms", nargs="*", help="List of arm_name:display_label")
    args = parser.parse_args()
    
    if args.mode == "compare":
        render_comparison(
            pot=args.pot,
            run_dir=args.run_dir,
            arm_left=args.arm_left,
            label_left=args.label_left,
            arm_right=args.arm_right,
            label_right=args.label_right,
            npieces=args.npieces,
            out_path=args.out,
            title=args.title
        )
    elif args.mode == "multi":
        specs = []
        for item in args.multi_arms:
            parts = item.split(":", 1)
            specs.append((parts[0], parts[1] if len(parts) > 1 else parts[0]))
        render_multi_k(
            pot=args.pot,
            run_dir=args.run_dir,
            arm_specs=specs,
            npieces=args.npieces,
            out_path=args.out,
            title=args.title
        )
