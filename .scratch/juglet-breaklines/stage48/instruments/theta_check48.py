#!/usr/bin/env python3
"""ticket 48 PART 1 -- theta_check48: the [GROWTH-45] formula theta of every cell against the
ticket-43 prediction, at the ~2% band the ticket names.

REPORT ONLY.  A miss is a RESULT ("report where it lands and STOP -- no tuning, no re-runs"),
never a failure exit: this script exits 0 with the table even when every piece lands outside
the band.  It exits nonzero only when it cannot produce the table at all (missing/unreadable
inputs, a cell with no theta evidence), because then there is nothing to report.

columns: pot piece arm theta_computed_deg theta_ref_deg delta_abs delta_pct within_2pct note
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


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cells", required=True, help="pipeline_cells.tsv of the t48 run")
    ap.add_argument("--ref", required=True, help="thetas48.tsv (k43 predictions, pot/piece/theta_ref_deg)")
    ap.add_argument("--out", required=True, help="theta_check48.tsv to write")
    ap.add_argument("--band-pct", type=float, default=2.0, help="band width in %% of ref (default 2.0)")
    args = ap.parse_args()

    try:
        cells = read_tsv(args.cells)
    except OSError as e:
        print("[THETA48] FAIL cannot read cells %s: %s" % (args.cells, e)); return 4
    try:
        refs = {(r["pot"], r["piece"]): r["theta_ref_deg"] for r in read_tsv(args.ref)}
    except OSError as e:
        print("[THETA48] FAIL cannot read ref %s: %s" % (args.ref, e)); return 4

    rows = []
    missing_theta = []
    for c in cells:
        key = (c["pot"], c["piece"])
        ref = refs.get(key)
        got = (c.get("theta_computed_deg") or "").strip()
        note = ""
        if ref is None:
            note = "no k43 reference row for this piece"
        if not got:
            note = (note + "; " if note else "") + "no GROWTH-45 theta in the cell"
            missing_theta.append("%s/%s" % key)
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
            "theta_computed_deg": got or "na", "theta_ref_deg": ref if ref is not None else "na",
            "delta_abs": d_abs, "delta_pct": d_pct, "within_2pct": within, "note": note,
        })

    fields = ["pot", "piece", "arm", "theta_computed_deg", "theta_ref_deg",
              "delta_abs", "delta_pct", "within_2pct", "note"]
    with open(args.out, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=fields, delimiter="\t", lineterminator="\n")
        w.writeheader()
        w.writerows(rows)

    print("[THETA48] theta vs k43 at %.1f%% band -- REPORT ONLY, misses are results" % args.band_pct)
    for r in rows:
        print("[THETA48] %s/%s arm=%s computed=%s ref=%s d=%s%% within=%s %s" % (
            r["pot"], r["piece"], r["arm"], r["theta_computed_deg"], r["theta_ref_deg"],
            r["delta_pct"], r["within_2pct"], r["note"]))
    n_in = sum(1 for r in rows if r["within_2pct"] == "yes")
    n_out = sum(1 for r in rows if r["within_2pct"] == "NO")
    n_na = sum(1 for r in rows if r["within_2pct"] == "no-evidence")
    print("[THETA48] in-band %d / out %d / no-evidence %d of %d cells (written %s)" % (
        n_in, n_out, n_na, len(rows), args.out))
    if missing_theta:
        print("[THETA48] cells with no theta evidence: %s" % ", ".join(missing_theta))
        return 5
    return 0


if __name__ == "__main__":
    sys.exit(main())
