import numpy as np, math
AUTH="/data/gpfs/projects/punim2657/sfs_main/original_samples/SfS_pp"
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
print("piece lane n r_p5 r_p50 r_p95 r_min r_max frac_within_1mm_of_r95")
for pot,nn,surf,lane in [("Pot_C","03",1,1),("Pot_J","03",1,1),("Pot_A","01",0,0),("Pot_A","01",1,1),("Pot_C","03",0,0),("Pot_J","03",0,0)]:
    S=np.loadtxt("%s/Surfaces/%s_Piece_%s_Surface_%d.xyz"%(AUTH,pot,nn,surf))[:,0:3]
    p0,a=axis(pot,nn); D=ref(pot,nn,lane)
    def rad(P):
        d=P-p0; t=d@a; perp=d-np.outer(t,a); return np.sqrt((perp*perp).sum(1))
    rd=rad(D); rs=rad(S); r95=np.percentile(rs,95)
    print("%s_%s %d %4d %7.2f %7.2f %7.2f %7.2f %7.2f %6.3f" % (pot.replace("Pot_",""),nn,lane,len(D),
        np.percentile(rd,5),np.median(rd),np.percentile(rd,95),rd.min(),rd.max(),(np.abs(rd-r95)<1.0).mean()))
