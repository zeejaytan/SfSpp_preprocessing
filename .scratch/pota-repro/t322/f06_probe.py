#!/usr/bin/env python3
"""Ticket 322: why Pot F 06 loses its true axis under profile ranking (one piece, small).

usage: f06_probe.py basins_all.json profile_rank.json jugkey [stem]
Prints: cost at the reference and at its profile optimum; the shipped winner; the profile
optimum reached from every raw/normal basin representative within 15 deg of the reference;
angles between those optima and the winner (does the 15-deg dedup swallow the true one?).
"""
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from dump_basins import load_wall, piece_paths, ref_errors  # noqa: E402
from profile_probe import cost, refine, stride  # noqa: E402
from sfs_axes.io_axes import direction_angle_deg, read_axes  # noqa: E402

stem = sys.argv[4] if len(sys.argv) > 4 else "Pot_F_Piece_06"
row = [r for r in json.load(open(sys.argv[1])) if r["stem"] == stem][0]
pr = [p for p in json.load(open(sys.argv[2])) if p["stem"] == stem][0]
pot, p0, p1, relp, gtp = piece_paths(stem, sys.argv[3])
C0, C1 = load_wall(p0), load_wall(p1)
W = [stride(C0, 2500), stride(C1, 2500)]
C = np.concatenate([C0, C1], axis=1)
c = C[0:3].mean(1)
rel = read_axes(relp[0])
gt = read_axes(gtp)[:, 0] if gtp and os.path.isfile(gtp) else None
cands = [rel[:, k] for k in range(rel.shape[1])] + ([gt] if gt is not None else [])
truth = min(cands, key=lambda t: ref_errors(t, rel, gt, c)["err"])
L = row["L"]
win = np.array(pr["ranked"][0]["v"])
print("%s L=%.1f mm  n0=%d n1=%d" % (stem, L, C0.shape[1], C1.shape[1]))
print("winner: err %.1f cost %.4f" % (ref_errors(win, rel, gt, c)["err"], cost(win, W)))
print("truth : cost %.4f" % cost(truth, W))
t_opt, t_c = refine(truth, W, c, 0.1 * L)
print("truth optimum: err %.1f cost %.4f  angle to winner %.1f deg"
      % (ref_errors(t_opt, rel, gt, c)["err"], t_c, direction_angle_deg(t_opt[0:3], win[0:3])))
done_ref = False
for bi, b in enumerate(row["basins"]):
    for kind in ("raw", "ref"):
        if b[kind + "_e"]["err"] > 15 or (kind == "ref" and done_ref):
            continue
        done_ref = done_ref or kind == "ref"
        v, s = refine(np.array(b[kind]), W, c, 0.1 * L)
        print("start basin %2d %s err %.1f (size %d) -> err %.1f cost %.4f  angle to winner %.1f"
              % (bi, kind, b[kind + "_e"]["err"], b["size"], ref_errors(v, rel, gt, c)["err"], s,
                 direction_angle_deg(v[0:3], win[0:3])))
# the physical shape: radius range and height of each wall about the truth
a = truth[0:3] / np.linalg.norm(truth[0:3])
for name, X in (("S0", C0), ("S1", C1)):
    dp = X[0:3] - (truth[3:6] - (truth[3:6] @ a) * a)[:, None]
    z = a @ dp
    r = np.linalg.norm(dp - np.outer(a, z), axis=0)
    print("%s about truth: r %.1f-%.1f mm (median %.1f), height %.1f mm" % (name, r.min(), r.max(), np.median(r), np.ptp(z)))
