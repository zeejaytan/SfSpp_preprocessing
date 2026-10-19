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
def load_ply_vn(p):
    V, N, in_v = [], [], False
    for ln in open(p):
        s = ln.strip()
        if s.startswith('end_header'): in_v = True; continue
        if not in_v or not s: continue
        try: v = list(map(float, s.split()[:6]))
        except ValueError: continue
        V.append(v[:3]); N.append(v[3:6])
    return np.array(V), np.array(N)
log = open(".scratch/pota174_repro/p174_facespill.txt", "w")
def say(s):
    print(s, flush=True); log.write(s + "\n")
# face-spill: staged S1 (second face, control split) vs thr_8 S0
S1 = load_xyz(".scratch/pota163_repro/inputs/C01S1_STAGED.xyz")[:,:3]
S8 = load_xyz(".scratch/pota174_repro/sweep/thr_8/Pot_C_Piece_01_Surface_0.xyz")[:,:3]
S45 = load_xyz(".scratch/pota174_repro/sweep/thr_4.5/Pot_C_Piece_01_Surface_0.xyz")[:,:3]
K8, K45 = cKDTree(S8), cKDTree(S45)
d8 = K8.query(S1)[0]; d45 = K45.query(S1)[0]
say("S1 n=%d" % len(S1))
say("S1->thr8-S0: med %.3f max %.3f frac<1mm %.3f frac<2mm %.3f" % (np.median(d8), d8.max(), (d8<1).mean(), (d8<2).mean()))
say("S1->ctl-S0: med %.3f max %.3f frac<1mm %.3f frac<2mm %.3f" % (np.median(d45), d45.max(), (d45<1).mean(), (d45<2).mean()))
say("FACE-SPILL verdict: " + ("SPILL -- second face absorbed into S0" if (d8<1).mean()>0.9 and (d45<1).mean()<0.5 else "check numbers"))
