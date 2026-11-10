
import sys, glob, os, json, itertools
import numpy as np, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D  # noqa

H = "artifacts/pota328/jobH"
SC = os.path.join(H, "score")
COLS = ["#d1495b","#00798c","#edae49","#66a182","#6d597a","#b56576","#2e86ab","#8d99ae","#386641"]

def obj_verts(p):
    V=[]
    for ln in open(p, "r", errors="ignore"):
        if ln[:2]=="v ":
            a=ln.split()
            V.append((float(a[1]),float(a[2]),float(a[3])))
    return np.array(V)

def arm_clouds(label, dirname):
    out=[]
    for i in range(1,10):
        g=glob.glob(os.path.join(H,dirname,"*_OBJ_%d.obj"%i))
        if not g: continue
        V=obj_verts(g[0])
        if len(V)>1500:
            V=V[np.linspace(0,len(V)-1,1500).astype(int)]
        out.append((i,V))
    return out

def draw(ax, arm, elev, azim):
    for k,(i,V) in enumerate(arm):
        ax.scatter(V[:,0],V[:,1],V[:,2], s=2.2, c=COLS[(i-1)%9], linewidths=0, alpha=0.95,
                   label=("piece %d"%i) if (elev==18 and azim==30) else None)
    ax.view_init(elev=elev, azim=azim)
    ax.set_xticks([]); ax.set_yticks([]); ax.set_zticks([])
    allv=np.vstack([V for _,V in arm])
    c=allv.mean(0); r=0.55*max(allv.max(0)-allv.min(0))
    ax.set_xlim(c[0]-r,c[0]+r); ax.set_ylim(c[1]-r,c[1]+r); ax.set_zlim(c[2]-r,c[2]+r)
    try: ax.set_box_aspect((1,1,1))
    except Exception: pass
    ax.grid(False)
    for p in (ax.xaxis,ax.yaxis,ax.zaxis): p.pane.set_edgecolor("#dddddd"); p.pane.set_alpha(0.2)
    ax.set_facecolor("white")

cur = arm_clouds("cured", "T328C_r1")
ctl = arm_clouds("ctl", "T66O_r1")

fig = plt.figure(figsize=(19,12.4))
gs = fig.add_gridspec(2,2, height_ratios=[1,1], hspace=0.16, wspace=0.03)

ax=fig.add_subplot(gs[0,0], projection="3d"); draw(ax, cur, 18, 30)
ax.set_title("cured lanes, repeat 1 — the assembler's own output, as returned (8 pieces placed, piece 9 unplaced)", fontsize=11, pad=2)
ax=fig.add_subplot(gs[0,1], projection="3d"); draw(ax, cur, 4, 118)
ax.set_title("same assembly, second view", fontsize=11, pad=2)
ax=fig.add_subplot(gs[1,0], projection="3d"); draw(ax, ctl, 18, 30)
ax.set_title("shipped lanes (t66), control — 8 pieces placed, piece 9 unplaced", fontsize=11, pad=2)
ax=fig.add_subplot(gs[1,1], projection="3d"); draw(ax, ctl, 4, 118)
ax.set_title("same assembly, second view", fontsize=11, pad=2)
for a in fig.axes:
    for t in a.get_xticklabels()+a.get_yticklabels()+a.get_zticklabels(): t.set_visible(False)

fig.suptitle("Ticket 328 bar 4 — Juglet end-to-end through the pristine assembler, GT-axes arm (FLOOR 20, NP 9), the meshes the assembler returned\n"
             "cured r1: sherd 2/9 | edge print 1/18 | directed passes 2/36 | seated 0/9     ·     shipped control: sherd 2/9 | edge print 0/18 | directed passes 1/36 | seated 0/9",
             fontsize=13.5, y=0.985)
plt.savefig("artifacts/pota328/renders/fig4_bar4_seating.png", dpi=140, bbox_inches="tight", facecolor="white")
print("wrote fig4")

# ---- edge error panel
fig2, ax2 = plt.subplots(figsize=(15,7.2))
sc={l:json.load(open(os.path.join(SC,l+".json"))) for l in ("T328C_r1","T328C_r2","T66O_r1")}
labels={"T328C_r1":("cured r1","#d1495b",  -0.18),
        "T328C_r2":("cured r2","#edae49",  0.0),
        "T66O_r1":("shipped control","#00798c", 0.18)}
edges=[(e["i"],e["j"]) for e in sc["T328C_r1"]["tables"]["per_edge"]][:19]
xs=np.arange(len(edges))
ax2.axhspan(0,20,color="#e8f2e8",zorder=0)
ax2.axhline(20,color="#7aa87a",lw=1.2,ls="--",zorder=1)
for lab,(name,col,dx) in labels.items():
    pe=sc[lab]["tables"]["per_edge"][:19]
    deg=[e["deg"] for e in pe]; mm=[e["mm"] for e in pe]
    ax2.scatter(xs+dx, deg, s=52, color=col, edgecolor="white", linewidth=0.7, zorder=3, label=name)
ax2.set_yscale("log"); ax2.set_ylim(1.5, 400)
ax2.set_xticks(xs); ax2.set_xticklabels(["%d-%d"%e for e in edges], rotation=60, fontsize=9)
ax2.set_ylabel("pair rotation error (deg, log)")
ax2.text(0.2, 12.5, "acc305 pass zone: < 20 deg and < 50 mm", color="#3f6f3f", fontsize=10.5)
for i,(lab) in enumerate(["T328C_r1","T66O_r1"]):
    pe=sc[lab]["tables"]["per_edge"][:19]
    for k,e in enumerate(pe):
        if e["pass"]:
            ax2.annotate("PASS\n%.1f deg / %.0f mm"%(e["deg"],e["mm"]), (k, e["deg"]), textcoords="offset points",
                         xytext=(0,-34), ha="center", fontsize=9, color="#111111",
                         bbox=dict(boxstyle="round,pad=0.25", fc="#fff6cc", ec="#c9b458", lw=0.8))
ax2.set_title("Per-pair pose error of the returned assembly, all 19 directed pairs — only 1-8 (cured, both repeats) and 1-4 (control) clear the gate;\n"
              "nothing seats: the seating bar is an own-place chamfer at 4.596 mm and every piece is 50-205 mm from home in both arms", fontsize=11.5)
ax2.grid(alpha=0.25, axis="y"); ax2.legend(loc="upper right", fontsize=10)
plt.tight_layout()
plt.savefig("artifacts/pota328/renders/fig5_bar4_edge_errors.png", dpi=140, bbox_inches="tight", facecolor="white")
print("wrote fig5")
