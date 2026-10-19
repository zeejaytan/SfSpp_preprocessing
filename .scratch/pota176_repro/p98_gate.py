import numpy as np, os
O='/data/gpfs/projects/punim2657/sfs_main/original_samples/SfS_pp'
S='/data/gpfs/projects/punim2657/pota98_repro/prep/pota98_bundle_C_SXC/SfS_pp'
HDR=('VERSION','FIELDS','SIZE','TYPE','COUNT','WIDTH','HEIGHT','VIEWPOINT','POINTS','DATA')
def load_pcd3(p):
    P=[]
    for ln in open(p):
        s=ln.strip()
        if not s or s[0]=='#' or s.split()[0] in HDR: continue
        try: P.append(list(map(float,s.split()[:3])))
        except: continue
    return np.array(P)
def load_T(b,i):
    for c in (f'Pot_C_Piece_{i}_T.txt',f'Pot_C_Piece_{i:02d}_T.txt'):
        p=os.path.join(b,'Ground Truth',c)
        if os.path.exists(p): return np.loadtxt(p)
    raise FileNotFoundError(c)
def nn_med_share(A,B,chunk=500):
    d=np.concatenate([np.sqrt(((a[:,None,:]-B[None,:,:])**2).sum(-1)).min(axis=1) for a in [A[i:i+chunk] for i in range(0,len(A),chunk)]])
    return float(np.median(d)),float((d<2).mean()*100)
ns={}
for piece,no in [('01',1),('02',2),('03',3),('04',4)]:
    TO=load_T(O,no); TS=load_T(S,no)
    G=load_pcd3(f'{O}/Breaklines/Pot_C_Piece_{piece}_Breakline_0.pcd')@TO[:3,:3].T+TO[:3,3]
    F=load_pcd3(f'{S}/Breaklines/Pot_C_Piece_{piece}_Breakline_0.pcd')@TS[:3,:3].T+TS[:3,3]
    med,share=nn_med_share(F,G)
    d=np.sqrt(((F[1:]-F[:-1])**2).sum(-1)); jumps=sorted([(int(x)+1,round(float(d[x]),1)) for x in np.where(d>5)[0]])
    ns[piece]=len(F)
    print(f'C{piece} SXC-Bl_0 n={len(F)} med={med:.2f} <2mm={share:.1f}% jumps>5={jumps[:4]} GATE={"PASS" if med<2 else "FAIL"}')
print('MIN-NEW-Bl_0(C02,C04) =',min(ns['02'],ns['04']),'DENSIFY-NEEDED=' , min(ns['02'],ns['04'])<=50)
