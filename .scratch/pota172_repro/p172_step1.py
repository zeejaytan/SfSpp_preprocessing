import numpy as np
from scipy.spatial import cKDTree
H = ".scratch/pota172_repro"
log = open(H + "/p172_step1.txt", "w")
def say(s):
    print(s, flush=True); log.write(s + "\n")
T = np.loadtxt(".scratch/pota162_repro/sfs_main/original_samples/SfS_pp/Ground Truth/Pot_C_Piece_1_T.txt")
R, t = T[:3,:3], T[:3,3]
def load_ply3(p):
    U = []
    for ln in open(p):
        s = ln.strip()
        if not s or s[0] == '#' or s.startswith(('ply','format','element','property','end_header')): continue
        try: U.append(list(map(float, s.split()[:3])))
        except ValueError: continue
    return np.array(U)
U = load_ply3(".scratch/pota163_repro/inputs/Pot_C_Piece_01_unclustered.ply")
say("unclustered n=%d" % len(U))
Ug = U @ R.T + t
z = np.load(H + "/p172_meshgap.npz")
gidx, d_sheet, d_surf = z["gidx"], z["d_sheet"], z["d_surf"]
runs = [tuple(map(int, r)) for r in z["runs"]]
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
G = G0[gidx]
S = np.loadtxt(".scratch/pota163_repro/inputs/C01S0_STAGED.xyz")[:,:3] @ R.T + t
KU = cKDTree(Ug); KS = cKDTree(S)
d_unc = KU.query(G)[0]
say("gap station -> nearest unclustered: min %.3f med %.3f max %.3f | frac<2mm %.3f" % (
    d_unc.min(), float(np.median(d_unc)), d_unc.max(), float((d_unc < 2.0).mean())))
# the near-rim unclustered points: how far are THEY from the sheet (are they the missing strip)?
d2, j2 = KU.query(G, k=1)
near_pts = Ug[j2[d_unc < 2.0]]
d_near_to_sheet = KS.query(near_pts)[0]
say("near-rim unclustered pts n=%d: dist-to-sheet min %.2f med %.2f max %.2f" % (
    len(near_pts), d_near_to_sheet.min(), float(np.median(d_near_to_sheet)), d_near_to_sheet.max()))
say("--- per-run station->unclustered min/med/max ---")
for ri, (a, b) in enumerate(runs):
    m = (gidx >= a) & (gidx <= b)
    du = d_unc[m]
    say("R%-2d: unc min %.2f med %.2f max %.2f | lt2 %d/%d" % (ri, du.min(), float(np.median(du)), du.max(), int((du < 2.0).sum()), m.sum()))
np.savez(H + "/p172_unclustered.npz", d_unc=d_unc)
log.close(); print("STEP1 DONE")
