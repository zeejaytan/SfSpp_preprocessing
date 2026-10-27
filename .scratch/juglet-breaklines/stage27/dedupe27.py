#!/usr/bin/env python3
"""Ticket 27 measurements.

Subcommands
  surfaces <cellroot>   per (arm, piece, surface): written points, distinct positions, duplicates,
                        and the [DEDUPE-27] in/out this run printed -- the exact within-run chain
                        PLY count == in (switch off) and PLY count == out (switch on).
  seteq    <cellroot>   compares the distinct-position sets of the arms per surface: exact set
                        equality, counts either way, and nearest-neighbour distance between the two
                        sets in mm. A/A2 is the run-to-run baseline in the same units, because the
                        30 ray casts are unseeded and every arm is a different draw.
  partA    <dumproot>   rung-2 and rung-5 sidecars of arm P: points entering the segmentation,
                        region sizes, points_in_no_cluster and its fraction, points on each written
                        surface and how many of them are distinct positions.
  dots     <cellroot>   Breakline_0/1 dot counts per (arm, piece) from our own edgeline stage.
Writes one TSV beside the input root and prints one [S27-...] line per table.
"""
import glob
import json
import os
import sys

import numpy as np
from scipy.spatial import cKDTree

ARMS = ["OLD", "A", "A2", "P", "B"]
SURF_RE = "Surface_"


def read_ply(path):
    """ASCII PLY -> (xyz float64 (N,3), props list, body rows list)."""
    xyz = []
    props = []
    body = 0
    nvert = 0
    fmt = None
    with open(path, "r", errors="replace") as fh:
        for line in fh:
            s = line.strip()
            if body == 0:
                if s.startswith("format"):
                    fmt = s.split()[1]
                elif s.startswith("element vertex"):
                    nvert = int(s.split()[2])
                elif s.startswith("element") and not s.startswith("element vertex"):
                    pass
                elif s.startswith("property") and nvert and not xyz:
                    props.append(s.split()[-1])
                elif s == "end_header":
                    body = 1
                continue
            parts = s.split()
            if not parts:
                continue
            if len(xyz) < nvert:
                xyz.append((float(parts[0]), float(parts[1]), float(parts[2])))
    if fmt != "ascii":
        raise SystemExit("[S27] %s is %s, expected ascii" % (path, fmt))
    return np.asarray(xyz, dtype=np.float64).reshape(-1, 3), props


def unique_positions(xyz):
    if xyz.size == 0:
        return xyz.reshape(0, 3)
    return np.unique(xyz, axis=0)


def cell_dirs(cellroot):
    out = []
    for d in sorted(glob.glob(os.path.join(cellroot, "*", "*", "*"))):
        if not os.path.isdir(d):
            continue
        tag = os.path.basename(os.path.dirname(os.path.dirname(d)))
        pot = os.path.basename(os.path.dirname(d))
        piece = os.path.basename(d)
        out.append((tag, pot, piece, d))
    return out


def surfaces_of(cell):
    res = {}
    for k in (0, 1):
        hits = sorted(glob.glob(os.path.join(cell, "surfaces", "*_Surface_%d.ply" % k)))
        if hits:
            res[k] = hits[0]
    return res


def dedupe_lines(cell):
    """surface -> list of (mode, in, out) from this cell's mesh.log."""
    res = {}
    log = os.path.join(cell, "logs", "mesh.log")
    if not os.path.isfile(log):
        return res
    with open(log, "r", errors="replace") as fh:
        for line in fh:
            if "[DEDUPE-27]" not in line:
                continue
            f = {}
            for tok in line.split():
                if "=" in tok:
                    a, b = tok.split("=", 1)
                    f[a] = b
            try:
                k = int(f.get("surface", "-1"))
            except ValueError:
                continue
            res.setdefault(k, []).append((f.get("mode", "?"), int(f.get("in", -1)), int(f.get("out", -1))))
    return res


def cmd_surfaces(cellroot):
    rows = []
    for tag, pot, piece, cell in cell_dirs(cellroot):
        dlines = dedupe_lines(cell)
        for k, path in sorted(surfaces_of(cell).items()):
            xyz, _ = read_ply(path)
            uni = unique_positions(xyz)
            ls = dlines.get(k, [])
            modes = ",".join(m for m, _, _ in ls) if ls else "-"
            ins = sum(i for _, i, _ in ls) if ls else -1
            outs = sum(o for _, _, o in ls) if ls else -1
            rows.append(dict(tag=tag, pot=pot, piece=piece, surface=k,
                             n=len(xyz), distinct=len(uni), dup=int(len(xyz) - len(uni)),
                             ratio=(len(xyz) / len(uni) if len(uni) else float("nan")),
                             calls=len(ls), modes=modes, line_in=ins, line_out=outs,
                             eq_in=("yes" if ins == len(xyz) else "no"),
                             eq_out=("yes" if outs == len(uni) else "no")))
    rows.sort(key=lambda r: (ARMS.index(r["tag"]) if r["tag"] in ARMS else 9, r["pot"], r["piece"], r["surface"]))
    out = os.path.join(cellroot, "surfaces27.tsv")
    with open(out, "w") as fh:
        fh.write("tag\tpot\tpiece\tsurface\tn_ply\tdistinct\tduplicates\tratio\tdedupe_calls\tmodes\tline_in\tline_out\tply_eq_in\tply_eq_out\n")
        for r in rows:
            fh.write("%s\t%s\t%s\t%d\t%d\t%d\t%d\t%.3f\t%d\t%s\t%d\t%d\t%s\t%s\n" % (
                r["tag"], r["pot"], r["piece"], r["surface"], r["n"], r["distinct"], r["dup"],
                r["ratio"], r["calls"], r["modes"], r["line_in"], r["line_out"], r["eq_in"], r["eq_out"]))
    for r in rows:
        print("[S27-SURF] tag=%(tag)s piece=%(piece)s s=%(surface)d n_ply=%(n)d distinct=%(distinct)d dup=%(dup)d ratio=%(ratio).3f line_in=%(line_in)d line_out=%(line_out)d ply_eq_in=%(eq_in)s ply_eq_out=%(eq_out)s modes=%(modes)s" % r)
    print("[S27] surfaces: %d rows -> %s" % (len(rows), out))


def load_sets(cellroot):
    """(tag, piece, surface) -> distinct positions."""
    sets = {}
    for tag, pot, piece, cell in cell_dirs(cellroot):
        for k, path in surfaces_of(cell).items():
            xyz, _ = read_ply(path)
            sets[(tag, piece, k)] = unique_positions(xyz)
    return sets


def compare(pa, pb):
    a, b = np.asarray(pa), np.asarray(pb)
    if len(a) == 0 or len(b) == 0:
        return None
    ta, tb = cKDTree(a), cKDTree(b)
    dab, _ = tb.query(a, k=1)  # a -> b
    dba, _ = ta.query(b, k=1)  # b -> a
    only_a = int(np.sum(dab > 0))  # a positions with no exact twin in b
    only_b = int(np.sum(dba > 0))
    both = [d for d in (dab, dba) if len(d)]
    d = np.concatenate(both) if both else np.zeros(0)
    return dict(only_a=only_a, only_b=only_b, exact_equal=("yes" if only_a == 0 and only_b == 0 else "no"),
                nn_med=float(np.median(d)), nn_p90=float(np.percentile(d, 90)), nn_max=float(np.max(d)))


PAIRS = [("A", "OLD"), ("A", "A2"), ("P", "A"), ("B", "A"), ("B", "A2")]


def cmd_seteq(cellroot):
    sets = load_sets(cellroot)
    keys = sorted({(p, k) for (t, p, k) in sets})
    out = os.path.join(cellroot, "seteq27.tsv")
    rows = []
    with open(out, "w") as fh:
        fh.write("arm_test\tarm_ref\tpot\tpiece\tsurface\tn_test\tn_ref\tonly_in_test\tonly_in_ref\tset_equal\tnn_med_mm\tnn_p90_mm\tnn_max_mm\n")
        for (pa, pb) in PAIRS:
            for (piece, k) in keys:
                a, b = sets.get((pa, piece, k)), sets.get((pb, piece, k))
                if a is None or b is None:
                    continue
                pot = "Pot_A" if piece.startswith("Pot_A") else "Juglet"
                c = compare(a, b)
                if c is None:
                    continue
                row = dict(ref=pb, test=pa, pot=pot, piece=piece, surface=k, na=len(a), nb=len(b), **c)
                rows.append(row)
                fh.write("%(test)s\t%(ref)s\t%(pot)s\t%(piece)s\t%(surface)d\t%(na)d\t%(nb)d\t%(only_a)d\t%(only_b)d\t%(exact_equal)s\t%(nn_med).6f\t%(nn_p90).6f\t%(nn_max).6f\n" % row)
    for r in rows:
        print("[S27-SETEQ] test=%(test)s ref=%(ref)s piece=%(piece)s s=%(surface)d n_test=%(na)d n_ref=%(nb)d only_in_test=%(only_a)d only_in_ref=%(only_b)d equal=%(exact_equal)s nn_med=%(nn_med).6f nn_max=%(nn_max).6f" % r)
    print("[S27] seteq: %d rows -> %s" % (len(rows), out))


def jload(path):
    try:
        with open(path) as fh:
            return json.load(fh)
    except Exception as exc:  # noqa: BLE001
        return {"_error": str(exc)}


def cmd_partA(dumproot):
    pieces = sorted(d for d in glob.glob(os.path.join(dumproot, "*")) if os.path.isdir(d))
    rows = []
    for d in pieces:
        piece = os.path.basename(d)
        pot = "Pot_A" if piece.startswith("Pot_A") else "Juglet"
        r2 = jload(os.path.join(d, "r2_clusters_premerge.json"))
        r5 = jload(os.path.join(d, "r5_write.json"))
        npts = r2.get("npts", "-")
        nocl = r2.get("points_in_no_cluster", "-")
        frac = (nocl / npts) if isinstance(nocl, int) and isinstance(npts, int) and npts else float("nan")
        cl = r2.get("clusters", [])
        cl_s = ",".join(str(x) for x in cl) if isinstance(cl, list) else str(cl)
        sv = {x.get("surface"): x for x in r5.get("surface_vertices", []) if isinstance(x, dict)}
        rows.append(dict(pot=pot, piece=piece, npts=npts, nclus=(len(cl) if isinstance(cl, list) else "-"),
                         clusters=cl_s, nocl=nocl, frac=frac,
                         min_cluster=r2.get("min_cluster", "-"), min_eff=r2.get("min_cluster_eff", "-"),
                         floor=r2.get("floor_applied", "-"), count_scale=r2.get("count_scale", "-"),
                         spacing=r2.get("spacing_mm", "-"), theta=r2.get("theta", "-"), kappa=r2.get("kappa", "-"),
                         nb=r2.get("nb", "-"), r2_retry=r2.get("retry", "-"),
                         s0v=sv.get(0, {}).get("vertices", "-"), s0d=sv.get(0, {}).get("distinct_positions", "-"),
                         s1v=sv.get(1, {}).get("vertices", "-"), s1d=sv.get(1, {}).get("distinct_positions", "-"),
                         on_s0=r5.get("points_on_surface_0", "-"), on_s1=r5.get("points_on_surface_1", "-"),
                         on_neither=r5.get("points_on_neither", "-"), nonormal=r5.get("points_without_normal", "-"),
                         gate=r5.get("write_gate", "-"), r5_retry=r5.get("retry", "-"),
                         r5_points=r5.get("points", "-"), err=("r2:" + r2["_error"] if "_error" in r2 else "") + ("r5:" + r5["_error"] if "_error" in r5 else "")))
    rows.sort(key=lambda r: (0 if r["pot"] == "Pot_A" else 1, r["piece"]))
    out = os.path.join(dumproot, "partA27.tsv")
    cols = ["pot", "piece", "npts", "nclus", "clusters", "nocl", "frac", "min_cluster", "min_eff", "floor",
            "count_scale", "spacing", "theta", "kappa", "nb", "r2_retry", "s0v", "s0d", "s1v", "s1d",
            "on_s0", "on_s1", "on_neither", "nonormal", "gate", "r5_retry", "r5_points", "err"]
    with open(out, "w") as fh:
        fh.write("\t".join(cols) + "\n")
        for r in rows:
            fh.write("\t".join(("%.4f" % r[c]) if c == "frac" and isinstance(r[c], float) else str(r[c]) for c in cols) + "\n")
    for r in rows:
        print("[S27-PARTA] pot=%(pot)s piece=%(piece)s npts=%(npts)s clusters=[%(clusters)s] points_in_no_cluster=%(nocl)s frac=%(frac).4f r2_retry=%(r2_retry)s s0=%(s0v)s/%(s0d)s s1=%(s1v)s/%(s1d)s on_s0=%(on_s0)s on_s1=%(on_s1)s neither=%(on_neither)s gate=%(gate)s r5_retry=%(r5_retry)s" % r)
    print("[S27] partA: %d pieces -> %s" % (len(rows), out))


def cmd_dots(cellroot):
    rows = {}
    for tag, pot, piece, cell in cell_dirs(cellroot):
        f = os.path.join(cell, "breakdots.tsv")
        if not os.path.isfile(f):
            continue
        with open(f) as fh:
            for line in fh:
                p = line.rstrip("\n").split("\t")
                if len(p) < 9:
                    continue
                rows[(p[0], p[2], p[3])] = dict(tag=p[0], pot=p[1], piece=p[2], surface=p[3], file=p[4],
                                                pcd_points=p[5], segs=p[6], header_pts=p[7], xyz_lines=p[8])
    out = os.path.join(cellroot, "dots27.tsv")
    with open(out, "w") as fh:
        fh.write("tag\tpot\tpiece\tsurface\tfile\tpcd_points\theader_segs\theader_pts\txyz_lines\n")
        for k in sorted(rows):
            r = rows[k]
            fh.write("%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n" % (r["tag"], r["pot"], r["piece"], r["surface"], r["file"], r["pcd_points"], r["segs"], r["header_pts"], r["xyz_lines"]))
    print("[S27] dots: %d rows -> %s" % (len(rows), out))
    pieces = sorted({(v["pot"], v["piece"]) for v in rows.values()})
    for pot, piece in pieces:
        line = ["piece=%s" % piece]
        for arm in ("OLD", "A", "A2", "B"):
            v = rows.get((arm, piece, "0"))
            line.append("%s_bl0=%s" % (arm, v["pcd_points"] if v else "missing"))
        print("[S27-DOTS] " + " ".join(line))
        line = ["piece=%s" % piece]
        for arm in ("OLD", "A", "A2", "B"):
            v = rows.get((arm, piece, "1"))
            line.append("%s_bl1=%s" % (arm, v["pcd_points"] if v else "missing"))
        print("[S27-DOTS1] " + " ".join(line))


def main(argv):
    if len(argv) < 3:
        print(__doc__)
        return 2
    cmd, root = argv[1], argv[2]
    if not os.path.isdir(root):
        raise SystemExit("[S27] not a directory: %s" % root)
    {"surfaces": cmd_surfaces, "seteq": cmd_seteq, "partA": cmd_partA, "dots": cmd_dots}[cmd](root)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
