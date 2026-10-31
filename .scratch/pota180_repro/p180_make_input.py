"""POTA-180 single-loop input: de-double 439-dot TRUE walk -> one strand,
uniform arc-length resample at 1.80mm, closed loop. Laptop-side numpy only.
Ticket 180 (method from 179 s3). No dataset writes, no assembler touch."""
import numpy as np, hashlib, os
S180 = 'C:/PR/SfSpp_preprocessing/.scratch/pota180_repro'
W = 'C:/PR/SfSpp_preprocessing/.scratch/pota176_repro/p176_C01_TRUE_walk.npy'
G0P = 'C:/PR/SfSpp_preprocessing/artifacts/pota26/pota26_fetch/rims_orig/Pot_C_Piece_01_Breakline_0.pcd'
TP = 'C:/PR/SfSpp_preprocessing/.scratch/pota176_repro/inputs/Pot_C_Piece_1_T.txt'
HDR = ('VERSION','FIELDS','SIZE','TYPE','COUNT','WIDTH','HEIGHT','VIEWPOINT','POINTS','DATA')
log = open(os.path.join(S180,'p180_report.txt'),'w')
def say(s):
    print(s,flush=True); log.write(s+'\n')
def load7(p):
    R=[]
    for ln in open(p):
        s=ln.strip()
        if not s or s[0]=='#' or s.split()[0] in HDR: continue
        R.append([float(x) for x in s.split()[:7]])
    return np.array(R)
L = np.load(W)
assert L.shape==(439,3) and hashlib.md5(open(W,'rb').read()).hexdigest()=='5f902355dd99a4fe35885bf596193733'
G0 = load7(G0P)
T=np.loadtxt(TP); R=T[:3,:3]; t=T[:3,3]
Gs = G0[:,:3]@R.T+t   # author seated loop (211)
say('author ORIG n=%d arc=%.1f closure=%.2f'%(len(Gs), float(np.sqrt(((Gs[1:]-Gs[:-1])**2).sum(-1)).sum()+np.linalg.norm(Gs[-1]-Gs[0])), float(np.linalg.norm(Gs[-1]-Gs[0]))))
dm = np.sqrt(((Gs[:,None,:]-L[None,:,:])**2).sum(-1))
N=211
cands=[np.where(dm[i]<2.0)[0].tolist() for i in range(N)]
assert all(len(c)>0 for c in cands), 'empty station -- STOP'
say('candidates/station: min=%d med=%.1f (all stations covered)'%(min(map(len,cands)), float(np.median([len(c) for c in cands]))))
# closed Viterbi: one candidate per station, min total length incl closure; try each start in station 0
C0=cands[0]
best=None
for s0 in C0:
    INF=float('inf')
    prev={s0:0.0}; back=[{s0:None}]
    for i in range(1,N):
        cur={}; bk={}
        for c in cands[i]:
            candP=[p for p in prev if p!=c] or list(prev)
            pc=min(candP, key=lambda p: prev[p]+float(np.linalg.norm(L[c]-L[p])))
            cur[c]=prev[pc]+float(np.linalg.norm(L[c]-L[pc])); bk[c]=pc
        prev=cur; back.append(bk)
    end=min(prev, key=lambda p: prev[p]+float(np.linalg.norm(L[s0]-L[p])))
    tot=prev[end]+float(np.linalg.norm(L[s0]-L[end]))
    if best is None or tot<best[0]: best=(tot,s0,end,[dict(b) for b in back])
tot,s0,end,back=best
path=[end]
for i in range(N-1,0,-1): path.append(back[i][path[-1]])
path=path[::-1]
assert path[0]==s0 and len(path)==N
S_single=L[np.array(path)]  # ours xyz, seated frame, author-loop order
say('Viterbi single track: total=%.1f (was 673.7 open doubled)'%tot)
# dedupe exact consecutive dupes
keep=[True]
for i in range(1,N): keep.append(np.linalg.norm(S_single[i]-S_single[i-1])>1e-9)
S_single=S_single[np.array(keep)]
say('dedupe: kept %d/%d'%(len(S_single),N))
# to mesh frame (bundle lives in mesh frame; assembler applies T at runtime; 176 s7a)
M=(S_single-t)@R
# closed-loop uniform arc-length resample at 1.80mm
P=np.vstack([M,M[:1]])
seg=np.sqrt(((P[1:]-P[:-1])**2).sum(-1))
A=float(seg.sum())
n=int(round(A/1.80))
target=np.arange(n)*A/n
cum=np.concatenate([[0.0],np.cumsum(seg)])
new=np.zeros((n,3))
j=0
for k in range(n):
    while j<len(seg)-1 and cum[j+1]<target[k]: j+=1
    f=(target[k]-cum[j])/max(seg[j],1e-12)
    new[k]=P[j]+f*(P[j+1]-P[j])
st=np.sqrt(((new[1:]-new[:-1])**2).sum(-1))
closure=float(np.linalg.norm(new[-1]-new[0]))
full=np.append(st,closure)
say('SINGLE n=%d arc=%.1f closure=%.2f max=%.2f med=%.2f n>5mm=%d nzerostep=%d'%(n,A,closure,float(full.max()),float(np.median(full)),int((full>5).sum()),int((full==0).sum())))
# gate vs author (176 s7 recipe: seat via T, NN med vs author seated)
seated=new@R.T+t
def nn(A,B):
    return np.sqrt(((A[:,None,:]-B[None,:,:])**2).sum(-1)).min(1)
dO=nn(seated,Gs); dA=nn(Gs,seated)
say('RIM-TRUTH ours-vs-author med=%.2f <2mm=%.1f%% max=%.2f'%(float(np.median(dO)),float((dO<2).mean()*100),float(dO.max())))
say('RIM-TRUTH author-vs-ours med=%.2f max=%.2f'%(float(np.median(dA)),float(dA.max())))
# D-tokens, 0.15 bins (179 proxy)
bins=np.floor(full/0.15).astype(int)
u=np.unique(bins)
from collections import Counter
cc=Counter(bins)
top=cc.most_common(3)
run=1; best_run=1
for k in range(1,len(bins)):
    run=run+1 if bins[k]==bins[k-1] else 1
    best_run=max(best_run,run)
say('D-TOKENS distinct=%d top=%s longest-run=%d (author: 3 / longest 4)'%(len(u),[(int(b),int(c)) for b,c in top],best_run))
np.save(os.path.join(S180,'p180_C01_single_walk.npy'),new)
np.save(os.path.join(S180,'p180_C01_single_walk_seated.npy'),seated)
say('saved p180_C01_single_walk.npy (%dx3, mesh frame) md5=%s'%(n,hashlib.md5(open(os.path.join(S180,'p180_C01_single_walk.npy'),'rb').read()).hexdigest()))
log.close()
