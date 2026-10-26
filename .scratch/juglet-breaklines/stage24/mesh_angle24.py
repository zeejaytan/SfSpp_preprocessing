#!/usr/bin/env python3
"""ticket 24: angle between each estimated normal and the MESH normal at the nearest surface point.

The reference is the mesh, never another neighbour count (that would be circular): every Juglet
mesh is watertight and triangulates the same cloud, so 'the normal of the triangle nearest this
point' is the surface the sampler was told to approximate.

usage: mesh_angle24.py <mesh.obj> <dump_dir> <out_angles.tsv> <out_points.tsv> <tag> <pot> <piece>
        [--max-calls N] [--points-out <path>]

reads <dump_dir>/<piece>_call<N>.ply (PCL ASCII PLY, xyz + normals) as written by the stage.
writes one summary row per call and, for the render pieces only, a per-point table.
"""
import argparse
import os
import sys

import numpy as np


def load_ply(path):
    with open(path, "rb") as fh:
        raw = fh.read()
    end = raw.find(b"end_header")
    if end < 0:
        raise SystemExit("%s: no end_header" % path)
    head = raw[:end].decode("ascii", "replace")
    fmt = "ascii"
    n = 0
    for line in head.splitlines():
        if line.startswith("format "):
            fmt = line.split()[1]
        elif line.startswith("element vertex "):
            n = int(line.split()[2])
    if fmt != "ascii":
        raise SystemExit("%s: only ascii PLY is expected here, got %s" % (path, fmt))
    body = raw[end + len(b"end_header"):].splitlines()[1:n + 1]
    if len(body) != n:
        raise SystemExit("%s: header says %d vertices, %d read" % (path, n, len(body)))
    xyz = np.empty((len(body), 3))
    nrm = np.empty((len(body), 3))
    for i, line in enumerate(body):
        f = line.split()
        xyz[i] = [float(f[0]), float(f[1]), float(f[2])]
        nrm[i] = [float(f[3]), float(f[4]), float(f[5])]
    return xyz, nrm


def unit(v):
    ln = np.linalg.norm(v, axis=1, keepdims=True)
    ln[ln == 0] = 1.0
    return v / ln


def mesh_normals(mesh, pts):
    """closest point on the mesh and that triangle's normal, for every row of pts."""
    import trimesh
    m = mesh
    if not isinstance(m, trimesh.Trimesh):
        m = trimesh.load(mesh, process=False, force="mesh")
    if m.faces is None or len(m.faces) == 0:
        raise SystemExit("mesh has no faces")
    closest, dist, tri = trimesh.proximity.closest_point(m, pts)
    fn = unit(np.asarray(m.face_normals, dtype=float))
    return closest, np.asarray(dist, dtype=float), fn[np.asarray(tri, dtype=int)]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("mesh")
    ap.add_argument("dump_dir")
    ap.add_argument("out")
    ap.add_argument("out_points")
    ap.add_argument("tag")
    ap.add_argument("pot")
    ap.add_argument("piece")
    ap.add_argument("--max-calls", type=int, default=4)
    a = ap.parse_args()

    render = (a.pot, a.piece) in {("Juglet", "Juglet_Piece_1"), ("Juglet", "Juglet_Piece_2"),
                                  ("Juglet", "Juglet_Piece_4"), ("Juglet", "Juglet_Piece_9"),
                                  ("Pot_A", "Pot_A_Piece_07")}

    calls = []
    for name in os.listdir(a.dump_dir):
        if not name.endswith(".ply"):
            continue
        stem = name[:-4]
        if "_call" not in stem:
            continue
        try:
            k = int(stem.rsplit("_call", 1)[1])
        except ValueError:
            continue
        calls.append((k, os.path.join(a.dump_dir, name)))
    calls.sort()
    dropped = max(0, len(calls) - a.max_calls)
    calls = calls[:a.max_calls]

    cols = ["tag", "pot", "piece", "call", "n", "med_signed_deg", "med_abs_deg",
            "p90_abs_deg", "frac_abs_gt10", "frac_abs_gt30", "frac_same_hemisphere",
            "med_dist_mm", "frame_ok"]
    rows = []
    ptab = []
    import trimesh
    mesh = trimesh.load(a.mesh, process=False, force="mesh")
    for k, path in calls:
        try:
            xyz, nrm = load_ply(path)
        except SystemExit as exc:
            print("[ANGLES] %s call %d unreadable: %s" % (a.piece, k, exc), file=sys.stderr)
            rows.append([a.tag, a.pot, a.piece, k, "NA"] + ["NA"] * 8)
            continue
        if len(xyz) == 0:
            rows.append([a.tag, a.pot, a.piece, k, 0] + ["NA"] * 8)
            continue
        closest, dist, fn = mesh_normals(mesh, xyz)
        nu = unit(nrm)
        dot = np.clip(np.einsum("ij,ij->i", nu, fn), -1.0, 1.0)
        ang = np.degrees(np.arccos(dot))
        absang = np.degrees(np.arccos(np.abs(dot)))
        med_signed = float(np.median(ang))
        med_abs = float(np.median(absang))
        p90 = float(np.percentile(absang, 90))
        g10 = float((absang > 10.0).mean())
        g30 = float((absang > 30.0).mean())
        same = float((dot > 0).mean())
        med_dist = float(np.median(dist))
        frame_ok = "yes" if med_dist <= 1.0 else "no"
        rows.append([a.tag, a.pot, a.piece, k, len(xyz),
                     "%.4f" % med_signed, "%.4f" % med_abs, "%.4f" % p90,
                     "%.4f" % g10, "%.4f" % g30, "%.4f" % same,
                     "%.4f" % med_dist, frame_ok])
        if render:
            for i in range(len(xyz)):
                ptab.append((a.tag, a.pot, a.piece, k, xyz[i, 0], xyz[i, 1], xyz[i, 2],
                             ang[i], dot[i]))
        print("[ANGLES] %s %s/%s call=%d n=%d med_abs=%.3f p90=%.3f gt30=%.4f frame=%s"
              % (a.tag, a.pot, a.piece, k, len(xyz), med_abs, p90, g30, frame_ok), flush=True)

    with open(a.out, "w") as fh:
        fh.write("\t".join(cols) + "\n")
        for r in rows:
            fh.write("\t".join(map(str, r)) + "\n")
    with open(a.out_points, "w") as fh:
        fh.write("tag\tpot\tpiece\tcall\tx\ty\tz\tang_deg\tdot\n")
        for r in ptab:
            fh.write("%s\t%s\t%s\t%d\t%.6f\t%.6f\t%.6f\t%.4f\t%.6f\n" % r)
    if dropped:
        print("[ANGLES] %s %s: %d later calls not measured (--max-calls %d)"
              % (a.tag, a.piece, dropped, a.max_calls), flush=True)
    print("[ANGLES] %s %s/%s wrote %d call rows, %d point rows (render=%s)"
          % (a.tag, a.pot, a.piece, len(rows), len(ptab), render), flush=True)


if __name__ == "__main__":
    main()
