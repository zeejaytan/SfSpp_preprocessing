#!/usr/bin/env python3
"""ticket 295 -- does the authors' own DS mesh end where THEIR line is, or where OURS is?

The one artefact neither release derived through our pipeline is the authors' DS mesh
(<Piece>_Mesh_DS.obj).  It is a surface reconstruction: its triangles stop somewhere, and the
open edge of that surface is a boundary loop.  A breakline that traces the sherd's break should
sit on that loop; a breakline drawn 3-12 mm inside it is a line on a face, not the edge of the
mesh's own surface.

Method, per piece, no thresholds invented here:
  * read the OBJ, build undirected edges; an edge used by exactly one triangle is a boundary edge
    (an edge of the reconstructed surface, not of a hole the reconstruction filled).
  * d_boundary(p) = exact point-to-segment distance to the nearest boundary edge (midpoint KD-tree
    prefilter k=40, exact distance to the candidate segments).
  * report it for the authors' breakline dots and for OUR rim (kept-material boundary points,
    100 deg mask, k=80 -- the same definition ticket 293 used for gap_share_gt108).
A line that lies on the loop comes back at a few hundredths of a millimetre; a line drawn inside
the mesh comes back at millimetres.  Both numbers are printed, so the reader can see whose line
the authors' own reconstruction ends at.
"""
import os, sys
import numpy as np
from scipy.spatial import cKDTree

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import p295_lib as L

PIECES = ["Pot_C_Piece_03", "Pot_D_Piece_22", "Pot_D_Piece_27", "Pot_E_Piece_16",
          "Pot_H_Piece_02", "Pot_H_Piece_10", "Pot_I_Piece_06", "Pot_I_Piece_13",
          "Pot_I_Piece_25"]
LANES = {"Pot_C_Piece_03": [1], "Pot_D_Piece_22": [0], "Pot_D_Piece_27": [0, 1],
         "Pot_E_Piece_16": [0], "Pot_H_Piece_02": [1], "Pot_H_Piece_10": [1],
         "Pot_I_Piece_06": [1], "Pot_I_Piece_13": [1], "Pot_I_Piece_25": [0, 1]}
DIAG = "/data/gpfs/projects/punim2657/SfSpp/runs/20261025-0456_3ada802_p293-census/out/diag"


def boundary_edges(V, idx):
    cnt = {}
    for t in idx:
        for a, b in ((t[0], t[1]), (t[1], t[2]), (t[2], t[0])):
            k = (a, b) if a < b else (b, a)
            cnt[k] = cnt.get(k, 0) + 1
    e = np.array([k for k, c in cnt.items() if c == 1], dtype=np.int64)
    return e


def point_seg_dist(P, A, B):
    """min over segments (A[i],B[i]) of distance from the single point P."""
    AB = B - A
    den = (AB * AB).sum(1)
    den[den == 0] = 1e-12
    t = ((P - A) * AB).sum(1) / den
    t = np.clip(t, 0.0, 1.0)
    Q = A + t[:, None] * AB
    return float(np.sqrt(((Q - P) ** 2).sum(1)).min())


def d_boundary(pts, V, e):
    if len(pts) == 0 or len(e) == 0:
        return np.full(len(pts), np.nan)
    A, B = V[e[:, 0]], V[e[:, 1]]
    ends = np.vstack([A, B])
    owner = np.concatenate([np.arange(len(e)), np.arange(len(e))])
    tr = cKDTree(ends)
    out = np.empty(len(pts))
    for i, p in enumerate(pts):
        _, ii = tr.query(p, k=min(40, len(ends)))
        ii = np.atleast_1d(ii)
        cand = np.unique(owner[ii])
        out[i] = point_seg_dist(p, A[cand], B[cand])
    return out


def main():
    rows = []
    for piece in PIECES:
        mp = os.path.join(L.CORP, "Mesh", piece + "_Mesh_DS.obj")
        V, idx = L.read_obj(mp)
        e = boundary_edges(V, idx)
        if len(e) == 0:
            # measured, not assumed: every edge of the authors' reconstructed surface is shared by
            # exactly two triangles, so the surface is CLOSED.  A closed surface has no boundary
            # loop, so "where does the authors' own mesh end" has no answer on this artefact and the
            # break is not a mesh boundary here.
            print("%s mesh V=%d T=%d CLOSED (no boundary edge): every edge is shared by exactly two "
                  "triangles" % (piece, len(V), len(idx)))
            rows.append([piece, "", 0, "", "", "", "", 0, "", "", "", "", 0, ""])
            continue
        blen = float(np.linalg.norm(V[e[:, 0]] - V[e[:, 1]], axis=1).sum())
        elen = np.linalg.norm(V[e[:, 0]] - V[e[:, 1]], axis=1)
        print("%s mesh V=%d T=%d boundary_edges=%d loop_len=%.2f edge_len_med=%.4f"
              % (piece, len(V), len(idx), len(e), blen, float(np.median(elen))))
        dump = os.path.join(DIAG, piece + ".diag276.txt")
        hdr, cl, labels, P = L.read_dump(dump)
        kept = L.kept_clusters(labels)
        km = np.isin(labels, kept)
        KP = P[km]
        Fedge = KP[L.boundary_mask(KP, L.GAP_DEG_100, 80)]
        for k in LANES[piece]:
            dot = os.path.join(L.CORP, "Breaklines", "%s_Breakline_%d.pcd" % (piece, k))
            BL = L.read_pcd_xyz(dot)[:, :3]
            dr = d_boundary(BL, V, e)
            # our rim, restricted to points near this lane's line (20 mm) so the number is local
            tl = cKDTree(BL)
            near = Fedge[tl.query(Fedge)[0] <= 20.0]
            drm = d_boundary(near, V, e) if len(near) else np.array([np.nan])
            rows.append([piece, k, len(BL), round(float(np.median(dr)), 4),
                         round(float(np.percentile(dr, 95)), 4), round(float(dr.max()), 4),
                         round(float(100.0 * (dr <= 2.0).mean()), 2),
                         len(near), round(float(np.median(drm)), 4),
                         round(float(np.percentile(drm, 95)), 4),
                         round(float(drm.max()), 4),
                         round(float(100.0 * (drm <= 2.0).mean()), 2),
                         len(e), round(blen, 2)])
    out = sys.argv[1] if len(sys.argv) > 1 else "outf_extra"
    os.makedirs(out, exist_ok=True)
    L.write_tsv(os.path.join(out, "meshrim.tsv"), rows,
                ["piece", "lane", "n_theirs", "their_d_bnd_med", "their_d_bnd_p95",
                 "their_d_bnd_max", "their_share_on_bnd", "n_our_rim", "our_d_bnd_med",
                 "our_d_bnd_p95", "our_d_bnd_max", "our_share_on_bnd",
                 "n_bnd_edges", "bnd_len_mm"])


main()
