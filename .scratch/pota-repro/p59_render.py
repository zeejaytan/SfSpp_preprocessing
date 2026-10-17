"""Ticket 59 render (Arm C run 33264463): GT-seated ORIG rims (gray) vs
EST-seated flagged-fresh rims. Fresh 4/6+3/9: seated [2,3,5,6] green,
piece 4 placed-but-wrong red, piece 1 unplaced (no T file) black.
Eye-check: seated fresh ring tracks the GT ring; P1 absent, P4 off-pot.
"""
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

FETCH = r"C:\PR\SfSpp_preprocessing\artifacts\pota59\fetch_C1\pota59_fetch_F_C"
ORIG = r"C:\PR\SfSpp_preprocessing\artifacts\pota59\orig_F_bl"
SEATED = [2, 3, 5, 6]
MISS = [4]
UNPLACED = [1]


def load_rim_pts(pcd):
    with open(pcd) as f:
        lines = [l.rstrip("\n") for l in f]
    di = next(i for i, l in enumerate(lines) if l.strip() == "DATA ascii")
    return np.array([[float(x) for x in l.split()[:3]]
                      for l in lines[di + 1:] if l.strip()])


def load_T4(path):
    M = np.eye(4)
    rows = []
    with open(path) as f:
        for line in f:
            line = line.strip()
            if line:
                rows.append([float(x) for x in line.split()])
    M[:3, :] = np.array(rows[:3])
    return M


def apply_T(pts, T):
    return pts @ T[:3, :3].T + T[:3, 3]


GT = {i: load_T4(rf"{FETCH}\GT\Pot_F_Piece_{i}_T.txt") for i in range(1, 7)}
EST = {}
for i in range(2, 7):
    EST[i] = load_T4(rf"{FETCH}\T_fresh\T_{i - 1}to_{i - 1}.txt")

fig = plt.figure(figsize=(16, 7))
for k, (ax, title, elev, azim) in enumerate([
        (fig.add_subplot(1, 2, 1, projection="3d"), "top-oblique", 15, -60),
        (fig.add_subplot(1, 2, 2, projection="3d"), "side", 5, 30)]):
    for i in range(1, 7):
        orig = load_rim_pts(rf"{ORIG}\Pot_F_Piece_{i:02d}_Breakline_0.pcd")
        ax.plot(*apply_T(orig, GT[i]).T, color="gray", linewidth=1)
        if i in EST:
            fresh = load_rim_pts(
                rf"{FETCH}\rims_fresh\Pot_F_Piece_{i:02d}_Breakline_0.pcd")
            e = apply_T(fresh, EST[i])
            c = e.mean(axis=0)
            seated = i in SEATED
            ax.plot(e[:, 0], e[:, 1], e[:, 2],
                    color="green" if seated else "red", linewidth=1.0,
                    linestyle="-" if seated else "--")
            ax.text(c[0], c[1], c[2],
                    f"P{i} OK" if seated else f"P{i} MISS",
                    fontsize=9, color="green" if seated else "red")
        else:
            g = apply_T(orig, GT[i]).mean(axis=0)
            ax.text(g[0], g[1], g[2], f"P{i} UNPLACED", fontsize=9,
                    color="black")
    ax.set_title("F flagged-fresh arm C run 33264463, 4/6+3/9 — " + title +
                 "\ngray=GT-seated ORIG rim, green=seated fresh, red=miss")
    ax.set_box_aspect((1, 1, 1))
    ax.view_init(elev=elev, azim=azim)
fig.savefig(r"C:\PR\SfSpp_preprocessing\artifacts\pota59\pota59_seating_F_C1.png",
            dpi=80)
print("saved C:\\PR\\SfSpp_preprocessing\\artifacts\\pota59\\pota59_seating_F_C1.png")
