import json, os
d = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", "artifacts", "pota327", "swap"))
labels = [("ctrl","diag_jug_GTctrl.txt"),("swap1","diag_jug_SWAPr1.txt"),("NEG","diag_jug_NEG.txt"),
          ("NEG7","diag_jug_NEG7.txt"),("NEGALL","diag_jug_NEGALL.txt")]
run = {}
for lab, fn in labels:
    t = {}
    cols = None
    for l in open(os.path.join(d, fn)):
        if not l.startswith("GTPAIR"): continue
        p = l.rstrip("\n").split("\t")
        if p[1] == "y":
            cols = p[3:]; continue
        t[(int(p[1]), int(p[2]))] = dict(zip(cols, [float(x) for x in p[3:]]))
    run[lab] = t
pairs = [(1,2),(1,4),(1,8),(1,9),(2,5),(2,9),(3,5),(6,7),(7,9)]
print("pair | ctrl | swap | NEG(2,6,9) | NEG7 | NEGALL   (dot_med_d3 / n_d3)")
for pr in pairs:
    row = []
    for lab in ("ctrl","swap1","NEG","NEG7","NEGALL"):
        r = run[lab].get(pr)
        row.append("   -     " if r is None else "%+6.3f/%2d" % (r["dot_med_d3"], int(r["n_d3"])))
    print("%d-%d | %s" % (pr[0], pr[1], " | ".join(row)))
print()
for pr in [(1,2),(1,9),(2,5),(6,7),(7,9)]:
    print(pr, " | ".join("%s gap=%.3f dot07=%d neg=%d" % (lab, run[lab][pr]["gap_min"], int(run[lab][pr]["n_dot07"]), int(run[lab][pr]["n_d3_dotneg"])) for lab in ("ctrl","swap1","NEG","NEG7","NEGALL")))
