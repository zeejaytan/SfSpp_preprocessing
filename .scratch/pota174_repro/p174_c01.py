import numpy as np
from scipy.spatial import cKDTree
def load_xyz(p, cols=3):
    rows = []
    for ln in open(p):
        s = ln.strip()
        if not s or s[0] == '#': continue
        try: rows.append(list(map(float, s.split()[:cols])))
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
runs = [(0,1),(3,21),(23,30),(34,68),(72,81),(83,88),(93,124),(126,136),(139,143),(145,147),(151,156),(158,203),(206,210)]
gidx = np.concatenate([np.arange(a,b+1) for a,b in runs])
G = G0[gidx]
log = open(".scratch/pota174_repro/p174_C01_reclaim.txt", "w")
def say(s):
    print(s, flush=True); log.write(s + "\n")
for tag in ["reclaim", "ctl"]:
    import os
    p = ".scratch/pota174_repro/run/C01_%s_S0.xyz" % tag
    if not os.path.exists(p):
        say("%s: MISSING" % tag); continue
    S = load_xyz(p)[:, :3] @ R.T + t
    d = cKDTree(S).query(G)[0]
    say("%s S0 n=%d GAP188: min %.3f med %.3f max %.3f frac<2mm %.3f n<2 %d/188" % (tag, len(S), d.min(), np.median(d), d.max(), (d<2).mean(), int((d<2).sum())))
say("DONE")
