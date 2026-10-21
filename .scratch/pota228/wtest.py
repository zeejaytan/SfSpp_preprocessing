import numpy as np, re
B='C:/PR/SfSpp_preprocessing/.scratch/'
def loadpcd(p):
    d=open(p,'rb').read().replace(b'\r\n',b'\n')
    h,_,b=d.partition(b'DATA ascii\n')
    m=re.search(r'FIELDS(.*)',h.decode())
    nf=len(m.group(1).split()) if m else 3
    return np.fromstring(b.decode(),sep=' ').reshape(-1,nf)[:,:3]
def loadxyz(p):
    return np.loadtxt(p,usecols=(0,1,2))
def smooth(L,w):
    n=len(L);out=np.empty_like(L);h=w//2
    cs=np.vstack([np.zeros((1,3)),np.cumsum(L,axis=0)])
    for i in range(n):
        a=max(0,i-h);bb=min(n,i+h+1);out[i]=(cs[bb]-cs[a])/(bb-a)
    return out
jobs=[('P27@12/Bl0',loadpcd(B+'pota227/lanes/Pot_D_Piece_27_Breakline_0.pcd')),
('P27@12/Bl1',loadpcd(B+'pota227/lanes/Pot_D_Piece_27_Breakline_1.pcd')),
('P27@4.5/Bl0',loadpcd(B+'pota225/lanes/Pot_D_Piece_27_Breakline_0.pcd')),
('P15@8/Bl0',loadxyz(B+'pota222/lanes/Pot_D_Piece_15_Breakline_0.xyz')),
('P16@10/Bl1',loadxyz(B+'pota222/lanes/Pot_D_Piece_16_Breakline_1.xyz')),
('P01@8/Bl0',loadpcd(B+'.wt-220/artifacts/pota220/p01_8_Bl0.pcd')),
('P12@4.5/Bl0',loadpcd(B+'pota223/lanes/Pot_D_Piece_12_Breakline_0.pcd')),
('P12@4.5/Bl1',loadpcd(B+'pota223/lanes/Pot_D_Piece_12_Breakline_1.pcd')),
('P12@3/Bl1',loadpcd(B+'pota224/lanes/Pot_D_Piece_12_Breakline_1.pcd'))]
for tag,L in jobs:
    sp=np.linalg.norm(np.diff(L,axis=0),axis=1).mean()
    line='%-10s sp=%.2f '%(tag,sp)
    for w in (5,7,9,11):
        r=np.linalg.norm(L-smooth(L,w),axis=1)
        line+='w%d:%.1f/%.1f '%(w,r.max(),(r>2).mean()*100)
    print(line,flush=True)
