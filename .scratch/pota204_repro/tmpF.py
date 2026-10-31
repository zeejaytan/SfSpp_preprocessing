import numpy as np, sys
sys.path.insert(0, ".scratch/pota176_repro")
from p176_lib import load_pcd3
from scipy.spatial import cKDTree
def med(A,B):
    D = np.sqrt(((A[:,None,:]-B[None,:,:])**2).sum(-1)).min(1)
    return float(np.median(D))
W = np.load(".scratch/pota204_repro/p204_C01_true_walk.npy")
T = np.loadtxt(".scratch/pota176_repro/inputs/Pot_C_Piece_1_T.txt"); Rr,t = T[:3,:3], T[:3,3]
O1 = load_pcd3(".scratch/pota162_repro/sfs_main/original_samples/SfS_pp/Breaklines/Pot_C_Piece_01_Breakline_0.pcd")
print("walk", W.shape, "mean", W.mean(0).round(1))
print("ORIG", O1.shape, "mean", O1.mean(0).round(1))
print("med(walk,ORIG) =", round(med(W,O1),3))
print("med(walk,ORIG@T) =", round(med(W,O1@Rr.T+t),3))
print("med(ORIG,ORIG@T) =", round(med(O1,O1@Rr.T+t),3))
F1,_n,_c = __import__("p201_lib", globals(), locals(), ["read_pcd"], 0).__dict__["read_pcd"](".scratch/pota204_repro/FRESH_C01_Bl0.pcd") if False else (None,None,None)
from p201_lib import read_pcd
sys.path.insert(0, ".scratch/pota201_repro")
Fr,_,_ = read_pcd(".scratch/pota204_repro/FRESH_C01_Bl0.pcd")
print("fresh mean", Fr.mean(0).round(1), "med(walk,fresh) =", round(med(W,Fr),3))
