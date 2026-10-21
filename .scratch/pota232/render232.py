import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
def load_pcd_xyz(path):
    with open(path) as f: txt = f.read()
    head, data = txt.split('DATA ascii')
    npts = int([l for l in head.splitlines() if l.startswith('WIDTH')][0].split()[1])
    nf = len([l for l in head.splitlines() if l.startswith('FIELDS')][0].split())-1
    arr = np.fromstring(data, sep=' ')
    return arr[:npts*nf].reshape(npts, nf)[:, :3]
L = 'C:/PR/SfSpp_preprocessing/.scratch/pota221/pota221f/lanes/'
A = 'C:/PR/SfSpp_preprocessing/.scratch/pota221/pota221f/author/'
o0 = load_pcd_xyz(A+'Pot_D_Piece_22_Breakline_0.pcd')
o1 = load_pcd_xyz(A+'Pot_D_Piece_22_Breakline_1.pcd')
b0 = load_pcd_xyz(L+'Pot_D_Piece_22_Breakline_0.pcd')
b1 = load_pcd_xyz(L+'Pot_D_Piece_22_Breakline_1.pcd')
auth = np.vstack([o0, o1])
GOLD='#ffae00'; BLUE='#0057ff'
fig = plt.figure(figsize=(15, 7))
for k, (title, xlim, ylim, zlim, elev, azim) in enumerate([
  ('full: gold=author, blue=ours-on-rim, black=ours-off-rim, red ring=turn b1[48]', None, None, None, 20, -120),
  ('zoom corner: turn b1[48] [-4.15,18.58,439.21], lane ends b1[52]', [-14, 4], [12, 30], [434, 448], 18, -115),
]):
    ax = fig.add_subplot(1, 2, k+1, projection='3d')
    ax.scatter(o0[:,0], o0[:,1], o0[:,2], c=GOLD, s=8, label='author')
    ax.scatter(o1[:,0], o1[:,1], o1[:,2], c=GOLD, s=8)
    for lane in (b0, b1):
        d = np.linalg.norm(lane[:,None,:]-auth[None,:,:], axis=2).min(axis=1)
        on = d < 2.0
        ax.scatter(lane[on,0], lane[on,1], lane[on,2], c=BLUE, s=14)
        ax.scatter(lane[~on,0], lane[~on,1], lane[~on,2], c='black', s=14)
    t = b1[48]
    ax.scatter([t[0]], [t[1]], [t[2]], s=260, facecolors='none', edgecolors='red', linewidths=2.5)
    ax.set_title(title, fontsize=9)
    if xlim: ax.set_xlim(xlim[0],xlim[1]); ax.set_ylim(ylim[0],ylim[1]); ax.set_zlim(zlim[0],zlim[1]) 
    ax.view_init(elev=elev, azim=azim)
fig.suptitle('P22 turn-away: SPLIT-OK (author on crease) / turn at S1-UN cluster boundary', fontsize=11)
fig.tight_layout()
fig.savefig('C:/PR/SfSpp_preprocessing/.scratch/pota232/p232_P22_turn.png', dpi=100)
print('saved')
