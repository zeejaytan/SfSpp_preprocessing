import numpy as np
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
import csv
def load_csv(p):
    with open(p) as f: r = list(csv.DictReader(f))
    return np.array([[float(x['x']), float(x['y']), float(x['z'])] for x in r])
P = "C:/PR/SfSpp_preprocessing"
TF = np.loadtxt(P + "/.scratch/pota115_staging/inputs/TF.txt")
R, t = TF[:3,:3], TF[:3,3]
C0 = load_csv(P + "/.scratch/pota162_repro/pota160_repro/C01_ADAPT/veto_align_Pot_C_Piece_01_c0.csv")
print("C0 shape", C0.shape, flush=True)
print("C0row0", C0[0], flush=True)
G0a = load_pcd3(P + "/.scratch/pota162_repro/sfs_main/original_samples/SfS_pp/Breaklines/Pot_C_Piece_01_Breakline_0.pcd") @ R.T + t
d = np.load(P + "/.scratch/pota173_repro/p173_bag.npz", allow_pickle=True)
print("G0allclose", bool(np.allclose(G0a, d["G0"])), flush=True)
D = cKDTree(G0a).query(C0 @ R.T + t)[0]
print("NEAR", int((D<2).sum()), "MID", int(((D>=2)&(D<=5)).sum()), "FAR", int((D>5).sum()), flush=True)
print("D pct", np.percentile(D,[0,10,50,90,100]), flush=True)
