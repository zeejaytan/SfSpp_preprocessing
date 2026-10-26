#!/usr/bin/env python3
"""ticket 24: choose arm E's radius setting by a rule fixed before the run is read.

Rule (mechanical, not a judgement of which arm is better):
  for each candidate radius arm, take each Juglet piece's LAST normals call, keep that call's
  median absolute mesh-normal angle and its p90; pool the nine pieces by taking the median of
  the nine medians (and of the nine p90s); select the candidate with the lowest pooled median,
  tie broken by the lowest pooled p90, tie broken by the order the candidates were given.
  Report every candidate's numbers so the choice can be checked against them.

usage: pick_arm_e24.py <cells_root> <arms_env.tsv> <out_arm_e.txt> <cand> [<cand> ...]
       arms_env.tsv rows: tag<TAB>env
"""
import os
import statistics
import sys

JUGLET = ["Juglet_Piece_%d" % i for i in range(1, 10)]


def last_call(path):
    rows = []
    with open(path) as fh:
        header = fh.readline().rstrip("\n").split("\t")
        for line in fh:
            f = line.rstrip("\n").split("\t")
            rows.append(dict(zip(header, f)))
    if not rows:
        return None
    rows.sort(key=lambda r: int(r["call"]))
    return rows[-1]


def main():
    root, envfile, outpath = sys.argv[1], sys.argv[2], sys.argv[3]
    cands = sys.argv[4:]
    envs = {}
    with open(envfile) as fh:
        for line in fh:
            f = line.rstrip("\n").split("\t")
            if len(f) >= 2:
                envs[f[0]] = f[1]
    scored = []
    for tag in cands:
        meds, p90s, missing = [], [], []
        for p in JUGLET:
            f = os.path.join(root, tag, "Juglet", p, "angles24.tsv")
            if not os.path.exists(f):
                missing.append(p)
                continue
            r = last_call(f)
            if r is None or r.get("med_abs_deg", "NA") == "NA":
                missing.append(p)
                continue
            meds.append(float(r["med_abs_deg"]))
            p90s.append(float(r["p90_abs_deg"]))
        if missing or len(meds) != 9:
            print("[ARM-E] %s not eligible: %d/9 pieces measured, missing %s"
                  % (tag, len(meds), ",".join(missing)), flush=True)
            continue
        scored.append((tag, statistics.median(meds), statistics.median(p90s)))
        print("[ARM-E] %s pooled_med=%.4f pooled_p90=%.4f per_piece_med=%s"
              % (tag, scored[-1][1], scored[-1][2],
                 ",".join("%.2f" % m for m in meds)), flush=True)
    if not scored:
        print("[ARM-E] FATAL no candidate measured 9/9 Juglet pieces", flush=True)
        open(outpath, "w").write("none\tnone\tNA\tNA\n")
        return 1
    order = {t: i for i, t in enumerate(cands)}
    scored.sort(key=lambda x: (round(x[1], 6), round(x[2], 6), order[x[0]]))
    tag, pm, pp = scored[0]
    line = "%s\t%s\t%.4f\t%.4f" % (tag, envs.get(tag, ""), pm, pp)
    open(outpath, "w").write(line + "\n")
    print("[ARM-E] selected=%s pooled_med=%.4f pooled_p90=%.4f rule=lowest-median-of-nine-"
          "piece-last-call-median-abs-mesh-angle env=%s" % (tag, pm, pp, envs.get(tag, "")),
          flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
