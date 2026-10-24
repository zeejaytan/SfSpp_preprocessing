#!/usr/bin/env python3
# a278c.py -- ticket 278 part 3: is the corner continuous in the cloud, or a hole? (band -> kept U unclustered)
import sys, os, math
import numpy as np

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

def frame(axis_path):
    a = np.loadtxt(axis_path)
    p0 = a[:3].astype(np.float64); w = a[3:6].astype(np.float64); w /= np.linalg.norm(w)
    u = np.array([1.0,0,0]) - w*w[0]
    if np.linalg.norm(u) < 1e-6: u = np.array([0,1.0,0]) - w*w[1]
    u /= np.linalg.norm(u); v = np.cross(w, u)
    return p0, w, u, v

def axial(P, p0, w, u, v):
    d = P.astype(np.float64) - p0
    a = d @ w
    perp = d - a[:, None]*w[None, :]
    return a, np.linalg.norm(perp, axis=1), np.degrees(np.arctan2(perp @ v, perp @ u))

def cont(tag, labels, P, kept, band, p0, w, u, v):
    sel = labels == band
    Pb = P[sel]
    K = np.concatenate([P[labels==c] for c in kept])
    U = P[labels < 0]
    _, d_f = nn_query(Pb, K)
    _, d_u = nn_query(Pb, U)
    d_all = np.minimum(d_f, d_u)
    a, r, ang = axial(P, p0, w, u, v)
    print("== CONT %s c%d n=%d | to kept dmin=%.4f | to unclustered dmin=%.4f p50=%.4f | to kept+unclustered dmin=%.4f p10=%.4f p50=%.4f n<=0.5=%.1f%%" %
          (tag, band, int(sel.sum()), d_f.min(), d_u.min(), q(d_u,50), d_all.min(), q(d_all,10), q(d_all,50), 100.0*(d_all<=0.5).mean()))
    # corner points: unclustered within 3mm of both the band and the kept face
    ju, du_b = nn_query(U, Pb)
    _, du_f = nn_query(U, K)
    m = (du_b <= 3.0) & (du_f <= 3.0)
    print("   corner unclustered within 3mm of both = %d/%d" % (int(m.sum()), len(U)))
    if m.sum() > 10:
        idx = np.where(labels < 0)[0][m]
        print("   their radial p5=%.2f p50=%.2f p95=%.2f ; axial p5=%.2f p50=%.2f p95=%.2f ; angbins=%d" %
              (q(r[idx],5), q(r[idx],50), q(r[idx],95), q(a[idx],5), q(a[idx],50), q(a[idx],95),
               len(np.unique(np.floor((ang[idx] % 360.0)/10.0).astype(int)))))
        # continuity inside the corner set: nearest neighbour distance among all points of the corner (band side)
        Call = np.concatenate([Pb, K, U[idx]])
        _, dc = nn_query(U[idx], Call)
        print("   corner pts nearest-neighbour in the whole cloud p50=%.4f p95=%.4f max=%.4f" % (q(dc,50), q(dc,95), dc.max()))
    print()

if __name__ == "__main__":
    R3 = "/data/gpfs/projects/punim2657/SfSpp/runs/20261024-1223_0ab0935_p276-phase3a"
    jobs = [("Pot_C_03", R3+"/out/C03_diag/mergeDiag276_Pot_C_Piece_03.txt", "Pot_C", "03", R3+"/stage/C03_diag", [0,1], [2,3,4,5,6,7]),
            ("Pot_H_10", R3+"/out/H10_diag/mergeDiag276_Pot_H_Piece_10.txt", "Pot_H", "10", R3+"/stage/H10_diag", [0,1], [2,3,4,5,6])]
    for tag, dump, pot, nn, stage, kept, bands in jobs:
        labels, P = read_dump(dump)
        p0, w, u, v = frame(os.path.join(stage, "Dataset/Axes/%s_Piece_%s_Axis.xyz" % (pot, nn)))
        for b in bands:
            cont(tag, labels, P, kept, b, p0, w, u, v)
