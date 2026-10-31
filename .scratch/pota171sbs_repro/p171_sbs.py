import numpy as np, os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection

OUT = "artifacts/pota171sbs"
os.makedirs(".scratch/pota171sbs_repro", exist_ok=True); os.makedirs(OUT, exist_ok=True)

def load_obj(path):
    V, F = [], []
    with open(path) as fh:
        for ln in fh:
            if ln.startswith("v "): V.append([float(x) for x in ln.split()[1:4]])
            elif ln.startswith("f "):
                F.append([int(x.split("/")[0]) - 1 for x in ln.split()[1:4]])
    return np.array(V), np.array(F)

V, F = load_obj("temp_download/Mesh/Pot_A/Pot_A_Piece_02_Mesh.obj")
print("mesh", V.shape, F.shape, flush=True)
C = np.loadtxt("artifacts/pota171/Pot_A_Piece_02_Breakline_0_cure.xyz")[:, :3]
N = np.loadtxt("artifacts/pota171/Pot_A_Piece_02_Breakline_0_noveto.xyz")[:, :3]
print("cure", C.shape, "noveto", N.shape, flush=True)
print("mesh bbox", V.min(0).round(1), V.max(0).round(1), flush=True)

hi, lo = V.max(0), V.min(0)
ctr = (hi + lo) / 2
r = float(max(hi - lo)) / 2 * 1.02
LIM = [(ctr[i] - r, ctr[i] + r) for i in range(3)]

def draw(ax, walks, elev, azim, title):
    ax.add_collection3d(Poly3DCollection(V[F], facecolor=(0.72, 0.72, 0.74), edgecolor="none", alpha=0.9))
    for P, color, lw, label in walks:
        ax.plot(P[:, 0], P[:, 1], P[:, 2], color=color, lw=lw, label=label, zorder=10)
    ax.view_init(elev=elev, azim=azim)
    ax.set_title(title, fontsize=10)
    ax.set_box_aspect((1, 1, 1))
    ax.set_xlim(*LIM[0]); ax.set_ylim(*LIM[1]); ax.set_zlim(*LIM[2])
    ax.set_axis_off()
    ax.legend(fontsize=8, loc="upper left")

A = [(C, "blue", 1.8, "cured w/ veto (80 pts)")]
B = [(N, "red", 1.8, "veto-free (165 pts)")]
D = [(C, "blue", 1.8, "cured w/ veto (80)"), (N, "red", 1.5, "veto-free (165)")]
FULL = dict(elev=55, azim=-60)
jobs = [
    ("p171sbs_a_cured.png", A, "panel 1: P02 on its mesh, VETO-CURED trace (blue, 80 pts)"),
    ("p171sbs_b_noveto.png", B, "panel 2: P02 on its mesh, VETO-FREE trace (red, 165 pts)"),
    ("p171sbs_overlay.png", D, "overlay on the P02 mesh: cured veto (blue) vs veto-free (red)"),
]
for fn, walks, title in jobs:
    fig = plt.figure(figsize=(10, 8))
    ax = fig.add_subplot(111, projection="3d")
    draw(ax, walks, FULL["elev"], FULL["azim"], title)
    fig.tight_layout(); fig.savefig(os.path.join(OUT, fn), dpi=150); plt.close(fig)
    print("saved", fn, flush=True)
fig = plt.figure(figsize=(16, 8))
for k, (walks, title) in enumerate([(A, "cured w/ veto (blue, 80)"), (B, "veto-free (red, 165)")]):
    ax = fig.add_subplot(1, 2, k + 1, projection="3d")
    draw(ax, walks, FULL["elev"], FULL["azim"], "panel %d: %s" % (k + 1, title))
fig.suptitle("Pot A piece 02 on its mesh, same view (elev 55 / azim -60)", fontsize=11)
fig.tight_layout(); fig.savefig(os.path.join(OUT, "p171sbs_sbs.png"), dpi=150); plt.close(fig)
print("saved p171sbs_sbs.png", flush=True)
