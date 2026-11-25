#!/usr/bin/env python3
"""Ticket 08 report: evidence tables, the jobs table and the 11-row 20 mm render.

Reads only what Stage 1 (extract08.py) and Stage 2 (launch_e2e08.sh) wrote under
the run directory, plus the read-only frozen t03 baselines.  Copies the run tables
into <RUN>/evidence, adds sources/jobs/comparison tables, renders
renders/Pot_A_to_J_and_Juglet_e2e.png (11 rows, 20 mm scale bar in every panel).
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
ORACLE = RUNS + "/20261119-1823_f86432b_t336-juglet"
T05 = RUNS + "/20261125-0017_57a4da7_t05-sampling-coverage"

POTS = list("ABCDEFGHIJ")
ARMS = ["MOR1", "MOR2", "K3R1", "K3R2"]
FLOORS = {"A": (8, 8, 15, 15), "B": (9, 9, 15, 15), "C": (4, 4, 5, 5),
          "D": (23, 28, 55, 69), "E": (31, 31, 62, 62), "F": (5, 5, 7, 7),
          "G": (7, 7, 10, 10), "H": (11, 11, 17, 17), "I": (25, 26, 59, 62),
          "J": (8, 11, 16, 21)}
# Which floor a pot is held to, when it is not simply the Ticket 03 floor:
# E is the ticket's own Stage 2A target (31/31 62/62); J has no floor in the
# ticket, only the t03 OWN_RAW comparison, so 16/21 is Ticket 03's own floor.
FLOOR_NOTE = {"E": "floor 31/31 62/62 is the ticket's Stage 2A target",
              "J": "floor 16/21 is Ticket 03's scoring-code floor for J "
                   "(t03_score_pots.py FLOORS, equal to its MOR1/MOR2 row); the "
                   "ticket's J target is the t03 baseline 8/11 5/21"}
TERMINAL = {"COMPLETED", "FAILED", "CANCELLED", "TIMEOUT", "NODE_FAIL",
            "PREEMPTED", "OUT_OF_MEMORY", "BOOT_FAIL", "DEADLINE"}
JUG_LIMIT_MM = 0.50
SCALE_BAR_MM = 20

WALLS_HEADER = ["stem", "pot", "face", "native_points", "points", "duplicate_xyz",
                "xyz_sha256", "normals_sha256", "source_sha256"]
AXES_HEADER = ["stem", "pot", "in_141_gt", "excluded_by_paper", "k_raw", "k_dedup",
               "axes_sha256_dedup", "effective_stride", "drawn_points",
               "rank1_deg_raw", "rank1_deg_dedup", "best_deg_raw", "best_deg_dedup",
               "d_gt_to_est_mm_dedup", "d_est_to_gt_mm_dedup", "is_base_dedup"]
POTS_E2E_HEADER = ["pot", "arm", "sherd", "sherd_den", "edge", "edge_den",
                   "sherd_floor", "edge_floor", "floor_pass", "t03_sherd",
                   "t03_edge", "delta_edge", "wall_secs"]
JUG_HEADER = ["arm", "cluster_len", "cluster_seated", "cluster_max_chamfer_mm",
              "cluster_members_le_050", "edges_strict", "edges_of", "p7_strict",
              "floor_pass"]
CMP_HEADER = ["vessel", "mor_best", "t03_own_raw_best", "t08_own_dedup_best",
              "reached_by", "floor_pass", "regression_vs_t03", "note"]

STAMP = ""
TPL_GIT7 = "2e951d9"  # frozen E2E template commit token inside each run id


def t08_pot(P):
    return os.path.join(RUNS, "%s_%s_t08-pot%s" % (STAMP, TPL_GIT7, P))


def t08_juglet():
    return os.path.join(RUNS, "%s_%s_t08-juglet" % (STAMP, TPL_GIT7))


def log(msg):
    print("[t08-report] " + msg, flush=True)


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
    """Fraction string "31/31" -> (31, 31); anything else -> (None, None)."""
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
    """Best of the given arms: edge count first, then sherd count. Never a median."""
    cand = [(acc[a]["edge"], acc[a]["sherd"], a) for a in arms
            if a in acc and acc[a]["edge"] is not None]
    if not cand:
        return None, []
    best_key = max((c[0], c[1]) for c in cand)
    winners = sorted(c[2] for c in cand if (c[0], c[1]) == best_key)
    return best_key, winners


def fmt_pair(sherd, sherd_den, edge, edge_den):
    return "%s/%s %s/%s" % (sherd, sherd_den, edge, edge_den)


# ---------------------------------------------------------------- tables

def tables(run, ev):
    src = os.path.join(run, "out", "tables")
    head, wrows = read_tsv(os.path.join(src, "walls.tsv"))
    if head != WALLS_HEADER or len(wrows) != 314:
        raise SystemExit("walls.tsv bad: header_ok=%s rows=%d"
                         % (head == WALLS_HEADER, len(wrows)))
    bad = [r["stem"] + ":" + r["face"] for r in wrows if r.get("duplicate_xyz") != "0"]
    if bad:
        raise SystemExit("duplicate_xyz != 0 on %d walls: %s" % (len(bad), bad[:5]))
    head, arows = read_tsv(os.path.join(src, "axes.tsv"))
    if head != AXES_HEADER or len(arows) != 157:
        raise SystemExit("axes.tsv bad: header_ok=%s rows=%d"
                         % (head == AXES_HEADER, len(arows)))
    head, frows = read_tsv(os.path.join(src, "fixtures.tsv"))
    if head != ["fixture", "status", "detail"] or len(frows) < 4:
        raise SystemExit("fixtures.tsv bad")
    for r in frows:
        if r.get("status") != "PASS":
            raise SystemExit("fixture not PASS: %s %s"
                             % (r.get("fixture"), r.get("detail")))
    for name in ("walls.tsv", "axes.tsv", "fixtures.tsv"):
        with open(os.path.join(src, name)) as fi, open(os.path.join(ev, name), "w") as fo:
            fo.write(fi.read())
    log("tables: walls 314 rows dup=0, axes 157 rows, fixtures 4 PASS -> evidence/")


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


def pots_e2e(run):
    rows = []
    missing = []
    for P in POTS:
        r08 = t08_pot(P)
        r03 = os.path.join(RUNS, "20261121-1319_2e951d9_t03-pot%s" % P)
        a08 = acc_rows(r08)
        a03 = acc_rows(r03)
        fl = FLOORS[P]
        for arm in ARMS:
            lab = P + "_" + arm
            if lab not in a08:
                missing.append((P, arm))
                continue
            d = a08[lab]
            o = a03.get(lab, {})
            pass_floor = 1 if (d["sherd"] >= fl[0] and d["edge"] >= fl[2]) else 0
            tsec = panel_walls(r08).get(lab, d["time_s"] or "NA")
            try:
                tsec = "%.4f" % float(tsec)
            except ValueError:
                pass
            rows.append({"pot": P, "arm": lab, "sherd": d["sherd"],
                         "sherd_den": d["sherd_den"], "edge": d["edge"],
                         "edge_den": d["edge_den"],
                         "sherd_floor": "%d/%d" % (fl[0], fl[1]),
                         "edge_floor": "%d/%d" % (fl[2], fl[3]),
                         "floor_pass": pass_floor,
                         "t03_sherd": o.get("sherd", "NA"),
                         "t03_edge": o.get("edge", "NA"),
                         "delta_edge": (d["edge"] - o["edge"])
                         if o.get("edge") is not None else "NA",
                         "wall_secs": tsec})
    return rows, missing


def juglet_e2e(run):
    head, rows = read_tsv(os.path.join(t08_juglet(),
                                       "score", "juglet", "summary.tsv"))
    out = []
    for r in rows:
        seated = int(r["cluster_seated"])
        clen = int(r["cluster_len"])
        mx = float(r["cluster_max_chamfer_mm"])
        ok = 1 if (seated == 9 and clen == 9 and mx <= JUG_LIMIT_MM) else 0
        out.append({"arm": r["arm"], "cluster_len": clen, "cluster_seated": seated,
                    "cluster_max_chamfer_mm": "%.4f" % mx,
                    "cluster_members_le_050": r["cluster_members_le_050"],
                    "edges_strict": r["edges_strict"],
                    "edges_of": r["edges_of"],
                    "p7_strict": r["p7_strict"], "floor_pass": ok})
    return out


def comparison(run, pots, jug):
    rows = []
    for P in POTS:
        r08 = t08_pot(P)
        r03 = os.path.join(RUNS, "20261121-1319_2e951d9_t03-pot%s" % P)
        a08 = acc_rows(r08)
        a03 = acc_rows(r03)
        fl = FLOORS[P]
        mor_key, mor_w = best_of(a08, [P + "_MOR1", P + "_MOR2"])
        t03_key, t03_w = best_of(a03, [P + "_K3R1", P + "_K3R2"])
        t08_key, t08_w = best_of(a08, [P + "_K3R1", P + "_K3R2"])
        if t08_key is None:
            rows.append({"vessel": P, "mor_best": "NA", "t03_own_raw_best": "NA",
                         "t08_own_dedup_best": "NA", "reached_by": "NA",
                         "floor_pass": "NA", "regression_vs_t03": "NA",
                         "note": "Stage 2 arms missing"})
            continue
        reg = "none"
        if t03_key is not None:
            if t08_key[0] > t03_key[0]:
                reg = "improved"
            elif t08_key[0] < t03_key[0]:
                reg = "regressed"
            elif t08_key[1] < t03_key[1]:
                reg = "regressed_sherd"
            elif t08_key[1] > t03_key[1]:
                reg = "improved_sherd"
        d = a08[t08_w[0]]
        pass_floor = 1 if (d["sherd"] >= fl[0] and d["edge"] >= fl[2]) else 0
        notes = []
        if len(t08_w) > 1:
            notes.append("best reached by %d/2 K3 repeats" % len(t08_w))
        if P == "D":
            notes.append("D 18/29 released axis files point away from their own pose (defective input)")
        if P == "C":
            notes.append("C 01 interior Bl0 gap measures the input, not the seat")
        if P == "J":
            notes.append("J 01 interior gap; J 09 excluded from the bar tally")
        if P in ("F", "I", "J"):
            notes.append("paper-excluded pieces still inside the pot totals (see axes.tsv)")
        if P in FLOOR_NOTE:
            notes.append(FLOOR_NOTE[P])
        mor_txt = "NA"
        if mor_key:
            m = a08[mor_w[0]]
            mor_txt = fmt_pair(mor_key[1], m["sherd_den"], mor_key[0], m["edge_den"])
        t03_txt = "NA"
        if t03_key:
            o = a03[t03_w[0]]
            t03_txt = fmt_pair(t03_key[1], o["sherd_den"], t03_key[0], o["edge_den"])
        rows.append({"vessel": P, "mor_best": mor_txt,
                     "t03_own_raw_best": t03_txt,
                     "t08_own_dedup_best": fmt_pair(t08_key[1], d["sherd_den"],
                                                    t08_key[0], d["edge_den"]),
                     "reached_by": ",".join(t08_w), "floor_pass": pass_floor,
                     "regression_vs_t03": reg,
                     "note": "; ".join(notes) if notes else "no caveat"})
    head, jr = read_tsv(os.path.join(t08_juglet(),
                                     "score", "juglet", "summary.tsv"))
    h3, j3 = read_tsv(os.path.join(T03JUG, "score", "juglet", "summary.tsv"))
    if jr:
        best_ch = min(jr, key=lambda r: float(r["cluster_max_chamfer_mm"]))
        best_ed = max(jr, key=lambda r: int(r["edges_strict"]))
        ch_w = sorted(r["arm"] for r in jr
                      if float(r["cluster_max_chamfer_mm"])
                      == float(best_ch["cluster_max_chamfer_mm"]))
        ed_w = sorted(r["arm"] for r in jr
                      if int(r["edges_strict"]) == int(best_ed["edges_strict"]))
        t03ch = (min(j3, key=lambda r: float(r["cluster_max_chamfer_mm"]))
                 if j3 else None)
        t03ed = max(j3, key=lambda r: int(r["edges_strict"])) if j3 else None
        seated_all = all(int(r["cluster_seated"]) == int(r["cluster_len"]) == 9 for r in jr)
        reg = "none"
        if t03ch is not None:
            dch = float(best_ch["cluster_max_chamfer_mm"]) - float(
                t03ch["cluster_max_chamfer_mm"])
            ded = int(best_ed["edges_strict"]) - int(t03ed["edges_strict"])
            if dch < -1e-9 or ded > 0:
                reg = "improved"
            elif dch > 1e-9 or ded < 0:
                reg = "regressed"
        rows.append({"vessel": "JUGLET",
                     "mor_best": "n/a (no authors reference)",
                     "t03_own_raw_best": ("%s/9 @%s mm; edges %s/%s"
                                          % (t03ch["cluster_seated"],
                                             t03ch["cluster_max_chamfer_mm"],
                                             t03ed["edges_strict"],
                                             t03ed["edges_of"])) if t03ch else "NA",
                     "t08_own_dedup_best": "9/9 @%s mm; edges %s/%s"
                     % (best_ch["cluster_max_chamfer_mm"],
                        best_ed["edges_strict"], best_ed["edges_of"]),
                     "reached_by": "chamfer %s (%d/4); edges %s (%d/4); seated_all=%d"
                     % (",".join(x.split("_")[-1] for x in ch_w), len(ch_w),
                        ",".join(x.split("_")[-1] for x in ed_w), len(ed_w),
                        1 if seated_all else 0),
                     "floor_pass": 1 if (seated_all and float(
                         best_ch["cluster_max_chamfer_mm"]) <= JUG_LIMIT_MM) else 0,
                     "regression_vs_t03": reg,
                     "note": "p7_strict %s/4; per-piece seated best %s/9; "
                             "native 3x axes; oracle row in render"
                     % (sum(1 for r in jr if int(r["p7_strict"]) > 0),
                        max(int(r["seated"]) for r in jr))})
    return rows


def sources(run, ev):
    rows = []

    def add(kind, path, detail):
        if not os.path.isfile(path):
            rows.append({"kind": kind, "path": path, "sha256": "MISSING",
                         "bytes": 0, "detail": detail + " (missing)"})
            return
        rows.append({"kind": kind, "path": path, "sha256": sha256_file(path),
                     "bytes": os.path.getsize(path), "detail": detail})

    for f in ("extract08.py", "extract08.sbatch", "launch_e2e08.sh",
              "report08.py", "check08.py"):
        add("t08_script", os.path.join(run, "work", "t08", f), "Ticket 08 deliverable")
    ship_files = ["work/t03_lib.py", "work/t03_extract.py", "work/t03_score_pots.py",
                  "work/t03_render_eleven.py", "work/corpus_md5_t03.py",
                  "work/make_t03_e2e.sh", "work/make_t03_juglet.sh",
                  "work/submit_t03_jugsum.sbatch"]
    impl = os.path.join(SHIP, "work", "impl_t03")
    for root, dirs, files in os.walk(impl):
        depth = root[len(impl):].count(os.sep)
        if depth > 1:
            dirs[:] = []
            continue
        for f in sorted(files):
            if f.endswith(".py"):
                ship_files.append(os.path.relpath(os.path.join(root, f), SHIP))
    for rel in ship_files:
        add("ship_code", os.path.join(SHIP, rel), "frozen Ticket 03 SHIP code")
    for f in ("corpus_inputs_before.md5", "corpus_inputs_after.md5"):
        add("corpus_md5", os.path.join(run, "logs", f), "corpus_md5_t03.py proof")
    add("extract_summary", os.path.join(run, "out", "extract08_summary.json"),
        "Stage 1 summary")
    for name in sorted(os.listdir(os.path.join(SHIP, "out", "axes03_own"))):
        if name.endswith(".xyz"):
            add("raw_baseline", os.path.join(SHIP, "out", "axes03_own", name),
                "t03 OWN_RAW pot axis")
    for name in sorted(os.listdir(os.path.join(SHIP, "out", "axes03_juglet_def3x"))):
        if name.endswith(".xyz"):
            add("raw_baseline", os.path.join(SHIP, "out", "axes03_juglet_def3x", name),
                "t03 OWN_RAW juglet axis")
    for stem in ("Pot_E_Piece_27", "Pot_E_Piece_28"):
        add("pin", os.path.join(T05, "out", "axes05", stem, "OWN_DEDUP_Axis.xyz"),
            "Ticket 05 dedup pin")
    for P in POTS:
        add("e2e_t08", os.path.join(t08_pot(P),
                                    "score", "acc.tsv"), "t08 pot acc")
        add("t03_baseline", os.path.join(RUNS, "20261121-1319_2e951d9_t03-pot%s" % P,
                                         "score", "acc.tsv"), "t03 pot acc")
    jr = t08_juglet()
    add("e2e_t08", os.path.join(jr, "score", "juglet", "summary.tsv"), "t08 juglet summary")
    for arm in ("juglet_own_xy_r1", "juglet_own_xy_r2",
                "juglet_own_xy_r3", "juglet_own_xy_r4"):
        add("e2e_t08", os.path.join(jr, "score", arm + "_cluster.json"), "t08 juglet cluster")
    add("t03_baseline", os.path.join(T03JUG, "score", "juglet", "summary.tsv"),
        "t03 juglet summary")
    for f in ("walls.tsv", "axes.tsv", "fixtures.tsv", "pots_e2e.tsv",
              "juglet_e2e.tsv", "comparison_vs_t03.tsv", "renders.tsv", "jobs.tsv"):
        add("table", os.path.join(ev, f), "evidence table")
    add("render", os.path.join(ev, "renders", "Pot_A_to_J_and_Juglet_e2e.png"),
        "11 rows, 20 mm bar, MOR1 vs K3R1 + Juglet vs oracle")
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
    """20 mm bar in a 2D overlay at the panel's lower left, so no cloud hides it.

    Its length is the same fraction of the panel width that 20 mm is of the
    3D box width (2r), so it stays proportional to the plotted geometry.
    unit_mm converts the plotted coordinates to millimetres (the def_3x
    Juglet panels are in native 3x units, so a 20 mm bar is 60 units there).
    """
    if r <= 0:
        return
    frac = min(0.35, float(length) * float(unit_mm) / (2.0 * r))
    pos = ax.get_position()
    ov = fig.add_axes([pos.x0, pos.y0, pos.width, pos.height], frameon=False)
    ov.set_xlim(0, 1)
    ov.set_ylim(0, 1)
    ov.set_xticks([])
    ov.set_yticks([])
    ov.set_axis_off()
    x0, y0 = 0.06, 0.07
    ov.plot([x0, x0 + frac], [y0, y0], color="black", lw=3.0,
            solid_capstyle="butt", transform=ov.transAxes, clip_on=False)
    ov.text(x0 + frac / 2.0, y0 + 0.018, "%d mm" % length, fontsize=7,
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


def juglet_title(run, arm, label):
    sc = os.path.join(run, "score", arm + ".json")
    cl = os.path.join(run, "score", arm + "_cluster.json")
    txt = "JUGLET %s %s" % (label, arm)
    if os.path.isfile(sc):
        d = json.load(open(sc))
        rows = [r for r in d.get("tables", {}).get("per_edge", [])
                if 7 in (r.get("i"), r.get("j"))]
        good = sum(1 for r in rows if (r.get("deg") or 999.0) < 5.0)
        txt += " p7 %d/%d <5deg" % (good, len(rows))
    if os.path.isfile(cl):
        cd = json.load(open(cl))
        txt += " cluster %s/%s @%.3f mm" % (cd.get("cluster_seated"),
                                           cd.get("cluster_len"),
                                           cd.get("cluster_max_chamfer_mm") or -1)
    return txt


def render(run, ev):
    nrow = len(POTS) + 1
    fig = plt.figure(figsize=(17, 44))
    bars = []
    for row, P in enumerate(POTS):
        r08 = t08_pot(P)
        acc = acc_rows(r08)
        for col, (suffix, label) in enumerate([("_MOR1", "MOR1 [Authors control]"),
                                               ("_K3R1", "K3R1 [own code, dedup]")]):
            arm = P + suffix
            d = acc.get(arm, {})
            s = ("%s/%s" % (d.get("sherd"), d.get("sherd_den"))
                 if d.get("sherd") is not None else "-")
            e = ("%s/%s" % (d.get("edge"), d.get("edge_den"))
                 if d.get("edge") is not None else "-")
            bars.append(panel(fig, nrow, 2, row * 2 + col + 1,
                              os.path.join(r08, "out", arm),
                              "%s [%s] sherd %s edge %s" % (arm, label, s, e)))
    jrow = len(POTS)
    jr = t08_juglet()
    bars.append(panel(fig, nrow, 2, jrow * 2 + 1,
                      os.path.join(jr, "out", "juglet_own_xy_r1"),
                      juglet_title(jr, "juglet_own_xy_r1",
                                   "def_3x dedup axes [own code]"),
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
    fig.suptitle("Ticket 08: deduplicated own surfaces -- ten pots (rows 1-10) and the "
                 "def_3x Juglet (row 11); authors control left, deduplicated own chain right",
                 fontsize=14, y=0.998)
    fig.tight_layout(rect=[0, 0, 1, 1])
    fig.subplots_adjust(top=0.958, hspace=0.02)
    for ax, c, r, u in bars:
        scale_bar(fig, ax, c, r, SCALE_BAR_MM, u)
    out = os.path.join(ev, "renders", "Pot_A_to_J_and_Juglet_e2e.png")
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


def stage_vessel(tag):
    """Map a t08 run tag to (stage, vessel); None for a tag this ticket did not launch.

    runs/index.tsv is shared, and an older ticket used the prefix
    "t08-dedup-shortlist", so the tag must match this ticket's exact names.
    """
    if tag == "t08-ship":
        return "stage1", "ship"
    if tag.startswith("t08-pot"):
        pot = tag[len("t08-pot"):]
        if not pot or not set(pot) <= set("ABCDEFGHIJ"):
            return None
        return ("2A" if pot in "EGDJ" else "2B"), "POT" + pot
    if tag in ("t08-juglet", "t08-jugsum"):
        return "2A", "JUGLET"
    if tag == "t08-report":
        return "report", "summary"
    return None


def job_stage_vessel(name):
    """(stage, vessel) from a Slurm job name; None for anything not this ticket."""
    if not name.startswith("t08-"):
        return None
    if name == "t08-ship":
        return "stage1", "ship"
    if name == "t08-smoke":
        return "stage1", "smoke"
    if name == "t08-jugfix":
        return "stage1", "jugfix"
    if name.startswith("t08-pot"):
        pot = name[len("t08-pot"):]
        if not pot or not set(pot) <= set("ABCDEFGHIJ"):
            return None
        return ("2A" if pot in "EGDJ" else "2B"), "POT" + pot
    if name == "t08-juglet":
        return "2A", "JUGLET"
    if name == "t08-jugsum":
        return "jugsum", "JUGLET"
    if name == "t08-report":
        return "report", "ALL"
    if name == "t08-tables":
        return "report", "tables"
    if name == "t08-bars":
        return "report", "render"
    return None


def sacct_day():
    """Every job named t08-* sacct knows on the run's day -> (job_id, name, state, exit).

    jobs_submitted.tsv and runs/index.tsv are both written by the launcher, so a
    discarded attempt can drop out of both; sacct is the only complete record of
    every job this ticket ever submitted.
    """
    d0 = "%s-%s-%s" % (STAMP[0:4], STAMP[4:6], STAMP[6:8])
    d1 = (datetime.date(int(d0[0:4]), int(d0[5:7]), int(d0[8:10]))
          + datetime.timedelta(days=1)).isoformat()
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
        if len(f) < 4 or not f[1].startswith("t08-"):
            continue
        out.append((f[0], f[1], f[2].split()[0].upper(), f[3]))
    return out


def jobs(run, ev):
    head, rows = read_tsv(os.path.join(run, "out", "jobs_submitted.tsv"))
    order = []
    seen = set()
    for r in rows:
        jid = str(r.get("job_id", "")).strip().split("_")[0]  # array tasks fold to the parent
        if not jid or jid in seen:
            continue
        seen.add(jid)
        order.append((jid, r.get("stage", "NA"), r.get("vessel", "NA")))
    idx = os.path.join(RUNS, "index.tsv")
    if os.path.isfile(idx):
        with open(idx) as fh:
            for line in fh.read().splitlines()[1:]:
                f = line.split("	")
                if len(f) < 4:
                    continue
                runid, jid, tag = f[0], f[1].strip().split("_")[0], f[3].strip()
                if not jid.isdigit() or jid in seen:
                    continue
                if not (tag.startswith("t08-") and runid.endswith("_" + tag)):
                    continue
                sv = stage_vessel(tag)
                if sv is None:
                    continue
                seen.add(jid)
                order.append((jid,) + sv)
    for jid, name, _state, _code in sacct_day():
        jid = jid.split("_")[0]  # array tasks fold to the parent
        if jid in seen:
            continue
        sv = job_stage_vessel(name)
        if sv is None:
            continue
        seen.add(jid)
        order.append((jid,) + sv)
    out = []
    pending = []
    for jid, stage, vessel in sorted(order, key=lambda t: int(t[0])):
        state, code, err = sacct_state(jid)
        out.append({"job_id": jid, "stage": stage, "vessel": vessel,
                    "state": state,
                    "exit_code": code or ("ERR:" + err if err else "")})
        if state not in TERMINAL:
            pending.append((jid, state))
    write_tsv(os.path.join(ev, "jobs.tsv"),
              ["job_id", "stage", "vessel", "state", "exit_code"], out)
    log("jobs: %d rows, %d not terminal %s" % (len(out), len(pending), pending[:6]))
    return pending


def main():
    global STAMP
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", required=True)
    ap.add_argument("--phase", default="all",
                    choices=["tables", "jobs", "render", "all"])
    a = ap.parse_args()
    STAMP = os.path.basename(os.path.normpath(a.run)).split("_")[0]
    run = a.run
    ev = os.path.join(run, "evidence")
    os.makedirs(ev, exist_ok=True)
    log("run=%s stamp=%s phase=%s" % (run, STAMP, a.phase))

    if a.phase in ("tables", "all"):
        tables(run, ev)
        jrows = juglet_e2e(run)
        prows, missing = pots_e2e(run)
        if missing:
            log("MISSING arms: %s" % (missing,))
        write_tsv(os.path.join(ev, "pots_e2e.tsv"), POTS_E2E_HEADER, prows)
        write_tsv(os.path.join(ev, "juglet_e2e.tsv"), JUG_HEADER, jrows)
        write_tsv(os.path.join(ev, "comparison_vs_t03.tsv"), CMP_HEADER,
                  comparison(run, prows, jrows))
        log("pots_e2e %d rows, juglet_e2e %d rows, comparison %d rows"
            % (len(prows), len(jrows),
               len(read_tsv(os.path.join(ev, "comparison_vs_t03.tsv"))[1])))
    if a.phase in ("jobs", "all"):
        jobs(run, ev)
    if a.phase in ("render", "all"):
        render(run, ev)
        write_tsv(os.path.join(ev, "renders.tsv"),
                  ["figure", "path", "scale_bar_mm"],
                  [{"figure": "renders/Pot_A_to_J_and_Juglet_e2e.png",
                    "path": "renders/Pot_A_to_J_and_Juglet_e2e.png",
                    "scale_bar_mm": SCALE_BAR_MM}])
    if a.phase in ("tables", "all", "render"):
        write_tsv(os.path.join(ev, "sources.tsv"),
                  ["kind", "path", "sha256", "bytes", "detail"], sources(run, ev))
        log("sources.tsv %d rows"
            % len(read_tsv(os.path.join(ev, "sources.tsv"))[1]))
    log("done")


if __name__ == "__main__":
    main()
