import numpy as np, os
from scipy.spatial import cKDTree
H = ".scratch/pota174_repro"
S = H + "/surf"
def load_xyz(p, cols=3):
    rows = []
    for ln in open(p):
        s = ln.strip()
        if not s or s[0] == '#': continue
        try: rows.append(list(map(float, s.split()[:cols])))
        except ValueError: continue
    return np.array(rows)
def gate(A, B, tag):
    if len(A) == 0 or len(B) == 0:
        print("%s EMPTY a=%d b=%d" % (tag, len(A), len(B))); return
    d1 = cKDTree(B).query(A)[0]; d2 = cKDTree(A).query(B)[0]
    print("%s nA=%d nB=%d | A-vs-B cov%.3f med%.2f | B-vs-A cov%.3f med%.2f" % (tag, len(A), len(B), (d1<2).mean(), np.median(d1), (d2<2).mean(), np.median(d2)))
pairs = [("01","1"),("02","0"),("03","0"),("04","0"),("05","0"),("06","0")]
for pc, br in pairs:
    ref = load_xyz("%s/refs/Pot_A_Piece_%s_Breakline_%s.xyz" % (H, pc, br))
    for s in ["0","1"]:
        f = "%s/Pot_A_Piece_%s_Surface_%s.xyz" % (S, pc, s)
        if os.path.exists(f):
            gate(load_xyz(f), ref, "PA%s_S%s-vs-ref" % (pc, s))
G0 = load_xyz(".scratch/pota162_repro/sfs_main/original_samples/SfS_pp/Breaklines/Pot_C_Piece_01_Breakline_0.pcd")
for s in ["0","1"]:
    f = "%s/Pot_C_Piece_01_Surface_%s.xyz" % (S, s)
    if os.path.exists(f):
        gate(load_xyz(f), G0, "C01_S%s-vs-ORIGraw" % s)
print("DONE")
