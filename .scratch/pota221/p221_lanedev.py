"""POTA-221 lane deviation runs vs author rim."""
import numpy as np, sys
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
lane, a0, a1 = sys.argv[1], sys.argv[2], sys.argv[3]
L, o0, o1 = load_pcd(lane), load_pcd(a0), load_pcd(a1)
rim = np.vstack([o0, o1])
d = dist_to(L, rim)
bad = np.nonzero(d >= 2.0)[0]
print("n=%d med=%.2f cov=%.1f max=%.1f nbad=%d" % (len(L), float(np.median(d)), 100*(d < 2).mean(), float(d.max()), len(bad)))
runs, start, prev = [], (bad[0] if len(bad) else None), None
if len(bad):
    start, prev = bad[0], bad[0]
    for b in bad[1:]:
        if b == prev + 1: prev = b
        else: runs.append((start, prev)); start, prev = b, b
    runs.append((start, prev))
    print("runs(start-end-peak):", [(int(a), int(b), round(float(d[a:b+1].max()), 1)) for a, b in runs])
d0, d1 = dist_to(L, o0), dist_to(L, o1)
print("frac<2mm from o0: %.2f from o1: %.2f" % ((d0 < 2).mean(), (d1 < 2).mean()))
