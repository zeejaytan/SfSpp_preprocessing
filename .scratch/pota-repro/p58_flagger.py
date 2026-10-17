"""Ticket 58 (pilot, Pot F): relaxed rim flagger — COPY of the banked B recipe.

Port of .scratch/pota-repro/p49_flagger.py (paper-recipe test from author's
check_base_and_rim.m: std(h)<1.0 & std(r)<1.0 & |mean dr|,|mean dh|<0.1, OR
over axes) with the relaxed >=10-pt rule (MIN_N=10), adapted to Pot F
(POT=F, pieces 1..7 files present; piece 07 has an EMPTY axle file in the
bundle so the binary auto-excludes it — flagging its files is harmless).

Reads the COPIED F bundle + F finder axes, writes per-seg rim flags into the
copy only. Never touches ORIG or ticket-39/49 dirs. Verifies DATA sections
byte-identical after (gate carries over formally: gate is coordinates-only).
"""

import hashlib
import os
import sys

import numpy as np

MIN_N = int(os.environ.get("P58_MIN_N", "10"))
POT = os.environ.get("P58_POT", "F")
N_PIECES = int(os.environ.get("P58_N_PIECES", "7"))
BUN = os.environ.get(
    "P58_BUN",
    "/data/gpfs/projects/punim2657/pota58_repro/prep/pota58_bundle_F/SfS_pp",
)
BL = os.path.join(BUN, "Breaklines")
AXDIR = os.environ.get(
    "P58_AXDIR",
    "/data/gpfs/projects/punim2657/Temp/potsac-p39-run/finder_axes_F",
)
ORIG_BL = os.environ.get(
    "P58_ORIG_BL",
    "/data/gpfs/projects/punim2657/sfs_main/original_samples/SfS_pp/Breaklines",
)


def load_rim(path):
    with open(path) as f:
        lines = [l.rstrip("\n") for l in f]
    h1 = lines[1].split()
    nseg = int(h1[1])
    topo = h1[3] if len(h1) > 3 else "0"
    ranges = []
    for i in range(nseg):
        p = lines[2 + i].split()
        ranges.append([p[0], int(p[1]), int(p[2]), int(p[3])])
    di = next(i for i, l in enumerate(lines) if l.strip() == "DATA ascii")
    return lines, h1, topo, ranges, di


def seg_stats(h, R, s, e):
    seg = np.arange(s - 1, e)
    hs = h[seg]
    rs = R[seg]
    n = len(seg)
    sh = float(np.std(hs)) if n > 1 else 0.0
    sr = float(np.std(rs)) if n > 1 else 0.0
    dh = float(np.mean(np.diff(hs)[1:])) if n > 4 else 0.0
    dr = float(np.mean(np.diff(rs)[1:])) if n > 4 else 0.0
    return dict(n=n, sh=sh, sr=sr, dh=dh, dr=dr)


def passes(st):
    return (
        st["sh"] < 1.0
        and st["sr"] < 1.0
        and abs(st["dr"]) < 0.1
        and abs(st["dh"]) < 0.1
        and st["n"] >= MIN_N
    )


def detect_ranges_points(ranges, data, axrows):
    P = data[:, :3]
    flags = []
    detail = []
    for (tag, s, e, oldfl) in ranges:
        hit = False
        best = None
        for ax in axrows:
            c = np.array(ax[:3])
            d = np.array(ax[3:])
            d /= np.linalg.norm(d)
            t = (P - c) @ d
            R = np.linalg.norm(P - (c + np.outer(t, d)), axis=1)
            st = seg_stats(t, R, s, e)
            if best is None or st["sh"] + st["sr"] < best["sh"] + best["sr"]:
                best = st
            hit = hit or passes(st)
        flags.append(1 if hit else 0)
        detail.append(best)
    return flags, detail


def orig_flags(piece, side):
    f = os.path.join(ORIG_BL, f"Pot_{POT}_Piece_{piece:02d}_Breakline_{side}.pcd")
    with open(f) as fh:
        lines = [l.rstrip("\n") for l in fh]
    h1 = lines[1].split()
    nseg = int(h1[1])
    segs = []
    for i in range(nseg):
        segs.append(int(lines[2 + i].split()[3]))
    return h1[3], segs


def md5_data(path):
    with open(path, "rb") as f:
        raw = f.read()
    marker = b"DATA ascii\n"
    i = raw.find(marker) + len(marker)
    return hashlib.md5(raw[i:]).hexdigest()


print(f"P58 flagger: POT={POT} MIN_N={MIN_N} BUN={BUN} AXDIR={AXDIR}", flush=True)
report = []
for piece in range(1, N_PIECES + 1):
    for side in (0, 1):
        name = f"Pot_{POT}_Piece_{piece:02d}_Breakline_{side}.pcd"
        path = os.path.join(BL, name)
        if not os.path.exists(path):
            print(f"{name} ABSENT — skipped", flush=True)
            continue
        before = md5_data(path)
        lines, h1, topo, ranges, di = load_rim(path)
        data = np.array(
            [[float(x) for x in l.split()[:7]] for l in lines[di + 1 :] if l.strip()]
        )
        ax = np.atleast_2d(
            np.loadtxt(os.path.join(AXDIR, f"Pot_{POT}_Piece_{piece:02d}_Axis.xyz"))
        )
        flags, detail = detect_ranges_points(ranges, data, ax)
        new_top = "1" if any(flags) else "0"
        # rewrite header lines only
        h1[3] = new_top
        lines[1] = " ".join(h1)
        for i, (tag, s, e, oldfl) in enumerate(ranges):
            lines[2 + i] = f"{tag} {s} {e} {flags[i]}"
        with open(path, "w") as f:
            f.write("\n".join(lines) + "\n")
        after = md5_data(path)
        assert before == after, f"DATA changed in {name}"
        otop, osegs = orig_flags(piece, side)
        omatch = otop == new_top and osegs == flags
        on = len(osegs)
        report.append(
            (name, topo, new_top, [r[3] for r in ranges], flags, osegs, omatch, before)
        )
        cells = " ".join(
            f"[s{i}:n={d['n']} sh={d['sh']:.2f} sr={d['sr']:.2f} "
            f"dr={d['dr']:.3f} dh={d['dh']:.3f} new={flags[i]} "
            f"orig={(osegs[i] if i < on else '-')}]"
            for i, d in enumerate(detail)
        )
        print(
            f"{name} top {topo}->{new_top} ORIGtop={otop} ORIGnseg={on} "
            f"layout-match={omatch} datamd5={before[:8]} {cells}",
            flush=True,
        )

n_match = sum(1 for r in report if r[6])
print(f"LAYOUT-MATCH {n_match}/{len(report)} files exactly match ORIG flags")
