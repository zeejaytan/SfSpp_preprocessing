#!/usr/bin/env python3
# a278.py -- ticket 278: what is the rim band? Reuses the ticket 276 Phase 3a dumps.
import sys, os, math
import numpy as np

AUTH_DIR = "/data/gpfs/projects/punim2657/sfs_main/original_samples/SfS_pp/Breaklines"

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
    txt = ''.join(lines[i:]).replace('\n', ' ')
    arr = np.fromstring(txt, dtype=np.float64, sep=' ')
    arr = arr[:(len(arr)//nf)*nf].reshape(-1, nf)
    return arr, fields

def read_dump(path):
    a = np.loadtxt(path, comments='#', dtype=np.float64)
    return a[:, 1].astype(np.int32), a[:, 2:5].astype(np.float32)

def nn_query(A, B, clamp=None):
    na = len(A); nb = len(B)
    chunk = max(1, int(3_000_000 // max(1, nb)))
    idx = np.empty(na, dtype=np.int64); dist = np.empty(na, dtype=np.float32)
    for s in range(0, na, chunk):
        e = min(na, s + chunk)
        d = A[None, :, :] if False else (A[s:e, None, :] - B[None, :, :])
        d2 = np.einsum('ijk,ijk->ij', d, d, optimize=True)
        j = np.argmin(d2, axis=1)
        idx[s:e] = j
        dist[s:e] = np.sqrt(d2[np.arange(e - s), j])
    return idx, dist

def pca_normals(P, k=20, queryset=None):
    Q = P if queryset is None else queryset
    n = len(Q); m = len(P); kk = min(k + 1, m)
    out = np.empty((n, 3), dtype=np.float32)
    chunk = max(1, int(3_000_000 // max(1, m)))
    for s in range(0, n, chunk):
        e = min(n, s + chunk)
        d = Q[s:e, None, :] - P[None, :, :]
        d2 = np.einsum('ijk,ijk->ij', d, d, optimize=True)
        part = np.argpartition(d2, kk - 1, axis=1)[:, :kk]
        pts = P[part].astype(np.float64)
        pts = pts - pts.mean(axis=1, keepdims=True)
        cov = np.einsum('mki,mkj->mij', pts, pts) / kk
        w, v = np.linalg.eigh(cov)
        out[s:e] = v[:, :, 0].astype(np.float32)
    return out

def q(x, p):
    return float(np.percentile(x, p))

def fmt(x):
    return "%.4f" % x if abs(x) < 100 else "%.3f" % x

def frame(axis_path):
    a = np.loadtxt(axis_path)
    p0 = a[:3].astype(np.float64); w = a[3:6].astype(np.float64)
    w = w / np.linalg.norm(w)
    u = np.array([1.0, 0, 0]) - w * w[0]
    if np.linalg.norm(u) < 1e-6:
        u = np.array([0, 1.0, 0]) - w * w[1]
    u = u / np.linalg.norm(u); v = np.cross(w, u)
    return p0, w, u, v

def axial(P, p0, w, u, v):
    d = P.astype(np.float64) - p0
    a = d @ w
    perp = d - a[:, None] * w[None, :]
    r = np.linalg.norm(perp, axis=1)
    ang = np.degrees(np.arctan2(perp @ v, perp @ u))
    return a, r, ang

def main(dump, pot, nn, stage, thresh_dots=2.0):
    md5 = os.popen("md5sum " + dump).read().split()[0]
    labels, P = read_dump(dump)
    n = len(labels)
    print("== PIECE %s_%s dump=%s md5=%s npoints=%d" % (pot, nn, dump, md5, n))
    sizes = {}
    for c in np.unique(labels):
        sizes[int(c)] = int((labels == c).sum())
    kept = [c for c in sorted(sizes) if c >= 0 and c <= 1]
    print("CENSUS " + " ".join("c%d=%d%s" % (c, sizes[c], "K" if c in kept else "") for c in sorted(sizes)))
    axis_path = os.path.join(stage, "Dataset/Axes/%s_Piece_%s_Axis.xyz" % (pot, nn))
    p0, w, u, v = frame(axis_path)
    print("AXIS " + " ".join("%.4f" % x for x in np.concatenate([p0, w])))
    K = np.concatenate([P[labels == c] for c in kept])
    ksz = [sizes[c] for c in kept]
    for ci, c in enumerate(kept):
        print("KEPT c%d size=%d" % (c, sizes[c]))
    # face normals for the whole kept set
    fN = pca_normals(K, k=20)
    ja, da = nn_query(P, K)          # every point -> kept face
    a_ax, a_r, a_ang = axial(P, p0, w, u, v)
    # normals for all points once (band + others reuse)
    PN = pca_normals(P, k=20)
    # author lanes
    authors = {}
    for lane in (0, 1):
        apath = "%s/%s_Piece_%s_Breakline_%d.pcd" % (AUTH_DIR, pot, nn, lane)
        arr, fld = read_pcd(apath)
        authors[lane] = arr
        print("AUTHOR Bl%d n=%d cols=%s" % (lane, len(arr), ",".join(fld)))
    # per dropped cluster carrying author dots
    for c in sorted(sizes):
        if c in kept: continue
        sel = labels == c
        ndots = 0
        for lane in (0, 1):
            A = authors[lane][:, :3].astype(np.float32)
            jb, db = nn_query(A, P[sel])
            ndots += int((db <= thresh_dots).sum())
        if ndots == 0 and sizes[c] < 200: continue
        print("-- BAND c%d size=%d author_dots_within_%.1fmm=%d" % (c, sizes[c], thresh_dots, ndots))
        Pb = P[sel]; Nb = PN[sel]
        b_ax, b_r, b_ang = a_ax[sel], a_r[sel], a_ang[sel]
        # orientation of the band's own normals vs the axial frame
        nb2 = Nb.astype(np.float64)
        dot_axis = np.abs(nb2 @ w)
        dr = P[sel].astype(np.float64) - p0
        perpvec = dr - (dr @ w)[:, None] * w[None, :]
        perpvec /= (np.linalg.norm(perpvec, axis=1)[:, None] + 1e-12)
        dot_rad = np.abs(np.einsum('ij,ij->i', nb2, perpvec))
        print("   n_band_vs_radial med|dot|=%.4f q10=%.4f q90=%.4f | vs_axis med|dot|=%.4f" %
              (q(dot_rad,50), q(dot_rad,10), q(dot_rad,90), q(dot_axis,50)))
        # extent
        print("   radial p5=%.3f p50=%.3f p95=%.3f width=%.3f | axial p5=%.3f p50=%.3f p95=%.3f height=%.3f" %
              (q(b_r,5), q(b_r,50), q(b_r,95), q(b_r,95)-q(b_r,5), q(b_ax,5), q(b_ax,50), q(b_ax,95), q(b_ax,95)-q(b_ax,5)))
        bins = np.floor((b_ang[0:] % 360.0) / 10.0).astype(int)
        uq = np.unique(bins)
        print("   angle bins10_occupied=%d/36 span=%.1fdeg arclen=%.2fmm (r50=%.2f)" % (len(uq), len(uq)*10.0, len(uq)*10.0*math.pi/180.0*q(b_r,50), q(b_r,50)))
        X = Pb.astype(np.float64); Xc = X - X.mean(0)
        ev = np.linalg.eigvalsh(np.cov(Xc.T))
        print("   pca l1=%.1f l2=%.1f l3=%.1f l3/l1=%.4f l2/l1=%.4f" % (ev[2], ev[1], ev[0], ev[0]/ev[2], ev[1]/ev[2]))
        # gap to kept + per-cluster split
        jb, db = nn_query(Pb, K)
        print("   gap band->kept dmin=%.4f p1=%.4f p10=%.4f p50=%.4f p90=%.4f max=%.4f n<=2=%.1f%% n<=3=%.1f%%" %
              (db.min(), q(db,1), q(db,10), q(db,50), q(db,90), db.max(),
               100.0*(db<=2).mean(), 100.0*(db<=3).mean()))
        for ci, c2 in enumerate(kept):
            Kc = P[labels == c2]
            _, d2 = nn_query(Pb, Kc)
            print("     to c%d(size %d): dmin=%.4f p50=%.4f n<=3=%d" % (c2, sizes[c2], d2.min(), q(d2,50), int((d2<=3).sum())))
        # local orientation vs each kept cluster (paired nearest)
        for ci, c2 in enumerate(kept):
            Kc = P[labels == c2]
            Nc = pca_normals(Kc, k=20)
            jc, dc = nn_query(Pb, Kc)
            dots = np.abs(np.einsum('ij,ij->i', Nb.astype(np.float64), Nc[jc].astype(np.float64)))
            print("     orient vs c%d(size %d): med|dot|=%.4f q10=%.4f q90=%.4f frac>0.8=%.3f frac<0.4=%.3f (pairs n=%d)" %
                  (c2, sizes[c2], q(dots,50), q(dots,10), q(dots,90), float((dots>0.8).mean()), float((dots<0.4).mean()), len(dots)))
        # contact spread
        near = db <= 3.0
        if near.sum():
            nb_bins = np.unique(np.floor(((b_ang[near] % 360.0) / 10.0)).astype(int))
            print("   contact: band pts d<=3mm n=%d angular_bins=%d span=%.1fdeg" % (int(near.sum()), len(nb_bins), len(nb_bins)*10.0))
        else:
            print("   contact: none within 3mm")
        # author dots relation
        for lane in (0, 1):
            A = authors[lane][:, :3].astype(np.float32)
            if len(A) == 0: continue
            jb2, db2 = nn_query(A, Pb)
            near_dot = db2 <= thresh_dots
            if near_dot.sum() == 0: continue
            selb = jb2[near_dot]
            dface_of_near = db[selb]
            pct = np.searchsorted(np.sort(db), dface_of_near) / float(len(db))
            r_of_near = b_r[selb]
            rpct = np.searchsorted(np.sort(b_r), r_of_near) / float(len(b_r))
            # outer / inner boundary sets of the band (radial extremes)
            rs = np.sort(b_r); lo = rs[int(0.05*len(rs))]; hi = rs[int(0.95*len(rs))]
            outer = Pb[b_r >= hi]; inner = Pb[b_r <= lo]
            jo, do = nn_query(A[near_dot], outer)
            ji, di = nn_query(A[near_dot], inner)
            face_side = int((pct < 0.25).sum()); mid = int(((pct >= 0.25) & (pct <= 0.75)).sum()); far = int((pct > 0.75).sum())
            print("   AUTHOR Bl%d dots_on_band=%d dist_to_band p50=%.4f max=%.4f | face-side=%d middle=%d far-edge=%d (d_face pct p50=%.3f)" %
                  (lane, int(near_dot.sum()), q(db2[near_dot],50), db2[near_dot].max(), face_side, mid, far, q(pct,50)))
            print("        dot radial pct p50=%.3f ; dist to OUTER boundary p50=%.3f ; INNER boundary p50=%.3f" %
                  (q(rpct,50), q(do,50), q(di,50)))
        # unclustered slab census
        un = labels < 0
        if un.sum():
            Pu = P[un]
            _, du_b = nn_query(Pu, Pb)
            _, du_f = nn_query(Pu, K)
            slab = (du_b <= 1.35) & (du_f <= 1.35)
            lens = (du_b + du_f) <= 3.6
            print("   SLAB unclustered=%d d<=1.35 both=%d sum<=3.6=%d" % (int(un.sum()), int(slab.sum()), int(lens.sum())))
    print()

if __name__ == "__main__":
    R = sys.argv[1]
    main(R + "/out/C03_diag/mergeDiag276_Pot_C_Piece_03.txt", "Pot_C", "03", R + "/stage/C03_diag")
    main(R + "/out/H10_diag/mergeDiag276_Pot_H_Piece_10.txt", "Pot_H", "10", R + "/stage/H10_diag")
