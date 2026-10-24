#!/usr/bin/env python3
# a278b.py -- ticket 278 part 2: per-cluster geometry in the pot frame, near-approach slab, normal validation
import sys, os, math
import numpy as np

def read_pcd(path):
    with open(path, 'r', errors='replace') as f:
        lines = f.readlines()
    fields = None; i = 0
    while i < len(lines):
        s = lines[i].strip()
        if s.startswith('FIELDS'): fields = s.split()[1:]
        if s.startswith('DATA'):
            i += 1; break
        i += 1
    nf = len(fields) if fields else 3
    arr = np.fromstring(''.join(lines[i:]).replace('\n',' '), dtype=np.float64, sep=' ')
    arr = arr[:(len(arr)//nf)*nf].reshape(-1, nf)
    return arr, fields

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

def pca_normals(Q, k=20):
    n = len(Q); kk = min(k+1, n)
    out = np.empty((n, 3), dtype=np.float32)
    chunk = max(1, int(3_000_000 // max(1, n)))
    for s in range(0, n, chunk):
        e = min(n, s+chunk)
        d = Q[s:e, None, :] - Q[None, :, :]
        d2 = np.einsum('ijk,ijk->ij', d, d, optimize=True)
        part = np.argpartition(d2, kk-1, axis=1)[:, :kk]
        pts = Q[part].astype(np.float64)
        pts = pts - pts.mean(axis=1, keepdims=True)
        cov = np.einsum('mki,mkj->mij', pts, pts) / kk
        w, v = np.linalg.eigh(cov)
        out[s:e] = v[:, :, 0].astype(np.float32)
    return out

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

def cluster_table(tag, labels, P, p0, w, u, v, kept):
    print("== CLUSTERS %s" % tag)
    print("clu size kept radp5 radp50 radp95 axp5 axp50 axp95 |n.rad| |n.ax| angbins l2/l1 l3/l1")
    a, r, ang = axial(P, p0, w, u, v)
    for c in np.unique(labels):
        sel = labels == c
        if sel.sum() < 20: continue
        Q = P[sel]; n = len(Q)
        N = pca_normals(Q, k=20).astype(np.float64)
        d0 = Q.astype(np.float64) - p0
        perp = d0 - (d0 @ w)[:, None]*w[None, :]
        perp /= (np.linalg.norm(perp, axis=1)[:, None] + 1e-12)
        dot_rad = np.abs(np.einsum('ij,ij->i', N, perp)); dot_ax = np.abs(N @ w)
        bins = np.unique(np.floor((ang[sel] % 360.0)/10.0).astype(int))
        X = Q.astype(np.float64); Xc = X - X.mean(0)
        ev = np.linalg.eigvalsh(np.cov(Xc.T))
        print("c%-3d %6d %s %6.2f %6.2f %6.2f %7.2f %7.2f %7.2f %.3f %.3f %2d %.4f %.4f" %
              (c, n, "K" if c in kept else "-", q(r[sel],5), q(r[sel],50), q(r[sel],95),
               q(a[sel],5), q(a[sel],50), q(a[sel],95), q(dot_rad,50), q(dot_ax,50), len(bins),
               ev[1]/ev[2], ev[0]/ev[2]))
    print()

def near_slab(tag, labels, P, kept_labels, band, thr=3.0):
    K = np.concatenate([P[labels==c] for c in kept_labels])
    Pb = P[labels==band]
    _, db = nn_query(Pb, K)
    near = db <= thr
    un = labels < 0
    Pu = P[un]
    if near.sum() == 0:
        print("== NEAR %s c%d none" % (tag, band)); return
    Pn = Pb[near]
    ju, du_b = nn_query(Pu, Pn)
    _, du_f = nn_query(Pu, K)
    print("== NEAR %s c%d band_pts<=%.1fmm=%d dmin=%.4f | unclustered=%d within%.1fmm_of_those_band_pts=%d of_which<=%.1fmm_of_face=%d" %
          (tag, band, thr, int(near.sum()), db.min(), int(un.sum()), thr, int((du_b<=thr).sum()), thr, int(((du_b<=thr)&(du_f<=thr)).sum())))
    # how far the unclustered points get into the gap: histogram of max(du_b,du_f) for those within thr of both
    m = (du_b<=thr)&(du_f<=thr)
    if m.sum():
        print("   those points: max(d_band,d_face) p50=%.3f min=%.3f" % (q(np.maximum(du_b[m],du_f[m]),50), np.maximum(du_b[m],du_f[m]).min()))

def normcheck(tag, labels, P, band, stage, pot, nn):
    inp, fld = read_pcd(os.path.join(stage, "Dataset/Point/%s/%s_Piece_%s_Point.pcd" % (pot, pot, nn)))
    if fld is None or 'normal_x' not in fld:
        print("== NORMCHECK %s no normals in input" % tag); return
    Pb = P[labels==band]
    lo = Pb.min(0) - 1.0; hi = Pb.max(0) + 1.0
    m = np.all((inp[:, :3] >= lo) & (inp[:, :3] <= hi), axis=1)
    sub = inp[m]
    print("== NORMCHECK %s c%d input_pts_in_box=%d of %d" % (tag, band, len(sub), len(inp)))
    if len(sub) < 100: return
    rng = np.random.default_rng(278)
    pi = rng.choice(len(Pb), size=min(800, len(Pb)), replace=False)
    Ps = Pb[pi]
    j, d = nn_query(Ps, sub[:, :3].astype(np.float32))
    Np = pca_normals(Pb, k=20)[pi].astype(np.float64)
    Ni = sub[j, 3:6].astype(np.float64)
    Ni /= (np.linalg.norm(Ni, axis=1)[:, None] + 1e-12)
    dots = np.abs(np.einsum('ij,ij->i', Np, Ni))
    print("   pca-vs-input median|dot|=%.4f frac>0.9=%.3f match_dist p50=%.5f p95=%.5f max=%.4f" %
          (q(dots,50), float((dots>0.9).mean()), q(d,50), q(d,95), d.max()))

if __name__ == "__main__":
    R3 = "/data/gpfs/projects/punim2657/SfSpp/runs/20261024-1223_0ab0935_p276-phase3a"
    pieces = [("Pot_C_03", R3+"/out/C03_diag/mergeDiag276_Pot_C_Piece_03.txt", "Pot_C", "03", R3+"/stage/C03_diag", [0,1], [2,3,4,5,6,7]),
              ("Pot_H_10", R3+"/out/H10_diag/mergeDiag276_Pot_H_Piece_10.txt", "Pot_H", "10", R3+"/stage/H10_diag", [0,1], [2,3,4,5,6,7,8])]
    for tag, dump, pot, nn, stage, kept, bands in pieces:
        labels, P = read_dump(dump)
        p0, w, u, v = frame(os.path.join(stage, "Dataset/Axes/%s_Piece_%s_Axis.xyz" % (pot, nn)))
        cluster_table(tag, labels, P, p0, w, u, v, kept)
        for b in bands:
            if (labels==b).sum() == 0: continue
            near_slab(tag, labels, P, kept, b)
        for b in bands[:1] + [5]:
            if (labels==b).sum() == 0: continue
            normcheck(tag, labels, P, b, stage, pot, nn)
        print()
