import sys, math
import numpy as np

RUN = "/data/gpfs/projects/punim2657/SfSpp/runs/20261024-1223_0ab0935_p276-phase3a"
AUTHD = "/data/gpfs/projects/punim2657/sfs_main/original_samples/SfS_pp"
TAGS = [("C03","C03_diag","Pot_C","03"),("C01","C01_diag","Pot_C","01"),
        ("H02","H02_diag","Pot_H","02"),("H10","H10_diag","Pot_H","10")]

def read_dump(path):
    hdr={}; cl={}; xs=[]
    for line in open(path):
        if line.startswith("# npoints"):
            p=line[1:].split(); hdr=dict(zip(p[0::2],p[1::2]))
        elif line.startswith("# cluster"):
            p=line[1:].split(); d=dict(zip(p[0::2],p[1::2]))
            cl[int(d["cluster"])] = (int(d["size"]), int(d["surface"]))
        elif line.startswith("i "):
            continue
        else:
            v=line.split()
            if len(v)==6: xs.append(v)
    return hdr, cl, np.array(xs, dtype=np.float64)

def read_axis(path):
    v=[float(x) for x in open(path).read().split()]
    p0=np.array(v[0:3]); a=np.array(v[3:6]); a=a/np.linalg.norm(a); return p0,a

def read_ref(pot, nn, lane):
    path="%s/Breaklines/%s_Piece_%s_Breakline_%d.pcd" % (AUTHD, pot, nn, lane)
    pts=[]; started=False
    for line in open(path, errors="ignore"):
        if not started:
            if line.startswith("DATA"): started=True
            continue
        v=line.split()
        if len(v)>=3: pts.append(v[0:3])
    return np.array(pts, dtype=np.float64)

def nn_dist(A, B, chunk=256):
    out=np.empty(len(A))
    for i in range(0,len(A),chunk):
        d=A[i:i+chunk,None,:]-B[None,:,:]
        out[i:i+chunk]=np.sqrt((d*d).sum(-1)).min(1)
    return out

def region_stats(P, p0, a):
    d=P-p0; t=d@a; perp=d-np.outer(t,a)
    r=np.sqrt((perp*perp).sum(1))
    th=np.arctan2(perp[:,1],perp[:,0])
    b=((th+math.pi)/(2*math.pi)*36).astype(int)%36
    bins=[r[b==k] for k in range(36)]
    n10=sum(1 for x in bins if len(x)>=10)
    p95=np.array([np.percentile(x,95) if len(x)>=10 else np.nan for x in bins])
    ok=~np.isnan(p95)
    ringmask=np.zeros(len(P), dtype=bool)
    for k in range(36):
        if np.isnan(p95[k]): continue
        sel=(b==k)&(np.abs(r-p95[k])<1.0)
        ringmask|=sel
    edge_r=float(np.median(p95[ok])) if ok.any() else float("nan")
    edge_cv=float(np.std(p95[ok])/np.mean(p95[ok])) if ok.sum()>2 else float("nan")
    C=P.mean(0); Q=P-C
    ev=np.linalg.eigvalsh(Q.T@Q)
    l3l1=float(max(ev[0],0)/ev[2]) if ev[2]>0 else float("nan")
    return dict(n=len(P), r5=float(np.percentile(r,5)), r50=float(np.percentile(r,50)),
                r95=float(np.percentile(r,95)), t5=float(np.percentile(t,5)),
                t50=float(np.percentile(t,50)), t95=float(np.percentile(t,95)),
                axsp=float(np.percentile(t,95)-np.percentile(t,5)),
                bins10=n10, edge_r=edge_r, edge_cv=edge_cv, l3l1=l3l1, ring=ringmask)

print("tag clu kept size |dotax| l3l1 axsp r50 bins10 edge_r edge_cv FLAG ref0_med ref1_med ref0_edge ref1_edge")
for tag, sub, pot, nn in TAGS:
    import glob
    dump=glob.glob("%s/out/%s/mergeDiag276_*.txt" % (RUN, sub))[0]
    hdr, cl, arr = read_dump(dump)
    p0, a = read_axis("%s/stage/%s/Dataset/Axes/%s_Piece_%s_Axis.xyz" % (RUN, sub, pot, nn))
    ref=[read_ref(pot, nn, 0), read_ref(pot, nn, 1)]
    N=int(hdr["npoints"])
    print("# %s npoints=%s nclusters=%s refn=%d/%d" % (tag, N, hdr["nclusters"], len(ref[0]), len(ref[1])))
    lab=arr[:,1].astype(int); P=arr[:,2:5]
    for c,(size,surf) in sorted(cl.items()):
        if size < 200: continue
        M=P[lab==c]
        st=region_stats(M, p0, a)
        C=M.mean(0); Q=M-C
        n=np.linalg.svd(Q, full_matrices=False)[2][2]
        dot=abs(float(n@a))
        flag = (st["n"]>=360 and st["bins10"]==36 and dot>0.95 and st["l3l1"]<=0.02
                and st["edge_cv"]<=0.15 and st["axsp"]<=0.3*st["r50"])
        d0=nn_dist(ref[0],M); d1=nn_dist(ref[1],M)
        Rm=M[st["ring"]]
        e0=np.median(nn_dist(ref[0],Rm)) if len(Rm) else float("nan")
        e1=np.median(nn_dist(ref[1],Rm)) if len(Rm) else float("nan")
        print("%-3s %3d %4d %6d %6.3f %6.4f %6.1f %5.1f %5d %6.1f %6.3f %d %7.3f %7.3f %7.3f %7.3f" % (
            tag, c, surf, size, dot, st["l3l1"], st["axsp"], st["r50"], st["bins10"], st["edge_r"],
            st["edge_cv"], 1 if flag else 0, np.median(d0), np.median(d1), e0, e1))