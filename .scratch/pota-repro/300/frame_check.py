import json
from collections import defaultdict
from pathlib import Path
import numpy as np
from scipy.spatial import cKDTree

ROOT = Path(r"C:/PR/SfSpp_preprocessing/artifacts/pota300")
IN = ROOT / "inputs" / "stage"; CORPUS = IN / "corpus"

def load_obj(path):
    vs, fs = [], []
    for line in open(path, "r", errors="ignore"):
        if line.startswith("v "): vs.append([float(x) for x in line.split()[1:4]])
        elif line.startswith("f "):
            idx = [int(t.split("/")[0]) for t in line.split()[1:]]
            for k in range(1, len(idx)-1): fs.append([idx[0], idx[k], idx[k+1]])
    return np.asarray(vs, float), np.asarray(fs, np.int64)-1

def load_axis(p):
    a = np.loadtxt(p).ravel(); return a[:3], a[3:6]/np.linalg.norm(a[3:6])

V, F = load_obj(CORPUS / "Mesh" / "Pot_C_Piece_01_Mesh_DS.obj")
S0 = np.loadtxt(IN/"prep_geom"/"Pot_C_Piece_01.S0.xyz", usecols=(0,1,2))
S1 = np.loadtxt(IN/"prep_geom"/"Pot_C_Piece_01.S1.xyz", usecols=(0,1,2))
t0, t1 = cKDTree(S0), cKDTree(S1)
idx = np.random.default_rng(0).choice(len(V), 3000, replace=False)
d0,_ = t0.query(V[idx]); d1,_ = t1.query(V[idx]); d = np.minimum(d0,d1)
print("mesh vertex -> nearest surface-cloud point (mm): median %.3f p90 %.3f p99 %.3f, frac<0.5mm %.3f" % (
    np.median(d), np.quantile(d,0.9), np.quantile(d,0.99), (d<0.5).mean()))
print("mesh bbox", np.round(np.ptp(V,axis=0),1), " S0 bbox", np.round(np.ptp(S0,axis=0),1), " S1 bbox", np.round(np.ptp(S1,axis=0),1))
print("mesh min", np.round(V.min(0),1), "S0 min", np.round(S0.min(0),1), "S1 min", np.round(S1.min(0),1))
