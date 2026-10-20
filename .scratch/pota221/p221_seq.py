"""Which author lane is each our-point nearest to, in lane order."""
import numpy as np, sys
def load_pcd(p):
    with open(p, "rb") as f: data = f.read()
    head, _, body = data.partition(b"DATA ascii\n")
    if not body: head, _, body = data.partition(b"DATA ascii\r\n")
    nf = 3
    for line in head.decode("ascii", errors="replace").splitlines():
        if line.startswith("FIELDS"): nf = len(line.split()) - 1
    return np.fromstring(body.decode("ascii", errors="replace"), sep=" ").reshape(-1, nf)[:, :3]
lane, a0, a1 = sys.argv[1], sys.argv[2], sys.argv[3]
L, o0, o1 = load_pcd(lane), load_pcd(a0), load_pcd(a1)
D0 = np.sqrt((((L[:, None, :] - o0[None, :, :]) ** 2).sum(-1)).min(1))
D1 = np.sqrt((((L[:, None, :] - o1[None, :, :]) ** 2).sum(-1)).min(1))
tag = np.where((np.minimum(D0, D1) >= 2.0), 'X', np.where(D0 < D1, '0', '1'))
s = ''.join(tag)
print("len=" + str(len(L)))
print(s)
sw = sum(1 for i in range(1, len(s)) if s[i] != s[i-1])
print("switches=" + str(sw))
