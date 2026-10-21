import numpy as np
def load(p):
    d = open(p, 'rb').read()
    h, _, b = d.partition(b'DATA ascii\n')
    return np.fromstring(b.decode(), sep=' ').reshape(-1, 7)[:, :3]
for k in [0, 1]:
    P = load('C:/PR/SfSpp_preprocessing/.scratch/pota223/lanes/Pot_D_Piece_12_Breakline_%d.pcd' % k)
    seg = __import__('numpy').sqrt(((P[1:] - P[:-1]) ** 2).sum(-1))
    j = __import__('numpy').nonzero(seg > 10)[0]
    gap = float(__import__('numpy').linalg.norm(P[-1] - P[0]))
    print('Bl%d: n=%d jumps=%d jumpmax=%.1f endgap=%.1f' % (k, len(P), len(j), float(seg[j].max()) if len(j) else 0.0, gap))
