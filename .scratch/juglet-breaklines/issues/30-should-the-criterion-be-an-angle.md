# 30 — Should the growth's criterion be an angle at all?

**Status:** done — every measurement below was taken in this ticket's own runs; no verdict recorded here (the lead's call).
**Working in:** chat on Thinkbook16 (2026-10-27)
**Branch:** 30-should-the-criterion-be-an-angle, in /c/PR/worktrees/sfs/30
**Answers:** U19
**Blocked by:** none (ticket 29 merged as 8a50992; this ticket edits no C++)
**Blocks:** any change to the growth rule, and the end-to-end run behind it

## Why this exists

Ticket 29 measured the fact this ticket has to act on: the median angle between neighbouring
normals at the growth's own `k = 10` is **1.20° on Pot A 07** and **8.21–15.80°** on four
Juglet clouds, so the shipped `paperTheta = 3.4` accepts **72.4 %** of the pot's neighbour
pairs and **7.9–19.5 %** of the vessel's. A ladder from 2° to 12° leaves no overlap: the pot
sits above the region floor at 3.4° and nowhere else, the vessel's clouds only at 12°, and at
12° the pot has lost five of its eight regions.

That says one constant cannot serve both. It does **not** say what should replace it, and it
does not test the explanation the conservator asked to check first: that the angle a curved
surface carries is set by its **curvature**, so a threshold expressed as an angle is the wrong
kind of quantity for a small round sherd and the right kind for a flat pot wall.

This ticket tests that explanation, then derives a threshold from the cloud and runs the
pipeline once at it with Pot A beside it. It changes no C++: `SFS_PAPER_THETA` already exists
(`mesh_processing_headless.cpp`, read by `growPaper234`), so every theta here is an
environment value on the shipped binary.

## The clouds

The nine distinct clouds ticket 29 used are geometry and were deleted when it closed (its
ticket records 130 files, 15 882 729 B). They are cheap to re-derive, and this ticket
re-derives them **inside its own jobs** rather than borrowing anything:

| cloud | piece | arm | what it is |
|---|---|---|---|
| B | Juglet 2, 3, 5, 7 | defaults | shipped chain, 0.6 mm |
| E | Juglet 2, 3, 5, 7 | `SFS_PAPER_CHAIN=0`, native | PCL region growing, no crush |
| PA | Pot A 07 | defaults | the sample, the reference cloud |

`SFS_DUMP_STAGE=r1_downsampled` (on main since ticket 25) writes exactly the rung-1 cloud the
growth consumes, so the dump harness in `.scratch/juglet-breaklines/stage25/` is reused as-is.
Twelve cells, one job.

## A — does curvature explain the angle the cloud carries?

For each of the nine clouds, measure on the cloud itself (not the mesh — the growth sees the
cloud):

- `s`: median nearest-neighbour spacing, mm.
- `rho`: median local curvature radius, mm. Estimate per point from a quadric fit over its
  `k = 30` nearest neighbours in a local frame, radius = `1 / max(|k1|, |k2|)`, then take the
  median over points. Report the same at `k = 10` as a sensitivity check, plus p25/p50/p75 of
  `rho`.
- `pred_deg`: the angle the hypothesis predicts between neighbouring normals,
  `s / rho` in degrees (a normal turns by about `s / rho` radians over a step `s` on a
  surface of radius `rho`).
- `measured_p50`: the p50 of the neighbour-normal angle distribution at `k = 10`, which ticket
  29 already established (recompute it here rather than quoting it, so the table is one run).

The hypothesis is **supported** when `pred_deg` and `measured_p50` move together across the nine
clouds: report Pearson and Spearman correlation, the ratio `measured_p50 / pred_deg` per cloud,
and the spread of that ratio. It is **refuted** when the ratio varies more than the measured
p50 itself does — i.e. when curvature accounts for less of the variation between clouds than
the noise floor of the estimator.

Record also, for each cloud, the median folded angle between the cloud's own normals and the
**mesh** normal at the nearest surface point (the nine Juglet meshes are watertight, walls
2.09–2.90 mm, and the mm meshes are in `Dataset/Mesh/Juglet/`). That is the honest noise
floor: whatever the curvature term cannot explain should look like this number.

## B — two ways to derive theta from a cloud, and how to tell them apart

Both rules are fitted so that **Pot A 07's own cloud gives back the shipped 3.4°**. That makes
the pot a calibration, not a test — say so wherever the numbers are reported.

- **Rule C (curvature).** `theta = c * pred_deg`, with `c` fitted from Pot A 07. One free
  constant and a physical model, so it **can fail**: if the nine clouds' `measured_p50` is not
  proportional to `pred_deg`, no single `c` fits and the rule is dead. Report `c`, the residual
  per cloud in degrees, and the theta it gives each cloud.
- **Rule Q (quantile transfer).** `theta = the 0.7237 quantile` of that cloud's own
  neighbour-pair angle distribution — 0.7237 being the fraction of Pot A 07's pairs the shipped
  3.4° accepts, so the rule transfers *what the pot's tuning actually did* rather than a
  physical claim. It fits by construction and therefore cannot fail on the pot; its only test
  is part C. Report the theta it gives each cloud.

State plainly which rule the data supports, and what would change that answer.

## C — one pipeline run per vessel at the derived theta

Runs on the shipped binary, `SFS_PAPER_THETA` set per arm, everything else at defaults
(`SFS_SINGLE_CLUSTER` unset, `SFS_WINDOW_MODE` unset, `SFS_SPACING_POLICY` unset):

1. **Pot A at 3.4°** — the reference arm. 8 pieces.
2. **Juglet at Rule C's theta** — 9 pieces.
3. **Juglet at Rule Q's theta** — 9 pieces, only if it differs from Rule C's by more than 1°.

For every arm: surfaces written per piece (two / one / none), point counts, the two-surface
coverage, and the **corrected pair statistic** — for each Surface_1 point take its nearest
Surface_0 point and split the offset into the component **through** that Surface_0 point's own
normal and the component **along** it, plus coincidence at 1 micron. This replaces the
mean-normal dot test, which was withdrawn in ticket 24 because a curved sherd lets two patches
of one shell point nearly opposite ways. A genuine inner/outer pair is **through 2–4 mm**
(the measured wall thickness), **along ≤ 0.5 mm**, **coincidence ≈ 0**.

Also report, per arm, the number of points in no region at all (the multiplicity the growth
leaves), and the `Breakline_0` dot count per piece — a count only, no comparison with the
authors' lines.

## What "the answer" would look like

- If a derived theta gives any Juglet piece a genuine wall pair (the corrected test) while
  Pot A keeps 8 of 8 with bar passes, the derivation is worth carrying into a pipeline change.
- If it gives more regions but still no genuine pair, the growth's criterion is not the whole
  story and the next suspect is the merge (ticket 20 measured the merge fusing one-wall
  patches correctly) or the second pass over unclaimed points.
- If Rule C's fit fails, that is a **result about the material**: the angle these clouds carry
  is not set by their curvature, and the honest conclusion is that a per-cloud distribution
  (Rule Q) is all we can justify.

`not determined` is a legitimate outcome and must be reported as such rather than forced.

## Acceptance criteria

1. The nine clouds re-derived in this ticket's own run directory, with the dump harness's cell
   count and each cloud's point count printed; not borrowed from any earlier run.
2. Table A complete for all nine clouds with `s`, `rho` (k = 30 and k = 10), `pred_deg`,
   `measured_p50`, the ratio, the mesh-normal noise floor, and both correlations.
3. Both rules reported with their theta per cloud; the pot's 3.4° recovered by construction
   stated as such; `c` and the residuals given for Rule C.
4. The pipeline arms run, with each arm's theta in the run name and in `run.json`.
5. The corrected pair statistic reported for every two-surface piece in every arm, with its
   three columns named.
6. Pot A keeps 8 of 8 surfaces; any piece that changes fate is named with its counts.
7. Corpus read-only: `/data/gpfs/projects/punim2657/sfs_main/original_samples/SfS_pp` and the
   canonical checkout unchanged, md5 listing before and after, compared and quoted.
   `/opt/sfs-pristine` is recorded as ABSENT if it is (do not create it).
8. Geometry deleted with a counted record (per-extension file counts and bytes, manifest written
   before the delete); surfaces, tables and logs kept for the lead to re-measure.
9. Index rows appended with `verdict` and `human_note` EMPTY.
10. Ticket updated with the numbers and paths; `Status` moved.

## Evidence to return

1. Job ids and `sacct` states for every submission, including failures, with what failed.
2. Table A as a file path plus the rows pasted.
3. The two rules' theta per cloud, and Rule C's fit statistics.
4. Per arm: `[STATUS]`-style counts of surfaces written per piece.
5. The corrected pair table per arm.
6. Corpus md5 before/after paths and the equality statement.
7. The deletion manifest path and its totals.
8. The pushed branch sha, and anything not done with the command that stopped it.

## Results (2026-10-27)

### What ran — five jobs, all COMPLETED, exit 0:0

| job | run directory | tag | theta (deg) | role | pieces | elapsed |
|---|---|---|---|---|---|---|
| 33868337 | `/data/gpfs/projects/punim2657/SfSpp/runs/20261027-0637_66c84dc_t30-clouds/ | t30-clouds | — | clouds + part A/B | 9 | 00:01:30 |
| 33868514 | `/data/gpfs/projects/punim2657/SfSpp/runs/20261027-0647_5bc82a9_t30-arm1-pa3p4/ | t30-arm1-pa3p4 | 3.4 | reference | 8 (Pot A) | 00:03:19 |
| 33868765 | `/data/gpfs/projects/punim2657/SfSpp/runs/20261027-0655_cc9c6d9_t30-arm2-jc71p56/ | t30-arm2-jc71p56 | 71.56443628069724 | ruleC | 9 (Juglet) | 00:02:11 |
| 33868766 | `/data/gpfs/projects/punim2657/SfSpp/runs/20261027-0655_cc9c6d9_t30-arm3-jq23p29/ | t30-arm3-jq23p29 | 23.28614631218063 | ruleQ | 9 (Juglet) | 00:02:23 |
| 33868808 | `/data/gpfs/projects/punim2657/SfSpp/runs/20261027-0659_cc9c6d9_t30-arm4-control-jug3p4/ | t30-arm4-control-jug3p4 | 3.4 | control | 9 (Juglet) | 00:02:36 |

Five of the six jobs the rules allow. No job was re-run and no failure is hidden: the four defects
found and fixed are recorded below.

The nine clouds are this ticket's own: the dump job printed `[JOB] runid=20261027-0637_66c84dc_t30-clouds
new=66c84dc clouds=9 cpus=8`, `[JOB] cells in list: 9`, `[JOB] cells finished rc=0 rows=9`, and wrote
**45 rung files** — `out/dump/<tag>/<piece>/r1_downsampled.ply` through `r5_write.ply`, five per
cloud, listed in its log under "cloud inventory".

Arm 4 is a fourth arm the ticket did not ask for. Without a Juglet baseline in the **same**
instrument, "no surfaces at 71.56" cannot be told apart from "these clouds never split". The dump
job's theta-3.4 cells are not that baseline: they carry `SFS_DUMP_STAGE` and split on only some
pieces (B 7, E 2, E 5, E 7 two; B 2, B 3, B 5, E 3 none). Arm 4 is the same script, binary and
staging as arms 2 and 3, with only the theta changed to 3.4.

Each arm's theta is in its run name (`t30-arm1-pa3p4`, `t30-arm2-jc71p56`, `t30-arm3-jq23p29`,
`t30-arm4-control-jug3p4`) and exact in its `run.json`: `sfs_paper_theta` and
`parameters.theta_deg` = 3.4 / 71.56443628069724 / 23.28614631218063 / 3.4, with `arm_role` =
`reference` / `ruleC` / `ruleQ` / `control`.

### Part A — Table A, nine clouds re-derived in this ticket's own run

``/data/gpfs/projects/punim2657/SfSpp/runs/20261027-0637_66c84dc_t30-clouds/out/tableA30.tsv` (25 columns; `out/tableA30_v2.tsv` corrects two of them, see the
defects). `s` is the median nearest-neighbour spacing (mm), `rho` the median local curvature radius
(k = 30, radius `1/max(|k1|,|k2|)`), `pred` = degrees(s/rho), `measured` = p50 of the k = 10
neighbour-normal angle, `floor` = median folded angle against the nearest **mesh** vertex normal,
`share` = fraction of pairs at or under 3.4 deg.

| cloud | n | s | rho (p25 / p75) | rho k=10 | pred | measured p50 | ratio | thetaQ | floor | p10 / p90 | share<=3.4 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| PA/Pot_A_Piece_07 | 8598 | 0.223418 | 21.452780 (2.485642 / 43.377542) | 19.370301 | 0.596701 | 1.198365 | 2.008318 | 3.399955 | 0.712306 | 0.235734 / 21.814020 | 0.723715 |
| B/Juglet_Piece_2 | 1031 | 0.389812 | 1.248285 (0.827136 / 2.570899) | 1.160996 | 17.892240 | 15.802038 | 0.883178 | 30.733660 | 8.100939 | 3.202786 / 50.565024 | 0.107856 |
| B/Juglet_Piece_3 | 1467 | 0.425786 | 1.349624 (0.833020 / 2.527277) | 1.678991 | 18.075954 | 13.460271 | 0.744651 | 27.251288 | 6.106824 | 2.593836 / 50.178081 | 0.149830 |
| B/Juglet_Piece_5 | 3021 | 0.436314 | 3.459150 (1.211553 / 8.238610) | 2.762920 | 7.226912 | 9.302990 | 1.287271 | 19.321004 | 4.002523 | 2.180860 / 41.226816 | 0.191592 |
| B/Juglet_Piece_7 | 4254 | 0.441125 | 5.128811 (1.807651 / 10.528977) | 3.438998 | 4.927965 | 8.211739 | 1.666355 | 15.788703 | 3.392114 | 2.129827 / 35.541745 | 0.195299 |
| E/Juglet_Piece_2 | 2565 | 0.210898 | 0.783016 (0.485119 / 2.087189) | 0.599743 | 15.432076 | 14.856244 | 0.962686 | 23.776141 | 5.154915 | 4.057675 / 37.625805 | 0.078947 |
| E/Juglet_Piece_3 | 3486 | 0.214884 | 0.823793 (0.502600 / 2.008554) | 0.635207 | 14.945453 | 14.314728 | 0.957798 | 23.567504 | 4.897050 | 3.443481 / 37.158597 | 0.098135 |
| E/Juglet_Piece_5 | 6208 | 0.238527 | 1.593183 (0.520063 / 4.176559) | 1.247782 | 8.578169 | 10.918432 | 1.272816 | 18.750072 | 3.640240 | 2.654907 / 32.819794 | 0.140255 |
| E/Juglet_Piece_7 | 8421 | 0.257988 | 2.045253 (0.710577 / 6.510015) | 1.491426 | 7.227298 | 8.728907 | 1.207769 | 15.369696 | 4.215472 | 2.196152 / 27.928748 | 0.185465 |

- `pred` against `measured_p50`: **Pearson 0.9407731599321881, Spearman 0.8833333333333333**.
- The refutation test the ticket names is whether the ratio varies more than `measured_p50` itself:
  **cv(ratio) = 0.3304110977815581 against cv(measured_p50) = 0.42395841071178875** — the ratio
  varies **less**. `pred` spans ~30x (0.596701 to 18.075954 deg), `measured_p50` ~13x (1.198365 to
  15.802038).
- Noise floor: **0.712306 deg on the pot and 3.392114–8.100939 deg on the eight Juglet clouds**, i.e.
  above 3.4 deg on seven of the eight (B 7's 3.392114 is the one just under). The mesh normal is the
  reference, so this is the smallest angle the cloud/mesh pair can report as agreement.
- `rho_k30_share_at_cap` = 0, `zero_normals` = 0 and `angles_nan` = 0 on every row; `n_pairs` = 10n.
- `rho` is heavy-tailed (p75/p25 3.03–17.45), so the k = 10 column is quoted beside it: swapping
  k = 30 for k = 10 moves `pred` on the pot from 0.596701 to 0.661 deg and on the eight Juglet clouds
  by −3.55 to +4.72 deg — B 3 falls 18.076 → 14.530 while the other seven rise (E 2 15.432 →
  20.148). The size of `pred` is k-sensitive, and not in one direction.
- `r1_eq_r2` (the dump stage leaves the cloud identical to the pre-merge stage) holds on 7 of 9 and is
  **false on B/Juglet_Piece_5 and E/Juglet_Piece_5**. The measurements read the premerge file.
- Five clouds (PA and the four B) ran the pipeline's default chain; the four E clouds ran with the
  paper chain off (`SFS_PAPER_CHAIN=0`, `SFS_DOWNSAMPLE_TARGET=-1`), i.e. as released. The `tag`
  column carries the scheme (`defaults` / `chain0-raw`), so the two are separable in the table.
- `mesh_verts_used` / `mesh_faces` (v2 column): PA 10593 / 21174, B2=E2 2565 / 5126, B3=E3 3493 /
  6982, B5=E5 6211 / 12418, B7=E7 8421 / 16838 — the raw Juglet clouds carry about one point per
  mesh vertex.

### Part B — the two rules

Both are **calibrated on the pot**, so the pot is calibration and not test wherever their numbers
appear.

**Rule C** — theta = c * pred, with c fitted so Pot A 07 returns the shipped 3.4 deg:
**c = 5.697997971284436** (= 3.4 / 0.596701; the pot's own measured/pred of 2.008 is what the
constant absorbs, so the residual on the pot is negative by construction).

| cloud | pred | theta_C | residual (measured_p50 − theta_C) |
|---|---|---|---|
| PA/Pot_A_Piece_07 | 0.596701 | 3.4 (by construction) | −2.201635 |
| B/Juglet_Piece_2 | 17.892240 | 101.949945 | −86.147907 |
| B/Juglet_Piece_3 | 18.075954 | 102.996747 | −89.536476 |
| B/Juglet_Piece_5 | 7.226912 | 41.178927 | −31.875937 |
| B/Juglet_Piece_7 | 4.927965 | 28.079532 | −19.867793 |
| E/Juglet_Piece_2 | 15.432076 | 87.931937 | −73.075692 |
| E/Juglet_Piece_3 | 14.945453 | 85.159161 | −70.844433 |
| E/Juglet_Piece_5 | 8.578169 | 48.878391 | −37.959959 |
| E/Juglet_Piece_7 | 7.227298 | 41.181132 | −32.452225 |

**Rule Q** — theta = the 0.7237 quantile of the cloud's own k = 10 neighbour-pair angle distribution
(0.7237 is the fraction of Pot A 07's pairs that 3.4 deg accepts). PA 3.399955 — the calibration
check, reproducing the shipped 3.4 to 4.5e-5 deg — then B 30.733660 / 27.251288 / 19.321004 /
15.788703 and E 23.776141 / 23.567504 / 18.750072 / 15.369696.

The two arm thetas, and why three vessel arms: the median over the four B clouds is
**71.56443628069724** for Rule C and **23.28614631218063** for Rule Q — a gap of
**48.2782899685166 deg**, far past the 1 deg threshold, so the third arm runs. (E-cloud medians,
quoted for completeness: 67.01877610568621 and 21.158788063057727.) `out/thetas30.json`.

### Part C — the four arms

Per piece: surfaces written (`[STATUS-23]` outcome), the two surface point counts, points in no
region, clusters, and the `Breakline_0` dot count. Tables: `out/arms/armcells30.tsv` (arm 1:
`armcells30_v2.tsv`), `out/arms/measure30.tsv` (arms 2–4), `out/arms/measure30_v2.tsv` (arm 1).

**Arm 1 — Pot A at 3.4 (reference), 8 pieces, 8 of 8 written as two surfaces:**

| piece | outcome | n0 | n1 | npts | no region | clusters | Breakline_0 |
|---|---|---|---|---|---|---|---|
| Pot_A_Piece_01 | two | 66763 | 57284 | 85136 | 13780 | 11 | 203 pts / 5 segs |
| Pot_A_Piece_02 | two | 42203 | 46334 | 49528 | 5174 | 3 | 162 / 3 |
| Pot_A_Piece_03 | two | 39773 | 43573 | 46784 | 5145 | 4 | 152 / 4 |
| Pot_A_Piece_04 | two | 32687 | 35790 | 38901 | 4537 | 5 | 147 / 3 |
| Pot_A_Piece_05 | two | 31575 | 34138 | 38074 | 5075 | 5 | 144 / 4 |
| Pot_A_Piece_06 | two | 22572 | 24918 | 27944 | 4693 | 6 | 146 / 2 |
| Pot_A_Piece_07 | two | 6066 | 6437 | 8598 | 1874 | 7 | 63 / 3 |
| Pot_A_Piece_08 | two | 5528 | 6097 | 7682 | 1690 | 4 | 57 / 3 |

**Arm 2 — Juglet at Rule C's 71.56443628069724, 9 pieces: 0 of 9 wrote a surface.** Every piece
`outcome=none`, one cluster, `n0=n1=0`, points in no region −1 (no unclustered file is written when
the piece ends in one cluster), `Breakline_0` 0. `[MEASURE30] cells=9 with_pair=0 ok=0`.

**Arm 3 — Juglet at Rule Q's 23.28614631218063, 9 pieces: 0 of 9.** Identical shape to arm 2,
`[MEASURE30] with_pair=0`.

**Arm 4 — Juglet at 3.4 in the same instrument, 9 pieces: 4 of 9 wrote two surfaces, 5 of 9 none.**

| piece | outcome | n0 | n1 | npts | no region | clusters | Breakline_0 |
|---|---|---|---|---|---|---|---|
| Juglet_Piece_1 | two | 3580 | 12092 | 14546 | 7829 | 18 | 57 pts / 2 segs |
| Juglet_Piece_4 | two | 182 | 732 | 1530 | 1237 | 2 | 15 / 3 |
| Juglet_Piece_6 | two | 608 | 1016 | 2351 | 1773 | 2 | 31 / 2 |
| Juglet_Piece_7 | two | 1012 | 829 | 4254 | 3455 | 4 | 34 / 2 |
| Juglet_Piece_2 | none | 0 | 0 | 1031 | 1031 | 0 | — |
| Juglet_Piece_3 | none | 0 | 0 | 1467 | — | 1 | — |
| Juglet_Piece_5 | none | 0 | 0 | 3021 | — | 1 | — |
| Juglet_Piece_8 | none | 0 | 0 | 1988 | — | 1 | — |
| Juglet_Piece_9 | none | 0 | 0 | 787 | 787 | 0 | — |

So the pieces that change fate between 3.4 and either rule theta are **1, 4, 6 and 7** (two surfaces
at 3.4, none at 71.56, none at 23.29); **2, 3, 5, 8 and 9** write nothing at any of the three.

The mechanism is in the logs and is not a threshold effect: `[PAPER-234] pass 1 done: 1 clusters`,
then `[SINGLE-23] ... mode=off cluster=1 clusterPoints=3020 wrote=none surface0=none`, then
`[STATUS-23] ... reason=no temp surface; final clusters=1`. With `SFS_SINGLE_CLUSTER` unset — which
the ticket requires — a cloud that resolves to one cluster writes **no** surface at all, so such a
cell has neither a surface nor an unclustered file.

### Corrected pair statistic

Nearest `Surface_0` point for each `Surface_1` point; the offset is split into its component **INTO**
that point's normal (`along`) and **ALONG** it (`across`), plus the share of pairs coincident within
1 micron. A genuine pair is through 2–4 mm, across <= 0.5 mm, coincidence ~0. Columns as named in the
file: `med_nn_mm med_along_mm p90_along_mm max_along_mm med_across_mm p90_across_mm max_across_mm
coincidence_share_1um`.

**Arm 1 (Pot A, 3.4) — 8 of 8 pairs ok, `count_match=yes` on all 8:**

| piece | n0 / n1 | through (med / p90 / max) | across (med / p90 / max) | coincidence |
|---|---|---|---|---|
| 01 | 66763 / 57284 | 7.088806 / 9.943167 / 12.954713 | 0.270913 / 0.543714 / 4.665201 | 0.000000 |
| 02 | 42203 / 46334 | 3.631598 / 4.458488 / 6.353303 | 0.251306 / 0.447429 / 3.722243 | 0.000000 |
| 03 | 39773 / 43573 | 3.671327 / 4.409236 / 5.567134 | 0.244369 / 0.423660 / 3.629513 | 0.000000 |
| 04 | 32687 / 35790 | 3.656668 / 4.146562 / 5.053718 | 0.237421 / 0.414635 / 3.006544 | 0.000000 |
| 05 | 31575 / 34138 | 3.766865 / 4.354132 / 5.318628 | 0.250533 / 0.433210 / 3.159894 | 0.000000 |
| 06 | 22572 / 24918 | 3.547159 / 3.745495 / 4.228921 | 0.256260 / 0.722800 / 2.899785 | 0.000000 |
| 07 | 6066 / 6437 | 3.919588 / 4.297276 / 4.596343 | 0.248680 / 0.467674 / 3.556027 | 0.000000 |
| 08 | 5528 / 6097 | 3.603650 / 3.816507 / 4.000407 | 0.250306 / 1.202003 / 2.891494 | 0.000000 |

**Arm 4 (Juglet, 3.4) — 4 pairs ok, 5 `no_pair`, `count_match=yes` on the 4:**

| piece | n0 / n1 | through (med / p90 / max) | across (med / p90 / max) | coincidence |
|---|---|---|---|---|
| 01 | 3580 / 12092 | 0.367769 / 6.067037 / 14.723662 | 4.198927 / 13.665355 / 19.424410 | 0.325174 |
| 04 | 182 / 732 | 2.320256 / 3.528705 / 5.920901 | 3.100769 / 7.548509 / 10.425337 | 0.071038 |
| 06 | 608 / 1016 | 0.593007 / 3.245706 / 5.148966 | 4.536969 / 10.080212 / 12.315292 | 0.240157 |
| 07 | 1012 / 829 | 0.643408 / 4.001059 / 8.127458 | 4.295400 / 10.693149 / 14.039432 | 0.262967 |

Arms 2 and 3 have no pair table at all: no piece wrote a surface, so there is nothing to pair.

### Instruments — four defects found and fixed (no C++ was touched)

1. A stray `$` in `awk '` + `{print $3}` + `'` in both cell scripts (written as a shell brace) left every
   point count at 0 and every `POINTS` field empty in the dump run's tables. Fixed in `5bc82a9`;
   `fixup30.py` rebuilt the counts from the kept PLYs (`out/FIXUPS30.txt`, `out/cells/cells30_v2.tsv`,
   `out/cells/dumpcounts30_v2.tsv`, `out/tableA30_v2.tsv`). The dump cells wrote no surfaces at all
   (`SFS_DUMP_STAGE` stops before clustering), so their `n0`/`n1` legitimately have nothing to recount.
2. `IXTAG` was not in the cell template's `export` list, so every cell ran with an empty tag and wrote
   to `out/arms//Pot_A/...` with blank `tag`/`scheme` columns. Fixed in the template plus a hard refusal
   in `run_arm30.sh` (`exit 9` on an empty tag).
3. The PCD parser read the first `#` line, which is `.PCD v0.7`, not the segment count: `segs` came out
   as `.PCD` and `hpts` as `v0.7`. The real second line is `# <segs> <span> <flag>`; `span` is the last
   index and runs 1–5 above the point count, so it is recorded as its own `span` column. Fixed in
   `run_arm30.sh`.
4. `measure_pair30.py` globbed the dump-cell layout (`root/*/*/*`), so in the arm layout it read
   `surfaces`/`logs` as the piece name: 24 rows, all `no_pair`, meta keys shifted. Fixed to walk for
   `surfaces/` directories, which reads both layouts.

Fixes are in `cc9c6d9`, which adds `fixup_arm30.py`. **Arm 1's tables were repaired, not re-run:** the
script was pushed into the run directory and run there read-only against the kept files; it says so in
`out/arms/FIXUPS-ARM30.txt` (`uname`, `SLURM_JOB_ID`, that it is post-processing of kept files with no
geometry and no pipeline). That is the one place work touched the login node — about a second of
read-only table repair on files the job had already written. Arms 2–4 ran with the fixed instrument and
needed no repair.

### Corpus, deletion and index

- Corpus read-only, both sides listed and compared in every run: `out/inputs_before.md5` /
  `out/inputs_after.md5` (27 rows dump, 24 arm 1, 27 arms 2–4) and `out/corpus_before.txt` /
  `out/corpus_after.txt` (1803 rows). Each run printed `[INPUTS] identical before and after` and
  `[CORPUS] identical before and after`, and `/opt/sfs-pristine` is recorded **ABSENT**, not created.
- Geometry deleted with a counted record written first: `out/arms/geometry_counts.tsv` plus
  `out/GEOMETRY_DELETED.txt`. Arm 1: 97 rows, **520 files, 1 025 007 161 B**. Arm 4: 79 rows, **310
  files, 40 713 937 B**. Surfaces, breaklines, logs and the tables are kept; the run dirs are 404 MB
  (arm 1), 23 MB (arm 4) and 19 MB (dump).
- Index: one row per run appended to `/data/gpfs/projects/punim2657/SfSpp/runs/index.tsv` with
  `verdict` and `human_note` empty — checked with `cat -A`, each row ends `^I^I$`.

### Not done here

No assembly run, no C++ change, no `/opt/sfs-pristine` creation. The deletion above is of staged
copies only; the corpus and the released clouds are untouched.


## Rules for the worker

- Work only in the worktree `C:/PR/worktrees/sfs/30`. Change nothing outside
  `.scratch/juglet-breaklines/stage30/` — **no C++ change is expected**; if one turns out to be
  necessary, stop and report instead of editing.
- Compute nodes only, never the login node and never the laptop (the October laptop-probe breach
  is the reason this is written down). **At most six jobs.**
- Check every submitted script for CRLF before submitting — two grids have died on
  `set: pipefail: invalid option name`.
- Write run directories under `/data/gpfs/projects/punim2657/SfSpp/runs/` using the project's
  convention, and one `index.tsv` row per run with `verdict` and `human_note` left empty.
- **Report evidence, not verdicts.** Whether the hypothesis is supported, which rule wins, and
  what it means are the lead's calls and are not yours to make.
- A failure you keep and report is worth more than a re-run you hide.

## What this cannot settle

- The derivation is calibrated on **one pot** and tested on **one vessel**, nine clouds between
  them. A rule that fits here is a lead about material, not a rate.
- No assembly is run: this measures surfaces, not seating. The per-sherd seating score stays
  where it is until a sherd gives two real faces.
- Region counts and surface counts are not faces. Even a genuine pair is a pair of *written
  surfaces*, and whether Breakline_0 then lies on the real broken edge is ticket 25's
  unmeasured strip question.
- Rule Q cannot fail by construction, so a win for it is weaker evidence than a win for Rule C,
  and the two are reported separately for that reason.
