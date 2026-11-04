import sys,glob,os,numpy as np,re
C="/data/gpfs/projects/punim2657/SfSpp/runs/20261105-0450_9c5eec2_t305-e2e-a-smoke/out"
def load_obj(p):
    pts=[]
    for line in open(p,errors="ignore"):
        if line.startswith("v "):
            q=line.split(); pts.append([float(q[1]),float(q[2]),float(q[3])])
    return np.array(pts)
def edges(rd):
    return np.vstack([np.loadtxt(f)[:,:3] for f in glob.glob(rd+"/*_Edgeline_*.xyz")])
for arm in ("OOR1","MMR1"):
    rd=os.path.join(C,arm); E=edges(rd)
    print("==",arm,"edges",E.shape)
    for i in (1,7,8):
        f=glob.glob(rd+"/*_OBJ_%d.obj"%i)
        if not f: continue
        a=load_obj(f[0]); s=a[::max(1,len(a)//300)]
        T=np.loadtxt(rd+"/T_%dto_%d.txt"%(i-1,i-1))
        b=s@T[:3,:3].T+T[:3,3]
        # nearest edge distance
        d=np.sqrt(((b[:,None,:]-E[None,::7,:])**2).sum(-1)).min(1)
        print("  piece %d: median dist transformed->edges %.2f mm  (raw z range %.1f..%.1f)"%(i,np.median(d),a[:,2].min(),a[:,2].max()))
