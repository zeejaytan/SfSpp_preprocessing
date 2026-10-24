#!/usr/bin/env python3
"""Synthetic dry run for p294_render.py: a wavy 40x40 grid mesh, two surfaces, two wiggly lines."""
import json, os, shutil, sys
import numpy as np

ROOT = sys.argv[1]
shutil.rmtree(ROOT, ignore_errors=True)
for d in ["scripts", "out/geom", "out/png"]:
    os.makedirs(os.path.join(ROOT, d), exist_ok=True)
shutil.copyfile(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "292", "score292.py"),
                os.path.join(ROOT, "scripts", "score292.py"))

n = 30
xs = np.linspace(0, 60, n)
ys = np.linspace(0, 45, n)
V = []
for y in ys:
    for x in xs:
        V.append([x, y, 2.0 * np.sin(x / 9.0) * np.cos(y / 7.0)])
V = np.array(V)
F = []
for j in range(n - 1):
    for i in range(n - 1):
        a = j * n + i
        F.append([a, a + 1, a + n + 1])
        F.append([a, a + n + 1, a + n])
F = np.array(F)
with open(os.path.join(ROOT, "out/geom/test_mesh.obj"), "w") as f:
    for v in V:
        f.write("v %.4f %.4f %.4f\n" % tuple(v))
    for t in F:
        f.write("f %d %d %d\n" % tuple(t + 1))

rng = np.random.default_rng(7)


def surf(offset, count):
    pts = V[rng.choice(len(V), count)] + rng.normal(0, 0.15, (count, 3)) + np.array([0, 0, offset])
    return pts


def wline(npts, wobble, shift):
    t = np.linspace(0, 1, npts)
    x = 2 + 56 * t
    y = 3 + 8 * t + wobble * np.sin(6 * t)
    z = 2.0 * np.sin(x / 9.0) * np.cos(y / 7.0) + shift
    return np.stack([x, y, z], 1)


def wxyz(path, pts):
    np.savetxt(path, pts, fmt="%.4f")


def wpcd(path, pts):
    with open(path, "w") as f:
        f.write("VERSION .7\nFIELDS x y z\nSIZE 4 4 4\nTYPE F F F\nCOUNT 1 1 1\n")
        f.write("WIDTH %d\nHEIGHT 1\nVIEWPOINT 0 0 0 1 0 0 0\nPOINTS %d\nDATA ascii\n" % (len(pts), len(pts)))
        for p in pts:
            f.write("%.5f %.5f %.5f\n" % tuple(p))


wxyz(os.path.join(ROOT, "out/geom/test.S0.xyz"), surf(0.0, 4000))
wxyz(os.path.join(ROOT, "out/geom/test.S1.xyz"), surf(1.0, 4000))
ours = wline(60, 1.5, 0.6)
auth = wline(58, 0.4, 0.6)
ours[20:34] += np.array([0, 6.0, 0])
wpcd(os.path.join(ROOT, "out/geom/test.Bl1.pcd"), ours)
wpcd(os.path.join(ROOT, "out/geom/auth.Bl1.pcd"), auth)

man = {"lanes": [{
    "pot": "Pot_T", "piece": "Pot_T_Piece_01", "lane": "1",
    "our_pcd": os.path.join(ROOT, "out/geom/test.Bl1.pcd"),
    "auth_pcd": os.path.join(ROOT, "out/geom/auth.Bl1.pcd"),
    "mesh_obj": os.path.join(ROOT, "out/geom/test_mesh.obj"),
    "surf0": os.path.join(ROOT, "out/geom/test.S0.xyz"),
    "surf1": os.path.join(ROOT, "out/geom/test.S1.xyz"),
    "n_ours": len(ours), "n_auth": len(auth), "median": 1.234, "cov_ours": 78.5, "cov_auth": 81.0,
    "jumps": 0, "max_step": 4.2, "len_ours": 120.0, "len_auth": 118.0,
    "n292": "60", "n292a": "58", "median292": "1.111", "cov292": "80.00", "cov292a": "82.00", "jumps292": "0",
    "d_median": 0.123, "d_cov": -1.5, "flag": "",
    "commit": "0f8a4a417221647e7d6e7f7d031a90109930d44d",
    "edge_md5": "a28d10afab2b50bbe750d599ee2b7214", "mesh_md5": "0171f471d0558d2676df7c4b113c1e9d",
    "theta": "3.40000",
    "classify": "[PAPER-234] classify: face0 n=1 interior_frac=0.0000 ; classify: swapped -> Surface_0=interior"
}]}
json.dump(man, open(os.path.join(ROOT, "out", "manifest.json"), "w"), indent=1)
print("synthetic run dir ready:", ROOT)
