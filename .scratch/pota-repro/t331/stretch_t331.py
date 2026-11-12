#!/usr/bin/env python3
"""Ticket 331 Part B -- the matched stretch between touching pairs, measured in the vessel frame.

For every pair: take both pieces' Breakline_0 dot sets (ASCII PCD as exported by the chain),
put each piece into the assembled vessel frame with its answer-key transform (X = R x + t),
then walk each line's dots in file order and keep the longest contiguous stretch whose dots
sit within TOL of the other line (distance to the other polyline, not to its dots).
Reported per pair: dots in the stretch, mm of arclength along that line, the worst distance
inside the stretch, and the fraction of the line it covers.

The matcher (structure-from-sherds-pp class/feature_matching.cpp) needs an LCS run of >= 7 dots
with dots 1.9 mm apart = 12.6 mm, in whatever frame the line arrives in.  A 3x model keeps the
1.9 mm spacing, so the same 7 dots cover 4.2 mm of original vessel.

TOL is given in the arm's own frame: 1.5 mm is the ticket's bar, and for the 3x arm 4.5 mm is
the same physical tolerance expressed on the scaled model (both are reported).
"""
import argparse
import json
import os
import sys

import numpy as np

TOUCHING = [(1, 2), (1, 4), (1, 8), (1, 9), (2, 5), (2, 9), (3, 5), (6, 7), (7, 9)]
NONTOUCH = [(1, 5), (1, 6), (3, 7), (4, 5), (4, 6), (5, 9), (6, 8), (7, 8), (8, 9)]


def read_pcd(path):
    pts = []
    with open(path, "r", errors="ignore") as fh:
        header = True
        for line in fh:
            if header:
                if line.startswith("DATA"):
                    header = False
                continue
            f = line.split()
            if len(f) >= 3:
                pts.append((float(f[0]), float(f[1]), float(f[2])))
    return np.asarray(pts, dtype=float)


def read_key(path):
    M = np.loadtxt(path)
    return M[:3, :3].copy(), M[:3, 3].copy()


def seg_dist(P, Q):
    A, B = Q[:-1], Q[1:]
    AB = B - A
    L2 = (AB * AB).sum(1)
    L2 = np.where(L2 <= 0.0, 1e-12, L2)
    AP = P[:, None, :] - A[None, :, :]
    tt = np.clip((AP * AB[None, :, :]).sum(2) / L2[None, :], 0.0, 1.0)
    C = A[None, :, :] + tt[:, :, None] * AB[None, :, :]
    return np.linalg.norm(P[:, None, :] - C, axis=2).min(1)


def runs_of(mask):
    out = []
    start = None
    for i, v in enumerate(mask):
        if v and start is None:
            start = i
        elif not v and start is not None:
            out.append((start, i - 1))
            start = None
    if start is not None:
        out.append((start, len(mask) - 1))
    return out


def arclen(P):
    if len(P) < 2:
        return np.zeros(len(P))
    return np.r_[0.0, np.cumsum(np.linalg.norm(np.diff(P, axis=0), axis=1))]


def best_stretch(P, Q, tol):
    """longest contiguous in-tolerance stretch of P against the polyline Q"""
    if len(P) < 2 or len(Q) < 2:
        return None
    d = seg_dist(P, Q)
    s = arclen(P)
    best = None
    for i, j in runs_of(d <= tol):
        mm = float(s[j] - s[i])
        cand = {"dots": int(j - i + 1), "mm": mm, "max_gap": float(d[i:j + 1].max()),
                "s0": float(s[i]), "s1": float(s[j]), "i": int(i), "j": int(j)}
        if best is None or mm > best["mm"] or (mm == best["mm"] and cand["dots"] > best["dots"]):
            best = cand
    return {"best": best, "dist": d, "s": s}


def measure(A, B, tol):
    res = {}
    for name, (P, Q) in (("A", (A, B)), ("B", (B, A))):
        r = best_stretch(P, Q, tol)
        if r is None:
            continue
        b = r["best"]
        if b is None:
            res[name] = {"dots": 0, "mm": 0.0, "max_gap": float("nan"), "frac": 0.0,
                         "line_len": float(r["s"][-1])}
            continue
        b["frac"] = b["mm"] / float(r["s"][-1]) if r["s"][-1] > 0 else 0.0
        b["line_len"] = float(r["s"][-1])
        res[name] = b
    if not res:
        return None
    pick = "A" if res.get("A", {}).get("mm", 0.0) >= res.get("B", {}).get("mm", 0.0) else "B"
    out = dict(res[pick])
    out["line"] = pick
    out["A"] = res.get("A")
    out["B"] = res.get("B")
    return out


def order_check(P):
    if len(P) < 3:
        return (float("nan"), float("nan"))
    d = np.linalg.norm(np.diff(P, axis=0), axis=1)
    return (float(np.median(d)), float(d.max()))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--geom-large", required=True)
    ap.add_argument("--key-large", required=True)
    ap.add_argument("--geom-ctl", required=True)
    ap.add_argument("--key-ctl", required=True)
    ap.add_argument("--geom-rad3", default="")
    ap.add_argument("--key-rad3", default="")
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    arms = [("ctl", a.geom_ctl, a.key_ctl, [1.5, 4.5]),
            ("large", a.geom_large, a.key_large, [1.5, 4.5])]
    if a.geom_rad3:
        arms.append(("rad3", a.geom_rad3, a.key_rad3, [1.5, 4.5]))

    rows = []
    diag = []
    for arm, gdir, kdir, tols in arms:
        pts = {}
        for i in range(1, 10):
            f = os.path.join(gdir, "Juglet_Piece_%d.Bl0" % i)
            P = read_pcd(f)
            R, t = read_key(os.path.join(kdir, "Juglet_Piece_%d_T.txt" % i))
            pts[i] = P @ R.T + t
            med, mx = order_check(pts[i])
            diag.append((arm, i, len(P), med, mx))
        for pair in TOUCHING + NONTOUCH:
            i, j = pair
            kind = "touching" if pair in TOUCHING else "nontouching"
            A = pts[i] - pts[i].mean(0)  # only to keep the numbers small; rigid shift is irrelevant
            B = pts[j] - pts[i].mean(0)
            for tol in tols:
                m = measure(A, B, tol)
                if m is None:
                    rows.append([arm, kind, "%d-%d" % (i, j), "%.1f" % tol, "none", 0, 0.0, "", ""])
                    continue
                rows.append([arm, kind, "%d-%d" % (i, j), "%.1f" % tol, m["line"], m["dots"],
                             m["mm"], m["max_gap"], m["frac"]])
    with open(os.path.join(a.out, "stretch.tsv"), "w") as fh:
        fh.write("arm\tkind\tpair\ttol_mm\tline\tdots\tmm\tmax_gap_mm\tfrac_of_line\n")
        for r in rows:
            fh.write("%s\t%s\t%s\t%s\t%s\t%s\t%.4f\t%s\t%s\n"
                     % (r[0], r[1], r[2], r[3], r[4], r[5], r[6],
                        "" if r[7] == "" else "%.4f" % r[7],
                        "" if r[8] == "" else "%.4f" % r[8]))
    with open(os.path.join(a.out, "dot_order.tsv"), "w") as fh:
        fh.write("arm\tpiece\tdots\tmedian_step_mm\tmax_step_mm\n")
        for d in diag:
            fh.write("%s\t%d\t%d\t%.4f\t%.4f\n" % d)

    print("%-6s %-11s %-6s %5s %5s %9s %9s %7s" % ("arm", "kind", "pair", "tol", "line", "dots", "mm", "maxgap"))
    for r in rows:
        if r[1] == "touching":
            print("%-6s %-11s %-6s %5s %5s %9d %9.3f %7s"
                  % (r[0], r[1], r[2], r[3], r[4], r[5], r[6], "" if r[7] == "" else "%.3f" % r[7]))
    print()
    summary = {}
    for arm, _, _, tols in arms:
        for tol in tols:
            sel = [r for r in rows if r[0] == arm and r[1] == "touching" and r[3] == "%.1f" % tol]
            reach7 = [r for r in sel if r[5] >= 7]
            reach126 = [r for r in sel if r[6] >= 12.6]
            both = [r for r in sel if r[5] >= 7 and r[6] >= 12.6]
            summary["%s|%.1f" % (arm, tol)] = {
                "pairs": len(sel), "dots_ge7": len(reach7), "mm_ge12.6": len(reach126), "both": len(both),
                "pairs_both": [r[2] for r in both], "pairs_fail": [r[2] for r in sel if r not in both]}
            print("SUMMARY %-6s tol=%.1f mm : dots>=7 %d/9 | mm>=12.6 %d/9 | both %d/9 | fail=%s"
                  % (arm, tol, len(reach7), len(reach126), len(both),
                     ",".join(r[2] for r in sel if r not in both)))
    with open(os.path.join(a.out, "stretch_summary.json"), "w") as fh:
        json.dump(summary, fh, indent=1)
    print()
    print("dot order (median / max step between consecutive dots, mm) -- a walk order shows ~the dot spacing:")
    for d in diag:
        print("  %-6s piece %d  dots=%-4d median=%.3f max=%.3f" % d)


if __name__ == "__main__":
    main()
