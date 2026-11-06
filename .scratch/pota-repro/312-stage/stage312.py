#!/usr/bin/env python3
"""stage312.py -- Ticket 312: Reverse engineer author axis extraction.
Steps 2 to 5:
- Step 2: Energy Landscape & Lever-Arm Centroid Bias Audit (34 Pot E pieces + 1D geodesic profiles on 10 failing pieces)
- Step 3: Input Cloud Perturbations & Surface Provenance (mesh normals, breakline trimming, single-wall, dense mesh)
- Step 4: Objective Refinements & Missing Constraints (polynomial profile consistency V_poly, distance-invariant normal loss, rim constraint)
- Step 5: Benchmark-Wide Reference vs Ground Truth Audit (all 163 pieces across Pots A-K)
"""

import argparse
import glob
import json
import math
import os
import sys
import time
from multiprocessing import Pool

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D  # noqa: F401
import numpy as np
from scipy.optimize import least_squares, minimize
from scipy.spatial import cKDTree

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, ".."))
sys.path.insert(0, os.path.join(HERE, "work"))

from sfs_axes.cao import compute_biaxial_cao_error
from sfs_axes.io_axes import direction_angle_deg, read_axes, split_axis, write_axes
from sfs_axes.potsac import refine_axis
from sfs_axes.robust import apply_robustifier, robustifier_huber

FAILING_PIECES_POT_E = [3, 9, 23, 24, 25, 26, 27, 28, 29, 31]


def unit(v):
    v = np.asarray(v[:3], dtype=float)
    n = np.linalg.norm(v)
    return v / n if n > 1e-12 else v


def load_surface(path):
    """Load xyz + nx ny nz (6 columns)."""
    a = np.loadtxt(path, usecols=(0, 1, 2, 3, 4, 5), ndmin=2)
    return np.asarray(a, dtype=float).T  # (6, N)


def load_pcd_xyz(path):
    """Load x y z from ascii or simple PCD."""
    pts = []
    if not os.path.exists(path):
        return np.zeros((3, 0), dtype=float)
    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        in_data = False
        for line in f:
            line = line.strip()
            if not line:
                continue
            if not in_data:
                if line.startswith("DATA ascii"):
                    in_data = True
                continue
            parts = line.split()
            if len(parts) >= 3:
                try:
                    pts.append([float(parts[0]), float(parts[1]), float(parts[2])])
                except ValueError:
                    pass
    if not pts:
        return np.zeros((3, 0), dtype=float)
    return np.array(pts, dtype=float).T  # (3, N)


def hub_cost(vt, X):
    """Mean Huber cost per point on cloud X (6, N)."""
    err = np.atleast_1d(compute_biaxial_cao_error(vt, X))
    return float(np.sum(apply_robustifier(robustifier_huber, err))) / max(X.shape[1], 1)


def point_to_line_dist(pt, line_dir, line_pos):
    """Orthogonal distance from 3D point pt to 3D line (line_pos, line_dir)."""
    pt = np.asarray(pt, dtype=float).reshape(3)
    d = unit(line_dir)
    p0 = np.asarray(line_pos, dtype=float).reshape(3)
    diff = pt - p0
    proj = diff - (diff @ d) * d
    return float(np.linalg.norm(proj))


def slerp_direction(d1, d2, t):
    """Slerp between two unit directions d1 and d2."""
    d1 = unit(d1)
    d2 = unit(d2)
    if d1 @ d2 < 0:
        d2 = -d2
    dot = np.clip(d1 @ d2, -1.0, 1.0)
    theta = np.arccos(dot)
    if theta < 1e-6:
        return d1
    st = np.sin(theta)
    return unit((np.sin((1 - t) * theta) / st) * d1 + (np.sin(t * theta) / st) * d2)


def interp_line(d1, p1, d2, p2, t, ref_pt=None):
    """Geodesic interpolation between two 3D lines at parameter t in [0, 1]."""
    d1 = unit(d1)
    d2 = unit(d2)
    if d1 @ d2 < 0:
        d2 = -d2
    d_t = slerp_direction(d1, d2, t)
    
    if ref_pt is not None:
        p1_proj = p1 + ((ref_pt - p1) @ d1) * d1
        p2_proj = p2 + ((ref_pt - p2) @ d2) * d2
    else:
        p1_proj = p1
        p2_proj = p2
    p_t = (1 - t) * p1_proj + t * p2_proj
    if ref_pt is not None:
        p_t = p_t - ((p_t - ref_pt) @ d_t) * d_t
    else:
        p_t = p_t - (p_t @ d_t) * d_t
    return d_t, p_t


def fit_cylindrical_polynomial_profile(d, p0, X, degree=3):
    """Transform points to cylindrical (r, z) around line (p0, d) and fit polynomial r(z)."""
    d = unit(d)
    pts = X[:3, :].T  # (N, 3)
    rel = pts - p0.reshape(1, 3)
    z = rel @ d  # (N,)
    rad_vec = rel - np.outer(z, d)
    r = np.linalg.norm(rad_vec, axis=1)  # (N,)
    
    z_min, z_max = z.min(), z.max()
    z_span = max(z_max - z_min, 1e-6)
    z_norm = 2.0 * (z - z_min) / z_span - 1.0
    
    V = np.vander(z_norm, degree + 1)
    c, residuals, rank, s = np.linalg.lstsq(V, r, rcond=None)
    pred_r = V @ c
    res = r - pred_r
    huber_res = float(np.sum(apply_robustifier(robustifier_huber, res))) / len(res)
    mse = float(np.mean(res ** 2))
    return huber_res, mse, c, z, r, pred_r


def distance_invariant_normal_loss(d, p0, X):
    """Decoupled normal alignment loss (Cao error divided by radial distance)."""
    d = unit(d)
    pts = X[:3, :].T  # (N, 3)
    normals = X[3:6, :].T  # (N, 3)
    rel = pts - p0.reshape(1, 3)
    z = rel @ d
    rad_vec = rel - np.outer(z, d)
    r = np.linalg.norm(rad_vec, axis=1)
    r_safe = np.maximum(r, 1e-4)
    
    n_cross_a = np.cross(normals, d.reshape(1, 3))
    raw_err = np.sum(rel * n_cross_a, axis=1)
    norm_err = raw_err / r_safe
    huber_loss = float(np.sum(apply_robustifier(robustifier_huber, norm_err))) / len(norm_err)
    return huber_loss


def render_pot_e_vessel_3d(args):
    """Renders 3D view of Pot E with GT vessel axis, released axes, and Huber false minima."""
    print("Generating 3D vessel render of Pot E with candidate axes...", flush=True)
    all_vessel_pts = []
    rel_axes_vessel = []
    min_axes_vessel = []
    
    for piece in range(1, 32):
        stem = f"Pot_E_Piece_{piece:02d}"
        t_path = os.path.join(args.corp, "Ground Truth", f"Pot_E_Piece_{piece}_T.txt")
        if not os.path.exists(t_path):
            t_path = os.path.join(args.corp, "Ground Truth", f"Pot_E_Piece_{piece:02d}_T.txt")
        if not os.path.exists(t_path):
            continue
        T = np.loadtxt(t_path)
        R = T[:3, :3]
        t = T[:3, 3]
        
        # Load surface points (subsampled for rendering)
        s0_path = os.path.join(args.corp, "Surfaces", f"{stem}_Surface_0.xyz")
        if os.path.exists(s0_path):
            C0 = load_surface(s0_path)
            pts = C0[:3, ::20]  # subsample
            pts_vessel = (R @ pts) + t.reshape(3, 1)
            all_vessel_pts.append(pts_vessel)
            
        # Transform released axis
        rel_path = os.path.join(args.corp, "Axes", f"{stem}_Axis.xyz")
        if os.path.exists(rel_path):
            vt = read_axes(rel_path)[:, 0]
            d, p = split_axis(vt)
            d_v = R @ unit(d)
            p_v = R @ p + t
            rel_axes_vessel.append((piece, d_v, p_v))
            
        # Transform Huber min axis (if failing piece)
        if piece in FAILING_PIECES_POT_E:
            ax310_path = os.path.join(args.ax310, f"{stem}_Axis.xyz")
            if os.path.exists(ax310_path):
                vt = read_axes(ax310_path)[:, 0]
                d, p = split_axis(vt)
                d_v = R @ unit(d)
                p_v = R @ p + t
                min_axes_vessel.append((piece, d_v, p_v))
                
    if not all_vessel_pts:
        return
        
    vessel_pts = np.hstack(all_vessel_pts)
    z_min, z_max = vessel_pts[2, :].min(), vessel_pts[2, :].max()
    
    # 3D Side View
    fig = plt.figure(figsize=(12, 10))
    ax = fig.add_subplot(111, projection="3d")
    ax.scatter(vessel_pts[0, ::2], vessel_pts[1, ::2], vessel_pts[2, ::2], s=0.3, c="silver", alpha=0.15, label="Pot E Sherds")
    
    # Plot GT vessel axis (Z-axis at origin)
    z_line = np.linspace(z_min - 20, z_max + 20, 100)
    ax.plot(np.zeros_like(z_line), np.zeros_like(z_line), z_line, "k-", lw=4, label="Ground Truth Vessel Axis")
    
    # Plot Released axes (in green)
    for p_id, d_v, p_v in rel_axes_vessel:
        p_proj = p_v - ((p_v[2]) / d_v[2]) * d_v if abs(d_v[2]) > 1e-4 else p_v
        pts_line = p_proj.reshape(3, 1) + d_v.reshape(3, 1) * np.linspace(-100, 100, 50)
        ax.plot(pts_line[0], pts_line[1], pts_line[2], color="forestgreen", lw=1.2, alpha=0.6)
    ax.plot([], [], [], color="forestgreen", lw=2, label="Authors' Released Axes (31 pieces, Concordant)")
    
    # Plot Huber false minima axes for failing pieces (in red)
    for p_id, d_v, p_v in min_axes_vessel:
        pts_line = p_v.reshape(3, 1) + d_v.reshape(3, 1) * np.linspace(-80, 80, 50)
        ax.plot(pts_line[0], pts_line[1], pts_line[2], color="crimson", lw=2.5, alpha=0.85)
    ax.plot([], [], [], color="crimson", lw=2.5, label="Huber Minima on Failing Pieces (Centroid-Hugging Basins)")
    
    ax.set_title("Pot E: Vessel Reassembly with Candidate Symmetry Axes\nCentroid-Hugging Huber False Minima vs Ground Truth Central Axis", fontsize=13)
    ax.set_xlabel("X (mm)")
    ax.set_ylabel("Y (mm)")
    ax.set_zlabel("Z (mm)")
    ax.legend(loc="upper right", framealpha=0.9)
    ax.view_init(elev=20, azim=45)
    
    render_path = os.path.join(args.out, "renders", "pot_e_vessel_axes_3d.png")
    fig.tight_layout()
    fig.savefig(render_path, dpi=150)
    plt.close(fig)
    print(f"-> Saved {render_path}", flush=True)
    
    # Top-Down View (XY plane projection)
    fig2, ax2 = plt.subplots(figsize=(8, 8))
    ax2.scatter(vessel_pts[0, ::2], vessel_pts[1, ::2], s=0.5, c="lightgray", alpha=0.3, label="Vessel Profile (Top View)")
    ax2.plot(0, 0, "k+", markersize=16, markeredgewidth=3, label="GT Vessel Center (0, 0)")
    
    for p_id, d_v, p_v in rel_axes_vessel:
        pts_line = p_v.reshape(3, 1) + d_v.reshape(3, 1) * np.linspace(-60, 60, 30)
        ax2.plot(pts_line[0], pts_line[1], color="forestgreen", lw=1, alpha=0.5)
    ax2.plot([], [], color="forestgreen", lw=1.5, label="Authors' Released Axes")
    
    for p_id, d_v, p_v in min_axes_vessel:
        pts_line = p_v.reshape(3, 1) + d_v.reshape(3, 1) * np.linspace(-60, 60, 30)
        ax2.plot(pts_line[0], pts_line[1], color="crimson", lw=2.2, alpha=0.85)
        ax2.scatter(p_v[0], p_v[1], color="crimson", s=30)
    ax2.plot([], [], color="crimson", lw=2.2, label="Huber False Minima (Passing Through Sherds)")
    
    ax2.set_xlabel("X (mm)")
    ax2.set_ylabel("Y (mm)")
    ax2.set_title("Pot E (Top-Down XY View): Centroid Proximity Bias\nHuber Minimizer Passes Through Sherds Near Outer Wall (~120mm from Center)", fontsize=11)
    ax2.grid(True, alpha=0.3)
    ax2.axis("equal")
    ax2.legend(loc="upper right", framealpha=0.9)
    
    render_top_path = os.path.join(args.out, "renders", "pot_e_vessel_axes_topdown.png")
    fig2.tight_layout()
    fig2.savefig(render_top_path, dpi=150)
    plt.close(fig2)
    print(f"-> Saved {render_top_path}", flush=True)


def run_step2(args):
    """Step 2: Energy Landscape & Lever-Arm Centroid Bias Audit."""
    print("=== Step 2: Energy Landscape & Lever-Arm Centroid Bias Audit ===", flush=True)
    out_dir = args.out
    renders_dir = os.path.join(out_dir, "renders")
    os.makedirs(renders_dir, exist_ok=True)
    
    rows = []
    geodesic_rows = []
    
    for piece in range(1, 35):
        stem = f"Pot_E_Piece_{piece:02d}"
        s0_path = os.path.join(args.corp, "Surfaces", f"{stem}_Surface_0.xyz")
        s1_path = os.path.join(args.corp, "Surfaces", f"{stem}_Surface_1.xyz")
        if not (os.path.exists(s0_path) and os.path.exists(s1_path)):
            continue
            
        C0 = load_surface(s0_path)
        C1 = load_surface(s1_path)
        C_all = np.hstack([C0, C1])
        pts = C_all[:3, :].T
        centroid = np.mean(pts, axis=0)
        
        # Bounding box
        bbox_min = pts.min(axis=0)
        bbox_max = pts.max(axis=0)
        bbox_dim = bbox_max - bbox_min
        bbox_diag = float(np.linalg.norm(bbox_dim))
        
        # Authors' released axis
        rel_path = os.path.join(args.corp, "Axes", f"{stem}_Axis.xyz")
        has_rel = os.path.exists(rel_path)
        if has_rel:
            vt_rel = read_axes(rel_path)
            d_rel, p_rel = split_axis(vt_rel[:, 0])
            d_rel = unit(d_rel)
            lever_arm_rel = point_to_line_dist(centroid, d_rel, p_rel)
            cost_rel = hub_cost(vt_rel[:, 0], C_all)
        else:
            d_rel, p_rel = np.array([0, 0, 1]), centroid
            lever_arm_rel = float("nan")
            cost_rel = float("nan")
            
        # Ground Truth axis (1..31)
        gt_path = os.path.join(args.corp, "Ground Truth Axes", f"{stem}_Axis.xyz")
        has_gt = os.path.exists(gt_path)
        if has_gt:
            vt_gt = read_axes(gt_path)
            d_gt, p_gt = split_axis(vt_gt[:, 0])
            d_gt = unit(d_gt)
            lever_arm_gt = point_to_line_dist(centroid, d_gt, p_gt)
            cost_gt = hub_cost(vt_gt[:, 0], C_all)
            ang_rel_gt = direction_angle_deg(d_rel, d_gt)
        else:
            d_gt, p_gt = None, None
            lever_arm_gt = float("nan")
            cost_gt = float("nan")
            ang_rel_gt = float("nan")
            
        # Our Huber rank-1 line from axes310
        ax310_path = os.path.join(args.ax310, f"{stem}_Axis.xyz")
        has_310 = os.path.exists(ax310_path)
        if has_310:
            vt_310 = read_axes(ax310_path)
            d_310, p_310 = split_axis(vt_310[:, 0])
            d_310 = unit(d_310)
            lever_arm_min = point_to_line_dist(centroid, d_310, p_310)
            cost_min = hub_cost(vt_310[:, 0], C_all)
            ang_min_rel = direction_angle_deg(d_310, d_rel)
            ang_min_gt = direction_angle_deg(d_310, d_gt) if has_gt else float("nan")
        else:
            d_310, p_310 = None, None
            lever_arm_min = float("nan")
            cost_min = float("nan")
            ang_min_rel = float("nan")
            ang_min_gt = float("nan")
            
        ratio_min_rel = lever_arm_min / lever_arm_rel if lever_arm_rel > 0 else float("nan")
        ratio_min_gt = lever_arm_min / lever_arm_gt if (has_gt and lever_arm_gt > 0) else float("nan")
        
        is_failing = piece in FAILING_PIECES_POT_E
        status_group = "failing_10" if is_failing else ("passing_21" if piece <= 31 else "extra_3")
        
        row = dict(
            piece=piece, stem=stem, group=status_group, n_pts=C_all.shape[1],
            bbox_x_mm=round(float(bbox_dim[0]), 2), bbox_y_mm=round(float(bbox_dim[1]), 2), bbox_z_mm=round(float(bbox_dim[2]), 2),
            bbox_diag_mm=round(bbox_diag, 2),
            lever_arm_rel_mm=round(lever_arm_rel, 3),
            lever_arm_gt_mm=round(lever_arm_gt, 3) if has_gt else "NA",
            lever_arm_min_mm=round(lever_arm_min, 3),
            ratio_min_vs_rel=round(ratio_min_rel, 4),
            ratio_min_vs_gt=round(ratio_min_gt, 4) if has_gt else "NA",
            cost_rel=round(cost_rel, 3), cost_gt=round(cost_gt, 3) if has_gt else "NA", cost_min=round(cost_min, 3),
            ang_min_rel_deg=round(ang_min_rel, 3), ang_rel_gt_deg=round(ang_rel_gt, 3) if has_gt else "NA",
            ang_min_gt_deg=round(ang_min_gt, 3) if has_gt else "NA"
        )
        rows.append(row)
        
        # Geodesic profile for failing pieces
        if is_failing and has_rel and has_310:
            ts = np.linspace(0.0, 1.0, 101)
            t_costs = []
            t_worst = []
            t_arms = []
            t_angs = []
            
            for t_val in ts:
                d_t, p_t = interp_line(d_rel, p_rel, d_310, p_310, t_val, ref_pt=centroid)
                vt_t = np.r_[d_t, p_t]
                c0_t = hub_cost(vt_t, C0)
                c1_t = hub_cost(vt_t, C1)
                call_t = hub_cost(vt_t, C_all)
                arm_t = point_to_line_dist(centroid, d_t, p_t)
                ang_t = direction_angle_deg(d_t, d_rel)
                
                t_costs.append(call_t)
                t_worst.append(max(c0_t, c1_t))
                t_arms.append(arm_t)
                t_angs.append(ang_t)
                
                geodesic_rows.append(dict(
                    piece=piece, stem=stem, t=round(float(t_val), 3),
                    ang_deg=round(float(ang_t), 3),
                    lever_arm_mm=round(float(arm_t), 3),
                    cost_all=round(float(call_t), 4),
                    cost_worst=round(float(t_worst[-1]), 4)
                ))
                
            # Plot geodesic profile
            fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(8, 6), sharex=True)
            ax1.plot(ts, t_costs, "b-", lw=2, label="Huber Loss $E_{all}$")
            ax1.plot(ts, t_worst, "r--", lw=1.5, label="Worst Wall Loss")
            ax1.set_ylabel("Loss per point")
            ax1.set_title(f"{stem} (Loss vs Path from Released Axis to Huber Min)")
            ax1.grid(True, alpha=0.3)
            ax1.legend(loc="upper right")
            
            ax2.plot(ts, t_arms, "g-", lw=2, label="Lever-arm $d(C, L)$ (mm)")
            ax2.set_xlabel("Geodesic step $t$ ($0 = L_{rel}, 1 = L_{min}$)")
            ax2.set_ylabel("Lever arm to centroid (mm)")
            ax2.grid(True, alpha=0.3)
            ax2.legend(loc="upper right")
            
            plot_path = os.path.join(renders_dir, f"step2_profile_{stem}.png")
            fig.tight_layout()
            fig.savefig(plot_path, dpi=120)
            plt.close(fig)
            
    # Write step2_lever_arm.tsv
    cols = [
        "piece", "stem", "group", "n_pts", "bbox_x_mm", "bbox_y_mm", "bbox_z_mm", "bbox_diag_mm",
        "lever_arm_rel_mm", "lever_arm_gt_mm", "lever_arm_min_mm",
        "ratio_min_vs_rel", "ratio_min_vs_gt",
        "cost_rel", "cost_gt", "cost_min",
        "ang_min_rel_deg", "ang_rel_gt_deg", "ang_min_gt_deg"
    ]
    step2_tsv = os.path.join(out_dir, "step2_lever_arm.tsv")
    with open(step2_tsv, "w", encoding="utf-8") as f:
        f.write("\t".join(cols) + "\n")
        for r in rows:
            f.write("\t".join(str(r[c]) for c in cols) + "\n")
    print(f"-> Saved {step2_tsv}", flush=True)
    
    # Write step2_geodesic_profiles.tsv
    geo_cols = ["piece", "stem", "t", "ang_deg", "lever_arm_mm", "cost_all", "cost_worst"]
    geo_tsv = os.path.join(out_dir, "step2_geodesic_profiles.tsv")
    with open(geo_tsv, "w", encoding="utf-8") as f:
        f.write("\t".join(geo_cols) + "\n")
        for r in geodesic_rows:
            f.write("\t".join(str(r[c]) for c in geo_cols) + "\n")
    print(f"-> Saved {geo_tsv}", flush=True)
    
    # Render 3D vessel view
    render_pot_e_vessel_3d(args)


def run_step3_single_piece(piece, args):
    """Step 3 analysis for a single failing Pot E piece."""
    stem = f"Pot_E_Piece_{piece:02d}"
    s0_path = os.path.join(args.corp, "Surfaces", f"{stem}_Surface_0.xyz")
    s1_path = os.path.join(args.corp, "Surfaces", f"{stem}_Surface_1.xyz")
    mesh_path = os.path.join(args.corp, "Mesh", f"{stem}_Mesh_DS.obj")
    bl0_path = os.path.join(args.corp, "Breaklines", f"{stem}_Breakline_0.pcd")
    bl1_path = os.path.join(args.corp, "Breaklines", f"{stem}_Breakline_1.pcd")
    rel_path = os.path.join(args.corp, "Axes", f"{stem}_Axis.xyz")
    ax310_path = os.path.join(args.ax310, f"{stem}_Axis.xyz")
    
    C0 = load_surface(s0_path)
    C1 = load_surface(s1_path)
    C_all = np.hstack([C0, C1])
    
    vt_rel = read_axes(rel_path)[:, 0]
    vt_min = read_axes(ax310_path)[:, 0]
    d_rel, p_rel = split_axis(vt_rel)
    
    results = []
    
    # Baseline shipped
    c_rel_base = hub_cost(vt_rel, C_all)
    c_min_base = hub_cost(vt_min, C_all)
    vt_lm_base = refine_axis(vt_rel.copy(), C_all, method=2, max_iters=300, tolerance=1e-9)
    drift_base = direction_angle_deg(vt_lm_base[:3], d_rel)
    results.append(dict(
        piece=piece, stem=stem, perturbation="shipped_baseline", param="none",
        n_pts=C_all.shape[1], cost_rel=round(c_rel_base, 3), cost_min=round(c_min_base, 3),
        drift_lm_deg=round(drift_base, 3), ang_conv_to_min=round(direction_angle_deg(vt_lm_base[:3], vt_min[:3]), 3)
    ))
    
    # 1. Mesh Recomputed Normals (PCA and Quadric)
    import trimesh
    mesh = trimesh.load(mesh_path, process=False)
    mesh_v = np.asarray(mesh.vertices, dtype=float)
    kdtree_mesh = cKDTree(mesh_v)
    
    pts_all = C_all[:3, :].T
    
    for r in [1.0, 2.0, 5.0]:
        # PCA normals on C_all points using mesh vertices
        pca_normals = []
        for pt in pts_all:
            idx = kdtree_mesh.query_ball_point(pt, r)
            if len(idx) < 3:
                pca_normals.append(pt / np.linalg.norm(pt))
                continue
            nbrs = mesh_v[idx]
            cov = np.cov(nbrs, rowvar=False)
            evals, evecs = np.linalg.eigh(cov)
            n_pca = evecs[:, 0]  # smallest variance direction
            pca_normals.append(n_pca)
        pca_normals = np.array(pca_normals).T  # (3, N)
        dots = np.sum(pca_normals * C_all[3:6, :], axis=0)
        pca_normals[:, dots < 0] *= -1.0
        
        C_pca = C_all.copy()
        C_pca[3:6, :] = pca_normals
        
        c_rel_pca = hub_cost(vt_rel, C_pca)
        c_min_pca = hub_cost(vt_min, C_pca)
        vt_lm_pca = refine_axis(vt_rel.copy(), C_pca, method=2, max_iters=300, tolerance=1e-9)
        drift_pca = direction_angle_deg(vt_lm_pca[:3], d_rel)
        results.append(dict(
            piece=piece, stem=stem, perturbation="mesh_normals_pca", param=f"r={r}mm",
            n_pts=C_pca.shape[1], cost_rel=round(c_rel_pca, 3), cost_min=round(c_min_pca, 3),
            drift_lm_deg=round(drift_pca, 3), ang_conv_to_min=round(direction_angle_deg(vt_lm_pca[:3], vt_min[:3]), 3)
        ))
        
        # Quadric normal fit (local paraboloid z = ax^2 + bxy + cy^2 + dx + ey + f)
        quad_normals = []
        for i, pt in enumerate(pts_all):
            idx = kdtree_mesh.query_ball_point(pt, r)
            if len(idx) < 6:
                quad_normals.append(pca_normals[:, i])
                continue
            nbrs = mesh_v[idx] - pt
            n_p = pca_normals[:, i]
            ref_u = np.array([1, 0, 0]) if abs(n_p[0]) < 0.8 else np.array([0, 1, 0])
            u = unit(np.cross(ref_u, n_p))
            v = unit(np.cross(n_p, u))
            R_local = np.vstack([u, v, n_p])  # (3, 3)
            nbrs_loc = (R_local @ nbrs.T).T  # (K, 3)
            
            xl, yl, zl = nbrs_loc[:, 0], nbrs_loc[:, 1], nbrs_loc[:, 2]
            A_mat = np.column_stack([xl**2, xl*yl, yl**2, xl, yl, np.ones_like(xl)])
            try:
                c_q, _, _, _ = np.linalg.lstsq(A_mat, zl, rcond=None)
                d_q, e_q = c_q[3], c_q[4]
                n_loc = unit(np.array([-d_q, -e_q, 1.0]))
                n_global = R_local.T @ n_loc
                quad_normals.append(n_global)
            except Exception:
                quad_normals.append(pca_normals[:, i])
                
        quad_normals = np.array(quad_normals).T
        dots_q = np.sum(quad_normals * C_all[3:6, :], axis=0)
        quad_normals[:, dots_q < 0] *= -1.0
        
        C_quad = C_all.copy()
        C_quad[3:6, :] = quad_normals
        c_rel_quad = hub_cost(vt_rel, C_quad)
        c_min_quad = hub_cost(vt_min, C_quad)
        vt_lm_quad = refine_axis(vt_rel.copy(), C_quad, method=2, max_iters=300, tolerance=1e-9)
        drift_quad = direction_angle_deg(vt_lm_quad[:3], d_rel)
        results.append(dict(
            piece=piece, stem=stem, perturbation="mesh_normals_quadric", param=f"r={r}mm",
            n_pts=C_quad.shape[1], cost_rel=round(c_rel_quad, 3), cost_min=round(c_min_quad, 3),
            drift_lm_deg=round(drift_quad, 3), ang_conv_to_min=round(direction_angle_deg(vt_lm_quad[:3], vt_min[:3]), 3)
        ))
        
    # 2. Breakline Edge Erosion Trimming
    bl_pts0 = load_pcd_xyz(bl0_path)
    bl_pts1 = load_pcd_xyz(bl1_path)
    bl_all = np.hstack([bl_pts0, bl_pts1])
    if bl_all.shape[1] > 0:
        kdtree_bl = cKDTree(bl_all.T)
        dists, _ = kdtree_bl.query(C_all[:3, :].T)
        for d_cut in [1.0, 2.0, 3.0]:
            keep = dists >= d_cut
            if keep.sum() < 100:
                continue
            C_trim = C_all[:, keep]
            c_rel_trim = hub_cost(vt_rel, C_trim)
            c_min_trim = hub_cost(vt_min, C_trim)
            vt_lm_trim = refine_axis(vt_rel.copy(), C_trim, method=2, max_iters=300, tolerance=1e-9)
            drift_trim = direction_angle_deg(vt_lm_trim[:3], d_rel)
            results.append(dict(
                piece=piece, stem=stem, perturbation="breakline_erosion", param=f"cut={d_cut}mm",
                n_pts=C_trim.shape[1], cost_rel=round(c_rel_trim, 3), cost_min=round(c_min_trim, 3),
                drift_lm_deg=round(drift_trim, 3), ang_conv_to_min=round(direction_angle_deg(vt_lm_trim[:3], vt_min[:3]), 3)
            ))
            
    # 3. Single-Wall vs Joint-Wall Optimization
    vt_lm_s0 = refine_axis(vt_rel.copy(), C0, method=2, max_iters=300, tolerance=1e-9)
    vt_lm_s1 = refine_axis(vt_rel.copy(), C1, method=2, max_iters=300, tolerance=1e-9)
    drift_s0 = direction_angle_deg(vt_lm_s0[:3], d_rel)
    drift_s1 = direction_angle_deg(vt_lm_s1[:3], d_rel)
    results.append(dict(
        piece=piece, stem=stem, perturbation="single_wall_S0", param="S0_only",
        n_pts=C0.shape[1], cost_rel=round(hub_cost(vt_rel, C0), 3), cost_min=round(hub_cost(vt_min, C0), 3),
        drift_lm_deg=round(drift_s0, 3), ang_conv_to_min=round(direction_angle_deg(vt_lm_s0[:3], vt_min[:3]), 3)
    ))
    results.append(dict(
        piece=piece, stem=stem, perturbation="single_wall_S1", param="S1_only",
        n_pts=C1.shape[1], cost_rel=round(hub_cost(vt_rel, C1), 3), cost_min=round(hub_cost(vt_min, C1), 3),
        drift_lm_deg=round(drift_s1, 3), ang_conv_to_min=round(direction_angle_deg(vt_lm_s1[:3], vt_min[:3]), 3)
    ))
    
    # 4. Dense Mesh Vertices
    mesh_v = np.asarray(mesh.vertices, dtype=float)
    mesh_vn = np.asarray(mesh.vertex_normals, dtype=float)
    C_dense = np.vstack([mesh_v.T, mesh_vn.T])  # (6, N)
    c_rel_dense = hub_cost(vt_rel, C_dense)
    c_min_dense = hub_cost(vt_min, C_dense)
    vt_lm_dense = refine_axis(vt_rel.copy(), C_dense, method=2, max_iters=300, tolerance=1e-9)
    drift_dense = direction_angle_deg(vt_lm_dense[:3], d_rel)
    results.append(dict(
        piece=piece, stem=stem, perturbation="dense_mesh_vertices", param="raw_vertices",
        n_pts=C_dense.shape[1], cost_rel=round(c_rel_dense, 3), cost_min=round(c_min_dense, 3),
        drift_lm_deg=round(drift_dense, 3), ang_conv_to_min=round(direction_angle_deg(vt_lm_dense[:3], vt_min[:3]), 3)
    ))
    
    return results


def run_step3(args):
    """Step 3: Input Cloud Perturbations & Surface Provenance on 10 failing pieces."""
    print("=== Step 3: Input Cloud Perturbations & Surface Provenance ===", flush=True)
    all_results = []
    
    with Pool(args.jobs) as pool:
        job_args = [(p, args) for p in FAILING_PIECES_POT_E]
        res_lists = pool.starmap(run_step3_single_piece, job_args)
        for res in res_lists:
            all_results.extend(res)
            
    cols = ["piece", "stem", "perturbation", "param", "n_pts", "cost_rel", "cost_min", "drift_lm_deg", "ang_conv_to_min"]
    step3_tsv = os.path.join(args.out, "step3_perturbations.tsv")
    with open(step3_tsv, "w", encoding="utf-8") as f:
        f.write("\t".join(cols) + "\n")
        for r in all_results:
            f.write("\t".join(str(r[c]) for c in cols) + "\n")
    print(f"-> Saved {step3_tsv}", flush=True)


def run_step4_single_piece(piece, args):
    """Step 4 analysis for a single failing Pot E piece."""
    stem = f"Pot_E_Piece_{piece:02d}"
    s0_path = os.path.join(args.corp, "Surfaces", f"{stem}_Surface_0.xyz")
    s1_path = os.path.join(args.corp, "Surfaces", f"{stem}_Surface_1.xyz")
    bl0_path = os.path.join(args.corp, "Breaklines", f"{stem}_Breakline_0.pcd")
    rel_path = os.path.join(args.corp, "Axes", f"{stem}_Axis.xyz")
    ax310_path = os.path.join(args.ax310, f"{stem}_Axis.xyz")
    
    C0 = load_surface(s0_path)
    C1 = load_surface(s1_path)
    C_all = np.hstack([C0, C1])
    centroid = np.mean(C_all[:3, :], axis=1)
    
    vt_rel = read_axes(rel_path)[:, 0]
    vt_min = read_axes(ax310_path)[:, 0]
    d_rel, p_rel = split_axis(vt_rel)
    d_min, p_min = split_axis(vt_min)
    
    # 1. Polynomial Profile Consistency V_poly
    vpoly_rel_k2, _, _, _, _, _ = fit_cylindrical_polynomial_profile(d_rel, p_rel, C_all, degree=2)
    vpoly_rel_k3, _, _, z_rel, r_rel, pred_rel = fit_cylindrical_polynomial_profile(d_rel, p_rel, C_all, degree=3)
    vpoly_rel_k4, _, _, _, _, _ = fit_cylindrical_polynomial_profile(d_rel, p_rel, C_all, degree=4)
    
    vpoly_min_k2, _, _, _, _, _ = fit_cylindrical_polynomial_profile(d_min, p_min, C_all, degree=2)
    vpoly_min_k3, _, _, z_min, r_min, pred_min = fit_cylindrical_polynomial_profile(d_min, p_min, C_all, degree=3)
    vpoly_min_k4, _, _, _, _, _ = fit_cylindrical_polynomial_profile(d_min, p_min, C_all, degree=4)
    
    hub_rel = hub_cost(vt_rel, C_all)
    hub_min = hub_cost(vt_min, C_all)
    delta_hub = hub_rel - hub_min
    delta_poly = vpoly_min_k3 - vpoly_rel_k3
    crit_lambda = delta_hub / delta_poly if delta_poly > 1e-6 else float("inf")
    
    # 2. Distance-Invariant Normal Loss
    norm_loss_rel = distance_invariant_normal_loss(d_rel, p_rel, C_all)
    norm_loss_min = distance_invariant_normal_loss(d_min, p_min, C_all)
    
    # 3. Rim Coplanarity Constraint
    bl_pts = load_pcd_xyz(bl0_path)
    has_rim = False
    rim_ang_rel = float("nan")
    rim_ang_min = float("nan")
    if bl_pts.shape[1] >= 20:
        cov_bl = np.cov(bl_pts, rowvar=True)
        evals, evecs = np.linalg.eigh(cov_bl)
        n_rim = evecs[:, 0]
        has_rim = True
        rim_ang_rel = direction_angle_deg(d_rel, n_rim)
        rim_ang_min = direction_angle_deg(d_min, n_rim)
        
    # Render Step 4 profile plot
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 4.5))
    ax1.scatter(z_rel, r_rel, s=2, c="blue", alpha=0.3, label="Data around $L_{rel}$")
    sort_idx = np.argsort(z_rel)
    ax1.plot(z_rel[sort_idx], pred_rel[sort_idx], "r-", lw=2, label="Degree-3 fit")
    ax1.set_xlabel("Axial coordinate $z$ (mm)")
    ax1.set_ylabel("Radius $r$ (mm)")
    ax1.set_title(f"{stem} (Released Axis $L_{{rel}}$, $V_{{poly}}={vpoly_rel_k3:.2f}$)")
    ax1.grid(True, alpha=0.3)
    ax1.legend(loc="upper right")
    
    ax2.scatter(z_min, r_min, s=2, c="purple", alpha=0.3, label="Data around $L_{min}$")
    sort_idx_min = np.argsort(z_min)
    ax2.plot(z_min[sort_idx_min], pred_min[sort_idx_min], "r-", lw=2, label="Degree-3 fit")
    ax2.set_xlabel("Axial coordinate $z$ (mm)")
    ax2.set_ylabel("Radius $r$ (mm)")
    ax2.set_title(f"{stem} (Huber Basin $L_{{min}}$, $V_{{poly}}={vpoly_min_k3:.2f}$)")
    ax2.grid(True, alpha=0.3)
    ax2.legend(loc="upper right")
    
    plot_path = os.path.join(args.out, "renders", f"step4_profile_{stem}.png")
    fig.tight_layout()
    fig.savefig(plot_path, dpi=120)
    plt.close(fig)
    
    return dict(
        piece=piece, stem=stem,
        hub_rel=round(hub_rel, 3), hub_min=round(hub_min, 3),
        vpoly_rel_k2=round(vpoly_rel_k2, 3), vpoly_min_k2=round(vpoly_min_k2, 3),
        vpoly_rel_k3=round(vpoly_rel_k3, 3), vpoly_min_k3=round(vpoly_min_k3, 3),
        vpoly_rel_k4=round(vpoly_rel_k4, 3), vpoly_min_k4=round(vpoly_min_k4, 3),
        poly_ratio_min_vs_rel=round(vpoly_min_k3 / max(vpoly_rel_k3, 1e-6), 2),
        crit_lambda=round(crit_lambda, 3),
        norm_loss_rel=round(norm_loss_rel, 4), norm_loss_min=round(norm_loss_min, 4),
        norm_favors_rel=(norm_loss_rel < norm_loss_min),
        has_rim=has_rim,
        rim_ang_rel=round(rim_ang_rel, 2) if has_rim else "NA",
        rim_ang_min=round(rim_ang_min, 2) if has_rim else "NA"
    )


def run_step4(args):
    """Step 4: Objective Refinements & Missing Constraints."""
    print("=== Step 4: Objective Refinements & Missing Constraints ===", flush=True)
    with Pool(args.jobs) as pool:
        job_args = [(p, args) for p in FAILING_PIECES_POT_E]
        rows = pool.starmap(run_step4_single_piece, job_args)
        
    cols = [
        "piece", "stem", "hub_rel", "hub_min",
        "vpoly_rel_k2", "vpoly_min_k2", "vpoly_rel_k3", "vpoly_min_k3", "vpoly_rel_k4", "vpoly_min_k4",
        "poly_ratio_min_vs_rel", "crit_lambda",
        "norm_loss_rel", "norm_loss_min", "norm_favors_rel",
        "has_rim", "rim_ang_rel", "rim_ang_min"
    ]
    step4_tsv = os.path.join(args.out, "step4_profile_objective.tsv")
    with open(step4_tsv, "w", encoding="utf-8") as f:
        f.write("\t".join(cols) + "\n")
        for r in rows:
            f.write("\t".join(str(r[c]) for c in cols) + "\n")
    print(f"-> Saved {step4_tsv}", flush=True)


def process_step5_piece(path_rel, args):
    """Step 5 audit for a single piece in the 163-piece corpus."""
    filename = os.path.basename(path_rel)
    stem = filename.replace("_Axis.xyz", "")
    parts = stem.split("_")
    pot = parts[1]
    piece_num = int(parts[3])
    
    vt_rel = read_axes(path_rel)[:, 0]
    d_rel, p_rel = split_axis(vt_rel)
    d_rel = unit(d_rel)
    
    gt_path = os.path.join(args.corp, "Ground Truth Axes", filename)
    has_gt = os.path.exists(gt_path)
    
    s0_path = os.path.join(args.corp, "Surfaces", f"{stem}_Surface_0.xyz")
    s1_path = os.path.join(args.corp, "Surfaces", f"{stem}_Surface_1.xyz")
    has_surfaces = os.path.exists(s0_path) and os.path.exists(s1_path)
    
    n_pts = 0
    centroid = np.zeros(3)
    bbox_dim = np.zeros(3)
    bbox_diag = 0.0
    aspect_ratio = 1.0
    wall_thick_med = float("nan")
    wall_thick_std = float("nan")
    
    if has_surfaces:
        C0 = load_surface(s0_path)
        C1 = load_surface(s1_path)
        C_all = np.hstack([C0, C1])
        n_pts = C_all.shape[1]
        pts = C_all[:3, :].T
        centroid = np.mean(pts, axis=0)
        bmin = pts.min(axis=0)
        bmax = pts.max(axis=0)
        bbox_dim = bmax - bmin
        bbox_diag = float(np.linalg.norm(bbox_dim))
        min_dim = max(bbox_dim.min(), 1.0)
        aspect_ratio = float(bbox_dim.max() / min_dim)
        
        kd_s1 = cKDTree(C1[:3, :].T)
        dists, _ = kd_s1.query(C0[:3, :].T)
        wall_thick_med = float(np.median(dists))
        wall_thick_std = float(np.std(dists))
        
    mesh_path = os.path.join(args.corp, "Mesh", f"{stem}_Mesh.obj")
    if not os.path.exists(mesh_path):
        mesh_path = os.path.join(args.corp, "Mesh", f"{stem}_Mesh_DS.obj")
    surf_area = float("nan")
    if os.path.exists(mesh_path):
        try:
            import trimesh
            m = trimesh.load(mesh_path, process=False)
            surf_area = float(m.area)
        except Exception:
            pass
            
    sherd_pos = "Body"
    bl0_path = os.path.join(args.corp, "Breaklines", f"{stem}_Breakline_0.pcd")
    if os.path.exists(bl0_path):
        bl_pts = load_pcd_xyz(bl0_path)
        if bl_pts.shape[1] >= 20:
            cov = np.cov(bl_pts, rowvar=True)
            evals, _ = np.linalg.eigh(cov)
            if evals[0] / max(evals[2], 1e-6) < 0.05:
                sherd_pos = "Rim_or_Base"
                
    if has_gt:
        vt_gt = read_axes(gt_path)[:, 0]
        d_gt, p_gt = split_axis(vt_gt)
        d_gt = unit(d_gt)
        theta_deg = direction_angle_deg(d_rel, d_gt)
        dist_sherd_mm = abs(point_to_line_dist(centroid, d_rel, p_rel) - point_to_line_dist(centroid, d_gt, p_gt))
        
        if theta_deg < 3.0:
            category = "High (<3 deg)"
        elif theta_deg < 10.0:
            category = "Moderate (3-10 deg)"
        elif theta_deg < 25.0:
            category = "Deviated (10-25 deg)"
        else:
            category = "Gross Outlier (>=25 deg)"
    else:
        theta_deg = float("nan")
        dist_sherd_mm = float("nan")
        category = "Excluded_No_GT"
        
    return dict(
        pot=pot, piece=piece_num, stem=stem, has_gt=has_gt,
        theta_deg=round(theta_deg, 3) if has_gt else "NA",
        dist_sherd_mm=round(dist_sherd_mm, 2) if has_gt else "NA",
        category=category,
        n_pts=n_pts,
        surf_area_mm2=round(surf_area, 1) if not np.isnan(surf_area) else "NA",
        bbox_x_mm=round(float(bbox_dim[0]), 2), bbox_y_mm=round(float(bbox_dim[1]), 2), bbox_z_mm=round(float(bbox_dim[2]), 2),
        bbox_diag_mm=round(bbox_diag, 2),
        aspect_ratio=round(aspect_ratio, 2),
        wall_thick_med_mm=round(wall_thick_med, 2) if not np.isnan(wall_thick_med) else "NA",
        wall_thick_std_mm=round(wall_thick_std, 2) if not np.isnan(wall_thick_std) else "NA",
        sherd_pos=sherd_pos
    )


def run_step5(args):
    """Step 5: Benchmark-Wide Reference vs Ground Truth Audit (163 Pieces)."""
    print("=== Step 5: Benchmark-Wide Reference vs Ground Truth Audit ===", flush=True)
    axes_paths = sorted(glob.glob(os.path.join(args.corp, "Axes", "Pot_*_Piece_*_Axis.xyz")))
    print(f"Auditing {len(axes_paths)} pieces across Pots A-K...", flush=True)
    
    with Pool(args.jobs) as pool:
        job_args = [(p, args) for p in axes_paths]
        rows = pool.starmap(process_step5_piece, job_args)
        
    rows.sort(key=lambda r: (r["pot"], r["piece"]))
    
    cols = [
        "pot", "piece", "stem", "has_gt", "theta_deg", "dist_sherd_mm", "category",
        "n_pts", "surf_area_mm2", "bbox_x_mm", "bbox_y_mm", "bbox_z_mm", "bbox_diag_mm",
        "aspect_ratio", "wall_thick_med_mm", "wall_thick_std_mm", "sherd_pos"
    ]
    step5_tsv = os.path.join(args.out, "step5_corpus_audit.tsv")
    with open(step5_tsv, "w", encoding="utf-8") as f:
        f.write("\t".join(cols) + "\n")
        for r in rows:
            f.write("\t".join(str(r[c]) for c in cols) + "\n")
    print(f"-> Saved {step5_tsv}", flush=True)
    
    summary = {}
    for r in rows:
        pot = r["pot"]
        cat = r["category"]
        if pot not in summary:
            summary[pot] = {"total": 0, "High (<3 deg)": 0, "Moderate (3-10 deg)": 0, "Deviated (10-25 deg)": 0, "Gross Outlier (>=25 deg)": 0, "Excluded_No_GT": 0}
        summary[pot]["total"] += 1
        summary[pot][cat] += 1
        
    sum_cols = ["pot", "total", "High (<3 deg)", "Moderate (3-10 deg)", "Deviated (10-25 deg)", "Gross Outlier (>=25 deg)", "Excluded_No_GT"]
    sum_tsv = os.path.join(args.out, "step5_summary.tsv")
    with open(sum_tsv, "w", encoding="utf-8") as f:
        f.write("\t".join(sum_cols) + "\n")
        tot_all = {c: 0 for c in sum_cols[1:]}
        for pot in sorted(summary.keys()):
            s = summary[pot]
            f.write("\t".join([pot] + [str(s[c]) for c in sum_cols[1:]]) + "\n")
            for c in sum_cols[1:]:
                tot_all[c] += s[c]
        f.write("\t".join(["TOTAL"] + [str(tot_all[c]) for c in sum_cols[1:]]) + "\n")
    print(f"-> Saved {sum_tsv}", flush=True)
    
    # Generate Corpus Distribution Plot
    thetas = [r["theta_deg"] for r in rows if r["has_gt"]]
    areas = [r["surf_area_mm2"] for r in rows if r["has_gt"] and r["surf_area_mm2"] != "NA"]
    thetas_area = [r["theta_deg"] for r in rows if r["has_gt"] and r["surf_area_mm2"] != "NA"]
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11, 4.5))
    ax1.hist(thetas, bins=30, color="steelblue", edgecolor="black", alpha=0.7)
    ax1.axvline(3.0, color="green", linestyle="--", label="3° (High)")
    ax1.axvline(10.0, color="orange", linestyle="--", label="10° (Moderate)")
    ax1.axvline(25.0, color="red", linestyle="--", label="25° (Deviated/Outlier)")
    ax1.set_xlabel("Angular Difference $\\theta(L_{rel}, L_{GT})$ (degrees)")
    ax1.set_ylabel("Count of Pieces")
    ax1.set_title("Corpus Angular Agreement Distribution (141 pieces)")
    ax1.grid(True, alpha=0.3)
    ax1.legend(loc="upper right")
    
    ax2.scatter(areas, thetas_area, c="darkblue", s=25, alpha=0.6)
    ax2.set_xlabel("Surface Area ($mm^2$)")
    ax2.set_ylabel("Angular Difference $\\theta$ (degrees)")
    ax2.set_title("Angle Error vs Fragment Surface Area")
    ax2.grid(True, alpha=0.3)
    
    fig.tight_layout()
    plot_path = os.path.join(args.out, "renders", "step5_corpus_distribution.png")
    fig.savefig(plot_path, dpi=120)
    plt.close(fig)
    print(f"-> Saved {plot_path}", flush=True)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--corp", default="/data/gpfs/projects/punim2657/sfs_main/original_samples/SfS_pp")
    parser.add_argument("--ax310", default="/data/gpfs/projects/punim2657/SfSpp/runs/20261105-1215_1a6f16e_t310b3-timing/out/axes310")
    parser.add_argument("--out", required=True)
    parser.add_argument("--jobs", type=int, default=20)
    args = parser.parse_args()
    
    os.makedirs(args.out, exist_ok=True)
    os.makedirs(os.path.join(args.out, "renders"), exist_ok=True)
    
    t0 = time.time()
    run_step2(args)
    run_step3(args)
    run_step4(args)
    run_step5(args)
    print("=== All Steps 2-5 Completed in %.1fs ===" % (time.time() - t0), flush=True)


if __name__ == "__main__":
    main()
