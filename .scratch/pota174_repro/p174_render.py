import numpy as np, os
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
from scipy.spatial import cKDTree
OUT = "artifacts/pota174"
os.makedirs(OUT, exist_ok=True)
log = open(".scratch/pota174_repro/p174_render.txt", "w")
def say(s):
    print(s, flush=True); log.write(s + "\n")
def load_obj(path):
    V, F = [], []
    with open(path) as fh:
        for ln in fh:
            if ln.startswith("v "): V.append([float(x) for x in ln.split()[1:4]])
            elif ln.startswith("f "):
                try: F.append([int(x.split("/")[0]) - 1 for x in ln.split()[1:4]])
                except ValueError: pass
    return np.array(V), np.array(F, dtype=np.int64)
def load_xyz(p, cols=3):
    rows = []
    for ln in open(p):
        s = ln.strip()
        if not s or s[0] == '#': continue
        try: rows.append(list(map(float, s.split()[:cols])))
        except ValueError: continue
    return np.array(rows)
def mesh_lim(V):
    hi, lo = V.max(0), V.min(0); ctr = (hi + lo) / 2
    r = float(max(hi - lo)) / 2 * 1.03
    return [(ctr[i] - r, ctr[i] + r) for i in range(3)]
# ---- C01 coverage + top view ----
T = np.loadtxt(".scratch/pota162_repro/sfs_main/original_samples/SfS_pp/Ground Truth/Pot_C_Piece_1_T.txt")
R, t = T[:3,:3], T[:3,3]
def load_pcd3(p):
    HDR = ('VERSION','FIELDS','SIZE','TYPE','COUNT','WIDTH','HEIGHT','VIEWPOINT','POINTS','DATA')
    P = []
    for ln in open(p):
        s = ln.strip()
        if not s or s[0] == '#' or s.split()[0] in HDR: continue
        try: P.append(list(map(float, s.split()[:3])))
        except ValueError: continue
    return np.array(P)
G0 = load_pcd3(".scratch/pota162_repro/sfs_main/original_samples/SfS_pp/Breaklines/Pot_C_Piece_01_Breakline_0.pcd") @ R.T + t
runs = [(0,1),(3,21),(23,30),(34,68),(72,81),(83,88),(93,124),(126,136),(139,143),(145,147),(151,156),(158,203),(206,210)]
gidx = np.concatenate([np.arange(a,b+1) for a,b in runs])
G = G0[gidx]
Sctl = load_xyz(".scratch/pota163_repro/inputs/C01S0_STAGED.xyz")[:, :3] @ R.T + t
Src = load_xyz(".scratch/pota174_repro/run/C01_reclaim_S0.xyz")[:, :3] @ R.T + t
dctl = cKDTree(Sctl).query(G)[0]; drc = cKDTree(Src).query(G)[0]
fig, ax = plt.subplots(figsize=(13, 4.5))
xs = np.arange(211)
for (a, b) in runs: ax.axvspan(a, b, color="red", alpha=0.08)
fctl = np.full(211, np.nan); frc = np.full(211, np.nan)
for k, st in enumerate(gidx): fctl[int(st)] = dctl[k]; frc[int(st)] = drc[k]
ax.plot(xs, fctl, ".", color="gray", ms=4, label="control S0 (staged, 7/188)")
ax.plot(xs, frc, ".", color="green", ms=4, label="reclaim S0 (188/188)")
ax.axhline(2.0, color="black", lw=1)
ax.set_xlabel("ORIG station"); ax.set_ylabel("sheet-station dist (mm)")
ax.legend(fontsize=8); ax.set_title("C01 rim reach: control vs reclaimed S0 (188 gap stations)")
fig.savefig(OUT + "/C174_C01_coverage.png", dpi=110); plt.close(fig)
say("C01 coverage: ctl<2 %d/188, reclaim<2 %d/188" % (int((dctl<2).sum()), int((drc<2).sum())))
V, F = load_obj("temp_download/Mesh/Pot_C/Pot_C_Piece_01_Mesh_DS.obj")
Vg = V @ R.T + t
fig = plt.figure(figsize=(9, 8)); ax = fig.add_subplot(111, projection="3d")
ax.add_collection3d(Poly3DCollection(Vg[F], facecolor=(0.72,0.72,0.74), edgecolor="none", alpha=0.55))
ok = drc < 2
ax.scatter(G[ok,0], G[ok,1], G[ok,2], c="green", s=8, label="station<2mm (%d)" % int(ok.sum()))
ax.scatter(G[~ok,0], G[~ok,1], G[~ok,2], c="red", s=20, label="station>=2mm (%d)" % int((~ok).sum()))
LIM = mesh_lim(Vg)
ax.set_xlim(*LIM[0]); ax.set_ylim(*LIM[1]); ax.set_zlim(*LIM[2])
ax.view_init(elev=-90, azim=-90); ax.set_axis_off(); ax.legend(fontsize=8)
ax.set_title("C01 reclaim: 188 gap stations vs sheet (top view)")
fig.savefig(OUT + "/C174_C01_top.png", dpi=110); plt.close(fig)
say("C01 top view saved")
# ---- tripwire overlays ----
for pc, br, meshf in [("02","0","temp_download/Mesh/Pot_A/Pot_A_Piece_02_Mesh.obj"),("03","0","temp_download/Mesh/Pot_A/Pot_A_Piece_03_Mesh.obj"),("01","1","temp_download/Mesh/Pot_A/Pot_A_Piece_01_Mesh.obj")]:
    V, F = load_obj(meshf)
    F = F[(F >= 0).all(1) & (F < len(V)).all(1)]
    ref = load_xyz(".scratch/pota174_repro/refs/Pot_A_Piece_%s_Breakline_%s.xyz" % (pc, br))
    red = load_xyz("artifacts/pota171/Pot_A_Piece_%s_Breakline_%s_noveto.xyz" % (pc, br))
    blue = load_xyz(".scratch/pota174_repro/cure/Pot_A_Piece_%s_Breakline_%s.xyz" % (pc, br))
    fig = plt.figure(figsize=(9, 8)); ax = fig.add_subplot(111, projection="3d")
    ax.add_collection3d(Poly3DCollection(V[F], facecolor=(0.72,0.72,0.74), edgecolor="none", alpha=0.55))
    ax.plot(ref[:,0], ref[:,1], ref[:,2], color="gray", lw=1.5, label="ref (%d)" % len(ref))
    ax.plot(red[:,0], red[:,1], red[:,2], color="red", lw=1.2, label="red noveto (%d)" % len(red))
    ax.plot(blue[:,0], blue[:,1], blue[:,2], color="blue", lw=1.2, label="blue cure (%d)" % len(blue))
    LIM = mesh_lim(V)
    ax.set_xlim(*LIM[0]); ax.set_ylim(*LIM[1]); ax.set_zlim(*LIM[2])
    ax.view_init(elev=20, azim=-60); ax.set_axis_off(); ax.legend(fontsize=8)
    ax.set_title("P%s_%s tripwire: ref vs noveto(red) vs cure(blue)" % (pc, br))
    fig.savefig(OUT + "/C174_P%s_%s_tripwire.png" % (pc, br), dpi=110); plt.close(fig)
    say("tripwire P%s_%s saved" % (pc, br))
say("DONE")
