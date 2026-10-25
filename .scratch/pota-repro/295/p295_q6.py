#!/usr/bin/env python3
"""ticket 295, Q6 (C6) -- Pot E 16 Bl0 and Pot H 02 both lanes.

Two new readings from the conservator (2026-10-25):
  Q6a Pot E 16 Bl0: "our edgeline fits better than the reference".
  Q6b Pot H 02 both lanes: "our edgelines stopped at the dish's base-rim -- a sharp turn of the
      pottery -- but that is not the end of that surface"; he still judges ours slightly better.

The decisive question for Q6b is what the material immediately past our line IS: a steep fracture
facet (our line is right, the reference ran onto the break) or the dish's own face continuing
across a shallow crease or a small scan gap (the reference is the more complete edge and our line
stops short).  Measured here, no threshold invented beyond the ones pre-registered in
p295_lanes.py (T_BAR 2.0, T_EDGE 100, T_TILT 45, T_BAND 2.0/T4b 4.0, T_MAT 0.5, corner-ring 1.0
sample spacing per ticket 278):

  A  where the reference lies relative to OUR kept face: distance to material, distance to the
     material's >100 deg edge, share within 1.0 mm of that edge, and the nearest-label shares
     (kept / dropped / unclustered) taken over every dump point.
  B  where our material's edge lies relative to the reference and to the reference's own surface
     boundary (our line geometry is deleted -- out/geom was removed after ticket 293 -- so the
     material edge stands in for our line, which 293 measured as riding that edge at 0.98 mm with
     a 0.40-0.46 mm ring; stated as a substitution, never as our line).
  C  the face test on the stretch corridor with a HISTOGRAM of normal disagreement (not a mean)
     against the authors' own supplied normals, and the perpendicular spread.
  D  continuity of the sampling: label histogram of all dump points in the corridor, and the
     ticket-278 corner-ring test -- do unclustered points sit within one sample spacing of both
     the kept material and the non-kept material next to it (a labelling split of continuous
     material), or is the gap empty (a physical gap in the sampling)?
  E  what lies immediately past our material's edge in the stretch: a plane fit on each side and
     the fold angle between them, plus the counts.  A steep fracture facet gives a large fold
     angle; the same face continuing gives a small one.
"""
import os, sys, json
import numpy as np
from scipy.spatial import cKDTree

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import p295_lib as L

DIAG = "/data/gpfs/projects/punim2657/SfSpp/runs/20261025-0456_3ada802_p293-census/out/diag"
LANES = [("Pot_E_Piece_16", 0), ("Pot_H_Piece_02", 0), ("Pot_H_Piece_02", 1)]
T_BAR, T_EDGE, T_TILT, T_BAND, T_BAND2, T_MAT = 2.0, 100.0, 45.0, 2.0, 4.0, 0.5


def nn_spacing(Q, tree=None, k=8):
    tr = tree if tree is not None else cKDTree(Q)
    d, _ = tr.query(Q, k=k)
    return float(np.median(d[:, 1:]))


def longest_run(mask):
    best = (0, 0, 0)
    i = 0
    n = len(mask)
    while i < n:
        if mask[i]:
            j = i
            while j + 1 < n and mask[j + 1]:
                j += 1
            if j - i + 1 > best[0]:
                best = (j - i + 1, i, j)
            i = j + 1
        else:
            i += 1
    return best


def plane_normals(Q):
    c = Q - Q.mean(0)
    u, s, vt = np.linalg.svd(c, full_matrices=False)
    return vt[2], float(np.sqrt((s[2] ** 2) / max(len(Q), 1)))


def fold_angle(A, B):
    na, _ = plane_normals(A)
    nb, _ = plane_normals(B)
    c = abs(float(np.dot(na, nb)))
    return float(np.degrees(np.arccos(min(1.0, c))))


def lane(piece, k):
    hdr, cl, labels, P = L.read_dump(os.path.join(DIAG, piece + ".diag276.txt"))
    kept = L.kept_clusters(labels)
    km = np.isin(labels, kept)
    KP = P[km]
    treeP = cKDTree(P)
    treeK = cKDTree(KP)
    _bg, bmask = L.boundary_mask(KP, L.GAP_DEG_100, 80)
    Fedge = KP[bmask]
    treeF = cKDTree(Fedge)

    p0, w, u, v2 = L.frame(os.path.join(L.CORP, "Axes", piece + "_Axis.xyz"))

    SP = [L.read_xyz6(os.path.join(L.CORP, "Surfaces", "%s_Surface_%d.xyz" % (piece, i)))
          for i in (0, 1)]
    S = [a for a, b in SP]
    BL = L.read_pcd_xyz(os.path.join(L.CORP, "Breaklines", "%s_Breakline_%d.pcd" % (piece, k)))[:, :3]
    Ns = [b for a, b in SP]
    dS = [np.median(cKDTree(a).query(BL)[0]) for a in S]
    rides = int(np.argmin(dS))
    Sride = S[rides]
    Nride = Ns[rides]
    treeS = cKDTree(Sride)
    margin = float(min(dS[(rides + 1) % 2], 99.0) - dS[rides]) if dS[(rides + 1) % 2] < 99 else float(abs(dS[0] - dS[1]))

    # --- A: reference relative to our kept face
    d_kept, _ = treeK.query(BL)
    d_rim, _ = treeF.query(BL)
    nl = labels[treeP.query(BL)[1]]
    lab_share = {}
    for c in sorted(set(labels.tolist())):
        share = float(100.0 * (nl == c).mean())
        if share > 0:
            lab_share[int(c)] = round(share, 2)
    on_edge = float(100.0 * (d_rim <= 1.0).mean())

    # --- corridor (stretch) definition: longest run of reference dots > T_BAR from our material edge
    run = longest_run(d_rim > T_BAR)
    if run[0] >= 3:
        i0, i1 = run[1], run[2]
        sd = BL[i0:i1 + 1]
        stretch_arc = float(L.polyline_length(sd))
    else:
        i0 = i1 = 0
        sd = BL
        stretch_arc = float(L.polyline_length(BL))
    cen = sd.mean(0)
    dsd = cKDTree(sd)   # locality is measured to the reference segment itself, never to its
                        # centroid: a whole closed loop's centroid falls off the material entirely.
    near_ref = lambda Q: dsd.query(Q)[0]

    # --- B: our material edge vs the reference and vs their surface boundary
    near = Fedge[near_ref(Fedge) <= 20.0]
    treeB = cKDTree(BL)
    rim_d_ref = treeB.query(near)[0] if len(near) else np.array([np.nan])
    _sg, sb_mask = L.boundary_mask(Sride, L.GAP_DEG_100, 80)
    Sedge = Sride[sb_mask]
    treeSedge = cKDTree(Sedge) if len(Sedge) else None
    rim_d_their_edge = (treeSedge.query(near)[0] if (treeSedge is not None and len(near))
                        else np.array([np.nan]))

    # --- C: face test on the corridor, histogram not mean
    d_kp_ref = near_ref(KP)
    band_r = T_BAND
    if int((d_kp_ref <= T_BAND).sum()) < 30:
        band_r = T_BAND2
    Nour = L.local_normals(KP, treeK, 20)
    Nmap = dict()
    nrm = np.full((len(KP), 3), np.nan)
    idx_all = np.arange(len(KP))
    dq, iq = treeS.query(KP)
    nrm[idx_all] = Nride[iq]
    ok = np.isfinite(nrm[:, 0])
    ang = np.degrees(np.arccos(np.clip(np.abs((Nour * nrm).sum(1)), 0.0, 1.0)))
    sel = d_kp_ref <= band_r
    a_sel = ang[sel & ok]
    sgn = ((KP - Sride[iq]) * nrm).sum(1)
    s_sel = np.abs(sgn[sel & ok])

    # --- D: continuity -- labels of every dump point in the corridor, and the corner-ring test
    dall = near_ref(P)
    inc = dall <= T_BAND
    labs = labels[inc]
    sp = nn_spacing(KP, treeK)
    unk = inc & (labels == -1)
    bridge = 0
    if unk.any():
        du, _ = treeK.query(P[unk])
        bridge = int((du <= 1.0 * sp).sum())
    # empty-gap check: nearest non-kept dump point to the kept material inside the corridor
    nonkept = inc & (~np.isin(labels, kept))
    empty = float("nan")
    if nonkept.any():
        empty = float(np.percentile(treeK.query(P[nonkept])[0], 50))

    # --- E: what lies immediately past our material edge in the stretch
    # E -- what lies IMMEDIATELY past our material's edge near the stretch: non-kept dump points
    # within 2.0 mm of a rim point, each compared with our face's own local normal at that rim point.
    # A steep fracture facet puts those normals tens of degrees off; continuous material keeps them
    # on the same face.
    near = Fedge[near_ref(Fedge) <= 20.0]
    oth_ang = np.array([])
    E_n_our = 0
    E_n_other = 0
    fold = float("nan")
    if len(near):
        Nour_all = L.local_normals(KP, treeK, 20)
        rim_id = np.flatnonzero(np.isin(KP, near).all(1))
        d_rp = cKDTree(near).query(P)[0]
        oth = (~np.isin(labels, kept)) & (d_rp <= 2.0)
        E_n_other = int(oth.sum())
        E_n_our = int(len(near))
        if E_n_other:
            NP = L.local_normals(P, treeP, 20)
            _, ir = cKDTree(near).query(P[oth])
            nB = NP[oth]
            ok2 = np.isfinite(nB[:, 0]) & np.isfinite(Nour_all[ir][:, 0])
            angE = np.degrees(np.arccos(np.clip(
                np.abs((nB[ok2] * Nour_all[ir][ok2]).sum(1)), 0.0, 1.0)))
            oth_ang = angE
            if len(near) >= 30 and int(oth.sum()) >= 30:
                fold = fold_angle(near, P[oth])

    med = lambda a: float(np.median(a)) if len(a) else float("nan")
    p95 = lambda a: float(np.percentile(a, 95)) if len(a) else float("nan")
    sh = lambda a, f: round(float(100.0 * f(a).mean()), 2) if len(a) else float("nan")
    row = dict(
        piece=piece, lane="Bl%d" % k, n_theirs=len(BL), arc_theirs=round(float(L.polyline_length(BL)), 3),
        rides="authS%d" % rides, ride_d=round(float(dS[rides]), 4), ride_margin=round(margin, 4),
        A_d_kept_med=round(float(np.median(d_kept)), 4),
        A_d_kept_p95=round(float(np.percentile(d_kept, 95)), 4),
        A_d_kept_max=round(float(d_kept.max()), 4),
        A_d_rim_med=round(float(np.median(d_rim)), 4),
        A_d_rim_p95=round(float(np.percentile(d_rim, 95)), 4),
        A_share_on_our_edge_1mm=round(on_edge, 2),
        A_near_labels=json.dumps(lab_share),
        stretch_n=int(i1 - i0 + 1), stretch_arc=round(stretch_arc, 3),
        B_rim_d_ref_med=round(float(np.nanmedian(rim_d_ref)), 4),
        B_rim_d_ref_p95=round(float(np.nanpercentile(rim_d_ref, 95)), 4),
        B_rim_share_within_2=round(float(100.0 * np.nanmean(rim_d_ref <= 2.0)), 2),
        B_rim_d_their_edge_med=round(float(np.nanmedian(rim_d_their_edge)), 4),
        B_rim_share_on_their_edge=round(float(100.0 * np.nanmean(rim_d_their_edge <= 1.0)), 2),
        C_n=int(len(a_sel)), C_band_r=band_r,
        C_ang_med=round(med(a_sel), 3),
        C_share_lt10=sh(a_sel, lambda a: a < 10),
        C_share_10_20=sh(a_sel, lambda a: (a >= 10) & (a < 20)),
        C_share_20_30=sh(a_sel, lambda a: (a >= 20) & (a < 30)),
        C_share_30_45=sh(a_sel, lambda a: (a >= 30) & (a < 45)),
        C_share_gt45=sh(a_sel, lambda a: a > T_TILT),
        C_s_med=round(med(s_sel), 4),
        C_s_p95=round(p95(s_sel), 4),
        C_share_s_gt03=sh(s_sel, lambda a: a > 0.3),
        D_spacing=round(sp, 4),
        D_corridor_pts=int(inc.sum()),
        D_labels=json.dumps({str(c): int((labs == c).sum()) for c in sorted(set(labs.tolist()))}),
        D_bridge_unk_within_1sp=bridge,
        D_nonkept_med_dist_to_kept=round(empty, 4),
        E_n_our=E_n_our, E_n_other=E_n_other,
        E_fold_deg=round(fold, 3) if np.isfinite(fold) else float("nan"),
        E_other_ang_med=round(med(oth_ang), 3),
        E_other_share_lt10=sh(oth_ang, lambda a: a < 10),
        E_other_share_10_30=sh(oth_ang, lambda a: (a >= 10) & (a < 30)),
        E_other_share_30_45=sh(oth_ang, lambda a: (a >= 30) & (a < 45)),
        E_other_share_gt45=sh(oth_ang, lambda a: a >= 45),
    )
    return row


def main():
    out = sys.argv[1] if len(sys.argv) > 1 else "outf_q6"
    os.makedirs(out, exist_ok=True)
    rows = [lane(p, k) for p, k in LANES]
    L.write_tsv(os.path.join(out, "q6.tsv"), rows, list(rows[0].keys()))
    for r in rows:
        print(json.dumps(r, indent=1))


main()
