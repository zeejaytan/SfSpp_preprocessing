import numpy as np
def load(p):
    d=[]
    f=open(p)
    for ln in f:
        s=ln.split()
        if len(s)>=3:
            try: d.append([float(x) for x in s[:3]])
            except ValueError: pass
    return np.array(d)
P12='C:/PR/SfSpp_preprocessing/.scratch/pota222/p12/'
box=np.array([[33,54],[-28,10],[432,474]])
for tag in ['at8','at4p5']:
    for nm in ['S0','S1']:
        s=load(P12+'p12_%s_%s.xyz'%(nm,tag))
        m=(s[:,0]>=box[0,0])&(s[:,0]<=box[0,1])&(s[:,1]>=box[1,0])&(s[:,1]<=box[1,1])&(s[:,2]>=box[2,0])&(s[:,2]<=box[2,1])
        print(tag,nm,'corner-region dots: %d (of %d)'%(int(m.sum()),len(s)),flush=True)
