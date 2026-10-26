
import numpy as np, sys
def load(p):
    hdr=[]; n=0
    with open(p,'rb') as f:
        while True:
            line=f.readline().decode('ascii','ignore').strip()
            hdr.append(line)
            if line.startswith('element vertex'): n=int(line.split()[2])
            if line=='end_header': break
        data=np.loadtxt(f, dtype=float, max_rows=n)
    names=[h.split()[2] for h in hdr if h.startswith('property')]
    return names, data
for arm in ('A','D'):
    for s in ('0','1'):
        names, d = load('C:/PR/worktrees/sfs/24/.scratch/juglet-breaklines/stage24/p7_%s_S%s.ply' % (arm,s))
        xyz=d[:,0:3]; nrm=d[:,3:6]
        if s=='0':
            globals()['X0_'+arm]=xyz; globals()['N0_'+arm]=nrm
        else:
            globals()['X1_'+arm]=xyz; globals()['N1_'+arm]=nrm
    X0=X0_+arm if False else globals()['X0_'+arm]; X1=globals()['X1_'+arm]
    n0=globals()['N0_'+arm]; n1=globals()['N1_'+arm]
    m0=n0.mean(axis=0); m0/=np.linalg.norm(m0)
    m1=n1.mean(axis=0); m1/=np.linalg.norm(m1)
    # project everything onto m0
    p0=X0@m0; p1=X1@m0
    print(arm, 'npts', len(X0), len(X1), 'mean-normal dot %.4f' % float(m0@m1))
    print('   along S0 mean normal: S0 median %.3f  S1 median %.3f  difference %.3f mm' % (np.median(p0), np.median(p1), abs(np.median(p1)-np.median(p0))))
    print('   along-normal spread: S0 p5-p95 %.3f..%.3f  S1 p5-p95 %.3f..%.3f' % (np.percentile(p0,5),np.percentile(p0,95),np.percentile(p1,5),np.percentile(p1,95)))
    # mean normals angle between the two patches at their centroids, plus lateral separation
    print('   centroid separation %.2f mm' % float(np.linalg.norm(X0.mean(axis=0)-X1.mean(axis=0))))
