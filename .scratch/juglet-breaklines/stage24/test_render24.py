
import os, sys, tempfile, numpy as np
here = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(here, "..", "stage24"))
import render24

tmp = tempfile.mkdtemp(prefix="r24test_")
cell = os.path.join(tmp, "cells", "A", "Juglet", "Juglet_Piece_1")
os.makedirs(os.path.join(cell, "surfaces"))
rng = np.random.default_rng(1)

def write_ply(path, xyz):
    n = len(xyz)
    with open(path, "w") as fh:
        fh.write("ply\nformat ascii 1.0\nelement vertex %d\nproperty float x\nproperty float y\nproperty float z\nproperty float nx\nproperty float ny\nproperty float nz\nend_header\n" % n)
        for p in xyz:
            fh.write("%.6f %.6f %.6f 0.0 0.0 1.0\n" % (p[0], p[1], p[2]))

plane = np.column_stack([rng.uniform(0, 30, 400), rng.uniform(0, 20, 400), rng.normal(0, 0.05, 400)])
pcd = os.path.join(tmp, "cloud.pcd")
with open(pcd, "w") as fh:
    fh.write("# .PCD v0.7\nVERSION 0.7\nFIELDS x y z\nSIZE 4 4 4\nTYPE F F F\nCOUNT 1 1 1\nWIDTH %d\nHEIGHT 1\nVIEWPOINT 0 0 0 1 0 0 0\nPOINTS %d\nDATA ascii\n" % (len(plane), len(plane)))
    for p in plane:
        fh.write("%.6f %.6f %.6f\n" % tuple(p))
write_ply(os.path.join(cell, "surfaces", "Juglet_Piece_1_Surface_0.ply"), plane[:150] + [0, 0, 0.4])
write_ply(os.path.join(cell, "surfaces", "Juglet_Piece_1_Surface_1.ply"), plane[150:] + [0, 0, -0.4])
with open(os.path.join(cell, "angle_points.tsv"), "w") as fh:
    fh.write("tag\tpot\tpiece\tcall\tx\ty\tz\tang_deg\tdot\n")
    for call in (0, 1):
        for i, p in enumerate(plane[:120]):
            fh.write("A\tJuglet\tJuglet_Piece_1\t%d\t%.6f\t%.6f\t%.6f\t%.4f\t%.5f\n" % (call, p[0], p[1], p[2], 2.0 * (i % 30), 0.99))

render24.cloud_path = lambda pot, piece: pcd
out = os.path.join(tmp, "renders")
sys.argv = ["render24.py", os.path.join(tmp, "cells"), out, "A", "Juglet/Juglet_Piece_1"]
render24.main()
png = [f for f in os.listdir(out) if f.endswith(".png")]
print("[TEST] png=%s bytes=%d" % (png, os.path.getsize(os.path.join(out, png[0])) if png else -1))
print("[TEST] ok" if png and os.path.getsize(os.path.join(out, png[0])) > 20000 else "[TEST] FAILED")
