
import numpy as np
IN='C:/PR/worktrees/sfs/328-juglet-wall-side-cure/artifacts/pota328/in'
for k in range(1,10):
    T=np.loadtxt(f'{IN}/gt/Juglet_Piece_{k}_T.txt'); R=T[:3,:3]
    s=np.linalg.svd(R,compute_uv=False)
    print(k, np.round(s,4), 'det=%.4f'%np.linalg.det(R), 't=',np.round(T[:3,3],2))
print(np.loadtxt(f'{IN}/gt/Juglet_Piece_1_T.txt'))
