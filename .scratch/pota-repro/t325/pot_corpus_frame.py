
import numpy as np, itertools, glob, os
def read_pcd(p):
    rows=[]; data=False
    for line in open(p, errors="replace"):
        if line.startswith("DATA"): data=True; continue
        if not data: continue
        s=line.split()
        if len(s)>=3:
            try: rows.append([float(s[0]),float(s[1]),float(s[2])])
            except ValueError: pass
    return np.array(rows)
D=r"C:/PR/worktrees/sfs/325/artifacts/pota325/potbl_corpus"
F={int(os.path.basename(f).split("_Piece_")[1][:2]):read_pcd(f) for f in sorted(glob.glob(D+"/*.pcd"))}
for k,v in F.items(): print(k, v.shape, np.round(v.mean(0),1))
print()
for i,j in itertools.combinations(sorted(F),2):
    d=np.min(np.linalg.norm(F[i][:,None,:]-F[j][None,:,:],axis=2))
    print(f"corpus Pot_A {i:02d}-{j:02d}: min gap {d:8.3f} mm")
