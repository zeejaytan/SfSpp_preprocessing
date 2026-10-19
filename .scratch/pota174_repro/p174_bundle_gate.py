import numpy as np, os, glob
from scipy.spatial import cKDTree
def load_pcd3(p):
    HDR = ('VERSION','FIELDS','SIZE','TYPE','COUNT','WIDTH','HEIGHT','VIEWPOINT','POINTS','DATA')
    P = []
    for ln in open(p):
        s = ln.strip()
        if not s or s[0] == '#' or s.split()[0] in HDR: continue
        try: P.append(list(map(float, s.split()[:3])))
        except ValueError: continue
    return np.array(P)
def load_xyz(p, cols=3):
    rows = []
    for ln in open(p):
        s = ln.strip()
        if not s or s[0] == '#': continue
        try: rows.append(list(map(float, s.split()[:cols])))
        except ValueError: continue
    return np.array(rows)
B = ".scratch/pota174_repro/bundle"
os.makedirs(B, exist_ok=True)
import shutil
for f in glob.glob("/tmp/nonexistent"):
    pass
log = open(".scratch/pota174_repro/p174_bundle_gate.txt", "w")
def say(s):
    print(s, flush=True); log.write(s + "\n")
pairs = [("01","1"),("02","0"),("03","0"),("04","0"),("05","0"),("06","0")]
for pc, br in pairs:
    src = ".scratch/pota174_repro/bundle_src/Pot_A_Piece_%s_Breakline_%s.pcd" % (pc, br)
    F = load_pcd3(src)
    np.savetxt(".scratch/pota174_repro/bundle/Pot_A_Piece_%s_Breakline_%s.xyz" % (pc, br), F, fmt="%.6f")
    say("bundle P%s_%s n=%d" % (pc, br, len(F)))
    for tag, p in (("red-noveto", "artifacts/pota171/Pot_A_Piece_%s_Breakline_%s_noveto.xyz" % (pc, br)),
                   ("blue-cure", ".scratch/pota174_repro/cure/Pot_A_Piece_%s_Breakline_%s.xyz" % (pc, br)),
                   ("worktree-ref", ".scratch/pota174_repro/refs/Pot_A_Piece_%s_Breakline_%s.xyz" % (pc, br))):
        import os as _os
        if not _os.path.exists(p):
            say("  %s: MISSING" % tag); continue
        X = load_xyz(p)
        d1 = cKDTree(F).query(X)[0]; d2 = cKDTree(X).query(F)[0]
        say("  %s n=%d: trace-vs-bun cov%.3f med%.2f max%.2f | bun-vs-trace cov%.3f med%.2f max%.2f" % (tag, len(X), (d1<2).mean(), np.median(d1), d1.max(), (d2<2).mean(), np.median(d2), d2.max()))
say("DONE")
