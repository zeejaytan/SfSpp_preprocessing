import glob, os, shutil, numpy as np
def rd(p):
    A = np.loadtxt(p, ndmin=2)
    return A.T
def ang(a, b):
    c = abs(float(np.dot(a, b)) / (np.linalg.norm(a) * np.linalg.norm(b)))
    return float(np.degrees(np.arccos(min(1.0, c))))
def wr(p, M):
    with open(p, "w", newline="\n") as f:
        for i in range(M.shape[1]):
            f.write(" ".join("%.12f" % v for v in M[:, i]) + "\n")

for d in ("out/d1", "out/d3"):
    shutil.rmtree(d, ignore_errors=True); os.makedirs(d)

# D1 = the 305 notrunc seed-1 set + P07's second line (diagnostic: GT picks the line)
for p in sorted(glob.glob("out/n305/*.xyz")):
    shutil.copy(p, "out/d1/" + os.path.basename(p))
stem = "Pot_A_Piece_07_Axis"
N = rd("out/n305/%s.xyz" % stem); U = rd("out/union/%s.xyz" % stem); R = rd("out/rel/%s.xyz" % stem)
j = int(np.argmin([ang(U[3:6, i], R[3:6, 1]) for i in range(U.shape[1])]))
M = np.column_stack([N[:, 0], U[:, j]])
wr("out/d1/%s.xyz" % stem, M)
print("D1 P07 = n305 line (%.2f deg L0) + union line %d (%.2f deg L1)" % (
    min(ang(M[3:6,0], R[3:6,k]) for k in range(R.shape[1])), j+1, ang(M[3:6,1], R[3:6,1])))

# D3 = union capped at 3 lines per piece (files are already best-cost first)
tot = 0
for p in sorted(glob.glob("out/union/*.xyz")):
    stem = os.path.basename(p)[:-4]
    U = rd(p); R = rd("out/rel/%s.xyz" % stem)
    M = U[:, :3]; wr("out/d3/%s.xyz" % stem, M); tot += M.shape[1]
    print("  %-22s K=%d ang_to_nearest_released %s" % (stem, M.shape[1],
          " ".join("%.2f" % min(ang(M[3:6,i], R[3:6,k]) for k in range(R.shape[1])) for i in range(M.shape[1]))))
print("D3 total %d lines; D1 total %d" % (tot, sum(rd(p).shape[1] for p in glob.glob("out/d1/*.xyz"))))
