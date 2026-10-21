import sys, numpy as np
def xyz(p):
    d = np.loadtxt(p)
    return np.atleast_2d(d)[:, :3]
S0 = xyz(sys.argv[1]); S1 = xyz(sys.argv[2])
turn = np.array([float(x) for x in sys.argv[3:6]])
# subsample for speed
A = S0[::3]; B = S1[::3]
d2 = ((A[:, None, :] - B[None, :, :]) ** 2).sum(-1)
i, j = np.unravel_index(np.argmin(d2), d2.shape)
pa, pb = A[i], B[j]
print('min-dist pair: S0 %s S1 %s dist=%.3f' % (pa, pb, np.sqrt(d2[i, j])))
print('dist pair-mid to turn: %.2f' % np.linalg.norm((pa + pb) / 2 - turn))
print('S0 pair-pt to turn: %.2f  S1 pair-pt to turn: %.2f' % (np.linalg.norm(pa - turn), np.linalg.norm(pb - turn)))
