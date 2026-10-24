#!/usr/bin/env python3
"""Ticket 287 item 2: is our after-run export the same closed loop as the parked 275 selector's?

The start dot decides where the export begins, so a different start rotates the point order.
This compares each lane's exported breakline against the p275 selector run's export two ways:
  ordered  -> max pointwise distance when both keep the same start (0 means identical export)
  as sets  -> max nearest-neighbour distance (0..mm; small means the same loop, rotated or not)
and prints the first point of each export, which IS the start dot.
"""
import os, sys
import numpy as np

OURS = os.environ["OURS"]
P275 = os.environ["P275"]

def readpts(p):
    pts, started = [], False
    with open(p, "r", errors="ignore") as f:
        for line in f:
            if not started:
                if line.startswith("DATA"):
                    started = True
                continue
            s = line.split()
            if len(s) >= 3:
                pts.append((float(s[0]), float(s[1]), float(s[2])))
    return np.asarray(pts, dtype=float)

def nn_max(a, b):
    d = np.linalg.norm(a[:, None, :] - b[None, :, :], axis=2)
    return float(d.min(axis=1).max()), float(d.min(axis=1).mean())

LANES = [("C01", "Pot_C_Piece_01", 0), ("C01", "Pot_C_Piece_01", 1),
         ("J01", "Pot_J_Piece_01", 0), ("J01", "Pot_J_Piece_01", 1)]
print("The p275 run holds two selector arms per lane: _247 (selector in the vote-247 host) and")
print("_full (selector in the full walk). Ours changes the full walk's start dot, so _full is the")
print("arm that state should match; _247 is printed too because the ticket's C01 Bl1 reference")
print("(226 points) is the one the _247 arm carries.")
print("")
print("our lane is always our after arm: out/<lab>_after/")
for arm in ("full", "247"):
  print("== p275 arm: %s ==" % arm)
  print("lane st  n_ours n_275  ordered_max  set_max  set_mean   seed_ours(x,y,z)                seed_275(x,y,z)")
  for lab, piece, st in LANES:
    f_ours = os.path.join(OURS, lab + "_after", "%s_Breakline_%d.pcd" % (piece, st))
    f_275 = os.path.join(P275, lab + "_" + arm, "%s_Breakline_%d.pcd" % (piece, st))
    if not (os.path.exists(f_ours) and os.path.exists(f_275)):
        print("%s Bl%d MISSING (%s | %s)" % (lab, st, os.path.exists(f_ours), os.path.exists(f_275)))
        continue
    a, b = readpts(f_ours), readpts(f_275)
    om = float(np.abs(a - b).max()) if a.shape == b.shape else float("nan")
    sm, mn = nn_max(a, b)
    sa = " ".join("%.3f" % v for v in a[0])
    sb = " ".join("%.3f" % v for v in b[0])
    print("%s Bl%d  %5d %5d  %11.6f  %7.4f  %7.4f   %-30s  %s" % (lab, st, len(a), len(b), om, sm, mn, sa, sb))