#!/usr/bin/env python3
"""Ticket 09 report: the evidence tables, the jobs table and the 11-row 20 mm render.

Reads what Stage 3 (extract09.py) wrote under <RUN>/evidence, the t09 E2E runs, and the
read-only frozen t03/t08 baselines.  Adds fixtures.tsv, pots_e2e.tsv, juglet_e2e.tsv,
comparison_vs_t08.tsv, renders.tsv (and renders/Pot_A_to_J_and_Juglet_t09_regen.png),
jobs.tsv and sources.tsv.  Best-of-N is reported as the best attempt with the number of
repeats that reached it -- never a median.
"""
import argparse
import datetime
import glob
import hashlib
import json
import os
import subprocess

import numpy as np
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from mpl_toolkits.mplot3d import Axes3D  # noqa: F401,E402

RUNS = "/data/gpfs/projects/punim2657/SfSpp/runs"
SHIP = RUNS + "/20261121-1319_2e951d9_t03-ship"
T03JUG = RUNS + "/20261121-1319_2e951d9_t03-juglet"
T08 = RUNS + "/20261125-1218_fc5d0ac_t08-ship"
ORACLE = RUNS + "/20261119-1823_f86432b_t336-juglet"

POTS = list("ABCDEFGHIJ")
ARMS = ["MOR1", "MOR2", "K3R1", "K3R2"]
FLOORS = {"A": (8, 8, 15, 15), "B": (9, 9, 15, 15), "C": (4, 4, 5, 5),
          "D": (23, 28, 55, 69), "E": (31, 31, 62, 62), "F": (5, 5, 7, 7),
          "G": (7, 7, 10, 10), "H": (11, 11, 17, 17), "I": (25, 26, 59, 62),
          "J": (8, 11, 16, 21)}
TERMINAL = {"COMPLETED", "FAILED", "CANCELLED", "TIMEOUT", "NODE_FAIL",
            "PREEMPTED", "OUT_OF_MEMORY", "BOOT_FAIL", "DEADLINE"}
JUG_LIMIT_MM = 0.50
SCALE_BAR_MM = 20
STAGE3A = set("EGDJ")

DEDUPE27_HEADER = ["stem", "pot", "face", "mode", "in_rows", "out_rows",
                   "improved_rows", "dups_skipped", "appended", "normal_maxdiff"]
WALLS_HEADER = ["stem", "pot", "face", "points", "duplicate_xyz", "bl_points",
                "nn_med_mm_vs_t08", "nn_p90_mm_vs_t08", "xyz_sha256", "normals_sha256"]
AXES_HEADER = ["stem", "pot", "in_141_gt", "excluded_by_paper", "k_t08", "k_t09",
               "axes_sha256_t09", "effective_stride", "drawn_points",
               "rank1_deg_t08", "rank1_deg_t09", "best_deg_t08", "best_deg_t09",
               "d_gt_to_est_mm_t09", "d_est_to_gt_mm_t09", "is_base_t09"]
POTS_E2E_HEADER = ["pot", "arm", "sherd", "sherd_den", "edge", "edge_den",
                   "sherd_floor", "edge_floor", "floor_pass", "t03_sherd",
                   "t03_edge", "t08_sherd", "t08_edge", "delta_edge_vs_t03",
                   "delta_edge_vs_t08", "wall_secs"]
JUG_HEADER = ["arm", "cluster_len", "cluster_seated", "cluster_max_chamfer_mm",
              "cluster_members_le_050", "edges_strict", "edges_of", "p7_strict",
              "floor_pass"]
CMP_HEADER = ["vessel", "mor_best", "t03_own_raw_best", "t08_own_dedup_best",
              "t09_own_regen_best", "reached_by", "floor_pass",
              "regression_vs_t03", "regression_vs_t08", "note"]
FIX_HEADER = ["fixture", "status", "detail"]

STAMP = ""
TPL_GIT7 = "2e951d9"   # frozen E2E template commit token inside the t08 run ids
T09_GIT7 = "a50f8cc"   # Ticket 09 commit token inside the t09 run ids


_TAG_CACHE = {}


def run_for_tag(tag):
    """The newest run directory carrying a tag, read from runs/index.tsv.

    Stage 3A and 3B were launched at two different stamps, so the stamp in the
    own-surfaces run's own name does not name them; the index is the record.
    """
    if not _TAG_CACHE:
        path = os.path.join(RUNS, "index.tsv")
        if os.path.isfile(path):
            with open(path) as fh:
                for line in fh:
                    f = line.rstrip("\n").split("\t")
                    if len(f) < 4 or not f[0]:
                        continue
                    _TAG_CACHE.setdefault(f[3], []).append(f[0])
    ids = sorted(set(_TAG_CACHE.get(tag) or []))
    if not ids:
        return os.path.join(RUNS, "MISSING_" + tag)
    return os.path.join(RUNS, ids[-1])


def t09_pot(P):
    return run_for_tag("t09-pot%s" % P)


def t09_juglet():
    return run_for_tag("t09-juglet")


def t08_pot(P):
    return run_for_tag("t08-pot%s" % P)


def t08_juglet():
    return run_for_tag("t08-juglet")


def t03_pot(P):
    return run_for_tag("t03-pot%s" % P)


def log(msg):
    print("[t09-report] " + msg, flush=True)


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for blk in iter(lambda: fh.read(1 << 20), b""):
            h.update(blk)
    return h.hexdigest()


def read_tsv(path):
    if not os.path.isfile(path):
        return None, []
    with open(path) as fh:
        lines = [ln.rstrip("\n") for ln in fh if ln.strip()]
    if not lines:
        return None, []
    head = lines[0].split("\t")
    rows = [dict(zip(head, ln.split("\t"))) for ln in lines[1:]]
    return head, rows


def write_tsv(path, header, rows):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as fh:
        fh.write("\t".join(header) + "\n")
        for r in rows:
            fh.write("\t".join(str(r.get(k, "")) for k in header) + "\n")


def frac(s):
    try:
        a, b = str(s).split("/")
        return int(a), int(b)
    except (ValueError, AttributeError):
        return None, None


def acc_rows(run):
    head, rows = read_tsv(os.path.join(run, "score", "acc.tsv"))
    out = {}
    for r in rows:
        s, sd = frac(r.get("sherd"))
        e, ed = frac(r.get("edge"))
        out[r["label"]] = {"sherd": s, "sherd_den": sd, "edge": e, "edge_den": ed,
                           "time_s": r.get("time_s", "")}
    return out


def best_of(acc, arms):
    """Best of the given arms: edge count first, then sherd count.  Never a median."""
    cand = [(acc[a]["edge"], acc[a]["sherd"], a) for a in arms
            if a in acc and acc[a]["edge"] is not None]
    if not cand:
        return None, []
    best_key = max((c[0], c[1]) for c in cand)
    winners = sorted(c[2] for c in cand if (c[0], c[1]) == best_key)
    return best_key, winners


def fmt_pair(sherd, sherd_den, edge, edge_den):
    return "%s/%s %s/%s" % (sherd, sherd_den, edge, edge_den)


def panel_walls(run):
    """arm -> wall seconds from logs/panel.tsv (acc.tsv time_s is often empty)."""
    path = os.path.join(run, "logs", "panel.tsv")
    out = {}
    if not os.path.isfile(path):
        return out
    with open(path) as fh:
        head = fh.readline().rstrip("\n").split("\t")
        if "arm" not in head or "wall_s" not in head:
            return out
        ai = head.index("arm")
        wi = head.index("wall_s")
        for line in fh:
            f = line.rstrip("\n").split("\t")
            if len(f) <= max(ai, wi):
                continue
            try:
                out[f[ai]] = float(f[wi])
            except ValueError:
                pass
    return out


# ---------------------------------------------------------------- tables
def check_manifest(path):
    """The four manifest invariants the ticket names (schema, 11 vessels, 157 pieces)."""
    bad = []
    if isinstance(path, dict):
        d = path
    else:
        if not os.path.isfile(path):
            return ["manifest missing: " + path]
        try:
            d = json.load(open(path))
        except ValueError as exc:
            return ["manifest is not JSON: %s" % exc]
    for k in ("run_id", "run_root", "preprocessing_commit", "binaries_sha256",
              "sfs_dedupe", "sfs_wall_pair_filter", "total_pieces", "total_walls",
              "duplicate_xyz", "vessels", "axes_own_regen", "axes_juglet_def3x_regen"):
        if k not in d:
            bad.append("missing key " + k)
    if bad:
        return bad
    v = d["vessels"]
    if sorted(v) != ["A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "JUGLET_DEF3X"]:
        bad.append("vessel keys %s" % sorted(v))
    tot = sum(int(v[k].get("pieces", 0)) for k in v)
    if tot != 157 or int(d.get("total_pieces", -1)) != 157:
        bad.append("piece total %d / %s (want 157)" % (tot, d.get("total_pieces")))
    if int(d.get("total_walls", -1)) != 314:
        bad.append("total_walls %s (want 314)" % d.get("total_walls"))
    if str(d.get("duplicate_xyz")) != "0":
        bad.append("duplicate_xyz %r" % d.get("duplicate_xyz"))
    if d.get("sfs_dedupe") != "off":
        bad.append("sfs_dedupe %r" % d.get("sfs_dedupe"))
    commit = str(d.get("preprocessing_commit", ""))
    if len(commit) != 40 or any(c not in "0123456789abcdef" for c in commit):
        bad.append("preprocessing_commit %r" % commit)
    for name, h in (d.get("binaries_sha256") or {}).items():
        if len(str(h)) != 64:
            bad.append("binary hash %s %r" % (name, h))
    root = str(d.get("run_root", ""))
    paths = [str(d.get("axes_own_regen", "")), str(d.get("axes_juglet_def3x_regen", ""))]
    paths += [str(v[k].get("geom_dir", "")) for k in v]
    for p in paths:
        if not p.startswith(root) or "_t09-own-surfaces" not in p:
            bad.append("path not under run_root: " + p)
        if any(s in p for s in ("t305-lane", "t66-admitsign", "t80-default-on",
                                "out_poth")):
            bad.append("stale run reference: " + p)
    return bad


def tables(run, ev, manifest):
    head, drows = read_tsv(os.path.join(ev, "dedupe27.tsv"))
    if head != DEDUPE27_HEADER:
        raise SystemExit("dedupe27.tsv header %r" % (head,))
    if len(drows) != 314:
        raise SystemExit("dedupe27.tsv rows %d (want 314)" % len(drows))
    bad = [r["stem"] + ":" + r["face"] for r in drows
           if r.get("mode") != "off" or r.get("in_rows") != r.get("out_rows")
           or not (0.0 <= float(r.get("normal_maxdiff") or "nan") <= 1e-6)]
    fixture_d27 = ("FAIL", "%d bad rows: %s" % (len(bad), bad[:4])) if bad else (
        "PASS", "314 rows: mode=off, in==out, 0<=normal_maxdiff<=1e-6")

    head, wrows = read_tsv(os.path.join(ev, "walls.tsv"))
    if head != WALLS_HEADER:
        raise SystemExit("walls.tsv header %r" % (head,))
    if len(wrows) != 314:
        raise SystemExit("walls.tsv rows %d (want 314)" % len(wrows))
    bad = [r["stem"] + ":" + r["face"] for r in wrows
           if r.get("duplicate_xyz") != "0" or int(r.get("bl_points") or 0) <= 0]
    fixture_dup = ("FAIL", "%d walls bad: %s" % (len(bad), bad[:4])) if bad else (
        "PASS", "314 walls: duplicate_xyz=0 and bl_points>0")

    head, arows = read_tsv(os.path.join(ev, "axes.tsv"))
    if head != AXES_HEADER:
        raise SystemExit("axes.tsv header %r" % (head,))
    if len(arows) != 157:
        raise SystemExit("axes.tsv rows %d (want 157)" % len(arows))
    gt = [r for r in arows if r.get("in_141_gt") == "1"]
    exc = [r["stem"] for r in arows if r.get("excluded_by_paper") == "1"]
    bases = [r["stem"] for r in arows if r.get("is_base_t09") == "1"
             and r["stem"].startswith("Juglet")]
    summ_path = os.path.join(run, "logs", "extract09_summary.json")
    guard = {}
    if os.path.isfile(summ_path):
        guard = json.load(open(summ_path))
    p1 = arows[[r["stem"] for r in arows].index("Juglet_Piece_1")] if any(
        r["stem"] == "Juglet_Piece_1" for r in arows) else {}
    p1pos = 0.0
    try:
        with open(os.path.join(manifest["axes_juglet_def3x_regen"],
                               "Juglet_Piece_1_Axis.xyz")) as fh:
            p1pos = max(abs(float(x)) for x in fh.readline().split()[:3])
    except (OSError, ValueError, KeyError):
        p1pos = 0.0
    ok_guard = (bases == ["Juglet_Piece_7"] and 300.0 < p1pos < 1000.0
                and abs(float(p1.get("drawn_points") or 0)) > 0)
    fixture_jug = ("PASS", "bases=%s; Piece_1 native (3x) axes written un-divided"
                   % ",".join(bases)) if ok_guard else (
        "FAIL", "juglet natives: bases=%s" % (bases,))
    if len(gt) != 141:
        fixture_dup = ("FAIL", fixture_dup[1] + "; GT rows %d (want 141)" % len(gt))
    log("tables: dedupe27 314, walls 314, axes 157 (GT %d, paper-excluded %d)"
        % (len(gt), len(exc)))

    bad = check_manifest(manifest)
    fixture_man = ("FAIL", "; ".join(bad[:6])) if bad else (
        "PASS", "schema ok: 11 vessels, 157 pieces, commit 40-hex, paths under run_root")
    write_tsv(os.path.join(ev, "fixtures.tsv"), FIX_HEADER,
              [{"fixture": "zero_dup_all_314", "status": fixture_dup[0],
                "detail": fixture_dup[1]},
               {"fixture": "dedupe27_in_eq_out", "status": fixture_d27[0],
                "detail": fixture_d27[1]},
               {"fixture": "juglet_native_3x_guard", "status": fixture_jug[0],
                "detail": fixture_jug[1]},
               {"fixture": "manifest_schema_valid", "status": fixture_man[0],
                "detail": fixture_man[1]}])
    fails = [f for f in (fixture_dup, fixture_d27, fixture_jug, fixture_man)
             if f[0] != "PASS"]
    if fails:
        log("FIXTURES NOT ALL PASS: %s" % (fails,))
    return fails


def pots_e2e():
    rows = []
    missing = []
    for P in POTS:
        a09 = acc_rows(t09_pot(P))
        a08 = acc_rows(t08_pot(P))
        a03 = acc_rows(t03_pot(P))
        pw = panel_walls(t09_pot(P))
        fl = FLOORS[P]
        for arm in ARMS:
            lab = P + "_" + arm
            if lab not in a09:
                missing.append((P, arm))
                continue
            d = a09[lab]
            o = a03.get(lab, {})
            p8 = a08.get(lab, {})
            pass_floor = 1 if (d["sherd"] >= fl[0] and d["edge"] >= fl[2]) else 0
            # wall seconds this arm actually spent (logs/panel.tsv wall_s).
            # score/acc.tsv time_s is not usable: blank for both MO arms and
            # inconsistent for the K3 arms (Pot E: K3R1 12708, K3R2 1.16).
            if lab in pw:
                tsec = "%.1f" % pw[lab]
            else:
                tsec = d["time_s"] or "NA"
                try:
                    tsec = "%.4f" % float(tsec)
                except ValueError:
                    pass
            rows.append({
                "pot": P, "arm": lab, "sherd": d["sherd"],
                "sherd_den": d["sherd_den"], "edge": d["edge"],
                "edge_den": d["edge_den"],
                "sherd_floor": "%d/%d" % (fl[0], fl[1]),
                "edge_floor": "%d/%d" % (fl[2], fl[3]),
                "floor_pass": pass_floor,
                "t03_sherd": o.get("sherd", "NA"), "t03_edge": o.get("edge", "NA"),
                "t08_sherd": p8.get("sherd", "NA"), "t08_edge": p8.get("edge", "NA"),
                "delta_edge_vs_t03": (d["edge"] - o["edge"])
                if o.get("edge") is not None else "NA",
                "delta_edge_vs_t08": (d["edge"] - p8["edge"])
                if p8.get("edge") is not None else "NA",
                "wall_secs": tsec})
    return rows, missing


def juglet_e2e():
    head, rows = read_tsv(os.path.join(t09_juglet(), "score", "juglet",
                                       "summary.tsv"))
    out = []
    for r in rows:
        seated = int(r["cluster_seated"])
        clen = int(r["cluster_len"])
        mx = float(r["cluster_max_chamfer_mm"])
        ok = 1 if (seated == 9 and clen == 9 and mx <= JUG_LIMIT_MM) else 0
        out.append({"arm": r["arm"], "cluster_len": clen, "cluster_seated": seated,
                    "cluster_max_chamfer_mm": "%.4f" % mx,
                    "cluster_members_le_050": r["cluster_members_le_050"],
                    "edges_strict": r["edges_strict"], "edges_of": r["edges_of"],
                    "p7_strict": r["p7_strict"], "floor_pass": ok})
    return out


def _reg(base, new):
    """Compare a (edge, sherd) pair against a baseline -> improved/regressed/none."""
    if base is None or new is None:
        return "NA"
    if new[0] > base[0]:
        return "improved"
    if new[0] < base[0]:
        return "regressed"
    if new[1] > base[1]:
        return "improved_sherd"
    if new[1] < base[1]:
        return "regressed_sherd"
    return "none"


def comparison(pots, jug):
    rows = []
    for P in POTS:
        a09 = acc_rows(t09_pot(P))
        a08 = acc_rows(t08_pot(P))
        a03 = acc_rows(t03_pot(P))
        fl = FLOORS[P]
        mor_key, mor_w = best_of(a09, [P + "_MOR1", P + "_MOR2"])
        k03, k03_w = best_of(a03, [P + "_K3R1", P + "_K3R2"])
        k08, k08_w = best_of(a08, [P + "_K3R1", P + "_K3R2"])
        k09, k09_w = best_of(a09, [P + "_K3R1", P + "_K3R2"])
        if k09 is None:
            rows.append({"vessel": P, "note": "Stage 3 arms missing"})
            continue
        d = a09[k09_w[0]]
        notes = []
        if len(k09_w) > 1:
            notes.append("best reached by %d/2 K3 repeats" % len(k09_w))
        if P == "D":
            notes.append("D 18/29 released axis files point away from their own pose")
        if P == "C":
            notes.append("C 01 interior Bl0 gap measures the input, not the seat")
        if P == "J":
            notes.append("J 01 interior gap; J 09 excluded from the bar tally")
        if P in ("F", "I", "J"):
            notes.append("paper-excluded pieces still inside the pot totals")
        rows.append({
            "vessel": P,
            "mor_best": (fmt_pair(mor_key[1], a09[mor_w[0]]["sherd_den"],
                                  mor_key[0], a09[mor_w[0]]["edge_den"])
                         if mor_key else "NA"),
            "t03_own_raw_best": (fmt_pair(k03[1], a03[k03_w[0]]["sherd_den"],
                                          k03[0], a03[k03_w[0]]["edge_den"])
                                 if k03 else "NA"),
            "t08_own_dedup_best": (fmt_pair(k08[1], a08[k08_w[0]]["sherd_den"],
                                            k08[0], a08[k08_w[0]]["edge_den"])
                                   if k08 else "NA"),
            "t09_own_regen_best": fmt_pair(k09[1], d["sherd_den"], k09[0],
                                           d["edge_den"]),
            "reached_by": ",".join(w.split("_")[-1] for w in k09_w),
            "floor_pass": 1 if (d["sherd"] >= fl[0] and d["edge"] >= fl[2]) else 0,
            "regression_vs_t03": _reg(k03, k09),
            "regression_vs_t08": _reg(k08, k09),
            "note": "; ".join(notes) if notes else "no caveat"})

    head, jr = read_tsv(os.path.join(t09_juglet(), "score", "juglet",
                                     "summary.tsv"))
    h8, j8 = read_tsv(os.path.join(t08_juglet(), "score", "juglet",
                                   "summary.tsv"))
    h3, j3 = read_tsv(os.path.join(T03JUG, "score", "juglet", "summary.tsv"))
    if jr:
        best_ch = min(jr, key=lambda r: float(r["cluster_max_chamfer_mm"]))
        best_ed = max(jr, key=lambda r: int(r["edges_strict"]))
        ch_w = sorted(r["arm"] for r in jr
                      if float(r["cluster_max_chamfer_mm"])
                      == float(best_ch["cluster_max_chamfer_mm"]))
        ed_w = sorted(r["arm"] for r in jr
                      if int(r["edges_strict"]) == int(best_ed["edges_strict"]))
        seated_all = all(int(r["cluster_seated"]) == int(r["cluster_len"]) == 9
                         for r in jr)
        txt8 = "NA"
        if j8:
            c8 = min(j8, key=lambda r: float(r["cluster_max_chamfer_mm"]))
            e8 = max(j8, key=lambda r: int(r["edges_strict"]))
            txt8 = "9/9 @%s mm; edges %s/%s" % (c8["cluster_max_chamfer_mm"],
                                                e8["edges_strict"], e8["edges_of"])
        txt3 = "NA"
        reg3 = "NA"
        if j3:
            c3 = min(j3, key=lambda r: float(r["cluster_max_chamfer_mm"]))
            e3 = max(j3, key=lambda r: int(r["edges_strict"]))
            txt3 = "9/9 @%s mm; edges %s/%s" % (c3["cluster_max_chamfer_mm"],
                                                e3["edges_strict"], e3["edges_of"])
            dch = float(best_ch["cluster_max_chamfer_mm"]) - float(
                c3["cluster_max_chamfer_mm"])
            ded = int(best_ed["edges_strict"]) - int(e3["edges_strict"])
            reg3 = ("improved" if (dch < -1e-9 or ded > 0)
                    else "regressed" if (dch > 1e-9 or ded < 0) else "none")
        reg8 = "NA"
        if j8:
            dch = float(best_ch["cluster_max_chamfer_mm"]) - float(
                c8["cluster_max_chamfer_mm"])
            ded = int(best_ed["edges_strict"]) - int(c8["edges_strict"])
            reg8 = ("improved" if (dch < -1e-9 or ded > 0)
                    else "regressed" if (dch > 1e-9 or ded < 0) else "none")
        rows.append({
            "vessel": "JUGLET", "mor_best": "n/a (no authors reference)",
            "t03_own_raw_best": txt3, "t08_own_dedup_best": txt8,
            "t09_own_regen_best": "9/9 @%s mm; edges %s/%s"
            % (best_ch["cluster_max_chamfer_mm"], best_ed["edges_strict"],
               best_ed["edges_of"]),
            "reached_by": "chamfer %s (%d/4); edges %s (%d/4); seated_all=%d"
            % (",".join(x.split("_")[-1] for x in ch_w), len(ch_w),
               ",".join(x.split("_")[-1] for x in ed_w), len(ed_w),
               1 if seated_all else 0),
            "floor_pass": 1 if (seated_all and float(
                best_ch["cluster_max_chamfer_mm"]) <= JUG_LIMIT_MM) else 0,
            "regression_vs_t03": reg3, "regression_vs_t08": reg8,
            "note": "p7_strict %s/4; per-piece seated best %s/9; native 3x axes; "
                    "oracle row in render"
            % (sum(1 for r in jr if int(r["p7_strict"]) > 0),
               max(int(r["seated"]) for r in jr))})
    return rows


# ---------------------------------------------------------------- render
def read_obj(path):
    v = []
    with open(path) as fh:
        for line in fh:
            if line.startswith("v "):
                v.append([float(x) for x in line.split()[1:4]])
    return np.asarray(v, dtype=float) if v else np.zeros((0, 3))


def sample(V, n=2500):
    if V.shape[0] == 0:
        return V
    idx = np.linspace(0, V.shape[0] - 1, min(n, V.shape[0])).astype(int)
    return V[idx]


def scale_bar(fig, ax, c, r, length=SCALE_BAR_MM, unit_mm=1.0):
    """20 mm bar in a 2D overlay at the panel's lower left (native 3x = 60 units)."""
    if r <= 0:
        return
    frac_ = min(0.35, float(length) * float(unit_mm) / (2.0 * r))
    pos = ax.get_position()
    ov = fig.add_axes([pos.x0, pos.y0, pos.width, pos.height], frameon=False)
    ov.set_xlim(0, 1)
    ov.set_ylim(0, 1)
    ov.set_xticks([])
    ov.set_yticks([])
    ov.set_axis_off()
    x0, y0 = 0.06, 0.07
    ov.plot([x0, x0 + frac_], [y0, y0], color="black", lw=3.0,
            solid_capstyle="butt", transform=ov.transAxes, clip_on=False)
    ov.text(x0 + frac_ / 2.0, y0 + 0.018, "%d mm" % length, fontsize=7,
            ha="center", va="bottom", color="black", transform=ov.transAxes)


def panel(fig, nrow, ncol, pos, objdir, title, unit_mm=1.0):
    ax = fig.add_subplot(nrow, ncol, pos, projection="3d")
    objs = sorted(glob.glob(os.path.join(objdir, "*_OBJ_*.obj")))
    xs, ys, zs = [], [], []
    for ob in objs:
        V = sample(read_obj(ob))
        if V.shape[0] == 0:
            continue
        xs.append(V[:, 0]); ys.append(V[:, 1]); zs.append(V[:, 2])
    c = np.zeros(3)
    r = 1.0
    if xs:
        xs = np.concatenate(xs); ys = np.concatenate(ys); zs = np.concatenate(zs)
        ax.scatter(xs, ys, zs, s=0.35, c="#1f77b4", linewidths=0, alpha=0.8)
        allv = np.column_stack([xs, ys, zs])
        c = allv.mean(axis=0)
        r = max(1e-6, float(np.max(np.linalg.norm(allv - c, axis=1))))
        ax.set_xlim(c[0] - r, c[0] + r)
        ax.set_ylim(c[1] - r, c[1] + r)
        ax.set_zlim(c[2] - r, c[2] + r)
    ax.set_title("%s  pieces=%d" % (title, len(objs)), fontsize=8)
    ax.set_axis_off()
    return ax, c, r, unit_mm


def render(ev):
    nrow = len(POTS) + 1
    fig = plt.figure(figsize=(17, 44))
    bars = []
    for row, P in enumerate(POTS):
        r09 = t09_pot(P)
        acc = acc_rows(r09)
        for col, (suffix, label) in enumerate(
                [("_MOR1", "MOR1 [Authors control]"),
                 ("_K3R1", "K3R1 [regenerated surfaces, own code]")]):
            arm = P + suffix
            d = acc.get(arm, {})
            s = ("%s/%s" % (d.get("sherd"), d.get("sherd_den"))
                 if d.get("sherd") is not None else "-")
            e = ("%s/%s" % (d.get("edge"), d.get("edge_den"))
                 if d.get("edge") is not None else "-")
            bars.append(panel(fig, nrow, 2, row * 2 + col + 1,
                              os.path.join(r09, "out", arm),
                              "%s [%s] sherd %s edge %s" % (arm, label, s, e)))
    jrow = len(POTS)
    jr = t09_juglet()
    jtitle = "JUGLET def_3x regenerated axes [own code]"
    cl = os.path.join(jr, "score", "juglet_own_xy_r1_cluster.json")
    if os.path.isfile(cl):
        cd = json.load(open(cl))
        jtitle += " cluster %s/%s @%.3f mm" % (cd.get("cluster_seated"),
                                              cd.get("cluster_len"),
                                              cd.get("cluster_max_chamfer_mm") or -1)
    bars.append(panel(fig, nrow, 2, jrow * 2 + 1,
                      os.path.join(jr, "out", "juglet_own_xy_r1"), jtitle,
                      unit_mm=3.0))
    orc_title = "JUGLET oracle axes [reference]"
    ocl = os.path.join(ORACLE, "score", "juglet_oracle_xy_cluster.json")
    if os.path.isfile(ocl):
        cd = json.load(open(ocl))
        orc_title += " cluster %s/%s @%.3f mm" % (cd.get("cluster_seated"),
                                                 cd.get("cluster_len"),
                                                 cd.get("cluster_max_chamfer_mm") or -1)
    bars.append(panel(fig, nrow, 2, jrow * 2 + 2,
                      os.path.join(ORACLE, "out", "juglet_oracle_xy"), orc_title,
                      unit_mm=3.0))
    fig.suptitle("Ticket 09: regenerated canonical own surfaces (a50f8cc) -- ten pots "
                 "(rows 1-10) and the def_3x Juglet (row 11); authors control left, "
                 "regenerated own chain right", fontsize=14, y=0.998)
    fig.tight_layout(rect=[0, 0, 1, 1])
    fig.subplots_adjust(top=0.958, hspace=0.02)
    for ax, c, r, u in bars:
        scale_bar(fig, ax, c, r, SCALE_BAR_MM, u)
    out = os.path.join(ev, "renders", "Pot_A_to_J_and_Juglet_t09_regen.png")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    fig.savefig(out, dpi=100)
    plt.close(fig)
    log("render: %s (%d bytes)" % (out, os.path.getsize(out)))
    return out


# ---------------------------------------------------------------- jobs
def sacct_state(job_id):
    try:
        r = subprocess.run(["sacct", "-j", str(job_id),
                            "--format=JobID,State,ExitCode", "-n", "-P"],
                           capture_output=True, text=True, timeout=120)
    except Exception as exc:  # noqa: BLE001
        return "QUERY_FAILED", "", str(exc)
    for line in r.stdout.splitlines():
        p = line.strip().split("|")
        if len(p) >= 3 and p[0] and "." not in p[0]:
            return p[1].split()[0].upper(), p[2], ""
    return "UNKNOWN", "", r.stderr.strip()[:200]


def job_stage_vessel(name):
    """Stage and vessel from the Slurm job name, which is the job's own record.

    All three extract attempts share the name t09-extract, and the juglet
    summary job kept the frozen template's t03-jugsum name.
    """
    name = (name or "").strip()
    if name == "t09-build":
        return "1", "all-vessels"
    if name == "t09-regen":
        return "2", "all-11-vessels"
    if name == "t09-extract":
        return "3", "axes"
    if name.startswith("t09-pot"):
        pot = name[len("t09-pot"):]
        if not pot or not set(pot) <= set("ABCDEFGHIJ"):
            return None
        return ("3A" if pot in STAGE3A else "3B"), "Pot" + pot
    if name == "t09-juglet":
        return "3A", "Juglet_def3x"
    if name == "t03-jugsum":
        return "3A", "JUGSUM"
    return None


def sacct_name(job_id):
    try:
        r = subprocess.run(["sacct", "-j", str(job_id), "--format=JobID,JobName%40",
                            "-n", "-P"], capture_output=True, text=True, timeout=120)
    except Exception:  # noqa: BLE001
        return "", "query failed"
    for line in r.stdout.splitlines():
        p = line.strip().split("|")
        if len(p) >= 2 and p[0] and "." not in p[0]:
            return p[1], ""
    return "", r.stderr.strip()[:200]


def sacct_day():
    # Spartan's clock is UTC and the run id's date is UTC, so jobs submitted just
    # after midnight UTC fall outside a same-day window; scan one day either side.
    base = datetime.date(int(STAMP[0:4]), int(STAMP[4:6]), int(STAMP[6:8]))
    d0 = (base - datetime.timedelta(days=1)).isoformat()
    d1 = (base + datetime.timedelta(days=2)).isoformat()
    try:
        r = subprocess.run(["sacct", "-u", os.environ.get("USER", ""),
                            "-S", d0, "-E", d1, "-n", "-P", "-X",
                            "--format=JobID,JobName%40,State,ExitCode"],
                           capture_output=True, text=True, timeout=300)
    except Exception as exc:  # noqa: BLE001
        log("jobs: sacct day scan failed: %s" % exc)
        return []
    out = []
    for line in r.stdout.splitlines():
        f = line.strip().split("|")
        if len(f) < 4 or job_stage_vessel(f[1]) is None:
            continue
        out.append((f[0], f[1], f[2].split()[0].upper(), f[3]))
    return out


def sacct_tasks(jid):
    """Per-array-task rows for an array job: (jobid_task, state, exitcode)."""
    try:
        r = subprocess.run(["sacct", "-j", str(jid), "-n", "-P",
                            "--format=JobID,State,ExitCode"],
                           capture_output=True, text=True, timeout=180)
    except Exception:  # noqa: BLE001
        return []
    tasks = []
    for line in r.stdout.splitlines():
        f = line.strip().split("|")
        if (len(f) < 3 or "." in f[0]
                or not f[0].startswith(str(jid) + "_")):
            continue
        tasks.append((f[0].strip(), f[1].split()[0].upper(), f[2].strip()))
    return tasks


def jobs(run, ev):
    order = []
    seen = set()
    idx = os.path.join(RUNS, "index.tsv")
    if os.path.isfile(idx):
        with open(idx) as fh:
            for line in fh.read().splitlines()[1:]:
                f = line.split("\t")
                if len(f) < 4:
                    continue
                jid, tag = f[1].strip().split("_")[0], f[3].strip()
                if not jid.isdigit() or jid in seen:
                    continue
                if not (tag == "t09-own-surfaces" or tag.startswith("t09-pot")
                        or tag in ("t09-extract", "t09-extract-retry",
                                   "t09-extract-retry2", "t09-juglet")):
                    continue
                seen.add(jid)
                order.append(jid)
    for jid, name, _state, _code in sacct_day():
        jid = jid.split("_")[0]
        if jid in seen:
            continue
        seen.add(jid)
        order.append(jid)
    out = []
    pending = []
    for jid in sorted(order, key=int):
        state, code, err = sacct_state(jid)
        name, nerr = sacct_name(jid)
        stage, vessel = job_stage_vessel(name) or ("?", name or "?")
        tasks = sacct_tasks(jid)
        if tasks:
            # An array submission is only fully described by its tasks: the parent
            # can read COMPLETED while individual tasks failed 8:0.
            for tid, tstate, tcode in tasks:
                out.append({"job_id": tid, "stage": stage, "vessel": vessel,
                            "state": tstate, "exit_code": tcode})
                if tstate not in TERMINAL:
                    pending.append((tid, tstate))
            continue
        out.append({"job_id": jid, "stage": stage, "vessel": vessel,
                    "state": state,
                    "exit_code": code or ("ERR:" + (err or nerr or "unknown"))})
        if state not in TERMINAL:
            pending.append((jid, state))
    write_tsv(os.path.join(ev, "jobs.tsv"),
              ["job_id", "stage", "vessel", "state", "exit_code"], out)
    log("jobs: %d rows, %d not terminal %s" % (len(out), len(pending), pending[:6]))
    return pending


def sources(run, ev):
    rows = []

    def add(kind, path, detail):
        if not os.path.isfile(path):
            rows.append({"kind": kind, "path": path, "sha256": "MISSING",
                         "bytes": 0, "detail": detail + " (missing)"})
            return
        rows.append({"kind": kind, "path": path, "sha256": sha256_file(path),
                     "bytes": os.path.getsize(path), "detail": detail})

    for f in ("build09.sbatch", "regen09.sbatch", "extract09.py",
              "extract09.sbatch", "launch_e2e09.sh", "report09.py",
              "check09.py"):
        add("t09_script", os.path.join(run, "work", "t09", f),
            "Ticket 09 deliverable (one of the seven ticket scripts)")
    for f in ("make_t09_e2e.sh", "make_t09_juglet.sh"):
        add("t09_generated", os.path.join(run, "work", "t09", f),
            "launch-time make script written by launch_e2e09.sh")
    add("binaries", os.path.join(run, "binaries.sha256"), "built binary hashes")
    add("unit_test", os.path.join(run, "logs", "unit_test.txt"),
        "SurfaceDedupeTest stdout, 5 CASE PASS, fail=0")
    add("stagers", os.path.join(run, "logs", "stagers.sha256"), "frozen stager hashes")
    for rel in ("work/t03_lib.py", "work/t03_extract.py",
                "work/impl_t03/sfs_axes/io_axes.py"):
        add("ship_code", os.path.join(SHIP, rel), "frozen SHIP estimator code")
    before = os.path.join(run, "logs", "corpus_inputs_before.md5")
    after = os.path.join(run, "logs", "corpus_inputs_after.md5")
    detail = "frozen corpus md5 before"
    try:
        detail += " (identical to after: %s)" % (
            "yes" if open(before, "rb").read() == open(after, "rb").read()
            else "NO")
    except OSError:
        pass
    add("corpus_before", before, detail)
    add("corpus_after", after, "frozen corpus md5 after")
    add("t331_before", os.path.join(run, "logs", "t331_inputs_before.md5"),
        "ticket-331 cloud/mesh sha256 before")
    add("t331_after", os.path.join(run, "logs", "t331_inputs_after.md5"),
        "ticket-331 cloud/mesh sha256 after")
    for P in POTS:
        add("e2e_t09", os.path.join(t09_pot(P), "score", "acc.tsv"),
            "t09 pot acc")
    jr = t09_juglet()
    add("e2e_t09", os.path.join(jr, "score", "juglet", "summary.tsv"),
        "t09 juglet summary")
    add("e2e_t08", os.path.join(t08_juglet(), "score", "juglet", "summary.tsv"),
        "t08 juglet summary")
    add("t03_baseline", os.path.join(T03JUG, "score", "juglet", "summary.tsv"),
        "t03 juglet summary")
    for f in ("dedupe27.tsv", "walls.tsv", "walls_nn_detail.tsv", "axes.tsv",
              "fixtures.tsv", "pots_e2e.tsv", "juglet_e2e.tsv",
              "comparison_vs_t08.tsv", "renders.tsv", "jobs.tsv"):
        add("table", os.path.join(ev, f), "evidence table")
    add("render", os.path.join(ev, "renders",
                               "Pot_A_to_J_and_Juglet_t09_regen.png"),
        "11 rows, 20 mm bar, MOR1 vs regenerated K3R1 + Juglet vs oracle")
    return rows


def main():
    global STAMP
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", required=True)
    ap.add_argument("--manifest", default="")
    ap.add_argument("--phase", default="all",
                    choices=["tables", "jobs", "render", "all"])
    a = ap.parse_args()
    STAMP = os.path.basename(os.path.normpath(a.run)).split("_")[0]
    run = a.run
    ev = os.path.join(run, "evidence")
    os.makedirs(ev, exist_ok=True)
    manifest = a.manifest or os.path.join(run, "manifest", "own_surfaces.json")
    log("run=%s stamp=%s phase=%s" % (run, STAMP, a.phase))
    # tables() needs the parsed manifest, not its path
    try:
        with open(manifest) as fh:
            manifest = json.load(fh)
    except OSError:
        manifest = {}

    if a.phase in ("tables", "all"):
        # fixtures first, so a FAIL is visible even if a later table raises
        try:
            tables(run, ev, manifest)
        except SystemExit as exc:
            write_tsv(os.path.join(ev, "fixtures.tsv"), FIX_HEADER,
                      [{"fixture": "manifest_schema_valid", "status": "FAIL",
                        "detail": str(exc)}])
            raise
        jrows = juglet_e2e()
        prows, missing = pots_e2e()
        if missing:
            log("MISSING arms: %s" % (missing,))
        write_tsv(os.path.join(ev, "pots_e2e.tsv"), POTS_E2E_HEADER, prows)
        write_tsv(os.path.join(ev, "juglet_e2e.tsv"), JUG_HEADER, jrows)
        write_tsv(os.path.join(ev, "comparison_vs_t08.tsv"), CMP_HEADER,
                  comparison(prows, jrows))
        log("pots_e2e %d rows, juglet_e2e %d rows" % (len(prows), len(jrows)))
    if a.phase in ("jobs", "all"):
        jobs(run, ev)
    if a.phase in ("render", "all"):
        render(ev)
        write_tsv(os.path.join(ev, "renders.tsv"),
                  ["figure", "path", "scale_bar_mm"],
                  [{"figure": "renders/Pot_A_to_J_and_Juglet_t09_regen.png",
                    "path": "renders/Pot_A_to_J_and_Juglet_t09_regen.png",
                    "scale_bar_mm": SCALE_BAR_MM}])
    if a.phase in ("tables", "all", "render"):
        write_tsv(os.path.join(ev, "sources.tsv"),
                  ["kind", "path", "sha256", "bytes", "detail"], sources(run, ev))
        log("sources.tsv written")
    log("done")


if __name__ == "__main__":
    main()
