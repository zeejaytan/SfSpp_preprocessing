#!/usr/bin/env python3
# a278f.py -- ticket 278: spacing inside the corner ring, self excluded, for Pot_C_03 c2 and Pot_H_10 c2/c3/c4/c5
import numpy as np

def read_dump(path):
    a = np.loadtxt(path, comments='#', dtype=np.float64)
    return a[:, 1].astype(np.int32), a[:, 2:5].astype(np.float32)

def nn_excl(A, B, s):
    """nearest neighbour of A[s] inside B, excluding row s itself (A must be a subset of B by row alignment)"""
    na, nb = len(A), len(B)
    out = np.empty(na, dtype=np.float32)
    chunk = max(1, int(3_000_000 // max(1, nb)))
    for st in range(0, na, chunk):
        e = min(na, st+chunk)
        d = A[st:e, None, :] - B[None, :, :]
        d2 = np.einsum('ijk,ijk->ij', d, d, optimize=True)
        if s is not None:
            for k in range(st, e):
                d2[k-st, s[k]] = np.inf
        out[st:e] = np.sqrt(np.min(d2, axis=1))
    return out

def q(x, p): return float(np.percentile(x, p))

def report(tag, labels, P, kept, band):
    Pb = P[labels == band]
    K = np.concatenate([P[labels == c] for c in kept])
    U = P[labels < 0]
    jb = nn_excl(U, Pb, None); jf = nn_excl(U, K, None)
    m = (jb <= 3.0) & (jf <= 3.0)
    Uc = U[m]
    if len(Uc) < 10:
        print("%s c%d ring too small (%d)" % (tag, band, len(Uc))); return
    # self indices inside Uc: find rows of Uc in U
    Ui = np.nonzero(m)[0]
    if len(Uc) > 3000:
        pick = np.random.default_rng(278).choice(len(Uc), 3000, replace=False)
    else:
        pick = np.arange(len(Uc))
    d = nn_excl(Uc[pick], Uc, pick)
    print("%s c%d ring=%d spacing(self excl) p50=%.4f p90=%.4f p99=%.4f max=%.4f | <=1mm band %d kept %d both %d" %
          (tag, band, len(Uc), q(d,50), q(d,90), q(d,99), float(d.max()),
           int((jb[m]<=1.0).sum()), int((jf[m]<=1.0).sum()), int(((jb[m]<=1.0)&(jf[m]<=1.0)).sum())))

if __name__ == "__main__":
    R3 = "/data/gpfs/projects/punim2657/SfSpp/runs/20261024-1223_0ab0935_p276-phase3a"
    labels, P = read_dump(R3+"/out/C03_diag/mergeDiag276_Pot_C_Piece_03.txt"); report("Pot_C_03", labels, P, [0,1], 2)
    labels, P = read_dump(R3+"/out/H10_diag/mergeDiag276_Pot_H_Piece_10.txt")
    for b in (2,3,4,5): report("Pot_H_10", labels, P, [0,1], b)
