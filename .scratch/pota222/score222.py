import numpy as np, os
B = 'C:/PR/SfSpp_preprocessing/.scratch/'

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

def med_cov(A, B, thr=2.0):
    d = np.sqrt((((A[:, None, :] - B[None, :, :]) ** 2).sum(-1)).min(1))
    return float(np.median(d)), float((d < thr).mean()), float(d.max())

for pc in ['15', '16']:
    L = [load_xyz(B + 'pota222/lanes/Pot_D_Piece_%s_Breakline_%d.xyz' % (pc, b)) for b in [0, 1]]
    A = [load_pcd(B + 'pota221/pota221f/author/Pot_D_Piece_%s_Breakline_%d.pcd' % (pc, b)) for b in [0, 1]]
    print('refs o0=%d o1=%d' % (len(A[0]), len(A[1])), flush=True)
    m = [[np.median(np.sqrt((((x[:, None, :] - y[None, :, :]) ** 2).sum(-1)).min(1))) for y in A] for x in L]
    print('P%s slot matrix: Bl0->o0 %.2f Bl0->o1 %.2f | Bl1->o0 %.2f Bl1->o1 %.2f' % (pc, m[0][0], m[0][1], m[1][0], m[1][1]), flush=True)
    for b in [0, 1]:
        s = 0 if m[b][0] < m[b][1] else 1
        med, cov, mx = med_cov(L[b], A[s])
        print('  ourBl%d vs o%d: n=%d med=%.2f cov=%.1f max=%.1f %s' % (b, s, len(L[b]), med, cov*100, mx, 'AT-BAR' if (med<2 and cov>=0.90) else 'below-bar'), flush=True)
