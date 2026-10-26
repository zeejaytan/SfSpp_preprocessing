#!/usr/bin/env python3
"""ticket 24: angle between each estimated normal and the MESH normal at the nearest surface point.

The reference is the mesh, never another neighbour count (that would be circular): every Juglet
mesh is watertight and triangulates the same cloud, so "the normal of the triangle nearest this
point" is the surface the sampler was told to approximate.

The nearest triangle is found without trimesh.proximity, which needs the rtree module and is not
available in the tora environment: candidate faces come from a KD-tree over face centroids and the
exact point-triangle distance is then computed for each candidate. Candidates are pruned by
centroid distance, which is exact whenever the winning face is among the k nearest centroids --
reported alongside as the distance itself, and the selftest pins both the distance and the angle.

usage: mesh_angle24.py <mesh.obj> <dump_dir> <out_angles.tsv> <out_points.tsv> <tag> <pot> <piece>
        [--max-calls N] [--k-faces N] [--points-out <path>]
       mesh_angle24.py --selftest

reads <dump_dir>/<piece>_call<N>.ply (PCL ASCII PLY, xyz + normals) as written by the stage.
writes one summary row per call and, for the render pieces only, a per-point table.
"""
import argparse
import os
import sys

import numpy as np
from scipy.spatial import cKDTree


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


def load_obj(path):
    """vertices and fan-triangulated faces; only "v " and "f " lines are read."""
    verts = []
    faces = []
    with open(path, "r", errors="replace") as fh:
        for line in fh:
            if line.startswith("v "):
                f = line.split()
                verts.append((float(f[1]), float(f[2]), float(f[3])))
            elif line.startswith("f "):
                idx = []
                for tok in line.split()[1:]:
                    i = int(tok.split("/")[0])
                    idx.append(i - 1 if i > 0 else len(verts) + i)
                for j in range(1, len(idx) - 1):
                    faces.append((idx[0], idx[j], idx[j + 1]))
    if not verts or not faces:
        raise SystemExit("%s: %d vertices, %d faces -- not a surface" % (path, len(verts), len(faces)))
    return np.asarray(verts, dtype=float), np.asarray(faces, dtype=np.int64)


def unit(v):
    ln = np.linalg.norm(v, axis=-1, keepdims=True)
    ln[ln == 0] = 1.0
    return v / ln


def closest_on_tri(P, a, b, c):
    """closest point on triangle (a,b,c) for every row of P; a,b,c are per-row arrays."""
    ab = b - a
    ac = c - a
    ap = P - a
    bp = P - b
    cp = P - c
    d1 = np.einsum("ij,ij->i", ap, ab)
    d2 = np.einsum("ij,ij->i", ap, ac)
    d3 = np.einsum("ij,ij->i", bp, ab)
    d4 = np.einsum("ij,ij->i", bp, ac)
    d5 = np.einsum("ij,ij->i", cp, ab)
    d6 = np.einsum("ij,ij->i", cp, ac)
    va = d3 * d6 - d5 * d4
    vb = d5 * d2 - d1 * d6
    vc = d1 * d4 - d3 * d2
    q = np.empty_like(P)
    with np.errstate(divide="ignore", invalid="ignore"):
        denom = va + vb + vc
        denom = np.where(denom == 0, 1.0, denom)
        q[:] = a + ab * (vb / denom)[:, None] + ac * (vc / denom)[:, None]

        m = (va <= 0) & ((d4 - d3) >= 0) & ((d5 - d6) >= 0)
        if m.any():
            e = (d4 - d3)[m]
            f = (d5 - d6)[m]
            s = np.where(e + f == 0, 0.0, e / (e + f))
            q[m] = b[m] + (c[m] - b[m]) * s[:, None]

        m = (vb <= 0) & (d2 >= 0) & (d6 <= 0)
        if m.any():
            e = d2[m]
            f = d6[m]
            s = np.where(e - f == 0, 0.0, e / (e - f))
            q[m] = a[m] + ac[m] * s[:, None]

        m = (d6 >= 0) & (d5 <= d6)
        if m.any():
            q[m] = c[m]

        m = (vc <= 0) & (d1 >= 0) & (d3 <= 0)
        if m.any():
            e = d1[m]
            f = d3[m]
            s = np.where(e - f == 0, 0.0, e / (e - f))
            q[m] = a[m] + ab[m] * s[:, None]

        m = (d3 >= 0) & (d4 <= d3)
        if m.any():
            q[m] = b[m]

        m = (d1 <= 0) & (d2 <= 0)
        if m.any():
            q[m] = a[m]
    return q


def face_normals(V, F):
    return unit(np.cross(V[F[:, 1]] - V[F[:, 0]], V[F[:, 2]] - V[F[:, 0]]))


def mesh_normals(V, F, pts, k_faces=12):
    """closest point on the mesh and that triangle's normal, for every row of pts."""
    fn = face_normals(V, F)
    cent = V[F].mean(axis=1)
    tree = cKDTree(cent)
    kk = int(min(max(1, k_faces), len(cent)))
    _, idx = tree.query(pts, k=kk)
    idx = np.asarray(idx).reshape(len(pts), kk)
    best = np.full(len(pts), np.inf)
    best_face = np.zeros(len(pts), dtype=np.int64)
    for j in range(kk):
        fi = idx[:, j]
        q = closest_on_tri(pts, V[F[fi, 0]], V[F[fi, 1]], V[F[fi, 2]])
        d2 = np.einsum("ij,ij->i", pts - q, pts - q)
        better = d2 < best
        best[better] = d2[better]
        best_face[better] = fi[better]
    return np.sqrt(best), fn[best_face]


def angle_stats(nrm, fn):
    nu = unit(nrm)
    dot = np.clip(np.einsum("ij,ij->i", nu, fn), -1.0, 1.0)
    ang = np.degrees(np.arccos(dot))
    absang = np.degrees(np.arccos(np.abs(dot)))
    return {
        "med_signed_deg": float(np.median(ang)),
        "med_abs_deg": float(np.median(absang)),
        "p90_abs_deg": float(np.percentile(absang, 90)),
        "frac_abs_gt10": float((absang > 10.0).mean()),
        "frac_abs_gt30": float((absang > 30.0).mean()),
        "frac_same_hemisphere": float((dot > 0).mean()),
        "ang": ang,
        "dot": dot,
    }


def selftest():
    n = 21
    g = np.linspace(0.0, 10.0, n)
    xs, ys = np.meshgrid(g, g)
    V = np.column_stack([xs.ravel(), ys.ravel(), np.zeros(xs.size)])
    F = []
    for j in range(n - 1):
        for i in range(n - 1):
            p = j * n + i
            F.append((p, p + 1, p + n))
            F.append((p + 1, p + n + 1, p + n))
    V = np.asarray(V, dtype=float)
    F = np.asarray(F, dtype=np.int64)
    rng = np.random.default_rng(7)
    P = np.column_stack([rng.uniform(0.2, 9.8, 400), rng.uniform(0.2, 9.8, 400),
                         rng.uniform(0.05, 0.5, 400)])
    dist, fn = mesh_normals(V, F, P, k_faces=12)
    s = angle_stats(np.tile([0.0, 0.0, 1.0], (len(P), 1)), fn)
    ok1 = bool(np.allclose(dist, P[:, 2])) and s["med_abs_deg"] < 1e-6 and abs(s["med_signed_deg"]) < 1e-6
    s2 = angle_stats(np.tile([0.0, 0.0, -1.0], (len(P), 1)), fn)
    ok2 = abs(s2["med_signed_deg"] - 180.0) < 1e-6 and s2["frac_same_hemisphere"] == 0.0 and s2["med_abs_deg"] < 1e-6
    # a tilted plane: the reference must follow the surface, so no angle survives the tilt
    V3 = V.copy()
    V3[:, 2] = 0.30 * V3[:, 0]
    fn3 = face_normals(V3, F)
    tilt = unit(np.array([[-0.30, 0.0, 1.0]]))[0]
    P3 = np.column_stack([P[:, 0], P[:, 1], 0.30 * P[:, 0] + P[:, 2]])
    dist3, fn3b = mesh_normals(V3, F, P3, k_faces=12)
    s3 = angle_stats(np.tile(tilt, (len(P3), 1)), fn3b)
    ok3 = bool(np.allclose(dist3, P[:, 2] / np.sqrt(1.0 + 0.30 ** 2))) and s3["med_abs_deg"] < 1e-6
    # a 35 deg error must come back as 35 deg and must count as beyond 30 (35, not 30: at exactly
    # 30.0 the floating-point angle can land either side of the threshold and the test would flake)
    s4 = angle_stats(np.tile(unit(np.array([[np.sin(np.radians(35.0)), 0.0, np.cos(np.radians(35.0))]]))[0], (len(P), 1)), fn)
    ok4 = abs(s4["med_abs_deg"] - 35.0) < 1e-6 and s4["frac_abs_gt30"] == 1.0
    print("[SELFTEST] plane max_dist=%.3e med_abs=%.3e flipped_med=%.6f same_hemi=%.3f"
          % (float(dist.max()), s["med_abs_deg"], s2["med_signed_deg"], s2["frac_same_hemisphere"]))
    print("[SELFTEST] tilted max_dist=%.3e med_abs=%.3e  30deg_case med_abs=%.6f gt30=%.3f"
          % (float(dist3.max()), s3["med_abs_deg"], s4["med_abs_deg"], s4["frac_abs_gt30"]))
    ok = bool(ok1 and ok2 and ok3 and ok4)
    print("[SELFTEST] %s faces=%d" % ("ok" if ok else "FAILED", len(F)), flush=True)
    return 0 if ok else 1


def main():
    if len(sys.argv) > 1 and sys.argv[1] == "--selftest":
        raise SystemExit(selftest())
    ap = argparse.ArgumentParser()
    ap.add_argument("mesh")
    ap.add_argument("dump_dir")
    ap.add_argument("out")
    ap.add_argument("out_points")
    ap.add_argument("tag")
    ap.add_argument("pot")
    ap.add_argument("piece")
    ap.add_argument("--max-calls", type=int, default=4)
    ap.add_argument("--k-faces", type=int, default=12)
    a = ap.parse_args()

    render = (a.pot, a.piece) in {("Juglet", "Juglet_Piece_1"), ("Juglet", "Juglet_Piece_2"),
                                  ("Juglet", "Juglet_Piece_4"), ("Juglet", "Juglet_Piece_9"),
                                  ("Pot_A", "Pot_A_Piece_07")}

    calls = []
    for name in sorted(os.listdir(a.dump_dir)) if os.path.isdir(a.dump_dir) else []:
        if not name.endswith(".ply") or "_call" not in name:
            continue
        try:
            k = int(name[:-4].rsplit("_call", 1)[1])
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
    V, F = load_obj(a.mesh)
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
        dist, fn = mesh_normals(V, F, xyz, k_faces=a.k_faces)
        s = angle_stats(nrm, fn)
        med_dist = float(np.median(dist))
        frame_ok = "yes" if med_dist <= 1.0 else "no"
        rows.append([a.tag, a.pot, a.piece, k, len(xyz),
                     "%.4f" % s["med_signed_deg"], "%.4f" % s["med_abs_deg"],
                     "%.4f" % s["p90_abs_deg"], "%.4f" % s["frac_abs_gt10"],
                     "%.4f" % s["frac_abs_gt30"], "%.4f" % s["frac_same_hemisphere"],
                     "%.4f" % med_dist, frame_ok])
        if render:
            for i in range(len(xyz)):
                ptab.append((a.tag, a.pot, a.piece, k, xyz[i, 0], xyz[i, 1], xyz[i, 2],
                             s["ang"][i], s["dot"][i]))
        print("[ANGLES] %s %s/%s call=%d n=%d med_abs=%.3f p90=%.3f gt30=%.4f frame=%s"
              % (a.tag, a.pot, a.piece, k, len(xyz), s["med_abs_deg"], s["p90_abs_deg"],
                 s["frac_abs_gt30"], frame_ok), flush=True)

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
