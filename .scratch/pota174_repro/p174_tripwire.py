import numpy as np, os
from scipy.spatial import cKDTree
A = "artifacts/pota171"
R = ".scratch/pota174_repro/refs"
log = open(".scratch/pota174_repro/p174_tripwire.txt", "w")
def say(s):
    print(s, flush=True); log.write(s + "\n")
def cov(X, Y, t=2.0):
    d, _ = cKDTree(Y).query(X)
    return float((d < t).mean()), float(np.median(d)), float(d.max())
pairs = [("01","1"),("02","0"),("03","0"),("04","0"),("05","0"),("06","0")]
for pc, br in pairs:
    ref = os.path.join(R, "Pot_A_Piece_%s_Breakline_%s.xyz" % (pc, br))
    nv = os.path.join(A, "Pot_A_Piece_%s_Breakline_%s_noveto.xyz" % (pc, br))
    cu = os.path.join(".scratch/pota174_repro/cure", "Pot_A_Piece_%s_Breakline_%s.xyz" % (pc, br))
    F = np.loadtxt(ref)[:, :3]
    say("PAIR P%s_%s ref n=%d" % (pc, br, len(F)))
    for tag, p in (("red-noveto", nv), ("blue-cure", cu)):
        if not os.path.exists(p):
            say("  %s: MISSING" % tag); continue
        X = np.loadtxt(p)[:, :3]
        c1, m1, x1 = cov(X, F)
        c2, m2, x2 = cov(F, X)
        say("  %s n=%d: trace-vs-ref cov%.3f med%.2f max%.2f | ref-vs-trace cov%.3f med%.2f max%.2f" % (tag, len(X), c1, m1, x1, c2, m2, x2))
say("DONE")
