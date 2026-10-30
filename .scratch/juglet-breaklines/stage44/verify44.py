#!/usr/bin/env python3
"""verify44.py <run-out-dir>  -- acceptance report for ticket 44 (curvature-derived angle).

Reads the TSVs run_cell44.sh writes into <out>/cells-pipeline/ plus thetas_committed.tsv
and prints the ticket's acceptance checklist as PASS/FAIL/VOID lines with the numbers.
Stdlib only; verdicts are the lead's to write, this just lines up the evidence.
"""
import sys, os, csv

OUT = sys.argv[1]
PC = os.path.join(OUT, "cells-pipeline")
def tsv(name):
    with open(os.path.join(PC, name), newline="") as f:
        return list(csv.DictReader(f, delimiter="\t"))

cells = tsv("pipeline_cells.tsv")
proof = tsv("theta_proof.tsv")
defs = tsv("defaults_proof.tsv")
try:
    pairs = tsv("surface_pairs.tsv")
except FileNotFoundError:
    pairs = []
thetas = {}
with open(os.path.join(OUT, "thetas_committed.tsv"), newline="") as f:
    for row in csv.DictReader(f, delimiter="\t"):
        thetas[(row["pot"], row["piece"])] = float(row["theta_formula_deg"])

T42 = {  # med_along / med_across at ladder theta 10.2, run of record 33989453 (t43 part C)
    "Juglet_Piece_1": (1.82, 0.53), "Juglet_Piece_2": (1.88, 0.67), "Juglet_Piece_3": (1.77, 0.51),
    "Juglet_Piece_4": (2.14, 0.45), "Juglet_Piece_5": (2.46, 0.42), "Juglet_Piece_6": (2.28, 0.48),
    "Juglet_Piece_7": (2.52, 0.52), "Juglet_Piece_8": (1.86, 0.38), "Juglet_Piece_9": (0.79, 2.42),
}
ok = lambda b: "PASS" if b else "FAIL"

# 1. cell census: 17 pieces x arms A,B
bykey = {}
for c in cells:
    bykey.setdefault((c["pot"], c["piece"]), {})[c["arm"]] = c
want = [("Juglet", "Juglet_Piece_%d" % i) for i in range(1, 10)] + \
       [("Pot_A", "Pot_A_Piece_%02d" % i) for i in range(1, 9)]
missing = [k for k in want if set(bykey.get(k, {})) != {"A", "B"}]
print("[1] 34 cells (17 pieces x A/B): %s (%d pieces seen, missing/short: %s)" %
      (ok(len(cells) == 34 and not missing), len(bykey), missing or "none"))

# 2. theta proof: every arm-B cell match=yes AND requested == committed formula theta
bad = []
for p in proof:
    if p["arm"] != "B":
        continue
    req = float(p["requested_theta"]); com = thetas.get((p["pot"], p["piece"]))
    if p["match"] != "yes" or com is None or abs(req - com) > 5e-4:
        bad.append((p["pot"], p["piece"], p["requested_theta"], p["paper_grow_theta"], p["match"], com))
print("[2] theta_proof match=yes on all 17 arm-B cells, requested==committed: %s (%s)" %
      (ok(not bad), bad or "all yes"))

# 3. defaults proof: 4 rows, md5 same (DIFF = measured spread per ticket 291, not a hard fail)
sames = [d for d in defs if d.get("same") == "same"]
print("[3] defaults proof armN md5==armA: %d/%d same%s" %
      (len(sames), len(defs), "" if len(sames) == len(defs) else "  DIFF: " +
       ", ".join(d["piece"] for d in defs if d.get("same") != "same")))

# 4. Pot A arm B vs arm A: same status_outcome and two non-empty surfaces, 8/8 (void bar)
pa_ok, pa_rows = 0, []
for pot, piece in want:
    if pot != "Pot_A":
        continue
    a, b = bykey[(pot, piece)]["A"], bykey[(pot, piece)]["B"]
    good = (b["status_outcome"] == a["status_outcome"] == "two"
            and int(b["surf0_points"] or 0) > 0 and int(b["surf1_points"] or 0) > 0)
    pa_ok += good
    pa_rows.append("  %s B: outcome=%s s0=%s s1=%s (A: %s/%s/%s) %s" %
                   (piece.replace("Pot_A_Piece_", "PA"), b["status_outcome"], b["surf0_points"],
                    b["surf1_points"], a["status_outcome"], a["surf0_points"], a["surf1_points"],
                    "ok" if good else "<-- CHECK"))
print("[4] Pot A arm B two clean surfaces 8/8 (void bar): %s (%d/8)" % (ok(pa_ok == 8), pa_ok))
print("\n".join(pa_rows))

# 5. Juglet arm B: outcome + med_along/med_across vs the t42 ladder reference (theta 10.2)
print("[5] Juglet arm B, per-piece (formula theta each) vs t42 10.2 reference along/across mm:")
for pot, piece in want:
    if pot != "Juglet":
        continue
    b = bykey[(pot, piece)]["B"]
    pr = next((q for q in pairs if q["pot"] == pot and q["piece"] == piece and q["arm"] == "B"), None)
    ref = T42.get(piece, (float("nan"),) * 2)
    prtxt = ("along=%.2f across=%.2f angle=%.0f coin=%s" %
             (float(pr["med_along"]), float(pr["med_across"]), float(pr["med_angle_deg"]), pr["coin"])) if pr else "no pair"
    print("  %s theta=%-5s outcome=%-9s clusters=%-3s %s   | t42 10.2: %.2f/%.2f" %
          (piece.replace("Juglet_Piece_", "J"), b["theta_env"], b["status_outcome"], b["clusters"], prtxt, ref[0], ref[1]))

print("\nVOID bar: if [4] fails, the formula run is void (positive control broken); if [4] passes,")
print("read [5] against the reference and judge whether the formula carries the wall pairs the ladder found.")
