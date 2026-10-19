import numpy as np, os
from scipy.spatial import cKDTree
from collections import Counter
H = ".scratch/pota172_repro"
OUT = "artifacts/pota172"
log = open(os.path.join(H, "p172_step0.txt"), "w")
def say(s):
    print(s, flush=True); log.write(s + "\n")

def load_obj(path):
    V, F = [], []
    with open(path) as fh:
        for ln in fh:
            if ln.startswith("v "):
                V.append([float(x) for x in ln.split()[1:4]])
            elif ln.startswith("f "):
                F.append([int(x.split("/")[0]) - 1 for x in ln.split()[1:4]])
    return np.array(V), np.array(F, dtype=np.int64)

def load_pcd3(p):
    HDR = ('VERSION','FIELDS','SIZE','TYPE','COUNT','WIDTH','HEIGHT','VIEWPOINT','POINTS','DATA')
    P = []
    for ln in open(p):
        s = ln.strip()
        if not s or s[0] == '#' or s.split()[0] in HDR: continue
        try: P.append(list(map(float, s.split()[:3])))
        except ValueError: continue
    return np.array(P)

T = np.loadtxt(".scratch/pota162_repro/sfs_main/original_samples/SfS_pp/Ground Truth/Pot_C_Piece_1_T.txt")
R, t = T[:3,:3], T[:3,3]
V, F = load_obj("temp_download/Mesh/Pot_C/Pot_C_Piece_01_Mesh_DS.obj")
say("mesh local verts %d faces %d" % (len(V), len(F)))
assert (len(V), len(F)) == (11875, 23114)
Vg = V @ R.T + t
G0 = load_pcd3(".scratch/pota162_repro/sfs_main/original_samples/SfS_pp/Breaklines/Pot_C_Piece_01_Breakline_0.pcd") @ R.T + t
assert G0.shape == (211, 3)
say("G0 %s" % (G0.shape,))
S = np.loadtxt(".scratch/pota163_repro/inputs/C01S0_STAGED.xyz")
Xg = S[:,:3] @ R.T + t
say("S0 staged n=%d" % len(Xg))
assert len(Xg) == 11165

EC = Counter()
for f in F:
    for a, b in [(f[0],f[1]),(f[1],f[2]),(f[2],f[0])]:
        EC[tuple(sorted((a,b)))] += 1
bnd = [e for e, c in EC.items() if c == 1]
say("boundary edges %d (expect 636)" % len(bnd))
assert len(bnd) == 636
A = Vg[np.array([e[0] for e in bnd])]
B = Vg[np.array([e[1] for e in bnd])]

runs = [(0,1),(3,21),(23,30),(34,68),(72,81),(83,88),(93,124),(126,136),(139,143),(145,147),(151,156),(158,203),(206,210)]
gidx = np.concatenate([np.arange(a,b+1) for a,b in runs])
say("gap stations n=%d" % len(gidx))
G = G0[gidx]

KX = cKDTree(Xg)
d_sheet = KX.query(G)[0]
csv = np.genfromtxt(".scratch/pota169_repro/p169_gapstations.csv", delimiter=",", skip_header=1)
csv_d = {}
for row in csv:
    csv_d[int(row[0])] = row[2]
mine = np.array([csv_d[int(i)] for i in gidx])
say("sheet_d reproduce CSV: max abs diff = %.6f" % np.abs(d_sheet - mine).max())
assert np.abs(d_sheet - mine).max() < 1e-6

def pt_seg(P, A, B):
    AB = B - A
    denom = np.einsum('ij,ij->i', AB, AB)
    tt = np.einsum('ij,ij->i', P[None,:] - A, AB) / np.maximum(denom, 1e-12)
    tt = np.clip(tt, 0, 1)
    C = A + tt[:,None] * AB
    return np.sqrt(((P[None,:] - C)**2).sum(1)).min()
d_bnd = np.array([pt_seg(p, A, B) for p in G])
say("d_bnd: min %.2f med %.2f max %.2f" % (d_bnd.min(), np.median(d_bnd), d_bnd.max()))

M = len(G); K = len(F)
d_surf = np.full(M, np.inf)
Vf = Vg[F]
CH = 2000
def segd(P_, A_, B_):
    AB_ = B_ - A_
    den = np.einsum('cj,cj->c', AB_, AB_)[None,:]
    tt = np.einsum('cj,mcj->mc', AB_, P_[:,None,:] - A_[None,:,:]) / np.maximum(den, 1e-24)
    tt = np.clip(tt, 0, 1)
    C_ = A_[None,:,:] + tt[:,:,None]*AB_[None,:,:]
    return np.sqrt(((P_[:,None,:]-C_)**2).sum(-1))
for s in range(0, K, CH):
    T0 = Vf[s:s+CH,0]; T1 = Vf[s:s+CH,1]; T2 = Vf[s:s+CH,2]
    e0 = T1-T0; e1 = T2-T0
    a1 = np.einsum('cj,cj->c', e0, e0)[None,:]
    b1 = np.einsum('cj,cj->c', e0, e1)[None,:]
    c1 = np.einsum('cj,cj->c', e1, e1)[None,:]
    dv = T0[None,:,:] - G[:,None,:]
    d_ = np.einsum('cj,mcj->mc', e0, dv)
    e_ = np.einsum('cj,mcj->mc', e1, dv)
    det1 = np.maximum(a1*c1 - b1*b1, 1e-24)
    s1 = (b1*e_ - c1*d_) / det1
    t1 = (b1*d_ - a1*e_) / det1
    inside = (s1 >= 0) & (t1 >= 0) & (s1 + t1 <= 1)
    n = np.cross(e0, e1)
    nlen = np.sqrt(np.einsum('cj,cj->c', n, n))[None,:]
    dist_plane = np.abs(np.einsum('cj,mcj->mc', n, dv)) / np.maximum(nlen, 1e-24)
    d_out = np.minimum(np.minimum(segd(G,T0,T1), segd(G,T0,T2)), segd(G,T1,T2))
    d_chunk = np.where(inside, dist_plane, d_out)
    d_surf = np.minimum(d_surf, d_chunk.min(1))
    print("chunk", s, flush=True)
say("d_surf(mesh triangles): min %.3f med %.3f max %.3f" % (d_surf.min(), np.median(d_surf), d_surf.max()))
say("mesh-surf <1mm %.3f <2mm %.3f <5mm %.3f" % (float((d_surf<1).mean()), float((d_surf<2).mean()), float((d_surf<5).mean())))
np.savez(os.path.join(H, "p172_meshgap.npz"), gidx=gidx, d_sheet=d_sheet, d_bnd=d_bnd, d_surf=d_surf, runs=np.array(runs))
with open(os.path.join(H, "p172_gapstations.csv"), "w") as fh:
    fh.write("# station,run,sheet_d,mesh_surf_d,mesh_bnd_d,verdict\n")
    k = 0
    for ri,(a,b) in enumerate(runs):
        for st in range(a, b+1):
            v = "MESH-HAS-IT" if d_surf[k] < 2.0 else "MESH-MISSING"
            fh.write("%d,%d,%.4f,%.4f,%.4f,%s\n" % (st, ri, d_sheet[k], d_surf[k], d_bnd[k], v))
            k += 1
say("--- per-run ---")
for ri,(a,b) in enumerate(runs):
    m = (gidx >= a) & (gidx <= b)
    ds = d_sheet[m]; dm = d_surf[m]; db = d_bnd[m]
    n_has = int((dm < 2.0).sum())
    v = "MESH-HAS-IT" if n_has == m.sum() else ("MESH-PARTIAL %d/%d" % (n_has, m.sum()) if n_has else "MESH-MISSING")
    say("R%-2d (%3d..%3d n=%2d): sheet min %.2f med %.2f | mesh min %.3f med %.3f max %.3f | bnd min %.1f | lt2 %d/%d -> %s" % (
        ri, a, b, m.sum(), ds.min(), float(np.median(ds)), dm.min(), float(np.median(dm)), dm.max(), db.min(), n_has, m.sum(), v))
say("saved p172_meshgap.npz + p172_gapstations.csv")
log.close(); print("STEP0 DONE")
