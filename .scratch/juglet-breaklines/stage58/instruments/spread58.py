#!/usr/bin/env python3
"""Ticket 58: viewpoint-independent spread of each arm's posed assembly, so the
renders can be read against a number. Reports, per arm: the bounding-box diagonal
of the posed estimate vertices, the same for the GT-posed reference, the largest
pairwise centroid distance inside each, and the estimate/reference centroid offset.
"""
import json, os, sys
import numpy as np

def read_T(p): return np.loadtxt(p)
def pose(T, P): return (T[:3, :3] @ P.T).T + T[:3, 3]
def read_obj(p, cap=3000):
    pts = []
    for line in open(p, "r", errors="ignore"):
        if line.startswith("v "):
            f = line.split(); pts.append((float(f[1]), float(f[2]), float(f[3])))
    P = np.asarray(pts, float)
    if len(P) > cap:
        P = P[::int(np.ceil(len(P) / cap))]
    return P

def centroid_pair_max(C):
    if len(C) < 2: return 0.0
    d = np.linalg.norm(C[:, None, :] - C[None, :, :], axis=2)
    return float(d.max())

def run(arm, resdir, scoredir, meshdir, meshfmt, gtdir, gtfmt, ng):
    sc = json.load(open(os.path.join(scoredir, arm + ".json"))) if os.path.exists(os.path.join(scoredir, arm + ".json")) else None
    G = np.eye(4)
    if sc and sc.get("gauge", {}).get("pieces_used"):
        G[:3, :3] = np.asarray(sc["gauge"]["R"]); G[:3, 3] = np.asarray(sc["gauge"]["t"])
    T = {}
    for f in os.listdir(resdir):
        if f.startswith("T_") and f.endswith(".txt"):
            T[int(f.split("_")[1][:-2])] = read_T(os.path.join(resdir, f))
    if not T:
        return {"arm": arm, "pieces": 0, "note": "no T files"}
    Est, Ref, CE, CR = [], [], [], []
    for i in sorted(T):
        P = read_obj(os.path.join(meshdir, meshfmt % (i + 1)))
        E = pose(G @ T[i], P); R = pose(read_T(os.path.join(gtdir, gtfmt % (i + 1))), P)
        Est.append(E); Ref.append(R); CE.append(E.mean(axis=0)); CR.append(R.mean(axis=0))
    Est = np.vstack(Est); Ref = np.vstack(Ref)
    CE = np.array(CE); CR = np.array(CR)
    return {"arm": arm, "pieces": len(T),
            "est_bbox_diag_mm": round(float(np.linalg.norm(Est.max(0) - Est.min(0))), 1),
            "ref_bbox_diag_mm": round(float(np.linalg.norm(Ref.max(0) - Ref.min(0))), 1),
            "est_centroid_max_mm": round(centroid_pair_max(CE), 1),
            "ref_centroid_max_mm": round(centroid_pair_max(CR), 1),
            "centroid_offset_mm": round(float(np.linalg.norm(CE.mean(0) - CR.mean(0))), 1)}

run_dir = sys.argv[1]
out = "C:/PR/SfSpp_preprocessing/artifacts/t58/run_t58"
mesh = run_dir + "/mesh"
gt = "C:/PR/SfSpp_preprocessing/artifacts/t58/prior/B"
rows = []
for arm in ["F50", "F45", "F10", "F0", "F10R", "I60"]:
    rows.append(run(arm, run_dir + "/harvest/out/" + arm, run_dir + "/harvest/score",
                    mesh, "Juglet_Piece_%d_Mesh.obj", gt, "Juglet_Piece_%d_T.txt", 9))
rows.append(run("PA10", run_dir + "/harvest/out/PA10", out + "/pota",
                out + "/pota/mesh", "Pot_A_Piece_%d_Mesh.obj", out + "/pota/gt",
                "Pot_A_Piece_%d_T.txt", 8))
print(json.dumps(rows, indent=1))
open(out + "/spread.json", "w").write(json.dumps(rows, indent=1) + "\n")
