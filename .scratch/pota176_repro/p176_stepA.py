import numpy as np, os
from scipy.spatial import cKDTree
from collections import Counter, defaultdict
H = ".scratch/pota176_repro"
I = os.path.join(H, "inputs"); R = os.path.join(H, "refs")
log = open(os.path.join(H, "p176_stepA.txt"), "w")
def say(s):
    print(s, flush=True); log.write(s + "\n")
def load_obj(path):
    V, F = [], []
    with open(path) as fh:
        for ln in fh:
            if ln.startswith("v "): V.append([float(x) for x in ln.split()[1:4]])
            elif ln.startswith("f "): F.append([int(x.split("/")[0]) - 1 for x in ln.split()[1:4]])
    return np.array(V), np.array(F, dtype=np.int64)
HDR = ('VERSION','FIELDS','SIZE','TYPE','COUNT','WIDTH','HEIGHT','VIEWPOINT','POINTS','DATA')
def load_pcd3(p):
    P = []
    for ln in open(p):
        s = ln.strip()
        if not s or s[0] == '#' or s.split()[0] in HDR: continue
        try: P.append(list(map(float, s.split()[:3])))
        except ValueError: continue
    return np.array(P)
for piece in ["01","02","03","04"]:
    ref = "Pot_C_Piece_%s" % piece
    Rdir = R if piece != "01" else ".scratch/pota162_repro/sfs_main/original_samples/SfS_pp/Breaklines"
    no = int(piece)
    V, F = load_obj("temp_download/Mesh/Pot_C/Pot_C_Piece_%s_Mesh_DS.obj" % piece)
    say("C%s mesh: %d v %d f" % (piece, len(V), len(F)))
    EC = Counter()
    for f in F:
        for a, b in [(f[0],f[1]),(f[1],f[2]),(f[2],f[0])]: EC[tuple(sorted((a,b)))] += 1
    nb = sum(1 for c in EC.values() if c == 1)
    say("C%s boundary edges=%d" % (piece, nb))
    bnd = [e for e, c in EC.items() if c == 1]
    adj = defaultdict(set)
    for a, b in bnd: adj[a].add(b); adj[b].add(a)
    seen = set(); loops = []
    for s in adj:
        if s in seen: continue
        cur, prev, loop = s, -1, [s]; seen.add(s)
        while True:
            nxts = [x for x in adj[cur] if x != prev]
            if not nxts: break
            nxt = nxts[0] if nxts[0] not in seen else (nxts[1] if len(nxts) > 1 and nxts[1] not in seen else None)
            if nxt is None: break
            if nxt == s: break
            prev, cur = cur, nxt; seen.add(cur); loop.append(cur)
    say("C%s loops=%s" % (piece, sorted([len(l) for l in loops], reverse=True)))
    T = np.loadtxt(os.path.join(I, "Pot_C_Piece_%d_T.txt" % no)); Rr, t = T[:3,:3], T[:3,3]
    Vg = V @ Rr.T + t
    for s in ["0","1"]:
        S = np.loadtxt(os.path.join(I, "Pot_C_Piece_%s_Surface_%s.xyz" % (piece, s)))
        say("C%s S%s n=%d" % (piece, s, len(S)))
        Xg = S[:,:3] @ Rr.T + t
        for b in ["0","1"]:
            G = load_pcd3(os.path.join(Rdir, ref + "_Breakline_%s.pcd" % b)) @ Rr.T + t
            KX = cKDTree(Xg)
            d = KX.query(G)[0]
            say("C%s S%s vs ORIG Bl_%s(n=%d): min=%.2f med=%.2f max=%.2f <2mm=%d/%d unc5=%d" % (
                piece, s, b, len(G), d.min(), float(np.median(d)), d.max(), int((d<2).sum()), len(G), int((d>5).sum())))
log.close(); print("saved stepA")
