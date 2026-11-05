
import sys, numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

S = "C:/Users/hermi/AppData/Local/Temp/surf306"
ST = "C:/PR/worktrees/sfs/306/.scratch/pota-repro/306-stage/out"
OUT = "C:/PR/SfSpp_preprocessing/artifacts/pota306/pota_axes_before_after.png"

def surf(p, w):
    return np.loadtxt(f"{S}/Pot_A_Piece_{p}_Surface_{w}.xyz", ndmin=2).T[:3]

def axes(path):
    A = np.loadtxt(path, ndmin=2)
    return A.T if A.size else np.zeros((6, 1))

def ang(a, b):
    c = abs(float(np.dot(a, b)) / (np.linalg.norm(a) * np.linalg.norm(b)))
    return float(np.degrees(np.arccos(min(1.0, c))))

fig = plt.figure(figsize=(13, 10))
for r, p in enumerate(["07", "08"]):
    C0, C1 = surf(p, 0), surf(p, 1)
    allp = np.hstack([C0, C1]); ctr = allp.mean(axis=1)
    rad = np.linalg.norm(allp - ctr[:, None], axis=0).max() * 1.25
    rel = axes(f"{ST}/rel/Pot_A_Piece_{p}_Axis.xyz")
    tr = axes(f"{ST}/c3pt/Pot_A_Piece_{p}_Axis.xyz")
    wh = axes(f"{ST}/c3pw/Pot_A_Piece_{p}_Axis.xyz")
    for c, (ttl, elev, azim) in enumerate([("view 1", 22, -60), ("view 2", 70, 20)]):
        ax = fig.add_subplot(2, 2, r * 2 + c + 1, projection="3d")
        ax.scatter(*C0, s=0.6, c="#9aa0a6", label="wall 0 (grey)")
        ax.scatter(*C1, s=0.6, c="#7fb3d5", label="wall 1 (blue)")
        for k in range(rel.shape[1]):
            d = rel[3:6, k]; d = d / np.linalg.norm(d)
            a, b = ctr - rad * d, ctr + rad * d
            ax.plot(*zip(a, b), color="k", ls="--", lw=1.0,
                    label="released" if k == 0 else None)
        for k in range(tr.shape[1]):
            d = tr[3:6, k]; d = d / np.linalg.norm(d)
            a, b = ctr - rad * d, ctr + rad * d
            ax.plot(*zip(a, b), color="#c0392b", lw=2.2,
                    label="ours, equal-count cut (today)" if k == 0 else None)
        for k in range(wh.shape[1]):
            d = wh[3:6, k]; d = d / np.linalg.norm(d)
            a, b = ctr - rad * d, ctr + rad * d
            ax.plot(*zip(a, b), color="#1f4fd8", lw=2.2, ls="-",
                    label="ours, walls whole (B1)" if k == 0 else None)
        ax.view_init(elev=elev, azim=azim)
        ax.set_xticklabels([]); ax.set_yticklabels([]); ax.set_zticklabels([])
        ax.set_title(f"Pot A piece {p} - {ttl}", fontsize=10)
        if r == 0 and c == 0:
            handles, labels = ax.get_legend_handles_labels()
            fig.legend(handles, labels, loc="lower center", ncol=5, fontsize=9,
                       frameon=False)
fig.suptitle("Pot A 07/08: released axes (dashed black) vs the axes we write\n"
             "red = today's equal-count cut, blue = walls whole (ticket 306 B1)", fontsize=11)
fig.tight_layout(rect=[0, 0.05, 1, 0.95])
fig.savefig(OUT, dpi=150)
print("wrote", OUT)

# the numbers behind the picture
for p in ["07", "08"]:
    rel = axes(f"{ST}/rel/Pot_A_Piece_{p}_Axis.xyz")
    for name, f in (("cut", "c3pt"), ("whole", "c3pw")):
        O = axes(f"{ST}/{f}/Pot_A_Piece_{p}_Axis.xyz")
        cov = [min(ang(rel[3:6, j], O[3:6, i]) for i in range(O.shape[1]))
               for j in range(rel.shape[1])]
        print(f"piece {p} {name:5s} K={O.shape[1]} released-line coverage (deg): "
              + ", ".join("%.2f" % c for c in cov))