import os, sys, numpy as np
CORPUS = "/data/gpfs/projects/punim2657/sfs_main/original_samples/SfS_pp"
sys.path.insert(0, ".")
from check_ref_drift import load_surface, read_axis
from sfs_axes.normalized import centroid_distance

dists = []
for fn in sorted(os.listdir(os.path.join(CORPUS, "Surfaces"))):
    if fn.endswith("_Surface_0.xyz"):
        stem = fn[:-len("_Surface_0.xyz")]
        rel_path = os.path.join(CORPUS, "Axes", f"{stem}_Axis.xyz")
        if not os.path.isfile(rel_path): continue
        s0 = load_surface(os.path.join(CORPUS, "Surfaces", fn))
        vt = read_axis(rel_path)[:, 0]
        d = centroid_distance(vt, s0)
        dists.append(d)

print(f"Corpus 163 pieces: min d={min(dists):.1f} mm, max d={max(dists):.1f} mm, median d={np.median(dists):.1f} mm, p95={np.percentile(dists, 95):.1f} mm")
