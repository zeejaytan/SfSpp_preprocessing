#!/usr/bin/env python
"""ticket 327 bar 4 -- read the three diag326 pair outputs and compare per GT edge.

Control = the untouched copy; SWAPr1/r2 = the same copy with P2/P6/P9 Surface_0<->Surface_1
swapped and Breakline_0 <- the t66 Bl1. Columns of interest: dot_med_d3 (the median
normal-sign of the strict-gate correspondence set; +1 = walls agree) and n_d3 (that set's size).
"""
import json, os
f = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", "artifacts", "pota327", "swap")
f = os.path.abspath(f)
cols = None
run = {}
for lab, fn in (("ctrl", "diag_jug_GTctrl.txt"), ("swap1", "diag_jug_SWAPr1.txt"), ("swap2", "diag_jug_SWAPr2.txt")):
    d = {}
    for l in open(os.path.join(f, fn)):
        if not l.startswith("GTPAIR"):
            continue
        p = l.rstrip("\n").split("\t")
        if p[1] == "y":
            cols = p[3:]
            continue
        d[(int(p[1]), int(p[2]))] = dict(zip(cols, p[3:]))
    run[lab] = d
touching = [(1, 2), (1, 4), (1, 8), (1, 9), (2, 5), (2, 9), (3, 5), (6, 7), (7, 9)]
formerly_bad = [(1, 2), (1, 9), (2, 5), (6, 7), (7, 9)]
print("pair  gap_mm   ctrl dot/n   swap1 dot/n  swap2 dot/n  verdict")
rows = []
for pr in sorted(run["ctrl"]):
    c, s1, s2 = run["ctrl"][pr], run["swap1"].get(pr), run["swap2"].get(pr)
    mark = "TOUCH" if pr in touching else ""
    print(f"{pr[0]}-{pr[1]}  {float(c['gap_min']):8.4f}  {float(c['dot_med_d3']):+7.3f}/{c['n_d3']:>3s}"
          f"  {float(s1['dot_med_d3']):+7.3f}/{s1['n_d3']:>3s}  {float(s2['dot_med_d3']):+7.3f}/{s2['n_d3']:>3s}  {mark}")
    rows.append(dict(pair=f"{pr[0]}-{pr[1]}", touching=pr in touching,
                     gap_mm=float(c["gap_min"]),
                     ctrl_dot=float(c["dot_med_d3"]), ctrl_n=int(c["n_d3"]), ctrl_neg=int(c.get("n_d3_dotneg", -1)),
                     s1_dot=float(s1["dot_med_d3"]), s1_n=int(s1["n_d3"]), s1_neg=int(s1.get("n_d3_dotneg", -1)),
                     s2_dot=float(s2["dot_med_d3"]), s2_n=int(s2["n_d3"]), s2_neg=int(s2.get("n_d3_dotneg", -1))))
print()
print("BAR 4 CHECK (five formerly-failing pairs: swap median >= +0.7 and strict inliers > 0)")
ok = True
for pr in formerly_bad:
    r = [x for x in rows if x["pair"] == f"{pr[0]}-{pr[1]}"][0]
    good = r["s1_dot"] >= 0.7 and r["s1_n"] > 0 and r["s2_dot"] >= 0.7 and r["s2_n"] > 0
    ok &= good
    print(f"  {r['pair']}: ctrl {r['ctrl_dot']:+.3f} (n={r['ctrl_n']}, neg={r['ctrl_neg']}) -> "
          f"swap1 {r['s1_dot']:+.3f} (n={r['s1_n']}, neg={r['s1_neg']}) swap2 {r['s2_dot']:+.3f} (n={r['s2_n']}) "
          f"{'PASS' if good else 'FAIL'}")
print("ALL FIVE PASS:", ok)
print()
print("same-wall reference pairs (should be unchanged):")
for pr in [(1, 4), (1, 8), (2, 9), (3, 5)]:
    r = [x for x in rows if x["pair"] == f"{pr[0]}-{pr[1]}"][0]
    print(f"  {r['pair']}: ctrl {r['ctrl_dot']:+.3f} -> swap1 {r['s1_dot']:+.3f}")
json.dump(rows, open(os.path.join(f, "bar4_pairs.json"), "w"), indent=1)