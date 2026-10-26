#!/usr/bin/env python3
"""ticket 24 (lead follow-up): one figure for Juglet_Piece_7, the only Juglet cell that passes the
wall-pair bar in the grid, so a picture can be compared with the numbers.

Row = arm (A, A2, B, C, D, E). Column 1 = the points of the two written surfaces coloured by the
angle between the normal shipped in each surface PLY and the MESH normal at the same point. The
cloud-wide per-point table (angle_points.tsv) exists for this piece as a header only -- the ticket-24
instrument kept per-point tables for Juglet 1, 2, 4, 9 and Pot A 07 -- and the call normals it would
have coloured died with the stage, so colouring the cloud itself would need a cell re-run. What is
drawn is every point of Surface_0 and Surface_1, which is 43 % of the cloud under A and 64 % under D.
Column 2 = the whole cloud in grey with Surface_0 red over Surface_1 blue.
Column 3 = the D row only: an edge-on view along the mean Surface_0 normal, so the pair is two bands.

Nothing here measures anything new: it projects and colours points that are already on disk.

usage: render_p7_24.py <cells_root> <out_dir> <mesh.obj> <pot/piece> [tags]
"""
import os
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from coverage23 import cloud_path, read_pcd_xyz  # noqa: E402
from measure_arm23 import load_ply  # noqa: E402
from mesh_angle24 import load_obj, mesh_normals, unit  # noqa: E402

VMAX = 45.0
MAXPLOT = 25000


def project(pts, centre, basis):
    d = pts - centre
    return d.dot(basis[:, 0]), d.dot(basis[:, 1])


def scale_bar(ax, lim, dpi, inches):
    dx = lim[1] - lim[0]
    x0 = lim[0] + 0.06 * dx
    y0 = lim[2] + 0.07 * (lim[3] - lim[2])
    ax.plot([x0, x0 + 5.0], [y0, y0], color="k", lw=2.0, solid_capstyle="butt")
    ax.annotate("5 mm", (x0 + 2.5, y0), textcoords="offset points", xytext=(0, 5),
                ha="center", fontsize=7)
    return (lim[1] - lim[0]) / (inches * dpi)


def main():
    root, outdir, meshpath, target = sys.argv[1:5]
    tags = (sys.argv[5] if len(sys.argv) > 5 else "A,A2,B,C,D,E").split(",")
    pot, piece = target.split("/")
    os.makedirs(outdir, exist_ok=True)
    dpi = 100

    V, F = load_obj(meshpath)
    cloud, _n, _s = read_pcd_xyz(cloud_path(pot, piece))
    centre = cloud.mean(axis=0)
    _u, _sv, vt = np.linalg.svd(cloud - centre, full_matrices=False)
    basis = vt.T
    cx, cy = project(cloud, centre, basis)
    lim = [cx.min(), cx.max(), cy.min(), cy.max()]
    padx = 0.06 * (lim[1] - lim[0])
    pady = 0.06 * (lim[3] - lim[2])
    lim = [lim[0] - padx, lim[1] + padx, lim[2] - pady, lim[3] + pady]
    idx = np.arange(len(cloud))
    if len(idx) > MAXPLOT:
        idx = np.random.default_rng(24).choice(len(idx), MAXPLOT, replace=False)

    print("[RENDER7] piece=%s cloud_points=%d mesh_faces=%d vmax=%.0fdeg dpi=%d"
          % (piece, len(cloud), len(F), VMAX, dpi))
    fig, axes = plt.subplots(len(tags), 3, figsize=(10.4, 3.4 * len(tags)), squeeze=False)
    gap_text = {}
    for r, tag in enumerate(tags):
        cell = os.path.join(root, tag, pot, piece)
        axL, axR, axS = axes[r][0], axes[r][1], axes[r][2]
        pts, angs, n = [], [], {}
        for k, col, lab in ((0, "tab:red", "S0"), (1, "tab:blue", "S1")):
            f = os.path.join(cell, "surfaces", "%s_Surface_%d.ply" % (piece, k))
            if not os.path.exists(f):
                n[k] = 0
                continue
            p, nrm = load_ply(f)
            n[k] = len(p)
            if len(p) == 0:
                continue
            nrm = np.array([unit(v) for v in nrm])
            _d, fn = mesh_normals(V, F, p)
            dot = np.einsum("ij,ij->i", nrm, fn)
            pts.append(p)
            angs.append(np.degrees(np.arccos(np.clip(dot, -1.0, 1.0))))
        if pts:
            P = np.concatenate(pts)
            A = np.concatenate(angs)
            px, py = project(P, centre, basis)
            sc = axL.scatter(px, py, c=np.clip(A, 0, VMAX), cmap="RdYlGn_r", vmin=0, vmax=VMAX,
                             s=2.0, linewidths=0)
            axL.set_title("%s  surface points: normal vs mesh  med=%.1f deg  (n=%d of %d cloud pts)"
                          % (tag, float(np.median(A)), len(P), len(cloud)), fontsize=6)
        else:
            axL.set_title("%s  no surface written" % tag, fontsize=6)
        axL.set_xlim(lim[0], lim[1]); axL.set_ylim(lim[2], lim[3])
        axL.set_aspect("equal", "box"); axL.tick_params(labelsize=5)
        mmpx = scale_bar(axL, lim, dpi, 3.5)

        axR.scatter(cx[idx], cy[idx], c="0.75", s=0.6, linewidths=0)
        for k, col, lab in ((0, "tab:red", "S0"), (1, "tab:blue", "S1")):
            f = os.path.join(cell, "surfaces", "%s_Surface_%d.ply" % (piece, k))
            if not os.path.exists(f):
                continue
            p, _nrm = load_ply(f)
            if len(p) == 0:
                continue
            qx, qy = project(p, centre, basis)
            axR.scatter(qx, qy, c=col, s=2.0, linewidths=0, label=lab)
        axR.set_xlim(lim[0], lim[1]); axR.set_ylim(lim[2], lim[3])
        axR.set_aspect("equal", "box"); axR.tick_params(labelsize=5)
        axR.set_title("%s  S0=%d S1=%d" % (tag, n.get(0, 0), n.get(1, 0)), fontsize=6)
        scale_bar(axR, lim, dpi, 3.5)

        if tag == "D" and n.get(0, 0) > 0 and n.get(1, 0) > 0:
            p0, m0 = load_ply(os.path.join(cell, "surfaces", "%s_Surface_0.ply" % piece))
            p1, m1 = load_ply(os.path.join(cell, "surfaces", "%s_Surface_1.ply" % piece))
            nrm_mean = unit(np.array([unit(v) for v in m0]).mean(axis=0))
            w0 = (p0 - centre).dot(nrm_mean)
            w1 = (p1 - centre).dot(nrm_mean)
            # in-plane axis: the cloud's widest direction orthogonal to nrm_mean
            plane = basis[:, 0] - nrm_mean * basis[:, 0].dot(nrm_mean)
            plane = plane / np.linalg.norm(plane)
            s0 = (p0 - centre).dot(plane)
            s1 = (p1 - centre).dot(plane)
            axS.scatter(s0, w0, c="tab:red", s=1.6, linewidths=0)
            axS.scatter(s1, w1, c="tab:blue", s=1.6, linewidths=0)
            gap = float(np.median(w1)) - float(np.median(w0))
            gap_text["D"] = gap
            axS.annotate("", xy=(s0.min() + 0.5, float(np.median(w1))),
                         xytext=(s0.min() + 0.5, float(np.median(w0))),
                         arrowprops=dict(arrowstyle="<->", lw=1.0, color="k"))
            axS.annotate("%.2f mm" % gap, (s0.min() + 1.2, 0.5 * (float(np.median(w0)) + float(np.median(w1)))),
                         fontsize=7)
            axS.set_title("D edge-on along the S0 mean normal: separation %.2f mm" % gap, fontsize=6)
            axS.set_xlim(s0.min() - 1.0, max(s0.max(), s1.max()) + 1.0)
            lo = min(w0.min(), w1.min()); hi = max(w0.max(), w1.max())
            axS.set_ylim(lo - 0.1 * (hi - lo), hi + 0.1 * (hi - lo))
            axS.set_aspect("equal", "box"); axS.tick_params(labelsize=5)
            scale_bar(axS, [s0.min() - 1.0, max(s0.max(), s1.max()) + 1.0,
                            lo - 0.1 * (hi - lo), hi + 0.1 * (hi - lo)], dpi, 3.5)
        else:
            axS.axis("off")
        print("[RENDER7] %s/%s row=%s n0=%d n1=%d mm_per_px=%.4f"
              % (pot, piece, tag, n.get(0, 0), n.get(1, 0), mmpx), flush=True)
    cax = fig.add_axes([0.92, 0.55, 0.008, 0.30])
    cb = fig.colorbar(sc, cax=cax)
    cb.set_label("normal vs mesh normal (deg)", fontsize=7)
    cb.ax.tick_params(labelsize=5)
    fig.suptitle("%s / %s  (column 3: D only, edge-on; 5 mm bar on every drawn panel)" % (pot, piece),
                 fontsize=8)
    out = os.path.join(outdir, "render24_%s_%s_lead.png" % (pot, piece))
    fig.savefig(out, dpi=dpi)
    plt.close(fig)
    print("[RENDER7] wrote %s" % out, flush=True)
    if gap_text:
        print("[RENDER7] D separation along the S0 mean normal = %.4f mm" % gap_text["D"], flush=True)


if __name__ == "__main__":
    main()
