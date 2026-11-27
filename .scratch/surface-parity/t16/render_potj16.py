#!/usr/bin/env python3
"""Ticket 16 render: five J01 arms side by side, locked camera, 20 mm bar per panel.

Hierarchy-T13 writes its per-piece OBJ files in RAW SCAN coordinates and records each piece
pose as T_<p-1>to_<p-1>.txt, so this script reads the decimated corpus meshes
(Pot_J_Piece_NN_Mesh_DS.obj), applies each piece pose, anchors every panel to the control
panel through one seated body sherd (piece 3) and only then draws.  Piece 1 is bright red and
the other sherds muted greys; each panel carries its joins and the J01 seams found.  Hard
assertions fail the render if the panels are not actually posed: panel 5 has to move its J01
centroid by more than 10 mm against panel 1, which untransformed meshes can never do.

Writes renders/Pot_J_handle_deleted_comparison.png (180 dpi) and evidence/renders.tsv.
"""
import argparse
import glob
import json
import os
import sys

import numpy as np
from scipy.spatial import cKDTree

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

TAB, NL = chr(9), chr(10)
STEM = "Pot_J_Piece_01"
ARMS = ["CTL_T09_WITH_AUTHOR_J01", "OWN_NO_HANDLE_SHIP", "OWN_NO_HANDLE_THICKSEC",
        "OWN_VOXEL_THICKSEC", "OWN_S0_ONLY_SHIP"]
SHORT = {"CTL_T09_WITH_AUTHOR_J01": "CTL: Author J01",
         "OWN_NO_HANDLE_SHIP": "OWN: shipped selector",
         "OWN_NO_HANDLE_THICKSEC": "OWN: + thickness sec.",
         "OWN_VOXEL_THICKSEC": "OWN voxel: + thickness sec.",
         "OWN_S0_ONLY_SHIP": "OWN: S0 only, shipped"}
GREY = ["#b9c0c8", "#c9cfd6", "#aab2bb", "#d3d8de"]
RED = "#d62728"
ANCHOR_PIECE = 3
MIN_PANEL_DIFF_MM = 10.0
MESH_DIR = "/data/gpfs/projects/punim2657/sfs_main/original_samples/SfS_pp/Mesh"
POINTS_PER_PANEL = 150000


def log(m):
    print("[t16-render] " + m, flush=True)


def read_tsv(path):
    with open(path) as fh:
        cols = fh.readline().rstrip(NL).split(TAB)
        return [dict(zip(cols, ln.rstrip(NL).split(TAB))) for ln in fh if ln.strip()]


def load_vertices(path):
    vs = []
    with open(path) as fh:
        for ln in fh:
            if ln.startswith("v "):
                p = ln.split()
                vs.append((float(p[1]), float(p[2]), float(p[3])))
    return np.asarray(vs, dtype=float)


def load_pose(path):
    T = np.loadtxt(path, dtype=float)
    if T.shape != (4, 4):
        raise SystemExit("pose %s has shape %s not (4, 4)" % (path, T.shape))
    return T


def apply_pose(V, T):
    return V @ T[:3, :3].T + T[:3, 3]


def piece_mesh_path(mesh_dir, p):
    return os.path.join(mesh_dir, "Pot_J_Piece_%02d_Mesh_DS.obj" % p)


def poses_in(resdir):
    out = {}
    for path in glob.glob(os.path.join(resdir, "T_*to_*.txt")):
        base = os.path.basename(path)
        try:
            a, b = base[2:-4].split("to_")
            p = int(a) + 1
        except (IndexError, ValueError):
            continue
        if int(b) != p - 1:
            continue
        if os.path.getsize(path) == 0:
            continue
        out[p] = path
    return out


def seams_of(score):
    if not os.path.exists(score):
        return 0, 21, [], 5
    ok, tot, j01, j01_tot, in_join = 0, 0, [], 0, False
    with open(score) as fh:
        for ln in fh:
            ln = ln.rstrip(NL)
            if ln.startswith("join_i" + TAB):
                in_join = True
                continue
            if not in_join or not ln.strip():
                continue
            fd = ln.split(TAB)
            if ln.startswith("#") or fd[0].startswith("SUMMARY") or len(fd) < 5:
                in_join = False
                continue
            try:
                i, j = int(fd[0]), int(fd[1])
            except ValueError:
                in_join = False
                continue
            tot += 1
            if fd[4] == "PASS":
                ok += 1
            if i == 1 or j == 1:
                j01_tot += 1
                if fd[4] == "PASS":
                    j01.append((i, j))
    return ok, tot, j01, j01_tot


def best_rep(panel, arm):
    cand = [r for r in panel if r["arm"] == arm]
    if not cand:
        return None
    cand.sort(key=lambda r: (-int(r["joins_ok"]), -int(r["j01_joins_ok"]), int(r["rep"])))
    return cand[0]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", required=True)
    ap.add_argument("--dpi", type=int, default=180)
    ap.add_argument("--mesh-dir", default=MESH_DIR)
    ap.add_argument("--points-per-panel", type=int, default=POINTS_PER_PANEL)
    ap.add_argument("--anchor-piece", type=int, default=ANCHOR_PIECE)
    a = ap.parse_args()
    run = os.path.abspath(a.run)
    panel = read_tsv(os.path.join(run, "logs", "panel16.tsv"))
    ev = os.path.join(run, "evidence")
    rdir = os.path.join(run, "renders")
    os.makedirs(rdir, exist_ok=True)
    os.makedirs(ev, exist_ok=True)

    chosen, raw, poses = {}, {}, {}
    for arm in ARMS:
        r = best_rep(panel, arm)
        if r is None:
            raise SystemExit("no panel row for arm %s" % arm)
        resdir = os.path.join(run, "out", "%s_%s" % (arm, r["rep"]))
        pc = poses_in(resdir)
        if a.anchor_piece not in pc:
            raise SystemExit("no pose for anchor piece %d under %s" % (a.anchor_piece, resdir))
        chosen[arm] = r
        poses[arm] = {p: load_pose(path) for p, path in pc.items()}
        raw[arm] = {}
        for p in sorted(pc):
            mp = piece_mesh_path(a.mesh_dir, p)
            if not os.path.exists(mp):
                log("%-24s piece %02d has a pose but no decimated mesh (%s)" % (arm, p, mp))
                continue
            raw[arm][p] = load_vertices(mp)
        if 1 not in raw[arm]:
            raise SystemExit("no J01 mesh for arm %s" % arm)
        log("%-24s rep=%s pieces=%d anchor=%d %s" % (arm, r["rep"], len(raw[arm]),
                                                    a.anchor_piece, resdir))

    asm = {}
    for arm in ARMS:
        asm[arm] = {p: apply_pose(raw[arm][p], poses[arm][p]) for p in raw[arm]}

    Tc = poses[ARMS[0]][a.anchor_piece]
    shift = {}
    for arm in ARMS:
        M = Tc @ np.linalg.inv(poses[arm][a.anchor_piece])
        shift[arm] = float(np.linalg.norm(M[:3, 3]))
        if arm != ARMS[0]:
            asm[arm] = {p: apply_pose(V, M) for p, V in asm[arm].items()}
    log("anchor piece %d: panel shifts (mm) %s" % (a.anchor_piece,
                                                   {k: round(v, 2) for k, v in shift.items()}))

    j01_c = {arm: asm[arm][1].mean(axis=0) for arm in ARMS}
    diff = {arm: float(np.linalg.norm(j01_c[arm] - j01_c[ARMS[0]])) for arm in ARMS}
    max_panel_diff = max(diff.values())
    log("J01 centroid shift against CTL (mm): %s" %
        {k: round(v, 2) for k, v in diff.items()})
    if diff[ARMS[4]] <= MIN_PANEL_DIFF_MM:
        raise SystemExit("panel 5 J01 centroid moved only %.3f mm (need more than %.1f): meshes likely untransformed" % (diff[ARMS[4]], MIN_PANEL_DIFF_MM))
    if max_panel_diff <= MIN_PANEL_DIFF_MM:
        raise SystemExit("max_panel_diff %.3f mm is not above %.1f: meshes likely untransformed" % (max_panel_diff, MIN_PANEL_DIFF_MM))

    prox = {}
    for arm in ARMS:
        body = np.concatenate([V for p, V in asm[arm].items() if p != 1])
        if len(body) > 40000:
            body = body[::int(np.ceil(len(body) / 40000.0))]
        j1 = asm[arm][1]
        if len(j1) > 5000:
            j1 = j1[::int(np.ceil(len(j1) / 5000.0))]
        d, _ = cKDTree(body).query(j1)
        prox[arm] = float(np.median(d))
    log("J01 median distance to the other sherds (mm): %s" %
        {k: round(v, 2) for k, v in prox.items()})

    lo = np.array([1e30, 1e30, 1e30])
    hi = -lo.copy()
    for arm in ARMS:
        for V in asm[arm].values():
            lo = np.minimum(lo, V.min(axis=0))
            hi = np.maximum(hi, V.max(axis=0))
    pad = 0.04 * float(np.max(hi - lo))
    xlim = (lo[0] - pad, hi[0] + pad)
    ylim = (lo[1] - pad, hi[1] + pad)
    zlim = (lo[2] - pad, hi[2] + pad)
    dz, dy, dx = zlim[1] - zlim[0], ylim[1] - ylim[0], xlim[1] - xlim[0]
    bar = 20.0

    fig = plt.figure(figsize=(27.0, 6.6))
    title = ("Ticket 16 - Pot J with the handle deleted from OUR J01 surface "
             "(posed decimated scans; best of 2 repeats; Piece 01 red; locked camera)")
    fig.suptitle(title, fontsize=15)
    n = len(ARMS)
    for i, arm in enumerate(ARMS):
        ax = fig.add_subplot(1, n, i + 1, projection="3d")
        r = chosen[arm]
        ok, tot, j01, j01_tot = seams_of(r.get("score", ""))
        pts = sum(len(V) for V in asm[arm].values())
        step = max(1, int(np.ceil(pts / float(a.points_per_panel))))
        for p in sorted(asm[arm]):
            V = asm[arm][p][::step]
            if p == 1:
                continue
            ax.scatter(V[:, 0], V[:, 1], V[:, 2], s=0.55,
                       c=GREY[(p // 2) % len(GREY)], marker=".", linewidths=0,
                       depthshade=True, edgecolors="none")
        J1 = asm[arm][1][::max(1, step)]
        ax.scatter(J1[:, 0], J1[:, 1], J1[:, 2], s=1.3, c=RED, marker=".",
                   linewidths=0, depthshade=False, edgecolors="none")
        ax.set_xlim(*xlim)
        ax.set_ylim(*ylim)
        ax.set_zlim(*zlim)
        ax.set_box_aspect((dx, dy, dz))
        ax.view_init(elev=14, azim=-68)
        ax.set_axis_off()
        ax.plot([xlim[0] + 0.04 * dx, xlim[0] + 0.04 * dx + bar],
                [ylim[0] + 0.05 * dy, ylim[0] + 0.05 * dy],
                [zlim[0], zlim[0]], color="black", linewidth=4)
        ax.text(xlim[0] + 0.04 * dx, ylim[0] + 0.08 * dy, zlim[0], "20 mm",
                fontsize=9, color="black")
        found = ",".join("%d-%d" % e for e in sorted(j01)) if j01 else "none"
        ax.set_title("%s\nrepeat %s: %d/%d joins, J01 %d/%d\nJ01 seams: %s"
                     % (SHORT.get(arm, arm), r["rep"], ok, tot or 21, len(j01),
                        j01_tot or 5, found), fontsize=10)
        log("%-24s rep=%s joins=%d/%d j01=%d/%d seams=%s"
            % (arm, r["rep"], ok, tot, len(j01), j01_tot, found))
        r["_joins_ok"] = ok
        r["_joins_total"] = tot or 21
        r["_j01"] = found

    png = os.path.join(rdir, "Pot_J_handle_deleted_comparison.png")
    fig.subplots_adjust(left=0.005, right=0.995, bottom=0.01, top=0.85, wspace=0.02)
    fig.savefig(png, dpi=a.dpi)
    plt.close(fig)
    log("wrote %s (%d bytes)" % (png, os.path.getsize(png)))

    with open(os.path.join(ev, "renders.tsv"), "w") as fh:
        cols = ["name", "path", "description"]
        fh.write(TAB.join(cols) + NL)
        fh.write(TAB.join([
            "Pot_J_handle_deleted_comparison.png",
            "renders/Pot_J_handle_deleted_comparison.png",
            "five Best-of-2 Pot J assemblies; posed decimated scans; locked camera; J01 red; 20 mm scale bar"]) + NL)
    with open(os.path.join(run, "logs", "render16_status.json"), "w") as fh:
        json.dump({"png": png, "dpi": a.dpi, "points_per_panel": a.points_per_panel,
                   "mesh_dir": a.mesh_dir, "anchor_piece": a.anchor_piece,
                   "limits": {"x": xlim, "y": ylim, "z": zlim},
                   "panel_shift_mm": shift, "j01_centroid_shift_mm": diff,
                   "max_panel_diff_mm": max_panel_diff,
                   "j01_to_body_median_mm": prox,
                   "panels": {arm: {"rep": chosen[arm]["rep"],
                                    "joins": chosen[arm].get("_joins_ok"),
                                    "j01": chosen[arm].get("_j01")} for arm in ARMS}},
                  fh, indent=1)
    print("T16-RENDER-OK", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main() or 0)
