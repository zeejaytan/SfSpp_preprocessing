#!/usr/bin/env python3
"""collect305.py POT... -- print one markdown block per pot from its score/ dir.
Usage: collect305.py RUNDIR [RUNDIR...]"""
import sys, os, glob, re, statistics

def read_acc(rd):
    rows = {}
    p = os.path.join(rd, "score", "acc.tsv")
    if not os.path.exists(p):
        return rows
    for ln in open(p).read().splitlines()[1:]:
        f = ln.split("\t")
        if len(f) >= 3:
            rows[f[0]] = (int(f[1]) if f[1].isdigit() else -1, f[2], f[3])
    return rows

def read_strict(rd, lab):
    p = os.path.join(rd, "score", lab + ".tsv")
    if not os.path.exists(p):
        return None
    pc = joins = None
    npieces = njoins = 0
    for ln in open(p).read().splitlines():
        f = ln.split("\t")
        if f[0] == "SUMMARY":
            m = re.search(r"pieces=(\d+)/(\d+)", ln); n = re.search(r"joins=(\d+)/(\d+)", ln)
            pc, npieces = int(m.group(1)), int(m.group(2))
            joins, njoins = int(n.group(1)), int(n.group(2))
    return pc, npieces, joins, njoins

def oncount(rd, pot):
    p = os.path.join(rd, "trees", "arm_pieces_%s.tsv" % pot)
    if not os.path.exists(p):
        return None
    d = {}
    for ln in open(p).read().splitlines()[1:]:
        f = ln.split("\t")
        if len(f) >= 5:
            d.setdefault(f[1], [0, 0])
            d[f[1]][1] += 1
            if f[4] == "on":
                d[f[1]][0] += 1
    return d

def main():
    for rd in sys.argv[1:]:
        base = os.path.basename(rd).rstrip("/")
        m = re.search(r"t305-e2e-([a-zA-Z])(?:-s\d+|-moom)?", base)
        pot = m.group(1).upper() if m else "?"
        acc = read_acc(rd)
        on = oncount(rd, pot) or {}
        print("\n### Pot %s  (%s)" % (pot, os.path.basename(rd)))
        print("| arm | reps | on/total | T placed | sherd best | edges best | strict pieces | strict joins | reps at best |")
        print("|---|---|---|---|---|---|---|---|---|")
        arms = {}
        for lab in acc:
            m2 = re.match(r"(OO|MO|OM|MMu|MM)R\d+$", lab)
            if m2:
                arms.setdefault(m2.group(1), []).append(lab)
        for arm in ["OO", "MO", "OM", "MM", "MMu"]:
            labs = sorted(arms.get(arm, []))
            if not labs:
                continue
            se = []
            st = []
            nt = []
            for lab in labs:
                t, s, e = acc[lab]
                s = tuple(int(x) for x in s.split("/"))
                e = tuple(int(x) for x in e.split("/"))
                se.append((s, e)); nt.append(len(glob.glob(os.path.join(rd,"out",lab,"T_*.txt"))))
                q = read_strict(rd, lab)
                st.append(q if q else (0, 0, 0, 0))
            bs = max(x[0][0] for x in se); ns = sum(1 for x in se if x[0][0] == bs)
            be = max(x[1][0] for x in se); ne = sum(1 for x in se if x[1][0] == be)
            bp = max(x[0] for x in st); nbp = sum(1 for x in st if x[0] == bp)
            bj = max(x[2] for x in st); nbj = sum(1 for x in st if x[2] == bj)
            o = on.get(arm, ["?", "?"])
            print("| %s | %d | %s/%s | T %d | %d/%d | %d/%d | %d/%d | %d/%d | sherd %d, edges %d, pieces %d, joins %d |" % (
                arm, len(labs), o[0], o[1], max(nt), bs, se[0][0][1], be, se[0][1][1],
                bp, st[0][1] or 0, bj, st[0][3] or 0, ns, ne, nbp, nbj))
        # per-repeat detail
        for arm in ["OO", "MO", "OM", "MM", "MMu"]:
            labs = sorted(arms.get(arm, []))
            if not labs:
                continue
            print("  %s detail: " % arm + " ; ".join(
                "%s %s/%s + %s/%s strict %s" % (lab, acc[lab][1], acc[lab][1].split("/")[1],
                                                acc[lab][2], acc[lab][2].split("/")[1],
                                                (lambda q: "%d/%d+%d/%d" % q if q else "-")(read_strict(rd, lab)))
                for lab in labs))

main()