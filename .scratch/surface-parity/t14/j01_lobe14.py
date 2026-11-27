#!/usr/bin/env python3
"""Ticket 14 Part A: the J01 face-1 lobe, and an off-author-wall scan of the corpus.

Two measurements, and no production code touched:

  (a) OWN_T09 face 1 (S1) is split by 1-NN distance to the Authors' face-1 wall at
      1.0 mm into o1_on (on their outer wall) and o1_off (off it), then drawn against
      the real triangle mesh of Pot_J_Piece_01 in three orthographic views and one
      oblique view, so the extra lobe is looked at rather than only counted.
  (b) every one of the 143 released Pot A..J stems, both faces: the 1-NN distance from
      every own (t09) point to the Authors' own wall for that face.  That is what
      settles whether J01 is one bad piece or the corpus habit.

Read-only: the Ticket 13 walls, the Ticket 09 own surfaces, the released corpus, GT.
Writes only under --run:
  renders/J01_mesh_and_s1_lobe_3d.png
  evidence/corpus_offwall_143.tsv        stem,pot,face,own_points,author_points,...
  logs/j01_lobe_status.json              counts, classification, both-pass evidence
  logs/j01_lobe14.log                    this module's stdout
"""
import argparse
import json
import os
import sys
from multiprocessing import Pool

import numpy as np
from scipy.spatial import cKDTree

STEM = "Pot_J_Piece_01"
POT = "Pot_J"

T13_WALLS = ("/data/gpfs/projects/punim2657/SfSpp/runs/"
             "20261126-1500_cf88609_t13-diagnose/j01/walls")
T09_OUT = ("/data/gpfs/projects/punim2657/SfSpp/runs/"
           "20261125-1340_a50f8cc_t09-own-surfaces/out")
CORP = "/data/gpfs/projects/punim2657/sfs_main/original_samples/SfS_pp"
MANIFEST = os.path.join(CORP, "Point", "MANIFEST_released.tsv")
MESH = os.path.join(CORP, "Mesh", "Pot_J_Piece_01_Mesh_DS.obj")

SHIP = "/data/gpfs/projects/punim2657/SfSpp/runs/20261121-1319_2e951d9_t03-ship"
IMPL = os.path.join(SHIP, "work", "impl_t03")

# Ticket 13 diagnostic donor line (evaluation only; never fed to the selector).
DONOR_DIR = np.array([0.992676, 0.042854, 0.112950], dtype=float)
DONOR_DIR = DONOR_DIR / np.linalg.norm(DONOR_DIR)
DONOR_PT = np.array([-53.313366, -28.804402, 479.479140], dtype=float)
CENTROID = np.array([30.107, 12.692, 452.566], dtype=float)

ON_MM = 1.0          # o1_on / o1_off split
COVER_MM = 2.0       # mesh-vertex coverage test
SCALE_BAR_MM = 20.0

OFF_COLS = ["stem", "pot", "face", "own_points", "author_points",
            "pct_within_1mm", "pct_over_5mm", "nn_p90_mm", "nn_max_mm"]
TAB = chr(9)
NL = chr(10)
RUN = ""

for _p in (os.path.join(SHIP, "work"), IMPL, os.path.join(IMPL, "scripts")):
    if _p not in sys.path:
        sys.path.insert(0, _p)
os.environ.setdefault("SFS_IMPL", IMPL)

import t03_lib as dl  # noqa: E402


def log(msg):
    print("[lobe14] " + msg, flush=True)


def _load_ply_ascii(path):
    """PCL ASCII PLY with named properties -> (array, property names)."""
    names = []
    nvert = None
    in_vertex = False
    hlen = 0
    with open(path, "r", errors="replace") as fh:
        if fh.readline().strip() != "ply":
            raise ValueError("%s: not a PLY file" % path)
        hlen = 1
        for line in fh:
            hlen += 1
            t = line.split()
            if not t:
                continue
            if t[0] == "format":
                if len(t) < 2 or t[1] != "ascii":
                    raise ValueError("%s: only ascii PLY is supported, got %r"
                                     % (path, " ".join(t[1:])))
            elif t[0] == "element":
                in_vertex = bool(len(t) >= 3 and t[1] == "vertex")
                if in_vertex:
                    nvert = int(t[2])
            elif t[0] == "property":
                if in_vertex and len(t) >= 3 and t[1] != "list":
                    names.append(t[2])
            elif t[0] == "end_header":
                break
    if nvert is None or not names:
        raise ValueError("%s: PLY has no named vertex properties" % path)
    a = np.loadtxt(path, dtype=float, skiprows=hlen, max_rows=nvert,
                   usecols=list(range(len(names))))
    if a.ndim == 1:
        a = a.reshape(-1, 1)
    if a.shape[0] != nvert:
        raise ValueError("%s: PLY declares %d vertices, read %d"
                         % (path, nvert, a.shape[0]))
    return a, names


def load_wall(path):
    """Wall file -> (6, N) as x y z nx ny nz.

    Two formats occur in this corpus: plain ASCII six columns (the Authors'
    released Surfaces, and the saved Ticket 13 walls) and PCL-generated ASCII
    PLY with named properties (the t09 own surfaces under out/Pot_<P>/geom).
    The header is read so the six columns are chosen by name, not by position.
    """
    with open(path, "rb") as fh:
        head = fh.read(8)
    if not head.startswith(b"ply"):
        a = np.loadtxt(path, dtype=float)
        if a.ndim == 1:
            a = a.reshape(1, -1)
        if a.shape[1] != 6:
            raise ValueError("%s: expected 6 columns, got %d" % (path, a.shape[1]))
        return np.ascontiguousarray(a.T)
    a, names = _load_ply_ascii(path)
    want = ["x", "y", "z", "nx", "ny", "nz"]
    if all(w in names for w in want):
        cols = [names.index(w) for w in want]
    elif a.shape[1] == 6:
        cols = list(range(6))
    else:
        raise ValueError("%s: PLY has no x/y/z/nx/ny/nz (properties: %s)"
                         % (path, ", ".join(names)))
    return np.ascontiguousarray(a[:, cols].T)


def xyz(P):
    return np.ascontiguousarray(np.asarray(P[0:3, :].T, dtype=float))


def nn_dist(src, dst):
    """1-NN distance from every src point to dst (scene units are mm)."""
    if dst.shape[1] == 0 or src.shape[1] == 0:
        return np.full(src.shape[1], np.nan)
    d, _ = cKDTree(xyz(dst)).query(xyz(src), k=1)
    return d


def mesh_vertices(path):
    vs = []
    with open(path, "r", errors="replace") as fh:
        for line in fh:
            if line.startswith("v "):
                f = line.split()
                vs.append((float(f[1]), float(f[2]), float(f[3])))
    return np.asarray(vs, dtype=float)


def classify_vertices(verts, a0, a1, o1_off, tol=COVER_MM):
    """covered (<= tol to a0|a1) / o1_off-only / uncovered, per mesh vertex."""
    author = np.concatenate([a0, a1], axis=1)
    d_author = nn_dist(verts.T, author)
    d_off = nn_dist(verts.T, o1_off)
    covered = d_author <= tol
    offonly = (~covered) & (d_off <= tol)
    uncovered = (~covered) & (~offonly)
    return d_author, d_off, covered, offonly, uncovered


def scan_one(row):
    """Both faces of one released stem: own wall -> 1-NN -> Authors' face wall."""
    pot, stem = row[0], row[1]
    out = []
    for f in (0, 1):
        own_p = os.path.join(T09_OUT, pot, "geom", "%s.S%d" % (stem, f))
        auth_p = os.path.join(CORP, "Surfaces", "%s_Surface_%d.xyz" % (stem, f))
        for p in (own_p, auth_p):
            if not os.path.isfile(p):
                raise IOError("missing wall: %s" % p)
        own = load_wall(own_p)
        auth = load_wall(auth_p)
        d = nn_dist(own, auth)
        if not np.all(np.isfinite(d)):
            raise ValueError("%s face %d: non-finite distances" % (stem, f))
        out.append({
            "stem": stem, "pot": pot, "face": f,
            "own_points": int(own.shape[1]), "author_points": int(auth.shape[1]),
            "pct_within_1mm": 100.0 * float(np.mean(d <= 1.0)),
            "pct_over_5mm": 100.0 * float(np.mean(d > 5.0)),
            "nn_p90_mm": float(np.percentile(d, 90.0)),
            "nn_max_mm": float(np.max(d)),
        })
    return out


def write_tsv(path, cols, rows):
    with open(path, "w") as fh:
        fh.write(TAB.join(cols) + NL)
        for r in rows:
            fh.write(TAB.join(fmt_cell(r[c]) for c in cols) + NL)


def fmt_cell(v):
    if isinstance(v, float):
        return "%.4f" % v
    return str(v)


def seg2d_of(ax, v, axes, span=70.0, **kw):
    """Draw a 3D line (direction v[0:3] through point v[3:6]) on an ortho panel."""
    d = np.asarray(v[0:3], dtype=float)
    d = d / max(np.linalg.norm(d), 1e-12)
    p0 = np.asarray(v[3:6], dtype=float) - span * d
    p1 = np.asarray(v[3:6], dtype=float) + span * d
    i, j = axes
    ax.plot([p0[i], p1[i]], [p0[j], p1[j]], **kw)


def scale_bar(ax, mm=SCALE_BAR_MM):
    xl, yl = ax.get_xlim(), ax.get_ylim()
    dx, dy = xl[1] - xl[0], yl[1] - yl[0]
    x0 = xl[1] - 0.06 * dx - mm
    y0 = yl[0] + 0.06 * dy
    ax.plot([x0, x0 + mm], [y0, y0], color="black", lw=3.4, solid_capstyle="butt",
            zorder=8)
    ax.text(x0 + mm / 2.0, y0 + 0.015 * dy, "%d mm" % mm, ha="center", va="bottom",
            fontsize=7, zorder=9)


def render(mesh, a0, o1_on, o1_off, gt, path, stats):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    col_mesh, col_a0, col_on, col_off = "#cccccc", "#4c72b0", "#1b9e77", "#d95f02"
    fig = plt.figure(figsize=(19.0, 18.0), dpi=200)
    ax_xy = fig.add_subplot(2, 2, 1)
    ax_xz = fig.add_subplot(2, 2, 2)
    ax_yz = fig.add_subplot(2, 2, 3)
    ax_3d = fig.add_subplot(2, 2, 4, projection="3d")

    handles = []

    def draw(ax, axes, label_suffix):
        i, j = axes
        h = ax.scatter(mesh[:, i], mesh[:, j], s=1.2, c=col_mesh, linewidths=0,
                       rasterized=True, label="mesh vertices (%d)" % mesh.shape[0])
        ax.scatter(a0[i, :], a0[j, :], s=2.2, c=col_a0, linewidths=0,
                   rasterized=True, label="AUTHOR.S0 (a0, %d)" % a0.shape[1])
        ax.scatter(o1_on[i, :], o1_on[j, :], s=2.2, c=col_on, linewidths=0,
                   rasterized=True,
                   label="o1_on <=1 mm (%d)" % stats["n_on"])
        ax.scatter(o1_off[i, :], o1_off[j, :], s=2.6, c=col_off, linewidths=0,
                   rasterized=True,
                   label="o1_off >1 mm (%d)" % stats["n_off"])
        seg2d_of(ax, np.r_[DONOR_DIR, DONOR_PT], (i, j), color="#0a7d28", lw=1.8,
                 ls="--", label="AUTHOR donor line")
        seg2d_of(ax, gt, (i, j), color="black", lw=1.6, label="GT axis")
        lo_i = min(mesh[:, i].min(), a0[i].min(), o1_off[i].min())
        hi_i = max(mesh[:, i].max(), a0[i].max(), o1_off[i].max())
        lo_j = min(mesh[:, j].min(), a0[j].min(), o1_off[j].min())
        hi_j = max(mesh[:, j].max(), a0[j].max(), o1_off[j].max())
        mi = 0.04 * max(hi_i - lo_i, 1.0)
        mj = 0.04 * max(hi_j - lo_j, 1.0)
        ax.set_xlim(lo_i - mi, hi_i + mi)
        ax.set_ylim(lo_j - mj, hi_j + mj)
        ax.set_xlabel("%s (mm)" % "xyz"[i], fontsize=8)
        ax.set_ylabel("%s (mm)" % "xyz"[j], fontsize=8)
        ax.set_title("J01 %s view (orthographic, equal aspect)" % label_suffix,
                     fontsize=10)
        ax.set_aspect("equal", adjustable="box")
        ax.grid(alpha=0.25, lw=0.4)
        ax.tick_params(labelsize=7)
        scale_bar(ax)
        return h

    draw(ax_xy, (0, 1), "XY")
    draw(ax_xz, (0, 2), "XZ")
    draw(ax_yz, (1, 2), "YZ")

    ax_3d.scatter(mesh[:, 0], mesh[:, 1], mesh[:, 2], s=1.2, c=col_mesh,
                  linewidths=0, rasterized=True)
    ax_3d.scatter(a0[0, :], a0[1, :], a0[2, :], s=2.2, c=col_a0, linewidths=0)
    ax_3d.scatter(o1_on[0, :], o1_on[1, :], o1_on[2, :], s=2.2, c=col_on,
                  linewidths=0)
    ax_3d.scatter(o1_off[0, :], o1_off[1, :], o1_off[2, :], s=2.8, c=col_off,
                  linewidths=0)
    d = DONOR_DIR
    p0 = DONOR_PT - 70.0 * d
    p1 = DONOR_PT + 70.0 * d
    ax_3d.plot([p0[0], p1[0]], [p0[1], p1[1]], [p0[2], p1[2]], color="#0a7d28",
               lw=1.8, ls="--")
    g = gt
    g0 = g[3:6] - 70.0 * g[0:3] / max(np.linalg.norm(g[0:3]), 1e-12)
    g1 = g[3:6] + 70.0 * g[0:3] / max(np.linalg.norm(g[0:3]), 1e-12)
    ax_3d.plot([g0[0], g1[0]], [g0[1], g1[1]], [g0[2], g1[2]], color="black", lw=1.6)
    allp = np.concatenate([mesh, a0[0:3].T, o1_off[0:3].T], axis=0)
    spans = np.maximum(allp.max(axis=0) - allp.min(axis=0), 1.0)
    ax_3d.set_box_aspect(tuple(spans))
    ax_3d.view_init(elev=25, azim=-55)
    ax_3d.set_xlabel("x (mm)", fontsize=8)
    ax_3d.set_ylabel("y (mm)", fontsize=8)
    ax_3d.set_zlabel("z (mm)", fontsize=8)
    ax_3d.tick_params(labelsize=6)
    ax_3d.set_title("J01 oblique view (mesh + S1 wall)", fontsize=10)
    # 20 mm scale bar along +x, at the low corner of the cloud
    base = allp.min(axis=0) + 0.08 * spans
    ax_3d.plot([base[0], base[0] + SCALE_BAR_MM], [base[1], base[1]],
               [base[2], base[2]], color="black", lw=3.4)
    ax_3d.text(base[0] + SCALE_BAR_MM / 2.0, base[1], base[2], "  %d mm" % SCALE_BAR_MM,
               fontsize=7)

    handles, labels = ax_xy.get_legend_handles_labels()
    fig.legend(handles, labels, loc="lower center", ncol=3, fontsize=9,
               frameon=False, bbox_to_anchor=(0.5, 0.005))
    cover = stats["n_covered"]
    fig.suptitle(
        "J01 (Pot_J_Piece_01, %d mesh vertices): OWN_T09 face 1 has %d points, "
        "%d off the Authors' face-1 wall at >%.0f mm = %.1f%%"
        "\n(own within 1 mm: %d = %.1f%%; own nn p90 %.2f mm, max %.2f mm)"
        "\nmesh vertices vs a0|a1 at <=%.0f mm: %d covered (%.1f%%), "
        "%d o1_off-only (%.1f%%), %d uncovered (%.1f%%)"
        % (mesh.shape[0], stats["n_own_S1"], stats["n_off"], ON_MM, stats["off_frac"],
           stats["n_on"], stats["on_frac"], stats["nn_p90"], stats["nn_max"],
           COVER_MM, cover, 100.0 * cover / mesh.shape[0], stats["n_offonly"],
           100.0 * stats["n_offonly"] / mesh.shape[0], stats["n_uncovered"],
           100.0 * stats["n_uncovered"] / mesh.shape[0]),
        fontsize=11.5)
    fig.tight_layout(rect=(0, 0.035, 1, 0.955))
    fig.savefig(path)
    plt.close(fig)
    return os.path.getsize(path)


def j01_lobe(run):
    w = os.path.join(T13_WALLS)
    own0 = load_wall(os.path.join(w, "OWN_T09.S0.xyz"))
    own1 = load_wall(os.path.join(w, "OWN_T09.S1.xyz"))
    a0 = load_wall(os.path.join(w, "AUTHOR.S0.xyz"))
    a1 = load_wall(os.path.join(w, "AUTHOR.S1.xyz"))

    d = nn_dist(own1, a1)
    on = d <= ON_MM
    o1_on = np.ascontiguousarray(own1[:, on])
    o1_off = np.ascontiguousarray(own1[:, ~on])
    log("OWN_T09.S1 %d points vs AUTHOR.S1 %d: on %d, off %d"
        % (own1.shape[1], a1.shape[1], o1_on.shape[1], o1_off.shape[1]))
    if o1_off.shape[1] == 0:
        raise SystemExit("[lobe14] FAIL no off-wall points -- fixture moved")

    mesh = mesh_vertices(MESH)
    d_author, d_off, covered, offonly, uncovered = classify_vertices(
        mesh, a0, a1, o1_off)
    log("mesh vertices %d: covered %d, o1_off-only %d, uncovered %d"
        % (mesh.shape[0], int(covered.sum()), int(offonly.sum()),
           int(uncovered.sum())))

    gt = dl.gt_axis(STEM)
    stats = {
        "n_own_S1": int(own1.shape[1]), "n_author_S1": int(a1.shape[1]),
        "n_on": int(o1_on.shape[1]), "n_off": int(o1_off.shape[1]),
        "on_frac": 100.0 * float(on.mean()),
        "off_frac": 100.0 * float(1.0 - on.mean()),
        "nn_p90": float(np.percentile(d, 90.0)), "nn_max": float(d.max()),
        "n_mesh_vertices": int(mesh.shape[0]),
        "n_covered": int(covered.sum()), "n_offonly": int(offonly.sum()),
        "n_uncovered": int(uncovered.sum()),
        "off_median_mm": float(np.median(d[~on])),
        "off_p90_mm": float(np.percentile(d[~on], 90.0)),
        "off_max_mm": float(d[~on].max()),
        "off_within_a0_1mm_pct": 100.0 * float(
            np.mean(nn_dist(o1_off, a0) <= 1.0)),
        "off_bbox_min": [float(x) for x in o1_off[0:3].min(axis=1)],
        "off_bbox_max": [float(x) for x in o1_off[0:3].max(axis=1)],
        "mesh_bbox_min": [float(x) for x in mesh.min(axis=0)],
        "mesh_bbox_max": [float(x) for x in mesh.max(axis=0)],
        "on_mm": ON_MM, "cover_mm": COVER_MM,
        "own0_points": int(own0.shape[1]),
        "donor_dir": [float(x) for x in DONOR_DIR],
        "donor_pt": [float(x) for x in DONOR_PT],
        "centroid": [float(x) for x in CENTROID],
    }
    png = os.path.join(run, "renders", "J01_mesh_and_s1_lobe_3d.png")
    stats["render_bytes"] = render(mesh, a0, o1_on, o1_off, gt, png, stats)
    log("render %s (%d bytes)" % (png, stats["render_bytes"]))
    return stats


def corpus_scan(run, jobs):
    with open(MANIFEST) as fh:
        head = fh.readline().rstrip(NL).split(TAB)
        rows = [l.rstrip(NL).split(TAB) for l in fh if l.strip()]
    if head[:2] != ["pot", "piece"]:
        raise SystemExit("[lobe14] FAIL manifest header %r" % (head,))
    log("released stems: %d" % len(rows))
    work = [(r[0], r[1]) for r in rows]
    with Pool(max(1, min(jobs, len(work)))) as pool:
        out = pool.map(scan_one, work, chunksize=1)
    recs = [r for sub in out for r in sub]
    if len(recs) != 2 * len(work):
        raise SystemExit("[lobe14] FAIL %d rows for %d stems"
                         % (len(recs), len(work)))
    recs.sort(key=lambda r: (r["pot"], r["stem"], r["face"]))
    path = os.path.join(run, "evidence", "corpus_offwall_143.tsv")
    write_tsv(path, OFF_COLS, recs)
    with open(path) as fh:
        n = sum(1 for _ in fh) - 1
    log("wrote %s (%d data rows)" % (path, n))
    if n != 286:
        raise SystemExit("[lobe14] FAIL expected 286 rows, wrote %d" % n)

    over10 = [r for r in recs if r["pct_over_5mm"] > 10.0]
    over10.sort(key=lambda r: -r["pct_over_5mm"])
    j01 = [r for r in recs if r["stem"] == STEM]
    summary = {
        "rows": n, "stems": len(work),
        "pct_over_5mm_median": float(np.median([r["pct_over_5mm"] for r in recs])),
        "pct_over_5mm_p90": float(np.percentile([r["pct_over_5mm"] for r in recs], 90.0)),
        "pct_within_1mm_median": float(np.median([r["pct_within_1mm"] for r in recs])),
        "pieces_over_10pct_off": [
            {"stem": r["stem"], "pot": r["pot"], "face": r["face"],
             "pct_over_5mm": round(r["pct_over_5mm"], 4),
             "pct_within_1mm": round(r["pct_within_1mm"], 4),
             "nn_p90_mm": round(r["nn_p90_mm"], 4),
             "nn_max_mm": round(r["nn_max_mm"], 4),
             "own_points": r["own_points"]}
            for r in over10],
        "n_pieces_over_10pct_off": len(over10),
        "j01": [{"face": r["face"], "own_points": r["own_points"],
                 "pct_within_1mm": round(r["pct_within_1mm"], 4),
                 "pct_over_5mm": round(r["pct_over_5mm"], 4),
                 "nn_p90_mm": round(r["nn_p90_mm"], 4),
                 "nn_max_mm": round(r["nn_max_mm"], 4)} for r in j01],
        "rank_of_j01_S1_by_pct_over_5mm": [
            i + 1 for i, r in enumerate(
                sorted(recs, key=lambda x: -x["pct_over_5mm"]))
            if r["stem"] == STEM and r["face"] == 1],
    }
    return summary


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", required=True)
    ap.add_argument("--jobs", type=int, default=8)
    a = ap.parse_args()
    run = os.path.abspath(a.run)
    for d in ("renders", "evidence", "logs", "out"):
        os.makedirs(os.path.join(run, d), exist_ok=True)
    stats = j01_lobe(run)
    corpus = corpus_scan(run, a.jobs)
    status = {"stem": STEM, "run": run, "j01": stats, "corpus": corpus,
              "gates": {
                  "off_wall_points_found": bool(stats["n_off"] > 0),
                  "rows_286": bool(corpus["rows"] == 286),
                  "render_written": bool(stats["render_bytes"] > 0),
                  "tsv_tab_delimited": True,
              }}
    with open(os.path.join(run, "logs", "j01_lobe_status.json"), "w") as fh:
        json.dump(status, fh, indent=1)
    log("J01: %d of %d S1 points off the Author wall (%.2f%%)"
        % (stats["n_off"], stats["n_own_S1"], stats["off_frac"]))
    log("corpus: %d of %d faces over 10%% beyond 5 mm; median over-5mm %.2f%%"
        % (corpus["n_pieces_over_10pct_off"], corpus["rows"],
           corpus["pct_over_5mm_median"]))
    log("LOBE14-OK")
    return 0


if __name__ == "__main__":
    sys.exit(main() or 0)
