import glob, os, shutil, numpy as np
def rd(p):
    A = np.loadtxt(p, ndmin=2); return A.T
def wr(p, M):
    with open(p, "w", newline="\n") as f:
        for i in range(M.shape[1]):
            f.write(" ".join("%.12f" % v for v in M[:, i]) + "\n")
for d in ("out/d4", "out/d7"):
    shutil.rmtree(d, ignore_errors=True); os.makedirs(d)
for p in sorted(glob.glob("out/n305/*.xyz")):
    shutil.copy(p, "out/d4/" + os.path.basename(p)); shutil.copy(p, "out/d7/" + os.path.basename(p))
stem = "Pot_A_Piece_07_Axis"
N = rd("out/n305/%s.xyz" % stem); R = rd("out/rel/%s.xyz" % stem)
wr("out/d7/%s.xyz" % stem, np.column_stack([N[:, 0], R[:, 1]]))
shutil.copy("out/rel/%s.xyz" % stem, "out/d4/%s.xyz" % stem)
print("D7 P07 = n305 + released line 2 (2 lines); D4 P07 = released file (%d lines)" % R.shape[1])
