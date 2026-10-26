
import json, os
import numpy as np
ROOT = r"C:\PR\worktrees\sfs\299\.scratch\pota-repro\299-work\t299"
d = json.load(open(os.path.join(ROOT, "analysis.json")))
for r in d:
    print("=== Pot_%s %s  SA %d/%d  EA %d/%d" % (r["pot"], r["arm"], r["k_sherd"], r["t_sherd"], r["k_edge"], r["t_edge"]))
    print("  idx piece  on gt  nbrs  seated bestj  best_deg best_mm   abs_deg abs_mm  edges")
    for row in r["rows"]:
        print("  %2d  %2d   %s %s  %2d   %-6s %-5s  %8s %7s  %7s %6s  %d/%d" % (
            row["idx"], row["piece"], "Y" if row["on"] else "n", "Y" if row["gt_present"] else "n",
            row["nbrs"], "YES" if row["seated"] else "no", row["best_j"],
            row["best_deg"], row["best_mm"], row["abs_deg"], row["abs_mm"],
            row["deg_correct"], row["deg_total"]))
    print()
