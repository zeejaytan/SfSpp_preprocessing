import numpy as np, os
def lxyz(p, cols=3):
    r = []
    for ln in open(p):
        s = ln.strip()
        if not s or s[0] == '#': continue
        try: r.append(list(map(float, s.split()[:cols])))
        except ValueError: continue
    return np.array(r)
T = np.loadtxt(".scratch/pota162_repro/sfs_main/original_samples/SfS_pp/Ground Truth/Pot_C_Piece_1_T.txt")
R, t = T[:3,:3], T[:3,3]
print("C01 files:", sorted([f for f in os.listdir(".scratch/pota174_repro/run") if "C01" in f]))
S = lxyz(".scratch/pota174_repro/surf/Pot_C_Piece_01_Surface_0.xyz")
print("raw surf centroid", S.mean(0).round(1), "n=", len(S))
print("T(surf) centroid", (S @ R.T + t).mean(0).round(1))
G0 = lxyz(".scratch/pota162_repro/sfs_main/original_samples/SfS_pp/Breaklines/Pot_C_Piece_01_Breakline_0.pcd")
print("raw ORIG centroid", G0.mean(0).round(1))
print("T(ORIG) centroid", (G0 @ R.T + t).mean(0).round(1))
S2 = lxyz(".scratch/pota174_repro/run/C01_reclaim_S0.xyz")
print("run/C01_reclaim_S0 centroid", S2.mean(0).round(1), "n=", len(S2))
print("DONE")
