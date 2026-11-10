
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
def ax(k,which='gt'):
    d0='gt' if which=='gt' else 'dsaxis'
    v=[float(x) for x in open(f'{IN}/{d0}/Juglet_Piece_{k}_Axis.xyz').read().split()]
    o=np.array(v[-6:-3]); d=np.array(v[-3:]); return o,d/np.linalg.norm(d)
INT={2:1,6:1,9:1}
print('piece  face: mean(n.rhat) frac_out medR   line: mean frac_out medR   [interior face marked *]')
for k in range(1,10):
    o,d=ax(k); row=[f'{k:>2d}']
    for f in (0,1):
        S=load_ply(f'{IN}/geom/Juglet_Piece_{k}.S{f}')
        P,N=S[:,:3],S[:,3:6]
        w=P-o; r=w-np.outer(w@d,d); rn=np.linalg.norm(r,axis=1); rh=r/rn[:,None]
        dd=np.sum(N*rh,axis=1)
        L=load_pcd(f'{IN}/geom/Juglet_Piece_{k}.Bl{f}')
        w2=L[:,:3]-o; r2=w2-np.outer(w2@d,d); rh2=r2/np.maximum(np.linalg.norm(r2,axis=1),1e-9)[:,None]
        dl=np.sum(L[:,3:6]*rh2,axis=1)
        star='*' if INT.get(k,0)==f else ' '
        row.append(f'S{f}{star} {dd.mean():+.2f} {np.mean(dd>0):.2f} R{np.median(rn):.1f} | Bl{f} {dl.mean():+.2f} {np.mean(dl>0):.2f} R{np.median(np.linalg.norm(r2,axis=1)):.1f}')
    print('   '.join(row))
