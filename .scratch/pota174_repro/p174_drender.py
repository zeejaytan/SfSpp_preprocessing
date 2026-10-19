import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
def load_xyz(p, cols=3):
    rows = []
    for ln in open(p):
        s = ln.strip()
        if not s or s[0] == '#': continue
        try: rows.append(list(map(float, s.split()[:cols])))
        except ValueError: continue
    return np.array(rows)
G0 = load_xyz(".scratch/pota162_repro/sfs_main/original_samples/SfS_pp/Breaklines/Pot_C_Piece_01_Breakline_0.pcd")
A = load_xyz(".scratch/pota174_repro/bl_D_Cctl/Pot_C_Piece_01_Breakline_0.xyz")
B = load_xyz(".scratch/pota174_repro/bl_D_C/Pot_C_Piece_01_Breakline_0.xyz")
fig = plt.figure(figsize=(10,9))
ax = fig.add_subplot(111, projection="3d")
ax.scatter(G0[:,0], G0[:,1], G0[:,2], s=4, c="black", label="ORIG 211")
ax.scatter(A[:,0], A[:,1], A[:,2], s=4, c="red", label="D0+noveto 351")
ax.scatter(B[:,0], B[:,1], B[:,2], s=12, c="blue", label="D6+noveto 21")
ax.legend(); ax.set_title("C01 veto-free loops vs ORIG (mesh frame)")
ax.view_init(elev=25, azim=-60)
plt.savefig("artifacts/pota174/C174_D_loops.png", dpi=80)
print("saved")
