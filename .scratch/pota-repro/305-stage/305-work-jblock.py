import re
p='/data/gpfs/projects/punim2657/sfs_main/sfspreproc-docker/class/data_path.h'
s=open(p,errors='ignore').read()
i=s.find('#ifdef POT_J')
j=s.find('#endif', i)
b=s[i:j]
print(b[:6000])
