#!/usr/bin/env python3
"""Ticket 58: score the Pot A regression-control arm (PA10) with the same
binary-faithful CountResult replay and seat measures score58.py uses, but with
the Pot A bundle names (Piece_01..08 meshes, Piece_1..8 GT T files).

Usage: score_pota58.py --result DIR --gt DIR --mesh DIR [--out FILE] [--label NAME]
"""
import argparse, json, os
import numpy as np
from scipy.spatial import cKDTree

RAD = 0.35
TT = 50.0
STRICT_DEG = 5.0
STRICT_MM = 10.0
POT_SIZE_MM = 0.0  # set from the mesh extent below


def read_T(path):
    return np.loadtxt(path)


def read_graph(path):
    return np.loadtxt(path, dtype=int)


def rot_angle_deg(R):
    v = (np.trace(R) - 1.0) / 2.0
    return float(np.degrees(np.arccos(np.clip(v, -1.0, 1.0))))


def similar(GT_rel, E_rel, rad=RAD, tt=TT):
    D = GT_rel @ np.linalg.inv(E_rel)
    ang = rot_angle_deg(D[:3, :3])
    dt = float(np.linalg.norm(D[:3, 3]))
    return ang, dt, (ang < np.degrees(rad) and dt < tt)


def kabsch(P, Q):
    C = P.T @ Q
    V, S, Wt = np.linalg.svd(C)
    d = np.sign(np.linalg.det(V @ Wt))
    D = np.diag([1.0, 1.0, d])
    R = V @ D @ Wt
    t = Q.mean(axis=0) - R @ P.mean(axis=0)
    return R, t


def apply_G(G, M):
    return np.vstack([np.hstack([G[:3, :3], G[:3, 3][:, None]]), [0, 0, 0, 1]]) @ M


def read_obj_verts(path, cap=6000):
    pts = []
    with open(path, "r", errors="ignore") as fh:
        for line in fh:
            if line.startswith("v "):
                f = line.split()
                pts.append((float(f[1]), float(f[2]), float(f[3])))
    P = np.asarray(pts, dtype=float)
    if len(P) > cap:
        k = int(np.ceil(len(P) / cap))
        P = P[::k]
    return P


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--result", required=True)
    ap.add_argument("--gt", required=True)
    ap.add_argument("--mesh", required=True)
    ap.add_argument("--out")
    ap.add_argument("--label", default="PA10")
    a = ap.parse_args()

    ng = 8
    graph = read_graph(os.path.join(a.gt, "Pot_A_simple_graph.txt"))
    GT = {i: read_T(os.path.join(a.gt, "Pot_A_Piece_%d_T.txt" % (i + 1)))
          for i in range(ng)}
    res = {}
    for f in sorted(os.listdir(a.result)):
        if f.startswith("T_") and f.endswith(".txt"):
            i = int(f.split("_")[1][:-2])
            res[i] = read_T(os.path.join(a.result, f))

    out = {"label": a.label, "pieces_with_T": sorted(i + 1 for i in res),
           "graph_directed_total": int(graph.sum())}

    # ---- metric A: binary-faithful CountResult ------------------------------
    k = 0
    total = 0
    right = set()
    for i in range(ng):
        for j in range(ng):
            if not graph[i, j]:
                continue
            total += 1
            if i not in res or j not in res:
                continue
            GT_rel = np.linalg.inv(GT[i]) @ GT[j]
            E_rel = np.linalg.inv(res[i]) @ res[j]
            ang, dt, ok = similar(GT_rel, E_rel)
            if ok:
                k += 1
                right.add(i + 1)
                right.add(j + 1)
    out["countresult"] = {"k_directed_pass": k, "total_directed": total,
                          "k_sherd": len(right), "right_sherd": sorted(right),
                          "edge_print_pair": [k // 2, total // 2],
                          "pct": (100.0 * k / total) if total else 0.0}

    # ---- metric B: per-piece error + translation gauge ----------------------
    have = sorted(res)
    P = np.array([res[i][:3, 3] for i in have])
    Q = np.array([GT[i][:3, 3] for i in have])
    if len(have) >= 3:
        R, t = kabsch(P, Q)
        G = np.eye(4); G[:3, :3] = R; G[:3, 3] = t
        used = [i + 1 for i in have]
    else:
        G = np.eye(4); used = []
    out["gauge"] = {"pieces_used": used,
                    "R": G[:3, :3].tolist(), "t": G[:3, 3].tolist()}
    pp = []
    for i in have:
        dR = res[i][:3, :3] @ GT[i][:3, :3].T
        raw_deg = rot_angle_deg(dR)
        raw_mm = float(np.linalg.norm(res[i][:3, 3] - GT[i][:3, 3]))
        E = apply_G(G, res[i])
        g_deg = rot_angle_deg(E[:3, :3] @ GT[i][:3, :3].T)
        g_mm = float(np.linalg.norm(E[:3, 3] - GT[i][:3, 3]))
        pp.append({"piece": i + 1, "raw_deg": round(raw_deg, 3),
                   "raw_mm": round(raw_mm, 3), "gauge_deg": round(g_deg, 3),
                   "gauge_mm": round(g_mm, 3),
                   "strict_raw": bool(raw_deg < STRICT_DEG and raw_mm < STRICT_MM),
                   "strict_gauge": bool(g_deg < STRICT_DEG and g_mm < STRICT_MM)})
    out["tables"] = {"per_piece": pp}

    # ---- metric C: own-place chamfer (Pot A size from the reference extent) --
    verts = {}
    for i in have:
        p = os.path.join(a.mesh, "Pot_A_Piece_%d_Mesh.obj" % (i + 1))
        verts[i] = read_obj_verts(p)
    ref = np.vstack([(GT[i][:3, :3] @ verts[i].T).T + GT[i][:3, 3] for i in have])
    size = float(np.max(vert_span(ref)))
    bar = 0.0707 * size
    seat = []
    for i in have:
        E = (apply_G(G, res[i])[:3, :3] @ verts[i].T).T + apply_G(G, res[i])[:3, 3]
        H = (GT[i][:3, :3] @ verts[i].T).T + GT[i][:3, 3]
        te = cKDTree(E); th = cKDTree(H)
        de, _ = th.query(E); dh, _ = te.query(H)
        cham = 0.5 * (de.mean() + dh.mean())
        seat.append({"piece": i + 1, "verts": int(len(verts[i])),
                     "chamfer_mm": round(float(cham), 3),
                     "median_est2home_mm": round(float(np.median(de)), 3),
                     "median_home2est_mm": round(float(np.median(dh)), 3),
                     "own_place": bool(cham < bar),
                     "right_way_round": bool(cham < bar and np.median(de) < bar
                                              and np.median(dh) < bar)})
    out["tables"]["seating"] = seat
    out["seated_count"] = sum(1 for r in seat if r["own_place"])
    out["right_way_count"] = sum(1 for r in seat if r["right_way_round"])
    out["pot_size_mm"] = round(size, 3)
    out["seat_bar_mm"] = round(bar, 3)

    txt = json.dumps(out, indent=1)
    print(txt)
    if a.out:
        with open(a.out, "w") as fh:
            fh.write(txt + "\n")


def vert_span(P):
    return P.max(axis=0) - P.min(axis=0)


if __name__ == "__main__":
    main()
