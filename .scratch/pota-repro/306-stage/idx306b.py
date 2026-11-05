import sys
IDX = "/data/gpfs/projects/punim2657/SfSpp/runs/index.tsv"
row = ["20261104-2331_c333dc7_t306b1-union-a", "34357586", "c333dc7",
       "t306b1-union-a", "", ""]
with open(IDX) as f:
    lines = f.read().splitlines()
print("rows before", len(lines))
assert lines[0].split("\t")[:6] == ["runid", "jobid", "commit", "tag", "verdict", "human_note"], lines[0]
assert not any(l.split("\t")[0] == row[0] for l in lines), "row already present"
with open(IDX, "a") as f:
    f.write("\t".join(row) + "\n")
with open(IDX) as f:
    lines = f.read().splitlines()
print("rows after", len(lines))
print("last:", repr(lines[-1]))
print("fields in last:", len(lines[-1].split("\t")))
