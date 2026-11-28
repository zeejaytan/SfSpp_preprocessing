"""Ticket 17 shared readers, paths and small helpers.

READ-ONLY on the corpus and on the t09 canonical run.  Every wall reader
dispatches on the PLY magic and selects x,y,z(,nx,ny,nz) by property name, so a
PCL ASCII PLY (.S0/.S1) and a 6-column text wall (Author Surfaces/) both load.

Frames: Pot A..J t09 surfaces are in the mesh frame (1x mm).  Juglet_def3x
surfaces and axes09_juglet_def3x_regen are in 3x units -- divide positions by
3.0 (JUG_ROWS) before comparing with the 1x Dataset/Mesh/Juglet/ meshes or the
1x Dataset/Juglet_GT/ axis.  Axis files are written pos(3) dir(3) per line;
read_axis_lines returns them as rows [dir; pos] like sfs_axes.io_axes.read_axes.
"""
import os

import numpy as np

RUN09 = "/data/gpfs/projects/punim2657/SfSpp/runs/20261125-1340_a50f8cc_t09-own-surfaces"
OUT09 = os.path.join(RUN09, "out")
CORPUS = "/data/gpfs/projects/punim2657/sfs_main/original_samples/SfS_pp"
MESH_DIR = os.path.join(CORPUS, "Mesh")
GT_DIR = os.path.join(CORPUS, "Ground Truth Axes")
SURF_DIR = os.path.join(CORPUS, "Surfaces")
JUG_MESH = "/data/gpfs/projects/punim2657/Dataset/Mesh/Juglet"
JUG_GT = "/data/gpfs/projects/punim2657/Dataset/Juglet_GT"
JUG_ROWS = 3.0
POTS = list("ABCDEFGHIJ")


def is_jug(stem):
    return stem.startswith("Juglet_")


def pot_of(stem):
    return "JUG" if is_jug(stem) else stem.split("_")[1]


def piece_no(stem):
    return int(stem.rsplit("_", 1)[-1])


def stems():
    """The 157 canonical t09 stems: 148 Pot A..J + 9 Juglet, deterministic order."""
    pots = []
    for p in POTS:
        d = os.path.join(OUT09, "Pot_" + p, "geom")
        pots += [f[:-3] for f in os.listdir(d) if f.endswith(".S0")]
    pots.sort(key=lambda s: (s.split("_")[1], piece_no(s)))
    jug = sorted(("Juglet_Piece_%d" % i for i in range(1, 10)), key=piece_no)
    return pots + jug


def geom_dir(stem):
    if is_jug(stem):
        return os.path.join(OUT09, "Juglet_def3x", "geom")
    return os.path.join(OUT09, "Pot_" + pot_of(stem), "geom")


def mesh_log(stem):
    if is_jug(stem):
        return os.path.join(OUT09, "Juglet_def3x", "pieces", stem, "mesh.log")
    return os.path.join(OUT09, "Pot_" + pot_of(stem), "pieces", stem, "mesh.log")


def author_wall(stem, which=1):
    return os.path.join(SURF_DIR, "%s_Surface_%d.xyz" % (stem, which))


def mesh_obj(stem):
    if is_jug(stem):
        return os.path.join(JUG_MESH, stem + "_Mesh.obj")
    ds = os.path.join(MESH_DIR, stem + "_Mesh_DS.obj")
    return ds if os.path.isfile(ds) else os.path.join(MESH_DIR, stem + "_Mesh.obj")


def axis09_path(stem):
    base = "axes09_juglet_def3x_regen" if is_jug(stem) else "axes09_own_regen"
    return os.path.join(OUT09, base, stem + "_Axis.xyz")


def read_ply(path, with_normals=True):
    """(cols x N) float array: x,y,z or x,y,z,nx,ny,nz selected by property name."""
    with open(path, "r", errors="replace") as fh:
        if fh.readline().strip() != "ply":
            raise ValueError("%s: not a PLY" % path)
        fmt, nverts, props, element = None, 0, [], None
        while True:
            line = fh.readline()
            if not line:
                raise ValueError("%s: unterminated header" % path)
            s = line.strip()
            if s.startswith("format "):
                fmt = s.split()[1]
            elif s.startswith("element "):
                p = s.split()
                element = p[1]
                if element == "vertex":
                    nverts = int(p[2])
            elif s.startswith("property ") and element == "vertex":
                p = s.split()
                if p[1] == "list":
                    raise ValueError("%s: list property on vertex" % path)
                props.append(p[-1])
            elif s == "end_header":
                break
        if fmt != "ascii":
            raise ValueError("%s: format %r, expected ascii" % (path, fmt))
        for k in ("x", "y", "z"):
            if k not in props:
                raise ValueError("%s: no property %s" % (path, k))
        cols = [props.index(k) for k in ("x", "y", "z")]
        normals = all(k in props for k in ("nx", "ny", "nz"))
        if with_normals and normals:
            cols += [props.index(k) for k in ("nx", "ny", "nz")]
        if nverts == 0:
            return np.zeros((len(cols), 0))
        data = np.loadtxt(fh, max_rows=nverts, usecols=tuple(cols), ndmin=2)
    return np.ascontiguousarray(data.T)


def read_wall(path, with_normals=True):
    """Dispatching wall reader: PLY by magic, else 6-column text (Author Surfaces)."""
    with open(path, "rb") as fh:
        magic = fh.readline().strip()
    if magic == b"ply":
        a = read_ply(path, with_normals=with_normals)
        return a if with_normals else a[0:3]
    a = np.loadtxt(path, usecols=(0, 1, 2, 3, 4, 5), ndmin=2)
    a = np.asarray(a, dtype=float)
    return np.ascontiguousarray(a.T) if with_normals else np.ascontiguousarray(a[:, 0:3].T)


def read_obj_vertices(path):
    """(N,3) mesh vertices; positions only (the scan meshes are mm, 1x)."""
    out = []
    with open(path, "r", errors="replace") as fh:
        for line in fh:
            if line.startswith("v "):
                p = line.split()
                out.append((float(p[1]), float(p[2]), float(p[3])))
    return np.asarray(out, dtype=float)


def read_axis_lines(path):
    """(6,K) rows [dir(3); pos(3)], matching sfs_axes.io_axes.read_axes semantics."""
    if not os.path.isfile(path) or os.path.getsize(path) == 0:
        return np.zeros((6, 0))
    raw = np.loadtxt(path, ndmin=2)
    if raw.size == 0:
        return np.zeros((6, 0))
    raw = np.asarray(raw, dtype=float)
    v = np.zeros((6, raw.shape[0]))
    v[0:3] = raw[:, 3:6].T
    v[3:6] = raw[:, 0:3].T
    return v


def gt_axis(stem):
    """(6,) [dir; pos] reference line, or None when the piece has no GT.

    Pots: canonicalized so dir z >= 0 (t03_lib.canonicalize).  Juglet: the GT is
    already in the 1x frame and is never divided or canonicalized.
    """
    if is_jug(stem):
        v = read_axis_lines(os.path.join(JUG_GT, stem + "_Axis.xyz"))
    else:
        p = os.path.join(GT_DIR, stem + "_Axis.xyz")
        if not os.path.isfile(p):
            return None
        v = read_axis_lines(p)
    if v.shape[1] == 0:
        return None
    out = v[:, 0].copy()
    if not is_jug(stem) and out[2] < 0:
        out[0:3] = -out[0:3]
    return out


def line_angle_deg(a, b):
    """Acute angle between two undirected line directions, degrees."""
    a = np.asarray(a, dtype=float)[0:3]
    b = np.asarray(b, dtype=float)[0:3]
    na, nb = np.linalg.norm(a), np.linalg.norm(b)
    if na == 0 or nb == 0:
        return float("nan")
    c = abs(float(np.dot(a, b)) / (na * nb))
    return float(np.degrees(np.arccos(min(1.0, max(-1.0, c)))))


def project_basis(direction):
    d = np.asarray(direction, dtype=float)
    d = d / np.linalg.norm(d)
    a = np.array([1.0, 0.0, 0.0]) if abs(d[0]) < 0.9 else np.array([0.0, 1.0, 0.0])
    e1 = np.cross(d, a)
    e1 /= np.linalg.norm(e1)
    e2 = np.cross(d, e1)
    return d, e1, e2


def wrap_deg(points, axis, bin_deg=1.0):
    """Spanned azimuth, degrees, of points around the axis [dir(3), pos(3)]."""
    d, e1, e2 = project_basis(axis[0:3])
    rel = np.asarray(points, dtype=float) - np.asarray(axis[3:6], dtype=float)[None, :]
    ang = np.degrees(np.arctan2(rel @ e2, rel @ e1)) % 360.0
    nb = int(round(360.0 / bin_deg))
    bins = np.zeros(nb, dtype=bool)
    bins[(ang / bin_deg).astype(int) % nb] = True
    idx = np.where(bins)[0]
    if idx.size < 2:
        return 0.0
    gaps = np.diff(np.r_[idx, idx[0] + nb])
    return float(360.0 - gaps.max() * bin_deg)


def write_tsv(path, header, rows):
    d = os.path.dirname(path)
    if d:
        os.makedirs(d, exist_ok=True)
    with open(path, "w", newline="") as fh:
        if header:
            fh.write("\t".join(header) + "\n")
        for r in rows:
            fh.write("\t".join(str(x) for x in r) + "\n")
