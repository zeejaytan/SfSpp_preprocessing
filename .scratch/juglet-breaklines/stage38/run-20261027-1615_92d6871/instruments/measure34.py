#!/usr/bin/env python3
"""ticket 34 measurement.  Tables only: nothing here writes or keeps geometry.

Readers are field-name based on purpose.  Two earlier tickets were killed by a reader that
assumed a column order or a column count: io32.py mis-read the released clouds (their FIELDS
line is "normal_x normal_y normal_z x y z _", normals FIRST, with a COUNT=4 padding field)
and ticket 20 died on KeyError 'normal_x'.  So: parse the header, pick x/y/z and the normals
BY NAME, and build the numpy dtype from SIZE/TYPE/COUNT, so a varying column count is fine.

subcommands
  selftest                        readers and geometry against synthetic truth
  cell      --cell DIR ...        one finished cell -> DIR/measure/*.tsv
  agg       --cellroot DIR --out  every cell's tables -> <out>/*.tsv
  defaults  --orig DIR --new DIR  the defaults proof over two arm directories
"""
import argparse
import os
import sys

import numpy as np
from scipy.spatial import cKDTree

COINCIDENCE_MM = 1e-3
FOLD_EPS = 1e-12
NORM_PCA_K = 10


def warn(msg):
    sys.stderr.write("[M34] %s\n" % msg)


# ------------------------------------------------------------------ readers
def _pcd_header(path):
    hdr = {}
    with open(path, "rb") as f:
        while True:
            raw = f.readline()
            if not raw:
                raise ValueError("no DATA line in %s" % path)
            line = raw.decode("ascii", "replace").strip()
            if not line or line.startswith("#"):
                continue
            tok = line.split()
            key = tok[0].upper()
            hdr[key] = tok[1:]
            if key == "DATA":
                hdr["_offset"] = f.tell()
                hdr["_mode"] = tok[1].lower() if len(tok) > 1 else "ascii"
                break
    return hdr


def _pcd_dtype(hdr):
    fields = hdr["FIELDS"]
    sizes = [int(x) for x in hdr.get("SIZE", ["4"] * len(fields))]
    types = [t.upper() for t in hdr.get("TYPE", ["F"] * len(fields))]
    counts = [int(x) for x in hdr.get("COUNT", ["1"] * len(fields))]
    code = {("F", 4): "<f4", ("F", 8): "<f8",
            ("U", 1): "u1", ("U", 2): "<u2", ("U", 4): "<u4", ("U", 8): "<u8",
            ("I", 1): "i1", ("I", 2): "<i2", ("I", 4): "<i4", ("I", 8): "<i8"}
    out = []
    for name, size, typ, cnt in zip(fields, sizes, types, counts):
        key = (typ, size)
        if key not in code:
            raise ValueError("PCD field %s: unsupported TYPE/SIZE %s/%d" % (name, typ, size))
        if cnt == 1:
            out.append((name, code[key]))
        else:
            out.append((name, code[key], (cnt,)))
    return out


def read_pcd(path, maxpts=0):
    """-> dict(xyz=(N,3) float64, normals=(N,3)|None, n=int, strided=bool)."""
    hdr = _pcd_header(path)
    fields = [f.lower() for f in hdr["FIELDS"]]
    counts = [int(x) for x in hdr.get("COUNT", ["1"] * len(fields))]
    mode = hdr["_mode"]
    if mode == "ascii":
        with open(path, "r", errors="replace") as f:
            for line in f:
                if line.upper().startswith("DATA"):
                    break
            rows = [ln.split() for ln in f if ln.strip() and not ln.startswith("#")]
        idx = {}
        base = 0
        for name, cnt in zip(fields, counts):
            idx[name] = list(range(base, base + cnt))
            base += cnt
        arr = np.array(rows, dtype=np.float64)
        if arr.ndim != 2 or arr.shape[1] < base:
            raise ValueError("PCD %s: ascii rows carry %d columns, header wants %d"
                             % (path, arr.shape[1] if arr.ndim == 2 else -1, base))
        pick = lambda nm: arr[:, idx[nm][0]] if nm in idx else None
        x, y, z = pick("x"), pick("y"), pick("z")
        if x is None or y is None or z is None:
            raise ValueError("PCD %s: no x/y/z field (FIELDS=%s)" % (path, fields))
        xyz = np.stack([x, y, z], axis=1)
        nx, ny, nz = pick("normal_x"), pick("normal_y"), pick("normal_z")
        nrm = np.stack([nx, ny, nz], axis=1) if (nx is not None and ny is not None and nz is not None) else None
    elif mode.startswith("binary"):
        dt = np.dtype(_pcd_dtype(hdr))
        npts = int(hdr.get("POINTS", hdr.get("WIDTH", ["0"]))[0])
        with open(path, "rb") as f:
            f.seek(hdr["_offset"])
            buf = f.read()
        if len(buf) < dt.itemsize * npts:
            npts = len(buf) // dt.itemsize
            warn("PCD %s: only %d whole records" % (path, npts))
        rec = np.frombuffer(buf[:dt.itemsize * npts], dtype=dt, count=npts)
        names = set(str(nm).lower() for nm in dt.names)
        for nm in ("x", "y", "z"):
            if nm not in names:
                raise ValueError("PCD %s: no %s field (FIELDS=%s)" % (path, nm, fields))
        xyz = np.stack([rec["x"], rec["y"], rec["z"]], axis=1).astype(np.float64)
        if {"normal_x", "normal_y", "normal_z"} <= names:
            nrm = np.stack([rec["normal_x"], rec["normal_y"], rec["normal_z"]],
                           axis=1).astype(np.float64)
        else:
            nrm = None
    else:
        raise ValueError("PCD %s: DATA %s not supported" % (path, mode))
    n = len(xyz)
    strided = False
    if maxpts and n > maxpts:
        sel = np.linspace(0, n - 1, maxpts).astype(np.int64)
        xyz = xyz[sel]
        nrm = nrm[sel] if nrm is not None else None
        strided = True
    return {"xyz": xyz, "normals": nrm, "n": n, "strided": strided}


_PLY_T = {"float": "<f4", "float32": "<f4", "double": "<f8", "float64": "<f8",
          "uchar": "u1", "uint8": "u1", "char": "i1", "int8": "i1",
          "short": "<i2", "int16": "<i2", "ushort": "<u2", "uint16": "<u2",
          "int": "<i4", "int32": "<i4", "uint": "<u4", "uint32": "<u4"}


def read_ply(path):
    """-> dict of float64 arrays keyed by property name.  ascii and binary_little_endian;
    elements other than 'vertex' are skipped (PCL appends an element camera)."""
    with open(path, "rb") as f:
        fmt = None
        elements = []
        while True:
            raw = f.readline()
            if not raw:
                raise ValueError("PLY %s: no end_header" % path)
            line = raw.decode("ascii", "replace").strip()
            if line.startswith("format"):
                fmt = line.split()[1]
            elif line.startswith("element"):
                tok = line.split()
                elements.append((tok[1], int(tok[2]), []))
            elif line.startswith("property"):
                tok = line.split()
                if tok[1] == "list":
                    elements[-1][2].append((tok[-1].lower(), "list"))
                else:
                    elements[-1][2].append((tok[2].lower(), tok[1].lower()))
            elif line == "end_header":
                body = f.tell()
                break
    if fmt not in ("ascii", "binary_little_endian"):
        raise ValueError("PLY %s: format %s not supported" % (path, fmt))
    vtx = None
    for name, count, props in elements:
        if name == "vertex":
            vtx = (count, props)
            break
    if vtx is None:
        raise ValueError("PLY %s: no vertex element" % path)
    count, props = vtx
    names = [q[0] for q in props]
    if fmt == "ascii":
        with open(path, "r", errors="replace") as f:
            f.seek(body)
            rows = []
            for ln in f:
                if len(rows) >= count:
                    break
                if ln.strip():
                    rows.append(ln.split())
        arr = np.array(rows, dtype=np.float64)
        return {nm: arr[:, i] for i, nm in enumerate(names)}
    dt = np.dtype([(q[0], _PLY_T[q[1]]) for q in props])
    with open(path, "rb") as f:
        f.seek(body)
        buf = f.read(dt.itemsize * count)
    if len(buf) < dt.itemsize * count:
        count = len(buf) // dt.itemsize
        warn("PLY %s: only %d vertices" % (path, count))
    rec = np.frombuffer(buf[:dt.itemsize * count], dtype=dt, count=count)
    return {nm: np.asarray(rec[nm], dtype=np.float64) for nm in names}


def ply_normals(d):
    for trio in (("nx", "ny", "nz"), ("normal_x", "normal_y", "normal_z")):
        if all(k in d for k in trio):
            return np.stack([d[trio[0]], d[trio[1]], d[trio[2]]], axis=1)
    return None


def ply_xyz(d):
    return np.stack([d["x"], d["y"], d["z"]], axis=1)


def unit(v, axis=-1):
    n = np.linalg.norm(v, axis=axis, keepdims=True)
    n = np.where(n < FOLD_EPS, np.inf, n)
    return v / n


def pca_normals(pts, k=NORM_PCA_K):
    """PCL-style normals and curvature from k neighbours (smallest eigenvector; curvature
    lambda0 / sum lambda).  Used only where a file carries no normals of its own, and the
    table records that it did."""
    k = int(min(max(3, k), len(pts)))
    _d, idx = cKDTree(pts).query(pts, k=k)
    nb = pts[idx]
    nb = nb - nb.mean(axis=1, keepdims=True)
    cov = np.einsum("nki,nkj->nij", nb, nb)
    w, v = np.linalg.eigh(cov)
    s = w.sum(axis=1)
    s = np.where(s < FOLD_EPS, np.inf, s)
    return v[:, :, 0], w[:, 0] / s


def read_obj(path):
    """Vertices and area-weighted per-vertex normals of a Wavefront OBJ (n-gons are
    fan-triangulated).  Same arithmetic as ticket 30's analyse30.py, so these numbers stay
    comparable with the 3.39-8.10 deg / 0.414-1.635 deg already on record."""
    verts = []
    faces = []
    with open(path, "r", errors="replace") as f:
        for line in f:
            if line.startswith("v "):
                t = line.split()
                verts.append((float(t[1]), float(t[2]), float(t[3])))
            elif line.startswith("f "):
                idx = []
                for tok in line.split()[1:]:
                    head = tok.split("/")[0]
                    if not head:
                        continue
                    i = int(head)
                    idx.append(i - 1 if i > 0 else len(verts) + i)
                for a in range(1, len(idx) - 1):
                    faces.append((idx[0], idx[a], idx[a + 1]))
    v = np.asarray(verts, dtype=np.float64)
    fc = np.asarray(faces, dtype=np.int64)
    if fc.size == 0:
        raise ValueError("OBJ %s: no faces" % path)
    p0, p1, p2 = v[fc[:, 0]], v[fc[:, 1]], v[fc[:, 2]]
    fn = np.cross(p1 - p0, p2 - p0)
    vn = np.zeros_like(v)
    for c in range(3):
        np.add.at(vn, fc[:, c], fn)
    return v, unit(vn)


def folded_angle_deg(nrm, ref):
    d = np.abs(np.einsum("ij,ij->i", unit(nrm), unit(ref)))
    return np.degrees(np.arccos(np.clip(d, 0.0, 1.0)))


def median_fold_to_mesh(pts, nrm, verts, vnorm):
    _d, near = cKDTree(verts).query(pts, k=1)
    return float(np.median(folded_angle_deg(nrm, vnorm[near])))


def coverage_fraction(surface_pts, cloud_pts, radius=2.0):
    d, _i = cKDTree(surface_pts).query(cloud_pts, k=1)
    return float(np.count_nonzero(d <= radius)) / float(len(cloud_pts))


def surface_row(path, cloud_xyz, verts, vnorm):
    d = read_ply(path)
    pts = ply_xyz(d)
    nrm = ply_normals(d)
    src = "ply"
    if nrm is None:
        nrm, _c = pca_normals(pts, NORM_PCA_K)
        src = "pca%d" % NORM_PCA_K
    lo, hi = pts.min(axis=0), pts.max(axis=0)
    return {"points": int(len(pts)),
            "ext_x": float(hi[0] - lo[0]), "ext_y": float(hi[1] - lo[1]),
            "ext_z": float(hi[2] - lo[2]),
            "diag": float(np.linalg.norm(hi - lo)),
            "cov_2mm": coverage_fraction(pts, cloud_xyz),
            "fold_deg": median_fold_to_mesh(pts, nrm, verts, vnorm),
            "normal_src": src}


def pair_stats(p0, n0, p1, n1):
    """Corrected pair statistic (ticket 24 retired the mean-normal dot test): for every
    Surface_1 point take the nearest Surface_0 point and split that step along Surface_0's
    own normal and across it."""
    d, idx = cKDTree(p0).query(p1, k=1)
    v = p1 - p0[idx]
    a = unit(n0)[idx]
    along = np.abs(np.einsum("ij,ij->i", v, a))
    across = np.linalg.norm(v - along[:, None] * a, axis=1)
    return {"n0": int(len(p0)), "n1": int(len(p1)),
            "med_nn": float(np.median(d)),
            "med_along": float(np.median(along)), "p90_along": float(np.percentile(along, 90)),
            "med_across": float(np.median(across)),
            "p90_across": float(np.percentile(across, 90)),
            "coin": float(np.count_nonzero(d <= COINCIDENCE_MM)) / float(len(p1))}


# ------------------------------------------------------------------ replay
def _k2_avg(cloud, ctree, mem, normals, qid, k2):
    """C++ k2AvgNormal234: the k2 nearest points *within the cluster*, normals averaged,
    renormalised."""
    K = int(min(k2, len(mem)))
    _d, rr = ctree.query(cloud[qid], k=K)
    m = normals[mem[np.atleast_1d(rr)]].sum(axis=0)
    ln = np.linalg.norm(m)
    return m / ln if ln > 1e-9 else np.array([0.0, 0.0, 1.0])


def _median_internal(cloud, mem, axis):
    if len(mem) == 0:
        return -1
    m = cloud[mem].mean(axis=0)
    ln = np.linalg.norm(axis)
    an = axis / ln if ln > 1e-9 else np.array([0.0, 0.0, 1.0])
    w = cloud[mem] - m
    along = w @ an
    perp = np.linalg.norm(w - along[:, None] * an, axis=1)
    order = np.lexsort((mem, perp))
    return int(mem[order[len(order) // 2]])


def try_pair(cloud, normals, curv, A, B, isb, axisA, axisB,
             rhoD, rhoN, rhoC, rhoInN, rhoInC, k2, minPairs):
    """One pair verdict, gate for gate in the binary's own order.  'gate' is the criterion
    that refused the pair (or 'merge')."""
    out = {"pairs": 0, "dot": float("nan"), "curv_A": float("nan"), "curv_B": float("nan"),
           "in_dot": float("nan"), "in_cdiff": float("nan"), "gate": ""}
    bA, bB = A[isb[A]], B[isb[B]]
    if len(bA) == 0 or len(bB) == 0:
        out["gate"] = "no_boundary"
        return out
    if len(bA) > len(bB):
        sP, lP, s_is_a = bB, bA, False
    else:
        sP, lP, s_is_a = bA, bB, True
    lt = cKDTree(cloud[lP])
    pairs = []
    for sid in sP:
        if len(pairs) >= 200:
            break
        d, k = lt.query(cloud[sid], k=1)
        if float(d) * float(d) <= rhoD * rhoD:
            pairs.append((sid, lP[int(k)]) if s_is_a else (lP[int(k)], sid))
    out["pairs"] = len(pairs)
    if len(pairs) < minPairs:
        out["gate"] = "min_pairs"
        return out
    tA, tB = cKDTree(cloud[A]), cKDTree(cloud[B])
    sNA = np.zeros(3)
    sNB = np.zeros(3)
    sCA = 0.0
    sCB = 0.0
    for pa, pb in pairs:
        sNA += _k2_avg(cloud, tA, A, normals, pa, k2)
        sNB += _k2_avg(cloud, tB, B, normals, pb, k2)
        sCA += curv[pa]
        sCB += curv[pb]
    nA, nB = np.linalg.norm(sNA), np.linalg.norm(sNB)
    if nA < 1e-9 or nB < 1e-9:
        out["gate"] = "degenerate"
        return out
    sNA /= nA
    sNB /= nB
    out["dot"] = float(np.dot(sNA, sNB))
    if np.dot(sNA, sNB) < rhoN:
        out["gate"] = "rhoN"
        return out
    out["curv_A"] = sCA / len(pairs)
    out["curv_B"] = sCB / len(pairs)
    if abs(sCA / len(pairs) - sCB / len(pairs)) >= rhoC:
        out["gate"] = "rhoC"
        return out
    ia = _median_internal(cloud, A, axisA)
    ib = _median_internal(cloud, B, axisB)
    if ia < 0 or ib < 0:
        out["gate"] = "internal"
        return out
    na, nb = normals[ia], normals[ib]
    la, lb = np.linalg.norm(na), np.linalg.norm(nb)
    if la < 1e-9 or lb < 1e-9:
        out["gate"] = "degenerate_in"
        return out
    out["in_dot"] = float(np.dot(na, nb) / (la * lb))
    if np.dot(na, nb) / (la * lb) < rhoInN:
        out["gate"] = "rhoInN"
        return out
    out["in_cdiff"] = float(abs(curv[ia] - curv[ib]))
    if abs(curv[ia] - curv[ib]) >= rhoInC:
        out["gate"] = "rhoInC"
        return out
    out["gate"] = "merge"
    return out


def replay_merge(cloud, normals, curv, cid, thr, minPairs, max_pass=25):
    """Offline replay of mergePaper234 over the pre-merge cluster ids the binary dumped at
    rung 2.  Positions and normals are the binary's own; CURVATURE IS RECOMPUTED here with
    PCL's k = clamp(npts/300, 10, 50), because rung 2 carries no curvature column -- the two
    curvature gates are replay values and the table says so."""
    clusters = [np.nonzero(cid == c)[0] for c in sorted(set(np.asarray(cid, dtype=int).tolist())) if c >= 0]
    k1 = max(1, int(thr["k1"]))
    rows = []
    pass_i = 0
    while pass_i < max_pass and len(clusters) > 1:
        pass_i += 1
        member = np.full(len(cloud), -1, dtype=np.int64)
        for ci, mem in enumerate(clusters):
            member[mem] = ci
        live = np.nonzero(member >= 0)[0]
        isb = np.zeros(len(cloud), dtype=bool)
        kk = int(min(k1 + 1, len(cloud)))
        _dd, nb = cKDTree(cloud).query(cloud[live], k=kk)
        for r, p in enumerate(live):
            ns = np.atleast_1d(nb[r])
            other = ns[ns != p]
            if len(other) and np.any(member[other] != member[p]):
                isb[p] = True
        axes = []
        for mem in clusters:
            c = cloud[mem] - cloud[mem].mean(axis=0)
            _w, v = np.linalg.eigh(c.T @ c)
            axes.append(v[:, 2])
        dead = np.zeros(len(clusters), dtype=bool)
        merged_any = False
        for i in range(len(clusters)):
            if dead[i]:
                continue
            for j in range(i + 1, len(clusters)):
                if dead[j]:
                    continue
                v = try_pair(cloud, normals, curv, clusters[i], clusters[j], isb,
                             axes[i], axes[j], thr["rhoD"], thr["rhoN"], thr["rhoC"],
                             thr["rhoInN"], thr["rhoInC"], thr["k2"], minPairs)
                v.update({"pass": pass_i, "i": i, "j": j,
                          "size_i": int(len(clusters[i])), "size_j": int(len(clusters[j]))})
                rows.append(v)
                if v["gate"] == "merge":
                    clusters[i] = np.concatenate([clusters[i], clusters[j]])
                    dead[j] = True
                    merged_any = True
        if not merged_any:
            break
        clusters = [c for ci, c in enumerate(clusters) if not dead[ci]]
    return rows, len(clusters)


# ------------------------------------------------------------------ log
def kv(line):
    d = {}
    for tok in line.split():
        if "=" in tok:
            k, v = tok.split("=", 1)
            d[k] = v
    return d


def parse_log(path):
    info = {"paper": {}, "count": {}, "floor": {}, "retry": [], "status": {},
            "normal": [], "passes": []}
    if not os.path.exists(path):
        return info
    with open(path, "r", errors="replace") as f:
        for line in f:
            if "[PAPER-234] appendix-A merge:" in line:
                info["paper"] = kv(line.split("merge:", 1)[1])
            elif "[COUNT-22] merge k1=" in line:
                info["count"] = kv(line.split("[COUNT-22]", 1)[1])
            elif "[FLOOR-23]" in line:
                info["floor"] = kv(line.split("[FLOOR-23]", 1)[1])
            elif "[RETRY-23]" in line:
                info["retry"].append(kv(line.split("[RETRY-23]", 1)[1]))
            elif "[STATUS-23]" in line:
                info["status"] = kv(line.split("[STATUS-23]", 1)[1])
            elif "[NORMAL-33]" in line:
                info["normal"].append(kv(line.split("[NORMAL-33]", 1)[1]))
            elif "[PAPER-234] pass" in line:
                info["passes"].append(line.strip())
    return info


def pick(y, *names):
    for n in names:
        if n in y and y[n] is not None:
            return y[n]
    return None


def thresholds_from(info):
    p = info["paper"]
    c = info["count"]
    if not p or "rhoD" not in p:
        return None
    try:
        thr = {"rhoD": float(p["rhoD"]), "rhoN": float(p["rhoN"]), "rhoC": float(p["rhoC"]),
               "rhoInN": float(p["rhoInN"]), "rhoInC": float(p["rhoInC"]),
               "k1": int(float(c.get("k1", p.get("k1", 10)))),
               "k2": int(float(c.get("k2", p.get("k2", 30))))}
    except (KeyError, ValueError):
        return None
    return thr


def dump_dir(cell, piece):
    for cand in (os.path.join(cell, "dump", piece), os.path.join(cell, "dump", piece.split("_")[-1]),
                 os.path.join(cell, "dump")):
        if os.path.isdir(cand):
            return cand
    return os.path.join(cell, "dump", piece)


# ------------------------------------------------------------------ tsv
def write_tsv(path, rows, cols=None):
    if not rows:
        return 0
    cols = cols or list(rows[0].keys())
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    with open(path, "w") as f:
        f.write("\t".join(cols) + "\n")
        for r in rows:
            vals = []
            for c in cols:
                v = r.get(c, "")
                if isinstance(v, float):
                    vals.append("%.6f" % v)
                else:
                    vals.append(str(v))
            f.write("\t".join(vals) + "\n")
    return len(rows)


def read_tsv(path):
    with open(path) as f:
        lines = [ln.rstrip("\n") for ln in f if ln.strip()]
    if not lines:
        return [], []
    head = lines[0].split("\t")
    return head, [dict(zip(head, ln.split("\t"))) for ln in lines[1:]]


# ------------------------------------------------------------------ subcommands
def cell(a):
    mdir = os.path.join(a.cell, "measure")
    os.makedirs(mdir, exist_ok=True)
    info = parse_log(os.path.join(a.cell, "logs", "mesh.log"))
    cloud = read_pcd(a.cloud, maxpts=a.maxpts)
    verts, vnorm = read_obj(a.mesh)
    warn("cell %s/%s/%s cloud=%d(%s) mesh_v=%d" % (a.arm, a.pot, a.piece, cloud["n"],
                                                   "strided" if cloud["strided"] else "all", len(verts)))

    srows = []
    got = {}
    for k in (0, 1):
        p = os.path.join(a.cell, "surfaces", "%s_Surface_%d.ply" % (a.piece, k))
        if not os.path.exists(p):
            srows.append({"surface": k, "present": 0})
            continue
        r = surface_row(p, cloud["xyz"], verts, vnorm)
        r.update({"surface": k, "present": 1})
        srows.append(r)
        got[k] = p
    write_tsv(os.path.join(mdir, "surface.tsv"), srows)

    prow = []
    if 0 in got and 1 in got:
        d0, d1 = read_ply(got[0]), read_ply(got[1])
        p0, p1 = ply_xyz(d0), ply_xyz(d1)
        n0, n1 = ply_normals(d0), ply_normals(d1)
        src = "ply"
        if n0 is None:
            n0, _c = pca_normals(p0, NORM_PCA_K)
            src = "pca%d" % NORM_PCA_K
        if n1 is None:
            n1, _c = pca_normals(p1, NORM_PCA_K)
        r = pair_stats(p0, n0, p1, n1)
        r["normal_src"] = src
        prow.append(r)
    write_tsv(os.path.join(mdir, "pairs.tsv"), prow)

    drows = []
    dd = dump_dir(a.cell, a.piece)
    for rung in ("r1_downsampled", "r2_clusters_premerge"):
        p = os.path.join(dd, rung + ".ply")
        if not os.path.exists(p):
            continue
        d = read_ply(p)
        pts = ply_xyz(d)
        nrm = ply_normals(d)
        if nrm is None:
            continue
        ln = np.linalg.norm(nrm, axis=1)
        good = ln > 1e-6
        drows.append({"rung": rung, "points": int(len(pts)),
                      "zero_normals": int(np.count_nonzero(~good)),
                      "unit_frac": float(np.mean(np.abs(ln[good] - 1.0) <= 1e-3)) if np.any(good) else 0.0,
                      "fold_deg_to_mesh": median_fold_to_mesh(pts[good], nrm[good], verts, vnorm) if np.any(good) else float("nan")})
    write_tsv(os.path.join(mdir, "carried.tsv"), drows)

    rrows = []
    p2 = os.path.join(dd, "r2_clusters_premerge.ply")
    thr = thresholds_from(info)
    if os.path.exists(p2):
        d = read_ply(p2)
        pts = ply_xyz(d)
        nrm = ply_normals(d)
        cid = np.asarray(d.get("cluster_id", np.full(len(pts), -1)), dtype=np.int64)
        live = np.nonzero(cid >= 0)[0]
        groups = {}
        for c in sorted(set(cid[live].tolist())):
            groups[int(c)] = live[cid[live] == c]
        for c, mem in sorted(groups.items()):
            rrows.append({"kind": "cluster", "cluster": c, "size": int(len(mem))})
        minp = int(float(info["paper"].get("minPairs", 3))) if info["paper"] else 3
        if thr is not None and nrm is not None and len(live):
            kc = int(max(10, min(50, len(pts) // 300)))
            nrm_all, curv_all = pca_normals(pts, kc)
            use = nrm if nrm is not None else nrm_all
            rows, nfinal = replay_merge(pts, unit(use), curv_all, cid, thr, minp)
            rrows.append({"kind": "replay_summary", "cluster": -1, "size": len(live),
                          "passes": max([r["pass"] for r in rows], default=0),
                          "tested": len(rows), "merges": sum(1 for r in rows if r["gate"] == "merge"),
                          "clusters_final": nfinal, "minPairs": minp,
                          "curv_k": kc, "curv_src": "replay_pca"})
            for r in rows:
                rrows.append(dict(r, kind="pair_verdict", cluster=-1, size=r.get("size_i", 0)))
        else:
            rrows.append({"kind": "replay_summary", "cluster": -1, "size": len(live),
                          "passes": 0, "tested": 0, "merges": 0, "clusters_final": len(groups),
                          "minPairs": minp, "curv_k": 0,
                          "curv_src": "thresholds_missing" if thr is None else "no_normals"})
    write_tsv(os.path.join(mdir, "replay.tsv"), rrows)
    print("[M34] %s/%s/%s surfaces=%d pairs=%d carried=%d replay=%d"
          % (a.arm, a.pot, a.piece, len(srows), len(prow), len(drows), len(rrows)))
    return 0


def agg(a):
    out = a.out
    os.makedirs(out, exist_ok=True)
    surf, prs, car, rep = [], [], [], []
    for tag in sorted(os.listdir(a.cellroot)):
        tdir = os.path.join(a.cellroot, tag)
        if not os.path.isdir(tdir):
            continue
        for pot in sorted(os.listdir(tdir)):
            pdir = os.path.join(tdir, pot)
            if not os.path.isdir(pdir):
                continue
            for piece in sorted(os.listdir(pdir)):
                cdir = os.path.join(pdir, piece)
                mdir = os.path.join(cdir, "measure")
                if not os.path.isdir(cdir):
                    continue
                base = {"tag": tag, "pot": pot, "piece": piece}
                for name, sink in (("surface.tsv", surf), ("pairs.tsv", prs),
                                   ("carried.tsv", car), ("replay.tsv", rep)):
                    p = os.path.join(mdir, name)
                    if not os.path.exists(p):
                        continue
                    _h, rows = read_tsv(p)
                    for r in rows:
                        r.update(base)
                        sink.append(r)
    n = 0
    for name, rows in (("surfaces34.tsv", surf), ("pairs34.tsv", prs),
                       ("carried34.tsv", car), ("replay34.tsv", rep)):
        n += write_tsv(os.path.join(out, name), rows)
    print("[M34] agg rows=%d -> %s" % (n, out))
    return 0


def _surface_paths(armdir, pot, piece):
    return {k: os.path.join(armdir, pot, piece, "surfaces", "%s_Surface_%d.ply" % (piece, k))
            for k in (0, 1)}


def _canon_points(path):
    d = read_ply(path)
    pts = np.round(ply_xyz(d), 6)
    order = np.lexsort((pts[:, 2], pts[:, 1], pts[:, 0]))
    return pts[order]


def defaults(a):
    rows = []
    for pot in sorted(os.listdir(a.new)):
        pdir = os.path.join(a.new, pot)
        if not os.path.isdir(pdir):
            continue
        for piece in sorted(os.listdir(pdir)):
            for k in (0, 1):
                pn = _surface_paths(a.new, pot, piece)[k]
                po = _surface_paths(a.orig, pot, piece)[k]
                r = {"pot": pot, "piece": piece, "surface": k,
                     "orig_present": int(os.path.exists(po)), "new_present": int(os.path.exists(pn))}
                if os.path.exists(po) and os.path.exists(pn):
                    bo = open(po, "rb").read()
                    bn = open(pn, "rb").read()
                    r["bytes_orig"] = len(bo)
                    r["bytes_new"] = len(bn)
                    r["byte_identical"] = int(bo == bn)
                    co, cn = _canon_points(po), _canon_points(pn)
                    same_n = co.shape == cn.shape
                    r["points_orig"] = int(co.shape[0])
                    r["points_new"] = int(cn.shape[0])
                    r["points_identical"] = int(same_n and np.allclose(co, cn, atol=0.0, rtol=0.0))
                    r["max_abs_diff_mm"] = float(np.max(np.abs(co - cn))) if same_n else float("nan")
                rows.append(r)
    write_tsv(a.out, rows)
    bad = [r for r in rows if r["orig_present"] and r["new_present"]
           and not (r["byte_identical"] and r["points_identical"])]
    print("[M34] defaults rows=%d non_identical=%d -> %s" % (len(rows), len(bad), a.out))
    return 0


def _write_ply(path, pts, nrm=None, extra=None):
    with open(path, "w") as f:
        f.write("ply\nformat ascii 1.0\nelement vertex %d\n" % len(pts))
        f.write("property float x\nproperty float y\nproperty float z\n")
        if nrm is not None:
            f.write("property float nx\nproperty float ny\nproperty float nz\n")
        if extra:
            for nm, _v in extra:
                f.write("property float %s\n" % nm)
        f.write("end_header\n")
        for i in range(len(pts)):
            row = ["%.6f" % pts[i, 0], "%.6f" % pts[i, 1], "%.6f" % pts[i, 2]]
            if nrm is not None:
                row += ["%.6f" % nrm[i, 0], "%.6f" % nrm[i, 1], "%.6f" % nrm[i, 2]]
            if extra:
                row += ["%d" % extra[0][1][i]]
            f.write(" ".join(row) + "\n")


def selftest():
    import tempfile
    tmp = tempfile.mkdtemp(prefix="m34-")
    bad = 0

    def check(name, cond, detail=""):
        nonlocal bad
        if cond:
            print("[SELFTEST] ok   %s %s" % (name, detail))
        else:
            print("[SELFTEST] FAIL %s %s" % (name, detail))
            bad += 1

    # 1. binary PCD with the released clouds' column order (normals first, COUNT=4 padding)
    pts = np.array([[1.0, 2.0, 3.0], [4.0, 5.0, 6.0], [-7.0, 8.0, -9.0]])
    nrm = np.array([[0.0, 0.0, 1.0], [1.0, 0.0, 0.0], [0.0, 1.0, 0.0]])
    rec = np.zeros(3, dtype=[("normal_x", "<f4"), ("normal_y", "<f4"), ("normal_z", "<f4"),
                             ("x", "<f4"), ("y", "<f4"), ("z", "<f4"), ("_", "u1", (4,))])
    rec["normal_x"], rec["normal_y"], rec["normal_z"] = nrm[:, 0], nrm[:, 1], nrm[:, 2]
    rec["x"], rec["y"], rec["z"] = pts[:, 0], pts[:, 1], pts[:, 2]
    pb = os.path.join(tmp, "released.pcd")
    with open(pb, "wb") as f:
        f.write(b"# .PCD v0.7\nVERSION 0.7\nFIELDS normal_x normal_y normal_z x y z _\n")
        f.write(b"SIZE 4 4 4 4 4 4 1\nTYPE F F F F F F U\nCOUNT 1 1 1 1 1 1 4\n")
        f.write(b"WIDTH 3\nHEIGHT 1\nVIEWPOINT 0 0 0 1 0 0 0\nPOINTS 3\nDATA binary\n")
        f.write(rec.tobytes())
    got = read_pcd(pb)
    check("pcd/binary normals-first", np.allclose(got["xyz"], pts) and np.allclose(got["normals"], nrm),
          got["xyz"].tolist())

    # 2. ascii PCD, six columns, x first (the Juglet layout)
    pa = os.path.join(tmp, "juglet.pcd")
    with open(pa, "w") as f:
        f.write("# .PCD v0.7\nVERSION 0.7\nFIELDS x y z normal_x normal_y normal_z\n")
        f.write("SIZE 4 4 4 4 4 4\nTYPE F F F F F F\nCOUNT 1 1 1 1 1 1\n")
        f.write("WIDTH 3\nHEIGHT 1\nPOINTS 3\nDATA ascii\n")
        for i in range(3):
            f.write("%f %f %f %f %f %f\n" % (pts[i, 0], pts[i, 1], pts[i, 2],
                                             nrm[i, 0], nrm[i, 1], nrm[i, 2]))
    got = read_pcd(pa)
    check("pcd/ascii x-first", np.allclose(got["xyz"], pts) and np.allclose(got["normals"], nrm))

    # 3. PLY ascii round trip with normals, plus a binary one written by hand
    pp = os.path.join(tmp, "s.ply")
    _write_ply(pp, pts, nrm, extra=[("cluster_id", np.array([0, 0, 1]))])
    d = read_ply(pp)
    check("ply/ascii", np.allclose(ply_xyz(d), pts) and np.allclose(ply_normals(d), nrm)
          and list(d["cluster_id"]) == [0.0, 0.0, 1.0])

    # 4. folded angle: 30 deg about z
    ang = np.radians(30.0)
    a = np.array([[0.0, 0.0, 1.0]])
    b = np.array([[np.sin(ang), 0.0, np.cos(ang)]])
    check("fold/30deg", abs(float(folded_angle_deg(a, b)[0]) - 30.0) < 1e-6,
          "%.6f" % folded_angle_deg(a, b)[0])

    # 5. coverage: half the cloud inside 2 mm
    surf = np.array([[0.0, 0.0, 0.0]])
    cloud = np.array([[0.0, 0.0, 1.0], [0.0, 0.0, 3.0]])
    check("coverage/2mm", abs(coverage_fraction(surf, cloud) - 0.5) < 1e-12)

    # 6. pair statistic: Surface_1 is Surface_0 shifted 4 mm along its own normal
    p0 = np.array([[0.0, 0.0, 0.0], [1.0, 0.0, 0.0]])
    n0 = np.array([[0.0, 0.0, 1.0], [0.0, 0.0, 1.0]])
    p1 = p0 + np.array([[0.0, 0.0, 4.0], [0.0, 0.0, 4.0]])
    r = pair_stats(p0, n0, p1, n0)
    check("pairs/along", abs(r["med_along"] - 4.0) < 1e-6 and abs(r["med_across"]) < 1e-6
          and r["coin"] == 0.0, "along=%.3f across=%.3f" % (r["med_along"], r["med_across"]))
    p1c = p0 + np.array([[0.0, 0.0, 0.0005], [0.0, 0.0, 0.0005]])
    r = pair_stats(p0, n0, p1c, n0)
    check("pairs/coincidence", abs(r["coin"] - 1.0) < 1e-12, "coin=%.3f" % r["coin"])

    # 7. replay: two parallel 20x20 patches 0.2 mm apart, same normals -> a merge at pass 1
    g = np.mgrid[0:4, 0:4].reshape(2, -1).T.astype(float)
    Apts = np.column_stack([g[:, 0], g[:, 1], np.zeros(len(g))])
    Bpts = np.column_stack([g[:, 0] + 0.2, g[:, 1], np.zeros(len(g))])
    cl = np.vstack([Apts, Bpts])
    nrmv = np.tile(np.array([0.0, 0.0, 1.0]), (len(cl), 1))
    cid = np.array([0] * len(Apts) + [1] * len(Bpts))
    thr = {"rhoD": 0.6, "rhoN": 0.7, "rhoC": 0.1, "rhoInN": 0.7, "rhoInC": 0.1, "k1": 10, "k2": 4}
    rows, nfinal = replay_merge(cl, nrmv, np.full(len(cl), 0.01), cid, thr, 3)
    gates = [r["gate"] for r in rows]
    check("replay/merge", gates and gates[0] == "merge" and nfinal == 1,
          "gates=%s final=%d pairs=%d" % (gates, nfinal, rows[0]["pairs"] if rows else -1))
    thr2 = dict(thr, rhoD=0.05)   # nearer than the 0.2 mm gap: no boundary pair qualifies
    rows, nfinal = replay_merge(cl, nrmv, np.full(len(cl), 0.01), cid, thr2, 3)
    check("replay/min_pairs", rows and rows[0]["gate"] == "min_pairs" and nfinal == 2,
          "gate=%s pairs=%d" % (rows[0]["gate"] if rows else "-", rows[0]["pairs"] if rows else -1))
    rows, nfinal = replay_merge(cl, nrmv, np.full(len(cl), 0.01), cid, thr, 2)
    check("replay/min_pairs_2", rows and rows[0]["gate"] == "merge")
    thr3 = dict(thr, rhoN=1.1)
    rows, nfinal = replay_merge(cl, nrmv, np.full(len(cl), 0.01), cid, thr3, 3)
    check("replay/rhoN", rows and rows[0]["gate"] == "rhoN", "gate=%s" % (rows[0]["gate"] if rows else "-"))

    # 8. OBJ reader: one triangle in the z=0 plane -> vertices must have unit normals along +z
    po = os.path.join(tmp, "m.obj")
    with open(po, "w") as f:
        f.write("v 0 0 0\nv 1 0 0\nv 0 1 0\nf 1 2 3\n")
    v, vn = read_obj(po)
    check("obj/triangle", v.shape == (3, 3) and np.allclose(vn, [[0, 0, 1]] * 3),
          vn.tolist())

    # 9. pca_normals: a flat sheet -> normals along +-z, curvature ~0
    sheet = np.column_stack([np.repeat(np.arange(10.0), 10), np.tile(np.arange(10.0), 10),
                             np.zeros(100)])
    nn, cc = pca_normals(sheet, 10)
    check("pca/flat", np.all(np.abs(nn[:, 2]) > 0.999) and float(np.max(cc)) < 1e-6,
          "max curv=%.3g" % float(np.max(cc)))
    print("[SELFTEST] %s (%d failures) tmp=%s" % ("PASS" if bad == 0 else "FAIL", bad, tmp))
    return 1 if bad else 0


def main(argv=None):
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("selftest")
    ac = sub.add_parser("cell")
    ac.add_argument("--cell", required=True)
    ac.add_argument("--pot", required=True)
    ac.add_argument("--piece", required=True)
    ac.add_argument("--arm", required=True)
    ac.add_argument("--mesh", required=True)
    ac.add_argument("--cloud", required=True)
    ac.add_argument("--maxpts", type=int, default=60000)
    ag = sub.add_parser("agg")
    ag.add_argument("--cellroot", required=True)
    ag.add_argument("--out", required=True)
    df = sub.add_parser("defaults")
    df.add_argument("--orig", required=True)
    df.add_argument("--new", required=True)
    df.add_argument("--out", required=True)
    a = ap.parse_args(argv)
    if a.cmd == "selftest":
        return selftest()
    if a.cmd == "cell":
        return cell(a)
    if a.cmd == "agg":
        return agg(a)
    return defaults(a)


if __name__ == "__main__":
    sys.exit(main())
