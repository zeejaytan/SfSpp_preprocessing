#!/usr/bin/env python3
"""Ticket 01 reduction: evidence tables and locked join renders.

Fork of $T19/work/t19/render19.py (drawing conventions only). Every number here comes
from a file the cells wrote: score/<ARM>_<REP>.tsv, logs/panel.tsv, logs/cell_status.tsv,
logs/inputs_*.tsv, out/<ARM>_<REP>/container_inputs.tsv, out/<ARM>_<REP>/t18_raw.jsonl.

Frames: the export poses are the scorer's input, so a join figure is drawn by anchoring
piece A on its reference (GT) pose -- base = Tref[A] @ inv(TA) -- exactly as render19 did.
No registration, no resampling, no ICP.
"""
import argparse, csv, hashlib, json, os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ARMS = ["OWN", "AUTHOR", "OWN_E27_AUTHOR", "AUTHOR_E27_OWN"]
REPS = [1, 2]
SEAMS = [(13, 28), (27, 28), (28, 31)]
PRIMARY = "27-28"
SECONDARY_RENDER = [("AUTHOR", 1), ("OWN", 1)]


def read_T(p):
    return np.loadtxt(p)


def as_T(v):
    return np.asarray(v, dtype=float).reshape(4, 4)


def pose(T, P):
    """Apply a 4x4 pose to points given as (N,3) rows (a (3,N) array is transposed)."""
    Q = np.atleast_2d(np.asarray(P, dtype=float))
    if Q.shape[0] == 3 and Q.shape[1] != 3:
        Q = Q.T
    return Q[:, 0:3] @ T[0:3, 0:3].T + T[0:3, 3]


def load_xyz(p):
    return np.loadtxt(p, usecols=(0, 1, 2))


def read_tsv(path, header=True):
    """Return (header, rows). header=False means the file has no header line."""
    if not os.path.isfile(path):
        return [], []
    with open(path) as f:
        rows = [r for r in csv.reader(f, delimiter="\t") if r]
    if not rows:
        return [], []
    if not header:
        return [], rows
    return rows[0], rows[1:]


def write(path, rows, cols):
    with open(path, "w") as f:
        f.write("\t".join(cols) + "\n")
        for r in rows:
            out = []
            for c in cols:
                v = r.get(c, "")
                if isinstance(v, float):
                    out.append("%.6f" % v)
                elif v is None:
                    out.append("")
                else:
                    out.append(str(v))
            f.write("\t".join(out) + "\n")
    print("WROTE %s rows=%d" % (path, len(rows)))


def read_score(path):
    """Parse one pinned-scorer sheet: piece rows are 4 columns, join rows 5."""
    pieces, joins, summary = [], [], ""
    mode = ""
    if not os.path.isfile(path):
        return pieces, joins, summary
    for ln in open(path):
        ln = ln.rstrip("\n")
        if not ln or ln.startswith("#"):
            continue
        c = ln.split("\t")
        if c[0] == "piece":
            mode = "piece"
            continue
        if c[0] == "join_i":
            mode = "join"
            continue
        if c[0] == "SUMMARY":
            summary = ln
            continue
        if mode == "piece" and len(c) >= 4:
            pieces.append(dict(i=c[0], ang=c[1], t=c[2], verdict=c[3]))
        elif mode == "join" and len(c) >= 5:
            joins.append(dict(i=c[0], j=c[1], ang=c[2], t=c[3], verdict=c[4]))
    return pieces, joins, summary


def parse_summary(s):
    d = {}
    for tok in s.split("\t")[1:]:
        if "=" in tok:
            k, v = tok.split("=", 1)
            d[k] = v
    return d


def ang_deg(u, v):
    u = np.asarray(u, float); v = np.asarray(v, float)
    nu, nv = np.linalg.norm(u), np.linalg.norm(v)
    if nu == 0 or nv == 0:
        return float("nan")
    return float(np.degrees(np.arccos(max(-1.0, min(1.0, float(u @ v) / (nu * nv))))))


def line_dist(p0, g0, gd):
    gd = np.asarray(gd, float) / np.linalg.norm(gd)
    d = np.asarray(p0, float) - np.asarray(g0, float)
    return float(np.linalg.norm(d - (d @ gd) * gd))


def axis_rows(piece, path, source, gt_pos, gt_dir, ref_normal):
    rows = []
    if not os.path.isfile(path):
        return rows
    for k, ln in enumerate(open(path)):
        c = ln.split()
        if len(c) < 6:
            continue
        v = np.array([float(x) for x in c[:6]])
        pos, d = v[0:3], v[3:6]
        un = ang_deg(d, gt_dir)
        sd = float(np.sign(float((d / np.linalg.norm(d)) @ ref_normal)) or 1.0) * un
        du = d / np.linalg.norm(d)
        rows.append(dict(piece=piece, source=source, row=k + 1, signed_deg=sd,
                         unsigned_deg=un, distance_mm=line_dist(pos, gt_pos, gt_dir),
                         pos_x=pos[0], pos_y=pos[1], pos_z=pos[2],
                         dir_x=du[0], dir_y=du[1], dir_z=du[2]))
    return rows


def join_figure(cell, A, B, seam, ang, tmm, pas, TA, TB, TrefA, nat, REF, camc, half, ovc, ovh):
    fig, axs = plt.subplots(1, 3, figsize=(23.0, 7.4))
    allpts = np.vstack([REF[p] for p in sorted(REF)])
    out_note = ""
    # panel 1: the exported pair, anchored on piece A's reference pose
    ax = axs[0]
    ax.scatter(allpts[:, 0], allpts[:, 1], s=0.06, c="0.85", alpha=0.20, linewidths=0)
    if TA is None or TB is None:
        ax.text(0.5, 0.5, "no exported pose recorded for\npiece %s" % ("%d" % A if TA is None else "%d" % B),
                ha="center", va="center")
        ax.set_title("final export: missing pose")
    else:
        # T maps a piece's native cloud into the export frame, so the reference frame is
        # reached by Tref[A] @ inv(TA) applied to an already exported cloud. Piece A therefore
        # lands exactly on its reference pose, and only B's placement is contrasted.
        PA = pose(TrefA[A], nat[A])
        PB = pose(TrefA[A] @ np.linalg.inv(TA) @ TB, nat[B])
        ax.scatter(PA[:, 0], PA[:, 1], s=1.1, c="C3", linewidths=0, label="piece %d (export)" % A)
        ax.scatter(PB[:, 0], PB[:, 1], s=1.1, c="C0", linewidths=0, label="piece %d (export)" % B)
        lo = np.vstack([PA, PB]).min(axis=0)
        hi = np.vstack([PA, PB]).max(axis=0)
        if lo[0] < camc[0] - half or hi[0] > camc[0] + half or lo[1] < camc[1] - half or hi[1] > camc[1] + half:
            out_note = "off-frame"
            ax.text(0.02, 0.98, "piece reaches outside the locked window", transform=ax.transAxes,
                    va="top", fontsize=9, color="darkred")
        ax.set_title("final export (score row), anchored on piece %d" % A)
        ax.legend(loc="upper right", fontsize=7, markerscale=6)
    ax.set_xlim(camc[0] - half, camc[0] + half)
    ax.set_ylim(camc[1] - half, camc[1] + half)
    ax.set_aspect("equal"); ax.set_xlabel("x (mm)"); ax.set_ylabel("y (mm)")
    ax.plot([camc[0] - half + 6, camc[0] - half + 46], [camc[1] - half + 8, camc[1] - half + 8], "k-", lw=3)
    ax.text(camc[0] - half + 6, camc[1] - half + 3, "40 mm", fontsize=8)
    # panel 2: the fixed reference answer, same locked camera
    ax = axs[1]
    ax.scatter(allpts[:, 0], allpts[:, 1], s=0.06, c="0.85", alpha=0.20, linewidths=0)
    ax.scatter(REF[A][:, 0], REF[A][:, 1], s=1.1, c="C3", linewidths=0, label="piece %d reference" % A)
    ax.scatter(REF[B][:, 0], REF[B][:, 1], s=1.1, c="C0", linewidths=0, label="piece %d reference" % B)
    ax.set_xlim(camc[0] - half, camc[0] + half)
    ax.set_ylim(camc[1] - half, camc[1] + half)
    ax.set_aspect("equal"); ax.set_xlabel("x (mm)"); ax.set_ylabel("y (mm)")
    ax.set_title("fixed reference answer (GT poses), same camera")
    ax.legend(loc="upper right", fontsize=7, markerscale=6)
    ax.plot([camc[0] - half + 6, camc[0] - half + 46], [camc[1] - half + 8, camc[1] - half + 8], "k-", lw=3)
    ax.text(camc[0] - half + 6, camc[1] - half + 3, "40 mm", fontsize=8)
    # panel 3: whole pot, plan view, export pair in place
    ax = axs[2]
    ax.scatter(allpts[:, 0], allpts[:, 1], s=0.05, c="0.85", alpha=0.20, linewidths=0)
    if TA is not None and TB is not None:
        PA = pose(TrefA[A], nat[A])
        PB = pose(TrefA[A] @ np.linalg.inv(TA) @ TB, nat[B])
        ax.scatter(PA[:, 0], PA[:, 1], s=0.9, c="C3", linewidths=0)
        ax.scatter(PB[:, 0], PB[:, 1], s=0.9, c="C0", linewidths=0)
    ax.set_xlim(ovc[0] - ovh, ovc[0] + ovh)
    ax.set_ylim(ovc[1] - ovh, ovc[1] + ovh)
    ax.set_aspect("equal"); ax.set_xlabel("x (mm)"); ax.set_ylabel("y (mm)")
    ax.set_title("plan overview, whole pot (final export)")
    fig.suptitle("%s seam %s  angle %s deg  t %s mm  %s"
                 % (cell, seam, ang if ang != "" else "-", tmm if tmm != "" else "-",
                    "pass" if str(pas) == "1" else "fail"), fontsize=11)
    fig.text(0.005, 0.945, "red = piece %d, blue = piece %d, grey = fixed reference answer; "
             "locked camera and 40 mm bar; eyeball check of the numbered comparison, not a measurement"
             % (A, B), fontsize=9, color="darkred")
    cam = ("reference frame (GT poses); centre (%.1f,%.1f,%.1f) half %.1f mm; bar 40 mm; "
           "overview centre (%.1f,%.1f) half %.1f mm%s"
           % (camc[0], camc[1], camc[2], half, ovc[0], ovc[1], ovh,
              ("; " + out_note) if out_note else ""))
    return fig, cam


def main():
    ap = argparse.ArgumentParser()
    for k in ("run", "fixed", "orig", "t19", "evidence", "renders", "gt"):
        ap.add_argument("--" + k, required=True)
    a = ap.parse_args()
    os.makedirs(a.evidence, exist_ok=True)
    os.makedirs(a.renders, exist_ok=True)
    ev = lambda n: os.path.join(a.evidence, n)

    # ---------- score sheets
    sc_rows, seam_rows, cell_summary = [], [], {}
    for arm in ARMS:
        for rep in REPS:
            cell = "%s_%d" % (arm, rep)
            pieces, joins, summary = read_score(os.path.join(a.run, "score", cell + ".tsv"))
            sm = parse_summary(summary) if summary else {}
            cell_summary[cell] = sm
            for pc in pieces:
                sc_rows.append(dict(arm=arm, repeat=rep, kind="piece", i=pc["i"], j="",
                                    ang_deg=pc["ang"], t_mm=pc["t"], verdict=pc["verdict"],
                                    primary=1 if pc["i"] == "27" else 0))
            for jn in joins:
                s = "%s-%s" % (jn["i"], jn["j"])
                prim = 1 if s == PRIMARY else (2 if s in ("13-28", "28-31") else 0)
                ok = 1 if str(jn["verdict"]).upper().startswith("PASS") else 0
                sc_rows.append(dict(arm=arm, repeat=rep, kind="join", i=jn["i"], j=jn["j"],
                                    ang_deg=jn["ang"], t_mm=jn["t"], verdict=jn["verdict"],
                                    primary=prim))
                seam_rows.append({"arm": arm, "repeat": rep, "seam": s,
                                  "angle_deg": jn["ang"], "translation_mm": jn["t"],
                                  "pass": ok, "primary": prim})
    write(ev("scores.tsv"), sc_rows, ["arm", "repeat", "kind", "i", "j", "ang_deg", "t_mm",
                                      "verdict", "primary"])
    write(ev("seams.tsv"), seam_rows, ["arm", "repeat", "seam", "angle_deg", "translation_mm",
                                       "pass", "primary"])

    # ---------- replay rows from the cell panel and status logs
    PANEL = ["arm", "rep", "want_sha", "pre", "post", "ok", "rc", "dt", "job_id"]
    ph, prow = read_tsv(os.path.join(a.run, "logs", "panel.tsv"), header=False)
    ph = PANEL
    sh, srow = read_tsv(os.path.join(a.run, "logs", "cell_status.tsv"), header=False)
    status = {}
    for r in srow:
        if len(r) >= 4:
            status[(r[0], r[1])] = (r[3], r[4])
    replay = []
    for r in prow:
        d = dict(zip(ph, r))
        cell = "%s_%s" % (d["arm"], d["rep"])
        sm = cell_summary.get(cell, {})
        replay.append(dict(arm=d["arm"], repeat=d["rep"], executable_sha256=d["want_sha"],
                           pre_sha256=d["pre"], post_sha256=d["post"], container_ok=d["ok"],
                           job_id=d["job_id"], status=(status.get((d["arm"], d["rep"]), ("", ""))[0] or "unscored"),
                           joins=sm.get("joins", ""), sherds=sm.get("pieces", "")))
    write(ev("replay.tsv"), replay, ["arm", "repeat", "executable_sha256", "pre_sha256",
                                     "post_sha256", "container_ok", "job_id", "status", "joins", "sherds"])

    # ---------- matching events from the raw trace
    mrows, frows = [], []
    for arm in ARMS:
        for rep in REPS:
            cell = "%s_%d" % (arm, rep)
            fp = os.path.join(a.run, "out", cell, "t18_raw.jsonl")
            cnt = {"%d-%d" % s: dict(q=0, iv=0, ft=0, fq="", fiv="", fft="", loss=None)
                   for s in SEAMS}
            if os.path.isfile(fp):
                for ln in open(fp):
                    try:
                        e = json.loads(ln)
                    except Exception:
                        continue
                    s = e.get("seam")
                    if s not in cnt:
                        continue
                    k = cnt[s]
                    st, dp = e.get("stage"), e.get("disp", "")
                    if st == "query" and dp == "attempt":
                        k["q"] += 1
                        if k["fq"] == "":
                            k["fq"] = e.get("ev")
                    elif st == "interval" and dp == "emitted":
                        k["iv"] += 1
                        if k["fiv"] == "":
                            k["fiv"] = e.get("ev")
                    elif st == "pair_fit" and (dp == "fit" or dp == ""):
                        k["ft"] += 1
                        if k["fft"] == "":
                            k["fft"] = e.get("ev")
                    if k["loss"] is None and dp in ("rejected", "empty"):
                        k["loss"] = e
            for (A, B) in SEAMS:
                s = "%d-%d" % (A, B)
                k = cnt["%d-%d" % (A, B)]
                mrows.append(dict(arm=arm, repeat=rep, seam=s, query_count=k["q"],
                                  interval_count=k["iv"], fit_count=k["ft"],
                                  first_query_event=k["fq"], first_interval_event=k["fiv"],
                                  first_fit_event=k["fft"]))
                lo = k["loss"] or {}
                frows.append(dict(arm=arm, repeat=rep, seam=s, stage=lo.get("stage", ""),
                                  event=lo.get("ev", ""), status=lo.get("state", ""),
                                  reason=lo.get("reason", "")))
    write(ev("matching.tsv"), mrows, ["arm", "repeat", "seam", "query_count", "interval_count",
                                      "fit_count", "first_query_event", "first_interval_event",
                                      "first_fit_event"])
    # first_loss.tsv withdrawn: it recorded the first rejected exploratory branch of a seam,
    # which for a passing seam reads "no_interval" and invites the opposite conclusion to
    # matching.tsv. The required record is matching.tsv plus the raw trace on Spartan.

    # ---------- inputs actually bound at the container path
    inrows = []
    for arm in ARMS:
        for rep in REPS:
            cell = "%s_%d" % (arm, rep)
            ch, crow = read_tsv(os.path.join(a.run, "out", cell, "container_inputs.tsv"),
                                header=False)
            bh, brow = read_tsv(os.path.join(a.run, "logs", "inputs_before_%s.tsv" % cell))
            ah, arow = read_tsv(os.path.join(a.run, "logs", "inputs_after_%s.tsv" % cell))
            if not crow:
                continue
            def index(h, rows, label_col, sha_col):
                out = {}
                for r in rows:
                    if len(r) > max(label_col, sha_col):
                        out[r[label_col]] = r[sha_col]
                return out
            b = index(bh, brow, 1, 2)
            af = index(ah, arow, 1, 2)
            m = {}
            for k, v in b.items():
                if k.startswith("axes/"):
                    m["/Dataset/SfS_pp/Axes/" + os.path.basename(k)] = v
                elif "/" in k:
                    m["/Dataset/SfS_pp/" + k] = v
            ma = {}
            for k, v in af.items():
                if k.startswith("axes/"):
                    ma["/Dataset/SfS_pp/Axes/" + os.path.basename(k)] = v
                elif "/" in k:
                    ma["/Dataset/SfS_pp/" + k] = v
            for r in crow:
                if len(r) < 2:
                    continue
                inrows.append(dict(arm=arm, repeat=rep, path=r[0], before_sha256=m.get(r[0], ""),
                                   after_sha256=ma.get(r[0], ""), container_sha256=r[1]))
    write(ev("inputs.tsv"), inrows, ["arm", "repeat", "path", "before_sha256", "after_sha256",
                                     "container_sha256"])

    # ---------- shadow listing vs the bound axis directory (the archived trap)
    def inputs_map(cell):
        h, rows = read_tsv(os.path.join(a.run, "logs", "inputs_before_%s.tsv" % cell))
        d = {}
        for r in rows:
            if len(r) > 2:
                d[r[1]] = r[2]
        return d

    shrows = []
    BOUND, SHADOW, CONT = {}, {}, {}
    for arm in ARMS:
        for rep in REPS:
            cell = "%s_%d" % (arm, rep)
            bmap = inputs_map(cell)
            bound = {os.path.basename(k): v for k, v in bmap.items() if k.startswith("axes/")}
            shadow = {os.path.basename(k): v for k, v in bmap.items() if k.startswith("Axes/")}
            ch, crow = read_tsv(os.path.join(a.run, "out", cell, "container_inputs.tsv"),
                                header=False)
            cont = {r[0]: r[1] for r in crow if len(r) > 1}
            BOUND[(arm, rep)] = bound
            SHADOW[(arm, rep)] = shadow
            CONT[(arm, rep)] = cont
            for name in sorted(bound):
                cp = "/Dataset/SfS_pp/Axes/" + name
                shrows.append(dict(arm=arm, repeat=rep, container_path=cp,
                                   shadow_sha256=shadow.get(name, ""),
                                   bound_sha256=bound[name],
                                   container_sha256=cont.get(cp, ""),
                                   overrides_shadow=1 if (shadow.get(name)
                                                          and shadow[name] != bound[name]) else 0))
    write(ev("provenance_axes_shadow.tsv"), shrows,
          ["arm", "repeat", "container_path", "shadow_sha256", "bound_sha256",
           "container_sha256", "overrides_shadow"])

    # ---------- the reciprocal contrast: which input differs from the background
    recrows = []
    for arm, bg in (("OWN_E27_AUTHOR", "OWN"), ("AUTHOR_E27_OWN", "AUTHOR")):
        for rep in REPS:
            c1, c2 = "%s_%d" % (arm, rep), "%s_%d" % (bg, rep)
            f1, f2 = inputs_map(c1), inputs_map(c2)
            ax1 = {os.path.basename(k): v for k, v in f1.items() if k.startswith("axes/")}
            ax2 = {os.path.basename(k): v for k, v in f2.items() if k.startswith("axes/")}
            diff = sorted(n for n in ax1 if ax1[n] != ax2.get(n))
            keep = lambda m: {k: v for k, v in m.items()
                              if not k.startswith("axes/") and not k.startswith("Axes/")}
            recrows.append(dict(arm=arm, repeat=rep, background=bg,
                                differing_paths=";".join(diff), diff_count=len(diff),
                                other_inputs_identical=1 if keep(f1) == keep(f2) else 0))
    write(ev("reciprocal_inputs.tsv"), recrows,
          ["arm", "repeat", "background", "differing_paths", "diff_count",
           "other_inputs_identical"])

    # ---------- raw traces stay on Spartan: record path, bytes, lines, hash
    trrows = []
    for arm in ARMS:
        for rep in REPS:
            cell = "%s_%d" % (arm, rep)
            for nm in ("t18_raw.jsonl", "t19_decisions.jsonl"):
                p = os.path.join(a.run, "out", cell, nm)
                if not os.path.isfile(p):
                    continue
                h = hashlib.sha256()
                n = 0
                with open(p, "rb") as fh:
                    for blk in iter(lambda: fh.read(1 << 20), b""):
                        h.update(blk)
                        n += len(blk)
                with open(p, "rb") as fh:
                    lines = sum(1 for _ in fh)
                trrows.append(dict(arm=arm, repeat=rep, file=nm,
                                   path="out/%s/%s" % (cell, nm), sha256=h.hexdigest(),
                                   bytes=n, lines=lines))
    write(ev("traces.tsv"), trrows, ["arm", "repeat", "file", "path", "sha256", "bytes", "lines"])

    # ---------- archived Ticket 19 benchmark record (released and both controls)
    t19rows = []
    for arm in ("ORIG", "OWN", "AUTHOR", "REVERSE"):
        for rep in (1, 2):
            p = os.path.join(a.t19, "score", "%s_%d.tsv" % (arm, rep))
            if not os.path.isfile(p):
                continue
            pieces, joins, summary = read_score(p)
            sm = parse_summary(summary) if summary else {}
            row = dict(arm=arm, repeat=rep, pieces=sm.get("pieces", ""), joins=sm.get("joins", ""))
            for jn in joins:
                if "%s-%s" % (jn["i"], jn["j"]) == PRIMARY:
                    row.update(seam=PRIMARY, angle_deg=jn["ang"], translation_mm=jn["t"],
                               verdict=jn["verdict"])
            t19rows.append(row)
    write(ev("t19_benchmark.tsv"), t19rows,
          ["arm", "repeat", "pieces", "joins", "seam", "angle_deg", "translation_mm", "verdict"])

    # ---------- one line per cell: outcome, primary seam, matching counts
    srows = []
    for arm in ARMS:
        for rep in REPS:
            cell = "%s_%d" % (arm, rep)
            sm = cell_summary.get(cell, {})
            srow = next((r for r in seam_rows if r["arm"] == arm and r["repeat"] == rep
                         and r["seam"] == PRIMARY), {})
            mrow = next((r for r in mrows if r["arm"] == arm and r["repeat"] == rep
                         and r["seam"] == PRIMARY), {})
            srows.append(dict(arm=arm, repeat=rep, joins=sm.get("joins", ""),
                              sherds=sm.get("pieces", ""),
                              seam=PRIMARY, angle_deg=srow.get("angle_deg", ""),
                              translation_mm=srow.get("translation_mm", ""),
                              verdict_pass=srow.get("pass", ""),
                              query_count=mrow.get("query_count", ""),
                              interval_count=mrow.get("interval_count", ""),
                              fit_count=mrow.get("fit_count", "")))
    write(ev("summary.tsv"), srows, ["arm", "repeat", "joins", "sherds", "seam", "angle_deg",
                                     "translation_mm", "verdict_pass", "query_count",
                                     "interval_count", "fit_count"])

    # ---------- axis candidates against the released ground-truth axis
    axrows = []
    gta = {}
    for pc in (27, 28):
        f = os.path.join(a.orig, "Ground Truth Axes", "Pot_E_Piece_%d_Axis.xyz" % pc)
        v = np.array([float(x) for x in open(f).read().split()[:6]])
        gta[pc] = (v[0:3], v[3:6])
        nrm = np.loadtxt(os.path.join(a.orig, "Surfaces", "Pot_E_Piece_%d_Surface_0.xyz" % pc))
        axrows.extend(axis_rows(pc, f, "released-GT-axis", v[0:3], v[3:6],
                                np.mean(nrm[:, 3:6], axis=0)))
    for pc in (27, 28):
        cand = [("OWN", os.path.join(a.t19, "axes", "OWN", "Pot_E_Piece_%d_Axis.xyz" % pc)),
                ("AUTHOR", os.path.join(a.t19, "axes", "AUTHOR", "Pot_E_Piece_%d_Axis.xyz" % pc)),
                ("released", os.path.join(a.orig, "Axes", "Pot_E_Piece_%d_Axis.xyz" % pc))]
        nrm = np.loadtxt(os.path.join(a.orig, "Surfaces", "Pot_E_Piece_%d_Surface_0.xyz" % pc))
        for src, path in cand:
            axrows.extend(axis_rows(pc, path, src, gta[pc][0], gta[pc][1],
                                    np.mean(nrm[:, 3:6], axis=0)))
    write(ev("axes.tsv"), axrows, ["piece", "source", "row", "signed_deg", "unsigned_deg",
                                   "distance_mm", "pos_x", "pos_y", "pos_z",
                                   "dir_x", "dir_y", "dir_z"])

    # ---------- jobs: sacct plus the wave log
    jrows = []
    wh, wrow = read_tsv(os.path.join(a.run, "logs", "waves.tsv"))
    role = {}
    for r in wrow:
        d = dict(zip(wh, r))
        if d.get("job_id"):
            role[d["job_id"]] = "%s_%s" % (d.get("arm", ""), d.get("repeat", ""))
    runid = os.path.basename(a.run.rstrip("/"))
    sac = os.path.join(a.run, "logs", "sacct_final.tsv")
    have = set()
    if os.path.isfile(sac):
        for ln in open(sac):
            c = ln.rstrip("\n").split("|")
            if len(c) < 4 or not c[0]:
                continue
            jid = c[0].split(".")[0]
            if jid in have:
                continue
            have.add(jid)
            jrows.append(dict(job_id=jid, run_id=runid, state=c[2], exit_code=c[3],
                              elapsed=c[4] if len(c) > 4 else "",
                              role=role.get(jid, ""), polled=1))
    write(ev("jobs.tsv"), jrows, ["job_id", "run_id", "state", "exit_code", "elapsed", "role",
                                  "polled"])
    # ---------- locked join renders, one per repeat of the primary seam
    Tref = {q: read_T(os.path.join(a.gt, "Pot_E_Piece_%d_T.txt" % q)) for q in range(1, 32)}
    nat = {q: load_xyz(os.path.join(a.fixed, "Surfaces", "Pot_E_Piece_%02d_Surface_0.xyz" % q))
           for q in range(1, 32)}
    REF = {q: pose(Tref[q], nat[q]) for q in nat}
    allp = np.vstack([REF[q] for q in sorted(REF)])
    ovc = allp.mean(axis=0)
    ovh = max(90.0, 0.5 * float(np.max(allp.max(axis=0) - allp.min(axis=0))) + 10.0)

    def T_of(cell, piece):
        fp = os.path.join(a.run, "out", cell, "T_%dto_%d.txt" % (piece - 1, piece - 1))
        if not os.path.isfile(fp):
            return None
        try:
            return read_T(fp)
        except Exception:
            return None

    rrows = []
    for arm in ARMS:
        for rep in REPS:
            cell = "%s_%d" % (arm, rep)
            todo = [PRIMARY] + (["13-28", "28-31"] if (arm, rep) in SECONDARY_RENDER else [])
            for s in todo:
                A, B = [int(x) for x in s.split("-")]
                pr = np.vstack([REF[A], REF[B]])
                camc = pr.mean(axis=0)
                half = max(70.0, 0.5 * float(np.max(pr.max(axis=0) - pr.min(axis=0))) + 20.0)
                row = next((r for r in seam_rows if r["arm"] == arm and r["repeat"] == rep
                            and r["seam"] == s), None)
                ang = row["angle_deg"] if row else ""
                tmm = row["translation_mm"] if row else ""
                pas = str(row["pass"]) if row else "0"
                TA, TB = T_of(cell, A), T_of(cell, B)
                fig, cam = join_figure(cell, A, B, s, ang, tmm, pas, TA, TB, Tref, nat, REF,
                                       camc, half, ovc, ovh)
                name = "%s_%s.png" % (cell, s)
                fig.tight_layout(rect=[0, 0, 1, 0.94])
                fig.savefig(os.path.join(a.renders, name), dpi=100)
                plt.close(fig)
                note = ("" if (TA is not None and TB is not None) else "missing exported pose")
                rrows.append(dict(kind="join", arm=arm, repeat=rep, piece="%d/%d" % (A, B),
                                  path="renders/" + name, camera=cam, scale_bar_mm=40,
                                  labels="red=piece %d blue=piece %d grey=fixed reference" % (A, B),
                                  note=note))
    sp = ev("renders_surface.tsv")
    shr, srows = read_tsv(sp)
    for r in srows:
        d = dict(zip(shr, r))
        rrows.append(dict(kind=d.get("kind", ""), arm=d.get("arm", ""), repeat=d.get("repeat", ""),
                          piece=d.get("piece", ""), path=d.get("path", ""),
                          camera=d.get("camera", ""), scale_bar_mm=d.get("scale_bar_mm", ""),
                          labels=d.get("labels", ""), note=d.get("note", "")))
    write(ev("renders.tsv"), rrows, ["kind", "arm", "repeat", "piece", "path", "camera",
                                     "scale_bar_mm", "labels", "note"])
    print("RENDER-OK join=%d surface=%d" % (len(rrows) - len(srows), len(srows)))


if __name__ == "__main__":
    main()
