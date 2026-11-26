#!/usr/bin/env python3
"""Ticket 13 Part B: nine single-factor surface arms for Pot_J_Piece_01 (J01).

One sherd, nine wall representations, the frozen SHIP selector unchanged:
  t03_lib.draw_pool(C, seeds=10, step=10) -> t03_extract.select_lines(..., 6, None)
  -> t03_extract.write_lines, with C = face 0 then face 1.

It records (a) the wall comparison of every arm against the other surface source, (b) the
candidate table (angles to GT and to the Ticket 13 donor line), and (c) the overlay figure.
OWN_T09 must reproduce the Ticket 09 axis byte-for-byte, AUTHOR must land on the donor line.

Read-only: the SHIP work tree, the Ticket 09 walls, the corpus surfaces and GT.
Writes only under --run:
  j01/walls/<ARM>.S<f>.xyz            the exact float64 walls each arm was run on
  j01/axes/<ARM>/Pot_J_Piece_01_Axis.xyz
  evidence/j01_walls.tsv              arm,face,points,... (18 rows)
  evidence/j01_factors.tsv            arm,k,... (9 rows)
  renders/J01_surface_factors_overlay.png
  logs/j01_status.json                own_t09_pin_match / author_donor_match /
                                      normal_transfer_fixed_xyz
  logs/j01_factors13.log              this module's stdout
"""
import argparse
import hashlib
import json
import os
import sys
from multiprocessing import Pool

import numpy as np
from scipy.spatial import cKDTree

STEM = "Pot_J_Piece_01"
FACES = (0, 1)
PIN_SHA = "a0d1b8af0143dfc71271701a16295d1db5bdc3236ab5361d4bcc796d0786de79"

# Ticket 13 diagnostic donor line (evaluation only; never fed to the selector).
DONOR_DIR = np.array([0.992676, 0.042854, 0.112950], dtype=float)
DONOR_DIR = DONOR_DIR / np.linalg.norm(DONOR_DIR)
DONOR_PT = np.array([-53.313366, -28.804402, 479.479140], dtype=float)
CENTROID = np.array([30.107, 12.692, 452.566], dtype=float)

SHIP = "/data/gpfs/projects/punim2657/SfSpp/runs/20261121-1319_2e951d9_t03-ship"
IMPL = os.path.join(SHIP, "work", "impl_t03")
T09_AX = ("/data/gpfs/projects/punim2657/SfSpp/runs/"
          "20261125-1340_a50f8cc_t09-own-surfaces/out/axes09_own_regen")
T09_WALLS = ("/data/gpfs/projects/punim2657/SfSpp/runs/"
             "20261125-1340_a50f8cc_t09-own-surfaces/out/Pot_J/geom")

for _p in (os.path.join(SHIP, "work"), IMPL, os.path.join(IMPL, "scripts")):
    if _p not in sys.path:
        sys.path.insert(0, _p)
os.environ.setdefault("SFS_IMPL", IMPL)

import t03_lib as dl  # noqa: E402
import t03_extract as tx  # noqa: E402
from sfs_axes.io_axes import direction_angle_deg  # noqa: E402

# The Ticket 09 walls are the OWN source for this ticket; t03_lib.walls(..., "own")
# reads <OWN[pot]>/<stem>.S0/.S1 through the frozen loader, so pointing OWN["J"] at
# them is the whole substitution.
dl.OWN = dict(dl.OWN)
dl.OWN["J"] = T09_WALLS

ARMS = ["OWN_T09", "AUTHOR", "OWN_AUTHOR_NORMALS", "AUTHOR_OWN_NORMALS",
        "OWN_SHARED_1MM", "AUTHOR_SHARED_1MM", "OWN_VOXEL_1MM", "AUTHOR_VOXEL_1MM",
        "OWN_BALANCED_S0S1"]
WALL_COLS = ["arm", "face", "points", "duplicate_xyz", "matched_1mm_pct", "nn_med_mm",
             "nn_p90_mm", "normal_ang_med_deg", "normal_ang_p90_deg", "xyz_sha256",
             "normals_sha256"]
FACT_COLS = ["arm", "k", "axes_sha256", "effective_stride", "drawn_points",
             "rank1_gt_deg", "best_gt_deg", "best_donor_deg", "best_donor_mm",
             "best_donor_rank", "qualifies_b2", "b2_best_joins"]
TAB = chr(9)
NL = chr(10)
RUN = ""


def log(msg):
    print("[j01] " + msg, flush=True)


def sha_bytes(b):
    return hashlib.sha256(b).hexdigest()


def sha_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for blk in iter(lambda: fh.read(1 << 20), b""):
            h.update(blk)
    return h.hexdigest()


def xyz_sha(P):
    return sha_bytes(np.ascontiguousarray(np.asarray(P[0:3, :].T, dtype="<f8")).tobytes())


def normals_sha(P):
    return sha_bytes(np.ascontiguousarray(np.asarray(P[3:6, :].T, dtype="<f8")).tobytes())


def duplicate_xyz(P):
    X = np.ascontiguousarray(np.asarray(P[0:3, :].T, dtype="<f8"))
    if X.shape[0] < 2:
        return 0
    return int(X.shape[0] - np.unique(X, axis=0).shape[0])


def nn(src, dst):
    """1-NN from every src point to dst; distances in mm (scene units are mm)."""
    d, i = cKDTree(np.ascontiguousarray(dst[0:3, :].T)).query(
        np.ascontiguousarray(src[0:3, :].T), k=1)
    return d, i


def transfer_normals(src, dst):
    out = np.array(src, dtype=float, copy=True)
    d, i = nn(src, dst)
    m = d <= 1.0
    out[3:6, m] = dst[3:6, i[m]]
    return out, {"matched": int(m.sum()), "points": int(src.shape[1]),
                 "xyz_sha": xyz_sha(out), "src_xyz_sha": xyz_sha(src)}


def shared_subset(src, dst):
    d, _ = nn(src, dst)
    m = d <= 1.0
    return np.ascontiguousarray(src[:, m]), {"kept": int(m.sum())}


def linspace_subset(P, n):
    m = P.shape[1]
    if m == n:
        return np.array(P, dtype=float, copy=True), {"kept": m, "native": m}
    idx = np.floor(np.linspace(0.0, m - 1.0, n)).astype(np.int64)
    return np.ascontiguousarray(P[:, idx]), {"kept": int(idx.size), "native": m}


def common_voxel(source, other, size=1.0):
    """Points of source in the 1 mm voxels both walls occupy, one per voxel.

    The representative is the source point closest to the voxel centre; ties break on
    the lowest source index.
    """
    def keys(P):
        return np.floor(np.asarray(P[0:3, :].T, dtype=float) / size).astype(np.int64)

    Ks, Ko = keys(source), keys(other)
    if Ks.shape[0] == 0 or Ko.shape[0] == 0:
        return source[:, :0], {"kept": 0, "common_voxels": 0}
    U, inv = np.unique(np.concatenate([Ks, Ko], axis=0), axis=0, return_inverse=True)
    cs = inv[:Ks.shape[0]]
    co = inv[Ks.shape[0]:]
    common = np.intersect1d(cs, co, assume_unique=False)
    if common.size == 0:
        return source[:, :0], {"kept": 0, "common_voxels": 0}
    idx = np.nonzero(np.isin(cs, common))[0]
    centres = (U[cs[idx]].astype(float) + 0.5) * size
    dist = np.linalg.norm(np.asarray(source[0:3, idx].T, dtype=float) - centres, axis=1)
    order = np.lexsort((idx, dist, cs[idx]))
    picked = idx[order]
    codes = cs[picked]
    first = np.ones(picked.size, dtype=bool)
    first[1:] = codes[1:] != codes[:-1]
    keep = picked[first]
    return np.ascontiguousarray(source[:, keep]), {"kept": int(keep.size),
                                                   "common_voxels": int(common.size)}


def build_arm(arm, own, auth):
    c0o, c1o = own
    c0a, c1a = auth
    info = {}
    if arm == "OWN_T09":
        return np.array(c0o, copy=True), np.array(c1o, copy=True), info
    if arm == "AUTHOR":
        return np.array(c0a, copy=True), np.array(c1a, copy=True), info
    if arm == "OWN_AUTHOR_NORMALS":
        c0, i0 = transfer_normals(c0o, c0a)
        c1, i1 = transfer_normals(c1o, c1a)
        info["transfer"] = [i0, i1]
        return c0, c1, info
    if arm == "AUTHOR_OWN_NORMALS":
        c0, i0 = transfer_normals(c0a, c0o)
        c1, i1 = transfer_normals(c1a, c1o)
        info["transfer"] = [i0, i1]
        return c0, c1, info
    if arm == "OWN_SHARED_1MM":
        c0, i0 = shared_subset(c0o, c0a)
        c1, i1 = shared_subset(c1o, c1a)
        info["subset"] = [i0, i1]
        return c0, c1, info
    if arm == "AUTHOR_SHARED_1MM":
        c0, i0 = shared_subset(c0a, c0o)
        c1, i1 = shared_subset(c1a, c1o)
        info["subset"] = [i0, i1]
        return c0, c1, info
    if arm == "OWN_VOXEL_1MM":
        c0, i0 = common_voxel(c0o, c0a)
        c1, i1 = common_voxel(c1o, c1a)
        info["subset"] = [i0, i1]
        return c0, c1, info
    if arm == "AUTHOR_VOXEL_1MM":
        c0, i0 = common_voxel(c0a, c0o)
        c1, i1 = common_voxel(c1a, c1o)
        info["subset"] = [i0, i1]
        return c0, c1, info
    if arm == "OWN_BALANCED_S0S1":
        c1, i1 = linspace_subset(c1o, c0o.shape[1])
        info["balanced"] = i1
        return np.array(c0o, copy=True), c1, info
    raise ValueError("unknown arm %r" % arm)


def normal_angles(P, ref):
    """Folded (unsigned) angle between each arm normal and the nearest reference normal."""
    d, i = nn(P, ref)
    a = np.asarray(P[3:6, :].T, dtype=float)
    b = np.asarray(ref[3:6, :].T, dtype=float)[i]
    c = np.abs(np.sum(a * b, axis=1)) / np.maximum(
        np.linalg.norm(a, axis=1) * np.linalg.norm(b, axis=1), 1e-12)
    return np.degrees(np.arccos(np.clip(c, -1.0, 1.0))), d


def wall_row(arm, face, P, ref, path):
    """xyz_sha256 is the hash of the saved .xyz bytes, so a reviewer can check it with sha256sum."""
    ang, d = normal_angles(P, ref)
    return {"arm": arm, "face": face, "points": int(P.shape[1]),
            "duplicate_xyz": duplicate_xyz(P),
            "matched_1mm_pct": round(100.0 * float(np.mean(d <= 1.0)), 4),
            "nn_med_mm": round(float(np.median(d)), 6),
            "nn_p90_mm": round(float(np.percentile(d, 90)), 6),
            "normal_ang_med_deg": round(float(np.median(ang)), 4),
            "normal_ang_p90_deg": round(float(np.percentile(ang, 90)), 4),
            "xyz_sha256": sha_file(path), "normals_sha256": normals_sha(P)}


def save_wall(path, P):
    """x y z nx ny nz per row, %.17g, so a reviewer can recompute every hash."""
    with open(path, "w") as fh:
        for k in range(P.shape[1]):
            fh.write(" ".join("%.17g" % float(x) for x in P[:, k]) + NL)


def perp_mm(v):
    """Perpendicular distance (mm) from the line's point to the donor line."""
    r = np.asarray(v[3:6], dtype=float) - DONOR_PT
    r = r - float(r @ DONOR_DIR) * DONOR_DIR
    return float(np.linalg.norm(r))


def run_arm(arm, own, auth):
    c0, c1, info = build_arm(arm, own, auth)
    wdir = os.path.join(RUN, "j01", "walls")
    adir = os.path.join(RUN, "j01", "axes", arm)
    for d in (wdir, adir):
        os.makedirs(d, exist_ok=True)
    save_wall(os.path.join(wdir, arm + ".S0.xyz"), c0)
    save_wall(os.path.join(wdir, arm + ".S1.xyz"), c1)
    C = np.concatenate([c0, c1], axis=1)
    path = os.path.join(adir, STEM + "_Axis.xyz")
    open(path, "w").close()
    rec = {"arm": arm, "info": info, "walls": [], "factor": None, "path": path,
           "lines": None}
    # The reference for the wall table is the OTHER surface source.
    ref0, ref1 = (auth if arm.startswith("OWN") else own)
    rec["walls"].append(wall_row(arm, 0, c0, ref0, os.path.join(wdir, arm + ".S0.xyz")))
    rec["walls"].append(wall_row(arm, 1, c1, ref1, os.path.join(wdir, arm + ".S1.xyz")))
    if C.shape[1] < 10:
        rec["factor"] = dict(arm=arm, k=0, axes_sha256="", effective_stride="",
                             drawn_points=0, rank1_gt_deg="", best_gt_deg="",
                             best_donor_deg="", best_donor_mm="", best_donor_rank="",
                             qualifies_b2=0, b2_best_joins="")
        return rec
    reps, sizes, V, st, nd = dl.draw_pool(C, seeds=10, step=10)
    out = tx.select_lines(reps, sizes, c0, c1, C, 6, None)
    if out is None or out[0].shape[1] == 0:
        rec["factor"] = dict(arm=arm, k=0, axes_sha256=sha_file(path),
                             effective_stride=int(st), drawn_points=int(C.shape[1] // int(st)),
                             rank1_gt_deg="", best_gt_deg="", best_donor_deg="",
                             best_donor_mm="", best_donor_rank="", qualifies_b2=0,
                             b2_best_joins="")
        return rec
    lines, costs = out
    tx.write_lines(path, lines)
    gt = dl.gt_axis(STEM)
    ang_gt = [float(direction_angle_deg(lines[0:3, k], gt[0:3]))
              for k in range(lines.shape[1])]
    ang_dn = [float(direction_angle_deg(lines[0:3, k], DONOR_DIR))
              for k in range(lines.shape[1])]
    mm_dn = [perp_mm(lines[:, k]) for k in range(lines.shape[1])]
    best_rank = int(np.argmin(ang_dn))
    best_gt = float(min(ang_gt))
    best_dn = float(ang_dn[best_rank])
    best_mm = float(mm_dn[best_rank])
    qual = int((best_dn <= 15.0 and best_mm <= 15.0) or best_gt <= 25.0)
    rec["lines"] = lines
    rec["factor"] = dict(arm=arm, k=int(lines.shape[1]), axes_sha256=sha_file(path),
                         effective_stride=int(st),
                         drawn_points=int(C.shape[1] // int(st)),
                         rank1_gt_deg=round(ang_gt[0], 4),
                         best_gt_deg=round(best_gt, 4),
                         best_donor_deg=round(best_dn, 4),
                         best_donor_mm=round(best_mm, 4),
                         best_donor_rank=best_rank,
                         qualifies_b2=qual, b2_best_joins="")
    return rec


def frame(P):
    """Orthonormal (centroid, u, v) best-fit plane of a wall; in-plane lengths are true mm."""
    X = np.asarray(P[0:3, :].T, dtype=float)
    c = X.mean(axis=0)
    _, _, vt = np.linalg.svd(X - c, full_matrices=False)
    u, v = vt[0], vt[1]
    return c, u, v


def project(P, c, u, v):
    X = np.asarray(P[0:3, :].T, dtype=float) - c
    return X @ u, X @ v


def seg2d(v, c, u, vv, span=60.0):
    """Project the ends of a 3D line (direction v[0:3] through v[3:6]) onto the plane."""
    d = np.asarray(v[0:3], dtype=float)
    d = d / np.linalg.norm(d)
    p0 = np.asarray(v[3:6], dtype=float) - span * d
    p1 = np.asarray(v[3:6], dtype=float) + span * d
    a = (p0 - c) @ u, (p0 - c) @ vv
    b = (p1 - c) @ u, (p1 - c) @ vv
    return a, b


def render(results, own0, gt, path):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    c, u, v = frame(own0)
    fig, axes = plt.subplots(3, 3, figsize=(15.5, 15.6), dpi=140)
    for ax, rec in zip(axes.ravel(), results):
        arm = rec["arm"]
        x, y = project(own0, c, u, v)
        ax.scatter(x, y, s=1.0, c="#b9b9b9", linewidths=0, rasterized=True)
        if rec["lines"] is not None:
            L = rec["lines"]
            for k in range(min(L.shape[1], 6)):
                a, b = seg2d(L[:, k], c, u, v)
                ax.plot([a[0], b[0]], [a[1], b[1]], color="#1f4fd8", lw=0.8, alpha=0.55)
            f = rec["factor"]
            k = int(f["best_donor_rank"])
            a, b = seg2d(L[:, k], c, u, v)
            ax.plot([a[0], b[0]], [a[1], b[1]], color="#1f4fd8", lw=2.2,
                    label="best donor-matching estimate")
        a, b = seg2d(gt, c, u, v)
        ax.plot([a[0], b[0]], [a[1], b[1]], color="black", lw=1.6, label="Ground Truth")
        a, b = seg2d(np.r_[DONOR_DIR, DONOR_PT], c, u, v)
        ax.plot([a[0], b[0]], [a[1], b[1]], color="#0a7d28", lw=1.8, ls="--",
                label="Ticket 13 donor line")
        f = rec["factor"] or {}
        title = arm
        if f.get("best_donor_deg", "") != "":
            own_gate = (arm.startswith("OWN_") and arm != "OWN_T09"
                        and int(f.get("qualifies_b2", 0) or 0))
            title += NL + "donor %.2f deg / %.2f mm - GT %.2f deg%s" % (
                float(f["best_donor_deg"]), float(f["best_donor_mm"]), float(f["best_gt_deg"]),
                "  [B2 candidate]" if own_gate else "")
        ax.set_title(title, fontsize=8.5)
        ax.set_xlabel("x (mm)", fontsize=6)
        ax.set_ylabel("y (mm)", fontsize=6)
        ax.set_aspect("equal", adjustable="datalim")
        ax.tick_params(labelsize=6)
        ax.grid(alpha=0.25, lw=0.4)
    lo = min(ax.get_xlim()[0] for ax in axes.ravel())
    hi = max(ax.get_xlim()[1] for ax in axes.ravel())
    for ax in axes.ravel():
        ax.set_xlim(lo, hi)
    for ax in axes.ravel():
        xl, yl = ax.get_xlim(), ax.get_ylim()
        dx, dy = xl[1] - xl[0], yl[1] - yl[0]
        x0 = xl[1] - 0.06 * dx - 20.0
        y0 = yl[0] + 0.08 * dy
        ax.plot([x0, x0 + 20.0], [y0, y0], color="black", lw=3.0, zorder=6)
        ax.text(x0 + 10.0, y0 + 0.02 * dy, "20 mm", ha="center", va="bottom", fontsize=6, zorder=6)
    axes.ravel()[0].legend(fontsize=6, loc="upper left")
    fig.suptitle("J01 surface factors: nine wall representations through the frozen SHIP "
                 "selector (projected on the OWN_T09 face-0 best-fit plane)", fontsize=10)
    fig.tight_layout(rect=(0, 0, 1, 0.97))
    fig.savefig(path)
    plt.close(fig)
    return os.path.getsize(path)


def load_records(run):
    """Rebuild the render inputs from the saved walls and axis files (no recomputation)."""
    facs = {}
    fp = os.path.join(run, "evidence", "j01_factors.tsv")
    with open(fp) as fh:
        head_line = fh.readline().rstrip(NL)
        sep = TAB if TAB in head_line else ","
        head = head_line.split(sep)
        for line in fh:
            v = line.rstrip(NL).split(sep)
            facs[v[0]] = dict(zip(head, v))
    recs = []
    for arm in ARMS:
        p = os.path.join(run, "j01", "axes", arm, STEM + "_Axis.xyz")
        lines = None
        if os.path.exists(p) and os.path.getsize(p) > 0:
            arr = np.atleast_2d(np.loadtxt(p))
            lines = np.vstack([arr[:, 3:6].T, arr[:, 0:3].T])
        recs.append({"arm": arm, "lines": lines, "factor": facs.get(arm, {}),
                     "info": {}, "walls": [], "path": p})
    return recs


def render_only(run):
    c0o, _, _ = dl.walls(STEM, "own")
    gt = dl.gt_axis(STEM)
    recs = load_records(run)
    png = os.path.join(run, "renders", "J01_surface_factors_overlay.png")
    nbytes = render(recs, c0o, gt, png)
    with open(os.path.join(run, "logs", "j01_render.json"), "w") as fh:
        json.dump({"render_bytes": nbytes, "render_scale_bar_mm": 20,
                   "arms": [r["arm"] for r in recs]}, fh, indent=1)
    log("render-only %s (%d bytes)" % (png, nbytes))
    return 0

def write_tsv(path, cols, rows):
    with open(path, "w") as fh:
        fh.write(TAB.join(cols) + NL)
        for r in rows:
            fh.write(TAB.join(str(r.get(c, "")) for c in cols) + NL)


def main():
    global RUN
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", required=True)
    ap.add_argument("--jobs", type=int, default=4)
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--render-only", action="store_true")
    a = ap.parse_args()
    RUN = os.path.abspath(a.run)
    for d in (os.path.join(RUN, "j01"), os.path.join(RUN, "evidence"),
              os.path.join(RUN, "renders"), os.path.join(RUN, "logs")):
        os.makedirs(d, exist_ok=True)
    if a.render_only:
        return render_only(RUN)
    c0o, c1o, _ = dl.walls(STEM, "own")
    c0a, c1a, _ = dl.walls(STEM, "authors")
    own = (c0o, c1o)
    auth = (c0a, c1a)
    gt = dl.gt_axis(STEM)
    log("own walls %r, author walls %r" % ((c0o.shape, c1o.shape), (c0a.shape, c1a.shape)))
    arms = ARMS if not a.limit else ARMS[:a.limit]
    with Pool(max(1, min(a.jobs, len(arms)))) as pool:
        results = pool.map(_run, [(arm, own, auth) for arm in arms], chunksize=1)
    if len(results) != len(ARMS):
        sys.exit("[j01] FAIL only %d arms ran" % len(results))
    walls = [w for r in results for w in r["walls"]]
    facts = [r["factor"] for r in results]
    write_tsv(os.path.join(RUN, "evidence", "j01_walls.tsv"), WALL_COLS, walls)
    write_tsv(os.path.join(RUN, "evidence", "j01_factors.tsv"), FACT_COLS, facts)
    png = os.path.join(RUN, "renders", "J01_surface_factors_overlay.png")
    nbytes = render(results, c0o, gt, png)
    log("render %s (%d bytes)" % (png, nbytes))

    f = {r["arm"]: r["factor"] for r in results}
    pin_ok = f["OWN_T09"]["axes_sha256"] == PIN_SHA
    auth_ok = (f["AUTHOR"]["best_donor_deg"] != "" and
               float(f["AUTHOR"]["best_donor_deg"]) <= 1.0 and
               float(f["AUTHOR"]["best_donor_mm"]) <= 1.0)
    norm_ok = True
    norm_detail = []
    for r in results:
        key = "transfer"
        if key in r["info"]:
            for i, t in enumerate(r["info"][key]):
                ok = (t["matched"] > 0 and t["xyz_sha"] == t["src_xyz_sha"])
                norm_ok = norm_ok and ok
                norm_detail.append({"arm": r["arm"], "face": i, "matched": t["matched"],
                                    "points": t["points"], "xyz_fixed": ok})
    status = {
        "stem": STEM,
        "run": RUN,
        "own_t09_axes_sha256": f["OWN_T09"]["axes_sha256"],
        "own_t09_pin_sha": PIN_SHA,
        "own_t09_pin_match": bool(pin_ok),
        "author_best_donor_deg": f["AUTHOR"]["best_donor_deg"],
        "author_best_donor_mm": f["AUTHOR"]["best_donor_mm"],
        "author_donor_match": bool(auth_ok),
        "normal_transfer_fixed_xyz": bool(norm_ok),
        "normal_transfer_detail": norm_detail,
        "single_file_swap_proof": "written by report13.py from Part A evidence",
        "b2_candidates": [arm for arm in ARMS if int(f[arm].get("qualifies_b2", 0))],
        "arms": {arm: {k: f[arm][k] for k in
                       ("k", "rank1_gt_deg", "best_gt_deg", "best_donor_deg",
                        "best_donor_mm")} for arm in ARMS},
        "render_bytes": nbytes,
        "render_scale_bar_mm": 20,
    }
    with open(os.path.join(RUN, "logs", "j01_status.json"), "w") as fh:
        json.dump(status, fh, indent=1)
    log("OWN_T09 pin match: %s" % pin_ok)
    log("AUTHOR donor match (<=1.0 deg, <=1.0 mm): %s (%.4f deg, %.4f mm)"
        % (auth_ok, float(f["AUTHOR"]["best_donor_deg"] or 0.0),
           float(f["AUTHOR"]["best_donor_mm"] or 0.0)))
    log("normal transfer left xyz fixed: %s" % norm_ok)
    log("B2 candidates: %r" % (status["b2_candidates"],))
    if not (pin_ok and auth_ok and norm_ok):
        sys.exit("[j01] FAIL fixture (own_t09=%s author=%s normals=%s)"
                 % (pin_ok, auth_ok, norm_ok))
    log("J01-FACTORS-OK")
    return 0


def _run(args):
    arm, own, auth = args
    try:
        return run_arm(arm, own, auth)
    except Exception as exc:
        import traceback
        traceback.print_exc()
        raise RuntimeError("arm %s failed: %s" % (arm, exc))


if __name__ == "__main__":
    sys.exit(main() or 0)
