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
pairs = [("01","1"),("02","0"),("03","0"),("04","0"),("05","0"),("06","0")]
for tag in ["bl_D_A", "bl_D_Actl"]:
    for pc, br in pairs:
        ref = load_xyz(".scratch/pota174_repro/refs/Pot_A_Piece_%s_Breakline_%s.xyz" % (pc, br))
        for b in ["0", "1"]:
            A = load_xyz(".scratch/pota174_repro/%s/Pot_A_Piece_%s_Breakline_%s.xyz" % (tag, pc, b))
            if len(A) == 0: print("%s P%s Bl_%s EMPTY" % (tag, pc, b)); continue
            d1 = cKDTree(ref).query(A)[0]; d2 = cKDTree(A).query(ref)[0]
            print("%s P%s_%s n=%d loopcov%.3f med%.2f refcov=%.3f med%.2f" % (tag, pc, b, len(A), (d1<2).mean(), np.median(d1), (d2<2).mean(), np.median(d2)))
print("DONE")
