import numpy as np
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.collections import PolyCollection
from scipy.spatial import cKDTree
H = ".scratch/pota172_repro"
OUT = "artifacts/pota172"
log = open(H + "/p172_step2.txt", "w")
def say(s):
    print(s, flush=True); log.write(s + "\n")

T = np.loadtxt(".scratch/pota162_repro/sfs_main/original_samples/SfS_pp/Ground Truth/Pot_C_Piece_1_T.txt")
R, t = T[:3,:3], T[:3,3]
def load_obj(path):
    V, F = [], []
    with open(path) as fh:
        for ln in fh:
            if ln.startswith("v "): V.append([float(x) for x in ln.split()[1:4]])
            elif ln.startswith("f "): F.append([int(x.split("/")[0]) - 1 for x in ln.split()[1:4]])
    return np.array(V), np.array(F, dtype=np.int64)
V, F = load_obj("temp_download/Mesh/Pot_C/Pot_C_Piece_01_Mesh_DS.obj")
Vg = V @ R.T + t
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
S = np.loadtxt(".scratch/pota163_repro/inputs/C01S0_STAGED.xyz")[:,:3] @ R.T + t
z = np.load(H + "/p172_meshgap.npz")
gidx, d_sheet, d_surf, d_bnd = z["gidx"], z["d_sheet"], z["d_surf"], z["d_bnd"]
runs = [tuple(map(int, r)) for r in z["runs"]]
csv = np.genfromtxt(".scratch/pota169_repro/p169_gapstations.csv", delimiter=",", skip_header=1)
fired = {int(r[0]): r[3] for r in csv}

# ---- 1. coverage plot ----
fig, ax = plt.subplots(figsize=(13, 4.5))
xs = np.arange(211)
sheet_full = np.full(211, np.nan); mesh_full = np.full(211, np.nan); fired_full = np.full(211, np.nan)
for k, st in enumerate(gidx):
    sheet_full[int(st)] = d_sheet[k]; mesh_full[int(st)] = d_surf[k]; fired_full[int(st)] = fired[int(st)]
for (a, b) in runs:
    ax.axvspan(a, b, color="red", alpha=0.08)
ax.plot(xs, sheet_full, ".", color="gray", ms=3, label="sheet sample dist (169)")
ax.plot(xs, fired_full, "x", color="orange", ms=3, label="fired-dot dist (169)")
ax.plot(xs, mesh_full, ".", color="green", ms=3, label="mesh triangle dist (172)")
ax.axhline(2.0, color="k", lw=1, label="2mm seat line")
ax.set_xlim(-2, 212); ax.set_ylim(0, 7)
ax.set_xlabel("ORIG Bl_0 station"); ax.set_ylabel("distance (mm)")
ax.set_title("p172: mesh-vs-sheet at 13 gap stations (red bands) -- green mesh curve hugs ~0, gray sheet rides 2-6mm")
ax.legend(fontsize=8, loc="upper right")
fig.tight_layout(); fig.savefig(OUT + "/p172_coverage.png", dpi=130); plt.close(fig)
say("saved p172_coverage.png")

# ---- 2-4. run closeups (R11, R3, R6): plane projection ----
def closeup(ri, tag):
    a, b = runs[ri]
    seg = np.arange(a, b + 1)
    P0 = G0[seg]
    C = P0.mean(0)
    U, Sv, Vt = np.linalg.svd(P0 - C, full_matrices=False)
    e1, e2 = Vt[0], Vt[1]
    def proj(P): return np.stack([(P - C) @ e1, (P - C) @ e2], 1)
    Q0 = proj(P0)
    # nearby mesh triangles (centroid within 14mm of span bbox center in 3D)
    cen = Vg[F].mean(1)
    K = cKDTree(cen)
    qq = K.query_ball_point(P0, 14.0)
    sel = np.unique(np.concatenate([np.asarray(q, dtype=np.int64) for q in qq if len(q)]))
    tris = [proj(Vg[F[i]]) for i in sel[:4000]]
    # nearby sheet samples
    KS = cKDTree(S)
    qs = KS.query_ball_point(P0, 14.0)
    ssel = np.unique(np.concatenate([np.asarray(q, dtype=np.int64) for q in qs if len(q)]))
    QS = proj(S[ssel]) if len(ssel) else np.zeros((0, 2))
    fig, ax = plt.subplots(figsize=(11, 8))
    if len(tris):
        ax.add_collection(PolyCollection(tris, facecolor=(0.75, 0.9, 0.75), edgecolor=(0.6, 0.8, 0.6), lw=0.2))
    ax.plot(QS[:, 0], QS[:, 1], ".", color="gray", ms=2, label="sheet samples")
    ax.plot(Q0[:, 0], Q0[:, 1], "o", color="green", ms=7, label="ORIG gap stations (MESH-HAS-IT)")
    for k, st in enumerate(seg):
        ax.text(Q0[k, 0], Q0[k, 1], str(st), fontsize=5, color="darkgreen")
    ax.set_aspect("equal"); ax.set_title("p172 run R%d stations %d..%d (n=%d): green ORIG on mesh triangulation beyond gray sheet edge" % (ri, a, b, len(seg)))
    ax.legend(fontsize=8, loc="best")
    fig.tight_layout(); fig.savefig(OUT + "/p172_runR%d%s.png" % (ri, tag), dpi=130); plt.close(fig)
    say("saved run R%d closeup: %d tris drawn, %d sheet pts" % (ri, len(tris), len(QS)))
closeup(11, "_46")
closeup(3, "_35")
closeup(6, "_32")

# ---- 5. overview: full mesh top view + spans ----
fig, ax = plt.subplots(figsize=(10, 8))
ax.triplot(Vg[:, 0], Vg[:, 1], F, color=(0.8, 0.8, 0.8), lw=0.05)
ax.plot(G0[:, 0], G0[:, 1], "k-", lw=0.8, label="ORIG Bl_0")
ax.plot(G0[gidx, 0], G0[gidx, 1], "o", color="green", ms=3, label="188 gap stations (all MESH-HAS-IT)")
ax.set_aspect("equal"); ax.set_title("p172 overview (gate XY): mesh triangulation under full ORIG rim, gap stations green")
ax.legend(fontsize=8, loc="best")
fig.tight_layout(); fig.savefig(OUT + "/p172_overview.png", dpi=130); plt.close(fig)
say("saved p172_overview.png")
log.close(); print("STEP2 DONE")
