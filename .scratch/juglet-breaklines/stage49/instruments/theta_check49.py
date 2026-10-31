#!/usr/bin/env python3
"""ticket 49 -- theta_check49: every cell's [GROWTH-45] formula theta against the ticket-43
k-rule reference, at the ~2% band the ticket names, SPLIT BY PATCH RADIUS AND CLOUD SET.

REPORT ONLY.  A miss is a RESULT ("if the prediction fails: report where it lands and STOP --
no tuning, no re-runs"), never a failure exit: this script exits 0 with the table even when every
piece lands outside the band.  It exits nonzero only when it cannot produce the table at all
(missing/unreadable inputs, a cell with no theta evidence), because then there is nothing to
report.

Why the split matters: ticket 48 showed the k = 30 patch shrank on the corpus clouds, so the SAME
reference theta is met or missed depending on the cloud the cell read.  One pooled "in band n/17"
number would hide exactly the effect this run exists to measure.

columns: pot piece arm patch_r cloud_set theta_computed_deg theta_ref_deg delta_abs delta_pct
         within_2pct note
"""
import argparse
import csv
import sys


def read_tsv(path):
    with open(path, newline="", encoding="utf-8") as fh:
        return list(csv.DictReader(fh, delimiter="\t"))


def fmt(x, nd=4):
    try:
        return ("%." + str(nd) + "f") % float(x)
    except (TypeError, ValueError):
        return "na"


def split_arm(arm):
    """r1.0-corpus -> ("1.0", "corpus"); an unexpected label is passed through, never guessed."""
    a = (arm or "").strip()
    if a.startswith("r") and "-" in a:
        rest = a[1:]
        r, _, cs = rest.partition("-")
        return r, cs
    return "na", a or "na"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cells", required=True, help="pipeline_cells.tsv of the t49 run")
    ap.add_argument("--ref", required=True, help="thetas49.tsv (k43 predictions, pot/piece/theta_ref_deg)")
    ap.add_argument("--out", required=True, help="theta_check49.tsv to write")
    ap.add_argument("--band-pct", type=float, default=2.0, help="band width in %% of ref (default 2.0)")
    args = ap.parse_args()

    try:
        cells = read_tsv(args.cells)
    except OSError as e:
        print("[THETA49] FAIL cannot read cells %s: %s" % (args.cells, e)); return 4
    try:
        refs = {(r["pot"], r["piece"]): r["theta_ref_deg"] for r in read_tsv(args.ref)}
    except OSError as e:
        print("[THETA49] FAIL cannot read ref %s: %s" % (args.ref, e)); return 4

    rows = []
    missing_theta = []
    for c in cells:
        key = (c["pot"], c["piece"])
        ref = refs.get(key)
        got = (c.get("theta_computed_deg") or "").strip()
        # a SKIP row carries "-" in every value column; that is a cell that never ran, not a cell
        # whose theta could not be parsed.  Treated as no evidence, and said so.
        skipped_row = got in ("-", "")
        if skipped_row:
            got = ""
        pr, cs = split_arm(c.get("arm", ""))
        note = ""
        if ref is None:
            note = "no k43 reference row for this piece"
        if skipped_row and (c.get("note") or "").strip():
            note = (note + "; " if note else "") + "cell did not run (%s)" % c["note"].strip()
        if not got:
            note = (note + "; " if note else "") + "no GROWTH-45 theta in the cell"
            missing_theta.append("%s/%s/%s" % (key[0], key[1], c.get("arm", "")))
        d_abs = d_pct = "na"
        within = "no-evidence"
        if got and ref not in (None, ""):
            try:
                da = abs(float(got) - float(ref))
                dp = 100.0 * da / float(ref)
                d_abs, d_pct = fmt(da), fmt(dp, 3)
                within = "yes" if dp <= args.band_pct else "NO"
            except ValueError:
                note = (note + "; " if note else "") + "unparseable theta"
        rows.append({
            "pot": c["pot"], "piece": c["piece"], "arm": c.get("arm", ""),
            "patch_r": (c.get("patch_r") or pr).strip() or "na", "cloud_set": cs,
            "theta_computed_deg": got or "na", "theta_ref_deg": ref if ref is not None else "na",
            "delta_abs": d_abs, "delta_pct": d_pct, "within_2pct": within, "note": note,
        })

    fields = ["pot", "piece", "arm", "patch_r", "cloud_set", "theta_computed_deg",
              "theta_ref_deg", "delta_abs", "delta_pct", "within_2pct", "note"]
    with open(args.out, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=fields, delimiter="\t", lineterminator="\n")
        w.writeheader()
        w.writerows(rows)

    print("[THETA49] theta vs the ticket-43 k-rule reference at %.1f%% band -- REPORT ONLY, misses are results" % args.band_pct)
    for r in rows:
        print("[THETA49] %s/%s arm=%s R=%s cloud=%s computed=%s ref=%s d=%s%% within=%s %s" % (
            r["pot"], r["piece"], r["arm"], r["patch_r"], r["cloud_set"],
            r["theta_computed_deg"], r["theta_ref_deg"], r["delta_pct"], r["within_2pct"], r["note"]))

    # ---- per (radius, cloud set): the number that answers the ticket's question, never pooled
    print("[THETA49] ---- in band, by patch radius and cloud set ----")
    groups = {}
    for r in rows:
        g = (r["patch_r"], r["cloud_set"])
        d = groups.setdefault(g, {"yes": 0, "NO": 0, "na": 0, "d": [], "pot": {}})
        if r["within_2pct"] == "yes":
            d["yes"] += 1
        elif r["within_2pct"] == "NO":
            d["NO"] += 1
        else:
            d["na"] += 1
        if r["delta_pct"] not in ("na", ""):
            d["d"].append(float(r["delta_pct"]))
        pd = d["pot"].setdefault(r["pot"], [0, 0])
        if r["within_2pct"] == "yes":
            pd[0] += 1
        pd[1] += 1
    for g in sorted(groups):
        d = groups[g]
        med = "na"
        if d["d"]:
            s = sorted(d["d"])
            n = len(s)
            med = "%.3f" % (s[n // 2] if n % 2 else 0.5 * (s[n // 2 - 1] + s[n // 2]))
        pots = " ".join("%s %d/%d" % (p, d["pot"][p][0], d["pot"][p][1]) for p in sorted(d["pot"]))
        print("[THETA49] R=%s cloud=%-6s in %d / out %d / no-evidence %d   median |delta|=%s%%   %s" % (
            g[0], g[1], d["yes"], d["NO"], d["na"], med, pots))

    n_in = sum(1 for r in rows if r["within_2pct"] == "yes")
    n_out = sum(1 for r in rows if r["within_2pct"] == "NO")
    n_na = sum(1 for r in rows if r["within_2pct"] == "no-evidence")
    print("[THETA49] pooled (for the record only -- read the split above): in %d / out %d / no-evidence %d of %d cells (written %s)" % (
        n_in, n_out, n_na, len(rows), args.out))
    if missing_theta:
        print("[THETA49] cells with no theta evidence: %s" % ", ".join(missing_theta))
        return 5
    return 0


if __name__ == "__main__":
    sys.exit(main())
