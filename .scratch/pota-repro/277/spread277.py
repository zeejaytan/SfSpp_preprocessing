#!/usr/bin/env python3
"""Ticket 277: measure the mesh stage's own run-to-run spread, then the pre/ post change.

The mesh stage draws unseeded points, so two runs of the same bytes are not assumed
identical: the spread is measured here from N runs of the *same* binary and used as the
envelope the changed binary must fall inside. Distances in mm, nearest-neighbour both ways.
"""
import hashlib
import json
import os
import sys

import numpy as np
from scipy.spatial import cKDTree

SURFS = ("Surface_0", "Surface_1")


def md5(path):
    h = hashlib.md5()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def load(path):
    a = np.loadtxt(path, usecols=(0, 1, 2))
    return a.reshape(-1, 3)


def nn(a, b):
    """nearest-neighbour distance of every point of a to the cloud b, both ways."""
    d_fwd = cKDTree(b).query(a, k=1, workers=-1)[0]
    d_bwd = cKDTree(a).query(b, k=1, workers=-1)[0]
    return {
        "med_fwd": round(float(np.median(d_fwd)), 6),
        "p99_fwd": round(float(np.percentile(d_fwd, 99)), 6),
        "max_fwd": round(float(d_fwd.max()), 6),
        "med_bwd": round(float(np.median(d_bwd)), 6),
        "p99_bwd": round(float(np.percentile(d_bwd, 99)), 6),
        "max_bwd": round(float(d_bwd.max()), 6),
    }


def envelope(pairs):
    """worst value of each metric over a set of comparisons."""
    if not pairs:
        return {}
    out = {}
    for k in pairs[0]:
        out[k] = round(max(p[k] for p in pairs), 6)
    return out


def inside(cross, env):
    """cross fits inside env if no metric exceeds it (spread is what the piece does)."""
    return all(cross[k] <= env[k] + 1e-9 for k in env)


def main():
    run = sys.argv[1]
    reps = int(sys.argv[2])
    geom = os.path.join(run, "out", "geom")
    tags = [t for t in os.listdir(geom) if os.path.isdir(os.path.join(geom, t))]
    pre = sorted([t for t in tags if t.startswith("pre_")])
    post = sorted([t for t in tags if t.startswith("post_")])
    result = {
        "run_dir": run,
        "reps": reps,
        "pre_tags": pre,
        "post_tags": post,
        "surfaces": {},
        "verdict": "inside",
    }

    for s in SURFS:
        rec = {"files": {}, "identical_across_all_runs": True}
        clouds = {}
        for t in pre + post:
            p = os.path.join(geom, t, s + ".xyz")
            if not os.path.exists(p):
                rec["files"][t] = None
                continue
            cloud = load(p)
            clouds[t] = cloud
            rec["files"][t] = {"md5": md5(p), "points": int(cloud.shape[0])}

        md5s = set(v["md5"] for v in rec["files"].values() if v)
        rec["identical_across_all_runs"] = len(md5s) == 1
        rec["distinct_md5"] = len(md5s)
        rec["points"] = sorted(set(v["points"] for v in rec["files"].values() if v))

        def pairs_within(tagsA):
            out = []
            for i in range(len(tagsA)):
                for j in range(i + 1, len(tagsA)):
                    if tagsA[i] in clouds and tagsA[j] in clouds:
                        out.append((tagsA[i], tagsA[j], nn(clouds[tagsA[i]], clouds[tagsA[j]])))
            return out

        pw_pre = pairs_within(pre)
        pw_post = pairs_within(post)
        cross = []
        for a in pre:
            for b in post:
                if a in clouds and b in clouds:
                    cross.append((a, b, nn(clouds[a], clouds[b])))

        env_pre = envelope([d for _, _, d in pw_pre])
        env_post = envelope([d for _, _, d in pw_post])
        env_all = envelope([d for _, _, d in pw_pre + pw_post])
        cross_worst = envelope([d for _, _, d in cross])
        rec["spread_pre"] = env_pre
        rec["spread_post"] = env_post
        rec["spread_both_binaries"] = env_all
        rec["cross_pre_vs_post"] = cross_worst
        rec["cross_max_row"] = max(cross, key=lambda r: r[2]["max_fwd"])[:2] if cross else None
        rec["within"] = inside(cross_worst, env_all) if cross_worst else None
        if rec["within"] is False:
            result["verdict"] = "outside"
        result["surfaces"][s] = rec

    out_json = os.path.join(run, "out", "spread.json")
    with open(out_json, "w") as f:
        json.dump(result, f, indent=2, sort_keys=True)
    with open(os.path.join(run, "out", "spread.tsv"), "w") as f:
        f.write("surface\tpoints\tdistinct_md5\tspread_pre_max\tspread_post_max\t"
                "cross_max\twithin\n")
        for s in SURFS:
            r = result["surfaces"][s]
            f.write("%s\t%s\t%s\t%s\t%s\t%s\t%s\n" % (
                s, r["points"], r["distinct_md5"],
                r["spread_pre"].get("max_fwd"), r["spread_post"].get("max_fwd"),
                r["cross_pre_vs_post"].get("max_fwd"), r["within"]))
    print("verdict: " + result["verdict"])
    for s in SURFS:
        r = result["surfaces"][s]
        print(s, "points=", r["points"], "distinct_md5=", r["distinct_md5"])
        print("  spread_pre ", r["spread_pre"])
        print("  spread_post", r["spread_post"])
        print("  cross      ", r["cross_pre_vs_post"], "within=", r["within"])


if __name__ == "__main__":
    main()
