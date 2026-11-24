#!/usr/bin/env python3
"""surface01.py -- Ticket 01: compare our Pot E 27/28 walls with the authors' walls in
the stored native scan frame, and render locked surface views.

Both sources are loaded only through the archived Ticket 03 loader
($SHIP/work/t03_lib.py:walls(stem, surfaces)), so the two walls pass the same code path
the axis estimator used.  No ICP, no estimated registration and no frame change: every
number is in the stored native coordinates (mm), which are the coordinates the axis
estimator consumes.

Outputs, all UTF-8 TSV with a header row:
  surfaces.tsv        same-face comparisons, both directions, both faces
  surface_crossed.tsv crossed-face comparisons (inner of one source vs outer of the other)
  surface_frame.tsv   per-cloud frame landmarks (frozen mesh, released pose/GT axis)
  renders_surface.tsv one row per PNG
"""
import argparse
import hashlib
import os
import sys

import numpy as np
from scipy.spatial import cKDTree, ConvexHull, QhullError
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D

COLS = ["piece", "face", "source", "path", "sha256", "points", "duplicate_xyz",
        "paired_1mm", "paired_2mm", "unpaired_1mm", "unpaired_2mm",
        "paired_fraction_1mm", "paired_fraction_2mm",
        "unpaired_fraction_1mm", "unpaired_fraction_2mm",
        "valid_normals", "invalid_normals",
        "distance_p50_mm", "distance_p95_mm", "spacing_p50_mm", "spacing_p95_mm",
        "normal_p50_deg", "normal_p95_deg", "normal_fraction_gt90",
        "own_only_cells", "author_only_cells", "shared_cells",
        "normal_unsigned_p50_deg", "normal_unsigned_p95_deg",
        "distance_max_mm", "cells_total", "note"]


def sha(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def unit(v):
    n = np.linalg.norm(v, axis=-1, keepdims=True)
    return v / np.where(n < 1e-12, 1.0, n)


def pct(v, q):
    return float(np.percentile(v, q)) if len(v) else None


def num(v, nd=6):
    return "" if v is None else ("%." + str(nd) + "f") % v


def read_T(p):
    a = np.loadtxt(p, ndmin=2)
    T = np.eye(4)
    T[0:3, 0:3] = a[0:3, 0:3]
    T[0:3, 3] = a[0:3, 3]
    return T


def apply_T(T, P):
    return P @ T[0:3, 0:3].T + T[0:3, 3]


def read_obj_vertices(p):
    out = []
    with open(p) as f:
        for ln in f:
            if ln[:2] == "v ":
                c = ln.split()
                out.append([float(c[1]), float(c[2]), float(c[3])])
    return np.asarray(out, dtype=float)


def cell_set(P, step=2.0):
    c = np.floor(P[:, 0:3] / step).astype(np.int64)
    return set(map(tuple, np.unique(c, axis=0).tolist()))


def measure(src, tgt):
    """Same-face comparison of a source cloud (6,N) against a target cloud (6,N)."""
    sp, sn = src[0:3].T, src[3:6].T
    tp, tn = tgt[0:3].T, tgt[3:6].T
    dist, idx = cKDTree(tp).query(sp, k=1)
    uniq = np.unique(sp, axis=0)
    rec = {"points": len(sp), "duplicate_xyz": len(sp) - len(uniq)}
    rec["paired_1mm"] = int((dist <= 1.0).sum())
    rec["paired_2mm"] = int((dist <= 2.0).sum())
    rec["unpaired_1mm"] = rec["points"] - rec["paired_1mm"]
    rec["unpaired_2mm"] = rec["points"] - rec["paired_2mm"]
    rec["paired_fraction_1mm"] = rec["paired_1mm"] / float(rec["points"])
    rec["paired_fraction_2mm"] = rec["paired_2mm"] / float(rec["points"])
    rec["unpaired_fraction_1mm"] = rec["unpaired_1mm"] / float(rec["points"])
    rec["unpaired_fraction_2mm"] = rec["unpaired_2mm"] / float(rec["points"])
    rec["distance_p50_mm"] = pct(dist, 50)
    rec["distance_p95_mm"] = pct(dist, 95)
    rec["distance_max_mm"] = float(dist.max())
    if len(uniq) > 1:
        dd = cKDTree(uniq).query(uniq, k=2)[0][:, 1]
        rec["spacing_p50_mm"] = pct(dd, 50)
        rec["spacing_p95_mm"] = pct(dd, 95)
    else:
        rec["spacing_p50_mm"] = rec["spacing_p95_mm"] = None
    m = dist <= 1.0
    ns, nt = sn[m], tn[idx[m]]
    ok = (np.isfinite(ns).all(axis=1) & np.isfinite(nt).all(axis=1)
          & (np.linalg.norm(ns, axis=1) > 1e-9) & (np.linalg.norm(nt, axis=1) > 1e-9))
    rec["valid_normals"] = int(ok.sum())
    rec["invalid_normals"] = int(len(ns) - ok.sum())
    if rec["valid_normals"]:
        ns, nt = unit(ns[ok]), unit(nt[ok])
        c = np.clip((ns * nt).sum(axis=1), -1.0, 1.0)
        ang = np.degrees(np.arccos(c))
        dv = tp[idx[m]][ok] - sp[m][ok]
        e = np.cross(ns, dv)
        en = np.linalg.norm(e, axis=1)
        u = np.zeros_like(e)
        nz = en > 1e-9
        u[nz] = e[nz] / en[nz, None]
        if (~nz).any():
            fb = np.cross(ns[~nz], np.array([0.0, 0.0, 1.0]))
            fn = np.linalg.norm(fb, axis=1)
            u[~nz] = np.where(fn[:, None] > 1e-9, fb / np.maximum(fn, 1e-12)[:, None],
                              np.array([0.0, 1.0, 0.0]))
        sgn = np.sign((np.cross(ns, nt) * u).sum(axis=1))
        sgn[sgn == 0] = 1.0
        signed = ang * sgn
        rec["normal_p50_deg"] = pct(signed, 50)
        rec["normal_p95_deg"] = pct(signed, 95)
        rec["normal_unsigned_p50_deg"] = pct(ang, 50)
        rec["normal_unsigned_p95_deg"] = pct(ang, 95)
        rec["normal_fraction_gt90"] = float((ang > 90.0).mean())
    else:
        for k in ("normal_p50_deg", "normal_p95_deg", "normal_unsigned_p50_deg",
                  "normal_unsigned_p95_deg", "normal_fraction_gt90"):
            rec[k] = None
    return rec


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", required=True)
    ap.add_argument("--fixed", required=True)
    ap.add_argument("--orig", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--renders", required=True)
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    os.makedirs(a.renders, exist_ok=True)
    if os.environ.get("SFS_SHIP"):
        sys.path.insert(0, os.environ["SFS_SHIP"])
    import t03_lib as L  # archived Ticket 03 loader

    stems = ["Pot_E_Piece_27", "Pot_E_Piece_28"]
    cloud, path, digest = {}, {}, {}
    for stem in stems:
        pot = L.pot_of(stem)
        own_dir = L.OWN[pot]
        own_paths = [os.path.join(own_dir, stem + ".S0"), os.path.join(own_dir, stem + ".S1")]
        _, c0p, c1p, _, _ = L.rb.get_piece_info(stem)
        auth_paths = [c0p, c1p]
        for src_name, paths in (("own", own_paths), ("authors", auth_paths)):
            for f in range(2):
                if not os.path.isfile(paths[f]):
                    sys.exit("surface01: missing %s" % paths[f])
                path[(stem, f, src_name)] = paths[f]
                digest[(stem, f, src_name)] = sha(paths[f])
        o0, o1, _ = L.walls(stem, "own")
        n0, n1, _ = L.walls(stem, "authors")
        cloud[(stem, 0, "own")], cloud[(stem, 1, "own")] = o0, o1
        cloud[(stem, 0, "authors")], cloud[(stem, 1, "authors")] = n0, n1
        for f in (0, 1):
            print("LOAD %s face %d own %s authors %s"
                  % (stem, f, cloud[(stem, f, "own")].shape,
                     cloud[(stem, f, "authors")].shape))

    # GT pose and released GT axis, used only as independent landmarks (never to fit).
    gt_T = {p: read_T(os.path.join(a.fixed, "Ground Truth", "Pot_E_Piece_%d_T.txt" % p))
            for p in (27, 28)}
    gt_axis = {}
    for p in (27, 28):
        q = os.path.join(a.orig, "Ground Truth Axes", "Pot_E_Piece_%d_Axis.xyz" % p)
        row = np.loadtxt(q, ndmin=2)[0]
        gt_axis[p] = (row[0:3].astype(float), unit(row[3:6].astype(float)))
    mesh = {p: read_obj_vertices(os.path.join(a.fixed, "Mesh",
                                             "Pot_E_Piece_%02d_Mesh_DS.obj" % p))
            for p in (27, 28)}

    load_rows = []
    for stem in stems:
        for fnum in (0, 1):
            for s in ("own", "authors"):
                q = path[(stem, fnum, s)]
                load_rows.append(dict(stem=stem, face=fnum, source=s, path=q,
                                      sha256=digest[(stem, fnum, s)],
                                      bytes=os.path.getsize(q),
                                      points=int(cloud[(stem, fnum, s)].shape[1]),
                                      dims="6 x %d" % cloud[(stem, fnum, s)].shape[1],
                                      estimator_input="yes",
                                      note=("own = Ticket 305 .S%d wall input to the axis "
                                            "estimator" % fnum) if s == "own" else
                                           ("authors = released Surface_%d" % fnum)))
    same_rows, cross_rows, frame_rows = [], [], []
    cells_face = {}
    for stem in stems:
        p = int(stem.split("_")[-1])
        for f in (0, 1):
            cells_face[(p, f)] = {s: cell_set(cloud[(stem, f, s)][0:3].T)
                                  for s in ("own", "authors")}
            own_c, aut_c = cells_face[(p, f)]["own"], cells_face[(p, f)]["authors"]
            shared = len(own_c & aut_c)
            for src_name, tgt_name in (("own", "authors"), ("authors", "own")):
                r = measure(cloud[(stem, f, src_name)], cloud[(stem, f, tgt_name)])
                r.update(piece=p, face=f, source=src_name,
                         path=path[(stem, f, src_name)],
                         sha256=digest[(stem, f, src_name)],
                         own_only_cells=len(own_c - aut_c),
                         author_only_cells=len(aut_c - own_c),
                         shared_cells=shared,
                         cells_total=len(own_c | aut_c),
                         note="native frame, no registration")
                same_rows.append(r)
        for sf, tf in ((0, 1), (1, 0)):
            for src_name, tgt_name in (("own", "authors"), ("authors", "own")):
                src = cloud[(stem, sf, src_name)]
                r = measure(src, cloud[(stem, tf, tgt_name)])
                other = cells_face[(p, tf)][tgt_name]
                mine = cell_set(src[0:3].T)
                r.update(piece=p, face=sf, target_face=tf,
                         source=src_name + "_face%d" % sf,
                         path=path[(stem, sf, src_name)],
                         sha256=digest[(stem, sf, src_name)],
                         own_only_cells=len(mine - other),
                         author_only_cells=len(other - mine),
                         shared_cells=len(mine & other),
                         cells_total=len(mine | other),
                         note="crossed face: source face %d vs target face %d" % (sf, tf))
                cross_rows.append(r)
        # frame landmarks per cloud
        for f in (0, 1):
            for src_name in ("own", "authors"):
                P = cloud[(stem, f, src_name)][0:3].T
                n_src = cloud[(stem, f, src_name)][3:6].T
                mu = P.mean(axis=0)
                lo, hi = P.min(axis=0), P.max(axis=0)
                dm, _ = cKDTree(mesh[p]).query(P, k=1)
                inside = np.all((P >= mesh[p].min(axis=0) - 2.0)
                                & (P <= mesh[p].max(axis=0) + 2.0), axis=1)
                av = gt_axis[p][0]
                ad = np.linalg.norm(np.cross(P - av, gt_axis[p][1]), axis=1)
                frame_rows.append(dict(
                    piece=p, face=f, source=src_name, path=path[(stem, f, src_name)],
                    sha256=digest[(stem, f, src_name)], points=len(P),
                    centroid_mm=" ".join("%.3f" % v for v in mu),
                    bbox_min_mm=" ".join("%.3f" % v for v in lo),
                    bbox_max_mm=" ".join("%.3f" % v for v in hi),
                    mesh_nn_p50_mm=pct(dm, 50), mesh_nn_p95_mm=pct(dm, 95),
                    mesh_bbox_inside_fraction=float(inside.mean()),
                    gt_axis_distance_p50_mm=pct(ad, 50),
                    gt_axis_distance_p95_mm=pct(ad, 95),
                    invalid_normals=int((~np.isfinite(n_src)).any(axis=1).sum())))
    for stem in stems:
        p = int(stem.split("_")[-1])
        for f in (0, 1):
            own_P = cloud[(stem, f, "own")][0:3].T
            aut_P = cloud[(stem, f, "authors")][0:3].T
            dmu = aut_P.mean(axis=0) - own_P.mean(axis=0)
            dbb = (aut_P.max(axis=0) + aut_P.min(axis=0)) / 2.0 \
                - (own_P.max(axis=0) + own_P.min(axis=0)) / 2.0
            for r in frame_rows:
                if r["piece"] == p and r["face"] == f:
                    r["centroid_delta_mm"] = float(np.linalg.norm(dmu))
                    r["bbox_centre_delta_mm"] = float(np.linalg.norm(dbb))

    def write(name, rows, cols):
        with open(os.path.join(a.out, name), "w", encoding="utf-8") as f:
            f.write("\t".join(cols) + "\n")
            for r in rows:
                f.write("\t".join(render_cell(r, c) for c in cols) + "\n")

    def render_cell(r, c):
        v = r.get(c, "")
        if v is None:
            return ""
        if isinstance(v, float):
            if c.startswith("paired_fraction") or "fraction" in c:
                return "%.6f" % v
            return "%.6f" % v
        return str(v)

    write("loads.tsv", load_rows, ["stem", "face", "source", "path", "sha256", "bytes",
                                   "points", "dims", "estimator_input", "note"])
    write("surfaces.tsv", same_rows, COLS)
    write("surface_crossed.tsv", cross_rows, COLS + ["target_face"])
    fcols = ["piece", "face", "source", "path", "sha256", "points", "centroid_mm",
             "bbox_min_mm", "bbox_max_mm", "centroid_delta_mm", "bbox_centre_delta_mm",
             "mesh_nn_p50_mm", "mesh_nn_p95_mm", "mesh_bbox_inside_fraction",
             "gt_axis_distance_p50_mm", "gt_axis_distance_p95_mm", "invalid_normals"]
    write("surface_frame.tsv", frame_rows, fcols)

    # ---------------- locked surface renders (no registration) ----------------
    rrows = []
    for stem in stems:
        p = int(stem.split("_")[-1])
        q = 55 - p  # the 27-28 partner
        ref = np.vstack([cloud[(stem, 0, "authors")][0:3].T,
                         cloud[(stem, 1, "authors")][0:3].T])
        nrm = np.vstack([cloud[(stem, 0, "authors")][3:6].T,
                         cloud[(stem, 1, "authors")][3:6].T])
        c = ref.mean(axis=0)
        e1 = unit(nrm.mean(axis=0))
        if np.linalg.norm(e1) < 0.5:
            e1 = unit(np.linalg.svd(ref - c)[2][0])
        u = np.linalg.svd(ref - c)[2].T
        e2 = u[:, 0] - (u[:, 0] @ e1) * e1
        if np.linalg.norm(e2) < 1e-6:
            e2 = u[:, 1] - (u[:, 1] @ e1) * e1
        e2 = unit(e2)
        e3 = np.cross(e1, e2)
        half = max(60.0, 0.55 * float(np.max(ref.max(axis=0) - ref.min(axis=0))) + 10.0)
        prj = lambda P: np.column_stack([(P - c) @ e2, (P - c) @ e3])

        partner = "Pot_E_Piece_%d" % q
        Tself, Tq = gt_T[p], gt_T[q]
        rel = np.linalg.inv(Tself) @ Tq
        pref = np.vstack([apply_T(rel, cloud[(partner, 0, "authors")][0:3].T),
                          apply_T(rel, cloud[(partner, 1, "authors")][0:3].T)])
        pc = pref.mean(axis=0)
        halfz = 30.0

        fig, axs = plt.subplots(1, 3, figsize=(25.0, 8.6))
        # two genuinely different views: along the mean normal, and along PC1
        for ax, (v1, v2, lab, xlab) in zip(
                axs[0:2],
                ((e2, e3, "along released mean normal", "released PCA axis 2"),
                 (e1, e3, "along released PC1", "released mean normal"))):
            pj = (lambda P, a1=v1, a2=v2:
                  np.column_stack([(P - c) @ a1, (P - c) @ a2]))
            mesh2 = pj(mesh[p])
            # the frozen mesh is the landmark the ticket asks for: dense enough to
            # read as a surface behind the clouds, faint enough not to hide them
            ax.scatter(mesh2[::3, 0], mesh2[::3, 1], s=16.0, c="#e0e0e0", alpha=1.0,
                       linewidths=0, rasterized=True, zorder=0,
                       label="frozen mesh (pale plate, every 3rd vertex)")
            # the plate is drawn under a dense cloud, so its extent is also traced:
            # the outline is the convex hull of the mesh vertices in this projection
            try:
                hv = ConvexHull(mesh2)
                hp = mesh2[np.append(hv.vertices, hv.vertices[0])]
                ax.plot(hp[:, 0], hp[:, 1], color="#8a8a8a", lw=1.3, zorder=2,
                        label="frozen mesh outline (convex hull)")
            except (QhullError, ValueError):
                pass
            for f in (0, 1):
                own = cloud[(stem, f, "own")]
                aut = cloud[(stem, f, "authors")]
                d, _ = cKDTree(aut[0:3].T).query(own[0:3].T, k=1)
                so = own[0:3].T[d > 1.0]
                sh = own[0:3].T[d <= 1.0]
                da, _ = cKDTree(own[0:3].T).query(aut[0:3].T, k=1)
                ao = aut[0:3].T[da > 1.0]
                for pts, col, mk in ((so, "C3", f), (ao, "C0", f), (sh, "0.62", f)):
                    if not len(pts):
                        continue
                    P2 = pj(pts)
                    lbl = None
                    if f == 0:
                        lbl = {"C3": "own-only (face 0)",
                               "C0": "authors-only (face 0)",
                               "0.62": "shared within 1 mm"}[col]
                    ax.scatter(P2[:, 0], P2[:, 1],
                               s=(11.0 if col != "0.62" else 1.6), marker="o",
                               facecolors=(col if mk == 0 else "none"),
                               edgecolors=("k" if col == "C3" else col) if mk == 0 else col,
                               linewidths=(0.6 if col == "C3" else 0.4) if mk == 0 else 0.6,
                               rasterized=True, zorder=(3 if col != "0.62" else 1),
                               label=lbl)
            pr = pj(ref)
            ax.set_xlim(pr[:, 0].mean() - half, pr[:, 0].mean() + half)
            ax.set_ylim(pr[:, 1].mean() - half, pr[:, 1].mean() + half)
            ax.set_aspect("equal")
            ax.set_xlabel("mm (%s)" % xlab)
            ax.set_ylabel("mm (released PCA axis 3)")
            ax.set_title("piece %d, view %s" % (p, lab))
            ax.legend(loc="lower right", fontsize=7.5, framealpha=0.75,
                      markerscale=0.9, borderpad=0.3)
            ax.plot([pr[:, 0].mean() - half + 6, pr[:, 0].mean() - half + 26],
                    [pr[:, 1].mean() - half + 8, pr[:, 1].mean() - half + 8], "k-", lw=3)
            ax.text(pr[:, 0].mean() - half + 6, pr[:, 1].mean() - half + 3, "20 mm",
                    fontsize=8)
        ax = axs[2]
        kdb = cKDTree(pref)
        band = {}
        for fn in (0, 1):
            own = cloud[(stem, fn, "own")]
            aut = cloud[(stem, fn, "authors")]
            band[(fn, "own")] = own[0:3].T[kdb.query(own[0:3].T, k=1)[0] <= 15.0]
            band[(fn, "authors")] = aut[0:3].T[kdb.query(aut[0:3].T, k=1)[0] <= 15.0]
        ob = np.vstack([band[(0, "own")], band[(1, "own")]])
        # the 3D bbox of the own band selects the mesh plate drawn behind the points;
        # panel limits must come from the PROJECTED points, or unmatched markers
        # outside the projected extent get clipped (piece 27 showed 1 of 4).
        lo3, hi3 = ob.min(axis=0) - 3.0, ob.max(axis=0) + 3.0
        mk = ((mesh2[:, 0] > lo3[0]) & (mesh2[:, 0] < hi3[0]) &
              (mesh2[:, 1] > lo3[1]) & (mesh2[:, 1] < hi3[1]))
        ax.scatter(mesh2[mk][::4, 0], mesh2[mk][::4, 1], s=12.0, c="#e6e6e6", alpha=1.0,
                   linewidths=0, rasterized=True, zorder=0,
                   label="frozen mesh (pale plate)")
        tip = prj(pref)
        ax.scatter(tip[::10, 0], tip[::10, 1], s=0.8, c="C2", alpha=0.35,
                   linewidths=0, rasterized=True,
                   label="piece %d reference placement (released GT pose)" % q)
        n_un = 0
        # limits from the own band only: the partner reference cloud is context and
        # would otherwise stretch the panel with empty space below the sherd
        flim = [prj(ob)]
        for fn in (0, 1):
            op, ap = band[(fn, "own")], band[(fn, "authors")]
            Q0 = prj(ap)
            ax.scatter(Q0[:, 0], Q0[:, 1], s=7.0, marker="o", facecolors="none",
                       edgecolors="C0", linewidths=0.5, alpha=0.9,
                       rasterized=True, zorder=1,
                       label=("authors-only in band" if fn == 0 else None))
            if len(op) and len(ap):
                d, idx = cKDTree(ap).query(op, k=1)
                un = d > 1.0
                n_un += int(un.sum())
                Q = prj(op[~un])
                ax.scatter(Q[:, 0], Q[:, 1], s=2.4, marker="o", facecolors="0.40",
                           edgecolors="none", rasterized=True, zorder=2)
                Q = prj(op[un])
                ax.scatter(Q[:, 0], Q[:, 1], s=42.0, marker="o", facecolors="C3",
                           edgecolors="k", linewidths=0.8, rasterized=True, zorder=3,
                           label=("own-only in band" if fn == 0 else None))
                for a_, b_ in zip(op[un], ap[idx[un]]):
                    sa, sb = prj(np.vstack([a_, b_]))
                    ax.plot([sa[0], sb[0]], [sa[1], sb[1]], "-", color="C3", lw=0.4,
                            alpha=0.7)
        fb = np.vstack(flim)
        lo2, hi2 = fb.min(axis=0) - 5.0, fb.max(axis=0) + 5.0
        ax.set_xlim(lo2[0], hi2[0])
        ax.set_ylim(lo2[1], hi2[1])
        ax.set_aspect("equal")
        ax.set_xlabel("mm (released PCA axis 2)")
        ax.set_ylabel("mm (released PCA axis 3)")
        ax.legend(loc="upper left", fontsize=6.5, framealpha=0.85, markerscale=0.7,
                  borderpad=0.3)
        ax.set_title("27-28 fracture-line band (15 mm): own vs authors, same face | "
                     "%d own-only points" % n_un, fontsize=10)
        fig.suptitle("piece %d surfaces, native scan frame, no registration | own vs authors, "
                     "grey = shared (<=1 mm), red = own-only, blue = authors-only, "
                     "filled = face 0, hollow = face 1" % p, fontsize=10)
        fig.text(0.005, 0.945, "locked camera from the released cloud only; 20 mm bar; "
                 "an eye check of the numbered comparison, not a measurement", fontsize=9,
                 color="darkred")
        # explicit margins: tight_layout cannot fit axes with aspect='equal'
        fig.subplots_adjust(left=0.05, right=0.985, top=0.855, bottom=0.155,
                            wspace=0.22)
        name = "surface_piece%d_views.png" % p
        fig.savefig(os.path.join(a.renders, name), dpi=110)
        plt.close(fig)
        cam = ("centre (%.1f,%.1f) half %.1f mm; seam band limits x %.1f..%.1f y %.1f..%.1f"
               % (prj(ref)[:, 0].mean(), prj(ref)[:, 1].mean(), half,
                  lo2[0], hi2[0], lo2[1], hi2[1]))
        rrows.append(dict(kind="surface", arm="-", repeat="-", piece=p,
                          path="renders/" + name, camera=cam, scale_bar_mm=20,
                          labels="filled=face0 hollow=face1 grey=shared red=own-only "
                                 "blue=authors-only"))
    with open(os.path.join(a.out, "renders_surface.tsv"), "w", encoding="utf-8") as f:
        f.write("kind\tarm\trepeat\tpiece\tpath\tcamera\tscale_bar_mm\tlabels\n")
        for r in rrows:
            f.write("\t".join(str(r[k]) for k in ("kind", "arm", "repeat", "piece",
                                                  "path", "camera", "scale_bar_mm",
                                                  "labels")) + "\n")
    print("SURFACE-OK rows=%d crossed=%d frame=%d renders=%d"
          % (len(same_rows), len(cross_rows), len(frame_rows), len(rrows)))


if __name__ == "__main__":
    main()
