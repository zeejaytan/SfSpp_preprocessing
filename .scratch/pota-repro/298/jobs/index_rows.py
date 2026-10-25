import os, re, glob
RUNS="/data/gpfs/projects/punim2657/SfSpp/runs"
IDX=os.path.join(RUNS,"index.tsv")
COMMIT=None  # taken from each run's own run.json
have=set()
for line in open(IDX):
    have.add(line.split("\t")[0])
rows=[]
for d in sorted(glob.glob(f"{RUNS}/*_p298-*")):
    rid=os.path.basename(d)
    if rid in have: continue
    tag=rid.split("_",2)[2]
    logs=sorted(glob.glob(f"{d}/logs/slurm-*.out"))
    if not logs: continue
    job=re.search(r"slurm-(\d+)\.out", logs[-1]).group(1)
    settled=False
    if "prep" in tag:
        txt=open(logs[-1]).read()
        settled = "[RUN] done" in txt and "geometry in out/geom" in txt
    else:
        settled = os.path.exists(f"{d}/out/Result/1. Acc.txt") and os.path.exists(f"{d}/out/summary.txt")
    if settled:
        import json
        c=json.load(open(f"{d}/run.json")).get("commit_preprocessing") or COMMIT
        rows.append((rid,job,c,tag))
with open(IDX,"a") as f:
    for r in rows: f.write("\t".join(r)+"\t\t\n")
print("appended", len(rows))
for r in rows: print(r[0], r[1])