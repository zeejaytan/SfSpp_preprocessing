import numpy as np, trimesh
base = r"C:/PR/SfSpp_preprocessing/artifacts/visual-qa/"
for p in ["pota300_potC_arms/left_authors.ply", "pota300_potC_arms/right_ours.ply",
          "pota300_potC_c01/c01_seated.ply"]:
    m = trimesh.load(base + p, process=False)
    print(p, len(m.faces), np.round(np.ptp(m.vertices, axis=0), 2),
          np.round(m.vertices.min(0), 2), m.visual.kind,
          np.unique(np.asarray(m.visual.vertex_colors)[:, :3], axis=0).shape[0])
