#!/usr/bin/env python3
"""Ticket 301 Phase 2 -- reduce assembly runs to per-piece rotation/translation error and pot counts.

The arithmetic is ticket 299's (299-work/edges299.py) verbatim, so the numbers are comparable with the
table in 299 section 3:

    T_rel = (G_i^-1 . G_j) . (T_i^-1 . T_j)^-1      for a ground-truth edge (i,j)
    seated on that edge  <=>  angle(T_rel) < 20.0488 deg  and  |t(T_rel)| < 50.0 mm

20.0488 deg and 50.0 mm are the assembler's own bar: class/data_structure.cpp:927 rad_threshold 0.35
and t_threshold 50.0, compared by isSimilarTrans at class/data_structure.cpp:661-680. A piece is
reported by its BEST incident ground-truth edge (the smallest angle, then the smallest translation),
which is how 299 section 3 reports it too.

A piece is "on" when the assembler saved out/Result/T_<i>to_<i>.txt for it. The assembler drops a piece
from the graph before assignment when its Breakline_0 has fewer than 50 points (Pot D 27 has 48).

Usage:
  python p301_report.py --corpus <dir with Axes/ + Ground Truth/> \
      --arm ctrl=<run dir> --arm swap=<run dir> [...] [--json out.json] [--pieces 18 25 26 28 29]
"""
import argparse, json, os
import numpy as np

BAR_DEG = 20.0488      # class/data_structure.cpp:927, rad_threshold 0.35
BAR_MM = 50.0          # class/data_structure.cpp:927, t_threshold 50.0
POT = "D"
N = 29


def read_T(p):
    M = np.eye(4)
    rows = [l.split() for l in open(p) if l.strip()]
    for i in range(len(rows) - 1):        # Trans::Read takes num-1 rows, class/data_structure.cpp:648
        M[i, :] = [float(x) for x in rows[i][:4]]
    return M


def rot_deg(R):
    return float(np.degrees(np.arccos(np.clip((np.trace(R) - 1) / 2, -1, 1))))


def err(Ta, Tb, Ga, Gb):
    Tr = (np.linalg.inv(Ga) @ Gb) @ np.linalg.inv(np.linalg.inv(Ta) @ Tb)
    d = rot_deg(Tr[:3, :3])
    m = float(np.linalg.norm(Tr[:3, 3]))
    return (d < BAR_DEG and m < BAR_MM), d, m


def load_arm(corpus, run_dir):
    gtd = os.path.join(corpus, "Ground Truth")
    G = np.array([[int(x) for x in l.split()]
                  for l in open(os.path.join(gtd, "Pot_%s_simple_graph.txt" % POT)) if l.strip()])
    gt = []
    for i in range(N):
        q = os.path.join(gtd, "Pot_%s_Piece_%d_T.txt" % (POT, i + 1))
        gt.append(read_T(q) if os.path.exists(q) else None)
    res = os.path.join(run_dir, "out", "Result")
    T, on = [None] * N, [False] * N
    for i in range(N):
        q = os.path.join(res, "T_%dto_%d.txt" % (i, i))
        if os.path.exists(q):
            T[i], on[i] = read_T(q), True
    return G, gt, T, on


def summarise(G, gt, T, on):
    Gg = G.copy()
    for i in range(N):
        if not on[i]:
            Gg[i, :] = 0
            Gg[:, i] = 0
    best = [None] * N            # (deg, mm, other, ok) -- smallest angle among the piece's GT edges
    edges = []
    for i in range(N):
        for j in range(i + 1, N):
            if not Gg[i, j]:
                continue
            Ga = gt[i] if gt[i] is not None else np.eye(4)
            Gb = gt[j] if gt[j] is not None else np.eye(4)
            ok, d, m = err(T[i], T[j], Ga, Gb)
            edges.append(dict(i=i + 1, j=j + 1, ok=ok, deg=round(d, 2), mm=round(m, 2)))
            for a, b in ((i, j), (j, i)):
                cur = best[a]
                if cur is None or (d, m) < (cur[0], cur[1]):
                    best[a] = (d, m, b + 1, ok)
    n_on = sum(on)
    seated = [i for i in range(N) if best[i] is not None and best[i][3]]
    joins_ok = sum(1 for e in edges if e["ok"])
    return dict(
        pieces_on=[i + 1 for i in range(N) if on[i]],
        pieces_off=[i + 1 for i in range(N) if not on[i]],
        sherds_seated=len(seated), sherds_denom=n_on,
        joins_ok=joins_ok, joins_denom=len(edges),
        per_piece={i + 1: (None if best[i] is None else
                           dict(deg=round(best[i][0], 2), mm=round(best[i][1], 2),
                                best_edge_with=best[i][2], seated=bool(best[i][3])))
                   for i in range(N)},
        not_seated=[i + 1 for i in range(N) if on[i] and (best[i] is None or not best[i][3])],
        edges=edges,
    )


def counts(txt):
    """The assembler's own printed counts, out of out/summary.txt."""
    import re as _re
    def g(pat):
        m = _re.search(pat, txt)
        return int(m.group(1)) if m else None
    return dict(hyp=g(r"Total number\s*:\s*(\d+)"),
                pruned=g(r"Total number pruned\s*:\s*(\d+)"))


def provenance(run_dir):
    p = os.path.join(run_dir, "out", "swap_provenance.json")
    return json.load(open(p)) if os.path.exists(p) else None


def markdown(out, arms):
    """The three tables the ticket quotes, generated from the runs so nothing is transcribed by hand."""
    import re as _re
    labels = [l for l, _ in arms]
    print("### Pot-level counts, all ten runs\n")
    print("| run | role | hypotheses | pruned | sherds seated | joins seated | pieces off | pieces not seated |")
    print("|---|---|---|---|---|---|---|---|")
    for l in labels:
        s = out[l]
        c = counts(s["summary_txt"])
        role = "swap" if l.endswith("-swap") else ("ctrl" if l.endswith("-ctrl") else "?")
        print("| `%s` | %s | %s | %s | %d/%d (%.4f%%) | %d/%d (%.3f%%) | %s | %s |" % (
            l, role, c["hyp"], c["pruned"], s["sherds_seated"], s["sherds_denom"],
            100.0 * s["sherds_seated"] / max(1, s["sherds_denom"]),
            s["joins_ok"], s["joins_denom"], 100.0 * s["joins_ok"] / max(1, s["joins_denom"]),
            ",".join(str(p) for p in s["pieces_off"]) or "none",
            ",".join(str(p) for p in s["not_seated"]) or "none"))

    def short(l):
        m = _re.search(r"(\d+)-(ctrl|swap)$", l)
        return "%s%s" % (m.group(1), "c" if m.group(2) == "ctrl" else "s") if m else l

    print("\n### Every staged piece, best incident ground-truth edge (deg / mm), all runs\n")
    print("Cell = the piece's best incident edge against its reference transform; * = within the bar"
          " (seated). 'off' = the assembler dropped the piece before assignment. Rows are the whole"
          " shard, not only the five targets, because the screen is global.\n")
    print("| piece | " + " | ".join(short(l) for l in labels) + " |")
    print("|---" * (len(labels) + 1) + "|")
    for p in range(1, N + 1):
        cells = []
        for l in labels:
            if p not in out[l]["pieces_on"]:
                cells.append("off")
                continue
            pp = out[l]["per_piece"].get(p)
            cells.append("-" if pp is None else "%.2f / %.1f%s" % (pp["deg"], pp["mm"],
                                                                   "*" if pp["seated"] else ""))
        print("| %d | %s |" % (p, " | ".join(cells)))

    pairs = {}
    for l in labels:
        m = _re.search(r"(d\d+)-(ctrl|swap)$", l)
        if m:
            pairs.setdefault(m.group(1), {})[m.group(2)] = l
    print("\n### Per piece: every incident ground-truth edge, ctrl against swap\n")
    print("Bar: %.2f deg / %.1f mm (class/data_structure.cpp:927, isSimilarTrans :661-680; seated when"
          " at least one incident edge passes, :967-983).\n" % (BAR_DEG, BAR_MM))
    for key in sorted(pairs, key=lambda k: int(k[1:])):
        p = int(key[1:])
        cl, sl = pairs[key].get("ctrl"), pairs[key].get("swap")
        es = {}
        for l in (cl, sl):
            if not l:
                continue
            for e in out[l]["edges"]:
                if e["i"] == p or e["j"] == p:
                    es.setdefault("%02d-%02d" % (e["i"], e["j"]), {})[l] = e
        print("**piece %d**\n" % p)
        print("| edge | ctrl deg | ctrl mm | swap deg | swap mm |")
        print("|---|---|---|---|---|")
        for k in sorted(es, key=lambda k: min(es[k][l]["deg"] for l in es[k])):
            ec, esw = es[k].get(cl), es[k].get(sl)
            print("| %s | %s | %s | %s | %s |" % (
                k,
                "%.2f" % ec["deg"] if ec else "-", "%.2f" % ec["mm"] if ec else "-",
                "%.2f" % esw["deg"] if esw else "-", "%.2f" % esw["mm"] if esw else "-"))
        print()
        print("| piece %d | best edge | best deg | best mm | seated |" % p)
        print("|---|---|---|---|---|")
        for l, nm in ((cl, "ctrl"), (sl, "swap")):
            if not l:
                continue
            pp = out[l]["per_piece"].get(p)
            if pp is None:
                print("| %d | %s | - | - | piece off |" % (p, nm))
            else:
                print("| %d | %d-%d | %.2f | %.2f | %s |" % (
                    p, p, pp["best_edge_with"], pp["deg"], pp["mm"],
                    "SEATED" if pp["seated"] else "failed"))
        print()

    print("\n### Swap landed: what the staged file says when read back\n")
    print("| run | piece | corpus md5 | staged md5 | real file | staged vs planted (deg) | R_GT.d_staged vs a_world (deg) | moved from corpus (deg) |")
    print("|---|---|---|---|---|---|---|---|")
    for l in labels:
        pv = provenance(dict(arms)[l])
        if not pv:
            continue
        sw = pv["swaps"]
        print("| `%s` | %d | `%s` | `%s` | %s | %s | %s | %s |" % (
            l, pv["piece"], pv["corpus_axis_md5"], pv["staged_axis_md5"],
            "yes" if pv["staged_is_real_file"] else "NO",
            ", ".join("%.2e" % s["angle_staged_vs_planted_deg"] for s in sw),
            ", ".join("%.2e" % s["angle_staged_in_world_vs_a_world_deg"] for s in sw),
            ", ".join("%.2f" % s["angle_staged_vs_corpus_deg"] for s in sw)))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--corpus", required=True)
    ap.add_argument("--arm", action="append", default=[], help="label=<run dir>")
    ap.add_argument("--json", default=None)
    ap.add_argument("--pieces", nargs="*", type=int, default=[18, 25, 26, 28, 29])
    ap.add_argument("--markdown", action="store_true",
                    help="emit the three ticket tables instead of the verbose blocks")
    a = ap.parse_args()

    arms = []
    for spec in a.arm:
        label, _, run_dir = spec.partition("=")
        arms.append((label, run_dir))
    out = {}
    for label, run_dir in arms:
        G, gt, T, on = load_arm(a.corpus, run_dir)
        s = summarise(G, gt, T, on)
        s["run_dir"] = run_dir
        s["summary_txt"] = open(os.path.join(run_dir, "out", "summary.txt")).read().strip() \
            if os.path.exists(os.path.join(run_dir, "out", "summary.txt")) else ""
        out[label] = s
        print("== %-22s sherds %2d/%2d   joins %2d/%2d (%6.4f / %6.3f%%)   off: %s"
              % (label, s["sherds_seated"], s["sherds_denom"], s["joins_ok"], s["joins_denom"],
                 100.0 * s["sherds_seated"] / max(1, s["sherds_denom"]),
                 100.0 * s["joins_ok"] / max(1, s["joins_denom"]),
                 ",".join(str(p) for p in s["pieces_off"]) or "none"))
        print("   not seated: %s" % (",".join(str(p) for p in s["not_seated"]) or "none"))

    if a.markdown:
        markdown(out, arms)
        if a.json:
            json.dump(out, open(a.json, "w"), indent=1)
        return

    print("\n-- per piece, EVERY incident ground-truth edge (bar %.2f deg / %.1f mm). A piece is seated"
          "\n   when at least one of its edges passes (class/data_structure.cpp:967-983)." % (BAR_DEG, BAR_MM))
    labels = [l for l, _ in arms]
    watch = sorted(set(a.pieces) | set().union(*[set(out[l]["not_seated"]) for l in labels]))
    fate_changed = []
    for p in watch:
        print("\npiece %d" % p)
        es = {}
        for l in labels:
            for e in out[l]["edges"]:
                if e["i"] == p or e["j"] == p:
                    es.setdefault("%02d-%02d" % (e["i"], e["j"]), {})[l] = e
        for key in sorted(es, key=lambda k: min(es[k][l]["deg"] for l in es[k])):
            row = "   edge %s :" % key
            for l in labels:
                e = es[key].get(l)
                row += "  %-8s %8.2f deg %9.2f mm" % (l, e["deg"], e["mm"]) if e else "  %-8s %-26s" % (l, "absent")
            row += "   %s" % ("PASS" if all(es[key][l]["ok"] for l in es[key]) else "fail")
            print(row)
        row = "   best deg/mm:"
        seated = []
        for l in labels:
            pp = out[l]["per_piece"].get(p)
            if pp is None:
                row += "  %-8s %-26s" % (l, "absent (piece off)")
                seated.append(None)
            else:
                row += "  %-8s %7.2f /%8.2f %s" % (l, pp["deg"], pp["mm"], "SEAT" if pp["seated"] else "fail")
                seated.append(pp["seated"])
        print(row)
        if len(set(seated)) > 1:
            fate_changed.append(p)
    print("\npieces whose seated/failed state differs between these arms: %s"
          % (",".join(str(p) for p in fate_changed) or "none"))

    if a.json:
        json.dump(out, open(a.json, "w"), indent=1)
        print("json -> %s" % a.json)


if __name__ == "__main__":
    main()
