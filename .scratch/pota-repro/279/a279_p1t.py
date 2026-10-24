import numpy as np, collections, itertools
R="/data/gpfs/projects/punim2657/SfSpp/runs/20261024-1417_dc869d4_p279-basefaces"
rows=[l.rstrip("\n").split("\t") for l in open(R+"/phase1_scan.tsv")][1:]
cols=open(R+"/phase1_scan.tsv").readline().rstrip("\n").split("\t")
ix={c:i for i,c in enumerate(cols)}
def f(r,c):
    try: return float(r[ix[c]])
    except: return float("nan")
cand=[r for r in rows if not np.isnan(f(r,"bins5"))]
print("cols:", len(cols), "rows", len(rows), "cand", len(cand))

def passes(r, nsel=360, ecv=0.15, l3=0.02, axf=0.30):
    r50=f(r,"r50")
    return (f(r,"nsel")>=nsel and f(r,"bins10")==36 and f(r,"edge_cv")<=ecv
            and f(r,"l3l1")<=l3 and f(r,"ax_spread")<=axf*r50)

byp=collections.defaultdict(list)
for r in cand: byp[r[0]].append(r)
base=[p for p,v in byp.items() if any(passes(r) for r in v)]
print("STRICT passes: %d pieces of %d candidates: %s" % (len(base), len(byp), sorted(base)))
print("per-pot strict:", dict(sorted(collections.Counter(p.split("_")[1] for p in base).items())))
paper={"A":1,"B":1,"C":1,"D":3,"E":4,"F":3,"G":4,"H":5,"I":3,"J":1}
cnt=collections.Counter(p.split("_")[1] for p in base)
print("pot  ours strict / paper actual")
for k in "ABCDEFGHIJ": print("  %s  %d / %d" % (k, cnt.get(k,0), paper[k]))

print("\nSENSITIVITY (pieces passing)")
print("%6s %6s %6s | %s" % ("nsel","edge_cv","l3l1","pieces"))
for nsel,ecv,l3 in itertools.product([150,300,360,600],[0.10,0.15,0.25,0.35],[0.01,0.02,0.05]):
    ps=[p for p,v in byp.items() if any(passes(r,nsel,ecv,l3) for r in v)]
    print("%6d %6.2f %6.2f | %2d  %s" % (nsel,ecv,l3,len(ps), ",".join(sorted(x.replace("Pot_","").replace("_Piece_","").replace("_","") for x in ps))))

print("\nDETAIL for the strict set + loose additions")
keys=["tag","surf","n","nsel","frac_sel","norm_med","dotax_frac95","bins5","bins10","r5","r50","r95",
      "ax5","ax50","ax95","ax_spread","axlo_frac","axhi_frac","edge_r50","edge_cv","l2l1","l3l1","spacing",
      "ref0_med","ref0_p90","ref0_edge_med","ref1_med","ref1_p90","ref1_edge_med"]
print(" ".join("%s" % k for k in keys))
for r in cand:
    nm=r[0].replace("Pot_","").replace("_Piece_","")
    if nm.split("_")[0] in ("A01","C03","J03","B01","D03","H10","H03") and (passes(r) or f(r,"bins10")>=30):
        print(" ".join(("%s" % (r[ix.get(k,-1)] if k in ("tag","surf") else ("%.3f"%f(r,k)))) for k in keys))
