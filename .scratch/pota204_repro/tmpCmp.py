import numpy as np
a = np.load(".scratch/pota186_repro/p186_C01_thin_walk.npy")
b = np.load(".scratch/pota204_repro/p204_C01_true_walk.npy")
c = np.load(".scratch/pota204_repro/p204_C01_true_seated.npy")
print("p186", a.shape, "mean", a.mean(0).round(2))
print("maxdiff p186-vs-Tframe:", float(np.abs(a-b).max()) if a.shape==b.shape else "shape-mismatch")
print("maxdiff p186-vs-seated:", float(np.abs(a-c).max()) if a.shape==c.shape else "shape-mismatch")
