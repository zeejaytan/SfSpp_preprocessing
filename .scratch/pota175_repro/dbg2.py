import numpy as np
from scipy.spatial import cKDTree as KD
from collections import Counter, defaultdict
P = "C:/PR/SfSpp_preprocessing"
def load_obj(path):
    V, F = [], []
    with open(path) as fh:
        for ln in fh:
            if ln.startswith("v "): V.append([float(x) for x in ln.split()[1:4]])
            elif ln.startswith("f "): F.append([int(x.split("/")[0]) - 1 for x in ln.split()[1:4]])
    return np.array(V), np.array(F, dtype=np.int64)
V, F = load_obj(P + "/temp_download/Mesh/Pot_C/Pot_C_Piece_01_Mesh_DS.obj")
TF = np.loadtxt(P + "/.scratch/pota115_staging/inputs/TF.txt")
R, t = TF[:3,:3], TF[:3,3]
Vg = V.dot(R.T) + t
EC = Counter()
for f in F:
    for a2,b2 in [(f[0],f[1]),(f[1],f[2]),(f[2],f[0])]: EC[tuple(sorted((a2,b2)))] += 1
bnd = [e for e,c in EC.items() if c==1]
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
print("loops", [len(l) for l in loops], flush=True)
print("loop0 head", loops[0][:5], "loop1 head", loops[1][:5], flush=True)
