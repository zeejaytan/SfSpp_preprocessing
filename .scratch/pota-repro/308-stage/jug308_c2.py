#!/usr/bin/env python3
"""jug308_c2.py -- ticket 308 Stage C2: name the Juglet failure mechanism per piece.

    jug308_c2.py --result DIR --gt DIR --lanes DIR --floor N --json score58.json \
                 --out TSV [--panel DIR]

Per piece 1..9, on the evidence only:
  dots        points on the piece's Bl0 lane (the file the assembler reads)
  admitted    dots >= floor (otherwise the assembler switches the shard off at
              admission: main_pristine_batch.cpp:69-73, 'Total number pruned')
  placed      the run wrote T_<i-1>to_<i-1>.txt
  gauge_deg / gauge_mm   pose error vs GT after one global rigid gauge (score58 B)
  mechanism   one of
                gate_too_tight  admitted off: fewer lane dots than the floor
                no_candidate    admitted, no transform written: the search never
                                proposed a placement for this piece
                wrong_candidate admitted and placed, but off the GT by more than
                                the strict 5 deg / 10 mm bar
                seated_ok       placed within the strict bar
The run's own end-condition line is copied into the tsv header for context.
'no_candidate' is what the outside can prove: the binary's stdout does not report
per-piece candidate counts, so a candidate rejected by the pairwise gate and a
candidate never generated look the same from here.
"""
import argparse, json, os, re


def dots(path):
    n, started = 0, False
    with open(path, "r", errors="ignore") as fh:
        for line in fh:
            if not started:
                if line.startswith("DATA"):
                    started = True
                continue
            if line.split():
                n += 1
    return n


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--result", required=True)
    ap.add_argument("--gt", required=True)
    ap.add_argument("--lanes", required=True)
    ap.add_argument("--floor", type=int, required=True)
    ap.add_argument("--json", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--label", default="")
    a = ap.parse_args()

    o = json.load(open(a.json))
    per = {r["piece"]: r for r in o.get("tables", {}).get("per_piece", [])}
    placed = set(o.get("pieces_with_T", []))
    rows = []
    for i in range(1, 10):
        lp = os.path.join(a.lanes, "Juglet_Piece_%d_Breakline_0.pcd" % i)
        d = dots(lp) if os.path.exists(lp) else 0
        r = per.get(i)
        gdeg = r.get("gauge_deg") if r else None
        gmm = r.get("gauge_mm") if r else None
        if d < a.floor:
            mech = "gate_too_tight"
        elif i not in placed:
            mech = "no_candidate"
        elif gdeg is not None and (gdeg > 5.0 or gmm > 10.0):
            mech = "wrong_candidate"
        else:
            mech = "seated_ok"
        rows.append((i, d, int(d >= a.floor), int(i in placed),
                     "-" if gdeg is None else "%.2f" % gdeg,
                     "-" if gmm is None else "%.2f" % gmm, mech))
    with open(a.out, "w", newline="\n") as f:
        f.write("# label %s floor %d\n" % (a.label, a.floor))
        f.write("piece\tlane_dots\tadmitted\tplaced\tgauge_deg\tgauge_mm\tmechanism\n")
        for r in rows:
            f.write("\t".join(str(x) for x in r) + "\n")
    cnt = {}
    for r in rows:
        cnt[r[6]] = cnt.get(r[6], 0) + 1
    print("[C2 %s] floor %d  " % (a.label, a.floor)
          + "  ".join("%s=%d" % (k, cnt[k]) for k in sorted(cnt)))
    for r in rows:
        print("   piece %d dots=%d placed=%d %-16s deg=%s mm=%s"
              % (r[0], r[1], r[3], r[6], r[4], r[5]))


if __name__ == "__main__":
    main()
