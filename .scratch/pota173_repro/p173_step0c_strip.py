# 173 step0c: ORIG-free strip definitions + their ORIG-proximity (measurement only).
import numpy as np
from scipy.spatial import cKDTree
H = ".scratch/pota173_repro"
log = open(H + "/p173_step0c.txt", "w")
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
def load_ply_x(p):
    XX = []
    for ln in open(p):
        s = ln.strip()
        if not s or s[0] == '#' or s.startswith(('ply','format','element','property','end_header','comment')): continue
        f = s.split()
        try: vals = list(map(float, f[:3]))
        except ValueError: continue
        XX.append(vals)
    return np.array(XX)
import csv
def load_csv(p):
    with open(p) as f: r = list(csv.DictReader(f))
    return np.array([[float(x['x']), float(x['y']), float(x['z'])] for x in r])
T = np.loadtxt(".scratch/pota162_repro/sfs_main/original_samples/SfS_pp/Ground Truth/Pot_C_Piece_1_T.txt")
R, t = T[:3,:3], T[:3,3]
S = np.loadtxt(".scratch/pota163_repro/inputs/C01S0_STAGED.xyz")[:,:3]
U = load_ply_x(".scratch/pota163_repro/inputs/Pot_C_Piece_01_unclustered.ply")
Ug = U @ R.T + t
G0 = load_pcd3(".scratch/pota162_repro/sfs_main/original_samples/SfS_pp/Breaklines/Pot_C_Piece_01_Breakline_0.pcd") @ R.T + t
C0 = load_csv(".scratch/pota162_repro/pota160_repro/C01_ADAPT/veto_align_Pot_C_Piece_01_c0.csv")
F0 = C0  # local frame S0-fired
Ksheet = cKDTree(S)
d_off = Ksheet.query(U)[0]
say("unclustered dist-to-S0-sheet: <1mm=%d | 1-2=%d | 2-6=%d | >6=%d (n=%d)" % (int((d_off<1).sum()), int(((d_off>=1)&(d_off<2)).sum()), int(((d_off>=2)&(d_off<6)).sum()), int((d_off>=6).sum()), len(U)))
KF = cKDTree(F0)
d_edge = KF.query(U)[0]
say("unclustered dist-to-S0fired-edge: <1=%d | 1-2.5=%d | 2.5-6=%d | >6=%d" % (int((d_edge<1).sum()), int(((d_edge>=1)&(d_edge<2.5)).sum()), int(((d_edge>=2.5)&(d_edge<6)).sum()), int((d_edge>=6).sum())))
cand = np.where((d_off>=1.0)&(d_edge<6.0))[0]
say("ORIG-free candidate (off-sheet>=1mm & edge-adjacent<6mm): n=%d" % len(cand))
d_cand_orig = cKDTree(G0).query(Ug[cand])[0]
say("  cand dist-to-ORIG: min=%.2f med=%.2f max=%.2f frac<2.5=%.3f" % (d_cand_orig.min(), float(np.median(d_cand_orig)), d_cand_orig.max(), float((d_cand_orig<2.5).mean())))
z = np.load(".scratch/pota172_repro/p172_meshgap.npz")
gidx = z["gidx"]
d_cand_gap = cKDTree(Ug[cand]).query(G0[gidx])[0]
say("  gap station -> cand: min=%.2f med=%.2f max=%.2f frac<2=%.3f" % (d_cand_gap.min(), float(np.median(d_cand_gap)), d_cand_gap.max(), float((d_cand_gap<2).mean())))
d_all_gap = cKDTree(Ug).query(G0[gidx])[0]
say("  gap station -> ALL unclustered: max=%.2f frac<2=%.3f" % (d_all_gap.max(), float((d_all_gap<2).mean())))
# ORIG-guided strip recall check: how much of ORIG-guided 612 is in cand?
d_to_G0 = cKDTree(G0).query(Ug)[0]
strip = np.where(d_to_G0 <= 2.5)[0]
say("ORIG-guided strip n=%d; overlap with cand=%d" % (len(strip), len(np.intersect1d(strip, cand))))
np.save(H + "/p173_cand.npy", cand)
say("STRIP DONE")
log.close()
