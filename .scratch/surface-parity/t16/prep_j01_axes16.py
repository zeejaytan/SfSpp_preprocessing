#!/usr/bin/env python3
"""Ticket 16: five Pot_J_Piece_01 axis candidates on handle-deleted own walls.

The question this feeds: after the handle is removed from OUR own J01 surface, does the
Pot J assembly match or beat the Authors' 16/21 control?  One axis per arm goes into the
exact pinned Hierarchy-T13 assembler (J02..J12 axes and every breakline byte-identical to
Ticket 13 T09_ALL).

Arms (all on the frozen SHIP selector, nothing in sfs_axes/ is edited):

  CTL_T09_WITH_AUTHOR_J01  the exact Ticket 13 AUTHOR J01 axis (positive control, 17/21 there)
  OWN_NO_HANDLE_SHIP       OWN_SHARED_1MM walls -> unchanged joint.select_joint_lines
  OWN_NO_HANDLE_THICKSEC   OWN_SHARED_1MM walls -> normal_arm + thickness_arm + shipped,
                           merged with merge_with_thick_secondaries (thickness secondaries
                           offered before the shipped ones), oriented once
  OWN_VOXEL_THICKSEC       OWN_VOXEL_1MM walls -> the same merge
  OWN_S0_ONLY_SHIP         OWN_T09 S0 alone (C0=C1=C=S0) -> unchanged select_joint_lines

The walls are the ones Ticket 14 saved (T13/j01/walls), so this ticket does not rebuild a
surface; it only re-selects.  Evidence: evidence/j01_axes16.tsv (5 rows, literal tabs) plus
logs/j01_axes16_detail.json (every candidate's angles and cost, and the pre-merge thickness
candidates the merge had to choose between).

Read-only inputs; writes only under --run.
"""
import argparse
import hashlib
import json
import os
import sys

import numpy as np

SHIP = "/data/gpfs/projects/punim2657/SfSpp/runs/20261121-1319_2e951d9_t03-ship"
IMPL = os.path.join(SHIP, "work", "impl_t03")
T13 = "/data/gpfs/projects/punim2657/SfSpp/runs/20261126-1500_cf88609_t13-diagnose"
T13_WALLS = os.path.join(T13, "j01", "walls")
T09_AX = ("/data/gpfs/projects/punim2657/SfSpp/runs/"
          "20261125-1340_a50f8cc_t09-own-surfaces/out/axes09_own_regen")
STEM = "Pot_J_Piece_01"

for _p in (os.path.join(SHIP, "work"), IMPL, os.path.join(IMPL, "scripts")):
    if _p not in sys.path:
        sys.path.insert(0, _p)
os.environ.setdefault("SFS_IMPL", IMPL)

import t03_lib as dl  # noqa: E402
import t03_extract as tx  # noqa: E402
import sfs_axes.joint as jt  # noqa: E402
import sfs_axes.select as sel  # noqa: E402
from sfs_axes.io_axes import direction_angle_deg  # noqa: E402
from sfs_axes.profile import stride  # noqa: E402

# Ticket 13 donor line: evaluation only, never fed to the selector.
DONOR_DIR = np.array([0.992676, 0.042854, 0.112950], dtype=float)
DONOR_DIR = DONOR_DIR / np.linalg.norm(DONOR_DIR)
DONOR_PT = np.array([-53.313366, -28.804402, 479.479140], dtype=float)

CTL_AXIS = os.path.join(T13, "axes", "T09_WITH_AUTHOR_J01", STEM + "_Axis.xyz")
CTL_OTHER = [os.path.join(T13, "j01", "axes", "AUTHOR", STEM + "_Axis.xyz"),
             os.path.join(SHIP, "out", "axes03_tri", STEM + "_Axis.xyz")]

ARMS = ["CTL_T09_WITH_AUTHOR_J01", "OWN_NO_HANDLE_SHIP", "OWN_NO_HANDLE_THICKSEC",
        "OWN_VOXEL_THICKSEC", "OWN_S0_ONLY_SHIP"]
WALL_OF = {"OWN_NO_HANDLE_SHIP": "OWN_SHARED_1MM",
           "OWN_NO_HANDLE_THICKSEC": "OWN_SHARED_1MM",
           "OWN_VOXEL_THICKSEC": "OWN_VOXEL_1MM"}
COLS = ["arm", "k", "best_donor_deg", "best_donor_mm", "best_gt_deg", "axes_sha256"]
TAB, NL = chr(9), chr(10)
RUN = ""


def log(msg):
    print("[t16] " + msg, flush=True)


def sha_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for blk in iter(lambda: fh.read(1 << 20), b""):
            h.update(blk)
    return h.hexdigest()


def load_wall(path):
    P = np.loadtxt(path, dtype=float)
    if P.ndim != 2 or P.shape[1] != 6:
        raise SystemExit("wall %s is not an N x 6 table (%r)" % (path, P.shape))
    if not np.all(np.isfinite(P)):
        raise SystemExit("wall %s has non-finite values" % path)
    return np.ascontiguousarray(P.T)


def read_table(path):
    """t13 wrote its tables comma-delimited under .tsv names; accept either."""
    with open(path) as fh:
        head = fh.readline().rstrip("\n")
        sep = TAB if TAB in head else ","
        cols = head.split(sep)
        rows = [dict(zip(cols, ln.rstrip("\n").split(sep))) for ln in fh if ln.strip()]
    return cols, rows


def pin_walls():
    """Every wall must be the exact bytes Ticket 13 measured (its evidence/j01_walls.tsv)."""
    _, rows = read_table(os.path.join(T13, "evidence", "j01_walls.tsv"))
    want = {(r["arm"], int(r["face"])): r["xyz_sha256"] for r in rows}
    got, bad = {}, []
    for arm in ("AUTHOR", "OWN_T09", "OWN_SHARED_1MM", "OWN_VOXEL_1MM"):
        for face in (0, 1):
            p = os.path.join(T13_WALLS, "%s.S%d.xyz" % (arm, face))
            s = sha_file(p)
            got["%s.S%d" % (arm, face)] = s
            if want.get((arm, face)) != s:
                bad.append("%s.S%d t13=%s now=%s" % (arm, face, want.get((arm, face)), s))
    return got, bad


def perp_mm(v):
    r = np.asarray(v[3:6], dtype=float) - DONOR_PT
    r = r - float(r @ DONOR_DIR) * DONOR_DIR
    return float(np.linalg.norm(r))


def _split(res):
    """(lines (6, K), costs (K,)) from a selector result, or (None, None). Same as joint._split."""
    if res is None:
        return None, None
    lines, costs = res
    lines = np.asarray(lines, dtype=float)
    if lines.ndim == 1:
        lines = lines.reshape(6, 1)
    if lines.size == 0 or lines.shape[1] == 0:
        return None, None
    costs = np.asarray(costs, dtype=float).ravel()
    if costs.size != lines.shape[1]:
        costs = (np.resize(costs, lines.shape[1]) if costs.size
                 else np.zeros(lines.shape[1]))
    return lines, costs


def merge_with_thick_secondaries(res_normal, res_thickness, res_shipped,
                                 dedup_deg=jt.JOINT_DEDUP_DEG, kmax=jt.JOINT_KMAX,
                                 include_thickness_secondaries=True):
    """joint.merge_lines ordering with the thickness arm's secondaries offered first.

    normal rank-0, then thickness rank-0, then shipped rank-0, then res_thickness[:, 1:]
    in rank order, then res_shipped[:, 1:] in rank order; every appended line must sit at
    least dedup_deg from each kept line and at most kmax lines are kept.  Nothing is
    reoriented here (joint.orient_merged does that once, after the merge).
    """
    a, ca = _split(res_normal)
    b, cb = _split(res_thickness)
    p, cp = _split(res_shipped)
    lines, costs = [], []

    def far_enough(v):
        return all(direction_angle_deg(v[0:3], u[0:3]) >= dedup_deg for u in lines)

    def add(v, c):
        lines.append(np.asarray(v, dtype=float).reshape(6))
        costs.append(float(c))

    if a is not None:
        add(a[:, 0], ca[0])
    for group, gc in ((b, cb), (p, cp)):
        if group is None or len(lines) >= kmax:
            continue
        if far_enough(group[:, 0]):
            add(group[:, 0], gc[0])
    if include_thickness_secondaries and b is not None:
        for k in range(1, b.shape[1]):
            if len(lines) >= kmax:
                break
            if far_enough(b[:, k]):
                add(b[:, k], cb[k])
    if p is not None:
        for k in range(1, p.shape[1]):
            if len(lines) >= kmax:
                break
            if far_enough(p[:, k]):
                add(p[:, k], cp[k])
    if not lines:
        return None
    return np.column_stack(lines), np.asarray(costs, dtype=float)


def draw(C):
    reps, sizes, _V, st, _nd = dl.draw_pool(C, seeds=10, step=10)
    return reps, sizes, int(st)


def ship_select(c0, c1, C):
    """The unchanged frozen SHIP path: joint.select_joint_lines, kmax resolves to 3."""
    reps, sizes, st = draw(C)
    out = jt.select_joint_lines(reps, sizes, c0, c1, C, jt.JOINT_MAX_CANDIDATES)
    # The union path's own entry point must agree exactly (tri_select is ON by default).
    alt = tx.select_lines(reps, sizes, c0, c1, C, 6, None)
    same = (out is not None and alt is not None
            and np.array_equal(np.asarray(out[0]), np.asarray(alt[0])))
    return out, {"effective_stride": st, "drawn_points": int(C.shape[1] // st),
                 "ship_path_identical": bool(same)}


def thicksec_select(c0, c1, C):
    """normal_arm + thickness_arm + shipped, merged thickness-secondaries-first, oriented once."""
    reps, sizes, st = draw(C)
    walls = [stride(c0), stride(c1)]
    size = float(np.linalg.norm(C[0:3].max(axis=1) - C[0:3].min(axis=1)))
    res_n = jt.normal_arm(reps, sizes, walls, C, size)
    res_t = jt.thickness_arm(reps, sizes, walls, C, size)
    res_s = sel.select_union_lines(reps, sizes, c0, c1, C, jt.JOINT_MAX_CANDIDATES,
                                   line_rule=True, base_orient=False, tri_select=False)
    merged = merge_with_thick_secondaries(res_n, res_t, res_s,
                                          dedup_deg=jt.JOINT_DEDUP_DEG, kmax=jt.JOINT_KMAX)
    out = jt.orient_merged(merged, C, base_orient=True)
    # Fixture: with the thickness secondaries withheld the helper is joint.merge_lines.
    plain = merge_with_thick_secondaries(res_n, res_t, res_s,
                                         dedup_deg=jt.JOINT_DEDUP_DEG, kmax=jt.JOINT_KMAX,
                                         include_thickness_secondaries=False)
    ref = jt.merge_lines(res_n, res_t, res_s, dedup_deg=jt.JOINT_DEDUP_DEG,
                         kmax=jt.JOINT_KMAX, include_shipped_secondaries=True)
    same = (plain is None and ref is None) or (
        plain is not None and ref is not None
        and np.array_equal(np.asarray(plain[0]), np.asarray(ref[0])))
    tb, _tbc = _split(res_t)
    tmin = None
    if tb is not None:
        tmin = float(min(direction_angle_deg(tb[0:3, k], DONOR_DIR)
                         for k in range(tb.shape[1])))
    nb, _nbc = _split(res_n)
    sb, _sbc = _split(res_s)
    return out, {"effective_stride": st, "drawn_points": int(C.shape[1] // st),
                 "merge_equals_merge_lines_without_thick_secondaries": bool(same),
                 "thickness_arm_k": (0 if tb is None else int(tb.shape[1])),
                 "thickness_arm_min_donor_deg": (None if tmin is None else round(tmin, 4)),
                 "normal_arm_k": (0 if nb is None else int(nb.shape[1])),
                 "shipped_arm_k": (0 if sb is None else int(sb.shape[1]))}


def axis_from_file(path):
    arr = np.atleast_2d(np.loadtxt(path, dtype=float))
    if arr.shape[1] != 6:
        raise SystemExit("axis %s is not an N x 6 table (%r)" % (path, arr.shape))
    return np.vstack([arr[:, 3:6].T, arr[:, 0:3].T])


def measure(lines, gt):
    if lines is None or np.asarray(lines).size == 0:
        return None
    L = np.asarray(lines, dtype=float)
    ang_d = [float(direction_angle_deg(L[0:3, k], DONOR_DIR)) for k in range(L.shape[1])]
    mm_d = [perp_mm(L[:, k]) for k in range(L.shape[1])]
    ang_g = [float(direction_angle_deg(L[0:3, k], gt[0:3])) for k in range(L.shape[1])]
    kd = int(np.argmin(ang_d))
    return {"k": int(L.shape[1]), "best_donor_deg": round(ang_d[kd], 4),
            "best_donor_mm": round(mm_d[kd], 4), "best_gt_deg": round(min(ang_g), 4),
            "best_donor_rank": kd,
            "per_line": [{"rank": k, "donor_deg": round(ang_d[k], 4),
                          "donor_mm": round(mm_d[k], 4),
                          "gt_deg": round(ang_g[k], 4)} for k in range(L.shape[1])]}


def main():
    global RUN
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", required=True)
    a = ap.parse_args()
    RUN = os.path.abspath(a.run)
    for d in (os.path.join(RUN, "evidence"), os.path.join(RUN, "logs"),
              os.path.join(RUN, "axes16")):
        os.makedirs(d, exist_ok=True)

    walls = {}
    for arm in ("AUTHOR", "OWN_T09", "OWN_SHARED_1MM", "OWN_VOXEL_1MM"):
        walls[arm] = (load_wall(os.path.join(T13_WALLS, arm + ".S0.xyz")),
                      load_wall(os.path.join(T13_WALLS, arm + ".S1.xyz")))
        log("wall %-16s S0=%d S1=%d" % (arm, walls[arm][0].shape[1], walls[arm][1].shape[1]))
    wsha, bad = pin_walls()
    if bad:
        raise SystemExit("wall pins disagree with Ticket 13 evidence: %r" % (bad,))
    log("walls pinned to Ticket 13 evidence: %d files" % len(wsha))

    gt = dl.gt_axis(STEM)
    rows, detail, fixtures = [], {}, {}

    # Positive control: the exact axis Ticket 13 swapped in (and it must equal the two
    # other copies of the same selector run on the Authors' walls).
    ctl = axis_from_file(CTL_AXIS)
    ctl_sha = sha_file(CTL_AXIS)
    others = {}
    for p in CTL_OTHER:
        others[p] = {"exists": os.path.exists(p),
                     "sha256": sha_file(p) if os.path.exists(p) else None}
    fixtures["ctl_axis_copies_identical"] = all(v["sha256"] == ctl_sha
                                                for v in others.values())
    lines_out = {arm: None for arm in ARMS}
    lines_out["CTL_T09_WITH_AUTHOR_J01"] = ctl
    detail["CTL_T09_WITH_AUTHOR_J01"] = {"source": CTL_AXIS, "copies": others,
                                         "effective_stride": 0, "drawn_points": 0}

    for arm in ("OWN_NO_HANDLE_SHIP", "OWN_S0_ONLY_SHIP",
                "OWN_NO_HANDLE_THICKSEC", "OWN_VOXEL_THICKSEC"):
        if arm == "OWN_S0_ONLY_SHIP":
            c0 = walls["OWN_T09"][0]
            c1 = walls["OWN_T09"][0]
        else:
            c0, c1 = walls[WALL_OF[arm]]
        C = np.concatenate([c0, c1], axis=1)
        if arm.endswith("_SHIP"):
            out, info = ship_select(c0, c1, C)
        else:
            out, info = thicksec_select(c0, c1, C)
        if out is None or np.asarray(out[0]).size == 0:
            raise SystemExit("arm %s returned no lines" % arm)
        lines_out[arm] = np.asarray(out[0], dtype=float)
        info["costs"] = [round(float(c), 6) for c in np.ravel(out[1])]
        detail[arm] = info
        log("arm %-24s k=%d info=%s" % (arm, lines_out[arm].shape[1],
                                        {k: v for k, v in info.items() if k != "costs"}))

    for arm in ARMS:
        adir = os.path.join(RUN, "axes16", arm)
        os.makedirs(adir, exist_ok=True)
        path = os.path.join(adir, STEM + "_Axis.xyz")
        tx.write_lines(path, lines_out[arm])
        m = measure(lines_out[arm], gt)
        if m is None:
            raise SystemExit("arm %s has no measurable line" % arm)
        rows.append({"arm": arm, "k": m["k"],
                     "best_donor_deg": "%.4f" % m["best_donor_deg"],
                     "best_donor_mm": "%.4f" % m["best_donor_mm"],
                     "best_gt_deg": "%.4f" % m["best_gt_deg"],
                     "axes_sha256": sha_file(path)})
        detail[arm].update(m)
        detail[arm]["axes_sha256"] = sha_file(path)
        detail[arm]["axis_file"] = path
        log("%-24s k=%d donor=%.4f deg / %.4f mm  GT=%.4f deg  sha=%s"
            % (arm, m["k"], m["best_donor_deg"], m["best_donor_mm"], m["best_gt_deg"],
               detail[arm]["axes_sha256"][:12]))

    with open(os.path.join(RUN, "evidence", "j01_axes16.tsv"), "w") as fh:
        fh.write(TAB.join(COLS) + NL)
        for r in rows:
            fh.write(TAB.join(str(r[c]) for c in COLS) + NL)
    status = {"stem": STEM, "run": RUN, "walls": wsha,
              "fixtures": {k: bool(v) for k, v in fixtures.items()},
              "arms": detail, "t13_donor": {"dir": DONOR_DIR.tolist(),
                                            "pt": DONOR_PT.tolist()},
              "gt_axis": np.asarray(gt, dtype=float).ravel().tolist()}
    with open(os.path.join(RUN, "logs", "j01_axes16_detail.json"), "w") as fh:
        json.dump(status, fh, indent=1)
    log("CTL axis copies identical: %s" % fixtures["ctl_axis_copies_identical"])
    log("T16-AXES-OK")
    return 0


if __name__ == "__main__":
    sys.exit(main() or 0)
