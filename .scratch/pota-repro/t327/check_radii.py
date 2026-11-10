import os, json
import numpy as np
BASE = os.path.dirname(os.path.abspath(__file__))
WT = os.path.abspath(os.path.join(BASE, "..", "..", ".."))
GEOM = os.path.join(WT, "artifacts", "pota327", "geom")
GT = os.path.join(WT, "artifacts", "pota327", "gt")
def load_ply(p):
    L = open(p).read().splitlines()
    i = [n for n, l in enumerate(L) if l == "end_header"][0]
    nvert = None
    for l in L[:i]:
        if l.startswith("element vertex"): nvert = int(l.split()[2])
    rows = [l.split() for l in L[i+1:i+1+nvert] if l.strip()]
    return np.array([[float(x) for x in r[:6]] for r in rows])
def load_pcd(p):
    L = open(p).read().splitlines()
    i = [n for n, l in enumerate(L) if l.startswith("DATA")][0]
    rows = [l.split() for l in L[i+1:] if l.strip() and len(l.split()) >= 6]
    return np.array([[float(x) for x in r[:6]] for r in rows])
def load_ax(k):
    v = [float(x) for x in open(os.path.join(GT, f"Juglet_Piece_{k}_Axis.xyz")).read().split()]
    return np.array(v[-6:-3]), np.array(v[-3:])
def rad(P, o, d):
    w = P - o
    return np.linalg.norm(w - np.outer(w @ d, d), axis=1)
for k in (1, 6, 7, 9):
    o, d = load_ax(k); d = d/np.linalg.norm(d)
    s0 = load_ply(os.path.join(GEOM, f"Juglet_Piece_{k}.S0"))
    s1 = load_ply(os.path.join(GEOM, f"Juglet_Piece_{k}.S1"))
    b0 = load_pcd(os.path.join(GEOM, f"Juglet_Piece_{k}.Bl0"))
    b1 = load_pcd(os.path.join(GEOM, f"Juglet_Piece_{k}.Bl1"))
    print(k, "S0 r", round(float(rad(s0[:,:3],o,d).mean()),3), "S1 r", round(float(rad(s1[:,:3],o,d).mean()),3),
          "| Bl0 r med", round(float(np.median(rad(b0[:,:3],o,d))),3), "| Bl1 r med", round(float(np.median(rad(b1[:,:3],o,d))),3))
j = json.load(open(os.path.join(WT, "artifacts", "pota327", "census_bar1.json")))
for r in j:
    if r["piece"] in (1,6,7,9):
        print("json", r["piece"], round(r["r_mean_S0"],3), round(r["r_mean_S1"],3), "bl0->S0", round(r["bl0_to_S0"],3), "bl1->S0", round(r["bl1_to_S0"],3), "bl1->S1", round(r["bl1_to_S1"],3))
