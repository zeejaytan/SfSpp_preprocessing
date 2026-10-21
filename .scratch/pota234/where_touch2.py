import sys, numpy as np
def xyz(p):
    d = np.loadtxt(p)
    return np.atleast_2d(d)[:, :3]
S0 = xyz(sys.argv[1]); S1 = xyz(sys.argv[2])
turn = np.array([float(x) for x in sys.argv[3:6]])
best = (1e18, None, None)
for s in range(0, len(S0), 2000):
    A = S0[s:s + 2000]
    d2 = ((A[:, None, :] - S1[None, :, :]) ** 2).sum(-1)
    i, j = np.unravel_index(np.argmin(d2), d2.shape)
    if d2[i, j] < best[0]:
        best = (d2[i, j], A[i].copy(), S1[j].copy())
pa, pb = best[1], best[2]
print('symmin=%.3f S0=%s S1=%s' % (np.sqrt(best[0]), pa, pb))
mid = (pa + pb) / 2
print('mid-to-turn=%.2f' % np.linalg.norm(mid - turn))
