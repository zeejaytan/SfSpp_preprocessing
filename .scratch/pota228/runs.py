import numpy as np, re
from scipy.spatial import cKDTree
B='C:/PR/SfSpp_preprocessing/.scratch/'
def loadpcd(p):
    d=open(p,'rb').read().replace(b'\r\n',b'\n')
    h,_,b=d.partition(b'DATA ascii\n')
    m=re.search(r'FIELDS(.*)',h.decode())
    nf=len(m.group(1).split()) if m else 3
    return np.fromstring(b.decode(),sep=' ').reshape(-1,nf)[:,:3]
def loadxyz(p): return np.loadtxt(p,usecols=(0,1,2))
A27=[loadpcd(B+'pota225/Pot_D_Piece_27_Breakline_%d_author.pcd'%i) for i in (0,1)]
A15=[loadpcd(B+'pota221/pota221f/author/Pot_D_Piece_15_Breakline_%d.pcd'%i) for i in (0,1)]
A16=[loadpcd(B+'pota221/pota221f/author/Pot_D_Piece_16_Breakline_%d.pcd'%i) for i in (0,1)]
A01=[loadpcd(B+'.wt-220/artifacts/pota220/p01_author_Bl%d.pcd'%i) for i in (0,1)]
A12=[loadpcd(B+'pota222/p12/auth_Bl%d.pcd'%i) for i in (0,1)]
jobs=[('P27@12/Bl0',B+'pota227/lanes/Pot_D_Piece_27_Breakline_0.pcd',A27,'pcd'),
('P27@12/Bl1',B+'pota227/lanes/Pot_D_Piece_27_Breakline_1.pcd',A27,'pcd'),
('P27@8/Bl0',B+'pota226/lanes/Pot_D_Piece_27_Breakline_0.pcd',A27,'pcd'),
('P27@4.5/Bl1',B+'pota225/lanes/Pot_D_Piece_27_Breakline_1.pcd',A27,'pcd'),
('P15@8/Bl0',B+'pota222/lanes/Pot_D_Piece_15_Breakline_0.xyz',A15,'xyz'),
('P16@10/Bl1',B+'pota222/lanes/Pot_D_Piece_16_Breakline_1.xyz',A16,'xyz'),
('P01@8/Bl0',B+'.wt-220/artifacts/pota220/p01_8_Bl0.pcd',A01,'pcd'),
('P01@8/Bl1',B+'.wt-220/artifacts/pota220/p01_8_Bl1.pcd',A01,'pcd'),
('P12@4.5/Bl0',B+'pota223/lanes/Pot_D_Piece_12_Breakline_0.pcd',A12,'pcd'),
('P12@4.5/Bl1',B+'pota223/lanes/Pot_D_Piece_12_Breakline_1.pcd',A12,'pcd'),
('P12@3/Bl0',B+'pota224/lanes/Pot_D_Piece_12_Breakline_0.pcd',A12,'pcd'),
('P12@3/Bl1',B+'pota224/lanes/Pot_D_Piece_12_Breakline_1.pcd',A12,'pcd')]
for tag,p,A,kind in jobs:
    L=loadxyz(p) if kind=='xyz' else loadpcd(p)
    dd=np.array([cKDTree(a).query(L)[0] for a in A])
    s=0 if float(np.median(dd[0]))<float(np.median(dd[1])) else 1
    d=dd[s]
    bad=np.nonzero(d>=2.0)[0]
    runs=np.split(bad,np.nonzero(np.diff(bad)>1)[0]+1) if len(bad) else []
    info=','.join('%d..%d(mx%.1f)'%(r.min(),r.max(),d[r].max()) for r in runs)
    print('%-10s slot=o%d n=%d med=%.2f cov=%.1f max=%.1f nruns=%d %s'%(tag,s,len(L),np.median(d),(d<2).mean()*100,d.max(),len(runs),info),flush=True)
