# 286 — H 02 and H 10 hold both a rim and a base: where does the line go wrong?

Status: ready
Answers: none
Working in: none

## Why this ticket

The conservator, 2026-10-24: **"H 02 and H 10 contain both rim and base. Can you tell me what went
wrong with it? Ideally picture show: surface, our edgeline, author edgeline."**

Both pieces look like the Pot C 03 case measured in ticket 279 — a piece carrying a base face as
well as a wall — but ticket 279's complete-disc rule flagged only Pot A 01, Pot C 03 and Pot J 03
across 163 pieces, and on these two it reported:

- Pot H 02: no complete disc (largest candidate c0 17091 points, `|n . axis|` 0.983, only 13 of 36
  angular bins filled, edge_cv 0.424).
- Pot H 10: c0 4484 points fills 36 of 36 bins but edge_cv 0.459 — ragged, so not a disc by the rule.

So the rule's *verdict* excluded them while the conservator's eye says the bases are there. The rule
was only ever a screening device; its thresholds are not evidence about these pieces. What is missing
is the direct comparison: the surface we kept, the line we exported, and the authors' line, on one
picture.

## What is already measured (do not re-derive; cite and use)

Lane scores at the shipped defaults on the frozen theta-3.4 sheets (ticket 280 Phase 0, binary
62ddd28f4476e9cdf5b27cf0ee01c2f0):

| lane | n | med mm | cov ours->author | jumps | author-side cov |
|---|---|---|---|---|---|
| H02 Bl0 | 152 | 0.582 | 100.00 | 0 | - |
| H02 Bl1 | 138 | 0.864 | 73.19 | 0 | 74.45 |
| H10 Bl0 | 98 | 0.661 | 100.00 | 0 | - |
| H10 Bl1 | 92 | 0.641 | 72.83 | 0 | 77.27 |

- Frozen sheets (reuse these, do NOT re-mesh): Pot H 02 Surface_0 md5 9de492c9..., Surface_1
  638a2219...; Pot H 10 Surface_0 07ba2430..., Surface_1 ee79326e... (full md5s in the 280 run's
  run.json).
- Ticket 280 Phase 1: H02 Bl1 has 35 uncovered author dots, all at 0.037-0.485 mm from a surface and
  all nearer Surface_1; H10 Bl1 has 20 uncovered, 19 nearer Surface_1. No detector radius/angle
  setting recovers them (16 settings swept); the max angular gap at those dots is 8.9 / 9.9 deg
  median against the 108 deg boundary threshold, i.e. they sit in smooth interior.
- Ticket 281: on H02 all 35 lie interior to kept cluster 1 and no other cluster comes within rho_d
  1.0 mm of it (nearest 1.3712 mm), so the merge cannot reach it; the rim there is a real 14.13 deg
  fold crossed in 3.23 deg median steps, 52.7% of them at or below the 3.4 deg growth gate. On H10,
  15 of the 19 map to dropped cluster 5 — a 629-point ribbon (21.66 x 3.20 x 1.76 mm at 45.0 deg to
  the axis) standing 0.3191 mm from kept cluster 1.
- Ticket 283: H10's ribbon was refused by the merge's Step 2 on rho_n — `nrm=0.9315` (21.33 deg)
  against 0.9500 (18.19 deg). Curvature passed. Step 3 was never reached, so this is not the Step 3
  defect measured on Pot C 03 / C 01.

## Phase 1 — the pictures (the deliverable the conservator asked for)

One PNG per lane (H02 Bl0, H02 Bl1, H10 Bl0, H10 Bl1), each containing:

1. the two kept surfaces as point clouds, distinguishable (e.g. Surface_0 one colour, Surface_1
   another), thin and small markers;
2. our exported breakline for that lane, thick and bright;
3. the authors' reference breakline for that lane, thick and black;
4. panels: a 3D view plus X-Y, X-Z, Y-Z;
5. a zoom on the failing stretch for the two Bl1 lanes (H02 indices 32-66, H10 40-58), where the
   author's dots have no counterpart within 2 mm.

Pull the PNGs to the laptop under `artifacts/pota286/` so the conservator can open them, and list
every path. Keep each file under ~2 MB.

## Phase 2 — the measurement behind the picture

1. **Which face does the authors' line belong to?** For every author dot on each of the four lanes:
   distance to Surface_0 and to Surface_1, its normal agreement with each, and thus whether their
   line is the boundary of a face (a) we kept as a surface, (b) we kept inside the other surface's
   points but not as a separate surface, or (c) we dropped as a cluster.
2. **Which face does our line belong to**, by the same test.
3. **Base or wall?** For every cluster on each piece (not only the top two), report ticket 279's disc
   numbers as numbers: points, angular bins filled, `l3/l1`, edge_cv, axial spread, `|n . axis|`.
   Say plainly, per piece, whether a base face exists and where it ended up (kept surface / dropped
   cluster / never clustered).
4. **Classification per lane**, using the classes already on record: (K) partition mismatch — their
   line is the boundary of a face we never kept as a surface; (S) same face, different contour —
   extent; (W) same contour, the walk lost it. Give the number that decides it.

## Constraints

- Mesh stage: do not re-run. The sheets are frozen, and the mesh RNG
  (`mesh_processing_headless.cpp:1526-1527`, `std::random_device rd`) makes a re-mesh a different
  surface.
- If the edge stage has to be re-run for an export, build from main HEAD and record the binary md5;
  do not use `build.sh --target nurbs` (ticket 282: it compiles the pre-247 duplicate).
- No code change, no default change, no retuning of any threshold. This ticket produces pictures and
  a classification.
- Copy the ticket and every evidence path into a run directory on Spartan
  (`/data/gpfs/projects/punim2657/SfSpp/runs/<YYYYMMDD-HHmm>_<git7>_<tag>/`) with its `run.json`,
  `submit.sbatch`, `logs/`, `out/`, and add its row to `runs/index.tsv`.

## Acceptance

- Four PNGs exist, each showing surfaces + our line + the authors' line, at a scale where the failing
  stretch is legible; paths reported.
- Per-lane classification (K / S / W) with the deciding number.
- Per piece, a plain statement of what the two surfaces are (which face, is either the base) and where
  the authors' line runs relative to them.
- If the answer is "the bases are only partly surfaced on both", say so and say which step loses
  them — with the numbers that show it.
