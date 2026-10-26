
import os, glob, json, itertools
import numpy as np

ROOT = r"C:\PR\worktrees\sfs\299\.scratch\pota-repro\299-work\t299"
GTD  = os.path.join(ROOT, "GT")
RD   = os.path.join(ROOT, "R")

ARMS = {
 "D": [("authb","20261026-0126_d1f1a4c_p298-Pot_D-authb"),
       ("oursd","20261026-0126_d1f1a4c_p298-Pot_D-oursd"),
       ("authb-rep2","20261026-0301_d1f1a4c_p298-Pot_D-authb-rep2")],
 "H": [("authb","20261026-0126_d1f1a4c_p298-Pot_H-authb"),
       ("oursd","20261026-0126_d1f1a4c_p298-Pot_H-oursd"),
       ("authb-rep2","20261026-0301_d1f1a4c_p298-Pot_H-authb-rep2")],
}
N = {"D":29, "H":11}

def read_T(path):
    M = np.eye(4)
    rows = [l.split() for l in open(path) if l.strip()]
    n = len(rows) - 1            # Trans::Read reads num-1 rows (data_structure.cpp:648)
    for i in range(n):
        M[i, :] = [float(x) for x in rows[i][:4]]
    return M

def rotvec_angle(R):
    c = (np.trace(R) - 1.0) / 2.0
    return float(np.degrees(np.arccos(np.clip(c, -1.0, 1.0))))

RAD = 0.35      # data_structure.cpp:927 rad_threshold
TTH = 50.0      # data_structure.cpp:927 t_threshold

def edge_err(Ta, Tb, GTa, GTb):
    """isSimilarTrans(GT_T, T) exactly as data_structure.cpp:951-959 + 661-680."""
    GT_T = np.linalg.inv(GTa) @ GTb
    T    = np.linalg.inv(Ta)  @ Tb
    Trel = GT_T @ np.linalg.inv(T)
    deg  = rotvec_angle(Trel[:3, :3])
    mm   = float(np.linalg.norm(Trel[:3, 3]))
    return (np.radians(deg) < RAD and mm < TTH), deg, mm

def gt_path(pot, n):
    return os.path.join(GTD, "Pot_%s_Piece_%d_T.txt" % (pot, n))

def load_graph(pot, n):
    p = os.path.join(GTD, "Pot_%s_simple_graph.txt" % pot)
    rows = [[int(x) for x in l.split()] for l in open(p) if l.strip()]
    return np.array(rows, dtype=int)

def analyse(pot, arm, runid):
    n = N[pot]
    G = load_graph(pot, n).copy()
    on = np.zeros(n, dtype=bool)
    res = [np.eye(4)] * n
    for i in range(n):
        p = os.path.join(RD, runid, "T_%dto_%d.txt" % (i, i))
        if os.path.exists(p):
            on[i] = True
            res[i] = read_T(p)
    gt = [np.eye(4)] * n
    gt_present = np.zeros(n, dtype=bool)
    for i in range(n):
        p = gt_path(pot, i + 1)
        if os.path.exists(p):
            gt[i] = read_T(p); gt_present[i] = True
    for i in range(n):
        if not on[i]:
            G[i, :] = 0; G[:, i] = 0
    n_on = int(on.sum())
    tot = int(G.sum())
    k = 0
    correct = np.zeros((n, n), dtype=bool)
    for i in range(n):
        for j in range(n):
            if not G[i, j]:
                continue
            ok, deg, mm = edge_err(res[i], res[j], gt[i], gt[j])
            if ok:
                k += 1; correct[i, j] = True
    seated = [bool(on[i] and (correct[i, :].sum() > 0)) for i in range(n)]
    # per piece diagnostics
    rows = []
    for i in range(n):
        nbrs = [j for j in range(n) if G[i, j]]
        best = None
        for j in nbrs:
            ok, deg, mm = edge_err(res[i], res[j], gt[i], gt[j])
            if best is None or (deg / 20.05 + mm / 50.0) < (best[1] / 20.05 + best[2] / 50.0):
                best = (j, deg, mm, ok)
        absT = np.linalg.inv(gt[i]) @ res[i]
        rows.append(dict(idx=i, piece=i + 1, on=bool(on[i]), gt_present=bool(gt_present[i]),
                         nbrs=len(nbrs), seated=seated[i],
                         best_j=(best[0] + 1) if best else None,
                         best_deg=round(best[1], 2) if best else None,
                         best_mm=round(best[2], 2) if best else None,
                         abs_deg=round(rotvec_angle(absT[:3, :3]), 2),
                         abs_mm=round(float(np.linalg.norm(absT[:3, 3])), 2),
                         deg_correct=int(sum(1 for j in nbrs if correct[i, j])),
                         deg_total=len(nbrs)))
    return dict(pot=pot, arm=arm, runid=runid, n=n, n_on=n_on, k_sherd=int(sum(seated)),
                t_sherd=n_on, k_edge=k // 2, t_edge=tot // 2, rows=rows,
                off=[i + 1 for i in range(n) if not on[i]],
                gt_missing=[i + 1 for i in range(n) if not gt_present[i]])

out = []
for pot in ("D", "H"):
    for arm, rid in ARMS[pot]:
        r = analyse(pot, arm, rid)
        out.append(r)
        print("== Pot_%s %-10s  SA %d/%d  EA %d/%d   off=%s gt_missing=%s" %
              (pot, arm, r["k_sherd"], r["t_sherd"], r["k_edge"], r["t_edge"], r["off"], r["gt_missing"]))
json.dump(out, open(os.path.join(ROOT, "analysis.json"), "w"), indent=1)

# graph diagnostics
for pot in ("D", "H"):
    G = load_graph(pot, N[pot])
    print("== graph Pot_%s: nodes %d  undirected edges %d  isolated %s" %
          (pot, G.shape[0], G.sum() // 2,
           [i + 1 for i in range(G.shape[0]) if G[i].sum() == 0]))
    print("   degree per piece:", {i + 1: int(G[i].sum()) for i in range(G.shape[0])})
