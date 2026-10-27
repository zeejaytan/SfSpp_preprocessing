#!/usr/bin/env python3
"""Ticket 35 - what are sherds 2 and 9.  Mesh-side measurement instrument.

Pure numpy (no scipy, no trimesh, no sklearn).  Everything is written out so the
job has no build step and no container:

  readers    OBJ (indexed and unindexed), PLY (ascii, multi-element), PCD (ascii
             and binary, arbitrary field order / COUNT / padding field)
  geometry   mesh welding, topology (Euler, boundary loops, components),
             vertex normals, Moller-Trumbore ray casting
  search     uniform-grid radius pairs, kNN, nearest-carry (all self-checking)
  growth     ticket 28's greedy 3.4 deg replica + order-free connected sets
  render     z-buffer rasteriser, 5x7 bitmap font, PNG via zlib

Usage: measure35.py --out DIR [--pieces 9,2] [--selftest-only]
"""
import argparse, hashlib, json, os, struct, sys, time, traceback, zlib
import numpy as np

CANON = "/data/gpfs/projects/punim2657/sfs_preprocessing"
CORP = "/data/gpfs/projects/punim2657/sfs_main/original_samples/SfS_pp"
RUNS = "/data/gpfs/projects/punim2657/SfSpp/runs"
JUG_ARMS = RUNS + "/20261027-0655_cc9c6d9_t30-arm3-jq23p29/out/arms/t30-arm3-jq23p29/Juglet"
POT_ARMS = RUNS + "/20261027-0647_5bc82a9_t30-arm1-pa3p4/out/arms/Pot_A"

def jug(n):
    return dict(pot="Juglet", tag=n,
                mesh="%s/Dataset/Mesh/Juglet/Juglet_Piece_%s_Mesh.obj" % (CANON, n),
                pcd="%s/Dataset/Point/Juglet/Juglet_Piece_%s_Point.pcd" % (CANON, n),
                arm="%s/Juglet_Piece_%s/surfaces/Juglet_Piece_%s_SampledWithNormals.ply" % (JUG_ARMS, n, n))

# smallest first: early evidence survives a late failure
PIECES = [jug("9"), jug("2"), jug("3"), jug("5"), jug("7"),
          dict(pot="Pot_A", tag="07",
               mesh=CORP + "/Mesh/Pot_A_Piece_07_Mesh.obj",
               pcd=CORP + "/Point/Pot_A/Pot_A_Piece_07_Point.pcd",
               arm=POT_ARMS + "/Pot_A_Piece_07/surfaces/Pot_A_Piece_07_SampledWithNormals.ply"),
          jug("1"),
          dict(pot="Pot_A", tag="01",
               mesh=CORP + "/Mesh/Pot_A_Piece_01_Mesh.obj",
               pcd=CORP + "/Point/Pot_A/Pot_A_Piece_01_Point.pcd",
               arm=POT_ARMS + "/Pot_A_Piece_01/surfaces/Pot_A_Piece_01_SampledWithNormals.ply")]

# on record already; ticket 35 criterion 4 asks me to reproduce these
P20 = {  # run 20261027-0148_f3896e4_p20-arm/out/C_mesh.tsv
 "9": dict(V=2094, F=4184, area=373.757, rays=787, med=2.59484, p10=2.06616, p90=8.18262,
           f13=0.613811, hmed=2, hmax=8, r2=783),
 "2": dict(V=2565, F=5126, area=491.067, rays=1031, med=2.69305, p10=2.13945, p90=6.75069,
           f13=0.598249, hmed=2, hmax=10, r2=1027),
 "3": dict(V=3493, F=6982, area=752.904, rays=1467, med=2.4516, p10=1.85722, p90=7.13893,
           f13=0.67054, hmed=2, hmax=9, r2=1460),
 "5": dict(V=6211, F=12418, area=1401.63, rays=1007, med=2.8998, p10=2.31574, p90=6.51743,
           f13=0.541294, hmed=2, hmax=9, r2=1005),
 "7": dict(V=8421, F=16838, area=1980.18, rays=851, med=3.26316, p10=2.32523, p90=5.78525,
           f13=0.338824, hmed=2, hmax=8, r2=847),
 "07": dict(V=63522, F=21174, area=2005.19, rays=860, med=4.05609, p10=3.50109, p90=11.9737,
            f13=0.00930233, hmed=2, hmax=2, r2=860),
}
T28 = {"3": 169, "5": 679, "2": 36, "9": 16}   # tickets 28 / 33, PCA normals
WELD_TOL = 1e-4
THETA, KAPPA, NB = 3.4, 1.0, 10

def log(msg, fh=None):
    line = "[%s] %s" % (time.strftime("%H:%M:%S"), msg)
    print(line, flush=True)
    if fh is not None:
        fh.write(line + "\n"); fh.flush()

def md5_of(path):
    h = hashlib.md5()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 22), b""):
            h.update(chunk)
    return h.hexdigest()

def pct(a, p):
    a = np.asarray(a, dtype=float)
    a = a[np.isfinite(a)]
    return float(np.percentile(a, p)) if a.size else float("nan")

def f6(x):
    try:
        if x is None or not np.isfinite(float(x)):
            return "nan"
        return "%.6g" % float(x)
    except Exception:
        return str(x)

def tsv(cols, rows):
    out = ["\t".join(cols)]
    for r in rows:
        out.append("\t".join("" if v is None else str(v) for v in r))
    return "\n".join(out) + "\n"

# ---------------------------------------------------------------- readers
def read_obj(path):
    V, Fraw = [], []
    n_vn = n_vt = 0
    with open(path, "r", errors="replace") as f:
        for line in f:
            c = line[:2]
            if c == "v ":
                p = line.split()
                V.append((float(p[1]), float(p[2]), float(p[3])))
            elif c == "f ":
                idx = [int(tok.split("/")[0]) for tok in line.split()[1:]]
                for k in range(1, len(idx) - 1):
                    Fraw.append((idx[0], idx[k], idx[k + 1]))
            elif c == "vn":
                n_vn += 1
            elif c == "vt":
                n_vt += 1
    V = np.asarray(V, dtype=np.float64)
    F = np.asarray(Fraw, dtype=np.int64)
    if (F < 0).any():
        F = F + len(V) + 1
    F = F - 1
    if len(V) == 0 or len(F) == 0:
        raise ValueError("OBJ empty: %d v %d f" % (len(V), len(F)))
    if F.min() < 0 or F.max() >= len(V):
        raise ValueError("OBJ index out of range: %d..%d for %d verts" % (F.min(), F.max(), len(V)))
    return V, F, dict(n_vn=n_vn, n_vt=n_vt)

def read_ply_vertices(path):
    """ascii PLY -> (vertex rows, property names).  Reads the vertex element
    only; a camera element with 30+ properties follows it in these files."""
    names, counts, props = [], [], []
    with open(path, "r", errors="replace") as f:
        first = f.readline().strip()
        if first != "ply":
            raise ValueError("PLY does not start with the magic line: %r" % first)
        fmt = None
        while True:
            line = f.readline()
            if not line:
                raise ValueError("PLY header ended without end_header")
            p = line.split()
            if not p:
                continue
            if p[0] == "format":
                fmt = line.strip()
                if "ascii" not in fmt:
                    raise ValueError("PLY not ascii: %r" % fmt)
            elif p[0] == "element":
                names.append(p[1]); counts.append(int(p[2])); props.append([])
            elif p[0] == "property":
                props[-1].append((p[4] if p[1] == "list" else p[2], p[1]))
            elif p[0] == "end_header":
                break
        if "vertex" not in names:
            raise ValueError("PLY has no vertex element")
        vi = names.index("vertex")
        for k in range(vi):
            if any(t == "list" for _, t in props[k]):
                raise ValueError("PLY list property before vertex")
            for _ in range(counts[k]):
                f.readline()
        nv = counts[vi]
        w = len(props[vi])
        rows = []
        for i in range(nv):
            line = f.readline()
            if not line:
                raise ValueError("PLY body ended at vertex %d of %d" % (i, nv))
            p = line.split()
            if len(p) != w:
                raise ValueError("PLY vertex %d has %d columns, expected %d: %r"
                                 % (i, len(p), w, line[:100]))
            rows.append(p)
    return np.array(rows, dtype=np.float64), [n for n, _ in props[vi]]

_TYPEMAP = {("F", 4): "f4", ("F", 8): "f8", ("U", 1): "u1", ("U", 2): "u2",
            ("U", 4): "u4", ("U", 8): "u8", ("I", 1): "i1", ("I", 2): "i2",
            ("I", 4): "i4", ("I", 8): "i8"}

def read_pcd(path):
    """-> points (n,3) x,y,z order, normals (n,3) or None, info dict
    ascii and binary; any field order; COUNT>1 padding fields."""
    hdr, nhead = {}, 0
    with open(path, "rb") as f:
        while True:
            line = f.readline()
            if not line:
                raise ValueError("PCD header ended without DATA")
            nhead += 1
            s = line.decode("ascii", "replace").strip()
            if not s or s.startswith("#"):
                continue
            parts = s.split()
            hdr[parts[0]] = parts[1:]
            if parts[0] == "DATA":
                offset = f.tell()
                break
    fields = hdr["FIELDS"]
    sizes = [int(x) for x in hdr.get("SIZE", ["4"] * len(fields))]
    types = hdr.get("TYPE", ["F"] * len(fields))
    cnts = [int(x) for x in hdr.get("COUNT", ["1"] * len(fields))]
    kind = hdr["DATA"][0].lower()
    npts = int((hdr.get("POINTS") or hdr.get("WIDTH") or ["0"])[0])
    if not (len(sizes) == len(types) == len(cnts) == len(fields)):
        raise ValueError("PCD header lengths disagree: %r" % hdr)
    if kind == "ascii":
        arr = np.loadtxt(path, skiprows=nhead, comments="#", ndmin=2)
        if arr.shape[0] != npts:
            raise ValueError("PCD ascii %d rows != POINTS %d" % (arr.shape[0], npts))
        col, c = {}, 0
        for nm, ct in zip(fields, cnts):
            col[nm] = c; c += ct
        if arr.shape[1] < c:
            raise ValueError("PCD ascii %d columns, header wants %d" % (arr.shape[1], c))
        P = np.stack([arr[:, col["x"]], arr[:, col["y"]], arr[:, col["z"]]], 1)
        N = None
        if all(k in col for k in ("normal_x", "normal_y", "normal_z")):
            N = np.stack([arr[:, col[k]] for k in ("normal_x", "normal_y", "normal_z")], 1)
    elif kind == "binary":
        dt, off = [], 0
        for nm, sz, ty, ct in zip(fields, sizes, types, cnts):
            if (ty.upper(), sz) not in _TYPEMAP:
                raise ValueError("PCD field %r type %r size %d unsupported" % (nm, ty, sz))
            dt.append((nm, _TYPEMAP[(ty.upper(), sz)], (ct,) if ct > 1 else ()))
            off += sz * ct
        npdt = np.dtype(dt)
        if npdt.itemsize != off:
            raise ValueError("PCD stride %d != %d" % (npdt.itemsize, off))
        buf = np.fromfile(path, dtype=npdt, count=npts, offset=offset)
        if buf.shape[0] != npts:
            raise ValueError("PCD binary read %d of %d (stride %d)"
                             % (buf.shape[0], npts, npdt.itemsize))
        P = np.stack([buf["x"], buf["y"], buf["z"]], 1).astype(np.float64)
        N = None
        if all(k in buf.dtype.names for k in ("normal_x", "normal_y", "normal_z")):
            N = np.stack([buf[k] for k in ("normal_x", "normal_y", "normal_z")], 1).astype(np.float64)
    else:
        raise ValueError("PCD DATA %r unsupported" % kind)
    return P, N, dict(kind=kind, n=len(P), fields=fields, sizes=sizes, types=types, counts=cnts)

def unit(v):
    n = np.linalg.norm(v, axis=1)
    out = np.zeros_like(v)
    ok = np.isfinite(n) & (n > 0)
    out[ok] = v[ok] / n[ok, None]
    return out, ok

# ---------------------------------------------------------------- geometry
def weld(V, F, tol):
    key = np.round(V / tol).astype(np.int64)
    uniq, first, inv = np.unique(key, axis=0, return_index=True, return_inverse=True)
    return V[first], inv[F], len(uniq)

def mesh_topology(V, F, loop_cap=400):
    E = np.sort(np.vstack([F[:, [0, 1]], F[:, [1, 2]], F[:, [2, 0]]]), 1)
    eu, cnt = np.unique(E, axis=0, return_counts=True)
    bnd = eu[cnt == 1]
    nonman = int((cnt > 2).sum())
    parent = np.arange(len(V))
    def find(a):
        while parent[a] != a:
            parent[a] = parent[parent[a]]; a = parent[a]
        return a
    for a, b in eu:
        ra, rb = find(int(a)), find(int(b))
        if ra != rb:
            parent[ra] = rb
    comps = len({find(i) for i in range(len(V))})
    loops, n_loops = [], 0
    if len(bnd):
        adj = {}
        for k, (a, b) in enumerate(bnd):
            adj.setdefault(int(a), []).append((int(b), k))
            adj.setdefault(int(b), []).append((int(a), k))
        used = np.zeros(len(bnd), bool)
        for k0 in range(len(bnd)):
            if used[k0]:
                continue
            used[k0] = True
            chain = [int(bnd[k0][0]), int(bnd[k0][1])]
            cur, closed = chain[1], False
            while True:
                nxt = None
                for (o, kk) in adj[cur]:
                    if not used[kk]:
                        nxt = (o, kk); break
                if nxt is None:
                    break
                used[nxt[1]] = True
                cur = nxt[0]
                if cur == chain[0]:
                    closed = True; break
                chain.append(cur)
            n_loops += 1
            if len(loops) < loop_cap:
                seg = V[np.asarray(chain)]
                loops.append(dict(n_edges=len(chain) - 1,
                                  length_mm=float(np.linalg.norm(np.diff(seg, axis=0), axis=1).sum()),
                                  closed=closed, start=V[chain[0]].tolist()))
    return dict(V=len(V), E=len(eu), F=len(F), euler=len(V) - len(eu) + len(F),
                boundary_edges=len(bnd), nonmanifold=nonman,
                watertight=(len(bnd) == 0 and nonman == 0), components=comps,
                loops=loops, n_loops=n_loops)

def vnormals(V, F):
    fn = np.cross(V[F[:, 1]] - V[F[:, 0]], V[F[:, 2]] - V[F[:, 0]])
    out = np.zeros_like(V)
    for k in range(3):
        for d in range(3):
            out[:, d] += np.bincount(F[:, k], weights=fn[:, d], minlength=len(V))
    return unit(out)[0]

def face_area(V, F):
    c = np.cross(V[F[:, 1]] - V[F[:, 0]], V[F[:, 2]] - V[F[:, 0]])
    return 0.5 * np.linalg.norm(c, axis=1)

def ray_hits(V, F, origins, dirs, eps=1e-9):
    """Moller-Trumbore, ticket 20 semantics: positive t only, one vectorised
    pass over all triangles per ray.  Returns a list of sorted hit distances."""
    v0 = V[F[:, 0]]; e1 = V[F[:, 1]] - v0; e2 = V[F[:, 2]] - v0
    out = []
    for k in range(len(origins)):
        d = np.asarray(dirs[k], float); p = np.asarray(origins[k], float)
        h = np.cross(d, e2)
        a = (e1 * h).sum(1)
        ok = np.abs(a) > 1e-12
        if not ok.any():
            out.append(np.zeros(0)); continue
        f = np.zeros_like(a); f[ok] = 1.0 / a[ok]
        s = p - v0
        u = f * (s * h).sum(1)
        qv = np.cross(s, e1)
        vv = f * (qv @ d)
        t = f * (e2 * qv).sum(1)
        m = ok & (u >= -eps) & (u <= 1 + eps) & (vv >= -eps) & (u + vv <= 1 + eps) & (t > 0)
        out.append(np.sort(t[m]))
    return out

def scatter_max(n, idx, val):
    if len(idx) == 0:
        return np.zeros(n)
    o = np.argsort(idx, kind="stable")
    i_s, v_s = idx[o], val[o]
    st = np.flatnonzero(np.r_[True, i_s[1:] != i_s[:-1]])
    out = np.zeros(n)
    out[i_s[st]] = np.maximum.reduceat(v_s, st)
    return out

# ---------------------------------------------------------------- grid search
OFFS = [(a, b, c) for a in (-1, 0, 1) for b in (-1, 0, 1) for c in (-1, 0, 1)]

class Grid:
    def __init__(self, P, cell):
        self.P = P; self.cell = float(cell)
        self.lo = P.min(0) - 3 * cell
        self.B2 = int(np.ceil(((P.max(0) - self.lo) / cell).max())) + 12
        key = self._encode(np.floor((P - self.lo) / cell).astype(np.int64))
        self.order = np.argsort(key, kind="stable")
        self.uniq, st, ct = np.unique(key[self.order], return_index=True, return_counts=True)
        self.start = st.astype(np.int64); self.cnt = ct.astype(np.int64)

    def _encode(self, c):
        c = c + 4
        if (c < 0).any() or (c >= self.B2).any():
            raise ValueError("grid: query outside the padded box")
        return (c[:, 0] * self.B2 + c[:, 1]) * self.B2 + c[:, 2]

    def _cand(self, Q, qidx):
        qi_l, rj_l = [], []
        c0 = np.floor((Q - self.lo) / self.cell).astype(np.int64)
        for o in OFFS:
            key = self._encode(c0 + np.array(o))
            pos = np.searchsorted(self.uniq, key)
            pp = np.clip(pos, 0, len(self.uniq) - 1)
            hit = (pos < len(self.uniq)) & (self.uniq[pp] == key)
            if not hit.any():
                continue
            h = np.where(hit)[0]
            cc = self.cnt[pp[h]]
            tot = int(cc.sum())
            if tot == 0:
                continue
            base = np.repeat(self.start[pp[h]], cc)
            off = np.arange(tot, dtype=np.int64) - np.repeat(np.cumsum(cc) - cc, cc)
            rj_l.append(self.order[base + off])
            qi_l.append(np.repeat(qidx[h], cc))
        if not qi_l:
            return np.zeros(0, np.int64), np.zeros(0, np.int64)
        return np.concatenate(qi_l), np.concatenate(rj_l)

    def pairs(self, Q, radius, chunk=20000):
        """all (i,j) with |Q_i - P_j| <= radius and i < j, original indices"""
        n = len(Q)
        qi = np.arange(n, dtype=np.int64)
        I, J = [], []
        for s in range(0, n, chunk):
            e = min(n, s + chunk)
            a, b = self._cand(Q[s:e], qi[s:e])
            if not len(a):
                continue
            d = np.linalg.norm(Q[a] - self.P[b], axis=1)
            m = (d <= radius) & (a < b)
            I.append(a[m]); J.append(b[m])
        if not I:
            return np.zeros(0, np.int64), np.zeros(0, np.int64)
        return np.concatenate(I), np.concatenate(J)

    def knn(self, Q, K, chunk=2048, _retry=3):
        n = len(Q)
        idx = np.zeros((n, K), np.int64); dist = np.zeros((n, K))
        for s in range(0, n, chunk):
            e = min(n, s + chunk)
            qi, rj = self._cand(Q[s:e], np.arange(s, e, dtype=np.int64))
            if not len(qi):
                raise ValueError("grid.knn: no candidates for rows %d..%d" % (s, e))
            d = np.linalg.norm(Q[qi] - self.P[rj], axis=1)
            o = np.lexsort((d, qi))
            qi, rj, d = qi[o], rj[o], d[o]
            bd = np.searchsorted(qi, np.arange(s, e + 1))
            for k, r in enumerate(range(s, e)):
                a, b = bd[k], bd[k + 1]
                if b - a < K:
                    if _retry > 0:
                        return Grid(self.P, self.cell * 2.0).knn(Q, K, chunk, _retry - 1)
                    raise ValueError("grid.knn: %d candidates for row %d (cell %.4f)"
                                     % (b - a, r, self.cell))
                idx[r] = rj[a:a + K]; dist[r] = d[a:a + K]
        return idx, dist, int((dist[:, -1] > self.cell).sum())

def grid_for(P, k, tries=8):
    vol = float(np.prod(np.maximum(P.max(0) - P.min(0), 1e-6)))
    cell = max(4.0 * (vol / max(len(P), 1)) ** (1 / 3.0), 1e-3)
    q = P[: min(len(P), 4000)]
    for _ in range(tries):
        g = Grid(P, cell)
        _, d, bad = g.knn(q, min(k, len(P)))
        if bad == 0 and float(d[:, -1].max()) <= 0.4 * cell:
            return g
        cell *= 2.0
    raise ValueError("grid_for: no cell satisfied the kNN proof (last %.4f)" % cell)

# ---------------------------------------------------------------- turning
def pair_angles(nrm, i, j):
    d = np.abs((nrm[i] * nrm[j]).sum(1))
    return np.degrees(np.arccos(np.clip(d, 0.0, 1.0)))

def grow(normals, curv, nbr, theta_deg, kappa, nb):
    """ticket 28 replica: stable curvature-ascending seeds, FIFO front, the
    front point's own normal is the reference, the nb nearest (self skipped)
    tested in distance order, <= theta joins, curvature < kappa required."""
    n = len(normals)
    claimed = np.zeros(n, bool)
    order = np.argsort(curv, kind="stable")
    nrm = normals.tolist(); cv = curv.tolist()
    cos_t = np.cos(np.radians(theta_deg))
    regs = []
    for s in order:
        s = int(s)
        if claimed[s]:
            continue
        claimed[s] = True
        reg, q, head = [s], [s], 0
        while head < len(q):
            cf = q[head]; head += 1
            nf = nrm[cf]; tested = 0
            for cand in nbr[cf]:
                cand = int(cand)
                if cand == cf:
                    continue
                if tested >= nb:
                    break
                tested += 1
                if claimed[cand] or not (cv[cand] < kappa):
                    continue
                nc = nrm[cand]
                if nf[0] * nc[0] + nf[1] * nc[1] + nf[2] * nc[2] >= cos_t:
                    claimed[cand] = True
                    reg.append(cand); q.append(cand)
        regs.append(len(reg))
    regs.sort(reverse=True)
    return regs

def comp_sizes(n, i, j):
    parent = np.arange(n, dtype=np.int64)
    def find(a):
        while parent[a] != a:
            parent[a] = parent[parent[a]]; a = parent[a]
        return a
    for a, b in zip(i.tolist(), j.tolist()):
        ra, rb = find(a), find(b)
        if ra != rb:
            parent[ra] = rb
    roots = np.array([find(a) for a in range(n)])
    _, cnt = np.unique(roots, return_counts=True)
    cnt = np.sort(cnt)[::-1]
    return len(cnt), int(cnt[0]) if len(cnt) else 0

def pca_curvature(P, nbr):
    k = nbr.shape[1]
    nb = P[nbr] - P[nbr].mean(1, keepdims=True)
    cov = np.einsum("nki,nkj->nij", nb, nb) / float(k)
    ev = np.linalg.eigvalsh(cov)
    tr = ev.sum(1)
    out = np.zeros(len(P))
    ok = tr > 1e-12
    out[ok] = np.abs(ev[ok, 0]) / tr[ok]
    return out

# ---------------------------------------------------------------- rendering
FONT = {
 "A":"01110/10001/10001/11111/10001/10001/10001","B":"11110/10001/10001/11110/10001/10001/11110",
 "C":"01110/10001/10000/10000/10000/10001/01110","D":"11110/10001/10001/10001/10001/10001/11110",
 "E":"11111/10000/10000/11110/10000/10000/11111","F":"11111/10000/10000/11110/10000/10000/10000",
 "G":"01110/10001/10000/10111/10001/10001/01111","H":"10001/10001/10001/11111/10001/10001/10001",
 "I":"11111/00100/00100/00100/00100/00100/11111","J":"00111/00010/00010/00010/00010/10010/01100",
 "K":"10001/10010/10100/11000/10100/10010/10001","L":"10000/10000/10000/10000/10000/10000/11111",
 "M":"10001/11011/10101/10101/10001/10001/10001","N":"10001/11001/10101/10011/10001/10001/10001",
 "O":"01110/10001/10001/10001/10001/10001/01110","P":"11110/10001/10001/11110/10000/10000/10000",
 "Q":"01110/10001/10001/10001/10101/10010/01101","R":"11110/10001/10001/11110/10100/10010/10001",
 "S":"01111/10000/10000/01110/00001/00001/11110","T":"11111/00100/00100/00100/00100/00100/00100",
 "U":"10001/10001/10001/10001/10001/10001/01110","V":"10001/10001/10001/10001/10001/01010/00100",
 "W":"10001/10001/10001/10101/10101/11011/10001","X":"10001/10001/01010/00100/01010/10001/10001",
 "Y":"10001/10001/01010/00100/00100/00100/00100","Z":"11111/00001/00010/00100/01000/10000/11111",
 "0":"01110/10001/10011/10101/11001/10001/01110","1":"00100/01100/00100/00100/00100/00100/01110",
 "2":"01110/10001/00001/00010/00100/01000/11111","3":"11111/00010/00100/00010/00001/10001/01110",
 "4":"00010/00110/01010/10010/11111/00010/00010","5":"11111/10000/11110/00001/00001/10001/01110",
 "6":"00110/01000/10000/11110/10001/10001/01110","7":"11111/00001/00010/00100/01000/01000/01000",
 "8":"01110/10001/10001/01110/10001/10001/01110","9":"01110/10001/10001/01111/00001/00010/01100",
 ".":"00000/00000/00000/00000/00000/01100/01100","-":"00000/00000/00000/11111/00000/00000/00000",
 "/":"00001/00010/00010/00100/01000/01000/10000",":":"00000/01100/01100/00000/01100/01100/00000",
 "_":"00000/00000/00000/00000/00000/00000/11111","=":"00000/00000/11111/00000/11111/00000/00000",
 "(":"00010/00100/01000/01000/01000/00100/00010",")":"01000/00100/00010/00010/00010/00100/01000",
 " ":"00000/00000/00000/00000/00000/00000/00000","+":"00000/00100/00100/11111/00100/00100/00000",
 ",":"00000/00000/00000/00000/01100/01100/01000",
}
_G = {k: np.array([[c == "1" for c in row] for row in v.split("/")]) for k, v in FONT.items()}

def draw_text(img, x, y, text, s=3, rgb=(20, 20, 20)):
    H, W, _ = img.shape
    cx = x
    for ch in text.upper():
        g = _G.get(ch, _G[" "])
        for r in range(7):
            for c in range(5):
                if g[r, c]:
                    y0, x0 = y + r * s, cx + c * s
                    if 0 <= y0 < H - s and 0 <= x0 < W - s:
                        img[y0:y0 + s, x0:x0 + s] = rgb
        cx += 6 * s

def write_png(path, rgb):
    H, W, _ = rgb.shape
    raw = b"".join(b"\x00" + rgb[y].tobytes() for y in range(H))
    def chunk(t, d):
        return struct.pack(">I", len(d)) + t + d + struct.pack(">I", zlib.crc32(t + d) & 0xFFFFFFFF)
    png = (b"\x89PNG\r\n\x1a\n"
           + chunk(b"IHDR", struct.pack(">IIBBBBB", W, H, 8, 2, 0, 0, 0))
           + chunk(b"IDAT", zlib.compress(raw, 6)) + chunk(b"IEND", b""))
    with open(path, "wb") as f:
        f.write(png)
    return len(png)

RAMP = np.array([[40, 40, 120], [30, 110, 190], [40, 180, 170], [70, 210, 90],
                 [230, 210, 60], [240, 140, 40], [220, 60, 40]], float)

def ramp(t):
    t = np.clip(np.asarray(t, float), 0.0, 1.0) * (len(RAMP) - 1)
    lo = np.floor(t).astype(int); hi = np.minimum(lo + 1, len(RAMP) - 1)
    f = (t - lo)[:, None]
    return RAMP[lo] * (1 - f) + RAMP[hi] * f

def view_basis(wd):
    ud = np.cross(wd, [0.0, 0.0, 1.0])
    if np.linalg.norm(ud) < 1e-6:
        ud = np.cross(wd, [0.0, 1.0, 0.0])
    ud = ud / np.linalg.norm(ud)
    return ud, np.cross(wd, ud), wd

def shade_from_normals(V, F, basis):
    u, v, w = basis
    fn = np.cross(V[F[:, 1]] - V[F[:, 0]], V[F[:, 2]] - V[F[:, 0]])
    fn = fn / np.maximum(np.linalg.norm(fn, axis=1, keepdims=True), 1e-30)
    sgn = np.sign(fn @ w); sgn[sgn == 0] = 1.0
    fn = fn * sgn[:, None]
    L = 0.35 * u + 0.45 * v + 0.82 * w
    L = L / np.linalg.norm(L)
    inten = 0.28 + 0.72 * np.clip(fn @ L, 0, 1) + 0.10 * np.clip(fn @ (u - 0.6 * v), 0, 1)
    g = (np.clip(inten, 0, 1.25) * 190).astype(np.uint8)
    return np.stack([g, g, np.minimum(255, g.astype(int) + 4).astype(np.uint8)], 1)

def raster(V, F, basis, width_px, pad_mm, shade, bg=(250, 250, 250)):
    u, v, w = basis
    px, py, pz = V @ u, V @ v, V @ w
    mpp = (max(px.max() - px.min(), py.max() - py.min()) + 2 * pad_mm) / width_px
    height_px = int(np.ceil((py.max() - py.min() + 2 * pad_mm) / mpp))
    SX = (px - px.min() + pad_mm) / mpp
    SY = height_px - (py - py.min() + pad_mm) / mpp
    img = np.zeros((height_px, width_px, 3), np.uint8); img[:, :] = bg
    zb = np.full((height_px, width_px), -1e30)
    tx = np.stack([SX[F[:, 0]], SX[F[:, 1]], SX[F[:, 2]]], 1)
    ty = np.stack([SY[F[:, 0]], SY[F[:, 1]], SY[F[:, 2]]], 1)
    tz = np.stack([pz[F[:, 0]], pz[F[:, 1]], pz[F[:, 2]]], 1)
    x0 = np.clip(np.floor(tx.min(1)).astype(int), 0, width_px - 1)
    x1 = np.clip(np.ceil(tx.max(1)).astype(int), 0, width_px - 1)
    y0 = np.clip(np.floor(ty.min(1)).astype(int), 0, height_px - 1)
    y1 = np.clip(np.ceil(ty.max(1)).astype(int), 0, height_px - 1)
    drawn = 0
    for f in range(len(F)):
        a0, a1, a2 = tx[f]; b0, b1, b2 = ty[f]; c0, c1, c2 = tz[f]
        den = (b1 - b2) * (a0 - a2) + (a2 - a1) * (b0 - b2)
        if abs(den) < 1e-12:
            continue
        xs = np.arange(x0[f], x1[f] + 1); ys = np.arange(y0[f], y1[f] + 1)
        if not len(xs) or not len(ys):
            continue
        X = xs[None, :]; Y = ys[:, None]
        L0 = ((b1 - b2) * (X - a2) + (a2 - a1) * (Y - b2)) / den
        L1 = ((b2 - b0) * (X - a2) + (a0 - a2) * (Y - b2)) / den
        L2 = 1.0 - L0 - L1
        m = (L0 >= -1e-9) & (L1 >= -1e-9) & (L2 >= -1e-9)
        if not m.any():
            continue
        Z = L0 * c0 + L1 * c1 + L2 * c2
        sub = zb[y0[f]:y1[f] + 1, x0[f]:x1[f] + 1]
        upd = m & (Z > sub)
        if not upd.any():
            continue
        sub[upd] = Z[upd]
        img[y0[f]:y1[f] + 1, x0[f]:x1[f] + 1][upd] = shade[f]
        drawn += 1
    return img, mpp, height_px, drawn

def scale_bar(img, mpp, bar_mm=5.0, x0=40, y0=None):
    H, W, _ = img.shape
    if y0 is None:
        y0 = H - 62
    npx = bar_mm / mpp
    seg = npx / 5.0
    if y0 + 24 >= H or x0 + npx + 6 >= W:
        return 0
    img[y0 - 4:y0 + 24, x0 - 4:int(x0 + npx) + 4] = (255, 255, 255)
    for k in range(5):
        a = int(round(x0 + k * seg)); b = int(round(x0 + (k + 1) * seg))
        img[y0:y0 + 20, a:max(b, a + 1)] = (20, 20, 20) if k % 2 == 0 else (255, 255, 255)
    img[y0 - 1:y0 + 21, x0 - 1] = (20, 20, 20)
    img[y0 - 1:y0 + 21, int(x0 + npx)] = (20, 20, 20)
    draw_text(img, x0, y0 + 27, "%g MM = %d PX" % (bar_mm, int(round(npx))), 2)
    return int(round(npx))

def colour_bar(img, x0, y0, h=220, w=26, label="TURNING DEG", lo=0.0, hi=30.0):
    H, W, _ = img.shape
    if y0 + h + 44 >= H or x0 + w + 60 >= W:
        return
    for k in range(h):
        img[y0 + k, x0:x0 + w] = ramp([1.0 - k / (h - 1.0)])[0].astype(np.uint8)
    img[y0 - 2:y0 + h + 2, x0 - 2] = (0, 0, 0)
    img[y0 - 2:y0 + h + 2, x0 + w + 1] = (0, 0, 0)
    img[y0 - 2, x0 - 2:x0 + w + 2] = (0, 0, 0)
    img[y0 + h + 1, x0 - 2:x0 + w + 2] = (0, 0, 0)
    for frac, val in ((0.0, hi), (0.5, 0.5 * (lo + hi)), (1.0, lo)):
        yy = int(y0 + frac * (h - 1))
        img[yy, x0 + w + 2:x0 + w + 7] = (0, 0, 0)
        draw_text(img, x0 + w + 9, yy - 6, "%g" % val, 2)
    draw_text(img, x0 - 2, y0 + h + 10, label, 2)

def basis_from_pca(V):
    c = V - V.mean(0)
    ev, evec = np.linalg.eigh((c.T @ c) / len(V))
    o = np.argsort(ev)[::-1]
    evec = evec[:, o]
    for k in range(3):
        j = int(np.argmax(np.abs(evec[:, k])))
        if evec[j, k] < 0:
            evec[:, k] = -evec[:, k]
    return evec

# ---------------------------------------------------------------- per piece
def process(p, figs_dir, fh, md5s):
    key = "%s_%s" % (p["pot"], p["tag"])
    name = "%s %s" % (p["pot"].replace("_", " "), p["tag"])
    T = dict(topology=[], loops=[], turn_mesh=[], growth=[], thickness=[], carry=[], figures=[])
    t0 = time.time()
    # ---- mesh ----
    V, F, oi = read_obj(p["mesh"])
    Vw, Fw, nw = weld(V, F, WELD_TOL)
    topo = mesh_topology(Vw, Fw)
    area = float(face_area(Vw, Fw).sum())
    bbox = Vw.max(0) - Vw.min(0)
    log("%s: OBJ %d v %d f -> welded %d v; euler %d boundary_edges %d loops %d watertight %s "
        "components %d area %.3f mm2 %.1fs"
        % (name, len(V), len(F), nw, topo["euler"], topo["boundary_edges"], topo["n_loops"],
           topo["watertight"], topo["components"], area, time.time() - t0), fh)
    T["topology"].append([key, name, os.path.basename(p["mesh"]), md5s[p["mesh"]],
                          len(V), nw, WELD_TOL, len(F), topo["E"], topo["euler"],
                          topo["boundary_edges"], topo["nonmanifold"], topo["n_loops"],
                          int(topo["watertight"]), topo["components"], f6(area),
                          f6(bbox[0]), f6(bbox[1]), f6(bbox[2])])
    for k, lp in enumerate(topo["loops"]):
        T["loops"].append([key, k, lp["n_edges"], f6(lp["length_mm"]), int(lp["closed"]),
                           "%.3f,%.3f,%.3f" % tuple(lp["start"])])
    if topo["n_loops"] > len(topo["loops"]):
        T["loops"].append([key, "truncated", topo["n_loops"] - len(topo["loops"]), "", "", ""])
    # ---- mesh turning ----
    vn = vnormals(Vw, Fw)
    vb6 = np.zeros(len(Vw))
    for rad in (0.6, 1.0):
        g = Grid(Vw, rad)
        i, j = g.pairs(Vw, rad)
        d = np.linalg.norm(Vw[i] - Vw[j], axis=1)
        m = (d > 1e-9) & (d <= rad)
        i, j = i[m], j[m]
        ang = pair_angles(vn, i, j)
        vb = np.maximum(scatter_max(len(Vw), i, ang), scatter_max(len(Vw), j, ang))
        if rad == 0.6:
            vb6 = vb
        T["turn_mesh"].append([key, name, rad, len(Vw), 0, len(i),
                               f6(pct(ang, 50)), f6(pct(ang, 90)), f6(ang.max() if len(ang) else None),
                               f6(float((ang > 3.4).mean()) if len(ang) else None),
                               f6(pct(vb, 50)), f6(pct(vb, 90)), f6(vb.max()),
                               f6(float((vb > 3.4).mean())), int((vb > 3.4).sum())])
        log("%s: turning r=%.1f mm over %d vertices: %d pairs, pair med %.3f p90 %.3f max %.3f, "
            "vertex-max med %.3f p90 %.3f max %.3f, %d verts above 3.4 deg"
            % (name, rad, len(Vw), len(i), pct(ang, 50), pct(ang, 90),
               ang.max() if len(ang) else float("nan"), pct(vb, 50), pct(vb, 90), vb.max(),
               int((vb > 3.4).sum())), fh)
    # ---- figures ----
    ev = basis_from_pca(Vw)
    order = np.argsort(bbox)[::-1]
    labels = {0: "VIEW 1 ALONG PC1", 1: "VIEW 2 ALONG PC2", 2: "VIEW 3 ALONG PC3"}
    for idx, wd in [(k, ev[:, k]) for k in range(3)]:
        bas = view_basis(wd)
        shade = shade_from_normals(Vw, Fw, bas)
        img, mpp, hp, drawn = raster(Vw, Fw, bas, 1400, 6.0, shade)
        draw_text(img, 24, 18, name, 4)
        draw_text(img, 24, 62, labels[idx], 3)
        draw_text(img, 24, 100, "EXTENT PC1 PC2 PC3 %0.2f %0.2f %0.2f MM"
                  % (bbox[order[0]], bbox[order[1]], bbox[order[2]]), 2)
        if drawn < 0.9 * len(Fw):
            draw_text(img, 24, 130, "ZBUFFER DREW %d OF %d FACES" % (drawn, len(Fw)), 3, (180, 0, 0))
        npx = scale_bar(img, mpp)
        draw_text(img, 24, hp - 24, "MM/PX %0.5f" % mpp, 2)
        path = os.path.join(figs_dir, "%s_view%d-pc%d.png" % (key, idx + 1, idx + 1))
        nb = write_png(path, img)
        T["figures"].append([name, "view%d-pc%d" % (idx + 1, idx + 1), path, nb,
                             int(img.shape[1]), int(img.shape[0]), f6(mpp), 5.0, npx,
                             "%0.2f,%0.2f,%.2f" % (bbox[order[0]], bbox[order[1]], bbox[order[2]])])
        log("%s: view%d %dx%d mm/px %.5f bar %d px %d B"
            % (name, idx + 1, img.shape[1], img.shape[0], mpp, npx, nb), fh)
    wd = ev[:, 2]
    bas = view_basis(wd)
    base = shade_from_normals(Vw, Fw, bas).astype(float) / 255.0
    col = ramp(np.clip(vb6[Fw].mean(1) / 30.0, 0, 1))
    shade = np.clip(col * (0.45 + 0.75 * base[:, :1]), 0, 255).astype(np.uint8)
    img, mpp, hp, drawn = raster(Vw, Fw, bas, 1400, 6.0, shade)
    draw_text(img, 24, 18, name + " LOCAL TURNING", 4)
    draw_text(img, 24, 62, "PER-VERTEX MAX ANGLE TO NEIGHBOURS WITHIN 0.6 MM", 3)
    draw_text(img, 24, 100, "MEDIAN %0.2f P90 %0.2f MAX %0.2f DEG"
              % (pct(vb6, 50), pct(vb6, 90), vb6.max()), 2)
    draw_text(img, 24, 130, "GATE 3.4 DEG: %d OF %d VERTICES ABOVE" % (int((vb6 > 3.4).sum()), len(vb6)), 2)
    npx = scale_bar(img, mpp)
    colour_bar(img, 1400 - 100, 210)
    path = os.path.join(figs_dir, "%s_view4-turning.png" % key)
    nb = write_png(path, img)
    T["figures"].append([name, "view4-turning", path, nb, int(img.shape[1]), int(img.shape[0]),
                         f6(mpp), 5.0, npx,
                         "%0.2f,%0.2f,%.2f" % (bbox[order[0]], bbox[order[1]], bbox[order[2]])])
    log("%s: view4-turning %dx%d bar %d px %d B" % (name, img.shape[1], img.shape[0], npx, nb), fh)
    # ---- thickness: ticket 20's 800-ray method, unchanged ----
    C, cols = read_ply_vertices(p["arm"])
    def pick(cands):
        for c in cands:
            if c in cols:
                return cols.index(c)
        raise ValueError("PLY has none of %r in %r" % (cands, cols))
    P = np.stack([C[:, pick(("x",))], C[:, pick(("y",))], C[:, pick(("z",))]], 1)
    ncols = [pick(("normal_x", "nx")), pick(("normal_y", "ny")), pick(("normal_z", "nz"))]
    Pn = unit(np.stack([C[:, c] for c in ncols], 1))[0]
    curv_ply = C[:, cols.index("curvature")] if "curvature" in cols else None
    step = max(1, len(P) // 800)
    p0 = P[::step]
    nn = Pn[::step]
    nn = nn / np.maximum(np.linalg.norm(nn, axis=1, keepdims=True), 1e-30)
    hits = ray_hits(Vw, Fw, p0 + nn * 1e-3, -nn)
    thick = np.full(len(hits), np.nan)
    counts = np.zeros(len(hits), int)
    for r, t in enumerate(hits):
        counts[r] = t.size
        tt = t[t > 0.15]
        if tt.size:
            thick[r] = tt.min()
    th = thick[np.isfinite(thick)]
    T["thickness"].append([key, name, os.path.basename(p["arm"]), len(P), len(p0),
                           int((counts >= 1).sum()), f6(pct(th, 50)), f6(pct(th, 10)),
                           f6(pct(th, 90)), f6(float(((th >= 1) & (th <= 3)).mean())),
                           int(np.median(counts)), int(counts.max()),
                           int((counts >= 2).sum()), int((counts >= 3).sum()),
                           f6(float((counts >= 3).mean())), int(np.isfinite(thick).sum())])
    log("%s: thickness on %d rays: med %.4f p10 %.4f p90 %.4f frac1-3 %.4f hits med %d max %d "
        ">=2 sheets %d >=3 sheets %d"
        % (name, len(p0), pct(th, 50), pct(th, 10), pct(th, 90),
           float(((th >= 1) & (th <= 3)).mean()) if th.size else float("nan"),
           int(np.median(counts)), counts.max(), int((counts >= 2).sum()), int((counts >= 3).sum())), fh)
    # ---- cloud: carry normals from the scan, then growth ----
    PR, NR, ri = read_pcd(p["pcd"])
    if NR is None:
        raise ValueError("PCD has no normals: %r" % (ri["fields"],))
    NRu, okn = unit(NR)
    ref, refn = PR[okn], NRu[okn]
    log("%s: PCD %s %d points (%s), %d usable normals"
        % (name, ri["kind"], ri["n"], ",".join(ri["fields"]), len(ref)), fh)
    gq = grid_for(ref, 1)
    idx, dist, _ = gq.knn(P, 1)
    carry = refn[idx[:, 0]]
    dmax = float(dist[:, 0].max())
    if dmax > 0.5 * gq.cell:
        raise ValueError("carry sufficiency broken: max nearest %.4f > cell/2 %.4f" % (dmax, 0.5 * gq.cell))
    ang_cv = pair_angles(np.vstack([carry, Pn]), np.arange(len(P)),
                         np.arange(len(P)) + len(P))
    kcurv = int(max(10, min(50, len(P) // 300)))
    K = max(NB + 1, kcurv + 1)
    gc = grid_for(P, K)
    nbr, ndist, badc = gc.knn(P, K)
    if badc:
        raise ValueError("cloud kNN sufficiency broken: %d rows with d_K > cell" % badc)
    log("%s: carry max nearest %.4f mm (grid cell %.4f); cloud kNN k=%d cell %.4f nn med %.4f"
        % (name, dmax, gq.cell, K, gc.cell, float(np.median(ndist[:, 1]))), fh)
    T["carry"].append([key, name, len(P), len(ref), f6(dmax), f6(gq.cell),
                       f6(pct(ang_cv, 50)), f6(pct(ang_cv, 90))])
    curv_re = pca_curvature(P, nbr[:, 1:1 + kcurv])
    srcs = [("recomputed(k=%d)" % kcurv, curv_re)]
    if curv_ply is not None:
        srcs.append(("ply-column", curv_ply))
    M = NB
    ni = np.repeat(np.arange(len(P)), M)
    nj = nbr[:, 1:1 + M].ravel()
    m = ni < nj
    ni, nj = ni[m], nj[m]
    for nm_name, nm_vec in (("pca", Pn), ("carry", carry)):
        ang = pair_angles(nm_vec, ni, nj)
        keep = ang <= THETA
        nc, big = comp_sizes(len(P), ni[keep], nj[keep])
        for cname, cvec in srcs:
            regs = grow(nm_vec, cvec, nbr, THETA, KAPPA, NB)
            T["growth"].append([key, name, len(P), nm_name, cname, K, THETA, KAPPA, NB,
                                len(ni), f6(pct(ang, 50)), f6(pct(ang, 90)), f6(ang.max()),
                                len(regs), regs[0] if regs else 0,
                                ";".join(str(x) for x in regs[:6]), nc, big,
                                f6(big / float(len(P)))])
            log("%s: growth normals=%s curvature=%s -> %d regions, largest %d; "
                "3.4 deg symmetric rule: %d components, largest %d pts (%.1f%%), %d edges kept"
                % (name, nm_name, cname, len(regs), regs[0] if regs else 0,
                   nc, big, 100.0 * big / len(P), int(keep.sum())), fh)
    return T

# ---------------------------------------------------------------- selftest
def selftest(fh):
    ok = True
    V = np.array([[x, y, z] for x in (0, 10) for y in (0, 10) for z in (0, 10)], float)
    F = np.array([[0, 1, 3], [0, 3, 2], [4, 6, 7], [4, 7, 5], [0, 4, 5], [0, 5, 1],
                  [2, 3, 7], [2, 7, 6], [0, 2, 6], [0, 6, 4], [1, 5, 7], [1, 7, 3]], np.int64)
    t = mesh_topology(V, F)
    a = float(face_area(V, F).sum())
    log("selftest cube: euler %d boundary %d watertight %s area %.3f (want 2/0/True/600)"
        % (t["euler"], t["boundary_edges"], t["watertight"], a), fh)
    ok &= (t["euler"] == 2 and t["boundary_edges"] == 0 and t["watertight"] and abs(a - 600) < 1e-9
           and t["components"] == 1)
    Vs = V.copy(); Vs[:, 2] *= 0.2            # 2 mm slab
    h = ray_hits(Vs, F, np.array([[5.0, 5.0, -5.0]]), np.array([[0.0, 0.0, 1.0]]))[0]
    log("selftest slab: %d hits at %s (want 2: 5 7)" % (len(h), np.round(h, 6).tolist()), fh)
    ok &= (len(h) == 2 and abs(h[0] - 5) < 1e-9 and abs(h[1] - 7) < 1e-9)
    rng = np.random.default_rng(7)
    Q = rng.random((300, 3)) * 5.0
    g = grid_for(Q, 4)
    idx, dd, bad = g.knn(Q, 4)
    brute = np.sort(np.linalg.norm(Q[:, None, :] - Q[None, :, :], axis=2), 1)[:, :4]
    err = float(np.abs(dd - brute).max())
    i, j = g.pairs(Q, 0.6)
    bd = np.linalg.norm(Q[i] - Q[j], axis=1)
    log("selftest grid: kNN max err %.3g bad %d, %d pairs max d %.4f (want 0/0/<=0.6)"
        % (err, bad, len(i), bd.max() if len(bd) else 0.0), fh)
    ok &= (err < 1e-9 and bad == 0 and (not len(bd) or bd.max() <= 0.6 + 1e-12))
    sm = scatter_max(5, np.array([0, 0, 2]), np.array([1.0, 3.0, 2.0]))
    log("selftest scatter_max: %s (want 3 0 2 0 0)" % sm.tolist(), fh)
    ok &= (sm.tolist() == [3.0, 0.0, 2.0, 0.0, 0.0])
    with open("/tmp/t35_selftest.ply", "w") as f:
        f.write("ply\nformat ascii 1.0\nelement vertex 2\nproperty float x\nproperty float y\n"
                "property float z\nproperty float nx\nelement camera 1\nproperty float f\n"
                "property float g\nend_header\n0 0 0 1\n1 2 3 1\n9 9\n")
    arr, names = read_ply_vertices("/tmp/t35_selftest.ply")
    log("selftest ply: shape %s names %s (want (2,4))" % (arr.shape, names), fh)
    ok &= (arr.shape == (2, 4) and arr[1, 2] == 3)
    with open("/tmp/t35_selftest.pcd", "wb") as f:
        f.write(b"# .PCD v0.7\nVERSION 0.7\nFIELDS normal_x normal_y normal_z x y z _\n"
                b"SIZE 4 4 4 4 4 4 1\nTYPE F F F F F F U\nCOUNT 1 1 1 1 1 1 4\n"
                b"WIDTH 2\nHEIGHT 1\nPOINTS 2\nDATA binary\n")
        f.write(struct.pack("<6f4B", 0, 0, 1, 1, 2, 3, 0, 0, 0, 0))
        f.write(struct.pack("<6f4B", 0, 1, 0, 4, 5, 6, 0, 0, 0, 0))
    P, N, info = read_pcd("/tmp/t35_selftest.pcd")
    log("selftest pcd binary: n %d stride-ok, P1 %s N1 %s (want [4,5,6] [0,1,0])"
        % (info["n"], P[1].tolist(), N[1].tolist()), fh)
    ok &= (info["n"] == 2 and P[1].tolist() == [4.0, 5.0, 6.0] and N[1].tolist() == [0.0, 1.0, 0.0])
    with open("/tmp/t35_selftest2.pcd", "w") as f:
        f.write("# .PCD v0.7\nFIELDS x y z normal_x normal_y normal_z\nSIZE 4 4 4 4 4 4\n"
                "TYPE F F F F F F\nCOUNT 1 1 1 1 1 1\nWIDTH 2\nHEIGHT 1\nPOINTS 2\nDATA ascii\n"
                "1 2 3 0 0 1\n4 5 6 0 1 0\n")
    P2, N2, i2 = read_pcd("/tmp/t35_selftest2.pcd")
    log("selftest pcd ascii: n %d P1 %s N1 %s (want [4,5,6] [0,1,0])"
        % (i2["n"], P2[1].tolist(), N2[1].tolist()), fh)
    ok &= (i2["n"] == 2 and P2[1].tolist() == [4.0, 5.0, 6.0] and N2[1].tolist() == [0.0, 1.0, 0.0])
    with open("/tmp/t35_selftest.obj", "w") as f:
        f.write("# c\nv 0 0 0\nv 1 0 0\nv 0 1 0\nv 1 1 0\nvn 0 0 1\nf 1/1/1 2/2/2 3/3/3\nf 2/2/2 4/4/4 3/3/3\n")
    V2, F2, _ = read_obj("/tmp/t35_selftest.obj")
    log("selftest obj: %d v %d f -> %s (want 4 2 [[0,1,2],[1,3,2]])" % (len(V2), len(F2), F2.tolist()), fh)
    ok &= (len(V2) == 4 and F2.tolist() == [[0, 1, 2], [1, 3, 2]])
    img = np.zeros((40, 60, 3), np.uint8); img[:, :] = (10, 20, 30)
    nb = write_png("/tmp/t35_selftest.png", img)
    ok &= (nb > 0)
    log("selftest png: %d B" % nb, fh)
    log("SELFTEST %s" % ("PASS" if ok else "FAIL"), fh)
    return bool(ok)

# ---------------------------------------------------------------- driver
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--pieces", default="")
    ap.add_argument("--selftest-only", action="store_true")
    args = ap.parse_args()
    tables = os.path.join(args.out, "tables")
    figs = os.path.join(args.out, "figures")
    os.makedirs(tables, exist_ok=True)
    os.makedirs(figs, exist_ok=True)
    fh = open(os.path.join(args.out, "measure.log"), "a")
    log("python %s numpy %s" % (sys.version.split()[0], np.__version__), fh)
    if not selftest(fh):
        log("ABORT: selftest failed", fh)
        return 3
    if args.selftest_only:
        return 0
    want = [x.strip() for x in args.pieces.split(",") if x.strip()]
    pieces = [p for p in PIECES if not want or p["tag"] in want]
    missing = [p["tag"] for p in pieces if not all(os.path.exists(p[k]) for k in ("mesh", "pcd", "arm"))]
    if missing:
        for p in pieces:
            for k in ("mesh", "pcd", "arm"):
                if not os.path.exists(p[k]):
                    log("MISSING %s %s: %s" % (p["tag"], k, p[k]), fh)
        return 4
    rows = []
    for p in pieces:
        for role, path in (("mesh", p["mesh"]), ("pcd", p["pcd"]), ("cloud0.6", p["arm"])):
            rows.append([path, role, os.path.getsize(path), md5_of(path)])
    before = {r[0]: r[3] for r in rows}
    log("md5 before: %d files" % len(rows), fh)
    allT = dict(topology=[], loops=[], turn_mesh=[], growth=[], thickness=[], carry=[],
                figures=[], failures=[], timing=[])
    COLS = {
     "topology": ["piece_key", "piece", "mesh_file", "mesh_md5", "v_raw", "v_welded",
                  "weld_tol_mm", "f", "e", "euler_chi", "boundary_edges", "nonmanifold_edges",
                  "boundary_loops", "watertight", "components", "area_mm2", "bbox_pc_x",
                  "bbox_pc_y", "bbox_pc_z"],
     "boundary_loops": ["piece_key", "loop", "n_edges", "length_mm", "closed", "start_xyz"],
     "turning_mesh": ["piece_key", "piece", "radius_mm", "n_vertices", "sampled", "n_pairs",
                      "pair_med_deg", "pair_p90_deg", "pair_max_deg", "frac_pairs_gt_3p4",
                      "vert_max_med_deg", "vert_max_p90_deg", "vert_max_max_deg",
                      "frac_verts_gt_3p4", "n_verts_gt_3p4"],
     "turning_cloud_growth": ["piece_key", "piece", "cloud_pts", "normals", "curvature",
                              "k_nn", "theta_deg", "kappa", "nb", "n_edges", "edge_med_deg",
                              "edge_p90_deg", "edge_max_deg", "greedy_n_regions",
                              "greedy_largest", "greedy_top6", "comp_n_components",
                              "comp_largest_pts", "comp_largest_share"],
     "thickness": ["piece_key", "piece", "cloud_file", "cloud_pts", "rays", "rays_with_a_hit",
                   "thick_med_mm", "thick_p10_mm", "thick_p90_mm", "frac_1to3mm",
                   "hits_per_ray_med", "hits_per_ray_max", "rays_2plus_sheets",
                   "rays_gt2_sheets", "frac_rays_gt2_sheets", "rays_with_a_hit_0p15"],
     "carry": ["piece_key", "piece", "cloud_pts", "pcd_pts_used", "max_nn_dist_mm",
               "grid_cell_mm", "carry_vs_pca_med_deg", "carry_vs_pca_p90_deg"],
     "figures": ["piece", "view", "path", "bytes", "width_px", "height_px", "mm_per_px",
                 "scale_bar_mm", "scale_bar_px", "extent_pc1_pc2_pc3_mm"],
    }
    def dump():
        for tname, cols in COLS.items():
            with open(os.path.join(tables, tname + ".tsv"), "w") as f:
                f.write(tsv(cols, allT[tname]))
        with open(os.path.join(args.out, "state.json"), "w") as f:
            json.dump(allT, f, indent=1)
    for p in pieces:
        t0 = time.time()
        try:
            T = process(p, figs, fh, before)
            for k, v in T.items():
                allT[k].extend(v)
            st = "ok"
        except Exception:
            tb = traceback.format_exc()
            log("%s FAILED\n%s" % (p["tag"], tb), fh)
            allT["failures"].append([p["pot"] + "_" + p["tag"], tb.strip().splitlines()[-1]])
            st = "failed"
        allT["timing"].append([p["pot"] + "_" + p["tag"], st, "%.1f" % (time.time() - t0)])
        dump()
    with open(os.path.join(tables, "failures.tsv"), "w") as f:
        f.write(tsv(["piece_key", "error"], allT["failures"]))
    with open(os.path.join(tables, "timing.tsv"), "w") as f:
        f.write(tsv(["piece_key", "status", "seconds"], allT["timing"]))
    aft = []
    for path, role, size, m0 in rows:
        m1 = md5_of(path)
        aft.append([path, role, size, m0, m1, int(m0 == m1)])
    with open(os.path.join(tables, "md5_check.tsv"), "w") as f:
        f.write(tsv(["file", "role", "bytes", "md5_before", "md5_after", "unchanged"], aft))
    log("md5 after: %d unchanged of %d" % (sum(r[5] for r in aft), len(aft)), fh)
    # ---- instrument checks: numbers already on record ----
    tk = {r[0]: r for r in allT["topology"]}
    th = {r[0]: r for r in allT["thickness"]}
    gr = {(r[0], r[3], r[4].split("(")[0]): r for r in allT["growth"]}
    chk = []
    def add(name, src, rec, meas, tol):
        try:
            r = float(rec); m = float(meas)
            d = abs(m - r)
            rel = d / abs(r) if r else float("inf")
            verdict = "identical" if d == 0 else ("within %g" % tol if rel <= tol else "DIFFERS")
            chk.append([name, src, rec, f6(m), f6(d), "%.3g" % rel, verdict])
        except Exception as e:
            chk.append([name, src, rec, str(meas), "", "", "unavailable"])
    for tag, ref in P20.items():
        k = ("Juglet_" + tag) if tag != "07" else "Pot_A_07"
        t = tk.get(k); x = th.get(k)
        if t:
            add("ticket20 v_raw piece %s" % tag, "C_mesh.tsv", ref["V"], t[4], 0)
            add("ticket20 f piece %s" % tag, "C_mesh.tsv", ref["F"], t[7], 0)
            add("ticket20 area_mm2 piece %s" % tag, "C_mesh.tsv", ref["area"], t[15], 1e-6)
        if x:
            add("ticket20 rays piece %s" % tag, "C_mesh.tsv", ref["rays"], x[4], 0)
            add("ticket20 thick_med_mm piece %s" % tag, "C_mesh.tsv", ref["med"], x[6], 1e-6)
            add("ticket20 thick_p10_mm piece %s" % tag, "C_mesh.tsv", ref["p10"], x[7], 1e-6)
            add("ticket20 thick_p90_mm piece %s" % tag, "C_mesh.tsv", ref["p90"], x[8], 1e-6)
            add("ticket20 frac_1to3 piece %s" % tag, "C_mesh.tsv", ref["f13"], x[9], 1e-6)
            add("ticket20 hits_per_ray_max piece %s" % tag, "C_mesh.tsv", ref["hmax"], x[11], 0)
            add("ticket20 rays_with_2plus piece %s" % tag, "C_mesh.tsv", ref["r2"], x[12], 0)
    for tag, want in T28.items():
        r = gr.get(("Juglet_" + tag, "pca", "recomputed"))
        if r:
            add("ticket28 greedy largest piece %s" % tag, "tickets 28/33", want, r[14], 0)
    with open(os.path.join(tables, "instrument_checks.tsv"), "w") as f:
        f.write(tsv(["check", "source", "recorded", "measured", "abs_diff", "rel_diff", "match"], chk))
    log("instrument checks: %d rows, %d identical, %d differ"
        % (len(chk), sum(1 for c in chk if c[6] == "identical"),
           sum(1 for c in chk if c[6] == "DIFFERS")), fh)
    fh.close()
    return 0 if not allT["failures"] else 1

if __name__ == "__main__":
    sys.exit(main())
