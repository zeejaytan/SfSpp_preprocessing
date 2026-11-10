#!/usr/bin/env python3
"""Ticket 325 step 1: measure scale-free gate statistics for every axis we trust.

For each piece (163 corpus pots + 9 Juglet) and each axis source
(axes323 rank0, authors' released axes, corpus Ground Truth Axes, Juglet_GT)
compute, with NO reference to any absolute millimetre threshold:

  D          bbox diagonal of the piece's two wall clouds (C0 + C1)
  d_c        distance from the cloud centroid to the axis line
  r_min/q01/med/mean/max   radial distance stats of all points to the line
  u_clr      r_q01 / r_mean          (material clearance, floor candidate)
  u1         d_c / r_mean            (wall standoff ratio, r_prior input)
  v          r_mean / D              (implied radius vs piece size, ceiling)
  mean_ax    mean |a.n| over all normals; mean_ax_near over the near set
  near_count points with r < 0.75 r_mean
  span_deg   angular span of the near set about the axis
  z_ext_all / z_ext_near   axial extent of all / near points
  z_frac     z_ext_near / D          (axial depth fraction, base test candidate)
  is_base_new  the scale-free base verdict:
               near_count>=80 and mean_ax_near>=0.70 and span>=160
               and z_frac>=0.08

Also scores the Juglet axes323 lines against Juglet_GT (direction error, deg).
Output: one TSV row per (piece, source) plus a printed summary of margins.
"""
import os
import sys
import glob
import numpy as np

A323 = "/data/gpfs/projects/punim2657/SfSpp/runs/20261110-0740_d628fc0_t323-axes/out/axes323"
CORPUS = "/data/gpfs/projects/punim2657/sfs_main/original_samples/SfS_pp"
JUG = "/data/gpfs/projects/punim2657/SfSpp/runs/20261103-1332_fab76f5_t66-admitsign-default/outU_jug/geom"
GTDIR = "/data/gpfs/projects/punim2657/Dataset/Juglet_GT"

NEAR_FRAC = 0.75   # near set = r < NEAR_FRAC * r_mean
MIN_NEAR = 80
MIN_AX = 0.70
MIN_SPAN = 160.0
MIN_ZFRAC = 0.08


def load_wall(path):
    with open(path) as fh:
        first = fh.readline()
    if first.startswith("ply"):
        n = None
        with open(path) as fh:
            for line in fh:
                if line.startswith("element vertex"):
                    n = int(line.split()[-1])
                if line.strip() == "end_header":
                    break
            rows = []
            for _ in range(n):
                rows.append([float(v) for v in fh.readline().split()[:6]])
        return np.asarray(rows, dtype=float).T
    a = np.loadtxt(path, usecols=(0, 1, 2, 3, 4, 5), ndmin=2)
    return np.asarray(a, dtype=float).T


def read_axis(path):
    row = np.atleast_2d(np.loadtxt(path, ndmin=2))
    return np.asarray(row[0], dtype=float)[:6]


def canon(a):
    a = np.asarray(a, dtype=float).copy()
    if a[2] < 0:
        a = -a
    return a


def line_stats(C, vt):
    """C: 6xN (xyz, normals), vt: 6-vector (point, direction)."""
    P = C[0:3]
    Nn = C[3:6]
    p = vt[0:3]
    a = vt[3:6]
    a = a / np.linalg.norm(a)
    d = P - p[:, None]
    t = a @ d                      # axial coordinate
    e = d - t[None, :] * a[:, None]
    r = np.linalg.norm(e, axis=0)
    ctr = P.mean(axis=1)
    dc = np.linalg.norm((ctr - p) - ((ctr - p) @ a) * a)
    D = float(np.linalg.norm(P.max(axis=1) - P.min(axis=1)))

    r_q01 = float(np.percentile(r, 1))
    r_mean = float(r.mean())
    u_clr = r_q01 / r_mean
    u1 = float(dc) / r_mean
    v = r_mean / D

    mean_ax = float(np.mean(np.abs(Nn.T @ a)))
    near = r < NEAR_FRAC * r_mean
    near_count = int(near.sum())
    if near_count:
        en = e[:, near]
        # azimuth in the plane perpendicular to a: build an orthonormal basis
        u = np.cross(a, [1.0, 0.0, 0.0])
        if np.linalg.norm(u) < 1e-9:
            u = np.cross(a, [0.0, 1.0, 0.0])
        u /= np.linalg.norm(u)
        wv = np.cross(a, u)
        az = np.sort(np.arctan2(en.T @ wv, en.T @ u))
        gaps = np.diff(np.concatenate([az, az[:1] + 2 * np.pi]))
        span = float(np.degrees(2 * np.pi - gaps.max()))
        tn = t[near]
        z_near = float(tn.max() - tn.min())
        mean_ax_near = float(np.mean(np.abs(Nn.T @ a)[near]))
    else:
        span = 0.0
        z_near = 0.0
        mean_ax_near = 0.0
    z_all = float(t.max() - t.min())
    z_frac = z_near / D
    is_base = (near_count >= MIN_NEAR and mean_ax_near >= MIN_AX
               and span >= MIN_SPAN and z_frac >= MIN_ZFRAC)
    return dict(D=D, d_c=float(dc), r_min=float(r.min()), r_q01=r_q01,
                r_med=float(np.median(r)), r_mean=r_mean, r_max=float(r.max()),
                u_clr=u_clr, u1=u1, v=v, mean_ax=mean_ax,
                mean_ax_near=mean_ax_near, near_count=near_count,
                span_deg=span, z_ext_all=z_all, z_ext_near=z_near,
                z_frac=z_frac, is_base_new=int(is_base))


def main():
    outdir = sys.argv[1]
    rows = []
    jug_scores = []
    for axf in sorted(glob.glob(os.path.join(A323, "*_Axis.xyz"))):
        stem = os.path.basename(axf)[:-len("_Axis.xyz")]
        if stem.startswith("Juglet_"):
            idx = int(stem.split("_")[-1])
            c0 = os.path.join(JUG, f"Juglet_Piece_{idx}.S0")
            c1 = os.path.join(JUG, f"Juglet_Piece_{idx}.S1")
            sources = [("juglet_gt", os.path.join(GTDIR, f"Juglet_Piece_{idx}_Axis.xyz"))]
        else:
            c0 = os.path.join(CORPUS, "Surfaces", f"{stem}_Surface_0.xyz")
            c1 = os.path.join(CORPUS, "Surfaces", f"{stem}_Surface_1.xyz")
            sources = [
                ("released", os.path.join(CORPUS, "Axes", f"{stem}_Axis.xyz")),
                ("gt_axes", os.path.join(CORPUS, "Ground Truth Axes", f"{stem}_Axis.xyz")),
            ]
        try:
            C = np.concatenate([load_wall(c0), load_wall(c1)], axis=1)
        except Exception as exc:
            print(f"LOAD-FAIL {stem} {exc}", flush=True)
            continue
        all_sources = [("axes323", axf)] + sources
        for sname, spath in all_sources:
            if not spath or not os.path.isfile(spath):
                continue
            vt = read_axis(spath)
            st = line_stats(C, vt)
            st.update(stem=stem, source=sname, pot=stem.split("_")[1] if not stem.startswith("Juglet_") else "JUG")
            rows.append(st)
            if stem.startswith("Juglet_") and sname == "axes323":
                gt = read_axis(os.path.join(GTDIR, f"Juglet_Piece_{idx}_Axis.xyz"))
                ca, cg = canon(vt[3:6]), canon(gt[3:6])
                err = float(np.degrees(np.arccos(np.clip(abs(ca @ cg), -1, 1))))
                jug_scores.append((stem, err, st["u_clr"], st["v"], st["is_base_new"]))

    cols = ["stem", "source", "pot", "D", "d_c", "r_min", "r_q01", "r_med", "r_mean",
            "r_max", "u_clr", "u1", "v", "mean_ax", "mean_ax_near", "near_count",
            "span_deg", "z_ext_all", "z_ext_near", "z_frac", "is_base_new"]
    with open(os.path.join(outdir, "gate_stats.tsv"), "w") as fh:
        fh.write("\t".join(cols) + "\n")
        for r in rows:
            fh.write("\t".join(
                (f"{r[c]:.4f}" if isinstance(r[c], float) else str(r[c])) for c in cols) + "\n")

    arr = np.array([[r["u_clr"], r["v"], r["z_frac"]] for r in rows])
    print(f"rows {len(rows)}  pieces {len(set(r['stem'] for r in rows))}")
    print(f"u_clr min {arr[:,0].min():.3f}  p1 {np.percentile(arr[:,0],1):.3f}  med {np.median(arr[:,0]):.3f}")
    print(f"v     max {arr[:,1].max():.3f}  p99 {np.percentile(arr[:,1],99):.3f}  med {np.median(arr[:,1]):.3f}")
    print(f"z_frac med {np.median(arr[:,2]):.3f}  is_base_new count {sum(r['is_base_new'] for r in rows)}")
    for src in ("axes323", "released", "gt_axes", "juglet_gt"):
        sub = [r for r in rows if r["source"] == src]
        if not sub:
            continue
        u = np.array([r["u_clr"] for r in sub])
        vv = np.array([r["v"] for r in sub])
        zb = sum(r["is_base_new"] for r in sub)
        print(f"{src:10s} n={len(sub):3d}  u_clr min {u.min():.3f}  v max {vv.max():.3f}  is_base_new {zb}")
    print("--- Juglet axes323 vs GT ---")
    for stem, err, u, v_, b in jug_scores:
        print(f"{stem}  dir_err {err:6.2f} deg  u_clr {u:.3f}  v {v_:.3f}  is_base_new {b}")


if __name__ == "__main__":
    main()
