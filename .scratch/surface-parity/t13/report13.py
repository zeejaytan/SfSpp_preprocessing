#!/usr/bin/env python3
"""Ticket 13 report: rebuild every evidence table from bytes on disk.

Usage: report13.py --run <RUN_DIR> [--no-sacct]

Reads (never invents): out/<arm>_<rep>/T_*to_*.txt, score/<arm>_<rep>.tsv,
logs/cell_raw_*.json, logs/array_map.tsv, logs/axis_diff.tsv, logs/j01_status.json,
j01/walls/*.xyz, j01/axes/*/*.xyz, evidence/j01_*.tsv.

Writes under <RUN>/evidence: sources.tsv, cells.tsv, seams.tsv, summary_partA.tsv,
j01_walls.tsv (refreshed), j01_factors.tsv (refreshed), fixtures.tsv, b2_gate.tsv,
renders.tsv, jobs.tsv, and renders/Pot_J_t08_vs_t09_and_swaps.png.
Exit 0 = every table written; 3 = a required input is missing (details on stdout).
"""
import argparse
import hashlib
import json
import os
import glob
import subprocess
import sys

ANG_BAR = 20.05
T_BAR = 50.0
PART_A_ARMS = ["MOR_CTL", "T08_ALL", "T09_ALL", "T09_WITH_AUTHOR_J01",
               "SWAP_J01", "SWAP_J02", "SWAP_J05", "SWAP_J06", "SWAP_J11"]
PART_A_REPS = {"MOR_CTL": 2, "T08_ALL": 4, "T09_ALL": 4, "T09_WITH_AUTHOR_J01": 2,
               "SWAP_J01": 2, "SWAP_J02": 2, "SWAP_J05": 2, "SWAP_J06": 2, "SWAP_J11": 2}
WANT_SHA = "de44ffc23c8db5208bd5f6f9c9f57d819bed7805f0330526bcb2750487bfd727"


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def sha256_tree(path):
    """sha256 over the sorted (relpath, size, sha256) listing of a directory tree."""
    rows = []
    for root, _dirs, files in os.walk(path):
        for name in sorted(files):
            full = os.path.join(root, name)
            rows.append("%s %d %s" % (os.path.relpath(full, path), os.path.getsize(full), sha256_file(full)))
    return hashlib.sha256(("\n".join(sorted(rows)) + "\n").encode("utf-8")).hexdigest(), len(rows)


def write_tsv(path, header, rows):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="") as fh:
        fh.write("\t".join(header) + "\n")
        for row in rows:
            fh.write("\t".join(str(x) for x in row) + "\n")
    return path


def write_csv(path, header, rows):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="") as fh:
        fh.write(",".join(header) + "\n")
        for row in rows:
            fh.write(",".join(str(x) for x in row) + "\n")
    return path


def read_tsv(path):
    if not os.path.exists(path):
        return []
    with open(path, encoding="utf-8") as fh:
        return [ln.rstrip("\n").split("\t") for ln in fh if ln.strip()]


def parse_score(path):
    """Return pieces, joins and the SUMMARY counts from one score305.py output."""
    if not os.path.exists(path):
        return None
    pieces, joins, summary = [], [], None
    mode = None
    with open(path, encoding="utf-8") as fh:
        for ln in fh:
            ln = ln.rstrip("\n")
            if ln.startswith("SUMMARY"):
                summary = ln
                continue
            if ln.startswith("#") or not ln:
                continue
            f = ln.split("\t")
            if f[0] == "piece":
                mode = "p"
                continue
            if f[0] == "join_i":
                mode = "j"
                continue
            if mode == "p" and len(f) >= 4:
                pieces.append({"piece": int(f[0]), "ang": float(f[1]), "t": float(f[2]), "verdict": f[3]})
            elif mode == "j" and len(f) >= 5:
                joins.append({"i": int(f[0]), "j": int(f[1]), "ang": float(f[2]), "t": float(f[3]), "verdict": f[4]})
    piece_counts = (0, 0)
    join_counts = (0, 0)
    if summary:
        for part in summary.split("\t"):
            if part.startswith("pieces="):
                a, b = part.split("=", 1)[1].split("/")
                piece_counts = (int(a), int(b))
            elif part.startswith("joins="):
                a, b = part.split("=", 1)[1].split("/")
                join_counts = (int(a), int(b))
    return {"pieces": pieces, "joins": joins, "piece_counts": piece_counts, "join_counts": join_counts}


def arm_of(tag):
    """B2_OWN_VOXEL_1MM_1 -> B2_OWN_VOXEL_1MM ; SWAP_J01_2 -> SWAP_J01."""
    return tag.rsplit("_", 1)[0] if tag else tag
def load_json(path, default=None):
    try:
        with open(path, encoding="utf-8") as fh:
            return json.load(fh)
    except Exception:
        return default


def collect_cells(run):
    """Every cell that actually finished writes logs/cell_raw_<arm>_<rep>.json."""
    rows = []
    for path in sorted(glob.glob(os.path.join(run, "logs", "cell_raw_*.json"))):
        d = load_json(path, {})
        if not d:
            continue
        tag = str(d.get("arm", "")) + "_" + str(d.get("rep", ""))
        sc = parse_score(os.path.join(run, "score", tag + ".tsv"))
        sherd = sc["piece_counts"] if sc else (0, 0)
        joins = sc["join_counts"] if sc else (0, 0)
        rows.append({
            "arm": str(d.get("arm", "")), "rep": str(d.get("rep", "")),
            "job_id": str(d.get("job_id", "")), "stage": str(d.get("stage", "")),
            "usable": int(d.get("usable", 0)),
            "exported_poses": int(d.get("exported_poses", 0)),
            "sherd": sherd[0], "sherd_den": sherd[1],
            "joins": joins[0], "joins_den": joins[1],
            "exe_sha_ok": int(d.get("exe_sha_ok", 0)),
            "inputs_unchanged": int(d.get("inputs_unchanged", 0)),
            "changed": int(d.get("changed_axis_files", -1)),
            "wall": int(d.get("wall_secs", 0)),
            "score": sc, "raw": d,
        })
    return rows


def cell_order(rows):
    order = {a: i for i, a in enumerate(PART_A_ARMS)}
    def key(c):
        return (0 if c["arm"] in order else 1, order.get(c["arm"], 99), c["arm"], int(c["rep"]) if c["rep"].isdigit() else 0)
    return sorted(rows, key=key)


def missing_expected(run, cells):
    """Array rows that never wrote a cell_raw json (job died before scoring)."""
    have = {(c["arm"], c["rep"]) for c in cells}
    job = ""
    jp = os.path.join(run, "logs", "array_job.txt")
    if os.path.exists(jp):
        job = open(jp, encoding="utf-8").read().strip()
    out = []
    for row in read_tsv(os.path.join(run, "logs", "array_map.tsv")):
        if len(row) < 4:
            continue
        idx, stage, arm, rep = row[0], row[1], row[2], row[3]
        if (arm, rep) in have:
            continue
        out.append({"idx": idx, "stage": stage, "arm": arm, "rep": rep,
                    "job_id": (job + "_" + idx) if job else ""})
    return out


def seam_rows(cells):
    rows = []
    for c in cell_order(cells):
        if not c["usable"] or not c["score"]:
            continue
        for j in c["score"]["joins"]:
            ok = (j["ang"] <= ANG_BAR and j["t"] <= T_BAR)
            rows.append([c["arm"], c["rep"], j["i"], j["j"],
                         "%.4f" % j["ang"], "%.4f" % j["t"], "pass" if ok else "fail"])
    return rows


def partA_summary(cells):
    best_t09 = 0
    for c in cells:
        if c["arm"] == "T09_ALL" and c["usable"]:
            best_t09 = max(best_t09, c["joins"])
    notes = {
        "MOR_CTL": "positive control: corpus M-orientation axes, 12/12 files differ from T09",
        "T08_ALL": "T08 axis pack (own-surface axes before the T09 regeneration)",
        "T09_ALL": "reference: the ticket's own-surface axes; 0 files should differ",
        "T09_WITH_AUTHOR_J01": "T09 pack with only Pot_J_Piece_01_Axis.xyz from the SHIP AUTHOR-wall axis",
        "SWAP_J01": "T09 pack with only J01's axis file from T08",
        "SWAP_J02": "T09 pack with only J02's axis file from T08",
        "SWAP_J05": "T09 pack with only J05's axis file from T08",
        "SWAP_J06": "T09 pack with only J06's axis file from T08",
        "SWAP_J11": "T09 pack with only J11's axis file from T08",
    }
    rows = []
    for arm in PART_A_ARMS:
        sub = [c for c in cells if c["arm"] == arm]
        ok = [c for c in sub if c["usable"]]
        all_joins = " ".join(str(c["joins"]) for c in sub if c["usable"]) or "-"
        if ok:
            best = max(ok, key=lambda c: (c["joins"], c["sherd"]))
            reached = sum(1 for c in ok if c["joins"] == best["joins"])
            delta = best["joins"] - best_t09 if arm != "T09_ALL" else 0
            rows.append([arm, len(ok), "%d/%d" % (best["sherd"], best["sherd_den"]), best["joins"],
                         "%d/%d" % (reached, len(ok)), all_joins, delta, notes[arm]])
        else:
            rows.append([arm, 0, "0/0", 0, "0/0", all_joins, -best_t09, notes[arm] + " (no usable repeat)"])
    return rows
MT = "/data/gpfs/projects/punim2657/sfs_main"
SIF = os.path.join(MT, "sfs_pristine_assembly.sif")
SHIP = "/data/gpfs/projects/punim2657/SfSpp/runs/20261121-1319_2e951d9_t03-ship"
TREE = "/data/gpfs/projects/punim2657/SfSpp/runs/20261125-1451_a50f8cc_t09-potJ/trees/J_K3R1/J/MM"
PIECES_TSV = "/data/gpfs/projects/punim2657/SfSpp/runs/20261125-1451_a50f8cc_t09-potJ/trees/J_K3R1/arm_pieces_J.tsv"
SCORER = "/data/gpfs/projects/punim2657/SfSpp/runs/20261125-1451_a50f8cc_t09-potJ/work/score305.py"
ACC = "/data/gpfs/projects/punim2657/SfSpp/runs/20261125-1451_a50f8cc_t09-potJ/work/acc305.py"
SCRIPT_NAMES = ["j01_factors13.py", "prep13.sbatch", "cell13.sbatch",
                "posecheck13.sh", "report13.py", "check13.py"]
OWN_ARMS = ["OWN_T09", "AUTHOR", "OWN_AUTHOR_NORMALS", "AUTHOR_OWN_NORMALS", "OWN_SHARED_1MM",
            "AUTHOR_SHARED_1MM", "OWN_VOXEL_1MM", "AUTHOR_VOXEL_1MM", "OWN_BALANCED_S0S1"]


def build_sources(run, cells):
    rows = []

    def add(kind, path, detail):
        if not os.path.exists(path):
            rows.append([kind, path, "-", 0, detail + " (MISSING)"])
        elif os.path.isdir(path):
            h, n = sha256_tree(path)
            rows.append([kind, path, h, n, detail + " | dir, bytes column = %d files" % n])
        else:
            rows.append([kind, path, sha256_file(path), os.path.getsize(path), detail])

    add("executable", os.path.join(run, "panel", "build", "Hierarchy-T13"), "pinned Hierarchy-T13, hardlinked from the t13-recip build")
    add("container", SIF, "apptainer image used for every cell")
    add("tree", TREE, "frozen Pot J J_K3R1 tree, bound read-only")
    for arm in PART_A_ARMS:
        add("axis_pack", os.path.join(run, "axes", arm), "12 Pot J axis files staged for this arm")
    add("score_script", SCORER, "score305.py joins/pieces scorer")
    add("acc_script", ACC, "acc305.py accuracy parser")
    add("pieces_tsv", PIECES_TSV, "arm_pieces_J.tsv eligibility (piece 9 off)")
    add("corpus_md5_before", os.path.join(run, "logs", "corpus_md5_before.txt"), "corpus pin before any read")
    add("corpus_md5_after", os.path.join(run, "logs", "corpus_md5_after.txt"), "corpus pin after the array")
    for c in cell_order(cells):
        add("score", os.path.join(run, "score", c["arm"] + "_" + c["rep"] + ".tsv"), "score305 output for this cell")
    for arm in OWN_ARMS:
        add("j01_axes", os.path.join(run, "j01", "axes", arm), "axis written by this Part B arm")
    add("j01_factors", os.path.join(run, "evidence", "j01_factors.tsv"), "Part B factor table")
    add("j01_walls", os.path.join(run, "evidence", "j01_walls.tsv"), "Part B wall table")
    wk = os.path.join(run, "work", "t13")
    for fn in SCRIPT_NAMES:
        add("script", os.path.join(wk, fn), "ticket script as run (bytes on Spartan)")
    add("work_dir", wk, "the six ticket scripts as run (one tree hash)")
    return rows


def run_corpus_md5(run):
    out = os.path.join(run, "logs", "corpus_md5_after.txt")
    script = os.path.join(SHIP, "work", "corpus_md5_t03.py")
    py = "/data/gpfs/projects/punim2657/TORA/envs/tora/bin/python3"
    try:
        subprocess.run([py, script, "--out", out], check=False,
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=3600)
    except Exception:
        return False
    return os.path.exists(out)


def build_fixtures(run, cells):
    st = load_json(os.path.join(run, "logs", "j01_status.json"), {}) or {}
    rows = []

    def fx(name, ok, detail):
        rows.append([name, "PASS" if ok else "FAIL", detail])

    want = ""
    sha_list = os.path.join(run, "panel", "logs", "executable.sha256")
    if os.path.exists(sha_list):
        want = open(sha_list, encoding="utf-8").read().split()[0]
    got = sha256_file(os.path.join(run, "panel", "build", "Hierarchy-T13"))
    fx("exe_pin_match", got == want and got == WANT_SHA, "panel exe %s vs list %s" % (got[:16], want[:16]))
    fx("own_t09_pin_match", bool(st.get("own_t09_pin_match")),
       "OWN_T09 xyz sha %s vs Ticket 09 pin %s"
       % (str(st.get("own_t09_axes_sha256", ""))[:16], str(st.get("own_t09_pin_sha", ""))[:16]))
    fx("author_donor_match", bool(st.get("author_donor_match")),
       "AUTHOR best candidate %.4f deg, %.4f mm from the donor line"
       % (float(st.get("author_best_donor_deg", -1)), float(st.get("author_best_donor_mm", -1))))
    fx("normal_transfer_fixed_xyz", bool(st.get("normal_transfer_fixed_xyz")),
       "%s" % str(st.get("normal_transfer_detail", "1-NN normals transferred, xyz bit-identical")))
    diff = {r[0]: int(r[1]) for r in read_tsv(os.path.join(run, "logs", "axis_diff.tsv")) if len(r) > 1}
    swaps_ok = all(diff.get(a) == 1 for a in ("SWAP_J01", "SWAP_J02", "SWAP_J05", "SWAP_J06", "SWAP_J11"))
    fx("single_file_swap_proof", swaps_ok and diff.get("T09_ALL") == 0 and diff.get("T09_WITH_AUTHOR_J01") == 1,
       "changed_axis_files " + " ".join("%s=%s" % (a, diff.get(a, "?")) for a in PART_A_ARMS))
    before = os.path.join(run, "logs", "corpus_md5_before.txt")
    after = os.path.join(run, "logs", "corpus_md5_after.txt")
    same = os.path.exists(before) and os.path.exists(after) and sha256_file(before) == sha256_file(after)
    nlines = sum(1 for _ in open(before, encoding="utf-8")) if os.path.exists(before) else -1
    fx("corpus_unchanged", same, "corpus md5 before/after identical (lines before=%d)" % nlines)
    usable = [c for c in cells if c["usable"]]
    fx("cells_usable", len(cells) > 0 and len(usable) == len(cells),
       "usable %d/%d cells" % (len(usable), len(cells)))
    return rows


def ids_of_record(run):
    """Job ids that produced this evidence: the array of record, its report job, prep, and any ad hoc stage job.

    Deliberately not a time window: sacct -S still returns short failed jobs from superseded
    launcher attempts, and those are recorded in logs/run_status.txt instead (the ticket allows
    a run note there). The job running this function is excluded so a terminal-mode check does
    not report itself as unfinished.
    """
    ids = []
    for fn in ("array_job.txt", "report_job.txt"):
        path = os.path.join(run, "logs", fn)
        if os.path.exists(path):
            tok = open(path, encoding="utf-8").read().split()
            if tok:
                ids.append(tok[0])
    j = load_json(os.path.join(run, "logs", "prep_status.json"), {}) or {}
    if j.get("prep_job"):
        ids.append(str(j["prep_job"]))
    path = os.path.join(run, "logs", "extra_jobs.txt")
    if os.path.exists(path):
        for ln in open(path, encoding="utf-8"):
            ln = ln.split("#")[0].strip()
            if ln:
                ids.append(ln.split()[0])
    cur = os.environ.get("SLURM_JOB_ID", "")
    curarr = os.environ.get("SLURM_ARRAY_JOB_ID", "")
    out = []
    for i in ids:
        if cur and (i == cur or (curarr and (i == curarr or i.startswith(curarr + "_")))):
            continue
        if i not in out:
            out.append(i)
    return out


def sacct_jobs(run):
    ids = ids_of_record(run)
    if not ids:
        return []
    try:
        out = subprocess.run(["sacct", "-n", "-P", "-j", ",".join(ids),
                              "-o", "JobID,JobName,State,ExitCode"],
                             capture_output=True, text=True, timeout=180).stdout
    except Exception:
        return []
    amap = {}
    for row in read_tsv(os.path.join(run, "logs", "array_map.tsv")):
        if len(row) >= 4:
            amap[row[0]] = (row[2], row[3])
    rows = []
    for ln in out.splitlines():
        f = ln.split("|")
        if len(f) < 4 or "." in f[0]:
            continue
        jid, name, state, code = f[0], f[1], f[2], f[3]
        if not name.startswith("t13-") and "_" not in jid:
            continue
        stage = name.replace("t13-", "") if name.startswith("t13-") else "cell"
        arm, rep = "-", "-"
        if "_" in jid:
            _base, idx = jid.split("_", 1)
            if idx in amap:
                arm, rep = amap[idx]
        rows.append([jid, stage, arm, rep, state, code])
    return rows
def read_table(path):
    """Read a comma- or tab-separated table written by this ticket's scripts."""
    if not os.path.exists(path):
        return []
    with open(path, encoding="utf-8") as fh:
        rows = [ln.rstrip("\n") for ln in fh if ln.strip()]
    if not rows:
        return []
    sep = "\t" if "\t" in rows[0] else ","
    return [r.split(sep) for r in rows]


def clean(x):
    return str(x).replace(",", ";").replace("\t", " ").replace("\n", " ")


def csv_rows(rows):
    return [[clean(x) for x in r] for r in rows]


def b2_gate(run, cells):
    fp = os.path.join(run, "evidence", "j01_factors.tsv")
    rows = read_table(fp)
    if len(rows) < 2:
        return [], "missing_j01_factors", []
    header, body = rows[0], [r for r in rows[1:] if len(r) >= 11]
    def num(x):
        try:
            return float(x)
        except Exception:
            return 1e9
    cands = [r for r in body if r[0].startswith("OWN_") and r[0] != "OWN_T09" and r[10] == "1"]
    cands.sort(key=lambda r: (num(r[7]), num(r[6])))
    chosen = [r[0] for r in cands[:2]]
    out = []
    for r in body:
        if not r[0].startswith("OWN_"):
            continue
        sub = [c for c in cells if c["arm"] == "B2_" + r[0]]
        best = max((c["joins"] for c in sub), default=None)
        if best is not None:
            r[11] = str(best)
        route = "donor" if (num(r[7]) <= 15.0 and num(r[8]) <= 15.0) else ("gt" if num(r[6]) <= 25.0 else "none")
        rank = (cands.index(r) + 1) if r in cands else "-"
        out.append([r[0], r[10], route, r[6], r[7], r[8], rank,
                    1 if r[0] in chosen else 0, len(sub), best if best is not None else "-"])
    write_csv(fp, header, body)
    if not chosen:
        status = "skipped_no_qualifying_arm"
    elif any(c["arm"].startswith("B2_") for c in cells):
        status = "submitted"
    else:
        status = "pending_submit"
    return out, status, chosen


def render_partA(run, cells):
    """Left: which of the 21 GT joins pass, per arm. Right: joins passed, best of repeats."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.patches import Rectangle

    order = []
    for c in cell_order(cells):
        if c["arm"] == "T09_ALL" and c["usable"] and c["score"]:
            order = [(j["i"], j["j"]) for j in c["score"]["joins"]]
            break
    if not order:
        seen = set()
        for c in cells:
            if c["usable"] and c["score"]:
                for j in c["score"]["joins"]:
                    key = (j["i"], j["j"])
                    if key not in seen:
                        seen.add(key)
                        order.append(key)
        order.sort()

    best = {}
    for arm in PART_A_ARMS:
        sub = [c for c in cells if c["arm"] == arm and c["usable"] and c["score"]]
        if sub:
            best[arm] = max(sub, key=lambda c: (c["joins"], c["sherd"]))
    diff = {r[0]: r[1] for r in read_tsv(os.path.join(run, "logs", "axis_diff.tsv")) if len(r) > 1}

    fig = plt.figure(figsize=(15.5, 7.2))
    gs = fig.add_gridspec(2, 2, width_ratios=[2.35, 1.0], height_ratios=[1.0, 0.10],
                          hspace=0.28, wspace=0.28)
    ax = fig.add_subplot(gs[0, 0])
    axb = fig.add_subplot(gs[0, 1])
    axs = fig.add_subplot(gs[1, 0])
    arms = [a for a in PART_A_ARMS if a in best]
    for row, arm in enumerate(arms):
        c = best[arm]
        verdict = {}
        for j in c["score"]["joins"]:
            verdict[(j["i"], j["j"])] = (j["ang"] <= ANG_BAR and j["t"] <= T_BAR)
        for col, key in enumerate(order):
            ok = verdict.get(key, False)
            ax.add_patch(Rectangle((col, row - 0.42), 0.92, 0.84,
                                   facecolor="#2e8b57" if ok else "#c1443b",
                                   edgecolor="white", linewidth=0.6))
        ax.text(len(order) + 0.4, row, "%d/%d" % (c["joins"], c["joins_den"]),
                va="center", ha="left", fontsize=9, fontweight="bold")
    ax.set_xlim(0, len(order) + 2.4)
    ax.set_ylim(len(arms) - 0.4, -0.6)
    ax.set_xticks([i + 0.45 for i in range(len(order))])
    ax.set_xticklabels(["%d-%d" % k for k in order], rotation=60, fontsize=7, ha="right")
    labels = []
    for arm in arms:
        d = diff.get(arm, "?")
        labels.append("%s (changed %s)" % (arm, d))
    ax.set_yticks(range(len(arms)))
    ax.set_yticklabels(labels, fontsize=9)
    ax.set_xlabel("GT join (piece i - piece j), ticket order", fontsize=9)
    ax.set_title("Ticket 13 Part A - joins passing the 20.05 deg / 50 mm bar, best repeat per arm",
                 fontsize=11, loc="left")
    ax.legend(handles=[Rectangle((0, 0), 1, 1, facecolor="#2e8b57"),
                       Rectangle((0, 0), 1, 1, facecolor="#c1443b")],
              labels=["join passes", "join fails"], loc="lower right", fontsize=8, framealpha=0.9)

    names = list(reversed(arms))
    vals = [best[a]["joins"] for a in names]
    axb.barh(range(len(names)), vals, color="#3f6fa8", height=0.62)
    t09 = best.get("T09_ALL", {}).get("joins")
    if t09 is not None:
        axb.axvline(t09, color="#c1443b", linestyle="--", linewidth=1.2)
        axb.set_ylim(-0.85, len(names) - 0.4)
        axb.text(t09, -0.72, "T09_ALL %d" % t09, color="#c1443b",
                 fontsize=8, ha="center", va="center")
    axb.set_yticks(range(len(names)))
    axb.set_yticklabels(names, fontsize=8)
    axb.set_xlim(0, max(len(order), 1))
    axb.set_xlabel("joins passed (of 21)", fontsize=9)
    axb.set_title("best of repeats", fontsize=10, loc="left")
    for i, v in enumerate(vals):
        axb.text(v + 0.3, i, str(v), va="center", fontsize=8)

    axs.set_axis_off()
    axs.plot([0.02, 0.22], [0.5, 0.5], color="black", linewidth=2.2, transform=axs.transAxes,
             clip_on=False)
    axs.text(0.115, 0.74, "20 mm", ha="center", fontsize=9, transform=axs.transAxes)
    axs.text(0.26, 0.42, "scale bar (20 mm); join strip is a verdict map, not geometry",
             fontsize=8, transform=axs.transAxes)

    out = os.path.join(run, "renders", "Pot_J_t08_vs_t09_and_swaps.png")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    fig.savefig(out, dpi=140, bbox_inches="tight", facecolor="white")
    plt.close(fig)

    rows = [["Pot_J_t08_vs_t09_and_swaps", out, 20]]
    j01 = os.path.join(run, "renders", "J01_surface_factors_overlay.png")
    if os.path.exists(j01):
        rows.append(["J01_surface_factors_overlay", j01, 20])
    return rows


def main():
    ap = argparse.ArgumentParser(description="Ticket 13 report")
    ap.add_argument("--run", required=True)
    ap.add_argument("--no-sacct", action="store_true")
    a = ap.parse_args()
    run = os.path.abspath(a.run)
    ev = os.path.join(run, "evidence")
    os.makedirs(ev, exist_ok=True)
    run_corpus_md5(run)
    cells = collect_cells(run)
    miss = missing_expected(run, cells)
    crows = []
    for c in cell_order(cells):
        crows.append([c["arm"], c["rep"], c["job_id"], c["usable"], c["exported_poses"],
                      c["sherd"], c["sherd_den"], c["joins"], c["joins_den"],
                      c["exe_sha_ok"], c["inputs_unchanged"], c["changed"], c["wall"]])
    for m in miss:
        crows.append([m["arm"], m["rep"], m["job_id"], 0, 0, 0, 0, 0, 0, 0, 0, -1, 0])
    write_csv(os.path.join(ev, "cells.tsv"),
              ["arm", "rep", "job_id", "usable", "exported_poses", "sherd", "sherd_den",
               "joins_pass", "joins_total", "exe_sha_ok", "inputs_unchanged",
               "changed_axis_files", "wall_secs"], csv_rows(crows))
    write_csv(os.path.join(ev, "seams.tsv"),
              ["arm", "rep", "join_i", "join_j", "ang_deg", "t_mm", "verdict"], csv_rows(seam_rows(cells)))
    write_csv(os.path.join(ev, "summary_partA.tsv"),
              ["arm", "repeats", "best_sherd", "best_joins", "reached_by", "all_joins",
               "delta_best_vs_t09", "note"], csv_rows(partA_summary(cells)))
    write_csv(os.path.join(ev, "sources.tsv"),
              ["kind", "path", "sha256", "bytes", "detail"], csv_rows(build_sources(run, cells)))
    walls_tbl = read_table(os.path.join(ev, "j01_walls.tsv"))
    if len(walls_tbl) > 1:
        write_csv(os.path.join(ev, "j01_walls.tsv"), walls_tbl[0], walls_tbl[1:])
    fx = build_fixtures(run, cells)
    b2rows, b2status, chosen = b2_gate(run, cells)
    write_csv(os.path.join(ev, "b2_gate.tsv"),
              ["arm", "qualifies", "route", "best_gt_deg", "best_donor_deg", "best_donor_mm",
               "rank", "selected", "b2_repeats", "b2_best_joins"], csv_rows(b2rows))
    renders = render_partA(run, cells)
    write_csv(os.path.join(ev, "renders.tsv"), ["figure", "path", "scale_bar_mm"], csv_rows(renders))
    jobs = [] if a.no_sacct else sacct_jobs(run)
    write_csv(os.path.join(ev, "jobs.tsv"), ["job_id", "stage", "arm", "rep", "state", "exit_code"], csv_rows(jobs))
    bad_fx = [r[0] for r in fx if r[1] != "PASS"]
    write_csv(os.path.join(ev, "fixtures.tsv"), ["fixture", "status", "detail"], csv_rows(fx))
    status = {
        "cells": len(cells), "usable": sum(1 for c in cells if c["usable"]),
        "missing_array_rows": len(miss), "fixtures_failed": bad_fx,
        "b2_status": b2status, "b2_chosen": chosen,
        "repeats_requested": PART_A_REPS,
    }
    with open(os.path.join(run, "logs", "report_status.json"), "w", encoding="utf-8") as fh:
        json.dump(status, fh, indent=2)
        fh.write("\n")
    print("REPORT cells=%d usable=%d missing=%d fixtures_failed=%s b2=%s chosen=%s" % (
        len(cells), status["usable"], len(miss), ",".join(bad_fx) or "-", b2status, ",".join(chosen) or "-"))
    for row in partA_summary(cells):
        print("  %-22s repeats=%s best_sherd=%-6s best_joins=%-3s reached=%s delta_vs_t09=%s" % (
            row[0], row[1], row[2], row[3], row[4], row[6]))
    if miss or len(renders) < 2:
        return 3
    return 0


if __name__ == "__main__":
    sys.exit(main())



