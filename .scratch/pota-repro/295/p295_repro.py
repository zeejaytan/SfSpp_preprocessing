#!/usr/bin/env python3
"""Ticket 295 -- reproduction gate against ticket 293.

The ticket says every 293 number this one quotes must reproduce to 0.05 mm and 1 coverage point, or
the difference must be stated.  So this script re-derives, from the artefacts that still exist, every
293 quantity that can be re-derived at all, and compares:

  assign_summary.tsv   6 rows x (c0, c1, dropped, unclustered, kept_share, nearest_kept_c0/c1,
                       d_all_med, d_kept_med)   -- from census/*.assign.tsv dots + the dump
  crosspair.tsv        6 rows' median / cov_ours / cov_auth / max_ours
  lanes_fresh.tsv      18 rows' n_ours, n_auth, median, len_ours, len_auth (len only where both
                       sides' dots survive, i.e. the three Phase-A lanes)
  clusters.tsv         per-cluster size / r50 / r95 / ax50 for the nine dump pieces
  classify.tsv         NOT reproducible: those lines are C++ log output ("[PAPER-234] classify: ...")
                       from the stage builds, whose trees were deleted.  Quoted as log, never as a
                       re-derivation -- stated in the ticket.

Tolerances: geometric quantities 0.05 mm; shares/coverage 1.0 point; counts 0.
Output: out/repro293.tsv (item, subject, quantity, v293, v295, delta, tol, verdict) and a summary
line per group.
"""
import os
import sys
import numpy as np
from scipy.spatial import cKDTree

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from p295_lib import (CORP, read_dump, read_pcd_xyz, frame, axial, radial_unit, read_xyz6,
                      polyline_length, write_tsv, q)

R293 = "/data/gpfs/projects/punim2657/SfSpp/runs/20261025-0456_3ada802_p293-census/out"
TOL_MM = 0.05
TOL_PP = 1.0


def rows(path):
    with open(path) as fh:
        hdr = fh.readline().rstrip("\n").split("\t")
        for line in fh:
            if not line.strip():
                continue
            yield dict(zip(hdr, line.rstrip("\n").split("\t")))


LF_COLS = ["pot", "piece", "k", "n_ours", "n_auth", "median", "cov_ours", "cov_auth",
           "jumps", "max_step", "len_ours", "len_auth", "at_bar"]


def rows_nohdr(path, cols):
    for line in open(path):
        if not line.strip():
            continue
        yield dict(zip(cols, line.rstrip("\n").split("\t")))


def assign(dots, labels, P, kept):
    d_all, j_all = cKDTree(P).query(dots)
    lab_all = labels[j_all]
    K = np.concatenate([P[labels == c] for c in kept])
    Klab = np.concatenate([labels[labels == c] for c in kept])
    d_k, j_k = cKDTree(K).query(dots)
    return lab_all, d_all, Klab[j_k], d_k


def cov(a, b, bar=2.0):
    d, _ = cKDTree(b).query(a, k=1)
    return 100.0 * float((d <= bar).mean())


def main():
    out = []
    def chk(item, subject, quantity, v293, v295, tol, kind="mm"):
        try:
            d = abs(float(v293) - float(v295))
        except Exception:
            d = float("nan")
        ok = (d == d) and (d <= tol)
        if kind == "count":
            ok = (d == 0)
        out.append(dict(item=item, subject=subject, quantity=quantity, v293=v293, v295=v295,
                        delta=d, tol=tol, verdict="reproduced" if ok else "DIFFERS"))
        return ok

    # ---------- the three Phase-A lanes: both sides' dots survive, with their coordinates
    native = {}
    for name in sorted(os.listdir(os.path.join(R293, "census"))):
        if not name.endswith(".assign.tsv"):
            continue
        piece = name.split("_Bl")[0]
        lane = int(name.split("_Bl")[1].split(".")[0])
        side = {"ours": [], "authors": []}
        for r in rows(os.path.join(R293, "census", name)):
            side[r["side"]].append(r)
        P = {s: np.array([[float(x["x"]), float(x["y"]), float(x["z"])]
                          for x in sorted(side[s], key=lambda z: int(z["i"]))]) for s in side}
        native[(piece, lane)] = P

    print(f"[repro] Phase-A lanes with both sides' dots: {sorted(native)}", flush=True)
    for (piece, lane), P in native.items():
        hdr, cl, labels, Pd = read_dump(os.path.join(R293, "diag", piece + ".diag276.txt"))
        kept = [c for c in (0, 1) if int((labels == c).sum()) >= 200]
        a293 = {(r["piece"], int(r["lane"]), r["side"]): r
                for r in rows(os.path.join(R293, "assign_summary.tsv"))}
        for s in ("ours", "authors"):
            r = a293.get((piece, lane, s))
            if r is None:
                continue
            lab_all, d_all, lab_k, d_k = assign(P[s], labels, Pd, kept)
            n = len(P[s])
            sh = lambda m: 100.0 * float(m.sum()) / n
            for key, mine in (("c0", sh(lab_all == 0)), ("c1", sh(lab_all == 1)),
                              ("dropped", sh(lab_all >= 2)), ("unclustered", sh(lab_all < 0)),
                              ("nearest_kept_c0", sh(lab_k == 0)), ("nearest_kept_c1", sh(lab_k == 1)),
                              ("d_all_med", float(np.median(d_all))),
                              ("d_kept_med", float(np.median(d_k)))):
                kind = "mm" if key.startswith("d_") else "pp"
                chk("assign_summary", f"{piece}_Bl{lane}/{s}", key, r[key], mine,
                    TOL_MM if kind == "mm" else TOL_PP, kind)
            chk("assign_summary", f"{piece}_Bl{lane}/{s}", "n", r["n"], n, 0, "count")
        # crosspair: this lane's own dots against the authors' lane of the other index
        xp = [r for r in rows(os.path.join(R293, "crosspair.tsv"))]
        for r in xp:
            if r["piece"] != piece or int(r["ours_lane"]) != lane:
                continue
            j = int(r["authors_lane"])
            key = (piece, j)
            if key not in native:
                continue
            ours, auth = P["ours"], native[key]["authors"]
            d, _ = cKDTree(auth).query(ours, k=1)
            chk("crosspair", f"{piece} ours{lane} vs auth{j}", "median", r["median"],
                float(np.median(d)), TOL_MM)
            chk("crosspair", f"{piece} ours{lane} vs auth{j}", "cov_ours", r["cov_ours"],
                cov(ours, auth), TOL_PP, "pp")
            chk("crosspair", f"{piece} ours{lane} vs auth{j}", "cov_auth", r["cov_auth"],
                cov(auth, ours), TOL_PP, "pp")
            chk("crosspair", f"{piece} ours{lane} vs auth{j}", "max_ours", r["max_ours"],
                float(d.max()), TOL_MM)
        # lanes_fresh: arcs and n
        lf = {(r["piece"], int(r["k"])): r
              for r in rows_nohdr(os.path.join(R293, "lanes_fresh.tsv"), LF_COLS)}
        r = lf.get((piece, lane))
        if r is not None:
            chk("lanes_fresh", f"{piece}_Bl{lane}", "n_ours", r["n_ours"], len(P["ours"]), 0, "count")
            chk("lanes_fresh", f"{piece}_Bl{lane}", "n_auth", r["n_auth"], len(P["authors"]), 0, "count")
            chk("lanes_fresh", f"{piece}_Bl{lane}", "len_ours", r["len_ours"],
                polyline_length(P["ours"]), TOL_MM)
            chk("lanes_fresh", f"{piece}_Bl{lane}", "len_auth", r["len_auth"],
                polyline_length(P["authors"]), TOL_MM)
            d, _ = cKDTree(P["authors"]).query(P["ours"], k=1)
            chk("lanes_fresh", f"{piece}_Bl{lane}", "median", r["median"], float(np.median(d)), TOL_MM)

    # ---------- clusters.tsv over all nine dump pieces
    have = {p[:-len(".diag276.txt")] for p in os.listdir(os.path.join(R293, "diag"))
            if p.endswith(".diag276.txt")}
    for r in rows(os.path.join(R293, "clusters.tsv")):
        piece = r["piece"]
        if piece not in have:
            continue
        axis = os.path.join(CORP, "Axes", piece + "_Axis.xyz")
        p0, w, u, v = frame(axis)
        hdr, cl, labels, Pd = read_dump(os.path.join(R293, "diag", piece + ".diag276.txt"))
        c = int(r["cluster"])
        m = labels == c
        if m.sum() == 0:
            continue
        a, rad, _ = axial(Pd[m], p0, w, u, v)
        chk("clusters", f"{piece} c{c}", "size", r["size"], int(m.sum()), 0, "count")
        chk("clusters", f"{piece} c{c}", "r50", r["r50"], q(rad, 50), TOL_MM)
        chk("clusters", f"{piece} c{c}", "r95", r["r95"], q(rad, 95), TOL_MM)
        chk("clusters", f"{piece} c{c}", "ax50", r["ax50"], q(a, 50), TOL_MM)

    write_tsv(os.path.join(sys.argv[1] if len(sys.argv) > 1 else "out", "repro293.tsv"), out)
    bad = [o for o in out if o["verdict"] != "reproduced"]
    groups = {}
    for o in out:
        g = groups.setdefault(o["item"], [0, 0, 0.0])
        g[0] += 1
        if o["verdict"] != "reproduced":
            g[1] += 1
        if o["delta"] == o["delta"]:
            g[2] = max(g[2], o["delta"])
    for g, (n, nb, mx) in groups.items():
        print(f"[repro] {g:>14s}: {n-nb}/{n} reproduced, worst delta {mx:.4f}", flush=True)
    print(f"[repro] TOTAL {len(out)-len(bad)}/{len(out)} reproduced", flush=True)
    for o in bad[:40]:
        print("   DIFFERS", o, flush=True)


if __name__ == "__main__":
    main()
