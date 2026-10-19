# 173 step0d: FINAL densified bag = 168-curated S0 post-snap (291) + rim strip (unclustered <=2.5mm ORIG).
# Strip = real mesh vertices (zero invented); ORIG-guided instrument per 147 precedent, stated;
# 597/612 overlap ORIG-free cand (p173_step0c) so guidance barely matters. Estimator legs:
# S0-only bit-exact control (p173_step0) + merged-sheet experiment NEGATIVE (p173_step0/0b).
import numpy as np, os
from collections import Counter, defaultdict
from scipy.spatial import cKDTree
H = ".scratch/pota173_repro"
OUT = "artifacts/pota173"
os.makedirs(H, exist_ok=True); os.makedirs(OUT, exist_ok=True)
log = open(os.path.join(H, "p173_step0d.txt"), "w")
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
def load_ply_x(p):
    XX = []
    for ln in open(p):
        s = ln.strip()
        if not s or s[0] == '#' or s.startswith(('ply','format','element','property','end_header','comment')): continue
        f = s.split()
        try: vals = list(map(float, f[:3]))
        except ValueError: continue
        XX.append(vals)
    return np.array(XX)
V, F = load_obj("temp_download/Mesh/Pot_C/Pot_C_Piece_01_Mesh_DS.obj")
assert (len(V), len(F)) == (11875, 23114)
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
G0=load_pcd3(".scratch/pota162_repro/sfs_main/original_samples/SfS_pp/Breaklines/Pot_C_Piece_01_Breakline_0.pcd") @ R.T + t
assert G0.shape==(211,3)
G1=load_pcd3(".scratch/pota162_repro/sfs_main/original_samples/SfS_pp/Breaklines/Pot_C_Piece_01_Breakline_1.pcd") @ R.T + t
G=np.vstack([G0,G1]); KG=cKDTree(G)
KG0=cKDTree(G0)
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
def curate(Pg_local, tag):
    Pgg = Pg_local @ R.T + t
    D = KG.query(Pgg)[0]
    near, far = D<2.0, D>5.0
    dfar,jfar=seg_dist(Pgg[far])
    drop = np.zeros(len(Pgg),bool); drop[np.where(far)[0][jfar==HOLE]] = True
    say("%s: n=%d NEAR=%d MID=%d FAR=%d drop-FAR&HOLE=%d NEAR-dropped=%d" % (tag, len(Pgg), int(near.sum()), int((~(near|far)).sum()), int(far.sum()), int(drop.sum()), int((near&drop).sum())))
    assert (near&drop).sum()==0
    return ~drop, Pgg
C0 = load_csv(".scratch/pota162_repro/pota160_repro/C01_ADAPT/veto_align_Pot_C_Piece_01_c0.csv")
assert C0.shape==(364,3)
keep0, Pg0 = curate(C0, "S0-fired")
assert int((~keep0).sum())==73 and int(keep0.sum())==291
U = load_ply_x(".scratch/pota163_repro/inputs/Pot_C_Piece_01_unclustered.ply")
say("unclustered n=%d" % len(U))
Ug = U @ R.T + t
d_to_G0 = KG0.query(Ug)[0]
strip = np.where(d_to_G0 <= 2.5)[0]
say("rim strip (<=2.5mm ORIG): n=%d/2343" % len(strip))
keeps, Pgs = curate(U[strip], "strip")
say("strip kept=%d dropped=%d" % (int(keeps.sum()), int((~keeps).sum())))
cand = np.load(H + "/p173_cand.npy")
say("strip-overlap ORIG-free cand: %d/%d" % (len(np.intersect1d(strip, cand)), len(strip)))
KU = cKDTree(U)
Ds0, j0 = KU.query(C0[keep0])
say("S0 snap disp: med=%.2f n>1mm=%d/%d max=%.1f" % (float(np.median(Ds0)), int((Ds0>1).sum()), int(keep0.sum()), float(Ds0.max())))
_, jall = KU.query(C0)
d_post = cKDTree(U[jall] @ R.T + t).query(G0)[0]
say("full-364 post-snap seating: %d/211 (expect 90)" % int((d_post<2).sum()))
assert int((d_post<2).sum())==90
Dss, js = KU.query(U[strip][keeps])
say("strip snap disp: med=%.3f max=%.3f n>1mm=%d (expect ~identity)" % (float(np.median(Dss)), float(Dss.max()), int((Dss>1).sum())))
B0 = U[j0] @ R.T + t
BS = U[js] @ R.T + t
BAG = np.vstack([B0, BS])
say("concat n=%d (291+%d)" % (len(BAG), len(BS)))
K32 = np.array([BAG[i].astype(np.float64).tobytes() for i in range(len(BAG))])
_, uniq = np.unique(K32, return_index=True)
dup = len(BAG)-len(uniq)
BAG = BAG[np.sort(uniq)]
say("exact-duplicate rows removed=%d -> BAG n=%d" % (dup, len(BAG)))
d_bag = cKDTree(BAG).query(G0)[0]
cap = int((d_bag<2).sum())
say("DENSIFIED BAG CAP: %d/211" % cap)
z = np.load(".scratch/pota172_repro/p172_meshgap.npz")
gidx, runs = z["gidx"], [tuple(map(int,r)) for r in z["runs"]]
for ri,(a,b) in enumerate(runs):
    m = np.array([(g>=a)&(g<=b) for g in gidx])
    ddr = d_bag[gidx[m]]
    say("  R%-2d cap min=%.2f max=%.2f seated=%d/%d" % (ri, ddr.min(), ddr.max(), int((ddr<2).sum()), m.sum()))
d_toorig = cKDTree(G0).query(BAG)[0]
onarc = BAG[d_toorig<2.0]
say("on-arc dots (<2mm ORIG): %d/%d" % (len(onarc), len(BAG)))
if len(onarc) >= 2:
    sta = KG0.query(onarc)[1]
    o = np.argsort(sta, kind="stable")
    Q = onarc[o]
    gaps = np.sqrt(((Q[1:]-Q[:-1])**2).sum(-1))
    Big = float(np.sqrt(((Q[0]-Q[-1])**2).sum()))
    allg = np.append(gaps, Big)
    say("station-ordered gaps: med=%.2f p90=%.2f max=%.2f (author 1.80/1.80/1.97 per 147)" % (float(np.median(allg)), float(np.percentile(allg,90)), float(allg.max())))
np.savez(os.path.join(H, "p173_bag.npz"), BAG=BAG, G0=G0, TF=TF)
BASE=load_pcd3(".scratch/pota161_repro/C01_BASE_Pot_C_Piece_01_Breakline_0.pcd")
assert len(BASE)==402
Gb=BASE @ R.T + t
Db=np.sqrt(((Gb[:,None,:]-G0[None,:,:])**2).sum(-1)).min(1)
DOb=np.sqrt(((G0[:,None,:]-Gb[None,:,:])**2).sum(-1)).min(1)
say("BASE-CONTROL: n=402 med=%.2f <2mm=%.1f%% ORIGcov %d/211 (expect 5.61/22.9/92)" % (float(np.median(Db)), float((Db<2).mean()*100), int((DOb<2).sum())))
assert abs(float(np.median(Db))-5.61)<0.01 and int((DOb<2).sum())==92
say("STEP0D DONE")
log.close()
