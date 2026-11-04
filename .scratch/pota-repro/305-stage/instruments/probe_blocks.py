
import re,os,glob
H="/data/gpfs/projects/punim2657/sfs_main/sfspreproc-docker/class/data_path.h"
C="/data/gpfs/projects/punim2657/sfs_main/original_samples/SfS_pp"
src=open(H).read()
for pot in "ABCDEFGHIJ":
    m=re.search(r"#ifdef POT_"+pot+r"\b(.*?)\n#endif", src, re.S)
    if not m:
        print(pot,"NO BLOCK"); continue
    b=m.group(1)
    sh=re.search(r"#define SHARD_NUMBER (\d+)", b)
    s=re.search(r"shard_on_off\[SHARD_NUMBER\] = \{(.*?)\};", b, re.S)
    fl=" ".join(x.strip() for x in s.group(1).split(",")) if s else "?"
    print(pot,"NP",sh.group(1) if sh else "?","on_off",fl[:200])
print("=== T files")
for pot in "ABCDEFGHIJ":
    n=len(glob.glob(os.path.join(C,"Ground Truth","Pot_%s_Piece_*_T.txt"%pot)))
    print("Pot_%s T_files=%d"%(pot,n))
print("=== breakline pcd per pot")
for pot in "ABCDEFGHIJ":
    n=len(glob.glob(os.path.join(C,"Breaklines","Pot_%s_Piece_*_Breakline_0.pcd"%pot)))
    print("Pot_%s BL0=%d"%(pot,n))
print("=== graphs")
for f in sorted(glob.glob(os.path.join(C,"Ground Truth","*_simple_graph.txt"))):
    print(os.path.basename(f), sum(1 for _ in open(f)))
