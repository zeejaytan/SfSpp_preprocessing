#!/usr/bin/env python3
"""p293_crosspair.py -- pair every one of our lines with every one of the authors' lines.

The lane score pairs our Breakline_k with their Breakline_k. On Pot I 25 the census puts our
Bl0 on kept cluster c0 and their Bl0 on c1 (and the mirror on Bl1), so lane k compares two
different faces; this prints the whole 2x2 pairing matrix for the Phase A pieces so the pairing
that is geometrically sane can be named instead of assumed. Our dots come from the census
per-dot tables (out/census/<piece>_Bl<k>.assign.tsv, side ours), theirs from the frozen corpus.

Usage: p293_crosspair.py <run dir>
Writes: <run>/out/crosspair.tsv
"""
import os, sys
import numpy as np
from scipy.spatial import cKDTree

BAR = 2.0

def read_pcd_xyz(path):
    fields, data, n = None, None, 0
    with open(path, "rb") as fh:
        while True:
            line = fh.readline()
            if not line:
                break
            s = line.decode("ascii", "replace").strip()
            if s.upper().startswith("FIELDS"):
                fields = s.split()[1:]
            elif s.upper().startswith("DATA"):
                mode = s.split()[1].lower()
                break
        if mode == "ascii":
            arr = np.loadtxt(fh, ndmin=2)
        else:
            arr = np.frombuffer(fh.read(), dtype=np.float32).reshape(-1, len(fields))
    idx = [fields.index(a) for a in ("x", "y", "z")]
    return np.asarray(arr, dtype=float)[:, idx]

def read_ours(run, piece, lane):
    p = os.path.join(run, "out", "census", "%s_Bl%d.assign.tsv" % (piece, lane))
    if not os.path.exists(p):
        return None
    pts = []
    with open(p) as fh:
        next(fh)
        for line in fh:
            f = line.split("\t")
            if f[0] != "ours":
                continue
            pts.append([float(f[2]), float(f[3]), float(f[4])])
    return np.asarray(pts, dtype=float)

def score(ours, auth):
    d_o = cKDTree(auth).query(ours)[0]
    d_a = cKDTree(ours).query(auth)[0]
    return (float(np.median(d_o)), 100.0 * float((d_o < BAR).mean()),
            100.0 * float((d_a < BAR).mean()), float(np.max(d_o)))

def main(run):
    corpus = "/data/gpfs/projects/punim2657/sfs_main/original_samples/SfS_pp"
    rows = []
    for piece in ("Pot_C_Piece_03", "Pot_I_Piece_25"):
        for k in (0, 1):
            ours = read_ours(run, piece, k)
            if ours is None:
                print("no per-dot table for %s Bl%d (not a lane the renderer drew)" % (piece, k))
                continue
            for j in (0, 1):
                auth = read_pcd_xyz(os.path.join(corpus, "Breaklines", "%s_Breakline_%d.pcd" % (piece, j)))
                med, cov_o, cov_a, mx = score(ours, auth)
                rows.append("%s\t%d\t%d\t%d\t%d\t%.3f\t%.2f\t%.2f\t%.3f\t%s" % (
                    piece, k, j, len(ours), len(auth), med, cov_o, cov_a, mx,
                    "SAME-INDEX" if k == j else "cross"))
    hdr = "piece\tours_lane\tauthors_lane\tn_ours\tn_auth\tmedian\tcov_ours\tcov_auth\tmax_ours\tpairing"
    out = os.path.join(run, "out", "crosspair.tsv")
    with open(out, "w") as fh:
        fh.write(hdr + "\n")
        fh.write("\n".join(rows) + "\n")
    print(hdr)
    print("\n".join(rows))
    print("wrote %s" % out)

if __name__ == "__main__":
    main(sys.argv[1])
