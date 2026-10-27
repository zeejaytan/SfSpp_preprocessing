#!/usr/bin/env python3
"""Lead's independent re-measurement for ticket 26.

Written from scratch so it shares no code with the worker's measure_pairs26.py:
own PLY reader, brute-force nearest neighbour (chunked) instead of a KD-tree.
Same statistic it is checking: for each Surface_1 point, step to the nearest
Surface_0 point, split into the component ALONG that point's own normal and the
component ACROSS it, plus the 1-micron coincidence share.
"""
import sys, os
import numpy as np

def load(path):
    raw = open(path, "rb").read()
    e = raw.find(b"end_header")
    if e < 0:
        raise SystemExit("no end_header: " + path)
    e = raw.find(b"\n", e) + 1
    head = raw[:e].decode("ascii", "replace").splitlines()
    n = None
    props = []
    inv = False
    for line in head:
        t = line.split()
        if not t:
            continue
        if t[0] == "element":
            inv = len(t) > 2 and t[1] == "vertex"
            if inv:
                n = int(t[2])
        elif t[0] == "property" and inv:
            props.append(t[-1])
    lines = raw[e:].decode("ascii", "replace").split("\n")[:n]
    arr = np.fromstring(" ".join(lines), sep=" ") if hasattr(np, "fromstring") else None
    if arr is None or arr.size != n * len(props):
        arr = np.array([float(v) for ln in lines for v in ln.split()], dtype=np.float64)
    arr = arr.reshape(n, len(props))
    ix = {p: i for i, p in enumerate(props)}
    xyz = arr[:, [ix["x"], ix["y"], ix["z"]]].astype(np.float64)
    nrm = arr[:, [ix["nx"], ix["ny"], ix["nz"]]].astype(np.float64)
    ln = np.linalg.norm(nrm, axis=1)
    ln[ln == 0] = 1.0
    return xyz, nrm / ln[:, None]

def stat(p0, n0, p1, block=400):
    best_d = np.empty(p1.shape[0])
    best_i = np.empty(p1.shape[0], dtype=np.int64)
    for s in range(0, p1.shape[0], block):
        c = p1[s:s + block]
        d2 = ((c[:, None, :] - p0[None, :, :]) ** 2).sum(-1)
        best_i[s:s + block] = d2.argmin(1)
        best_d[s:s + block] = np.sqrt(d2.min(1))
    nn = n0[best_i]
    v = p1 - p0[best_i]
    a = (v * nn).sum(1)
    across = np.linalg.norm(v - a[:, None] * nn, axis=1)
    return dict(n0=p0.shape[0], n1=p1.shape[0],
                along=float(np.median(np.abs(a))), along_p90=float(np.percentile(np.abs(a), 90)),
                across=float(np.median(across)), across_p90=float(np.percentile(across, 90)),
                coin=float((best_d <= 1e-3).mean()), nn=float(np.median(best_d)))

def run(root, tag, pot, piece):
    d = os.path.join(root, tag, pot, piece, "surfaces")
    p0, n0 = load(os.path.join(d, piece + "_Surface_0.ply"))
    p1, n1 = load(os.path.join(d, piece + "_Surface_1.ply"))
    s = stat(p0, n0, p1)
    print("%s\t%s\t%s\t%d\t%d\t%.6f\t%.6f\t%.6f\t%.6f\t%.6f\t%.6f" % (
        tag, pot, piece, s["n0"], s["n1"], s["along"], s["across"], s["coin"], s["nn"],
        s["along_p90"], s["across_p90"]), flush=True)

if __name__ == "__main__":
    root = sys.argv[1]
    print("tag\tpot\tpiece\tn0\tn1\tmed_along_mm\tmed_across_mm\tcoincidence\tmed_nn_mm\tp90_along\tp90_across")
    for spec in sys.argv[2:]:
        tag, pot, piece = spec.split(":")
        run(root, tag, pot, piece)
