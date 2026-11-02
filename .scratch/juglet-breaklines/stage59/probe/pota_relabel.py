#!/usr/bin/env python3
"""ticket 59 -- Stage-0 addendum: Pot A label sweep + corrected per-piece medians.

Q1: do Pot A (full-res, big pot) labels come out sane (large wall comp, small
    fracture rim) at ANY (td, mf, along_max) in a plausible sweep?  Stage-0
    primary params collapsed them to 99% 'fracture'.
Q2: corrected per-piece Juglet signal medians (nanmedian, Stage-0 used the
    same but the pooled table is J1-weighted; record per piece explicitly).
Reads stage-0 run npz files read-only; writes out/ only.
"""
import argparse, json, math, os, sys, time
import numpy as np
from scipy.spatial import cKDTree
from scipy.sparse import coo_matrix

def log(m):
    print(f"[{time.strftime('%H:%M:%S')}] {m}", flush=True)

# ---------- mesh helpers (copied from stage0_probe.py, ranges parameterised) ----------
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
    return adj

def face_normals(V, F):
    tri = V[F]
    fn = np.cross(tri[:, 1] - tri[:, 0], tri[:, 2] - tri[:, 0])
    norm = np.linalg.norm(fn, axis=1)
    norm[norm == 0] = 1.0
    return fn / norm[:, None], 0.5 * norm

def vertex_normals(V, F):
    # area-weighted: accumulate (unnormalised) face cross products per vertex
    vn = np.zeros_like(V)
    tri = V[F]
    fn_area = np.cross(tri[:, 1] - tri[:, 0], tri[:, 2] - tri[:, 0])
    for col in (0, 1, 2):
        np.add.at(vn, F[:, col].astype(np.int64), fn_area)
    nrm = np.linalg.norm(vn, axis=1)
    nrm[nrm == 0] = 1.0
    return vn / nrm[:, None]

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

def slab_hits(V, vn, cen, fn, tree_v, along_max, perp=0.75, along_min=0.25, exit_dot=-0.5):
    # chunked: a 13mm ball on a full-res mesh holds ~6.5k points; materialising
    # all per-face lists at once OOM-killed job 34199355, so query+process in
    # blocks and free each block before the next.
    n = len(cen)
    along_min_arr = np.full(n, np.nan)
    CH = 4096
    for s in range(0, n, CH):
        e_ = min(n, s + CH)
        idx_lists = tree_v.query_ball_point(cen[s:e_], along_max + perp + 0.2, workers=8)
        for ii, i in enumerate(range(s, e_)):
            cand = idx_lists[ii]
            if cand is None or len(cand) == 0:
                continue
            d = V[cand] - cen[i]
            nv = fn[i]
            along = -(d @ nv)
            m = (along > along_min) & (along < along_max)
            if not m.any():
                continue
            dm = d[m]
            perp2 = (dm * dm).sum(1) - along[m] * along[m]
            m2 = perp2 < perp * perp
            if not m2.any():
                continue
            sub = np.asarray(cand)[m][m2]
            dots = vn[sub] @ nv
            okd = dots <= exit_dot
            if okd.any():
                along_min_arr[i] = float(along[m][m2][okd].min())
        del idx_lists
    return along_min_arr

def ray_cast(V, F, fn, cen, tree_f, L):
    n = len(cen)
    hit_dist = np.full(n, np.inf)
    hit_dot = np.full(n, np.nan)
    tri = V[F]
    RAY_EPS = 1e-4
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

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--stage0-dir', required=True)
    ap.add_argument('--out-dir', required=True)
    ap.add_argument('--pota-only', action='store_true')
    args = ap.parse_args()
    os.makedirs(args.out_dir, exist_ok=True)
    lab_dir = os.path.join(args.stage0_dir, 'out', 'labels')
    S0 = args.stage0_dir

    summary = {}
    tds = [10.0, 15.0, 20.0, 25.0, 30.0]
    mfs = [0.01, 0.02]
    alongs = [4.0, 8.0, 12.0]

    # ---------- Q1: Pot A sweep ----------
    rows = ['piece\ttd\tmf\talong_max\tt_est_mm\tW\tR\tF\tA\ttop1_pct\ttop3_pct']
    for i in range(1, 9):
        name = f'Pot_A_Piece_0{i}'
        z = np.load(os.path.join(lab_dir, name + '.npz'))
        V, F = z['V'], z['F']
        log(f'{name}: V={len(V)} F={len(F)}')
        fn, fa = face_normals(V, F)
        vn = vertex_normals(V, F)
        cen = V[F].mean(1)
        adj = face_adjacency(F)
        dih = dihedrals(fn, adj)
        tree_v = cKDTree(V)
        # slab hits per along_max (on all faces once)
        slab = {}
        for am in alongs:
            t0 = time.time()
            slab[am] = slab_hits(V, vn, cen, fn, tree_v, am)
            log(f'  slab along_max={am} done ({time.time()-t0:.0f}s)')
        smooth_cache = {}
        for td in tds:
            for mf in mfs:
                key = (td, mf)
                if key not in smooth_cache:
                    smooth_cache[key] = smooth_mask(td, mf, adj, dih, fa)
                smooth, top5 = smooth_cache[key]
                for am in alongs:
                    al = slab[am]
                    sm = smooth & np.isfinite(al)
                    if sm.sum() < 50:
                        rows.append(f'{name}\t{td:g}\t{mf:g}\t{am:g}\tnan\t0\t0\t0\t0\t{top5[0]:.2f}\t{sum(top5[:3]):.2f}')
                        continue
                    t_est = float(np.median(al[sm]))
                    wall = smooth & (al >= 0.5 * t_est) & (al <= 2.5 * t_est)
                    roll = smooth & ~np.isfinite(al)
                    rough = ~smooth
                    fracture = rough & ~np.isfinite(al)
                    anomaly = rough & np.isfinite(al)
                    # note: wall as defined includes smooth+finite-out-of-window; keep same
                    # convention as stage0: wall = smooth & paired-in-window
                    nf = len(F)
                    shares = [wall.sum()/nf, roll.sum()/nf, fracture.sum()/nf, anomaly.sum()/nf]
                    rows.append(f'{name}\t{td:g}\t{mf:g}\t{am:g}\t{t_est:.3f}\t'
                                + '\t'.join(f'{s:.4f}' for s in shares)
                                + f'\t{top5[0]:.2f}\t{sum(top5[:3]):.2f}')
        # ray pairing on best-guess labels for b-rate at extended range
        # choose td=20, mf=0.02, along=8 for the b probe
        smooth, top5 = smooth_mask(20.0, 0.02, adj, dih, fa)
        al = slab[8.0]
        sm = smooth & np.isfinite(al)
        if sm.sum() >= 50:
            t_est = float(np.median(al[sm]))
            wall = smooth & (al >= 0.5 * t_est) & (al <= 2.5 * t_est)
            fracture = (~smooth) & ~np.isfinite(al)
            sub = np.where(wall | fracture)[0]
            if len(sub) > 20000:
                sub = np.random.default_rng(0).choice(sub, 20000, replace=False)
            tree_f = cKDTree(cen)
            hd, hdg = ray_cast(V, F, fn[sub], cen[sub], tree_f, 2.5 * t_est + 1.0)
            wmask = wall[sub]
            summary[name] = {
                'V': int(len(V)), 'F': int(len(F)),
                't_est_mm@td20mf02am8': t_est,
                'b_wall_paired@ext': float(np.isfinite(hd[wmask]).mean()) if wmask.any() else None,
                'b_wall_n': int(wmask.sum()),
                'b_frac_paired@ext': float(np.isfinite(hd[~wmask]).mean()) if (~wmask).any() else None,
                'b_frac_n': int((~wmask).sum()),
                'area_mm2': float(fa.sum()),
            }
            log(f'  b@ext wall={summary[name]["b_wall_paired@ext"]} frac={summary[name]["b_frac_paired@ext"]} t_est={t_est:.2f}')
        else:
            summary[name] = {'V': int(len(V)), 'F': int(len(F)), 'no_smooth_faces': True}

    with open(os.path.join(args.out_dir, 'pota_relabel.tsv'), 'w') as f:
        f.write('\n'.join(rows) + '\n')

    # ---------- Q2: corrected Juglet per-piece medians ----------
    jr = ['piece\tlabel\ta_r1.0\ta_r1.5\ta_r2.0\ta_r3.0\tb_hit_rate\tc_tmed5\tc_tp90_5']
    for i in range(1, 10):
        name = f'Juglet_Piece_{i}'
        z = np.load(os.path.join(lab_dir, name + '.npz'))
        lab = z['labels']; devs = z['devs']
        hd = z['hit_dist']
        for L, nm in enumerate(['wall', 'roll', 'fracture', 'anomaly']):
            m = lab == L
            if not m.any():
                continue
            a = [f'{np.nanmedian(devs[r][m]):.4f}' if np.isfinite(devs[r][m]).any() else 'nan' for r in range(4)]
            b = f'{np.isfinite(hd[m]).mean():.4f}'
            jr.append(f'{name}\t{nm}\t' + '\t'.join(a) + f'\t{b}\tnan\tnan')
    with open(os.path.join(args.out_dir, 'juglet_perpiece_nanmedian.tsv'), 'w') as f:
        f.write('\n'.join(jr) + '\n')

    # c windows from stage0 summary json
    try:
        S = json.load(open(os.path.join(S0, 'out', 'stage0_summary.json')))
        with open(os.path.join(args.out_dir, 'juglet_perpiece_c5.tsv'), 'w') as f:
            f.write('piece\tlabel\tc_tmed_5\tc_tp90_5\n')
            for i in range(1, 10):
                d = S.get(f'Juglet_Piece_{i}', {})
                for cls in ('wall', 'roll', 'fracture', 'anomaly'):
                    e = (d.get('c') or {}).get(cls, {}).get('5.00') or {}
                    if e:
                        f.write(f"Juglet_Piece_{i}\t{cls}\t{e.get('tmed_med')}\t{e.get('tp90_med')}\n")
    except Exception as ex:
        log(f'c5 table failed: {ex}')

    with open(os.path.join(args.out_dir, 'pota_summary.json'), 'w') as f:
        json.dump(summary, f, indent=1)
    log('DONE')

if __name__ == '__main__':
    main()
