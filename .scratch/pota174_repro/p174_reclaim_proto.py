import numpy as np
from scipy.spatial import cKDTree
def load_xyz(p, cols=6):
    rows = []
    for ln in open(p):
        s = ln.strip()
        if not s or s[0] == '#': continue
        try: rows.append(list(map(float, s.split()[:cols])))
        except ValueError: continue
    return np.array(rows)
def load_ply_vn(p):
    V, N, in_v = [], [], False
    for ln in open(p):
        s = ln.strip()
        if s.startswith('end_header'): in_v = True; continue
        if not in_v or not s: continue
        parts = s.split()
        if len(parts) < 6: continue
        try: v = list(map(float, parts[:6]))
        except ValueError: continue
        V.append(v[:3]); N.append(v[3:6])
    V = np.array(V); N = np.array(N)
    return V, N / np.maximum(np.linalg.norm(N, axis=1, keepdims=True), 1e-12)
log = open(".scratch/pota174_repro/p174_reclaim.txt", "w")
def say(s):
    print(s, flush=True); log.write(s + "\n")
S0 = load_xyz(".scratch/pota163_repro/inputs/C01S0_STAGED.xyz")
S1 = load_xyz(".scratch/pota163_repro/inputs/C01S1_STAGED.xyz")
say("S0 %s S1 %s" % (S0.shape, S1.shape))
U, UN = load_ply_vn(".scratch/pota163_repro/inputs/Pot_C_Piece_01_unclustered.ply")
say("unclustered n=%d" % len(U))
N0 = S0[:,3:6]; N0 /= np.maximum(np.linalg.norm(N0,axis=1,keepdims=True),1e-12)
N1 = S1[:,3:6]; N1 /= np.maximum(np.linalg.norm(N1,axis=1,keepdims=True),1e-12)
D, A = 1.5, np.cos(np.deg2rad(25))
P = np.vstack([S0[:,:3], S1[:,:3]])
PN = np.vstack([N0, N1])
owner = np.array([0]*len(S0) + [1]*len(S1))
free = np.ones(len(U), bool)
admit_S0, admit_S1 = [], []
for rnd in range(6):
    K = cKDTree(P)
    dd, ii = K.query(U[free])
    take = dd < D
    idx = np.where(free)[0][take]
    nn = PN[ii[take]]
    un = UN[np.where(free)[0][take]]
    ok = np.einsum('ij,ij->i', nn, un) > A
    got = idx[ok]
    if len(got) == 0:
        say("round %d: none" % rnd); break
    P = np.vstack([P, U[got]])
    PN = np.vstack([PN, UN[got]])
    ow = owner[ii[take][ok]]
    owner = np.concatenate([owner, ow])
    admit_S0.append(int((ow==0).sum())); admit_S1.append(int((ow==1).sum()))
    free[got] = False
    say("round %d: +%d (S0 %d S1 %d) free=%d" % (rnd, len(got), int((ow==0).sum()), int((ow==1).sum()), int(free.sum())))
G0 = []
def load_pcd3(p):
    HDR = ('VERSION','FIELDS','SIZE','TYPE','COUNT','WIDTH','HEIGHT','VIEWPOINT','POINTS','DATA')
    P_ = []
    for ln in open(p):
        s = ln.strip()
        if not s or s[0] == '#' or s.split()[0] in HDR: continue
        try: P_.append(list(map(float, s.split()[:3])))
        except ValueError: continue
    return np.array(P_)
T = np.loadtxt(".scratch/pota162_repro/sfs_main/original_samples/SfS_pp/Ground Truth/Pot_C_Piece_1_T.txt")
R, t = T[:3,:3], T[:3,3]
G0 = load_pcd3(".scratch/pota162_repro/sfs_main/original_samples/SfS_pp/Breaklines/Pot_C_Piece_01_Breakline_0.pcd") @ R.T + t
runs = [(0,1),(3,21),(23,30),(34,68),(72,81),(83,88),(93,124),(126,136),(139,143),(145,147),(151,156),(158,203),(206,210)]
gidx = np.concatenate([np.arange(a,b+1) for a,b in runs])
G = G0[gidx]
Pg = P @ R.T + t
K = cKDTree(Pg)
d = K.query(G)[0]
say("RECLAIMED sheet n=%d (S0+%d S1+%d)" % (len(Pg), sum(admit_S0), sum(admit_S1)))
say("GAP188: min %.3f med %.3f max %.3f frac<2mm %.3f n<2 %d/188" % (d.min(), np.median(d), d.max(), (d<2).mean(), int((d<2).sum())))
o = 0
for ri,(a,b) in enumerate(runs):
    m = np.isin(gidx, np.arange(a,b+1))
    dd = d[m]
    say("  R%d n=%d max %.3f <2mm %d/%d" % (ri, m.sum(), dd.max(), int((dd<2).sum()), m.sum()))
# faces still split? S1-grown vs S0-grown separation: min dist between the two grown sets
K0 = cKDTree(Pg[owner==0])
d1 = K0.query(Pg[owner==1])[0]
say("S1-grown -> S0-grown: min %.3f med %.3f (faces distinct if min>>0)" % (d1.min(), np.median(d1)))
np.save(".scratch/pota174_repro/p174_reclaimed.npy", Pg)
say("saved p174_reclaimed.npy")
