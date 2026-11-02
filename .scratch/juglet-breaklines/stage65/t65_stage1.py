#!/usr/bin/env python3
"""Ticket 65 stage 1/2: what is J1's S0 boundary, physically, and what could a perfect one score?

Read-only on frozen bundles (t55 count, t62F radius 1.0); reuses t65_sector.py's sheet / rim-side
machinery and check_separation.py's frozen readers.  Per piece and arm:

  ceiling   the S0-side rim (t59 label rim whose non-fracture face is on the sheet S0 covers) taken
            as a PERFECT boundary, scored the way check_separation scores the real one:
              r2f_ceil   rim midpoints (both sides) within 1 mm of an S0-side rim midpoint
              cov_ceil   5-deg ring bins (frame = circle fit of the S0-side rim) holding a rim
                         midpoint within 1 mm of the S0-side rim
              gap_ceil   largest angular gap of S0-side rim midpoints in that frame (a lower bound
                         on the blind stretch of a boundary that sits exactly on the rim)
              rimgap_own largest angular gap of ALL rim midpoints in the arm's own (fold-fit) frame
  fold      each S0 boundary (fold) midpoint more than 2 mm from the S0-side rim is classed by the
            sheet of the face it sits on: s1 sheet = S0 overruns onto the far face (split artefact,
            class c); s0 sheet = S0 stops inside its own face (slice, class b); fracture = on the
            break face.  Component size of the fold graph (closed islands vs the main boundary).
  rim miss  each S0-side rim midpoint with no boundary within 1 mm is classed by who claims its two
            vertices: S0 (S0 reaches the rim and its boundary is elsewhere = overrun past the rim),
            S1 only (the seam was given to the other sheet = c), nobody (S0 stopped short = b).
  2a        S0-sheet wall-labelled vertices within 3 mm of the S0-side rim claimed by S1 and not S0.
  2d        fracture width at each S0-side rim midpoint (distance to the nearest S1-side rim
            midpoint), split by whether S0 overruns there.
"""
import json, os, sys
import numpy as np
from scipy.spatial import cKDTree
from scipy.sparse import coo_matrix
from scipy.sparse.csgraph import connected_components

WORK = os.path.dirname(os.path.abspath(__file__))
OUT = sys.argv[1]
_argv = sys.argv
sys.argv = [_argv[0], OUT] + _argv[2:]      # optional name=geomdir arms, as t65_sector.py
sys.path.insert(0, WORK)
import t65_sector as ts
cs = ts.cs
sys.argv = _argv


def fr(x, n=4):
    return round(float(x), n)


def piece_arm(P, geom, z, sh):
    V, F, labels = z['V'], z['F'], z['labels']
    sheet, fa, fb, ev, fn, cen, area, topfr = sh
    p0, p1 = cs.read_ply(os.path.join(geom, P + '.S0')), cs.read_ply(os.path.join(geom, P + '.S1'))
    S0 = np.stack([p0[c] for c in 'xyz'], 1); S1 = np.stack([p1[c] for c in 'xyz'], 1)
    covA = cKDTree(S0).query(V)[0] <= cs.COV_TOL
    covB = cKDTree(S1).query(V)[0] <= cs.COV_TOL
    vs = np.zeros((len(V), 4), int)
    sidx = np.where(sheet < 0, 3, sheet)
    for k in range(3):
        np.add.at(vs, (F[:, k], sidx), 1)
    vsheet = np.argmax(vs[:, :3], 1)
    vsheet[(vs[:, 0] == 0) & (vs[:, 1] == 0)] = 2
    s0s = 0 if covA[vsheet == 0].mean() >= covA[vsheet == 1].mean() else 1
    frm = labels == 2
    rimm = frm[fa] != frm[fb]
    nf = np.where(frm[fa[rimm]], fb[rimm], fa[rimm])
    rimE = ev[rimm]
    rside = sheet[nf]
    midr = V[rimE].mean(1)
    on0 = rside == s0s
    on1 = rside == 1 - s0s
    edges = cs.mesh_edges(F)
    fmask = covA[edges[:, 0]] != covA[edges[:, 1]]
    fold = edges[fmask]
    mid = V[fold].mean(1)
    # ---------- ceilings: the S0-side rim as a perfect boundary ----------
    r0 = midr[on0]
    d_all_to_r0 = cKDTree(r0).query(midr)[0]
    c_, R, (e1, e2, _n), _ = cs.circle_fit(r0)
    fr0 = (c_, e1, e2)
    a_r = ts.angle(midr, fr0)
    b5 = np.floor(a_r / 5).astype(int) % 72
    cov = np.zeros(72, bool); cov[b5[d_all_to_r0 <= 1.0]] = True
    gap_ceil = cs.largest_gap(ts.angle(r0, fr0))
    c2, R2, (f1, f2, _), _ = cs.circle_fit(mid)
    own = (c2, f1, f2)
    rimgap_own = cs.largest_gap(ts.angle(midr, own))
    rim0gap_own = cs.largest_gap(ts.angle(r0, own))
    b5o = np.floor(ts.angle(midr, own) / 5).astype(int) % 72
    occ_own = np.zeros(72, bool); occ_own[b5o] = True
    # ---------- fold classification ----------
    d_f2r0 = cKDTree(r0).query(mid)[0]
    _, ffc = cKDTree(cen).query(mid)
    fsh = sheet[ffc]
    off = d_f2r0 > 2.0
    nv = len(V)
    g = coo_matrix((np.ones(len(fold)), (fold[:, 0], fold[:, 1])), shape=(nv, nv))
    ncomp, comp = connected_components(g, directed=False)
    fcomp = comp[fold[:, 0]]
    csize = np.bincount(fcomp, minlength=ncomp)
    main = np.argmax(csize)
    in_main = fcomp == main
    comp_off = np.bincount(fcomp, weights=off.astype(float), minlength=ncomp)
    island = (comp_off == csize) & (csize > 0)           # components wholly > 2 mm off the rim
    fold_island = island[fcomp]
    # ---------- rim-miss classification ----------
    d_r2f = cKDTree(mid).query(midr)[0]
    miss0 = on0 & (d_r2f > 1.0)
    a0, a1 = rimE[:, 0], rimE[:, 1]
    byS0 = covA[a0] & covA[a1]
    byS1only = (covB[a0] | covB[a1]) & ~(covA[a0] | covA[a1])
    nobody = ~(covA[a0] | covA[a1] | covB[a0] | covB[a1])
    partS0 = ~byS0 & (covA[a0] | covA[a1])
    # fracture vertices beyond the S0-side rim: claimed by S0?
    fv = np.unique(F[frm].ravel())
    frS0 = covA[fv].mean(); frS1 = covB[fv].mean()
    # ---------- 2a ----------
    tr0 = cKDTree(r0)
    dv0 = tr0.query(V)[0]
    vlab = z['vlab']
    band = (vsheet == s0s) & (vlab == 0) & (dv0 <= 3.0)
    a2_s1only = (covB & ~covA)[band].mean() if band.any() else np.nan
    a2_none = (~covA & ~covB)[band].mean() if band.any() else np.nan
    # S1 band symmetric: S1-sheet wall vertices within 3 mm of S1-side rim claimed by S0 (overrun)
    r1 = midr[on1]
    dv1 = cKDTree(r1).query(V)[0] if len(r1) else np.full(len(V), np.inf)
    band1 = (vsheet == 1 - s0s) & (vlab == 0) & (dv1 <= 3.0)
    s1band_byS0 = covA[band1].mean() if band1.any() else np.nan
    s1band_byS0_notS1 = (covA & ~covB)[band1].mean() if band1.any() else np.nan
    # ---------- 2d: fracture width at each S0-side rim point ----------
    width = cKDTree(r1).query(r0)[0] if len(r1) else np.full(len(r0), np.nan)
    over = miss0[on0] & byS0[on0]
    row = dict(
        piece=P, s0sheet=s0s, n_rim=len(midr), n_rim0=int(on0.sum()), n_rim1=int(on1.sum()),
        n_fold=len(mid),
        r2f_ceil=fr((d_all_to_r0 <= 1.0).mean()), cov_ceil=fr(cov.mean() * 360, 1),
        gap_ceil=fr(gap_ceil[0], 2), rimgap_own=fr(rimgap_own[0], 2), rimgap_own_lo=fr(rimgap_own[1], 1),
        rim0gap_own=fr(rim0gap_own[0], 2), rimocc_own_deg=fr(occ_own.mean() * 360, 1),
        own_R=fr(R2, 2), rim0_R=fr(R, 2),
        fold_off2=fr(off.mean()), fold_off2_s1=fr((off & (fsh == 1 - s0s)).mean()),
        fold_off2_s0=fr((off & (fsh == s0s)).mean()), fold_off2_fr=fr((off & (fsh == 2)).mean()),
        fold_off2_unr=fr((off & (fsh < 0)).mean()),
        fold_ncomp=int(ncomp_used(fcomp)), fold_main_share=fr(in_main.mean()),
        fold_island_share=fr(fold_island.mean()),
        fold_off2_island=fr((off & fold_island).mean()),
        rim0_miss=fr(miss0[on0].mean()),
        miss_byS0=fr((miss0 & byS0).sum() / max(miss0.sum(), 1)),
        miss_partS0=fr((miss0 & partS0).sum() / max(miss0.sum(), 1)),
        miss_byS1only=fr((miss0 & byS1only).sum() / max(miss0.sum(), 1)),
        miss_nobody=fr((miss0 & nobody).sum() / max(miss0.sum(), 1)),
        frac_v_byS0=fr(frS0), frac_v_byS1=fr(frS1),
        a2_band_n=int(band.sum()), a2_s1only=fr(a2_s1only), a2_none=fr(a2_none),
        s1band_n=int(band1.sum()), s1band_byS0=fr(s1band_byS0), s1band_byS0_notS1=fr(s1band_byS0_notS1),
        width_med=fr(np.nanmedian(width), 3),
        width_med_over=fr(np.nanmedian(width[over]), 3) if over.any() else '',
        width_med_hit=fr(np.nanmedian(width[~miss0[on0]]), 3) if (~miss0[on0]).any() else '',
        n_over=int(over.sum()))
    dump = dict(mid=mid, d_f2r0=d_f2r0, fsh=fsh, fcomp=fcomp, fold_island=fold_island,
                midr=midr, on0=on0, on1=on1, d_r2f=d_r2f, byS0=byS0, byS1only=byS1only,
                nobody=nobody, partS0=partS0, s0s=s0s)
    return row, dump


def ncomp_used(fcomp):
    return len(np.unique(fcomp))


def main():
    os.makedirs(OUT, exist_ok=True)
    rows = []
    for P in ['Juglet_Piece_%d' % i for i in range(1, 10)]:
        z = ts.load_piece(P)
        sh = ts.sheets(z['V'], z['F'], z['labels'])
        for arm, geom in ts.ARMS:
            r, dump = piece_arm(P, geom, z, sh)
            r['arm'] = arm
            rows.append(r)
            ts.log('%s %s r2f_ceil %s cov_ceil %s gap_ceil %s rimgap_own %s off2 %s (s1 %s s0 %s fr %s) '
                   'miss %s byS0 %s S1only %s nobody %s a2 %s' % (
                       arm, P, r['r2f_ceil'], r['cov_ceil'], r['gap_ceil'], r['rimgap_own'], r['fold_off2'],
                       r['fold_off2_s1'], r['fold_off2_s0'], r['fold_off2_fr'], r['rim0_miss'], r['miss_byS0'],
                       r['miss_byS1only'], r['miss_nobody'], r['a2_s1only']))
            if P == 'Juglet_Piece_1':
                np.savez_compressed(os.path.join(OUT, 's1_j1_%s.npz' % arm), **dump)
    cols = ['arm'] + [c for c in rows[0] if c != 'arm']
    with open(os.path.join(OUT, 'stage1_pieces.tsv'), 'w') as fh:
        fh.write('\t'.join(cols) + '\n')
        for r in rows:
            fh.write('\t'.join(str(r.get(c, '')) for c in cols) + '\n')
    ts.log('done')


if __name__ == '__main__':
    main()
