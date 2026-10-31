import numpy as np
for pc in ["01","02","03","04"]:
    T = np.loadtxt(".scratch/pota176_repro/inputs/Pot_C_Piece_%d_T.txt" % int(pc))
    Rr, t = T[:3,:3], T[:3,3]
    print("C"+pc+" R=", np.round(Rr,3).tolist())
    print("C"+pc+" t=", np.round(t,1).tolist(), "det=", round(float(np.linalg.det(Rr)),4))
