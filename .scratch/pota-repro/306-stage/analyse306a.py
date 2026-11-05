#!/usr/bin/env python3
"""analyse306a.py -- read the Stage A pool dump and answer A1/A2.

Input: the fetched out/pool tree (one dir per <piece>_t<trunc>/s<seed>).
Output: a readable report on stdout plus out/pool_report.tsv (one row per
cluster, all cases merged) for the ticket.

Nothing here is part of the shipped rule; released-line angles are read from the
pool dump's own ang_rel_all column (computed at run time) and are scoring only.
"""
import argparse
import glob
import json
import os

import numpy as np

COLS = ["rank_gm", "cluster", "is_cluster_rep", "gm_cd", "huber_cd", "huber_all",
        "gm_all", "inl_all", "dx", "dy", "dz", "ang_rel_min", "ang_rel_idx",
        "ang_rel_all", "drop_dedup", "drop_prune", "in_top10", "kept"]


def load_case(d):
    with open(os.path.join(d, "case.json")) as fh:
        meta = json.load(fh)
    rows = []
    with open(os.path.join(d, "candidates.tsv")) as fh:
        head = fh.readline().rstrip("\n").split("\t")
        assert head == COLS, head
        for line in fh:
            f = line.rstrip("\n").split("\t")
            rows.append(dict(rank=int(f[0]), cluster=int(f[1]), is_rep=int(f[2]),
                             gm_cd=float(f[3]), huber_cd=float(f[4]),
                             huber_all=float(f[5]), inl_all=int(f[7]),
                             d=np.array([float(f[8]), float(f[9]), float(f[10])]),
                             ang=np.array([float(x) for x in f[13].split()]),
                             drop_dedup=int(f[14]), drop_prune=int(f[15]),
                             in_top10=int(f[16]), kept=int(f[17])))
    meta["dir"] = d
    meta["rows"] = rows
    return meta


def per_line(members, k):
    """min angle to released line k over the cluster's members, and which member."""
    a = np.array([r["ang"][k] if k < len(r["ang"]) else np.nan for r in members])
    j = int(np.argmin(a))
    return float(a[j]), members[j]["rank"]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pool", required=True)
    ap.add_argument("--out", default=".")
    ap.add_argument("--near", type=float, default=10.0, help="deg: 'a cluster here?'")
    a = ap.parse_args()

    cases = {}
    for d in sorted(glob.glob(os.path.join(a.pool, "*", "s*"))):
        m = load_case(d)
        tag = os.path.basename(os.path.dirname(d))          # PA07_t0
        m["trunc"] = int(tag.split("_t")[1])
        m["seed"] = int(os.path.basename(d)[1:])
        cases[(m["piece"], m["trunc"], m["seed"])] = m

    nlines = max(len(r["ang"]) for c in cases.values() for r in c["rows"])
    print("cases: %s" % ", ".join("P%02d t%d s%d" % k for k in sorted(cases)))
    print("released lines per piece: " + ", ".join(
        "P%02d=%d" % (p, max(len(r["ang"]) for c in cases.values() if c["piece"] == p
                             for r in c["rows"])) for p in sorted({k[0] for k in cases})))

    out_rows = []
    print("\n=== A1: clusters per case (rep = what the 10-deg dedup keeps) ===")
    for key in sorted(cases):
        m = cases[key]
        rows = m["rows"]
        print("\n-- P%02d trunc=%d seed=%d  n=%d  K=%d  clusters=%d  "
              "kept(full dedup+prune)=%d  shipped-replica K=%d  %.1fs"
              % (m["piece"], m["trunc"], m["seed"], m["n"], m["K"],
                 m["n_clusters"], m["n_kept"], m["faithful_K"], m["secs"]))
        print("  cl  size  rank  hub_cd_rep  hub_all_min  "
              + "  ".join("L%d" % k for k in range(nlines))
              + "   prune  top10  kept")
        for ci in range(m["n_clusters"]):
            mem = [r for r in rows if r["cluster"] == ci]
            rep = [r for r in mem if r["is_rep"]][0]
            pl = [per_line(mem, k) for k in range(nlines)]
            best = min(mem, key=lambda r: r["huber_all"])
            print("  %2d  %5d  %4d  %10.3e  %11.3e  "
                  % (ci, len(mem), rep["rank"], rep["huber_cd"], best["huber_all"])
                  + "  ".join("%5.1f" % pl[k][0] for k in range(nlines))
                  + "  %5d  %5d  %4d"
                  % (int(rep["drop_prune"]), int(rep["in_top10"]), int(rep["kept"])))
            out_rows.append(dict(piece=m["piece"], trunc=m["trunc"], seed=m["seed"],
                                 n=m["n"], cluster=ci, size=len(mem),
                                 rep_rank=rep["rank"], gm_cd=rep["gm_cd"],
                                 huber_cd_rep=rep["huber_cd"],
                                 huber_all_min=best["huber_all"],
                                 best_rank=best["rank"],
                                 **{"ang_L%d" % k: pl[k][0] for k in range(nlines)},
                                 drop_prune=int(rep["drop_prune"]),
                                 in_top10=int(rep["in_top10"]),
                                 kept=int(rep["kept"])))

    # ---- A2(i): does another line's basin exist anywhere in the pool?
    print("\n=== A2(i): every case, the best candidate per released line ===")
    for p in sorted({k[0] for k in cases}):
        for k in range(nlines):
            best = []
            for key in sorted(k for k in cases if k[0] == p):
                m = cases[key]
                cand = [r for r in m["rows"] if k < len(r["ang"])]
                if not cand:
                    continue
                r = min(cand, key=lambda r: r["ang"][k])
                best.append((key, r["ang"][k], r["rank"], r["cluster"], r["huber_cd"],
                             r["kept"]))
            print("  P%02d L%d: " % (p, k) + " | ".join(
                "t%d s%d %.2f (rank %d, cl %d, cost %.2e, kept %d)" % (
                    kk[1], kk[2], ang, rk, cl, c, kp)
                for kk, ang, rk, cl, c, kp in best))

    # ---- A2(ii): piece 08 cluster provenance, trunc-off vs trunc-on
    p8 = sorted(k for k in cases if k[0] == 8)
    if p8:
        print("\n=== A2(ii): Piece 08 -- clusters by released-line neighbourhood ===")
        for k in range(nlines):
            print("  released line %d:" % k)
            for key in p8:
                m = cases[key]
                cand = [r for r in m["rows"] if k < len(r["ang"])]
                if not cand:
                    continue
                r = min(cand, key=lambda r: r["ang"][k])
                mem = [x for x in m["rows"] if x["cluster"] == r["cluster"]]
                print("    t%d s%d nearest %.2f deg (cl %d, size %d, rank %d, "
                      "rep cost %.3e, rep dropped=%s, kept=%d)"
                      % (key[1], key[2], r["ang"][k], r["cluster"], len(mem),
                         r["rank"], r["huber_cd"],
                         "prune" if r["drop_prune"] else
                         ("dedup" if r["drop_dedup"] else "no"), r["kept"]))
        for seed in sorted({k[2] for k in p8}):
            off = [c for c in p8 if c[1] == 0 and c[2] == seed][0]
            on = [c for c in p8 if c[1] == 1 and c[2] == seed][0]
            print("  seed %d: clusters off=%d on=%d ; kept off=%d on=%d"
                  % (seed, cases[off]["n_clusters"], cases[on]["n_clusters"],
                     cases[off]["n_kept"], cases[on]["n_kept"]))

    # ---- A1 cost story: what the prune drops
    print("\n=== A1b: cost distribution among dedup survivors (the 1.1 prune) ===")
    for key in sorted(cases):
        m = cases[key]
        surv = [r for r in m["rows"] if not r["drop_dedup"]]
        if not surv:
            continue
        c0 = surv[0]["huber_cd"]
        ratios = np.array([r["huber_cd"] / c0 for r in surv])
        print("  P%02d t%d s%d: survivors=%d  ratio min/median/max = %.3f/%.3f/%.3f"
              "  cut at 1.1 -> kept %d"
              % (m["piece"], m["trunc"], m["seed"], len(surv), ratios.min(),
                 float(np.median(ratios)), ratios.max(),
                 int((ratios < 1.1).sum())))

    cols = ["piece", "trunc", "seed", "n", "cluster", "size", "rep_rank", "gm_cd",
            "huber_cd_rep", "huber_all_min", "best_rank"] + \
           ["ang_L%d" % k for k in range(nlines)] + \
           ["drop_prune", "in_top10", "kept"]
    with open(os.path.join(a.out, "pool_report.tsv"), "w") as fh:
        fh.write("\t".join(cols) + "\n")
        for r in out_rows:
            fh.write("\t".join(str(r[c]) if not isinstance(r[c], float)
                               else "%.6g" % r[c] for c in cols) + "\n")
    print("\nwrote %s (%d cluster rows)" % (os.path.join(a.out, "pool_report.tsv"),
                                            len(out_rows)))


if __name__ == "__main__":
    main()
