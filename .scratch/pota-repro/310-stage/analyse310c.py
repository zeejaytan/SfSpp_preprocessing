"""Ticket 310 C2 delta table: seat counts with the rule's axes against ticket 308's arms.

Reads each pot's score/acc.tsv (columns: label time_s sherd k/n edge k/n raw) from a
baseline run root and from the C2 run root, takes best-of-N per arm (never the median),
and prints per pot:

  pot  MOR(base)  MO(new)  dMO |  MMR(base)  MM(new)  dMM

Best-of-N order: (sherd fraction, edge fraction) lexicographic, as in analyse308b.py.
A pot is flagged WORSE when the new arm's best is below the baseline's best on either
count.  NP is printed beside every count (the ticket's rule: a seating number without NP
is not comparable).

Usage: analyse310c.py --base DIR --new DIR [--pots A,B,...]
   DIR must contain one subdirectory per pot (<base>/A, <base>/B, ... each with score/acc.tsv),
   or be a single run directory when --pots names one pot.
"""
import argparse
import os

ARMS = {"MOR": "baseline authors' axes", "MOR1": "as above",
        "MMR": "baseline our axes", "MMR1": "as above"}


def parse_acc(path):
    """-> {label: (sherd_k, sherd_n, edge_k, edge_n)}"""
    out = {}
    if not os.path.isfile(path):
        return out
    with open(path) as f:
        for line in f:
            p = line.rstrip("\n").split("\t")
            if len(p) < 5 or p[0] == "label":
                continue
            try:
                sk, sn = [int(x) for x in p[2].split("/")]
                ek, en = [int(x) for x in p[3].split("/")]
            except ValueError:
                continue
            out[p[0]] = (sk, sn, ek, en)
    return out


def best(rows, prefix):
    """best-of-N over labels starting with prefix, by (sherd frac, edge frac)"""
    cand = [(v[0] / v[1] if v[1] else 0.0, v[2] / v[3] if v[3] else 0.0, k, v)
            for k, v in rows.items() if k.startswith(prefix)]
    if not cand:
        return None
    cand.sort(reverse=True)
    return cand[0]


def fmt(b):
    if b is None:
        return "     -    "
    v = b[3]
    return "%2d/%2d %2d/%2d" % (v[0], v[1], v[2], v[3])


def verdict(b0, b1):
    if b0 is None or b1 is None:
        return "?"
    d = (b1[0] - b0[0]) + (b1[1] - b0[1])
    if d < -1e-9:
        return "WORSE"
    if d > 1e-9:
        return "better"
    return "same"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", required=True, help="308b run root (subdirs A..J)")
    ap.add_argument("--new", required=True, help="C2 run root (subdirs A..J)")
    ap.add_argument("--base-map", default="", help="file: pot<TAB>run-dir (instead of --base)")
    ap.add_argument("--new-map", default="", help="file: pot<TAB>run-dir (instead of --new)")
    ap.add_argument("--pots", default="A,B,C,D,E,F,G,I,J")
    a = ap.parse_args()
    pots = [p.strip() for p in a.pots.split(",") if p.strip()]
    print("pot  NP |  MOR base       MO new      dMO   |  MMR base      MM new      dMM")
    rows = []
    def mapping(path):
        m = {}
        if path and os.path.isfile(path):
            for line in open(path):
                p = line.rstrip("\n").split("\t")
                if len(p) >= 2 and p[0].strip():
                    m[p[0].strip()] = p[1].strip()
        return m

    m0, m1 = mapping(a.base_map), mapping(a.new_map)

    def dirs(pot):
        d0 = m0.get(pot) or os.path.join(a.base, pot)
        d1 = m1.get(pot) or os.path.join(a.new, pot)
        return d0, d1

    for pot in pots:
        d0, d1 = dirs(pot)
        r0 = os.path.join(d0, "score", "acc.tsv")
        r1 = os.path.join(d1, "score", "acc.tsv")
        b0 = parse_acc(r0)
        b1 = parse_acc(r1)
        mor0, mmr0 = best(b0, "MOR"), best(b0, "MMR")
        mor1, mmr1 = best(b1, "MOR"), best(b1, "MMR")
        np_ = None
        for src in (os.path.join(d0, "logs", "panel.tsv"),
                    os.path.join(d1, "logs", "panel.tsv")):
            if os.path.isfile(src):
                with open(src) as f:
                    ls = [l.split("\t") for l in f if l.strip()]
                if len(ls) > 1:
                    np_ = ls[1][4]
                    break
        print("%-3s %3s | %-13s %-13s %-6s | %-13s %-13s %-6s"
              % (pot, np_ or "?", fmt(mor0), fmt(mor1), verdict(mor0, mor1),
                 fmt(mmr0), fmt(mmr1), verdict(mmr0, mmr1)))
        rows.append((pot, np_, mor0, mor1, mmr0, mmr1,
                     verdict(mor0, mor1), verdict(mmr0, mmr1)))
    worse = [r[0] for r in rows if r[7] == "WORSE"]
    better = [r[0] for r in rows if r[7] == "better"]
    print("\nMM vs baseline MMR: better in %s; WORSE in %s"
          % (",".join(better) or "none", ",".join(worse) or "none"))
    cw = [r[0] for r in rows if r[6] == "WORSE"]
    cb = [r[0] for r in rows if r[6] == "better"]
    print("MO control vs baseline MOR: better in %s; worse in %s"
          % (",".join(cb) or "none", ",".join(cw) or "none"))


if __name__ == "__main__":
    main()
