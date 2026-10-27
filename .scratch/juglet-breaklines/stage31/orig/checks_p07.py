
import sys, glob, os, hashlib, itertools
import numpy as np
from scipy.spatial import cKDTree

ART = r"C:/PR/structure-from-sherds-pp/artifacts/p07_stage1"
G = os.path.join(ART, "geom")

def load_any(path):
    rows = []
    with open(path, "r", errors="replace") as f:
        for line in f:
            s = line.strip()
            if not s or s.startswith("#"):
                continue
            p = s.split()
            try:
                rows.append([float(p[0]), float(p[1]), float(p[2])])
            except ValueError:
                continue
    return np.array(rows, dtype=float)

print("== RIDE CHECK: Bl0 nearest-surface median distance (mm) ==")
print("piece\tBl0dots\tmed_S0\tmed_S1\tS0_closer")
for bl0 in sorted(glob.glob(os.path.join(G, "*.Bl0.pcd"))):
    stem = os.path.basename(bl0)[:-len(".Bl0.pcd")]
    s0p = os.path.join(G, stem + ".S0.xyz"); s1p = os.path.join(G, stem + ".S1.xyz")
    if not (os.path.exists(s0p) and os.path.exists(s1p)):
        print(stem + "\tMISSING surfaces"); continue
    b = load_any(bl0); s0 = load_any(s0p); s1 = load_any(s1p)
    d0 = cKDTree(s0).query(b)[0]; d1 = cKDTree(s1).query(b)[0]
    print("%s\t%d\t%.3f\t%.3f\t%s" % (stem, len(b), np.median(d0), np.median(d1), "YES" if np.median(d0) < np.median(d1) else "NO"))

print()
print("== MD5 UNIQUENESS per file class (12 pieces x 4 files) ==")
files = sorted(glob.glob(os.path.join(G, "*")))
md5 = {}
for f in files:
    h = hashlib.md5(open(f, "rb").read()).hexdigest()
    md5[f] = h
for suf in (".S0.xyz", ".S1.xyz", ".Bl0.pcd", ".Bl1.pcd"):
    grp = [(os.path.basename(f)[:-len(suf)], md5[f]) for f in files if f.endswith(suf)]
    byhash = {}
    for piece, h in grp:
        byhash.setdefault(h, []).append(piece)
    dup = {h: v for h, v in byhash.items() if len(v) > 1}
    print("%s: n=%d distinct_md5=%d duplicates=%s" % (suf, len(grp), len(byhash), dup if dup else "NONE"))
allh = {}
for f, h in md5.items():
    allh.setdefault(h, []).append(os.path.basename(f))
print("across ALL 48 files: distinct=%d of %d" % (len(allh), len(md5)))
