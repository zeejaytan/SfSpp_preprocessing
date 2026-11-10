
import numpy as np, itertools, glob, os
D=r"C:/PR/worktrees/sfs/325/artifacts/pota325/potbl"
F={}
for f in sorted(glob.glob(D+"/*.xyz")):
    k=int(os.path.basename(f).split("_Piece_")[1][:2]); F[k]=np.loadtxt(f)[:,:3]
for i,j in itertools.combinations(sorted(F),2):
    d=np.min(np.linalg.norm(F[i][:,None,:]-F[j][None,:,:],axis=2))
    print(f"Pot_A {i:02d}-{j:02d}: min gap {d:8.4f} mm")
