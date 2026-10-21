"""POTA-227 local scoring: P27@12 slot matrix + med/cov/jumps/gapmax/endgap (209 pattern)."""
import numpy as np
from scipy.spatial import cKDTree
B = "C:/PR/SfSpp_preprocessing/.scratch/"

def load_pcd(p):
    with open(p, "rb") as f: data = f.read().replace(b"\r\n", b"\n")
    head, _, body = data.partition(b"DATA ascii\n")
    nf = 3
    for ln in head.decode("ascii", errors="replace").splitlines():
        if ln.startswith("FIELDS"): nf = len(ln.split()) - 1
    return np.fromstring(body.decode("ascii", errors="replace"), sep=" ").reshape(-1, nf)[:, :3]

def stats(our, auth):
    dd, _ = cKDTree(auth).query(our)
    gaps = np.linalg.norm(np.diff(our, axis=0), axis=1)
    eg = float(np.linalg.norm(our[0] - our[-1])) if len(our) else 0.0
    return (round(float(np.median(dd)), 2), round(float((dd < 2.0).mean() * 100), 1),
            round(float(dd.max()), 1), int((gaps > 10.0).sum()),
            round(float(gaps.max()) if gaps.size else 0.0, 1), round(eg, 1), len(our))

L = [load_pcd(B + "pota227/lanes/Pot_D_Piece_27_Breakline_0.pcd"),
     load_pcd(B + "pota227/lanes/Pot_D_Piece_27_Breakline_1.pcd")]
A = [load_pcd(B + "pota225/Pot_D_Piece_27_Breakline_0_author.pcd"),
     load_pcd(B + "pota225/Pot_D_Piece_27_Breakline_1_author.pcd")]
print("P27@12 refs o0=%d o1=%d n0=%d n1=%d" % (len(A[0]), len(A[1]), len(L[0]), len(L[1])))
sums_straight = 0.0; sums_swap = 0.0
for i in [0, 1]:
    for j in [0, 1]:
        m, c, mx, jmp, gm, eg, n = stats(L[i], A[j])
        print("  SLOT o%d->a%d med=%.2f cov=%.1f max=%.1f jumps=%d gapmax=%.1f endgap=%.1f n=%d" % (i, j, m, c, mx, jmp, gm, eg, n))
        if i == j: sums_straight += m
        else: sums_swap += m
print("straight=%.2f swapped=%.2f => %s" % (sums_straight, sums_swap, "STRAIGHT" if sums_straight < sums_swap else "SWAPPED"))
print("RESCORE227-OK")
