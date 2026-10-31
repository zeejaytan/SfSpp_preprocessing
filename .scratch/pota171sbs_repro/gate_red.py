import numpy as np
from scipy.spatial import cKDTree
A = np.loadtxt('.scratch/pota171sbs_repro/P02_ORIG.xyz')[:, :3]
R = np.loadtxt('artifacts/pota171/Pot_A_Piece_02_Breakline_0_noveto.xyz')[:, :3]
B = np.loadtxt('artifacts/pota171/Pot_A_Piece_02_Breakline_0_cure.xyz')[:, :3]
print('ref', A.shape, 'bbox', A.min(0).round(1), A.max(0).round(1))

def cov(X, Y, t=2.0):
    d, _ = cKDTree(Y).query(X)
    return round(float((d < t).mean()), 3), round(float(np.median(d)), 2)

print('red-vs-ref cov/med:', cov(R, A))
print('ref-vs-red cov/med:', cov(A, R))
print('blue-vs-ref cov/med:', cov(B, A))
