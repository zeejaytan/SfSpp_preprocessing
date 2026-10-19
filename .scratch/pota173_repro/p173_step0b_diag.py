# 173 step0b: diagnose merged-sheet fire loss (r sensitivity + fire locations).
import numpy as np
from scipy.spatial import cKDTree
H = ".scratch/pota173_repro"
log = open(H + "/p173_step0b.txt", "w")
def say(s):
    print(s, flush=True); log.write(s + "\n")
def load_pcd3(p):
    HDR = ('VERSION','FIELDS','SIZE','TYPE','COUNT','WIDTH','HEIGHT','VIEWPOINT','POINTS','DATA')
    P = []
    for ln in open(p):
        s = ln.strip()
        if not s or s[0] == '#' or s.split()[0] in HDR: continue
        try: P.append(list(map(float, s.split()[:3])))
        except ValueError: continue
    return np.array(P)
TH = 0.6*np.pi
def pcl_flags(Xe, Ne, r):
    Kq = cKDTree(Xe)
    ball = Kq.query_ball_point(Xe, r)
    flags = np.zeros(len(Xe), dtype=bool)
    for i in range(len(Xe)):
        nb = [j for j in ball[i] if j != i]
        if len(nb) < 3: continue
        n = Ne[i]
        VV = Xe[nb]-Xe[i]
        VV = VV - np.outer(VV@n, n)
        up = np.array([0.0,0.0,1.0]) if abs(n[2]) < 0.9 else np.array([1.0,0.0,0.0])
        u = up - (up@n)*n; u = u/np.linalg.norm(u)
        v = np.cross(n, u)
        ang = np.sort(np.arctan2(VV@v, VV@u))
        dif = np.diff(ang)
        wrap = 2*np.pi - (ang[-1]-ang[0])
        flags[i] = max(dif.max(), wrap) > TH
    return flags
T = np.loadtxt(".scratch/pota162_repro/sfs_main/original_samples/SfS_pp/Ground Truth/Pot_C_Piece_1_T.txt")
R, t = T[:3,:3], T[:3,3]
S = np.loadtxt(".scratch/pota163_repro/inputs/C01S0_STAGED.xyz")
X, N = S[:,:3], S[:,3:6]
def load_ply_xn(p):
    XX, NN = [], []
    for ln in open(p):
        s = ln.strip()
        if not s or s[0] == '#' or s.startswith(('ply','format','element','property','end_header','comment')): continue
        f = s.split()
        try: vals = list(map(float, f[:7]))
        except ValueError: continue
        if len(vals) < 6: continue
        XX.append(vals[0:3]); NN.append(vals[3:6])
    return np.array(XX), np.array(NN)
U, UN = load_ply_xn(".scratch/pota163_repro/inputs/Pot_C_Piece_01_unclustered.ply")
Ug = U @ R.T + t
G0 = load_pcd3(".scratch/pota162_repro/sfs_main/original_samples/SfS_pp/Breaklines/Pot_C_Piece_01_Breakline_0.pcd") @ R.T + t
z = np.load(".scratch/pota172_repro/p172_meshgap.npz")
gidx, runs = z["gidx"], [tuple(map(int,r)) for r in z["runs"]]
d_to_G0 = cKDTree(G0).query(Ug)[0]
strip = np.where(d_to_G0 <= 2.5)[0]
Xm = np.vstack([X, U[strip]]); Nm = np.vstack([N, UN[strip]])
Ns = len(X)
# strip spacing (consecutive, station-ordered)
sta = cKDTree(G0).query(Ug[strip])[1]
o = np.argsort(sta, kind="stable")
Q = Ug[strip][o]
g = np.sqrt(((Q[1:]-Q[:-1])**2).sum(-1))
say("strip station-ordered consecutive spacing: n=%d med=%.2f p90=%.2f max=%.2f" % (len(g), float(np.median(g)), float(np.percentile(g,90)), float(g.max())))
# r sensitivity
for rr in [6.4657, 6.2954]:
    f = pcl_flags(Xm, Nm, rr)
    say("r=%.4f merged fired=%d strip-fires=%d/%d" % (rr, int(f.sum()), int(f[Ns:].sum()), len(strip)))
f_old = pcl_flags(X, N, 6.4657)
say("S0-only recheck fired=%d (expect 364)" % int(f_old.sum()))
f_new = pcl_flags(Xm, Nm, 6.4657)
say("merged r=6.4657: fired=%d strip-fires=%d" % (int(f_new.sum()), int(f_new[Ns:].sum())))
# where are lost S0 fires? (S0 fires not within 0.5mm of any merged fire, gate frame)
Xg = X @ R.T + t; Xmg = Xm @ R.T + t
lost = np.where(f_old)[0][cKDTree(Xmg[f_new]).query(Xg[f_old])[0] > 0.5]
say("lost S0 fires at r=6.4657: %d" % len(lost))
if len(lost):
    dl = cKDTree(G0).query(Xg[lost])[0]
    say("  lost dist-to-ORIG: min=%.2f med=%.2f max=%.2f" % (dl.min(), float(np.median(dl)), dl.max()))
    # nearest gap run?
    sl = cKDTree(G0).query(Xg[lost])[1]
    import collections
    runs_of = []
    for s in sl:
        hit = [ri for ri,(a,b) in enumerate(runs) if a <= s <= b]
        runs_of.append(hit[0] if hit else -1)
    say("  lost by run: %s" % dict(collections.Counter(runs_of)))
# where are strip fires? per run (nearest ORIG station)
sf = np.where(f_new[Ns:])[0]
say("strip fires: %d" % len(sf))
if len(sf):
    ss = cKDTree(G0).query((U[strip][sf]) @ R.T + t)[1]
    import collections
    runs_sf = []
    for s in ss:
        hit = [ri for ri,(a,b) in enumerate(runs) if a <= s <= b]
        runs_sf.append(hit[0] if hit else -1)
    say("  strip-fire by run: %s" % dict(collections.Counter(runs_sf)))
    dsf = cKDTree(G0).query((U[strip][sf]) @ R.T + t)[0]
    say("  strip-fire dist-to-ORIG: min=%.2f med=%.2f max=%.2f" % (dsf.min(), float(np.median(dsf)), dsf.max()))
say("DIAG DONE")
log.close()
