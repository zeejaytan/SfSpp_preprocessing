#!/usr/bin/env python3
"""ticket 49 -- k49: re-derive k, the one dimensionless constant in the curvature law.

THE LAW (ticket 45):  theta_deg = k * (S / R_fold) * (180/pi),  S = the pipeline's effective
voxel spacing, R_fold = the median fold radius the estimator measures.  Ticket 43 fixed k = 3.3573
on Pot A.  Ticket 49 changed HOW R_fold is measured (a fixed physical patch instead of k=30
neighbours); if that changes R, then the k that makes the law hold changes with it.  This script
answers: given the pair separation this run actually produced, what k would put the grown pair at
the measured WALL separation, per vessel and pooled -- and does one k serve both vessels?

WHAT THIS IS AND IS NOT.  This is a FIT on the same pieces it is then reported against, which is
not a test of the law.  The ticket says so and this file says so: a k derived here is a candidate
to be tested on pieces this run did not fit, never a result on its own.  The scaling used is

    s_target / s_now = theta_target / theta_now        (pair separation linear in the growth angle)

which is an ASSUMPTION, not a measurement: it is exact only if the grown surface advances in
proportion to the angle over this range.  Every row therefore carries k_needed_linear, and the
summary says plainly that it is a linear projection to be checked by running that k, not an
observed k.  Where a piece's pair already sits at wall scale the projection is a no-op (ratio ~1)
and the k is the one the run used -- those rows are the only ones that are not extrapolated.

A GENUINE WALL PAIR, the test applied here (stated, so a reader can disagree with it):
  * the cell grew two surfaces and the pair command succeeded;
  * coin <= 0.01            -- the two surfaces do not cross each other;
  * med_angle_deg >= 5.0    -- the surfaces are not parallel.  Two parallel layers of ONE face is
                              exactly the 0.2-0.3 mm failure of tickets 44/46; a wall's two faces
                              meet the break edge at an angle.
Rows that fail are still written, flagged, and excluded from the k groups (n counts only the
passes).  The test does not look at the separation it is used to explain, so it cannot pre-select
the answer.

CLI: k49.py --out OUT --pairs pairs49.tsv --wall wall49.tsv --cells out/cells-pipeline
Writes <out>/k49.tsv (per-piece rows, then the group summary rows) and prints both.
Exit 0 ok; 4 cannot read an input; 5 no pair rows at all (nothing to derive from -- a result).
"""
import argparse
import csv
import os
import sys


def log(m):
    sys.stdout.write("[K49] %s\n" % m)
    sys.stdout.flush()


def read_tsv(path):
    with open(path, newline="", encoding="utf-8") as fh:
        return list(csv.DictReader(fh, delimiter="\t"))


def read_cell(path):
    d = {}
    with open(path, "r") as fh:
        for line in fh:
            line = line.rstrip("\n").rstrip("\r")
            if "\t" in line:
                k, v = line.split("\t", 1)
                d[k] = v
    return d


def fnum(x):
    try:
        return float(x)
    except (TypeError, ValueError):
        return None


def fmt(x, nd=5):
    return "na" if x is None else ("%." + str(nd) + "f") % x


def median(xs):
    s = sorted(xs)
    n = len(s)
    if n == 0:
        return None
    return s[n // 2] if n % 2 else 0.5 * (s[n // 2 - 1] + s[n // 2])


def field(line, key):
    """'[GROWTH-45] piece=X S=0.27 R_med=13.2 theta=3.92 patch_r=1.0 skipped=0/20000' -> value."""
    for tok in (line or "").split():
        if tok.startswith(key + "="):
            return tok.split("=", 1)[1]
    return None


COLS = ["scope", "pot", "piece", "arm", "patch_r", "cloud_set", "S_mm", "R_med_mm",
        "theta_computed_deg", "pair_med_nn_mm", "pair_med_angle_deg", "pair_coin", "wall_mm",
        "pair_over_wall", "k_now", "k_needed_linear", "genuine_pair", "n", "note"]


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--pairs", required=True)
    ap.add_argument("--wall", required=True)
    ap.add_argument("--cells", required=True, help="out/cells-pipeline (for the [GROWTH-45] S= field)")
    ap.add_argument("--coin-max", type=float, default=0.01)
    ap.add_argument("--angle-min", type=float, default=5.0)
    a = ap.parse_args(argv)

    try:
        pairs = read_tsv(a.pairs)
    except OSError as e:
        log("FAIL cannot read pairs %s: %s" % (a.pairs, e))
        return 4
    try:
        walls = read_tsv(a.wall)
    except OSError as e:
        log("FAIL cannot read wall %s: %s" % (a.wall, e))
        return 4

    # wall thickness per (pot, piece) -- the median over the cells that measured it, so a piece
    # whose cloud was measured twice at the two radii contributes one number, not two.
    wvals = {}
    for w in walls:
        v = fnum(w.get("thick_med_mm"))
        if v is not None:
            wvals.setdefault((w.get("pot"), w.get("piece")), []).append(v)
    wall = dict((k, median(v)) for k, v in wvals.items())

    # the [GROWTH-45] line per cell gives S; R_med and theta are also in it, which is a cross-check
    # against pipeline_cells.tsv (a disagreement is noted, never silently preferred).
    g45 = {}
    for name in sorted(os.listdir(a.cells)):
        c = os.path.join(a.cells, name, "cell.tsv")
        if not os.path.exists(c):
            continue
        info = read_cell(c)
        line = info.get("growth45_line", "")
        g45[(info.get("pot"), info.get("piece"), info.get("arm"))] = {
            "S": fnum(field(line, "S")),
            "R": fnum(field(line, "R_med")),
            "theta": fnum(field(line, "theta")),
            "skipped": field(line, "skipped"),
        }

    rows = []
    for p in pairs:
        key = (p.get("pot"), p.get("piece"))
        arm = p.get("arm", "")
        g = g45.get((key[0], key[1], arm), {})
        s_now = fnum(p.get("med_nn"))
        ang = fnum(p.get("med_angle_deg"))
        coin = fnum(p.get("coin"))
        w = wall.get(key)
        S = g.get("S")
        R = g.get("R")
        th = g.get("theta")
        note = []
        if g.get("skipped") and "/" in g["skipped"]:
            sk, _, tot = g["skipped"].partition("/")
            if sk not in ("0", ""):
                note.append("skipped %s of %s patch points" % (sk, tot))
        if S is None or R in (None, 0.0) or th is None:
            note.append("no [GROWTH-45] S/R/theta for this cell")
        k_now = None
        if S not in (None, 0.0) and R not in (None, 0.0) and th is not None:
            k_now = th * (3.141592653589793 / 180.0) * R / S

        genuine = (coin is not None and coin <= a.coin_max
                   and ang is not None and ang >= a.angle_min)
        if coin is None or ang is None:
            genuine = False
            note.append("pair row carries no coin/angle")
        elif not genuine:
            note.append("not a genuine wall pair: coin=%s angle=%s deg (needs coin<=%g, angle>=%g)"
                        % (fmt(coin, 4), fmt(ang, 2), a.coin_max, a.angle_min))

        ratio = None
        k_needed = None
        if w is None:
            note.append("no wall thickness measured for this piece")
        elif s_now is not None and s_now > 0:
            ratio = w / s_now
            if k_now is not None and genuine:
                k_needed = k_now * ratio
        if genuine and k_needed is None:
            note.append("genuine pair but k not derivable (missing wall, S, R or theta)")

        rows.append({
            "scope": "piece", "pot": key[0], "piece": key[1], "arm": arm,
            "patch_r": p.get("patch_r", "na"), "cloud_set": p.get("cloud_set", "na"),
            "S_mm": fmt(S, 5), "R_med_mm": fmt(R, 5),
            "theta_computed_deg": fmt(th, 5),
            "pair_med_nn_mm": fmt(s_now, 4), "pair_med_angle_deg": fmt(ang, 3),
            "pair_coin": fmt(coin, 4), "wall_mm": fmt(w, 4),
            "pair_over_wall": fmt(ratio, 4),
            "k_now": fmt(k_now, 4), "k_needed_linear": fmt(k_needed, 4),
            "genuine_pair": "yes" if genuine else "no",
            "n": "1", "note": "; ".join(note),
        })

    # ---- the answer: k per vessel and pooled, with spread and n, at each patch radius and each
    # cloud set.  Grouped that way on purpose: pooling the radii would hide the thing under test.
    groups = []
    for scope_kind in ("per-radius+cloud", "pooled-all"):
        keys = set()
        for r in rows:
            if r["k_needed_linear"] == "na":
                continue
            if scope_kind == "pooled-all":
                keys.add((r["pot"],))
            else:
                keys.add((r["pot"], r["patch_r"], r["cloud_set"]))
        for kk in sorted(keys):
            sel = []
            for r in rows:
                if r["k_needed_linear"] == "na":
                    continue
                if scope_kind == "pooled-all":
                    if (r["pot"],) != kk:
                        continue
                else:
                    if (r["pot"], r["patch_r"], r["cloud_set"]) != kk:
                        continue
                sel.append(r)
            ks = [fnum(r["k_needed_linear"]) for r in sel]
            ks = [x for x in ks if x is not None]
            if not ks:
                continue
            med = median(ks)
            spread = (max(ks) - min(ks)) if len(ks) > 1 else 0.0
            rel = 100.0 * spread / med if med else None
            pot = kk[0]
            pr = kk[1] if len(kk) > 1 else "all"
            cs = kk[2] if len(kk) > 1 else "all"
            groups.append({
                "scope": "group(%s)" % scope_kind, "pot": pot, "piece": "(%d pieces)" % len(ks),
                "arm": "all", "patch_r": pr, "cloud_set": cs,
                "S_mm": "na", "R_med_mm": "na", "theta_computed_deg": "na",
                "pair_med_nn_mm": "na", "pair_med_angle_deg": "na", "pair_coin": "na",
                "wall_mm": "na", "pair_over_wall": "na",
                "k_now": fmt(median([fnum(r["k_now"]) for r in sel if fnum(r["k_now"]) is not None]), 4),
                "k_needed_linear": fmt(med, 4),
                "genuine_pair": "yes",
                "n": str(len(ks)),
                "note": "median; spread %.4f (%.1f%% of median), min %.4f max %.4f" % (
                    spread, rel if rel is not None else float("nan"), min(ks), max(ks)),
            })

    # ---- does ONE k serve both vessels?  Compare the pooled medians and say by how much.
    pooled = dict((g["pot"], fnum(g["k_needed_linear"])) for g in groups
                  if g["scope"] == "group(pooled-all)")
    verdict = []
    if len(pooled) >= 2 and all(v is not None for v in pooled.values()):
        hi = max(pooled.values())
        lo = min(pooled.values())
        if lo > 0:
            spread_pct = 100.0 * (hi - lo) / lo
            if spread_pct <= 10.0:
                verdict.append("ONE k serves both vessels: pooled medians differ by %.1f%% "
                               "(<= 10%%), so a single constant is adequate on this evidence"
                               % spread_pct)
            else:
                verdict.append("ONE k does NOT serve both vessels: pooled medians differ by %.1f%% "
                               "(> 10%%), so k must be stated per vessel or the difference explained"
                               % spread_pct)
        verdict.append("pooled medians: " + ", ".join(
            "%s %.4f" % (p, pooled[p]) for p in sorted(pooled)))
    else:
        verdict.append("one-k question not answerable: fewer than two vessels produced a k "
                       "(n=%d vessels)" % len(pooled))

    out_tsv = os.path.join(a.out, "k49.tsv")
    with open(out_tsv, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=COLS, delimiter="\t", lineterminator="\n")
        w.writeheader()
        for r in rows + groups:
            w.writerow(r)

    log("=== per piece (k_needed_linear = k_now x wall/pair; linear projection, see the header) ===")
    for r in rows:
        log("%s/%s %-12s R=%s cloud=%-6s S=%s Rmed=%s theta=%s pair=%s angle=%s coin=%s wall=%s "
            "ratio=%s k_now=%s k_needed=%s genuine=%s %s" % (
                r["pot"], r["piece"], r["arm"], r["patch_r"], r["cloud_set"], r["S_mm"],
                r["R_med_mm"], r["theta_computed_deg"], r["pair_med_nn_mm"],
                r["pair_med_angle_deg"], r["pair_coin"], r["wall_mm"], r["pair_over_wall"],
                r["k_now"], r["k_needed_linear"], r["genuine_pair"], r["note"]))
    log("=== groups (the answer: k per vessel, with spread and n) ===")
    for g in groups:
        log("%-16s %-7s R=%-4s cloud=%-6s n=%-2s k_needed=%s  %s" % (
            g["scope"], g["pot"], g["patch_r"], g["cloud_set"], g["n"],
            g["k_needed_linear"], g["note"]))
    log("=== does one k serve both vessels? ===")
    for v in verdict:
        log(v)
    log("caveat carried into the report: k49 is a FIT on the pieces it is reported against, and "
        "k_needed_linear is a linear projection to be TESTED by running that k, not an observed "
        "value.  Only rows whose pair already sits at wall scale (ratio ~ 1) are not extrapolated.")
    log("written %s" % out_tsv)
    if not rows:
        log("no pair rows at all: no cell grew a pairable two-surface result, so there is nothing "
            "to derive k from (a result, recorded)")
        return 5
    return 0


if __name__ == "__main__":
    sys.exit(main())
