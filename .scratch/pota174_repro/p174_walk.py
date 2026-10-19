import numpy as np, os
from scipy.spatial import cKDTree
H = ".scratch/pota174_repro/run"
OUTLOG = ".scratch/pota174_repro/p174_walk.txt"
log = open(OUTLOG, "w")
def say(s):
    print(s, flush=True); log.write(s + "\n")
def load_xyz(p, cols=3):
    rows = []
    for ln in open(p):
        s = ln.strip()
        if not s or s[0] == '#': continue
        try: rows.append(list(map(float, s.split()[:cols])))
        except ValueError: continue
    return np.array(rows)
def load_pcd3(p):
    HDR = ('VERSION','FIELDS','SIZE','TYPE','COUNT','WIDTH','HEIGHT','VIEWPOINT','POINTS','DATA')
    P = []
    for ln in open(p):
        s = ln.strip()
        if not s or s[0] == '#' or s.split()[0] in HDR: continue
        try: P.append(list(map(float, s.split()[:3])))
        except ValueError: continue
    return np.array(P)
T = np.loadtxt(".scratch/pota162_repro/sfs_main/original_samples/SfS_pp/Ground Truth/Pot_C_Piece_1_T.txt")
R, t = T[:3,:3], T[:3,3]
G0 = load_pcd3(".scratch/pota162_repro/sfs_main/original_samples/SfS_pp/Breaklines/Pot_C_Piece_01_Breakline_0.pcd") @ R.T + t
N = len(G0)
B0 = load_xyz(H + "/C01_walk_Bl_0.xyz")
B1f = H + "/C01_walk_Bl_1.xyz"
B1 = load_xyz(B1f) if os.path.exists(B1f) else np.zeros((0,3))
say("walk inputs: Bl_0 n=%d Bl_1 n=%d ORIG %d" % (len(B0), len(B1), N))
def walk(Tb):
    W = len(Tb)
    if W < 2: return np.array([], dtype=int)
    X32 = Tb.astype(np.float32); kk = np.array([X32[i].tobytes() for i in range(W)])
    cvis = {kk[0]: 0}; cseq = [0]; cur = 0
    for tt in range(1, W):
        dd = np.sqrt(((Tb - Tb[cur]) ** 2).sum(-1))
        idx = np.argsort(dd, kind="stable")[:34]
        if tt == 1:
            nxt = int(idx[1]); cseq.append(nxt); cvis[kk[nxt]] = 1; cur = nxt; continue
        unv = [int(j) for j in idx if kk[int(j)] not in cvis]
        if not unv: break
        j = int(unv[0]); cseq.append(j); cvis[kk[j]] = len(cseq)-1; cur = j
    seq = list(cseq); guard = 0
    while len(set(seq)) < W and guard < 60000:
        guard += 1
        dd = np.sqrt(((Tb - Tb[cur]) ** 2).sum(-1))
        idx = np.argsort(dd, kind="stable")[:34]
        sset = set(seq); nxt = None
        for j in idx:
            j = int(j)
            if j not in sset and float(dd[j]) >= 1.0: nxt = j; break
        if nxt is not None:
            seq.append(nxt); cur = nxt; continue
        break
    return np.array(seq)
s0 = walk(B0); s1 = walk(B1)
L1 = B0[s0] if len(s0) else np.zeros((0,3))
L2 = B1[s1] if len(s1) else np.zeros((0,3))
say("strand0 len=%d/%d strand1 len=%d/%d" % (len(s0), len(B0), len(s1), len(B1)))
D1 = cKDTree(G0).query(L1)[0] if len(L1) else np.full(N, 1e9)
D2 = cKDTree(G0).query(L2)[0] if len(L2) else np.full(N, 1e9)
DO1 = cKDTree(L1).query(G0)[0] if len(L1) else np.full(N, 1e9)
DO2 = cKDTree(L2).query(G0)[0] if len(L2) else np.full(N, 1e9)
if len(L1) and len(L2):
    Lu = np.vstack([L1, L2]); Du = cKDTree(G0).query(Lu)[0]; DOu = np.minimum(DO1, DO2)
elif len(L1):
    Du, DOu = D1, DO1
else:
    Du, DOu = D2, DO2
say("strand0-alone: ORIGcov=%d/211 med=%.4f <2mm=%.1f%%" % (int((DO1<2).sum()), float(np.median(D1)), float((D1<2).mean()*100)))
say("strand1-alone: ORIGcov=%d/211 med=%.4f <2mm=%.1f%%" % (int((DO2<2).sum()), float(np.median(D2)), float((D2<2).mean()*100)))
say("UNION: ORIGcov=%d/211 med=%.4f <2mm=%.1f%%" % (int((DOu<2).sum()), float(np.median(Du)), float((Du<2).mean()*100)))
say("fresh-bar(170): 92/211 | 173 union: 211/211 med 1.26")
say("DONE")
