# 173 step0: controls + rim-strip re-sample + merged-sheet estimator + curated post-snap bag.
# Method per 172 verdict: surfaceSegmentation dropped the 2-6mm rim strip into unclustered.ply;
# re-sample = real unclustered mesh vertices hugging ORIG (<=2.5mm), zero invented positions.
# Estimator replica verbatim from 169 step2a (pcl_flags, TH=0.6pi, r=6.4657).
import numpy as np, os
from collections import Counter, defaultdict
from scipy.spatial import cKDTree
H = ".scratch/pota173_repro"
OUT = "artifacts/pota173"
os.makedirs(H, exist_ok=True); os.makedirs(OUT, exist_ok=True)
log = open(os.path.join(H, "p173_step0.txt"), "w")
def say(s):
    print(s, flush=True); log.write(s + "\n")
def load_obj(path):
    V, F = [], []
    with open(path) as fh:
        for ln in fh:
            if ln.startswith("v "): V.append([float(x) for x in ln.split()[1:4]])
            elif ln.startswith("f "): F.append([int(x.split("/")[0]) - 1 for x in ln.split()[1:4]])
    return np.array(V), np.array(F, dtype=np.int64)
def load_pcd3(p):
    HDR = ('VERSION','FIELDS','SIZE','TYPE','COUNT','WIDTH','HEIGHT','VIEWPOINT','POINTS','DATA')
    P = []
    for ln in open(p):
        s = ln.strip()
        if not s or s[0] == '#' or s.split()[0] in HDR: continue
        try: P.append(list(map(float, s.split()[:3])))
        except ValueError: continue
    return np.array(P)
def load_csv(p):
    import csv
    with open(p) as f: r = list(csv.DictReader(f))
    return np.array([[float(x['x']), float(x['y']), float(x['z'])] for x in r])
def load_ply_xn(p):
    X, N = [], []
    for ln in open(p):
        s = ln.strip()
        if not s or s[0] == '#' or s.startswith(('ply','format','element','property','end_header','comment')): continue
        f = s.split()
        try: vals = list(map(float, f[:7]))
        except ValueError: continue
        if len(vals) < 6: continue
        X.append(vals[0:3]); N.append(vals[3:6])
    return np.array(X), np.array(N)
V, F = load_obj("temp_download/Mesh/Pot_C/Pot_C_Piece_01_Mesh_DS.obj")
assert (len(V), len(F)) == (11875, 23114), (len(V), len(F))
TF = np.loadtxt(".scratch/pota115_staging/inputs/TF.txt")
T = np.loadtxt(".scratch/pota162_repro/sfs_main/original_samples/SfS_pp/Ground Truth/Pot_C_Piece_1_T.txt")
assert np.allclose(T, TF)
R, t = TF[:3,:3], TF[:3,3]
Vg = V @ R.T + t
EC = Counter()
for f in F:
    for a, b in [(f[0],f[1]),(f[1],f[2]),(f[2],f[0])]: EC[tuple(sorted((a,b)))] += 1
assert sum(1 for c in EC.values() if c == 1) == 636
bnd = [e for e,c in EC.items() if c==1]
adj = defaultdict(set)
for a,b in bnd: adj[a].add(b); adj[b].add(a)
seen=set(); loops=[]
for s in adj:
    if s in seen: continue
    cur, prev, loop = s, -1, [s]
    seen.add(s)
    while True:
        nxts=[x for x in adj[cur] if x!=prev]
        if len(nxts)==0: break
        nxt=nxts[0] if nxts[0] not in seen else (nxts[1] if len(nxts)>1 and nxts[1] not in seen else None)
        if nxt is None: break
        if nxt==s: break
        prev,cur=cur,nxt; seen.add(cur); loop.append(cur)
    loops.append(loop)
order=sorted(range(len(loops)), key=lambda i:-len(loops[i]))
loops=[loops[i] for i in order]
assert [len(l) for l in loops]==[274,247,97,18]
HOLE=[i for i,l in enumerate(loops) if len(l)==247][0]
say("loops OK [274,247,97,18] HOLE=%d" % HOLE)
G0=load_pcd3(".scratch/pota162_repro/sfs_main/original_samples/SfS_pp/Breaklines/Pot_C_Piece_01_Breakline_0.pcd") @ R.T + t
assert G0.shape==(211,3)
G1=load_pcd3(".scratch/pota162_repro/sfs_main/original_samples/SfS_pp/Breaklines/Pot_C_Piece_01_Breakline_1.pcd") @ R.T + t
G=np.vstack([G0,G1]); KG=cKDTree(G)
S = np.loadtxt(".scratch/pota163_repro/inputs/C01S0_STAGED.xyz")
X, N = S[:,:3], S[:,3:6]
assert len(X)==11165
say("S0 staged n=%d" % len(X))
nn=np.linalg.norm(N,axis=1)
say("S0 normals: med=%.6f min=%.6f NaN=%d" % (float(np.median(nn)), float(nn.min()), int(np.isnan(N).sum())))
U, UN = load_ply_xn(".scratch/pota163_repro/inputs/Pot_C_Piece_01_unclustered.ply")
say("unclustered n=%d" % len(U))
Ug = U @ R.T + t
un=np.linalg.norm(UN,axis=1)
say("unc normals: med=%.6f min=%.6f NaN=%d zero=%d" % (float(np.median(un)), float(un.min()), int(np.isnan(UN).sum()), int((un<1e-12).sum())))
z = np.load(".scratch/pota172_repro/p172_meshgap.npz")
gidx, runs = z["gidx"], [tuple(map(int,r)) for r in z["runs"]]
say("gap stations n=%d" % len(gidx))
Xg = X @ R.T + t
d_sheet = cKDTree(Xg).query(G0[gidx])[0]
say("shortfall control: sheet->gap min=%.2f med=%.2f max=%.2f (expect ~0.76/~2.9/~5.2)" % (d_sheet.min(), float(np.median(d_sheet)), d_sheet.max()))
d_to_G0 = cKDTree(G0).query(Ug)[0]
strip = np.where(d_to_G0 <= 2.5)[0]
say("rim strip: unclustered within 2.5mm of ORIG: n=%d/%d" % (len(strip), len(U)))
say("strip dist-to-ORIG: min=%.3f med=%.3f max=%.3f" % (d_to_G0[strip].min(), float(np.median(d_to_G0[strip])), d_to_G0[strip].max()))
Kstrip = cKDTree(Ug[strip])
d_gap_strip = Kstrip.query(G0[gidx])[0]
say("gap station -> strip: min=%.3f med=%.3f max=%.3f frac<2mm=%.3f" % (d_gap_strip.min(), float(np.median(d_gap_strip)), d_gap_strip.max(), float((d_gap_strip<2).mean())))
snn = un[strip]
say("strip normals: med=%.6f min=%.6f NaN=%d" % (float(np.median(snn)), float(snn.min()), int(np.isnan(UN[strip]).sum())))
bb0 = np.stack([X.min(0), X.max(0)])
Xm = np.vstack([X, U[strip]]); Nm = np.vstack([N, UN[strip]])
bb1 = np.stack([Xm.min(0), Xm.max(0)])
say("merged sheet n=%d (+%d strip); bbox identical=%s" % (len(Xm), len(strip), bool((bb0==bb1).all())))
# exact code formula (edgeline_extraction_headless.cpp:869-891): spacing from sheet area, r=6x clamp[1,15]
be = bb1[1]-bb1[0]
s0, s1 = be[0], be[1]
if s1 > s0: s0, s1 = s1, s0
if be[2] > s0: s1, s0 = s0, be[2]
elif be[2] > s1: s1 = be[2]
sp_merged = float(np.sqrt((s0*s1)/max(100, len(Xm))))
r_merged = float(max(1.0, min(15.0, sp_merged*6.0)))
beS = bb0[1]-bb0[0]
t0, t1 = beS[0], beS[1]
if t1 > t0: t0, t1 = t1, t0
if beS[2] > t0: t1, t0 = t0, beS[2]
elif beS[2] > t1: t1 = beS[2]
sp_s0 = float(np.sqrt((t0*t1)/max(100, len(X))))
say("spacing S0=%.4f -> r=%.4f | merged=%.4f -> r=%.4f" % (sp_s0, max(1.0,min(15.0,sp_s0*6.0)), sp_merged, r_merged))
TH = 0.6*np.pi; r = 6.4657
def pcl_flags(Xe, Ne, r):
    Kq = cKDTree(Xe)
    ball = Kq.query_ball_point(Xe, r)
    flags = np.zeros(len(Xe), dtype=bool)
    maxgaps = np.full(len(Xe), np.nan)
    supN = np.zeros(len(Xe), dtype=int)
    for i in range(len(Xe)):
        nb = [j for j in ball[i] if j != i]
        n = Ne[i]
        supN[i] = len(nb)
        if len(nb) < 3: continue
        VV = Xe[nb]-Xe[i]
        VV = VV - np.outer(VV@n, n)
        up = np.array([0.0,0.0,1.0]) if abs(n[2]) < 0.9 else np.array([1.0,0.0,0.0])
        u = up - (up@n)*n; u = u/np.linalg.norm(u)
        v = np.cross(n, u)
        ang = np.sort(np.arctan2(VV@v, VV@u))
        dif = np.diff(ang)
        wrap = 2*np.pi - (ang[-1]-ang[0])
        mg = max(dif.max(), wrap)
        maxgaps[i] = mg
        flags[i] = mg > TH
    return flags, maxgaps, supN
say("running estimator on S0-only (control)...")
f0, mg0, sn0 = pcl_flags(X, N, r)
C0 = load_csv(".scratch/pota162_repro/pota160_repro/C01_ADAPT/veto_align_Pot_C_Piece_01_c0.csv")
assert C0.shape==(364,3)
C0g = C0 @ R.T + t
Xgf = (X[f0]) @ R.T + t
d_c0 = cKDTree(Xgf).query(C0g)[0]
say("S0-only control: mine-fired=%d c0=364 maxdev=%.4f n>0.5mm=%d (expect 364/0.0000/0)" % (int(f0.sum()), d_c0.max(), int((d_c0>0.5).sum())))
assert int(f0.sum())==364 and d_c0.max()<1e-9
say("ESTIMATOR CONTROL BIT-EXACT")
say("running estimator on merged sheet with code-formula r=%.4f..." % r_merged)
fm, mgm, snm = pcl_flags(Xm, Nm, r_merged)
say("merged fired=%d (S0-only 364); strip-point fires=%d/%d" % (int(fm.sum()), int(fm[len(X):].sum()), len(strip)))
Xmf = Xm[fm]
ret = cKDTree(Xmf).query(X[f0])[0]
say("of 364 S0 fires retained in merged set: %d (maxdev %.4f)" % (int((ret<0.5).sum()), ret.max()))
np.save(H + "/p173_fm.npy", fm)
say("PART1 DONE")
log.flush()
# --- part 2: labels + 168-identical curation + snap + spacing + save + BASE control ---
Pmg = Xmf @ R.T + t
D = KG.query(Pmg)[0]
near, far = D<2.0, D>5.0
say("merged fired labels: NEAR=%d MID=%d FAR=%d" % (int(near.sum()), int((~(near|far)).sum()), int(far.sum())))
segs=[]
for i,l in enumerate(loops):
    lv=Vg[l]; segs.append(np.stack([lv,np.roll(lv,-1,axis=0)],axis=1))
Sseg=np.vstack(segs); loop_of_seg=np.concatenate([np.full(len(ll),i) for i,ll in enumerate(loops)])
A,B=Sseg[:,0],Sseg[:,1]; AB=B-A; den=(AB**2).sum(axis=1)
def seg_dist(P):
    AP=P[:,None,:]-A[None,:,:]
    tt=np.clip((AP*AB[None,:,:]).sum(axis=2)/den[None,:],0,1)
    Cc=A[None,:,:]+tt[:,:,None]*AB[None,:,:]
    d=np.linalg.norm(P[:,None,:]-Cc,axis=2); j=d.argmin(axis=1)
    return d[np.arange(len(P)),j], loop_of_seg[j]
dfar,jfar=seg_dist(Pmg[far])
drop_far = np.zeros(len(Pmg),bool); drop_far[np.where(far)[0][jfar==HOLE]] = True
say("drop FAR&HOLE=%d; NEAR-dropped=%d" % (int(drop_far.sum()), int((near & drop_far).sum())))
assert (near & drop_far).sum()==0
keep = ~drop_far
say("kept=%d" % int(keep.sum()))
KU = cKDTree(U)
Dsnap, j_snap = KU.query(Xmf[keep])
Usnap = U[j_snap]
say("snap disp: med=%.2f n>1mm=%d/%d max=%.1f" % (float(np.median(Dsnap)), int((Dsnap>1).sum()), int(keep.sum()), float(Dsnap.max())))
BAG = Usnap @ R.T + t
d_bag = cKDTree(BAG).query(G0)[0]
DObag = cKDTree(G0).query(BAG)[0]
cap = int((DObag<2).sum())
say("DENSIFIED BAG: n=%d seating(cap)=%d/211" % (len(BAG), cap))
for ri,(a,b) in enumerate(runs):
    m = np.array([(g>=a)&(g<=b) for g in gidx])
    ddr = DObag[gidx[m]]
    say("  R%-2d post-snap min=%.2f max=%.2f seated=%d/%d" % (ri, ddr.min(), ddr.max(), int((ddr<2).sum()), m.sum()))
onarc = BAG[d_bag<2.0]
say("on-arc dots (<2mm of ORIG): %d/%d" % (len(onarc), len(BAG)))
if len(onarc) >= 2:
    sta = cKDTree(G0).query(onarc)[1]
    o = np.argsort(sta, kind="stable")
    Q = onarc[o]
    gaps = np.sqrt(((Q[1:]-Q[:-1])**2).sum(-1))
    Big = float(np.sqrt(((Q[0]-Q[-1])**2).sum()))
    allg = np.append(gaps, Big)
    say("station-ordered gaps: med=%.2f p90=%.2f max=%.2f (author 1.80/1.80/1.97 per 147)" % (float(np.median(allg)), float(np.percentile(allg,90)), float(allg.max())))
np.savez(os.path.join(H, "p173_bag.npz"), BAG=BAG, G0=G0, TF=TF, Dsnap=Dsnap, strip=strip, keep=np.where(keep)[0])
BASE=load_pcd3(".scratch/pota161_repro/C01_BASE_Pot_C_Piece_01_Breakline_0.pcd")
assert len(BASE)==402
Gb=BASE @ R.T + t
Db=np.sqrt(((Gb[:,None,:]-G0[None,:,:])**2).sum(-1)).min(1)
DOb=np.sqrt(((G0[:,None,:]-Gb[None,:,:])**2).sum(-1)).min(1)
say("BASE-CONTROL: n=402 med=%.2f <2mm=%.1f%% ORIGcov %d/211 (expect 5.61/22.9/92)" % (float(np.median(Db)), float((Db<2).mean()*100), int((DOb<2).sum())))
assert abs(float(np.median(Db))-5.61)<0.01 and int((DOb<2).sum())==92
say("STEP0 DONE")
log.close()
