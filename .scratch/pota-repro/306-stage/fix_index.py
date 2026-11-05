#!/usr/bin/env python3
"""Repair one malformed line appended to runs/index.tsv by a quoting accident."""
import os, tempfile

IX = "/data/gpfs/projects/punim2657/SfSpp/runs/index.tsv"
BAD = "20261104-2306_c333dc7_t306a-poolt34357356tc333dc7tt306a-poolttn"
GOOD = "20261104-2306_c333dc7_t306a-pool\t34357356\tc333dc7\tt306a-pool\t\t\n"

with open(IX, "r", newline="") as fh:
    lines = fh.readlines()
assert lines[-1].rstrip("\n") == BAD, "last line is not the malformed one: %r" % lines[-1][:80]
kept = lines[:-1]
bad = [(i + 1, l[:60]) for i, l in enumerate(kept) if l.count("\t") < 4]
assert not bad, "unexpected malformed rows: %r" % bad[:3]
assert not any(l.startswith("20261104-2306_c333dc7") for l in kept), "row already present"
fd, tmp = tempfile.mkstemp(dir=os.path.dirname(IX))
with os.fdopen(fd, "w", newline="") as fh:
    fh.writelines(kept)
    fh.write(GOOD)
os.replace(tmp, IX)
rows = open(IX, newline="").readlines()
print("rows now:", len(rows))
print("last:", repr(rows[-1]))
