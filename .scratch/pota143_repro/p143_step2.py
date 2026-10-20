"""Ticket 143 step2: finer TRUE extraction (rule R143 stated in p143_rule.txt BEFORE running).
Pool A: S0 verts within 10mm of current uncovered mids, boundary test at
  r0 / rA=r0*.75 / r1=r0/2 / rB=r1*.75 / r2=r0/4, K=1 snap to U,
  SURF-C1 disp<=2.5 + dmid<=5 (union of licensing mids).
Pool B: 21 ROR-6 rejects, r1-tested, per-span dmid<=5 rings.
Dedupe >=1mm vs 282 bag (A-then-B) + ROW40-exclusion. ORIG seating only."""
import numpy as np, os
H = ".scratch/pota143_repro"
R120 = ".scratch/pota120_repro"
R119 = ".scratch/pota119_repro"
INP = ".scratch/pota115_staging/inputs"
R123 = ".scratch/pota123_repro"
log = open(os.path.join(H, "p143_admit.txt"), "w")
def say(s):
    print(s, flush=True); log.write(s + "\n")
A = np.loadtxt(os.path.join(R123, "Pot_C_Piece_01_Surface_0.xyz")).astype(np.float64)
X = A[:, :3].astype(np.float32); N = A[:, 3:6].astype(np.float32)
Nf = (N / np.linalg.norm(N, axis=1, keepdims=True)).astype(np.float32)
X64 = X.astype(np.float64)
say("S0 cloud: %d verts" % len(X))
def load_ply_xyz(path):
    with open(path) as f: lines = f.readlines()
    nv = 0; start = 0
    for i, ln in enumerate(lines):
        s = ln.strip()
        if s.startswith("element vertex"): nv = int(s.split()[-1])
        if s == "end_header": start = i + 1; break
    return np.array([[float(x) for x in lines[start+k].split()[:3]] for k in range(nv)])
U = load_ply_xyz(os.path.join(R120, "unclustered.ply"))
say("U verts: %d" % len(U))
OG = np.load(os.path.join(R119, "p119_OG.npy"))
TF = np.loadtxt(os.path.join(INP, "TF.txt"))
Ri = np.linalg.inv(TF[:3, :3]); tt = TF[:3, 3]
OL = (OG - tt).dot(Ri.T)
MIDS = {"O36": OL[36], "O46": OL[46], "O96": OL[96], "O165": OL[165], "O173": OL[173], "O37": OL[37]}
for k, m in MIDS.items():
    say("%s local=%s" % (k, np.round(m, 2)))
G282 = np.load(os.path.join(H, "p143_G282.npy"))
w = np.load(os.path.join(R120, "p104_walk.npz")); bagP = w["bagP"]
C = np.load(os.path.join(INP, "p113_guarded.npz"))["bag"]
sp = set(map(tuple, np.round(bagP, 6))); sc = set(map(tuple, np.round(C, 6)))
ROW40 = np.array(sorted(sp - sc)); rowset = set(map(tuple, np.round(ROW40, 6)))
say("C=%d ROW40=%d G282=%d" % (len(C), len(ROW40), len(G282)))
Dmid_all = np.stack([np.sqrt(((X64 - MIDS[k].astype(np.float64))**2).sum(-1)) for k in MIDS])
nh = (Dmid_all.min(0) <= 10.0)
qidx = np.where(nh)[0]
say("S0 verts within 10mm of a current uncovered mid: %d/%d" % (int(nh.sum()), len(X)))
for k in MIDS:
    d = np.sqrt(((X64 - MIDS[k].astype(np.float64))**2).sum(-1))
    say("  near %s: n10=%d" % (k, int((d<=10).sum())))
FLT_MIN = np.float32(1.1754944e-38)
THR = np.float32(0.6 * np.pi); TAU = np.float32(2.0 * np.pi)
ex = np.array([1,0,0],np.float32); ey = np.array([0,1,0],np.float32)
r0 = 6.46567859
LAD = {"r0": r0, "rA": r0*0.75, "r1": r0/2.0, "rB": (r0/2.0)*0.75, "r2": r0/4.0}
say("ladder: " + " ".join("%s=%.5f" % (t, v) for t, v in LAD.items()))
def boundary_at(r, queries):
    n = len(X); rr = np.float32(r)
    m = np.zeros(len(queries), dtype=bool)
    bl = 200
    for s in range(0, len(queries), bl):
        e = min(s + bl, len(queries))
        Q = queries[s:e]
        D = np.sqrt(((X64[Q][:, None, :] - X64[None, :, :]) ** 2).sum(-1)).astype(np.float32)
        for t, i in enumerate(Q):
            row = D[t]
            nb = np.where((row <= rr) & (np.arange(n) != int(i)))[0]
            if len(nb) + 1 < 3:
                continue
            nn = (Nf[int(i)]).astype(np.float32)
            ref = ey if abs(float(nn[0])) > 0.9 else ex
            u = np.cross(nn, ref); u = (u / np.linalg.norm(u)).astype(np.float32)
            v = np.cross(nn, u).astype(np.float32)
            Dd = (X[nb] - X[int(i)]).astype(np.float32)
            Dd = Dd[(Dd != np.float32(0.0)).any(-1)]
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
PASS = {}
for tag, r in LAD.items():
    m = boundary_at(r, qidx)
    PASS[tag] = qidx[m]
    say("%s=%.5fmm: %d boundary dots in current-span neighbourhoods" % (tag, r, int(m.sum())))
    np.save(os.path.join(H, "p143_nh_%s.npy" % tag), X[qidx[m]])
say("")
say("RESPONSE vs SCALE per current uncovered mid (pre-snap boundary dots n5/n10/min):")
for k, mid in MIDS.items():
    mf = mid.astype(np.float64)
    row = []
    for tag in ("r0", "rA", "r1", "rB", "r2"):
        P = np.load(os.path.join(H, "p143_nh_%s.npy" % tag)).astype(np.float64)
        d = np.sqrt(((P - mf) ** 2).sum(-1)) if len(P) else np.array([np.inf])
        row.append((int((d<5).sum()), int((d<10).sum()), float(d.min())))
    say("  mid %-5s r0=%d/%d/%.2f rA=%d/%d/%.2f r1=%d/%d/%.2f rB=%d/%d/%.2f r2=%d/%d/%.2f" % (k, row[0][0], row[0][1], row[0][2], row[1][0], row[1][1], row[1][2], row[2][0], row[2][1], row[2][2], row[3][0], row[3][1], row[3][2], row[4][0], row[4][1], row[4][2]))
SNAP = {}
for tag in ("rA", "r1", "rB", "r2"):
    P = np.load(os.path.join(H, "p143_nh_%s.npy" % tag))
    if len(P) == 0:
        SNAP[tag] = (P, np.zeros((0,3)), np.zeros(0)); continue
    B = 64; idx = np.empty(len(P), dtype=int)
    for s in range(0, len(P), B):
        e = min(s + B, len(P))
        D2 = ((P[s:e, None, :] - U[None, :, :]) ** 2).sum(-1)
        idx[s:e] = D2.argmin(1)
    SI = U[idx]; disp = np.sqrt(((P - SI) ** 2).sum(-1))
    SNAP[tag] = (P, SI, disp)
    say("%s: %d cand snap disp med=%.2f p90=%.2f max=%.2f" % (tag, len(P), float(np.median(disp)), float(np.percentile(disp, 90)), float(disp.max())))
union_mids = np.stack([MIDS[k] for k in MIDS])
rowsA = []
for tag in ("rA", "r1", "rB", "r2"):
    P, SI, disp = SNAP[tag]
    if len(P) == 0: continue
    dmid = np.sqrt(((SI[:, None, :] - union_mids[None, :, :]) ** 2).sum(-1)).min(1)
    keep = (disp <= 2.5) & (dmid <= 5.0)
    say("%s SURF-C1(disp<=2.5,dmid<=5 union): disp-ok=%d mid-ok=%d both=%d" % (tag, int((disp<=2.5).sum()), int((dmid<=5.0).sum()), int(keep.sum())))
    for i in np.where(keep)[0]:
        rowsA.append(("A-"+tag, P[i], SI[i], float(disp[i]), float(dmid[i])))
say("Pool-A SURF-C1 survivors: %d" % len(rowsA))
S = np.load(os.path.join(R120, "p104_bnd_S0.npy"))
SI_all = np.load(os.path.join(R120, "p120_SI.npy"))
keep6 = np.load(os.path.join(R120, "p120_keep6_mask.npy"))
rej = np.where(~keep6)[0]
say("ROR-6 rejects: %d" % len(rej))
Xq = X; n = len(Xq); rr1 = np.float32(r0/2.0)
def passes_r1(s0):
    i = int(s0)
    row = np.sqrt(((X64[i][None,:] - X64)**2).sum(-1)).astype(np.float32)
    nb = np.where((row <= rr1) & (np.arange(n) != i))[0]
    if len(nb) + 1 < 3:
        return False, 0
    nn = Nf[i].astype(np.float32)
    ref = ey if abs(float(nn[0])) > 0.9 else ex
    u = np.cross(nn, ref); u = (u / np.linalg.norm(u)).astype(np.float32)
    v = np.cross(nn, u).astype(np.float32)
    Dd = (Xq[nb] - Xq[i]).astype(np.float32)
    Dd = Dd[(Dd != np.float32(0.0)).any(-1)]
    if len(Dd) == 0:
        return False, len(nb)
    ang = np.sort(np.arctan2(Dd.dot(v), Dd.dot(u)).astype(np.float32), kind="stable")
    if len(ang) < 2:
        md = np.float32(TAU - ang[-1] + ang[0])
    else:
        g = (ang[1:] - ang[:-1]).astype(np.float32)
        w_ = np.float32(TAU - ang[-1] + ang[0])
        md = np.float32(max(float(g.max()), float(w_)))
    return bool(md > THR), len(nb)
key2idx = {}
for k in range(len(X)): key2idx.setdefault(tuple(np.round(X64[k], 6)), k)
s0idx = np.empty(len(S), dtype=int); miss = 0
for i in range(len(S)):
    k = key2idx.get(tuple(np.round(S[i].astype(np.float64), 6)), None)
    if k is None:
        miss += 1
        k = int(np.argmin(np.sqrt(((X64 - S[i].astype(np.float64))**2).sum(-1))))
    s0idx[i] = k
say("S->S0 index map misses: %d/%d" % (miss, len(S)))
rowsB = []
for i in rej:
    ok, nnb = passes_r1(s0idx[i])
    disp = float(np.sqrt(((S[i].astype(np.float64) - SI_all[i].astype(np.float64))**2).sum()))
    dm_each = {k: float(np.sqrt(((SI_all[i].astype(np.float64) - MIDS[k].astype(np.float64))**2).sum())) for k in MIDS}
    dm = min(dm_each.values())
    inside = [k for k in MIDS if dm_each[k] <= 5.0]
    say("reject %3d r1=%s nnb=%3d disp=%.2f dmid-min=%.2f rings=%s" % (i, "PASS" if ok else "fail", nnb, disp, dm, inside if inside else "-"))
    if ok and disp <= 2.5 and inside:
        rowsB.append(("B-rej%d" % i, S[i], SI_all[i], disp, dm, inside))
say("Pool-B survivors (r1-pass & disp<=2.5 & per-span ring<=5): %d" % len(rowsB))
bag = [np.array(p, dtype=np.float64) for p in G282]
acc = []
for tag, pre, sn, disp, dm, *rest in rowsA + [(t, p, s, d, m, None) for (t, p, s, d, m) in rowsB]:
    sn = np.array(sn, dtype=np.float64)
    if tuple(np.round(sn, 6)) in rowset:
        say("  %s dropped: ROW40-coord" % tag); continue
    if all(np.sqrt(((sn - b) ** 2).sum()) >= 1.0 for b in bag):
        bag.append(sn); acc.append((tag, pre, sn, disp, dm))
    else:
        say("  %s dropped: dedupe-collision (dbag<1mm)" % tag)
say("ADMITTED after dedupe+ROW40 (A-then-B): %d" % len(acc))
for tag, pre, sn, disp, dm in acc:
    say("  %s snap=[%s] disp=%.2f dmid=%.2f" % (tag, np.round(sn, 2), disp, dm))
SN = np.array([a[2] for a in acc]) if acc else np.zeros((0, 3))
np.save(os.path.join(H, "p143_admit.npy"), SN)
if len(acc):
    G = SN.astype(np.float64).dot(TF[:3,:3].T) + TF[:3,3]
    Dn = np.sqrt(((G[:,None,:]-OG[None,:,:])**2).sum(-1)); nd = Dn.min(1); ni = Dn.argmin(1)
    say("admitted ORIG-seat dist: %s idx: %s within-5mm: %d/%d" % (np.round(nd,2), sorted(ni.tolist()), int((nd<=5).sum()), len(nd)))
    junk = int((nd>5).sum())
    say("JUNK (>5mm): %d" % junk)
    for (tag, pre, sn, disp, dm), d_, s_ in zip(acc, nd, ni):
        say("  %s -> ORIG[%d] d=%.2f disp=%.2f dmid=%.2f" % (tag, int(s_), float(d_), disp, dm))
else:
    say("admitted 0: bag unchanged (282+0)")
log.close(); print("step2 done")
