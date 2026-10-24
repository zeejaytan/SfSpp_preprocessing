#!/usr/bin/env python3
"""Ticket 289 - Pot J 09, picture first, numbers second.

Reads the copies submit.sbatch / draw2.sbatch wrote into $RUN/out (draw 1) - read-only here:
  Pot_J_Piece_09_Surface_{0,1}.xyz        the two faces the mesh stage kept (0 interior, 1 exterior)
  Pot_J_Piece_09_Breakline_{0,1}.pcd      our two exported lanes
  boundary.pcd / boundaryImproved.pcd / cloud_Filtered.pcd / cloudBreaklinePointsOnBSplineSurface.pcd
                                          pipeline stages, shared paths: LAST WRITER WINS
The per-face bags (boundary_S0/S1.pcd) exist only in the POTA-218 arm build, a compile-time
switch the shipped binary does not carry, so the shared files carry the last surface's lane -
lane 1's, verified by size (309 pre-walk dots, 84 post-walk dots, and lane 1's export is 84 dots).
Lane 0's bag is reported absent, never inferred.

Score rows come from the project's own scorer score275.lane(), so every column means what it
means in tickets 259 / 287 / 288. Nothing here changes code, defaults or thresholds.
"""
import os, sys, json, importlib.util
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D  # noqa: F401

RD = os.path.abspath(sys.argv[1])
OUT = os.path.join(RD, "out")
PNG = os.path.join(OUT, "png")
os.makedirs(PNG, exist_ok=True)
PIECE = "Pot_J_Piece_09"
LOG = []


def log(s):
    print(s, flush=True)
    LOG.append(str(s))


def read_pcd(p):
    with open(p, "r", errors="replace") as f:
        txt = f.read().splitlines()
    k = None
    for i, l in enumerate(txt):
        if l.strip().upper().startswith("DATA"):
            k = i + 1
            break
    if k is None:
        raise SystemExit("no DATA header in " + p)
    rows = []
    for l in txt[k:]:
        s = l.split()
        if len(s) >= 3:
            try:
                rows.append((float(s[0]), float(s[1]), float(s[2])))
            except ValueError:
                pass
    return np.array(rows, dtype=float).reshape(-1, 3)


def read_xyz(p):
    rows = []
    with open(p, "r", errors="replace") as f:
        for l in f:
            s = l.split()
            if len(s) < 3:
                continue
            try:
                rows.append((float(s[0]), float(s[1]), float(s[2])))
            except ValueError:
                continue
    return np.array(rows, dtype=float).reshape(-1, 3)


def nn_d(a, b, chunk=192):
    d = np.empty(len(a))
    for s in range(0, len(a), chunk):
        e = min(len(a), s + chunk)
        seg = a[s:e]
        dd = ((seg[:, None, :] - b[None, :, :]) ** 2).sum(-1)
        d[s:e] = np.sqrt(dd.min(1))
    return d


def plen(P):
    "closed-loop length of an ORDERED ring: consecutive steps plus the closing segment"
    if len(P) < 2:
        return 0.0
    st = np.sqrt(((P[1:] - P[:-1]) ** 2).sum(1))
    return float(st.sum() + np.linalg.norm(P[0] - P[-1]))


def stage_stats(P, A, thr=2.0, ring=False):
    "how far P is from the authors ring A, both directions, plus a length only for a ring"
    d = nn_d(P, A)
    da = nn_d(A, P)
    return dict(n=int(len(P)),
                med=float(np.median(d)), mx=float(d.max()),
                pct_dots=float(100.0 * (d > thr).mean()),
                covers_auth=float(100.0 * (da < thr).mean()),
                len=plen(P) if ring else None)


def face_stats(P, S0, S1):
    d0 = nn_d(P, S0)
    d1 = nn_d(P, S1)
    both = np.minimum(d0, d1)
    face = 0 if float(np.median(d0)) <= float(np.median(d1)) else 1
    return dict(medS0=float(np.median(d0)), medS1=float(np.median(d1)),
                pctS0=float(100.0 * (d0 < 1.0).mean()), pctS1=float(100.0 * (d1 < 1.0).mean()),
                med_surf=float(np.median(both)), mx_surf=float(both.max()),
                pct_off_surf=float(100.0 * (both > 1.0).mean()), face=face)


def runs_of(mask):
    out, i, n = [], 0, len(mask)
    while i < n:
        if mask[i]:
            j = i
            while j + 1 < n and mask[j + 1]:
                j += 1
            out.append((i, j))
            i = j + 1
        else:
            i += 1
    return out


def run_arc(P, i0, i1):
    if i1 <= i0:
        return 0.0, 0.0
    seg = P[i0:i1 + 1]
    st = np.sqrt(((seg[1:] - seg[:-1]) ** 2).sum(1))
    return float(st.sum()), float(st.max())


SCORE275 = "/data/gpfs/projects/punim2657/SfSpp/runs/20261024-0329_1308298_p275-walker/score275.py"
spec = importlib.util.spec_from_file_location("score275", SCORE275)
m = importlib.util.module_from_spec(spec)
_sav = sys.argv
sys.argv = ["score275", "/nonexistent"]
try:
    spec.loader.exec_module(m)
except SystemExit:
    pass
finally:
    sys.argv = _sav
AUTH = m.AUTH

log("[INPUT] RD=%s" % RD)
ours, auth = {}, {}
for i in (0, 1):
    ours[i] = read_pcd(os.path.join(OUT, "%s_Breakline_%d.pcd" % (PIECE, i)))
    auth[i] = read_pcd(AUTH % (PIECE, i))
    log("[INPUT] lane %d ours n=%d  authors n=%d  (%s)" % (i, len(ours[i]), len(auth[i]), AUTH % (PIECE, i)))
S0 = read_xyz(os.path.join(OUT, PIECE + "_Surface_0.xyz"))
S1 = read_xyz(os.path.join(OUT, PIECE + "_Surface_1.xyz"))
log("[INPUT] sheets kept: Surface_0 n=%d  Surface_1 n=%d" % (len(S0), len(S1)))

# ---------------- Phase 1: score on the shipped binary ----------------
rows = {}
log("")
log("[SCORE] lane  n   med_mm  cov_ours_to_auth  cov_auth_to_ours  jumps  max_step  len_ours  len_auth  ratio  bar")
for i in (0, 1):
    n, med, co, ca, j, mx, ok = m.lane(ours[i], auth[i])
    rows[i] = dict(n=n, med=med, cov_o=co, cov_a=ca, jumps=j, max_step=mx, ok=bool(ok),
                   len_ours=plen(ours[i]), len_auth=plen(auth[i]))
    log("[SCORE] Bl%d %5d %8.3f %8.2f %8.2f %5d %9.3f %9.2f %9.2f %6.3f  %s"
        % (i, n, med, co, ca, j, mx, rows[i]["len_ours"], rows[i]["len_auth"],
           rows[i]["len_ours"] / rows[i]["len_auth"], "PASS" if ok else "below"))

# ---------------- Phase 3: where the difference already exists ----------------
# Readings the pipeline cannot give per lane (shared paths, last writer wins) are named, not faked.
# Stages are measured as DOT SETS against the authors ring of the lane they belong to: the bag is
# an unordered dot set, so a closed-loop length for it would be meaningless and is not printed.
SHARED = 1
SHARED_FILES = (("bag (boundary)", "boundary.pcd", False),
                ("bag_improved", "boundaryImproved.pcd", False),
                ("bag_filtered", "cloud_Filtered.pcd", False),
                ("postwalk_bspline", "cloudBreaklinePointsOnBSplineSurface.pcd", True))
log("")
log("[P3] pipeline stages as DOT SETS against their own lane's authors ring (thr 2 mm)")
log("[P3] stage             lane   n   med_mm   max_mm  %%dots>2mm  %%auth_covered  len_mm")
p3 = {}
for lbl, fn, ring in SHARED_FILES:
    p = os.path.join(OUT, fn)
    if not os.path.exists(p):
        log("[P3] %-17s absent" % lbl)
        continue
    P = read_pcd(p)
    s = stage_stats(P, auth[SHARED], ring=ring)
    p3["%s|%d" % (lbl, SHARED)] = s
    log("[P3] %-17s Bl%d %5d %8.3f %8.3f %10.1f %13.1f  %s"
        % (lbl, SHARED, s["n"], s["med"], s["mx"], s["pct_dots"], s["covers_auth"],
           ("%.2f" % s["len"]) if s["len"] is not None else "n/a (dot set)"))
for i in (0, 1):
    s = stage_stats(ours[i], auth[i], ring=True)
    p3["exported|%d" % i] = s
    log("[P3] %-17s Bl%d %5d %8.3f %8.3f %10.1f %13.1f  %.2f"
        % ("exported", i, s["n"], s["med"], s["mx"], s["pct_dots"], s["covers_auth"], s["len"]))
log("[P3] authors rings: Bl0 n=%d len=%.2f mm | Bl1 n=%d len=%.2f mm"
    % (len(auth[0]), plen(auth[0]), len(auth[1]), plen(auth[1])))
log("[P3] NOTE the shared stage files hold Bl%d only (last surface written wins: 309 pre-walk dots,"
    " 84 post-walk dots, and export Bl1 has 84 dots); Bl0's bag is not retained on this binary." % SHARED)

log("")
log("[DEC] length and distance decomposition, per lane")
decomp = {}
for i in (0, 1):
    A = plen(auth[i])
    O = plen(ours[i])
    ex = p3["exported|%d" % i]
    d = dict(A=A, O=O, excess=O - A, exported_med=ex["med"], exported_pct=ex["pct_dots"],
             exported_covers=ex["covers_auth"], bag_med=None, bag_pct=None, bag_covers=None)
    b = p3.get("bag (boundary)|%d" % i)
    if b is not None:
        d.update(bag_med=b["med"], bag_pct=b["pct_dots"], bag_covers=b["covers_auth"])
        log("[DEC] Bl%d lengths A=%.2f O=%.2f excess=%+.2f mm | before the walk the bag was already "
            "med %.3f mm off with %.1f%% of its dots >2 mm and covered %.1f%% of the authors ring; "
            "after the walk the export is med %.3f mm, %.1f%% >2 mm, covers %.1f%%"
            % (i, A, O, O - A, b["med"], b["pct_dots"], b["covers_auth"],
               ex["med"], ex["pct_dots"], ex["covers_auth"]))
    else:
        log("[DEC] Bl%d lengths A=%.2f O=%.2f excess=%+.2f mm | bag not retained (shared path, last "
            "writer wins), so the before/after split is available for Bl%d only; the export itself is "
            "med %.3f mm off, %.1f%% >2 mm, covering %.1f%% of the authors ring"
            % (i, A, O, O - A, SHARED, ex["med"], ex["pct_dots"], ex["covers_auth"]))
    decomp[i] = d

# ---------------- face identity ----------------
log("")
log("[FACE] median distance to the two kept faces, and the share of dots within 1 mm of each")
faces = {}
for i in (0, 1):
    for lbl, P in (("authors_B%d" % i, auth[i]), ("our_B%d" % i, ours[i])):
        f = face_stats(P, S0, S1)
        faces[lbl] = f
        log("[FACE] %-12s n=%5d  medS0=%.3f (%.1f%% <1mm)  medS1=%.3f (%.1f%% <1mm)  on_surface med=%.3f max=%.3f  off>1mm=%.1f%%  rides S%d"
            % (lbl, len(P), f["medS0"], f["pctS0"], f["medS1"], f["pctS1"], f["med_surf"], f["mx_surf"],
               f["pct_off_surf"], f["face"]))

# ---------------- where the two rings part ----------------
log("")
log("[GEO] >2 mm stretches in ring order; 'at an end' means the stretch runs off one of that ring's")
log("[GEO] two ends, i.e. the two contours stop in different places there")
geo = {}
for i in (0, 1):
    O, A = ours[i], auth[i]
    d_oa = nn_d(O, A)
    d_ao = nn_d(A, O)
    g = {}
    for who, P, d in (("our", O, d_oa), ("authors", A, d_ao)):
        rr = runs_of(d > 2.0)
        runs = []
        for (i0, i1) in rr:
            arc, step = run_arc(P, i0, i1)
            runs.append(dict(i0=i0, i1=i1, dots=int(i1 - i0 + 1), arc=arc, step=step,
                             med=float(np.median(d[i0:i1 + 1])), mx=float(d[i0:i1 + 1].max()),
                             of=int(len(P)), at_end=bool(i0 <= 2 or i1 >= len(P) - 3)))
        g[who] = dict(nruns=len(runs), ends=sum(1 for r in runs if r["at_end"]), runs=runs)
        big = sorted(runs, key=lambda r: -r["arc"])[:3]
        desc = "; ".join("idx %d-%d of %d, %d dots, %.1f mm arc, med %.2f max %.2f mm%s"
                         % (r["i0"], r["i1"], r["of"], r["dots"], r["arc"], r["med"], r["mx"],
                            ", at an end" if r["at_end"] else ", interior") for r in big) or "none"
        log("[GEO] Bl%d %-7s ring n=%d: %d stretch(es) >2 mm, %d at an end | %s"
            % (i, who, len(P), g[who]["nruns"], g[who]["ends"], desc))
    geo[i] = g

# ---------------- class (K)/(S)/(W) ----------------
# Rule fixed before the numbers are read, from the ticket's own definitions:
#   K  the rings are on different surfaces (authors ring off every face we kept, or our ring rides
#      a different kept face than theirs) - a partition mismatch.
#   W  a retained bag was already on the authors ring (median <=1 mm, <=20% dots >2 mm) but the
#      export is not - the walk, not the bag.
#   S  a retained bag was already off the authors ring before any walk - same face, different
#      contour.
#   bag absent: S when the ring closes with no jump and our >2 mm stretches are interior
#      excursions (two contours that differ on one face); W when our ring is cut short.
cls = {}
for i in (0, 1):
    fa, fo = faces["authors_B%d" % i], faces["our_B%d" % i]
    exp = p3["exported|%d" % i]
    bag = p3.get("bag (boundary)|%d" % i)
    if fa["pct_off_surf"] > 50.0:
        c, why = "K", "the authors ring is off every face we kept (median %.3f mm, %.1f%% of its dots >1 mm from both)" % (fa["med_surf"], fa["pct_off_surf"])
    elif fo["face"] != fa["face"]:
        c, why = "K", "our ring rides kept face S%d and the authors ring rides S%d" % (fo["face"], fa["face"])
    elif bag is not None and bag["med"] <= 1.0 and bag["pct_dots"] <= 20.0 and exp["med"] > 1.5:
        c, why = "W", "the pre-walk bag was on the authors ring (median %.3f mm, %.1f%% of dots >2 mm) but the export is not (median %.3f mm)" % (bag["med"], bag["pct_dots"], exp["med"])
    elif bag is not None:
        c, why = "S", "both rings ride kept face S%d, and the bag was already %.3f mm off with %.1f%% of its dots >2 mm before any walk" % (fo["face"], bag["med"], bag["pct_dots"])
    else:
        ow = geo[i]["our"]
        ring_closed = rows[i]["jumps"] == 0
        if ring_closed and ow["ends"] == 0:
            c, why = "S", "same kept face S%d, bag not retained; our ring closes with no jump and all %d of its >2 mm stretches are interior excursions (worst %.1f mm arc, med %.2f mm), i.e. two contours that differ on one face" % (fo["face"], ow["nruns"], max([r["arc"] for r in ow["runs"]] or [0.0]), exp["med"])
        else:
            c, why = "W", "same kept face S%d, bag not retained; our ring does not close cleanly around the authors contour (%d of %d stretches at an end, %d jumps)" % (fo["face"], ow["ends"], ow["nruns"], rows[i]["jumps"])
        why += " [bag not retained: class rests on the exported geometry only]"
    cls[i] = dict(cls=c, why=why, bag_retained=bag is not None)
    log("[CLASS] Bl%d -> (%s): %s" % (i, c, why))

# ---------------- Phase 2: the picture ----------------
cols = dict(S0="#2b6cb0", S1="#dd6b20", O="#00c000", A="#000000")
names = dict(S0="Surface_0 (kept, interior)", S1="Surface_1 (kept, exterior)",
             O="our breakline", A="authors breakline")


def worst_window(O, A, w=15):
    d = nn_d(O, A)
    w = min(w, len(O))
    if w < 2:
        return 0, len(O) - 1
    cs = np.concatenate([[0.0], np.cumsum(d)])
    means = (cs[w:] - cs[:-w]) / w
    lo = int(np.argmax(means))
    return lo, lo + w - 1


def draw(ax, k1, k2, three=False, S0p=None, S1p=None, Op=None, Ap=None):
    S0p = S0 if S0p is None else S0p
    S1p = S1 if S1p is None else S1p
    if three:
        ax.scatter(S0p[:, 0], S0p[:, 1], S0p[:, 2], s=0.7, c=cols["S0"], alpha=0.35, lw=0)
        ax.scatter(S1p[:, 0], S1p[:, 1], S1p[:, 2], s=0.7, c=cols["S1"], alpha=0.35, lw=0)
        ax.plot(Op[:, 0], Op[:, 1], Op[:, 2], "-", c=cols["O"], lw=2.6)
        ax.scatter(Op[:, 0], Op[:, 1], Op[:, 2], s=13, c=cols["O"])
        ax.plot(Ap[:, 0], Ap[:, 1], Ap[:, 2], "-", c=cols["A"], lw=2.2)
        ax.scatter(Ap[:, 0], Ap[:, 1], Ap[:, 2], s=11, c=cols["A"])
        ax.set_xlabel("x"); ax.set_ylabel("y"); ax.set_zlabel("z")
    else:
        ax.scatter(S0p[:, k1], S0p[:, k2], s=0.7, c=cols["S0"], alpha=0.30, lw=0)
        ax.scatter(S1p[:, k1], S1p[:, k2], s=0.7, c=cols["S1"], alpha=0.30, lw=0)
        ax.plot(Op[:, k1], Op[:, k2], "-", c=cols["O"], lw=2.4)
        ax.scatter(Op[:, k1], Op[:, k2], s=11, c=cols["O"])
        ax.plot(Ap[:, k1], Ap[:, k2], "-", c=cols["A"], lw=2.0)
        ax.scatter(Ap[:, k1], Ap[:, k2], s=10, c=cols["A"])
        ax.set_xlabel("XYZ"[k1]); ax.set_ylabel("XYZ"[k2])
        ax.set_aspect("equal", adjustable="datalim")


png_rows = []
for i in (0, 1):
    Op, Ap = ours[i], auth[i]
    lo, hi = worst_window(Op, Ap)
    ctr = Op[lo:hi + 1]
    mn = ctr.min(0) - 14.0
    mx = ctr.max(0) + 14.0
    keep0 = np.all((S0 >= mn) & (S0 <= mx), axis=1)
    keep1 = np.all((S1 >= mn) & (S1 <= mx), axis=1)
    keepO = np.all((Op >= mn) & (Op <= mx), axis=1)
    keepA = np.all((Ap >= mn) & (Ap <= mx), axis=1)
    ext = mx - mn
    order = np.argsort(ext)[::-1]
    z1, z2 = int(order[0]), int(order[1])
    fig = plt.figure(figsize=(23.0, 5.2))
    ax = fig.add_subplot(1, 5, 1, projection="3d")
    draw(ax, 0, 1, three=True, Op=Op, Ap=Ap)
    ax.set_title("3D")
    for k, (i1, i2) in enumerate([(0, 1), (0, 2), (1, 2)]):
        ax = fig.add_subplot(1, 5, 2 + k)
        draw(ax, i1, i2, Op=Op, Ap=Ap)
        ax.set_title("XYZ"[i1] + "-" + "XYZ"[i2] + (" (plan)" if (i1, i2) == (0, 1) else ""))
    ax = fig.add_subplot(1, 5, 5)
    draw(ax, z1, z2, S0p=S0[keep0], S1p=S1[keep1], Op=Op[keepO], Ap=Ap[keepA])
    ax.set_title("ZOOM on our worst stretch (our dots %d-%d, %s-%s)" % (lo, hi, "XYZ"[z1], "XYZ"[z2]))
    ttl = ("%s  Bl%d   our line n=%d len %.1f mm   authors n=%d len %.1f mm (%.2fx)   median %.3f mm   "
           "our dots >2 mm from authors %.1f%%   class (%s)   DS-mesh cloud: a new draw, not a re-measure of 259") % (
        PIECE, i, len(Op), rows[i]["len_ours"], len(Ap), rows[i]["len_auth"],
        rows[i]["len_ours"] / rows[i]["len_auth"], rows[i]["med"], p3["exported|%d" % i]["pct_dots"], cls[i]["cls"])
    fig.suptitle(ttl, fontsize=11)
    from matplotlib.lines import Line2D
    handles = [Line2D([], [], color=cols[k], lw=6, label=names[k]) for k in ("S0", "S1", "O", "A")]
    fig.legend(handles=handles, loc="lower center", ncol=4, frameon=False, fontsize=9)
    fig.tight_layout(rect=(0, 0.05, 1, 0.94))
    p = os.path.join(PNG, "p289_J09_Bl%d.png" % i)
    fig.savefig(p, dpi=100)
    plt.close(fig)
    with open(p, "rb") as f:
        head = f.read(33)
    w, h = __import__("struct").unpack(">II", head[16:24])
    png_rows.append(dict(lane=i, path=p, px="%dx%d" % (w, h), bytes=os.path.getsize(p)))
    log("[PNG] %s  %dx%d px  %.2f MB" % (p, w, h, os.path.getsize(p) / 1e6))

json.dump(dict(scores={str(k): v for k, v in rows.items()},
               p3={k: v for k, v in p3.items()},
               decomp={str(k): v for k, v in decomp.items()},
               faces=faces, geo={str(k): v for k, v in geo.items()},
               cls={str(k): v for k, v in cls.items()},
               png=png_rows), open(os.path.join(OUT, "lanes.json"), "w"), indent=1)
with open(os.path.join(OUT, "a289_log.txt"), "w") as f:
    f.write("\n".join(LOG) + "\n")
log("done")
