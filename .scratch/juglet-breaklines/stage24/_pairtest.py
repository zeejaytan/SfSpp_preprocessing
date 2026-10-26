import glob, os, sys
import numpy as np

def load(p):
    names=[]; n=0
    with open(p,'rb') as f:
        while True:
            line=f.readline().decode('ascii','ignore').strip()
            if line.startswith('element vertex'): n=int(line.split()[2])
            if line.startswith('property'): names.append(line.split()[2])
            if line=='end_header': break
        d=np.loadtxt(f, dtype=np.float64, max_rows=n, ndmin=2)
    ix={k:i for i,k in enumerate(names)}
    return d[:,[ix['x'],ix['y'],ix['z']]], d[:,[ix['nx'],ix['ny'],ix['nz']]]

def u(v):
    n=np.linalg.norm(v,axis=-1,keepdims=True); n[n==0]=1.0; return v/n

def nn(A,B,maxa=1500):
    keep=None
    if len(A)>maxa:
        keep=np.linspace(0,len(A)-1,maxa).astype(int); A=A[keep]
    d=np.empty(len(A)); j=np.empty(len(A),dtype=int)
    B2=(B*B).sum(1)
    for s in range(0,len(A),200):
        q=A[s:s+200]
        D=B2-2.0*(q@B.T)+(q*q).sum(1)[:,None]
        j[s:s+200]=D.argmin(1); d[s:s+200]=np.sqrt(np.maximum(D[np.arange(len(q)),j[s:s+200]],0.0))
    return A,d,j,keep

rows=[]
for run in ('20261027-0532_1d8fb01_p24-normals-grid','20261027-0551_81d76c2_juglet-2x2'):
    for p0 in sorted(glob.glob('/data/gpfs/projects/punim2657/SfSpp/runs/%s/out/cells/*/*/*/surfaces/*_Surface_0.ply' % run)):
        p1=p0.replace('_Surface_0.ply','_Surface_1.ply')
        if not os.path.exists(p1): continue
        rel=p0.split('/out/cells/')[1].split('/surfaces/')[0]
        arm,pot,piece=rel.split('/')
        X0,N0=load(p0); X1,N1=load(p1)
        m0=u(N0.mean(0)); m1=u(N1.mean(0))
        c=X1.mean(0)-X0.mean(0)
        A,d,j,keep=nn(X1,X0)
        N1s=N1[keep] if keep is not None else N1
        vec=A-X0[j]
        nl=u(N0[j])                     # nearest S0 point's own normal
        al=np.abs((vec*nl).sum(1))      # along the wall normal
        lat=np.sqrt(np.maximum((vec**2).sum(1)-al**2,0.0))
        share=float((d<=1e-3).mean())
        rows.append([run[:4],arm,pot,piece,len(X0),len(X1),
                     '%.4f'%float(m0@m1),'%.3f'%float(np.linalg.norm(c)),'%.3f'%float(abs(c@m0)),
                     '%.3f'%float(np.median(d)),'%.4f'%share,
                     '%.3f'%float(np.median(al)),'%.3f'%float(np.median(lat)),
                     '%.3f'%float((lat<=1.0).mean())])
print('run\tarm\tpot\tpiece\tn0\tn1\tdot\tcsep\tcsep_along\tmed_nn\tshare1um\tmed_alongN0\tmed_latN0\tfrac_lat_under_1mm')
for r in rows:
    print('\t'.join(str(x) for x in r))
