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
def smooth(L,w):
    n=len(L);out=np.empty_like(L);h=w//2
    cs=np.vstack([np.zeros((1,3)),np.cumsum(L,axis=0)])
    for i in range(n):
        a=max(0,i-h);bb=min(n,i+h+1);out[i]=(cs[bb]-cs[a])/(bb-a)
    return out
def maxrun(mask):
    best=0;cur=0
    for v in mask:
        cur=cur+1 if v else 0;best=max(best,cur)
    return best
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
DATA={t:(loadxyz(p) if k=='xyz' else loadpcd(p)) for t,p,k in LANES}
for w in (15,21,25,31,41):
    print('== backbone w=%d: maxrun(resid>thr) / maxresid ==' % w)
    for t,L in DATA.items():
        r=np.linalg.norm(L-smooth(L,w),axis=1)
        print('  %-9s maxr=%5.1f r3=%2d r4=%2d r5=%2d r6=%2d'%(t,r.max(),maxrun(r>3),maxrun(r>4),maxrun(r>5),maxrun(r>6)),flush=True)
