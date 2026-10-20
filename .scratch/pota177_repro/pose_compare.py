
import numpy as np

def loadT(p):
    M = np.loadtxt(p)
    return M

def rot_angle_deg(R1, R2):
    # angle of R1^T R2
    dR = R1.T @ R2
    c = np.clip((np.trace(dR)-1)/2, -1, 1)
    return np.degrees(np.arccos(c))

def show(name, p):
    M = loadT(p)
    print(f"{name}: R=row0 {M[0,:3].round(4)} t=({M[0,3]:.2f},{M[1,3]:.2f},{M[2,3]:.2f})")

base145 = "fetch145/pota145_fetch"
inp177 = "C:/PR/SfSpp_preprocessing/.scratch/pota177_repro/inputs"
print("=== 176 C_176 vs 145 C_FIN: identical search output? ===")
print("--- direct ---")
pairs = [
  ("145C_FIN T_1to_1", f"{base145}/T_C_FIN/T_1to_1.txt", f"{inp177}/pota176_run_33449864_C_176_T_1to_1.txt"),
  ("145C_FIN T_3to_3", f"{base145}/T_C_FIN/T_3to_3.txt", f"{inp177}/pota176_run_33449864_C_176_T_3to_3.txt"),
]
for label, pa, pb in pairs:
    A = np.loadtxt(pa); B = np.loadtxt(pb)
    print(f"{label}: rot-diff={rot_angle_deg(A[:3,:3],B[:3,:3]):.4f}deg trans-diff={np.linalg.norm(A[:3,3]-B[:3,3]):.4f} maxabs={np.abs(A-B).max():.5f}")
print("=== GT edge 02-04 (frame-invariant rel-edge, 145 identity method) ===")
G = [np.loadtxt(f"{base145}/GT_C/Pot_C_Piece_{n}_T.txt") for n in [1,2,3,4]]
print("GT piece frames t:")
for n, M in enumerate(G, 1):
    print(f"  piece{n} t=({M[0,3]:.1f},{M[1,3]:.1f},{M[2,3]:.1f})")
print("=== chosen vs GT per seated slot (145 C_FIN) ===")
# slots: T_1to_1, T_3to_3 present; GT pieces 1..4. Try mapping slot->piece by nearest translation.
for f in ["T_1to_1.txt", "T_3to_3.txt"]:
    E = np.loadtxt(f"{base145}/T_C_FIN/{f}")
    dists = [(n+1, float(np.linalg.norm(E[:3,3]-M[:3,3])), rot_angle_deg(E[:3,:3], M[:3,:3])) for n, M in enumerate(G)]
    dists.sort(key=lambda x: x[1])
    print(f"C_FIN {f}: nearest GT " + ", ".join(f"piece{n}(dt={d:.1f},dR={a:.1f}deg)" for n, d, a in dists))
print("=== chosen vs GT per seated slot (176 C_orig, all 4) ===")
for f in ["T_0to_0.txt", "T_1to_1.txt", "T_2to_2.txt", "T_3to_3.txt"]:
    E = np.loadtxt(f"{base145}/T_C_orig/{f}")
    dists = [(n+1, float(np.linalg.norm(E[:3,3]-M[:3,3])), rot_angle_deg(E[:3,:3], M[:3,:3])) for n, M in enumerate(G)]
    dists.sort(key=lambda x: x[1])
    print(f"C_orig {f}: nearest GT " + ", ".join(f"piece{n}(dt={d:.1f},dR={a:.1f}deg)" for n, d, a in dists[:2]))

print("=== frame-invariant rel-edge T_1 vs T_3 (145 method) ===")
def reledge(pa, pb):
    A = np.loadtxt(pa); B = np.loadtxt(pb)
    R = A[:3,:3].T @ B[:3,:3]
    ang = np.degrees(np.arccos(np.clip((np.trace(R)-1)/2,-1,1)))
    d = float(np.linalg.norm(A[:3,3]-B[:3,3]))
    return ang, d
for label, pa, pb in [
  ("145 C_FIN", f"{base145}/T_C_FIN/T_1to_1.txt", f"{base145}/T_C_FIN/T_3to_3.txt"),
  ("176 C_176", "inputs/pota176_run_33449864_C_176_T_1to_1.txt", "inputs/pota176_run_33449864_C_176_T_3to_3.txt"),
  ("176 C_orig(T1vT3)", f"{base145}/T_C_orig/T_1to_1.txt", f"{base145}/T_C_orig/T_3to_3.txt"),
]:
    print(label, "rel-edge angle=%.2f offset=%.2f" % reledge(pa, pb))
G2 = np.loadtxt(f"{base145}/GT_C/Pot_C_Piece_2_T.txt"); G4 = np.loadtxt(f"{base145}/GT_C/Pot_C_Piece_4_T.txt")
R = G2[:3,:3].T @ G4[:3,:3]
print("GT 02-04 rel-edge angle=%.2f offset=%.2f" % (np.degrees(np.arccos(np.clip((np.trace(R)-1)/2,-1,1))), float(np.linalg.norm(G2[:3,3]-G4[:3,3]))))
print("=== 176 installed rim character (p176_C01_TRUE_walk.npy) ===")
W = np.load(open('/dev/null','rb')) if False else None
