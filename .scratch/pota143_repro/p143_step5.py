"""Ticket 143 step5: saturation rungs (lead steer 2026-10-19).
Rung-S (finer scales): r3=r0/8, r4=r0/16 on the same 339 S0 queries.
Rung-X2/X4 (finer SPACE): fresh local-frame grid nodes (pitch 1.2mm=2x / 0.6mm=4x
  vs S0 lip pitch ~2.4mm) in 10mm discs per mid, boundary-tested at r1 with
  nearest-S0 normal, snapped SURF-C1. Grid nodes are fresh surface candidates,
  never bag dots nor their midpoints.
Per-rung yield after dedupe>=1mm vs 292+earlier-rungs + ROW40-exclusion;
ORIG-seated (on-arc<=5mm) vs junk."""
import numpy as np, os
H = ".scratch/pota143_repro"
R120 = ".scratch/pota120_repro"
R119 = ".scratch/pota119_repro"
INP = ".scratch/pota115_staging/inputs"
R123 = ".scratch/pota123_repro"
log = open(os.path.join(H, "p143_rungs.txt"), "w")
def say(s):
    print(s, flush=True); log.write(s + "\n")
A = np.loadtxt(os.path.join(R123, "Pot_C_Piece_01_Surface_0.xyz")).astype(np.float64)
X = A[:, :3].astype(np.float32); N = A[:, 3:6].astype(np.float32)
Nf = (N / np.linalg.norm(N, axis=1, keepdims=True)).astype(np.float32)
X64 = X.astype(np.float64)
def load_ply_xyz(path):
    with open(path) as f: lines = f.readlines()
    nv = 0; start = 0
    for i, ln in enumerate(lines):
        s = ln.strip()
        if s.startswith("element vertex"): nv = int(s.split()[-1])
        if s == "end_header": start = i + 1; break
    return np.array([[float(x) for x in lines[start+k].split()[:3]] for k in range(nv)])
U = load_ply_xyz(os.path.join(R120, "unclustered.ply"))
OG = np.load(os.path.join(R119, "p119_OG.npy"))
TF = np.loadtxt(os.path.join(INP, "TF.txt"))
Ri = np.linalg.inv(TF[:3, :3]); tt = TF[:3, 3]
OL = (OG - tt).dot(Ri.T)
MIDS = {"O36": OL[36], "O46": OL[46], "O96": OL[96], "O165": OL[165], "O173": OL[173], "O37": OL[37]}
G292 = np.load(os.path.join(H, "p143_G292.npy"))
w = np.load(os.path.join(R120, "p104_walk.npz")); bagP = w["bagP"]
C = np.load(os.path.join(INP, "p113_guarded.npz"))["bag"]
sp = set(map(tuple, np.round(bagP, 6))); sc = set(map(tuple, np.round(C, 6)))
rowset = set(map(tuple, np.round(np.array(sorted(sp - sc)), 6)))
THR = np.float32(0.6 * np.pi); TAU = np.float32(2.0 * np.pi)
ex = np.array([1,0,0],np.float32); ey = np.array([0,1,0],np.float32)
r0 = 6.46567859
def boundary_pts(Q, Qn, r):
    n = len(X); rr = np.float32(r)
    m = np.zeros(len(Q), dtype=bool)
    bl = 100
    for s in range(0, len(Q), bl):
        e = min(s + bl, len(Q))
        D = np.sqrt(((Q[s:e, None, :].astype(np.float64) - X64[None, :, :]) ** 2).sum(-1)).astype(np.float32)
        for t in range(e - s):
            row = D[t]
            nb = np.where(row <= rr)[0]
            nb = nb[nb != -1]
            if len(nb) + 1 < 3:
                continue
            nn = Qn[s+t]
            ref = ey if abs(float(nn[0])) > 0.9 else ex
            u = np.cross(nn, ref); u = (u / np.linalg.norm(u)).astype(np.float32)
            v = np.cross(nn, u).astype(np.float32)
            Dd = (X[nb] - Q[s+t]).astype(np.float32)
            Dd = Dd[(np.abs(Dd).sum(-1) > 1e-9)]
            if len(Dd) == 0:
                continue
            ang = np.sort(np.arctan2(Dd.dot(v), Dd.dot(u)).astype(np.float32), kind="stable")
            if len(ang) < 2:
                md = np.float32(TAU - ang[-1] + ang[0])
            else:
                g = (ang[1:] - ang[:-1]).astype(np.float32)
                w_ = np.float32(TAU - ang[-1] + ang[0])
                md = np.float32(max(float(g.max()), float(w_)))
            if md > THR:
                m[s + t] = True
    return m
def snap_surf(Q):
    B = 64; idx = np.empty(len(Q), dtype=int)
    for s in range(0, len(Q), B):
        e = min(s + B, len(Q))
        D2 = ((Q[s:e, None, :] - U[None, :, :]) ** 2).sum(-1)
        idx[s:e] = D2.argmin(1)
    SI = U[idx]; disp = np.sqrt(((Q - SI) ** 2).sum(-1))
    return SI, disp
union_mids = np.stack([MIDS[k] for k in MIDS])
def dmid_union(SI):
    return np.sqrt(((SI[:, None, :] - union_mids[None, :, :]) ** 2).sum(-1)).min(1)
def seat(pts):
    G = pts.astype(np.float64).dot(TF[:3,:3].T) + TF[:3,3]
    Dn = np.sqrt(((G[:,None,:]-OG[None,:,:])**2).sum(-1))
    return Dn.min(1), Dn.argmin(1)
Dmid_all = np.stack([np.sqrt(((X64 - MIDS[k].astype(np.float64))**2).sum(-1)) for k in MIDS])
qidx = np.where(Dmid_all.min(0) <= 10.0)[0]
Q0 = X[qidx]
Q0n = Nf[qidx]
say("queries: %d S0 verts" % len(qidx))
bag = [np.array(p, dtype=np.float64) for p in G292]
curve = []
def admit_rung(tag, Q, Qn, r):
    m = boundary_pts(Q.astype(np.float32), Qn.astype(np.float32), r)
    say("%s r=%.5f: %d/%d pass" % (tag, r, int(m.sum()), len(Q)))
    if int(m.sum()) == 0:
        curve.append((tag, r, 0, 0, 0)); return np.zeros((0,3))
    P = Q[m]
    SI, disp = snap_surf(P.astype(np.float64))
    dm = dmid_union(SI)
    keep = (disp <= 2.5) & (dm <= 5.0)
    say("  SURF-C1: disp-ok=%d mid-ok=%d both=%d" % (int((disp<=2.5).sum()), int((dm<=5.0).sum()), int(keep.sum())))
    acc = []
    for i in np.where(keep)[0]:
        sn = np.array(SI[i], dtype=np.float64)
        if tuple(np.round(sn, 6)) in rowset:
            continue
        if all(np.sqrt(((sn - b) ** 2).sum()) >= 1.0 for b in bag):
            bag.append(sn); acc.append(sn)
    SN = np.array(acc) if acc else np.zeros((0,3))
    if len(acc):
        nd, ni = seat(SN)
        on = int((nd<=5).sum())
        say("  admitted %d (%d on-arc, %d junk): seats %s" % (len(acc), on, len(acc)-on, sorted(zip(ni.tolist(), np.round(nd,2).tolist()))))
    else:
        say("  admitted 0"); on = 0
    curve.append((tag, r, len(acc), on, len(acc)-on))
    return SN
r3 = r0/8.0; r4 = r0/16.0
SN_S = admit_rung("Rung-S r3", Q0, Q0n, r3)
SN_S2 = admit_rung("Rung-S r4", Q0, Q0n, r4)
np.save(os.path.join(H, "p143_admit_r3r4.npy"), np.vstack([SN_S, SN_S2]) if (len(SN_S)+len(SN_S2)) else np.zeros((0,3)))
def grid_queries(pitch, tag):
    Q = []; Qn = []
    for k, mid in MIDS.items():
        m = mid.astype(np.float64)
        R = 10.0; n = int(np.ceil(R / pitch))
        for ix in range(-n, n+1):
            for iy in range(-n, n+1):
                p = m + np.array([ix*pitch, iy*pitch, 0.0])
                if np.sqrt(((p - m)**2).sum()) > R:
                    continue
                Q.append(p)
    Q = np.array(Q)
    B = 64; idx = np.empty(len(Q), dtype=int)
    for s in range(0, len(Q), B):
        e = min(s + B, len(Q))
        D2 = ((Q[s:e, None, :] - X64[None, :, :]) ** 2).sum(-1)
        idx[s:e] = D2.argmin(1)
    Qn = Nf[idx]
    say("%s pitch=%.1f: %d grid nodes" % (tag, pitch, len(Q)))
    return Q.astype(np.float32), Qn
QX2, QX2n = grid_queries(1.2, "Rung-X2")
SN_X2 = admit_rung("Rung-X2 r1", QX2, QX2n, r0/2.0)
QX4, QX4n = grid_queries(0.6, "Rung-X4")
SN_X4 = admit_rung("Rung-X4 r1", QX4, QX4n, r0/2.0)
np.save(os.path.join(H, "p143_admit_grids.npy"), np.vstack([SN_X2, SN_X4]) if (len(SN_X2)+len(SN_X4)) else np.zeros((0,3)))
say("")
say("SATURATION CURVE (marginal new on-arc dots per rung, dedupe vs 292+earlier):")
say("  rung-1 (rA/r1/rB/r2 x S0-verts): 10 admitted, 10 on-arc, 0 junk (p143_admit.txt)")
for tag, r, n, on, junk in curve:
    say("  %s r=%.5f: %d admitted (%d on-arc, %d junk)" % (tag, r, n, on, junk))
log.close(); print("step5 done")
