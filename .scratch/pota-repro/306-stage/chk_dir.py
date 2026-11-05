import glob, os, numpy as np
def rd(p):
    A = np.loadtxt(p, ndmin=2)
    return A.T
def ang(a, b):
    c = abs(float(np.dot(a, b)) / (np.linalg.norm(a) * np.linalg.norm(b)))
    return float(np.degrees(np.arccos(min(1.0, c))))
for p in sorted(glob.glob("out/union/*.xyz")):
    stem = os.path.basename(p)[:-4]
    U = rd(p); R = rd("out/rel/%s.xyz" % stem)
    a = [min(ang(U[3:6, i], R[3:6, j]) for j in range(R.shape[1])) for i in range(U.shape[1])]
    print("%-22s K=%d  %s" % (stem, U.shape[1], " ".join("%.3f" % x for x in a)))
print()
for p in sorted(glob.glob("out/n305/*.xyz")):
    stem = os.path.basename(p)[:-4]
    O = rd(p); R = rd("out/rel/%s.xyz" % stem)
    a = [min(ang(O[3:6, i], R[3:6, j]) for j in range(R.shape[1])) for i in range(O.shape[1])]
    print("%-22s K=%d  %s" % (stem, O.shape[1], " ".join("%.2f" % x for x in a)))
