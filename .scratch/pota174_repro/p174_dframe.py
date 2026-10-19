import numpy as np
def load_xyz(p, cols=3):
    rows = []
    for ln in open(p):
        s = ln.strip()
        if not s or s[0] == '#': continue
        try: rows.append(list(map(float, s.split()[:cols])))
        except ValueError: continue
    return np.array(rows)
T = np.loadtxt(".scratch/pota162_repro/sfs_main/original_samples/SfS_pp/Ground Truth/Pot_C_Piece_1_T.txt")
R, t = T[:3,:3], T[:3,3]
G0 = load_xyz(".scratch/pota162_repro/sfs_main/original_samples/SfS_pp/Breaklines/Pot_C_Piece_01_Breakline_0.pcd")
A = load_xyz(".scratch/pota174_repro/bl_D_Cctl/Pot_C_Piece_01_Breakline_0.xyz")
B = load_xyz(".scratch/pota174_repro/bl_D_C/Pot_C_Piece_01_Breakline_0.xyz")
print("G0raw", G0.mean(0).round(1))
print("Dctl", A.mean(0).round(1))
print("Drec", B.mean(0).round(1))
print("T(G0)", (G0 @ R.T + t).mean(0).round(1))
from scipy.spatial import cKDTree
for tag, X in [("Dctl-vs-TORIG", A), ("Drec-vs-TORIG", B)]:
    G = G0 @ R.T + t
    d1 = cKDTree(G).query(X)[0]; d2 = cKDTree(X).query(G)[0]
    print("%s n=%d loopcov%.3f med%.2f ORIGcov=%d/211 med%.2f" % (tag, len(X), (d1<2).mean(), np.median(d1), int((d2<2).sum()), np.median(d2)))
print("DONE")
