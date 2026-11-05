import re
p='/data/gpfs/projects/punim2657/sfs_main/sfspreproc-docker/class/data_path.h'
s=open(p,errors='ignore').read()
blocks=re.split(r'^#ifdef (\w+)', s, flags=re.M)
for i in range(1,len(blocks),2):
    name=blocks[i]; body=blocks[i+1]
    m=re.search(r'#define SHARD_NUMBER (\d+)', body)
    if not m: continue
    pieces=re.findall(r'Breaklines/(\w+?)_Breakline_0\.pcd', body)
    if name.startswith('POT_'):
        print(name, m.group(1), len(pieces), ' '.join(p.replace('Pot_','') for p in pieces))
