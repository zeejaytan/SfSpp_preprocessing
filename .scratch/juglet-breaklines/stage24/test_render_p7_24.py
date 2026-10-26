import os, sys, tempfile, numpy as np
here = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(here, "..", "stage24"))
import render_p7_24 as R

tmp = tempfile.mkdtemp(prefix="p7test_")
pot, piece = "Juglet", "Juglet_Piece_7"
rng = np.random.default_rng(7)
h, w = 20.0, 25.0

def write_ply(path, xyz, nrm):
    with open(path, "w") as fh:
        fh.write("ply\nformat ascii 1.0\nelement vertex %d\nproperty float x\nproperty float y\nproperty float z\nproperty float nx\nproperty float ny\nproperty float nz\nend_header\n" % len(xyz))
        for p, q in zip(xyz, nrm):
            fh.write("%.6f %.6f %.6f %.6f %.6f %.6f\n" % (p[0], p[1], p[2], q[0], q[1], q[2]))

for tag, sep, flip in (("A", 0.4, False), ("D", 4.49, True)):
    cell = os.path.join(tmp, "cells", tag, pot, piece)
    os.makedirs(os.path.join(cell, "surfaces"))
    n0 = rng.uniform(0, w, 400); m0 = rng.uniform(0, h, 400)
    z0 = 0.30 * n0
    p0 = np.column_stack([n0, m0, z0])
    p1 = np.column_stack([n0, m0, z0 + sep])
    sgn = -1.0 if flip else 1.0
    nrm = np.tile(np.array([-0.30, 0.0, 1.0]) / np.sqrt(1.09) * sgn, (400, 1))
    write_ply(os.path.join(cell, "surfaces", piece + "_Surface_0.ply"), p0, nrm)
    write_ply(os.path.join(cell, "surfaces", piece + "_Surface_1.ply"), p1, nrm)

# a tilted plane mesh z = 0.30 x over the same footprint
gx, gy = np.meshgrid(np.linspace(-2, 27, 30), np.linspace(-2, 22, 30))
V = np.column_stack([gx.ravel(), gy.ravel(), 0.30 * gx.ravel()])
F = []
for j in range(29):
    for i in range(29):
        a = j * 30 + i; b = a + 1; c = a + 30; d = c + 1
        F.append([a, b, d]); F.append([a, d, c])
F = np.array(F)
obj = os.path.join(tmp, "mesh.obj")
with open(obj, "w") as fh:
    for v in V:
        fh.write("v %.6f %.6f %.6f\n" % tuple(v))
    for f in F:
        fh.write("f %d %d %d\n" % (f[0] + 1, f[1] + 1, f[2] + 1))

cloud = np.column_stack([rng.uniform(0, w, 2000), rng.uniform(0, h, 2000), 0.30 * rng.uniform(0, w, 2000)])
pcd = os.path.join(tmp, "cloud.pcd")
with open(pcd, "w") as fh:
    fh.write("# .PCD v0.7\nVERSION 0.7\nFIELDS x y z\nSIZE 4 4 4\nTYPE F F F\nCOUNT 1 1 1\nWIDTH %d\nHEIGHT 1\nVIEWPOINT 0 0 0 1 0 0 0\nPOINTS %d\nDATA ascii\n" % (len(cloud), len(cloud)))
    for p in cloud:
        fh.write("%.6f %.6f %.6f\n" % tuple(p))

R.cloud_path = lambda a, b: pcd
out = os.path.join(tmp, "renders")
sys.argv = ["render_p7_24.py", os.path.join(tmp, "cells"), out, obj, pot + "/" + piece, "A,D"]
R.main()
png = [f for f in os.listdir(out) if f.endswith(".png")]
print("[TEST] png=%s bytes=%d" % (png, os.path.getsize(os.path.join(out, png[0])) if png else -1))
