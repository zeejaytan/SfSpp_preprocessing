
import numpy as np, itertools
D=r"C:/PR/worktrees/sfs/325/artifacts/pota325/potbl"
B={i:np.loadtxt(f"{D}/Pot_A_Piece_{i:02d}_Breakline_0.xyz")[:,:3] for i in (1,2,3)}
T={}
for i in (1,2,3):
    M=np.array([
      [0.977177,-0.0718648,-0.199899,51.2681],
      [-0.00434055,0.934084,-0.357029,152.919],
      [0.21238,0.349748,0.912453,-350.3],
      [0,0,0,1]])
    T[i]=M
T[2]=np.array([[-0.184336,-0.905815,0.38147,-114.437],[0.909554,-0.304296,-0.283045,79.8716],[0.372466,0.294793,0.879981,-345.038],[0,0,0,1]])
T[3]=np.array([[-0.0220111,-0.99605,-0.0860205,26.8641],[0.274225,-0.0887568,0.957561,-345.351],[-0.961413,-0.00251209,0.275095,-94.7067],[0,0,0,1]])
def gap(A,Bp): return float(np.min(np.linalg.norm(A[:,None,:]-Bp[None,:,:],axis=2)))
for i,j in itertools.combinations((1,2,3),2):
    raw=gap(B[i],B[j])
    wi=B[i]@T[i][:3,:3].T+T[i][:3,3]; wj=B[j]@T[j][:3,:3].T+T[j][:3,3]
    w=gap(wi,wj)
    print(f"Pot_A {i:02d}-{j:02d}: raw {raw:8.4f} mm | after GT T {w:8.4f} mm")
