import numpy as np, sys
sys.path.insert(0, ".scratch/pota201_repro")
from p201_lib import read_pcd
from scipy.spatial import cKDTree
def med(A,B):
    D = cKDTree(B).query(A)[0]; DO = cKDTree(A).query(B)[0]
    return round(float(np.median(D)),4), int((DO<2).sum()), len(B)
G0 = {"01": ".scratch/pota162_repro/sfs_main/original_samples/SfS_pp/Breaklines/Pot_C_Piece_01_Breakline_0.pcd",
      "02": ".scratch/pota204_repro/ORIG_C02_Bl0.pcd",
      "03": ".scratch/pota204_repro/ORIG_C03_Bl0.pcd",
      "04": ".scratch/pota204_repro/ORIG_C04_Bl0.pcd"}
G1 = {"02": ".scratch/pota204_repro/ORIG_C02_Bl1.pcd",
      "03": ".scratch/pota204_repro/ORIG_C03_Bl1.pcd",
      "04": ".scratch/pota204_repro/ORIG_C04_Bl1.pcd"}
F = {"01": ".scratch/pota204_repro/FRESH_C01_Bl0.pcd",
     "02": ".scratch/pota204_repro/FRESH_C02_Bl0.pcd",
     "03": ".scratch/pota204_repro/FRESH_C03_Bl0.pcd",
     "04": ".scratch/pota204_repro/FRESH_C04_Bl0.pcd"}
for pc in ["01","02","03","04"]:
    W = np.load(".scratch/pota204_repro/p204_C%s_true_seated.npy" % pc)
    O = np.load(".scratch/pota204_repro/p204_C%s_outer_seated.npy" % pc)
    A, n1, c1 = read_pcd(G0[pc]); Fr, n2, c2 = read_pcd(F[pc])
    print("C"+pc, "thin-vs-Bl0", med(W,A), "fresh-vs-Bl0", med(Fr,A), "outer-vs-Bl0", med(O,A))
    if pc in G1:
        B, n3, c3 = read_pcd(G1[pc])
        print("C"+pc, "thin-vs-Bl1", med(W,B), "fresh-vs-Bl1", med(Fr,B), "outer-vs-Bl1", med(O,B))
print("GATE DONE")
