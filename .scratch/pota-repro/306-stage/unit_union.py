
import sys, time
import numpy as np
sys.path.insert(0, "C:/PR/worktrees/sfs/306")
from sfs_axes.potsac import run_potsac_union, run_potsac, _worst_surface_cost
from sfs_axes.io_axes import direction_angle_deg

# synthetic: arc of a cylinder, radius 40, axis = z through (10, -5, 0)
rng = np.random.default_rng(7)
def cloud(m, seed):
    r = np.random.default_rng(seed)
    th = r.uniform(0, np.deg2rad(120), m)
    z = r.uniform(0, 60, m)
    x = 10 + 40*np.cos(th); y = -5 + 40*np.sin(th)
    n = np.vstack([np.cos(th), np.sin(th), np.zeros_like(th)])
    return np.vstack([x, y, z, n])
C0 = cloud(700, 1); C1 = cloud(650, 2)
t0 = time.time()
v1 = run_potsac_union(C0, C1, seeds=range(2))
t1 = time.time()
print("K", v1.shape[1], "secs %.1f" % (t1-t0))
print("ang to z:", [round(direction_angle_deg(v1[0:3,i], np.array([0,0,1.0])),2) for i in range(v1.shape[1])])
print("costs:", [round(_worst_surface_cost(v1[:,i], C0, C1),2) for i in range(v1.shape[1])])
v2 = run_potsac_union(C0, C1, seeds=range(2))
print("deterministic:", np.array_equal(v1, v2))
v3 = run_potsac_union(C0, C1, seeds=range(3), max_candidates=2)
print("cap2 K", v3.shape[1], "top-two equal to first two of 2-seed run:",
      np.allclose(v3, v1[:, :2]))
vp = run_potsac(C0, C1, rng=np.random.default_rng(0), step=10)
print("paper chain K", vp.shape[1])
