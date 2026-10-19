import numpy as np
from scipy.spatial import cKDTree
def load_xyz(p, cols=3):
    rows = []
    for ln in open(p):
        s = ln.strip()
        if not s or s[0] == '#': continue
        try: rows.append(list(map(float, s.split()[:cols])))
        except ValueError: continue
    return np.array(rows)
G0 = load_xyz(".scratch/pota162_repro/sfs_main/original_samples/SfS_pp/Breaklines/Pot_C_Piece_01_Breakline_0.pcd")
for tag in ["bl_D_C", "bl_D_Cctl"]:
    for b in ["0", "1"]:
        A = load_xyz(".scratch/pota174_repro/%s/Pot_C_Piece_01_Breakline_%s.xyz" % (tag, b))
        d1 = cKDTree(G0).query(A)[0]; d2 = cKDTree(A).query(G0)[0]
        print("%s Bl_%s n=%d | loop-vs-ORIG cov%.3f med%.2f | ORIGcov=%d/211 med%.2f" % (tag, b, len(A), (d1<2).mean(), np.median(d1), int((d2<2).sum()), np.median(d2)))
print("DONE")
