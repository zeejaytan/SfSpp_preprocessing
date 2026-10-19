import numpy as np
def load_pcd3(p):
    HDR = ('VERSION','FIELDS','SIZE','TYPE','COUNT','WIDTH','HEIGHT','VIEWPOINT','POINTS','DATA')
    P = []
    for ln in open(p):
        s = ln.strip()
        if not s or s[0] == '#':
            continue
        if s.split()[0] in HDR:
            continue
        try:
            P.append(list(map(float, s.split()[:3])))
        except ValueError:
            continue
    return np.array(P)
cands = ['archive_old_datasets/NURBS_Dataset_20250831/SfS_pp/Breaklines/Pot_A_Piece_02_Breakline_0.pcd','archive_old_datasets/NURBS_Dataset_20250903/SfS_pp/Breaklines/Pot_A_Piece_02_Breakline_0.pcd','.scratch/pota162_repro/pota160_repro/PA_VAR/Pot_A_Piece_02_Breakline_0.pcd']
for src in cands:
    try:
        P = load_pcd3(src)
        print(src, P.shape, P[0].round(3))
    except Exception as e:
        print(src, 'ERR', e)
A = np.loadtxt('.scratch/pota171sbs_repro/P02_ORIG.xyz')[:, :3]
print('REF', A.shape, A[0].round(3))
