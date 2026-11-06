#!/usr/bin/env python3
"""summarise311b.py SCORE_DIR -- print per-arm summary table for Stage B."""
import glob
import json
import os
import sys


def main():
    sc = sys.argv[1]
    files = sorted(glob.glob(os.path.join(sc, "*_cpp.json")))
    print("label\tsherds\tjoins\tn_T\tfailed_pieces")
    for f in files:
        d = json.load(open(f))
        print("%s\t%d/%d\t%d/%d\t%d\t%s" % (
            d["label"], d["n_sherd"], d["total_sherd"],
            d["n_join"], d["total_join"], d["n_T_files"],
            ",".join(str(x) for x in d["failed_pieces"]) or "none"
        ))


if __name__ == "__main__":
    main()
