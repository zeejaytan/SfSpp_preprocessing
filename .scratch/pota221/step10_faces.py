import numpy as np, matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
B = 'C:/PR/SfSpp_preprocessing/.scratch/pota221/'

def load_xyz(p):
    pts = []
    with open(p) as f:
        for ln in f:
            s = ln.split()
            if len(s) >= 3:
                try: pts.append([float(x) for x in s[:3]])
                except ValueError: pass
    return np.array(pts)

def load_pcd(p):
    with open(p, 'rb') as f: data = f.read()
    head, _, body = data.partition(b'DATA ascii\n')
    if not body: head, _, body = data.partition(b'DATA ascii\r\n')
    nf = 3
    for ln in head.decode('ascii', errors='replace').splitlines():
        if ln.startswith('FIELDS'): nf = len(ln.split()) - 1
    return np.fromstring(body.decode('ascii', errors='replace'), sep=' ').reshape(-1, nf)[:, :3]

def dist_to(A, B):
    return np.sqrt((((A[:, None, :] - B[None, :, :]) ** 2).sum(-1)).min(1))

for pc in ['12', '15']:
    S = [load_xyz(B + 'pota221f2/P%s/Pot_D_Piece_%s_Surface_%d.xyz' % (pc, pc, k)) for k in [0, 1]]
    bnd = load_pcd(B + 'pota221f2/P%s/boundary.pcd' % pc)
    L = {b: load_pcd(B + 'pota221f/lanes/Pot_D_Piece_%s_Breakline_%s.pcd' % (pc, b)) for b in ['0', '1']}
    A = {b: load_pcd(B + 'pota221f/author/Pot_D_Piece_%s_Breakline_%s.pcd' % (pc, b)) for b in ['0', '1']}
    print('P%s S0=%d S1=%d bnd=%d' % (pc, len(S[0]), len(S[1]), len(bnd)), flush=True)
    # purity: face dots within 2mm of the OPPOSITE-side author lane (o0~inner/S1-side? use slot-reversed: S0 should avoid o1-side? just report both)
    for k in [0, 1]:
        d0 = (dist_to(S[k], A['0']) < 2.0).mean() * 100
        d1 = (dist_to(S[k], A['1']) < 2.0).mean() * 100
        print('  S%d: near author-o0 %.1f%% near author-o1 %.1f%%' % (k, d0, d1), flush=True)
    # rim overlap: S0 dots within 2mm of any S1 dot
    ov = (dist_to(S[0][::3], S[1]) < 2.0).mean() * 100
    print('  S0 near S1(<=2mm): %.1f%% (subsampled x3)' % ov, flush=True)
    fig, ax = plt.subplots(2, 3, figsize=(18, 11))
    for k in [0, 1]:
        P = S[k][::4]
        ax[k, 0].scatter(P[:, 0], P[:, 1], s=0.5, c='gray')
        ax[k, 0].scatter(bnd[:, 0], bnd[:, 1], s=3, c='black')
        ax[k, 0].scatter(L['0'][:, 0], L['0'][:, 1], s=8, c='red')
        ax[k, 0].scatter(L['1'][:, 0], L['1'][:, 1], s=8, c='orange')
        ax[k, 0].set_title('P%s S%d top XY (gray=face, black=pre, red/orange=lanes)' % (pc, k)); ax[k, 0].set_aspect('equal')
        ax[k, 1].scatter(P[:, 0], P[:, 2], s=0.5, c='gray')
        ax[k, 1].scatter(L['0'][:, 0], L['0'][:, 2], s=8, c='red')
        ax[k, 1].scatter(L['1'][:, 0], L['1'][:, 2], s=8, c='orange')
        ax[k, 1].set_title('P%s S%d side XZ' % (pc, k)); ax[k, 1].set_aspect('equal')
        ax[k, 2].scatter(P[:, 1], P[:, 2], s=0.5, c='gray')
        ax[k, 2].scatter(A['0'][:, 1], A['0'][:, 2], s=8, c='blue')
        ax[k, 2].scatter(A['1'][:, 1], A['1'][:, 2], s=8, c='cyan')
        ax[k, 2].scatter(L['0'][:, 1], L['0'][:, 2], s=8, c='red', marker='x')
        ax[k, 2].scatter(L['1'][:, 1], L['1'][:, 2], s=8, c='orange', marker='x')
        ax[k, 2].set_title('P%s S%d side YZ (blue/cyan=author)' % (pc, k)); ax[k, 2].set_aspect('equal')
    plt.tight_layout(); plt.savefig(B + 'P%s_faces.png' % pc, dpi=80); print('saved P%s_faces.png' % pc, flush=True)
