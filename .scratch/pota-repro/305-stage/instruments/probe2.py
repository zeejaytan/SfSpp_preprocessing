
import re,os,glob
H="/data/gpfs/projects/punim2657/sfs_main/sfspreproc-docker/class/data_path.h"
C="/data/gpfs/projects/punim2657/sfs_main/original_samples/SfS_pp"
src=open(H).read()
m=re.search(r"#ifdef POT_B\b(.*?)\n#endif", src, re.S).group(1)
for arr in ("file_path","obj_path","axis_path","surface_in","surface_out","surface_fr","gt_T_path"):
    mm=re.search(arr+r"\[SHARD_NUMBER\] = \{(.*?)\};", m, re.S)
    first=mm.group(1).split(",")[0].strip() if mm else "?"
    cnt=len(mm.group(1).split(",")) if mm else 0
    print(arr, cnt, first)
print("=== surfaces on disk")
print(sorted(os.path.basename(f) for f in glob.glob(os.path.join(C,"Surfaces","Pot_B_Piece_01*"))))
print(sorted(os.path.basename(f) for f in glob.glob(os.path.join(C,"Mesh","Pot_B_Piece_01*"))))
print(sorted(os.path.basename(f) for f in glob.glob(os.path.join(C,"Axes","Pot_B_Piece_01*"))))
print(sorted(os.path.basename(f) for f in glob.glob(os.path.join(C,"Breaklines","Pot_B_Piece_01*"))))
print("=== disk free")
print(os.statvfs("/data/gpfs/projects/punim2657/SfSpp"))
