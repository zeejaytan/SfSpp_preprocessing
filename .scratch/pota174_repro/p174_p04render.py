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
ref = load_xyz(".scratch/pota174_repro/refs/Pot_A_Piece_04_Breakline_0.xyz")
red = load_xyz(".scratch/pota174_repro/bl_D_Actl/Pot_A_Piece_04_Breakline_0.xyz")
blu = load_xyz(".scratch/pota174_repro/cure/Pot_A_Piece_04_Breakline_0.xyz")
fig = plt.figure(figsize=(10,9))
ax = fig.add_subplot(111, projection="3d")
ax.scatter(ref[:,0], ref[:,1], ref[:,2], s=5, c="black", label="ref 231")
ax.scatter(red[:,0], red[:,1], red[:,2], s=5, c="red", label="veto-free D0 145")
ax.scatter(blu[:,0], blu[:,1], blu[:,2], s=9, c="blue", label="cure")
ax.legend(); ax.set_title("P04_0: veto-free loop vs ref (tracker)")
plt.savefig("artifacts/pota174/C174_P04_0_tripwire.png", dpi=80)
print("saved n=", len(ref), len(red), len(blu))
