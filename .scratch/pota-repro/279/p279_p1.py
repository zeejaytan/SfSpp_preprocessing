#!/usr/bin/env python3
# p279_p1.py v2 -- ticket 279 Phase 1/2 scan.
# For every piece and both of the authors' surfaces: does the surface hold a base-like disc
# (axis-normal region, all azimuth bins, closed near-circular outer edge, near-planar, big enough),
# and where do that piece's reference breaklines sit relative to it (whole set and outer-edge ring).
import os, sys, numpy as np

S = "/data/gpfs/projects/punim2657/sfs_main/original_samples/SfS_pp"
OUT = sys.argv[1] if len(sys.argv) > 1 else "."
NB = 36
cols = ["piece","pot","nn","surface","n","nsel","frac_sel","norm_med","dotax_frac95",
        "bins5","bins10","r5","r50","r95","ax5","ax50","ax95","ax_spread","axlo_frac","axhi_frac",
        "edge_r50","edge_spread","edge_rel","edge_sd","edge_cv","l2l1","l3l1","spacing",
        "ref0_med","ref0_p90","ref1_med","ref1_p90","ref0_edge_med","ref1_edge_med"]

def read_xyz6(p):
    with open(p, "r", errors="replace") as f:
        a = np.array(f.read().split(), dtype=np.float64)
    return a.reshape(-1, 6)

def read_pcd3(p):
    rows, data = [], False
    with open(p, "r", errors="replace") as f:
        for ln in f:
            if not data:
                if ln.startswith("DATA"): data = True
                continue
            s = ln.split()
            if len(s) >= 3: rows.append((float(s[0]), float(s[1]), float(s[2])))
    return np.array(rows, dtype=np.float64)

def read_axis(piece):
    with open(os.path.join(S, "Axes", piece + "_Axis.xyz")) as f:
        v = np.array([float(x) for x in f.readline().split()[:6]])
    return v[:3], v[3:6] / np.linalg.norm(v[3:6])

def frame(d):
    e1 = np.array([1.0, 0.0, 0.0]); e1 = e1 - (e1 @ d) * d
    if np.linalg.norm(e1) < 1e-6:
        e1 = np.array([0.0, 1.0, 0.0]); e1 = e1 - (e1 @ d) * d
    e1 /= np.linalg.norm(e1)
    return e1, np.cross(d, e1)

def nnx(A, B, chunk=32):
    A = np.asarray(A, np.float32); B = np.asarray(B, np.float32)
    out = np.empty(len(A))
    for s in range(0, len(A), chunk):
        e = min(len(A), s + chunk)
        d = A[s:e, None, :] - B[None, :, :]
        out[s:e] = np.sqrt(np.min(np.einsum('ijk,ijk->ij', d, d, optimize=True), axis=1))
    return out

def spacing(P, k=1500, seed=279):
    idx = np.random.default_rng(seed).choice(len(P), min(k, len(P)), replace=False)
    Q = np.asarray(P, np.float32); out = np.empty(len(idx))
    for s in range(0, len(idx), 32):
        e = min(len(idx), s + 32)
        d = Q[idx[s:e], None, :] - Q[None, :, :]
        d2 = np.einsum('ijk,ijk->ij', d, d, optimize=True)
        for kk in range(s, e): d2[kk - s, idx[kk]] = np.inf
        out[s:e] = np.sqrt(np.min(d2, axis=1))
    return out

def q(x, p): return float(np.percentile(x, p)) if len(x) else float("nan")

def main():
    pieces = sorted({f.split("_Surface_")[0] for f in os.listdir(os.path.join(S, "Surfaces"))})
    rows = []
    for piece in pieces:
        pot = "_".join(piece.split("_")[:2]); nnn = piece.split("_")[3]
        p0, d = read_axis(piece)
        e1, e2 = frame(d)
        refs = {}
        for lane in (0, 1):
            fp = os.path.join(S, "Breaklines", "%s_Breakline_%d.pcd" % (piece, lane))
            if os.path.exists(fp): refs[lane] = read_pcd3(fp)
        surfs = []
        for si in (0, 1):
            fp = os.path.join(S, "Surfaces", "%s_Surface_%d.xyz" % (piece, si))
            surfs.append(read_xyz6(fp) if os.path.exists(fp) else None)
        allP = np.vstack([t[:, :3] for t in surfs if t is not None and len(t)])
        axall = (allP - p0) @ d
        axmin, axmax = float(axall.min()), float(axall.max())
        for si in (0, 1):
            T = surfs[si]
            if T is None: continue
            P = T[:, :3]
            N = T[:, 3:6]; nrm = np.linalg.norm(N, axis=1); N = N / np.maximum(nrm, 1e-12)[:, None]
            rel = P - p0
            ax = rel @ d
            r = np.linalg.norm(rel - np.outer(ax, d), axis=1)
            th = np.arctan2(rel @ e2, rel @ e1)
            b = ((th + np.pi) / (2 * np.pi) * NB).astype(int) % NB
            dotax = np.abs(N @ d)
            sel = dotax > 0.95
            nsel = int(sel.sum())
            rec = [piece, pot, nnn, si, len(P), nsel, nsel / len(P), q(nrm, 50), float(sel.mean())]
            if nsel >= 30:
                rs, axs, bs = r[sel], ax[sel], b[sel]
                cnt = np.bincount(bs, minlength=NB)
                ok = cnt >= 5
                ok10 = cnt >= 10
                q95 = np.array([np.percentile(rs[bs == k], 95) if ok[k] else np.nan for k in range(NB)])
                v = q95[ok]
                e_med = float(np.median(v)); e_sd = float(np.std(v))
                Ps = P[sel] - P[sel].mean(axis=0)
                ev = np.sort(np.linalg.eigvalsh(np.cov(Ps.T)))[::-1]
                sp = spacing(P[sel]) if nsel >= 50 else np.array([np.nan])
                span = (axmax - axmin) or 1.0
                rec += [int(ok.sum()), int(ok10.sum()), q(rs,5), q(rs,50), q(rs,95),
                        q(axs,5), q(axs,50), q(axs,95), q(axs,95)-q(axs,5),
                        (q(axs,5)-axmin)/span, (q(axs,95)-axmin)/span,
                        e_med, float(v.max()-v.min()), (v.max()-v.min())/e_med if e_med else float("nan"),
                        e_sd, e_sd/e_med if e_med else float("nan"),
                        float(ev[1]/ev[0]) if ev[0] > 0 else float("nan"),
                        float(ev[2]/ev[0]) if ev[0] > 0 else float("nan"),
                        q(sp, 50)]
                ring = np.zeros(len(P), bool)
                for k in range(NB):
                    if not ok[k]: continue
                    m = (bs == k) & (rs >= q95[k] - 1.0)
                    ring[np.nonzero(sel)[0][m]] = True
                for lane in (0, 1):
                    if lane in refs:
                        dd = nnx(refs[lane], P[sel]); rec += [q(dd,50), q(dd,90)]
                    else: rec += [np.nan, np.nan]
                for lane in (0, 1):
                    if lane in refs and ring.any(): rec.append(q(nnx(refs[lane], P[ring]), 50))
                    else: rec.append(np.nan)
            else:
                rec += [np.nan] * (len(cols) - len(rec))
            assert len(rec) == len(cols), (len(rec), len(cols))
            rows.append(rec)
    with open(os.path.join(OUT, "phase1_scan.tsv"), "w") as f:
        f.write("\t".join(cols) + "\n")
        for r_ in rows:
            f.write("\t".join(("%.4f" % v if isinstance(v, float) else str(v)) for v in r_) + "\n")
    print("rows", len(rows), "cols", len(cols), flush=True)

if __name__ == "__main__":
    main()
