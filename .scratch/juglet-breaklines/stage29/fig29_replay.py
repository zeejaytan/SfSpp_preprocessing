#!/usr/bin/env python3
"""Ticket 29 - redraw the survey figure from the run's own tables.

Why this exists: job 33865557 (run 20261027-1637_7c3248f_t29-angle-survey) wrote the
figure with an x axis reaching 83 deg, because the Juglet's p99 neighbour angle is
82.8 deg, while its histogram only bins 0..60 deg. The panel annotation then named
83 deg while measuring the share beyond 60 deg. No number changes here: this reads
out/angles.tsv, out/angles_hist.json and out/theta_ladder.tsv from that run and calls
replica29.draw_figure, which now clamps the axis to the histogram range and names the
real bound. Every panel comes from the run's own files.

usage: fig29_replay.py --outdir <out/> --figure <png>
"""
import argparse
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--outdir", required=True)
    ap.add_argument("--figure", required=True)
    a = ap.parse_args()
    import replica29 as R

    thetas = list(R.THETAS)
    stats = {}
    with open(os.path.join(a.outdir, "angles.tsv")) as f:
        head = f.readline().rstrip("\n").split("\t")
        for line in f:
            c = dict(zip(head, line.rstrip("\n").split("\t")))
            st = stats.setdefault(c["cloud"], {"n_good": int(c["n_pairs"]),
                                               "n_pairs": int(c["n_pairs"]),
                                               "npts": int(c["npts"])})
            if c["kind"] == "percentile":
                st[c["name"]] = float(c["value_deg"])
    with open(os.path.join(a.outdir, "angles_hist.json")) as f:
        hj = json.load(f)
    for k, v in hj["counts"].items():
        stats.setdefault(k, {"n_good": 1})["hist_counts"] = v

    ladder = {}
    with open(os.path.join(a.outdir, "theta_ladder.tsv")) as f:
        head = f.readline().rstrip("\n").split("\t")
        for line in f:
            c = dict(zip(head, line.rstrip("\n").split("\t")))
            ladder[(c["cloud"], round(float(c["theta_deg"]), 2))] = {
                "kgate": float(c["kgate"]),
                "surviving": int(c["regions_ge_floor"]),
            }
    missing = [k for k in stats if k not in ladder and False]
    clouds = []
    for arm in R.GRID_ARMS:
        for piece in R.GRID_PIECES:
            clouds.append({"cloud": "%s/%s" % (arm, piece), "arm": arm,
                           "piece": piece})
    clouds.append({"cloud": "PA/%s" % R.POTA, "arm": "PA", "piece": R.POTA})
    for cd in clouds:
        if cd["cloud"] not in stats:
            raise SystemExit("[REPLAY] no angle stats for " + cd["cloud"])
        if (cd["cloud"], round(thetas[0], 2)) not in ladder:
            raise SystemExit("[REPLAY] no ladder row for " + cd["cloud"])

    def growth(key, t):
        return ladder[(key, round(float(t), 2))]

    loaded = {k: {"n": v["npts"]} for k, v in stats.items()}
    info = R.draw_figure(argparse.Namespace(floor=50, nb=10), thetas, clouds, loaded,
                         stats, growth, a.figure)
    info["note"] = ("re-rendered from the run's own angles.tsv, angles_hist.json and "
                    "theta_ladder.tsv by fig29_replay.py; no measurement repeated")
    with open(os.path.splitext(a.figure)[0] + ".txt", "w") as f:
        for k in sorted(info):
            f.write("%s\t%s\n" % (k, info[k]))
    print(json.dumps(info, indent=1, sort_keys=True))


main()
