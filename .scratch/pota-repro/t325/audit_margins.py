import csv, statistics as st
rows = list(csv.DictReader(open(r"C:/PR/worktrees/sfs/325/artifacts/pota325/gate_stats.tsv"), delimiter="\t"))
def f(r, k):
    v = r[k]
    return float(v) if v not in ("", "nan", "None") else float("nan")
def stats(vals):
    vals = sorted(v for v in vals if v == v)
    return len(vals), vals[0], st.median(vals), vals[-1]
for src in ("released", "axes323"):
    sub = [r for r in rows if r["source"] == src and r["pot"] != "JUG"]
    print(f"== {src}  n={len(sub)}")
    for label, k, thr, side in (("u_clr floor 0.05", "u_clr", 0.05, "min"), ("v ceiling 2.5", "v", 2.5, "max"),
                                ("z_frac 0.05", "z_frac", 0.05, "min"), ("u1 = d_c/r_mean", "u1", None, None)):
        n, lo, med, hi = stats(f(r, k) for r in sub)
        print(f"  {label:18s} n={n:4d} min={lo:8.4f} med={med:8.4f} max={hi:9.4f}")
    # d_c / D for the 0.9*diag cone band
    dd = [f(r, "d_c") / f(r, "D") for r in sub]
    n, lo, med, hi = stats(dd)
    print(f"  {'d_c/D (cone 0.9)':18s} n={n:4d} min={lo:8.4f} med={med:8.4f} max={hi:9.4f}")
    base = [r for r in sub if r["is_base_new"] == "1"]
    if base:
        n, lo, med, hi = stats(f(r, "z_frac") for r in base)
        print(f"  base pieces n={len(base)} z_frac min={lo:.4f} med={med:.4f} max={hi:.4f}")
print()
print("margins (released): floor 0.05 -> min u_clr / 0.05 =", round(min(f(r,"u_clr") for r in rows if r["source"]=="released" and r["pot"]!="JUG")/0.05, 2))
print("margins (released): ceiling 2.5 -> 2.5 / max v =", round(2.5/max(f(r,"v") for r in rows if r["source"]=="released" and r["pot"]!="JUG"), 2))
print("margins (released): cone 0.9*D -> 0.9*D / max d_c =", round(0.9/max(f(r,"d_c")/f(r,"D") for r in rows if r["source"]=="released" and r["pot"]!="JUG"), 2))
