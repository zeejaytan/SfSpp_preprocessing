"""POTA-180 reference Bl_0: mesh-frame single-loop walk + G0 author channels
+ 13-seg rescale (p176 mechanics verbatim). Laptop-side reference for md5
slot-hygiene proof; Spartan build (p180_build.py) repeats this exactly."""
import numpy as np, hashlib, os, shutil
S180='C:/PR/SfSpp_preprocessing/.scratch/pota180_repro'
CSXC='C:/PR/SfSpp_preprocessing/.scratch/pota177_repro/fetch145/pota145_fetch/rims_CSXC'
G0P='C:/PR/SfSpp_preprocessing/artifacts/pota26/pota26_fetch/rims_orig/Pot_C_Piece_01_Breakline_0.pcd'
FRESH='C:/PR/SfSpp_preprocessing/.scratch/pota176_repro/inputs/Pot_C_Piece_01_Breakline_0.pcd'
HDR=set(['VERSION','FIELDS','SIZE','TYPE','COUNT','WIDTH','HEIGHT','VIEWPOINT','POINTS','DATA'])
log=open(os.path.join(S180,'p180_pcd.txt'),'w')
def say(s): print(s,flush=True); log.write(s+'\n')
def load7(p):
 R=[]
 for ln in open(p):
  s=ln.strip()
  if not s or s[0]=='#' or s.split()[0] in HDR: continue
  R.append([float(x) for x in s.split()[:7]])
 return np.array(R)
def load_head(p):
 lines=open(p).read().splitlines()
 seg1=lines[1]; nseg=int(seg1.split()[1]); npts=int(seg1.split()[2]); info=int(seg1.split()[3])
 segs=[lines[2+i] for i in range(nseg)]; head9=lines[2+nseg:2+nseg+9]
 return seg1,nseg,npts,info,segs,head9
W=np.load(os.path.join(S180,'p180_C01_single_walk.npy'))
NNEW=len(W)
G0=load7(G0P)
say('G0 curvature uniq=%d val=%r'%(len(set(G0[:,6].tolist())),float(G0[0,6])))
d=np.sqrt(((W[:,None,:]-G0[None,:,:3])**2).sum(-1))
nn=d.argmin(1); nd=d.min(1)
say('G0-donor NN (mesh-mesh): med=%.2f max=%.2f n>5mm=%d'%(float(np.median(nd)),float(nd.max()),int((nd>5).sum())))
assert float(np.median(nd))<5.0
NC=G0[nn][:,3:7]
seg1,nseg,npts,info,segs,head9=load_head(FRESH)
assert (nseg,npts,info)==(13,402,0)
bounds=[(int(s.split()[1]),int(s.split()[2]),s.split()[3]) for s in segs]
newsegs=[]
for k,(a,b,f) in enumerate(bounds):
 na=int(round((a-1)/402*NNEW))+1; nb=int(round(b/402*NNEW))
 if k==0: na=1
 if k==len(bounds)-1: nb=NNEW
 if nb<na: nb=na
 newsegs.append('# %d %d %s'%(na,nb,f))
for k in range(1,len(newsegs)):
 pa,pb,pf=newsegs[k-1].split()[1:4]; ca,cb,cf=newsegs[k].split()[1:4]
 if int(ca)!=int(pb)+1: newsegs[k]='# %d %s %s'%(int(pb)+1,cb,cf)
assert int(newsegs[-1].split()[2])==NNEW
say('segments rescaled 402->%d head=%s tail=%s'%(NNEW,newsegs[0],newsegs[-1]))
# reference bundle Breaklines dir: 7x CSXC + new Bl_0
B=os.path.join(S180,'ref_bundle','Breaklines')
shutil.rmtree(os.path.join(S180,'ref_bundle'),ignore_errors=True)
os.makedirs(B)
import glob as G
for p in G.glob(os.path.join(CSXC,'*.pcd')):
 shutil.copy(p,os.path.join(B,os.path.basename(p)))
with open(os.path.join(B,'Pot_C_Piece_01_Breakline_0.pcd'),'w') as f:
 f.write('# .PCD v0.7 - Point Cloud Data file format\n')
 f.write('# %d %d %d\n'%(nseg,NNEW,info))
 for s in newsegs: f.write(s+'\n')
 for h in head9:
  if h.startswith('WIDTH'): f.write('WIDTH %d\n'%NNEW)
  elif h.startswith('POINTS'): f.write('POINTS %d\n'%NNEW)
  else: f.write(h+'\n')
 f.write('DATA ascii\n')
 for i in range(NNEW):
  f.write('%.4f %.4f %.4f %.7g %.7g %.7g %.7g\n'%(W[i,0],W[i,1],W[i,2],NC[i,0],NC[i,1],NC[i,2],NC[i,3]))
def md5(p): return hashlib.md5(open(p,'rb').read()).hexdigest()
rows=[]
for fn in sorted(os.listdir(CSXC)):
 a=md5(os.path.join(CSXC,fn)); b=md5(os.path.join(B,fn))
 rows.append((fn,a,b,'SAME' if a==b else 'DIFFERS'))
for fn,a,b,s in rows: say('%s %s %s'%(s,fn,b if s=='SAME' else a+' -> '+b))
assert sum(1 for r in rows if r[3]=='DIFFERS')==1 and [r[0] for r in rows if r[3]=='DIFFERS']==['Pot_C_Piece_01_Breakline_0.pcd']
say('SLOT-HYGIENE PROOF: only C01-Bl_0 differs, all 7 other slots bit-identical')
open(os.path.join(S180,'p180_BL_md5.txt'),'w').write(''.join('%s  %s\n'%(md5(os.path.join(B,fn)),fn) for fn in sorted(os.listdir(B))))
log.close()
