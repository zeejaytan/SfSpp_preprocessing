
import sys, os
import numpy as np

def readxyz(path):
    pts = []
    with open(path, 'r', errors='ignore') as f:
        for ln in f:
            s = ln.split()
            if len(s) < 3: continue
            try: pts.append((float(s[0]), float(s[1]), float(s[2])))
            except ValueError: continue
    return np.array(pts, dtype=np.float64)

def cmp(mine, ref, label):
    if not os.path.exists(mine) or not os.path.exists(ref):
        print("%s MISSING mine=%s ref=%s" % (label, os.path.exists(mine), os.path.exists(ref)))
        return
    a = readxyz(mine); b = readxyz(ref)
    if len(a) != len(b):
        print("%s npoint differ mine=%d ref=%d" % (label, len(a), len(b)))
        return
    d_row = float(np.abs(a - b).max()) if len(a) else 0.0
    sa = a[np.lexsort((a[:, 2], a[:, 1], a[:, 0]))]
    sb = b[np.lexsort((b[:, 2], b[:, 1], b[:, 0]))]
    d_sort = float(np.abs(sa - sb).max()) if len(a) else 0.0
    print("%s n=%d max|dxyz|_row=%.6f max|dxyz|_sorted=%.6f" % (label, len(a), d_row, d_sort))

R = sys.argv[1]; T = "/data/gpfs/projects/punim2657"
specs = [("H02", "Pot_H", "02", "pota257_paper_Pot_H_02"),
         ("H10", "Pot_H", "10", "pota257_paper_Pot_H_10"),
         ("C03", "Pot_C", "03", "pota251_paper_Pot_C_03"),
         ("C01", "Pot_C", "01", "pota251_paper_Pot_C_01"),
         ("B01", "Pot_B", "01", "pota253_paper_Pot_B_01")]
for tag, pot, nn, tree in specs:
    outd = os.path.join(R, "out", tag + "_diag")
    for s in (0, 1):
        mine = os.path.join(outd, "%s_Surface_%d.xyz" % (pot + "_Piece_" + nn, s))
        cand = [os.path.join(T, tree, "Temp/Data", pot, "%s_Piece_%s_Surface_%d.xyz" % (pot, nn, s)),
                os.path.join(T, tree, "Dataset/Surfaces", pot, "%s_Piece_%s_Surface_%d.xyz" % (pot, nn, s))]
        ref = next((c for c in cand if os.path.exists(c)), cand[0])
        cmp(mine, ref, "%s_S%d" % (tag, s))
