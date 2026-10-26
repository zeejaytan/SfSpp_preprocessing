
import numpy as np
def load(p):
    hdr=[]; n=0
    with open(p,'rb') as f:
        while True:
            line=f.readline().decode('ascii','ignore').strip(); hdr.append(line)
            if line.startswith('element vertex'): n=int(line.split()[2])
            if line=='end_header': break
        d=np.loadtxt(f, dtype=float, max_rows=n)
    return d
import sys
for name in ('Pot_A_Piece_01','Pot_A_Piece_07'):
    d0=load('C:/PR/worktrees/sfs/24/.scratch/juglet-breaklines/stage24/%s_S0.ply'%name)
    d1=load('C:/PR/worktrees/sfs/24/.scratch/juglet-breaklines/stage24/%s_S1.ply'%name)
    X0,N0=d0[:,0:3],d0[:,3:6]; X1,N1=d1[:,0:3],d1[:,3:6]
    m0=N0.mean(axis=0); m0/=np.linalg.norm(m0); m1=N1.mean(axis=0); m1/=np.linalg.norm(m1)
    csep=(X1.mean(axis=0)-X0.mean(axis=0))
    print('%s n0=%d n1=%d dot=%.4f  centroid-sep=%.2f mm  along-n=%.2f mm' % (name,len(X0),len(X1),m0@m1,np.linalg.norm(csep),abs(csep@m0)))
