import numpy as np
F = "C:/PR/structure-from-sherds-pp/artifacts/pota208_e2e/pota208_fetch/T_L_fresh"
G = "C:/PR/structure-from-sherds-pp/artifacts/pota_restore_e2e/pota_restore_fetch/GT"
att = [np.loadtxt("%s/T_%dto_%d.txt" % (F, i, i)).reshape(4, 4) for i in range(8)]
gt = [np.loadtxt("%s/Pot_A_Piece_%d_T.txt" % (G, n)).reshape(4, 4) for n in range(1, 9)]

def kabsch(A, B):
    cA, cB = A.mean(0), B.mean(0)
    H = (A - cA).T @ (B - cB)
    U, _, Vt = np.linalg.svd(H)
    R = Vt.T @ U.T
    if np.linalg.det(R) < 0:
        Vt[-1, :] *= -1
        R = Vt.T @ U.T
    return R, cB - R @ cA

def rd(R):
    return float(np.degrees(np.arccos(np.clip((np.trace(R) - 1) / 2, -1, 1))))

keep = [i for i in range(8) if i != 0]
tA = np.array([att[i][:3, 3] for i in keep])
tG = np.array([gt[i][:3, 3] for i in keep])
RA, tA2 = kabsch(tA, tG)
print("Kabsch on pieces 2-8 (exclude p1 outlier):")
n = 0
for i in range(8):
    Re = gt[i][:3, :3].T @ RA @ att[i][:3, :3]
    te = gt[i][:3, 3] - (RA @ att[i][:3, 3] + tA2)
    r, t = rd(Re), float(np.linalg.norm(te))
    ok = r <= 5.0 and t <= 10.0
    n += ok
    print("%d | %.2f | %.2f | %s" % (i + 1, r, t, "PASS" if ok else "FAIL"))
print("STRICT: %d/8" % n)
