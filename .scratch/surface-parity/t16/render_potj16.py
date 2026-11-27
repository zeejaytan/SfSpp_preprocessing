#!/usr/bin/env python3
"""Ticket 16 render: five J01 arms side by side, locked camera, 20 mm bar per panel.

Uses the assembled per-piece meshes the Hierarchy-T13 run already wrote into
out/<ARM>_<rep>/*_OBJ_<p>.obj (already in the assembly frame, so no re-posing).  One panel
per arm, best of its two repeats, Pot_J_Piece_01 in red and every other sherd in a grey so
the Pot J seams stay readable.  Each panel is annotated with that repeat's joins and with
which of J01's five ground-truth seams were found.

Writes renders/Pot_J_handle_deleted_comparison.png (180 dpi) and evidence/renders.tsv.
"""
import argparse
import glob
import json
import os
import sys

import numpy as np

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from mpl_toolkits.mplot3d.art3d import Poly3DCollection  # noqa: E402

TAB, NL = chr(9), chr(10)
STEM = "Pot_J_Piece_01"
ARMS = ["CTL_T09_WITH_AUTHOR_J01", "OWN_NO_HANDLE_SHIP", "OWN_NO_HANDLE_THICKSEC",
        "OWN_VOXEL_THICKSEC", "OWN_S0_ONLY_SHIP"]
SHORT = {"CTL_T09_WITH_AUTHOR_J01": "CTL: Author J01",
         "OWN_NO_HANDLE_SHIP": "OWN: shipped selector",
         "OWN_NO_HANDLE_THICKSEC": "OWN: + thickness sec.",
         "OWN_VOXEL_THICKSEC": "OWN voxel: + thickness sec.",
         "OWN_S0_ONLY_SHIP": "OWN: S0 only, shipped"}
J01_EDGES = [(1, 3), (1, 4), (1, 5), (1, 6), (1, 7)]
GREY = ["#b9c0c8", "#c9cfd6", "#aab2bb", "#d3d8de"]
RED = "#d62728"
MAX_FACES = 900


def log(m):
    print("[t16-render] " + m, flush=True)


def read_tsv(path):
    with open(path) as fh:
        cols = fh.readline().rstrip(NL).split(TAB)
        return [dict(zip(cols, ln.rstrip(NL).split(TAB))) for ln in fh if ln.strip()]


def load_obj(path, max_faces=MAX_FACES):
    vs, fs = [], []
    with open(path) as fh:
        for ln in fh:
            if ln.startswith("v "):
                p = ln.split()
                vs.append((float(p[1]), float(p[2]), float(p[3])))
            elif ln.startswith("f "):
                idx = [int(t.split("/")[0]) for t in ln.split()[1:]]
                for k in range(1, len(idx) - 1):
                    fs.append((idx[0] - 1, idx[k] - 1, idx[k + 1] - 1))
    V = np.asarray(vs, dtype=float)
    F = np.asarray(fs, dtype=int)
    if len(V) == 0 or len(F) == 0:
        return V.reshape(0, 3), F.reshape(0, 3)
    step = max(1, int(np.ceil(len(F) / float(max_faces))))
    return V, F[::step]


def pieces_in(resdir):
    out = {}
    for p in glob.glob(os.path.join(resdir, "*_OBJ_*.obj")):
        try:
            n = int(os.path.basename(p).rsplit("_OBJ_", 1)[1].split(".")[0])
        except (IndexError, ValueError):
            continue
        out[n] = p
    return out


def seams_of(score):
    """(joins_ok, joins_total, J01 edges found, J01 edges expected) from a score305 table.

    score305 writes a piece block, then a join block introduced by its own header line, then
    SUMMARY; only the join block's five-column rows count here.
    """
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
            f = ln.split(TAB)
            if ln.startswith("#") or f[0].startswith("SUMMARY") or len(f) < 5:
                in_join = False
                continue
            try:
                i, j = int(f[0]), int(f[1])
            except ValueError:
                in_join = False
                continue
            tot += 1
            if f[4] == "PASS":
                ok += 1
            if i == 1 or j == 1:
                j01_tot += 1
                if f[4] == "PASS":
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
    ap.add_argument("--max-faces", type=int, default=MAX_FACES)
    a = ap.parse_args()
    run = os.path.abspath(a.run)
    panel = read_tsv(os.path.join(run, "logs", "panel16.tsv"))
    ev = os.path.join(run, "evidence")
    rdir = os.path.join(run, "renders")
    os.makedirs(rdir, exist_ok=True)
    os.makedirs(ev, exist_ok=True)

    chosen, loaded = {}, {}
    for arm in ARMS:
        r = best_rep(panel, arm)
        if r is None:
            raise SystemExit("no panel row for arm %s" % arm)
        resdir = os.path.join(run, "out", "%s_%s" % (arm, r["rep"]))
        pcs = pieces_in(resdir)
        if not pcs:
            raise SystemExit("no assembled OBJ under %s" % resdir)
        loaded[arm] = pcs
        chosen[arm] = r
        log("%-24s rep=%s pieces=%d %s" % (arm, r["rep"], len(pcs), resdir))

    lo = np.array([1e30, 1e30, 1e30])
    hi = -lo.copy()
    for arm in ARMS:
        for p, path in loaded[arm].items():
            V, _F = load_obj(path, 40)
            if len(V):
                lo = np.minimum(lo, V.min(axis=0))
                hi = np.maximum(hi, V.max(axis=0))
    pad = 0.04 * float(np.max(hi - lo))
    xlim = (lo[0] - pad, hi[0] + pad)
    ylim = (lo[1] - pad, hi[1] + pad)
    zlim = (lo[2] - pad, hi[2] + pad)
    dz, dy, dx = zlim[1] - zlim[0], ylim[1] - ylim[0], xlim[1] - xlim[0]
    bar = 20.0

    fig = plt.figure(figsize=(27.0, 6.4))
    fig.suptitle("Ticket 16 - Pot J with the handle deleted from OUR J01 surface "
                 "(best of 2 repeats per arm; Pot_J_Piece_01 red; locked camera)",
                 fontsize=15)
    n = len(ARMS)
    for i, arm in enumerate(ARMS):
        ax = fig.add_subplot(1, n, i + 1, projection="3d")
        r = chosen[arm]
        score = r.get("score", "")
        ok, tot, j01, j01_tot = seams_of(score)
        for p in sorted(loaded[arm]):
            V, F = load_obj(loaded[arm][p], a.max_faces)
            if len(F) == 0:
                continue
            col = RED if p == 1 else GREY[(p // 2) % len(GREY)]
            tri = V[F]
            pc = Poly3DCollection(tri, facecolors=col, edgecolors="none",
                                  linewidths=0.0, alpha=0.98, shade=False)
            ax.add_collection3d(pc)
        ax.set_xlim(*xlim)
        ax.set_ylim(*ylim)
        ax.set_zlim(*zlim)
        ax.set_box_aspect((dx, dy, dz))
        ax.view_init(elev=18, azim=-62)
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
    fig.subplots_adjust(left=0.005, right=0.995, bottom=0.01, top=0.86, wspace=0.02)
    fig.savefig(png, dpi=a.dpi)
    plt.close(fig)
    log("wrote %s (%d bytes)" % (png, os.path.getsize(png)))

    with open(os.path.join(ev, "renders.tsv"), "w") as fh:
        cols = ["name", "path", "description"]
        fh.write(TAB.join(cols) + NL)
        fh.write(TAB.join([
            "Pot_J_handle_deleted_comparison.png",
            "renders/Pot_J_handle_deleted_comparison.png",
            "five Best-of-2 Pot J assemblies; locked camera; J01 red; 20 mm scale bar"]) + NL)
    with open(os.path.join(run, "logs", "render16_status.json"), "w") as fh:
        json.dump({"png": png, "dpi": a.dpi, "max_faces": a.max_faces,
                   "limits": {"x": xlim, "y": ylim, "z": zlim},
                   "panels": {arm: {"rep": chosen[arm]["rep"],
                                    "joins": chosen[arm].get("_joins_ok"),
                                    "j01": chosen[arm].get("_j01")} for arm in ARMS}},
                  fh, indent=1)
    print("T16-RENDER-OK", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main() or 0)
