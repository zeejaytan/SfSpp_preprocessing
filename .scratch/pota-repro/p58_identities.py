"""Ticket 58 pilot (Pot F): replicate CountResult (data_structure.cpp) to name
seated pieces/edges. isSimilarTrans: D = GT_rel * T_rel^-1;
angle(norm of log(R)) < 0.35 rad, |t| < 50.
GT_rel(i,j) = inv(GT_i)*GT_j ; T_rel(i,j) = inv(Est_i)*Est_j.
Piece seated iff >=1 correct edge. Verifies recomputed tallies equal the
binary's printed tallies."""
import numpy as np, os, sys


def load_T(path):
    rows = []
    with open(path) as f:
        for line in line_strip(open(path)):
            rows.append([float(x) for x in line.split()])
    return np.array(rows[:3])  # first 3 rows (skip 0 0 0 1); Trans::Read skips last line


def line_strip(fh):
    for line in fh:
        line = line.strip()
        if line:
            yield line


def load_T4(path):
    M = np.eye(4)
    M[:3, :] = load_T(path)
    return M


def angle_of(R):
    cos_a = np.clip((np.trace(R) - 1.0) / 2.0, -1.0, 1.0)
    return float(np.arccos(cos_a))


def similar(GT_rel, T_rel, rad=0.35, t_thr=50.0):
    D = GT_rel @ np.linalg.inv(T_rel)
    R = D[:3, :3]; t = D[:3, 3]
    return (angle_of(R) < rad) and (float(np.linalg.norm(t)) < t_thr), angle_of(R), float(np.linalg.norm(t))


def evaluate(fetch, pot, arm, n):
    gdir = os.path.join(fetch, 'GT')
    tdir = os.path.join(fetch, f'T_{arm}')
    rows = []
    with open(os.path.join(gdir, f'Pot_{pot}_simple_graph.txt')) as f:
        for line in f:
            line = line.strip()
            if line:
                rows.append([float(x) for x in line.split()])
    graph = np.array(rows)
    GT = [load_T4(os.path.join(gdir, f'Pot_{pot}_Piece_{k}_T.txt')) for k in range(1, n + 1)]
    Est, missing_T = [], []
    for i in range(n):
        # binary writes T_ito_i with 0-based piece index (B precedent: T_0..T_8);
        # a missing file means the piece was never placed -> identity + flag
        p = os.path.join(tdir, f'T_{i}to_{i}.txt')
        if os.path.exists(p):
            Est.append(load_T4(p))
        else:
            Est.append(np.eye(4))
            missing_T.append(i + 1)
    edges = [(i, j) for i in range(n) for j in range(i + 1, n) if graph[i, j]]
    correct, wrong = [], []
    per_piece = {i: [] for i in range(n)}
    for (i, j) in edges:
        GT_rel = np.linalg.inv(GT[i]) @ GT[j]
        T_rel = np.linalg.inv(Est[i]) @ Est[j]
        ok, ang, tr = similar(GT_rel, T_rel)
        (correct if ok else wrong).append((i + 1, j + 1, ang, tr))
        per_piece[i].append(ok); per_piece[j].append(ok)
    seated = sorted([i + 1 for i in range(n) if any(per_piece[i])])
    missing = sorted([i + 1 for i in range(n) if not any(per_piece[i])])
    return seated, missing, correct, wrong, edges, missing_T


if __name__ == '__main__':
    fetch = sys.argv[1] if len(sys.argv) > 1 else r'C:\temp\p58\fetch_R1'
    pot = sys.argv[2] if len(sys.argv) > 2 else 'F'
    n = int(sys.argv[3]) if len(sys.argv) > 3 else 6
    for arm in ('fresh', 'orig'):
        seated, missing, correct, wrong, edges, missing_T = evaluate(fetch, pot, arm, n)
        print(f'{pot}_{arm}: recomputed {len(seated)}/{n} sherds, {len(correct)}/{len(edges)} edges')
        print(f'  unplaced (no T file): {missing_T}')
        print(f'  seated pieces: {seated}')
        print(f'  missing pieces: {missing}')
        print(f'  correct edges: {[(a,b) for a,b,_,_ in correct]}')
        print(f'  wrong edges: {[(a,b,round(g,3),round(t,1)) for a,b,g,t in wrong]}')
