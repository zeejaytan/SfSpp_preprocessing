#!/usr/bin/env python3
"""Ticket 290 Phase 2/3 - does the frozen cloud drop into the shipped pipeline?

Scores both Pot J 09 lanes against the authors' reference with the project's own scorer
(score275.lane, imported by path), puts them beside ticket 289's exported lanes re-scored on
the same basis, measures how far the two runs' lines actually are from each other, and draws
the two-panel overlay.

Usage: score290.py <run-dir>
Reads:  <run>/out/lane{0,1}.pcd      this run's exports
        <run>/out/surface_{0,1}.xyz  kept faces, for the picture
        ticket 289's exports, the authors' reference breaklines
Writes: <run>/out/lane_table.txt, <run>/out/png/p290_J09.png
"""
import hashlib
import importlib.util
import os
import struct
import sys

import numpy as np

SCORE275 = "/data/gpfs/projects/punim2657/SfSpp/runs/20261024-0329_1308298_p275-walker/score275.py"
AUTH = "/data/gpfs/projects/punim2657/sfs_main/original_samples/SfS_pp/Breaklines/Pot_J_Piece_09_Breakline_%d.pcd"
RUN289 = "/data/gpfs/projects/punim2657/SfSpp/runs/20261024-2151_8e1e514_p289-p09"

# Quoted from ticket 289's Results table (draw 1 / draw 2), for the side-by-side only.
T289 = {0: {"n": "78 / 79", "med": "1.204 / 1.041", "cov_o": "75.64 / 70.89", "cov_a": "81.08 / 75.68", "jmp": "0 / 0"},
        1: {"n": "84 / 86", "med": "1.980 / 2.122", "cov_o": "51.19 / 48.84", "cov_a": "65.22 / 63.77", "jmp": "0 / 0"}}


def load_score275():
    spec = importlib.util.spec_from_file_location("score275", SCORE275)
    mod = importlib.util.module_from_spec(spec)
    argv = sys.argv
    sys.argv = ["x", "/nonexistent"]
    try:
        spec.loader.exec_module(mod)
    except SystemExit:
        pass
    finally:
        sys.argv = argv
    return mod


def md5(p):
    h = hashlib.md5()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 22), b""):
            h.update(b)
    return h.hexdigest()


def closed_len(a):
    if len(a) < 2:
        return 0.0
    d = np.sqrt(((a[1:] - a[:-1]) ** 2).sum(1)).sum()
    return float(d + np.sqrt(((a[0] - a[-1]) ** 2).sum()))


def main():
    run = sys.argv[1]
    sm = load_score275()
    out = os.path.join(run, "out")
    lines = []

    def emit(s=""):
        print(s)
        lines.append(s)

    emit("%-6s %-3s %5s %8s %8s %8s %5s %9s %9s  %s"
         % ("arm", "st", "n", "med", "cov_o", "cov_a", "jmp", "maxstep", "len_mm", "bar"))
    rec = {}
    for st in (0, 1):
        f = os.path.join(out, "lane%d.pcd" % st)
        o, a = sm.readpts(f), sm.readpts(AUTH % st)
        n, med, co, ca, j, mx, ok = sm.lane(o, a)
        rec[st] = dict(n=n, med=med, co=co, ca=ca, j=j, mx=mx, ok=ok,
                       len=closed_len(o), len_a=closed_len(a), md5=md5(f), pts=o)
        emit("%-6s %-3d %5d %8.3f %8.2f %8.2f %5d %9.3f %9.2f  %s"
             % ("290", st, n, med, co, ca, j, mx, rec[st]["len"], "PASS" if ok else "below"))
        p289 = os.path.join(RUN289, "out", "d1", "lane%d.pcd" % st)
        o9 = sm.readpts(p289)
        n9, med9, co9, ca9, j9, mx9, ok9 = sm.lane(o9, a)
        emit("%-6s %-3d %5d %8.3f %8.2f %8.2f %5d %9.3f %9.2f  %s"
             % ("289", st, n9, med9, co9, ca9, j9, mx9, closed_len(o9), "PASS" if ok9 else "below"))
        d_O, d_9 = sm.nn(o, o9), sm.nn(o9, o)
        emit("[VS289] Bl%d  290->289 max %.4f mean %.4f | 289->290 max %.4f mean %.4f mm"
             % (st, d_O.max(), d_O.mean(), d_9.max(), d_9.mean()))
        emit("[VS289] Bl%d  as recorded in ticket 289 (draw1 / draw2): n %s  med %s  cov_o %s  cov_a %s  jumps %s"
             % (st, T289[st]["n"], T289[st]["med"], T289[st]["cov_o"], T289[st]["cov_a"], T289[st]["jmp"]))
        emit("[AUTH]  Bl%d  authors n=%d len=%.2f mm  (bar = med<=2.0 and cov_o>=90)"
             % (st, len(a), rec[st]["len_a"]))
        emit("[LEN]   Bl%d  ours %.2f mm  authors %.2f mm  ratio %.3f   (289 export %.2f mm, ratio %.3f)"
             % (st, rec[st]["len"], rec[st]["len_a"], rec[st]["len"] / rec[st]["len_a"],
                closed_len(o9), closed_len(o9) / rec[st]["len_a"]))

    with open(os.path.join(out, "lane_table.txt"), "w") as fh:
        fh.write("\n".join(lines) + "\n")

    # ---- picture -------------------------------------------------------------
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    s0 = sm.readpts(os.path.join(out, "surface_0.xyz"))
    s1 = sm.readpts(os.path.join(out, "surface_1.xyz"))
    fig, axes = plt.subplots(1, 2, figsize=(11.5, 5.2), dpi=100)
    for k, ax in enumerate(axes):
        st = k
        a = sm.readpts(AUTH % st)
        o = rec[st]["pts"]
        o9 = sm.readpts(os.path.join(RUN289, "out", "d1", "lane%d.pcd" % st))
        ax.scatter(s0[:, 0], s0[:, 1], s=0.3, c="#c8d4e0", marker=".", label="our Surface_0", rasterized=True)
        ax.scatter(s1[:, 0], s1[:, 1], s=0.3, c="#f2cfa8", marker=".", label="our Surface_1", rasterized=True)
        for arr, col, lw, lab, z in ((a, "#000000", 2.2, "authors", 5),
                                     (o9, "#1f6fd0", 1.4, "289 (derived cloud)", 4),
                                     (o, "#00a000", 2.6, "290 (frozen cloud)", 6)):
            ax.plot(np.append(arr[:, 0], arr[0, 0]), np.append(arr[:, 1], arr[0, 1]),
                    "-", color=col, lw=lw, label=lab, zorder=z)
        ax.set_aspect("equal")
        ax.set_title("Bl%d  n %d  med %.3f mm  cov %.1f/%.1f  %s"
                     % (st, rec[st]["n"], rec[st]["med"], rec[st]["co"], rec[st]["ca"],
                        "PASS" if rec[st]["ok"] else "below bar"), fontsize=9)
        ax.set_xlabel("x (mm)", fontsize=8)
        ax.set_ylabel("y (mm)", fontsize=8)
        ax.tick_params(labelsize=7)
        if k == 0:
            ax.legend(fontsize=7, loc="best", framealpha=0.9)
    fig.suptitle("Pot J Piece 09 - frozen released cloud (green) vs ticket 289's derived draw (blue) vs authors (black); X-Y plan",
                 fontsize=9)
    fig.tight_layout(rect=(0, 0, 1, 0.94))
    png = os.path.join(out, "png", "p290_J09.png")
    os.makedirs(os.path.dirname(png), exist_ok=True)
    fig.savefig(png, dpi=100)
    plt.close(fig)
    with open(png, "rb") as fh:
        blob = fh.read()
    w, h = struct.unpack(">II", blob[16:24])
    print("[PNG] %s px=%dx%d bytes=%d md5=%s" % (png, w, h, len(blob), hashlib.md5(blob).hexdigest()))
    return 0


if __name__ == "__main__":
    sys.exit(main())
