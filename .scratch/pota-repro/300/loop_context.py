import json
from collections import defaultdict
import numpy as np
from pathlib import Path
from scipy.spatial import cKDTree
ROOT = Path(r"C:/PR/SfSpp_preprocessing/artifacts/pota300"); IN = ROOT/"inputs"/"stage"; CORPUS = IN/"corpus"

def load_obj(path):
    vs, fs = [], []
    for line in open(path, "r", errors="ignore"):
        if line.startswith("v "): vs.append([float(x) for x in line.split()[1:4]])
        elif line.startswith("f "):
            ix = [int(t.split("/")[0]) for t in line.split()[1:]]
            for k in range(1,len(ix)-1): fs.append([ix[0],ix[k],ix[k+1]])
    return np.asarray(vs,float), np.asarray(fs,np.int64)-1

def load_axis(p):
    a = np.loadtxt(p).ravel(); return a[:3], a[3:6]/np.linalg.norm(a[3:6])

def loops_of(V,F):
    cnt = defaultdict(int)
    for tri in F:
        for a,b in ((tri[0],tri[1]),(tri[1],tri[2]),(tri[2],tri[0])): cnt[(min(a,b),max(a,b))]+=1
    be = {(a,b) for (a,b),c in cnt.items() if c==1}
    adj = defaultdict(set)
    for a,b in be: adj[a].add(b); adj[b].add(a)
    used, out = set(), []
    for a,b in sorted(be):
        if a in used: continue
        loop=[a]; used.add(a); cur,prev=b,a
        while cur!=a:
            if cur in used: break
            loop.append(cur); used.add(cur)
            nx=[x for x in adj[cur] if x!=prev and x not in used] or [x for x in adj[cur] if x!=prev]
            if not nx: break
            prev,cur=cur,nx[0]
        out.append(loop)
    return sorted(out, key=lambda l:-len(l))

V,F = load_obj(CORPUS/"Mesh"/"Pot_C_Piece_01_Mesh_DS.obj")
o,d = load_axis(IN/"axes"/"Pot_C_Piece_01_Axis.xyz")
S0 = np.loadtxt(IN/"prep_geom"/"Pot_C_Piece_01.S0.xyz", usecols=(0,1,2))
S1 = np.loadtxt(IN/"prep_geom"/"Pot_C_Piece_01.S1.xyz", usecols=(0,1,2))
L = loops_of(V,F)
cent = [V[np.asarray(l)].mean(0) for l in L]

# adjacent faces per loop -> mean normal vs radial direction
edge_faces = defaultdict(list)
for fi,tri in enumerate(F):
    for a,b in ((tri[0],tri[1]),(tri[1],tri[2]),(tri[2],tri[0])): edge_faces[(min(a,b),max(a,b))].append(fi)
n = np.cross(V[F[:,1]]-V[F[:,0]], V[F[:,2]]-V[F[:,0]]); nn=np.linalg.norm(n,axis=1,keepdims=True); nn[nn==0]=1; n=n/nn
radial = lambda P: np.asarray([ (lambda r: r/np.linalg.norm(r))(v-o-np.dot(v-o,d)*d) for v in P ])

# coverage
t0,t1 = cKDTree(S0), cKDTree(S1)
d0,_ = t0.query(V); d1,_ = t1.query(V); dmin = np.minimum(d0,d1)
unc = V[dmin > 2.0]
print("uncovered mesh vertices (>2mm from either cloud): %d of %d (%.1f%%)" % (len(unc), len(V), 100*len(unc)/len(V)))
print("uncovered bbox  ", np.round(np.ptp(unc,axis=0),1), " centroid", np.round(unc.mean(0),1))
print("mesh centroid   ", np.round(V.mean(0),1))

def bl0(path):
    rows=[]; seen=False
    for line in open(path,"r",errors="ignore"):
        if not seen:
            if line.startswith("DATA"): seen=True
            continue
        t=line.split()
        if len(t)>=3:
            try: rows.append([float(x) for x in t[:3]])
            except ValueError: pass
    return np.asarray(rows,float)
ours = bl0(IN/"prep_geom"/"Pot_C_Piece_01.Bl0.pcd")
auth = bl0(CORPUS/"Breaklines"/"Pot_C_Piece_01_Breakline_0.pcd")

print("\nloop  nv   centroid              r_med  rng          nbr_dot_to_loop(min/med)   ourBl0      authBl0")
for k,l in enumerate(L):
    P = V[np.asarray(l)]
    r = np.linalg.norm((P-o)-np.outer((P-o)@d,d),axis=1)
    fi = set()
    for i in range(len(l)):
        a,b = l[i], l[(i+1)%len(l)]
        fi.update(edge_faces.get((min(a,b),max(a,b)),[]))
    fi = sorted(fi)
    rn = radial(P.mean(0)[None,:])[0]
    dotn = float(np.mean([n[i]@rn for i in fi])) if fi else float('nan')
    tl = cKDTree(P)
    do,_ = tl.query(ours); da,_ = tl.query(auth)
    print("%d %5d %s  %5.1f %s  dot(n,radial)=%+.2f   %.1f/%.1f  %.1f/%.1f" % (
        k, len(l), np.round(P.mean(0),1), np.median(r), np.round([r.min(),r.max()],1), dotn,
        do.min(), np.median(do), da.min(), np.median(da)))
print("\nour Bl0 dots:", len(ours), " auth Bl0 dots:", len(auth))
