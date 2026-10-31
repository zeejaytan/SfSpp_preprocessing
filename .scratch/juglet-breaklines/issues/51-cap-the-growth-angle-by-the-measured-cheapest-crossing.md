# 51 — cap the growth angle by the measured cheapest crossing

## Why

The curvature formula (`theta = k * S/R_fold`, k = 3.3573, ticket 43/45) sets the growth
angle from the WALL's fold radius. But growth fails when theta exceeds the CHEAPEST
smooth bridge between the two wall faces — and that bridge is not always the wall:

- Juglet Piece 1 is a complete 360-degree rim (largest angular gap 0.2 deg). Its binding
  bridge is the intact lip (roll radius ~2.6 mm), tighter than the wall fold (5.93 mm).
  Any k above R_wall/R_lip ~ 2.3 glues at the lip; k = 3.36 overshoots: formula gives
  10.2 deg, the real threshold is 6.5-7.0 deg (threshold sweep 20261031-2145).
- Worn break edges are also smooth bridges cheaper than the formula assumes.

Measured evidence (run 20261031-2007_158ddc6_t50-edge, edge50.tsv): the graph-model
cheapest crossing (Kruskal, k=10 NN, curvature < 1.0, angle where the largest component
first reaches 60% of eligible points) predicted the real pipeline thresholds closely:
J1 7.0 vs real 6.5-7.0; PA08 4.3 vs real 4.0-4.5; Pot A PA01-06 8.1-10.0 vs real 8.1-9.9.

So: measure the crossing on the piece's OWN growth cloud, at runtime, and cap theta.

## Change

In `mesh_processing_headless.cpp`, in the formula path (where medianFoldRadius45 runs,
the `[GROWTH-45]` block near :4745), add a measured cap:

1. Build the k-nearest-neighbour graph on `downsampledCloudWithNormals` (k = 11,
   same KdTreeFLANN already used). For each directed edge, the angle between the two
   point normals, in degrees. Edges eligible only when BOTH curvatures < 1.0
   (same kappa as growth).
2. Kruskal union-find over edges sorted by ascending angle. Track the size of the
   largest component. `thetaCross51` = the edge angle at which the largest component
   first reaches 60% of the points that have at least one eligible edge.
3. Cap: when `SFS_GROWTH_CAP` is set to `1` (default: off — do not change default
   behaviour), `paperTheta = min(paperTheta, 0.9 * thetaCross51)`.
4. Log one line: `[GROWTH-51] crossing=<deg> capped=<0|1> theta=<deg>` right after
   the existing `[GROWTH-45]` line. If fewer than 1000 points have eligible edges,
   log `crossing=none` and do not cap.

Constraints:
- The change is confined to the formula path (env-gated by SFS_GROWTH_FORMULA=1
  AND SFS_GROWTH_CAP=1). Default behaviour byte-identical when either env is unset.
- No new library dependencies. Use the existing Eigen/std containers.
- Complexity: ~1.1M edges, sort + union-find is milliseconds. Do not slow the
  measurable path otherwise.

## Run

One run, 17 pieces (Juglet 1-9, Pot A 01-08), corpus clouds (MANIFEST_JUGLET_CC.tsv
gate as in ticket 48), TWO arms per piece in ONE job:

- arm C (cap): SFS_GROWTH_FORMULA=1, SFS_GROWTH_CAP=1
- arm U (uncapped control): SFS_GROWTH_FORMULA=1 (identical to ticket 48 run)

Per cell record: piece, arm, rc, theta used ([GROWTH-51] line), crossing, outcome
([STATUS-23]), cluster sizes, surface point counts. After the run, score PAIR QUALITY
with `runs/20261031-2046_158ddc6_t50-theta45/paircheck45.py` (med_nn, med_across,
med_angle). Genuine pair bar: med_across < 0.05 mm and med_nn within 30% of the known
wall thickness (Juglet walls 2.0-3.3 mm, Pot A 3.6-8.3 mm).

## Predictions (falsifiable)

- J1 arm C: crossing ~7 deg, theta capped 10.2 -> ~6.3, outcome two, genuine pair.
- J1 arm U: theta 10.2, outcome none (glued) — same as ticket 48.
- Pot A arm C: crossing 8-10 deg > formula 4.4-8.1, capped=0, identical to arm U.
- Juglet J2-J9 arm C: capped where crossing < formula; two faces where ticket 48
  gave none or garbage.

## Acceptance

- [ ] Diff confined to mesh_processing_headless.cpp (formula path) + stage51/** + this ticket.
- [ ] Default behaviour unchanged: SFS_GROWTH_CAP unset -> [GROWTH-45] path identical,
      no [GROWTH-51] line.
- [ ] Run COMPLETED 0:0; 34 cells (17 pieces x 2 arms); corpus gate 9/9 (pcd_md5 AND
      kept_points vs MANIFEST_JUGLET_CC.tsv); corpus.diff/inputs.diff empty.
- [ ] [GROWTH-51] line present in all 17 arm-C cells; crossing values within 1.5 deg of
      edge50.tsv glue60 where that table covers the piece (J1-9, PA01-04).
- [ ] Arm-U cells reproduce ticket 48's theta_computed to 2 dp (same clouds, same code path).
- [ ] Verdict table: per piece, arm C vs U outcome + pair quality, in the ticket write-back.

## Out of scope

- Changing the default growth angle or spacing (ticket 50's lane).
- Touching the merge pass, breaklines, or anything downstream of growth.

Status: ready-for-agent
