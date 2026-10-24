import numpy as np, math, os, glob
AUTH="/data/gpfs/projects/punim2657/sfs_main/original_samples/SfS_pp"
OUT=os.path.dirname(os.path.abspath(__file__))+"/boundary_test.tsv"
def ref(pot,nn,lane):
    pts=[];st=False
    for line in open("%s/Breaklines/%s_Piece_%s_Breakline_%d.pcd"%(AUTH,pot,nn,lane),errors="ignore"):
        if not st:
            st=line.startswith("DATA"); continue
        v=line.split()
        if len(v)>=3: pts.append(v[:3])
    return np.array(pts,dtype=np.float64)
def maxgap(pts2d):
    th=np.arctan2(pts2d[:,1],pts2d[:,0]); th=np.sort(th)
    if len(th)<6: return 360.0
    gaps=np.diff(np.concatenate([th,[th[0]+2*math.pi]]))
    return math.degrees(gaps.max())
rows=[]
surf_files=sorted(glob.glob(AUTH+"/Surfaces/*_Surface_*.xyz"))
for sf in surf_files:
    base=os.path.basename(sf)[:-4]
    piece,surf=base.rsplit("_Surface_",1)
    pot,nn=piece.split("_Piece_")[0],piece.split("_Piece_")[1]
    S=np.loadtxt(sf,dtype=np.float64)
    P=S[:,0:3]; N=S[:,3:6]
    for lane in (0,1):
        D=ref(pot,nn,lane)
        if len(D)==0: continue
        step=max(1,len(D)//60); D=D[::step]
        gaps=[]
        for p in D:
            d=P-p; dd=np.einsum("ij,ij->i",d,d)
            j=int(dd.argmin()); q=P[j]; n=N[j]/max(np.linalg.norm(N[j]),1e-12)
            v=q-P; dist=np.einsum("ij,ij->i",v,v)
            nb=v[(dist<4.0)&(dist>1e-12)]
            if len(nb)<6: gaps.append(360.0); continue
            nb=nb-np.outer(nb@n,n)
            nn_=np.linalg.norm(nb,axis=1); nb=nb[nn_>1e-6]
            if len(nb)<6: gaps.append(360.0); continue
            gaps.append(maxgap(nb[:,0:2]))
        gaps=np.array(gaps)
        rows.append((piece,pot,nn,int(surf),lane,len(D),float(np.median(gaps)),float((gaps>100).mean())))
    print(base,"done",flush=True)
with open(OUT,"w") as f:
    f.write("piece\tpot\tnn\tsurface\tlane\tn\tmed_maxgap\tfrac_gap100\n")
    for r in rows: f.write("%s\t%s\t%s\t%d\t%d\t%d\t%.3f\t%.3f\n"%r)
g=np.array([r[6] for r in rows]); fr=np.array([r[7] for r in rows])
print("lanes=%d med_maxgap overall p10/p50/p90=%.1f/%.1f/%.1f  frac_lanes_med>100=%.3f  mean_frac_dots>100=%.3f"%(
    len(rows),np.percentile(g,10),np.percentile(g,50),np.percentile(g,90),(g>100).mean(),fr.mean()))
