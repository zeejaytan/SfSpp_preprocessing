
import re
H="/data/gpfs/projects/punim2657/sfs_main/sfspreproc-docker/class/data_path.h"
src=open(H).read()
for pot in "ABCDEFGHIJ":
    m=re.search(r"#ifdef POT_"+pot+r"\b(.*?)\n#endif", src, re.S)
    b=m.group(1)
    fp=re.search(r"string file_path\[SHARD_NUMBER\] = \{(.*?)\};", b, re.S).group(1)
    ents=[x.strip().strip('"') for x in fp.split(",") if "Breaklines" in x]
    print(pot, len(ents), ents[0], "|", ents[-1])
