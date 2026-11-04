import numpy as np, os, glob
C="/data/gpfs/projects/punim2657/sfs_main/original_samples/SfS_pp"
def rd(p):
    a=np.loadtxt(p); a=np.atleast_2d(a); return a
rel=rd(C+"/Axes/Pot_A_Piece_08_Axis.xyz")
print("released rows",rel.shape)
def ang(a,b):
    a=a/np.linalg.norm(a); b=b/np.linalg.norm(b); c=min(abs(a@b),1.0); return np.degrees(np.arccos(c))
r=rel[:,3:6] if rel.shape[1]>=6 else rel[:,0:3]
print("released dir(s):", r[:2])
for p in ["/data/gpfs/projects/punim2657/SfSpp/runs/20261105-0153_3649473_t304-corpus-axes/out/axes302/Pot_A_Piece_08_Axis.xyz",
          "/data/gpfs/projects/punim2657/SfSpp/runs/20261105-0420_9c5eec2_t305-axes-stage0/out/a305/axes305/Pot_A_Piece_08_Axis.xyz",
          "/data/gpfs/projects/punim2657/SfSpp/runs/20261105-0420_9c5eec2_t305-axes-stage0/out/notrunc/axes305/Pot_A_Piece_08_Axis.xyz"]:
    if not os.path.exists(p): print("MISSING",p); continue
    a=rd(p)
    print(os.path.basename(os.path.dirname(os.path.dirname(p))), a.shape, [round(float(ang(a[i,3:6], r[0])),3) for i in range(a.shape[0])])
for d in glob.glob("/data/gpfs/projects/punim2657/SfSpp/runs/20261105-0217_3649473_t304-stageC/out/*"):
    print(d, os.path.isdir(d))
