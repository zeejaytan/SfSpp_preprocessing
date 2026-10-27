#!/usr/bin/env python3
"""ticket 26 -- the corrected ruler on every cell that wrote two surfaces.

For each Surface_1 point: take its nearest Surface_0 point, and split that step into
  - the component ALONG that Surface_0 point's own normal  (through the wall),
  - the component ACROSS it                                (tangential / slippage),
plus the coincidence share at 1 micron.

The older mean-normal dot test is retired: it passed two coplanar patches of one shell,
0.230 mm apart. med_off_mm_old is printed only so the retired number can be compared; it is
NOT a statistic of this ticket.

usage:
  measure_pairs26.py --selftest
  measure_pairs26.py <cellroot> [cells26.tsv]   -> writes <cellroot>/measure26.tsv
"""
import sys, os, glob
import numpy as np
from scipy.spatial import cKDTree

COINCIDENCE_MM = 1e-3


def load_ply(path):
    """PCL ASCII PLY: parse the header, return (xyz float64 (n,3), normals float64 (n,3))."""
    with open(path, "rb") as fh:
        raw = fh.read()
    end = raw.find(b"end_header")
    if end < 0:
        raise ValueError("no end_header in " + path)
    end = raw.find(b"\n", end) + 1
    header = raw[:end].decode("ascii", "replace")
    body = raw[end:].decode("ascii", "replace")
    n = None
    props = []
    in_vertex = False
    for line in header.splitlines():
        t = line.split()
        if not t:
            continue
        if t[0] == "element":
            in_vertex = len(t) >= 3 and t[1] == "vertex"
            if in_vertex:
                n = int(t[2])
        elif t[0] == "property" and in_vertex and len(t) >= 3:
            props.append(t[-1])
    if n is None or not props:
        raise ValueError("no vertex element in " + path)
    toks = body.split()
    want = n * len(props)
    if len(toks) < want:
        raise ValueError("short body in " + path + ": %d tokens for %d" % (len(toks), want))
    arr = np.asarray(toks[:want], dtype=np.float64).reshape(n, len(props))
    idx = {name: i for i, name in enumerate(props)}
    xyz = np.column_stack([arr[:, idx["x"]], arr[:, idx["y"]], arr[:, idx["z"]]])
    for cand in (("normal_x", "normal_y", "normal_z"), ("nx", "ny", "nz")):
        if all(c in idx for c in cand):
            nrm = np.column_stack([arr[:, idx[c]] for c in cand])
            break
    else:
        raise ValueError("no normals in " + path + " properties=" + ",".join(props))
    ok = np.isfinite(xyz).all(axis=1) & np.isfinite(nrm).all(axis=1)
    return xyz[ok], nrm[ok]


def unit(v):
    nn = np.linalg.norm(v, axis=1)
    nn[nn == 0] = 1.0
    return v / nn[:, None]


def pair_stats(p0, n0, p1, n1):
    """p0/n0 = Surface_0 points and their own normals; p1/n1 = Surface_1."""
    t0 = cKDTree(p0)
    d, idx = t0.query(p1, k=1)
    nn0 = unit(n0[idx])
    v = p1 - p0[idx]
    along_signed = np.einsum("ij,ij->i", v, nn0)
    along = np.abs(along_signed)
    across = np.linalg.norm(v - along_signed[:, None] * nn0, axis=1)
    old = np.abs(along_signed)  # placeholder, overwritten below by the retired statistic
    return {
        "n0": int(p0.shape[0]),
        "n1": int(p1.shape[0]),
        "med_nn_mm": float(np.median(d)),
        "med_along_mm": float(np.median(along)),
        "p90_along_mm": float(np.percentile(along, 90)),
        "max_along_mm": float(np.max(along)),
        "med_across_mm": float(np.median(across)),
        "p90_across_mm": float(np.percentile(across, 90)),
        "max_across_mm": float(np.max(across)),
        "coincidence_share_1um": float(np.mean(d <= COINCIDENCE_MM)),
    }


def cell_meta(tsv):
    meta = {}
    if not tsv or not os.path.isfile(tsv):
        return meta
    with open(tsv) as fh:
        head = fh.readline().rstrip("\n").split("\t")
        for line in fh:
            f = line.rstrip("\n").split("\t")
            if len(f) < len(head):
                continue
            row = dict(zip(head, f))
            key = (row.get("tag", ""), row.get("pot", ""), row.get("piece", ""))
            meta[key] = row
    return meta


def selftest():
    g = np.arange(20, dtype=np.float64)
    gx, gy = np.meshgrid(g, g, indexing="ij")
    p0 = np.column_stack([gx.ravel(), gy.ravel(), np.zeros(gx.size)])
    n0 = np.tile(np.array([0.0, 0.0, 1.0]), (p0.shape[0], 1))
    fails = []

    p1 = p0 + np.array([0.0, 0.0, 2.0])
    s = pair_stats(p0, n0, p1, n0)
    if abs(s["med_along_mm"] - 2.0) > 1e-9 or s["med_across_mm"] > 1e-9:
        fails.append("case1 along=%r across=%r" % (s["med_along_mm"], s["med_across_mm"]))

    p2 = p0 + np.array([0.4, 0.0, 0.0])
    s = pair_stats(p0, n0, p2, n0)
    if s["med_along_mm"] > 1e-9 or abs(s["med_across_mm"] - 0.4) > 1e-9:
        fails.append("case2 along=%r across=%r" % (s["med_along_mm"], s["med_across_mm"]))

    s = pair_stats(p0, n0, p0.copy(), n0)
    if s["med_along_mm"] > 1e-12 or s["med_across_mm"] > 1e-12 or abs(s["coincidence_share_1um"] - 1.0) > 1e-12:
        fails.append("case3 coincidence=%r" % (s["coincidence_share_1um"],))

    # a slanted pair: a 0.3 step along (0.6, 0, 0.8) -> all of it is ALONG, none across
    # (kept under half the 1.0 grid spacing so the nearest-neighbour pairing is unambiguous)
    nrm = np.tile(np.array([0.6, 0.0, 0.8]), (p0.shape[0], 1))
    p3 = p0 + 0.3 * np.array([0.6, 0.0, 0.8])
    s = pair_stats(p0, nrm, p3, nrm)
    if abs(s["med_along_mm"] - 0.3) > 1e-9 or s["med_across_mm"] > 1e-9:
        fails.append("case4 along=%r across=%r" % (s["med_along_mm"], s["med_across_mm"]))

    # two coplanar patches slid sideways: no coincidence at all, and the step is all ACROSS
    s = pair_stats(p0, n0, p0 + np.array([0.4, 0.4, 0.0]), n0)
    if s["coincidence_share_1um"] > 1e-12 or abs(s["med_across_mm"] - np.sqrt(0.32)) > 1e-9 or s["med_along_mm"] > 1e-9:
        fails.append("case5 coincidence=%r across=%r" % (s["coincidence_share_1um"], s["med_across_mm"]))

    if fails:
        for f in fails:
            print("[SELFTEST] FAIL " + f)
        return 1
    print("[SELFTEST] PASS 5/5 through/across/coincidence on synthetic patches")
    return 0


def main(argv):
    if len(argv) >= 2 and argv[1] == "--selftest":
        return selftest()
    if len(argv) < 2:
        print("usage: measure_pairs26.py --selftest | <cellroot> [cells26.tsv]")
        return 2
    root = argv[1]
    meta = cell_meta(argv[2] if len(argv) > 2 else os.path.join(root, "cells26.tsv"))
    cols = ["role", "tag", "scheme", "pot", "piece", "status", "n0", "n1", "med_nn_mm",
            "med_along_mm", "p90_along_mm", "max_along_mm", "med_across_mm", "p90_across_mm",
            "max_across_mm", "coincidence_share_1um", "surf0_points_log", "surf1_points_log",
            "count_match"]
    out = []
    cells = sorted(glob.glob(os.path.join(root, "*", "*", "*")))
    for cell in cells:
        parts = cell.replace("\\", "/").split("/")
        piece, pot, tag = parts[-1], parts[-2], parts[-3]
        sdir = os.path.join(cell, "surfaces")
        f0 = glob.glob(os.path.join(sdir, "*_Surface_0.ply"))
        f1 = glob.glob(os.path.join(sdir, "*_Surface_1.ply"))
        row = meta.get((tag, pot, piece), {})
        role = row.get("role", "?")
        scheme = row.get("scheme", tag)
        rec = [role, tag, scheme, pot, piece]
        if not f0 or not f1:
            rec += ["no_pair"] + [""] * 14
            out.append(rec)
            continue
        try:
            p0, n0 = load_ply(f0[0])
            p1, n1 = load_ply(f1[0])
            if p0.shape[0] < 3 or p1.shape[0] < 3:
                rec += ["degenerate"] + [""] * 14
                out.append(rec)
                continue
            s = pair_stats(p0, n0, p1, n1)
        except Exception as exc:
            rec += ["load_error:" + str(exc).replace("\t", " ")] + [""] * 14
            out.append(rec)
            continue
        l0 = row.get("surf0_points", "")
        l1 = row.get("surf1_points", "")
        match = ""
        if l0.isdigit() and l1.isdigit():
            match = "yes" if (int(l0) == s["n0"] and int(l1) == s["n1"]) else "no"
        rec += ["ok", str(s["n0"]), str(s["n1"]),
                "%.6f" % s["med_nn_mm"], "%.6f" % s["med_along_mm"], "%.6f" % s["p90_along_mm"],
                "%.6f" % s["max_along_mm"], "%.6f" % s["med_across_mm"], "%.6f" % s["p90_across_mm"],
                "%.6f" % s["max_across_mm"], "%.6f" % s["coincidence_share_1um"],
                l0, l1, match]
        out.append(rec)
    dest = os.path.join(root, "measure26.tsv")
    with open(dest, "w") as fh:
        fh.write("\t".join(cols) + "\n")
        for rec in out:
            fh.write("\t".join(rec) + "\n")
    ok = sum(1 for r in out if r[5] == "ok")
    nomatch = sum(1 for r in out if r[5] == "ok" and r[-1] == "no")
    print("[MEASURE26] cells=%d with_pair=%d ok=%d written=%s count_mismatch=%d"
          % (len(out), sum(1 for r in out if r[5] != "no_pair"), ok, dest, nomatch))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
