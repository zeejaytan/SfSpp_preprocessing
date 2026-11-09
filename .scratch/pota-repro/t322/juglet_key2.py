#!/usr/bin/env python3
"""Ticket 322 Q4, second half: how precise is the Juglet key, piece by piece?

Reads juglet_key.py's assembled_samples.npz and key/. Reports
  * robust (trimmed) circle per slice across the whole-vessel axis: body and neck
    centres, and the line through each group's centres -> body/neck coaxiality;
  * a body-only axis fit (slices below the shoulder) against the whole-vessel axis;
  * per piece, on the lane surfaces the axis finder actually reads: the frame check
    (surface points to scan mesh), the local optimum of the normalised cost started
    from the key (how far the piece's own best surface of revolution sits from the
    vessel's axis), and the costs at key / local optimum.
"""

import argparse
import json
import os
import sys

import numpy as np
from scipy.spatial import cKDTree

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from juglet_key import DS, load_obj, offset_at  # noqa: E402
from sfs_axes.io_axes import direction_angle_deg, read_axes  # noqa: E402
from sfs_axes.normalized import normalized_huber_cost, refine_axis_normalized  # noqa: E402

LANES = ("/data/gpfs/projects/punim2657/SfSpp/runs/"
         "20261103-1332_fab76f5_t66-admitsign-default/outU_jug/geom")


def load_wall(path):
    with open(path) as fh:
        first = fh.readline()
    if first.startswith("ply"):
        n = None
        with open(path) as fh:
            for line in fh:
                if line.startswith("element vertex"):
                    n = int(line.split()[-1])
                if line.strip() == "end_header":
                    break
            rows = [[float(v) for v in fh.readline().split()[:6]] for _ in range(n)]
        return np.asarray(rows).T
    return np.loadtxt(path, usecols=range(6), ndmin=2).T


def frame(d):
    d = d / np.linalg.norm(d)
    e1 = np.cross(d, [1.0, 0, 0] if abs(d[0]) < 0.9 else [0, 1.0, 0])
    e1 /= np.linalg.norm(e1)
    return d, e1, np.cross(d, e1)


def robust_circle(x, y, iters=6):
    keep = np.ones(len(x), bool)
    for _ in range(iters):
        A = np.c_[2 * x[keep], 2 * y[keep], np.ones(keep.sum())]
        sol, *_ = np.linalg.lstsq(A, x[keep] ** 2 + y[keep] ** 2, rcond=None)
        cx, cy = sol[0], sol[1]
        r = np.sqrt(max(sol[2] + cx ** 2 + cy ** 2, 1e-9))
        res = np.abs(np.hypot(x - cx, y - cy) - r)
        mad = np.median(res[keep]) + 1e-6
        keep = res < max(3.0 * mad, 0.3)
    return cx, cy, r, float(np.median(res[keep])), float(keep.mean())


def centre_line(rows):
    """Least-squares 3-D line through slice centres; returns tilt (deg) to the slicing axis."""
    Z = np.array([[r["cx"], r["cy"], r["z"]] for r in rows])
    m = Z.mean(0)
    _, _, Vt = np.linalg.svd(Z - m)
    d = Vt[0] * np.sign(Vt[0][2])
    return float(np.degrees(np.arccos(abs(d[2])))), m.tolist()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--jugkey", required=True)
    a = ap.parse_args()
    S = np.load(os.path.join(a.jugkey, "assembled_samples.npz"))
    P, N, owner, axis = S["P"], S["N"], S["owner"], S["axis"]
    d, e1, e2 = frame(axis[0:3])
    rel = P - axis[3:6]
    z, x, y = rel @ d, rel @ e1, rel @ e2
    zs = np.linspace(np.percentile(z, 1), np.percentile(z, 99), 25)
    rows = []
    for k in range(24):
        m = (z >= zs[k]) & (z < zs[k + 1])
        if m.sum() < 200:
            continue
        cx, cy, r, res, inl = robust_circle(x[m], y[m])
        rows.append(dict(z=float(0.5 * (zs[k] + zs[k + 1])), cx=float(cx), cy=float(cy),
                         off=float(np.hypot(cx, cy)), r=float(r), res=res, inlier=inl))
    rmax_z = max(rows, key=lambda r: r["r"])["z"]
    # body = below the shoulder (radius still >= 85% of max); neck = above it
    rmax = max(r["r"] for r in rows)
    body = [r for r in rows if r["r"] >= 0.85 * rmax]
    neck = [r for r in rows if r["z"] > rmax_z and r["r"] < 0.75 * rmax]
    out = dict(slices=rows, rmax=rmax, z_at_rmax=rmax_z)
    out["body_centre_line_tilt_deg"], _ = centre_line(body)
    out["neck_centre_line_tilt_deg"], _ = centre_line(neck) if len(neck) >= 3 else (None, None)
    out["body_slices"] = len(body)
    out["neck_slices"] = len(neck)
    # body-only axis fit
    zb = (min(r["z"] for r in body) - 1.0, max(r["z"] for r in body) + 1.0)
    mb = (z >= zb[0]) & (z <= zb[1])
    X = np.vstack([P[mb].T, N[mb].T])
    vb = refine_axis_normalized(axis, X, max_iters=200, tolerance=1e-10)
    ctr = P.mean(0)
    out["body_axis_vs_vessel_axis"] = dict(angle_deg=direction_angle_deg(vb[0:3], axis[0:3]),
                                           offset_mm_at_centroid=offset_at(vb, axis, ctr),
                                           n=int(mb.sum()))
    mn = z > zb[1]
    if mn.sum() > 500:
        Xn = np.vstack([P[mn].T, N[mn].T])
        vn = refine_axis_normalized(axis, Xn, max_iters=200, tolerance=1e-10)
        out["neck_axis_vs_vessel_axis"] = dict(angle_deg=direction_angle_deg(vn[0:3], axis[0:3]),
                                               offset_mm_at_centroid=offset_at(vn, axis, ctr),
                                               n=int(mn.sum()))
    # per piece on the lane surfaces
    out["pieces"] = {}
    for i in range(1, 10):
        C0 = load_wall(os.path.join(LANES, "Juglet_Piece_%d.S0" % i))
        C1 = load_wall(os.path.join(LANES, "Juglet_Piece_%d.S1" % i))
        V, _F = load_obj(os.path.join(DS, "Mesh/Juglet/Juglet_Piece_%02d_Mesh.obj" % i))
        dd, _ = cKDTree(V).query(C0[0:3].T, k=1)
        key = read_axes(os.path.join(a.jugkey, "key", "Juglet_Piece_%d_Axis.xyz" % i))[:, 0]
        C = np.concatenate([C0, C1], axis=1)
        c = C[0:3].mean(1)
        loc = refine_axis_normalized(key, C, max_iters=200, tolerance=1e-10)
        out["pieces"][i] = dict(
            n_S0=int(C0.shape[1]), n_S1=int(C1.shape[1]),
            S0_to_mesh_median_mm=float(np.median(dd)), S0_to_mesh_p99_mm=float(np.percentile(dd, 99)),
            local_opt_vs_key_deg=direction_angle_deg(loc[0:3], key[0:3]),
            local_opt_vs_key_offset_mm=offset_at(loc, key, c),
            cost_key=[normalized_huber_cost(key, C0), normalized_huber_cost(key, C1)],
            cost_local=[normalized_huber_cost(loc, C0), normalized_huber_cost(loc, C1)])
    with open(os.path.join(a.jugkey, "key2_report.json"), "w") as fh:
        json.dump(out, fh, indent=1, default=float)
    for r in rows:
        print("z=%6.1f r=%5.2f off=%4.2f res=%4.2f inl=%.2f" % (r["z"], r["r"], r["off"], r["res"], r["inlier"]))
    for k in ("rmax", "z_at_rmax", "body_slices", "neck_slices", "body_centre_line_tilt_deg",
              "neck_centre_line_tilt_deg", "body_axis_vs_vessel_axis", "neck_axis_vs_vessel_axis"):
        print(k, out.get(k))
    for i, p in out["pieces"].items():
        print(i, json.dumps({k: (round(v, 4) if isinstance(v, float) else v) for k, v in p.items()}))


if __name__ == "__main__":
    main()
