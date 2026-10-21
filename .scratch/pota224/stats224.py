"""POTA-224 per-stage formation statistics (author-free except ruler-only parts)."""
import numpy as np, os, re, sys
B = chr(92)
def load_xyz(p):
    d = []
    with open(p) as f:
        for ln in f:
            s = ln.split()
            if len(s) >= 3:
                try: d.append((float(s[0]), float(s[1]), float(s[2])))
                except ValueError: pass
    return np.array(d, dtype=np.float64)
def load_pcd(p):
    sep = b"DATA ascii"
    with open(p, "rb") as f: data = f.read()
    head, _, body = data.partition(sep)
    body = body.replace(bytes([13]), bytes([32]))
    nf = 3
    for ln in head.decode("ascii", errors="replace").splitlines():
        if ln.startswith("FIELDS"): nf = len(ln.split()) - 1
    v = np.fromstring(body.decode("ascii", errors="replace"), sep=" ")
    return v.reshape(-1, nf)[:, :3]
def un_verts(p):
    with open(p, "rb") as f: head = f.read(2048).decode("ascii", errors="replace")
    m = re.search("element vertex (" + B + "d+)", head)
    return int(m.group(1)) if m else -1
def min_dist(A, B, chunk=2000):
    A32 = A.astype(np.float32); B32 = B.astype(np.float32)
    out = np.empty(len(A32), dtype=np.float32)
    for i in range(0, len(A32), chunk):
        C = A32[i:i+chunk]
        d2 = ((C[:, None, :] - B32[None, :, :]) ** 2).sum(-1)
        out[i:i+chunk] = np.sqrt(d2.min(1))
    return out.astype(np.float64)
def jumps(P, thr=10.0):
    seg = np.sqrt(((P[1:] - P[:-1]) ** 2).sum(-1))
    idx = np.nonzero(seg > thr)[0]
    return len(idx), (float(seg[idx].max()) if len(idx) else 0.0)
tree, tag, piece = sys.argv[1], sys.argv[2], sys.argv[3]
POT = "Pot_D"
DD = os.path.join(tree, "Temp", "Data", POT)
base = "Pot_D_Piece_" + piece
log = open(os.path.join(tree, "mesh_" + tag + ".log"), errors="replace").read()
nc = int(re.search("Number of clusters is equal to (" + B + "d+)", log).group(1))
sizes = [int(x) for x in re.findall("Cluster " + B + "d+ : (" + B + "d+)", log)]
cloud = int(re.search("Total points: (" + B + "d+)", log).group(1))
UN = un_verts(os.path.join(DD, base + "_unclustered.ply"))
S0 = load_xyz(os.path.join(DD, base + "_Surface_0.xyz"))
S1 = load_xyz(os.path.join(DD, base + "_Surface_1.xyz"))
print("cloud=%d clusters=%d top5=%s" % (cloud, nc, sizes[:5]), flush=True)
print("S0=%d S1=%d UN=%d clustersum=%d accounting=%s" % (len(S0), len(S1), UN, sum(sizes), sum(sizes) + UN == cloud), flush=True)
top2 = (sizes[0] + sizes[1]) / cloud * 100 if nc >= 2 else 0.0
third = (sizes[2] / cloud * 100) if nc >= 3 else 0.0
bal = (sizes[1] / sizes[0]) if nc >= 2 else 0.0
print("top2=%.1f third=%.1f bal=%.3f R1=%s" % (top2, third, bal, (top2 >= 70 and third <= 8 and bal >= 0.5)), flush=True)
d01 = min_dist(S0, S1); d10 = min_dist(S1, S0)
alld = np.concatenate([d01, d10])
print("S0<->S1 symmin=%.2f p1=%.2f p50=%.2f frac20=%.2f" % (alld.min(), np.percentile(alld, 1), np.median(alld), (alld < 2).mean() * 100), flush=True)
BOX = (33, 54, -28, 10, 432, 474)
for nm, S in [("S0", S0), ("S1", S1)]:
    inside = ((S[:, 0] >= BOX[0]) & (S[:, 0] <= BOX[1]) & (S[:, 1] >= BOX[2]) & (S[:, 1] <= BOX[3]) & (S[:, 2] >= BOX[4]) & (S[:, 2] <= BOX[5])).sum()
    print("overshoot-box %s: %d of %d (%.2f)" % (nm, inside, len(S), inside / len(S) * 100), flush=True)
ADIR = "/data/gpfs/projects/punim2657/sfs_main/original_samples/SfS_pp/Breaklines"
a0 = load_pcd(os.path.join(ADIR, base + "_Breakline_0.pcd"))
a1 = load_pcd(os.path.join(ADIR, base + "_Breakline_1.pcd"))
A = np.vstack([a0, a1])
for nm, S in [("S0", S0), ("S1", S1)]:
    d = min_dist(S, A)
    print("face-vs-author %s: n=%d med=%.2f p90=%.2f p99=%.2f over2=%d (%.1f)" % (nm, len(S), np.median(d), np.percentile(d, 90), np.percentile(d, 99), int((d > 2).sum()), (d > 2).mean() * 100), flush=True)
LDIR = os.path.join(tree, "Dataset", "Breaklines", POT)
LL = [load_pcd(os.path.join(LDIR, base + "_Breakline_%d.pcd" % b)) for b in [0, 1]]
print("refs o0=%d o1=%d" % (len(a0), len(a1)), flush=True)
m = [[float(np.median(min_dist(x, y))) for y in (a0, a1)] for x in LL]
print("slot matrix: Bl0-o0 %.2f Bl0-o1 %.2f Bl1-o0 %.2f Bl1-o1 %.2f" % (m[0][0], m[0][1], m[1][0], m[1][1]), flush=True)
straight = m[0][0] + m[1][1]; swapped = m[0][1] + m[1][0]
print("slots: %s (straight-sum %.2f vs swapped-sum %.2f)" % ("STRAIGHT" if straight < swapped else "SWAPPED", straight, swapped), flush=True)
for b in [0, 1]:
    s = 0 if m[b][0] < m[b][1] else 1
    an = a0 if s == 0 else a1
    d = min_dist(LL[b], an)
    nj, mxj = jumps(LL[b])
    endgap = float(np.sqrt(((LL[b][0] - LL[b][-1]) ** 2).sum()))
    seg = np.sqrt(((LL[b][1:] - LL[b][:-1]) ** 2).sum(-1))
    ok = "AT-BAR" if (np.median(d) < 2 and (d < 2).mean() >= 0.90) else "below-bar"
    print("ourBl%d vs o%d: n=%d med=%.2f cov=%.1f max=%.1f jumps=%d-%.1f gapmax=%.1f endgap=%.1f %s" % (b, s, len(LL[b]), np.median(d), (d < 2).mean() * 100, d.max(), nj, mxj, (float(seg.max()) if len(seg) else 0.0), endgap, ok), flush=True)
