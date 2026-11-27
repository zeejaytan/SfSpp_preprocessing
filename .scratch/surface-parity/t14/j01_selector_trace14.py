#!/usr/bin/env python3
"""Ticket 14 Part B: which stage of the frozen SHIP selector drops the donor line.

Eight wall representations of the same piece (Pot_J_Piece_01) through the same frozen
selector, every intermediate candidate list recorded *before* the tau = 1.2 keep rule,
so the k = 1 vs k = 3 split between OWN_VOXEL_1MM and AUTHOR_VOXEL_1MM is read at the
stage that causes it and not inferred from the final axis files.

The selector is imported read-only from the Ticket 03 run tree, and the three stages of
the joint selector are reproduced with their own constants (ARM_REFINE_K, ARM_TAU,
LINE_RULE_KMAX, PROFILE_BASINS, PROFILE_NREF, PROFILE_NORMAL_ITERS, PROFILE_DEDUP_DEG,
JOINT_DEDUP_DEG).  Every reproduction is checked against the frozen function it copies:
a mismatch fails the job.

Read-only.  Writes only under --run:
  evidence/j01_arm_trace.tsv                 8 arms x 20 columns
  renders/J01_selector_trace.png
  logs/j01_selector_trace_detail.json        every candidate of every stage
  logs/j01_selector_trace14.log
"""
import argparse
import json
import os
import sys
import time
from multiprocessing import Pool

import numpy as np

STEM = "Pot_J_Piece_01"

T13_WALLS = ("/data/gpfs/projects/punim2657/SfSpp/runs/"
             "20261126-1500_cf88609_t13-diagnose/j01/walls")
SHIP = "/data/gpfs/projects/punim2657/SfSpp/runs/20261121-1319_2e951d9_t03-ship"
IMPL = os.path.join(SHIP, "work", "impl_t03")

DONOR_DIR = np.array([0.992676, 0.042854, 0.112950], dtype=float)
DONOR_DIR = DONOR_DIR / np.linalg.norm(DONOR_DIR)
DONOR_PT = np.array([-53.313366, -28.804402, 479.479140], dtype=float)
CENTROID = np.array([30.107, 12.692, 452.566], dtype=float)

SEEDS = 10
STEP = 10
CAP = 6

ARMS = ["AUTHOR", "OWN_T09", "OWN_SHARED_1MM", "AUTHOR_SHARED_1MM",
        "OWN_VOXEL_1MM", "AUTHOR_VOXEL_1MM",
        "VOXEL_OWN_XYZ_AUTH_N", "VOXEL_AUTH_XYZ_OWN_N"]
VOXEL_OWN = "OWN_VOXEL_1MM"
VOXEL_AUTH = "AUTHOR_VOXEL_1MM"

TRACE_COLS = ["arm", "n_basins", "pool_min_donor_deg", "top60_min_donor_deg",
              "normal_k", "normal_r0_donor_deg", "normal_pre_tau_donor_deg",
              "normal_pre_tau_ratio", "thick_k", "thick_r0_donor_deg",
              "thick_pre_tau_donor_deg", "thick_pre_tau_ratio", "ship_k",
              "ship_r0_donor_deg", "ship_pre_tau_donor_deg", "ship_pre_tau_ratio",
              "k_final", "final_best_donor_deg", "final_best_donor_mm",
              "final_best_gt_deg"]
STAGES = ["pool", "top60", "normal_pre_tau", "thick_pre_tau", "ship_pre_tau", "final"]
TAB = chr(9)
NL = chr(10)
RUN = ""

for _p in (os.path.join(SHIP, "work"), IMPL, os.path.join(IMPL, "scripts")):
    if _p not in sys.path:
        sys.path.insert(0, _p)
os.environ.setdefault("SFS_IMPL", IMPL)

import t03_lib as dl  # noqa: E402
from sfs_axes.io_axes import direction_angle_deg  # noqa: E402
from sfs_axes import select as sel  # noqa: E402
from sfs_axes import joint as jt  # noqa: E402
from sfs_axes import meridian as md  # noqa: E402
from sfs_axes import profile as pf  # noqa: E402


def log(msg):
    print("[trace14] " + msg, flush=True)


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

    Two formats occur: plain ASCII six columns (the Authors' released Surfaces
    and the saved Ticket 13 walls) and PCL-generated ASCII PLY with named
    properties (the t09 own surfaces).  Chosen by reading the header.
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


def donor_deg(v):
    return float(direction_angle_deg(np.asarray(v[0:3], dtype=float), DONOR_DIR))


def perp_mm(v):
    r = np.asarray(v[3:6], dtype=float) - DONOR_PT
    r = r - float(r @ DONOR_DIR) * DONOR_DIR
    return float(np.linalg.norm(r))


def gt_deg(v, gt):
    return float(direction_angle_deg(np.asarray(v[0:3], dtype=float), gt[0:3]))


def load_arm(arm):
    """(C0, C1, info) for one arm, from the six saved Ticket 13 walls."""
    def pair(name):
        return (load_wall(os.path.join(T13_WALLS, name + ".S0.xyz")),
                load_wall(os.path.join(T13_WALLS, name + ".S1.xyz")))

    info = {"source": arm}
    if arm in (VOXEL_OWN, VOXEL_AUTH) or arm in ARMS[:6]:
        c0, c1 = pair(arm)
        return c0, c1, info
    o0, o1 = pair(VOXEL_OWN)
    a0, a1 = pair(VOXEL_AUTH)
    for tag, P, Q in (("S0", o0, a0), ("S1", o1, a1)):
        if P.shape != Q.shape:
            raise SystemExit("[trace14] FAIL %s shape %r vs %r"
                             % (tag, P.shape, Q.shape))
        info["align_" + tag] = {
            "points": int(P.shape[1]),
            "max_abs_xyz_diff_mm": float(np.max(np.abs(P[0:3] - Q[0:3]))),
            "max_abs_normal_diff": float(np.max(np.abs(P[3:6] - Q[3:6]))),
        }
    out0 = np.array(o0 if arm == "VOXEL_OWN_XYZ_AUTH_N" else a0, dtype=float,
                    copy=True)
    n0 = np.array(a0 if arm == "VOXEL_OWN_XYZ_AUTH_N" else o0, dtype=float)
    out1 = np.array(o1 if arm == "VOXEL_OWN_XYZ_AUTH_N" else a1, dtype=float,
                    copy=True)
    n1 = np.array(a1 if arm == "VOXEL_OWN_XYZ_AUTH_N" else o1, dtype=float)
    out0[3:6] = n0[3:6]
    out1[3:6] = n1[3:6]
    info["source"] = ("xyz OWN_VOXEL_1MM + normals AUTHOR_VOXEL_1MM"
                      if arm == "VOXEL_OWN_XYZ_AUTH_N"
                      else "xyz AUTHOR_VOXEL_1MM + normals OWN_VOXEL_1MM")
    return out0, out1, info


def finish_stage(lines, costs, C, cap=CAP, orient=True):
    """Per-candidate angles + the keep_lines cut, on the refined candidate list."""
    lines = np.asarray(lines, dtype=float)
    costs = np.asarray(costs, dtype=float).ravel()
    if lines.size == 0 or lines.shape[1] == 0:
        return None
    dn = np.array([donor_deg(lines[:, k]) for k in range(lines.shape[1])])
    gt = dl.gt_axis(STEM)
    ga = np.array([gt_deg(lines[:, k], gt) for k in range(lines.shape[1])])
    best = int(np.argmin(dn))
    idx = sel.keep_lines(costs, tau=sel.LINE_RULE_TAU, kmax=sel.LINE_RULE_KMAX)[:cap]
    kept = lines[:, idx]
    if orient:
        kept = sel.orient_base_axis(kept, C)
    return {"pre_lines": lines, "pre_costs": costs, "donor": dn, "gt": ga,
            "best": best, "kept_idx": [int(i) for i in idx], "kept_lines": kept,
            "kept_costs": costs[idx], "r0_donor": float(dn[0]),
            "pre_tau_donor": float(dn[best]),
            "pre_tau_ratio": float(costs[best] / costs[0]),
            "k": int(len(idx))}


def trace_select(reps, sizes, walls, C, size, cost_fn, refine_fn, cap=CAP):
    """jt._select, copied line for line, returning the pre-tau candidate list too."""
    cs = jt._candidates(reps, sizes)
    costs = np.array([cost_fn(cs[:, i]) for i in range(cs.shape[1])], dtype=float)
    short = jt._dedup(cs, costs)[:jt.ARM_REFINE_K]
    refined, rcost = [], []
    for i in short:
        v = jt._bounded(cs[:, i], refine_fn(cs[:, i]), size, C)
        if not np.all(np.isfinite(v)):
            continue
        refined.append(v)
        rcost.append(float(cost_fn(v)))
    if not refined:
        return None
    lines = np.column_stack(refined)
    keep = jt._dedup(lines, rcost)
    lines = lines[:, keep]
    costs = np.asarray(rcost, dtype=float)[keep]
    return finish_stage(lines, costs, C, cap=cap, orient=True)


def trace_shipped(reps, sizes, c0, c1, C, cap=CAP):
    """sel.select_union_lines' own body (tri_select=False), pre-keep_lines."""
    n = C.shape[1]
    centre = C[0:3].mean(axis=1)
    size = float(np.linalg.norm(C[0:3].max(axis=1) - C[0:3].min(axis=1)))
    walls = [pf.stride(c0), pf.stride(c1)]
    Cr = C[:, 0:n:max(1, int(np.ceil(n / sel.PROFILE_NREF)))]
    lines, costs = [], []
    for j in np.argsort(-np.asarray(sizes, dtype=float), kind="stable")[
            :sel.PROFILE_BASINS]:
        raw = reps[:, j]
        ref = sel.refine_axis_normalized(raw, Cr,
                                         max_iters=sel.PROFILE_NORMAL_ITERS,
                                         tolerance=1e-6)
        lines += [raw, ref]
        costs += [pf.profile_cost(raw, walls), pf.profile_cost(ref, walls)]
    vt, c = sel.rank_by_profile(np.column_stack(lines), walls, centre, size,
                                costs=costs)
    vt, c = vt[:, :CAP], np.asarray(c, dtype=float)[:CAP]
    return finish_stage(vt, c, C, cap=cap, orient=False)


def maxdiff(A, B):
    if A is None or B is None:
        return float("nan")
    A = np.asarray(A, dtype=float)
    B = np.asarray(B, dtype=float)
    if A.shape != B.shape:
        return float("inf")
    return float(np.max(np.abs(A - B))) if A.size else 0.0


def trace_arm(arm):
    t0 = time.time()
    c0, c1, info = load_arm(arm)
    C = np.concatenate([c0, c1], axis=1)
    reps, sizes, V, st, nd = dl.draw_pool(C, seeds=SEEDS, step=STEP)
    sizes = np.asarray(sizes, dtype=float)
    n_basins = int(reps.shape[1])
    dn_reps = np.array([donor_deg(reps[:, j]) for j in range(n_basins)])
    top = np.argsort(-sizes, kind="stable")[:60]
    pool_min = float(dn_reps.min())
    top60_min = float(dn_reps[top].min())

    n = C.shape[1]
    size = float(np.linalg.norm(C[0:3].max(axis=1) - C[0:3].min(axis=1)))
    walls = [pf.stride(c0), pf.stride(c1)]

    def cost_n(v):
        return float(np.mean([md.normal_cost(v, W, md.NORMAL_WIDTH) for W in walls]))

    def refine_n(v):
        return md.refine_axis_normal(v, C, width=md.NORMAL_WIDTH)

    def cost_t(v):
        return float(np.mean([md.profile_thickness_cost(v, [W], normal_consistent=True)
                              for W in walls]))

    def refine_t(v):
        return md.refine_axis_profile_thickness(v, walls, centre, size,
                                                normal_consistent=True)[0]

    centre = C[0:3].mean(axis=1)
    tr_n = trace_select(reps, sizes, walls, C, size, cost_n, refine_n)
    tr_t = trace_select(reps, sizes, walls, C, size, cost_t, refine_t)
    tr_s = trace_shipped(reps, sizes, c0, c1, C)
    for tag, tr in (("normal", tr_n), ("thick", tr_t), ("ship", tr_s)):
        if tr is None:
            raise SystemExit("[trace14] FAIL arm %s stage %s produced no lines"
                             % (arm, tag))

    # The frozen functions of the same stages, for a fidelity check.
    fr_n = jt.normal_arm(reps, sizes, walls, C, size)
    fr_t = jt.thickness_arm(reps, sizes, walls, C, size)
    fr_s = sel.select_union_lines(reps, sizes, c0, c1, C, jt.JOINT_MAX_CANDIDATES,
                                  line_rule=sel.LINE_RULE, base_orient=False,
                                  tri_select=False)
    checks = {
        "normal_maxdiff": maxdiff(tr_n["kept_lines"], None if fr_n is None else fr_n[0]),
        "thick_maxdiff": maxdiff(tr_t["kept_lines"], None if fr_t is None else fr_t[0]),
        "ship_maxdiff": maxdiff(tr_s["kept_lines"], None if fr_s is None else fr_s[0]),
    }

    fl, fc = sel.select_union_lines(reps, sizes, c0, c1, C,
                                    jt.JOINT_MAX_CANDIDATES, tri_select=True)
    fl = np.asarray(fl, dtype=float)
    if fl.ndim == 1:
        fl = fl.reshape(6, 1)
    gt = dl.gt_axis(STEM)
    final_dn = np.array([donor_deg(fl[:, k]) for k in range(fl.shape[1])])
    final_mm = np.array([perp_mm(fl[:, k]) for k in range(fl.shape[1])])
    final_gt = np.array([gt_deg(fl[:, k], gt) for k in range(fl.shape[1])])
    fb = int(np.argmin(final_dn))

    row = {
        "arm": arm, "n_basins": n_basins,
        "pool_min_donor_deg": pool_min, "top60_min_donor_deg": top60_min,
        "normal_k": tr_n["k"], "normal_r0_donor_deg": tr_n["r0_donor"],
        "normal_pre_tau_donor_deg": tr_n["pre_tau_donor"],
        "normal_pre_tau_ratio": tr_n["pre_tau_ratio"],
        "thick_k": tr_t["k"], "thick_r0_donor_deg": tr_t["r0_donor"],
        "thick_pre_tau_donor_deg": tr_t["pre_tau_donor"],
        "thick_pre_tau_ratio": tr_t["pre_tau_ratio"],
        "ship_k": tr_s["k"], "ship_r0_donor_deg": tr_s["r0_donor"],
        "ship_pre_tau_donor_deg": tr_s["pre_tau_donor"],
        "ship_pre_tau_ratio": tr_s["pre_tau_ratio"],
        "k_final": int(fl.shape[1]),
        "final_best_donor_deg": float(final_dn[fb]),
        "final_best_donor_mm": float(final_mm[fb]),
        "final_best_gt_deg": float(final_gt.min()),
    }
    detail = {
        "arm": arm, "info": info, "wall_points": [int(c0.shape[1]), int(c1.shape[1])],
        "draw_pool": {"seeds": SEEDS, "step": STEP, "effective_stride": int(st),
                      "drawn_points": int(nd), "n_basins": n_basins},
        "pool": {"min_donor_deg": pool_min, "top60_min_donor_deg": top60_min,
                 "top60_cut_size": float(sizes[top][-1]),
                 "basins_rows": [
                     {"j": int(j), "size": float(sizes[j]),
                      "donor_deg": float(dn_reps[j]),
                      "r0_donor_deg": float(donor_deg(reps[:, j]))}
                     for j in np.argsort(-sizes, kind="stable")[:60]]},
        "wall_clock_s": None,
    }
    for tag, tr, key in (("normal", tr_n, "normal"), ("thick", tr_t, "thick"),
                         ("ship", tr_s, "ship")):
        detail[tag] = {
            "k": tr["k"],
            "kept_idx": tr["kept_idx"],
            "candidates": [
                {"i": i, "cost": float(tr["pre_costs"][i]),
                 "cost_ratio": float(tr["pre_costs"][i] / tr["pre_costs"][0]),
                 "donor_deg": float(tr["donor"][i]), "gt_deg": float(tr["gt"][i]),
                 "kept": bool(i in tr["kept_idx"])}
                for i in range(tr["pre_lines"].shape[1])],
            "kept_costs": [float(x) for x in tr["kept_costs"]],
            "best_donor_candidate": tr["best"],
            "checks": checks,
        }
    detail["final"] = {
        "k": int(fl.shape[1]), "costs": [float(x) for x in np.asarray(fc).ravel()],
        "donor_deg": [float(x) for x in final_dn],
        "donor_mm": [float(x) for x in final_mm],
        "gt_deg": [float(x) for x in final_gt],
        "best_donor_rank": fb,
        "candidates": [
            {"i": k, "donor_deg": float(final_dn[k]), "donor_mm": float(final_mm[k]),
             "gt_deg": float(final_gt[k]),
             "cost": float(np.asarray(fc).ravel()[k]) if k < np.asarray(fc).size else None}
            for k in range(fl.shape[1])],
    }
    checks_ok = all(np.isfinite(v) and v <= 1e-9 for v in checks.values())
    detail["checks"] = dict(checks, ok=bool(checks_ok))
    detail["wall_clock_s"] = round(time.time() - t0, 2)
    log("%-22s basins=%3d pool_min=%6.2f top60=%6.2f | n k=%d pre=%6.2f r=%7.3f"
        " | t k=%d pre=%6.2f r=%7.3f | s k=%d pre=%6.2f r=%7.3f | final k=%d d=%.2f"
        "%s" % (arm, n_basins, pool_min, top60_min, tr_n["k"],
                tr_n["pre_tau_donor"], tr_n["pre_tau_ratio"], tr_t["k"],
                tr_t["pre_tau_donor"], tr_t["pre_tau_ratio"], tr_s["k"],
                tr_s["pre_tau_donor"], tr_s["pre_tau_ratio"], fl.shape[1],
                row["final_best_donor_deg"], "" if checks_ok else "  CHECK-FAIL"))
    return row, detail, checks_ok, checks


def _worker(arm):
    try:
        return trace_arm(arm)
    except Exception:
        import traceback
        traceback.print_exc()
        raise


def write_tsv(path, cols, rows):
    with open(path, "w") as fh:
        fh.write(TAB.join(cols) + NL)
        for r in rows:
            fh.write(TAB.join(cell(r[c]) for c in cols) + NL)


def cell(v):
    if isinstance(v, float):
        if not np.isfinite(v):
            raise SystemExit("[trace14] FAIL non-finite value in a TSV row")
        return "%.4f" % v
    return str(v)


def render(rows, detail, path):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    arms = [r["arm"] for r in rows]
    fig = plt.figure(figsize=(17.0, 8.6), dpi=180)
    axl = fig.add_subplot(1, 2, 1)
    axr = fig.add_subplot(1, 2, 2)

    keys = {"pool": "pool_min_donor_deg", "top60": "top60_min_donor_deg",
            "normal_pre_tau": "normal_pre_tau_donor_deg",
            "thick_pre_tau": "thick_pre_tau_donor_deg",
            "ship_pre_tau": "ship_pre_tau_donor_deg",
            "final": "final_best_donor_deg"}
    cmap = plt.get_cmap("tab10")
    xs = np.arange(len(STAGES))
    for i, r in enumerate(rows):
        ys = [r[keys[s]] for s in STAGES]
        axl.plot(xs, ys, marker="o", ms=5, lw=1.5, color=cmap(i % 10),
                 label="%s (k_final=%d)" % (r["arm"], r["k_final"]))
    axl.set_xticks(xs)
    axl.set_xticklabels(["pool\n(all basins)", "top-60\nbasins",
                        "normal\npre-tau", "thickness\npre-tau",
                        "shipped\npre-tau", "final\nmerged"], fontsize=8.5)
    axl.set_ylabel("minimum angle to the Ticket 13 donor line (deg)", fontsize=9)
    axl.set_ylim(0, 90)
    axl.grid(alpha=0.3, lw=0.5)
    axl.set_title("Minimum donor-line angle at each stage\n"
                  "(8 arms, frozen SHIP selector; lower is closer to the Authors' "
                  "face-1 wall)", fontsize=10)
    axl.legend(fontsize=7.5, loc="upper center", ncol=2, framealpha=0.9)

    marks = {"normal_pre_tau_ratio": ("o", "#4c72b0", "normal_arm"),
             "thick_pre_tau_ratio": ("s", "#1b9e77", "thickness_arm"),
             "ship_pre_tau_ratio": ("^", "#d95f02", "shipped select_union_lines")}
    xs2 = np.arange(len(rows))
    for key, (mk, col, lab) in marks.items():
        axr.scatter(xs2, [r[key] for r in rows], marker=mk, s=64, color=col,
                    label=lab, zorder=3)
    axr.axhline(1.2, color="crimson", ls="--", lw=1.4,
                label="tau = 1.2 keep cut (cost <= 1.2 x cost[0])")
    axr.set_yscale("log")
    axr.set_xticks(xs2)
    axr.set_xticklabels([a.replace("_", "\n", 1) if len(a) > 16 else a for a in arms],
                        fontsize=7.5, rotation=20, ha="right")
    axr.set_ylabel("cost / cost[0] of the best-donor refined candidate", fontsize=9)
    axr.grid(alpha=0.3, lw=0.5, which="both")
    axr.set_title("Would the keep rule admit the best-donor candidate?\n"
                  "above the dashed line = dropped by keep_lines", fontsize=10)
    for i, r in enumerate(rows):
        lab = "%.1f deg" % r["thick_pre_tau_donor_deg"]
        axr.annotate(lab, (xs2[i], r["thick_pre_tau_ratio"]),
                     textcoords="offset points", xytext=(6, 6), fontsize=6.5)
    axr.legend(fontsize=7.5, loc="upper left")
    fig.suptitle("J01 selector trace: the same piece through 8 wall representations "
                 "and the frozen SHIP selector", fontsize=11.5)
    fig.tight_layout(rect=(0, 0, 1, 0.94))
    fig.savefig(path)
    plt.close(fig)
    return os.path.getsize(path)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", required=True)
    ap.add_argument("--jobs", type=int, default=8)
    ap.add_argument("--arms", default="")
    a = ap.parse_args()
    run = os.path.abspath(a.run)
    for d in ("renders", "evidence", "logs", "out"):
        os.makedirs(os.path.join(run, d), exist_ok=True)
    arms = [x for x in a.arms.split(",") if x] or ARMS
    log("arms: %s" % (", ".join(arms),))
    with Pool(max(1, min(a.jobs, len(arms)))) as pool:
        out = pool.map(_worker, arms, chunksize=1)
    rows = [r for r, _d, _ok, _c in out]
    details = [d for _r, d, _ok, _c in out]
    checks = [c for _r, _d, _ok, c in out]
    ok = all(f for _r, _d, f, _c in out)
    order = {arm: i for i, arm in enumerate(ARMS)}
    rows.sort(key=lambda r: order[r["arm"]])
    details.sort(key=lambda d: order[d["arm"]])
    if len(rows) != 8:
        raise SystemExit("[trace14] FAIL %d rows for %d arms" % (len(rows), 8))

    tsv = os.path.join(run, "evidence", "j01_arm_trace.tsv")
    write_tsv(tsv, TRACE_COLS, rows)
    with open(tsv) as fh:
        n = sum(1 for _ in fh) - 1
    log("wrote %s (%d data rows)" % (tsv, n))
    if n != 8:
        raise SystemExit("[trace14] FAIL expected 8 rows, wrote %d" % n)

    with open(os.path.join(run, "logs", "j01_selector_trace_detail.json"), "w") as fh:
        json.dump({"stem": STEM, "arms": details,
                   "donor_dir": [float(x) for x in DONOR_DIR],
                   "donor_pt": [float(x) for x in DONOR_PT],
                   "centroid": [float(x) for x in CENTROID],
                   "seeds": SEEDS, "step": STEP,
                   "tau": float(sel.LINE_RULE_TAU),
                   "kmax": int(sel.LINE_RULE_KMAX),
                   "basins": int(sel.PROFILE_BASINS),
                   "checks": checks}, fh, indent=1)
    png = os.path.join(run, "renders", "J01_selector_trace.png")
    nbytes = render(rows, details, png)
    log("render %s (%d bytes)" % (png, nbytes))
    summary = {"rows": rows, "render_bytes": nbytes, "fidelity_ok": bool(ok)}
    with open(os.path.join(run, "logs", "j01_trace_summary.json"), "w") as fh:
        json.dump(summary, fh, indent=1)
    if not ok:
        raise SystemExit("[trace14] FAIL stage reproduction does not match the "
                         "frozen selector; see logs/j01_selector_trace_detail.json")
    log("TRACE14-OK")
    return 0


if __name__ == "__main__":
    sys.exit(main() or 0)
