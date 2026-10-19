import numpy as np, os, glob
from scipy.spatial import cKDTree
H = ".scratch/pota174_repro/sweep"
OUT = "artifacts/pota174"
os.makedirs(OUT, exist_ok=True)
log = open(".scratch/pota174_repro/p174_gate_sweep.txt", "w")
def say(s):
    print(s, flush=True); log.write(s + "\n")
def load_xyz(p):
    rows = []
    for ln in open(p):
        s = ln.strip()
        if not s or s[0] == '#': continue
        try: rows.append(list(map(float, s.split()[:3])))
        except ValueError: continue
    return np.array(rows)
T = np.loadtxt(".scratch/pota162_repro/sfs_main/original_samples/SfS_pp/Ground Truth/Pot_C_Piece_1_T.txt")
R, t = T[:3,:3], T[:3,3]
def load_pcd3(p):
    HDR = ('VERSION','FIELDS','SIZE','TYPE','COUNT','WIDTH','HEIGHT','VIEWPOINT','POINTS','DATA')
    P = []
    for ln in open(p):
        s = ln.strip()
        if not s or s[0] == '#' or s.split()[0] in HDR: continue
        try: P.append(list(map(float, s.split()[:3])))
        except ValueError: continue
    return np.array(P)
G0 = load_pcd3(".scratch/pota162_repro/sfs_main/original_samples/SfS_pp/Breaklines/Pot_C_Piece_01_Breakline_0.pcd") @ R.T + t
assert G0.shape == (211, 3)
runs = [(0,1),(3,21),(23,30),(34,68),(72,81),(83,88),(93,124),(126,136),(139,143),(145,147),(151,156),(158,203),(206,210)]
gidx = np.concatenate([np.arange(a,b+1) for a,b in runs])
G = G0[gidx]
say("gap stations n=%d" % len(G))
Sref = load_xyz(".scratch/pota163_repro/inputs/C01S0_STAGED.xyz")[:,:3] @ R.T + t
say("staged S0 n=%d" % len(Sref))
for arm in ["4.5", "8", "12", "20"]:
    d = os.path.join(H, "thr_" + arm)
    if not os.path.isdir(d):
        say("ARM %s: MISSING" % arm); continue
    cands = sorted(glob.glob(os.path.join(d, "*Surface_0*")))
    if not cands:
        say("ARM %s: no Surface_0 in %s" % (arm, sorted(os.listdir(d)))); continue
    S = load_xyz(cands[0])[:,:3] @ R.T + t
    say("ARM %s: n=%d file=%s" % (arm, len(S), os.path.basename(cands[0])))
    KX = cKDTree(S)
    d_all = KX.query(G0)[0]
    d_gap = KX.query(G)[0]
    say("  ORIG211: min %.3f med %.3f max %.3f frac<2mm %.3f" % (d_all.min(), np.median(d_all), d_all.max(), (d_all<2).mean()))
    say("  GAP188: min %.3f med %.3f max %.3f frac<2mm %.3f n<2 %d/188" % (d_gap.min(), np.median(d_gap), d_gap.max(), (d_gap<2).mean(), int((d_gap<2).sum())))
    o = 0
    for ri,(a,b) in enumerate(runs):
        m = np.isin(gidx, np.arange(a,b+1))
        dd = d_gap[m]
        say("    R%d n=%d min %.3f med %.3f max %.3f <2mm %d/%d" % (ri, m.sum(), dd.min(), np.median(dd), dd.max(), int((dd<2).sum()), m.sum()))
    Kc = cKDTree(Sref)
    dc = Kc.query(S)[0]
    say("  vs-staged-S0: new->staged med %.3f max %.3f (reach gain if med>0 at rim)" % (np.median(dc), dc.max()))
    Kr = cKDTree(S)
    dr = Kr.query(Sref)[0]
    say("  staged->new (old covered?): med %.3f max %.3f fracoldcov<1mm %.3f" % (np.median(dr), dr.max(), (dr<1).mean()))
say("DONE")
