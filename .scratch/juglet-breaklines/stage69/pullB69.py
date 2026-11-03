#!/usr/bin/env python3
"""pullB69.py -- pack the lanes (and only the lanes) out of a ticket-69 preprocessing run."""
import os, subprocess, sys
run = sys.argv[1]
os.makedirs("outB", exist_ok=True)
n = 0
with open("outB/manifest.tsv", "w") as man:
    for cell in ("out_pota", "out_potc", "out_potd", "out_potj"):
        for g in ("geom18", "geom09"):
            d = os.path.join(run, cell, g)
            if not os.path.isdir(d):
                continue
            dst = os.path.join("outB", cell, g)
            os.makedirs(dst, exist_ok=True)
            for f in sorted(os.listdir(d)):
                if ".Bl" not in f:
                    continue
                src = os.path.join(d, f)
                subprocess.run(["cp", "-f", src, os.path.join(dst, f)], check=True)
                man.write("%s\t%s\t%s\n" % (cell, g, f))
                n += 1
print("copied", n, "lane files")
