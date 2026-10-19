import numpy as np, os, sys
sys.path.insert(0, ".scratch/pota176_repro")
from p176_lib import load_obj, load_pcd3
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
H = ".scratch/pota176_repro"
I = os.path.join(H, "inputs"); Rf = os.path.join(H, "refs")
A = "artifacts/pota176"; os.makedirs(A, exist_ok=True)
INFO = {
 "01": dict(n="C01", files=[("TRUE", "p176_C01_TRUE_walk.npy", 211, 0.9492, 92.0)]),
 "02": dict(n="C02", files=[("F0", "p176_C02_F0_walk.npy", 221, 0.6783, 99.5), ("F1", "p176_C02_F1_walk.npy", 312, 0.6314, 99.2)]),
 "03": dict(n="C03", files=[("F0", "p176_C03_F0_walk.npy", 190, 0.6882, 89.7), ("F1", "p176_C03_F1_walk.npy", 119, 0.8525, 91.9)]),
 "04": dict(n="C04", files=[("F0", "p176_C04_F0_walk.npy", 131, 0.7273, 100.0), ("F1", "p176_C04_F1_walk.npy", 146, 0.8134, 99.7)]),
}
REFN = {"01": (211, 230), "02": (221, 313), "03": (191, 120), "04": (131, 146)}
for pc, inf in INFO.items():
    V, F = load_obj("temp_download/Mesh/Pot_C/Pot_C_Piece_%s_Mesh_DS.obj" % pc)
    T = np.loadtxt(os.path.join(I, "Pot_C_Piece_%d_T.txt" % int(pc))); Rr, t = T[:3,:3], T[:3,3]
    Vg = V @ Rr.T + t
    dec = Vg[::5]
    Rdir = Rf if pc != "01" else ".scratch/pota162_repro/sfs_main/original_samples/SfS_pp/Breaklines"
    refs = [load_pcd3(os.path.join(Rdir, "Pot_C_Piece_%s_Breakline_%d.pcd" % (pc, b))) @ Rr.T + t for b in (0, 1)]
    for tag, fn, cov, med, c2 in inf["files"]:
        W = np.load(os.path.join(H, fn))
        fig = plt.figure(figsize=(16, 7))
        for k, (mode, ttl) in enumerate([("walk", "176 walk (red, n=%d)" % len(W)), ("ref", "ORIG reference (green)")]):
            ax = fig.add_subplot(1, 2, k+1, projection="3d")
            ax.scatter(dec[:,0], dec[:,1], dec[:,2], s=0.3, c="lightgray", alpha=0.4)
            if mode == "walk":
                ax.plot(W[:,0], W[:,1], W[:,2], color="red", linewidth=1.2)
                ax.scatter(W[:,0], W[:,1], W[:,2], s=6, c="red")
            else:
                for b, c in [(0, "green"), (1, "blue")]:
                    ax.plot(refs[b][:,0], refs[b][:,1], refs[b][:,2], color=c, linewidth=1.0)
            ax.set_title(ttl)
            ax.set_box_aspect((1, 1, 1))
            ax.view_init(elev=15, azim=-60)
        fig.suptitle("%s %s walk-in-slot-0 vs ORIG: cov=%d med=%.2f <2mm=%.1f%%  (veto-free)" % (inf["n"], tag, cov, med, c2))
        out = os.path.join(A, "p176_%s_%s_walk_vs_ref.png" % (pc, tag))
        fig.savefig(out, dpi=80); plt.close(fig)
        print("saved", out, flush=True)
print("renders done")
