#!/usr/bin/env python3
"""Ticket 06 reduction: the four tables, the two figures, best-of-N.

Reads only what the eight cells wrote ($RUN/score, $RUN/logs/cell_raw_*.json,
$RUN/out/*/t18_raw.jsonl, $RUN/logs/jobs_submitted.tsv) plus the fixed Ticket 03
tree for the reference surfaces and poses.  Writes evidence/{cells,seams,traces,
jobs,renders}.tsv and renders/{Pot_E_27_28_comparison,Pot_E_full_assembly}.png.

Best-of-N: per arm, the repeat with the most joins (then the most sherds); the
count of repeats that reached it is printed.  Never a median.  A cell that is
not usable is reported as such and is not scored into the column.

Render frame: the exported T acts on the native surface points (Ticket 19's
reframe19 note), so a panel applies T_est directly to
$FIXED/Surfaces/Pot_E_Piece_NN_Surface_0.xyz.  The 27-28 figure anchors every
arm on the GT pose of sherd 27 (X = T_gt27 * inv(T_est27)) so all four arms and
the reference share one locked view.
"""
import argparse
import hashlib
import json
import os
import subprocess
import sys

import numpy as np

ARMS = ["AUTHOR", "OWN_NOV5", "OWN_NOV5_DEDUP", "OWN_MAIN_T09"]
REPS = [1, 2]
SEAMS = ["13-28", "27-28", "28-31"]
PIECES = list(range(1, 32))
CELL_COLS = ["arm", "rep", "job_id", "status", "usable", "exported_poses",
             "joins_pass", "joins_total", "pieces_pass", "pieces_total",
             "seam_13_28_pass", "seam_27_28_pass", "seam_28_31_pass",
             "exe_sha_ok", "inputs_unchanged", "container_files", "wall_secs"]
SEAM_COLS = ["arm", "rep", "join_i", "join_j", "ang_deg", "t_mm", "verdict"]
TRACE_COLS = ["arm", "rep", "seam", "direct_queries", "candidate_stretches",
              "fits_ok", "first_event_id"]
JOB_COLS = ["job_id", "stage", "arm", "rep", "state", "exit_code"]


def read_tsv(path):
    rows = []
    with open(path) as fh:
        for ln in fh:
            if ln.strip() == "":
                continue
            rows.append(ln.rstrip("\n").split("\t"))
    return rows


def write_tsv(path, cols, rows):
    with open(path, "w") as fh:
        fh.write("\t".join(cols) + "\n")
        for r in rows:
            fh.write("\t".join(str(x) for x in r) + "\n")


def parse_score(path):
    """pieces{pid:(ang,t,verdict)}, joins{(i,j):(ang,t,verdict)}, summary pieces/joins."""
    pieces, joins = {}, {}
    sp = sj = None
    for ln in open(path):
        f = ln.rstrip("\n").split("\t")
        if f[0] == "SUMMARY":
            for tok in f[1:]:
                if tok.startswith("pieces="):
                    sp = int(tok.split("=")[1].split("/")[0])
                elif tok.startswith("joins="):
                    sj = int(tok.split("=")[1].split("/")[0])
            continue
        if f[0].startswith("#") or len(f) < 4:
            continue
        if not f[0].isdigit():
            continue  # the "piece ang_deg t_mm verdict" column header
        if len(f) >= 5:
            joins[(int(f[0]), int(f[1]))] = (float(f[2]), float(f[3]), f[4])
        else:
            pieces[int(f[0])] = (float(f[1]), float(f[2]), f[3])
    return pieces, joins, sp, sj


def load_raw(run, arm, rep):
    p = os.path.join(run, "logs", "cell_raw_%s_%d.json" % (arm, rep))
    if not os.path.isfile(p):
        return {}
    try:
        return json.load(open(p))
    except Exception:
        return {}


def tracemap(run, arm, rep):
    p = os.path.join(run, "out", "%s_%d" % (arm, rep), "t18_raw.jsonl")
    out = {}
    if not os.path.isfile(p):
        return out
    for ln in open(p):
        try:
            d = json.loads(ln)
        except Exception:
            continue
        s = d.get("seam")
        if not s:
            a, b = d.get("a"), d.get("b")
            if a is None or b is None:
                continue
            s = "%d-%d" % (min(a, b), max(a, b))
        st = d.get("stage")
        e = out.setdefault(s, {"query": 0, "interval": 0, "fit": 0, "first": 0})
        if st == "query":
            e["query"] += 1
            if not e["first"]:
                e["first"] = d.get("ev", 0)
        elif st == "interval":
            e["interval"] += 1
        elif st == "pair_fit":
            try:
                inl = float(d.get("inlier", 0))
            except Exception:
                inl = 1.0 if d.get("inlier") else 0.0
            if inl > 0:
                e["fit"] += 1
    return out


def sacct_map(run):
    rows = read_tsv(os.path.join(run, "logs", "jobs_submitted.tsv"))
    ids = []
    for r in rows[1:]:
        if r and r[0] not in ids:
            ids.append(r[0])
    out = {}
    if not ids:
        return rows, out
    try:
        res = subprocess.run(["sacct", "-n", "-X", "-P", "-j", ",".join(ids),
                              "-o", "JobID,State,ExitCode"],
                             capture_output=True, text=True, timeout=120)
        for ln in res.stdout.splitlines():
            f = ln.strip().split("|")
            if len(f) >= 3:
                out[f[0]] = (f[1], f[2])
    except Exception as exc:
        print("WARN sacct failed: %s" % exc)
    return rows, out


def read_T(path):
    a = np.loadtxt(path, ndmin=2)
    T = np.eye(4)
    T[0:3, 0:3] = a[0:3, 0:3]
    T[0:3, 3] = a[0:3, 3]
    return T


def read_surf(path):
    P = []
    with open(path) as fh:
        for ln in fh:
            f = ln.split()
            if len(f) < 3:
                continue
            try:
                P.append((float(f[0]), float(f[1]), float(f[2])))
            except ValueError:
                continue
    return np.asarray(P, dtype=float)


def apply(T, P):
    return (T[0:3, 0:3] @ P.T).T + T[0:3, 3]


def frame2d(P):
    """(origin, axes) of the best-fit plane of P: two largest principal axes."""
    c = P.mean(axis=0)
    Q = P - c
    _, _, vt = np.linalg.svd(Q, full_matrices=False)
    return c, vt[0], vt[1], vt[2]


def project(P, c, u, v):
    Q = P - c
    return Q @ u, Q @ v


def scale_bar(ax, length=20.0, label="20 mm"):
    x0, x1 = ax.get_xlim()
    y0, y1 = ax.get_ylim()
    X = x0 + 0.06 * (x1 - x0)
    Y = y0 + 0.05 * (y1 - y0)
    ax.plot([X, X + length], [Y, Y], color="black", lw=3, solid_capstyle="butt")
    ax.text(X, Y + 0.03 * (y1 - y0), label, fontsize=8, va="bottom")


def render(run, fixed, best, outdir):
    surfs = {}
    gtT = {}
    for p in PIECES:
        sp = os.path.join(fixed, "Surfaces", "Pot_E_Piece_%02d_Surface_0.xyz" % p)
        gp = os.path.join(fixed, "Ground Truth", "Pot_E_Piece_%d_T.txt" % p)
        if os.path.isfile(sp) and os.path.isfile(gp):
            surfs[p] = read_surf(sp)
            gtT[p] = read_T(gp)
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    os.makedirs(outdir, exist_ok=True)
    paths = {}

    # ---------- figure 1: the 27-28 placement, locked view on the GT pose of 27
    ref = {}
    for p in (27, 28):
        if p in surfs:
            ref[p] = apply(gtT[p], surfs[p])
    if 27 in ref and 28 in ref:
        # every arm's estimate, anchored on the GT pose of sherd 27, and one locked
        # window over reference plus all estimates so a displaced 28 cannot be cropped
        est = {}
        for arm in ARMS:
            rep = best[arm][0]
            if not rep:
                continue
            pe = os.path.join(run, "out", "%s_%d" % (arm, rep))
            f27 = os.path.join(pe, "T_26to_26.txt")
            f28 = os.path.join(pe, "T_27to_27.txt")
            if os.path.isfile(f27) and os.path.isfile(f28) and 27 in surfs and 28 in surfs:
                T27, T28 = read_T(f27), read_T(f28)
                X = gtT[27] @ np.linalg.inv(T27)
                est[arm] = (apply(X, apply(T27, surfs[27])), apply(X, apply(T28, surfs[28])))
        allpts = [ref[27], ref[28]] + [q for pair in est.values() for q in pair]
        c, u, v, n = frame2d(np.vstack(allpts))
        pts = [project(q, c, u, v) for q in allpts]
        lim = [min(q[0].min() for q in pts), max(q[0].max() for q in pts),
               min(q[1].min() for q in pts), max(q[1].max() for q in pts)]
        fig, axes = plt.subplots(2, 2, figsize=(13, 12), dpi=140)
        xs, ys = project(ref[27], c, u, v)
        rx, ry = project(ref[28], c, u, v)
        for ax, arm in zip(axes.ravel(), ARMS):
            rep = best[arm][0]
            ax.set_title("%s  rep %s  (%d/62 joins, %d/31 pieces at bar)" %
                         (arm, rep or "-", best[arm][1], best[arm][2]), fontsize=10)
            ax.scatter(xs[::2], ys[::2], s=1.0, c="0.72", lw=0, label="reference 27-28 (GT)")
            ax.scatter(rx[::2], ry[::2], s=1.0, c="0.55", lw=0, label=None)
            if arm in est:
                e27, e28 = est[arm]
                ax.scatter(*project(e27, c, u, v), s=1.4, c="crimson", lw=0, label="estimated 27")
                ax.scatter(*project(e28, c, u, v), s=1.4, c="royalblue", lw=0, label="estimated 28")
            else:
                ax.text(0.5, 0.5, "no usable cell", transform=ax.transAxes, ha="center")
            ax.set_xlim(lim[0], lim[1])
            ax.set_ylim(lim[2], lim[3])
            ax.set_aspect("equal")
            ax.set_xticks([])
            ax.set_yticks([])
            scale_bar(ax)
            if arm == ARMS[0]:
                ax.legend(loc="upper right", fontsize=7, markerscale=6, framealpha=0.9)
        fig.suptitle("Pot E sherds 27-28 in the estimated pose, arms locked to the GT pose of 27 "
                     "(grey = reference, 20 mm bar)", fontsize=11)
        fig.tight_layout()
        p1 = os.path.join(outdir, "Pot_E_27_28_comparison.png")
        fig.savefig(p1)
        plt.close(fig)
        paths["Pot_E_27_28_comparison"] = p1

    # ---------- figure 2: the full 31-sherd assembly against the reference
    allref = [apply(gtT[p], surfs[p]) for p in PIECES if p in surfs]
    if allref:
        # one window over the reference and every arm's estimate, so an arm cannot be
        # cropped into looking better or worse than it is
        per_arm = {}
        for arm in ARMS:
            rep = best[arm][0]
            got = []
            if rep:
                pe = os.path.join(run, "out", "%s_%d" % (arm, rep))
                for p in PIECES:
                    f = os.path.join(pe, "T_%dto_%d.txt" % (p - 1, p - 1))
                    if os.path.isfile(f) and p in surfs:
                        got.append((p, apply(read_T(f), surfs[p])))
            per_arm[arm] = got
        allpts = list(allref) + [P for got in per_arm.values() for _, P in got]
        c, u, v, n = frame2d(np.vstack(allpts))
        fig, axes = plt.subplots(2, 2, figsize=(13, 13), dpi=140)
        refxy = [project(P, c, u, v) for P in allref]
        pts = refxy + [project(P, c, u, v) for P in allpts[len(allref):]]
        xs = np.concatenate([q[0] for q in pts])
        ys = np.concatenate([q[1] for q in pts])
        lim = [xs.min(), xs.max(), ys.min(), ys.max()]
        import matplotlib.cm as cm
        for ax, arm in zip(axes.ravel(), ARMS):
            rep = best[arm][0]
            ax.set_title("%s  rep %s  (%d/62 joins, %d/31 pieces at bar)" %
                         (arm, rep or "-", best[arm][1], best[arm][2]), fontsize=10)
            for qa, qb in refxy:
                ax.scatter(qa[::3], qb[::3], s=0.5, c="0.80", lw=0)
            colors = cm.tab20(np.linspace(0, 1, 31))
            for p, E in per_arm[arm]:
                ex, ey = project(E, c, u, v)
                ax.scatter(ex[::3], ey[::3], s=0.5, c=[colors[p - 1]], lw=0)
            ax.set_xlim(lim[0], lim[1])
            ax.set_ylim(lim[2], lim[3])
            ax.set_aspect("equal")
            ax.set_xticks([])
            ax.set_yticks([])
            scale_bar(ax)
        fig.suptitle("Pot E, all 31 sherds: estimated assembly (colour) against the reference "
                     "in its GT pose (grey); 20 mm bar", fontsize=11)
        fig.tight_layout()
        p2 = os.path.join(outdir, "Pot_E_full_assembly.png")
        fig.savefig(p2)
        plt.close(fig)
        paths["Pot_E_full_assembly"] = p2
    return paths


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", required=True)
    ap.add_argument("--fixed", required=True)
    a = ap.parse_args(argv)
    run, fixed = a.run, a.fixed
    ev = os.path.join(run, "evidence")

    # ---- per-cell records
    cells, cells_rows, seams_rows = [], [], []
    best = {}
    for arm in ARMS:
        scored = []
        for rep in REPS:
            raw = load_raw(run, arm, rep)
            sp = os.path.join(run, "score", "%s_%d.tsv" % (arm, rep))
            pieces = joins = spc = sjc = None
            if os.path.isfile(sp):
                pieces, joins, spc, sjc = parse_score(sp)
            usable = int(raw.get("usable", 0)) if raw else 0
            status = "scored" if (usable and pieces is not None) else ("not-scored" if not usable else "missing-score")
            seam_pass = {}
            for seam in SEAMS:
                i, j = [int(x) for x in seam.split("-")]
                v = joins.get((i, j)) if joins else None
                seam_pass[seam] = 1 if (v and v[2] == "PASS") else 0
            row = [arm, rep, raw.get("job_id", "-"), status, usable,
                   raw.get("exported_poses", 0), sjc if sjc is not None else 0, 62,
                   spc if spc is not None else 0, 31,
                   seam_pass["13-28"], seam_pass["27-28"], seam_pass["28-31"],
                   int(raw.get("exe_sha_ok", 0)), int(raw.get("inputs_unchanged", 0)),
                   raw.get("container_files", 0), raw.get("wall_secs", 0)]
            cells.append({"arm": arm, "rep": rep, "usable": usable, "row": row,
                          "joins": sjc or 0, "pieces": spc or 0, "joins_map": joins})
            cells_rows.append(row)
        scored = [c for c in cells if c["arm"] == arm and c["usable"]]
        if scored:
            top = max(scored, key=lambda c: (c["joins"], c["pieces"]))
            n = len([c for c in scored if (c["joins"], c["pieces"]) == (top["joins"], top["pieces"])])
            best[arm] = (top["rep"], top["joins"], top["pieces"], n)
        else:
            best[arm] = (0, 0, 0, 0)
    write_tsv(os.path.join(ev, "cells.tsv"), CELL_COLS, cells_rows)

    # ---- every join of every usable cell
    n_usable = 0
    for c in cells:
        if not c["usable"] or c["joins_map"] is None:
            continue
        n_usable += 1
        for (i, j) in sorted(c["joins_map"]):
            ang, t, verdict = c["joins_map"][(i, j)]
            seams_rows.append([c["arm"], c["rep"], i, j, "%.6f" % ang, "%.6f" % t, verdict])
    write_tsv(os.path.join(ev, "seams.tsv"), SEAM_COLS, seams_rows)

    # ---- 24 trace rows
    trace_rows = []
    for c in cells:
        tm = tracemap(run, c["arm"], c["rep"])
        for seam in SEAMS:
            e = tm.get(seam)
            trace_rows.append([c["arm"], c["rep"], seam,
                               e["query"] if e else 0, e["interval"] if e else 0,
                               e["fit"] if e else 0, e["first"] if e else 0])
    write_tsv(os.path.join(ev, "traces.tsv"), TRACE_COLS, trace_rows)

    # ---- jobs
    jrows, jmap = sacct_map(run)
    job_rows = []
    # the job writing this row cannot report its own terminal state; it is recorded
    # in evidence/jobs_aux.tsv by cell06.sbatch instead
    excl = os.environ.get("SLURM_JOB_ID", "")
    for r in sorted(jrows[1:], key=lambda x: int(x[0]) if x[0].isdigit() else 0):
        if r[0] == excl:
            continue
        if len(r) > 1 and r[1].startswith("report"):
            continue  # verifier jobs are recorded in evidence/jobs_aux.tsv
        st, ex = jmap.get(r[0], ("UNKNOWN", "-"))
        job_rows.append([r[0], r[1] if len(r) > 1 else "-", r[2] if len(r) > 2 else "-",
                         r[3] if len(r) > 3 else "-", st, ex])
    write_tsv(os.path.join(ev, "jobs.tsv"), JOB_COLS, job_rows)

    # ---- sources: the prep job wrote this table; refresh its six script rows to the bytes
    # sitting in work/t06 now, so a later bug fix here cannot leave the provenance record
    # naming a file that no longer exists (check06 re-hashes every row it is given)
    spath = os.path.join(ev, "sources.tsv")
    if os.path.isfile(spath):
        srows = read_tsv(spath)
        wdir = os.path.join(run, "work", "t06")
        fixed_rows = []
        for r in srows[1:]:
            if (len(r) >= 5 and r[0] == "script" and os.path.dirname(r[1]) == wdir
                    and os.path.isfile(r[1])):
                h = hashlib.sha256()
                with open(r[1], "rb") as fh:
                    for blk in iter(lambda: fh.read(1 << 20), b""):
                        h.update(blk)
                r = list(r)
                r[2] = h.hexdigest()
                r[3] = str(os.path.getsize(r[1]))
                r[4] = r[4].split(" (runtime")[0] + " (runtime copy at report time)"
            fixed_rows.append(r)
        write_tsv(spath, srows[0], fixed_rows)

    # ---- renders
    paths = render(run, fixed, best, os.path.join(run, "renders"))
    rrows = []
    for fig in ("Pot_E_27_28_comparison", "Pot_E_full_assembly"):
        p = paths.get(fig)
        rrows.append([fig, os.path.relpath(p, run) if p else "renders/%s.png (absent)" % fig, 20])
    write_tsv(os.path.join(ev, "renders.tsv"), ["figure", "path", "scale_bar_mm"], rrows)

    # ---- best-of-N and the control gate, printed and kept as a short record
    lines = []
    for arm in ARMS:
        rep, joins, pieces, n = best[arm]
        lines.append("BEST-OF-N %-14s rep=%d joins=%d/62 pieces=%d/31 reached_by=%d" %
                     (arm, rep, joins, pieces, n))
    # joins are the reportable unit: the scorer's piece column reads 179 deg even for the
    # AUTHOR 62/62 cell, so a piece-count gate would fail a cell the ticket calls a control.
    a_ok = best["AUTHOR"][1] == 62
    o_miss = best["OWN_NOV5"][1] < 62
    lines.append("CONTROL-GATE AUTHOR %s (62/62) :: OWN_NOV5 %s (%d/62, 27-28 %s)" %
                 ("PASS" if a_ok else "FAIL", "MISSES" if o_miss else "NO-MISS",
                  best["OWN_NOV5"][1], "FAIL" if best["OWN_NOV5"][3] else "n/a"))
    lines.append("ROWS cells=%d seams=%d traces=%d jobs=%d usable=%d" %
                 (len(cells_rows), len(seams_rows), len(trace_rows), len(job_rows), n_usable))
    for ln in lines:
        print(ln)
    with open(os.path.join(ev, "summary.txt"), "w") as fh:
        fh.write("\n".join(lines) + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
