#!/usr/bin/env python3
"""p293_render.py -- one picture per below-bar lane: our line and the authors line, laid on the
sherd mesh (top row) and on the extracted surface point cloud (bottom row).

Generalises artifacts/pota289/data/onmesh.py: same Poly3DCollection + LightSource shading, same
0.45 mm lift of the drawn dots along the nearest face normal. Adds the surface row, a projection
panel chosen to resolve the failing stretch, and a zoom on that stretch.

Usage:   p293_render.py <run dir> [piece ...]
Reads:   <run>/out/manifest.json, <run>/scripts/score292.py
Writes:  <run>/out/png/p293_<Pot>_<Piece>_Bl<k>.png
"""
import importlib.util
import json
import os
import sys

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.colors import LightSource
from matplotlib.lines import Line2D
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
from scipy.spatial import cKDTree

RUN = sys.argv[1]
OUT = os.path.join(RUN, "out", "png")
MAXF = 20000
MAXS = 60000
LIFT = 0.45
C_OURS = "#12b012"
C_AUTH = "#000000"
C_S0 = "#2b6cb0"
C_S1 = "#dd6b20"


def load_scorer():
    spec = importlib.util.spec_from_file_location("score292", os.path.join(RUN, "scripts", "score292.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


SC = load_scorer()


def rd_xyz(path):
    pts = []
    for line in open(path, errors="ignore"):
        tok = line.split()
        if len(tok) >= 3:
            try:
                pts.append([float(tok[0]), float(tok[1]), float(tok[2])])
            except ValueError:
                pass
    return np.array(pts, dtype=float)


def load_mesh(path):
    verts, faces = [], []
    for line in open(path, errors="ignore"):
        if line.startswith("v "):
            verts.append([float(x) for x in line.split()[1:4]])
        elif line.startswith("f "):
            idx = [int(t.split("/")[0]) - 1 for t in line.split()[1:]]
            for k in range(1, len(idx) - 1):
                faces.append([idx[0], idx[k], idx[k + 1]])
    return np.array(verts, dtype=float), np.array(faces, dtype=int)


def lift(pts, verts, faces, dist=LIFT):
    tri = verts[faces]
    cen = tri.mean(1)
    nrm = np.cross(tri[:, 1] - tri[:, 0], tri[:, 2] - tri[:, 0])
    nrm /= (np.linalg.norm(nrm, axis=1, keepdims=True) + 1e-12)
    _, idx = cKDTree(cen).query(pts)
    return pts + dist * nrm[idx]


def subsample(arr, cap):
    if len(arr) <= cap:
        return arr, len(arr)
    idx = np.linspace(0, len(arr) - 1, cap).astype(int)
    return arr[idx], len(arr)


PLANES = [(0, 1, "x", "y", "X-Y"), (0, 2, "x", "z", "X-Z"), (1, 2, "y", "z", "Y-Z")]


def worst_stretch(ours, auth):
    dist, _ = cKDTree(auth).query(ours)
    thr = 2.0
    over = dist > thr
    if not over.any():
        thr = max(1.0, float(np.median(dist)) + 0.5)
        over = dist > thr
    best = None
    i = 0
    while i < len(over):
        if not over[i]:
            i += 1
            continue
        j = i
        while j + 1 < len(over) and over[j + 1]:
            j += 1
        seg = ours[i:j + 1]
        arc = float(np.linalg.norm(np.diff(seg, axis=0), axis=1).sum()) if len(seg) > 1 else 0.0
        key = arc * float(dist[i:j + 1].mean())
        if best is None or key > best[0]:
            best = (key, i, j)
        i = j + 1
    if best is None:
        k = int(np.argmax(dist))
        return k, k, float(dist[k]), 0.0, thr
    _, i, j = best
    seg = ours[i:j + 1]
    arc = float(np.linalg.norm(np.diff(seg, axis=0), axis=1).sum()) if len(seg) > 1 else 0.0
    return i, j, float(dist[i:j + 1].mean()), arc, thr


def choose_plane(ours, auth, i, j):
    """The projection that resolves the failing stretch: long along the stretch AND wide across the
    gap. The second term matters: a stretch can be long in a plane that looks straight at it and so
    hides the very separation the picture is for."""
    seg = ours[i:j + 1]
    best = None
    for a, b, _, _, name in PLANES:
        arc = float(np.linalg.norm(np.diff(seg[:, [a, b]], axis=0), axis=1).sum()) if len(seg) > 1 else 0.0
        sep2, _ = cKDTree(auth[:, [a, b]]).query(seg[:, [a, b]])
        sep = float(np.median(sep2)) if len(sep2) else 0.0
        key = (arc + 1.0) * (sep + 0.05)
        if best is None or key > best[0]:
            best = (key, a, b, name, arc, sep)
    return best[1], best[2], best[3]


def shaded(verts, faces, cap):
    idx, total = subsample(np.arange(len(faces)), cap)
    tri = verts[faces[idx]]
    nrm = np.cross(tri[:, 1] - tri[:, 0], tri[:, 2] - tri[:, 0])
    shade = LightSource(azdeg=315, altdeg=45).shade_normals(nrm, fraction=1.0)
    base = np.array([0.88, 0.85, 0.78])
    cols = np.clip(shade[:, None] * base[None, :] * 1.22, 0.0, 1.0)
    coll = Poly3DCollection(tri, facecolors=cols, edgecolors="none", linewidths=0)
    return coll, total, len(idx)


def view3d(ax, pts, elev, azim):
    ax.view_init(elev=elev, azim=azim)
    lo = pts.min(0)
    hi = pts.max(0)
    ctr = (lo + hi) / 2.0
    half = float(max(np.ptp(pts[:, 0]), np.ptp(pts[:, 1]), np.ptp(pts[:, 2]))) * 0.62
    ax.set_xlim(ctr[0] - half, ctr[0] + half)
    ax.set_ylim(ctr[1] - half, ctr[1] + half)
    ax.set_zlim(ctr[2] - half, ctr[2] + half)
    ax.set_box_aspect((1, 1, 1))
    ax.tick_params(labelsize=7)
    ax.set_xlabel("x mm", fontsize=8)
    ax.set_ylabel("y mm", fontsize=8)
    ax.set_zlabel("z mm", fontsize=8)


def fmt_row(lbl, n, med, co, ca, ju):
    return "%s: n %s, median %s mm, cov %s / %s, jumps %s" % (lbl, n, med, co, ca, ju)


def render(e):
    pot = e["pot"]
    piece = e["piece"]
    lane = int(e["lane"])
    ours = SC.read_pcd(e["our_pcd"])
    auth = SC.read_pcd(e["auth_pcd"])
    verts, faces = load_mesh(e["mesh_obj"])
    s0 = rd_xyz(e["surf0"])
    s1 = rd_xyz(e["surf1"])
    d0 = float(np.median(cKDTree(s0).query(ours)[0]))
    d1 = float(np.median(cKDTree(s1).query(ours)[0]))
    if d0 <= d1:
        surf, sname, sdist, scol = s0, "Surface_0", d0, C_S0
    else:
        surf, sname, sdist, scol = s1, "Surface_1", d1, C_S1
    i, j, mean_gap, arc, thr = worst_stretch(ours, auth)
    a, b, pname = choose_plane(ours, auth, i, j)
    ours_l = lift(ours, verts, faces)
    auth_l = lift(auth, verts, faces)
    fig = plt.figure(figsize=(23, 13.4), dpi=100)
    gs = fig.add_gridspec(2, 3, left=0.04, right=0.985, top=0.90, bottom=0.085, wspace=0.16, hspace=0.20)
    ax3m = fig.add_subplot(gs[0, 0], projection="3d")
    ax2m = fig.add_subplot(gs[0, 1])
    axzm = fig.add_subplot(gs[0, 2])
    ax3s = fig.add_subplot(gs[1, 0], projection="3d")
    ax2s = fig.add_subplot(gs[1, 1])
    axzs = fig.add_subplot(gs[1, 2])
    coll, nf_total, nf_drawn = shaded(verts, faces, MAXF)
    ax3m.add_collection3d(coll)
    ax3m.plot(ours_l[:, 0], ours_l[:, 1], ours_l[:, 2], color=C_OURS, lw=3.2, label="ours (edge stage)")
    ax3m.plot(auth_l[:, 0], auth_l[:, 1], auth_l[:, 2], color=C_AUTH, lw=2.2, ls=(0, (6, 3)), label="authors (reference)")
    view3d(ax3m, verts, 24, -60)
    ax3m.set_title("MESH, 3D  (dots lifted %.2f mm)" % LIFT, fontsize=11)
    ax3m.legend(handles=[Line2D([], [], color=C_OURS, lw=3.2, label="ours"), Line2D([], [], color=C_AUTH, lw=2.2, ls=(0, (6, 3)), label="authors")], loc="upper left", fontsize=9, framealpha=0.9)
    fc, _ = subsample(verts[faces].mean(1), 40000)
    ax2m.scatter(fc[:, a], fc[:, b], s=1.0, c="#9a9a9a", alpha=0.35, linewidths=0, rasterized=True)
    ax2m.plot(ours[:, a], ours[:, b], color=C_OURS, lw=2.6)
    ax2m.plot(auth[:, a], auth[:, b], color=C_AUTH, lw=2.0, ls=(0, (6, 3)))
    ax2m.set_title("MESH, %s projection  (faces as centroids)" % pname, fontsize=11)
    ax2m.set_aspect("equal", adjustable="datalim")
    ax2m.tick_params(labelsize=8)
    lab = [q for q in PLANES if q[4] == pname][0]
    ax2m.set_xlabel(lab[2] + " mm", fontsize=9)
    ax2m.set_ylabel(lab[3] + " mm", fontsize=9)
    seg = ours[i:j + 1]
    lo = np.vstack([seg[:, [a, b]], auth[:, [a, b]]]).min(0)
    hi = np.vstack([seg[:, [a, b]], auth[:, [a, b]]]).max(0)
    pad = max(6.0, 0.35 * float(np.max(hi - lo)))
    for ax in (axzm,):
        ax.scatter(fc[:, a], fc[:, b], s=1.4, c="#9a9a9a", alpha=0.35, linewidths=0, rasterized=True)
        ax.plot(ours[:, a], ours[:, b], color=C_OURS, lw=2.6)
        ax.plot(auth[:, a], auth[:, b], color=C_AUTH, lw=2.0, ls=(0, (6, 3)))
        ax.set_xlim(lo[0] - pad, hi[0] + pad)
        ax.set_ylim(lo[1] - pad, hi[1] + pad)
        ax.set_aspect("equal", adjustable="box")
        ax.tick_params(labelsize=8)
        ax.set_xlabel(lab[2] + " mm", fontsize=9)
        ax.set_ylabel(lab[3] + " mm", fontsize=9)
        ax.set_title("MESH, zoom on the failing stretch (%s)" % pname, fontsize=11)
    axzm.text(0.02, 0.98, "stretch: our dots %d-%d (%d of %d)\narc %.1f mm, mean gap %.2f mm, threshold %.2f mm" % (i, j, j - i + 1, len(ours), arc, mean_gap, thr), transform=axzm.transAxes, va="top", ha="left", fontsize=8.5, bbox=dict(fc="white", ec="#888888", alpha=0.9))
    ax3s.scatter(surf[:, 0], surf[:, 1], surf[:, 2], s=1.2, c=scol, alpha=0.55, linewidths=0, rasterized=True)
    ax3s.plot(ours[:, 0], ours[:, 1], ours[:, 2], color=C_OURS, lw=3.2)
    ax3s.plot(auth[:, 0], auth[:, 1], auth[:, 2], color=C_AUTH, lw=2.2, ls=(0, (6, 3)))
    view3d(ax3s, surf, 24, -60)
    ax3s.legend(handles=[Line2D([], [], color=C_OURS, lw=3.2, label="ours"), Line2D([], [], color=C_AUTH, lw=2.2, ls=(0, (6, 3)), label="authors")], loc="upper left", fontsize=9, framealpha=0.9)
    ax3s.set_title("SURFACE, 3D  (%s, the face this lane rides)" % sname, fontsize=11)
    sc, _ = subsample(surf, MAXS)
    ax2s.scatter(sc[:, a], sc[:, b], s=1.2, c=scol, alpha=0.45, linewidths=0, rasterized=True)
    ax2s.plot(ours[:, a], ours[:, b], color=C_OURS, lw=2.6)
    ax2s.plot(auth[:, a], auth[:, b], color=C_AUTH, lw=2.0, ls=(0, (6, 3)))
    ax2s.set_xlabel(lab[2] + " mm", fontsize=9)
    ax2s.set_ylabel(lab[3] + " mm", fontsize=9)
    ax2s.set_title("SURFACE, %s projection" % pname, fontsize=11)
    ax2s.set_aspect("equal", adjustable="datalim")
    ax2s.tick_params(labelsize=8)
    axzs.scatter(sc[:, a], sc[:, b], s=1.6, c=scol, alpha=0.5, linewidths=0, rasterized=True)
    axzs.plot(ours[:, a], ours[:, b], color=C_OURS, lw=2.6)
    axzs.plot(auth[:, a], auth[:, b], color=C_AUTH, lw=2.0, ls=(0, (6, 3)))
    axzs.set_xlim(lo[0] - pad, hi[0] + pad)
    axzs.set_ylim(lo[1] - pad, hi[1] + pad)
    axzs.set_aspect("equal", adjustable="box")
    axzs.tick_params(labelsize=8)
    axzs.set_xlabel(lab[2] + " mm", fontsize=9)
    axzs.set_ylabel(lab[3] + " mm", fontsize=9)
    axzs.set_title("SURFACE, zoom on the failing stretch (%s)" % pname, fontsize=11)
    fresh = fmt_row("fresh run", "%d/%d" % (e["n_ours"], e["n_auth"]), "%.3f" % e["median"], "%.2f" % e["cov_ours"], "%.2f" % e["cov_auth"], e["jumps"])
    old = fmt_row("ticket 292", "%s/%s" % (e["n292"], e["n292a"]), e["median292"], e["cov292"], e["cov292a"], e["jumps292"])
    fig.suptitle("%s %s  Bl%d  --  our line and the authors line on the mesh and on the surface" % (pot, piece, lane), fontsize=15, y=0.975)
    fig.text(0.5, 0.938, fresh + "     |     " + old + "     |     delta median %+.3f mm, delta cov_ours %+.2f pp" % (e["d_median"], e["d_cov"]), ha="center", fontsize=11.5)
    if e.get("flag"):
        fig.text(0.5, 0.912, "READING MAY DIFFER FROM TICKET 292: " + e["flag"], ha="center", fontsize=11.5, color="#b00000")
    foot = ("commit %s  |  edge md5 %s  |  mesh md5 %s  |  theta %s  |  %s  |  surface shown %s (median %.2f mm)  |  faces drawn %d of %d, surface dots %d of %d (display decimation only)" % (e["commit"][:12], e["edge_md5"], e["mesh_md5"], e["theta"], e["classify"], sname, sdist, nf_drawn, nf_total, min(len(surf), MAXS), len(surf)))
    fig.text(0.5, 0.012, foot, ha="center", fontsize=8.2, color="#333333")
    name = "p293_%s_%s_Bl%d.png" % (pot.replace("Pot_", ""), piece.split("_Piece_")[1], lane)
    path = os.path.join(OUT, name)
    fig.savefig(path, dpi=100)
    plt.close(fig)
    print("[PNG] %s %dx%d %d bytes stretch=%d-%d arc=%.1fmm meangap=%.2fmm plane=%s surf=%s" % (path, 2300, 1340, os.path.getsize(path), i, j, arc, mean_gap, pname, sname))


def main():
    man = json.load(open(os.path.join(RUN, "out", "manifest.json")))
    want = sys.argv[2:]
    os.makedirs(OUT, exist_ok=True)
    for e in man["lanes"]:
        if want and e["piece"] not in want:
            continue
        render(e)
    return 0


if __name__ == "__main__":
    sys.exit(main())