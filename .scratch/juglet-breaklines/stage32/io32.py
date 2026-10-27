#!/usr/bin/env python3
"""Ticket 32 -- readers and geometry helpers.

No measurement policy lives here: every arm, window and threshold is in partA32.py,
partB32.py and partD32.py.  The OBJ reader, the quadric fit and the mesh floor are
ticket 30's arithmetic (analyse30.py); this module only adds what ticket 30 did not
need -- the binary PCD reader, the ground-truth transform reader, the voxel subsample
and a variable-length neighbour version of the fit.
"""
import hashlib
import numpy as np

PCD_CODE = {"F": "f", "U": "u", "I": "i", "f": "f", "u": "u", "i": "i"}


def md5_file(path, blocksize=1 << 22):
    h = hashlib.md5()
    with open(path, "rb") as f:
        while True:
            b = f.read(blocksize)
            if not b:
                break
            h.update(b)
    return h.hexdigest()


def read_pcd(path):
    """Read an ASCII or binary PCD.

    The true point count is taken from the body length, not from the header: the
    released Pot A clouds declare POINTS 1000000 and carry fewer.
    """
    with open(path, "rb") as f:
        raw = f.read()
    pos = 0
    head = {}
    while True:
        nl = raw.find(b"\n", pos)
        if nl < 0:
            raise SystemExit("[io32] no DATA line in %s" % path)
        line = raw[pos:nl].decode("ascii", "replace").strip()
        pos = nl + 1
        if not line or line.startswith("#"):
            continue
        head[line.split()[0]] = line
        if line.split()[0] == "DATA":
            break
    mode = head["DATA"].split()[1].lower() if len(head["DATA"].split()) > 1 else "ascii"
    fields = head["FIELDS"].split()[1:]
    sizes = [int(s) for s in head["SIZE"].split()[1:]]
    types = head["TYPE"].split()[1:]
    counts = ([int(c) for c in head["COUNT"].split()[1:]] if "COUNT" in head
              else [1] * len(fields))
    if not (len(fields) == len(sizes) == len(types) == len(counts)):
        raise SystemExit("[io32] ragged header in %s" % path)
    header_points = int(head["POINTS"].split()[1]) if "POINTS" in head else -1
    body = raw[pos:]
    off = {}
    o = 0
    for nm, c in zip(fields, counts):
        off[nm] = (o, c)
        o += c
    ncols = o
    if mode == "ascii":
        txt = body.decode("ascii", "replace").split()
        vals = np.asarray(txt, dtype=np.float64)
        if vals.size % ncols:
            raise SystemExit("[io32] ascii body %d values is not a multiple of %d in %s"
                             % (vals.size, ncols, path))
        a = vals.reshape(-1, ncols)
        n = a.shape[0]
    elif mode == "binary":
        dt = []
        for nm, sz, ty, c in zip(fields, sizes, types, counts):
            base = "<" + PCD_CODE[ty] + str(sz)
            dt.append((nm, base) if c == 1 else (nm, base, (c,)))
        dt = np.dtype(dt)
        if len(body) % dt.itemsize:
            raise SystemExit("[io32] binary body %d is not a multiple of %d in %s"
                             % (len(body), dt.itemsize, path))
        a = np.frombuffer(body, dtype=dt)
        n = a.size
    else:
        raise SystemExit("[io32] unsupported PCD data mode %r in %s" % (mode, path))
    if n == 0:
        raise SystemExit("[io32] empty cloud: %s" % path)
    def col(nm):
        # the ascii branch is a plain float array (no named fields); the binary branch is
        # a structured array.  Both are addressed by the header's own column offsets.
        if a.dtype.names:
            return np.asarray(a[nm], dtype=np.float64)
        return np.asarray(a[:, off[nm][0]], dtype=np.float64)

    xyz = np.stack([col("x"), col("y"), col("z")], axis=1)
    nrm = None
    if all(k in off for k in ("normal_x", "normal_y", "normal_z")):
        nrm = np.stack([col("normal_x"), col("normal_y"), col("normal_z")], axis=1)
    return {"xyz": xyz, "nrm": nrm, "n_points": int(n),
            "header_points": int(header_points), "data": mode,
            "fields": fields, "md5": md5_file(path), "path": path}


def read_obj(path):
    """Vertices, face index array, area-weighted vertex normals and total area (mm^2).

    Same parse and the same fan triangulation and accumulation as
    analyse30.read_obj_normals (stage30, reused), extended to return the faces and
    the summed triangle area.
    """
    verts = []
    faces = []
    with open(path, "r", errors="replace") as fh:
        for line in fh:
            if line.startswith("v "):
                p = line.split()
                verts.append((float(p[1]), float(p[2]), float(p[3])))
            elif line.startswith("f "):
                idx = []
                for tok in line.split()[1:]:
                    idx.append(int(tok.split("/")[0]))
                if len(idx) >= 3:
                    faces.append(idx)
    v = np.asarray(verts, dtype=np.float64)
    if v.size == 0 or not faces:
        raise SystemExit("[io32] no geometry in %s" % path)
    fn = np.zeros_like(v)
    area = 0.0
    for f in faces:
        idx = np.asarray([i - 1 if i > 0 else v.shape[0] + i for i in f], dtype=np.int64)
        p = v[idx]
        for t in range(1, idx.size - 1):
            a, b, c = p[0], p[t], p[t + 1]
            cr = np.cross(b - a, c - a)
            fn[idx[0]] += cr
            fn[idx[t]] += cr
            fn[idx[t + 1]] += cr
            area += 0.5 * float(np.linalg.norm(cr))
    ln = np.linalg.norm(fn, axis=1)
    ln[ln == 0.0] = 1.0
    return {"verts": v, "faces": len(faces), "vnorm": fn / ln[:, None],
            "area_mm2": area}


def read_t(path):
    """A 4x4 transform written as four rows of four numbers (row-major)."""
    rows = []
    with open(path, "r", errors="replace") as fh:
        for line in fh:
            p = line.split()
            if len(p) >= 4:
                rows.append([float(x) for x in p[:4]])
    if len(rows) != 4:
        raise SystemExit("[io32] expected 4 rows in %s, got %d" % (path, len(rows)))
    return np.asarray(rows, dtype=np.float64)


def place(xyz, T, mode):
    """p' = R p + t ('Rp+t'), p' = p R + t ('pR+t'), p = R^T (p' - t) ('inv')."""
    R = T[:3, :3]
    t = T[:3, 3]
    if mode == "Rp+t":
        return xyz @ R.T + t
    if mode == "pR+t":
        return xyz @ R + t
    if mode == "inv":
        return (xyz - t) @ R
    raise SystemExit("[io32] unknown placement mode %r" % mode)


def bbox_sides(xyz):
    lo = xyz.min(axis=0)
    hi = xyz.max(axis=0)
    return (hi - lo)


def extent_mm(xyz):
    """Bounding-box diagonal in mm -- one definition used for sherd and vessel alike."""
    return float(np.linalg.norm(bbox_sides(xyz)))


def voxel_subsample(xyz, cell):
    """One point per cell, the first in file order: deterministic, no rng."""
    if cell <= 0:
        raise SystemExit("[io32] cell must be > 0")
    ijk = np.floor(xyz / float(cell)).astype(np.int64)
    key = (ijk[:, 0] << 42) ^ (ijk[:, 1] << 21) ^ ijk[:, 2]
    _, first = np.unique(key, return_index=True)
    return np.sort(first)


def median_spacing(pts, tree):
    d, _ = tree.query(pts, k=2, workers=-1)
    return float(np.median(d[:, 1]))
