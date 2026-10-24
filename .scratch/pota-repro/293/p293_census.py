#!/usr/bin/env python3
"""Ticket 293 -- the cluster/face census behind the three Phase-A pictures and the eight Phase-B rows.

Reads only what job A left in the run directory (out/diag/*.diag276.txt, out/axis/*.xyz, out/geom/*,
out/pieces_run.tsv) and the frozen corpus (read-only). Writes tables under out/; no geometry.

Instrument of ticket 278/286:
  - region_stats (ticket 279): 36 azimuth bins in the axis frame, bins10, edge_r = median p95 radius,
    edge_cv = std(p95)/mean(p95), l3/l1 = smallest/largest covariance eigenvalue, axsp = t95-t5.
  - cluster_table (ticket 278): size, radial/axial percentiles, |n.rad| |n.ax| from PCA normals,
    angbins, l2/l1, l3/l1.
  - boundary statistic (ticket 286): largest angular gap over kept-cluster points within 4 mm, 108 deg
    as the boundary threshold.
  - reference-to-mesh (ticket 294): exact point-to-triangle distance, here for OUR dots at a stretch.
"""
import os
import sys
import json
import math
import struct
import numpy as np
from scipy.spatial import cKDTree

RUN = os.path.abspath(sys.argv[1])
CORP = "/data/gpfs/projects/punim2657/sfs_main/original_samples/SfS_pp"
OUT = os.path.join(RUN, "out")
PHASE_A = [("Pot_C_Piece_03", 1), ("Pot_I_Piece_25", 0), ("Pot_I_Piece_25", 1)]
PHASE_B = [("Pot_D_Piece_22", 0), ("Pot_D_Piece_27", 0), ("Pot_D_Piece_27", 1),
           ("Pot_E_Piece_16", 0), ("Pot_H_Piece_02", 1), ("Pot_H_Piece_10", 1),
           ("Pot_I_Piece_06", 1), ("Pot_I_Piece_13", 1)]
BAR = 2.0
GAP_R = 4.0
GAP_DEG = 108.0
ERRORS = []


def err(msg):
    ERRORS.append(msg)
    print("[ERR] " + msg)


def q(x, p):
    x = np.asarray(x, dtype=float)
    if x.size == 0:
        return float("nan")
    return float(np.percentile(x, p))


# ---------------------------------------------------------------- readers
def read_dump(path):
    """The ticket-276 dump: '# npoints N nclusters M thetaDeg T split S', one '# cluster c size S
    surface b' per cluster, then rows 'index cluster x y z half' (-1 = in no cluster)."""
    hdr = {}
    cl = {}
    with open(path) as fh:
        for line in fh:
            if line.startswith("# npoints"):
                p = line[1:].split()
                hdr = dict(zip(p[0::2], p[1::2]))
            elif line.startswith("# cluster"):
                p = line[1:].split()
                d = dict(zip(p[0::2], p[1::2]))
                cl[int(d["cluster"])] = int(d["size"])
            elif line.startswith("#"):
                continue
            else:
                break
    a = np.loadtxt(path, comments="#", dtype=np.float64, ndmin=2)
    labels = a[:, 1].astype(int)
    P = a[:, 2:5]
    return hdr, cl, labels, P


def frame(axis_path):
    v = np.loadtxt(axis_path, dtype=float).ravel()
    p0 = np.asarray(v[0:3], dtype=float)
    w = np.asarray(v[3:6], dtype=float)
    w = w / np.linalg.norm(w)
    u = np.array([1.0, 0.0, 0.0]) - w * w[0]
    if np.linalg.norm(u) < 1e-6:
        u = np.array([0.0, 1.0, 0.0]) - w * w[1]
    u = u / np.linalg.norm(u)
    v2 = np.cross(w, u)
    return p0, w, u, v2


def axial(P, p0, w, u, v):
    d = np.asarray(P, dtype=float) - p0
    a = d @ w
    perp = d - a[:, None] * w[None, :]
    r = np.linalg.norm(perp, axis=1)
    ang = np.degrees(np.arctan2(perp @ v, perp @ u))
    return a, r, ang


def read_xyz(path):
    pts = []
    with open(path, "r", errors="ignore") as fh:
        for line in fh:
            p = line.split()
            if len(p) >= 3:
                try:
                    pts.append((float(p[0]), float(p[1]), float(p[2])))
                except ValueError:
                    continue
    return np.asarray(pts, dtype=float)


def read_pcd_xyz(path):
    """ASCII or binary PCD, field order honoured (the authors' files put normals first)."""
    fields = None; size = None; typ = None; count = None; npts = 0; data = "ascii"; off = 0
    with open(path, "rb") as fh:
        while True:
            line = fh.readline()
            if not line:
                break
            off = fh.tell()
            s = line.decode("ascii", errors="replace").strip()
            k = s.split()
            if not k:
                continue
            key = k[0].upper()
            if key == "FIELDS":
                fields = k[1:]
            elif key == "SIZE":
                size = [int(x) for x in k[1:]]
            elif key == "TYPE":
                typ = k[1:]
            elif key == "COUNT":
                count = [int(x) for x in k[1:]]
            elif key == "POINTS":
                npts = int(k[1])
            elif key == "DATA":
                data = k[1].lower()
                break
        fh.seek(off)
        if data == "ascii":
            ix, iy, iz = fields.index("x"), fields.index("y"), fields.index("z")
            pts = []
            for line in fh:
                v = line.split()
                if len(v) < 3:
                    continue
                pts.append((float(v[ix]), float(v[iy]), float(v[iz])))
            return np.asarray(pts, dtype=float)
        if count is None:
            count = [1] * len(fields)
        rec = sum(s * c for s, c in zip(size, count))
        fmts = {"F": "f", "U": "I", "I": "i"}
        tags = []
        for t, c, sz in zip(typ, count, size):
            base = fmts[t]
            tags.append(str(c) + base if c > 1 else base)
        st = struct.Struct("".join(tags))
        raw = fh.read(npts * rec)
        ix, iy, iz = fields.index("x"), fields.index("y"), fields.index("z")
        pts = [(float(r[ix]), float(r[iy]), float(r[iz])) for r in st.iter_unpack(raw)]
        return np.asarray(pts, dtype=float)


def read_obj(path):
    V = []; F = []
    with open(path, "r", errors="ignore") as fh:
        for line in fh:
            if line.startswith("v "):
                p = line.split()
                V.append((float(p[1]), float(p[2]), float(p[3])))
            elif line.startswith("f "):
                idx = [int(tok.split("/")[0]) - 1 for tok in line.split()[1:]]
                for k in range(1, len(idx) - 1):
                    F.append((idx[0], idx[k], idx[k + 1]))
    A = np.asarray(V, dtype=float)
    idx = np.asarray(F, dtype=int)
    return A, idx


def dist_point_tri(P, A, B, C):
    """Vectorised closest point from one point to many triangles (Ericson's regions)."""
    AB = B - A; AC = C - A; AP = P - A
    d1 = (AB * AP).sum(1); d2 = (AC * AP).sum(1)
    BP = P - B; d3 = (AB * BP).sum(1); d4 = (AC * BP).sum(1)
    CP = P - C; d5 = (AB * CP).sum(1); d6 = (AC * CP).sum(1)
    va = d3 * d6 - d5 * d4; vb = d5 * d2 - d1 * d6; vc = d1 * d4 - d3 * d2
    denom = va + vb + vc
    denom = np.where(np.abs(denom) < 1e-20, 1e-20, denom)
    v = vb / denom; w = vc / denom
    out = np.empty((A.shape[0], 3))
    m = (d1 <= 0) & (d2 <= 0); out[m] = A[m]
    m = (d3 >= 0) & (d4 <= d3); out[m] = B[m]
    m = (d6 >= 0) & (d5 <= d6); out[m] = C[m]
    m = (vc <= 0) & (d1 >= 0) & (d3 <= 0); t = np.where((d1 - d3) == 0, 0, d1 / (d1 - d3)); out[m] = (A + t[:, None] * AB)[m]
    m = (vb <= 0) & (d2 >= 0) & (d6 <= 0); t = np.where((d2 - d6) == 0, 0, d2 / (d2 - d6)); out[m] = (A + t[:, None] * AC)[m]
    m = (va <= 0) & ((d4 - d3) >= 0) & ((d5 - d6) >= 0); t = np.where(((d4 - d3) + (d5 - d6)) == 0, 0, (d4 - d3) / ((d4 - d3) + (d5 - d6))); out[m] = (B + t[:, None] * (C - B))[m]
    m2 = ~((d1 <= 0) & (d2 <= 0)) & ~((d3 >= 0) & (d4 <= d3)) & ~((d6 >= 0) & (d5 <= d6)) & \
         ~((vc <= 0) & (d1 >= 0) & (d3 <= 0)) & ~((vb <= 0) & (d2 >= 0) & (d6 <= 0)) & \
         ~((va <= 0) & ((d4 - d3) >= 0) & ((d5 - d6) >= 0))
    out[m2] = (A + v[:, None] * AB + w[:, None] * AC)[m2]
    return out


def mesh_distance(pts, V, idx, cap=None):
    if cap is not None and len(pts) > cap:
        sel = np.linspace(0, len(pts) - 1, cap).astype(int)
        pts = pts[sel]
    T1 = V[idx[:, 0]]; T2 = V[idx[:, 1]]; T3 = V[idx[:, 2]]
    d = []
    for p in pts:
        P = np.asarray(p, dtype=float)
        Q = dist_point_tri(P, T1, T2, T3)
        d.append(float(np.sqrt(((Q - P) ** 2).sum(1)).min()))
    return np.asarray(d, dtype=float)


# ---------------------------------------------------------------- geometry measures
def pca_normals(Q, k=20):
    n = len(Q); kk = min(k + 1, n)
    out = np.empty((n, 3), dtype=float)
    chunk = max(1, int(2000000 // max(1, n)))
    for s in range(0, n, chunk):
        e = min(n, s + chunk)
        d = Q[s:e, None, :] - Q[None, :, :]
        d2 = np.einsum("ijk,ijk->ij", d, d, optimize=True)
        part = np.argpartition(d2, kk - 1, axis=1)[:, :kk]
        pts = Q[part]
        pts = pts - pts.mean(axis=1, keepdims=True)
        cov = np.einsum("mki,mkj->mij", pts, pts) / kk
        w, v = np.linalg.eigh(cov)
        out[s:e] = v[:, :, 0]
    return out


def region_stats(P, p0, w, u, v):
    a, r, ang = axial(P, p0, w, u, v)
    b = (np.floor((ang % 360.0) / 10.0)).astype(int) % 36
    bins = [r[b == k] for k in range(36)]
    n10 = sum(1 for x in bins if len(x) >= 10)
    p95 = np.array([np.percentile(x, 95) if len(x) >= 10 else np.nan for x in bins])
    ok = ~np.isnan(p95)
    ring = np.zeros(len(P), dtype=bool)
    for k in range(36):
        if np.isnan(p95[k]):
            continue
        ring |= (b == k) & (np.abs(r - p95[k]) < 1.0)
    edge_r = float(np.median(p95[ok])) if ok.any() else float("nan")
    edge_cv = float(np.std(p95[ok]) / np.mean(p95[ok])) if ok.sum() > 2 else float("nan")
    C = P.mean(0); Qc = P - C
    ev = np.linalg.eigvalsh(Qc.T @ Qc)
    l3l1 = float(max(ev[0], 0) / ev[2]) if ev[2] > 0 else float("nan")
    l2l1 = float(max(ev[1], 0) / ev[2]) if ev[2] > 0 else float("nan")
    return dict(n=len(P), r5=q(r, 5), r50=q(r, 50), r95=q(r, 95), ax5=q(a, 5), ax50=q(a, 50),
                ax95=q(a, 95), axsp=q(a, 95) - q(a, 5), bins10=n10, edge_r=edge_r,
                edge_cv=edge_cv, l2l1=l2l1, l3l1=l3l1, ring=ring)


def gap_stats(dots, tree_k, k=80):
    """Ticket 286's boundary statistic: largest angular gap over kept-cluster points within 4 mm."""
    if len(dots) == 0:
        return np.array([])
    d, j = tree_k.query(dots, k=min(k, tree_k.n))
    out = []
    for i in range(len(dots)):
        nb = j[i][d[i] < GAP_R]
        if len(nb) < 8:
            nb = j[i][:max(8, min(20, len(j[i])))]
        Q = tree_k.data[nb] - dots[i]
        Qc = Q - Q.mean(0)
        _, _, vt = np.linalg.svd(Qc, full_matrices=False)
        e1, e2 = vt[0], vt[1]
        th = np.sort(np.degrees(np.arctan2(Q @ e2, Q @ e1)) % 360.0)
        gaps = np.diff(np.concatenate([th, th[:1] + 360.0]))
        out.append(float(gaps.max()) if len(gaps) else float("nan"))
    return np.asarray(out, dtype=float)


def polyline_length(X):
    if len(X) < 2:
        return 0.0
    return float(np.linalg.norm(np.diff(X, axis=0), axis=1).sum())


def runs(mask):
    out = []; s = None
    for i, m in enumerate(mask):
        if m and s is None:
            s = i
        if not m and s is not None:
            out.append((s, i - 1)); s = None
    if s is not None:
        out.append((s, len(mask) - 1))
    return out


def arc_between(X, i, j):
    if j <= i:
        return 0.0
    return polyline_length(X[i:j + 1])


def chord_ratio(X):
    a = polyline_length(X)
    if a <= 0:
        return float("nan")
    return float(np.linalg.norm(X[-1] - X[0]) / a)


# ---------------------------------------------------------------- per piece
def piece_inputs(piece):
    d = dict(
        dump=os.path.join(OUT, "diag", piece + ".diag276.txt"),
        axis=os.path.join(OUT, "axis", piece + ".axis.xyz"),
        s0=os.path.join(OUT, "geom", piece + ".S0.xyz"),
        s1=os.path.join(OUT, "geom", piece + ".S1.xyz"),
        bl=[os.path.join(OUT, "geom", piece + ".Bl0.pcd"),
            os.path.join(OUT, "geom", piece + ".Bl1.pcd")],
        auth=[os.path.join(CORP, "Breaklines", piece + "_Breakline_0.pcd"),
              os.path.join(CORP, "Breaklines", piece + "_Breakline_1.pcd")],
    )
    return d


def census_rows(piece, labels, P, cl, p0, w, u, v):
    kept = [c for c in (0, 1) if int((labels == c).sum()) >= 200]
    trees = {c: cKDTree(P[labels == c]) for c in kept}
    rows = []
    ids = sorted(cl.keys()) + [-1]
    for c in ids:
        mask = labels == c
        n = int(mask.sum())
        if n < 200:
            continue
        Q = P[mask]
        st = region_stats(Q, p0, w, u, v)
        N = pca_normals(Q, k=20)
        d0 = Q - p0
        perp = d0 - (d0 @ w)[:, None] * w[None, :]
        perp = perp / (np.linalg.norm(perp, axis=1)[:, None] + 1e-12)
        dot_rad = float(np.median(np.abs(np.einsum("ij,ij->i", N, perp))))
        dot_ax = float(np.median(np.abs(N @ w)))
        if c in kept:
            others = [k for k in kept if k != c]
            if others:
                K = np.concatenate([P[labels == k] for k in others])
                dk = cKDTree(K).query(Q)[0]
            else:
                dk = np.full(n, np.nan)
        else:
            K = np.concatenate([P[labels == k] for k in kept]) if kept else P
            dk = cKDTree(K).query(Q)[0]
        rows.append(dict(piece=piece, cluster=int(c), kept=bool(c in kept), size=n,
                         r5=st["r5"], r50=st["r50"], r95=st["r95"], ax5=st["ax5"],
                         ax50=st["ax50"], ax95=st["ax95"], axsp=st["axsp"], angbins=st["bins10"],
                         edge_r=st["edge_r"], edge_cv=st["edge_cv"], l2l1=st["l2l1"],
                         l3l1=st["l3l1"], n_ax=dot_ax, n_rad=dot_rad,
                         dkept_min=float(np.nanmin(dk)) if dk.size else float("nan"),
                         dkept_med=float(np.nanmedian(dk)) if dk.size else float("nan")))
    return rows, kept, trees


def assign(dots, labels, P, kept):
    d_all, j_all = cKDTree(P).query(dots)
    lab_all = labels[j_all]
    K = np.concatenate([P[labels == c] for c in kept])
    Klab = np.concatenate([labels[labels == c] for c in kept])
    d_k, j_k = cKDTree(K).query(dots)
    lab_k = Klab[j_k]
    return lab_all, d_all, lab_k, d_k


def rim_profile(Q, p0, w, u, v, line):
    """Outer (p95) and inner (p5) radius of a kept cluster per azimuth bin, against the line's own
    radius in the same bin - which boundary of that face does the line follow."""
    a, r, ang = axial(Q, p0, w, u, v)
    b = (np.floor((ang % 360.0) / 10.0)).astype(int) % 36
    _, rl, angl = axial(line, p0, w, u, v)
    bl = (np.floor((angl % 360.0) / 10.0)).astype(int) % 36
    dout = []; din = []
    for k in range(36):
        if (b == k).sum() < 10 or (bl == k).sum() < 2:
            continue
        ro = np.percentile(r[b == k], 95)
        ri = np.percentile(r[b == k], 5)
        rl_k = np.median(rl[bl == k])
        dout.append(abs(rl_k - ro)); din.append(abs(rl_k - ri))
    return dict(bins=len(dout), d_outer=q(dout, 50), d_inner=q(din, 50),
                width=q(r, 95) - q(r, 5))


def boundary_ring(Q, p0, w, u, v, line):
    """Fraction of the line's dots that sit on the cluster's outer ring (within 1 mm of the per-bin p95
    radius) - i.e. whether the line is that face's rim or something inside it."""
    a, r, ang = axial(Q, p0, w, u, v)
    b = (np.floor((ang % 360.0) / 10.0)).astype(int) % 36
    p95 = np.full(36, np.nan)
    for k in range(36):
        if (b == k).sum() >= 10:
            p95[k] = np.percentile(r[b == k], 95)
    _, rl, angl = axial(line, p0, w, u, v)
    bl = (np.floor((angl % 360.0) / 10.0)).astype(int) % 36
    ok = ~np.isnan(p95)[bl]
    if ok.sum() == 0:
        return float("nan")
    return float((np.abs(rl - p95[bl])[ok] < 1.0).mean())


def share_row(piece, lane, side, dots, labels, P, kept):
    lab_all, d_all, lab_k, d_k = assign(dots, labels, P, kept)
    n = len(dots)
    def sh(m):
        return round(100.0 * float(m.sum()) / n, 2) if n else float("nan")
    row = dict(piece=piece, lane=lane, side=side, n=n,
               c0=sh(lab_all == 0), c1=sh(lab_all == 1),
               dropped=sh(lab_all >= 2), unclustered=sh(lab_all < 0),
               kept_share=sh(lab_all == 0) + sh(lab_all == 1),
               nearest_kept_c0=sh(lab_k == 0), nearest_kept_c1=sh(lab_k == 1),
               d_all_med=round(float(np.median(d_all)), 3),
               d_kept_med=round(float(np.median(d_k)), 3))
    return row


def main():
    os.makedirs(os.path.join(OUT, "census"), exist_ok=True)
    pieces = {}
    pieces_run = os.path.join(OUT, "pieces_run.tsv")
    if os.path.exists(pieces_run):
        for line in open(pieces_run):
            v = line.rstrip("\n").split("\t")
            if len(v) >= 6:
                pieces[v[0]] = dict(pot=v[1], theta=v[2], mesh=v[3], s0=v[4], s1=v[5])
    cluster_rows = []
    census_json = dict(pieces={}, phaseA={}, phaseB={}, shares=[], errors=[])
    loaded = {}

    wanted = sorted(set([p for p, _ in PHASE_A] + [p for p, _ in PHASE_B] + list(pieces.keys())))
    for piece in wanted:
        inp = piece_inputs(piece)
        if not (os.path.exists(inp["dump"]) and os.path.exists(inp["axis"])):
            err("%s: no dump or axis (dump=%s axis=%s)" % (piece, os.path.exists(inp["dump"]), os.path.exists(inp["axis"])))
            continue
        try:
            hdr, cl, labels, P = read_dump(inp["dump"])
            p0, w, u, v = frame(inp["axis"])
            rows, kept, trees = census_rows(piece, labels, P, cl, p0, w, u, v)
            cluster_rows += rows
            loaded[piece] = dict(hdr=hdr, cl=cl, labels=labels, P=P, p0=p0, w=w, u=u, v=v,
                                 kept=kept, rows=rows,
                                 tree_k=cKDTree(np.concatenate([P[labels == c] for c in kept])) if kept else None)
            census_json["pieces"][piece] = dict(npoints=int(hdr.get("npoints", len(P))),
                                                nclusters=int(hdr.get("nclusters", len(cl))),
                                                thetaDeg=hdr.get("thetaDeg"), kept=kept, rows=rows)
        except Exception as e:
            err("%s: census failed: %r" % (piece, e))

    # ---------------- Phase A: assignment of every dot of the three lanes
    assign_rows = []
    for piece, lane in PHASE_A:
        d = loaded.get(piece)
        if d is None:
            continue
        inp = piece_inputs(piece)
        try:
            ours = read_pcd_xyz(inp["bl"][lane])
            auth = read_pcd_xyz(inp["auth"][lane])
        except Exception as e:
            err("%s Bl%d: cannot read a line: %r" % (piece, lane, e))
            continue
        for side, dots in (("ours", ours), ("authors", auth)):
            row = share_row(piece, lane, side, dots, d["labels"], d["P"], d["kept"])
            assign_rows.append(row)
        # per-dot table for the record (phase A only)
        with open(os.path.join(OUT, "census", "%s_Bl%d.assign.tsv" % (piece, lane)), "w") as fh:
            fh.write("side\ti\tx\ty\tz\tnearest_cluster\td_all_mm\tnearest_kept_cluster\td_kept_mm\n")
            for side, dots in (("ours", ours), ("authors", auth)):
                lab_all, d_all, lab_k, d_k = assign(dots, d["labels"], d["P"], d["kept"])
                for i in range(len(dots)):
                    fh.write("%s\t%d\t%.4f\t%.4f\t%.4f\t%d\t%.4f\t%d\t%.4f\n" % (
                        side, i, dots[i][0], dots[i][1], dots[i][2],
                        int(lab_all[i]), float(d_all[i]), int(lab_k[i]), float(d_k[i])))
        # which face / which boundary each line follows, and the second rim of that face
        try:
            lab_all_o, _, lab_k_o, _ = assign(ours, d["labels"], d["P"], d["kept"])
            lab_all_a, _, lab_k_a, _ = assign(auth, d["labels"], d["P"], d["kept"])
            face_o = int(np.bincount(lab_k_o, minlength=2).argmax())
            face_a = int(np.bincount(lab_k_a, minlength=2).argmax())
            Q = d["P"][d["labels"] == face_o]
            rim_o = rim_profile(Q, d["p0"], d["w"], d["u"], d["v"], ours)
            ring_o = boundary_ring(Q, d["p0"], d["w"], d["u"], d["v"], ours)
            rim_a = rim_profile(Q, d["p0"], d["w"], d["u"], d["v"], auth)
            ring_a = boundary_ring(Q, d["p0"], d["w"], d["u"], d["v"], auth)
            gap_o = gap_stats(ours, d["tree_k"]) if d["tree_k"] is not None else np.array([])
            gap_a = gap_stats(auth, d["tree_k"]) if d["tree_k"] is not None else np.array([])
            census_json["phaseA"]["%s Bl%d" % (piece, lane)] = dict(
                n_ours=int(len(ours)), n_auth=int(len(auth)),
                len_ours=round(polyline_length(ours), 2), len_auth=round(polyline_length(auth), 2),
                face_ours=face_o, face_auth=face_a, face_size_ours=int((d["labels"] == face_o).sum()),
                rim_ours=rim_o, rim_auth=rim_a, ring_share_ours=ring_o, ring_share_auth=ring_a,
                gap_med_ours=q(gap_o, 50), gap_share_gt108_ours=round(100.0 * float((gap_o > GAP_DEG).mean()), 2) if gap_o.size else None,
                gap_med_auth=q(gap_a, 50), gap_share_gt108_auth=round(100.0 * float((gap_a > GAP_DEG).mean()), 2) if gap_a.size else None)
        except Exception as e:
            err("%s Bl%d: rim/gap stats failed: %r" % (piece, lane, e))

    # ---------------- Phase B: per-lane stretch, where it is and what the surfaces say
    phaseB = []
    for piece, lane in PHASE_B:
        d = loaded.get(piece)
        if d is None:
            continue
        inp = piece_inputs(piece)
        try:
            ours = read_pcd_xyz(inp["bl"][lane])
            auth = read_pcd_xyz(inp["auth"][lane])
        except Exception as e:
            err("%s Bl%d: cannot read a line: %r" % (piece, lane, e))
            continue
        try:
            d_ours, j_ours = cKDTree(auth).query(ours)
            d_auth, j_auth = cKDTree(ours).query(auth)
            cand = []
            for (i, j) in runs(d_ours > BAR):
                arc = arc_between(ours, i, j)
                mg = float(np.mean(d_ours[i:j + 1]))
                cand.append((arc * mg, i, j, arc, mg))
            cand.sort(reverse=True)
            if not cand:
                err("%s Bl%d: no >%.1f mm stretch on our line" % (piece, lane, BAR))
                continue
            score, i0, i1, arc, mg = cand[0]
            A = ours[i0:i1 + 1]
            # the reference dots opposite our stretch
            sel = (j_auth >= i0) & (j_auth <= i1)
            X = auth[sel]
            runs_auth = [(s, e) for (s, e) in runs(d_auth > BAR)]
            best_auth = None
            if runs_auth:
                best_auth = max(runs_auth, key=lambda se: arc_between(auth, se[0], se[1]) *
                                float(np.mean(d_auth[se[0]:se[1] + 1])))
            ln_ours = polyline_length(ours); ln_auth = polyline_length(auth)
            gap_A = gap_stats(A, d["tree_k"]) if d["tree_k"] is not None else np.array([])
            gap_X = gap_stats(X, d["tree_k"]) if (d["tree_k"] is not None and len(X)) else np.array([])
            lab_A, dA_all, labk_A, dk_A = assign(A, d["labels"], d["P"], d["kept"]) if len(A) else (np.array([]),) * 4
            lab_X, dX_all, labk_X, dk_X = assign(X, d["labels"], d["P"], d["kept"]) if len(X) else (np.array([]),) * 4
            meshd = None
            try:
                mo = pieces.get(piece, {}).get("mesh")
                if mo and os.path.exists(mo):
                    V, idx = read_obj(mo)
                    meshd = mesh_distance(A, V, idx, cap=60)
            except Exception as e:
                err("%s Bl%d: our-stretch-to-authors-mesh failed: %r" % (piece, lane, e))
            row = dict(
                piece=piece, lane=lane,
                i0=int(i0), i1=int(i1), n_ours=int(len(ours)), n_auth=int(len(auth)),
                arc=round(arc, 2), share_loop=round(100.0 * arc / ln_ours, 2) if ln_ours > 0 else None,
                max_gap=round(float(np.max(d_ours[i0:i1 + 1])), 3),
                mean_gap=round(mg, 3),
                d_median_all=round(float(np.median(d_ours)), 3),
                auth_run=([int(best_auth[0]), int(best_auth[1]),
                           round(arc_between(auth, *best_auth), 2),
                           round(100.0 * arc_between(auth, *best_auth) / ln_auth, 2),
                           round(float(np.max(d_auth[best_auth[0]:best_auth[1] + 1])), 3),
                           round(float(np.mean(d_auth[best_auth[0]:best_auth[1] + 1])), 3)]
                          if best_auth else None),
                chord_ratio_ours=round(chord_ratio(A), 3) if len(A) > 1 else None,
                chord_ratio_auth=round(chord_ratio(X), 3) if len(X) > 1 else None,
                gap_med_ours=None if gap_A.size == 0 else round(q(gap_A, 50), 2),
                gap_share_gt108_ours=None if gap_A.size == 0 else round(100.0 * float((gap_A > GAP_DEG).mean()), 2),
                gap_med_auth=None if gap_X.size == 0 else round(q(gap_X, 50), 2),
                gap_share_gt108_auth=None if gap_X.size == 0 else round(100.0 * float((gap_X > GAP_DEG).mean()), 2),
                auth_dots_kept=None if len(X) == 0 else round(100.0 * float((lab_X == 0).sum() + (lab_X == 1).sum()) / len(X), 2),
                auth_dots_c0=None if len(X) == 0 else round(100.0 * float((lab_X == 0).mean()), 2),
                auth_dots_c1=None if len(X) == 0 else round(100.0 * float((lab_X == 1).mean()), 2),
                auth_dots_dropped=None if len(X) == 0 else round(100.0 * float((lab_X >= 2).mean()), 2),
                auth_dots_unclustered=None if len(X) == 0 else round(100.0 * float((lab_X < 0).mean()), 2),
                auth_dkept_med=None if len(X) == 0 else round(float(np.median(dk_X)), 3),
                ours_dkept_med=None if len(A) == 0 else round(float(np.median(dk_A)), 3),
                ours_to_authors_mesh_med=None if meshd is None else round(float(np.median(meshd)), 3),
                ours_to_authors_mesh_max=None if meshd is None else round(float(np.max(meshd)), 3),
                ours_to_authors_mesh_gt2=None if meshd is None else round(100.0 * float((meshd > 2.0).mean()), 2),
            )
            phaseB.append(row)
            census_json["phaseB"]["%s Bl%d" % (piece, lane)] = row
        except Exception as e:
            err("%s Bl%d: lane stats failed: %r" % (piece, lane, e))

    # ---------------- self-check against ticket 286's published table (old dumps, same pieces)
    old = "/data/gpfs/projects/punim2657/SfSpp/runs/20261024-1223_0ab0935_p276-phase3a/out"
    sc = []
    for piece, sub in (("Pot_H_Piece_02", "H02_diag"), ("Pot_H_Piece_10", "H10_diag")):
        p = os.path.join(old, sub, "mergeDiag276_" + piece + ".txt")
        ax = os.path.join(OUT, "axis", piece + ".axis.xyz")
        if not (os.path.exists(p) and os.path.exists(ax)):
            sc.append("%s: skipped (dump %s, axis %s)" % (piece, os.path.exists(p), os.path.exists(ax)))
            continue
        try:
            hdr, cl, labels, P = read_dump(p)
            p0, w, u, v = frame(ax)
            rows, kept, _ = census_rows(piece, labels, P, cl, p0, w, u, v)
            sc.append("== %s (%s) npoints=%s kept=%s" % (piece, os.path.basename(p), hdr.get("npoints"), kept))
            for r in rows:
                sc.append("c%-3d %6d kept=%d rad %.1f/%.1f/%.1f ax %.1f/%.1f/%.1f |n.ax| %.3f angbins %2d l2/l1 %.4f l3/l1 %.4f dkept %.3f" % (
                    r["cluster"], r["size"], 1 if r["kept"] else 0, r["r5"], r["r50"], r["r95"],
                    r["ax5"], r["ax50"], r["ax95"], r["n_ax"], r["angbins"], r["l2l1"], r["l3l1"], r["dkept_med"]))
        except Exception as e:
            sc.append("%s: self-check failed: %r" % (piece, e))

    # ---------------- write the tables
    with open(os.path.join(OUT, "clusters.tsv"), "w") as fh:
        cols = ["piece", "cluster", "kept", "size", "r5", "r50", "r95", "ax5", "ax50", "ax95", "axsp",
                "angbins", "edge_r", "edge_cv", "l2l1", "l3l1", "n_ax", "n_rad", "dkept_min", "dkept_med"]
        fh.write("\t".join(cols) + "\n")
        for r in cluster_rows:
            fh.write("\t".join([str(r[c]) if not isinstance(r[c], float) else "%.4f" % r[c] for c in cols]) + "\n")
    with open(os.path.join(OUT, "assign_summary.tsv"), "w") as fh:
        cols = ["piece", "lane", "side", "n", "c0", "c1", "dropped", "unclustered", "kept_share",
                "nearest_kept_c0", "nearest_kept_c1", "d_all_med", "d_kept_med"]
        fh.write("\t".join(cols) + "\n")
        for r in assign_rows:
            fh.write("\t".join(str(r[c]) for c in cols) + "\n")
    with open(os.path.join(OUT, "phaseB.tsv"), "w") as fh:
        if phaseB:
            cols = list(phaseB[0].keys())
            fh.write("\t".join(cols) + "\n")
            for r in phaseB:
                fh.write("\t".join("" if r[c] is None else str(r[c]) for c in cols) + "\n")
    census_json["errors"] = ERRORS
    with open(os.path.join(OUT, "census.json"), "w") as fh:
        json.dump(census_json, fh, indent=1)
    with open(os.path.join(OUT, "selfcheck286.txt"), "w") as fh:
        fh.write("\n".join(sc) + "\n")
    print("\n".join(sc[-14:]))
    print("[CENSUS] pieces=%d clusters=%d assign rows=%d phaseB rows=%d errors=%d" % (
        len(loaded), len(cluster_rows), len(assign_rows), len(phaseB), len(ERRORS)))


main()
