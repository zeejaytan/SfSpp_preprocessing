"""POTA-208 fresh-arm strict table (5deg/10mm) + seating render. T attempt frame T_ito_i <-> piece N=i+1. Global Kabsch align of attempt to GT, then per-piece rot/trans error."""
import numpy as np, os
from PIL import Image, ImageDraw

ASM_ART = "C:/PR/structure-from-sherds-pp/artifacts"
FETCH208 = ASM_ART + "/pota208_e2e/pota208_fetch/T_L_fresh"
GTD = ASM_ART + "/pota_restore_e2e/pota_restore_fetch/GT"
MESH = ASM_ART + "/pot_a_mesh_all/Pot_A_Piece_%02d_Mesh.obj"
OUTD = "C:/PR/SfSpp_preprocessing/.scratch/.wt-e2e-pristine/.scratch/pota208_repro"
COLORS = {1:(200,60,50),2:(210,180,140),3:(230,140,40),4:(220,190,60),
          5:(0,150,150),6:(60,160,80),7:(70,120,200),8:(150,80,180)}

def load_T(p):
    return np.loadtxt(p).reshape(4,4)

def kabsch(A, B):
    cA, cB = A.mean(0), B.mean(0)
    H = (A-cA).T @ (B-cB)
    U,_,Vt = np.linalg.svd(H)
    R = Vt.T @ U.T
    if np.linalg.det(R) < 0:
        Vt[-1,:] *= -1; R = Vt.T @ U.T
    return R, cB - R @ cA

def rot_deg(R):
    return float(np.degrees(np.arccos(np.clip((np.trace(R)-1)/2,-1,1))))

def mesh_verts(n, step=150):
    pts = []
    with open(MESH % n) as f:
        for line in f:
            if line.startswith("v "):
                p = line.split()
                pts.append((float(p[1]),float(p[2]),float(p[3])))
    return np.array(pts[::step])

def place(pts, T):
    return pts @ T[:3,:3].T + T[:3,3]

att = [load_T("%s/T_%dto_%d.txt" % (FETCH208,i,i)) for i in range(8)]
gt  = [load_T("%s/Pot_A_Piece_%d_T.txt" % (GTD,n)) for n in range(1,9)]
keep = [i for i in range(8) if i != 0]  # robust: exclude p1 outlier (112deg/271mm off; the assembly's single misplaced sherd)
tA = np.array([att[i][:3,3] for i in keep]); tG = np.array([gt[i][:3,3] for i in keep])
RA, tA2 = kabsch(tA, tG)
print("== STRICT TABLE L-fresh208 (robust align on pieces 2-8 excl p1 outlier, then per-piece err) ==")
print("piece | rot_err_deg | trans_err_mm | strict(<=5deg,<=10mm)")
npass = 0
for i in range(8):
    Re = gt[i][:3,:3].T @ RA @ att[i][:3,:3]
    te = gt[i][:3,3] - (RA @ att[i][:3,3] + tA2)
    rd, tm = rot_deg(Re), float(np.linalg.norm(te))
    ok = (rd <= 5.0 and tm <= 10.0); npass += ok
    print("%d | %.2f | %.2f | %s" % (i+1,rd,tm,"PASS" if ok else "FAIL"))
print("STRICT-SHERD: %d/8" % npass)

clouds_gt, clouds_att = [], []
for i in range(8):
    v = mesh_verts(i+1, 25)
    clouds_gt.append(place(v, gt[i]))
    A = np.eye(4); A[:3,:3]=RA; A[:3,3]=tA2
    clouds_att.append(place(v, A @ att[i]))
allp = np.vstack(clouds_gt+clouds_att)
img = Image.new("RGB",(1600,800),(255,255,255))
dr = ImageDraw.Draw(img)
for panel,(ax,ay) in enumerate([(0,2),(0,1)]):
    x0 = panel*800
    P = allp[:,[ax,ay]]
    mn, mx = P.min(0), P.max(0)
    sc = min(740/(mx[0]-mn[0]),740/(mx[1]-mn[1]))
    def proj(q):
        return (x0+30+(q[:,0]-mn[0])*sc, 770-(q[:,1]-mn[1])*sc)
    gx,gy = proj(np.vstack(clouds_gt))
    for a,b in zip(gx[::2],gy[::2]):
        dr.ellipse([a-2,b-2,a+2,b+2],fill=(180,180,180))
    for i,cl in enumerate(clouds_att):
        qx,qy = proj(cl)
        c = COLORS[i+1]
        for a,b in zip(qx[::2],qy[::2]):
            dr.ellipse([a-2,b-2,a+2,b+2],fill=c)
    dr.text((x0+30,10), ["L-fresh208 side (x-z): GT gray + attempt color",
                         "L-fresh208 top (x-y): GT gray + attempt color"][panel], fill=(0,0,0))
out = OUTD+"/seat_fresh208_vs_gt.png"
img.save(out)
print("render saved:", out, "strict %d/8" % npass)
