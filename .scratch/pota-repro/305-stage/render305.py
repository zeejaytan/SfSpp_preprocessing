#!/usr/bin/env python3
"""render305.py OUT_PNG TITLE LABEL=RESULTDIR ...
Result dirs: OBJ_*.obj are the RAW piece clouds; T_<i>to_<i>.txt (piece i+1) places
them in the assembly frame; Edgeline_*.xyz are already in that frame.
All panels share one view box (taken from the clouds, 1-99 pct) so panels are comparable;
stray edges outside that box are dropped."""
import sys, os, glob, re
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import cm

CAP = 900

def idx_of(fn, pat):
    m = re.search(pat, fn)
    return int(m.group(1)) if m else None

def load_obj(path):
    pts = []
    for line in open(path, "r", errors="ignore"):
        if line.startswith("v "):
            p = line.split()
            pts.append((float(p[1]), float(p[2]), float(p[3])))
    return np.asarray(pts, dtype=float)

def load_xyz(path):
    a = np.loadtxt(path)
    if a.ndim == 1:
        a = a[None, :]
    return a[:, :3]

def collect(rd, want_edges=True):
    byp = {}
    for f in sorted(glob.glob(os.path.join(rd, "*_OBJ_*.obj"))):
        i = idx_of(f, r"_OBJ_(\d+)\.obj$")
        if i is None:
            continue
        a = load_obj(f)
        if len(a):
            byp.setdefault(i, []).append(a)
    out = {}
    for i, parts in byp.items():
        a = np.vstack(parts)
        tf = os.path.join(rd, "T_%dto_%d.txt" % (i - 1, i - 1))
        if os.path.exists(tf):
            M = np.loadtxt(tf).reshape(4, 4)
            a = a @ M[:3, :3].T + M[:3, 3]
        out[i] = a
    eds = []
    if want_edges:
        for f in sorted(glob.glob(os.path.join(rd, "*_Edgeline_*.xyz"))):
            eds.append(load_xyz(f))
    return out, eds

def main():
    out, title = sys.argv[1], sys.argv[2]
    panels = [s.split("=", 1) for s in sys.argv[3:]]
    data = [(lab, rd) + collect(rd) for lab, rd in panels]
    allp = np.vstack([p for _, _, byp, _ in data for p in byp.values()])
    lo = np.percentile(allp, 1, axis=0); hi = np.percentile(allp, 99, axis=0)
    pad = 0.06 * max(hi - lo)
    lo -= pad; hi += pad
    n = len(data)
    fig = plt.figure(figsize=(5.6 * n, 10.4))
    for j, (lab, rd, byp, eds) in enumerate(data):
        for row, (ai, aj) in enumerate([(0, 1), (0, 2)]):
            ax = fig.add_subplot(2, n, row * n + j + 1)
            for i, p in sorted(byp.items()):
                c = cm.tab20((i - 1) % 20 / 19.0)
                q = p[:: max(1, len(p) // CAP)]
                ax.scatter(q[:, ai], q[:, aj], s=0.8, c=[c], linewidths=0, rasterized=True)
                sel = np.abs(q[:, ai] - np.median(q[:, ai])) < 0.5 * (hi[ai] - lo[ai])
                ax.text(np.median(q[sel, ai]) if sel.any() else np.median(q[:, ai]),
                        np.median(q[sel, aj]) if sel.any() else np.median(q[:, aj]),
                        str(i), fontsize=8, color="k", ha="center", va="center",
                        bbox=dict(fc="w", ec="none", alpha=0.6, pad=0.6))
            for e in eds:
                k = ((e[:, ai] > lo[ai]) & (e[:, ai] < hi[ai]) & (e[:, aj] > lo[aj]) & (e[:, aj] < hi[aj]))
                if k.sum() > 1:
                    ax.plot(e[k, ai], e[k, aj], "-", color="k", lw=0.8, alpha=0.9)
            ax.set_xlim(lo[ai], hi[ai]); ax.set_ylim(lo[aj], hi[aj])
            ax.set_aspect("equal", adjustable="box")
            ax.set_xticks([]); ax.set_yticks([])
            ax.set_title("%s  %s" % (lab, "top (x,y)" if row == 0 else "side (x,z)"), fontsize=9)
    fig.suptitle(title, fontsize=10)
    fig.tight_layout(rect=[0, 0, 1, 0.96])
    fig.savefig(out, dpi=140)
    print("wrote", out, os.path.getsize(out))

main()
