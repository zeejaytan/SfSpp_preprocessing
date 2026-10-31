import numpy as np, os, sys
PASS=sys.argv[1] if len(sys.argv)>1 else 'ADAPT'
S='/data/gpfs/projects/punim2657/pota159_repro/C01_'+PASS+'/Pot_C_Piece_01_Breakline_%d.pcd'
F='/data/gpfs/projects/punim2657/pota39_repro/prep/pota39_bundle_C/SfS_pp/Breaklines'
O='/data/gpfs/projects/punim2657/sfs_main/original_samples/SfS_pp'
HDR=('VERSION','FIELDS','SIZE','TYPE','COUNT','WIDTH','HEIGHT','VIEWPOINT','POINTS','DATA')
def load_pcd3(p):
    P=[]
    for ln in open(p):
        s=ln.strip()
        if not s or s[0]=='#' or s.split()[0] in HDR: continue
        try: P.append(list(map(float,s.split()[:3])))
        except: continue
    return np.array(P)
def load_T(b,i): return np.loadtxt(os.path.join(b,'Ground Truth',f'Pot_C_Piece_{i}_T.txt'))
TO=load_T(O,1); TS=load_T(os.path.dirname(F),1)
GO0=load_pcd3(f'{O}/Breaklines/Pot_C_Piece_01_Breakline_0.pcd')@TO[:3,:3].T+TO[:3,3]
GO1=load_pcd3(f'{O}/Breaklines/Pot_C_Piece_01_Breakline_1.pcd')@TO[:3,:3].T+TO[:3,3]
for slot in [0,1]:
    C=load_pcd3((S%slot))
    Cg=C@TS[:3,:3].T+TS[:3,3]
    dd=np.sqrt(((C[1:]-C[:-1])**2).sum(-1))
    print(f'{PASS} Bl_{slot}: n={len(C)} steps max={dd.max():.2f} med={np.median(dd):.2f} n>5mm={int((dd>5).sum())} n>=40mm={int((dd>=40).sum())}')
    for oname,G in [('ORIG-Bl0',GO0),('ORIG-Bl1',GO1)]:
        D=np.sqrt(((Cg[:,None,:]-G[None,:,:])**2).sum(-1)).min(1)
        print(f'  vs {oname}: med={np.median(D):.2f} cov2={100*(D<2).mean():.1f}%')
print('ORIG sizes:', len(GO0), len(GO1))
