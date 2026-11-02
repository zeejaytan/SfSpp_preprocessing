#!/usr/bin/env python3
"""Ticket 59 Stage 0 probe: mesh-structural labels + four signals. READ-ONLY over
Dataset and the t55 run of record; writes only under its own --out dir.

Labels (per mesh, from mesh structure only, no t55 claims):
  union-find over face-adjacency edges with dihedral < T_d  -> components
  smooth comps = area >= min_frac * total area; rough = rest
  t_piece from vertex-slab pairing on smooth faces
  wall      = smooth  AND paired (along in [0.5t,2.5t], exit dot <= -0.5)
  roll      = smooth  AND NOT wall-paired
  fracture  = rough   AND NOT paired ([0.5t,2.5t], dot <= -0.5)
  anomaly   = rough   AND paired (reported, counted separately)

Signals (measured once per face/vertex, regrouped per label variant):
  (a) plane-fit deviation of ball neighbourhood at face centroid, radii 1.0/1.5/2.0/3.0 mm
  (b) exact ray-triangle cast along -normal, slab 1.5*t_piece: hit_dist, hit-face-normal dot
  (c) geodesic-window normal turn T(v,L) at pure-label source vertices, L in {2,5,10,Lf}
      Lf = (pi/4)*Rf, Rf = mesh-side fold radius from band pairs at geodesic 1.5-2.5 mm
  (d) t55 claim clouds vs labels: per-face covered shares + boundary-midpoint distances
"""
import argparse, hashlib, json, math, os, sys, time
import numpy as np
import trimesh
from scipy.spatial import cKDTree
from scipy.sparse import coo_matrix
from scipy.sparse.csgraph import dijkstra

BALL_RADII = [1.0, 1.5, 2.0, 3.0]
TDS = [8.0, 10.0, 15.0]          # dihedral thresholds, 10 primary
MINFRACS = [0.02, 0.03, 0.05]    # smooth-comp area fraction, 0.03 primary
PRIMARY = (10.0, 0.03)
SLAB_PERP = 0.75
SLAB_ALONG_MIN, SLAB_ALONG_MAX = 0.25, 4.0
EXIT_DOT = -0.5
RAY_EPS = 0.01
WINDOWS = [2.0, 5.0, 10.0]
SRC_CAP_LABEL = 800
SRC_CAP_POTA = 150
BATCH = 64

def log(msg):
    print(f"[{time.strftime('%H:%M:%S')}] {msg}", flush=True)

def fmd5(path):
    h = hashlib.md5()
    with open(path, 'rb') as f:
        for chunk in iter(lambda: f.read(1 << 20), b''):
            h.update(chunk)
    return h.hexdigest()

# ---------------- mesh ----------------

def load_mesh(path):
    m = trimesh.load(path, process=False, force='mesh')
    if not m.is_watertight:
        m.fix_normals(multibody=True)
    V = np.asarray(m.vertices, dtype=np.float64)
    F = np.asarray(m.faces, dtype=np.int64)
    tri = V[F]
    fn = np.cross(tri[:, 1] - tri[:, 0], tri[:, 2] - tri[:, 0])
    fa2 = np.linalg.norm(fn, axis=1)
    area = 0.5 * fa2
    ok = fa2 > 0
    fn = np.zeros_like(fn)
    fn[ok] = (fn[ok] / fa2[ok, None])
    cen = tri.mean(axis=1)
    vn = np.zeros_like(V)
    for k in range(3):
        np.add.at(vn, F[:, k], fn * area[:, None])
    nrm = np.linalg.norm(vn, axis=1)
    vn[nrm > 0] = vn[nrm > 0] / nrm[nrm > 0, None]
    return V, F, fn, area, cen, vn, bool(m.is_watertight)

def face_adjacency(F):
    edges = {}
    for k in range(3):
        a, b = F[:, k], F[:, (k + 1) % 3]
        lo = np.minimum(a, b); hi = np.maximum(a, b)
        for e0, e1, f in zip(lo, hi, np.arange(len(F))):
            key = (int(e0), int(e1))
            lst = edges.get(key)
            if lst is None:
                edges[key] = [int(f)]
            elif len(lst) == 1:
                lst.append(int(f))
            else:
                lst.append(int(f))
    pairs = [(v[0], v[1]) for v in edges.values() if len(v) == 2]
    return np.asarray(pairs, dtype=np.int64).reshape(-1, 2), edges

class DSU:
    def __init__(self, n):
        self.p = np.arange(n)
    def find(self, x):
        p = self.p
        while p[x] != x:
            p[x] = p[p[x]]
            x = p[x]
        return x
    def union(self, a, b):
        ra, rb = self.find(a), self.find(b)
        if ra != rb:
            self.p[rb] = ra

def labels_for(T_d, min_frac, adj, dihedral, area):
    dsu = DSU(len(area))
    sel = adj[dihedral < T_d]
    for a, b in sel:
        dsu.union(int(a), int(b))
    root = np.array([dsu.find(i) for i in range(len(area))])
    comp_area = {}
    for r, a in zip(root, area):
        comp_area[r] = comp_area.get(r, 0.0) + float(a)
    total = float(area.sum())
    smooth_comp = {r for r, a in comp_area.items() if a >= min_frac * total}
    smooth = np.array([r in smooth_comp for r in root])
    comps_sorted = sorted(comp_area.items(), key=lambda kv: -kv[1])
    return smooth, root, comp_area, comps_sorted

# ---------------- pairing ----------------

def vertex_slab_pairs(V, vn, cen, fn, area, smooth, tree):
    """per face: nearest opposing-slab vertex hit; returns along (min), paired mask (rough def)"""
    n = len(cen)
    along_min = np.full(n, np.nan)
    hit_dot = np.full(n, np.nan)
    idx_lists = tree.query_ball_point(cen, SLAB_ALONG_MAX + SLAB_PERP + 0.2, workers=8)
    for i in range(n):
        cand = idx_lists[i]
        if not cand:
            continue
        c = cen[i]; nv = fn[i]
        d = V[cand] - c
        along = -(d @ nv)
        perp2 = (d * d).sum(1) - along * along
        m = (along > SLAB_ALONG_MIN) & (along < SLAB_ALONG_MAX) & (perp2 < SLAB_PERP * SLAB_PERP)
        if not m.any():
            continue
        cd = np.where(m)[0]
        dots = vn[cand[cd]] @ nv
        ok = dots <= EXIT_DOT
        if ok.any():
            aa = along[cd][ok]
            k = int(np.argmin(aa))
            along_min[i] = aa[k]
            hit_dot[i] = dots[k]
    return along_min, hit_dot

def ray_cast(V, F, fn, cen, tree_f, t_piece):
    """exact ray-triangle along -normal up to 1.5*t+0.5; returns hit_dist, hit_dot, self-excluded."""
    n = len(cen)
    L = 1.5 * t_piece + 0.5
    hit_dist = np.full(n, np.nan)
    hit_dot = np.full(n, np.nan)
    tri = V[F]
    CH = 512
    for s in range(0, n, CH):
        e = min(n, s + CH)
        rays = np.arange(s, e)
        o = cen[rays] + RAY_EPS * fn[rays]
        d = -fn[rays]
        cand = tree_f.query_ball_point(cen[rays], L + 2.0, workers=8)
        fl_r, fl_t = [], []
        for ri, cl in enumerate(cand):
            for tj in cl:
                if tj == rays[ri]:
                    continue
                fl_r.append(ri); fl_t.append(tj)
        if not fl_r:
            continue
        fl_r = np.asarray(fl_r); fl_t = np.asarray(fl_t)
        A = tri[fl_t, 0]; B = tri[fl_t, 1]; C = tri[fl_t, 2]
        oo = o[fl_r]; dd = d[fl_r]
        e1 = B - A; e2 = C - A
        h = np.cross(dd, e2)
        a = (e1 * h).sum(1)
        valid = np.abs(a) > 1e-14
        f = np.zeros_like(a)
        f[valid] = 1.0 / a[valid]
        u = f * ((oo - A) * h).sum(1)
        q = np.cross(oo - A, e1)
        v = f * (dd * q).sum(1)
        tt = f * (e2 * q).sum(1)
        valid &= (u >= 0) & (v >= 0) & (u + v <= 1) & (tt > RAY_EPS) & (tt <= L)
        if not valid.any():
            continue
        rr_local = fl_r[valid]; dist = tt[valid]; fidx = fl_t[valid]
        for rl in np.unique(rr_local):
            mm = rr_local == rl
            k = int(np.argmin(dist[mm]))
            gi = int(rays[rl])
            hit_dist[gi] = dist[mm][k]
            hit_dot[gi] = float(fn[fidx[mm][k]] @ fn[gi])
    return hit_dist, hit_dot

# ---------------- roughness ----------------

def plane_dev(cen, tree_v, V, radius):
    n = len(cen)
    dev = np.full(n, np.nan)
    CH = 2048
    for s in range(0, n, CH):
        e = min(n, s + CH)
        pts = cen[s:e]
        cand = tree_v.query_ball_point(pts, radius, workers=8)
        for i, cl in enumerate(cand):
            if len(cl) < 8:
                continue
            P = V[cl]
            P = P - P.mean(0)
            cov = (P.T @ P) / len(P)
            w, vecs = np.linalg.eigh(cov)
            d = P @ vecs[:, 0]
            dev[s + i] = math.sqrt(float((d * d).mean()))
    return dev

# ---------------- geodesic turn ----------------

def edge_graph(V, F):
    a = np.concatenate([F[:, 0], F[:, 1], F[:, 2]])
    b = np.concatenate([F[:, 1], F[:, 2], F[:, 0]])
    lo = np.minimum(a, b); hi = np.maximum(a, b)
    key = lo.astype(np.int64) * (len(V) + 1) + hi
    uk = np.unique(key)
    src = (uk // (len(V) + 1)).astype(np.int64)
    dst = (uk % (len(V) + 1)).astype(np.int64)
    w = np.linalg.norm(V[src] - V[dst], axis=1)
    g = coo_matrix((w, (src, dst)), shape=(len(V), len(V))).tocsr()
    return g

def window_turn(g, V, vn, sources, L, maxL):
    dist = dijkstra(g, directed=False, indices=sources, limit=maxL + 0.1)
    tmed, tp90, nrng = [], [], []
    nv = vn / np.maximum(np.linalg.norm(vn, axis=1, keepdims=True), 1e-30)
    for r in range(len(sources)):
        d = dist[r]
        m = (d >= 0.8 * L) & (d <= L) & np.isfinite(d)
        k = int(m.sum())
        if k < 20:
            tmed.append(np.nan); tp90.append(np.nan); nrng.append(k)
            continue
        dots = np.clip(nv[m] @ nv[sources[r]], -1, 1)
        ang = np.degrees(np.arccos(dots))
        tmed.append(float(np.median(ang))); tp90.append(float(np.percentile(ang, 90)))
        nrng.append(k)
    return np.asarray(tmed), np.asarray(tp90), nrng

def fold_radius(g, V, vn, band_sources, maxL=2.6):
    if len(band_sources) == 0:
        return np.nan
    dist = dijkstra(g, directed=False, indices=band_sources, limit=maxL)
    ratios = []
    nv = vn / np.maximum(np.linalg.norm(vn, axis=1, keepdims=True), 1e-30)
    for r in range(len(band_sources)):
        d = dist[r]
        m = (d >= 1.5) & (d <= 2.5) & np.isfinite(d)
        k = int(m.sum())
        if k < 10:
            continue
        dots = np.clip(nv[m] @ nv[sources := band_sources[r]], -1, 1)
        ang = np.arccos(dots)
        ang[ang < 1e-6] = np.nan
        rat = d[m] / ang
        rat = rat[np.isfinite(rat)]
        if len(rat):
            ratios.append(float(np.median(rat)))
    return float(np.median(ratios)) if ratios else np.nan

# ---------------- erosion ----------------

def erode(face_lab, adj, rings=2):
    lab = face_lab.copy()
    n = len(lab)
    adjl = {}
    for a, b in adj:
        adjl.setdefault(int(a), []).append(int(b))
        adjl.setdefault(int(b), []).append(int(a))
    cur = lab.copy()
    for _ in range(rings):
        nxt = cur.copy()
        for i in range(n):
            nb = adjl.get(i)
            if nb and any(cur[j] != cur[i] for j in nb):
                nxt[i] = -1
        cur = nxt
    core = cur >= 0
    return core & (lab >= 0)

# ---------------- PLY ----------------

def read_ply_vertices(path):
    nvert = None; props = 0; in_vert = False; hdr_done = False; elements = []
    with open(path, 'r', errors='replace') as f:
        lines = f.readlines()
    i = 0
    while i < len(lines):
        ln = lines[i].strip()
        if ln == 'end_header':
            i += 1
            break
        if ln.startswith('element'):
            parts = ln.split()
            elements.append((parts[1], int(parts[2])))
            in_vert = parts[1] == 'vertex'
            if in_vert:
                nvert = int(parts[2])
                props = 0
        elif ln.startswith('property') and in_vert:
            props += 1
        i += 1
    if nvert is None or props == 0:
        raise ValueError(f'bad ply header {path}')
    rows = []
    for j in range(nvert):
        rows.append(lines[i + j].split())
    arr = np.asarray(rows, dtype=np.float64)
    return arr[:, :3] if arr.shape[1] >= 3 else arr

def point_tri_dist(P, A, B, C):
    AB = B - A; AC = C - A; AP = P - A
    d1 = (AB * AP).sum(1); d2 = (AC * AP).sum(1)
    N = len(P)
    res = np.empty(N)
    # region A
    mA = (d1 <= 0) & (d2 <= 0)
    res[mA] = np.linalg.norm(AP[mA], axis=1)
    # region B
    BP = P - B
    d3 = (AB * BP).sum(1); d4 = (AC * BP).sum(1)
    mB = (~mA) & (d3 >= 0) & (d4 <= d3)
    res[mB] = np.linalg.norm(BP[mB], axis=1)
    # region C
    CP = P - C
    d5 = (AB * CP).sum(1); d6 = (AC * CP).sum(1)
    mC = (~mA) & (~mB) & (d6 >= 0) & (d5 <= d6)
    res[mC] = np.linalg.norm(CP[mC], axis=1)
    # edge AB
    vc = d1 * d4 - d3 * d2
    mAB = (~mA) & (~mB) & (~mC) & (vc <= 0) & (d1 >= 0) & (d3 <= 0)
    if mAB.any():
        t = (d1[mAB] / (d1[mAB] - d3[mAB]))[:, None]
        res[mAB] = np.linalg.norm(AP[mAB] + t * AB[mAB], axis=1)
    # edge BC
    d11 = (AB * CP).sum(1); d12 = (AC * CP).sum(1)  # note: reuse
    vb = d5 * d2 - d1 * d6  # not used directly; use standard form below
    # BC: denom = (d4-d3)*(d2-d1)-(d6-d5)*(d1-d3)? fallback generic: project on segment
    rest = ~(mA | mB | mC | mAB)
    if rest.any():
        # edge BC
        for nm, PP, QQ, AA in (('BC', BP, CP, AB), ('CA', CP, AP, AC)):
            pass
    # generic edge/interior for the rest
    m = rest
    if m.any():
        # edge BC
        e1 = C - B
        t1 = np.clip(((P[m] - B) * e1).sum(1) / np.maximum((e1 * e1).sum(1), 1e-30), 0, 1)
        pBC = B + t1[:, None] * e1
        # edge CA
        e2 = A - C
        t2 = np.clip(((P[m] - C) * e2).sum(1) / np.maximum((e2 * e2).sum(1), 1e-30), 0, 1)
        pCA = C + t2[:, None] * e2
        # interior: barycentric
        va = d3 * d6 - d5 * d4  # not standard; do full barycentric
        den = d1[m] * (d6[m] - d4[m]) - d3[m] * (d2[m] - d5[m]) * 0  # placeholder
        # robust: normal projection
        nn = np.cross(AB[m], AC[m])
        nlen = np.maximum(np.linalg.norm(nn, axis=1), 1e-30)
        nn = nn / nlen[:, None]
        dist_plane = np.abs((AP[m] * nn).sum(1))
        # decide interior via barycentric with cross products
        u = np.cross(AP[m], AC[m]); v = np.cross(AB[m], AP[m])
        s1 = np.sign((u * nn).sum(1)); s2 = np.sign((v * nn).sum(1))
        inside = (s1 >= 0) & (s2 >= 0)
        dist_bc = np.linalg.norm(P[m] - pBC, axis=1)
        dist_ca = np.linalg.norm(P[m] - pCA, axis=1)
        r = np.where(inside, dist_plane, np.minimum(dist_bc, dist_ca))
        res[m] = r
    return res

def nearest_faces(P, V, F, tree_f, fcen, k0=32):
    k = k0
    kd, ki = tree_f.query(P, k=k, workers=8)
    if kd.ndim == 1:
        kd = kd[:, None]; ki = ki[:, None]
    best = np.full(len(P), np.inf)
    bidx = np.full(len(P), -1, dtype=np.int64)
    for it in range(6):
        cand_best = np.full(len(P), np.inf)
        # exact distance to candidate triangles in chunks
        for s in range(0, len(P), 4096):
            e = min(len(P), s + 4096)
            chunk_idx = np.unique(ki[s:e].ravel())
            chunk_idx = chunk_idx[chunk_idx >= 0]
            tri = V[F[chunk_idx]]
            loc = {int(g): j for j, g in enumerate(chunk_idx)}
            sub = ki[s:e]
            A = tri[np.vectorize(lambda g: loc[int(g)])(sub), 0]
            # too slow path avoided below
        # simpler: per-point loop over k candidates (k small)
        for i in range(len(P)):
            cs = [g for g in ki[i] if g >= 0]
            if not cs:
                continue
            cs = np.asarray(cs)
            d = point_tri_dist(np.repeat(P[i][None], len(cs), 0),
                               V[F[cs, 0]], V[F[cs, 1]], V[F[cs, 2]])
            j = int(np.argmin(d))
            if d[j] < best[i]:
                best[i] = d[j]; bidx[i] = cs[j]
        need = kd[:, -1] < best + 0.5
        if (not need.any()) or k >= 512:
            break
        k *= 4
        kd, ki = tree_f.query(P, k=k, workers=8)
        if kd.ndim == 1:
            kd = kd[:, None]; ki = ki[:, None]
    return best, bidx

# ---------------- stats ----------------

def ovl_and_thr(a, b, bins=40):
    a = a[np.isfinite(a)]; b = b[np.isfinite(b)]
    if len(a) < 10 or len(b) < 10:
        return np.nan, np.nan, np.nan, np.nan, np.nan, np.nan
    lo = min(a.min(), b.min()); hi = max(a.max(), b.max())
    if hi <= lo:
        return 0.0, np.nan, np.nan, np.nan, np.nan, np.nan
    ha, _ = np.histogram(a, bins=bins, range=(lo, hi))
    hb, _ = np.histogram(b, bins=bins, range=(lo, hi))
    ha = ha / ha.sum(); hb = hb / hb.sum()
    ovl = float(np.minimum(ha, hb).sum())
    ma, mb = float(np.median(a)), float(np.median(b))
    qa = float(np.percentile(a, 75) - np.percentile(a, 25))
    qb = float(np.percentile(b, 75) - np.percentile(b, 25))
    margin = abs(ma - mb) / max(0.5 * (qa + qb), 1e-12)
    grid = np.unique(np.quantile(np.concatenate([a, b]), np.linspace(0.02, 0.98, 120)))
    err = np.array([ (a > t).mean() * len(a) + (b <= t).mean() * len(b) for t in grid ])
    j = int(np.argmin(err))
    thr = float(grid[j]); e = float(err[j] / (len(a) + len(b)))
    return ovl, thr, e, margin, (ma, qa), (mb, qb)

# ---------------- per piece ----------------

def process_piece(name, mesh_path, out_dir, claims_dir, is_pota):
    log(f'=== {name} ===')
    t0 = time.time()
    V, F, fn, area, cen, vn, watertight = load_mesh(mesh_path)
    adj, edges = face_adjacency(F)
    n1, n2 = adj[:, 0], adj[:, 1]
    cosd = np.clip((fn[n1] * fn[n2]).sum(1), -1, 1)
    dihedral = np.degrees(np.arccos(cosd))
    tree_v = cKDTree(V)
    tree_f = cKDTree(cen)

    res = {'name': name, 'V': len(V), 'F': len(F), 'watertight': watertight,
           'mesh_md5': fmd5(mesh_path), 'area_total_mm2': float(area.sum())}

    # labels over param grid
    label_variants = {}
    for td in TDS:
        for mf in MINFRACS:
            smooth, root, comp_area, comps = labels_for(td, mf, adj, dihedral, area)
            along, hd = vertex_slab_pairs(V, vn, cen, fn, area, smooth, tree_v)
            smooth_idx = np.where(smooth)[0]
            hits = along[smooth_idx]
            hits = hits[np.isfinite(hits)]
            t_piece = float(np.median(hits)) if len(hits) > max(20, 0.05 * len(smooth_idx)) else 2.0
            paired = np.isfinite(along) & (along >= 0.5 * t_piece) & (along <= 2.5 * t_piece)
            lab = np.full(len(F), 0, dtype=np.int8)   # 0 wall
            lab[smooth & ~paired] = 1                # roll
            lab[~smooth & ~paired] = 2               # fracture
            lab[~smooth & paired] = 3                # anomaly
            label_variants[(td, mf)] = {'labels': lab, 't_piece': t_piece,
                'comp_count': len(comp_area), 'top5_comps_pct': [100 * a / area.sum() for _, a in comps[:5]]}
    # keep first-pass pairing (primary) for signals that need t
    prim = label_variants[PRIMARY]
    t_piece = prim['t_piece']
    lab = prim['labels']
    res['t_piece_mm'] = t_piece
    for td in TDS:
        for mf in MINFRACS:
            v = label_variants[(td, mf)]
            sh = [float((v['labels'] == k).sum() / len(F)) for k in range(4)]
            res[f'labels_td{td}_mf{mf}'] = {'shares': sh, 't_piece': v['t_piece'],
                                            'top5_comps_pct': [round(x, 2) for x in v['top5_comps_pct']]}
    log(f'  labels done t={t_piece:.3f} shares(W/R/F/A)={[round(x,3) for x in res[f"labels_td10.0_mf0.03"]["shares"]]} ({time.time()-t0:.0f}s)')

    # signal b: ray cast (uses primary t)
    hit_dist, hit_dot = ray_cast(V, F, fn, cen, tree_f, t_piece)
    res['b_paired_frac'] = {}
    for labname, k in (('wall', 0), ('roll', 1), ('fracture', 2)):
        m = lab == k
        pb = np.isfinite(hit_dist) & (hit_dist <= 1.5 * t_piece) & (hit_dot <= EXIT_DOT)
        res['b_paired_frac'][labname] = float(pb[m].mean()) if m.any() else np.nan
    log(f'  signal b done ({time.time()-t0:.0f}s)')

    # signal a: plane dev at all face centroids
    devs = {}
    for r in BALL_RADII:
        devs[r] = plane_dev(cen, tree_v, V, r)
    log(f'  signal a done ({time.time()-t0:.0f}s)')

    # cores (primary)
    core = erode(lab, adj, rings=2)
    res['core_face_frac'] = float(core.sum() / len(F))

    # signal c: geodesic turn
    g = edge_graph(V, F)
    pure = np.ones(len(V), dtype=bool)
    vlab = np.full(len(V), -1, dtype=np.int8)
    inc = {}
    for fi in range(len(F)):
        for k in range(3):
            inc.setdefault(int(F[fi, k]), []).append(fi)
    for vi, fl in inc.items():
        labs = {int(lab[f]) for f in fl}
        if len(labs) == 1:
            vlab[vi] = next(iter(labs))
    cap = SRC_CAP_POTA if is_pota else SRC_CAP_LABEL
    sources = {}
    for k, nm in ((0, 'wall'), (1, 'roll'), (2, 'fracture'), (3, 'anomaly')):
        idx = np.where(vlab == k)[0]
        if len(idx) > cap:
            idx = np.random.default_rng(59).choice(idx, cap, replace=False)
        sources[nm] = idx
    Rf = fold_radius(g, V, vn, np.concatenate([sources['roll'], sources['fracture']]) if len(sources['roll']) + len(sources['fracture']) else np.array([], dtype=int))
    Lf = (math.pi / 4.0) * Rf if np.isfinite(Rf) else np.nan
    wins = [w for w in WINDOWS]
    if np.isfinite(Lf) and not any(abs(Lf - w) < 0.15 * w for w in wins):
        wins.append(float(Lf))
    res['Rf_mm'] = Rf; res['Lf_mm'] = Lf; res['windows'] = wins
    res['c'] = {}
    for nm, idx in sources.items():
        if len(idx) == 0:
            continue
        for L in wins:
            allsrc = idx if not np.isfinite(Lf) or L not in (Lf,) else np.concatenate([idx, idx])
            tmed, tp90, nrng = window_turn(g, V, vn, idx, L, max(wins))
            res['c'].setdefault(nm, {})[f'{L:.2f}'] = {
                'tmed': [None if not np.isfinite(x) else round(float(x), 3) for x in tmed],
                'tp90': [None if not np.isfinite(x) else round(float(x), 3) for x in tp90],
                'n': len(idx)}
    log(f'  signal c done Rf={Rf} ({time.time()-t0:.0f}s)')

    # signal d: claims vs labels
    res['d'] = {}
    if not is_pota and claims_dir:
        for suf, sname in (('S0', 'S0'), ('S1', 'S1')):
            p = os.path.join(claims_dir, f'{name}.{suf}')
            if not os.path.exists(p):
                res['d'][sname] = 'missing'
                continue
            P = read_ply_vertices(p)
            dist, fidx = nearest_faces(P, V, F, tree_f, cen)
            clab = lab[fidx]
            shares = {nm: float((clab == k).mean()) for k, nm in ((0, 'wall'), (1, 'roll'), (2, 'fracture'), (3, 'anomaly'))}
            covered = np.zeros(len(F), dtype=bool)
            uq, cnt = np.unique(fidx, return_counts=True)
            covered[uq] = True
            band = (lab == 1) | (lab == 2) | (lab == 3)
            band_boundary = boundary_midpoints(covered_ok=None, F=F, adj=adj, maskA=band, maskB=~band)
            claim_bnd = boundary_midpoints(covered_ok=None, F=F, adj=adj, maskA=covered, maskB=~covered)
            d_c2b, d_b2c = [np.nan], [np.nan]
            if len(claim_bnd) and len(band_boundary):
                t2 = cKDTree(band_boundary)
                d_c2b, _ = t2.query(claim_bnd, workers=8)
                t3 = cKDTree(claim_bnd)
                d_b2c, _ = t3.query(band_boundary, workers=8)
            frac_bnd = boundary_midpoints(covered_ok=None, F=F, adj=adj, maskA=(lab == 2), maskB=~(lab == 2))
            d_c2f = [np.nan]
            if len(claim_bnd) and len(frac_bnd):
                d_c2f, _ = cKDTree(frac_bnd).query(claim_bnd, workers=8)
            res['d'][sname] = {
                'n_points': int(len(P)),
                'label_shares': {k2: round(v2, 4) for k2, v2 in shares.items()},
                'claim_boundary_n': int(len(claim_bnd)),
                'band_boundary_n': int(len(band_boundary)),
                'claim_to_band_mm': quant(d_c2b),
                'band_to_claim_mm': quant(d_b2c),
                'claim_to_fracture_mm': quant(d_c2f)}
            log(f'  signal d {sname} done ({time.time()-t0:.0f}s)')

    # save npz for renders + regroup
    np.savez_compressed(os.path.join(out_dir, 'labels', f'{name}.npz'),
        F=F, V=V, labels=lab, core=core, hit_dist=hit_dist, hit_dot=hit_dot,
        devs=np.stack([devs[r] for r in BALL_RADII]),
        ball_radii=np.asarray(BALL_RADII),
        labels_td8=next(v['labels'] for k2, v in label_variants.items() if k2 == (8.0, 0.02)),
        labels_td15=next(v['labels'] for k2, v in label_variants.items() if k2 == (15.0, 0.05)),
        vlab=vlab)
    res['elapsed_s'] = round(time.time() - t0, 1)
    return res

def quant(x):
    x = np.asarray(x); x = x[np.isfinite(x)]
    if len(x) == 0:
        return None
    return {'n': int(len(x)), 'med': round(float(np.median(x)), 3),
            'p90': round(float(np.percentile(x, 90)), 3)}

def boundary_midpoints(covered_ok, F, adj, maskA, maskB):
    if maskA is None or maskB is None:
        return np.zeros((0, 3))
    sel = maskA[adj[:, 0]] & maskB[adj[:, 1]] | maskB[adj[:, 0]] & maskA[adj[:, 1]]
    e = adj[sel]
    if len(e) == 0:
        return np.zeros((0, 3))
    mid = cen_of(F, e)
    return mid

def cen_of(F, e):
    v0 = (F[e[:, 0]] == F[e[:, 1]]).all()  # nonsense guard
    tri_a = F[e[:, 0]]; tri_b = F[e[:, 1]]
    shared = []
    for ra, rb in zip(tri_a, tri_b):
        s = set(ra.tolist()) & set(rb.tolist())
        shared.append(sorted(s))
    mids = []
    Vc = None
    return mids  # placeholder replaced below
