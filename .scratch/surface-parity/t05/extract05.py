#!/usr/bin/env python3
"""Ticket 05: ten sampling / coverage arms on Pot E 27 and 28.

The frozen shipped loader and extractor do all the estimating; this script only
chooses which native wall rows are handed to them, records what came back, and
writes the two locked comparison figures.

  python extract05.py --run <run dir> --fixtures
  python extract05.py --run <run dir> [--no-render]

Nothing is transferred, re-estimated, averaged, normalized or flipped: every
retained point is the native 6-vector (x, y, z, nx, ny, nz), and every retained
index map is written to evidence/indices/ so that claim can be re-derived.
"""
import argparse
import datetime
import glob
import json
import os
import platform
import sys
import time

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
SHIP = "/data/gpfs/projects/punim2657/SfSpp/runs/20261121-1319_2e951d9_t03-ship"
T19 = "/data/gpfs/projects/punim2657/SfSpp/runs/20261124-0443_21446b8_t19-decisions"
IMPL = os.path.join(SHIP, "work", "impl_t03")

os.environ.setdefault("SFS_IMPL", IMPL)
for p in (HERE, os.path.join(SHIP, "work"), IMPL, os.path.join(IMPL, "scripts")):
    if p not in sys.path:
        sys.path.insert(0, p)

import t03_lib as dl                                      # noqa: E402
import t03_extract as tx                                  # noqa: E402

import sampling05 as sp                                   # noqa: E402

SEEDS = 10
CAP = 6
STEMS = [("Pot_E_Piece_27", 27), ("Pot_E_Piece_28", 28)]
ARM_SPEC = {
    "OWN": ("own", 10),
    "AUTHOR": ("authors", 10),
    "OWN_DEDUP": ("own", 10),
    "OWN_STRIDE1": ("own", 1),
    "OWN_DEDUP_STRIDE1": ("own", 1),
    "OWN_SHARED_1MM": ("own", 10),
    "AUTHOR_SHARED_1MM": ("authors", 10),
    "OWN_MATCHED_TO_AUTHOR": ("own", 10),
    "OWN_COMMON_VOXEL": ("own", 10),
    "AUTHOR_COMMON_VOXEL": ("authors", 10),
}
ARMS = list(ARM_SPEC)
NATIVE = ("OWN", "AUTHOR")
NON_NATIVE = [a for a in ARMS if a not in NATIVE]

INPUT_COLS = ["sherd", "arm", "face", "native_points", "points", "duplicate_xyz",
              "retained_fraction", "xyz_sha256", "normals_sha256", "source_sha256"]
RUN_COLS = ["sherd", "arm", "status", "k", "axes_sha256", "archive_ok",
            "requested_step", "effective_stride", "drawn_points", "basins", "reason",
            "archived_sha256", "archive_rank_count_agree", "archive_max_abs", "secs"]
AXIS_COLS = ["sherd", "arm", "rank", "oriented_deg", "line_deg", "anchor_mm",
             "pos_x", "pos_y", "pos_z", "dir_x", "dir_y", "dir_z", "cost"]
CHANGE_COLS = ["sherd", "arm", "parent_arm", "k_parent", "k_arm", "axes_bytes_identical",
               "best_ref_line_deg_parent", "best_ref_line_deg_arm",
               "best_ref_anchor_mm_parent", "best_ref_anchor_mm_arm",
               "max_rank_line_delta_deg", "max_rank_anchor_delta_mm"]
RENDER_COLS = ["sherd", "path", "scale_bar_mm"]
SOURCE_COLS = ["kind", "name", "path", "sha256"]


def log(msg):
    print("[t05] %s" % msg, flush=True)


def write_tsv(path, rows, cols):
    with open(path, "w") as fh:
        fh.write("\t".join(cols) + "\n")
        for r in rows:
            fh.write("\t".join("" if r.get(c) is None else str(r.get(c))
                               for c in cols) + "\n")


def read_axis_rows(path):
    """[position-first, direction] rows as written by t03_extract.write_lines."""
    rows = []
    if not os.path.isfile(path):
        return rows
    for line in open(path):
        c = line.split()
        if len(c) < 6:
            continue
        v = np.array([float(x) for x in c[:6]], dtype=float)
        rows.append((v[0:3], v[3:6]))
    return rows


def unit(v):
    n = float(np.linalg.norm(v))
    return np.asarray(v, dtype=float) / n if n else np.asarray(v, dtype=float)


def ang_deg(u, v):
    c = float(np.clip(unit(u) @ unit(v), -1.0, 1.0))
    return float(np.degrees(np.arccos(c)))


def line_dist(p0, g0, gd):
    gd = unit(gd)
    d = np.asarray(p0, dtype=float) - np.asarray(g0, dtype=float)
    return float(np.linalg.norm(d - (d @ gd) * gd))


def anchor_point(pos, g0, gd):
    """Closest pass of the line (pos, gd) to the reference anchor point g0."""
    gd = unit(gd)
    d = np.asarray(g0, dtype=float) - np.asarray(pos, dtype=float)
    return np.asarray(pos, dtype=float) + float(d @ gd) * gd


def source_paths(stem):
    pot = dl.pot_of(stem)
    own = [os.path.join(dl.OWN[pot], stem + ".S0"),
           os.path.join(dl.OWN[pot], stem + ".S1")]
    _, c0p, c1p, _, _ = dl.rb.get_piece_info(stem)
    return own, [c0p, c1p]


def archive_path(sid, source):
    return os.path.join(T19, "axes", "OWN" if source == "own" else "AUTHOR",
                        "Pot_E_Piece_%d_Axis.xyz" % sid)


# --------------------------------------------------------------- arm cutting
def build_arms(stem):
    """arm -> (walls (w0, w1), native index maps (i0, i1)). Rows are never rewritten."""
    o0, o1, _ = dl.walls(stem, surfaces="own")
    a0, a1, _ = dl.walls(stem, surfaces="authors")
    O = [np.asarray(o0, dtype=float), np.asarray(o1, dtype=float)]
    A = [np.asarray(a0, dtype=float), np.asarray(a1, dtype=float)]
    oi = [np.arange(O[f].shape[1], dtype=np.int64) for f in (0, 1)]
    ai = [np.arange(A[f].shape[1], dtype=np.int64) for f in (0, 1)]

    arms = {}
    arms["OWN"] = ([O[0], O[1]], [oi[0], oi[1]])
    arms["AUTHOR"] = ([A[0], A[1]], [ai[0], ai[1]])

    dd = [sp.dedup_indices(O[f][0:3].T) for f in (0, 1)]
    D = [sp.take(O[f], dd[f]) for f in (0, 1)]
    arms["OWN_DEDUP"] = (D, dd)

    arms["OWN_STRIDE1"] = ([O[0], O[1]], [oi[0], oi[1]])
    arms["OWN_DEDUP_STRIDE1"] = ([D[0], D[1]], [dd[0], dd[1]])

    sh = [sp.shared_indices(O[f][0:3].T, A[f][0:3].T) for f in (0, 1)]
    arms["OWN_SHARED_1MM"] = ([sp.take(O[f], sh[f]) for f in (0, 1)], sh)

    su = [sp.shared_indices(A[f][0:3].T, O[f][0:3].T) for f in (0, 1)]
    arms["AUTHOR_SHARED_1MM"] = ([sp.take(A[f], su[f]) for f in (0, 1)], su)

    mt = [sp.matched_indices(D[f][0:3].T, A[f][0:3].T) for f in (0, 1)]
    arms["OWN_MATCHED_TO_AUTHOR"] = ([sp.take(D[f], mt[f]) for f in (0, 1)],
                                     [dd[f][mt[f]] for f in (0, 1)])

    vox = [sp.common_voxel_indices(O[f][0:3].T, A[f][0:3].T) for f in (0, 1)]
    vo = [vox[0][0], vox[1][0]]
    va = [vox[0][1], vox[1][1]]
    arms["OWN_COMMON_VOXEL"] = ([sp.take(O[f], vo[f]) for f in (0, 1)], vo)
    arms["AUTHOR_COMMON_VOXEL"] = ([sp.take(A[f], va[f]) for f in (0, 1)], va)
    for arm in ARMS:
        assert arm in arms, "arm %s not built" % arm
    return arms


# ------------------------------------------------------------------- running
def run_arm(arm, walls):
    """Concat face 0 then face 1, draw the frozen pool, run the frozen selector."""
    w0, w1 = walls
    C = np.concatenate([w0, w1], axis=1)
    step = ARM_SPEC[arm][1]
    t0 = time.time()
    got = dl.draw_pool(C, seeds=SEEDS, step=step)
    if len(got) == 6:
        reps, sizes, V, st, nd = got[0], got[1], got[2], got[3], got[4]
        basins = 0
        empty_pool = True
    else:
        reps, sizes, V, st, nd = got
        basins = int(np.asarray(V).shape[1])
        empty_pool = False
    rec = dict(requested_step=step, effective_stride=int(st), drawn_points=int(nd),
               basins=basins, n_points=int(C.shape[1]))
    if empty_pool:
        rec.update(status="no_axis", k=0, lines=np.zeros((6, 0)),
                   costs=np.zeros(0), stage="draw_pool", secs=round(time.time() - t0, 2),
                   reason="stage=draw_pool reason=empty_pool")
        return rec
    try:
        out = tx.select_lines(reps, sizes, w0, w1, C, CAP, None)
    except Exception as exc:                                    # noqa: BLE001
        rec.update(status="no_axis", k=0, lines=np.zeros((6, 0)),
                   costs=np.zeros(0), stage="select_lines",
                   secs=round(time.time() - t0, 2),
                   reason="stage=select_lines reason=%s: %s" % (type(exc).__name__, exc))
        return rec
    lines = np.asarray(out[0], dtype=float)
    costs = np.asarray(out[1], dtype=float).ravel()
    if lines.ndim != 2 or not np.all(np.isfinite(lines)):
        rec.update(status="no_axis", k=0, lines=np.zeros((6, 0)),
                   costs=np.zeros(0), stage="select_lines",
                   secs=round(time.time() - t0, 2),
                   reason="stage=select_lines reason=non_finite_candidates")
        return rec
    rec.update(status="ok", k=int(lines.shape[1]), lines=lines, costs=costs,
               stage="", secs=round(time.time() - t0, 2), reason="")
    return rec


def archive_gate(axis_file, archived):
    """(ok, rank_count_agree, max_abs, archived_sha) against the Ticket 19 pack."""
    if not os.path.isfile(archived):
        return 0, 0, "", ""
    sha_a = sp.sha_file(archived)
    if sp.sha_file(axis_file) == sha_a:
        return 1, 1, 0.0, sha_a
    a = read_axis_rows(archived)
    b = read_axis_rows(axis_file)
    agree = 1 if (len(a) == len(b) and len(a) > 0) else 0
    maxabs = 0.0
    if agree:
        for (pa, da), (pb, db) in zip(a, b):
            maxabs = max(maxabs, float(np.max(np.abs(pa - pb))),
                         float(np.max(np.abs(da - db))))
        ok = 1 if maxabs <= 1e-9 else 0
    else:
        ok = 0
    return ok, agree, maxabs, sha_a


def axis_rows(sid, arm, lines, costs):
    """Readout against the reference line; the estimator never sees it."""
    gt = dl.gt_axis("Pot_E_Piece_%d" % sid)
    gd = unit(gt[0:3])
    gp = np.asarray(gt[3:6], dtype=float)
    rows = []
    for k in range(lines.shape[1]):
        pos = np.asarray(lines[3:6, k], dtype=float)
        d = np.asarray(lines[0:3, k], dtype=float)
        oriented = ang_deg(d, gd)
        line = min(oriented, 180.0 - oriented)
        row = dict(sherd=sid, arm=arm, rank=k + 1,
                   oriented_deg="%.6f" % oriented, line_deg="%.6f" % line,
                   anchor_mm="%.6f" % line_dist(pos, gp, gd))
        for j, nmx in enumerate(("pos_x", "pos_y", "pos_z")):
            row[nmx] = "%.17g" % pos[j]
        for j, nmx in enumerate(("dir_x", "dir_y", "dir_z")):
            row[nmx] = "%.17g" % d[j]
        row["cost"] = "" if costs is None else "%.17g" % float(costs[k])
        rows.append(row)
    return rows


def best_ref(rows):
    if not rows:
        return "", ""
    b = min(rows, key=lambda r: (float(r["line_deg"]), int(r["rank"])))
    return b["line_deg"], b["anchor_mm"]


def change_rows(sid, arm, parent, res):
    pr, ar = res[(sid, parent)], res[(sid, arm)]
    lp, la = pr["lines"], ar["lines"]
    kp, ka = int(lp.shape[1]), int(la.shape[1])
    bp_l, bp_a = best_ref(pr["ax_rows"])
    ba_l, ba_a = best_ref(ar["ax_rows"])
    same = 1 if pr["sha"] == ar["sha"] else 0
    m = min(kp, ka)
    line_delta = ""
    anchor_delta = ""
    if m > 0:
        gt = dl.gt_axis("Pot_E_Piece_%d" % sid)
        gd = unit(gt[0:3])
        gp = np.asarray(gt[3:6], dtype=float)
        dl_max = 0.0
        da_max = 0.0
        for k in range(m):
            dp = unit(lp[0:3, k])
            da = unit(la[0:3, k])
            c = float(np.clip(abs(dp @ da), -1.0, 1.0))
            dl_max = max(dl_max, float(np.degrees(np.arccos(c))))
            pp = anchor_point(lp[3:6, k], gp, gd)
            pa = anchor_point(la[3:6, k], gp, gd)
            da_max = max(da_max, float(np.linalg.norm(pp - pa)))
        line_delta = "%.6f" % dl_max
        anchor_delta = "%.6f" % da_max
    return dict(sherd=sid, arm=arm, parent_arm=parent, k_parent=kp, k_arm=ka,
                axes_bytes_identical=same,
                best_ref_line_deg_parent=bp_l, best_ref_line_deg_arm=ba_l,
                best_ref_anchor_mm_parent=bp_a, best_ref_anchor_mm_arm=ba_a,
                max_rank_line_delta_deg=line_delta,
                max_rank_anchor_delta_mm=anchor_delta)


# ------------------------------------------------------------------ figures
def line_segments(tag, lines_, colour, style, lw, centre, span):
    """Anchor each axis line where it passes closest to the sherd centre."""
    out = []
    for k in range(lines_.shape[1]):
        d = unit(lines_[0:3, k])
        p0 = np.asarray(lines_[3:6, k], dtype=float)
        w = centre - p0
        t = float(np.dot(w, d))
        off = float(np.linalg.norm(w - t * d))
        h = 0.16 * span
        out.append(("%s%d" % (tag, k + 1), colour, style, lw,
                    p0 + (t - h) * d, p0 + (t + h) * d, off))
    return out


def render_compare(stem, rows, path):
    """Two geometry rows, two locked views each: base solid, comparison dashed."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    fig = plt.figure(figsize=(15.0, 15.0))
    for ri, R in enumerate(rows):
        base0, base1 = R["base"]
        n0 = unit(np.mean(base0[3:6], axis=1))
        azim = float(np.degrees(np.arctan2(n0[1], n0[0])))
        elev = 24.0
        pts = np.concatenate([base0[0:3], base1[0:3]], axis=1)
        centre = pts.mean(axis=1)
        span0 = float(np.max(pts.max(axis=1) - pts.min(axis=1)))
        segs = line_segments("s", R["base_lines"], "#08306b", "-", 2.2, centre, span0)
        segs += line_segments("c", R["cmp_lines"], "#e377c2", "--", 1.8, centre, span0)
        allpts = [pts.T]
        for s in segs:
            allpts += [s[4][None, :], s[5][None, :]]
        A = np.concatenate(allpts, axis=0)
        lo = A.min(axis=0).astype(float)
        hi = A.max(axis=0).astype(float)
        span = float(np.max(hi - lo))
        pad = 0.05 * span
        for panel in range(2):
            ax = fig.add_subplot(2, 2, 2 * ri + panel + 1, projection="3d")
            for fp, col in ((base0[0:3], "#b8b8b8"), (base1[0:3], "#707070")):
                st_ = max(1, int(fp.shape[1] // 4000))
                ax.scatter(fp[0, ::st_], fp[1, ::st_], fp[2, ::st_], s=1.2, c=col,
                           alpha=0.5, depthshade=False, linewidths=0)
            extra = R.get("extra")
            if extra is not None:
                for fp in extra:
                    st_ = max(1, int(fp.shape[1] // 4000))
                    ax.scatter(fp[0, ::st_], fp[1, ::st_], fp[2, ::st_], s=1.6,
                               c="#2ca25f", alpha=0.55, depthshade=False, linewidths=0)
            for label, colour, style, lw, e0, e1, off in segs:
                ax.plot([e0[0], e1[0]], [e0[1], e1[1]], [e0[2], e1[2]],
                        style, color=colour, linewidth=lw, alpha=0.95)
                side = 1.0 if label.startswith("s") else -1.0
                f_ = 0.14 if side > 0 else 0.86
                d = unit(e1 - e0)
                q = np.cross(d, np.array([0.0, 0.0, 1.0]))
                if float(np.linalg.norm(q)) < 1e-6:
                    q = np.cross(d, np.array([1.0, 0.0, 0.0]))
                q = unit(q) * (0.035 * span)
                at = e0 + f_ * (e1 - e0) + side * q
                ax.text(at[0], at[1], at[2], "%s %.0f mm" % (label, off),
                        fontsize=6.2, color=colour, fontweight="bold",
                        ha="left" if side > 0 else "right")
            bx, by, bz = lo[0] + pad, lo[1] + pad, lo[2] + pad
            ax.plot([bx, bx + 20.0], [by, by], [bz, bz], color="k", linewidth=2.6)
            ax.text(bx + 10.0, by, bz, "20 mm", fontsize=8, ha="center", va="bottom")
            ax.set_xlim(lo[0] - pad, hi[0] + pad)
            ax.set_ylim(lo[1] - pad, hi[1] + pad)
            ax.set_zlim(lo[2] - pad, hi[2] + pad)
            try:
                ax.set_box_aspect((hi[0] - lo[0] + 2 * pad, hi[1] - lo[1] + 2 * pad,
                                   hi[2] - lo[2] + 2 * pad))
            except Exception:                                   # noqa: BLE001
                pass
            ax.view_init(elev=elev, azim=azim + 180.0 * panel)
            ax.set_xlabel("x mm", fontsize=7)
            ax.set_ylabel("y mm", fontsize=7)
            ax.set_zlabel("z mm", fontsize=7)
            ax.tick_params(labelsize=6)
            if panel == 0:
                from matplotlib.lines import Line2D
                handles = [Line2D([], [], color="#08306b", lw=2.2,
                                  label="%s axis, at closest pass" % R["base_name"]),
                           Line2D([], [], color="#e377c2", lw=1.8, ls="--",
                                  label="%s axis, at closest pass" % R["cmp_name"])]
                if extra is not None:
                    handles.append(Line2D([], [], color="#2ca25f", marker="o", ls="",
                                          ms=3, label="%s points" % R["cmp_name"]))
                ax.legend(handles=handles, fontsize=7, loc="upper left")
            ax.set_title("%s\n%s" % (R["title"],
                                      "view 1, face-0 side" if panel == 0
                                      else "view 2, face-1 side"), fontsize=9)
    fig.suptitle("%s\nranked candidate axes drawn where each line passes closest to the "
                 "sherd (label = rank and that offset in mm); grey points are the two wall "
                 "faces of the solid arm\n"
                 "top row: OWN vs OWN_MATCHED_TO_AUTHOR; bottom row: OWN_COMMON_VOXEL "
                 "(solid) vs AUTHOR_COMMON_VOXEL (dashed, green points)" % stem,
                 fontsize=9.5, y=0.995)
    fig.subplots_adjust(left=0.01, right=0.99, top=0.925, bottom=0.01, wspace=0.01,
                        hspace=0.06)
    fig.savefig(path, dpi=150)
    plt.close(fig)


# ------------------------------------------------------------------- sources
def source_rows(run):
    rows = []
    for kind, name, path in (
            ("root", "ship", SHIP), ("root", "t19", T19), ("root", "impl", IMPL)):
        rows.append(dict(kind=kind, name=name, path=path, sha256=""))
    for stem, sid in STEMS:
        own, auth = source_paths(stem)
        for f in (0, 1):
            rows.append(dict(kind="input_wall", name="OWN %s S%d" % (stem, f),
                             path=own[f], sha256=sp.sha_file(own[f])))
            rows.append(dict(kind="input_wall", name="AUTHOR %s Surface_%d" % (stem, f),
                             path=auth[f], sha256=sp.sha_file(auth[f])))
        gt = os.path.join(dl.GT_DIR, stem + "_Axis.xyz")
        rows.append(dict(kind="reference", name="GT %s" % stem, path=gt,
                         sha256=sp.sha_file(gt)))
        for src in ("own", "authors"):
            p = archive_path(sid, src)
            rows.append(dict(kind="archive_axis",
                             name="T19 %s %s" % ("OWN" if src == "own" else "AUTHOR", stem),
                             path=p, sha256=sp.sha_file(p)))
    code = [os.path.join(SHIP, "work", "t03_lib.py"),
            os.path.join(SHIP, "work", "t03_extract.py"),
            os.path.join(IMPL, "scripts", "run_benchmark_172.py")]
    code += sorted(glob.glob(os.path.join(IMPL, "sfs_axes", "*.py")))
    code += [os.path.join(HERE, "sampling05.py"), os.path.join(HERE, "extract05.py"),
             os.path.join(HERE, "check05.py"), os.path.join(HERE, "submit.sbatch")]
    for p in code:
        rows.append(dict(kind="code", name=os.path.basename(p), path=p,
                         sha256=sp.sha_file(p)))
    return rows


# ---------------------------------------------------------------------- main
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", required=True)
    ap.add_argument("--fixtures", action="store_true")
    ap.add_argument("--no-render", action="store_true")
    args = ap.parse_args()
    run = os.path.abspath(args.run)
    ev = os.path.join(run, "evidence")
    idxdir = os.path.join(ev, "indices")
    axroot = os.path.join(run, "out", "axes05")
    rdir = os.path.join(run, "renders")
    for d in (ev, idxdir, axroot, rdir):
        os.makedirs(d, exist_ok=True)

    if args.fixtures:
        rows = sp.fixture_suite()
        write_tsv(os.path.join(ev, "fixtures.tsv"), rows, ["fixture", "status", "detail"])
        bad = [r for r in rows if r["status"] != "PASS"]
        for r in rows:
            log("fixture %-24s %s  %s" % (r["fixture"], r["status"], r["detail"]))
        log("fixtures %d/%d PASS" % (len(rows) - len(bad), len(rows)))
        return 1 if bad else 0

    started = datetime.datetime.now().isoformat(timespec="seconds")
    inputs, runs, axes, changes, renders = [], [], [], [], []
    res = {}
    gate_fail = []

    for stem, sid in STEMS:
        arms = build_arms(stem)
        own_src, auth_src = source_paths(stem)
        src_of = {"own": own_src, "authors": auth_src}
        native = {"own": [arms["OWN"][0][0], arms["OWN"][0][1]],
                  "authors": [arms["AUTHOR"][0][0], arms["AUTHOR"][0][1]]}
        axdir = os.path.join(axroot, stem)
        os.makedirs(axdir, exist_ok=True)
        for arm in ARMS:
            source = ARM_SPEC[arm][0]
            walls, idx = arms[arm]
            for f in (0, 1):
                w = walls[f]
                n = int(w.shape[1])
                npz = os.path.join(idxdir, "E%d_%s_f%d.npz" % (sid, arm, f))
                np.savez(npz, idx=np.asarray(idx[f], dtype=np.int64),
                         wall=np.asarray(w, dtype=np.float64),
                         source=np.array(source), step=np.array(ARM_SPEC[arm][1]))
                np_ = int(native[source][f].shape[1])
                inputs.append(dict(
                    sherd=sid, arm=arm, face=f, native_points=np_, points=n,
                    duplicate_xyz=sp.duplicate_count(w[0:3].T),
                    retained_fraction="%.9f" % (float(n) / np_ if np_ else 0.0),
                    xyz_sha256=sp.matrix_sha(w[0:3].T),
                    normals_sha256=sp.matrix_sha(w[3:6].T),
                    source_sha256=sp.sha_file(src_of[source][f])))
            rec = run_arm(arm, walls)
            axfile = os.path.join(axdir, "%s_Axis.xyz" % arm)
            if rec["k"] > 0:
                tx.write_lines(axfile, rec["lines"])
                rec["sha"] = sp.sha_file(axfile)
            else:
                open(axfile, "w").close()
                rec["sha"] = sp.sha_file(axfile)
            rec["axis_file"] = axfile
            rec["walls"] = walls
            rec["ax_rows"] = axis_rows(sid, arm, rec["lines"], rec["costs"])
            axes.extend(rec["ax_rows"])
            row = dict(sherd=sid, arm=arm, status=rec["status"], k=rec["k"],
                       axes_sha256=rec["sha"],
                       archive_ok="", requested_step=rec["requested_step"],
                       effective_stride=rec["effective_stride"],
                       drawn_points=rec["drawn_points"], basins=rec["basins"],
                       reason=rec["reason"], secs=rec["secs"])
            if arm in NATIVE:
                ok, agree, maxabs, sha_a = archive_gate(axfile, archive_path(sid, source))
                row["archive_ok"] = ok
                row["archived_sha256"] = sha_a
                row["archive_rank_count_agree"] = agree
                row["archive_max_abs"] = ("%.17g" % maxabs) if agree else ""
                if not ok:
                    gate_fail.append((sid, arm))
            runs.append(row)
            res[(sid, arm)] = rec
            log("%s %-22s k=%d stride=%d drawn=%d basins=%d arch=%s secs=%.1f"
                % (stem, arm, rec["k"], rec["effective_stride"], rec["drawn_points"],
                   rec["basins"], row["archive_ok"], rec["secs"]))
        for arm in NON_NATIVE:
            parent = "AUTHOR" if ARM_SPEC[arm][0] == "authors" else "OWN"
            changes.append(change_rows(sid, arm, parent, res))
        if not args.no_render:
            png = os.path.join(rdir, stem + ".png")
            render_compare(stem, [
                dict(title="OWN (solid) vs OWN_MATCHED_TO_AUTHOR (dashed)",
                     base_name="OWN", cmp_name="OWN_MATCHED_TO_AUTHOR",
                     base=res[(sid, "OWN")]["walls"],
                     base_lines=res[(sid, "OWN")]["lines"],
                     cmp_lines=res[(sid, "OWN_MATCHED_TO_AUTHOR")]["lines"]),
                dict(title="OWN_COMMON_VOXEL (solid) vs AUTHOR_COMMON_VOXEL (dashed)",
                     base_name="OWN_COMMON_VOXEL", cmp_name="AUTHOR_COMMON_VOXEL",
                     base=res[(sid, "OWN_COMMON_VOXEL")]["walls"],
                     extra=res[(sid, "AUTHOR_COMMON_VOXEL")]["walls"],
                     base_lines=res[(sid, "OWN_COMMON_VOXEL")]["lines"],
                     cmp_lines=res[(sid, "AUTHOR_COMMON_VOXEL")]["lines"]),
            ], png)
            renders.append(dict(sherd=sid, path=os.path.relpath(png, run), scale_bar_mm=20))
            log("rendered %s" % png)

    write_tsv(os.path.join(ev, "inputs.tsv"), inputs, INPUT_COLS)
    write_tsv(os.path.join(ev, "runs.tsv"), runs, RUN_COLS)
    write_tsv(os.path.join(ev, "axes.tsv"), axes, AXIS_COLS)
    write_tsv(os.path.join(ev, "changes.tsv"), changes, CHANGE_COLS)
    write_tsv(os.path.join(ev, "renders.tsv"), renders, RENDER_COLS)
    write_tsv(os.path.join(ev, "sources.tsv"), source_rows(run), SOURCE_COLS)

    run_json = dict(
        run=run, job_id=os.environ.get("SLURM_JOB_ID", ""),
        started=started, finished=datetime.datetime.now().isoformat(timespec="seconds"),
        ship=SHIP, t19=T19, impl=IMPL, seeds=SEEDS, cap=CAP, step=10,
        stride1=1, cut_mm=sp.CUT_MM, voxel_mm=sp.VOXEL_MM,
        arms=ARMS, stems=[s for s, _ in STEMS],
        python=platform.python_version(), numpy=np.__version__,
        git=os.environ.get("T05_GIT", ""), tag=os.environ.get("T05_TAG", ""))
    with open(os.path.join(run, "run.json"), "w") as fh:
        json.dump(run_json, fh, indent=1)
        fh.write("\n")

    if gate_fail:
        log("ARCHIVE GATE FAILED on %s -- experiment is inconclusive; "
            "arms are not interpreted" % (gate_fail,))
        return 3
    log("done: %d inputs rows, %d runs, %d axis rows, %d changes"
        % (len(inputs), len(runs), len(axes), len(changes)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
