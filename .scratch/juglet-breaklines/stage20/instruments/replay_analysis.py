#!/usr/bin/env python3
"""Ticket 20 analysis: replay the paper chain offline against the harvested
segmentation inputs, measure the meshes directly, and render the two clusters
of a fusing piece and of a working control.

Nothing here is a verdict. Every row is a measured quantity with the file it
came from; the lead marks supported/refuted.

Replays (mesh_processing_headless.cpp):
  growPaper234            :1725-1783   (seed order, BFS, nb, theta, kappa)
  mergePaper234           :1929-1984   (k1 boundary, pca axes, pass loop)
  tryMergePair234         :1861-1927   (rhoD/rhoN/rhoC/rhoInN/rhoInC)
  classifyAndOrderPaper234:2004-2049   (axis-ray interior fraction, satA/satB)

usage:
  replay_analysis.py --runs-root RUNS --stamp STAMP --out DIR \
                     --dset DATASET --corpus CORPUS --variables VARIANTS_TSV
"""
import argparse
import glob
import json
import math
import os
import re
import sys

import numpy as np

NP_PIECES = ["Juglet_Piece_2", "Juglet_Piece_3", "Juglet_Piece_4", "Juglet_Piece_5",
             "Juglet_Piece_7", "Juglet_Piece_8", "Juglet_Piece_9", "Pot_A_Piece_07"]
RENDER_PIECES = ["Juglet_Piece_3", "Pot_A_Piece_07"]
PAPER = dict(theta=3.4, kappa=1.0, nb=10, rhoD=1.0, rhoN=0.95, rhoC=0.1,
             rhoInN=0.75, rhoInC=0.25, k1=10, k2=30)


def log(*a):
    print(*a, flush=True)


# ---------------------------------------------------------------- PLY reading
def load_ply(path):
    """ASCII PLY as PLYWriter wrote pcl::PointNormal: x y z nx ny nz curvature.

    A second element ("camera") follows the vertices; its properties are not
    collected, so the vertex column indices stay the vertex ones.
    """
    props, nvert, body, in_v, el = [], 0, [], False, None
    with open(path, "r") as fh:
        for ln in fh:
            s = ln.split()
            if not s:
                continue
            k = s[0]
            if k == "end_header":
                in_v = True
                continue
            if not in_v:
                if k == "element":
                    el = s[1]
                    if el == "vertex":
                        nvert = int(s[2])
                elif k == "property" and el == "vertex":
                    props.append("__list__" if s[1] == "list" else s[-1])
                continue
            body.append(s)
    arr = np.asarray([[float(x) for x in row] for row in body[:nvert]], dtype=float)
    ix = {nm: i for i, nm in enumerate(props)}

    def pick(*names):
        for nm in names:
            if nm in ix:
                return arr[:, ix[nm]]
        raise KeyError("none of %s in %s" % (names, props))

    pts = np.stack([pick("x"), pick("y"), pick("z")], axis=1)
    nrm = np.stack([pick("nx", "normal_x"), pick("ny", "normal_y"), pick("nz", "normal_z")], axis=1)
    curv = pick("curvature") if "curvature" in ix else np.zeros(len(pts))
    return pts, nrm, curv, props


def find_axis(root, corpus, piece):
    """The axis the pipeline was given for this piece: boot bundle, PotSAC file, or the released one."""
    for c in (os.path.join(root, "boot", piece + "_boot_Axis.xyz"),
              os.path.join(root, "axes", piece + "_Axis.xyz"),
              os.path.join(corpus, "Axes", piece + "_Axis.xyz"),
              os.path.join(corpus, "Axes", piece.split("_")[0], piece + "_Axis.xyz")):
        if os.path.exists(c):
            return c
    return None


def read_axis(path):
    vals = [float(x) for x in open(path).read().split()[:6]]
    return np.asarray(vals[:3]), np.asarray(vals[3:6])


# ------------------------------------------------------------------- replays
def grow(pts, nrm, curv, nb, theta, kappa, dynmin, convention):
    from scipy.spatial import cKDTree
    n = len(pts)
    tree = cKDTree(pts)
    order = np.argsort(curv, kind="stable")
    claimed = np.zeros(n, dtype=bool)
    out = []
    for sd in order:
        if claimed[sd]:
            continue
        claimed[sd] = True
        reg, front, fi = [sd], [sd], 0
        while fi < len(front):
            cf = front[fi]
            fi += 1
            k = min(nb + 1, n)
            _d, idx = tree.query(pts[cf], k=k)
            cur = nrm[cf]
            for cand in np.atleast_1d(idx):
                cand = int(cand)
                if cand == cf or claimed[cand]:
                    continue
                if curv[cand] >= kappa:
                    continue
                dot = float(np.dot(cur, nrm[cand]))
                if convention == "abs":
                    ang = math.degrees(math.acos(min(1.0, abs(dot))))
                else:
                    ang = math.degrees(math.acos(max(-1.0, min(1.0, dot))))
                if ang > theta:
                    continue
                claimed[cand] = True
                reg.append(cand)
                front.append(cand)
        if len(reg) >= dynmin:
            out.append(reg)
    out.sort(key=len, reverse=True)
    return out


def mean_normal(idx, nrm):
    m = nrm[idx].sum(axis=0)
    ln = np.linalg.norm(m)
    return m / ln if ln > 1e-9 else np.array([0.0, 0.0, 1.0])


def pca_axis(pts, idx):
    p = pts[idx]
    c = p.mean(axis=0)
    cov = (p - c).T @ (p - c)
    w, v = np.linalg.eigh(cov)
    return v[:, -1]


def median_internal(pts, idx, axis):
    if not len(idx):
        return -1
    p = pts[idx]
    m = p.mean(axis=0)
    an = axis / (np.linalg.norm(axis) + 1e-30)
    w = p - m
    along = w @ an
    perp = np.linalg.norm(w - np.outer(along, an), axis=1)
    order = np.argsort(perp, kind="stable")
    return int(idx[order[len(idx) // 2]])


def k2_avg_normal(pts, nrm, cidx, qid, k2):
    from scipy.spatial import cKDTree
    if not len(cidx) or k2 <= 0:
        return np.array([0.0, 0.0, 1.0])
    K = min(k2, len(cidx))
    _d, rr = cKDTree(pts[cidx]).query(pts[qid], k=K)
    rr = np.atleast_1d(rr)
    m = nrm[np.asarray(cidx)[rr]].sum(axis=0)
    ln = np.linalg.norm(m)
    return m / ln if ln > 1e-9 else np.array([0.0, 0.0, 1.0])


def is_boundary(pts, member, k1):
    from scipy.spatial import cKDTree
    n = len(pts)
    bnd = np.zeros(n, dtype=bool)
    K = min(k1 + 1, n)
    _d, idx = cKDTree(pts).query(pts, k=K)
    for p in range(n):
        if member[p] < 0:
            continue
        for q in np.atleast_1d(idx[p]):
            q = int(q)
            if q == p:
                continue
            if member[q] != member[p]:
                bnd[p] = True
                break
    return bnd


def try_merge_pair(pts, nrm, curv, A, B, bnd, axisA, axisB, cfg):
    """Returns (fires, detail dict) -- faithful to tryMergePair234:1861-1927."""
    from scipy.spatial import cKDTree
    d = dict(nA=len(A), nB=len(B), step="ok", pairs=0,
             pairDistMin=float("nan"), pairDistMed=float("nan"),
             dot_sNA_sNB=float("nan"), curvA=float("nan"), curvB=float("nan"),
             dCurv=float("nan"), dot_internal=float("nan"), dCurvInternal=float("nan"))
    if len(A) == 0 or len(B) == 0:
        d["step"] = "empty"
        return False, d
    bA = [i for i in A if bnd[i]]
    bB = [i for i in B if bnd[i]]
    d["bA"] = len(bA)
    d["bB"] = len(bB)
    if not bA or not bB:
        d["step"] = "no-boundary"
        return False, d
    if len(bA) > len(bB):
        sP, lP, sIsA = bB, bA, False
    else:
        sP, lP, sIsA = bA, bB, True
    ltree = cKDTree(pts[lP])
    pairs = []
    for sid in sP:
        if len(pairs) >= 200:
            break
        dist, pos = ltree.query(pts[sid], k=1)
        if dist * dist <= cfg["rhoD"] * cfg["rhoD"]:
            lid = lP[int(pos)]
            a, b = (sid, lid) if sIsA else (lid, sid)
            pairs.append((a, b, dist))
    d["pairs"] = len(pairs)
    if len(pairs) < 3:
        d["step"] = "too-few-pairs"
        return False, d
    dd = np.array([p[2] for p in pairs])
    d["pairDistMin"] = float(dd.min())
    d["pairDistMed"] = float(np.median(dd))
    sNA = np.zeros(3)
    sNB = np.zeros(3)
    sCA = sCB = 0.0
    for a, b, _dist in pairs:
        sNA += k2_avg_normal(pts, nrm, A, a, cfg["k2"])
        sNB += k2_avg_normal(pts, nrm, B, b, cfg["k2"])
        sCA += curv[a]
        sCB += curv[b]
    nA, nB = np.linalg.norm(sNA), np.linalg.norm(sNB)
    if nA < 1e-9 or nB < 1e-9:
        d["step"] = "zero-normal"
        return False, d
    sNA, sNB = sNA / nA, sNB / nB
    d["dot_sNA_sNB"] = float(np.dot(sNA, sNB))
    d["curvA"] = sCA / len(pairs)
    d["curvB"] = sCB / len(pairs)
    d["dCurv"] = abs(d["curvA"] - d["curvB"])
    if d["dot_sNA_sNB"] < cfg["rhoN"]:
        d["step"] = "rhoN"
        return False, d
    if d["dCurv"] >= cfg["rhoC"]:
        d["step"] = "rhoC"
        return False, d
    ia = median_internal(pts, A, axisA)
    ib = median_internal(pts, B, axisB)
    if ia < 0 or ib < 0:
        d["step"] = "no-internal"
        return False, d
    na, nb = nrm[ia], nrm[ib]
    la, lb = np.linalg.norm(na), np.linalg.norm(nb)
    if la < 1e-9 or lb < 1e-9:
        d["step"] = "zero-internal-normal"
        return False, d
    d["dot_internal"] = float(np.dot(na, nb) / (la * lb))
    d["dCurvInternal"] = abs(float(curv[ia] - curv[ib]))
    d["ia"] = ia
    d["ib"] = ib
    if d["dot_internal"] < cfg["rhoInN"]:
        d["step"] = "rhoInN"
        return False, d
    if d["dCurvInternal"] >= cfg["rhoInC"]:
        d["step"] = "rhoInC"
        return False, d
    return True, d


def merge(pts, nrm, curv, clusters, cfg, trace):
    clusters = [list(c) for c in clusters]
    n = len(pts)
    p = 0
    any_ = True
    while any_:
        any_ = False
        p += 1
        member = np.full(n, -1, dtype=int)
        for ci, c in enumerate(clusters):
            member[c] = ci
        bnd = is_boundary(pts, member, cfg["k1"])
        axes = [pca_axis(pts, np.asarray(c)) for c in clusters]
        dead = [False] * len(clusters)
        for i in range(len(clusters)):
            if dead[i]:
                continue
            for j in range(i + 1, len(clusters)):
                if dead[j]:
                    continue
                fires, d = try_merge_pair(pts, nrm, curv, clusters[i], clusters[j],
                                          bnd, axes[i], axes[j], cfg)
                d.update(pass_=p, i=i, j=j, fired=bool(fires))
                trace.append(d)
                if fires:
                    clusters[i] = clusters[i] + clusters[j]
                    dead[j] = True
                    any_ = True
        if any_:
            clusters = [c for k, c in enumerate(clusters) if not dead[k]]
        if p > 25:
            break
    clusters.sort(key=len, reverse=True)
    return clusters, p


def classify(pts, nrm, clusters, axis_pt, axis_dir):
    """Returns inFrac, satA, satB, swap and the per-cluster cos statistics."""
    if len(clusters) < 2:
        return None
    a = axis_dir / np.linalg.norm(axis_dir)
    res = []
    for f in range(2):
        idx = np.asarray(clusters[f])
        pp = pts[idx]
        nn = nrm[idx]
        w = pp - axis_pt
        t = w @ a
        cp = axis_pt + np.outer(t, a)
        v = cp - pp
        cos = np.einsum("ij,ij->i", v, nn) / (np.linalg.norm(v, axis=1) * np.linalg.norm(nn, axis=1) + 1e-30)
        res.append(dict(n=len(idx), interior_frac=float((cos > 0).sum()) / len(idx),
                        cos_med=float(np.median(cos)),
                        frac_abs_gt_0p9=float((np.abs(cos) > 0.9).mean()),
                        frac_cos_gt_0=float((cos > 0).mean()),
                        cos=cos))
    n0, n1 = res[0]["n"], res[1]["n"]
    satA = res[0]["interior_frac"] * n0 + (1 - res[1]["interior_frac"]) * n1
    satB = (1 - res[0]["interior_frac"]) * n0 + res[1]["interior_frac"] * n1
    res[0].pop("cos")
    res[1].pop("cos")
    return dict(face=res, satA=satA, satB=satB, swap=bool(satB > satA))


# ------------------------------------------------------------------ mesh work
def mesh_measure(mesh_path, pts, nrm, nmax=800):
    import trimesh
    from trimesh.ray.ray_triangle import RayMeshIntersector
    m = trimesh.load(mesh_path, process=False)
    out = dict(mesh=mesh_path, vertices=int(len(m.vertices)),
               faces=int(len(m.faces)), area_mm2=float(m.area),
               watertight=bool(getattr(m, "is_watertight", False)),
               bounds_mm=[float(x) for x in (m.bounds[1] - m.bounds[0])])
    step = max(1, len(pts) // nmax)
    p = pts[::step]
    nn = nrm[::step]
    ln = np.linalg.norm(nn, axis=1)
    ok = ln > 1e-9
    p, nn = p[ok], nn[ok] / ln[ok][:, None]
    inter = RayMeshIntersector(m)
    origins = p + nn * 1e-3
    loc, ray_id, _tri = inter.intersects_location(origins, -nn, multiple_hits=False)
    thick = np.full(len(p), np.nan)
    if len(loc):
        dist = np.linalg.norm(loc - origins[ray_id], axis=1)
        keep = dist > 0.15
        thick[ray_id[keep]] = dist[keep]
    good = thick[~np.isnan(thick)]
    out["rays"] = int(len(p))
    out["ray_hits"] = int(len(good))
    if len(good):
        out["thick_med_mm"] = float(np.median(good))
        out["thick_p10_mm"] = float(np.percentile(good, 10))
        out["thick_p90_mm"] = float(np.percentile(good, 90))
        out["thick_frac_1to3mm"] = float(((good >= 1.0) & (good <= 3.0)).mean())
    loc2, ray2, _t2 = inter.intersects_location(origins, -nn, multiple_hits=True)
    counts = np.bincount(ray2, minlength=len(p)) if len(ray2) else np.zeros(len(p), int)
    out["hits_per_ray_med"] = float(np.median(counts)) if len(counts) else 0.0
    out["hits_per_ray_max"] = int(counts.max()) if len(counts) else 0
    return out


def normal_density_test(pts, nmax=1500):
    """How far a 5-NN PCA normal sits from a 20-NN PCA normal on this cloud."""
    from scipy.spatial import cKDTree
    n = len(pts)
    t = cKDTree(pts)
    step = max(1, n // nmax)
    q = np.arange(0, n, step)

    def pca_normals(k):
        _d, idx = t.query(pts[q], k=k)
        out = np.zeros((len(q), 3))
        for r in range(len(q)):
            P = pts[idx[r]]
            c = P.mean(axis=0)
            w, v = np.linalg.eigh((P - c).T @ (P - c))
            out[r] = v[:, 0]
        return out
    n5 = pca_normals(5)
    n20 = pca_normals(20)
    dots = np.abs(np.einsum("ij,ij->i", n5, n20))
    ang = np.degrees(np.arccos(np.clip(dots, -1, 1)))
    return dict(points=int(len(q)), angle_med=float(np.median(ang)),
                angle_p90=float(np.percentile(ang, 90)),
                frac_gt30=float((ang > 30).mean()),
                frac_gt60=float((ang > 60).mean()))


# ------------------------------------------------------------------- renders
def render(piece, pts, clusters, axis_pt, axis_dir, png, caption_lines):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    a = axis_dir / np.linalg.norm(axis_dir)
    cA = pts[np.asarray(clusters[0])].mean(axis=0)
    m = cA - axis_pt
    u = m - (m @ a) * a
    u /= np.linalg.norm(u)
    w = pts - axis_pt
    z = w @ a
    s = w @ u
    lab = np.full(len(pts), -1)
    for ci, c in enumerate(clusters[:2]):
        lab[np.asarray(c)] = ci
    fig, ax = plt.subplots(1, 3, figsize=(15, 5), dpi=150)
    lim = dict(x0=float(z.min()), x1=float(z.max()), y0=float(s.min()), y1=float(s.max()))
    for k, (axi, ttl) in enumerate([(ax[0], "full side view"), (ax[1], "zoom on the two clusters")]):
        axi.scatter(z[lab < 0], s[lab < 0], s=0.6, c="0.82", lw=0, label="unclustered")
        axi.scatter(z[lab == 0], s[lab == 0], s=1.4, c="tab:red", lw=0, label="cluster 0 (n=%d)" % len(clusters[0]))
        axi.scatter(z[lab == 1], s[lab == 1], s=1.4, c="tab:blue", lw=0, label="cluster 1 (n=%d)" % len(clusters[1]) if len(clusters) > 1 else "")
        axi.set_title("%s: %s" % (piece, ttl), fontsize=9)
        axi.set_xlabel("z along the symmetry axis (mm)", fontsize=8)
        axi.set_ylabel("s across the axis, radial direction to cluster 0 (mm)", fontsize=8)
        axi.tick_params(labelsize=7)
        axi.set_aspect("equal", adjustable="datalim")
    ax[0].legend(fontsize=6, markerscale=6, loc="best")
    if len(clusters) > 1:
        zz = np.concatenate([z[np.asarray(clusters[0])], z[np.asarray(clusters[1])]])
        ss = np.concatenate([s[np.asarray(clusters[0])], s[np.asarray(clusters[1])]])
        pad = 3.0
        ax[1].set_xlim(zz.min() - pad, zz.max() + pad)
        ax[1].set_ylim(ss.min() - pad, ss.max() + pad)
        ax[1].set_aspect("equal", adjustable="box")
        span = max(zz.max() - zz.min(), ss.max() - ss.min()) + 2 * pad
        px = fig.get_size_inches()[0] * fig.dpi / 3.0
        caption_lines.append("%s zoom window: %.2f mm across %.0f px = %.4f mm/px"
                             % (piece, span, px, span / px))
        med0 = float(np.median(s[np.asarray(clusters[0])]))
        med1 = float(np.median(s[np.asarray(clusters[1])]))
        ax[1].axhline(med0, ls="--", lw=0.6, c="tab:red")
        ax[1].axhline(med1, ls="--", lw=0.6, c="tab:blue")
        ax[1].annotate("median s: %.2f / %.2f mm  (separation %.2f mm)"
                       % (med0, med1, abs(med1 - med0)),
                       xy=(0.02, 0.98), xycoords="axes fraction", fontsize=6, va="top")
        caption_lines.append("%s median s of cluster 0 = %.3f mm, of cluster 1 = %.3f mm, separation %.3f mm"
                             % (piece, med0, med1, abs(med1 - med0)))
        ax[1].plot([zz.min() + 0.5, zz.min() + 1.5], [ss.min() - pad + 0.6] * 2, "k-", lw=1.2)
        ax[1].annotate("1 mm", (zz.min() + 0.5, ss.min() - pad + 0.9), fontsize=6)
    ax[2].hist(s[lab == 0], bins=np.arange(s.min(), s.max() + 0.1, 0.1) if len(clusters) > 1 else 30,
               color="tab:red", alpha=0.65, label="cluster 0")
    if len(clusters) > 1:
        ax[2].hist(s[lab == 1], bins=np.arange(s.min(), s.max() + 0.1, 0.1),
                   color="tab:blue", alpha=0.65, label="cluster 1")
    ax[2].set_title("%s: distribution of s (0.1 mm bins)" % piece, fontsize=9)
    ax[2].set_xlabel("s across the axis (mm)", fontsize=8)
    ax[2].set_ylabel("points", fontsize=8)
    ax[2].tick_params(labelsize=7)
    ax[2].legend(fontsize=6)
    fig.tight_layout()
    fig.savefig(png)
    plt.close(fig)


# ---------------------------------------------------------------------- main
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--runs-root", required=True)
    ap.add_argument("--stamp", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--dset", required=True)
    ap.add_argument("--corpus", required=True)
    ap.add_argument("--axes", required=True, help="job 1 out dir holding boot/ and axes/")
    ap.add_argument("--variants", required=True, help="job 1 out/variants.tsv")
    ap.add_argument("--renders", required=True, help="directory for the PNGs")
    args = ap.parse_args()
    os.makedirs(args.out, exist_ok=True)
    os.makedirs(args.renders, exist_ok=True)
    cfg = dict(PAPER)
    stamp = args.stamp
    var_dirs = sorted(d for d in glob.glob(os.path.join(args.runs_root, "*_p20-*"))
                      if os.path.basename(d).startswith(stamp))
    log("[A] variant run dirs under this job:", len(var_dirs))

    # ---- A. is the segmentation input the same bytes across the whole sweep?
    md5_by_piece = {}
    ply_of = {}
    for d in var_dirs:
        for f in glob.glob(os.path.join(d, "out", "segmentation", "*_SampledWithNormals.ply")):
            piece = os.path.basename(f).replace("_SampledWithNormals.ply", "")
            md5 = os.popen("md5sum %s | awk '{print $1}'" % f).read().strip()
            md5_by_piece.setdefault(piece, {}).setdefault(md5, []).append(os.path.basename(d))
            ply_of.setdefault(piece, (f, md5))
    with open(os.path.join(args.out, "A_segmentation_input.tsv"), "w") as fh:
        fh.write("piece\tmd5\tbytes\tdistinct_md5_over_variants\tn_variants\n")
        for piece in sorted(ply_of):
            f, md5 = ply_of[piece]
            n = sum(len(v) for v in md5_by_piece[piece].values())
            fh.write("%s\t%s\t%d\t%d\t%d\n" % (piece, md5, os.path.getsize(f), len(md5_by_piece[piece]), n))
    log("[A] pieces with a harvested segmentation input:", sorted(ply_of))

    # ---- A2. the pipeline's own printouts, per variant, straight from run.json
    rows_pipe = []
    for d in var_dirs:
        rj = os.path.join(d, "run.json")
        if not os.path.exists(rj):
            continue
        j = json.load(open(rj))
        if j.get("tag") == "p20-sweep" or "piece" not in j:
            continue
        rows_pipe.append(dict(tag=j["tag"], piece=j["piece"], env=j.get("env", ""),
                              clusters=j.get("clusters"), sizes=j.get("cluster_sizes"),
                              adaptive=j.get("adaptive_normals"), grow=j.get("paper_grow"),
                              rule=j.get("splitter_rule"), merge=j.get("merge_line"),
                              classify=j.get("classify_line"), face_order=j.get("face_order"),
                              s0=j.get("surface_0_written"), s1=j.get("surface_1_written"),
                              notfound=j.get("source_file_not_found_lines"),
                              mesh_exit=j.get("mesh_exit"), elapsed=j.get("elapsed_s"),
                              ply_md5=j.get("segmentation_input", {}).get("md5")))
    if rows_pipe:
        cols = list(rows_pipe[0].keys())
        with open(os.path.join(args.out, "A2_pipeline_printouts.tsv"), "w") as fh:
            fh.write("\t".join(cols) + "\n")
            for r in rows_pipe:
                fh.write("\t".join(str(r.get(c, "")) for c in cols) + "\n")
    log("[A2] pipeline rows:", len(rows_pipe))

    # ---- B. replay grow + merge + classify per piece
    rows_merge, rows_cls, rows_two = [], [], []
    replay_ok = {}
    for piece in NP_PIECES:
        if piece not in ply_of:
            log("[B] no segmentation input for", piece)
            continue
        f, _md5 = ply_of[piece]
        pts, nrm, curv, props = load_ply(f)
        n = len(pts)
        dynmin = max(50, max(30, n // 500))
        nb_density = max(5, min(20, n // 1000))
        res = {}
        for conv in ("signed", "abs"):
            cl = grow(pts, nrm, curv, cfg["nb"], cfg["theta"], cfg["kappa"], dynmin, conv)
            res[conv] = cl
        chosen = "signed" if len(res["signed"]) >= len(res["abs"]) else "abs"
        if [len(c) for c in res["signed"]] == [len(c) for c in res["abs"]]:
            chosen = "signed"
        clusters = res[chosen]
        replay_ok[piece] = dict(n=n, dynmin=dynmin, nb_density=nb_density,
                                sizes_signed=[len(c) for c in res["signed"]],
                                sizes_abs=[len(c) for c in res["abs"]],
                                convention=chosen, props=props,
                                cluster0=clusters[0], cluster1=clusters[1] if len(clusters) > 1 else None,
                                premerge_sizes=[len(c) for c in clusters])
        log("[B]", piece, "N=%d dynmin=%d pre-merge sizes signed=%s abs=%s"
            % (n, dynmin, replay_ok[piece]["sizes_signed"], replay_ok[piece]["sizes_abs"]))
        trace = []
        post, npass = merge(pts, nrm, curv, clusters, cfg, trace)
        for d in trace:
            rows_merge.append(dict(piece=piece, **d))
        axis_file = find_axis(args.axes, args.corpus, piece)
        if axis_file is None:
            log("[B]", piece, "no axis available for classify")
            continue
        ap_, ad_ = read_axis(axis_file)
        for label, cl in (("pre-merge", clusters), ("post-merge", post)):
            c = classify(pts, nrm, cl, ap_, ad_)
            if c is None:
                log("[B]", piece, label, "fewer than 2 clusters -> classify returns immediately")
                continue
            rows_cls.append(dict(piece=piece, stage=label, axis=axis_file,
                                 satA=c["satA"], satB=c["satB"], swap=c["swap"],
                                 **{"face0_" + k: v for k, v in c["face"][0].items()},
                                 **{"face1_" + k: v for k, v in c["face"][1].items()}))
        if len(clusters) > 1:
            A = np.asarray(clusters[0])
            B = np.asarray(clusters[1])
            na = mean_normal(A, nrm)
            nb = mean_normal(B, nrm)
            from scipy.spatial import cKDTree
            dist, _ = cKDTree(pts[A]).query(pts[B], k=1)
            off = (pts[B] - pts[A].mean(axis=0)) @ na
            rows_two.append(dict(piece=piece, n0=len(A), n1=len(B),
                                 dot_mean_normals=float(np.dot(na, nb)),
                                 dot_abs=float(abs(np.dot(na, nb))),
                                 nn_dist_min_mm=float(dist.min()),
                                 nn_dist_med_mm=float(np.median(dist)),
                                 offset_along_n0_med_mm=float(np.median(off)),
                                 offset_along_n0_p10_mm=float(np.percentile(off, 10)),
                                 offset_along_n0_p90_mm=float(np.percentile(off, 90)),
                                 centroid_dist_mm=float(np.linalg.norm(pts[A].mean(axis=0) - pts[B].mean(axis=0)))))

    def dump(name, rows, cols=None):
        if not rows:
            return
        cols = cols or list(rows[0].keys())
        with open(os.path.join(args.out, name), "w") as fh:
            fh.write("\t".join(cols) + "\n")
            for r in rows:
                fh.write("\t".join(("%.6g" % r[c]) if isinstance(r.get(c), float) else str(r.get(c, ""))
                                   for c in cols) + "\n")
    dump("B_merge_criteria.tsv", rows_merge)
    dump("B_classify_replay.tsv", rows_cls)
    dump("B_two_clusters.tsv", rows_two)

    # ---- B2. does the replay reproduce the pipeline's own cluster sizes?
    base_env = ("", "SFS_PAPER_NB=10 SFS_PAPER_THETA=3.4")
    rows_id = []
    for piece, r in sorted(replay_ok.items()):
        pipe = [x for x in rows_pipe if x["piece"] == piece and x.get("env", "") in base_env]
        psizes = pipe[0]["sizes"] if pipe else ""
        ptxt = [s for s in str(psizes).split(",") if s and s != "none"]
        def same(trial):
            return ",".join(str(x) for x in trial) == ",".join(ptxt)
        rows_id.append(dict(piece=piece, N=r["n"], dynmin=r["dynmin"],
                            nb_at_line_420=r["nb_density"],
                            pipeline_baseline=psizes or "none",
                            replay_signed=",".join(str(x) for x in r["sizes_signed"]),
                            replay_abs=",".join(str(x) for x in r["sizes_abs"]),
                            convention=r["convention"],
                            signed_matches=same(r["sizes_signed"]),
                            abs_matches=same(r["sizes_abs"]),
                            adaptive_line=(pipe[0]["adaptive"] if pipe else ""),
                            grow_line=(pipe[0]["grow"] if pipe else "")))
    dump("B2_replay_identity.tsv", rows_id)

    # ---- C. the meshes themselves
    rows_mesh = []
    for piece in NP_PIECES:
        if piece not in replay_ok:
            continue
        if piece.startswith("Pot_A"):
            mesh = os.path.join(args.corpus, "Mesh", piece + "_Mesh.obj")
        else:
            mesh = os.path.join(args.dset, "Mesh", piece.split("_")[0], piece + "_Mesh.obj")
        if not os.path.exists(mesh):
            log("[C] mesh missing", mesh)
            continue
        f, _ = ply_of[piece]
        pts, nrm, _c, _p = load_ply(f)
        try:
            m = mesh_measure(mesh, pts, nrm)
        except Exception as exc:
            log("[C] mesh measure failed for", piece, repr(exc))
            continue
        m["piece"] = piece
        rows_mesh.append(m)
        log("[C]", piece, {k: m[k] for k in ("vertices", "faces", "thick_med_mm") if k in m})
    dump("C_mesh.tsv", rows_mesh)

    # ---- D. 5-NN vs 20-NN normals
    rows_n = []
    for piece in NP_PIECES:
        if piece not in ply_of:
            continue
        f, _ = ply_of[piece]
        pts, _n, _c, _p = load_ply(f)
        try:
            d = normal_density_test(pts)
        except Exception as exc:
            log("[D] failed for", piece, repr(exc))
            continue
        d["piece"] = piece
        rows_n.append(d)
        log("[D]", piece, d)
    dump("D_normal_density.tsv", rows_n)

    # ---- E. renders
    caps = []
    for piece in RENDER_PIECES:
        if piece not in replay_ok:
            log("[E] nothing to render for", piece)
            continue
        f, _ = ply_of[piece]
        pts, nrm, curv, _p = load_ply(f)
        d = replay_ok[piece]
        clusters = [d["cluster0"]] + ([d["cluster1"]] if d["cluster1"] else [])
        axis_file = find_axis(args.axes, args.corpus, piece)
        if axis_file is None:
            log("[E] no axis for", piece)
            continue
        ap_, ad_ = read_axis(axis_file)
        png = os.path.join(args.renders, piece + ".png")
        try:
            render(piece, pts, clusters, ap_, ad_, png, caps)
        except Exception as exc:
            log("[E] render failed for", piece, repr(exc))
            continue
        caps.append("%s: pre-merge clusters %s from %s, axis %s, PNG %s"
                    % (piece, [len(c) for c in clusters], os.path.basename(f), os.path.basename(axis_file), os.path.basename(png)))
    with open(os.path.join(args.out, "E_captions.txt"), "w") as fh:
        fh.write("\n".join(caps) + "\n")

    # ---- F. the sweep table as a markdown block
    with open(os.path.join(args.out, "F_sweep_table.md"), "w") as fh:
        fh.write("| piece | SFS_PAPER_NB | SFS_PAPER_THETA | other env | clusters first print | clusters final | retries | cluster sizes | surface 0/1 | not found | run directory |\n")
        fh.write("|---|---|---|---|---|---|---|---|---|---|---|\n")
        with open(args.variants) as v:
            hdr = v.readline()
            for ln in v:
                p = ln.rstrip("\n").split("\t")
                if len(p) < 12:
                    continue
                tag, pot, piece, env, ex, cl, sizes, s0, s1, nf = p[:10]
                d = [x for x in glob.glob(os.path.join(args.runs_root, "*_p20-" + tag))
                     if os.path.exists(os.path.join(x, "logs", "mesh.log"))]
                fin, ret = "-", "-"
                if d:
                    txt = open(os.path.join(d[0], "logs", "mesh.log"), errors="replace").read()
                    cs = re.findall(r"Number of clusters is equal to (\d+)", txt)
                    fin = cs[-1] if cs else "-"
                    ret = str(len(re.findall(r"Single cluster failed|Single cluster found \(iteration", txt)))
                nb = th = "-"
                other = []
                for tok in env.split():
                    if tok.startswith("SFS_PAPER_NB="):
                        nb = tok.split("=", 1)[1]
                    elif tok.startswith("SFS_PAPER_THETA="):
                        th = tok.split("=", 1)[1]
                    else:
                        other.append(tok)
                fh.write("| %s | %s | %s | %s | %s | %s | %s | %s | %s/%s | %s | %s |\n"
                         % (piece.replace("Juglet_", "J"), nb, th, " ".join(other) or "-",
                            cl, fin, ret, sizes, s0, s1, nf, os.path.basename(d[0]) if d else "?"))
    log("[F] wrote", os.path.join(args.out, "F_sweep_table.md"))
    log("[DONE]")


if __name__ == "__main__":
    sys.exit(main())
