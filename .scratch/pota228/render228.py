"""POTA-228 eye-check: P27@12/Bl0 (worst) our-blue vs author-gold, excursion black; P15@8/Bl0 control."""
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D  # noqa
import numpy as np, re
from scipy.spatial import cKDTree
B = 'C:/PR/SfSpp_preprocessing/.scratch/'
W = B + 'pota228/'
GOLD = '#ffae00'; BLUE = '#0057ff'; BLACK = '#000000'
def loadpcd(p):
    d = open(p,'rb').read().replace(b'\r\n', b'\n')
    h, _, b = d.partition(b'DATA ascii\n')
    m = re.search(r'FIELDS(.*)', h.decode())
    nf = len(m.group(1).split()) if m else 3
    return np.fromstring(b.decode(), sep=' ').reshape(-1, nf)[:, :3]
def loadxyz(p): return np.loadtxt(p, usecols=(0, 1, 2))
# worst wandering: P27@12/Bl0 (cov 58.5, max 17.7, runs 0..13 + 52..64 = one seam-spanning excursion)
L = loadpcd(B + 'pota227/lanes/Pot_D_Piece_27_Breakline_0.pcd')
A1 = loadpcd(B + 'pota225/Pot_D_Piece_27_Breakline_1_author.pcd')
A0 = loadpcd(B + 'pota225/Pot_D_Piece_27_Breakline_0_author.pcd')
d0, _ = cKDTree(A0).query(L); d1, _ = cKDTree(A1).query(L)
A = A1 if np.median(d1) < np.median(d0) else A0
d = d1 if np.median(d1) < np.median(d0) else d0  # 209 slot: whole lane vs nearer author lane
off = d >= 2.0
print('P27@12/Bl0 vs author: med=%.2f cov=%.1f max=%.1f off=%d/%d' % (np.median(d), (d < 2).mean()*100, d.max(), off.sum(), len(L)), flush=True)
exc = L[off]
fig = plt.figure(figsize=(18, 6))
ax = fig.add_subplot(131, projection='3d')
ax.scatter(A[:, 0], A[:, 1], A[:, 2], s=6, c=GOLD, label='author')
ax.scatter(L[:, 0], L[:, 1], L[:, 2], s=6, c=BLUE, label='ours P27@12/Bl0')
ax.set_title('P27@12/Bl0 overview (gold=author, blue=ours)\nNO MESH on laptop -- lane-only overlay')
ax.legend(markerscale=2, fontsize=8)
ax2 = fig.add_subplot(132, projection='3d')
ax2.scatter(A[:, 0], A[:, 1], A[:, 2], s=8, c=GOLD)
ax2.scatter(L[:, 0], L[:, 1], L[:, 2], s=8, c=BLUE)
ax2.scatter(exc[:, 0], exc[:, 1], exc[:, 2], s=22, c=BLACK, label='off-rim dots (>=2mm)')
cx, cy, cz = exc.mean(0); R = 18.0
ax2.set_xlim(cx-R, cx+R); ax2.set_ylim(cy-R, cy+R); ax2.set_zlim(cz-R, cz+R)
ax2.set_title('ZOOM excursion (black=%d dots, max %.1fmm)' % (off.sum(), d.max()))
ax2.legend(fontsize=8)
# control: good lane P15@8/Bl0 same treatment
L2 = loadxyz(B + 'pota222/lanes/Pot_D_Piece_15_Breakline_0.xyz')
B0 = loadpcd(B + 'pota221/pota221f/author/Pot_D_Piece_15_Breakline_0.pcd')
B1 = loadpcd(B + 'pota221/pota221f/author/Pot_D_Piece_15_Breakline_1.pcd')
e0, _ = cKDTree(B0).query(L2); e1, _ = cKDTree(B1).query(L2)
C = B1 if np.median(e1) < np.median(e0) else B0
e = e1 if np.median(e1) < np.median(e0) else e0
ax3 = fig.add_subplot(133, projection='3d')
ax3.scatter(C[:, 0], C[:, 1], C[:, 2], s=4, c=GOLD)
ax3.scatter(L2[:, 0], L2[:, 1], L2[:, 2], s=4, c=BLUE)
o2 = L2[e >= 2]
if len(o2): ax3.scatter(o2[:, 0], o2[:, 1], o2[:, 2], s=20, c=BLACK)
ax3.set_title('CONTROL P15@8/Bl0 (med %.2f cov %.1f max %.1f)' % (np.median(e), (e < 2).mean()*100, e.max()))
plt.tight_layout(); plt.savefig(W + 'p228_P27worst_vs_P15control.png', dpi=80)
print('saved p228_P27worst_vs_P15control.png', flush=True)
