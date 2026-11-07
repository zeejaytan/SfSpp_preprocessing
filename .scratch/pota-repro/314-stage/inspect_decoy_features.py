import os
import numpy as np

CORPUS = "/data/gpfs/projects/punim2657/sfs_main/original_samples/SfS_pp"

wall_pieces = ["Pot_E_Piece_03", "Pot_E_Piece_23", "Pot_E_Piece_24", "Pot_E_Piece_25", "Pot_E_Piece_26", "Pot_E_Piece_28"]

for stem in wall_pieces:
    s0 = np.loadtxt(f"{CORPUS}/Surfaces/{stem}_Surface_0.xyz", usecols=range(6)).T
    s1 = np.loadtxt(f"{CORPUS}/Surfaces/{stem}_Surface_1.xyz", usecols=range(6)).T
    C = np.concatenate([s0, s1], axis=1)
    
    C_cent = np.mean(C[:3, :], axis=1)
    N_mean = np.mean(C[3:6, :], axis=1)
    N_mean /= np.linalg.norm(N_mean)
    vt_decoy = np.r_[N_mean, C_cent]
    
    a = vt_decoy[:3]
    p0 = vt_decoy[3:6]
    P = C[:3, :]
    N = C[3:6, :]
    
    dp = P - p0[:, None]
    z = a @ dp
    r_vec = dp - a[:, None] * z[None, :]
    r = np.linalg.norm(r_vec, axis=0)
    
    near = r < 25.0
    mean_ax_whole = np.mean(np.abs(a @ N))
    mean_ax_near = np.mean(np.abs(a @ N[:, near]))
    
    print(f"{stem:18s} | near_pts={np.sum(near):4d} | whole_ax={mean_ax_whole:.2f} | near_ax={mean_ax_near:.2f}")
