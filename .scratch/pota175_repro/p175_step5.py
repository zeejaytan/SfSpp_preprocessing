# 175 step5 render: cloud classes + spread2 walk vs ORIG (eye-check).
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
H = "C:/PR/SfSpp_preprocessing/.scratch/pota175_repro"
OUT = "C:/PR/SfSpp_preprocessing/artifacts/pota175"
d = np.load("C:/PR/SfSpp_preprocessing/.scratch/pota173_repro/p173_bag.npz", allow_pickle=True)
BAG, G0 = d["BAG"], d["G0"]
z = np.load(H + "/p175_probe0.npz")
alB = z["alB"]
TRUE = np.load(H + "/p175_mask_true.npy")
T = BAG[TRUE]
C0 = G0.mean(0); Uu, Ss, Vt = np.linalg.svd(G0-C0, full_matrices=False); e1, e2, nn = Vt[0], Vt[1], Vt[2]
P2 = lambda P: np.c_[ (P-C0).dot(e1),(P-C0).dot(e2)]
Gp, Bp = P2(G0), P2(BAG)
fig, ax = plt.subplots(figsize=(9,9))
ax.scatter(Bp[~TRUE,0], Bp[~TRUE,1], s=8, c="red", alpha=0.5, label="OUTER cloud (155)")
ax.scatter(Bp[TRUE&(alB<-0.5),0], Bp[TRUE&(alB<-0.5),1], s=8, c="blue", alpha=0.6, label="TRUE inner-face (328)")
ax.scatter(Bp[TRUE&(alB>=-0.5),0], Bp[TRUE&(alB>=-0.5),1], s=8, c="green", alpha=0.6, label="TRUE edge (270)")
ax.plot(np.append(Gp[:,0],Gp[0,0]), np.append(Gp[:,1],Gp[0,1]), "k--", lw=1, label="ORIG Bl_0")
ax.set_aspect("equal"); ax.legend(fontsize=8); ax.set_title("p175: two face clouds vs ORIG (top view)")
fig.tight_layout(); fig.savefig(OUT+"/p175_cloud_top.png", dpi=110, bbox_inches="tight"); print("wrote cloud")
seq = np.load(H + "/p175_seed_spread2.npy")
L = T[np.array(seq, dtype=int)]
Lp = P2(L)
fig, ax = plt.subplots(figsize=(9,9))
ax.plot(np.append(Gp[:,0],Gp[0,0]), np.append(Gp[:,1],Gp[0,1]), "k--", lw=1, label="ORIG Bl_0")
sc = ax.scatter(Lp[:,0], Lp[:,1], s=6, c=np.arange(len(Lp)), cmap="plasma", alpha=0.8)
plt.colorbar(sc, ax=ax, label="walk order")
ax.set_aspect("equal"); ax.legend(fontsize=8); ax.set_title("p175: TRUE spread2 walk (553) vs ORIG -- order-colored")
fig.tight_layout(); fig.savefig(OUT+"/p175_walk_top.png", dpi=110, bbox_inches="tight"); print("wrote walk")
# cross-sections: radial(bag-frame) vs axial at 3 angles
cenB = BAG.mean(0)
Ub,Sb,Vtb = np.linalg.svd(BAG-cenB, full_matrices=False); nB = Vtb[2]
rh = (BAG-cenB); rh = rh/np.maximum(np.linalg.norm(rh,axis=1)[:,None],1e-9)
axg = (BAG-cenB).dot(nB)
rr = np.sqrt(np.maximum(((BAG-cenB)**2).sum(-1)-axg**2,0))
ang = np.arctan2((BAG-cenB).dot(Vtb[1]),(BAG-cenB).dot(Vtb[0]))
fig, axes = plt.subplots(1,3, figsize=(14,4.5), sharey=True)
for ax, a0 in zip(axes, [-2.5, -0.5, 1.5]):
    m = np.abs((ang-a0+np.pi)%(2*np.pi)-np.pi) < 0.06
    ax.scatter(rr[m&TRUE&(alB<-0.5)], axg[m&TRUE&(alB<-0.5)], s=10, c="blue", label="inner-face")
    ax.scatter(rr[m&TRUE&(alB>=-0.5)], axg[m&TRUE&(alB>=-0.5)], s=10, c="green", label="edge")
    ax.scatter(rr[m&~TRUE], axg[m&~TRUE], s=10, c="red", label="outer")
    ax.set_xlabel("bag-radius [mm]"); ax.set_title("angle %.1f" % a0); ax.grid(alpha=0.3)
axes[0].set_ylabel("bag-axial [mm]"); axes[0].legend(fontsize=7)
fig.suptitle("p175: cross-sections (radius vs axial) -- track structure")
fig.tight_layout(); fig.savefig(OUT+"/p175_xsec.png", dpi=110, bbox_inches="tight"); print("wrote xsec")
