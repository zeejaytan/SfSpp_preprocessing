"""POTA-228: lane rim-adherence leg candidates (LAPTOP-ONLY, author-free except scorer ref)."""
import numpy as np, csv
from scipy.spatial import cKDTree
B = 'C:/PR/SfSpp_preprocessing/.scratch/'
W = B + 'pota228/'

def load_xyz(p):
    pts = []
    with open(p) as f:
        for ln in f:
            s = ln.split()
            if len(s) >= 3:
                try: pts.append([float(x) for x in s[:3]])
                except ValueError: pass
    return np.array(pts, dtype=np.float64)

def load_pcd(p):
    with open(p, 'rb') as f: data = f.read().replace(b'\r\n', b'\n')
    head, _, body = data.partition(b'DATA ascii\n')
    nf = 3
    for ln in head.decode('ascii', errors='replace').splitlines():
        if ln.startswith('FIELDS'): nf = len(ln.split()) - 1
    return np.fromstring(body.decode('ascii', errors='replace'), sep=' ').reshape(-1, nf)[:, :3].astype(np.float64)

def smooth(L, w):
    # centered moving average with edge shrink (author-free backbone)
    n = len(L); out = np.empty_like(L); h = w // 2
    cs = np.vstack([np.zeros((1, 3)), np.cumsum(L, axis=0)])
    for i in range(n):
        a = max(0, i - h); b = min(n, i + h + 1)
        out[i] = (cs[b] - cs[a]) / (b - a)
    return out

def lane_metrics(L):
    seg = np.linalg.norm(np.diff(L, axis=0), axis=1)
    length = float(seg.sum())
    endgap = float(np.linalg.norm(L[0] - L[-1]))
    maxjump = float(seg.max()) if len(seg) else 0.0
    njumps = int((seg > 10.0).sum())
    res = {}
    for w in (15, 31):
        r = np.linalg.norm(L - smooth(L, w), axis=1)
        res[w] = (float(r.max()), float((r > 2.0).mean() * 100))
    span = float(np.sqrt(((L[:, None, :] - L[None, :, :]) ** 2).sum(-1)).max())
    return dict(n=len(L), length=round(length,1), spCV=round(float(seg.std()/seg.mean()),3),
                lenspan=round(float(seg.sum())/span,3), endgap=round(endgap,1),
                endgap_rel=round(endgap/length,4) if length else 0.0,
                maxjump=round(maxjump,1), njumps=njumps,
                res15max=round(res[15][0],1), res15share=round(res[15][1],1),
                res31max=round(res[31][0],1), res31share=round(res[31][1],1))

def face_metrics(L, faces, bnd):
    out = {}
    if faces is not None:
        F = np.vstack(faces)
        d, _ = cKDTree(F).query(L)
        out['offface_share'] = round(float((d > 2.0).mean()*100),1)
        out['offface_max'] = round(float(d.max()),1)
    else:
        out['offface_share'] = 'NA'; out['offface_max'] = 'NA'
    if bnd is not None:
        d, _ = cKDTree(bnd).query(L)
        out['offbnd_share'] = round(float((d > 2.0).mean()*100),1)
        out['offbnd_max'] = round(float(d.max()),1)
    else:
        out['offbnd_share'] = 'NA'; out['offbnd_max'] = 'NA'
    return out

def author_ref(L, A0, A1):
    rec = []
    for A in (A0, A1):
        d, _ = cKDTree(A).query(L)
        rec.append((float(np.median(d)), float((d<2.0).mean()*100), float(d.max())))
    s = 0 if rec[0][0] < rec[1][0] else 1
    return s, round(rec[s][0],2), round(rec[s][1],1), round(rec[s][2],1)

FACES = {
    'P12@4.5': ([B+'pota222/p12/p12_S0_at4p5.xyz', B+'pota222/p12/p12_S1_at4p5.xyz'], None),
    'P12@3': (None, None),
    'P15@8': ([B+'pota221/pota221f2/P15/Pot_D_Piece_15_Surface_0.xyz',
               B+'pota221/pota221f2/P15/Pot_D_Piece_15_Surface_1.xyz'],
              B+'pota221/pota221f2/P15/boundary.pcd'),
    'P16@10': ([B+'.wt-220/artifacts/pota220/c14_Pot_D_Piece_16_Surface_0.xyz',
                B+'.wt-220/artifacts/pota220/c14_Pot_D_Piece_16_Surface_1.xyz'],
               B+'.wt-220/artifacts/pota220/c14_boundary.pcd'),
    'P01@8': (None, None),
    'P27@4.5': (None, None), 'P27@8': (None, None), 'P27@12': (None, None),
}
LANES = {
    'P27@4.5': (B+'pota225/lanes/Pot_D_Piece_27_Breakline_%d.pcd',
                B+'pota225/Pot_D_Piece_27_Breakline_%d_author.pcd', 'pcd'),
    'P27@8': (B+'pota226/lanes/Pot_D_Piece_27_Breakline_%d.pcd',
              B+'pota225/Pot_D_Piece_27_Breakline_%d_author.pcd', 'pcd'),
    'P27@12': (B+'pota227/lanes/Pot_D_Piece_27_Breakline_%d.pcd',
               B+'pota225/Pot_D_Piece_27_Breakline_%d_author.pcd', 'pcd'),
    'P15@8': (B+'pota222/lanes/Pot_D_Piece_15_Breakline_%d.xyz',
              B+'pota221/pota221f/author/Pot_D_Piece_15_Breakline_%d.pcd', 'mix'),
    'P16@10': (B+'pota222/lanes/Pot_D_Piece_16_Breakline_%d.xyz',
               B+'pota221/pota221f/author/Pot_D_Piece_16_Breakline_%d.pcd', 'mix'),
    'P01@8': (B+'.wt-220/artifacts/pota220/p01_8_Bl%d.pcd',
              B+'.wt-220/artifacts/pota220/p01_author_Bl%d.pcd', 'pcd'),
    'P12@4.5': (B+'pota223/lanes/Pot_D_Piece_12_Breakline_%d.pcd',
                B+'pota222/p12/auth_Bl%d.pcd', 'pcd'),
    'P12@3': (B+'pota224/lanes/Pot_D_Piece_12_Breakline_%d.pcd',
              B+'pota222/p12/auth_Bl%d.pcd', 'pcd'),
}
rows = []
for tag, (lp, ap, kind) in LANES.items():
    A = [load_pcd(ap % 0), load_pcd(ap % 1)]
    flist, bndp = FACES[tag]
    faces = [load_xyz(p) for p in flist] if flist else None
    bnd = load_pcd(bndp) if bndp else None
    for b in (0, 1):
        L = (load_xyz if (kind=='mix' and tag in ('P15@8','P16@10')) else load_pcd)(lp % b)
        m = lane_metrics(L)
        fm = face_metrics(L, faces, bnd)
        s, med, cov, mx = author_ref(L, A[0], A[1])
        rows.append(dict(tag=tag, bl=b, slot=s, **m, **fm, med=med, cov=cov, mx=mx))
    print(tag + ' done', flush=True)
with open(W+'metrics.csv','w',newline='') as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
    w.writeheader(); w.writerows(rows)
print('LANE tag/bl n length endgap endgap_rel maxjump nj res15max/res15sh res31max/res31sh offface_sh/max offbnd_sh/max authslot med cov max')
for r in rows:
    print('%(tag)s/Bl%(bl)d n=%(n)d len=%(length)s eg=%(endgap)s egrel=%(endgap_rel)s mj=%(maxjump)s nj=%(njumps)d r15=%(res15max)s/%(res15share)s r31=%(res31max)s/%(res31share)s offF=%(offface_share)s/%(offface_max)s offB=%(offbnd_share)s/%(offbnd_max)s slot=o%(slot)d med=%(med)s cov=%(cov)s max=%(mx)s' % r)
print('METRICS-OK')
