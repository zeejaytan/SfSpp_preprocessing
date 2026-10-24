# 293 — The two miss families the corpus re-score exposed

Status: ready-for-agent
Answers: E1
Working in: unassigned (open with `scripts/ticket_start.sh SfSpp_preprocessing .scratch/pota-repro/issues/293-miss-families.md`)
Created: 2026-10-25
Follows: 292 (the baseline: 281/292 sound lanes at bar), 286 (H02/H10 mechanism), 278/279 (base-band partition)

## Why

Ticket 292 measured every lane of the frozen corpus at the shipped defaults. Eleven sound lanes are
below bar and they are not one thing. Eight keep the reference's route and length and differ over one
stretch; three are different contours. This ticket names both families so a later session does not
re-measure them, and answers the one question the numbers cannot: **is the eight-lane family one
mechanism or several?**

## The lanes

Different contours -- three lanes where our line and the reference are both real edges of the
same sherd, taken differently (ticket 294 read this off the pictures and off the authors' own mesh):

| piece | lane | n ours/auth | median mm | cov ours/auth | len ours/auth mm |
|---|---|---|---|---|---|
| Pot_C_Piece_03 | 1 | 337/120 | 11.327 | 18.40 / 50.83 | 607.34 / 273.69 |
| Pot_I_Piece_25 | 0 | 58/69 | 6.910 | 0.00 / 0.00 | 105 / 124 |
| Pot_I_Piece_25 | 1 | 67/60 | 6.951 | 0.00 / 0.00 | 121 / 106 |

`Pot_C_Piece_03` Bl1: ours is the sherd's outer rim, theirs a closed ring on the flat of the same
face about 11 mm inside. `Pot_I_Piece_25`: ours a small closed triangle, theirs a larger loop,
6.9 mm apart in 3D and crossing only in projection.

The picture (`C:/PR/SfSpp_preprocessing/artifacts/pota292/png/Pot_I_Piece_25_Bl0.png`) shows our
closed loop crossing outside a smaller closed reference loop. Both are on the piece; they are not the
same curve.

One-stretch family -- eight lanes (median well under the 2 mm bar, coverage 62-86%):

| piece | lane | median mm | cov ours | len ratio |
|---|---|---|---|---|
| Pot_D_Piece_22 | 0 | 0.757 | 86.40 | 0.92 |
| Pot_D_Piece_27 | 0 | 0.673 | 73.21 | 1.20 |
| Pot_D_Piece_27 | 1 | 0.798 | 62.07 | 1.21 |
| Pot_E_Piece_16 | 0 | 0.676 | 72.97 | 1.01 |
| Pot_H_Piece_02 | 1 | 0.688 | 72.46 | 1.01 |
| Pot_H_Piece_10 | 1 | 0.728 | 72.22 | 1.05 |
| Pot_I_Piece_06 | 1 | 0.883 | 70.22 | 1.01 |
| Pot_I_Piece_13 | 1 | 0.734 | 82.61 | 1.02 |

(`Pot_H_Piece_02` Bl1 and `Pot_H_Piece_10` Bl1 were already diagnosed in ticket 286 -- (S) same
face different contour, and (K) partition mismatch -- so they are members with a known reading, not
open cases.)

## Phase A -- Pot I 25, what are the two curves

Use the instrument of ticket 278/286, on a fresh mesh at theta 3.4 with `SFS_AXIS_FILE` set (quote
the `[PAPER-234] classify` line; ticket 277's trap). Deliver:

1. Per-cluster census for both lanes: points, azimuth bins filled, `l3/l1`, `edge_cv`, axial spread,
   `|n.axis|`, distance to the kept surface.
2. Every author dot and every one of our dots assigned to a surface/cluster; report the share that
   lands on nothing.
3. Per lane a picture `C:/PR/SfSpp_preprocessing/artifacts/pota293/png/p293_I25_Bl<k>.png`
   (3D + X-Y + X-Z + Y-Z + a zoom on the divergence, style as ticket 286).
4. One class per lane: (K) partition mismatch, (S) same face different contour, (W) walk,
   (X) our line is right and the reference wrong -- with the evidence that decides it. A reference
   ruling is the conservator's to make, not the worker's: state the case, do not close it.

## Phase B -- the one-stretch family, one mechanism or several

Same instrument, one table row per lane above: where along the reference the >2 mm stretch sits
(start/end index, arc length, share of the loop), how far it goes (max, mean), and whether at that
stretch **our kept surface spans a feature the reference turns into** (a fold, a notch, a step) or
**our line leaves the surface** (rides an edge the reference does not use). Ticket 286 already showed
both happen (H02 (S) vs H10 (K)); the question is the mix across eight lanes.

Pieces to mesh: Pot_C 03, Pot_D 22, 27, Pot_E 16, Pot_H 02, 10, Pot_I 06, 13, 25 -- nine
pieces, one job (Phase A's three-piece run and Phase B's seven overlap on four).

## Constraints

- Inputs: the frozen corpus only (`/data/gpfs/projects/punim2657/sfs_main/original_samples/SfS_pp/`),
  staged by `scripts/stage_piece.sh` (symlinks; a fresh cloud is refused by design, ticket 291).
- No C++ change, no default change, no threshold retune, no re-run of the corpus.
- The mesh stage is piece-dependently non-deterministic (unseeded `std::random_device`,
  `mesh_processing_headless.cpp:1526-1527`): report each piece's own run-to-run spread if a claim
  rests on a sub-millimetre difference, and land all identity claims on fixed inputs.
- Build with the committed recipe (`git archive` + cmake + sbatch); never `build.sh --target nurbs`
  (ticket 282 -- it compiles the pre-247 duplicate).
- Run directory under `/data/gpfs/projects/punim2657/SfSpp/runs/` with `run.json`, and an index row.
- Geometry dies with the ticket: delete the stage trees and any `.pcd/.xyz/.obj/.ply` output before
  reporting, write `out/GEOMETRY_DELETED.txt`, keep the PNGs, the tables and the scripts.
- Write results into this ticket in the main clone and leave it uncommitted; the lead commits.

## Acceptance

1. A table with every lane above and its class, each cell traceable to a file in the run directory.
2. One answer to "one mechanism or several" for the eight-lane family, with the split by class.
3. Pot I 25's case stated precisely enough for the conservator to rule on the reference.
4. Pictures for at least both Pot I 25 lanes and one member of each class found in Phase B.

## Amendment (lead, 2026-10-25) -- ticket 294 answered most of Phase A and B

The eleven pictures (ticket 294, `artifacts/pota294/png/`) settle the "what", so this ticket is narrowed
to the "why". Do not re-measure the geometry that is already established:

- **Established by 294, do not re-derive**: our line is the boundary of the surface we kept, the
  reference is the boundary of the surface the authors kept, in all eleven lanes. Eight lanes are the
  same face with a different reading of one stretch (18-65 mm; on `Pot_D_Piece_22` Bl0 **the reference
  is the one drawing a chord** -- 18 mm across the notch, mean gap 4.33 mm; on `Pot_H_Piece_10` Bl1 the
  reference steps 4.42 mm inside our face for 39.6 mm). Three lanes are a different partition
  (`Pot_C_Piece_03` Bl1: our outer rim 607 mm vs their inner ring 274 mm; `Pot_I_Piece_25` both lanes:
  our small closed triangle 105 / 121 mm vs their larger loop 124 / 106 mm, 6.9 mm apart in 3D and
  crossing only in projection). Every reference line sits on the authors' own DS mesh (18/18 rows,
  median 0.007-0.024 mm, max 1.386 mm, 0.00% beyond 2 mm).
- **Phase A, what remains**: for `Pot_I_Piece_25` both lanes, name the closed edge each line follows --
  which face, which boundary, and whether a second closed edge exists in the same kept surface. A
  picture exists; what is missing is the cluster/face census behind it (one run, three pieces with
  `Pot_C_Piece_03`, geometry deleted after).
- **Phase B, what remains**: why the walk chose the boundary of the whole face rather than turning where
  the reference turns. The candidates are now specific: (i) the reference is not a boundary at all in
  that stretch (it is a chord over a notch -- D22 Bl0 shows this directly), (ii) the reference follows a
  crease inside the face (H10 Bl1), (iii) our kept region spans a fold the reference turns into (H02 Bl1,
  ticket 286). Decide which of the eight each lane is, from the surfaces, and say which of the three the
  walk could ever know about from the boundary set alone.
- **Still the conservator's, not the worker's**: whether `Pot_C_Piece_03` Bl1 and `Pot_I_Piece_25`'s
  lines should count as references at all. State the case; do not close it.

Everything else in the ticket stands: no code change, frozen corpus by symlink, geometry deleted, run
directory and index row, results written into the ticket for the lead to commit.
