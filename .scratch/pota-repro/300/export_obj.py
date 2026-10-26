"""Export one combined OBJ per arm: the four pieces at their stored seated poses.

Frame: the assembler's own world frame (the T's as written), one `g` group per piece.
The GT-frame copies used for visual-qa are the same vertices after one global rigid
alignment; no inter-piece geometry differs between them.
"""
import json
from pathlib import Path
import numpy as np

ROOT = Path(r"C:/PR/SfSpp_preprocessing/artifacts/pota300")
STAGE = ROOT / "inputs" / "stage"
CORPUS = STAGE / "corpus"
OUT = ROOT / "geom"
PIECES = ["C01", "C02", "C03", "C04"]
FILES = {"C01": "01", "C02": "02", "C03": "03", "C04": "04"}
NUM = {"C01": 1, "C02": 2, "C03": 3, "C04": 4}

def read_T(p):
    a = np.loadtxt(p)
    return np.vstack([a, [0, 0, 0, 1]]) if a.shape == (3, 4) else a

def load_obj(p):
    vs, fs = [], []
    with open(p, "r", errors="ignore") as fh:
        for line in fh:
            if line.startswith("v "):
                vs.append([float(x) for x in line.split()[1:4]])
            elif line.startswith("f "):
                ix = [int(t.split("/")[0]) for t in line.split()[1:]]
                for k in range(1, len(ix) - 1):
                    fs.append([ix[0], ix[k], ix[k + 1]])
    return np.asarray(vs, float), np.asarray(fs, np.int64) - 1

meshes = {k: load_obj(CORPUS / "Mesh" / f"Pot_C_Piece_{FILES[k]}_Mesh_DS.obj") for k in PIECES}
rec = {}
for arm in ("oursd", "authb"):
    lines = [f"# Pot C, {arm} arm, ticket 300: four pieces at the seated poses the assembler",
             "# wrote in T_0to_0.txt .. T_3to_3.txt, applied as p_world = R p_local + t.",
             f"# source run: 20261026-0126_d1f1a4c_p298-Pot_C-{arm}", "# millimetres, assembler world frame"]
    base = 1
    for k in PIECES:
        T = read_T(STAGE / "run" / arm / f"T_{NUM[k]-1}to_{NUM[k]-1}.txt")
        V, F = meshes[k]
        W = V @ T[:3, :3].T + T[:3, 3]
        lines.append(f"g Pot_C_Piece_{FILES[k]}")
        lines.extend("v %.6f %.6f %.6f" % tuple(v) for v in W)
        lines.extend("f %d %d %d" % (a + base, b + base, c + base) for a, b, c in F)
        base += len(W)
        rec.setdefault(arm, {})[k] = {"vertices": int(len(W)), "faces": int(len(F)),
                                      "centroid": [round(float(x), 3) for x in W.mean(0)]}
    p = OUT / f"potC_{arm}_assembled.obj"
    p.write_text("\n".join(lines) + "\n")
    print("wrote", p.name, p.stat().st_size // 1024, "KB")

# read back and confirm the export keeps the seams
from scipy.spatial import cKDTree
back = {}
for arm in ("oursd", "authb"):
    per = {}
    cur = None
    for line in open(OUT / f"potC_{arm}_assembled.obj"):
        if line.startswith("g "):
            cur = line.split()[1].split("_")[-1]
            per[cur] = []
        elif line.startswith("v ") and cur:
            per[cur].append([float(x) for x in line.split()[1:4]])
    back[arm] = {k: np.asarray(v) for k, v in per.items()}
    W = back[arm]
    tr = {k: cKDTree(W[k]) for k in W}
    d = {}
    for a, b in [("01", "02"), ("01", "03"), ("01", "04"), ("02", "03"), ("02", "04"), ("03", "04")]:
        dd, _ = tr[b].query(W[a])
        d[f"C{a}-C{b}"] = round(float(dd.min()), 4)
    rec[arm]["roundtrip_seams_mm"] = d
    print(arm, "roundtrip seams", json.dumps(d))

(OUT / "obj_export.json").write_text(json.dumps(rec, indent=1))
