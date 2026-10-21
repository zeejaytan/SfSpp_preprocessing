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
LANES=[('P27@4.5/0',B+'pota225/lanes/Pot_D_Piece_27_Breakline_0.pcd','pcd'),
('P27@4.5/1',B+'pota225/lanes/Pot_D_Piece_27_Breakline_1.pcd','pcd'),
('P27@8/0',B+'pota226/lanes/Pot_D_Piece_27_Breakline_0.pcd','pcd'),
('P27@8/1',B+'pota226/lanes/Pot_D_Piece_27_Breakline_1.pcd','pcd'),
('P27@12/0',B+'pota227/lanes/Pot_D_Piece_27_Breakline_0.pcd','pcd'),
('P27@12/1',B+'pota227/lanes/Pot_D_Piece_27_Breakline_1.pcd','pcd'),
('P15@8/0',B+'pota222/lanes/Pot_D_Piece_15_Breakline_0.xyz','xyz'),
('P15@8/1',B+'pota222/lanes/Pot_D_Piece_15_Breakline_1.xyz','xyz'),
('P16@10/0',B+'pota222/lanes/Pot_D_Piece_16_Breakline_0.xyz','xyz'),
('P16@10/1',B+'pota222/lanes/Pot_D_Piece_16_Breakline_1.xyz','xyz'),
('P01@8/0',B+'.wt-220/artifacts/pota220/p01_8_Bl0.pcd','pcd'),
('P01@8/1',B+'.wt-220/artifacts/pota220/p01_8_Bl1.pcd','pcd'),
('P12@4.5/0',B+'pota223/lanes/Pot_D_Piece_12_Breakline_0.pcd','pcd'),
('P12@4.5/1',B+'pota223/lanes/Pot_D_Piece_12_Breakline_1.pcd','pcd'),
('P12@3/0',B+'pota224/lanes/Pot_D_Piece_12_Breakline_0.pcd','pcd'),
('P12@3/1',B+'pota224/lanes/Pot_D_Piece_12_Breakline_1.pcd','pcd')]
for t,p,k in LANES:
    L=loadxyz(p) if k=='xyz' else loadpcd(p)
    n=len(L); tree=cKDTree(L)
    best=1e9;pair=None
    for i in range(n):
        dd,ii=tree.query(L[i],k=8)
        for d,j in zip(dd[1:],ii[1:]):
            gap=min(abs(i-j),n-abs(i-j))
            if gap>=15 and d<best: best=d;pair=(i,j)
    print('%-9s selfneck=%.2f pair=%s'%(t,best,pair),flush=True)
