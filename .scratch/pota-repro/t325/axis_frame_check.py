
import numpy as np, itertools
ART = r"C:/PR/worktrees/sfs/325/artifacts/pota325"
def T(i):
    M=np.loadtxt(f"{ART}/gtT/Juglet_Piece_{i}_T.txt"); return M[:3,:3], M[:3,3]
print("piece  d_world                 pt_world")
lines={}
for i in range(1,10):
    R,t=T(i)
    row=np.loadtxt(f"{ART}/axes/gt/Juglet_Piece_{i}_Axis.xyz",ndmin=2)[0]
    p,d=row[:3],row[3:6]; d=d/np.linalg.norm(d)
    pw=R@p+t; dw=R@d
    lines[i]=(pw,dw)
    print(f"{i}  {np.round(dw,4)}  {np.round(pw,3)}")
A=[v for v in lines.values()]
print("\npairwise angle between the 9 world directions (deg) and point-to-line distances (mm):")
mx_ang=0; mx_d=0
for (i,a),(j,b) in itertools.combinations(lines.items(),2):
    ang=np.degrees(np.arccos(min(1,abs(a[1]@b[1]))))
    w=b[0]-a[0]; dist=np.linalg.norm(w-np.dot(w,a[1])*a[1])
    mx_ang=max(mx_ang,ang); mx_d=max(mx_d,dist)
print("max direction spread deg", round(mx_ang,3), " max line offset mm", round(mx_d,3))
