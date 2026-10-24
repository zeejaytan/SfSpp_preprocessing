#!/usr/bin/env python3
# a278g.py -- ticket 278: is the band's outer edge a manufactured circle (constant radius) or a wandering fracture?
import numpy as np

def read_dump(path):
    a = np.loadtxt(path, comments='#', dtype=np.float64)
    return a[:, 1].astype(np.int32), a[:, 2:5].astype(np.float64)

def read_pcd(path):
    rows = []
    with open(path, 'r', errors='replace') as f:
        data = False
        for ln in f:
            if not data:
                if ln.startswith('DATA'): data = True
                continue
            p = ln.split()
            if len(p) >= 5: rows.append([float(p[0]), float(p[1]), float(p[2]), float(p[3]), float(p[4]), float(p[5]) if len(p) > 5 else 0.0])
    return np.array(rows)

def frame(axispath):
    p0 = None; d = None
    with open(axispath) as f:
        for ln in f:
            p = ln.split()
            if len(p) < 3: continue
            v = np.array([float(p[0]), float(p[1]), float(p[2])])
            if p0 is None: p0 = v
            else: d = v
    return p0, d/np.linalg.norm(d)

def cyl(P, p0, d):
    rel = P - p0
    ax = rel @ d
    rad = np.linalg.norm(rel - np.outer(ax, d), axis=1)
    return rad, ax

def ang(rel, d):
    # stable angular coordinate around the axis
    e1 = np.array([1.0,0,0]); e1 = e1 - (e1@d)*d; e1 /= np.linalg.norm(e1)
    e2 = np.cross(d, e1)
    return np.arctan2(rel @ e2, rel @ e1)

def prof(tag, P, p0, d, nb=36, label=""):
    rel = P - p0
    rad, ax = cyl(P, p0, d)
    th = ang(rel, d)
    b = ((th + np.pi) / (2*np.pi) * nb).astype(int) % nb
    outr = []; outa = []
    for k in range(nb):
        m = b == k
        if m.sum() < 5: outr.append(np.nan); continue
        outr.append(float(np.percentile(rad[m], 95)))
        outa.append(float(np.percentile(ax[m], 50)))
    o = np.array(outr); o = o[~np.isnan(o)]
    print("== EDGE %s %s n=%d bins=%d/%d outer_radius p50=%.3f min=%.3f max=%.3f spread=%.3f std=%.3f" %
          (tag, label, len(P), len(o), nb, np.median(o), o.min(), o.max(), o.max()-o.min(), o.std()))
    if len(outa):
        a = np.array(outa); print("   bin median axial: p50=%.3f min=%.3f max=%.3f spread=%.3f" % (np.median(a), a.min(), a.max(), a.max()-a.min()))

if __name__ == "__main__":
    R3 = "/data/gpfs/projects/punim2657/SfSpp/runs/20261024-1223_0ab0935_p276-phase3a"
    AUTH = "/data/gpfs/projects/punim2657/sfs_main/original_samples/SfS_pp/Breaklines"
    AX = R3 + "/stage/C03_diag/Dataset/Axes/Pot_C_Piece_03_Axis.xyz"
    p0, d = frame(AX)
    labels, P = read_dump(R3+"/out/C03_diag/mergeDiag276_Pot_C_Piece_03.txt")
    band = P[labels == 2]
    prof("Pot_C_03", band, p0, d, 36, "band c2 (all)")
    # author Bl1 dots that lie within 2 mm of the band
    B = read_pcd(AUTH + "/Pot_C_Piece_03_Breakline_1.pcd")[:, :3].astype(np.float64)
    print("   author Bl1 n=%d" % len(B))
    # nearest band distance via chunking
    def nn(A, Bm):
        out = np.empty(len(A))
        for s in range(0, len(A), 4000):
            e = min(len(A), s+4000)
            dd = A[s:e, None, :] - Bm[None, :, :]
            out[s:e] = np.sqrt(np.min(np.einsum('ijk,ijk->ij', dd, dd, optimize=True), axis=1))
        return out
    dist = nn(B, band)
    Ba = B[dist <= 2.0]
    print("   author Bl1 within 2mm of band: %d (median d %.4f)" % (len(Ba), np.median(dist[dist<=2.0])))
    prof("Pot_C_03", Ba, p0, d, 36, "author Bl1 near band")
    # same for the kept exterior face c1 outer edge, as a reference profile
    prof("Pot_C_03", P[labels == 1], p0, d, 36, "kept exterior c1 (all)")
