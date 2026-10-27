#!/usr/bin/env python3
"""ticket 30 -- part A: does curvature explain the angle the cloud carries?
part B: two rules that derive theta from a cloud, and what each one gives.

Runs on this ticket's OWN re-derived clouds (out/dump/<TAG>/<PIECE>/r1_downsampled.ply --
the cloud the growth consumes) and on the meshes named in out/meshpaths.tsv, so the table
is one run and nothing is quoted from ticket 29.

Part A, per cloud, measured on the cloud (not the mesh):
  s            median nearest-neighbour spacing, mm
  rho          median local curvature radius, mm: a quadric fit over the k nearest
               neighbours in a local PCA frame, radius = 1 / max(|k1|,|k2|), at k = 30 and
               as a sensitivity check at k = 10, with p25/p50/p75 at k = 30
  pred_deg     degrees(s / rho): a normal turns by about s / rho radians over a step s
  measured_p50 p50 of the neighbour-normal angle distribution at k = 10, using ticket 29's
               own arithmetic (replica29.pair_angles: float32 normalise/dot/clamp, double
               acos), so this number is comparable with that ticket's
  ratio        measured_p50 / pred_deg, and its spread against the spread of measured_p50
  mesh_floor   median folded angle (|dot|) between the cloud's own normal and the normal of
               the nearest mesh vertex -- the honest noise floor of the estimator

Part B:
  Rule C  theta = c * pred_deg, c fitted so Pot A 07 gives back the shipped 3.4 deg.
  Rule Q  theta = the 0.7237 quantile of that cloud's own k = 10 neighbour-angle
          distribution (0.7237 is the fraction of Pot A 07's pairs 3.4 deg accepts).
Both are calibrated on the pot BY CONSTRUCTION: the pot is a calibration, not a test.

usage: analyse30.py <run_dir>
writes <run_dir>/out/tableA30.tsv, rules30.tsv, thetas30.json
"""
import json
import math
import os
import sys

import numpy as np
from scipy import stats as sps
from scipy.spatial import cKDTree

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import replica29 as R  # noqa: E402  (ticket 29's own angle arithmetic, reused verbatim)

NB = 10                      # the growth's own k (ticket 29 part A)
K_RHO = 30
K_RHO_SENS = 10
RHO_CAP_MM = 1.0e4           # a flat patch: report the cap, not 1e12
SPACING_CAP_MM = 1.0e4
MAX_PTS_RHO = 100000         # curvature fit is per-point lstsq; a cap keeps memory sane
MAX_PTS_MESH = 200000
POTA = "Pot_A_Piece_07"
POTA_DEG = 3.4
QFRAC = 0.7237
CLOUDS = ([("PA", POTA)] +
          [("B", "Juglet_Piece_%d" % i) for i in (2, 3, 5, 7)] +
          [("E", "Juglet_Piece_%d" % i) for i in (2, 3, 5, 7)])
ARM_OF = {"PA": "Pot A 07 (defaults)", "B": "Juglet defaults (chain on, 0.6 mm)",
          "E": "Juglet chain off, native density"}


def read_cloud_cell(dump, tag, piece):
    """The two rung files this cloud needs, and the r1 == r2 identity the growth relies on."""
    d = os.path.join(dump, tag, piece)
    r1 = os.path.join(d, "r1_downsampled.ply")
    r2 = os.path.join(d, "r2_clusters_premerge.ply")
    for f in (r1, r2):
        if not os.path.isfile(f):
            raise SystemExit("[A30] missing cloud file: %s" % f)
    xyz, nrm, _cid, _rsn, props = R.read_rung2_ply(r2)
    x1, n1, _c1, _r1, _p1 = R.read_rung2_ply(r1)
    same = bool(x1.shape == xyz.shape and np.array_equal(x1, xyz)
                and np.array_equal(n1, nrm))
    return xyz, nrm, props, same, r1


def nearest_spacing(pts, tree):
    d, _ = tree.query(pts, k=2, workers=-1)
    return float(np.median(d[:, 1]))


def quadric_radii(pts, sub, tree, k):
    """radius = 1 / max(|k1|,|k2|) of an osculating paraboloid over the k nearest neighbours.

    Local frame: PCA of the neighbour offsets (z = direction of least variance), so the fit
    does not inherit a noisy stored normal.  z = a x + b y + L x^2/2 + M xy + N y^2/2 + d;
    a tangent frame gives the second fundamental form [[L,M],[M,N]] at the point, so the
    principal curvatures are its eigenvalues.
    """
    n = pts.shape[0]
    kq = int(min(k, n))
    _d, nb = tree.query(pts[sub], k=kq, workers=-1)
    Q = pts[nb]                                  # (m,k,3)
    P = pts[sub]
    C = Q - Q.mean(axis=1, keepdims=True)
    cov = np.einsum("mki,mkj->mij", C, C)
    _w, V = np.linalg.eigh(cov)
    e = V[:, :, 0]                               # least-variance direction
    a = np.tile(np.array([1.0, 0.0, 0.0]), (e.shape[0], 1))
    a[np.abs(e[:, 0]) > 0.9] = np.array([0.0, 1.0, 0.0])
    u = np.cross(e, a)
    u /= np.linalg.norm(u, axis=1, keepdims=True)
    v = np.cross(e, u)
    rel = Q - P[:, None, :]
    x = np.einsum("mki,mi->mk", rel, u)
    y = np.einsum("mki,mi->mk", rel, v)
    z = np.einsum("mki,mi->mk", rel, e)
    one = np.ones_like(x)
    A = np.stack([x, y, 0.5 * x * x, x * y, 0.5 * y * y, one], axis=2)
    M = np.einsum("mki,mkj->mij", A, A)
    b = np.einsum("mki,mk->mi", A, z)
    ridge = 1e-12 * np.trace(M, axis1=1, axis2=2)
    M[:, np.arange(6), np.arange(6)] += ridge[:, None]
    coef = np.linalg.solve(M, b[:, :, None])[:, :, 0]
    L, Mm, N = coef[:, 2], coef[:, 3], coef[:, 4]
    tr = L + N
    det = L * N - Mm * Mm
    disc = np.sqrt(np.maximum(0.25 * tr * tr - det, 0.0))
    k1 = 0.5 * tr + disc
    k2 = 0.5 * tr - disc
    kmax = np.maximum(np.abs(k1), np.abs(k2))
    ok = np.isfinite(kmax)
    rad = np.full(kmax.shape, np.inf)
    good = ok & (kmax > 1.0 / RHO_CAP_MM)
    rad[good] = 1.0 / kmax[good]
    rad[~np.isfinite(rad)] = RHO_CAP_MM
    return np.clip(rad, 0.0, RHO_CAP_MM)


def rho_stats(pts, tree, k, rng):
    sub = np.arange(pts.shape[0])
    if sub.size > MAX_PTS_RHO:
        sub = np.sort(rng.choice(sub, size=MAX_PTS_RHO, replace=False))
    rad = quadric_radii(pts, sub, tree, k)
    q = np.percentile(rad, [25, 50, 75])
    return {"k": int(k), "n_fit": int(rad.size), "p25": float(q[0]),
            "p50": float(q[1]), "p75": float(q[2]),
            "share_at_cap": float(np.mean(rad >= RHO_CAP_MM - 1e-9)),
            "median": float(np.median(rad))}


def read_obj_normals(path):
    """Vertices and area-weighted vertex normals from a Wavefront OBJ."""
    verts = []
    faces = []
    with open(path, "r", errors="replace") as fh:
        for line in fh:
            if line.startswith("v "):
                p = line.split()
                verts.append((float(p[1]), float(p[2]), float(p[3])))
            elif line.startswith("f "):
                idx = []
                for tok in line.split()[1:]:
                    idx.append(int(tok.split("/")[0]))
                if len(idx) >= 3:
                    faces.append(idx)
    v = np.asarray(verts, dtype=np.float64)
    fn = np.zeros_like(v)
    for f in faces:
        idx = np.asarray([i - 1 if i > 0 else v.shape[0] + i for i in f], dtype=np.int64)
        p = v[idx]
        # fan triangulation keeps quads and n-gons honest
        for t in range(1, idx.size - 1):
            a, b, c = p[0], p[t], p[t + 1]
            nrm = np.cross(b - a, c - a)
            fn[idx[0]] += nrm
            fn[idx[t]] += nrm
            fn[idx[t + 1]] += nrm
    ln = np.linalg.norm(fn, axis=1)
    ln[ln == 0.0] = 1.0
    return v, fn / ln[:, None], len(faces)


def mesh_floor(pts, nrm, verts, vnorm, rng):
    """Median folded angle (deg) between the cloud's normal and the nearest mesh vertex normal."""
    sub = np.arange(pts.shape[0])
    if sub.size > MAX_PTS_MESH:
        sub = np.sort(rng.choice(sub, size=MAX_PTS_MESH, replace=False))
    tree = cKDTree(verts)
    _d, idx = tree.query(pts[sub], k=1, workers=-1)
    a = R.normalised_f32(nrm[sub])
    b = R.normalised_f32(vnorm[idx])
    dot = (a[:, 0] * b[:, 0] + a[:, 1] * b[:, 1] + a[:, 2] * b[:, 2]).astype(np.float32)
    dot = np.where(dot < -1.0, np.float32(-1.0), dot).astype(np.float32)
    dot = np.where(dot > 1.0, np.float32(1.0), dot).astype(np.float32)
    ang = np.degrees(np.arccos(np.abs(dot).astype(np.float64)))
    ang = ang[np.isfinite(ang)]
    return float(np.median(ang)), int(ang.size)


def corr(xs, ys):
    a = np.asarray(xs, dtype=np.float64)
    b = np.asarray(ys, dtype=np.float64)
    pear = float(np.corrcoef(a, b)[0, 1]) if a.size > 2 else float("nan")
    spr = float(sps.spearmanr(a, b).correlation) if a.size > 2 else float("nan")
    return pear, spr


def cv(xs):
    a = np.asarray(xs, dtype=np.float64)
    m = float(np.mean(a))
    return float(np.std(a, ddof=1) / m) if a.size > 1 and m != 0.0 else float("nan")


def write_tsv(path, header, rows):
    with open(path, "w") as fh:
        fh.write("\t".join(header) + "\n")
        for r in rows:
            fh.write("\t".join("" if v is None else (("%.6f" % v) if isinstance(v, float) else str(v))
                               for v in r) + "\n")


def _angles_p50(pts, nu, tree):
    _d, nbr = tree.query(pts, k=NB + 1, workers=-1)
    rows, cols = R.neighbour_pairs(pts.shape[0], nbr, NB)
    ang = R.pair_angles(nu, rows, cols)
    st = R.angles_stats(ang)
    return float(st["p50"])


def selftest():
    """A sphere of known radius: recover the radius, and show that measured/pred is a pure
    function of s / rho (so part A compares clouds, not absolute ratios -- the p50 pair angle
    sits at the median of the k = 10 neighbour distances, not at the nearest-neighbour step).
    """
    rng = np.random.default_rng(30)
    n = 8000
    u = rng.normal(size=(n, 3))
    u /= np.linalg.norm(u, axis=1, keepdims=True)
    nu = R.normalised_f32(u.astype(np.float32))
    fails = []
    ratios = {}
    for rad in (20.0, 40.0):
        pts = u * rad
        tree = cKDTree(pts)
        s = nearest_spacing(pts, tree)
        st = rho_stats(pts, tree, K_RHO, rng)
        err = abs(st["p50"] - rad) / rad
        measured = _angles_p50(pts, nu, tree)
        pred = math.degrees(s / rad)
        ratios[rad] = measured / pred
        print("[SELFTEST] sphere r=%5.1f spacing=%.4f rho50=%.3f (err %.2f%%) pred=%.4f "
              "measured_p50=%.4f ratio=%.3f" % (rad, s, st["p50"], 100.0 * err, pred, measured,
                                                ratios[rad]))
        if err > 0.10:
            fails.append("rho r=%g err=%.2f%%" % (rad, 100.0 * err))
    spread = abs(ratios[20.0] - ratios[40.0]) / ratios[20.0]
    print("[SELFTEST] ratio is invariant across the two radii: %.3f vs %.3f (spread %.2f%%)"
          % (ratios[20.0], ratios[40.0], 100.0 * spread))
    if spread > 0.05:
        fails.append("ratio not scale invariant: spread %.2f%%" % (100.0 * spread))
    if fails:
        for f in fails:
            print("[SELFTEST] FAIL " + f)
        return 1
    print("[SELFTEST] PASS curvature radius recovered, and measured/pred depends only on s/rho")
    return 0


def main(argv):
    if len(argv) >= 2 and argv[1] == "--selftest":
        return selftest()
    if len(argv) < 2:
        print("usage: analyse30.py --selftest | <run_dir>")
        return 2
    run = os.path.abspath(argv[1])
    dump = os.path.join(run, "out", "dump")
    out = os.path.join(run, "out")
    mp = os.path.join(out, "meshpaths.tsv")
    mesh_of = {}
    if os.path.isfile(mp):
        with open(mp) as fh:
            for line in fh:
                f = line.rstrip("\n").split("\t")
                if len(f) >= 2 and f[0] and not f[0].startswith("#"):
                    mesh_of[(f[0], f[1])] = f[2] if len(f) > 2 else f[1]
    rng = np.random.default_rng(30)
    rows = []
    loaded = {}
    for tag, piece in CLOUDS:
        key = "%s/%s" % (tag, piece)
        xyz, nrm, props, same, r1path = read_cloud_cell(dump, tag, piece)
        n = int(xyz.shape[0])
        pts = xyz.astype(np.float64)
        tree = cKDTree(pts)
        s = nearest_spacing(pts, tree)
        nu = R.normalised_f32(nrm)
        zero_normals = int(np.count_nonzero(np.isnan(nu[:, 0])))
        _d, nbr = tree.query(pts, k=int(min(NB + 1, n)), workers=-1)
        nbr = np.atleast_2d(np.asarray(nbr))
        if nbr.shape[0] != n:
            nbr = nbr.reshape(n, -1)
        rows_ij, cols_ij = R.neighbour_pairs(n, nbr, NB)
        ang = R.pair_angles(nu, rows_ij, cols_ij)
        ast = R.angles_stats(ang)
        measured = float(ast["p50"])
        q72 = float(np.quantile(ang[np.isfinite(ang)], QFRAC))
        st30 = rho_stats(pts, tree, K_RHO, rng)
        st10 = rho_stats(pts, tree, K_RHO_SENS, rng)
        rho = st30["median"]
        pred = math.degrees(s / rho) if rho > 0 else float("nan")
        floor = float("nan")
        nfloor = 0
        mpath = mesh_of.get((tag, piece), "")
        if mpath and os.path.isfile(mpath):
            verts, vnorm, nfaces = read_obj_normals(mpath)
            floor, nfloor = mesh_floor(pts, nrm, verts, vnorm, rng)
        else:
            nfaces = -1
        rec = {"cloud": key, "arm": tag, "piece": piece, "n": n, "props": ",".join(props),
               "r1_eq_r2": same, "s_mm": s, "rho_k30": rho, "rho_p25": st30["p25"],
               "rho_p75": st30["p75"], "rho_share_at_cap": st30["share_at_cap"],
               "rho_k10": st10["median"], "pred_deg": pred, "measured_p50": measured,
               "ratio": measured / pred if pred else float("nan"),
               "theta_q": q72, "mesh_floor_deg": floor, "mesh_verts": nfloor,
               "mesh_faces": nfaces, "zero_normals": zero_normals,
               "n_pairs": ast.get("n_pairs"), "n_angles_nan": ast.get("n_nan"),
               "p10": ast.get("p10"), "p90": ast.get("p90"),
               "share_le_3p4": ast.get("le_3.4")}
        loaded[key] = rec
        rows.append(rec)
        print("[A30] %-22s n=%-7d s=%.4f rho30=%.3f rho10=%.3f pred=%.3f measured_p50=%.3f "
              "ratio=%.3f thetaQ=%.3f floor=%.3f r1eqr2=%s"
              % (key, n, s, rho, st10["median"], pred, measured,
                 rec["ratio"], q72, floor, same))

    hdr = ["cloud", "arm", "piece", "n_cloud", "s_mm", "rho_k30_mm", "rho_k30_p25", "rho_k30_p75",
           "rho_k30_share_at_cap", "rho_k10_mm", "pred_deg", "measured_p50_deg", "ratio_p50_over_pred",
           "theta_q_deg", "mesh_floor_deg", "mesh_verts_used", "mesh_faces",
           "r1_eq_r2", "zero_normals", "n_pairs", "angles_nan", "p10_deg", "p90_deg",
           "share_le_3p4", "r1_file"]
    table = []
    for r in rows:
        table.append([r["cloud"], r["arm"], r["piece"], r["n"], r["s_mm"], r["rho_k30"],
                      r["rho_p25"], r["rho_p75"], r["rho_share_at_cap"], r["rho_k10"],
                      r["pred_deg"], r["measured_p50"], r["ratio"], r["theta_q"],
                      r["mesh_floor_deg"], r["mesh_verts"], r["mesh_faces"],
                      r["r1_eq_r2"], r["zero_normals"], r["n_pairs"], r["n_angles_nan"],
                      r["p10"], r["p90"], r["share_le_3p4"], ""])
    write_tsv(os.path.join(out, "tableA30.tsv"), hdr, table)

    preds = [r["pred_deg"] for r in rows]
    meas = [r["measured_p50"] for r in rows]
    ratios = [r["ratio"] for r in rows]
    pear, spr = corr(preds, meas)
    cv_ratio = cv(ratios)
    cv_meas = cv(meas)
    print("[A30] correlation across the %d clouds: pearson=%.4f spearman=%.4f" % (len(rows), pear, spr))
    print("[A30] ratio spread cv=%.4f vs measured_p50 spread cv=%.4f -> %s"
          % (cv_ratio, cv_meas,
             "ratio varies MORE than measured_p50 (hypothesis refuted by the ticket's own test)"
             if cv_ratio > cv_meas else
             "ratio varies less than measured_p50 (hypothesis not refuted by that test)"))

    # ---- part B: the two rules, both calibrated so Pot A 07 gives back 3.4 deg
    pac = loaded.get("PA/%s" % POTA)
    if pac is None:
        print("[B30] FATAL no Pot A 07 cloud; the calibration cannot be run")
        return 3
    cfit = POTA_DEG / pac["pred_deg"]
    print("[B30] calibration: Pot A 07 pred_deg=%.6f so c = 3.4 / pred = %.6f"
          % (pac["pred_deg"], cfit))
    rules = []
    for r in rows:
        thc = cfit * r["pred_deg"]
        rules.append({"cloud": r["cloud"], "arm": r["arm"], "piece": r["piece"],
                      "pred_deg": r["pred_deg"], "theta_c": thc,
                      "residual_deg": r["measured_p50"] - thc,
                      "theta_q": r["theta_q"], "c": cfit})
        print("[B30] %-22s thetaC=%.4f residual=%.4f thetaQ=%.4f" %
              (r["cloud"], thc, r["measured_p50"] - thc, r["theta_q"]))
    write_tsv(os.path.join(out, "rules30.tsv"),
              ["cloud", "arm", "piece", "pred_deg", "theta_c_deg", "residual_measured_p50_minus_theta_c",
               "theta_q_deg", "c"],
              [[x["cloud"], x["arm"], x["piece"], x["pred_deg"], x["theta_c"], x["residual_deg"],
                x["theta_q"], x["c"]] for x in rules])

    def med(vals):
        return float(np.median(np.asarray(vals, dtype=np.float64)))

    b_rules = [x for x in rules if x["arm"] == "B"]
    e_rules = [x for x in rules if x["arm"] == "E"]
    thetas = {
        "calibration": {"cloud": "PA/" + POTA, "computed_pota_theta_q": pac["theta_q"],
                        "shipped_theta": POTA_DEG, "qfrac": QFRAC},
        "ruleC": {"c_from_pota": cfit,
                  "per_cloud": {x["cloud"]: x["theta_c"] for x in rules},
                  "juglet_arm_theta": med([x["theta_c"] for x in b_rules]),
                  "juglet_arm_theta_e_clouds": med([x["theta_c"] for x in e_rules]),
                  "residuals_deg": {x["cloud"]: x["residual_deg"] for x in rules}},
        "ruleQ": {"per_cloud": {x["cloud"]: x["theta_q"] for x in rules},
                  "juglet_arm_theta": med([x["theta_q"] for x in b_rules]),
                  "juglet_arm_theta_e_clouds": med([x["theta_q"] for x in e_rules])},
        "arm_policy": "a pipeline arm sets one theta per vessel, so the vessel's value is the "
                      "median over the four defaults-chain clouds (arm B) -- the chain the "
                      "shipped binary actually runs; the E-cloud medians are reported beside it",
        "correlations": {"pearson": pear, "spearman": spr},
        "ratio_spread": {"cv_ratio": cv_ratio, "cv_measured_p50": cv_meas},
    }
    gap = abs(thetas["ruleC"]["juglet_arm_theta"] - thetas["ruleQ"]["juglet_arm_theta"])
    thetas["arm_gap_deg"] = gap
    thetas["run_third_juglet_arm"] = bool(gap > 1.0)
    with open(os.path.join(out, "thetas30.json"), "w") as fh:
        json.dump(thetas, fh, indent=2, sort_keys=True)
    print("[B30] THETA rule C juglet arm = %.4f deg (E clouds %.4f)"
          % (thetas["ruleC"]["juglet_arm_theta"], thetas["ruleC"]["juglet_arm_theta_e_clouds"]))
    print("[B30] THETA rule Q juglet arm = %.4f deg (E clouds %.4f)"
          % (thetas["ruleQ"]["juglet_arm_theta"], thetas["ruleQ"]["juglet_arm_theta_e_clouds"]))
    print("[B30] gap=%.4f deg -> third juglet arm %s"
          % (gap, "RUNS (gap > 1 deg)" if thetas["run_third_juglet_arm"] else "NOT run (gap <= 1 deg)"))
    print("[B30] wrote %s, %s, %s"
          % (os.path.join(out, "tableA30.tsv"), os.path.join(out, "rules30.tsv"),
             os.path.join(out, "thetas30.json")))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
