IDX="/data/gpfs/projects/punim2657/SfSpp/runs/index.tsv"
lines = open(IDX).read().splitlines()
keep = [l for l in lines if "t308b-" not in l.split("\t")[0]]
drop = [l.split("\t")[0] for l in lines if "t308b-" in l.split("\t")[0]]
print("before", len(lines), "after", len(keep), "dropped", len(drop))
for d in drop: print("  ", d)
open(IDX, "w").write("\n".join(keep) + "\n")
print("header", keep[0].split("\t")[:6])
