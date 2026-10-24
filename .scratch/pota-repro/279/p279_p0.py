#!/usr/bin/env python3
# p279_p0.py -- ticket 279 Phase 0: reachability of the authors' reference breaklines against
# the authors' own surfaces, every piece, both lanes.  Read-only.
import os, sys, numpy as np

ROOT = "/data/gpfs/projects/punim2657/sfs_main/original_samples/SfS_pp"
OUT  = sys.argv[1] if len(sys.argv) > 1 else "."

def read_xyz6(path):
    with open(path, "r", errors="replace") as f:
        a = np.array(f.read().split(), dtype=np.float64)
    if a.size % 6 != 0:
        raise RuntimeError("not 6N floats: %s (%d)" % (path, a.size))
    return a.reshape(-1, 6)

def read_pcd3(path):
    rows = []
    data = False
    with open(path, "r", errors="replace") as f:
        for ln in f:
            if not data:
                if ln.startswith("DATA"):
                    data = True
                continue
            s = ln.split()
            if len(s) >= 3:
                rows.append((float(s[0]), float(s[1]), float(s[2])))
    return np.array(rows, dtype=np.float64)

def nn(A, B, chunk=48):
    """nearest distance from every row of A to the point set B"""
    A = np.asarray(A, dtype=np.float32); B = np.asarray(B, dtype=np.float32)
    out = np.empty(len(A), dtype=np.float64)
    for s in range(0, len(A), chunk):
        e = min(len(A), s + chunk)
        d = A[s:e, None, :] - B[None, :, :]
        out[s:e] = np.sqrt(np.min(np.einsum('ijk,ijk->ij', d, d, optimize=True), axis=1))
    return out

def q(x, p):
    return float(np.percentile(x, p)) if len(x) else float("nan")

def main():
    pieces = sorted({f.split("_Surface_")[0] for f in os.listdir(os.path.join(ROOT, "Surfaces"))})
    print("pieces:", len(pieces), flush=True)
    cols = ["piece", "pot", "nn", "lane", "ndots", "ns0", "ns1",
            "med_s0", "p90_s0", "max_s0", "med_s1", "p90_s1", "max_s1",
            "med_best", "p90_best", "max_best", "closer", "frac_1mm_best"]
    rows = []
    for k, piece in enumerate(pieces):
        pot = piece.split("_")[0] + "_" + piece.split("_")[1]
        nnn = piece.split("_")[3]
        S = []
        for i in (0, 1):
            p = os.path.join(ROOT, "Surfaces", "%s_Surface_%d.xyz" % (piece, i))
            S.append(read_xyz6(p)[:, :3] if os.path.exists(p) else np.zeros((0, 3)))
        for lane in (0, 1):
            p = os.path.join(ROOT, "Breaklines", "%s_Breakline_%d.pcd" % (piece, lane))
            if not os.path.exists(p):
                continue
            B = read_pcd3(p)
            d0 = nn(B, S[0]) if len(S[0]) else np.full(len(B), np.inf)
            d1 = nn(B, S[1]) if len(S[1]) else np.full(len(B), np.inf)
            best = np.minimum(d0, d1)
            m0, m1, mb = q(d0, 50), q(d1, 50), q(best, 50)
            closer = "S0" if m0 <= m1 else "S1"
            rows.append([piece, pot, nnn, lane, len(B), len(S[0]), len(S[1]),
                         m0, q(d0, 90), float(d0.max()),
                         m1, q(d1, 90), float(d1.max()),
                         mb, q(best, 90), float(best.max()),
                         closer, float((best <= 1.0).mean())])
        if (k + 1) % 10 == 0:
            print("done %d/%d" % (k + 1, len(pieces)), flush=True)
    with open(os.path.join(OUT, "phase0_reachability.tsv"), "w") as f:
        f.write("\t".join(cols) + "\n")
        for r in rows:
            f.write("\t".join(("%s" % (round(v, 4) if isinstance(v, float) else v)) for v in r) + "\n")
    print("rows:", len(rows), flush=True)

if __name__ == "__main__":
    main()
