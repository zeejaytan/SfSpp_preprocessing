# 175 probe0: ruler + ORIG-free observables on the 753-dot bag. Read-only inputs.
import numpy as np, os
H = "C:/PR/SfSpp_preprocessing/.scratch/pota175_repro"
os.makedirs(H, exist_ok=True)
log = open(H + "/p175_probe0.txt", "w")
def say(s):
    print(s, flush=True); log.write(s + "\n")
def load_obj(path):
    V, F = [], []
    with open(path) as fh:
        for ln in fh:
            if ln.startswith("v "): V.append([float(x) for x in ln.split()[1:4]])
            elif ln.startswith("f "): F.append([int(x.split("/")[0]) - 1 for x in ln.split()[1:4]])
    return np.array(V), np.array(F, dtype=np.int64)
d = np.load("C:/PR/SfSpp_preprocessing/.scratch/pota173_repro/p173_bag.npz", allow_pickle=True)
BAG, G0 = d["BAG"], d["G0"]
say("bag=%d ORIG=%d" % (len(BAG), len(G0)))
from scipy.spatial import cKDTree
KG0 = cKDTree(G0)
dmin = KG0.query(BAG)[0]; sta = KG0.query(BAG)[1]
cenO = G0.mean(0)
U,S,Vt = np.linalg.svd(G0-cenO, full_matrices=False); nO = Vt[2]
def radialO(P):
    v = P-cenO; ax = v.dot(nO); return np.sqrt(np.maximum((v**2).sum(-1)-ax**2,0))
dr = radialO(BAG) - radialO(G0)[np.clip(sta,0,len(G0)-1)]
inner = dr <= 1.0; outer = dr > 2.5; mid = (~inner)&(~outer)
say("ruler: inner=%d outer=%d mid=%d" % (int(inner.sum()), int(outer.sum()), int(mid.sum())))
both = sorted(set(np.unique(sta[inner]).tolist()) & set(np.unique(sta[outer]).tolist()))
say("straddle stations (inner+outer same st): %d %s" % (len(both), both[:40]))
cenB = BAG.mean(0)
Ub,Sb,Vtb = np.linalg.svd(BAG-cenB, full_matrices=False); nB = Vtb[2]
def radialB(P):
    v = P-cenB; ax = v.dot(nB); return np.sqrt(np.maximum((v**2).sum(-1)-ax**2,0))
rB = radialB(BAG)
say("bag-frame radius: inner med=%.2f outer med=%.2f mid med=%.2f" % (float(np.median(rB[inner])), float(np.median(rB[outer])), float(np.median(rB[mid])) if mid.sum() else -1))
V, F = load_obj("C:/PR/SfSpp_preprocessing/temp_download/Mesh/Pot_C/Pot_C_Piece_01_Mesh_DS.obj")
TF = np.loadtxt("C:/PR/SfSpp_preprocessing/.scratch/pota115_staging/inputs/TF.txt")
Vg = V.dot(TF[:3,:3].T) + TF[:3,3]
v0,v1,v2 = Vg[F[:,0]],Vg[F[:,1]],Vg[F[:,2]]
fn = np.cross(v1-v0,v2-v0); L=np.linalg.norm(fn,axis=1); L[L==0]=1; fn=fn/L[:,None]
C = (v0+v1+v2)/3
ji = np.empty(len(BAG),int)
for i in range(0,len(BAG),25):
    q = BAG[i:i+25]; dd = ((q[:,None,:]-C[None,:,:])**2).sum(-1)
    ji[i:i+25] = np.argmin(dd,axis=1)
rh = (BAG-cenB)/np.maximum(np.linalg.norm(BAG-cenB,axis=1)[:,None],1e-9)
alB = (fn[ji]*rh).sum(-1)
say("mesh-align(bag-radial): inner med=%+.2f frac<-0.5=%.2f frac>0.5=%.2f" % (float(np.median(alB[inner])), float((alB[inner]<-0.5).mean()), float((alB[inner]>0.5).mean())))
say("mesh-align(bag-radial): outer med=%+.2f frac<-0.5=%.2f frac>0.5=%.2f" % (float(np.median(alB[outer])), float((alB[outer]<-0.5).mean()), float((alB[outer]>0.5).mean())))
if mid.sum():
    say("mesh-align(bag-radial): mid med=%+.2f frac<-0.5=%.2f frac>0.5=%.2f" % (float(np.median(alB[mid])), float((alB[mid]<-0.5).mean()), float((alB[mid]>0.5).mean())))
e1b, e2b = Vtb[0], Vtb[1]
ang = np.arctan2((BAG-cenB).dot(e2b),(BAG-cenB).dot(e1b))
nb=72
bins=(np.floor((ang+np.pi)/(2*np.pi)*nb)).astype(int).clip(0,nb-1)
ib=set(np.unique(bins[inner]).tolist()); ob=set(np.unique(bins[outer]).tolist())
sboth=sorted(ib&ob)
say("angular bins with both classes: %d/72" % len(sboth))
np.savez(H+"/p175_probe0.npz", alB=alB, rB=rB, ang=ang, dr=dr, sta=sta, dmin=dmin)
log.close(); print("probe0 done")
