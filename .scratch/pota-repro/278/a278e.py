#!/usr/bin/env python3
# a278e.py -- ticket 278 part 5: is the corner ring a real surface (spacing) and does it bridge band and face?
import numpy as np, os

def read_dump(path):
    a = np.loadtxt(path, comments='#', dtype=np.float64)
    return a[:, 1].astype(np.int32), a[:, 2:5].astype(np.float32)

def nn_query(A, B):
    na = len(A); nb = len(B)
    chunk = max(1, int(3_000_000 // max(1, nb)))
    idx = np.empty(na, dtype=np.int64); dist = np.empty(na, dtype=np.float32)
    for s in range(0, na, chunk):
        e = min(na, s+chunk)
        d = A[s:e, None, :] - B[None, :, :]
        d2 = np.einsum('ijk,ijk->ij', d, d, optimize=True)
        j = np.argmin(d2, axis=1)
        idx[s:e] = j; dist[s:e] = np.sqrt(d2[np.arange(e-s), j])
    return idx, dist

def q(x, p): return float(np.percentile(x, p))

def report(tag, labels, P, kept, band):
    Pb = P[labels == band]
    K = np.concatenate([P[labels == c] for c in kept])
    U = P[labels < 0]
    ju, du_b = nn_query(U, Pb)
    _, du_f = nn_query(U, K)
    m = (du_b <= 3.0) & (du_f <= 3.0)
    Uc = U[m]
    print("== RING %s c%d corner_pts=%d" % (tag, band, len(Uc)))
    if len(Uc) < 10: return
    print("   corner->band dmin=%.4f p50=%.4f p95=%.4f | corner->kept dmin=%.4f p50=%.4f p95=%.4f" %
          (du_b[m].min(), q(du_b[m],50), q(du_b[m],95), du_f[m].min(), q(du_f[m],50), q(du_f[m],95)))
    # spacing inside the corner set, excluding self
    if len(Uc) > 4000:
        Uc_s = Uc[np.random.default_rng(278).choice(len(Uc), 4000, replace=False)]
    else:
        Uc_s = Uc
    j, d = nn_query(Uc_s, Uc)
    d = d.astype(np.float64)
    print("   corner internal NN spacing (self excluded) p50=%.4f p90=%.4f max=%.4f" % (q(d,50), q(d,90), d.max()))
    # how many corner points are within rho_d=1.0 of both a band point and a kept point -> pair-eligible bridge
    print("   corner pts <=1.0mm of band: %d ; <=1.0mm of kept: %d ; both: %d" %
          (int((du_b[m]<=1.0).sum()), int((du_f[m]<=1.0).sum()), int(((du_b[m]<=1.0)&(du_f[m]<=1.0)).sum())))

if __name__ == "__main__":
    R3 = "/data/gpfs/projects/punim2657/SfSpp/runs/20261024-1223_0ab0935_p276-phase3a"
    for tag, dump, kept, bands in [("Pot_C_03", R3+"/out/C03_diag/mergeDiag276_Pot_C_Piece_03.txt", [0,1], [2,3,4,5,6,7]),
                                   ("Pot_H_10", R3+"/out/H10_diag/mergeDiag276_Pot_H_Piece_10.txt", [0,1], [2,3,4,5,6])]:
        labels, P = read_dump(dump)
        for b in bands: report(tag, labels, P, kept, b)
        print()
