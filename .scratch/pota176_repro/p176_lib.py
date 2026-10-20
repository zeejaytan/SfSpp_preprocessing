import numpy as np, os
from scipy.spatial import cKDTree
from collections import Counter, defaultdict
HDR = ('VERSION','FIELDS','SIZE','TYPE','COUNT','WIDTH','HEIGHT','VIEWPOINT','POINTS','DATA')
def load_obj(path):
    V, F = [], []
    with open(path) as fh:
        for ln in fh:
            if ln.startswith("v "): V.append([float(x) for x in ln.split()[1:4]])
            elif ln.startswith("f "): F.append([int(x.split("/")[0]) - 1 for x in ln.split()[1:4]])
    return np.array(V), np.array(F, dtype=np.int64)
def load_pcd3(p):
    P = []
    for ln in open(p):
        s = ln.strip()
        if not s or s[0] == '#' or s.split()[0] in HDR: continue
        try: P.append(list(map(float, s.split()[:3])))
        except ValueError: continue
    return np.array(P)
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
def mesh_loops(V, F):
    EC = Counter()
    for f in F:
        for a, b in [(f[0],f[1]),(f[1],f[2]),(f[2],f[0])]: EC[tuple(sorted((a,b)))] += 1
    bnd = [e for e, c in EC.items() if c == 1]
    adj = defaultdict(set)
    for a, b in bnd: adj[a].add(b); adj[b].add(a)
    seen = set(); loops = []
    for s in adj:
        if s in seen: continue
        cur, prev, loop = s, -1, [s]; seen.add(s)
        while True:
            nxts = [x for x in adj[cur] if x != prev]
            if len(nxts) == 0: break
            nxt = nxts[0] if nxts[0] not in seen else (nxts[1] if len(nxts) > 1 and nxts[1] not in seen else None)
            if nxt is None: break
            if nxt == s: break
            prev, cur = cur, nxt; seen.add(cur); loop.append(cur)
        loops.append(loop)
    order = sorted(range(len(loops)), key=lambda i: -len(loops[i]))
    return [loops[i] for i in order]
def code_r(X):
    bb = np.stack([X.min(0), X.max(0)]); be = bb[1] - bb[0]
    s0, s1 = be[0], be[1]
    if s1 > s0: s0, s1 = s1, s0
    if be[2] > s0: s1, s0 = s0, be[2]
    elif be[2] > s1: s1 = be[2]
    sp = float(np.sqrt((s0*s1)/max(100, len(X))))
    return float(max(1.0, min(15.0, sp*6.0)))
def pcl_flags(Xe, Ne, r, TH=0.6*np.pi):
    Kq = cKDTree(Xe)
    ball = Kq.query_ball_point(Xe, r)
    flags = np.zeros(len(Xe), dtype=bool)
    for i in range(len(Xe)):
        nb = [j for j in ball[i] if j != i]
        if len(nb) < 3: continue
        n = Ne[i]
        VV = Xe[nb]-Xe[i]
        VV = VV - np.outer(VV@n, n)
        up = np.array([0.0,0.0,1.0]) if abs(n[2]) < 0.9 else np.array([1.0,0.0,0.0])
        u = up - (up@n)*n; u = u/np.linalg.norm(u)
        v = np.cross(n, u)
        ang = np.sort(np.arctan2(VV@v, VV@u))
        dif = np.diff(ang)
        wrap = 2*np.pi - (ang[-1]-ang[0])
        if max(dif.max(), wrap) > TH: flags[i] = True
    return flags
def walk_m144(T):
    W = len(T)
    X32 = T.astype(np.float32); kk = np.array([X32[i].tobytes() for i in range(W)])
    cvis = {kk[0]: 0}; cseq = [0]; cur = 0
    for t in range(1, W):
        dd = np.sqrt(((T - T[cur]) ** 2).sum(-1))
        idx = np.argsort(dd, kind="stable")[:34]
        if t == 1:
            nxt = int(idx[1]); cseq.append(nxt); cvis[kk[nxt]] = 1; cur = nxt; continue
        unv = [int(j) for j in idx if kk[int(j)] not in cvis]
        if not unv: break
        j = int(unv[0]); cseq.append(j); cvis[kk[j]] = len(cseq)-1; cur = j
    Lg = T[np.array(cseq)]
    gsteps = np.sqrt(((Lg[1:]-Lg[:-1])**2).sum(-1))
    BAND = float(gsteps.max()) if len(gsteps) else 0.0
    seq = list(cseq); cvm = dict(cvis); cur = seq[-1]; guard = 0; HALT = ""
    retreats = 0; forwards = 0
    while len(set(seq)) < W and guard < 60000:
        guard += 1
        dd = np.sqrt(((T - T[cur]) ** 2).sum(-1))
        idx = np.argsort(dd, kind="stable")[:34]
        sset = set(seq); nxt = None
        for j in idx:
            j = int(j)
            if j not in sset and float(dd[j]) >= 1.0: nxt = j; break
        if nxt is not None:
            seq.append(nxt); cvm.setdefault(kk[nxt], len(seq)-1); cur = nxt; continue
        dc = np.sqrt(((T - T[cur])**2).sum(-1))
        order = np.argsort(dc, kind="stable")
        seen = {}
        for p, s_ in enumerate(seq):
            if int(s_) not in seen: seen[int(s_)] = p
        best = None
        for s_ in order:
            s_ = int(s_)
            if s_ == cur: continue
            ddx = np.sqrt(((T - T[s_])**2).sum(-1)); iix = np.argsort(ddx, kind="stable")[:34]
            if any(int(j) not in sset and float(ddx[int(j)]) >= 1.0 for j in iix): best = s_; break
        if best is not None and float(dc[best]) <= BAND:
            retreats += 1; seq.append(best); cur = best; continue
        if best is not None:
            HALT = "HALT %.2f>%.2f" % (float(dc[best]), BAND); break
        mask = np.array([kk[i] in cvm for i in range(W)])
        if mask.all(): break
        ddx = dc.copy(); ddx[mask] = np.inf; nx = int(np.argmin(ddx))
        forwards += 1; seq.append(nx); cvm[kk[nx]] = len(seq)-1; cur = nx
    seq = np.array(seq, dtype=int)
    L = T[seq]
    bst = np.sqrt(((L[1:]-L[:-1])**2).sum(-1))
    return seq, cseq, BAND, HALT, retreats, forwards, bst
def gate_walk(L, Og):
    D = np.sqrt(((L[:,None,:]-Og[None,:,:])**2).sum(-1)).min(1)
    DO = np.sqrt(((Og[:,None,:]-L[None,:,:])**2).sum(-1)).min(1)
    bst = np.sqrt(((L[1:]-L[:-1])**2).sum(-1))
    return dict(seqlen=len(L), med=float(np.median(D)), cov2=float((D<2).mean()*100),
        gaps5=int((bst>5).sum()), maxstep=float(bst.max()) if len(bst) else 0.0,
        origcov=int((DO<2).sum()), uncovered=int((DO>5).sum()),
        over25=sorted([float(x) for x in bst if x > 25]))
def topo(Bag, sq, Og):
    C0 = Og.mean(0); Uu, Ss, Vt = np.linalg.svd(Og-C0, full_matrices=False); e1, e2, nn = Vt[0], Vt[1], Vt[2]
    A3 = Og[:-1]; AB = Og[1:]-Og[:-1]; Ll = np.linalg.norm(AB,axis=1); Ll[Ll==0]=1; ttv = AB/Ll[:,None]
    Lw = Bag[np.array(sq)]
    w = Lw[:,None,:]-A3[None,:,:]; s = (w*ttv[None,:,:]).sum(-1).clip(0,1)
    proj = A3[None,:,:]+s[:,:,None]*ttv[None,:,:]; r = Lw[:,None,:]-proj
    dd = np.linalg.norm(r,axis=2); j = np.argmin(dd,axis=1)
    rr = r[np.arange(len(Lw)),j]; tj = ttv[j]
    sgn = np.sign(np.cross(tj,rr).dot(nn)); mag = dd[np.arange(len(Lw)),j]
    q = [x for x,m in zip(sgn,np.abs(mag)>=1.0) if m]
    fl = sum(1 for a,b in zip(q,q[1:]) if a != b)
    P2 = np.c_[ (Lw-C0).dot(e1),(Lw-C0).dot(e2)]
    S = [(P2[i],P2[i+1]) for i in range(len(P2)-1)]; nc = 0
    def c2(a,b): return a[0]*b[1]-a[1]*b[0]
    for i in range(len(S)):
        for k in range(i+2,len(S)):
            a,b = S[i]; c,dd2 = S[k]; rv = b-a; sv = dd2-c; den = c2(rv,sv)
            if abs(den) < 1e-12: continue
            t1 = c2(c-a,sv)/den; u1 = c2(c-a,rv)/den
            if 0 < t1 < 1 and 0 < u1 < 1: nc += 1
    dseg = P2[1:]-P2[:-1]; ang = np.arccos(np.clip((dseg[:-1]*dseg[1:]).sum(-1)/np.maximum(np.linalg.norm(dseg[:-1],axis=1)*np.linalg.norm(dseg[1:],axis=1),1e-12),-1,1))*180/np.pi
    return len(q), fl, nc, int((ang>90).sum())

def pt_tri_dist(P, V, F, chunk=2000):
    A = V[F[:,0]]; B = V[F[:,1]]; C = V[F[:,2]]
    AB = B-A; AC = C-A
    out_d = np.full(len(P), np.inf); out_j = np.zeros(len(P), dtype=np.int64)
    for s in range(0, len(P), chunk):
        Pc = P[s:s+chunk]
        AP = Pc[:,None,:]-A[None,:,:]
        d1 = (AP*AB[None,:,:]).sum(-1); d2 = (AP*AC[None,:,:]).sum(-1)
        v = Pc[:,None,:]-A[None,:,:]
        d3 = (AB[None,:,:]*AB[None,:,:]).sum(-1); d4 = (AB[None,:,:]*AC[None,:,:]).sum(-1)
        d5 = (AC[None,:,:]*AC[None,:,:]).sum(-1)
        denom = d3*d5-d4*d4
        denom = np.where(np.abs(denom) < 1e-18, 1e-18, denom)
        vb = (d5*d1-d4*d2)/denom; wb = (d3*d2-d4*d1)/denom
        inb = (vb >= 0)&(wb >= 0)&(vb+wb <= 1)
        Q = A[None,:,:]+AB[None,:,:]*vb[:,:,None]+AC[None,:,:]*wb[:,:,None]
        d_in = np.where(inb, np.linalg.norm(Pc[:,None,:]-Q, axis=2), np.inf)
        eAB0 = A[None,:,:]; eAB1 = B[None,:,:]
        t = np.clip(((Pc[:,None,:]-eAB0)*AB[None,:,:]).sum(-1)/np.maximum((AB*AB).sum(-1),1e-18)[None,:], 0, 1)
        d_ab = np.linalg.norm(Pc[:,None,:]-(eAB0+t[:,:,None]*AB[None,:,:]), axis=2)
        t2 = np.clip(((Pc[:,None,:]-B[None,:,:])*(C-B)[None,:,:]).sum(-1)/np.maximum(((C-B)*(C-B)).sum(-1),1e-18)[None,:], 0, 1)
        d_bc = np.linalg.norm(Pc[:,None,:]-(B[None,:,:]+t2[:,:,None]*(C-B)[None,:,:]), axis=2)
        t3 = np.clip(((Pc[:,None,:]-C[None,:,:])*(A-C)[None,:,:]).sum(-1)/np.maximum(((A-C)*(A-C)).sum(-1),1e-18)[None,:], 0, 1)
        d_ca = np.linalg.norm(Pc[:,None,:]-(C[None,:,:]+t3[:,:,None]*(A-C)[None,:,:]), axis=2)
        d_all = np.minimum(np.minimum(d_in, d_ab), np.minimum(d_bc, d_ca))
        j = d_all.argmin(axis=1)
        out_d[s:s+chunk] = d_all[np.arange(len(Pc)), j]; out_j[s:s+chunk] = j
    return out_d, out_j

def wall_labels(V, F):
    Tc = (V[F[:,0]]+V[F[:,1]]+V[F[:,2]])/3.0
    e1 = V[F[:,1]]-V[F[:,0]]; e2 = V[F[:,2]]-V[F[:,0]]
    N = np.cross(e1, e2); N = N/np.maximum(np.linalg.norm(N,axis=1,keepdims=True),1e-12)
    C = V.mean(0); Rv = Tc - C; Rn = Rv/np.maximum(np.linalg.norm(Rv,axis=1,keepdims=True),1e-12)
    return (N*Rn).sum(-1)
