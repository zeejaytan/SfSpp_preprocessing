#!/usr/bin/env python3
"""Ticket 59 Stage 0: mesh-structural labels + four signals (read-only vs Dataset/t55).

Labels per mesh, from mesh structure ONLY (no t55 claims in the labelling):
  union-find over face-adjacency edges with dihedral < T_d  -> components
  smooth comps = component area >= min_frac * total; rough = rest
  t_piece = median vertex-slab pairing distance on smooth faces
    (slab: perp<0.75mm, along in (0.25,4.0) behind -n, opposing vertex-normal dot<=-0.5)
  wall     = smooth  AND slab-hit in [0.5t, 2.5t]
  roll     = smooth  AND no such hit
  fracture = rough   AND no such hit
  anomaly  = rough   AND such a hit (reported separately)
Primary params T_d=10deg, min_frac=0.03; sensitivity at (8,0.02) and (15,0.05).

Signals measured ONCE per face/vertex, regrouped per label:
  (a) plane-fit RMS deviation of ball neighbourhood at face centroid, r=1.0/1.5/2.0/3.0 mm
  (b) exact ray-triangle cast along -n up to 1.5t+0.5mm: hit_dist, hit-face-normal dot
  (c) geodesic-window normal turn T(v,L)=median & p90 over ring [0.8L,L], L in {2,5,10,Lf};
      Rf = median d/angle over band pairs at geodesic 1.5..2.5 mm; Lf = pi/4 * Rf
  (d) t55 claim clouds (S0/S1, header-aware PLY) -> exact point-triangle distance ->
      label shares + claim-boundary vs band-boundary midpoint distances

Writes: out/labels/<piece>.npz, out/stage0_summary.json, out/decision_table.tsv,
out/pota_control.tsv
"""
import argparse, hashlib, json, math, os, time, traceback
import numpy as np
import trimesh
from scipy.spatial import cKDTree
from scipy.sparse import coo_matrix, csr_matrix, identity
from scipy.sparse.csgraph import dijkstra

BALL_RADII = [1.0, 1.5, 2.0, 3.0]
TDS = [8.0, 10.0, 15.0]
MINFRACS = [0.02, 0.03, 0.05]
PRIMARY = (10.0, 0.03)
SENS = [(8.0, 0.02), (15.0, 0.05)]
SLAB_PERP = 0.75
SLAB_ALONG_MIN, SLAB_ALONG_MAX = 0.25, 4.0
EXIT_DOT = -0.5
RAY_EPS = 0.01
WINDOWS = [2.0, 5.0, 10.0]
SRC_CAP = 800
SRC_CAP_POTA = 150
DJ_BATCH = 64

def log(m):
    print(f"[{time.strftime('%H:%M:%S')}] {m}", flush=True)

def fmd5(path):
    h = hashlib.md5()
    with open(path, 'rb') as f:
        for chunk in iter(lambda: f.read(1 << 20), b''):
            h.update(chunk)
    return h.hexdigest()

# ---------- mesh ----------

def load_mesh(path):
    m = trimesh.load(path, process=False, force='mesh')
    if not m.is_watertight:
        m.fix_normals(multibody=True)
    V = np.asarray(m.vertices, dtype=np.float64)
    F = np.asarray(m.faces, dtype=np.int64)
    tri = V[F]
    cr = np.cross(tri[:, 1] - tri[:, 0], tri[:, 2] - tri[:, 0])
    ln = np.linalg.norm(cr, axis=1)
    area = 0.5 * ln
    fn = np.zeros_like(cr)
    ok = ln > 0
    fn[ok] = cr[ok] / ln[ok, None]
    cen = tri.mean(axis=1)
    vn = np.zeros_like(V)
    for k in range(3):
        np.add.at(vn, F[:, k], fn * area[:, None])
    nrm = np.linalg.norm(vn, axis=1)
    nz = nrm > 0
    vn[nz] = vn[nz] / nrm[nz, None]
    return V, F, fn, area, cen, vn, bool(m.is_watertight)

def face_adjacency(F):
    ed = {}
    for fi in range(len(F)):
        f0, f1, f2 = int(F[fi, 0]), int(F[fi, 1]), int(F[fi, 2])
        for u, v in ((f0, f1), (f1, f2), (f2, f0)):
            k2 = (u, v) if u < v else (v, u)
            lst = ed.get(k2)
            if lst is None:
                ed[k2] = [fi]
            else:
                lst.append(fi)
    pairs = [v for v in ed.values() if len(v) == 2]
    adj = np.array([[p[0], p[1]] for p in pairs], dtype=np.int64).reshape(-1, 2)
    shared = []
    for p in pairs:
        s = {int(F[p[0], 0]), int(F[p[0], 1]), int(F[p[0], 2])} & {int(F[p[1], 0]), int(F[p[1], 1]), int(F[p[1], 2])}
        shared.append(sorted(s))
    return adj, shared

def dihedrals(fn, adj):
    c = np.clip((fn[adj[:, 0]] * fn[adj[:, 1]]).sum(1), -1.0, 1.0)
    return np.degrees(np.arccos(c))

class DSU:
    __slots__ = ('p',)
    def __init__(self, n):
        self.p = list(range(n))
    def find(self, x):
        p = self.p
        r = x
        while p[r] != r:
            r = p[r]
        while p[x] != r:
            p[x], x = r, p[x]
        return r
    def union(self, a, b):
        ra, rb = self.find(a), self.find(b)
        if ra != rb:
            self.p[rb] = ra

def smooth_mask(td, mf, adj, dih, area):
    dsu = DSU(len(area))
    for a, b in adj[dih < td]:
        dsu.union(int(a), int(b))
    comp_area = {}
    roots = [dsu.find(i) for i in range(len(area))]
    for r, a in zip(roots, area):
        comp_area[r] = comp_area.get(r, 0.0) + float(a)
    total = float(area.sum())
    big = {r for r, a in comp_area.items() if a >= mf * total}
    smooth = np.fromiter((r in big for r in roots), dtype=bool, count=len(area))
    comps_sorted = sorted(comp_area.values(), reverse=True)
    return smooth, [100.0 * a / total for a in comps_sorted[:5]]

# ---------- pairing ----------

def slab_hits(V, vn, cen, fn, tree_v):
    n = len(cen)
    along_min = np.full(n, np.nan)
    idx_lists = tree_v.query_ball_point(cen, SLAB_ALONG_MAX + SLAB_PERP + 0.2, workers=8)
    for i in range(n):
        cand = idx_lists[i]
        if cand is None or len(cand) == 0:
            continue
        d = V[cand] - cen[i]
        nv = fn[i]
        along = -(d @ nv)
        m = (along > SLAB_ALONG_MIN) & (along < SLAB_ALONG_MAX)
        if not m.any():
            continue
        dm = d[m]
        perp2 = (dm * dm).sum(1) - along[m] * along[m]
        m2 = perp2 < SLAB_PERP * SLAB_PERP
        if not m2.any():
            continue
        sub = np.asarray(cand)[m][m2]
        dots = vn[sub] @ nv
        okd = dots <= EXIT_DOT
        if okd.any():
            along_min[i] = float(along[m][m2][okd].min())
    return along_min

def ray_cast(V, F, fn, cen, tree_f, t_piece):
    n = len(cen)
    L = 1.5 * t_piece + 0.5
    hit_dist = np.full(n, np.inf)
    hit_dot = np.full(n, np.nan)
    tri = V[F]
    CH = 384
    for s in range(0, n, CH):
        e = min(n, s + CH)
        rg = np.arange(s, e)
        o = cen[rg] + RAY_EPS * fn[rg]
        d = -fn[rg]
        cand = tree_f.query_ball_point(cen[rg], L + 2.0, workers=8)
        lens = [len(c) for c in cand]
        if sum(lens) == 0:
            continue
        fl_r = np.concatenate([np.full(ln, ri, dtype=np.int64) for ri, ln in enumerate(lens)])
        fl_t = np.concatenate([np.asarray(c, dtype=np.int64) for c in cand if len(c)])
        keep = fl_t != rg[fl_r]
        fl_r, fl_t = fl_r[keep], fl_t[keep]
        if len(fl_t) == 0:
            continue
        A, B, C = tri[fl_t, 0], tri[fl_t, 1], tri[fl_t, 2]
        oo, dd = o[fl_r], d[fl_r]
        e1, e2 = B - A, C - A
        h = np.cross(dd, e2)
        a = (e1 * h).sum(1)
        f = np.zeros_like(a)
        nz = np.abs(a) > 1e-14
        f[nz] = 1.0 / a[nz]
        ap = oo - A
        u = f * (ap * h).sum(1)
        q = np.cross(ap, e1)
        v = f * (dd * q).sum(1)
        tt = f * (e2 * q).sum(1)
        val = nz & (u >= 0) & (v >= 0) & (u + v <= 1) & (tt > RAY_EPS) & (tt <= L)
        if not val.any():
            continue
        gi = rg[fl_r[val]]
        dv = tt[val]
        fidx = fl_t[val]
        order = np.argsort(dv, kind='stable')
        gi, dv, fidx = gi[order], dv[order], fidx[order]
        ug, first = np.unique(gi, return_index=True)
        cur = hit_dist[ug]
        better = dv[first] < cur
        gsel = ug[better]
        hit_dist[gsel] = dv[first][better]
        hit_dot[gsel] = (fn[fidx[first][better]] * fn[gsel]).sum(1)
    hit_dist[~np.isfinite(hit_dist)] = np.nan
    return hit_dist, hit_dot

# ---------- roughness ----------

def plane_dev(cen, tree_v, V, radius):
    n = len(cen)
    dev = np.full(n, np.nan)
    CH = 2048
    for s in range(0, n, CH):
        e = min(n, s + CH)
        cand = tree_v.query_ball_point(cen[s:e], radius, workers=8)
        for i, cl in enumerate(cand):
            if cl is None or len(cl) < 8:
                continue
            P = V[cl]
            P = P - P.mean(0)
            cov = (P.T @ P) / len(P)
            _, vecs = np.linalg.eigh(cov)
            dd = P @ vecs[:, 0]
            dev[s + i] = math.sqrt(float((dd * dd).mean()))
    return dev

# ---------- geodesic ----------

def edge_graph(V, F):
    a = np.concatenate([F[:, 0], F[:, 1], F[:, 2]])
    b = np.concatenate([F[:, 1], F[:, 2], F[:, 0]])
    lo = np.minimum(a, b)
    hi = np.maximum(a, b)
    nv = len(V)
    key = lo.astype(np.int64) * nv + hi
    uk = np.unique(key)
    src = (uk // nv).astype(np.int64)
    dst = (uk % nv).astype(np.int64)
    w = np.linalg.norm(V[src] - V[dst], axis=1)
    return coo_matrix((w, (src, dst)), shape=(nv, nv)).tocsr()

def rings_from_dist(dist, vn, src_i, L):
    tmed = np.full(len(src_i), np.nan)
    tp90 = np.full(len(src_i), np.nan)
    nrng = np.zeros(len(src_i), dtype=int)
    for r in range(len(src_i)):
        drow = dist[r]
        m = (drow >= 0.8 * L) & (drow <= L) & np.isfinite(drow)
        k = int(m.sum())
        nrng[r] = k
        if k < 20:
            continue
        dots = np.clip(vn[m] @ vn[src_i[r]], -1, 1)
        ang = np.degrees(np.arccos(dots))
        tmed[r] = float(np.median(ang))
        tp90[r] = float(np.percentile(ang, 90))
    return tmed, tp90, nrng

def fold_radius(dist, vn, src_i):
    rats = []
    for r in range(len(src_i)):
        drow = dist[r]
        m = (drow >= 1.5) & (drow <= 2.5) & np.isfinite(drow)
        if int(m.sum()) < 10:
            continue
        dots = np.clip(vn[m] @ vn[src_i[r]], -1, 1)
        ang = np.arccos(dots)
        good = ang > 1e-5
        if not good.any():
            continue
        rat = drow[m][good] / ang[good]
        rats.append(float(np.median(rat)))
    return float(np.median(rats)) if rats else np.nan

# ---------- erosion ----------

def build_badj(adj, nF):
    rows = np.concatenate([adj[:, 0], adj[:, 1]])
    cols = np.concatenate([adj[:, 1], adj[:, 0]])
    return csr_matrix((np.ones(len(rows), dtype=np.int32), (rows, cols)), shape=(nF, nF))

def erode_labels(lab, Bself, deg, rings=2):
    core = np.ones(len(lab), dtype=bool)
    for _ in range(rings):
        new = np.zeros(len(lab), dtype=bool)
        for k in range(4):
            mk = lab == k
            if not mk.any():
                continue
            cnt = np.asarray(Bself @ mk.astype(np.int32)).ravel()
            new |= (cnt == deg) & mk
        core = new
        if not core.any():
            break
    return core

# ---------- PLY ----------

def read_ply_vertices(path):
    with open(path, 'r', errors='replace') as f:
        lines = f.readlines()
    nvert, props, in_vert, i = None, 0, False, 0
    for i, ln in enumerate(lines):
        s = ln.strip()
        if s == 'end_header':
            i += 1
            break
        if s.startswith('element'):
            p = s.split()
            in_vert = p[1] == 'vertex'
            if in_vert:
                nvert = int(p[2])
                props = 0
        elif s.startswith('property') and in_vert:
            props += 1
    if nvert is None or props < 3:
        raise ValueError(f'bad ply header: {path}')
    rows = [lines[i + j].split() for j in range(nvert)]
    arr = np.asarray(rows, dtype=np.float64)
    return arr[:, :3]

# ---------- point-triangle (Ericson closest point) ----------

def point_tri_dist(P, A, B, C):
    AB, AC, AP = B - A, C - A, P - A
    d1 = (AB * AP).sum(1)
    d2 = (AC * AP).sum(1)
    BP = P - B
    d3 = (AB * BP).sum(1)
    d4 = (AC * BP).sum(1)
    CP = P - C
    d5 = (AB * CP).sum(1)
    d6 = (AC * CP).sum(1)
    va = d3 * d6 - d5 * d4
    vb = d5 * d2 - d1 * d6
    vc = d1 * d4 - d3 * d2
    Q = np.zeros_like(P)
    done = np.zeros(len(P), dtype=bool)
    m = (d1 <= 0) & (d2 <= 0)
    Q[m] = A[m]
    done |= m
    m = (~done) & (d3 >= 0) & (d4 <= d3)
    Q[m] = B[m]
    done |= m
    m = (~done) & (d6 >= 0) & (d5 <= d6)
    Q[m] = C[m]
    done |= m
    m = (~done) & (vc <= 0) & (d1 >= 0) & (d3 <= 0)
    if m.any():
        t = np.clip(d1[m] / (d1[m] - d3[m]), 0, 1)[:, None]
        Q[m] = A[m] + t * AB[m]
    done |= m
    m = (~done) & (va <= 0) & ((d4 - d3) >= 0) & ((d6 - d5) >= 0)
    if m.any():
        den = (d4[m] - d3[m]) + (d6[m] - d5[m])
        t = np.where(den > 0, (d4[m] - d3[m]) / np.maximum(den, 1e-30), 0.0)[:, None]
        Q[m] = B[m] + t * (C[m] - B[m])
    done |= m
    m = (~done) & (vb <= 0) & (d6 >= 0) & (d2 <= 0)
    if m.any():
        t = np.clip(d6[m] / (d6[m] - d2[m]), 0, 1)[:, None]
        Q[m] = C[m] + t * (A[m] - C[m])
    done |= m
    m = ~done
    if m.any():
        den = va[m] + vb[m] + vc[m]
        okd = np.abs(den) > 1e-30
        v = np.zeros(len(den))
        w = np.zeros(len(den))
        v[okd] = vb[m][okd] / den[okd]
        w[okd] = vc[m][okd] / den[okd]
        Q[m] = A[m] + v[:, None] * AB[m] + w[:, None] * AC[m]
    return np.linalg.norm(P - Q, axis=1)

def assign_faces(P, V, F, tree_f):
    nP = len(P)
    best = np.full(nP, np.inf)
    bidx = np.full(nP, -1, dtype=np.int64)

    def run_pass(Pp, base_idx, k, best, bidx):
        kd, ki = tree_f.query(Pp, k=k, workers=8)
        if kd.ndim == 1:
            kd = kd[:, None]
            ki = ki[:, None]
        rep = np.repeat(np.arange(len(Pp)), k)
        cs = ki.ravel()
        gd = cs >= 0
        rep, cs = rep[gd], cs[gd]
        d = point_tri_dist(Pp[rep], V[F[cs, 0]], V[F[cs, 1]], V[F[cs, 2]])
        o = np.lexsort((cs, d, rep))
        rep, d, cs = rep[o], d[o], cs[o]
        ug, first = np.unique(rep, return_index=True)
        gi = base_idx[ug]
        better = d[first] < best[gi]
        best[gi[better]] = d[first][better]
        bidx[gi[better]] = cs[first][better]

    run_pass(P, np.arange(nP), 32, best, bidx)
    need = tree_f.query(P, k=32, workers=8)[0][:, -1] < (best + 0.5)
    if need.any() and nP:
        P2 = P[need]
        b2 = best.copy()[need]
        bi2 = bidx.copy()[need]
        run_pass(P2, np.where(need)[0], 128, best, bidx)
    return best, bidx

# ---------- stats ----------

def med(x):
    return float(np.median(x))

def iqr(x):
    return float(np.percentile(x, 75) - np.percentile(x, 25))

def ovl_thr(a, b, bins=40):
    a = a[np.isfinite(a)]
    b = b[np.isfinite(b)]
    if len(a) < 25 or len(b) < 25:
        return None
    lo = min(a.min(), b.min())
    hi = max(a.max(), b.max())
    if not hi > lo:
        return None
    ha, _ = np.histogram(a, bins=bins, range=(lo, hi))
    hb, _ = np.histogram(b, bins=bins, range=(lo, hi))
    ha = ha / len(a)
    hb = hb / len(b)
    ovl = float(np.minimum(ha, hb).sum())
    grid = np.unique(np.quantile(np.concatenate([a, b]), np.linspace(0.02, 0.98, 120)))
    errs = np.array([(a > t).mean() * len(a) + (b <= t).mean() * len(b) for t in grid])
    j = int(np.argmin(errs))
    margin = abs(med(a) - med(b)) / max(0.5 * (iqr(a) + iqr(b)), 1e-12)
    return {'ovl': round(ovl, 4), 'thr': round(float(grid[j]), 4),
            'err': round(float(errs[j] / (len(a) + len(b))), 4),
            'margin': round(float(margin), 3),
            'med_a': round(med(a), 4), 'iqr_a': round(iqr(a), 4),
            'med_b': round(med(b), 4), 'iqr_b': round(iqr(b), 4),
            'n_a': int(len(a)), 'n_b': int(len(b))}

def quant(x):
    x = np.asarray(x, dtype=float)
    x = x[np.isfinite(x)]
    if len(x) == 0:
        return None
    return {'n': int(len(x)), 'med': round(float(np.median(x)), 3),
            'p90': round(float(np.percentile(x, 90)), 3)}

def boundary_mids(V, adj, shared, maskA, maskB):
    sel = np.where((maskA[adj[:, 0]] & maskB[adj[:, 1]]) | (maskB[adj[:, 0]] & maskA[adj[:, 1]]))[0]
    mids = np.zeros((len(sel), 3))
    for j, si in enumerate(sel):
        s = shared[si]
        mids[j] = (V[s[0]] + V[s[1]]) / 2.0
    return mids

# ---------- per piece ----------

def process_piece(name, mesh_path, out_dir, claims_dir, is_pota, pooled, pota_acc):
    t0 = time.time()
    log(f'=== {name} ===')
    V, F, fn, area, cen, vn, wt = load_mesh(mesh_path)
    adj, shared = face_adjacency(F)
    dih = dihedrals(fn, adj)
    tree_v = cKDTree(V)
    tree_f = cKDTree(cen)
    res = {'name': name, 'V': len(V), 'F': len(F), 'watertight': wt,
           'mesh_md5': fmd5(mesh_path), 'area_mm2': round(float(area.sum()), 1)}

    along = slab_hits(V, vn, cen, fn, tree_v)
    log(f'  slab hits done ({time.time()-t0:.0f}s)')

    labvars = {}
    for td in TDS:
        for mf in MINFRACS:
            smooth, top5 = smooth_mask(td, mf, adj, dih, area)
            sm = along[smooth]
            smf = sm[np.isfinite(sm)]
            t_piece = float(np.median(smf)) if len(smf) > max(20, int(0.05 * int(smooth.sum()))) else 2.0
            paired = np.isfinite(along) & (along >= 0.5 * t_piece) & (along <= 2.5 * t_piece)
            lab = np.zeros(len(F), dtype=np.int8)
            lab[smooth & ~paired] = 1
            lab[~smooth & ~paired] = 2
            lab[~smooth & paired] = 3
            labvars[(td, mf)] = (lab, t_piece, top5)
    lab, t_piece, _ = labvars[PRIMARY]
    res['t_piece_mm'] = round(t_piece, 3)
    for td in TDS:
        for mf in MINFRACS:
            lb, tp, top5 = labvars[(td, mf)]
            res[f'labels_td{int(td)}_mf{mf}'] = {
                'shares_W_R_F_A': [round(float((lb == k).mean()), 4) for k in range(4)],
                't_piece': round(tp, 3),
                'top5_comps_pct': [round(x, 2) for x in top5]}
    log(f'  labels done t={t_piece:.3f} ({time.time()-t0:.0f}s)')

    hit_dist, hit_dot = ray_cast(V, F, fn, cen, tree_f, t_piece)
    Bself = (build_badj(adj, len(F)) + identity(len(F), dtype=np.int32, format='csr')).tocsr()
    deg = np.asarray(Bself.sum(1)).ravel()
    core = erode_labels(lab, Bself, deg, rings=2)
    res['core_frac'] = round(float(core.mean()), 3)
    pb_mask = np.isfinite(hit_dist) & (hit_dist <= 1.5 * t_piece) & (hit_dot <= EXIT_DOT)
    for k, nm in ((0, 'wall'), (1, 'roll'), (2, 'fracture'), (3, 'anomaly')):
        m = lab == k
        if m.any():
            res.setdefault('b_paired_rate', {})[nm] = round(float(pb_mask[m].mean()), 4)
    log(f'  signal b done ({time.time()-t0:.0f}s)')

    devs = {r: plane_dev(cen, tree_v, V, r) for r in BALL_RADII}
    log(f'  signal a done ({time.time()-t0:.0f}s)')

    if not is_pota:
        for k, nm in ((0, 'wall'), (1, 'roll'), (2, 'fracture')):
            m = core & (lab == k)
            pooled[f'b_paired_{nm}'].append(pb_mask[m])
            pooled[f'b_dist_{nm}'].append(hit_dist[m & np.isfinite(hit_dist)])
            for r in BALL_RADII:
                pooled[f'a_r{r}_{nm}'].append(devs[r][m])
    else:
        m = core & (lab == 0)
        pota_acc['a15'].append(devs[1.5][m])
        pota_acc['a20'].append(devs[2.0][m])
        pota_acc['bpaired'].append(pb_mask[m])
        pota_acc['bdist'].append(hit_dist[m & np.isfinite(hit_dist)])

    g = edge_graph(V, F)
    vmin = np.full(len(V), 9, dtype=np.int8)
    vmax = np.full(len(V), -1, dtype=np.int8)
    for k in range(4):
        fk = lab == k
        if not fk.any():
            continue
        for kk in range(3):
            np.minimum.at(vmin, F[fk, kk], k)
            np.maximum.at(vmax, F[fk, kk], k)
    vlab = np.where(vmin == vmax, vmin, -1)
    cap = SRC_CAP_POTA if is_pota else SRC_CAP
    src = {}
    for k, nm in ((0, 'wall'), (1, 'roll'), (2, 'fracture')):
        idx = np.where(vlab == k)[0]
        if len(idx) > cap:
            idx = np.sort(np.random.default_rng(59 + k).choice(idx, cap, replace=False))
        src[nm] = idx
    band_src = np.concatenate([src['roll'], src['fracture']]) if (len(src['roll']) + len(src['fracture'])) else np.array([], dtype=np.int64)
    Rf = np.nan
    if len(band_src):
        db = dijkstra(g, directed=False, indices=band_src, limit=2.6)
        Rf = fold_radius(db, vn, band_src)
    Lf = (math.pi / 4.0) * Rf if np.isfinite(Rf) else np.nan
    wins = list(WINDOWS)
    if np.isfinite(Lf) and not any(abs(Lf - w) < 0.15 * w for w in wins):
        wins.append(float(Lf))
    res['Rf_mm'] = None if not np.isfinite(Rf) else round(Rf, 2)
    res['Lf_mm'] = None if not np.isfinite(Lf) else round(Lf, 2)
    res['c_windows'] = [round(w, 2) for w in wins]
    res['c'] = {}
    maxwin = max(wins)
    for nm, idx in src.items():
        if len(idx) == 0:
            continue
        res['c'][nm] = {}
        store = {L: ([], []) for L in wins}
        for s0 in range(0, len(idx), DJ_BATCH):
            bsrc = idx[s0:s0 + DJ_BATCH]
            dist = dijkstra(g, directed=False, indices=bsrc, limit=maxwin + 0.2)
            for L in wins:
                tm, tp, _ = rings_from_dist(dist, vn, bsrc, L)
                store[L][0].append(tm)
                store[L][1].append(tp)
        for L in wins:
            tmed = np.concatenate(store[L][0])
            tp90 = np.concatenate(store[L][1])
            res['c'][nm][f'{L:.2f}'] = {
                'tmed_med': None if not np.isfinite(tmed).any() else round(float(np.nanmedian(tmed)), 2),
                'tp90_med': None if not np.isfinite(tp90).any() else round(float(np.nanmedian(tp90)), 2),
                'n_src': int(len(idx))}
            if not is_pota and L in WINDOWS:
                pooled[f'c_tmed_{L:.1f}_{nm}'].append(tmed)
                pooled[f'c_tp90_{L:.1f}_{nm}'].append(tp90)
            if is_pota and nm == 'wall' and L == 5.0:
                pota_acc['c5'].append(tmed)
    log(f'  signal c done Rf={res["Rf_mm"]} ({time.time()-t0:.0f}s)')

    res['d'] = {}
    if not is_pota and claims_dir:
        for suf in ('S0', 'S1'):
            p = os.path.join(claims_dir, f'{name}.{suf}')
            if not os.path.exists(p):
                res['d'][suf] = 'missing'
                continue
            P = read_ply_vertices(p)
            best, bidx2 = assign_faces(P, V, F, tree_f)
            clab = lab[bidx2]
            shares = {nm2: round(float((clab == k2).mean()), 4)
                      for k2, nm2 in ((0, 'wall'), (1, 'roll'), (2, 'fracture'), (3, 'anomaly'))}
            covered = np.zeros(len(F), dtype=bool)
            uqc = np.unique(bidx2)
            covered[uqc[uqc >= 0]] = True
            band = (lab == 1) | (lab == 2) | (lab == 3)
            cb = boundary_mids(V, adj, shared, covered, ~covered)
            bb = boundary_mids(V, adj, shared, band, ~band)
            fb = boundary_mids(V, adj, shared, lab == 2, lab != 2)
            out = {'n_points': int(len(P)), 'label_shares': shares,
                   'claim_bnd_n': int(len(cb)), 'band_bnd_n': int(len(bb)),
                   'frac_bnd_n': int(len(fb))}
            if len(cb) and len(bb):
                out['claim_to_band_mm'] = quant(cKDTree(bb).query(cb, workers=8)[0])
                out['band_to_claim_mm'] = quant(cKDTree(cb).query(bb, workers=8)[0])
            if len(cb) and len(fb):
                out['claim_to_fracture_mm'] = quant(cKDTree(fb).query(cb, workers=8)[0])
            res['d'][suf] = out
            log(f'  signal d {suf} done ({time.time()-t0:.0f}s)')

    np.savez_compressed(os.path.join(out_dir, 'labels', f'{name}.npz'),
                        V=V, F=F, labels=lab, core=core,
                        hit_dist=hit_dist, hit_dot=hit_dot,
                        devs=np.stack([devs[r] for r in BALL_RADII]),
                        ball_radii=np.asarray(BALL_RADII),
                        lab_sens0=labvars[SENS[0]][0], lab_sens1=labvars[SENS[1]][0],
                        vlab=vlab, t_piece=t_piece)
    res['elapsed_s'] = round(time.time() - t0, 1)
    return res

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--mesh-root', default='/data/gpfs/projects/punim2657/sfs_preprocessing/Dataset/Mesh')
    ap.add_argument('--t55', default='/data/gpfs/projects/punim2657/SfSpp/runs/20261101-2004_05be12c_t55-worness07-breaklines')
    ap.add_argument('--out', required=True)
    ap.add_argument('--only', default='')
    args = ap.parse_args()
    os.makedirs(os.path.join(args.out, 'labels'), exist_ok=True)
    claims = os.path.join(args.t55, 'out', 'geom')

    jug = [(f'Juglet_Piece_{i}', os.path.join(args.mesh_root, 'Juglet', f'Juglet_Piece_{i}_Mesh.obj')) for i in range(1, 10)]
    pota = [(f'Pot_A_Piece_{i:02d}', os.path.join(args.mesh_root, 'Pot_A', f'Pot_A_Piece_{i:02d}_Mesh.obj')) for i in range(1, 9)]
    if args.only:
        want = set(args.only.split(','))
        jug = [p for p in jug if p[0] in want]
        pota = [p for p in pota if p[0] in want]

    pooled = {k: [] for k in
              [f'b_paired_{nm}' for nm in ('wall', 'roll', 'fracture')] +
              [f'b_dist_{nm}' for nm in ('wall', 'roll', 'fracture')] +
              [f'a_r{r}_{nm}' for r in BALL_RADII for nm in ('wall', 'roll', 'fracture')] +
              [f'c_tmed_{w:.1f}_{nm}' for w in WINDOWS for nm in ('wall', 'roll', 'fracture')] +
              [f'c_tp90_{w:.1f}_{nm}' for w in WINDOWS for nm in ('wall', 'roll', 'fracture')]}
    pota_acc = {'a15': [], 'a20': [], 'bpaired': [], 'bdist': [], 'c5': []}
    summary = {'params': {'tds': TDS, 'minfracs': MINFRACS, 'primary': list(PRIMARY),
                          'sens': [list(s) for s in SENS], 'ball_radii': BALL_RADII,
                          'windows': WINDOWS, 'slab': {'perp_mm': SLAB_PERP,
                          'along': [SLAB_ALONG_MIN, SLAB_ALONG_MAX], 'exit_dot': EXIT_DOT,
                          'ray_max_t': 1.5}, 'src_cap': SRC_CAP, 'src_cap_pota': SRC_CAP_POTA}}

    for name, mp in jug + pota:
        is_pota = name.startswith('Pot_A')
        try:
            summary[name] = process_piece(name, mp, args.out, claims if not is_pota else None,
                                          is_pota, pooled, pota_acc)
        except Exception:
            summary[name] = {'error': traceback.format_exc(limit=10)}
            log(f'  !! {name} FAILED')

    def cat(k):
        v = pooled.get(k) or []
        return np.concatenate(v) if v else np.zeros(0)

    rows = []
    sigs = ([f'a_r{r}' for r in BALL_RADII] + ['b_dist'] +
            [f'c_tmed_{w:.1f}' for w in WINDOWS] + [f'c_tp90_{w:.1f}' for w in WINDOWS])
    for sig in sigs:
        wallv = cat(f'{sig}_wall')
        if len(wallv) < 25:
            continue
        for grp in ('roll', 'fracture', 'roll+fracture'):
            if grp == 'roll+fracture':
                a1, a2 = cat(f'{sig}_roll'), cat(f'{sig}_fracture')
                gv = np.concatenate([a1, a2]) if (len(a1) or len(a2)) else np.zeros(0)
            else:
                gv = cat(f'{sig}_{grp}')
            st = ovl_thr(wallv, gv)
            if st:
                rows.append({'signal': sig, 'pair': f'wall_vs_{grp}', **st})
    with open(os.path.join(args.out, 'decision_table.tsv'), 'w') as f:
        f.write('signal\tpair\tovl\tthr\terr\tmargin\tmed_a\tiqr_a\tmed_b\tiqr_b\tn_a\tn_b\n')
        for r in rows:
            f.write('\t'.join(str(r.get(k2, '')) for k2 in
                    ('signal', 'pair', 'ovl', 'thr', 'err', 'margin',
                     'med_a', 'iqr_a', 'med_b', 'iqr_b', 'n_a', 'n_b')) + '\n')
    summary['decision_rows'] = rows
    summary['b_paired_rates_pooled'] = {
        nm: (round(float(np.concatenate(pooled[f'b_paired_{nm}']).mean()), 4)
             if pooled[f'b_paired_{nm}'] else None)
        for nm in ('wall', 'roll', 'fracture')}

    # Pot A control misfire rates using Juglet-derived wall-vs-band thresholds
    pota_rows = []
    def pc(k):
        v = pota_acc[k]
        return np.concatenate(v) if v else np.zeros(0)

    def thr_of(sig):
        for r in rows:
            if r['signal'] == sig and r['pair'] == 'wall_vs_roll+fracture':
                return r['thr'], r['med_a'], r['med_b']
        return None, None, None

    for sig, arr in (('a_r1.5', pc('a15')), ('a_r2.0', pc('a20'))):
        thr, mw, mb = thr_of(sig)
        if thr is None or len(arr) == 0:
            continue
        mis = float((arr > thr).mean()) if mb > mw else float((arr < thr).mean())
        pota_rows.append({'signal': sig, 'threshold': thr, 'direction': 'band_higher' if mb > mw else 'band_lower',
                          'pota_wall_n': int(len(arr)), 'pota_wall_misfire': round(mis, 4)})
    thr, mw, mb = thr_of('b_dist')
    bd = pc('bdist')
    if thr is not None and len(bd):
        mis = float((bd > thr).mean()) if mb > mw else float((bd < thr).mean())
        pota_rows.append({'signal': 'b_dist(with-hit subset)', 'threshold': thr,
                          'direction': 'band_higher' if mb > mw else 'band_lower',
                          'pota_wall_n': int(len(bd)), 'pota_wall_misfire': round(mis, 4)})
    bp = pc('bpaired')
    wall_rate = summary['b_paired_rates_pooled']['wall']
    if len(bp) and wall_rate is not None:
        pota_rows.append({'signal': 'b_paired', 'threshold': 'unpaired=band-like',
                          'pota_wall_n': int(len(bp)), 'pota_wall_misfire_unpaired': round(float(1.0 - bp.mean()), 4)})
    thr, mw, mb = thr_of('c_tmed_5.0')
    c5 = pc('c5')
    if thr is not None and len(c5):
        mis = float((c5[np.isfinite(c5)] > thr).mean()) if mb > mw else float((c5[np.isfinite(c5)] < thr).mean())
        pota_rows.append({'signal': 'c_tmed_5.0', 'threshold': thr,
                          'direction': 'band_higher' if mb > mw else 'band_lower',
                          'pota_wall_n': int(np.isfinite(c5).sum()), 'pota_wall_misfire': round(mis, 4)})
    with open(os.path.join(args.out, 'pota_control.tsv'), 'w') as f:
        f.write('signal\tthreshold\tdirection\tpota_wall_n\tmisfire\n')
        for r in pota_rows:
            f.write(f"{r['signal']}\t{r.get('threshold', '')}\t{r.get('direction', '')}\t"
                    f"{r.get('pota_wall_n', '')}\t{r.get('pota_wall_misfire', r.get('pota_wall_misfire_unpaired', ''))}\n")
    summary['pota_control'] = pota_rows

    json.dump(summary, open(os.path.join(args.out, 'stage0_summary.json'), 'w'), indent=1)
    log('summary + tables written')
    log('DONE')

if __name__ == '__main__':
    main()
