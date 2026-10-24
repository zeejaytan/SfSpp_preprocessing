import sys
p = "/data/gpfs/projects/punim2657/SfSpp/runs/index.tsv"
row = ["20261024-2328_d36a33e_p290-corpus", "33748526", "d36a33e58bbbdcfa52daf41689ae902fa51266d1", "p290-corpus", "", ""]
head = open(p).readline().rstrip("\n")
print("header:", head.replace("\t", "<TAB>"))
assert head.split("\t") == ["runid", "jobid", "commit", "tag", "verdict", "human_note"], "unexpected header"
with open(p, "a") as f:
    f.write("\t".join(row) + "\n")
print("appended:", "\t".join(row).replace("\t", "<TAB>"))
