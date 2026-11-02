#!/usr/bin/env python3
"""Ticket 65 stage 0/1: per-sector localisation of J1's Surface_0 boundary (read-only).

Frozen definitions come from check_separation.py (t57) and the t62 frontier kit; nothing here
re-defines blind stretch, far share or the f2r/r2f distances.  What this adds:

  sheet        each mesh face is put on sheet A or B (the two largest dihedral<10deg smooth
               components, the remaining non-fracture faces attached to the nearer of the two by
               face-graph geodesic) or left as fracture / unreachable.  Mesh-only, arm-independent.
  rim side     a t59 label-rim edge (fracture | non-fracture) is on the S0 side when its
               non-fracture face is on the sheet Surface_0 mostly covers.  The scorer's rim holds
               BOTH sides; the S0 boundary can only ever follow the S0-side one.
  sector       10-deg bins of ring angle in ONE common frame: the circle fit of the t62F J1
               fold midpoints (the frame its blind stretch 271.8-340.1 is stated in).

Writes <out>/sectors_<arm>.tsv (J1), <out>/pieces_side.tsv (nine, both arms), <out>/j1_<arm>.npz.
"""
import collections, json, os, sys, time
import numpy as np
sys.path.insert(0, '/data/gpfs/projects/punim2657/SfSpp/runs/20261102-0450_05be12c_t57-sweep')
import check_separation as cs
from scipy.spatial import cKDTree
from scipy.sparse import coo_matrix
from scipy.sparse.csgraph import connected_components, dijkstra

RUNS = '/data/gpfs/projects/punim2657/SfSpp/runs'
LAB = RUNS + '/20261102-1144_638504b_t59-breakstop-stage0/out/labels'
ARMS = [('t55_count', RUNS + '/20261101-2004_05be12c_t55-worness07-breaklines/out/geom'),
        ('t62F_r1.0', RUNS + '/20261103-0035_ca520fe_t62-normalfix-s2/outF/geom')]
OUT = sys.argv[1] if len(sys.argv) > 1 else '.'
ARM_EXTRA = sys.argv[2:]          # optional name=geomdir pairs for stage 3 arms
for a in ARM_EXTRA:
    n, g = a.split('=', 1)
    ARMS.append((n, g))
NB = 36
TD = 10.0


def log(m):
    print('[%s] %s' % (time.strftime('%H:%M:%S'), m), flush=True)


def face_pairs(F, nv):
    e = np.vstack([F[:, [0, 1]], F[:, [1, 2]], F[:, [2, 0]]])
    fid = np.tile(np.arange(len(F)), 3)
    e.sort(1)
    key = e[:, 0].astype(np.int64) * nv + e[:, 1]
    o = np.argsort(key, kind='stable')
    ks = key[o]
    same = ks[1:] == ks[:-1]
    return fid[o][:-1][same], fid[o][1:][same], e[o][:-1][same]


def sheets(V, F, labels):
    tri = V[F]
    cr = np.cross(tri[:, 1] - tri[:, 0], tri[:, 2] - tri[:, 0])
    area = 0.5 * np.linalg.norm(cr, axis=1)
    fn = cr / np.maximum(2 * area[:, None], 1e-12)
    cen = tri.mean(1)
    fa, fb, ev = face_pairs(F, len(V))
    dih = np.degrees(np.arccos(np.clip((fn[fa] * fn[fb]).sum(1), -1, 1)))
    n = len(F)
    m = dih < TD
    g = coo_matrix((np.ones(m.sum()), (fa[m], fb[m])), shape=(n, n))
    _, comp = connected_components(g, directed=False)
    carea = np.bincount(comp, weights=area)
    top = np.argsort(carea)[::-1][:2]
    sheet = np.full(n, -1, int)
    sheet[comp == top[0]] = 0
    sheet[comp == top[1]] = 1
    nonfr = labels != 2
    ok = nonfr[fa] & nonfr[fb]
    w = np.linalg.norm(cen[fa[ok]] - cen[fb[ok]], axis=1) + 1e-6
    gg = coo_matrix((w, (fa[ok], fb[ok])), shape=(n, n)).tocsr()
    src = np.where(sheet >= 0)[0]
    d, _, srcs = dijkstra(gg, directed=False, indices=src, min_only=True, return_predecessors=True)
    fill = (sheet < 0) & nonfr & np.isfinite(d) & (srcs >= 0)
    sheet[fill] = sheet[srcs[fill]]
    sheet[~nonfr] = 2            # fracture
    return sheet, fa, fb, ev, fn, cen, area, [float(carea[t] / carea.sum()) for t in top]


def vgraph(V, F):
    a = np.concatenate([F[:, 0], F[:, 1], F[:, 2]])
    b = np.concatenate([F[:, 1], F[:, 2], F[:, 0]])
    lo, hi = np.minimum(a, b), np.maximum(a, b)
    nv = len(V)
    uk = np.unique(lo.astype(np.int64) * nv + hi)
    s, t = uk // nv, uk % nv
    return coo_matrix((np.linalg.norm(V[s] - V[t], axis=1), (s, t)), shape=(nv, nv)).tocsr()


def turn(g, vn, src, Ls=(2.0, 5.0, 10.0)):
    out = {L: [] for L in Ls}
    for s0 in range(0, len(src), 64):
        b = src[s0:s0 + 64]
        dist = dijkstra(g, directed=False, indices=b, limit=max(Ls) + 0.2)
        for r in range(len(b)):
            for L in Ls:
                mm = (dist[r] >= 0.8 * L) & (dist[r] <= L)
                if mm.sum() < 20:
                    out[L].append(np.nan); continue
                out[L].append(float(np.median(np.degrees(np.arccos(np.clip(vn[mm] @ vn[b[r]], -1, 1))))))
    return {L: np.array(v) for L, v in out.items()}


def angle(X, frame):
    c, e1, e2 = frame
    return np.mod(np.degrees(np.arctan2((X - c) @ e2, (X - c) @ e1)), 360.0)


def q(x, p):
    return round(float(np.percentile(x, p)), 3) if len(x) else ''


def load_piece(P):
    z = np.load(os.path.join(LAB, P + '.npz'))
    return z


def arm_piece(P, geom, z, sh, frame=None, want_sectors=False, g=None, vn=None):
    V, F, labels, vlab, hit = z['V'], z['F'], z['labels'], z['vlab'], z['hit_dist']
    sheet, fa, fb, ev, fn, cen, area, topfr = sh
    fS0, fS1 = os.path.join(geom, P + '.S0'), os.path.join(geom, P + '.S1')
    if not (os.path.isfile(fS0) and os.path.isfile(fS1)):
        return None
    p0, p1 = cs.read_ply(fS0), cs.read_ply(fS1)
    S0 = np.stack([p0[c] for c in 'xyz'], 1); S1 = np.stack([p1[c] for c in 'xyz'], 1)
    nS0 = np.stack([p0[c] for c in ('nx', 'ny', 'nz')], 1)
    nS0 /= np.maximum(np.linalg.norm(nS0, axis=1, keepdims=True), 1e-12)
    covA = cKDTree(S0).query(V)[0] <= cs.COV_TOL
    covB = cKDTree(S1).query(V)[0] <= cs.COV_TOL
    # vertex sheet: majority of incident faces' sheets
    vs = np.zeros((len(V), 4), int)
    sidx = np.where(sheet < 0, 3, sheet)
    for k in range(3):
        np.add.at(vs, (F[:, k], sidx), 1)
    vsheet = np.argmax(vs[:, :3], 1)
    vsheet[(vs[:, 0] == 0) & (vs[:, 1] == 0)] = 2
    s0sheet = 0 if covA[vsheet == 0].mean() >= covA[vsheet == 1].mean() else 1
    # rim edges and their side
    fr = labels == 2
    rimm = fr[fa] != fr[fb]
    nf = np.where(fr[fa[rimm]], fb[rimm], fa[rimm])
    rimE = ev[rimm]
    rside = sheet[nf]                      # 0/1 sheet id (or -1 unreachable)
    midr = V[rimE].mean(1)
    on0 = rside == s0sheet
    # fold
    edges = cs.mesh_edges(F)
    fold = edges[covA[edges[:, 0]] != covA[edges[:, 1]]]
    mid = V[fold].mean(1)
    c_, R, (e1, e2, _n), ang = cs.circle_fit(mid)
    own = (c_, e1, e2)
    if frame is None:
        frame = own
    fire = cs.fire_dots(S0, nS0)
    fa_own = angle(S0[fire], own)
    gap, glo, ghi = cs.largest_gap(fa_own)
    fa_com = angle(S0[fire], frame)
    gapc, gloc, ghic = cs.largest_gap(fa_com)
    d_f2r = cKDTree(midr).query(mid)[0]
    d_r2f = cKDTree(mid).query(midr)[0]
    d_f2r0 = cKDTree(midr[on0]).query(mid)[0]
    d_r2f0 = d_r2f[on0]
    ra_own = angle(midr, own)
    b5 = np.floor(ra_own / 5.0).astype(int) % 72
    cov = np.zeros(72, bool); cov[b5[d_r2f <= 1.0]] = True
    cov0 = np.zeros(72, bool); cov0[b5[on0 & (d_r2f <= 1.0)]] = True
    row = dict(piece=P, n_fold=len(mid), n_rim=len(midr), n_rim_s0side=int(on0.sum()),
               n_rim_s1side=int((rside == 1 - s0sheet).sum()), n_rim_other=int((rside < 0).sum()),
               sheet_top2=';'.join('%.3f' % t for t in topfr), s0sheet=s0sheet,
               blind_own=round(gap, 2), blind_lo=round(glo, 1),
               f2r_med=round(float(np.median(d_f2r)), 3), f2r_le1=round(float((d_f2r <= 1).mean()), 4),
               f2r_gt2=round(float((d_f2r > 2).mean()), 4), f2r_max=round(float(d_f2r.max()), 3),
               r2f_le1=round(float((d_r2f <= 1).mean()), 4), ring_cov_deg5=round(float(cov.mean() * 360), 1),
               f2r0_med=round(float(np.median(d_f2r0)), 3), f2r0_le1=round(float((d_f2r0 <= 1).mean()), 4),
               f2r0_max=round(float(d_f2r0.max()), 3),
               r2f0_med=round(float(np.median(d_r2f0)), 3), r2f0_le1=round(float((d_r2f0 <= 1).mean()), 4),
               r2f0_le2=round(float((d_r2f0 <= 2).mean()), 4),
               ring_cov0_deg5=round(float(cov0.mean() * 360), 1),
               S0_on_s0sheet=round(float(covA[vsheet == s0sheet].mean()), 4),
               S1_on_s0sheet=round(float(covB[vsheet == s0sheet].mean()), 4),
               S0_on_s1sheet=round(float(covA[vsheet == 1 - s0sheet].mean()), 4),
               S0_on_frac=round(float(covA[vsheet == 2].mean()), 4))
    if not want_sectors:
        return row, frame, None
    # ---------- per-sector (common frame) ----------
    tf = cKDTree(cen)
    _, fmid_face = tf.query(mid)
    flab = labels[fmid_face]; fsh = sheet[fmid_face]
    am = angle(mid, frame); ar = angle(midr, frame)
    acen = angle(cen, frame)
    sm = np.floor(am / 10).astype(int) % NB
    sr = np.floor(ar / 10).astype(int) % NB
    scen = np.floor(acen / 10).astype(int) % NB
    av = angle(V, frame); sv = np.floor(av / 10).astype(int) % NB
    tr0 = cKDTree(midr[on0])
    dv0 = tr0.query(V)[0]                   # vertex -> S0-side rim
    dc0 = tr0.query(cen)[0]
    trall = cKDTree(midr)
    dcall = trall.query(cen)[0]
    ingapc = np.mod(am - gloc, 360.0) < gapc
    # normal-turn sources: S0-side rim edge vertices
    rimv0 = np.unique(rimE[on0].ravel())
    rng = np.random.default_rng(65)
    srcs, ssec = [], []
    av_r = angle(V[rimv0], frame); sv_r = np.floor(av_r / 10).astype(int) % NB
    for s in range(NB):
        ids = rimv0[sv_r == s]
        if len(ids) > 24:
            ids = rng.choice(ids, 24, replace=False)
        srcs.extend(ids.tolist()); ssec.extend([s] * len(ids))
    srcs = np.array(srcs, int); ssec = np.array(ssec, int)
    T = turn(g, vn, srcs) if len(srcs) else {2.0: np.array([]), 5.0: np.array([]), 10.0: np.array([])}
    rows = []
    for s in range(NB):
        R0 = on0 & (sr == s)
        Fm = sm == s
        d0 = d_r2f[R0]
        f0 = d_f2r0[Fm]
        near = (sv == s) & (vsheet == s0sheet) & (dv0 <= 5.0)
        wallf = (scen == s) & (labels == 0) & (sheet == s0sheet) & (dc0 <= 5.0) & np.isfinite(hit)
        nearf = (scen == s) & (dcall <= 3.0)
        lm = np.bincount(labels[nearf], minlength=4) / max(nearf.sum(), 1)
        flm = np.bincount(flab[Fm], minlength=4) / max(Fm.sum(), 1)
        t2 = T[2.0][ssec == s]; t5 = T[5.0][ssec == s]; t10 = T[10.0][ssec == s]
        rows.append(dict(
            sector='%03d-%03d' % (10 * s, 10 * s + 10),
            in_blind=round(float(ingapc[Fm].mean()), 2) if Fm.any() else '',
            rim0_n=int(R0.sum()), rim1_n=int(((rside == 1 - s0sheet) & (sr == s)).sum()),
            r2f0_med=q(d0, 50), r2f0_p90=q(d0, 90), r2f0_max=round(float(d0.max()), 3) if len(d0) else '',
            r2f0_le1=round(float((d0 <= 1).mean()), 3) if len(d0) else '',
            cov1mm=int(bool((d0 <= 1).any())),
            fold_n=int(Fm.sum()), f2r0_med=q(f0, 50), f2r0_p90=q(f0, 90),
            f2r0_max=round(float(f0.max()), 3) if len(f0) else '',
            f2r0_gt2=round(float((f0 > 2).mean()), 3) if len(f0) else '',
            fold_W=round(flm[0], 2), fold_R=round(flm[1], 2), fold_F=round(flm[2], 2), fold_A=round(flm[3], 2),
            fold_on_s0=round(float((fsh[Fm] == s0sheet).mean()), 2) if Fm.any() else '',
            fold_on_s1=round(float((fsh[Fm] == 1 - s0sheet).mean()), 2) if Fm.any() else '',
            fold_on_fr=round(float((fsh[Fm] == 2).mean()), 2) if Fm.any() else '',
            s0band_n=int(near.sum()),
            s0band_byS0=round(float(covA[near].mean()), 3) if near.any() else '',
            s0band_byS1only=round(float((covB & ~covA)[near].mean()), 3) if near.any() else '',
            s0band_none=round(float((~covA & ~covB)[near].mean()), 3) if near.any() else '',
            wall_med=round(float(np.median(hit[wallf])), 3) if wallf.any() else '',
            wall_p10=q(hit[wallf], 10) if wallf.any() else '',
            lab3_W=round(lm[0], 2), lab3_R=round(lm[1], 2), lab3_F=round(lm[2], 2), lab3_A=round(lm[3], 2),
            turn2=round(float(np.nanmedian(t2)), 2) if np.isfinite(t2).any() else '',
            turn5=round(float(np.nanmedian(t5)), 2) if np.isfinite(t5).any() else '',
            turn10=round(float(np.nanmedian(t10)), 2) if np.isfinite(t10).any() else '',
            rate10=round(float(np.nanmedian(t10)) / 10.0, 2) if np.isfinite(t10).any() else ''))
    dump = dict(V=V, F=F, labels=labels, sheet=sheet, s0sheet=s0sheet, midr=midr, rside=rside,
                mid=mid, d_f2r0=d_f2r0, d_r2f=d_r2f, covA=covA, covB=covB, vsheet=vsheet,
                frame_c=frame[0], frame_e1=frame[1], frame_e2=frame[2], fire_pts=S0[fire],
                gapc=gapc, gloc=gloc, fold_face_lab=flab, fold_face_sheet=fsh)
    return row, frame, (rows, dump)


def main():
    os.makedirs(OUT, exist_ok=True)
    side_rows = []
    j1 = 'Juglet_Piece_1'
    pieces = ['Juglet_Piece_%d' % i for i in range(1, 10)]
    frame = None
    # common frame = t62F J1 fold-mid fit
    for P in pieces:
        z = load_piece(P)
        sh = sheets(z['V'], z['F'], z['labels'])
        log('%s sheets top2 %s' % (P, sh[7]))
        if P == j1:
            V, F = z['V'], z['F']
            g = vgraph(V, F)
            flip = -1.0 if cs.signed_volume(V, F) < 0 else 1.0
            vn = cs.vertex_normals(V, F) * flip
            _, frame, _ = arm_piece(P, dict(ARMS)['t62F_r1.0'], z, sh)
        for arm, geom in ARMS:
            ws = P == j1
            r = arm_piece(P, geom, z, sh, frame=frame if ws else None, want_sectors=ws,
                          g=g if ws else None, vn=vn if ws else None)
            if r is None:
                log('%s %s missing' % (arm, P)); continue
            row, _, extra = r
            row['arm'] = arm
            side_rows.append(row)
            log('%s %s blind %.2f f2r_le1 %.4f r2f_le1 %.4f r2f0_le1 %.4f cov %.1f cov0 %.1f' % (
                arm, P, row['blind_own'], row['f2r_le1'], row['r2f_le1'], row['r2f0_le1'],
                row['ring_cov_deg5'], row['ring_cov0_deg5']))
            if extra:
                rows, dump = extra
                cols = list(rows[0].keys())
                with open(os.path.join(OUT, 'sectors_%s.tsv' % arm), 'w') as fh:
                    fh.write('\t'.join(cols) + '\n')
                    for rr in rows:
                        fh.write('\t'.join(str(rr[c]) for c in cols) + '\n')
                np.savez_compressed(os.path.join(OUT, 'j1_%s.npz' % arm), **dump)
    cols = ['arm'] + [c for c in side_rows[0] if c != 'arm']
    with open(os.path.join(OUT, 'pieces_side.tsv'), 'w') as fh:
        fh.write('\t'.join(cols) + '\n')
        for r in side_rows:
            fh.write('\t'.join(str(r.get(c, '')) for c in cols) + '\n')
    log('done')


if __name__ == '__main__':
    main()
