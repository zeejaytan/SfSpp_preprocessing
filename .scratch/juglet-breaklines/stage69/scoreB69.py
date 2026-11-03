#!/usr/bin/env python3
"""scoreB69.py -- ticket 69 Part B: score every emitted lane, both densities, against the
authors' own breakline.

Reads a ticket-69 preprocessing run dir (out_pota/out_potc/out_potd/out_potj, each with
geom18/ and geom09/) and, for every piece and lane, scores geom18/<P>.Bl<k> and
geom09/<P>.Bl<k> against $CORP/Breaklines/<P>_Breakline_<k>.pcd with score292.py (the
reference scorer of .scratch/pota-repro/292/, whose selftest passes).

Bar (ticket 69): median <= 2.0 mm AND coverage >= 90 %. A lane is "at bar" or not; the
question is the DELTA, so every lane is reported with both arms side by side and a
direction: better / worse / same-at-bar / same-out.

Exclusions are applied and listed SEPARATELY, never silently dropped:
  Pot C 01 interior Bl0  (corpus gap; measures the input, not the method)
  Pot C 03 exterior Bl1  (the authors' line is not a break edge there)
  Pot J 09 both lanes    (the authors' lines on this piece are wrong)

usage: scoreB69.py --run <run dir> --corpus <SfS_pp> --out <dir> [--arms 18,09]
"""
import argparse, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
SCORER = os.path.join(HERE, "..", "..", "pota-repro", "292", "score292.py")
SCORER = os.path.abspath(SCORER)
sys.path.insert(0, os.path.dirname(SCORER))
import score292  # noqa: E402

EXCLUDE = {
    ("Pot_C_Piece_01", 0): "corpus gap: interior Bl0 measures the input, not the method (AGENTS.md)",
    ("Pot_C_Piece_03", 1): "authors' Bl1 is the rim of their own small face, not a break edge",
    ("Pot_J_Piece_09", 0): "authors' breaklines on this piece are wrong (ticket 289)",
    ("Pot_J_Piece_09", 1): "authors' breaklines on this piece are wrong (ticket 289)",
}

CELLS = [("Pot_A", "out_pota"), ("Pot_C", "out_potc"), ("Pot_D", "out_potd"), ("Pot_J", "out_potj")]


def read_geom(d):
    """piece -> {lane: path} for every <P>.Bl<k> in the geom dir."""
    out = {}
    if not os.path.isdir(d):
        return out
    for f in sorted(os.listdir(d)):
        if ".Bl" not in f:
            continue
        stem, _, k = f.rpartition(".Bl")
        if not k.isdigit():
            continue
        out.setdefault(stem, {})[int(k)] = os.path.join(d, f)
    return out


def bar_of(row):
    return "yes" if (row["median"] <= 2.0 and row["cov_ours"] >= 90.0) else "no"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", required=True)
    ap.add_argument("--corpus", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--arms", default="18,09")
    a = ap.parse_args()
    arms = [x.strip() for x in a.arms.split(",") if x.strip()]
    os.makedirs(a.out, exist_ok=True)

    rows, excluded = [], []
    for pot, cell in CELLS:
        geom = {g: read_geom(os.path.join(a.run, cell, "geom" + g)) for g in arms}
        pieces = sorted(set().union(*[set(v) for v in geom.values()]))
        for P in pieces:
            for k in (0, 1):
                auth = os.path.join(a.corpus, "Breaklines", "%s_Breakline_%d.pcd" % (P, k))
                if not os.path.isfile(auth):
                    excluded.append((pot, P, k, "no authors' line at " + auth))
                    continue
                if (P, k) in EXCLUDE:
                    excluded.append((pot, P, k, EXCLUDE[(P, k)]))
                    continue
                rec = {"pot": pot, "piece": P, "lane": k}
                ok = True
                for g in arms:
                    f = geom[g].get(P, {}).get(k)
                    if not f or not os.path.isfile(f):
                        rec["arm" + g] = None
                        ok = False
                        continue
                    try:
                        r = score292.score(f, auth)
                    except Exception as e:  # noqa: BLE001
                        rec["arm" + g] = None
                        rec.setdefault("err", []).append("arm%s: %s" % (g, e))
                        ok = False
                        continue
                    rec["arm" + g] = {
                        "n_ours": r[0], "n_auth": r[1], "median": r[2], "cov_ours": r[3],
                        "cov_auth": r[4], "jumps": r[5], "max_step": r[6],
                        "len_ours": r[7], "len_auth": r[8], "at_bar": r[9],
                    }
                if not ok:
                    excluded.append((pot, P, k, "a lane file is missing: " + str(rec.get("err", ""))))
                    continue
                rows.append(rec)

    cols = ["pot", "piece", "lane"]
    for g in arms:
        cols += ["dots" + g, "med" + g, "cov" + g, "bar" + g]
    cols += ["delta_med", "direction"]
    tsv = os.path.join(a.out, "lanes.tsv")
    with open(tsv, "w") as fh:
        fh.write("\t".join(cols) + "\n")
        for r in rows:
            vals = [r["pot"], r["piece"], str(r["lane"])]
            for g in arms:
                d = r["arm" + g]
                vals += [str(d["n_ours"]), "%.3f" % d["median"], "%.1f" % d["cov_ours"], bar_of(d)]
            if len(arms) >= 2:
                a0, a1 = r["arm" + arms[0]], r["arm" + arms[1]]
                dm = a1["median"] - a0["median"]
                b0, b1 = bar_of(a0) == "yes", bar_of(a1) == "yes"
                if b0 and not b1:
                    d = "CROSSED_OUT"
                elif b1 and not b0:
                    d = "CROSSED_IN"
                elif b0 and b1:
                    d = "both_at_bar"
                else:
                    d = "both_out"
                vals += ["%+.3f" % dm, d]
            fh.write("\t".join(vals) + "\n")

    with open(os.path.join(a.out, "excluded.tsv"), "w") as fh:
        fh.write("pot\tpiece\tlane\treason\n")
        for e in excluded:
            fh.write("%s\t%s\t%d\t%s\n" % e)

    # per arm, per pot: at-bar / measured, and the median-distance distribution
    with open(os.path.join(a.out, "per_arm.tsv"), "w") as fh:
        fh.write("arm\tpot\tlanes\tat_bar\tmed_median\tmed_p90\tcov_median\tcov_p10\n")
        for g in arms:
            for pot in ["ALL"] + [c[0] for c in CELLS]:
                sel = [r for r in rows if pot == "ALL" or r["pot"] == pot]
                if not sel:
                    continue
                meds = sorted(r["arm" + g]["median"] for r in sel)
                covs = sorted(r["arm" + g]["cov_ours"] for r in sel)
                nb = sum(1 for r in sel if bar_of(r["arm" + g]) == "yes")
                p90 = meds[min(len(meds) - 1, int(round(0.9 * (len(meds) - 1))))]
                p10 = covs[min(len(covs) - 1, int(round(0.1 * (len(covs) - 1))))]
                fh.write("%s\t%s\t%d\t%d\t%.3f\t%.3f\t%.1f\t%.1f\n"
                         % (g, pot, len(sel), nb, meds[len(meds) // 2], p90,
                            covs[len(covs) // 2], p10))

    with open(os.path.join(a.out, "deltas.tsv"), "w") as fh:
        fh.write("direction\tlanes\n")
        for d in ["CROSSED_OUT", "CROSSED_IN", "both_at_bar", "both_out"]:
            fh.write("%s\t%d\n" % (d, sum(1 for r in rows if _dir(r, arms) == d)))

    print("scored %d lanes, excluded %d" % (len(rows), len(excluded)))
    for g in arms:
        nb = sum(1 for r in rows if bar_of(r["arm" + g]) == "yes")
        print("arm %s: %d/%d lanes at bar" % (g, nb, len(rows)))
    for d in ["CROSSED_OUT", "CROSSED_IN", "both_at_bar", "both_out"]:
        print("  %-12s %d" % (d, sum(1 for r in rows if _dir(r, arms) == d)))
    print("wrote", tsv)


def _dir(r, arms):
    if len(arms) < 2:
        return "n/a"
    b0 = bar_of(r["arm" + arms[0]]) == "yes"
    b1 = bar_of(r["arm" + arms[1]]) == "yes"
    if b0 and not b1:
        return "CROSSED_OUT"
    if b1 and not b0:
        return "CROSSED_IN"
    return "both_at_bar" if b0 else "both_out"


if __name__ == "__main__":
    main()
