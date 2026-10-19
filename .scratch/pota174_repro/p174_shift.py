import numpy as np
from scipy.spatial import cKDTree
def load(p, cols=3):
    rows = []
    for ln in open(p):
        s = ln.strip()
        if not s or s[0] == '#': continue
        try: rows.append(list(map(float, s.split()[:cols])))
        except ValueError: continue
    return np.array(rows)
for pc, br in [("01","1"),("02","0"),("03","0"),("04","0"),("05","0"),("06","0")]:
    B = load(".scratch/pota174_repro/bundle/Pot_A_Piece_%s_Breakline_%s.xyz" % (pc, br))
    W = load(".scratch/pota174_repro/refs/Pot_A_Piece_%s_Breakline_%s.xyz" % (pc, br))
    off = B.mean(0) - W.mean(0)
    A = B - off
    d1 = cKDTree(W).query(A)[0]; d2 = cKDTree(A).query(W)[0]
    print("P%s_%s shift=%s | after-shift: bun-vs-ref cov%.3f med%.2f | ref-vs-bun cov%.3f med%.2f" % (pc, br, np.round(off,2), (d1<2).mean(), np.median(d1), (d2<2).mean(), np.median(d2)))
