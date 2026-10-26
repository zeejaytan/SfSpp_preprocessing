#!/usr/bin/env python
"""Ticket 300: rebuild the two Pot C reassemblies from stored transforms and measure them.

Read-only: reads the four corpus DS meshes, the two arms' T_ito_i.txt, the corpus GT
transforms/graph, and both Bl0/Bl1 sets; writes geometry into artifacts/pota300/ and a
machine-readable numbers file beside it.  No algorithm is re-run.
"""
import json, sys
from pathlib import Path
import numpy as np
from scipy.spatial import cKDTree

ROOT = Path(r"C:/PR/SfSpp_preprocessing/artifacts/pota300")
IN = ROOT / "inputs" / "stage"
CORPUS = IN / "corpus"
OUT = ROOT / "geom"
OUT.mkdir(parents=True, exist_ok=True)
SLOTS = [1, 2, 3, 4]          # slot i  <->  Pot_C_Piece_{i+1:02d}


def load_obj(path):
    vs, fs = [], []
    with open(path, "r", errors="ignore") as fh:
        for line in fh:
            if line.startswith("v "):
                vs.append([float(x) for x in line.split()[1:4]])
            elif line.startswith("f "):
                idx = [int(tok.split("/")[0]) for tok in line.split()[1:]]
                for k in range(1, len(idx) - 1):
                    fs.append([idx[0], idx[k], idx[k + 1]])
    return np.asarray(vs, float), np.asarray(fs, np.int64) - 1


def load_T(path):
    return np.loadtxt(path)


def apply_T(V, T):
    return V @ T[:3, :3].T + T[:3, 3]


def apply_T_inv(V, T):
    """the other reading of the same numbers: p = R^T (v - t), i.e. world->local used as local->world"""
    return (V - T[:3, 3]) @ T[:3, :3]


def rot_deg(R):
    c = (np.trace(R) - 1.0) / 2.0
    return float(np.degrees(np.arccos(np.clip(c, -1.0, 1.0))))


def log_rot_deg(Rmat):
    """same rodrigues-style angle the assembler uses (R.log() -> vector norm), in degrees"""
    from scipy.spatial.transform import Rotation as Rot
    return float(np.degrees(np.linalg.norm(Rot.from_matrix(Rmat).as_rotvec())))


def edge_metrics(Vi, Vj):
    d, _ = cKDTree(Vj).query(Vi, k=1)
    return {
        "min_mm": float(d.min()),
        "p001_mm": float(np.quantile(d, 0.001)),
        "p01_mm": float(np.quantile(d, 0.01)),
        "p1_mm": float(np.quantile(d, 0.01)),
        "median_mm": float(np.median(d)),
        "frac_i_within_2mm": float((d < 2.0).mean()),
        "n_i_verts": int(len(Vi)),
    }


def kabsch_rigid(A, B):
    """rigid G minimising |G a - b| over paired rows of A, B"""
    ca, cb = A.mean(0), B.mean(0)
    H = (A - ca).T @ (B - cb)
    U, S, Vt = np.linalg.svd(H)
    D = np.eye(3)
    if np.linalg.det(Vt.T @ U.T) < 0:
        D[2, 2] = -1.0
    R = Vt.T @ D @ U.T
    t = cb - R @ ca
    T = np.eye(4)
    T[:3, :3] = R
    T[:3, 3] = t
    return T


# ---------------------------------------------------------------- inputs
pieces = {}
for s in SLOTS:
    V, F = load_obj(CORPUS / "Mesh" / f"Pot_C_Piece_{s:02d}_Mesh_DS.obj")
    pieces[s] = (V, F)

graph = np.loadtxt(CORPUS / "GroundTruth" / "Pot_C_simple_graph.txt")
GT = {s: load_T(CORPUS / "GroundTruth" / f"Pot_C_Piece_{s}_T.txt") for s in SLOTS}
ARMS = {a: {s: load_T(IN / "run" / a / f"T_{s-1}to_{s-1}.txt") for s in SLOTS}
        for a in ("authb", "oursd")}

edges = [(i, j) for i in SLOTS for j in SLOTS if i < j and graph[i - 1, j - 1] > 0]
nonedges = [(i, j) for i in SLOTS for j in SLOTS if i < j and graph[i - 1, j - 1] == 0]

rep = {
    "pieces": {f"C{s:02d}": {"n_verts": int(pieces[s][0].shape[0]), "n_faces": int(pieces[s][1].shape[0])}
               for s in SLOTS},
    "gt_edges": [f"C{i:02d}-C{j:02d}" for i, j in edges],
    "gt_non_edges": [f"C{i:02d}-C{j:02d}" for i, j in nonedges],
}

# mesh resolution floor (median edge length of the triangulation)
res = {}
for s in SLOTS:
    V, F = pieces[s]
    e = np.concatenate([V[F[:, 0]] - V[F[:, 1]], V[F[:, 1]] - V[F[:, 2]], V[F[:, 2]] - V[F[:, 0]]])
    res[f"C{s:02d}"] = float(np.median(np.linalg.norm(e, axis=1)))
rep["median_edge_length_mm"] = res

# ------------------------------------------------- 1. convention, proved on GT
conv = {}
for name, fn in (("local_to_world", apply_T), ("inverted", apply_T_inv)):
    W = {s: fn(pieces[s][0], GT[s]) for s in SLOTS}
    conv[name] = {
        "edges": {f"C{i:02d}-C{j:02d}": edge_metrics(W[i], W[j])["min_mm"] for i, j in edges},
        "non_edges": {f"C{i:02d}-C{j:02d}": edge_metrics(W[i], W[j])["min_mm"] for i, j in nonedges},
    }
    conv[name]["median_edge_min_mm"] = float(np.median(list(conv[name]["edges"].values())))
rep["convention_test_on_GT"] = conv
CONV = apply_T if conv["local_to_world"]["median_edge_min_mm"] < conv["inverted"]["median_edge_min_mm"] else apply_T_inv
rep["convention_used"] = "local_to_world" if CONV is apply_T else "inverted"

# ------------------------------------------------- 2. seated geometry + seams
seams = {}
seat = {"GT": {s: CONV(pieces[s][0], GT[s]) for s in SLOTS}}
for a in ARMS:
    seat[a] = {s: CONV(pieces[s][0], ARMS[a][s]) for s in SLOTS}

for name in ("GT", "authb", "oursd"):
    W = seat[name]
    seams[name] = {
        "edges": {f"C{i:02d}-C{j:02d}": edge_metrics(W[i], W[j]) for i, j in edges},
        "non_edges": {f"C{i:02d}-C{j:02d}": edge_metrics(W[i], W[j]) for i, j in nonedges},
    }
rep["seams"] = seams

# ------------------------------------------------- 3. pose error vs GT
pose = {}
for a in ARMS:
    per_edge = {}
    for i, j in edges:
        Trel = np.linalg.inv(ARMS[a][i]) @ ARMS[a][j]
        Grel = np.linalg.inv(GT[i]) @ GT[j]
        E = Trel @ np.linalg.inv(Grel)          # identical to isSimilarTrans(GT_T, T)
        per_edge[f"C{i:02d}-C{j:02d}"] = {
            "rot_deg": log_rot_deg(E[:3, :3]),
            "trans_mm": float(np.linalg.norm(E[:3, 3])),
            "passes_assembler_0p35rad_50mm": bool(log_rot_deg(E[:3, :3]) < np.degrees(0.35)
                                                  and np.linalg.norm(E[:3, 3]) < 50.0),
        }
    # one global rigid alignment of the whole hand into the GT frame (removes frame choice only)
    A = np.vstack([seat[a][s] for s in SLOTS])
    B = np.vstack([seat["GT"][s] for s in SLOTS])
    G = kabsch_rigid(A, B)
    RA = apply_T(A, G)
    RB = B
    off = 0
    per_piece = {}
    for s in SLOTS:
        n = seat[a][s].shape[0]
        Va, Vg = RA[off:off + n], RB[off:off + n]
        off += n
        Ra = ARMS[a][s][:3, :3]
        Rg = GT[s][:3, :3]
        per_piece[f"C{s:02d}"] = {
            "rot_deg_frame_free": log_rot_deg(Ra @ Rg.T),
            "centroid_shift_raw_mm": float(np.linalg.norm(seat[a][s].mean(0) - seat["GT"][s].mean(0))),
            "centroid_shift_after_global_align_mm": float(np.linalg.norm(Va.mean(0) - Vg.mean(0))),
            "rms_point_shift_after_global_align_mm": float(np.sqrt(((Va - Vg) ** 2).sum(1).mean())),
        }
    pose[a] = {
        "global_align_rot_deg": log_rot_deg(G[:3, :3]),
        "global_align_trans_mm": float(np.linalg.norm(G[:3, 3])),
        "rms_after_global_align_mm": float(np.sqrt(((RA - RB) ** 2).sum(1).mean())),
        "per_edge_vs_GT": per_edge,
        "per_piece_vs_GT": per_piece,
    }
rep["pose_vs_GT"] = pose

# ------------------------------------------------- 4. the two arms against each other
arm_diff = {}
for s in SLOTS:
    Trel = np.linalg.inv(ARMS["oursd"][SLOTS[0]]) @ ARMS["oursd"][s]
    Trel2 = np.linalg.inv(ARMS["authb"][SLOTS[0]]) @ ARMS["authb"][s]
    E = Trel @ np.linalg.inv(Trel2)
    arm_diff[f"C{s:02d}"] = {
        "rot_deg": log_rot_deg(E[:3, :3]),
        "trans_mm_of_relative_pose": float(np.linalg.norm(E[:3, 3])),
        "centroid_mm_between_arms_raw": float(np.linalg.norm(seat["authb"][s].mean(0) - seat["oursd"][s].mean(0))),
    }
G2 = kabsch_rigid(np.vstack([seat["oursd"][s] for s in SLOTS]), np.vstack([seat["authb"][s] for s in SLOTS]))
rep["ours_vs_authb"] = {"global_align_rot_deg": log_rot_deg(G2[:3, :3]),
                        "global_align_trans_mm": float(np.linalg.norm(G2[:3, 3])),
                        "per_piece": arm_diff}

# ------------------------------------------------- 5. C01 holes (the scan gap)
def boundary_loops(V, F):
    from collections import defaultdict
    cnt = defaultdict(int)
    for tri in F:
        for a, b in ((tri[0], tri[1]), (tri[1], tri[2]), (tri[2], tri[0])):
            cnt[(min(a, b), max(a, b))] += 1
    bedges = [e for e, c in cnt.items() if c == 1]
    adj = defaultdict(list)
    for a, b in bedges:
        adj[a].append(b)
        adj[b].append(a)
    seen = set()
    loops = []
    for a, b in bedges:
        if (a, b) in seen:
            continue
        loop = [a]
        seen.add((a, b))
        cur, prev = b, a
        while cur != a:
            loop.append(cur)
            nxt = [x for x in adj[cur] if x != prev]
            if not nxt:
                break
            prev, cur = cur, nxt[0]
        loops.append(loop)
    out = []
    for lp in loops:
        P = V[np.asarray(lp)]
        per = float(np.linalg.norm(np.diff(np.vstack([P, P[:1]]), axis=0), axis=1).sum())
        out.append({"n_verts": len(lp), "perimeter_mm": per, "centroid": P.mean(0).tolist(),
                    "bbox_mm": (P.max(0) - P.min(0)).tolist(), "idx": lp})
    return sorted(out, key=lambda r: -r["perimeter_mm"])

holes = {}
for s in SLOTS:
    V, F = pieces[s]
    lp = boundary_loops(V, F)
    holes[f"C{s:02d}"] = {
        "n_boundary_loops": len(lp),
        "n_loops_over_5mm": int(sum(1 for r in lp if r["perimeter_mm"] > 5.0)),
        "loops_perimeter_gt_3mm": [{"n_verts": r["n_verts"], "perimeter_mm": round(r["perimeter_mm"], 3),
                                    "centroid": [round(c, 2) for c in r["centroid"]],
                                    "bbox_mm": [round(c, 2) for c in r["bbox_mm"]]} for r in lp if r["perimeter_mm"] > 3.0][:12],
    }
rep["mesh_holes"] = holes

(OUT / "measure.json").write_text(json.dumps(rep, indent=1))
print(json.dumps({k: rep[k] for k in ("pieces", "median_edge_length_mm", "convention_used")}, indent=1))
print("convention test:", json.dumps(rep["convention_test_on_GT"], indent=1))
print("--- seams min_mm ---")
for name in ("GT", "authb", "oursd"):
    print(name, {k: round(v["min_mm"], 3) for k, v in seams[name]["edges"].items()},
          "non:", {k: round(v["min_mm"], 3) for k, v in seams[name]["non_edges"].items()})
print("--- pose ---")
print(json.dumps(pose, indent=1))
print("--- ours vs authb ---")
print(json.dumps(rep["ours_vs_authb"], indent=1))
print("--- holes ---")
print(json.dumps(holes, indent=1))
