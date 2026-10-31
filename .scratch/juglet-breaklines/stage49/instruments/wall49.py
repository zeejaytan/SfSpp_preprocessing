#!/usr/bin/env python3
"""ticket 49 -- wall49: the measured wall thickness of every piece, beside every cell.

WHY THIS EXISTS.  The bar ticket 49 sets is that the grown pair must separate to the WALL scale,
not the 0.2-0.3 mm of tickets 44/46.  That sentence is only checkable if the wall thickness sits
in the same table as the pair separation, measured the same way on the same pieces.  wall40.py
(ticket 40) already holds the method: 800 rays cast from the piece's own sampled cloud along its
normals through the released mesh, first return beyond 0.15 mm, median over the rays that hit.
The machinery (read_obj / weld / read_ply_vertices / unit / ray_hits / sheets / pct / the ray
block) is lifted VERBATIM from wall40.py so the numbers stay comparable with tickets 35 and 40.

What changes from wall40.py: it walks the run's cells instead of taking one mesh and one arm, it
carries patch_r and cloud_set so a row can be joined to pairs49.tsv, it caches on
(mesh md5, arm md5) because the same cloud set measures the same wall at both patch radii (the
patch radius moves the fold-radius estimate, not the sampling), and it records the wall thickness
measured on these pieces by the earlier stages (J2 2.693, J3 2.452, J5 2.900, J7 3.263, J9 2.595
mm) in a known_wall_mm column, so the comparison is in one place and a disagreement is visible.

Report only: a missing arm cloud writes a row with na and a note, never a failure.

Writes <out>/wall49.tsv and per-cell <cell>/measure/wall49.json.
"""
import argparse
import hashlib
import json
import os
import sys

import numpy as np

# measured on these pieces by the earlier stages -- the comparison column, not a gate
KNOWN_WALL = {
    "Juglet_Piece_2": 2.693,
    "Juglet_Piece_3": 2.452,
    "Juglet_Piece_5": 2.900,
    "Juglet_Piece_7": 3.263,
    "Juglet_Piece_9": 2.595,
}


def log(m):
    sys.stdout.write("[WALL49] %s\n" % m)
    sys.stdout.flush()


# ---------------------------------------------------------------- lifted verbatim from wall40.py
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


# ---------------------------------------------------------------------------------------------
def measure(mesh_path, arm_path):
    V, F, mh = read_obj(mesh_path)
    Vw, Fw, nweld = weld(V, F, 1e-4)
    C, cols = read_ply_vertices(arm_path)

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
    return dict(
        mesh_obj=dict(verts=len(V), faces=len(F), **mh),
        mesh_welded_components=nweld,
        cloud_pts=int(len(P)), rays=int(len(p0)),
        rays_with_hits=int((counts >= 1).sum()),
        thick_med_mm=round(pct(th, 50), 6) if th.size else None,
        thick_p10_mm=round(pct(th, 10), 6) if th.size else None,
        thick_p90_mm=round(pct(th, 90), 6) if th.size else None,
        frac_1_to_3_mm=round(float(((th >= 1) & (th <= 3)).mean()), 6) if th.size else None,
        hits_median=int(np.median(counts)), hits_max=int(counts.max()),
        rays_2plus=int((counts >= 2).sum()), rays_3plus=int((counts >= 3).sum()),
        merged_max=int(cmerge.max()),
    )


def read_cell(path):
    d = {}
    with open(path, "r") as fh:
        for line in fh:
            line = line.rstrip("\n").rstrip("\r")
            if "\t" in line:
                k, v = line.split("\t", 1)
                d[k] = v
    return d


def mesh_for(pot, piece, ds, corp):
    if pot == "Pot_A":
        return os.path.join(corp, "Mesh", "%s_Mesh.obj" % piece)
    return os.path.join(ds, "Mesh", pot, "%s_Mesh.obj" % piece)


COLS = ["pot", "piece", "arm", "patch_r", "cloud_set", "mesh", "mesh_md5", "arm_ply", "arm_md5",
        "cloud_pts", "rays", "rays_with_hits", "thick_med_mm", "thick_p10_mm", "thick_p90_mm",
        "frac_1_to_3_mm", "hits_median", "hits_max", "rays_2plus", "rays_3plus", "merged_max",
        "known_wall_mm", "note"]


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True, help="run out/ directory")
    ap.add_argument("--cells", required=True, help="out/cells-pipeline of this run")
    ap.add_argument("--ds", required=True, help="the Dataset directory")
    ap.add_argument("--corp", required=True, help="the released corpus (sfs_main/original_samples/SfS_pp)")
    a = ap.parse_args(argv)

    cells = []
    for name in sorted(os.listdir(a.cells)):
        c = os.path.join(a.cells, name, "cell.tsv")
        if os.path.exists(c):
            cells.append(c)
    if not cells:
        log("no cell.tsv under %s -- nothing to measure" % a.cells)
        return 2

    out_tsv = os.path.join(a.out, "wall49.tsv")
    cache = {}          # (mesh_md5, arm_md5) -> measurement dict
    rows = []
    for c in cells:
        info = read_cell(c)
        pot, piece, arm = info.get("pot", "?"), info.get("piece", "?"), info.get("arm", "?")
        pr = (info.get("patch_r_env") or "na").strip()
        cs = (info.get("cloud_set") or "na").strip()
        cell = os.path.dirname(c)
        mesh = mesh_for(pot, piece, a.ds, a.corp)
        armply = os.path.join(cell, "surfaces", "%s_SampledWithNormals.ply" % piece)
        row = dict((k, "na") for k in COLS)
        row.update(pot=pot, piece=piece, arm=arm, patch_r=pr, cloud_set=cs,
                   known_wall_mm=("%.3f" % KNOWN_WALL[piece]) if piece in KNOWN_WALL else "na")
        note = ""
        m = None
        if not os.path.isfile(mesh):
            note = "no released mesh at %s" % mesh
        elif not os.path.isfile(armply):
            note = "no sampled cloud kept for this cell (the pipeline wrote none)"
        else:
            row["mesh"] = mesh
            row["arm_ply"] = armply
            mm = md5_of(mesh)
            am = md5_of(armply)
            row["mesh_md5"] = mm
            row["arm_md5"] = am
            key = (mm, am)
            if key in cache:
                m = cache[key]
                note = "same mesh+cloud as an earlier cell: reused (the patch radius does not resample)"
            else:
                try:
                    m = measure(mesh, armply)
                except (OSError, ValueError) as e:
                    m = None
                    note = "measure failed: %s" % e
                if m is not None:
                    cache[key] = m
            if m is not None:
                for k in ("cloud_pts", "rays", "rays_with_hits", "thick_med_mm", "thick_p10_mm",
                          "thick_p90_mm", "frac_1_to_3_mm", "hits_median", "hits_max",
                          "rays_2plus", "rays_3plus", "merged_max"):
                    row[k] = "na" if m.get(k) is None else str(m[k])
                mdir = os.path.join(cell, "measure")
                os.makedirs(mdir, exist_ok=True)
                with open(os.path.join(mdir, "wall49.json"), "w") as fh:
                    json.dump(dict(row=row, measurement=m), fh, indent=1, sort_keys=True)
                    fh.write("\n")
                log("%s/%s arm=%s: med %s mm p10 %s p90 %s (known %s)" % (
                    pot, piece, arm, row["thick_med_mm"], row["thick_p10_mm"],
                    row["thick_p90_mm"], row["known_wall_mm"]))
        row["note"] = note
        rows.append(row)

    with open(out_tsv, "w", newline="", encoding="utf-8") as fh:
        fh.write("\t".join(COLS) + "\n")
        for r in rows:
            fh.write("\t".join(str(r.get(k, "na")) for k in COLS) + "\n")

    ok = [r for r in rows if r["thick_med_mm"] not in ("na", "")]
    log("wall rows: %d of %d cells measured (written %s)" % (len(ok), len(rows), out_tsv))
    for r in rows:
        if r["thick_med_mm"] in ("na", ""):
            log("  no measurement: %s/%s arm=%s -- %s" % (r["pot"], r["piece"], r["arm"], r["note"]))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
