
import numpy as np, sys, struct
def read_ply(path):
    with open(path,'rb') as f:
        if f.readline().strip()!=b'ply': raise SystemExit('not ply')
        fmt=f.readline().strip(); n=0; props=[]; ints=[]; in_vert=False
        while True:
            l=f.readline().strip()
            if l.startswith(b'element'):
                parts=l.split()
                if parts[1]==b'vertex': n=int(parts[2]); in_vert=True
                else: in_vert=False
            elif l.startswith(b'property') and in_vert:
                t=parts=l.split()
                props.append((t[1].decode(), t[2].decode() if len(t)>2 else ''))
            elif l==b'end_header': break
        data=f.read()
    if b'binary_little_endian' in fmt:
        dt=[]
        for typ,name in props:
            dt.append({'float':'f4','float32':'f4','double':'f8','int':'i4','int32':'i4','uchar':'u1','uint8':'u1','unsigned_char':'u1','short':'i2'}[typ])
        arr=np.frombuffer(data, dtype=np.dtype([(props[i][1],dt[i]) for i in range(len(props))]), count=n)
        return {p[1]: np.asarray(arr[p[1]], dtype=float) for p in props}
    else:
        txt=data.decode('ascii','replace').strip().split('\n')[:n]
        vals=np.array([[float(x) for x in line.split()] for line in txt])
        return {props[i][1]: vals[:,i] for i in range(len(props))}

def stats(path):
    d=read_ply(path)
    P=np.column_stack([d['x'],d['y'],d['z']])
    N=np.column_stack([d['nx'],d['ny'],d['nz']])
    return P, N

for tag,paths in [('P2',['p2_s0.ply','p2_s1.ply']),('P9',['p9_s0.ply','p9_s1.ply'])]:
    (P0,N0)=stats('C:/PR/SfSpp_preprocessing/artifacts/juglet-p38/'+paths[0])
    (P1,N1)=stats('C:/PR/SfSpp_preprocessing/artifacts/juglet-p38/'+paths[1])
    k0=set(map(lambda r: tuple(np.round(r,4)), P0)); k1=set(map(lambda r: tuple(np.round(r,4)), P1))
    shared=len(k0 & k1)
    print(f"== {tag}: s0 {len(P0)} pts ({len(k0)} distinct), s1 {len(P1)} ({len(k1)} distinct), shared rounded 1e-4: {shared} ({shared/min(len(k0),len(k1)):.3f} of the smaller)")
    mn0=N0.mean(0); mn0/=np.linalg.norm(mn0); mn1=N1.mean(0); mn1/=np.linalg.norm(mn1)
    print(f"   mean-normal dot s0.s1 = {float(mn0@mn1):+.4f}")
    for nm,P,N in (('s0',P0,N0),('s1',P1,N1)):
        m=N.mean(0); m/=np.linalg.norm(m)
        proj=P@m
        print(f"   {nm}: own-normal projection span {proj.max()-proj.min():.3f} mm, p05 {np.percentile(proj,5):.3f} p95 {np.percentile(proj,95):.3f}")
    # through-distance s1 -> s0 with s0's own normal at the nearest point
    from scipy.spatial import cKDTree
    t=cKDTree(P0).query(P1,k=1); d=t[0]; idx=t[1]
    v=P1-P0[idx]; a=N0[idx]; a=a/np.linalg.norm(a,axis=1,keepdims=True)
    ts=np.einsum('ij,ij->i',v,a)
    hist,edges=np.histogram(ts,bins=[-4,-2,-1,-0.2,0.2,1,2,4])
    print("   signed through distance s1->s0 histogram:", dict(zip([f'{edges[i]:.1f}..{edges[i+1]:.1f}' for i in range(len(hist))], hist.tolist())))
