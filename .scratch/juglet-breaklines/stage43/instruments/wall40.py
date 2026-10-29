#!/usr/bin/env python3
"""wall40.py -- ticket 40's wall-thickness measurement, ticket 20's 800-ray method.

The thickness machinery (read_obj / weld / read_ply_vertices / unit / ray_hits /
sheets / the ray block) is lifted verbatim from measure35.py's thickness block so
the numbers reproduce ticket 35's rows when run on the same inputs.  Unlike
measure35.py this takes one --mesh and one --arm ply and writes one JSON, because
ticket 40 measures every cell inside the grid job that produced it.

CLI: wall40.py --group G --pot P --piece TAG --mesh M.obj --arm sampled.ply --out W.json
"""
import argparse, hashlib, json, os, sys
import numpy as np


def read_obj(path):
    V, Fraw = [], []
    n_vn = n_vt = 0
    with open(path, "r", errors="replace") as f:
        for line in f:
            c = line[:2]
            if c == "v ":
                p = line.split()
                V.append((float(p[1]), float(p[2]), float(p[3])))
            elif c == "f ":
                idx = [int(tok.split("/")[0]) for tok in line.split()[1:]]
                for k in range(1, len(idx) - 1):
                    Fraw.append((idx[0], idx[k], idx[k + 1]))
            elif c == "vn":
                n_vn += 1
            elif c == "vt":
                n_vt += 1
    V = np.asarray(V, dtype=np.float64)
    F = np.asarray(Fraw, dtype=np.int64)
    if (F < 0).any():
        F = F + len(V) + 1
    F = F - 1
    if len(V) == 0 or len(F) == 0:
        raise ValueError("OBJ empty: %d v %d f" % (len(V), len(F)))
    if F.min() < 0 or F.max() >= len(V):
        raise ValueError("OBJ index out of range: %d..%d for %d verts" % (F.min(), F.max(), len(V)))
    return V, F, dict(n_vn=n_vn, n_vt=n_vt)


def read_ply_vertices(path):
    names, counts, props = [], [], []
    with open(path, "r", errors="replace") as f:
        first = f.readline().strip()
        if first != "ply":
            raise ValueError("PLY does not start with the magic line: %r" % first)
        fmt = None
        while True:
            line = f.readline()
            if not line:
                raise ValueError("PLY header ended without end_header")
            p = line.split()
            if not p:
                continue
            if p[0] == "format":
                fmt = line.strip()
                if "ascii" not in fmt:
                    raise ValueError("PLY not ascii: %r" % fmt)
            elif p[0] == "element":
                names.append(p[1]); counts.append(int(p[2])); props.append([])
            elif p[0] == "property":
                props[-1].append((p[4] if p[1] == "list" else p[2], p[1]))
            elif p[0] == "end_header":
                break
        if "vertex" not in names:
            raise ValueError("PLY has no vertex element")
        vi = names.index("vertex")
        for k in range(vi):
            if any(t == "list" for _, t in props[k]):
                raise ValueError("PLY list property before vertex")
            for _ in range(counts[k]):
                f.readline()
        nv = counts[vi]
        w = len(props[vi])
        rows = []
        for i in range(nv):
            line = f.readline()
            if not line:
                raise ValueError("PLY body ended at vertex %d of %d" % (i, nv))
            p = line.split()
            if len(p) != w:
                raise ValueError("PLY vertex %d has %d columns, expected %d: %r"
                                 % (i, len(p), w, line[:100]))
            rows.append(p)
    return np.array(rows, dtype=np.float64), [n for n, _ in props[vi]]


def unit(v):
    n = np.linalg.norm(v, axis=1)
    out = np.zeros_like(v)
    ok = np.isfinite(n) & (n > 0)
    out[ok] = v[ok] / n[ok, None]
    return out, ok


def weld(V, F, tol):
    key = np.round(V / tol).astype(np.int64)
    uniq, first, inv = np.unique(key, axis=0, return_index=True, return_inverse=True)
    return V[first], inv[F], len(uniq)


def ray_hits(V, F, origins, dirs, eps=1e-9):
    v0 = V[F[:, 0]]; e1 = V[F[:, 1]] - v0; e2 = V[F[:, 2]] - v0
    out = []
    for k in range(len(origins)):
        d = np.asarray(dirs[k], float); p = np.asarray(origins[k], float)
        h = np.cross(d, e2)
        a = (e1 * h).sum(1)
        ok = np.abs(a) > 1e-12
        if not ok.any():
            out.append(np.zeros(0)); continue
        f = np.zeros_like(a); f[ok] = 1.0 / a[ok]
        s = p - v0
        u = f * (s * h).sum(1)
        qv = np.cross(s, e1)
        vv = f * (qv @ d)
        t = f * (e2 * qv).sum(1)
        m = ok & (u >= -eps) & (u <= 1 + eps) & (vv >= -eps) & (u + vv <= 1 + eps) & (t > 0)
        out.append(np.sort(t[m]))
    return out


def sheets(t, tol=1e-4):
    if t.size == 0:
        return t
    t = np.sort(t)
    return t[np.r_[True, np.diff(t) > tol]]


def pct(a, p):
    a = np.asarray(a, dtype=float)
    a = a[np.isfinite(a)]
    return float(np.percentile(a, p)) if a.size else float("nan")


def md5_of(path):
    h = hashlib.md5()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def main():
    ap = argparse.ArgumentParser(description="ticket 40 wall thickness, 800-ray method")
    ap.add_argument("--group", required=True)
    ap.add_argument("--pot", required=True)
    ap.add_argument("--piece", required=True)
    ap.add_argument("--mesh", required=True)
    ap.add_argument("--arm", required=True, help="the cell's <P>_SampledWithNormals.ply")
    ap.add_argument("--out", required=True, help="JSON path")
    a = ap.parse_args()

    V, F, mh = read_obj(a.mesh)
    Vw, Fw, nweld = weld(V, F, 1e-4)
    C, cols = read_ply_vertices(a.arm)

    def pick(cands):
        for c in cands:
            if c in cols:
                return cols.index(c)
        raise ValueError("PLY has none of %r in %r" % (cands, cols))

    P = np.stack([C[:, pick(("x",))], C[:, pick(("y",))], C[:, pick(("z",))]], 1)
    ncols = [pick(("normal_x", "nx")), pick(("normal_y", "ny")), pick(("normal_z", "nz"))]
    Pn = unit(np.stack([C[:, c] for c in ncols], 1))[0]
    step = max(1, len(P) // 800)
    p0 = P[::step]
    nn = Pn[::step]
    nn = nn / np.maximum(np.linalg.norm(nn, axis=1, keepdims=True), 1e-30)
    hits = ray_hits(Vw, Fw, p0 + nn * 1e-3, -nn)
    thick = np.full(len(hits), np.nan)
    counts = np.zeros(len(hits), int)
    cmerge = np.zeros(len(hits), int)
    for r, t in enumerate(hits):
        counts[r] = t.size
        cmerge[r] = sheets(t).size
        tt = t[t > 0.15]
        if tt.size:
            thick[r] = tt.min()
    th = thick[np.isfinite(thick)]

    res = dict(
        group=a.group, pot=a.pot, piece=a.piece,
        mesh=a.mesh, mesh_md5=md5_of(a.mesh), mesh_obj=dict(verts=len(V), faces=len(F), **mh),
        mesh_welded_components=nweld,
        arm=a.arm, arm_md5=md5_of(a.arm), arm_basename=os.path.basename(a.arm),
        cloud_pts=len(P), rays=len(p0),
        rays_with_hits=int((counts >= 1).sum()),
        thick_med_mm=round(pct(th, 50), 6) if th.size else None,
        thick_p10_mm=round(pct(th, 10), 6) if th.size else None,
        thick_p90_mm=round(pct(th, 90), 6) if th.size else None,
        frac_1_to_3_mm=round(float(((th >= 1) & (th <= 3)).mean()), 6) if th.size else None,
        hits_median=int(np.median(counts)), hits_max=int(counts.max()),
        rays_2plus=int((counts >= 2).sum()), rays_3plus=int((counts >= 3).sum()),
        merged_max=int(cmerge.max()),
    )
    with open(a.out, "w") as f:
        json.dump(res, f, indent=1, sort_keys=True)
        f.write("\n")
    print("[WALL40] %s/%s: %d pts, %d rays, med %.5f mm p10 %.5f p90 %.5f frac1-3 %.4f"
          % (a.group, a.piece, len(P), len(p0), res["thick_med_mm"] or float("nan"),
             res["thick_p10_mm"] or float("nan"), res["thick_p90_mm"] or float("nan"),
             res["frac_1_to_3_mm"] if res["frac_1_to_3_mm"] is not None else float("nan")))
    return 0


if __name__ == "__main__":
    sys.exit(main())
