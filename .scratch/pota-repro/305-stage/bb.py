import sys,glob,re,numpy as np,os
def bb(files, mode):
    lo=np.full(3,1e9); hi=np.full(3,-1e9); n=0
    for f in files:
        pts=[]
        for line in open(f,errors="ignore"):
            if mode=="obj" and line.startswith("v "):
                p=line.split(); pts.append([float(p[1]),float(p[2]),float(p[3])])
            elif mode=="xyz":
                q=line.split()
                if len(q)>=3:
                    try: pts.append([float(q[0]),float(q[1]),float(q[2])])
                    except: pass
        if not pts: continue
        a=np.array(pts); lo=np.minimum(lo,a.min(0)); hi=np.maximum(hi,a.max(0)); n+=len(a)
    return lo,hi,n
for rd in sys.argv[1:]:
    print("==",rd)
    print(" obj  ", bb(glob.glob(rd+"/*_OBJ_*.obj"),"obj"))
    print(" edge ", bb(glob.glob(rd+"/*_Edgeline_*.xyz"),"xyz"))
    t=sorted(glob.glob(rd+"/T_*.txt"))
    if t:
        print(" T0:"); print(open(t[0]).read()[:400])
