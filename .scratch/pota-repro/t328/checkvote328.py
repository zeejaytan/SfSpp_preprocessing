"""checkvote328.py - is the exported line normal exactly the k5 wall mean (my patch), or its global negation (the old per-line vote)?"""
import numpy as np, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import geomio
from scipy.spatial import cKDTree

G = sys.argv[1]
for k in (1, 6, 9):
    for s in (0, 1):
        w, _ = geomio.load_ply(os.path.join(G, 'Juglet_Piece_%d.S%d' % (k, s)))
        b, _, _ = geomio.load_pcd(os.path.join(G, 'Juglet_Piece_%d.Bl%d' % (k, s)))
        t = cKDTree(w[:, :3])
        d, j = t.query(b[:, :3], k=5)
        mean = w[j, 3:6].mean(axis=1)
        nl = np.linalg.norm(mean, axis=1)
        mean = mean / np.where(nl[:, None] < 1e-12, 1.0, nl[:, None])
        dot5 = np.einsum('ij,ij->i', b[:, 3:6], mean)
        d1, j1 = t.query(b[:, :3], k=1)
        dot1 = np.einsum('ij,ij->i', b[:, 3:6], w[j1, 3:6])
        print('piece %d Bl%d n=%d: dot(exported,k5mean) med %+.4f frac>0 %.3f frac<-0.9 %.3f | vs single NN med %+.4f frac>0 %.3f'
              % (k, s, len(dot5), np.median(dot5), (dot5 > 0).mean(), (dot5 < -0.9).mean(),
                 np.median(dot1), (dot1 > 0).mean()))
        neg = np.where(dot5 < 0)[0]
        if 0 < len(neg) < len(dot5):
            print('   negated idx %s of %d' % (neg[:25].tolist(), len(dot5)))
