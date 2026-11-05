#!/usr/bin/env python3
"""specgen308.py -- build render308 spec lines from each pot run's score/acc.tsv.

    specgen308.py RUN_DIR [RUN_DIR ...]

One output line per pot:  POT<TAB>TITLE<TAB>LABEL=RESULTDIR ...

For each arm (MOR / MMR / MMpR) the best repeat is chosen by (sherd k, edge k) -- the
figure must show the best attempt, not the median, so the panels answer "when it works,
what does it look like".  A pot whose three arms are identical in score still gets three
panels: the point is whether the pieces land in the same place.
"""
import os, sys

ARMS = [("MOR", "OO"), ("MMR", "MM"), ("MMpR", "MMp")]


def read_acc(rd):
    rows = []
    p = os.path.join(rd, "score", "acc.tsv")
    if not os.path.exists(p):
        return rows
    with open(p) as fh:
        hdr = fh.readline().rstrip("\n").split("\t")
        for line in fh:
            f = line.rstrip("\n").split("\t")
            if len(f) < 4:
                continue
            d = dict(zip(hdr, f))
            try:
                sk, sn = d["sherd"].split("/")
                ek, en = d["edge"].split("/")
                d["sherd_k"], d["edge_k"] = int(sk), int(ek)
                d["sherd_n"], d["edge_n"] = int(sn), int(en)
            except Exception:
                continue
            rows.append(d)
    return rows


def main():
    for rd in sys.argv[1:]:
        base = os.path.basename(rd.rstrip("/"))
        pot = base.split("-")[-1]
        rows = read_acc(rd)
        panels, notes = [], []
        for pre, name in ARMS:
            cand = [r for r in rows if r["label"].startswith(pre)]
            if not cand:
                continue
            cand.sort(key=lambda r: (r["sherd_k"], r["edge_k"]), reverse=True)
            b = cand[0]
            panels.append("%s=%s" % (name, os.path.join(rd, "out", b["label"])))
            notes.append("%s %d/%d+%d/%d(%s)" % (name, b["sherd_k"], b["sherd_n"],
                                                b["edge_k"], b["edge_n"], b["label"]))
        if not panels:
            continue
        np_ = ""
        rj = os.path.join(rd, "run.json")
        if os.path.exists(rj):
            import json
            try:
                np_ = " NP %s" % json.load(open(rj)).get("np", "")
            except Exception:
                np_ = ""
        title = "Pot %s  %s%s  best repeat per arm" % (pot, " ".join(notes), np_)
        print("%s\t%s\t%s" % (pot, title, " ".join(panels)))


if __name__ == "__main__":
    main()
