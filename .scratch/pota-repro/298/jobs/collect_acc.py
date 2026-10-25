import glob, os, re
RUNS="/data/gpfs/projects/punim2657/SfSpp/runs"
dirs=sorted(glob.glob(f"{RUNS}/20261026-0046_63cf615_p298-Pot_B-*")+glob.glob(f"{RUNS}/20261026-0126_d1f1a4c_p298-Pot_*")+glob.glob(f"{RUNS}/20261026-0301_d1f1a4c_p298-Pot_*-rep2"))
for d in dirs:
    b=os.path.basename(d)
    if "prep" in b: continue
    acc=os.path.join(d,"out","Result","1. Acc.txt")
    if not os.path.exists(acc): continue
    log=os.path.join(d,"logs","assembly.log")
    txt=open(log,errors="ignore").read()
    tot=re.search(r"Total number : (\d+)",txt); pr=re.search(r"Total number pruned : (\d+)",txt)
    s=re.findall(r"Sherd accuracy : (\d+ / \d+ \([0-9.]+ ?%\))",txt)
    e=re.findall(r"Edge accuracy : (\d+ / \d+ \([0-9.]+ ?%\))",txt)
    a=open(acc,errors="ignore").read().strip().splitlines()
    tag=b.split("_p298-")[1]
    print(f"{tag}\ttotal={tot.group(1) if tot else '-'} pruned={pr.group(1) if pr else '-'}\tsherd={s[0] if s else '-'}\tedge={e[0] if e else '-'}\tAccLine2={a[1].strip() if len(a)>1 else '-'}\tAccLine3={a[2].strip() if len(a)>2 else '-'}")
