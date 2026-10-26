import numpy as np
from pathlib import Path
STAGE = Path(r"C:/PR/SfSpp_preprocessing/artifacts/pota300/inputs/stage")
a = np.loadtxt(STAGE / "axes" / "Pot_C_Piece_01_Axis.xyz").ravel()
o, d = a[:3], a[3:6] / np.linalg.norm(a[3:6])
T = np.loadtxt(STAGE / "corpus" / "GroundTruth" / "Pot_C_Piece_1_T.txt")
if T.shape == (3, 4):
    T = np.vstack([T, [0, 0, 0, 1]])
print("piece 01 axis in the GT vessel frame: origin", np.round(T[:3,:3] @ o + T[:3,3], 1),
      " direction", np.round(T[:3,:3] @ d, 3))
