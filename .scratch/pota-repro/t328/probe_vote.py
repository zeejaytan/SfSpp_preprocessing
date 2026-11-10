
import numpy as np, os, json
from scipy.spatial import cKDTree
IN='artifacts/pota328/in'
OUT='artifacts/pota328/probe'

def load_ply(p):
    rows=[]; hdr=True
    with open(p) as f:
        for ln in f:
            if hdr:
                if ln.strip()=='end_header': hdr=False
                continue
            t=ln.split()
            if len(t)>=6: rows.append([float(x) for x in t[:7]] if len(t)>=7 else [float(x) for x in t[:6]])
    a=np.array(rows)
    return a[:,:3], a[:,3:6]

def load_axis(p):
    v=np.array([float(x) for x in open(p).read().split()[:6]])
    c=v[:3]; d=v[3:]; d/=np.linalg.norm(d); return c,d

def load_T(p):
    return np.loadtxt(p)

def infrac(P,N,c,d):
    # foot of P on line (c,d)
    t=(P-c)@d
    cp=c+t[:,None]*d
    return float(np.mean(np.sum((cp-P)*N,axis=1)>0))

def girth(P,N,c,d):
    v=P-c; v-= (v@d)[:,None]*d
    r=np.linalg.norm(v,axis=1,keepdims=True)
    rr=np.where(r<1e-9,1,r)
    g=np.cross(np.broadcast_to(d,(len(P),3)), v/rr)
    gg=np.linalg.norm(g,axis=1,keepdims=True); gg=np.where(gg<1e-9,1,gg)
    return np.sum(N*(g/gg),axis=1)

def orient(Pa,Na,Pb):
    tb=cKDTree(Pb)
    _,j=tb.query(Pa,k=1)
    v=Pb[j]-Pa
    s=np.sum(v*Na,axis=1)
    return float(np.median(np.sign(s))), float(np.mean(s>0))

def curv(P,N,k=60,cap=600):
    n=len(P)
    stride=max(1,n//cap)
    idx=np.arange(0,n,stride)[:cap]
    tree=cKDTree(P)
    out=[]
    for i in idx:
        nbr=tree.query(P[i],k=min(k,n))[1]
        if len(nbr)<10: continue
        q=P[nbr]-P[i]
        nv=N[i]/ (np.linalg.norm(N[i]) or 1)
        # tangent frame
        a=np.array([1.0,0,0]) if abs(nv[0])<0.9 else np.array([0,1.0,0])
        t1=np.cross(nv,a); t1/=np.linalg.norm(t1); t2=np.cross(nv,t1)
        u=q@t1; v=q@t2; w=q@nv
        X=np.column_stack([0.5*u*u, u*v, 0.5*v*v, u, v])
        c,_,_,_=np.linalg.lstsq(X,w,rcond=None)
        A,B,C=c[0],c[1],c[2]
        tr=(A+C)/2; df=np.sqrt(((A-C)/2)**2+B*B)
        out.append(max(abs(tr+df),abs(tr-df)))
    return float(np.median(out))

rows=[]
for k in range(1,10):
    P0,N0=load_ply(f'{IN}/geom/Juglet_Piece_{k}.S0')
    P1,N1=load_ply(f'{IN}/geom/Juglet_Piece_{k}.S1')
    cg,dg=load_axis(f'{IN}/gt/Juglet_Piece_{k}_Axis.xyz')
    cd,dd=load_axis(f'{IN}/dsaxis/Juglet_Piece_{k}_Axis.xyz')
    O0,fr0=orient(P0,N0,P1); O1,fr1=orient(P1,N1,P0)
    af_ds=float(np.mean(np.abs(girth(np.vstack([P0,P1]),np.vstack([N0,N1]),cd,dd))<0.3))
    af_gt=float(np.mean(np.abs(girth(np.vstack([P0,P1]),np.vstack([N0,N1]),cg,dg))<0.3))
    # pre-flip normals (code's vote frame): flip happened if O>0
    flip = O0>0
    M0 = -N0 if flip else N0
    M1 = -N1 if flip else N1
    A=(P0,M0) if len(P0)>=len(P1) else (P1,M1)
    B=(P1,M1) if len(P0)>=len(P1) else (P0,M0)
    aFirst = 0 if len(P0)>=len(P1) else 1
    f0=infrac(A[0],A[1],cd,dd); f1=infrac(B[0],B[1],cd,dd)
    n0,n1=len(A[0]),len(B[0])
    satA=f0*n0+(1-f1)*n1; satB=(1-f0)*n0+f1*n1
    pick = aFirst if satA>satB else 1-aFirst   # predicted slot0 index into exported S
    z=(satA-satB)/(0.5*np.sqrt(n0+n1))
    # curated vote: orientation-corrected normals
    g0=infrac(A[0],A[1],cd,dd); g1=infrac(B[0],B[1],cd,dd)
    # geometry: curvature
    k0=curv(P0,N0); k1=curv(P1,N1)
    geo = 0 if k0>k1 else 1
    rows.append(dict(piece=k,n0=len(P0),n1=len(P1),orient_O=O0,orient_frac=fr0,
        axisfit_ds=af_ds,axisfit_gt=af_gt,flip=bool(flip),
        infrac_A=round(f0,4),infrac_B=round(f1,4),satA=round(satA,2),satB=round(satB,2),
        z=round(float(z),2),vote_slot0=pick, kappa0=round(k0,4),kappa1=round(k1,4),
        kratio=round(max(k0,k1)/min(k0,k1),3), geo_slot0=geo))
    print(json.dumps(rows[-1]))
json.dump(rows,open(f'{OUT}/vote_model.json','w'),indent=1)
