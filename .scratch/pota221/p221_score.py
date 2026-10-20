"""POTA-221 scoring: per-piece slot matrix + lane med/cov vs author (220 pattern).”
Usage: python p221_score.py <piece:12|15|22|25|27|16> <lane_dir> <author_dir>
lane_dir holds Pot_D_Piece_<P>_Breakline_0/1.pcd (+ boundary optionally).
author_dir holds Pot_D_Piece_<P>_Breakline_0/1.pcd (ORIG author lanes).
"""
import numpy as np, os, sys

def load_pcd(p):
    with open(p, "rb") as f: data = f.read()
    head, _, body = data.partition(b"DATA ascii\n")
    if not body: head, _, body = data.partition(b"DATA ascii\r\n")
    nf = 3
    for line in head.decode("ascii", errors="replace").splitlines():
        if line.startswith("FIELDS"): nf = len(line.split()) - 1
    return np.fromstring(body.decode("ascii", errors="replace"), sep=" ").reshape(-1, nf)[:, :3]

def dist_to(A, B):
    return np.sqrt((((A[:, None, :] - B[None, :, :]) ** 2).sum(-1)).min(1))

def med_cov(A, B, thr=2.0):
    d = dist_to(A, B)
    return float(np.median(d)), float((d < thr).mean()), float(d.max())

def jumps(P, thr=10.0):
    seg = np.sqrt(((P[1:] - P[:-1]) ** 2).sum(-1))
    idx = np.nonzero(seg > thr)[0]
    return len(idx), (float(seg[idx].max()) if len(idx) else 0.0)

def main():
    piece, ldir, adir = sys.argv[1], sys.argv[2], sys.argv[3]
    o0 = load_pcd(os.path.join(adir, "Pot_D_Piece_%s_Breakline_0.pcd" % piece))
    o1 = load_pcd(os.path.join(adir, "Pot_D_Piece_%s_Breakline_1.pcd" % piece))
    print("refs: o0=%d o1=%d" % (len(o0), len(o1)))
    L = {b: load_pcd(os.path.join(ldir, "Pot_D_Piece_%s_Breakline_%s.pcd" % (piece, b))) for b in ["0", "1"]}
    m00 = float(np.median(dist_to(L["0"], o0))); m01 = float(np.median(dist_to(L["0"], o1)))
    m10 = float(np.median(dist_to(L["1"], o0))); m11 = float(np.median(dist_to(L["1"], o1)))
    print("slot matrix: ourBl0->o0 %.2f ourBl0->o1 %.2f | ourBl1->o0 %.2f ourBl1->o1 %.2f" % (m00, m01, m10, m11))
    slot = {"0": ("o0" if m00 < m01 else "o1"), "1": ("o0" if m10 < m11 else "o1")}
    print("slots: ourBl0->" + slot["0"] + " ourBl1->" + slot["1"])
    for b in ["0", "1"]:
        an = o0 if slot[b] == "o0" else o1
        med, cov, mx = med_cov(L[b], an)
        nj, mxj = jumps(L[b])
        bar = "AT-BAR" if (med < 2 and cov >= 0.90) else "below-bar"
        print("ourBl%s vs author-%s: n=%d med=%.2f cov=%.1f max=%.1f jumps=%d/%.1f %s" % (b, slot[b], len(L[b]), med, cov*100, mx, nj, mxj, bar))

if __name__ == "__main__":
    main()
