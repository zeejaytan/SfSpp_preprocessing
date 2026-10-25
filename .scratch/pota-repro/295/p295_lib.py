#!/usr/bin/env python3
"""Ticket 295 -- the shared instrument.

Every reader and every geometry measure that ticket 293 also used is COPIED VERBATIM from
.scratch/pota-repro/293/p293_census.py (read_dump, frame, axial, read_xyz, read_pcd_xyz, read_obj,
dist_point_tri, mesh_distance, gap_stats, polyline_length, runs, chord_ratio, q). Copying rather than
importing is deliberate: an import would drag in 293's module-level sys.argv[1] and its PHASE_A /
PHASE_B tables, and the point of the copy is that a number this ticket quotes from 293 must come out
of the same code path, not out of a re-derivation.

Added here (293 has no equivalent):
  read_xyz6      the authors' Surface_<k>.xyz carries per-point normals in columns 4-6;
  radial_unit    the unit outward radial direction r_hat of the axis frame;
  plane_fit      total-least-squares plane (centroid + normal + rms) -- "the face's dominant plane";
  local_normals  PCA normal per point of a subset, k=20 (ticket 278 validated k=20 against the PCD
                 normals at median |dot| 0.9990-0.9999), same covariance as 293's pca_normals;
  boundary_mask  ticket 286/280's boundary statistic applied per point of a point set.
"""
import os
import struct
import numpy as np
from scipy.spatial import cKDTree

CORP = "/data/gpfs/projects/punim2657/sfs_main/original_samples/SfS_pp"
BAR = 2.0          # mm, the edgeline bar (ticket 292/294 scorer)
GAP_R = 4.0        # mm, the boundary statistic's neighbourhood radius (ticket 286)
GAP_DEG = 108.0    # deg, 293's boundary threshold
GAP_DEG_100 = 100.0  # deg, ticket 295's Q3 wording


def q(x, p):
    x = np.asarray(x, dtype=float)
    if x.size == 0:
        return float("nan")
    return float(np.percentile(x, p))


# ---------------------------------------------------------------- readers (293 verbatim)
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


def read_xyz6(path):
    """The authors' Surface_<k>.xyz: x y z nx ny nz. Normals returned as given (not normalised)."""
    a = np.loadtxt(path, dtype=float, ndmin=2)
    P = a[:, 0:3]
    N = a[:, 3:6] if a.shape[1] >= 6 else np.full((len(a), 3), np.nan)
    return P, N


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
                p = line.decode("ascii", errors="replace").split()
                if len(p) < 3:
                    continue
                try:
                    pts.append((float(p[ix]), float(p[iy]), float(p[iz])))
                except ValueError:
                    continue
            return np.asarray(pts, dtype=float)
        tmap = {"F": "f", "U": "u", "I": "i"}
        fmt = "<" + "".join(tmap[t] for t in typ)
        rec = struct.calcsize(fmt)
        raw = fh.read(npts * rec)
        st = struct.Struct(fmt)
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
def gap_stats(dots, tree_k, k=80):
    """Ticket 286/280's boundary statistic: largest angular gap over points within 4 mm."""
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


def chord_ratio(X):
    a = polyline_length(X)
    if a <= 0:
        return float("nan")
    return float(np.linalg.norm(X[-1] - X[0]) / a)


def radial_unit(P, p0, w):
    """Unit outward radial direction r_hat (away from the axis) and the perpendicular radius."""
    d = np.asarray(P, dtype=float) - p0
    a = d @ w
    perp = d - a[:, None] * w[None, :]
    r = np.linalg.norm(perp, axis=1)
    return perp / (r[:, None] + 1e-12), r


def plane_fit(Q):
    """Total-least-squares plane: centroid, unit normal (smallest eigenvector), rms residual (mm)."""
    Q = np.asarray(Q, dtype=float)
    C = Q.mean(0)
    X = Q - C
    ev, evec = np.linalg.eigh(X.T @ X)
    nrm = evec[:, 0] / np.linalg.norm(evec[:, 0])
    return C, nrm, float(np.sqrt(max(ev[0], 0.0) / max(len(Q), 1)))


def local_normals(Q, tree, k=20):
    """PCA normal per point of Q from its k nearest neighbours among tree.data (self included).

    Same covariance as 293's pca_normals (kk = k+1 for self), without its O(n^2) chunking: the
    neighbours come from a KD-tree instead of an argpartition over the whole set."""
    kk = min(k + 1, tree.n)
    d, j = tree.query(Q, k=kk)
    pts = tree.data[j]
    pts = pts - pts.mean(axis=1, keepdims=True)
    cov = np.einsum("mki,mkj->mij", pts, pts) / kk
    ev, evec = np.linalg.eigh(cov)
    return evec[:, :, 0]


def boundary_mask(points, gap_deg=GAP_DEG_100, k=80):
    """Per-point boundary flag of a point set: ticket 280's >100 deg tangent-plane angular gap."""
    g = gap_stats(points, cKDTree(points), k=k)
    return g, (g > gap_deg)


def kept_clusters(labels):
    """293's rule: the survivor clusters the merge kept are 0 and 1, each of at least 200 points."""
    return [c for c in (0, 1) if int((labels == c).sum()) >= 200]


def write_tsv(path, rows, cols=None):
    if not rows:
        open(path, "w").close()
        return
    cols = cols or list(rows[0].keys())
    with open(path, "w") as fh:
        fh.write("\t".join(cols) + "\n")
        for r in rows:
            fh.write("\t".join(fmt(r.get(c, "")) for c in cols) + "\n")


def fmt(v):
    if isinstance(v, float):
        return "nan" if v != v else f"{v:.4f}"
    return str(v)
