import numpy as np
hdr=None
def ang(a,b):
    c=abs(float(np.dot(a,b))/(np.linalg.norm(a)*np.linalg.norm(b))); return float(np.degrees(np.arccos(min(1.0,c))))
for case in ("PA07_t0/s0","PA07_t1/s0","PA08_t0/s0","PA08_t1/s0","PA01_t0/s0"):
    p="out/a2/x/%s/candidates3.tsv"%case
    L=open(p).read().splitlines()
    h=L[0].split("\t"); ix={k:i for i,k in enumerate(h)}
    reps=[]
    for ln in L[1:]:
        f=ln.split("\t")
        if f[ix["is_cluster_rep"]]!="1": continue
        reps.append(dict(cl=int(f[ix["cluster"]]), max_pt=float(f[ix["max_pt"]]),
                         c0=float(f[ix["c0_pt"]]), c1=float(f[ix["c1_pt"]]),
                         d=np.array([float(f[ix["dx"]]),float(f[ix["dy"]]),float(f[ix["dz"]])]),
                         rel=[float(x) for x in f[ix["ang_rel_all"]].split()],
                         size=None))
    # sizes from reps3
    S=open("out/a2/x/%s/reps3.tsv"%case).read().splitlines()[1:]
    for ln in S:
        f=ln.split("\t"); cl=int(f[0])
        for r in reps:
            if r["cl"]==cl: r["size"]=int(f[1])
    reps.sort(key=lambda r:r["max_pt"])
    b=reps[0]
    print("==",case," best cl=%d size=%s max_pt=%.1f rel=%s"%(b["cl"],b["size"],b["max_pt"],[round(x,1) for x in b["rel"]]))
    for r in reps:
        a2b=ang(r["d"],b["d"])
        print("   cl%-2d size=%4s max_pt=%7.1f c0=%6.1f c1=%6.1f ang2best=%5.1f rel=%s"%(
            r["cl"],r["size"],r["max_pt"],r["c0"],r["c1"],a2b,[round(x,1) for x in r["rel"]]))
