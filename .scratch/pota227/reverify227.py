"""POTA-227 re-verification of cited lane scores (209 pattern, xyz- or pcd-capable)."""
import numpy as np, os
from scipy.spatial import cKDTree
B = "C:/PR/SfSpp_preprocessing/.scratch/"

def load_any(p):
    if p.endswith(".pcd"):
        with open(p, "rb") as f: data = f.read().replace(b"\r\n", b"\n")
        head, _, body = data.partition(b"DATA ascii\n")
        nf = 3
        for ln in head.decode("ascii", errors="replace").splitlines():
            if ln.startswith("FIELDS"): nf = len(ln.split()) - 1
        return np.fromstring(body.decode("ascii", errors="replace"), sep=" ").reshape(-1, nf)[:, :3]
    pts = []
    with open(p) as f:
        for ln in f:
            s = ln.split()
            if len(s) >= 3:
                try: pts.append([float(x) for x in s[:3]])
                except ValueError: pass
    return np.array(pts)

def stats(our, auth):
    dd, _ = cKDTree(auth).query(our)
    gaps = np.linalg.norm(np.diff(our, axis=0), axis=1)
    eg = float(np.linalg.norm(our[0] - our[-1])) if len(our) else 0.0
    return (round(float(np.median(dd)), 2), round(float((dd < 2.0).mean() * 100), 1),
            round(float(dd.max()), 1), int((gaps > 10.0).sum()),
            round(float(gaps.max()) if gaps.size else 0.0, 1), round(eg, 1), len(our))

jobs = [
    ("P12@4.5", B+"pota223/lanes/Pot_D_Piece_12_Breakline_%d.pcd", B+"pota221/pota221f/author/Pot_D_Piece_12_Breakline_%d.pcd"),
    ("P15@8", B+"pota222/lanes/Pot_D_Piece_15_Breakline_%d.xyz", B+"pota221/pota221f/author/Pot_D_Piece_15_Breakline_%d.pcd"),
    ("P16@10", B+"pota222/lanes/Pot_D_Piece_16_Breakline_%d.xyz", B+"pota221/pota221f/author/Pot_D_Piece_16_Breakline_%d.pcd"),
    ("P01@8", B+".wt-220/artifacts/pota220/p01_8_Bl%d.pcd", B+".wt-220/artifacts/pota220/p01_author_Bl%d.pcd"),
]
for tag, lp, ap in jobs:
    try:
        L = [load_any(lp % 0), load_any(lp % 1)]
        A = [load_any(ap % 0), load_any(ap % 1)]
    except Exception as e:
        print(tag, "LOAD-FAIL", e); continue
    print("%s refs o0=%d o1=%d n0=%d n1=%d" % (tag, len(A[0]), len(A[1]), len(L[0]), len(L[1])))
    sm = {}
    for i in [0,1]:
        for j in [0,1]:
            m,c,mx,jmp,gm,eg,n = stats(L[i], A[j]); sm[(i,j)]=(m,c)
            print("  SLOT o%d->a%d med=%.2f cov=%.1f max=%.1f jumps=%d gapmax=%.1f endgap=%.1f n=%d" % (i,j,m,c,mx,jmp,gm,eg,n))
    st = sm[(0,0)][0]+sm[(1,1)][0]; sw = sm[(0,1)][0]+sm[(1,0)][0]
    print("  straight=%.2f swapped=%.2f => %s" % (st, sw, "STRAIGHT" if st < sw else "SWAPPED"))
print("REVERIFY227-OK")
