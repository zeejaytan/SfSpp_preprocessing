import numpy as np, math
AUTH="/data/gpfs/projects/punim2657/sfs_main/original_samples/SfS_pp"
def read_xyz(p):
    return np.loadtxt(p, dtype=np.float64)
def axis(pot,nn):
    v=[float(x) for x in open("%s/Axes/%s_Piece_%s_Axis.xyz"%(AUTH,pot,nn)).read().split()]
    return np.array(v[0:3]), np.array(v[3:6])/np.linalg.norm(v[3:6])
def ref(pot,nn,lane):
    pts=[];st=False
    for line in open("%s/Breaklines/%s_Piece_%s_Breakline_%d.pcd"%(AUTH,pot,nn,lane),errors="ignore"):
        if not st:
            st=line.startswith("DATA"); continue
        v=line.split()
        if len(v)>=3: pts.append(v[:3])
    return np.array(pts,dtype=np.float64)
def nnd(A,B,chunk=256):
    out=np.empty(len(A)); arg=np.empty(len(A),dtype=int)
    for i in range(0,len(A),chunk):
        d=A[i:i+chunk,None,:]-B[None,:,:]
        dd=np.sqrt((d*d).sum(-1)); out[i:i+chunk]=dd.min(1); arg[i:i+chunk]=dd.argmin(1)
    return out,arg
def rad(P,p0,a):
    d=P-p0; t=d@a; perp=d-np.outer(t,a); return np.sqrt((perp*perp).sum(1)), t
cases=[("Pot_A","01",0,0),("Pot_A","01",1,1),("Pot_C","03",1,1),("Pot_C","03",0,0),("Pot_J","03",1,1),("Pot_J","03",0,0)]
print("piece surf lane ndot dot_r_med surf_r50 surf_r95 surf_rmax d_med d_p90 d_max nearest_r_med nearest_r_p90")
for pot,nn,surf,lane in cases:
    S=read_xyz("%s/Surfaces/%s_Piece_%s_Surface_%d.xyz"%(AUTH,pot,nn,surf))[:,0:3]
    p0,a=axis(pot,nn); Rf=ref(pot,nn,lane)
    rs,_=rad(S,p0,a); rd,_=rad(Rf,p0,a)
    d,arg=nnd(Rf,S)
    print("%s %s_%s  %d %4d %8.3f %8.2f %8.2f %8.2f %7.3f %7.3f %7.3f %8.2f %8.2f" % (
        pot.replace("Pot_",""), nn, surf, lane, len(Rf), np.median(rd), np.median(rs), np.percentile(rs,95),
        rs.max(), np.median(d), np.percentile(d,90), d.max(), np.median(rs[arg]), np.percentile(rs[arg],90)))
