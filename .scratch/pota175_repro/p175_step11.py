# 175 step11: parent-surface split. Per-triangle wall labels on DS mesh (mesh-frame, ORIG-free);
# each BAG dot inherits nearest-triangle wall label. Origin mapping S0-vs-strip through snap/dedup.
import numpy as np
from scipy.spatial import cKDTree
H = "C:/PR/SfSpp_preprocessing/.scratch/.wt-dchain-port/.scratch/pota175_repro"
log = open(H + "/p175_step11.txt", "w")
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
P = "C:/PR/SfSpp_preprocessing/.scratch/.wt-dchain-port"
V, F = load_obj(P + "/temp_download/Mesh/Pot_C/Pot_C_Piece_01_Mesh_DS.obj")
assert (len(V), len(F)) == (11875, 23114)
TF = np.loadtxt(P + "/.scratch/pota115_staging/inputs/TF.txt")
T = np.loadtxt(P + "/.scratch/pota162_repro/sfs_main/original_samples/SfS_pp/Ground Truth/Pot_C_Piece_1_T.txt")
assert np.allclose(T, TF)
R, t = TF[:3,:3], TF[:3,3]
Vg = V.dot(R.T) + t
v0,v1,v2 = Vg[F[:,0]],Vg[F[:,1]],Vg[F[:,2]]
fn = np.cross(v1-v0,v2-v0); L=np.linalg.norm(fn,axis=1); L[L==0]=1; fn=fn/L[:,None]
C = (v0+v1+v2)/3
# ORIG-free mesh frame: centroid + radial of the MESH itself
cenM = Vg.mean(0)
rhat = (C-cenM)/np.maximum(np.linalg.norm(C-cenM,axis=1)[:,None],1e-9)
tri_align = (fn*rhat).sum(-1)
wall = np.where(tri_align < -0.5, -1, np.where(tri_align > 0.5, 1, 0))  # -1 inner-wall, +1 outer-wall, 0 fold
say("mesh triangles: inner-wall=%d outer-wall=%d fold=%d (of 23114)" % (int((wall==-1).sum()), int((wall==1).sum()), int((wall==0).sum())))
d = np.load(P + "/.scratch/pota173_repro/p173_bag.npz", allow_pickle=True)
BAG, G0 = d["BAG"], d["G0"]
say("bag=%d ORIG=%d" % (len(BAG), len(G0)))
# exact point-to-triangle (Ericson 5.1.5), chunked over faces
A = v0; AB = v1-v0; AC = v2-v0
d1 = (AB*AB).sum(1); d2 = (AB*AC).sum(1); d3 = (AC*AC).sum(1)
den = d1*d3-d2*d2; den[den==0] = 1e-30
best_d = np.full(len(BAG), 1e18); best_j = np.zeros(len(BAG), dtype=int)
CH = 2000
for a in range(0, len(F), CH):
    b = min(a+CH, len(F))
    AP = BAG[:,None,:]-A[None,a:b,:]
    d4 = (AP*AB[None,a:b,:]).sum(-1); d5 = (AP*AC[None,a:b,:]).sum(-1)
    vb = (d3[a:b][None,:]*d4-d2[a:b][None,:]*d5)/den[a:b][None,:]
    wb = (d1[a:b][None,:]*d5-d2[a:b][None,:]*d4)/den[a:b][None,:]
    ub = 1.0-vb-wb
    inside = (ub>=0)&(vb>=0)&(wb>=0)
    Cc = A[None,a:b,:]+AB[None,a:b,:]*vb[:,:,None]+AC[None,a:b,:]*wb[:,:,None]
    dd_in = np.where(inside, ((BAG[:,None,:]-Cc)**2).sum(-1), 1e18)
    # outside: distance to 3 segments
    dd_out = np.full_like(dd_in, 1e18)
    for P0,P1 in ((v0[a:b],v1[a:b]),(v1[a:b],v2[a:b]),(v2[a:b],v0[a:b])):
        E = P1-P0; L2 = (E*E).sum(-1); L2[L2==0]=1
        tt = np.clip(((BAG[:,None,:]-P0[None,:,:])*E[None,:,:]).sum(-1)/L2[None,:],0,1)
        Q = P0[None,:,:]+tt[:,:,None]*E[None,:,:]
        dd_out = np.minimum(dd_out, ((BAG[:,None,:]-Q)**2).sum(-1))
    dd = np.minimum(dd_in, np.where(inside, 1e18, dd_out))
    j = dd.argmin(1); dv = dd[np.arange(len(BAG)),j]
    upd = dv < best_d
    best_d[upd] = dv[upd]; best_j[upd] = (a+j[upd])
    if a % 6000 == 0: print("chunk %d/%d" % (a, len(F)), flush=True)
best_d = np.sqrt(best_d)
say("nearest-triangle dist: med=%.3f max=%.3f" % (float(np.median(best_d)), float(best_d.max())))
plab = wall[best_j]  # inherited parent-face label: -1 inner wall, +1 outer wall, 0 fold
say("parent-face labels: inner-wall=%d outer-wall=%d fold=%d" % (int((plab==-1).sum()), int((plab==1).sum()), int((plab==0).sum())))
np.save(H+"/p175_parentface.npy", plab)
np.save(H+"/p175_tridist.npy", best_d)
# origin mapping: S0 (291 snapped) vs strip (612) through dedup
C0 = load_csv(P + "/.scratch/pota162_repro/pota160_repro/C01_ADAPT/veto_align_Pot_C_Piece_01_c0.csv")
assert C0.shape == (364,3)
KG0loc = None
from scipy.spatial import cKDTree as KD
G0loc = load_pcd3(P + "/.scratch/pota162_repro/sfs_main/original_samples/SfS_pp/Breaklines/Pot_C_Piece_01_Breakline_0.pcd")
KG = KD(G0loc @ R.T + t)
D = KD(G0loc @ R.T + t).query(C0 @ R.T + t)[0]
# replicate 173 curate: NEAR<2 FAR>5 + FAR&HOLE drop (need boundary loops; recompute quickly)
from collections import Counter, defaultdict
EC = Counter()
for f in F:
    for a2,b2 in [(f[0],f[1]),(f[1],f[2]),(f[2],f[0])]: EC[tuple(sorted((a2,b2)))] += 1
assert sum(1 for c in EC.values() if c == 1) == 636
bnd = [e for e,c in EC.items() if c==1]
say("boundary edges=%d (expect 636)" % len(bnd))
adj = defaultdict(set)
for a2,b2 in bnd: adj[a2].add(b2); adj[b2].add(a2)
seen=set(); loops=[]
for ss in adj:
    if ss in seen: continue
    cur, prev, loop = ss, -1, [ss]
    seen.add(ss)
    while True:
        nxts=[x for x in adj[cur] if x!=prev]
        if len(nxts)==0: break
        nxt=nxts[0] if nxts[0] not in seen else (nxts[1] if len(nxts)>1 and nxts[1] not in seen else None)
        if nxt is None: break
        if nxt==ss: break
        prev,cur=cur,nxt; seen.add(cur); loop.append(cur)
    loops.append(loop)
order=np.argsort([-len(l) for l in loops]); loops=[loops[i] for i in order]
say("loops=%s (expect [274, 247, 97, 18])" % [len(l) for l in loops])
HOLE=[i for i,l in enumerate(loops) if len(l)==247][0]
G1loc = load_pcd3(P + "/.scratch/pota162_repro/sfs_main/original_samples/SfS_pp/Breaklines/Pot_C_Piece_01_Breakline_1.pcd")
Gboth = np.vstack([G0loc, G1loc]) @ R.T + t
KG0g = KD(Gboth)
C0g = C0 @ R.T + t
Dcur = KG0g.query(C0g)[0]
near, far = Dcur<2.0, Dcur>5.0
# FAR&HOLE via all-loop segs (173 replica)
segs=[]; loop_of=[]
for i,l in enumerate(loops):
    ll=Vg[l]; s3=np.stack([ll,np.roll(ll,-1,axis=0)],axis=1); segs.append(s3); loop_of+=([i]*len(s3))
Sseg=np.vstack(segs); loop_of=np.array(loop_of)
A3a,B3a=Sseg[:,0],Sseg[:,1]; AB3=B3a-A3a; den3=(AB3**2).sum(axis=1)
AP3=C0g[:,None,:]-A3a[None,:,:]
tt3=np.clip((AP3*AB3[None,:,:]).sum(axis=2)/den3[None,:],0,1)
Cc3=A3a[None,:,:]+tt3[:,:,None]*AB3[None,:,:]
dd3=np.sqrt(((C0g[:,None,:]-Cc3)**2).sum(axis=2)); j3=dd3.argmin(1)
drop = np.zeros(len(C0g),bool); drop[np.where(far)[0][j3[far]==HOLE]] = True
say("S0 curate (replica attempt): n=364 NEAR=%d MID=%d FAR=%d drop=%d (173 recorded 86/187/91/73; loop-trace diverges, keep0 NOT reused)" % (int(near.sum()), int((~(near|far)).sum()), int(far.sum()), int(drop.sum())))
say("origin mapping: INDEPENDENT route -- match BAG rows to unclustered rows (tolerance), strip set recomputed exactly")
U = load_ply_x(P + "/.scratch/pota163_repro/inputs/Pot_C_Piece_01_unclustered.ply")
KU = KD(U)
Ug = U @ R.T + t
d_to_G0 = KD(G0).query(Ug)[0]
strip = np.where(d_to_G0 <= 2.5)[0]
say("strip recomputed=%d (173 recorded 612)" % len(strip))
Bloc = (BAG - t) @ R
drow, jrow = KU.query(Bloc)
say("BAG->U row match: maxdist=%.2e (premise: BAG rows are unclustered rows)" % float(drow.max()))
okm = drow < 1e-6
say("matched rows: %d/753" % int(okm.sum()))
R753 = set(jrow[okm].tolist())
Sset = set(strip.tolist())
s0only = R753 - Sset
say("BAG unclustered-rows=%d | in-strip=%d | S0-exclusive=%d" % (len(R753), len(R753 & Sset), len(s0only)))
say("stage ledger: estimator fires 364 (173) -> curation keeps 291 (173, FAR&HOLE drop 73, NOT recomputed here) -> snap replaces positions (labels re-derived, 291) ; strip 612 native unclustered rows carried (wall labels re-derived, 612) ; dedup 903->753 drops 150 rows (173)")
np.save(H+"/p175_urows.npy", np.array(sorted(R753)))
np.save(H+"/p175_strip.npy", strip)
jlab = plab
inS = np.array([r in Sset for r in jrow])
say("origin x parent (by final unclustered-row; S0-snapped-onto-strip reads as strip): strip-row dots=%d (inner=%d outer=%d fold=%d) | S0-exclusive dots=%d (inner=%d outer=%d fold=%d)" % (
  int(inS.sum()), int(((jlab==-1)&inS).sum()), int(((jlab==1)&inS).sum()), int(((jlab==0)&inS).sum()),
  int((~inS).sum()), int(((jlab==-1)&~inS).sum()), int(((jlab==1)&~inS).sum()), int(((jlab==0)&~inS).sum())))
log.close(); print("step11 done")
