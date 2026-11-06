#!/usr/bin/env python3
"""Ticket 311 renders (compute node):
1. pote_axes_mechanisms.png: 3D surface clouds (S0 grey, S1 blue) + released axis (dashed black)
   + 308 BASE axis (green) + 310 rank-1 axis (solid blue) + 310 decoy lines 2..K (red/orange)
   + LM-from-released trajectory end (purple) across 6 representative Pot E pieces covering both
   failure mechanisms (side view + down-released-axis top view).
2. pote_stationarity_landscape.png: All 34 Pot E pieces — angle to released axis (308 BASE,
   310 rank-1 K1, 310 best-of-6 K6, and LM refined directly from released axis) + worse-wall
   Huber cost ratio vs cross-wall disagreement angle.
3. pote_kladder_assembly.png: 3D reassembled Pot E meshes (31 counted pieces transformed by
   T_<i>to_<root>.txt aligned to Ground Truth frame, green = seated within 0.35 rad / 50 mm on
   at least one GT join, red = failed/unseated) across GT, E_MO, E_BASE, E_K1, E_K2, E_K3, E_K6.
"""
import csv
import glob
import json
import os
import sys
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

CORP = "/data/gpfs/projects/punim2657/sfs_main/original_samples/SfS_pp"
RUNS = "/data/gpfs/projects/punim2657/SfSpp/runs"
AX_MO = os.path.join(CORP, "Axes")
AX_BASE = os.path.join(RUNS, "20261105-0532_d330469_t308a-axes/out/axes_paper")
AX_310 = os.path.join(RUNS, "20261105-1215_1a6f16e_t310b3-timing/out/axes310")
R_CD = os.path.join(RUNS, "20261106-0502_3695976_t311cd-basins/out")
R_308E = os.path.join(RUNS, "20261105-0548_d330469_t308b-E/out")
R_310E = os.path.join(RUNS, "20261105-1407_1a6f16e_t310c2-E/out")


def load_surf(piece, wall):
    p = os.path.join(CORP, "Surfaces", f"Pot_E_Piece_{piece:02d}_Surface_{wall}.xyz")
    a = np.loadtxt(p, usecols=(0, 1, 2), ndmin=2)
    return np.asarray(a, dtype=float).T


def load_axes_file(path):
    if not os.path.isfile(path):
        return np.zeros((6, 0))
    a = np.loadtxt(path, ndmin=2)
    if a.size == 0:
        return np.zeros((6, 0))
    # File format: x y z nx ny nz -> convert to [n(3); p(3)] columns
    out = np.zeros((6, a.shape[0]))
    out[0:3, :] = a[:, 3:6].T
    out[3:6, :] = a[:, 0:3].T
    return out


def ang_deg(u, v):
    u = u / np.linalg.norm(u)
    v = v / np.linalg.norm(v)
    return float(np.degrees(np.arccos(np.clip(abs(float(np.dot(u, v))), -1.0, 1.0))))


def rot_to_z(d):
    """Rotation matrix R that maps unit vector d to [0, 0, 1]."""
    d = d / np.linalg.norm(d)
    z = np.array([0.0, 0.0, 1.0])
    if abs(np.dot(d, z)) > 0.99999:
        return np.eye(3) if np.dot(d, z) > 0 else np.diag([1.0, -1.0, -1.0])
    v = np.cross(d, z)
    s = np.linalg.norm(v)
    c = float(np.dot(d, z))
    vx = np.array([[0, -v[2], v[1]], [v[2], 0, -v[0]], [-v[1], v[0], 0]])
    return np.eye(3) + vx + (vx @ vx) * ((1.0 - c) / (s * s))


def render_mechanisms(outdir):
    pieces = [
        (18, "P18: Mech 1 (decoy line breaks K=1 pass)\nrank1=0.52° (K=1 in 308 -> K=2 in 310, line2=88.9°)"),
        (21, "P21: Mech 1+2A (misranked + 6 lines)\n308=6.21° (K=1) vs 310 rank1=18.40°, rank5=10.31°"),
        (31, "P31: Mech 2A (true basin at rank 6)\nrank1=78.73° (83.7/pt) vs rank6=2.42° (182.4/pt, 2.18x)"),
        (3,  "P03: Mech 2B (ref not stationary, 37° wall split)\nref cost 1.41x; LM from ref drifts 28.47° -> rank1"),
        (23, "P23: Mech 2B (ref not stationary, 29° wall split)\nref cost 2.03x; LM from ref drifts 44.86° -> rank1"),
        (27, "P27: Mech 2B (ref cost 8.58x worse than rank 1)\nLM from ref drifts 39.90° -> rank1"),
    ]
    fig = plt.figure(figsize=(16, 18))
    for row_idx, (p, desc) in enumerate(pieces):
        C0 = load_surf(p, 0)
        C1 = load_surf(p, 1)
        C0s = C0[:, ::max(1, C0.shape[1] // 2000)]
        C1s = C1[:, ::max(1, C1.shape[1] // 2000)]
        allp = np.hstack([C0s, C1s])
        ctr = allp.mean(axis=1)
        rad = float(np.linalg.norm(allp - ctr[:, None], axis=0).max()) * 1.15

        rel = load_axes_file(os.path.join(AX_MO, f"Pot_E_Piece_{p:02d}_Axis.xyz"))
        base = load_axes_file(os.path.join(AX_BASE, f"Pot_E_Piece_{p:02d}_Axis.xyz"))
        a310 = load_axes_file(os.path.join(AX_310, f"Pot_E_Piece_{p:02d}_Axis.xyz"))

        d_ref = rel[0:3, 0] / np.linalg.norm(rel[0:3, 0])
        R = rot_to_z(d_ref)
        C0r = R @ (C0s - ctr[:, None])
        C1r = R @ (C1s - ctr[:, None])

        for col_idx, (vname, elev, azim) in enumerate([
            ("Side view (ref axis vertical)", 12, -55),
            ("Top view (looking down ref axis)", 88, 0),
        ]):
            ax = fig.add_subplot(len(pieces), 2, row_idx * 2 + col_idx + 1, projection="3d")
            ax.scatter(C0r[0], C0r[1], C0r[2], s=0.6, c="#8c969e", alpha=0.55, label="Wall 0 (S0)" if (row_idx == 0 and col_idx == 0) else None)
            ax.scatter(C1r[0], C1r[1], C1r[2], s=0.6, c="#5fa2ce", alpha=0.55, label="Wall 1 (S1)" if (row_idx == 0 and col_idx == 0) else None)

            # Plot decoy lines first (ranks 2..K in a310)
            for k in range(1, a310.shape[1]):
                dk = R @ (a310[0:3, k] / np.linalg.norm(a310[0:3, k]))
                pk = R @ (a310[3:6, k] - ctr)
                pk = pk - np.dot(pk, dk) * dk
                seg = np.column_stack([pk - rad * dk, pk + rad * dk])
                is_good_sub = ang_deg(a310[0:3, k], d_ref) < 11.0
                col = "#8e44ad" if is_good_sub else "#e67e22"
                lw = 2.0 if is_good_sub else 1.1
                lbl = None
                if row_idx == 0 and col_idx == 0 and k == 1:
                    lbl = "310 lines 2..K (decoys)"
                ax.plot(seg[0], seg[1], seg[2], color=col, ls="-", lw=lw, alpha=0.85, label=lbl)

            # Plot 308 BASE rank-1
            if base.shape[1] > 0:
                db = R @ (base[0:3, 0] / np.linalg.norm(base[0:3, 0]))
                pb = R @ (base[3:6, 0] - ctr)
                pb = pb - np.dot(pb, db) * db
                seg = np.column_stack([pb - rad * db, pb + rad * db])
                ax.plot(seg[0], seg[1], seg[2], color="#27ae60", ls="-.", lw=2.0,
                        label="308 BASE line 1" if (row_idx == 0 and col_idx == 0) else None)

            # Plot 310 rank-1
            if a310.shape[1] > 0:
                d1 = R @ (a310[0:3, 0] / np.linalg.norm(a310[0:3, 0]))
                p1 = R @ (a310[3:6, 0] - ctr)
                p1 = p1 - np.dot(p1, d1) * d1
                seg = np.column_stack([p1 - rad * d1, p1 + rad * d1])
                ax.plot(seg[0], seg[1], seg[2], color="#1f4fd8", ls="-", lw=2.5,
                        label="310 rule rank 1 (K1)" if (row_idx == 0 and col_idx == 0) else None)

            # Plot released axis (ref[0])
            dr = R @ d_ref
            pr = R @ (rel[3:6, 0] - ctr)
            pr = pr - np.dot(pr, dr) * dr
            seg = np.column_stack([pr - rad * dr, pr + rad * dr])
            ax.plot(seg[0], seg[1], seg[2], color="#111111", ls="--", lw=2.2,
                    label="Authors' released axis (MO)" if (row_idx == 0 and col_idx == 0) else None)

            ax.view_init(elev=elev, azim=azim)
            if col_idx == 1:
                ax.set_proj_type("ortho")
            lim = rad * 0.95
            ax.set_xlim(-lim, lim)
            ax.set_ylim(-lim, lim)
            ax.set_zlim(-lim, lim)
            ax.set_box_aspect((1, 1, 1))
            ax.set_xticklabels([])
            ax.set_yticklabels([])
            ax.set_zticklabels([])
            ax.set_title(f"{desc}\n[{vname}]", fontsize=8.5)

    fig.suptitle(
        "Pot E Axis Failure Mechanisms on Sherd Clouds (aligned with authors' released axis vertical)\n"
        "Black dashed = Authors' released (MO) | Blue = 310 Rank 1 (K1) | Green dash-dot = 308 BASE | Orange = 310 extra lines 2..K | Purple = 310 lower-rank near-ref basin",
        fontsize=11, fontweight="bold"
    )
    handles, labels = fig.axes[0].get_legend_handles_labels()
    fig.legend(handles, labels, loc="lower center", ncol=5, fontsize=9, frameon=True)
    fig.tight_layout(rect=[0, 0.03, 1, 0.96])
    out_path = os.path.join(outdir, "pote_axes_mechanisms.png")
    fig.savefig(out_path, dpi=140)
    plt.close(fig)
    print("wrote", out_path)


def render_stationarity_landscape(outdir):
    stat_rows = []
    with open(os.path.join(R_CD, "pot_e_ref_stationarity.tsv")) as f:
        for r in csv.DictReader(f, delimiter="\t"):
            if int(r["ref_idx"]) == 0:
                stat_rows.append(r)

    pieces = [int(r["piece"]) for r in stat_rows]
    line0_ang = [float(r["line0_310_ang_to_this_ref"]) for r in stat_rows]
    best_ang = [float(r["best310_ang_to_this_ref"]) for r in stat_rows]
    drift_ang = [float(r["drift_on_C_deg"]) for r in stat_rows]
    cost_ratio = [float(r["ref_vs_best310_ratio"]) for r in stat_rows]
    wall_split = [float(r["wall0_vs_wall1_deg"]) for r in stat_rows]

    # Also get 308 BASE best angle to ref[0]
    base_ang = []
    for p in pieces:
        rel = load_axes_file(os.path.join(AX_MO, f"Pot_E_Piece_{p:02d}_Axis.xyz"))
        bas = load_axes_file(os.path.join(AX_BASE, f"Pot_E_Piece_{p:02d}_Axis.xyz"))
        d0 = rel[0:3, 0]
        if bas.shape[1] > 0:
            base_ang.append(min(ang_deg(d0, bas[0:3, j]) for j in range(bas.shape[1])))
        else:
            base_ang.append(90.0)

    base_fail = {3, 9, 23, 24, 25, 26, 27, 28, 29, 31}
    mm_extra_fail = {12, 14, 17, 18, 21, 30}

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(15, 9.5), sharex=True)
    x = np.arange(len(pieces))

    for idx, p in enumerate(pieces):
        if p > 31:
            ax1.axvspan(idx - 0.5, idx + 0.5, color="#dddddd", alpha=0.5)
            ax2.axvspan(idx - 0.5, idx + 0.5, color="#dddddd", alpha=0.5)
        elif p in base_fail:
            ax1.axvspan(idx - 0.45, idx + 0.45, color="#fadbd8", alpha=0.45)
            ax2.axvspan(idx - 0.45, idx + 0.45, color="#fadbd8", alpha=0.45)
        elif p in mm_extra_fail:
            ax1.axvspan(idx - 0.45, idx + 0.45, color="#fdebd0", alpha=0.55)
            ax2.axvspan(idx - 0.45, idx + 0.45, color="#fdebd0", alpha=0.55)

    ax1.plot(x, line0_ang, "o-", color="#1f4fd8", lw=1.8, ms=5.5, label="310 Rank-1 angle to Authors' ref[0] (deg)")
    ax1.plot(x, best_ang, "s--", color="#8e44ad", lw=1.4, ms=5.0, label="310 Best-of-K6 angle to Authors' ref[0] (deg)")
    ax1.plot(x, base_ang, "^:", color="#27ae60", lw=1.4, ms=5.0, label="308 BASE best angle to Authors' ref[0] (deg)")
    ax1.plot(x, drift_ang, "x", color="#c0392b", ms=7.5, mew=2.0, label="LM drift when started directly at Authors' ref[0] (deg)")
    ax1.axhline(5.0, color="#2ecc71", ls="--", lw=1.0, label="5° accuracy bar")
    ax1.axhline(25.0, color="#e74c3c", ls=":", lw=1.0, label="25° assembler axis-pair gate (0.436 rad)")
    ax1.set_ylabel("Angle to Authors' Axis ref[0] (deg)", fontsize=10)
    ax1.set_ylim(-2, 95)
    ax1.grid(True, alpha=0.3)
    ax1.legend(loc="upper left", ncol=3, fontsize=8.5)
    ax1.set_title(
        "Pot E (All 34 Pieces): Angle to Authors' Released Axis & LM Stationarity Drift\n"
        "Pink = fails in both 308 BASE & 310 MM (10 pieces) | Orange = passes in 308 BASE, fails in 310 MM (6 pieces) | Grey = dropped by assembler (P32-P34)",
        fontsize=10.5, fontweight="bold"
    )

    ax2_r = ax2.twinx()
    b1 = ax2.bar(x - 0.18, cost_ratio, width=0.35, color="#c0392b", alpha=0.8, label="Worse-wall Huber cost ratio (Authors' ref[0] / 310 Rank-1)")
    b2 = ax2_r.bar(x + 0.18, wall_split, width=0.35, color="#2980b9", alpha=0.75, label="Cross-wall optimum split on ref[0] (|wall0 - wall1| deg)")
    ax2.axhline(1.0, color="k", ls="-", lw=0.8)
    ax2.set_ylabel("Cost Ratio (ref[0] / best310 worst-wall)", color="#c0392b", fontsize=10)
    ax2_r.set_ylabel("Single-wall optimum split (deg)", color="#2980b9", fontsize=10)
    ax2.set_xticks(x)
    ax2.set_xticklabels([f"P{p:02d}" for p in pieces], rotation=45, fontsize=8.5)
    ax2.set_xlabel("Pot E Piece Index (01..31 counted by assembler; 32..34 excluded by SHARD_NUMBER=31 & no GT)", fontsize=10)
    ax2.grid(True, alpha=0.3)

    lines1, labels1 = ax2.get_legend_handles_labels()
    lines2, labels2 = ax2_r.get_legend_handles_labels()
    ax2.legend(lines1 + lines2, labels1 + labels2, loc="upper left", ncol=2, fontsize=9)

    fig.tight_layout()
    out_path = os.path.join(outdir, "pote_stationarity_landscape.png")
    fig.savefig(out_path, dpi=140)
    plt.close(fig)
    print("wrote", out_path)


def parse_T(path):
    with open(path) as f:
        toks = f.read().split()
    vals = [float(x) for x in toks[:16]]
    return np.array(vals, dtype=float).reshape(4, 4)


def load_mesh_vertices(piece, max_pts=600):
    p_ds = os.path.join(CORP, "Mesh", f"Pot_E_Piece_{piece:02d}_Mesh_DS.obj")
    p_full = os.path.join(CORP, "Mesh", f"Pot_E_Piece_{piece:02d}_Mesh.obj")
    p = p_ds if os.path.isfile(p_ds) else p_full
    verts = []
    with open(p) as f:
        for ln in f:
            if ln.startswith("v "):
                parts = ln.split()
                verts.append((float(parts[1]), float(parts[2]), float(parts[3])))
    v = np.array(verts, dtype=float)
    if v.shape[0] > max_pts:
        v = v[::max(1, v.shape[0] // max_pts)]
    return v


def render_assemblies(outdir, b_run_dir, b2_run_dir=None):
    # Load GT poses and simple_graph for Pot E (pieces 1..31)
    gt_T = {}
    for i in range(1, 32):
        gt_T[i] = parse_T(os.path.join(CORP, "Ground Truth", f"Pot_E_Piece_{i}_T.txt"))
    sg = np.loadtxt(os.path.join(CORP, "Ground Truth", "Pot_E_simple_graph.txt"), dtype=int)
    verts = {i: load_mesh_vertices(i, max_pts=500) for i in range(1, 32)}

    # Collect arms to plot
    panels = [("Ground Truth\n31/31 sherds, 62/62 joins", None, set(), 0.0, 0.0)]

    candidate_arms = [
        ("E_MO (Authors' Axes)", [
            os.path.join(b_run_dir, "out/E_MOR1") if b_run_dir else "",
            os.path.join(b_run_dir, "out/E_MOR2") if b_run_dir else "",
            os.path.join(R_310E, "MOR1"),
        ]),
        ("E_BASE (308 Paper Chain)", [
            os.path.join(b_run_dir, "out/E_BASER2") if b_run_dir else "",
            os.path.join(b_run_dir, "out/E_BASER1") if b_run_dir else "",
            os.path.join(R_308E, "MMR1"),
        ]),
        ("E_K1 (310 Rule Top-1)", [
            os.path.join(b_run_dir, "out/E_K1R1") if b_run_dir else "",
            os.path.join(b_run_dir, "out/E_K1R2") if b_run_dir else "",
        ]),
        ("E_K2 (310 Rule Top-2)", [
            os.path.join(b2_run_dir, "out/E_K2R2") if b2_run_dir else "",
            os.path.join(b2_run_dir, "out/E_K2R1") if b2_run_dir else "",
            os.path.join(b_run_dir, "out/E_K2R2") if b_run_dir else "",
        ]),
        ("E_K3 (310 Rule Top-3)", [
            os.path.join(b2_run_dir, "out/E_K3R2") if b2_run_dir else "",
            os.path.join(b2_run_dir, "out/E_K3R1") if b2_run_dir else "",
            os.path.join(b_run_dir, "out/E_K3R1") if b_run_dir else "",
        ]),
        ("E_K6 (310 Rule Top-6)", [
            os.path.join(b_run_dir, "out/E_K6R1") if b_run_dir else "",
            os.path.join(b_run_dir, "out/E_K6R2") if b_run_dir else "",
            os.path.join(R_310E, "MMR2"),
        ]),
    ]

    for label, dirs in candidate_arms:
        arm_dir = None
        for d in dirs:
            if d and os.path.isfile(os.path.join(d, "1. Acc.txt")):
                arm_dir = d
                break
        if not arm_dir:
            continue
        # Load 1-based predicted transforms (T_<p-1>to_<p-1>.txt maps Piece p)
        pred_T = {}
        for p in range(1, 32):
            tf = os.path.join(arm_dir, f"T_{p-1}to_{p-1}.txt")
            if os.path.isfile(tf):
                pred_T[p] = parse_T(tf)

        # Score joins & pieces exactly per C++ CountResult (0.35 rad / 50 mm)
        join_pass = 0
        join_tot = 0
        piece_ok = {i: False for i in range(1, 32)}
        seated_deg = []
        seated_mm = []
        for i in range(1, 32):
            for j in range(i + 1, 32):
                if sg[i - 1, j - 1] == 1:
                    join_tot += 1
                    if i in pred_T and j in pred_T:
                        # rel_pr = inv(T[i]) @ T[j]; rel_gt = inv(GT[i]) @ GT[j]
                        rel_pr = np.linalg.inv(pred_T[i]) @ pred_T[j]
                        rel_gt = np.linalg.inv(gt_T[i]) @ gt_T[j]
                        err = rel_pr @ np.linalg.inv(rel_gt)
                        tr = np.clip((np.trace(err[:3, :3]) - 1.0) / 2.0, -1.0, 1.0)
                        rad = float(np.arccos(tr))
                        mm = float(np.linalg.norm(err[:3, 3]))
                        if rad < 0.35 and mm < 50.0:
                            join_pass += 1
                            piece_ok[i] = True
                            piece_ok[j] = True
                            seated_deg.append(np.degrees(rad))
                            seated_mm.append(mm)
        sherd_pass = sum(1 for i in range(1, 32) if piece_ok[i])
        failed_set = {i for i in range(1, 32) if not piece_ok[i]}
        med_deg = float(np.median(seated_deg)) if seated_deg else 0.0
        med_mm = float(np.median(seated_mm)) if seated_mm else 0.0

        # Align predicted assembly to GT frame via first seated piece
        seated_indices = [i for i in range(1, 32) if piece_ok[i] and i in pred_T]
        anchor = seated_indices[0] if seated_indices else (1 if 1 in pred_T else None)
        T_align = (gt_T[anchor] @ np.linalg.inv(pred_T[anchor])) if anchor else np.eye(4)
        aligned_T = {i: (T_align @ pred_T[i]) for i in pred_T}
        title = (
            f"{label}\n"
            f"{sherd_pass}/31 sherds, {join_pass}/62 joins\n"
            f"(seated med {med_deg:.2f}° / {med_mm:.1f} mm)"
        )
        panels.append((title, aligned_T, failed_set, med_deg, med_mm))

    ncols = min(4, len(panels))
    nrows = (len(panels) + ncols - 1) // ncols
    fig = plt.figure(figsize=(4.4 * ncols, 4.8 * nrows))

    # Compute GT bounding box for consistent camera
    all_gt_pts = []
    for i in range(1, 32):
        vh = np.hstack([verts[i], np.ones((verts[i].shape[0], 1))])
        vw = (gt_T[i] @ vh.T).T[:, :3]
        all_gt_pts.append(vw)
    all_gt = np.vstack(all_gt_pts)
    ctr = all_gt.mean(axis=0)
    span = float(np.max(np.ptp(all_gt, axis=0))) * 0.65

    for idx, (title, aligned_T, failed_set, _, _) in enumerate(panels):
        ax = fig.add_subplot(nrows, ncols, idx + 1, projection="3d")
        for i in range(1, 32):
            vh = np.hstack([verts[i], np.ones((verts[i].shape[0], 1))])
            if aligned_T is None:
                vw = (gt_T[i] @ vh.T).T[:, :3]
                col = "#2ecc71"
                alpha = 0.55
            elif i in aligned_T:
                vw = (aligned_T[i] @ vh.T).T[:, :3]
                # Clip wild outliers to keep vessel scale readable while showing misplacement
                offset = vw.mean(axis=0) - ctr
                if np.linalg.norm(offset) > span * 1.6:
                    vw = vw - offset + (offset / np.linalg.norm(offset)) * (span * 1.45)
                col = "#e74c3c" if i in failed_set else "#2ecc71"
                alpha = 0.65 if i in failed_set else 0.50
            else:
                continue
            ax.scatter(vw[:, 0], vw[:, 1], vw[:, 2], s=0.7, c=col, alpha=alpha)

        ax.set_xlim(ctr[0] - span * 1.5, ctr[0] + span * 1.5)
        ax.set_ylim(ctr[1] - span * 1.5, ctr[1] + span * 1.5)
        ax.set_zlim(ctr[2] - span * 1.5, ctr[2] + span * 1.5)
        ax.set_box_aspect((1, 1, 1))
        ax.view_init(elev=18, azim=-45)
        ax.set_xticklabels([])
        ax.set_yticklabels([])
        ax.set_zticklabels([])
        ax.set_title(title, fontsize=8.5)

    fig.suptitle(
        "Pot E Reassembly Across Axis Sets (Green = seated within 0.35 rad / 50 mm on >=1 GT join; Red = failed sherd)\n"
        "Same breaklines (305-lane-e2), same staged meshes/surfaces, same binary — only Axes/ substituted",
        fontsize=11, fontweight="bold"
    )
    fig.tight_layout(rect=[0, 0.01, 1, 0.94])
    out_path = os.path.join(outdir, "pote_kladder_assembly.png")
    fig.savefig(out_path, dpi=140)
    plt.close(fig)
    print("wrote", out_path)


if __name__ == "__main__":
    out_dir = sys.argv[1]
    b_dir = sys.argv[2] if len(sys.argv) > 2 else ""
    b2_dir = sys.argv[3] if len(sys.argv) > 3 else ""
    os.makedirs(out_dir, exist_ok=True)
    render_mechanisms(out_dir)
    render_stationarity_landscape(out_dir)
    render_assemblies(out_dir, b_dir, b2_dir)
