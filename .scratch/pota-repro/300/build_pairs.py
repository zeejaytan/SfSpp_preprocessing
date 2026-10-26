"""Build the two visual-qa source PLYs for ticket 300 (Pot C, both arms + C 01's gap).

Geometry only: no algorithm is touched. Poses come from the stored transforms
(local -> world, p' = R p + t, proved in rebuild_measure.py), the GT pose from
the authors' Ground Truth files, and each arm is brought into the GT vessel
frame by ONE global rigid alignment (frame choice only; inter-piece geometry
unchanged).
"""
import json
from pathlib import Path
import numpy as np
import trimesh

ROOT = Path(r"C:/PR/SfSpp_preprocessing/artifacts/pota300")
STAGE = ROOT / "inputs" / "stage"
CORPUS = STAGE / "corpus"
OUT = Path(r"C:/PR/SfSpp_preprocessing/artifacts/visual-qa")
PIECES = ["C01", "C02", "C03", "C04"]
FILES = {"C01": "01", "C02": "02", "C03": "03", "C04": "04"}
GTNAME = {"C01": "1", "C02": "2", "C03": "3", "C04": "4"}
EDGES = [("C01", "C02"), ("C01", "C03"), ("C01", "C04"), ("C02", "C03"), ("C02", "C04")]
COL = {"C01": (200, 160, 106), "C02": (79, 157, 157),
       "C03": (156, 156, 79), "C04": (143, 107, 168)}

def read_T(p):
    a = np.loadtxt(p)
    if a.shape == (3, 4):
        a = np.vstack([a, [0, 0, 0, 1]])
    assert a.shape == (4, 4), (p, a.shape)
    return a

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

def kabsch(P, Q):
    """Rigid R,t with R P + t ~ Q (frame removal only)."""
    p0, q0 = P.mean(0), Q.mean(0)
    H = (P - p0).T @ (Q - q0)
    U, S, Vt = np.linalg.svd(H)
    D = np.diag([1.0, 1.0, np.sign(np.linalg.det(Vt.T @ U.T))])
    R = Vt.T @ D @ U.T
    return R, q0 - R @ p0

def world(V, T):
    return V @ T[:3, :3].T + T[:3, 3]

def pcd_points(p):
    rows, seen = [], False
    with open(p, "r", errors="ignore") as fh:
        for line in fh:
            if not seen:
                if line.startswith("DATA"):
                    seen = True
                continue
            t = line.split()
            if len(t) >= 3:
                try:
                    rows.append([float(x) for x in t[:3]])
                except ValueError:
                    pass
    return np.asarray(rows, float)

def tube(P, radius, colour, closed=False, sections=6):
    segs = []
    n = len(P)
    for i in range(n if closed else n - 1):
        a, b = P[i], P[(i + 1) % n]
        v = b - a
        L = float(np.linalg.norm(v))
        if L < 1e-9:
            continue
        c = trimesh.creation.cylinder(radius=radius, height=L, sections=sections,
                                      segment=[a, b])
        c.visual = trimesh.visual.ColorVisuals(c, vertex_colors=np.tile(
            np.array([*colour, 255], np.uint8), (len(c.vertices), 1)))
        segs.append(c)
    return segs

def coloured(mesh, rgb):
    m = mesh.copy()
    m.visual = trimesh.visual.ColorVisuals(m, vertex_colors=np.tile(
        np.array([*rgb, 255], np.uint8), (len(m.vertices), 1)))
    return m

def build(meshes, poses, colours, name):
    parts = [coloured(trimesh.Trimesh(vertices=world(meshes[k][0], poses[k]),
                                      faces=meshes[k][1], process=False),
                      colours[k]) for k in PIECES]
    m = trimesh.util.concatenate(parts)
    m.export(str(OUT / name))
    return m

meshes, GT, ARM = {}, {}, {}
for k in PIECES:
    V, F = load_obj(CORPUS / "Mesh" / f"Pot_C_Piece_{FILES[k]}_Mesh_DS.obj")
    meshes[k] = (V, F)
    GT[k] = read_T(CORPUS / "GroundTruth" / f"Pot_C_Piece_{GTNAME[k]}_T.txt")
    for arm in ("authb", "oursd"):
        ARM.setdefault(arm, {})[k] = read_T(STAGE / "run" / arm / f"T_{int(GTNAME[k])-1}to_{int(GTNAME[k])-1}.txt")

# one global rigid alignment per arm: arm world frame -> GT vessel frame
ALIGN = {}
for arm in ("authb", "oursd"):
    P = np.vstack([world(meshes[k][0], ARM[arm][k]) for k in PIECES])
    Q = np.vstack([world(meshes[k][0], GT[k]) for k in PIECES])
    R, t = kabsch(P, Q)
    G = np.eye(4); G[:3, :3] = R; G[:3, 3] = t
    ALIGN[arm] = {"R": R, "t": t, "T": G}
    resid = np.linalg.norm(world(P, G) - Q, axis=1)
    ang = np.degrees(np.arccos(np.clip((np.trace(R) - 1) / 2, -1, 1)))
    print(f"{arm} -> GT frame: rot {ang:.3f} deg, trans {np.linalg.norm(t):.3f} mm, "
          f"RMS residual {resid.mean()*1000:.2f} um")

POSE_GTFRAME = {arm: {k: ALIGN[arm]["T"] @ ARM[arm][k] for k in PIECES} for arm in ALIGN}

# ---- pair 1: authors' assembly beside ours, both in the GT vessel frame
(OUT / "pota300_potC_arms").mkdir(parents=True, exist_ok=True)
L = build(meshes, POSE_GTFRAME["authb"], COL, "pota300_potC_arms/left_authors.ply")
R = build(meshes, POSE_GTFRAME["oursd"], COL, "pota300_potC_arms/right_ours.ply")
print("left(authors)  faces %d  bbox %s" % (len(L.faces), np.round(np.ptp(L.vertices, axis=0), 2)))
print("right(ours)    faces %d  bbox %s" % (len(R.faces), np.round(np.ptp(R.vertices, axis=0), 2)))

# seam distances in the GT frame, per arm, for the record
from scipy.spatial import cKDTree
seams = {}
for arm in ("authb", "oursd"):
    W = {k: world(meshes[k][0], POSE_GTFRAME[arm][k]) for k in PIECES}
    tr = {k: cKDTree(W[k]) for k in PIECES}
    for a, b in EDGES + [("C03", "C04")]:
        d, _ = tr[b].query(W[a])
        e, _ = tr[a].query(W[b])
        seams.setdefault(arm, {})[f"{a}-{b}"] = [round(float(d.min()), 4), round(float(e.min()), 4)]

# ---- pair 2: C 01 at its seated pose, the open rims and both interior lines marked
(OUT / "pota300_potC_c01").mkdir(parents=True, exist_ok=True)
V, F = meshes["C01"]
T = POSE_GTFRAME["oursd"]["C01"]
parts = [coloured(trimesh.Trimesh(vertices=world(V, T), faces=F, process=False),
                  (205, 205, 205))]

def boundary_loops(V, F):
    from collections import defaultdict
    cnt = defaultdict(int)
    for tri in F:
        for a, b in ((tri[0], tri[1]), (tri[1], tri[2]), (tri[2], tri[0])):
            cnt[(min(a, b), max(a, b))] += 1
    be = {(a, b) for (a, b), c in cnt.items() if c == 1}
    adj = defaultdict(set)
    for a, b in be:
        adj[a].add(b); adj[b].add(a)
    used, out = set(), []
    for a, b in sorted(be):
        if a in used:
            continue
        loop = [a]; used.add(a); cur, prev = b, a
        while cur != a:
            if cur in used:
                break
            loop.append(cur); used.add(cur)
            nx = [x for x in adj[cur] if x != prev and x not in used] or \
                 [x for x in adj[cur] if x != prev]
            if not nx:
                break
            prev, cur = cur, nx[0]
        out.append(loop)
    return sorted(out, key=lambda l: -len(l))

LOOPS = boundary_loops(V, F)
MAGENTA, YELLOW = (230, 40, 200), (240, 210, 40)
named = []
for i, lp in enumerate(LOOPS):
    P = world(V[np.asarray(lp)], T)
    big = len(lp) > 200
    parts.extend(tube(P, 0.9 if big else 0.7, MAGENTA if big else YELLOW, closed=True))
    named.append({"loop": i, "vertices": len(lp),
                  "perimeter_mm": round(float(np.linalg.norm(np.diff(P, axis=0), axis=1).sum()), 3),
                  "marker": "magenta" if big else "yellow",
                  "centroid_world": [round(float(x), 2) for x in P.mean(0)]})

ours_bl = world(pcd_points(STAGE / "prep_geom" / "Pot_C_Piece_01.Bl0.pcd"), T)
auth_bl = world(pcd_points(CORPUS / "Breaklines" / "Pot_C_Piece_01_Breakline_0.pcd"), T)
parts.extend(tube(ours_bl, 0.55, (220, 30, 30), closed=True))
parts.extend(tube(auth_bl, 0.55, (40, 90, 230), closed=True))
S = trimesh.util.concatenate(parts)
S.export(str(OUT / "pota300_potC_c01/c01_seated.ply"))
print("single(C 01)   faces %d  bbox %s" % (len(S.faces), np.round(np.ptp(S.vertices, axis=0), 2)))

rec = {"align_rot_deg": {a: round(float(np.degrees(np.arccos(np.clip((np.trace(ALIGN[a]['R']) - 1) / 2, -1, 1)))), 3) for a in ALIGN},
       "align_trans_mm": {a: round(float(np.linalg.norm(ALIGN[a]['t'])), 3) for a in ALIGN},
       "seams_gframe_mm": seams, "loops": named,
       "ours_bl0_dots": int(len(ours_bl)), "auth_bl0_dots": int(len(auth_bl)),
       "faces": {"left": int(len(L.faces)), "right": int(len(R.faces)), "single": int(len(S.faces))}}
(ROOT / "geom" / "pair_build.json").write_text(json.dumps(rec, indent=1))
print(json.dumps({k: rec[k] for k in ("align_rot_deg", "align_trans_mm", "seams_gframe_mm", "ours_bl0_dots", "auth_bl0_dots")}, indent=1))
