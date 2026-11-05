#!/usr/bin/env python3
"""Append one run row to the shared runs index (ticket 306). argv: runid jobid commit tag."""
import sys

IDX = "/data/gpfs/projects/punim2657/SfSpp/runs/index.tsv"
runid, jobid, commit, tag = sys.argv[1:5]
row = [runid, jobid, commit, tag, "", ""]
with open(IDX) as f:
    lines = f.read().splitlines()
assert lines[0].split("\t")[:6] == ["runid", "jobid", "commit", "tag", "verdict", "human_note"], lines[0]
assert not any(l.split("\t")[0] == runid for l in lines), "row already present for " + runid
with open(IDX, "a") as f:
    f.write("\t".join(row) + "\n")
with open(IDX) as f:
    lines = f.read().splitlines()
print("rows", len(lines), "last fields", len(lines[-1].split("\t")))
print("last", repr(lines[-1]))
