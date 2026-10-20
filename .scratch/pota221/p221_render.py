"""Render our vs author lane overlays (3 projections) for P12/P15."""
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
def load_pcd(p):
    with open(p, "rb") as f: data = f.read()
    head, _, body = data.partition(b"DATA ascii\n")
    if not body: head, _, body = data.partition(b"DATA ascii\r\n")
    nf = 3
    for line in head.decode("ascii", errors="replace").splitlines():
        if line.startswith("FIELDS"): nf = len(line.split()) - 1
    return np.fromstring(body.decode("ascii", errors="replace"), sep=" ").reshape(-1, nf)[:, :3]
import sys
piece, ldir, adir, out = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4]
o0 = load_pcd(adir + "/Pot_D_Piece_%s_Breakline_0.pcd" % piece)
o1 = load_pcd(adir + "/Pot_D_Piece_%s_Breakline_1.pcd" % piece)
b0 = load_pcd(ldir + "/Pot_D_Piece_%s_Breakline_0.pcd" % piece)
b1 = load_pcd(ldir + "/Pot_D_Piece_%s_Breakline_1.pcd" % piece)
fig, ax = plt.subplots(1, 3, figsize=(18, 6))
for a, (xi, yi, lab) in zip(ax, [(0, 1, "top XY"), (0, 2, "side XZ"), (1, 2, "side YZ")]):
    a.scatter(o0[:, xi], o0[:, yi], s=8, c="blue", label="author o0")
    a.scatter(o1[:, xi], o1[:, yi], s=8, c="cyan", label="author o1")
    a.plot(b0[:, xi], b0[:, yi], "r-", lw=1.2, label="our Bl0")
    a.plot(b1[:, xi], b1[:, yi], "orange", ls="--", lw=1.2, label="our Bl1")
    a.set_title("P%s %s" % (piece, lab)); a.set_aspect("equal"); a.legend(fontsize=8)
fig.tight_layout(); fig.savefig(out, dpi=80)
print("wrote " + out)
