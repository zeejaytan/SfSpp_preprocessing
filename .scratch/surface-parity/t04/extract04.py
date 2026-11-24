"""Ticket 04 worker: six arms on Pot E 27 and 28, the evidence tables, the renders.

Natives are the arrays t03_lib.walls returns; shams hand copies of those arrays through
the same normals04 wrapper; the two transfers swap only the last three values of the
target walls for same-face donor normals within 1.000 mm.  The estimator is the frozen
shipped joint selector, called exactly as t03_extract called it (seeds 10, step 10,
candidate cap 6, tri_select=None).  Nothing here retunes it.
"""

import argparse
import json
import os
import sys
import time
import traceback

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
SHIP = "/data/gpfs/projects/punim2657/SfSpp/runs/20261121-1319_2e951d9_t03-ship"
T19 = "/data/gpfs/projects/punim2657/SfSpp/runs/20261124-0443_21446b8_t19-decisions"
IMPL = os.path.join(SHIP, "work", "impl_t03")
os.environ.setdefault("SFS_IMPL", IMPL)
for p in (HERE, os.path.join(SHIP, "work"), IMPL, os.path.join(IMPL, "scripts")):
    if p not in sys.path:
        sys.path.insert(0, p)

import t03_lib as dl                      # noqa: E402
import t03_extract as tx                  # noqa: E402
import normals04 as nm                    # noqa: E402

STEMS = [("Pot_E_Piece_27", 27), ("Pot_E_Piece_28", 28)]
ARMS = ["OWN", "AUTHOR", "OWN_SHAM", "AUTHOR_SHAM",
        "OWN_AUTHOR_NORMALS", "AUTHOR_OWN_NORMALS"]
ARCHIVE = {"OWN": "OWN", "AUTHOR": "AUTHOR", "OWN_SHAM": "OWN",
           "AUTHOR_SHAM": "AUTHOR", "OWN_AUTHOR_NORMALS": None,
           "AUTHOR_OWN_NORMALS": None}
NATIVE_OF = {"OWN_SHAM": "OWN", "OWN_AUTHOR_NORMALS": "OWN",
             "AUTHOR_SHAM": "AUTHOR", "AUTHOR_OWN_NORMALS": "AUTHOR"}
SEEDS = 10
STEP = 10
CAP = 6


def log(msg):
    print("[t04] %s" % msg, flush=True)


def write_tsv(path, rows, cols):
    with open(path, "w") as fh:
        fh.write("\t".join(cols) + "\n")
        for r in rows:
            fh.write("\t".join("" if r.get(c) is None else str(r.get(c)) for c in cols) + "\n")


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
    u = unit(u)
    v = unit(v)
    c = float(np.clip(u @ v, -1.0, 1.0))
    return float(np.degrees(np.arccos(c)))


def line_dist(p0, g0, gd):
    gd = unit(gd)
    d = np.asarray(p0, dtype=float) - np.asarray(g0, dtype=float)
    return float(np.linalg.norm(d - (d @ gd) * gd))


def source_paths(stem):
    pot = dl.pot_of(stem)
    own = [os.path.join(dl.OWN[pot], stem + ".S0"),
           os.path.join(dl.OWN[pot], stem + ".S1")]
    _, c0p, c1p, _, _ = dl.rb.get_piece_info(stem)
    return own, [c0p, c1p]


def is_finite_lines(out):
    if out is None:
        return False
    lines = np.asarray(out[0], dtype=float)
    return bool(np.all(np.isfinite(lines)))


def run_arm(stem, arm, walls):
    """Concat face 0 then face 1, draw the frozen pool, run the frozen selector."""
    w0, w1 = walls
    C = np.concatenate([w0, w1], axis=1)
    t0 = time.time()
    got = dl.draw_pool(C, seeds=SEEDS, step=STEP)
    if len(got) == 6:
        reps, sizes, V, st, nd = got[0], got[1], got[2], got[3], got[4]
    else:
        reps, sizes, V, st, nd = got
    out = tx.select_lines(reps, sizes, w0, w1, C, CAP, None)
    return dict(C=C, reps=reps, sizes=sizes, V=V, st=int(st), nd=int(nd),
                out=out, secs=round(time.time() - t0, 2))


def archive_gate(axis_file, archived):
    """(ok, rank_count_agree, max_abs, archived_sha) against the Ticket 19 pack."""
    if archived is None or not os.path.isfile(archived):
        return 0, 0, "", ""
    sha_a = nm.sha_file(archived)
    if nm.sha_file(axis_file) == sha_a:
        return 1, 1, 0.0, sha_a
    a = read_axis_rows(archived)
    b = read_axis_rows(axis_file)
    agree = 1 if len(a) == len(b) and len(a) > 0 else 0
    maxabs = 0.0
    if agree:
        for (pa, da), (pb, db) in zip(a, b):
            maxabs = max(maxabs, float(np.max(np.abs(pa - pb))),
                         float(np.max(np.abs(da - db))))
        ok = 1 if maxabs <= 1e-9 else 0
    else:
        ok = 0
    return ok, agree, maxabs, sha_a


def axis_rows(sid, stem, arm, lines, costs):
    gt = dl.gt_axis(stem)
    gd = unit(gt[0:3])
    gp = gt[3:6]
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
        row["cost"] = "" if costs is None else "%.17g" % float(np.ravel(costs)[k])
        rows.append(row)
    return rows


def line_segments(tag, lines_, colour, style, lw, centre, span):
    """Anchor each axis line at its closest pass to the sherd centre."""
    out = []
    for k in range(lines_.shape[1]):
        d = unit(lines_[0:3, k])
        p0 = lines_[3:6, k]
        w = centre - p0
        t = float(np.dot(w, d))
        off = float(np.linalg.norm(w - t * d))
        h = 0.16 * span
        out.append(("%s%d" % (tag, k + 1), colour, style, lw,
                    p0 + (t - h) * d, p0 + (t + h) * d, off))
    return out


def render_pair(stem, rows, path):
    """Two geometry rows: each native arm against the arm that swaps its normals.

    rows: two dicts with keys title, nat=(wall0, wall1), tr=(wall0, wall1),
    rec=(rec0, rec1), nat_lines, tr_lines.
    """
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    fig = plt.figure(figsize=(15.0, 15.0))
    for ri, R in enumerate(rows):
        own0, own1 = R["nat"]
        t0, t1 = R["tr"]
        r0, r1 = R["rec"]
        nat_lines, tr_lines = R["nat_lines"], R["tr_lines"]
        n0 = unit(np.mean(own0[3:6], axis=1))
        azim = float(np.degrees(np.arctan2(n0[1], n0[0])))
        elev = 24.0
        pts = np.concatenate([own0[0:3], own1[0:3]], axis=1)
        centre = pts.mean(axis=1)
        span0 = float(np.max(pts.max(axis=1) - pts.min(axis=1)))
        segs = []
        if nat_lines is not None:
            segs += line_segments("n", nat_lines, "#08306b", "-", 2.2, centre, span0)
        if tr_lines is not None:
            segs += line_segments("t", tr_lines, "#e377c2", "--", 1.8, centre, span0)
        allpts = [pts.T] + [s[4][None, :] for s in segs] + [s[5][None, :] for s in segs]
        A = np.concatenate(allpts, axis=0)
        lo = A.min(axis=0).astype(float)
        hi = A.max(axis=0).astype(float)
        span = float(np.max(hi - lo))
        pad = 0.05 * span
        L = 0.045 * span
        for panel in range(2):
            ax = fig.add_subplot(2, 2, 2 * ri + panel + 1, projection="3d")
            for fp, col in ((own0[0:3], "#b8b8b8"), (own1[0:3], "#707070")):
                st = max(1, int(fp.shape[1] // 4000))
                ax.scatter(fp[0, ::st], fp[1, ::st], fp[2, ::st], s=1.2, c=col,
                           alpha=0.5, depthshade=False, linewidths=0)
            for P, Tn, rec in ((own0, t0, r0), (own1, t1, r1)):
                n = P.shape[1]
                changed = np.nonzero(rec["changed"])[0]
                pool = changed if changed.size else np.arange(n)
                step = max(1, int(pool.size // 24))
                idx = pool[::step][:24]
                xyz = P[0:3, idx]
                bn = P[3:6, idx]
                an = np.asarray(Tn)[3:6, idx]
                ax.quiver(xyz[0], xyz[1], xyz[2], an[0], an[1], an[2],
                          length=1.35 * L, color="#f4a582", linewidth=0.8,
                          arrow_length_ratio=0.35, alpha=0.85)
                ax.quiver(xyz[0], xyz[1], xyz[2], bn[0], bn[1], bn[2], length=L,
                          color="#08306b", linewidth=1.1, arrow_length_ratio=0.4)
            for label, colour, style, lw, e0, e1, off in segs:
                ax.plot([e0[0], e1[0]], [e0[1], e1[1]], [e0[2], e1[2]],
                        style, color=colour, linewidth=lw, alpha=0.95)
                f_ = 0.14 if label.startswith("n") else 0.86
                d = unit(e1 - e0)
                q = np.cross(d, np.array([0.0, 0.0, 1.0]))
                if float(np.linalg.norm(q)) < 1e-6:
                    q = np.cross(d, np.array([1.0, 0.0, 0.0]))
                q = unit(q) * (0.035 * span)
                side = 1.0 if label.startswith("n") else -1.0
                at = e0 + f_ * (e1 - e0) + side * q
                ax.text(at[0], at[1], at[2], "%s %.0f mm" % (label, off),
                        fontsize=6.2, color=colour, fontweight="bold",
                        ha="left" if label.startswith("n") else "right")
            bx, by, bz = lo[0] + pad, lo[1] + pad, lo[2] + pad
            ax.plot([bx, bx + 20.0], [by, by], [bz, bz], color="k", linewidth=2.6)
            ax.text(bx + 10.0, by, bz, "20 mm", fontsize=8, ha="center", va="bottom")
            ax.set_xlim(lo[0] - pad, hi[0] + pad)
            ax.set_ylim(lo[1] - pad, hi[1] + pad)
            ax.set_zlim(lo[2] - pad, hi[2] + pad)
            try:
                ax.set_box_aspect((hi[0] - lo[0] + 2 * pad, hi[1] - lo[1] + 2 * pad,
                                   hi[2] - lo[2] + 2 * pad))
            except Exception:
                pass
            ax.view_init(elev=elev, azim=azim + 180.0 * panel)
            ax.set_xlabel("x mm", fontsize=7)
            ax.set_ylabel("y mm", fontsize=7)
            ax.set_zlabel("z mm", fontsize=7)
            ax.tick_params(labelsize=6)
            if ri == 0 and panel == 0:
                from matplotlib.lines import Line2D
                ax.legend(handles=[
                    Line2D([], [], color="#08306b", lw=1.1, label="native normal"),
                    Line2D([], [], color="#f4a582", lw=1.1, label="transferred normal"),
                    Line2D([], [], color="#08306b", lw=2.2,
                           label="native axis, at closest pass"),
                    Line2D([], [], color="#e377c2", lw=1.8, ls="--",
                           label="transferred axis, at closest pass")], fontsize=7, loc="upper left")
            ax.set_title("%s\n%s" % (R["title"],
                                      "view 1, face-0 side" if panel == 0
                                      else "view 2, face-1 side"),
                         fontsize=9)
    fig.suptitle("%s\n24 sampled normal arrows per face (native blue over transferred orange); "
                 "ranked axis lines drawn where each line passes closest to the sherd "
                 "(native solid, transferred dashed; label = rank and that offset in mm)\n"
                 "top row: OWN geometry with the authors' normals; bottom row: the authors' "
                 "geometry with OWN normals" % stem, fontsize=9.5, y=0.995)
    fig.subplots_adjust(left=0.01, right=0.99, top=0.925, bottom=0.01, wspace=0.01,
                        hspace=0.06)
    fig.savefig(path, dpi=150)
    plt.close(fig)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", required=True)
    ap.add_argument("--fixtures", action="store_true")
    ap.add_argument("--no-render", action="store_true")
    a = ap.parse_args()
    run = os.path.abspath(a.run)
    ev = os.path.join(run, "evidence")
    outd = os.path.join(run, "out", "axes04")
    rd = os.path.join(run, "renders")
    for d in (ev, outd, rd, os.path.join(ev, "matches")):
        os.makedirs(d, exist_ok=True)

    if a.fixtures:
        rows = [dict(name=n, status=s, detail=d) for n, s, d in nm.fixture_suite()]
        write_tsv(os.path.join(ev, "fixtures.tsv"), rows, ["name", "status", "detail"])
        bad = [r for r in rows if r["status"] != "PASS"]
        log("fixtures: %d/%d PASS" % (len(rows) - len(bad), len(rows)))
        return 0 if not bad else 1

    job_id = os.environ.get("SLURM_JOB_ID", "")
    inputs, runs, axes, changes, renders = [], [], [], [], []
    force = {}
    started = time.strftime("%Y-%m-%dT%H:%M:%S")

    for stem, sid in STEMS:
        own_paths, auth_paths = source_paths(stem)
        own0, own1, _ = dl.walls(stem, "own")
        au0, au1, _ = dl.walls(stem, "authors")
        src = {"own": [nm.sha_file(p) for p in own_paths],
               "authors": [nm.sha_file(p) for p in auth_paths]}
        guard_before = {p: nm.sha_file(p) for p in own_paths + auth_paths}
        log("%s walls: own %d/%d authors %d/%d" % (stem, own0.shape[1], own1.shape[1],
                                                   au0.shape[1], au1.shape[1]))
        arm_walls, arm_recs = {}, {}
        arm_walls["OWN"] = (own0, own1)
        arm_recs["OWN"] = [nm.zero_rec(own0), nm.zero_rec(own1)]
        arm_walls["AUTHOR"] = (au0, au1)
        arm_recs["AUTHOR"] = [nm.zero_rec(au0), nm.zero_rec(au1)]
        arm_walls["OWN_SHAM"], arm_recs["OWN_SHAM"] = nm.experimental_pair(own0, own1)
        arm_walls["AUTHOR_SHAM"], arm_recs["AUTHOR_SHAM"] = nm.experimental_pair(au0, au1)
        arm_walls["OWN_AUTHOR_NORMALS"], arm_recs["OWN_AUTHOR_NORMALS"] = \
            nm.experimental_pair(own0, own1, au0, au1)
        arm_walls["AUTHOR_OWN_NORMALS"], arm_recs["AUTHOR_OWN_NORMALS"] = \
            nm.experimental_pair(au0, au1, own0, own1)

        face_src = {"OWN": src["own"], "AUTHOR": src["authors"],
                    "OWN_SHAM": src["own"], "AUTHOR_SHAM": src["authors"],
                    "OWN_AUTHOR_NORMALS": src["own"],
                    "AUTHOR_OWN_NORMALS": src["authors"]}
        for arm in ARMS:
            w0, w1 = arm_walls[arm]
            recs = arm_recs[arm]
            for face, (w, rec) in enumerate(((w0, recs[0]), (w1, recs[1]))):
                n = int(w.shape[1])
                row = dict(sherd=sid, arm=arm, face=face, points=n,
                           xyz_sha256=nm.matrix_sha(w[0:3].T),
                           normals_sha256=nm.matrix_sha(w[3:6].T),
                           matched=int(rec["matched"].sum()),
                           changed=int(rec["changed"].sum()),
                           invalid_target=int(rec["invalid_target"].sum()),
                           unmatched=int(rec["unmatched"].sum()),
                           source_sha256=face_src[arm][face])
                inputs.append(row)
                if arm in ("OWN_AUTHOR_NORMALS", "AUTHOR_OWN_NORMALS"):
                    np.savez_compressed(
                        os.path.join(ev, "matches", "%s_%s_face%d.npz" % (stem, arm, face)),
                        xyz=w[0:3].T, native_normals=arm_walls[NATIVE_OF[arm]][face][3:6].T,
                        out_normals=w[3:6].T, matched=rec["matched"],
                        changed=rec["changed"], invalid_target=rec["invalid_target"],
                        unmatched=rec["unmatched"], donor=rec["donor"],
                        distance=rec["distance"], cut_mm=nm.CUT_MM)

            est = run_arm(stem, arm, (w0, w1))
            od = os.path.join(outd, stem)
            os.makedirs(od, exist_ok=True)
            path = os.path.join(od, "%s_Axis.xyz" % arm)
            k, status, reason, costs = 0, "no_axis", "", None
            rows = []
            if est["out"] is None or np.asarray(est["out"][0]).shape[1] == 0:
                reason = "selector returned no line"
                open(path, "w").close()
            elif not is_finite_lines(est["out"]):
                reason = "non-finite candidate row at selector output"
                open(path, "w").close()
            else:
                lines, costs = est["out"]
                tx.write_lines(path, lines)
                k = int(lines.shape[1])
                status = "ok"
                rows = axis_rows(sid, stem, arm, lines, costs)
            axes.extend(rows)
            arch = None
            if ARCHIVE[arm] is not None:
                arch = os.path.join(T19, "axes", ARCHIVE[arm], stem + "_Axis.xyz")
            ok, agree, maxabs, sha_a = archive_gate(path, arch)
            force[(stem, arm)] = dict(lines=est["out"][0] if est["out"] is not None else None,
                                      costs=costs, rows=rows, status=status, k=k,
                                      reason=reason, st=est["st"], nd=est["nd"],
                                      V=est["V"].shape[1], n=int(est["C"].shape[1]),
                                      basins=int(est["reps"].shape[1]))
            runs.append(dict(sherd=sid, arm=arm, status=status, k=k,
                             axes_sha256=nm.sha_file(path), archive_ok=ok if arch else "",
                             effective_stride=est["st"], drawn_points=est["nd"],
                             reason=reason, archived_sha256=sha_a,
                             archive_rank_count_agree=agree,
                             archive_max_abs=("%.17g" % maxabs) if arch else "",
                             n_points=int(est["C"].shape[1]),
                             basins=int(est["reps"].shape[1]),
                             candidate_draws=int(est["V"].shape[1]),
                             secs=est["secs"]))
            log("%s %-20s k=%d stride=%d drawn=%d basins=%d %.1fs"
                % (stem, arm, k, est["st"], est["nd"], est["reps"].shape[1], est["secs"]))

        # relative to the same geometry's native arm
        for arm in ("OWN_SHAM", "OWN_AUTHOR_NORMALS", "AUTHOR_SHAM",
                    "AUTHOR_OWN_NORMALS"):
            nat = NATIVE_OF[arm]
            A, B = force[(stem, arm)], force[(stem, nat)]
            la = np.asarray(A["lines"]) if A["lines"] is not None else np.zeros((6, 0))
            lb = np.asarray(B["lines"]) if B["lines"] is not None else np.zeros((6, 0))
            kk = min(la.shape[1], lb.shape[1])
            dl_deg, da_mm, within = 0.0, 0.0, 0
            ra = {r["rank"]: r for r in A["rows"]}
            rb = {r["rank"]: r for r in B["rows"]}
            for rk in range(1, kk + 1):
                ang = ang_deg(la[0:3, rk - 1], lb[0:3, rk - 1])
                dl_deg = max(dl_deg, ang)
                da_mm = max(da_mm, abs(float(ra[rk]["anchor_mm"]) - float(rb[rk]["anchor_mm"])))
                within += int(ang <= 10.0)
            changes.append(dict(
                sherd=sid, arm=arm, native_arm=nat, k_native=B["k"], k_arm=A["k"],
                k_same=kk, axes_bytes_identical=int(
                    A["rows"] is not None and
                    nm.sha_file(os.path.join(outd, stem, "%s_Axis.xyz" % arm)) ==
                    nm.sha_file(os.path.join(outd, stem, "%s_Axis.xyz" % nat))),
                max_rank_line_delta_deg="%.6f" % dl_deg,
                max_rank_anchor_delta_mm="%.6f" % da_mm,
                n_ranks_within_10deg=within,
                axes_sha256=nm.sha_file(os.path.join(outd, stem, "%s_Axis.xyz" % arm)),
                native_axes_sha256=nm.sha_file(os.path.join(outd, stem, "%s_Axis.xyz" % nat))))

        if not a.no_render:
            png = os.path.join(rd, "%s.png" % stem)
            render_pair(stem, [
                dict(title="OWN geometry, authors' normals",
                     nat=(own0, own1), tr=arm_walls["OWN_AUTHOR_NORMALS"],
                     rec=arm_recs["OWN_AUTHOR_NORMALS"],
                     nat_lines=force[(stem, "OWN")]["lines"],
                     tr_lines=force[(stem, "OWN_AUTHOR_NORMALS")]["lines"]),
                dict(title="authors' geometry, OWN normals",
                     nat=(au0, au1), tr=arm_walls["AUTHOR_OWN_NORMALS"],
                     rec=arm_recs["AUTHOR_OWN_NORMALS"],
                     nat_lines=force[(stem, "AUTHOR")]["lines"],
                     tr_lines=force[(stem, "AUTHOR_OWN_NORMALS")]["lines"])], png)
            renders.append(dict(sherd=sid, path="renders/%s.png" % stem,
                                scale_bar_mm=20))
            log("render %s" % png)
        after = {p: nm.sha_file(p) for p in own_paths + auth_paths}
        if after != guard_before:
            raise RuntimeError("source wall files changed while reading: %s" % stem)

    write_tsv(os.path.join(ev, "inputs.tsv"), inputs,
              ["sherd", "arm", "face", "points", "xyz_sha256", "normals_sha256",
               "matched", "changed", "invalid_target", "unmatched", "source_sha256"])
    write_tsv(os.path.join(ev, "runs.tsv"), runs,
              ["sherd", "arm", "status", "k", "axes_sha256", "archive_ok",
               "effective_stride", "drawn_points", "reason", "archived_sha256",
               "archive_rank_count_agree", "archive_max_abs", "n_points", "basins",
               "candidate_draws", "secs"])
    write_tsv(os.path.join(ev, "axes.tsv"), axes,
              ["sherd", "arm", "rank", "oriented_deg", "line_deg", "anchor_mm",
               "pos_x", "pos_y", "pos_z", "dir_x", "dir_y", "dir_z", "cost"])
    write_tsv(os.path.join(ev, "changes.tsv"), changes,
              ["sherd", "arm", "native_arm", "k_native", "k_arm", "k_same",
               "axes_bytes_identical", "max_rank_line_delta_deg",
               "max_rank_anchor_delta_mm", "n_ranks_within_10deg",
               "axes_sha256", "native_axes_sha256"])
    if renders:
        write_tsv(os.path.join(ev, "renders.tsv"), renders,
                  ["sherd", "path", "scale_bar_mm"])

    manifest = []

    def add(kind, path, detail=""):
        manifest.append(dict(kind=kind, path=path, sha256=nm.sha_file(path),
                             bytes=os.path.getsize(path), detail=detail))

    for stem, sid in STEMS:
        own_paths, auth_paths = source_paths(stem)
        for p in own_paths + auth_paths:
            add("input_wall", p, "sherd %d" % sid)
        add("reference", os.path.join(dl.GT_DIR, stem + "_Axis.xyz"), "sherd %d GT" % sid)
        for arm in ("OWN", "AUTHOR"):
            ap_ = os.path.join(T19, "axes", arm, stem + "_Axis.xyz")
            if os.path.isfile(ap_):
                add("archive_axis", ap_, "Ticket 19 %s sherd %d" % (arm, sid))
    for p in (os.path.join(SHIP, "work", "t03_lib.py"),
              os.path.join(SHIP, "work", "t03_extract.py"),
              os.path.join(IMPL, "scripts", "run_benchmark_172.py"),
              os.path.join(IMPL, "sfs_axes", "select.py"),
              os.path.join(IMPL, "sfs_axes", "joint.py"),
              os.path.join(IMPL, "sfs_axes", "meridian.py"),
              os.path.join(IMPL, "sfs_axes", "profile.py"),
              os.path.join(IMPL, "sfs_axes", "normalized.py"),
              os.path.join(IMPL, "sfs_axes", "potsac.py"),
              os.path.join(IMPL, "sfs_axes", "io_axes.py"),
              os.path.join(HERE, "normals04.py"),
              os.path.join(HERE, "extract04.py"),
              os.path.join(HERE, "check04.py")):
        if os.path.isfile(p):
            add("code", p)
    write_tsv(os.path.join(ev, "sources.tsv"), manifest,
              ["kind", "path", "sha256", "bytes", "detail"])

    meta = dict(run=run, job_id=job_id, started=started,
                finished=time.strftime("%Y-%m-%dT%H:%M:%S"),
                ship=SHIP, t19=T19, impl=IMPL, seeds=SEEDS, step=STEP, cap=CAP,
                cut_mm=nm.CUT_MM, arms=ARMS, stems=[s for s, _ in STEMS],
                python=sys.version.split()[0], numpy=np.__version__,
                git=os.environ.get("T04_GIT", ""))
    with open(os.path.join(run, "run.json"), "w") as fh:
        json.dump(meta, fh, indent=1)
    log("done: %d inputs rows, %d runs rows, %d axes rows"
        % (len(inputs), len(runs), len(axes)))
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception:
        traceback.print_exc()
        sys.exit(1)
