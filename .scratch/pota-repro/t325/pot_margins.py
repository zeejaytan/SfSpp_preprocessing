import csv, statistics as st
p="/data/gpfs/projects/punim2657/SfSpp/runs/20261110-1416_22151d0_t325-measure/out/gate_stats.tsv"
rows=list(csv.DictReader(open(p), delimiter="\t"))
def f(r,k): return float(r[k])
pot=[r for r in rows if r["source"]=="released"]
jug=[r for r in rows if r["source"]=="juglet_gt"]
def summ(name, sub, key):
    xs=sorted(f(r,key) for r in sub)
    print(f"{name:12s} n={len(xs):3d} min {xs[0]:8.2f} p10 {xs[len(xs)//10]:8.2f} med {st.median(xs):8.2f} p90 {xs[9*len(xs)//10]:8.2f} max {xs[-1]:8.2f}")
print("== D (bbox diagonal, mm) ==")
summ("pots", pot, "D"); summ("juglet", jug, "D")
print("== r_mean (mm) ==")
summ("pots", pot, "r_mean"); summ("juglet", jug, "r_mean")
print("== floor in mm = 0.05*r_mean, vs old 25 mm ==")
for label, sub in (("pots",pot),("juglet",jug)):
    xs=sorted(0.05*f(r,"r_mean") for r in sub)
    print(f"{label:8s} n={len(xs):3d} min {xs[0]:6.2f} med {st.median(xs):6.2f} max {xs[-1]:6.2f}   old floor 25.0 mm")
print("== ceiling in mm = 2.5*D, vs old 250 mm ==")
for label, sub in (("pots",pot),("juglet",jug)):
    xs=sorted(2.5*f(r,"D") for r in sub)
    print(f"{label:8s} n={len(xs):3d} min {xs[0]:7.1f} med {st.median(xs):7.1f} max {xs[-1]:7.1f}   old cap 250.0 mm")
print("== Juglet GT u_clr vs floor 0.05, margin x ==")
for r in sorted(jug, key=lambda r:r["stem"]):
    u=f(r,"u_clr"); print(f"  {r['stem']:18s} u_clr {u:.3f}  margin x{u/0.05:.2f}  v {f(r,'v'):.2f}")
