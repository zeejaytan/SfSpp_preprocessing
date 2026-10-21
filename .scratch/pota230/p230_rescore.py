import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import sys
R = 2.0
GOLD, BLUE, BLACK = '#ffae00', '#0057ff', 'black'
D227 = '.scratch/pota227/lanes/'
D225 = '.scratch/pota225/'
CLOUDP = 'artifacts/pota229/Pot_D_Piece_27_Point.pcd'
OUT = '.scratch/pota230/'

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

ours0 = load_pcd_xyz(D227 + 'Pot_D_Piece_27_Breakline_0.pcd')
ours1 = load_pcd_xyz(D227 + 'Pot_D_Piece_27_Breakline_1.pcd')
auth0 = load_pcd_xyz(D225 + 'Pot_D_Piece_27_Breakline_0_author.pcd')
auth1 = load_pcd_xyz(D225 + 'Pot_D_Piece_27_Breakline_1_author.pcd')
C, N = load_cloud(CLOUDP)
print('cloud', len(C), 'lanes', len(ours0), len(ours1), len(auth0), len(auth1), flush=True)
assert (len(C), len(ours0), len(ours1), len(auth0), len(auth1)) == (83374, 65, 61, 48, 49)

def spread(dots):
    d2 = ((dots[:, None, :] - C[None, :, :]) ** 2).sum(axis=2)
    out = np.full(len(dots), np.nan)
    for i in range(len(dots)):
        m = d2[i] < R * R
        if m.sum() >= 8:
            v = N[m].mean(axis=0)
            out[i] = np.degrees(np.arccos(np.clip(np.linalg.norm(v), 0, 1)))
    return out

def nearest(dots, ref):
    d = np.linalg.norm(dots[:, None, :] - ref[None, :, :], axis=2)
    return d.argmin(axis=1), d.min(axis=1)

# ---- STEP 1: REPRO of 229 (identical code path) ----
rng = np.random.default_rng(229)
all_lanes = np.vstack([ours0, ours1, auth0, auth1])
cand = rng.choice(len(C), 4000, replace=False)
dmin = np.linalg.norm(C[cand][:, None, :] - all_lanes[None, :, :], axis=2).min(axis=1)
interior = cand[dmin > 6.0][:2000]
Sb = spread(C[interior])
base = float(np.nanmedian(Sb))
ni0, dn0 = nearest(ours0, auth1)
ctrl_ours = np.arange(20, 46)
ctrl_auth = np.unique(ni0[20:46])
S_ctrl_ours = spread(ours0[ctrl_ours])
S_ctrl_auth = spread(auth1[ctrl_auth])
mco, mca = float(np.nanmedian(S_ctrl_ours)), float(np.nanmedian(S_ctrl_auth))
LINE = base + 15.0
ctrl_pass = bool((mco >= LINE) and (mca >= LINE))
disp_ours = np.concatenate([np.arange(0, 14), np.arange(52, 65)])
disp_auth = np.unique(ni0[disp_ours])
S_disp_ours = spread(ours0[disp_ours])
S_disp_auth = spread(auth1[disp_auth])
mdo, mda = float(np.nanmedian(S_disp_ours)), float(np.nanmedian(S_disp_auth))
print('REPRO baseline=%.3f (exp 1.294) ctrl=%.2f/%.2f (exp 41.63/41.47) line=%.2f (exp 16.29) disput=%.2f/%.2f (exp 39.22/1.35) pass=%s' % (base, mco, mca, LINE, mdo, mda, ctrl_pass), flush=True)
exp = dict(base=1.2939624557352636, mco=41.63495513189831, mca=41.46665446426134, line=16.293962455735266, mdo=39.22283967437678, mda=1.3501642051729292)
ok = (abs(base-exp['base'])<1e-9 and abs(mco-exp['mco'])<1e-9 and abs(mca-exp['mca'])<1e-9 and abs(LINE-exp['line'])<1e-9 and abs(mdo-exp['mdo'])<1e-9 and abs(mda-exp['mda'])<1e-9 and ctrl_pass)
print('REPRO-CHECK:', 'PASS-EXACT' if ok else 'REPRO-FAIL', flush=True)
if not ok:
    sys.exit(7)
print('control dn0[20:46] max = %.3f' % float(dn0[20:46].max()), flush=True)

# ---- STEP 2: gate FULL author lanes ----
S_a0 = spread(auth0)
S_a1 = spread(auth1)
on0 = ~np.isnan(S_a0) & (S_a0 >= LINE)
on1 = ~np.isnan(S_a1) & (S_a1 >= LINE)
print('AUTH-Bl0 S: med=%.2f on-edge %d/%d (%.1f%%) nan=%d' % (float(np.nanmedian(S_a0)), int(on0.sum()), len(auth0), 100*on0.mean(), int(np.isnan(S_a0).sum())), flush=True)
print('AUTH-Bl1 S: med=%.2f on-edge %d/%d (%.1f%%) nan=%d' % (float(np.nanmedian(S_a1)), int(on1.sum()), len(auth1), 100*on1.mean(), int(np.isnan(S_a1).sum())), flush=True)

def score(ours, auth, onmask, tag):
    ni, dn = nearest(ours, auth)
    med_old = float(np.median(dn)); cov_old = float((dn < 2.0).mean())
    onidx = np.flatnonzero(onmask)
    d_on = np.linalg.norm(ours[:, None, :] - auth[onidx][None, :, :], axis=2).min(axis=1)
    med_new = float(np.median(d_on)); cov_new = float((d_on < 2.0).mean())
    excl = float(1 - onmask.mean())
    print('%s OLD med=%.2f cov=%.1f | NEW med=%.2f cov=%.1f | author-excluded=%.1f%%' % (tag, med_old, 100*cov_old, med_new, 100*cov_new, 100*excl), flush=True)
    return dict(tag=tag, med_old=med_old, cov_old=cov_old, med_new=med_new, cov_new=cov_new, excl=excl, ni=ni, dn=dn, d_on=d_on)

# slots per 209: fB0<->oB1, fB1<->oB0
rA = score(ours0, auth1, on1, 'ours-Bl0 vs auth-Bl1(matched)')
rB = score(ours1, auth0, on0, 'ours-Bl1 vs auth-Bl0(matched)')
# slot sanity (naive pairs should sit at wall thickness)
for nm, o, a in [('ours-Bl0 vs auth-Bl0(naive)', ours0, auth0), ('ours-Bl1 vs auth-Bl1(naive)', ours1, auth1)]:
    _, dd = nearest(o, a)
    print('%s med=%.2f cov=%.1f' % (nm, float(np.median(dd)), 100*float((dd<2).mean())), flush=True)

# ---- STEP 3: our dots opposite excluded segments ----
S_o0 = spread(ours0); S_o1 = spread(ours1)
exclA = ~on1[rA['ni']]   # ours-Bl0 dots whose nearest auth-Bl1 dot is off-edge
exclB = ~on0[rB['ni']]
for tag, S, ex in [('ours-Bl0 in excluded zones', S_o0, exclA), ('ours-Bl1 in excluded zones', S_o1, exclB)]:
    v = S[ex]
    print('%s: n=%d medS=%.2f (>=line %d/%d, nan=%d) -> %s' % (tag, int(ex.sum()), float(np.nanmedian(v)) if ex.sum() else float('nan'), int(((v>=LINE)).sum()) if ex.sum() else 0, int(ex.sum()), int(np.isnan(v).sum()) if ex.sum() else 0, 'ON-EDGE' if ex.sum() and float(np.nanmedian(v))>=LINE else 'OFF-EDGE'), flush=True)

np.savetxt(OUT+'p230_numbers.csv', np.array([[base, mco, mca, LINE, mdo, mda]]), delimiter=',', header='baseline,ctrl_ours,ctrl_auth,line,disputed_ours,disputed_auth', comments='')
with open(OUT+'p230_S_author.csv','w') as f:
    f.write('lane,idx,S,onedge\n')
    for i in range(len(auth0)):
        f.write('Bl0,%d,%.6f,%d\n' % (i, S_a0[i], int(on0[i])))
    for i in range(len(auth1)):
        f.write('Bl1,%d,%.6f,%d\n' % (i, S_a1[i], int(on1[i])))
with open(OUT+'p230_S_ours.csv','w') as f:
    f.write('lane,idx,S\n')
    for i in range(len(ours0)):
        f.write('Bl0,%d,%.6f\n' % (i, S_o0[i]))
    for i in range(len(ours1)):
        f.write('Bl1,%d,%.6f\n' % (i, S_o1[i]))
with open(OUT+'p230_rescore.csv','w') as f:
    f.write('lane,med_old,cov_old,med_new,cov_new,author_excluded\n')
    for r in (rA, rB):
        f.write('%s,%.4f,%.4f,%.4f,%.4f,%.4f\n' % (r['tag'], r['med_old'], r['cov_old'], r['med_new'], r['cov_new'], r['excl']))

# ---- picture: 2 rows (one per matched pair): profile + map; gold/blue/black only ----
arc0 = np.concatenate([[0], np.cumsum(np.linalg.norm(np.diff(ours0, axis=0), axis=1))])
arc1 = np.concatenate([[0], np.cumsum(np.linalg.norm(np.diff(ours1, axis=0), axis=1))])
S_all_o0 = S_o0; S_all_o1 = S_o1
fig, ax = plt.subplots(2, 2, figsize=(12, 8))
# row 0: ours-Bl0 vs auth-Bl1
a = ax[0,0]
a.plot(arc0, S_all_o0, color=BLUE, lw=1.2, label='ours Bl0 S')
a.scatter(arc0, S_all_o0, color=BLUE, s=8, zorder=4)
a.axhline(base, color=BLACK, ls='--', lw=1, label='face baseline')
a.axhline(LINE, color=BLACK, ls=':', lw=1, label='decision line')
a.set_ylabel('S (deg)'); a.set_xlabel('arc (mm)'); a.legend(fontsize=7); a.set_title('ours-Bl0 sharpness (all on-edge, med %.1f)' % float(np.nanmedian(S_all_o0)))
m = ax[0,1]
m.scatter(C[::20, 0], C[::20, 1], s=0.3, c='0.75')
m.plot(auth1[:,0], auth1[:,1], color=GOLD, lw=1.2, label='author Bl1 on-edge')
off1 = np.flatnonzero(~on1)
m.scatter(auth1[off1,0], auth1[off1,1], s=22, c=BLACK, zorder=5, label='author Bl1 OFF-edge (excluded)')
m.plot(ours0[:,0], ours0[:,1], color=BLUE, lw=1.2, label='ours Bl0')
m.set_aspect('equal'); m.legend(fontsize=7); m.set_title('plan map Bl0 (excluded black)')
# row 1: ours-Bl1 vs auth-Bl0
a = ax[1,0]
a.plot(arc1, S_all_o1, color=BLUE, lw=1.2, label='ours Bl1 S')
a.scatter(arc1, S_all_o1, color=BLUE, s=8, zorder=4)
a.axhline(base, color=BLACK, ls='--', lw=1)
a.axhline(LINE, color=BLACK, ls=':', lw=1)
a.set_ylabel('S (deg)'); a.set_xlabel('arc (mm)'); a.legend(fontsize=7); a.set_title('ours-Bl1 sharpness (med %.1f)' % float(np.nanmedian(S_all_o1)))
m = ax[1,1]
m.scatter(C[::20, 0], C[::20, 1], s=0.3, c='0.75')
m.plot(auth0[:,0], auth0[:,1], color=GOLD, lw=1.2, label='author Bl0 on-edge')
off0 = np.flatnonzero(~on0)
m.scatter(auth0[off0,0], auth0[off0,1], s=22, c=BLACK, zorder=5, label='author Bl0 OFF-edge (excluded)')
m.plot(ours1[:,0], ours1[:,1], color=BLUE, lw=1.2, label='ours Bl1')
m.set_aspect('equal'); m.legend(fontsize=7); m.set_title('plan map Bl1 (excluded black)')
fig.suptitle('P27 rescore: author gated by sharpness (line %.1f deg); black = off-edge, invisible to scorer)' % LINE)
fig.tight_layout()
fig.savefig(OUT+'p230_rescore.png', dpi=150)
print('saved p230 outputs', flush=True)
