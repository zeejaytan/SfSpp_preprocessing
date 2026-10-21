import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
R = 2.0
GOLD, BLUE, BLACK = '#ffae00', '#0057ff', 'black'

def load_pcd_xyz(path, skip=11):
    pts = []
    with open(path) as f:
        for i, line in enumerate(f):
            if i < skip:
                continue
            p = line.split()
            if len(p) >= 3:
                try:
                    pts.append([float(p[0]), float(p[1]), float(p[2])])
                except ValueError:
                    pass
    return np.array(pts)

def load_cloud(path):
    xyz, nrm = [], []
    with open(path) as f:
        for i, line in enumerate(f):
            if i < 11:
                continue
            p = line.split()
            if len(p) >= 6:
                xyz.append([float(p[0]), float(p[1]), float(p[2])])
                nrm.append([float(p[3]), float(p[4]), float(p[5])])
    xyz = np.array(xyz); nrm = np.array(nrm)
    nrm = nrm / np.linalg.norm(nrm, axis=1, keepdims=True)
    return xyz, nrm

ours0 = load_pcd_xyz('.scratch/pota227/lanes/Pot_D_Piece_27_Breakline_0.pcd')
ours1 = load_pcd_xyz('.scratch/pota227/lanes/Pot_D_Piece_27_Breakline_1.pcd')
auth0 = load_pcd_xyz('.scratch/pota225/Pot_D_Piece_27_Breakline_0_author.pcd')
auth1 = load_pcd_xyz('.scratch/pota225/Pot_D_Piece_27_Breakline_1_author.pcd')
C, N = load_cloud('artifacts/pota229/Pot_D_Piece_27_Point.pcd')
print('cloud', len(C), 'lanes', len(ours0), len(ours1), len(auth0), len(auth1))

def spread(dots):
    d2 = ((dots[:, None, :] - C[None, :, :]) ** 2).sum(axis=2)
    out = np.full(len(dots), np.nan)
    for i in range(len(dots)):
        m = d2[i] < R * R
        if m.sum() >= 8:
            v = N[m].mean(axis=0)
            out[i] = np.degrees(np.arccos(np.clip(np.linalg.norm(v), 0, 1)))
    return out

def nearest_idx(dots, ref):
    d = np.linalg.norm(dots[:, None, :] - ref[None, :, :], axis=2)
    return d.argmin(axis=1), d.min(axis=1)
rng = np.random.default_rng(229)
all_lanes = np.vstack([ours0, ours1, auth0, auth1])
cand = rng.choice(len(C), 4000, replace=False)
dmin = np.linalg.norm(C[cand][:, None, :] - all_lanes[None, :, :], axis=2).min(axis=1)
interior = cand[dmin > 6.0][:2000]
Sb = spread(C[interior])
base = float(np.nanmedian(Sb))
print('BASELINE face-interior: n=%d med=%.1f deg' % (len(interior), base))
ni0, dn0 = nearest_idx(ours0, auth1)
print('control dn0[20:46] max = %.3f' % float(dn0[20:46].max()))
ctrl_ours = np.arange(20, 46)
ctrl_auth = np.unique(ni0[20:46])
S_ctrl_ours = spread(ours0[ctrl_ours])
S_ctrl_auth = spread(auth1[ctrl_auth])
mco, mca = float(np.nanmedian(S_ctrl_ours)), float(np.nanmedian(S_ctrl_auth))
print('CONTROL ours med=%.1f (n=%d); auth med=%.1f (n=%d)' % (mco, len(ctrl_ours), mca, len(ctrl_auth)))
LINE = base + 15.0
print('DECISION LINE >= %.1f deg (baseline+15)' % LINE)
ctrl_pass = bool((mco >= LINE) and (mca >= LINE))
print('CONTROL:', 'PASS' if ctrl_pass else 'FAIL-BLIND')
disp_ours = np.concatenate([np.arange(0, 14), np.arange(52, 65)])
disp_auth = np.unique(ni0[disp_ours])
S_disp_ours = spread(ours0[disp_ours])
S_disp_auth = spread(auth1[disp_auth])
mdo, mda = float(np.nanmedian(S_disp_ours)), float(np.nanmedian(S_disp_auth))
print('DISPUTED ours-Bl0 med=%.1f (n=%d); author-Bl1 med=%.1f (n=%d)' % (mdo, len(disp_ours), mda, len(disp_auth)))
np.savetxt('.scratch/pota229/p229_numbers.csv', np.array([[base, mco, mca, LINE, float(ctrl_pass), mdo, mda]]), delimiter=',', header='baseline,ctrl_ours,ctrl_auth,line,ctrl_pass,disputed_ours,disputed_auth', comments='')
arc = np.concatenate([[0], np.cumsum(np.linalg.norm(np.diff(ours0, axis=0), axis=1))])
S_all_ours = spread(ours0)
S_all_auth = spread(auth1[ni0])
np.savetxt('.scratch/pota229/p229_profile.csv', np.column_stack([np.arange(len(ours0)), arc, dn0, S_all_ours, S_all_auth]), delimiter=',', header='idx,arc_mm,dist_to_auth,S_ours,S_auth_nearest', comments='')
fig, ax = plt.subplots(2, 1, figsize=(9, 7), sharex=False, gridspec_kw={'height_ratios': [3, 2]})
ax[0].axvspan(arc[0], arc[13], color='0.9')
ax[0].axvspan(arc[52], arc[64], color='0.9')
ax[0].axvspan(arc[20], arc[45], color='0.85')
ax[0].plot(arc, S_all_ours, color=BLUE, lw=1.5, label='ours Bl0')
ax[0].plot(arc, S_all_auth, color=GOLD, lw=1.5, label='author Bl1 (nearest)')
ax[0].axhline(base, color=BLACK, ls='--', lw=1, label='face baseline')
ax[0].axhline(LINE, color=BLACK, ls=':', lw=1, label='decision line')
ax[0].set_ylabel('normal-spread S (deg, r=2mm)')
ax[0].legend(fontsize=8, loc='best')
ax[0].set_title('P27@12 Bl0 sharpness along lane (dense cloud 83k pts)')
ax[0].set_xlabel('arc position (mm)')
ax[1].scatter(C[::20, 0], C[::20, 1], s=0.3, c='0.75')
ax[1].plot(auth1[:, 0], auth1[:, 1], color=GOLD, lw=1.5, label='author Bl1')
ax[1].plot(ours0[:, 0], ours0[:, 1], color=BLUE, lw=1.5, label='ours Bl0')
ax[1].scatter(ours0[disp_ours, 0], ours0[disp_ours, 1], s=18, c=BLUE, zorder=5)
ax[1].set_aspect('equal')
ax[1].set_xlabel('x (mm)')
ax[1].set_ylabel('y (mm)')
ax[1].legend(fontsize=8, loc='best')
fig.tight_layout()
fig.savefig('.scratch/pota229/p229_profile.png', dpi=150)
print('saved png + csvs')
