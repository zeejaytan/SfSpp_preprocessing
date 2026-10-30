#!/usr/bin/env python3
"""Ticket 46 prediction check: the theta and the counts, side by side.

Two references per piece, both carried as data:
  k43     the curvature formula's prediction (ticket 43), spec46.tsv column 5
  t45f    what run 20261030-2128_f4a3559_t45-default measured on the SHIPPED
          cloud, spec46.tsv column 6 (arm F, no env)

P1 asks whether feeding the growth an even covering at the spacing the run
already resolves puts theta back on the formula's number: within 2 pct on 9/9
Juglet pieces.  P4 asks whether the Pot A control is unchanged: same clusters
and same surface sizes as that run's arm F, which reads the same released
clouds with the same binary.

Exit 0 pass, 3 theta outside 2 pct, 4 a Juglet cell missing, 5 the Pot A
control moved, 6 the theta row is missing.
"""
import argparse
import os
import sys

# run 20261030-2128_f4a3559_t45-default, arm F (no env): pieces, clusters, surf0, surf1
T45F = {
    "Pot_A_Piece_01": (9, 67103, 82484),
    "Pot_A_Piece_02": (3, 42402, 46499),
    "Pot_A_Piece_03": (4, 40049, 43726),
    "Pot_A_Piece_04": (5, 34748, 38040),
    "Pot_A_Piece_05": (5, 31797, 34261),
    "Pot_A_Piece_06": (5, 22831, 25026),
    "Pot_A_Piece_07": (10, 24571, 26674),
    "Pot_A_Piece_08": (6, 27993, 29441),
}


def log(m):
    sys.stdout.write("[TH46] %s\n" % m)
    sys.stdout.flush()


def read_tsv(path):
    with open(path, "r") as fh:
        head = fh.readline().rstrip("\n").rstrip("\r").split("\t")
        rows = []
        for line in fh:
            line = line.rstrip("\n").rstrip("\r")
            if not line:
                continue
            p = line.split("\t")
            p += [""] * (len(head) - len(p))
            rows.append(dict(zip(head, p)))
    return head, rows


def fnum(s):
    try:
        return float(s)
    except (TypeError, ValueError):
        return None


def pct(a, b):
    if a is None or b in (None, 0):
        return None
    return 100.0 * (a - b) / b


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--cells", required=True)
    ap.add_argument("--spec", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--tol", type=float, default=2.0)
    a = ap.parse_args(argv)

    _h, spec_rows = read_tsv(a.spec)
    spec = {}
    for r in spec_rows:
        spec[(r["pot"], r["piece"])] = {"S": r["S_t45_mm"],
                                        "k43": fnum(r["theta_k43_deg"]),
                                        "t45": fnum(r["theta_t45_armF_deg"])}

    _h2, cells = read_tsv(a.cells)
    if not os.path.isdir(a.out):
        os.makedirs(a.out, exist_ok=True)
    out = os.path.join(a.out, "theta_check.tsv")
    head = ["pot", "piece", "arm", "ref_k43_deg", "ref_t45_armF_deg", "theta_deg",
            "abs_vs_k43", "pct_vs_k43", "within2pct_k43",
            "abs_vs_t45", "pct_vs_t45", "note"]
    rows = []
    jug_seen = 0
    jug_bad = []
    pota_bad = []
    missing_theta = []
    for r in cells:
        pot, piece, arm = r.get("pot", ""), r.get("piece", ""), r.get("arm", "")
        s = spec.get((pot, piece))
        if s is None:
            continue
        th = fnum(r.get("theta_computed_deg", ""))
        if th is None:
            missing_theta.append("%s/%s/%s" % (pot, piece, arm))
            rows.append({"pot": pot, "piece": piece, "arm": arm,
                         "ref_k43_deg": s["k43"], "ref_t45_armF_deg": s["t45"],
                         "theta_deg": "", "abs_vs_k43": "", "pct_vs_k43": "",
                         "within2pct_k43": "", "abs_vs_t45": "", "pct_vs_t45": "",
                         "note": "no GROWTH-45 theta in the log"})
            continue
        dk = None if s["k43"] is None else th - s["k43"]
        pk = pct(th, s["k43"])
        dt = None if s["t45"] is None else th - s["t45"]
        pt = pct(th, s["t45"])
        within = "" if pk is None else ("yes" if abs(pk) <= a.tol else "no")
        note = "ok"
        if arm == "covering":
            jug_seen += 1
            if within == "no":
                note = "theta moved %.2f pct off the k43 prediction" % abs(pk)
                jug_bad.append("%s(%+.2f%%)" % (piece, pk))
        rows.append({"pot": pot, "piece": piece, "arm": arm,
                     "ref_k43_deg": s["k43"], "ref_t45_armF_deg": s["t45"],
                     "theta_deg": "%.5f" % th,
                     "abs_vs_k43": "" if dk is None else "%.5f" % dk,
                     "pct_vs_k43": "" if pk is None else "%.3f" % pk,
                     "within2pct_k43": within,
                     "abs_vs_t45": "" if dt is None else "%.5f" % dt,
                     "pct_vs_t45": "" if pt is None else "%.3f" % pt,
                     "note": note})
        if arm == "control-released" and pot == "Pot_A":
            ref = T45F.get(piece)
            got = (fnum(r.get("clusters", "")), fnum(r.get("surf0_points", "")),
                   fnum(r.get("surf1_points", "")))
            if ref is None or None in got:
                note2 = "control counts unreadable"
                pota_bad.append("%s(unreadable)" % piece)
            elif got == tuple(float(x) for x in ref):
                note2 = "control identical to t45 arm F"
            else:
                note2 = "control differs from t45 arm F: %s vs %s" % (tuple(int(x) for x in got), ref)
                pota_bad.append("%s(%s)" % (piece, note2))
            rows[-1]["note"] = rows[-1]["note"] + "; " + note2

    with open(out, "w") as fh:
        fh.write("\t".join(head) + "\n")
        for r in rows:
            fh.write("\t".join(str(r[h]) for h in head) + "\n")
    log("wrote %s (%d rows)" % (out, len(rows)))
    for r in rows:
        log("%-4s %-16s %-16s ref=%-7s t45=%-8s got=%-9s pct=%s within=%s %s"
            % (r["pot"][:4], r["piece"][-16:], r["arm"][:16], r["ref_k43_deg"], r["ref_t45_armF_deg"],
               r["theta_deg"], r["pct_vs_k43"], r["within2pct_k43"], r["note"][:60]))

    log("Juglet covering cells seen: %d of 9" % jug_seen)
    if missing_theta:
        log("cells with no theta:%s" % (", ".join(missing_theta)))
    if jug_seen < 9:
        log("FAIL a Juglet piece did not produce a theta row")
        return 4
    if jug_bad:
        log("FAIL theta outside %.1f pct of the formula on: %s" % (a.tol, ", ".join(jug_bad)))
        return 3
    if pota_bad:
        log("FAIL the Pot A control is not unchanged: %s" % ", ".join(pota_bad))
        return 5
    if missing_theta:
        return 6
    log("PASS theta within %.1f pct of the formula on 9/9; Pot A control unchanged" % a.tol)
    return 0


if __name__ == "__main__":
    sys.exit(main())
