#!/usr/bin/env python3
"""Ticket 71 stage B1 — synthetic exactness, written independently of objcheck7.py.

Two exact surfaces of revolution, each with both walls. The outer wall's normal
points away from the axis; the inner wall's normal points toward the axis
(out of the clay). The true axis is the z axis through the origin.

For each of the six costs, minimise from the true axis and from two perturbed
starts (2 deg tilt with 1 mm radial offset, and 2 deg tilt with 20 mm). A cost
passes a start when the result is within 0.5 deg and 0.5 mm of the true axis.
A cost passes the geometry only when every start passes. sin_normal has no
position term, so a perturbed start is not expected to come back in millimetres.

usage: b1_synthetic.py OUT_TSV
"""
import os
import sys

import numpy as np

_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _HERE)
sys.path.insert(0, os.path.abspath(os.path.join(_HERE, "..", "..", "..")))

from costs71 import COSTS, canonicalize, cost_value, lower_neighbor, minimize_cost, perturb  # noqa: E402
from sfs_axes.io_axes import direction_angle_deg, radial_axial_errors  # noqa: E402

PASS_DEG = 0.5
PASS_MM = 0.5
TRUE = np.array([0.0, 0.0, 1.0, 0.0, 0.0, 0.0])


def revolution(slope, radius_at_zero, thickness, z0, z1, n_theta, n_z):
    """Two walls of r(z) = slope * z + radius_at_zero, inner wall `thickness` mm inside.

    Returns X (6, n) with both walls. Outer normals point away from the axis.
    """
    theta = np.linspace(0.0, 2.0 * np.pi, n_theta, endpoint=False)
    z = np.linspace(z0, z1, n_z)
    th, zz = np.meshgrid(theta, z, indexing="ij")
    th = th.ravel()
    zz = zz.ravel()
    r_out = slope * zz + radius_at_zero
    if np.any(r_out - thickness <= 0.0):
        raise RuntimeError("inner wall crossed the axis; choose a thicker radius")
    # Geometric outward normal of r = slope*z + b is (cos, sin, -slope), unit length.
    scale = np.sqrt(1.0 + slope * slope)
    n_rad = 1.0 / scale
    n_z = -slope / scale
    cols = []
    for radius, sign in ((r_out, 1.0), (r_out - thickness, -1.0)):
        pts = np.vstack([radius * np.cos(th), radius * np.sin(th), zz])
        nrm = sign * np.vstack([n_rad * np.cos(th), n_rad * np.sin(th),
                                np.full_like(th, n_z)])
        cols.append(np.vstack([pts, nrm]))
    return np.concatenate(cols, axis=1)


def shells():
    cylinder = revolution(0.0, 50.0, 4.0, -40.0, 40.0, 36, 16)
    cone = revolution(0.40, 0.0, 4.0, 40.0, 120.0, 36, 16)
    return (("cylinder", cylinder), ("cone", cone))


def starts():
    return (
        ("true", TRUE.copy()),
        ("tilt2_mm1", perturb(TRUE, 2.0, 1.0)),
        ("tilt2_mm20", perturb(TRUE, 2.0, 20.0)),
    )


def main():
    out_path = sys.argv[1] if len(sys.argv) > 1 else os.path.join(_HERE, "b1_laptop.tsv")
    parent = os.path.dirname(os.path.abspath(out_path))
    if parent:
        os.makedirs(parent, exist_ok=True)

    # The tilt helper is part of the gate. If it is not exactly 2 deg / the
    # requested offset, every later number is about the helper, not the cost.
    for deg, mm in ((2.0, 1.0), (2.0, 20.0)):
        got = perturb(TRUE, deg, mm)
        ang = direction_angle_deg(got[0:3], TRUE[0:3])
        rad = radial_axial_errors(got[3:6], TRUE[0:3], TRUE[3:6])[0]
        if abs(ang - deg) > 1e-8 or abs(rad - mm) > 1e-8:
            raise SystemExit("perturb(%g deg, %g mm) came out %.6g deg / %.6g mm"
                             % (deg, mm, ang, rad))

    rows = []
    print("geometry\tcost\tstart\tang_deg\trad_mm\tcost_final\tcost_at_true"
          "\tlower_neighbor\titers\tcapped\tpass")
    for gname, X in shells():
        # Signed residuals are identities on a surface of revolution. If they
        # are not numerically zero here, the shell is wrong and the table is void.
        for name in ("proj_signed", "cross", "triple"):
            c = cost_value(name, TRUE, X)
            if c > 1e-8:
                raise SystemExit("%s %s residual at the true axis is %.6g, not ~0"
                                 % (gname, name, c))
        for name in COSTS:
            lower, c_true, c_nb = lower_neighbor(name, TRUE, X)
            for sname, vt0 in starts():
                vt, final, iters, capped = minimize_cost(name, vt0, X, max_iters=80)
                vt = canonicalize(vt)
                ang = direction_angle_deg(vt[0:3], TRUE[0:3])
                rad = radial_axial_errors(vt[3:6], TRUE[0:3], TRUE[3:6])[0]
                ok = int(ang <= PASS_DEG and rad <= PASS_MM)
                row = dict(geometry=gname, cost=name, start=sname, n=X.shape[1],
                           ang_deg=ang, rad_mm=rad, cost_final=final,
                           cost_at_true=c_true, lower_neighbor=int(lower),
                           neighbor_cost=c_nb, iters=iters, capped=capped, passed=ok)
                rows.append(row)
                print("%s\t%s\t%s\t%.6g\t%.6g\t%.6g\t%.6g\t%d\t%d\t%d\t%d"
                      % (gname, name, sname, ang, rad, final, c_true, int(lower),
                         iters, capped, ok), flush=True)

    cols = ["geometry", "cost", "start", "n", "ang_deg", "rad_mm", "cost_final",
            "cost_at_true", "lower_neighbor", "neighbor_cost", "iters", "capped", "passed"]
    with open(out_path, "w") as fh:
        fh.write("\t".join(cols) + "\n")
        for r in rows:
            cells = []
            for c in cols:
                v = r[c]
                cells.append(("%.8g" % v) if isinstance(v, float) else str(v))
            fh.write("\t".join(cells) + "\n")
    print("[B1] wrote %s (%d rows)" % (out_path, len(rows)), flush=True)
    land_path = os.path.join(os.path.dirname(os.path.abspath(out_path)), "b1_landscape.tsv")
    with open(land_path, "w") as fh:
        fh.write("geometry\tcost\tcost_true\tcost_90deg\tcost_shift20mm\tcheaper\n")
        horiz = perturb(TRUE, 90.0, 0.0)
        shifted = perturb(TRUE, 0.0, 20.0)
        for gname, X in shells():
            for name in COSTS:
                c0 = cost_value(name, TRUE, X)
                c90 = cost_value(name, horiz, X)
                c20 = cost_value(name, shifted, X)
                cheaper = "true"
                if c90 < c0 - 1e-8:
                    cheaper = "90deg"
                elif c20 < c0 - 1e-8:
                    cheaper = "shift20"
                fh.write("%s\t%s\t%.8g\t%.8g\t%.8g\t%s\n"
                         % (gname, name, c0, c90, c20, cheaper))
                print("[B1] landscape %s %s true %.6g  90deg %.6g  shift20 %.6g  cheaper %s"
                      % (gname, name, c0, c90, c20, cheaper), flush=True)
    print("[B1] wrote %s" % land_path, flush=True)

    print("[B1] pass = every start within %.1f deg and %.1f mm" % (PASS_DEG, PASS_MM))
    for gname, _X in shells():
        for name in COSTS:
            sub = [r for r in rows if r["geometry"] == gname and r["cost"] == name]
            ok = all(r["passed"] for r in sub)
            lower = sub[0]["lower_neighbor"]
            print("[B1] %s %s %s (lower neighbour of the true axis: %s)"
                  % (gname, name, "PASS" if ok else "FAIL", "yes" if lower else "no"),
                  flush=True)


if __name__ == "__main__":
    main()
