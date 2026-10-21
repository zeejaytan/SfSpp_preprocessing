import numpy as np, re
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
    seg=np.linalg.norm(np.diff(L,axis=0),axis=1)
    span=np.sqrt(((L[:,None,:]-L[None,:,:])**2).sum(-1)).max()
    print('  %-9s n=%d spCV=%.3f len/span=%.3f'%(t,len(L),seg.std()/seg.mean(),seg.sum()/span),flush=True)
