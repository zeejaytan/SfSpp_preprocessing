#!/usr/bin/env python3
"""Ticket 331 Part A: build Dataset/Juglet_large -- the 3x vessel, derived, never edited.

Source = the mesh the preprocessing chain actually consumes, Dataset/Mesh/Juglet/
Juglet_Piece_0N_Mesh.obj (mm, scan pose, CRLF).  The Blender export Dataset/Juglet/Piece0N.obj
is recorded for provenance only: it is a different triangulation in different (non-mm) units.

Scaling is the similarity x -> 3x about the coordinate origin, the only scaling that pairs with
(R, t) -> (R, 3t):   R(3p) + 3t = 3(Rp + t).

Every byte that is not a scaled coordinate is copied through unchanged (including CRLF).
"""
import os, sys, hashlib, json, shutil
import numpy as np

SRC = "/data/gpfs/projects/punim2657/sfs_preprocessing/Dataset/Mesh/Juglet"
RAW = "/data/gpfs/projects/punim2657/Dataset/Juglet"
GT  = "/data/gpfs/projects/punim2657/Dataset/Juglet_GT"
OUT = "/data/gpfs/projects/punim2657/Dataset/Juglet_large"
K = 3.0
PIECES = list(range(1, 10))

def md5(path):
    h = hashlib.md5()
    with open(path, "rb") as f:
        for blk in iter(lambda: f.read(1 << 20), b""):
            h.update(blk)
    return h.hexdigest()

def fmt(val, tok):
    if "." in tok:
        return "%.*f" % (len(tok.split(".")[1]), val)
    return "%.0f" % val

def scaling_obj(src, dst):
    V = []
    with open(src, "r", newline="") as fi, open(dst, "w", newline="") as fo:
        for line in fi:
            body = line.rstrip("\r\n"); term = line[len(body):]
            t = body.split()
            if t and t[0] == "v":
                xyz = [float(t[k]) * K for k in (1, 2, 3)]
                V.append(xyz)
                out = "v " + " ".join(fmt(xyz[k], t[1 + k]) for k in range(3))
                if len(t) > 4:
                    out += " " + " ".join(t[4:])
                fo.write(out + term)
            else:
                fo.write(line)
    return np.array(V)

def read_obj_v(src):
    V = []; nv = nf = 0
    with open(src, "r") as f:
        for line in f:
            t = line.split()
            if t and t[0] == "v":
                V.append([float(x) for x in t[1:4]]); nv += 1
            elif t and t[0] == "f":
                nf += 1
    return np.array(V), nv, nf

def scaling_T(src, dst):
    """replace only the translation token of rows 1-3; every other byte is copied."""
    with open(src, "r", newline="") as fi:
        lines = fi.readlines()
    T = np.array([[float(x) for x in ln.split()] for ln in lines if ln.strip()])
    R, t = T[:3, :3], T[:3, 3]
    out = []
    for r, line in enumerate(lines):
        body = line.rstrip("\r\n"); term = line[len(body):]
        t_ = body.split()
        if not t_:
            out.append(line); continue
        if r < 3:
            s = " ".join([t_[0], t_[1], t_[2], fmt(t[r] * K, t_[3])])
            if body.endswith((" ", "\t")) and not s.endswith(" "):
                s += " "
            out.append(s + term)
        else:
            out.append(line)
    with open(dst, "w", newline="") as f:
        f.writelines(out)
    return R, t

def scaling_axis(src, dst):
    with open(src, "r", newline="") as fi:
        line = fi.readline()
    body = line.rstrip("\r\n"); term = line[len(body):]
    t_ = body.split()
    assert len(t_) == 6, (src, len(t_))
    v = [float(x) for x in t_]
    s = " ".join([fmt(v[0] * K, t_[0]), fmt(v[1] * K, t_[1]), fmt(v[2] * K, t_[2]),
                  t_[3], t_[4], t_[5]])
    with open(dst, "w", newline="") as f:
        f.write(s + term)
    return np.array([v[0] * K, v[1] * K, v[2] * K]), np.array(v[3:6])

def verify_obj(src, dst):
    """every non-v line byte-identical; every v line == K * source with the rest of the line kept."""
    with open(src, "rb") as f: a = f.read().splitlines()
    with open(dst, "rb") as f: b = f.read().splitlines()
    assert len(a) == len(b), (len(a), len(b))
    nv = 0
    for la, lb in zip(a, b):
        if la.startswith(b"v "):
            ta, tb = la.split(), lb.split()
            assert len(ta) == len(tb), (la, lb)
            for k in (1, 2, 3):
                xa, xb = ta[k].decode(), tb[k].decode()
                assert abs(float(xb) - K * float(xa)) <= 1e-9 * max(1.0, abs(K * float(xa))), (la, lb)
                assert xb.count(".") == xa.count("."), (la, lb)
            assert ta[4:] == tb[4:], (la, lb)
            nv += 1
        else:
            assert la == lb, (la, lb)
    return nv

def bbox_diag(V):
    return float(np.linalg.norm(V.max(0) - V.min(0)))

def main():
    os.makedirs(OUT, exist_ok=True)
    graph = np.loadtxt(os.path.join(GT, "Juglet_simple_graph.txt"), dtype=int)
    n = graph.shape[0]
    edges = [(i + 1, j + 1) for i in range(n) for j in range(i + 1, n) if graph[i, j]]
    rows = []; V1 = {}; V3 = {}; T1 = {}; T3 = {}
    for i in PIECES:
        s_obj = os.path.join(SRC, "Juglet_Piece_%02d_Mesh.obj" % i)
        r_obj = os.path.join(RAW, "Piece%02d.obj" % i)
        o_obj = os.path.join(OUT, "Piece%02d.obj" % i)
        Vs, nvs, nfs = read_obj_v(s_obj)
        Vr, nvr, nfr = read_obj_v(r_obj)
        Vw = scaling_obj(s_obj, o_obj)
        nvw = verify_obj(s_obj, o_obj)
        assert nvw == nvs == len(Vw)
        ds, dw, dr = bbox_diag(Vs), bbox_diag(Vw), bbox_diag(Vr)
        R, t = scaling_T(os.path.join(GT, "Juglet_Piece_%d_T.txt" % i),
                         os.path.join(OUT, "Juglet_Piece_%d_T.txt" % i))
        p3, d3 = scaling_axis(os.path.join(GT, "Juglet_Piece_%d_Axis.xyz" % i),
                              os.path.join(OUT, "Juglet_Piece_%d_Axis.xyz" % i))
        V1[i] = Vs; V3[i] = Vw; T1[i] = (R, t); T3[i] = (R, t * K)
        a_src = np.array([float(x) for x in open(os.path.join(GT, "Juglet_Piece_%d_Axis.xyz" % i)).read().split()])
        rows.append(dict(
            piece=i,
            src_obj=s_obj, src_md5=md5(s_obj), src_nv=nvs, src_nf=nfs, src_diag=ds,
            raw_obj=r_obj, raw_md5=md5(r_obj), raw_nv=nvr, raw_nf=nfr, raw_diag=dr,
            out_obj=o_obj, out_md5=md5(o_obj), out_nv=nvw, out_nf=nfs, out_diag=dw,
            ratio=dw / ds, ratio_vs_raw=dw / dr,
            axis_point_src=[float(x) for x in a_src[:3]],
            axis_point_out=[float(x) for x in p3],
            axis_point_norm_src=float(np.linalg.norm(a_src[:3])),
            axis_point_norm_out=float(np.linalg.norm(p3)),
            axis_dir_src=[float(x) for x in a_src[3:]],
            axis_dir_out=[float(x) for x in d3],
            axis_dir_norm_src=float(np.linalg.norm(a_src[3:])),
            axis_dir_norm_out=float(np.linalg.norm(d3)),
            T_md5_out=md5(os.path.join(OUT, "Juglet_Piece_%d_T.txt" % i)),
            axis_md5_out=md5(os.path.join(OUT, "Juglet_Piece_%d_Axis.xyz" % i)),
        ))
    worst = 0.0
    for i in PIECES:
        R, t = T1[i]
        y1 = V1[i] @ R.T + t
        y3 = V3[i] @ R.T + t * K
        worst = max(worst, float(np.abs(y3 - K * y1).max()))
    gaps = []
    for (i, j) in edges:
        R1, t1 = T1[i]; R2, t2 = T1[j]
        A1 = V1[i] @ R1.T + t1; B1 = V1[j] @ R2.T + t2
        A3 = V3[i] @ R1.T + t1 * K; B3 = V3[j] @ R2.T + t2 * K
        def mind(A, B):
            best = float("inf")
            for s in range(0, len(A), 512):
                d = ((A[s:s + 512, None, :] - B[None, :, :]) ** 2).sum(-1)
                best = min(best, float(np.sqrt(d.min())))
            return best
        g1 = mind(A1, B1); g3 = mind(A3, B3)
        gaps.append(dict(pair="%d-%d" % (i, j), gap1=g1, gap3=g3, ratio=(g3 / g1 if g1 else None)))
    shutil.copyfile(os.path.join(GT, "Juglet_simple_graph.txt"),
                    os.path.join(OUT, "Juglet_simple_graph.txt"))
    json.dump({"pieces": rows, "transform_residual_max_mm": worst, "gaps": gaps},
              open(os.path.join(OUT, "scale_checks.json"), "w"), indent=1)
    cols = ["piece", "src_md5", "out_md5", "src_nv", "out_nv", "src_nf", "out_nf",
            "src_diag", "out_diag", "ratio", "ratio_vs_raw",
            "axis_point_norm_src", "axis_point_norm_out", "axis_dir_norm_src", "axis_dir_norm_out",
            "raw_md5", "T_md5_out", "axis_md5_out", "src_obj", "out_obj"]
    with open(os.path.join(OUT, "scale_census.tsv"), "w") as f:
        f.write("\t".join(cols) + "\n")
        for r in rows:
            f.write("\t".join(str(r[c]) for c in cols) + "\n")
    print("transform residual max (mm):", worst)
    print("piece  ratio            out_nv out_nf   point_norm src->out      dir_norm src->out")
    for r in rows:
        print("%5d %14.10f %6d %6d  %11.3f -> %11.3f  %.9f -> %.9f" % (
            r["piece"], r["ratio"], r["out_nv"], r["out_nf"],
            r["axis_point_norm_src"], r["axis_point_norm_out"],
            r["axis_dir_norm_src"], r["axis_dir_norm_out"]))
    print("gaps (pair  gap1 -> gap3  ratio)")
    for g in gaps:
        print("  %-4s %10.6f -> %10.6f  x%.6f" % (g["pair"], g["gap1"], g["gap3"], g["ratio"]))
    return 0

if __name__ == "__main__":
    sys.exit(main())
