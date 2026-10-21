import numpy as np
def load_pcd(path, stride=None):
    with open(path) as f: txt = f.read()
    head, data = txt.split('DATA ascii')
    npts = int([l for l in head.splitlines() if l.startswith('WIDTH')][0].split()[1])
    nf = len([l for l in head.splitlines() if l.startswith('FIELDS')][0].split())-1
    arr = np.fromstring(data, sep=' ')
    arr = arr[:npts*nf].reshape(npts, nf)
    return arr[:, :3], head
A = 'C:/PR/SfSpp_preprocessing/.scratch/pota221/pota221f/author/'
L = 'C:/PR/SfSpp_preprocessing/.scratch/pota221/pota221f/lanes/'
o0, h0 = load_pcd(A+'Pot_D_Piece_22_Breakline_0.pcd')
o1, h1 = load_pcd(A+'Pot_D_Piece_22_Breakline_1.pcd')
b0, _ = load_pcd(L+'Pot_D_Piece_22_Breakline_0.pcd')
b1, _ = load_pcd(L+'Pot_D_Piece_22_Breakline_1.pcd')
print('n:', o0.shape, o1.shape, b0.shape, b1.shape)
print('author o0 comments:', [l for l in h0.splitlines() if l.startswith('#')])
print('author o1 comments:', [l for l in h1.splitlines() if l.startswith('#')])
def dist_to(a, b):
    return np.linalg.norm(a[:,None,:]-b[None,:,:], axis=2).min(axis=1)
def med_cov(ours, auth):
    d = dist_to(ours, auth)
    return float(np.median(d)), float((d<2.0).mean()*100), d
print('slot matrix (med/cov):')
for name, ours in [('b0',b0),('b1',b1)]:
    for an, auth in [('o0',o0),('o1',o1)]:
        m,c,_ = med_cov(ours, auth)
        print(f'  {name}->{an}: med {m:.2f} cov {c:.1f}')
for name, lane in [('b0',b0),('b1',b1),('o0',o0),('o1',o1)]:
    sp = np.linalg.norm(np.diff(lane,axis=0),axis=1)
    print(f'{name} spacing: med {np.median(sp):.2f} max {sp.max():.2f} njump>10 {(sp>10).sum()}')
auth_all = np.vstack([o0,o1])
for name, lane in [('b0',b0),('b1',b1)]:
    d = dist_to(lane, auth_all)
    print(f'{name} n={len(lane)} dist-to-either: min {d.min():.2f} max {d.max():.2f} nover {(d>2.0).sum()}')
    print('  idx:dist = ' + ' '.join(f'{i}:{v:.1f}' for i,v in enumerate(d)))
