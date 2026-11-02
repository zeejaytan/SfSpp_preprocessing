#!/usr/bin/env python3
"""check_separation.py -- read-only audit of a SfS++ preprocessing run's surface separation.

Ticket 57 (SfSpp_preprocessing).  Answers one question per piece: did the growth split the
piece along the break, or did one region slide onto the far face of the wall?

FROZEN DEFINITIONS (lead's ruling 2026-11-02, after the Task 1 baseline validation):

  far-skin share (per surface)   fold-edge midpoints of that surface's coverage; every k-th
                                 midpoint takes the area-weighted mesh vertex normal of the
                                 nearest mesh vertex; the median signed offset of the
                                 surface's points within a 3 mm ball along that normal; a
                                 fold point is far when the median < -0.8 mm.  Reported as a
                                 share plus the offsets.
  blind stretch                  DEGREES ONLY: the largest angular gap in Surface_0's
                                 boundary-fire dots (detector R=4 mm, 108-deg void),
                                 measured around the break-edge ring.  The "717 fold
                                 points" figure in the ticket's Given is DERIVED from the
                                 degrees (717/2824 = 91.4/360 = 0.2539) and is NOT a
                                 measurement: the fold's angular density is far from
                                 uniform (36 ten-degree bins, mean 78.4, sd 70.2, range
                                 4-266), so the widest 91.4-deg window holds 1309 midpoints,
                                 not 717.  Never calibrate to the point count.
  seam share                     fold points where mesh vertices 0.4-3.0 mm outward (in
                                 plane, away from the surface's LOCAL CENTROID = mean of
                                 the mesh vertices within 3 mm of the fold midpoint) are
                                 covered by the other surface at fraction > 0.6.  "Inside"
                                 = fold midpoints whose ring angle falls within the frozen
                                 blind stretch; "outside" = the rest.
  double-cover                   triangle share, >=1-vertex variant: faces with at least one
                                 vertex claimed by both surfaces (0.6 mm).  Point shares
                                 are reported alongside; variants >=2-vertex and all-3 are
                                 in the JSON detail.
  coincident lip                 number of S1 points that are EXACT duplicates of S0 points
                                 (distance 0.0) -- stronger than a near-touch count.
  dots                           Breakline_0 point count; pieces below 50 are flagged (the
                                 assembler's short-breakline floor, main.cpp ~line 86).
  genuine pairs                  t54 pairing protocol: median NN distance S1->S0 between 70%
                                 and 105% of the piece's own wall thickness AND median
                                 perpendicular residual <= 0.05 mm.

Read-only: opens the run's files, writes nothing except the tables you ask for with
--out-tsv / --out-json.  Exit codes: 0 clean, 1 a threshold was exceeded, 2 usage/IO error.

Usage:
  python check_separation.py --geom <run>/out/geom --mesh-dir <Dataset>/Mesh/Juglet \
      [--pieces a,b,c] [--walls <t54>/out/wall40] [--k 15] [--out-tsv f] [--out-json f] \
      [--max-far-share 0.2] [--max-dc-tri 0.15] [--max-blind-deg 30] [--min-seam-in 0.8] \
      [--min-dots 50] [--quiet]
"""
import argparse
import glob
import json
import os
import sys

import numpy as np
from scipy.spatial import cKDTree

# ---- frozen constants (do not tune per run) --------------------------------
COV_TOL = 0.6      # mm, vertex claimed by a surface
BALL = 3.0         # mm, far-skin offset ball
FAR_THR = -0.8     # mm, "far side of the wall" median threshold
BAND5 = 5.0        # mm, points near the blind fold
DC_TOL = 0.6       # mm, double-cover point tolerance
CENTROID_R = 3.0   # mm, mesh-vertex ball for the local centroid
SEAM_LO = 0.4      # mm, inner edge of the seam shell
SEAM_HI = 3.0      # mm, outer edge of the seam shell
SEAM_FRAC = 0.6    # covered fraction that makes a fold point a seam point
SMOOTH_W = 10      # fold-point window for the seam-arc indicator
SMOOTH_THR = 0.6   # smoothed seam level that marks the seam sector
FIRE_R = 4.0       # mm, boundary-fire detector neighbourhood
FIRE_VOID = 108.0  # deg, angular void that makes a point a boundary-fire dot
FIRE_MIN_OFF = 0.3 # mm, in-plane offset below which a neighbour is the point itself
DOT_FLOOR = 50     # assembler short-breakline floor
PAIR_LO, PAIR_HI = 70.0, 105.0   # % of own wall thickness
PAIR_ACROSS = 0.05 # mm


# ---- readers ---------------------------------------------------------------
def read_ply(path):
    """ASCII PLY -> dict of float arrays keyed by property name."""
    with open(path, 'r', errors='replace') as fh:
        n = None
        props = []
        while True:
            line = fh.readline()
            if not line:
                raise ValueError('PLY header unterminated: %s' % path)
            t = line.strip()
            if t.startswith('element vertex'):
                n = int(t.split()[-1])
            elif t.startswith('property'):
                p = t.split()
                if p[1] != 'list':
                    props.append(p[-1])
            elif t == 'end_header':
                break
        data = np.loadtxt(fh, max_rows=n, ndmin=2)
    out = {}
    for i, p in enumerate(props):
        if i < data.shape[1]:
            out[p] = data[:, i]
    return out


def read_pcd(path):
    """ASCII PCD -> dict of float arrays keyed by FIELD name."""
    with open(path, 'r', errors='replace') as fh:
        fields = []
        n = 0
        while True:
            line = fh.readline()
            if not line:
                raise ValueError('PCD header unterminated: %s' % path)
            t = line.strip()
            if t.startswith('FIELDS'):
                fields = t.split()[1:]
            elif t.startswith('POINTS'):
                n = int(t.split()[1])
            elif t.startswith('DATA'):
                break
        data = np.loadtxt(fh, max_rows=n, ndmin=2)
    out = {}
    for i, p in enumerate(fields):
        if i < data.shape[1]:
            out[p] = data[:, i]
    return out


def read_obj(path):
    verts, faces = [], []
    with open(path, 'r', errors='replace') as fh:
        for line in fh:
            if line.startswith('v '):
                p = line.split()
                verts.append((float(p[1]), float(p[2]), float(p[3])))
            elif line.startswith('f '):
                p = line.split()[1:]
                idx = [int(t.split('/')[0]) for t in p]
                idx = [i - 1 if i > 0 else len(verts) + i for i in idx]
                for k in range(1, len(idx) - 1):          # fan-triangulate
                    faces.append((idx[0], idx[k], idx[k + 1]))
    return np.asarray(verts, float), np.asarray(faces, int)


# ---- mesh helpers ----------------------------------------------------------
def mesh_edges(faces):
    e = np.vstack([faces[:, [0, 1]], faces[:, [1, 2]], faces[:, [2, 0]]])
    e = np.sort(e, axis=1)
    return np.unique(e, axis=0)


def vertex_normals(v, f):
    fn = np.cross(v[f[:, 1]] - v[f[:, 0]], v[f[:, 2]] - v[f[:, 0]])
    vn = np.zeros_like(v)
    for k in range(3):
        np.add.at(vn, f[:, k], fn)
    nrm = np.linalg.norm(vn, axis=1, keepdims=True)
    return vn / np.maximum(nrm, 1e-12)


def signed_volume(v, f):
    a, b, c = v[f[:, 0]], v[f[:, 1]], v[f[:, 2]]
    return float(np.einsum('ij,ij->i', a, np.cross(b, c)).sum() / 6.0)


def circle_fit(P):
    """Fit a circle in the best-fit plane.  Returns centre, R, basis, angles."""
    c = P.mean(axis=0)
    Q = P - c
    _, _, Vt = np.linalg.svd(Q, full_matrices=False)
    e1, e2, nrm = Vt[0], Vt[1], Vt[2]
    x, y = Q @ e1, Q @ e2
    A = np.stack([2 * x, 2 * y, np.ones_like(x)], 1)
    b = x * x + y * y
    sol, *_ = np.linalg.lstsq(A, b, rcond=None)
    cx, cy, k = sol
    R = float(np.sqrt(max(k + cx * cx + cy * cy, 1e-12)))
    centre = c + cx * e1 + cy * e2
    ang = np.mod(np.arctan2(y - cy, x - cx), 2 * np.pi)
    return centre, R, (e1, e2, nrm), ang


def smooth_circular(x, w):
    """Moving average on a circular sequence (wrap-around, length preserved)."""
    n = len(x)
    if n == 0 or w <= 1:
        return x.copy()
    w = min(w, n)
    k = np.ones(w) / w
    xx = np.concatenate([x[-w:], x, x[:w]])
    return np.convolve(xx, k, mode='same')[w:w + n]


def arc_span_deg(theta):
    """Smallest arc covering a set of angles (deg): 360 - largest gap."""
    if len(theta) == 0:
        return 0.0
    t = np.sort(np.mod(np.degrees(theta), 360.0))
    if len(t) == 1:
        return 0.0
    gaps = np.diff(np.concatenate([t, t[:1] + 360.0]))
    return float(360.0 - gaps.max())


# ---- boundary-fire dots ----------------------------------------------------
def fire_dots(P, N):
    """Boundary-fire detector: a point fires when its tangent-plane neighbourhood has an
    angular void wider than FIRE_VOID.  Returns a boolean mask."""
    if len(P) == 0:
        return np.zeros(0, bool)
    tree = cKDTree(P)
    nb = tree.query_ball_point(P, FIRE_R)
    fire = np.zeros(len(P), bool)
    for i in range(len(P)):
        idx = nb[i]
        if len(idx) < 3:
            continue
        off = P[idx] - P[i]
        off = off - np.outer(off @ N[i], N[i])          # into the tangent plane
        keep = np.linalg.norm(off, axis=1) > FIRE_MIN_OFF
        if keep.sum() < 3:
            continue
        e1 = np.cross(N[i], [0.0, 0.0, 1.0])
        if np.linalg.norm(e1) < 1e-6:
            e1 = np.cross(N[i], [0.0, 1.0, 0.0])
        e1 /= np.linalg.norm(e1)
        e2 = np.cross(N[i], e1)
        a = np.sort(np.arctan2(off[keep] @ e2, off[keep] @ e1))
        gaps = np.diff(a)
        wrap = 2 * np.pi - (a[-1] - a[0])
        void = max(gaps.max() if len(gaps) else 0.0, wrap)
        fire[i] = void > np.radians(FIRE_VOID)
    return fire


def largest_gap(dots_ang_deg):
    """Largest angular gap in a sorted set of angles (deg).  Returns (gap_deg, lo, hi)."""
    if len(dots_ang_deg) < 2:
        return 360.0, 0.0, 0.0
    a = np.sort(np.mod(dots_ang_deg, 360.0))
    gaps = np.diff(np.concatenate([a, a[:1] + 360.0]))
    i = int(np.argmax(gaps))
    return float(gaps[i]), float(a[i]), float(a[(i + 1) % len(a)])


# ---- the metrics -----------------------------------------------------------
def surface_metrics(A, N, B, verts, edges, vn, vt, k):
    """Separation metrics for surface A against surface B on a mesh."""
    out = {'n': int(len(A))}
    tA, tB = cKDTree(A), cKDTree(B)
    covA, _ = tA.query(verts); covA = covA <= COV_TOL
    covB, _ = tB.query(verts); covB = covB <= COV_TOL
    fold = edges[covA[edges[:, 0]] != covA[edges[:, 1]]]
    out['fold_edges'] = int(len(fold))
    covU = covA | covB
    out['union_rim_edges'] = int((covU[edges[:, 0]] != covU[edges[:, 1]]).sum())
    if len(fold) == 0:
        out.update({'blind_deg': 0.0, 'blind_lo': None, 'blind_hi': None,
                    'seam_arc_deg': 0.0, 'seam_arc_pts': 0, 'seam_arc_lo': None,
                    'seam_arc_hi': None, 'seam_gap_in': None, 'seam_gap_out': None,
                    'seam_arc_in_gap': None,
                    'seam_in': None, 'seam_out': None, 'seam_n_in': 0, 'seam_n_out': 0,
                    'far_share': None, 'far_share_in': None, 'far_share_out': None,
                    'far_n_sampled': 0, 'far_n_far': 0, 'far_in_far': 0, 'far_in_n': 0,
                    'far_in_med_lo': None, 'far_in_med_hi': None, 'far_pts5mm': None,
                    'ring_R': None, 'fire_dots': 0})
        return out, None

    mid = verts[fold].mean(axis=1)
    _, iv = vt.query(mid)
    n_mid = vn[iv]
    centre, R, (e1, e2, _n), ang = circle_fit(mid)
    out['ring_R'] = round(float(R), 3)
    order = np.argsort(ang)

    # ---- blind stretch (FROZEN): largest angular gap in THIS surface's fire dots, deg
    fire = fire_dots(A, N)
    out['fire_dots'] = int(fire.sum())
    if fire.any():
        fa = np.mod(np.degrees(np.arctan2((A[fire] - centre) @ e2,
                                          (A[fire] - centre) @ e1)), 360.0)
        gap, glo, ghi = largest_gap(fa)
    else:
        gap, glo, ghi = 360.0, 0.0, 0.0
    out['blind_deg'] = round(gap, 2)
    out['blind_lo'] = round(glo, 2)
    out['blind_hi'] = round(ghi, 2)
    angm = np.mod(np.degrees(ang), 360.0)
    in_firegap = np.mod(angm - glo, 360.0) < gap

    # ---- seam share (local centroid = mean of mesh vertices within CENTROID_R)
    ballv = vt.query_ball_point(mid, CENTROID_R)
    cs = np.array([verts[b].mean(axis=0) if len(b) else mid[i] for i, b in enumerate(ballv)])
    vshell = vt.query_ball_point(mid, SEAM_HI)
    seam = np.zeros(len(mid), np.int8)
    for i in range(len(mid)):
        d = mid[i] - cs[i]
        d = d - np.dot(d, n_mid[i]) * n_mid[i]
        nd = np.linalg.norm(d)
        if nd < 1e-9:
            continue
        dhat = d / nd
        cand = [j for j in vshell[i]
                if SEAM_LO <= np.linalg.norm(verts[j] - mid[i]) <= SEAM_HI
                and np.dot(verts[j] - mid[i], dhat) > 0]
        if not cand:
            continue
        seam[i] = 1 if float(covB[np.array(cand)].mean()) > SEAM_FRAC else 0
    # ---- seam arc: longest run of the smoothed seam indicator above SMOOTH_THR.
    # This is the SECTOR the seam test singles out; it is reported separately from the
    # fire-gap blind stretch because the two are different measurements (the seam arc sits
    # inside the fire gap: 161 of 161 arc points are inside J1's 85.5-deg gap, and the arc
    # spans only 11.65 deg of it).  Seam shares are reported under BOTH sectors.
    s_ord = seam[order].astype(float)
    sm = smooth_circular(s_ord, SMOOTH_W)
    mask = sm > SMOOTH_THR
    n = len(mask)
    runs = []
    if mask.any():
        mm = np.concatenate([mask, mask])
        i = 0
        while i < n:
            if mm[i]:
                j = i
                while j < i + n and mm[j]:
                    j += 1
                if j - i < n:
                    runs.append((i % n, (j - 1) % n, j - i))
                i = j
            else:
                i += 1
        runs = [r for r in runs if r[2] < n]
        if not runs:
            runs = [(0, n - 1, n)]
    in_arc = np.zeros(n, bool)
    if runs:
        aa, bb, LL = max(runs, key=lambda r: r[2])
        if aa <= bb:
            in_arc[aa:bb + 1] = True
        else:
            in_arc[aa:] = True
            in_arc[:bb + 1] = True
    theta_ord = ang[order]
    out['seam_arc_deg'] = round(float(arc_span_deg(theta_ord[in_arc])), 2) if in_arc.any() else 0.0
    out['seam_arc_pts'] = int(in_arc.sum())
    out['seam_arc_lo'] = round(float(np.degrees(theta_ord[in_arc]).min() % 360), 2) if in_arc.any() else None
    out['seam_arc_hi'] = round(float(np.degrees(theta_ord[in_arc]).max() % 360), 2) if in_arc.any() else None
    # seam shares: primary = under the seam arc (the sector the seam test singles out);
    # secondary = under the frozen fire gap, so the two are never confused
    out['seam_in'] = round(float(s_ord[in_arc].mean()), 3) if in_arc.any() else None
    out['seam_out'] = round(float(s_ord[~in_arc].mean()), 3) if (~in_arc).any() else None
    out['seam_n_in'] = int(in_arc.sum())
    out['seam_n_out'] = int((~in_arc).sum())
    out['seam_gap_in'] = round(float(seam[in_firegap].mean()), 3) if in_firegap.any() else None
    out['seam_gap_out'] = round(float(seam[~in_firegap].mean()), 3) if (~in_firegap).any() else None
    out['seam_arc_in_gap'] = bool(in_arc.any() and in_firegap.any() and
                                  (in_arc & ~in_firegap).sum() == 0)

    # ---- far skin: every k-th fold midpoint in ring order
    ballA = tA.query_ball_point(mid, BALL)
    samp = order[::k]
    meds = np.full(len(samp), np.nan)
    for si, i in enumerate(samp):
        idxA = ballA[i]
        if len(idxA) == 0:
            continue
        meds[si] = float(np.median((A[idxA] - mid[i]) @ n_mid[i]))
    ok = np.isfinite(meds)
    far = meds < FAR_THR
    out['far_n_sampled'] = int(ok.sum())
    out['far_n_far'] = int((far & ok).sum())
    out['far_share'] = round(float((far & ok).sum() / max(ok.sum(), 1)), 4)
    samp_in = in_firegap[samp]
    if (samp_in & ok).any():
        out['far_in_n'] = int((samp_in & ok).sum())
        out['far_in_far'] = int((far & samp_in & ok).sum())
        out['far_share_in'] = round(float(out['far_in_far'] / out['far_in_n']), 4)
        mm = meds[samp_in & ok]
        out['far_in_med_lo'] = round(float(mm.min()), 3)
        out['far_in_med_hi'] = round(float(mm.max()), 3)
    else:
        out['far_in_n'] = 0; out['far_in_far'] = 0
        out['far_share_in'] = None
        out['far_in_med_lo'] = out['far_in_med_hi'] = None
    if (~samp_in & ok).any():
        out['far_share_out'] = round(float((far & ~samp_in & ok).sum() / (~samp_in & ok).sum()), 4)
    else:
        out['far_share_out'] = None

    # ---- far share of A's points within 5 mm of the blind fold
    if in_firegap.any():
        blind_mid = mid[in_firegap]
        tBM = cKDTree(blind_mid)
        dbm, _ = tBM.query(A)
        band = dbm <= BAND5
        if band.any():
            _, nb_ = vt.query(blind_mid)
            _, imb = tBM.query(A[band])
            offs = np.einsum('ij,ij->i', A[band] - blind_mid[imb], vn[nb_[imb]])
            out['far_pts5mm'] = round(float((offs < FAR_THR).mean()), 4)
            out['n_pts5mm'] = int(band.sum())
        else:
            out['far_pts5mm'] = None; out['n_pts5mm'] = 0
    else:
        out['far_pts5mm'] = None; out['n_pts5mm'] = 0
    return out, mid


def coincident_lip(S0, S1):
    """S1 points that are EXACT duplicates of S0 points."""
    d, _ = cKDTree(S0).query(S1)
    return int((d <= 1e-9).sum()), int(len(S1))


def pair_quality(S0, S1, nA, nB, wall):
    """t54 pairing protocol."""
    dist, idx = cKDTree(S0).query(S1)
    nn = float(np.median(dist))
    dvec = S1 - S0[idx]
    dpar = np.abs(np.einsum('ij,ij->i', dvec, nA[idx]))
    across = float(np.median(np.abs(dist - dpar)))
    ang = float(np.degrees(np.median(np.arccos(np.clip(
        np.abs(np.einsum('ij,ij->i', nB, nA[idx])), -1, 1)))))
    pct = 100.0 * nn / wall
    return {'med_nn': round(nn, 3), 'med_across': round(across, 3),
            'med_angle': round(ang, 2), 'wall_mm': round(wall, 3),
            'pct_wall': round(pct, 1),
            'genuine': bool(PAIR_LO <= pct <= PAIR_HI and across <= PAIR_ACROSS)}


def piece_metrics(geom, mesh_dir, P, k, walls):
    """All frozen metrics for one piece.  Returns (row, detail)."""
    row = {'piece': P}
    fS0 = os.path.join(geom, P + '.S0')
    fS1 = os.path.join(geom, P + '.S1')
    fB0 = os.path.join(geom, P + '.Bl0')
    fOBJ = os.path.join(mesh_dir, P + '_Mesh.obj')
    if not (os.path.isfile(fS0) and os.path.isfile(fS1) and os.path.isfile(fOBJ)):
        row['status'] = 'NO-SURFACE'
        return row, {}
    v, f = read_obj(fOBJ)
    flip = -1.0 if signed_volume(v, f) < 0 else 1.0
    vn = vertex_normals(v, f) * flip
    edges = mesh_edges(f)
    vt = cKDTree(v)
    p0, p1 = read_ply(fS0), read_ply(fS1)
    S0 = np.stack([p0[c] for c in 'xyz'], 1)
    S1 = np.stack([p1[c] for c in 'xyz'], 1)
    nS0 = np.stack([p0[c] for c in ('nx', 'ny', 'nz')], 1)
    nS0 /= np.maximum(np.linalg.norm(nS0, axis=1, keepdims=True), 1e-12)
    nS1 = np.stack([p1[c] for c in ('nx', 'ny', 'nz')], 1)
    nS1 /= np.maximum(np.linalg.norm(nS1, axis=1, keepdims=True), 1e-12)

    m0, mid0 = surface_metrics(S0, nS0, S1, v, edges, vn, vt, k)
    m1, mid1 = surface_metrics(S1, nS1, S0, v, edges, vn, vt, k)

    cov0, _ = cKDTree(S0).query(v); cov0 = cov0 <= COV_TOL
    cov1, _ = cKDTree(S1).query(v); cov1 = cov1 <= COV_TOL
    d01, _ = cKDTree(S1).query(S0)
    d10, _ = cKDTree(S0).query(S1)
    dc_pt01 = float((d01 <= DC_TOL).mean())
    dc_pt10 = float((d10 <= DC_TOL).mean())
    dc_ge1 = float(((cov0[f].sum(1) >= 1) & (cov1[f].sum(1) >= 1)).mean())
    dc_ge2 = float(((cov0[f].sum(1) >= 2) & (cov1[f].sum(1) >= 2)).mean())
    dc_all3 = float((cov0[f].all(1) & cov1[f].all(1)).mean())
    lip_n, lip_tot = coincident_lip(S0, S1)

    bl0 = int(read_pcd(fB0)['x'].shape[0]) if os.path.isfile(fB0) else 0
    fB1 = os.path.join(geom, P + '.Bl1')
    bl1 = int(read_pcd(fB1)['x'].shape[0]) if os.path.isfile(fB1) else 0

    row.update({
        'status': 'ok', 'nS0': len(S0), 'nS1': len(S1),
        'foldS0': m0['fold_edges'], 'foldS1': m1['fold_edges'],
        'unionRim': m0['union_rim_edges'],
        'blindDeg': m0['blind_deg'], 'fireDots': m0['fire_dots'],
        'seamArcDeg': m0['seam_arc_deg'], 'seamArcPts': m0['seam_arc_pts'],
        'seamIn': m0['seam_in'], 'seamOut': m0['seam_out'],
        'seamGapIn': m0['seam_gap_in'], 'seamGapOut': m0['seam_gap_out'],
        'arcInGap': m0['seam_arc_in_gap'],
        'farS0': m0['far_share'], 'farS0_in': m0['far_share_in'], 'farS0_out': m0['far_share_out'],
        'farS0_in_k': '%d/%d' % (m0['far_in_far'], m0['far_in_n']),
        'farS0_med_lo': m0['far_in_med_lo'], 'farS0_med_hi': m0['far_in_med_hi'],
        'farPts5mm': m0['far_pts5mm'],
        'farS1': m1['far_share'],
        'dc_ge1': round(dc_ge1, 4), 'dc_ge2': round(dc_ge2, 4), 'dc_all3': round(dc_all3, 4),
        'dc_pt01': round(dc_pt01, 4), 'dc_pt10': round(dc_pt10, 4),
        'lip': lip_n, 'lip_of': lip_tot,
        'bl0': bl0, 'bl1': bl1, 'bl0_short': bl0 < DOT_FLOOR,
        'mesh_flip': flip < 0,
    })
    wall = (walls or {}).get(P)
    if wall:
        row.update(pair_quality(S0, S1, nS0, nS1, wall))
    det = {'S0': m0, 'S1': m1}
    return row, det



COLS = ['piece', 'status', 'nS0', 'nS1', 'foldS0', 'foldS1', 'unionRim',
        'blindDeg', 'fireDots', 'seamArcDeg', 'seamArcPts', 'seamIn', 'seamOut',
        'seamGapIn', 'seamGapOut', 'arcInGap',
        'farS0', 'farS0_in', 'farS0_out', 'farS0_in_k', 'farS0_med_lo', 'farS0_med_hi',
        'farPts5mm', 'farS1', 'dc_ge1', 'dc_ge2', 'dc_all3', 'dc_pt01', 'dc_pt10',
        'lip', 'lip_of', 'bl0', 'bl1', 'bl0_short', 'mesh_flip',
        'med_nn', 'med_across', 'med_angle', 'wall_mm', 'pct_wall', 'genuine']


def load_walls(path):
    walls = {}
    if path and os.path.isdir(path):
        for j in glob.glob(os.path.join(path, '*_wall.json')):
            try:
                r = json.load(open(j, encoding='utf-8'))
                if r.get('thick_med_mm') is not None:
                    walls[r.get('piece', os.path.basename(j))] = float(r['thick_med_mm'])
            except Exception:
                pass
    return walls


def table(rows, cols=None):
    cols = cols or COLS
    lines = ['\t'.join(cols)]
    for r in rows:
        lines.append('\t'.join(str(r.get(c, '')) for c in cols))
    return '\n'.join(lines) + '\n'


def main():
    ap = argparse.ArgumentParser(description='read-only surface-separation audit (ticket 57)')
    ap.add_argument('--geom', required=True, help="run's out/geom directory")
    ap.add_argument('--mesh-dir', required=True, help='directory of <piece>_Mesh.obj')
    ap.add_argument('--pieces', default=','.join('Juglet_Piece_%d' % i for i in range(1, 10)))
    ap.add_argument('--walls', default=None, help='t54 wall40 dir (<piece>_wall.json)')
    ap.add_argument('--k', type=int, default=15, help='sample every k-th fold midpoint')
    ap.add_argument('--out-tsv', default=None)
    ap.add_argument('--out-json', default=None)
    # thresholds -- NOT invented here; the sweep table is what they will be read from
    ap.add_argument('--max-far-share', type=float, default=None,
                    help='fail if any piece far-skin share exceeds this')
    ap.add_argument('--max-dc-ge1', type=float, default=None)
    ap.add_argument('--max-blind-deg', type=float, default=None)
    ap.add_argument('--min-seam-in', type=float, default=None)
    ap.add_argument('--min-dots', type=int, default=None)
    ap.add_argument('--quiet', action='store_true')
    a = ap.parse_args()

    if not os.path.isdir(a.geom):
        print('[SEP57] FATAL no geom dir %s' % a.geom, file=sys.stderr)
        return 2
    walls = load_walls(a.walls)
    rows, detail = [], {}
    for P in a.pieces.split(','):
        try:
            row, det = piece_metrics(a.geom, a.mesh_dir, P, a.k, walls)
        except Exception as e:
            row, det = {'piece': P, 'status': 'ERROR: %s' % e}, {}
        rows.append(row)
        detail[P] = det
    txt = table(rows)
    if a.out_tsv:
        open(a.out_tsv, 'w', encoding='utf-8').write(txt)
    if a.out_json:
        json.dump({'geom': a.geom, 'mesh_dir': a.mesh_dir, 'k': a.k,
                   'definitions': 'ticket 57 frozen (2026-11-02)',
                   'pieces': detail}, open(a.out_json, 'w'), indent=1, default=str)
    if not a.quiet:
        print(txt)

    fails = []
    for r in rows:
        if r.get('status') != 'ok':
            fails.append('%s %s' % (r['piece'], r.get('status')))
            continue
        if a.max_far_share is not None and (r.get('farS0') or 0) > a.max_far_share:
            fails.append('%s farS0 %s > %s' % (r['piece'], r['farS0'], a.max_far_share))
        if a.max_dc_ge1 is not None and (r.get('dc_ge1') or 0) > a.max_dc_ge1:
            fails.append('%s dc_ge1 %s > %s' % (r['piece'], r['dc_ge1'], a.max_dc_ge1))
        if a.max_blind_deg is not None and (r.get('blindDeg') or 0) > a.max_blind_deg:
            fails.append('%s blindDeg %s > %s' % (r['piece'], r['blindDeg'], a.max_blind_deg))
        if a.min_seam_in is not None and r.get('seamIn') is not None and r['seamIn'] < a.min_seam_in:
            fails.append('%s seamIn %s < %s' % (r['piece'], r['seamIn'], a.min_seam_in))
        if a.min_dots is not None and (r.get('bl0') or 0) < a.min_dots:
            fails.append('%s bl0 %s < %s' % (r['piece'], r['bl0'], a.min_dots))
    if fails:
        print('[SEP57] THRESHOLD FAILURES (%d):' % len(fails), file=sys.stderr)
        for f in fails:
            print('  ' + f, file=sys.stderr)
        return 1
    if not a.quiet:
        print('[SEP57] no threshold given or all thresholds met')
    return 0


if __name__ == '__main__':
    sys.exit(main())
