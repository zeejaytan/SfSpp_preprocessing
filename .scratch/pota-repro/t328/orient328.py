
import numpy as np
IN='artifacts/pota328/in'
def load_ply(p):
    rows=[];hdr=True
    for ln in open(p):
        if hdr:
            if ln.strip()=='end_header': hdr=False
            continue
        t=ln.split()
        if len(t)>=6: rows.append([float(x) for x in t[:6]])
    return np.array(rows)
def load_pcd(p):
    L=open(p).read().splitlines()
    i=[n for n,l in enumerate(L) if l.startswith('DATA')][0]
    rows=[l.split() for l in L[i+1:] if l.strip() and len(l.split())>=6]
    return np.array([[float(x) for x in r[:6]] for r in rows])
def ax(k):
    v=[float(x) for x in open(f'{IN}/gt/Juglet_Piece_{k}_Axis.xyz').read().split()]
    o=np.array(v[-6:-3]); d=np.array(v[-3:]); return o,d/np.linalg.norm(d)
print('piece face  mean_n_r  frac_out  |  line(BL) mean_n_r frac_out   medR')
for k in range(1,10):
    T=np.loadtxt(f'{IN}/gt/Juglet_Piece_{k}_T.txt'); o,d=ax(k)
    row=[f'{k:>2d}']
    for f in (0,1):
        S=load_ply(f'{IN}/geom/Juglet_Piece_{k}.S{f}')
        P=(T[:3,:3]@S[:,:3].T).T+T[:3,3]; N=(T[:3,:3]@S[:,3:6].T).T
        w=P-o; r=w-np.outer(w@d,d); rn=np.linalg.norm(r,axis=1)
        rh=r/rn[:,None]
        dd=np.sum(N*rh,axis=1)
        L=load_pcd(f'{IN}/geom/Juglet_Piece_{k}.Bl{f}')
        PL=(T[:3,:3]@L[:,:3].T).T+T[:3,3]; NL=(T[:3,:3]@L[:,3:6].T).T
        w2=PL-o; r2=w2-np.outer(w2@d,d); rh2=r2/np.maximum(np.linalg.norm(r2,axis=1),1e-9)[:,None]
        dl=np.sum(NL*rh2,axis=1)
        row.append(f'S{f}: {dd.mean():+.3f} {np.mean(dd>0):.2f} | Bl{f}: {dl.mean():+.3f} {np.mean(dl>0):.2f} medR {np.median(rn):.2f}')
    print('  '.join(row))
