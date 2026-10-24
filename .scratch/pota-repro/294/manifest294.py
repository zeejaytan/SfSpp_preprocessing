#!/usr/bin/env python3
"""manifest294.py -- join the fresh run, the ticket-292 baseline and the per-piece metadata into
out/manifest.json, the file p294_render.py reads.

Usage: manifest294.py <run dir> <292 run dir>
"""
import json
import os
import sys

RUN, PREV = sys.argv[1], sys.argv[2]
CORP = "/data/gpfs/projects/punim2657/sfs_main/original_samples/SfS_pp"
FLAG_MED = 0.20
FLAG_COV = 3.0


def rows(path):
    out = []
    for line in open(path):
        line = line.rstrip("\n")
        if line:
            out.append(line.split("\t"))
    return out


build = json.load(open(os.path.join(RUN, "out", "build.json")))

fresh = {}
for r in rows(os.path.join(RUN, "out", "lanes_fresh.tsv")):
    fresh[(r[1], r[2])] = r

base = {}
hdr = None
for r in rows(os.path.join(PREV, "out", "lanes.tsv")):
    if hdr is None:
        hdr = r
        continue
    d = dict(zip(hdr, r))
    base[(d["piece"], d["lane"])] = d

meta = {}
for r in rows(os.path.join(RUN, "out", "pieces_run.tsv")):
    meta[r[0]] = {"pot": r[1], "theta": r[2], "mesh_obj": r[3], "surf0": r[4], "surf1": r[5]}

cls = {}
for r in rows(os.path.join(RUN, "out", "classify.tsv")):
    cls[r[0]] = {"classify": r[1], "swapped": r[2], "theta": r[3]}

lanes = []
problems = 0
for w in rows(os.path.join(RUN, "out", "lanes_wanted.tsv")):
    piece, lane = w[0], w[1]
    f = fresh.get((piece, lane))
    d = base.get((piece, lane))
    m = meta.get(piece)
    c = cls.get(piece)
    if f is None or d is None or m is None or c is None:
        print("MISSING %s lane %s: fresh=%s base=%s meta=%s classify=%s" % (piece, lane, f is not None, d is not None, m is not None, c is not None))
        problems += 1
        continue
    med = float(f[5])
    co = float(f[6])
    ca = float(f[7])
    m292 = float(d["median"])
    co292 = float(d["cov_ours"])
    ca292 = float(d["cov_auth"])
    d_med = med - m292
    d_cov = co - co292
    flag = ""
    if abs(d_med) > FLAG_MED or abs(d_cov) > FLAG_COV:
        flag = "median %+.3f mm and cov_ours %+.2f pp against the ticket-292 row, i.e. more than this run may move by draw alone" % (d_med, d_cov)
    lanes.append({
        "pot": m["pot"],
        "piece": piece,
        "lane": lane,
        "our_pcd": os.path.join(RUN, "out", "geom", "%s.Bl%s.pcd" % (piece, lane)),
        "auth_pcd": os.path.join(CORP, "Breaklines", "%s_Breakline_%s.pcd" % (piece, lane)),
        "mesh_obj": m["mesh_obj"],
        "surf0": m["surf0"],
        "surf1": m["surf1"],
        "n_ours": int(f[3]),
        "n_auth": int(f[4]),
        "median": med,
        "cov_ours": co,
        "cov_auth": ca,
        "jumps": int(f[8]),
        "max_step": float(f[9]),
        "len_ours": float(f[10]),
        "len_auth": float(f[11]),
        "n292": d["n_ours"],
        "n292a": d["n_auth"],
        "median292": "%.3f" % m292,
        "cov292": "%.2f" % co292,
        "cov292a": "%.2f" % ca292,
        "jumps292": d["jumps"],
        "d_median": d_med,
        "d_cov": d_cov,
        "flag": flag,
        "commit": build["commit"],
        "edge_md5": build["edge_md5"],
        "mesh_md5": build["mesh_md5"],
        "theta": m["theta"],
        "classify": c["classify"] + " ; " + c["swapped"],
    })

man = {"run": RUN, "prev": PREV, "commit": build["commit"], "jobid": build.get("jobid", ""),
       "edge_md5": build["edge_md5"], "mesh_md5": build["mesh_md5"],
       "flag_rule": "flag when |d median| > %.2f mm or |d cov_ours| > %.1f pp" % (FLAG_MED, FLAG_COV),
       "lanes": lanes}
json.dump(man, open(os.path.join(RUN, "out", "manifest.json"), "w"), indent=1)
print("lanes=%d problems=%d flagged=%d" % (len(lanes), problems, sum(1 for e in lanes if e["flag"])))
for e in lanes:
    print("%s Bl%s fresh %d/%.3f/%.2f/%.2f/%d  292 %s/%s/%s/%s/%s  d_med %+.3f  d_cov %+.2f  %s" % (
        e["piece"], e["lane"], e["n_ours"], e["median"], e["cov_ours"], e["cov_auth"], e["jumps"],
        e["n292"], e["median292"], e["cov292"], e["cov292a"], e["jumps292"],
        e["d_median"], e["d_cov"], "FLAG" if e["flag"] else ""))
sys.exit(1 if problems else 0)
