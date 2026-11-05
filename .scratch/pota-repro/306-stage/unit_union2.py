
import sys, time
import numpy as np
sys.path.insert(0, "C:/PR/worktrees/sfs/306")
from sfs_axes.potsac import run_potsac_union, _worst_surface_cost
from sfs_axes.io_axes import direction_angle_deg

def cloud(m, seed):
    r = np.random.default_rng(seed)
    th = r.uniform(0, np.deg2rad(120), m)
    z = r.uniform(0, 60, m)
    x = 10 + 40*np.cos(th); y = -5 + 40*np.sin(th)
    n = np.vstack([np.cos(th), np.sin(th), np.zeros_like(th)])
    return np.vstack([x, y, z, n])

C0, C1 = cloud(300, 1), cloud(280, 2)
t0 = time.time()
v1 = run_potsac_union(C0, C1, seeds=1, max_candidates=3)
t1 = time.time()
print("K", v1.shape[1], "secs %.1f" % (t1-t0))
print("ang_to_z", [round(direction_angle_deg(v1[0:3,i], np.array([0,0,1.0])),2) for i in range(v1.shape[1])])
print("costs", [round(_worst_surface_cost(v1[:,i], C0, C1),2) for i in range(v1.shape[1])])
v2 = run_potsac_union(C0, C1, seeds=1, max_candidates=3)
print("deterministic", bool(np.array_equal(v1, v2)))
print("int-vs-range same", bool(np.array_equal(v1, run_potsac_union(C0, C1, seeds=range(1), max_candidates=3))))
