
import os, json
import numpy as np, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
H="artifacts/pota328/jobH"; SC=os.path.join(H,"score")
sc={l:json.load(open(os.path.join(SC,l+".json"))) for l in ("T328C_r1","T328C_r2","T66O_r1")}
labels=[("T328C_r1","cured r1","#d1495b",-0.20),("T328C_r2","cured r2","#edae49",0.0),("T66O_r1","shipped control","#00798c",0.20)]
edges=[(e["i"],e["j"]) for e in sc["T328C_r1"]["tables"]["per_edge"]][:19]
xs=np.arange(len(edges))
fig,ax=plt.subplots(figsize=(15.5,7.6))
ax.axhspan(1.4,20,color="#eef4ee",zorder=0); ax.axhline(20,color="#7aa87a",lw=1.2,ls="--",zorder=1)
ax.text(0.15,21.8,"angle gate: < 20 deg (dashed).  Filled dot = also within 50 mm; hollow = angle ok, distance over 50 mm",
        color="#3f6f3f",fontsize=9.8)
for lab,name,col,dx in labels:
    pe=sc[lab]["tables"]["per_edge"][:19]
    deg=np.array([e["deg"] for e in pe]); mm=np.array([e["mm"] for e in pe]); ok=mm<50
    ax.scatter(xs[ok]+dx,deg[ok],s=58,color=col,edgecolor="white",linewidth=0.6,zorder=4,label=name)
    ax.scatter(xs[~ok]+dx,deg[~ok],s=58,facecolor="white",edgecolor=col,linewidth=1.5,zorder=3)
seen=set()
for lab,name,col,dx in labels:
    pe=sc[lab]["tables"]["per_edge"][:19]
    for k in range(19):
        if pe[k]["pass"] and k not in seen:
            seen.add(k)
            tag=("cured r1 and r2" if lab=="T328C_r1" else "shipped control")
            ax.annotate("PASS %s\n%.1f deg / %.0f mm"%(tag,pe[k]["deg"],pe[k]["mm"]),(xs[k],pe[k]["deg"]),
                        textcoords="offset points",xytext=(0,-40),ha="center",fontsize=9,
                        bbox=dict(boxstyle="round,pad=0.28",fc="#fff6cc",ec="#c9b458",lw=0.9),zorder=6)
ax.set_yscale("log"); ax.set_ylim(1.4,420); ax.set_xlim(-0.7,18.7)
ax.set_xticks(xs); ax.set_xticklabels(["%d-%d"%e for e in edges],rotation=60,fontsize=9.5)
ax.set_ylabel("pair rotation error (deg, log scale)"); ax.set_xlabel("directed pair, in the order the assembler returned it")
ax.set_title("Bar 4 - pose error of every directed pair the assembler returned, GT-axes arm (FLOOR 20, NP 9)\n"
             "cured r1 and r2 both clear the gate on 1-8; the shipped control clears it on 1-4. Nothing seats: 0 of 9 pieces in every arm.",
             fontsize=11.5)
ax.grid(alpha=0.25,axis="y"); ax.legend(loc="upper right",fontsize=10,framealpha=0.95)
plt.tight_layout(); plt.savefig("artifacts/pota328/renders/fig5_bar4_edge_errors.png",dpi=140,bbox_inches="tight",facecolor="white")
print("ok")
