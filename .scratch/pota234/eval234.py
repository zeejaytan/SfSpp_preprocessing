"""POTA-234 evaluation: gap table (222 method) + fork-zone + UN/top2 + slot-verify + lane scores.
Usage:
  python eval234.py faces <S0.xyz> <S1.xyz> <unclustered.ply> <turn_x> <turn_y> <turn_z> <label>
  python eval234.py lanes <piece> <lane_dir> <author_dir>   (filenames Pot_D_Piece_<P>_Breakline_<b>.pcd)
"""
import numpy as np, os, sys

def load_xyz(p):
    d = np.loadtxt(p)
    return np.atleast_2d(d)[:, :3]

def load_pcd(p):
    with open(p, "rb") as f: data = f.read()
    head, _, body = data.partition(b"DATA ascii\n")
    if not body: head, _, body = data.partition(b"DATA ascii\r\n")
    nf = 3
    for line in head.decode("ascii", errors="replace").splitlines():
        if line.startswith("FIELDS"): nf = len(line.split()) - 1
    return np.fromstring(body.decode("ascii", errors="replace"), sep=" ").reshape(-1, nf)[:, :3]

def min_dist(A, B, chunk=2000):
    out = np.empty(len(A))
    for i in range(0, len(A), chunk):
        C = A[i:i+chunk]
        out[i:i+chunk] = np.sqrt((((C[:, None, :] - B[None, :, :]) ** 2).sum(-1)).min(1))
    return out

def faces(s0p, s1p, unp, turn, label):
    S0 = load_xyz(s0p); S1 = load_xyz(s1p)
    try: UN = load_pcd(unp); nun = len(UN)
    except Exception as e: UN = None; nun = -1
    d01 = min_dist(S0, S1); d10 = min_dist(S1, S0)
    dall = np.concatenate([d01, d10])
    symmin = float(min(d01.min(), d10.min()))
    p1, p50 = float(np.percentile(dall, 1)), float(np.median(dall))
    frac = float((dall < 2.0).mean())
    t = np.array(turn, float)
    z0 = int((np.sqrt(((S0 - t) ** 2).sum(-1)) < 5.0).sum())
    z1 = int((np.sqrt(((S1 - t) ** 2).sum(-1)) < 5.0).sum())
    n0, n1 = len(S0), len(S1)
    top2 = (n0 + n1) / max(1, n0 + n1 + (nun if nun >= 0 else 0))
    unshare = (nun / max(1, n0 + n1 + nun)) if nun >= 0 else -1
    print("[%s] S0=%d S1=%d UN=%d top2share=%.1f%% UNshare=%.1f%%" % (label, n0, n1, nun, top2*100, unshare*100))
    print("[%s] symmin=%.3f p1=%.2f p50=%.2f frac<2mm=%.2f%%" % (label, symmin, p1, p50, frac*100))
    print("[%s] fork-zone(<5mm turn): S0=%d S1=%d %s" % (label, z0, z1, "SINGLE-FACE" if z0 == 0 and z1 > 0 else ""))

def lanes(piece, ldir, adir):
    o0 = load_pcd(os.path.join(adir, "Pot_D_Piece_%s_Breakline_0.pcd" % piece))
    o1 = load_pcd(os.path.join(adir, "Pot_D_Piece_%s_Breakline_1.pcd" % piece))
    print("refs: o0=%d o1=%d" % (len(o0), len(o1)))
    L = {b: load_pcd(os.path.join(ldir, "Pot_D_Piece_%s_Breakline_%s.pcd" % (piece, b))) for b in ["0", "1"]}
    m = {}
    for b in ["0", "1"]:
        for a, an in [("o0", o0), ("o1", o1)]:
            d = min_dist(L[b], an)
            m[(b, a)] = (float(np.median(d)), float((d < 2.0).mean()))
    print("slot matrix (med/cov): Bl0->o0 %.2f/%.1f Bl0->o1 %.2f/%.1f | Bl1->o0 %.2f/%.1f Bl1->o1 %.2f/%.1f" % (
        m[("0","o0")][0], m[("0","o0")][1]*100, m[("0","o1")][0], m[("0","o1")][1]*100,
        m[("1","o0")][0], m[("1","o0")][1]*100, m[("1","o1")][0], m[("1","o1")][1]*100))
    straight = m[("0","o0")][0] + m[("1","o1")][0]; swapped = m[("0","o1")][0] + m[("1","o0")][0]
    slot = ("0", "o1", "1", "o0") if swapped < straight else ("0", "o0", "1", "o1")
    print("slots: %s (straight-sum %.2f vs swapped-sum %.2f)" % ("straight" if slot[1]=="o0" else "SWAPPED: Bl0->o1 Bl1->o0", straight, swapped))
    for b, a in [(slot[0], slot[1]), (slot[2], slot[3])]:
        an = o0 if a == "o0" else o1
        d = min_dist(L[b], an)
        seg = np.sqrt(((L[b][1:] - L[b][:-1]) ** 2).sum(-1))
        nj = int((seg > 10.0).sum()); mxj = float(seg.max()) if nj else 0.0
        med, cov = float(np.median(d)), float((d < 2.0).mean())
        bar = "AT-BAR" if (med < 2 and cov >= 0.90) else "below-bar"
        print("Bl%s->%s: n=%d med=%.2f cov=%.1f max=%.1f jumps=%d/%.1f %s" % (b, a, len(L[b]), med, cov*100, float(d.max()), nj, mxj, bar))

if __name__ == "__main__":
    if sys.argv[1] == "faces":
        _, _, s0p, s1p, unp, x, y, z, label = sys.argv
        faces(s0p, s1p, unp, (float(x), float(y), float(z)), label)
    elif sys.argv[1] == "lanes":
        _, _, piece, ldir, adir = sys.argv
        lanes(piece, ldir, adir)
