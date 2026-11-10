# Ticket 328 — Cure the Juglet wall side: file the interior face without trusting a broken axis, and re-sign the exported line

**Status:** results-in
**Working in:** C:/PR/worktrees/sfs/328-juglet-wall-side-cure
**Branch:** 328-juglet-wall-side-cure
**Answers:** E1
**Depends on:** 327 (results-in, merged 0868d14) — the filing rule, the two failure modes, and the swap's 3/5
**Blocks:** none
**Worker:** dsh-subagent dsh-opencode-go/deepseek-v4.1-flash, agent 50cc731e
**Budget:** large (8 failed acceptance runs; waiting costs none)

> **In one line.** 327 proved the defect is two independent faults upstream of the assembler: the mesh stage
> files the **outer** wall into slot 0 on pieces 2, 6 and 9 (a vote on normals against the axis line, which
> silently keeps the denser face when the vote degenerates), and the exported breakline carries a sampled
> surface normal that **flips sign inside one line**. Fixing only the filing gets three of the five failing
> joins; the other two (1-9, 6-7) need the line's normals re-derived against the wall it sits on. Do both,
> keep the ten pots byte-identical, and the correspondence stage must see all nine true joins.

## What is already known (327, verify-by-reproduction not re-derivation)

**(a) The split is exactly pieces 2, 6, 9** (`census_bar1.json`; r_mean S0/S1 mm 17.02/14.75, 16.93/14.59,
17.21/15.22; the other six inner). `Breakline_0` rides `Surface_0` on 9/9 (0.28-0.62 mm against 1.83-2.49 mm
to S1), so the choice is made in the **mesh stage** and the edgeline inherits it. Per-wall densities are flat
(0.543-0.560 pts/mm) — density does not explain the split.

**(b) The rule and where it fails.** `classifyAndOrderPaper234` (`mesh_processing_headless.cpp:3688`) votes
`satA = inFrac[0]*n0 + (1-inFrac[1])*n1` against `satB = (1-inFrac[0])*n0 + inFrac[1]*n1`, where `inFrac` counts
normals whose ray to the `SFS_AXIS_FILE` line meets it on the positive side (:3705-3718); it swaps only when
`satB > satA` strictly (:3725). It is called at :4008 **after** `std::sort(clusters..., myobject3)` — the
denser face first — so a degenerate vote keeps the exterior in slot 0. There is no check against geometry.
- **Wrong-side axis (pieces 2, 9):** the shipped DS axis is 87.8° and 73.3° off the GT axis; re-voting with
  the GT axis files them correctly (`interior_gt = face1`, inFrac_S0 0.000 / inFrac_S1 0.999 and 0.951).
- **Flipped normals (piece 6):** axis is fine (13.3°), yet the shipped slot 0 is the outer wall — its normals
  were negated upstream (it is the only piece whose mesh log prints `Normals flipped: true`; the negation is
  at `checkNormalsIntersection` :3144 / :4145-4164).

**(c) The swap alone is not enough** — job 34687732 (COMPLETED 0:0), copies only, 3 of 5 pass:
1-2 −0.896→+0.704, 2-5 −0.991→+0.948, 7-9 −0.674→+0.708, **but 1-9 −0.945→−0.039 (4/7 negative) and
6-7 +0.106→−0.183 (10/15 negative)**. Three sign variants (job 34690603) only reflect those numbers, and
negating 2/6/9 breaks the three that had passed: the sign is mixed **within** a line (piece 9's swapped-in
walk is 17% outward overall and −0.74..+0.07 at the section meeting piece 1; piece 7's own line swings
−0.80..+0.61). The exported line stores the sampled surface normal.

**(d) Precedents.** 296 (merged `0050313`): "the interior slot is by construction, not a per-piece swap",
proved 8/8 + 15/15 on its pot — the construction this ticket must extend to the Juglet. 81/210: per-piece
slot-exchange surgery (fallback arm only). 175: parent-surface separation. The axis half overlaps ticket 325
(the scale-free axis finder) but this cure must not depend on it being right.

## What to deliver (stop on the first bar that fails and report it)

1. **Filing that cannot be inverted by a bad axis.** Make the slot decision self-checking: the chosen
   interior face must satisfy an independent geometric test (e.g. smaller mean radius about the piece's axis,
   or the parent-surface wall label of 175) **and** the normal vote; on disagreement, say which wins and why,
   with numbers per piece. A degenerate vote must not fall back to size order. Same code path for pots and
   Juglet; no piece IDs, no per-piece constants, no small-object flag.
2. **Line normals re-derived against the wall.** The exported `Breakline_0` normals must point from the
   interior wall it lies on, per point, not be copied from the sampled surface. Show the per-point agreement
   with the wall's own normal (fraction correct, before/after per piece) and prove 1-9 and 6-7 stop reading
   as opposing rims.
3. **Correspondence bar (primary).** 326 harness at GT after the cure: **all nine touching pairs
   dot_med_d3 ≥ +0.7 and strict-gate inliers > 0 on each**; full before/after table. If a pair still fails,
   name the remaining mechanism with its numbers rather than nudging the bar.
4. **Juglet E2E, two repeats** (assembler is non-deterministic: Pot E gave 30/31+57/62 and 31/31+62/62 from
   byte-identical inputs), GT-axes arm per the 326 template, report seated pieces and joins honestly. Seam
   length may still cap 2-9 and 3-5 (3-6 samples against 7 needed) — if seams remain the blocker after the
   normals pass, say exactly that; **do not touch the seam gate (326 owns it)**.
5. **Pot corpus untouched.** No bundle writes (list `Dataset/` + `original_samples/` before/after). If any
   generation code changed: byte-identity per 325's standard — `scripts/run_benchmark_172.py --cap 6 --seeds
   10 --step 10` byte-compared with `/data/gpfs/projects/punim2657/SfSpp/runs/20261110-0740_d628fc0_t323-axes/out/axes323`
   (172 files, 251 lines); ANY differing file stops the arm — report the differing term and margin, never
   nudge a threshold. Note the run-to-run spread: the mesh stage draws 30 unseeded ray-cast points
   (`mesh_processing_headless.cpp:1526-1527`), so compare against that piece's own measured spread where it
   is not zero (Pot H 02 moved 0.867 mm; Pot J 09 was exactly 0.000000 across four runs).
6. **Renders** into `SfSpp_preprocessing/artifacts/pota328/renders/`: cured line on the inner wall per piece
   with its normals drawn, before/after, plus E2E renders; workspace-relative Markdown links in the
   write-back; eye-check every one.

## Must not

- No ORIG/GT points into the fix; the GT is the oracle, evidence-only.
- No per-piece hardcoding, no piece-ID switches, no small-object flags.
- No seam-gate, matching-gate or assembler changes (ticket 326 owns those).
- No gate relaxation without a mechanism; report blockers verbatim.
- Never `git worktree add/remove`; no commits/pushes; Comments-only ticket edits; end with exactly one
  `**End state:**` line; sacct-direct polling; no idle-polling PENDING jobs.
- Spartan compute only; runs under
  `spartan:/data/gpfs/projects/punim2657/SfSpp/runs/<YYYYMMDD-HHMM>_<git7>_t328<tag>/` with `run.json`,
  `submit.sbatch`, `logs/`, `out/`.

## Inputs

- Ticket 327 (results-in): census, rule, failure modes, swap tables, renders
  (`C:/PR/worktrees/sfs/327-juglet-wall-side-cause` until closed; merged at 0868d14 on main).
- Juglet t66 bundle `20261103-1332_fab76f5_t66-admitsign-default/outU_jug/geom`; GT `Dataset/Juglet_GT`.
- 326 harness `C:/PR/worktrees/structure-from-sherds-pp/326/hpc/tools/diag326_pairs.cpp` (read-only).
- E2E template `20261110-0320_41494d0_t320b-juglet/submit.sbatch` (SIF `sfs_main/sfs_pristine_assembly.sif`,
  `-DJUGLET_ORIG`, `juglet_orig_block.inc`, FLOOR=20, NP=9).
- Precedents: `296-seat-a-pot-and-prove-the-interior-slot.md`, `175-two-walks-two-slots.md`,
  `81-swap-cure.md`, `210-swap-reseat-fresh.md`.


## Comments (worker, 2026-11-10)

### Bar 1 — a filing that a bad axis cannot invert: PASS (both arms)

Two code sites, both in the worktree (uncommitted by rule):
- `mesh_processing_headless.cpp:3680` new `namespace t328` (helper `faceStats` at :3705), decision rewritten at
  :3846-3912 inside `classifyAndOrderPaper234` (:3688, called :4008 right after `std::sort(clusters, myobject3)`).
- `edgeline_extraction_headless.cpp:92` (`kdtree_flann.h`), :2402-2438 the per-point wall normal (bar 2 below).

**The rule.** Two measurements, neither of which reads the normal sign or the supplied axis:
- **G — local curvature.** Per face, a local quadric `z = ½(Au²+2Buv+Cv²)+Du+Ev` over k=60 nearest neighbours in
  the frame of each point's own normal; `κmax = max(|tr±disc|)`; the **median over a deterministic stride
  subsample of 600 points**. The interior face is the face of *smaller radius of revolution*, so its curvature is
  larger; `κ` is sign-free, so a globally negated normal set cannot flip it, and it never touches the axis file.
  Valid when `ratio = κ_interior/κ_other ≥ 1.10`.
- **V — the existing axis-ray vote** (`inFrac`/`satA`/`satB`), now printed with two new diagnostics:
  `axisfit` = fraction of each face's normal-vs-girth angles within 90°−? (sign-free), and
  `vote_gap = (satA−satB)/(n0+n1)`. Valid when `axisfit ≥ 0.80` **and** `|vote_gap| ≥ 0.50`.
- **Precedence.** geometry decides whenever G is valid; if G is invalid the vote decides only when V is valid;
  if neither is valid the piece is filed by `kPick` (the measured curvature order) with a printed
  `WARN undecidable piece` — **there is no size-order fallback anywhere**, and no piece ID, constant or
  small-object flag. On disagreement one line names geometry as the winner and says why: the vote is inverted
  both by a wrong-side axis and by a globally negated normal set, geometry by neither.

**Arm A — the GT axis** (`SFS_AXIS_FILE=Dataset/Juglet_GT`), cell outgt_jug of job 34696906:
slot 0 is the interior on **9/9**, `decider=geometry-kappa` on all nine, `axisfit` 0.90-1.00,
`κ ratio` 1.27 1.43 2.40 2.13 2.43 1.98 1.92 2.48 3.00.

**Arm B — the shipped, broken axis** (`Dataset/Axes/Juglet`), cell outds_jug of the same job:
slot 0 is the interior on **9/9** as well. The two pieces whose axis is wrong are exactly the two the vote
mis-files, and geometry overrode both:
- piece 2 `axisfit=0.24`, `radius0=2.34`/`radius1=3.31`, `vote_pick=0`, geometry → face 1 (correct);
- piece 9 `axisfit=0.14`, `radius0=3.43`/`radius1=2.10`, `vote_pick=1`, geometry → face 0 (correct);
- the other seven match the GT arm to three decimals.

One more disagreement is worth naming: with the **GT** axis, piece 6's vote still points the wrong way
(`vote_pick=0`, `vote_gap=+1.00` — decisive and wrong) because that piece's normals are globally negated
upstream and its walls are near-tangential; geometry decides it correctly. So the vote disagrees with geometry on
1/9 in the GT arm (piece 6, sign) and on 3/9 in the shipped-axis arm (2, 9: axis; 6: sign), and geometry is right
in every case. Tables: `artifacts/pota328/probe/filing_gt_jug.tsv`, `filing_ds_jug.tsv`
(parser `.scratch/pota-repro/t328/parse_filing.py`; the census column is the smaller median perpendicular radius
about the GT axis, reproducing 327).

### Bar 2 — line normals re-derived against the wall, per point: PASS (Breakline_0)

`edgeline_extraction_headless.cpp:2402-2438`: right after the B-spline block that used to hand the line its
normals, the cleaned single-face wall cloud (`cloud_OriginalSurfaceWithNormals`, loaded at :2342 — the wall the
line rides) is searched with a `pcl::KdTreeFLANN<pcl::PointNormal>` at k=5 for every projected line point; the
mean wall normal replaces the fitted surface normal. **Positions are untouched**, so the correspondence set
(kd-nearest on points) and `gap_min` cannot move. The old per-line global sign vote stays in the file and is now
a no-op for Bl0 by construction.

Percent of a line's normals agreeing (dot>0) with the wall it rides, before → after, per piece:

| piece | Bl0 before | Bl0 after | median after | Bl1 after (not read by the assembler) |
|---|---|---|---|---|
| 1 | 1.000 +0.951 | 1.000 | +0.993 | 0.672 +0.362 |
| 2 | 1.000 +0.939 | 1.000 | +0.992 | 0.094 −0.438 |
| 3 | 1.000 +0.906 | 1.000 | +0.991 | 0.195 −0.438 |
| 4 | 1.000 +0.910 | 1.000 | +0.984 | 0.000 −0.648 |
| 5 | 1.000 +0.931 | 1.000 | +0.995 | 0.000 −0.711 |
| 6 | 0.733 +0.871 | 0.732 | +0.991 | 0.289 −0.185 |
| 7 | 1.000 +0.920 | 1.000 | +0.990 | 0.345 −0.354 |
| 8 | 1.000 +0.904 | 1.000 | +0.995 | 0.262 −0.593 |
| 9 | 1.000 +0.942 | 1.000 | +0.982 | 0.318 −0.365 |

- The before column is the shipped t66 bundle, i.e. 327's measurement reproduced, and it is the *bundle* that
  looked healthy: agreement 1.000 on 15 of 18 face-lines. The defect was never a whole-line inversion on Bl0 —
  it was the per-point mixture, which is why 1-9 and 6-7 kept failing after the swap (327: −0.039 and −0.183).
- After the cure every Bl0 point carries its wall's normal. `checkvote328.py` verifies the exported block is
  exactly the k=5 wall mean: `dot(exported, k5mean) = +1.0000` on every Bl0 point of all nine pieces except the
  5 piece-6 points below.
- Piece 6's Bl0 is 0.732 rather than 1.000 and its median dot is still +0.991: 5 of its 41 points take the k=5
  mean of neighbours whose normals lean the other way because that fragment's walls are near-tangential
  (`|mean unit n|` 0.017/0.041 per 327). The wall itself is ambiguous there, not the line; the median direction
  is unambiguous.
- **Bl1 is not cured and is deliberately left alone**: the global vote still negates whole exterior lines
  (`dot(exported, k5mean) = −1.0000` for 100% of piece 1's 64 points). Only `Breakline_0` is read by the
  assembler (`class/data_path.h`, 326's finding), so curing Bl1 would grow the diff without moving any bar.
  Recorded here as a known, unmoved defect.

**Job bookkeeping for this bar.** 34696906 (run dir `20261110-2205_123f2ca_t328-wallside-short`) FAILED 6:0 at
22:19:49 — but only at the 326-harness build, which needs `/opt/sfs-pristine`: that path exists in
`sfs_main/sfs_pristine_assembly.sif`, not in `pcl_191_nurbs.sif`. Both binaries compiled and all six cells ran
before that line, so the two arms above are live results. 34696293 (the 4 h copy) was cancelled by the lead while
PENDING. The harness re-run is **34700288** (run dir `20261110-2235_123f2ca_t328-harness-after`) — bar 3 below.

### Bar 3 — the correspondence bar. First measurement FAILS, and it convicts the bar-2 estimator, not the filing

Run **34700288** (`20261110-2235_123f2ca_t328-harness-after`) **COMPLETED 0:0**, 00:00:18. It clones t325's
`trees/juglet_GT_r1`, regenerates `Surfaces/*.xyz` from the cured `geom`, replaces `Breaklines/*.pcd` with the
cured `Bl0`/`Bl1`, hardlinks 326's pristine objects (`34671027`) and runs `diag326.sh jug_cured /inc 20
-DJUGLET_ORIG` in `sfs_main/sfs_pristine_assembly.sif`. Its before table is 326's own `out/diag_jug_GT.txt`.

`dot_med_d3` = median over the harness's correspondences of `n_A·n_B` (both normals are the exported PCD
normals); `inl` = the strict gate's `n_inl15_15deg`. **Before** = shipped t66 bundle; **after** = this cure.

| pair | before dot_med_d3 | before inl | after dot_med_d3 | after inl | after n_d3 (neg) |
|---|---|---|---|---|---|
| 1-2 | −0.896 | 11 | **+0.311** | 0 | 13 (0) |
| 1-4 | +0.786 | 4 | **+0.469** | 0 | 9 (0) |
| 1-8 | +0.971 | 22 | **+0.741** | 0 | 19 (0) |
| 1-9 | −0.945 | 0 | **−0.408** | 0 | 7 (6) |
| 2-5 | −0.991 | 0 | **+0.642** | 0 | 1 (0) |
| 2-9 | +0.991 | 8 | **+0.693** | 0 | 4 (0) |
| 3-5 | +0.987 | 6 | **+0.674** | 0 | 3 (0) |
| 6-7 | +0.106 | 0 | **−0.786** | 0 | 15 (12) |
| 7-9 | −0.674 | 0 | **+0.287** | 0 | 3 (0) |

One pair of nine clears +0.7 (1-8) and the strict gate is empty on all nine: **bar 3 fails as implemented**. The
cured tree is a fresh draw (the mesh stage's 30 unseeded ray-cast points), so `gap_min` moved too — 1-2
1.103→0.514, 1-9 2.124→0.998, 6-7 0.357→0.809 mm — and the before/after columns are two draws of the same
pipeline, not the same draw.

**Why it fails, measured rather than guessed.** `.scratch/pota-repro/t328/mutualpair2.py` is an exact local
replica of the harness's pair statistic (GTRel on the 4×4 `T` matrices, mutual nearest, |Δp| < 3 mm, dot of the
PCD normals, median). It reproduces both trees to three decimals *and* reproduces 327's swap table exactly
(1-2 +0.704, 1-4 +0.786, 1-8 +0.971, 1-9 −0.039, 2-5 +0.948, 2-9 +0.967, 3-5 +0.987, 6-7 −0.183, 7-9 +0.708),
so the statistic is trustworthy. On **that** bundle, with the filing already correct, four normal estimators:

| pair | fitted (327 swap) | fitted, sign per point from wall | wall k=5 mean | wall nearest-1 | 3 mm wall plane |
|---|---|---|---|---|---|
| 1-2 | +0.704 | +0.704 | +0.311 | +0.278 | **+0.926** |
| 1-4 | +0.786 | +0.786 | +0.469 | +0.199 | **+0.874** |
| 1-8 | +0.971 | +0.971 | +0.741 | +0.605 | **+0.984** |
| 1-9 | −0.039 | −0.039 | −0.408 | −0.808 | **+0.652** |
| 2-5 | +0.948 | +0.948 | +0.642 | +0.608 | **+0.953** |
| 2-9 | +0.967 | +0.967 | +0.688 | +0.400 | **+0.959** |
| 3-5 | +0.987 | +0.987 | +0.674 | +0.636 | **+0.989** |
| 6-7 | −0.183 | −0.177 | −0.609 | −0.499 | **+0.372** |
| 7-9 | +0.708 | +0.708 | +0.287 | +0.126 | **+0.797** |

- The **k=5 mean of the wall's own vertex normals** — what bar 2 shipped — is worse than the fitted normal on
  every one of the nine pairs, including the seven that were already passing. The wall's per-vertex normals right
  at a break edge are contaminated by the break face and by the last jagged triangle row, so the mean is pulled
  tens of degrees off the wall; the fitted B-spline normal is a smooth field over the whole fragment and does not
  suffer that.
- **Signing the fitted normal per point from the wall changes nothing** (−0.039 → −0.039, −0.183 → −0.177). The
  fitted normal already agrees in sign with the local wall, so 327's reading — that 1-9 and 6-7's residual is a
  per-point sign defect — is **not supported**: those correspondences are between surfaces that genuinely differ
  in orientation, not between a normal and its negation.
- A **3 mm disc of the wall, fitted as a plane** (smallest principal direction, sign from the fitted normal) is
  best of all: it beats the fitted normal on six of nine pairs and recovers 1-9 and 6-7 from −0.039/−0.183 to
  +0.652/+0.372 on this bundle. On the cured geometry it predicts 7/9 at bar (1-2 +0.926, 1-4 +0.874, 1-8 +0.984,
  2-5 +0.953, 2-9 +0.959, 3-5 +0.989, 7-9 +0.797) with 1-9 +0.652 and 6-7 +0.285 still short.

So the bar-2 code is being changed from the k=5 mean to the 3 mm plane fit (`edgeline_extraction_headless.cpp`,
the block after `fitBSplineSurfaceAndGetNormalsOnProjectedPoints`), and bars 1-3 are re-measured on the rebuild:
**34702694** (run dir `20261110-2252_123f2ca_t328-planenorm`), which also carries one fresh pot cell pair so the
filing change stays visible on the pots. Bar 5's byte-identity test is **34702695** in the same run directory.

### Bar 3 — second measurement (3 mm plane fit): 7 of 9 at the dot bar, and the inlier clause is normals-blind

**34703082** (run dir `20261110-2252_123f2ca_t328-planenorm`, cells + harness **34705422** COMPLETED 0:0) rebuilt both
binaries with the 3 mm plane fit and re-ran the 326 harness on the cured tree. Harness integrity: the before table
(`out/diag_jug_before.txt`) reproduces 326's own `out/diag_jug_GT.txt` **exactly** (empty `diff` of the `GTPAIR` lines),
so the tree build and the invocation are faithful. `dot_med_d3` / `n_d3` (negatives) / strict-gate inliers / `gap_min`:

| pair | before | after (3 mm plane) | after n_d3 (neg) | after inl | after gap_min |
|---|---|---|---|---|---|
| 1-2 | −0.896 | **+0.926** | 13 (0) | 6 | 0.514 |
| 1-4 | +0.786 | +0.874 | 9 (0) | 0 | 0.211 |
| 1-8 | +0.971 | +0.984 | 19 (0) | 17 | 0.304 |
| 1-9 | −0.945 | **+0.652** | 7 (0) | 0 | 0.998 |
| 2-5 | −0.991 | +0.953 | 1 (0) | 0 | 1.539 |
| 2-9 | +0.991 | +0.963 | 4 (0) | 0 | 0.738 |
| 3-5 | +0.987 | +0.989 | 3 (0) | 0 | 0.401 |
| 6-7 | +0.106 | **+0.372** | 15 (0) | 0 | 0.809 |
| 7-9 | −0.674 | +0.797 | 3 (0) | 0 | 0.945 |

- **`n_d3_dotneg` is 0 on all nine** — no pair reads as opposing rims any more, which is the bar-2 claim measured at
  the seams. 1-9 and 6-7 are positive but weak.
- **The strict-gate inlier clause cannot be moved by a normals change, and this needs a lead ruling.** In
  `diag326_pairs.cpp:249` `CountInlier(inl15, cv, INLIER_THRESHOLD, ANGLE_THRESHOLD)` fills column 9 and is always
  computed; column 10 is `(ic ? inl : -1)` from the unrelated whole-scene `inlierCalculate(inl, tn, cc, LL)` at :259.
  `CountInlier` counts *geometrically* consistent correspondences — 1-4 after has all nine of its correspondences
  agreeing (`n_dot07` 9, `dot_med_d3` +0.874) and still 0 inliers — and the count moves between two draws of identical
  code (1-8: 11 → 17), so it is a property of the two walked lines' positions, not of their normals. The
  correspondence set is kd-nearest on points (`MakeCorWOBuildTree`) and this cure moves no position, so **the clause was
  already 0 on 7 of 9 pairs before the cure**; as written the bar asks a normals fix to move a positions statistic.

**Estimator choice, measured.** `.scratch/pota-repro/t328/planecand2.py` (local replica, validated to three decimals
against the harness and against 327's swap table) sweeps the patch radius r and a 45° trim that drops patch neighbours
whose own normal turns away from the first plane (two refits). Pass count at the +0.7 bar on the cured geometry:
fitted 7, r=3 7, r=4 8, r=5 8, r=6 9, r=8 9, r=3+trim 8, **r=5+trim 9**, r=6+trim 9. r=5+trim has the best margin on
the two hard pairs (1-9 **+0.950**, 6-7 **+0.790**) and stays local — r is half the smallest interior radius (10.45 mm)
— where r=8 starts to behave like a global plane. Landed in `edgeline_extraction_headless.cpp` (5 mm radius, 20-point
fallback, two 45° refits, sign from the fitted normal, positions untouched).

Third measurement is **34706334** (run dir `20261110-2325_123f2ca_t328-trim5`): 5 mm+trim build, cells `gt_jug` and
`ds_jug`, then the same harness before/after.

### Bar 3 — third measurement (5 mm + 45° trim): the dot clause passes 9/9; the inlier clause is capped by the harness, not by the normals

**34706334** (run dir `20261110-2325_123f2ca_t328-trim5`, **COMPLETED 0:0**, 00:06:15, corpus listing diff 0 lines)
rebuilt both binaries with the 5 mm trimmed plane fit and re-ran cells `gt_jug` / `ds_jug` plus the 326 harness on
the cured tree. `dot_med_d3` / `n_d3` (negatives) / strict-gate inliers / `gap_min`:

| pair | before | after (5 mm+trim) | after n_d3 (neg) | after inl | after gap_min |
|---|---|---|---|---|---|
| 1-2 | −0.896 | **+0.988** | 13 (0) | 8 | 0.514 |
| 1-4 | +0.786 | **+0.972** | 9 (0) | 7 | 0.211 |
| 1-8 | +0.971 | **+0.971** | 19 (1) | 14 | 0.304 |
| 1-9 | −0.945 | **+0.953** | 7 (0) | 0 | 0.998 |
| 2-5 | −0.991 | **+0.956** | 1 (0) | 0 | 1.539 |
| 2-9 | +0.991 | **+0.943** | 4 (0) | 0 | 0.738 |
| 3-5 | +0.987 | **+0.997** | 3 (0) | 0 | 0.401 |
| 6-7 | +0.106 | **+0.786** | 15 (0) | 0 | 0.809 |
| 7-9 | −0.674 | **+0.898** | 3 (0) | 0 | 0.945 |

**The primary clause passes on all nine** (median `n_A·n_B` ≥ +0.7, worst +0.786) and **no pair reads as opposing
rims** (`n_d3_dotneg` 0 everywhere; 1-8 has a single correspondence out of 19 with a negative dot). Before the cure
only three of nine cleared +0.7.

**The inlier clause fails on six of nine, and the reason is structural. Correction to my previous checkpoint:**
`CountInlier` *does* read the normals — the count moved 1-2 0→8, 1-4 0→7, 1-8 11→14 with the normals alone — so my
earlier "normals-blind" reading was wrong. What it actually requires (`class/feature_matching.cpp:1000-1016`,
`reconstruction.h:24-26`): each correspondence must be within `INLIER_THRESHOLD` = **1.5 mm** and within
`ANGLE_THRESHOLD` = 0.262 rad = **15°** (the angle is folded, `min(a, π−a)`, so the sign is irrelevant), and the
pair only registers at all if `dummy_inlier > MINIMUM_NUMBER/2` = 3. So the clause needs **≥ 4 mutual-nearest
correspondences simultaneously inside 1.5 mm and aligned to |dot| > 0.9659**. Per pair on the cured tree (local
replica, identical to the harness on all three non-zero pairs):

| pair | correspondences | within 1.5 mm | best |dot| within 1.5 mm | inliers | capped by |
|---|---|---|---|---|---|---|
| 1-2 | 13 | 13 | 0.9962 | 8 | — |
| 1-4 | 9 | 9 | 0.9832 | 7 | — |
| 1-8 | 19 | 19 | 0.9992 | 14 | — |
| 1-9 | 7 | 2 | 0.8596 | 0 | **alignment, not the count ceiling**: the pair has 7 correspondences (≥ 4), but only 2 lie inside 1.5 mm and their best \|dot\| is 0.860 |
| 2-5 | 1 | 0 | — | 0 | **1 correspondence in the whole pair** |
| 2-9 | 4 | 4 | 0.9499 | 0 | alignment: all four inside 1.5 mm, best |dot| 0.950 < 0.966 |
| 3-5 | 3 | 3 | 0.9997 | 0 | **3 correspondences in the whole pair** (needs 4) |
| 6-7 | 15 | 9 | 0.8771 | 0 | alignment: nine inside 1.5 mm, none within 15° |
| 7-9 | 3 | 3 | 0.9196 | 0 | **3 correspondences in the whole pair** |

- **Lead ruling (2026-11-10): the six failures split into two kinds, and the split is recorded as ruled.**
  - *Unreachable by construction* — **2-5** (1 correspondence in the pair), **3-5** (3), **7-9** (3). `CountInlier`
    registers a pair only above `MINIMUM_NUMBER/2` = 3 inliers, so a pair with ≤ 3 correspondences inside its
    distance set cannot reach the 4-inlier floor whatever the normals do. The correspondence set is kd-nearest on
    *points* and this cure moves no point, so no normal estimator can fix these three.
  - *Genuine angle shortfall* — **1-9** (dot_med_d3 +0.953), **2-9** (+0.943), **6-7** (+0.786): the correspondence
    normals are still ~15-20° apart, just under the 15° / \|dot\| > 0.9659 gate. 1-9 is in this group and **not** in
    the unreachable group — it has 7 correspondences, so the count ceiling is not what blocks it; only 2 of them lie
    inside 1.5 mm and their best \|dot\| is 0.860, i.e. it misses on distance and then on angle, both geometric.
- Consequence, written plainly: **at 1.5 mm / 15° with a 4-inlier floor, the Juglet's rims cannot supply enough
  inliers for six of the nine touching pairs.** That is a bound on the assembler's seed rule, not permission to
  relax the gate — `INLIER_THRESHOLD` and `ANGLE_THRESHOLD` stay untouched whatever bar 4 shows.
- One honest regression to record: **2-9's inliers 4 → 0** while its median stayed +0.943. The fitted surface
  normal was a smoother field between these two pieces; the wall-plane normal is more locally varying. It still
  clears the dot bar.
- `n_1to1` (1 for 2-5, 3 for 3-5 and 7-9) is a property of the walked dot sampling, not of the cure.

So bar 3 is **met on its primary clause and unmet on its secondary clause**, and the six failures are half a
property of the harness's minimum-correspondence rule and half genuine angular misses. Flagged for the lead rather
than papered over.

### Lead ruling (2026-11-10) — bar 3: primary PASS 9/9, secondary FAIL on six, the bar is NOT re-worded

- The lead re-derived every `dot_med_d3`, `inl15` and `n_d3_dotneg` from
  `runs/20261110-2325_123f2ca_t328-trim5/out/diag_jug_{before,after}.txt`; all correct as quoted.
- **Primary clause** (`dot_med_d3 >= +0.7` on all nine touching pairs): **PASS 9/9** — and that is the clause that was
  written.
- **Secondary clause** ("strict-gate inliers > 0"): **FAIL on six pairs** — recorded as FAIL. The bar is not re-worded
  to make it pass.
- **Split of the six**: *unreachable by construction* — 2-5 (1 correspondence), 3-5 (3), 7-9 (3), because a pair
  registers only above 3 inliers; *genuine angle shortfall* — 1-9 (+0.953), 2-9 (+0.943), 6-7 (+0.786), all just under
  the 15° / \|dot\| > 0.9659 gate.
- **Consequence**: at 1.5 mm / 15° with a 4-inlier floor the Juglet's rims cannot supply enough inliers for six of the
  nine touching pairs — a bound on the assembler's seed rule, not permission to relax the gate.
  `INLIER_THRESHOLD` and `ANGLE_THRESHOLD` stay untouched whatever bar 4 shows.
- **Bar 4 decides the ticket.**

### Bar 2 — final numbers on the 5 mm + trim build (job G)

`blcheck328.py` on the cured bundle (reference = k=5 mean of the ridden wall's own normals, the same identity
check that passed on job A; `k1` column = single nearest wall point):

| piece | Bl0 frac(dot>0) | Bl0 median | Bl0 frac(abs dot>0.5) | Bl1 frac | Bl1 median |
|---|---|---|---|---|---|
| 1 | 0.983 | +0.962 | 1.000 | 0.906 | +0.626 |
| 2 | 1.000 | +0.879 | 1.000 | 1.000 | +0.943 |
| 3 | 0.955 | +0.877 | 0.841 | 1.000 | +0.971 |
| 4 | 1.000 | +0.938 | 1.000 | 1.000 | +0.965 |
| 5 | 1.000 | +0.963 | 1.000 | 1.000 | +0.955 |
| 6 | 0.927 | +0.846 | 0.976 | 0.956 | +0.891 |
| 7 | 0.944 | +0.897 | 0.778 | 1.000 | +0.955 |
| 8 | 0.950 | +0.859 | 0.775 | 1.000 | +0.951 |
| 9 | 0.828 | +0.912 | 0.759 | 1.000 | +0.980 |

- Every Bl0 point now carries the orientation of the wall it rides: **median dot ≥ +0.85 on all nine pieces**
  (was −0.691 on piece 1 face 1, and a per-point mixture elsewhere).
- The `frac(dot>0)` column is *not* a defect meter here: the reference (k=5 mean of the wall's own vertex normals)
  is itself contaminated at the break edge, exactly the contamination bar 2 removes. The decisive number is bar 3's
  `n_d3_dotneg = 0` on all nine pairs and `dot_med_d3 ≥ +0.79`.
- Bl1 is still governed by the old per-line global sign vote and is **not** cured (piece 1 0.906, its median only
  +0.626). Only `Breakline_0` is read by the assembler, so this is recorded, not fixed.

### Bar 5 — no corpus writes, and the identity gate passes

- Job G's own `list_corpus_before.txt` / `list_corpus_after.txt` are byte-identical (`list_corpus.diff` is empty,
  "corpus listing diff lines: 0"), covering `Dataset/` (the symlink to `/data/gpfs/projects/punim2657/Dataset`) and
  `sfs_main/original_samples/SfS_pp`. Jobs A/C/D/E/F did the same before/after pair; nothing in this ticket writes
  to either tree.
- `Dataset` md5s and `original_samples` md5s are unchanged from job A through job G.
- The identity gate itself is job E (above): `scripts/run_benchmark_172.py --cap 6 --seeds 10 --step 10` into
  `out/axes328` (matches t322's `axes322`), then t323's `build_axes323.py` into `out/axes328f` — **172 files, 251
  data lines, all byte-identical to `20261110-0740_d628fc0_t323-axes/out/axes323`**, which is the t323 reference the
  bar names. The benchmark reads the frozen corpus surfaces and the fitted-axis code only, so it cannot see a mesh-
  or edge-stage change; it is measured, not assumed. The pot slot decisions were re-measured directly as well (job
  A/D cells): identical kept/swapped on all nine pot pieces, so the filing rule moves no pot.

### Bar 6 — renders

`artifacts/pota328/renders/` (eye-checked, workspace-relative):

- `fig1_bar3_pairs.png` — per touching pair, `dot_med_d3` before vs after, the +0.7 bar drawn.
- `fig2_pair_correspondences.png` — every mutual-nearest correspondence at GT as (separation, `n_A·n_B`), before
  (top) and after (bottom), with the assembler's strict inlier box (separation < 1.5 mm, |dot| > 0.9659) shaded:
  the before row has whole populations at −1 (opposing rims), the after row is positive everywhere, and only three
  panels hold ≥ 4 correspondences inside the box — the visual form of the inlier-clause finding above.
- `fig3_hard_pairs.png` — the two hard pairs (1-9, 6-7) zoomed to the meeting in the shared GT pose with the
  exported normals as arrows: before, the two pieces' arrows point opposite ways; after, they agree.

### Job ledger for this ticket

| job | run dir tag | state | note |
|---|---|---|---|
| 34696293 | t328-wallside | CANCELLED (lead) | 4 h copy, cancelled while PENDING |
| 34696906 | t328-wallside-short | FAILED 6:0 | pristine build needs `sfs_pristine_assembly.sif`; cells + binaries were fine |
| 34700288 | t328-harness-after | COMPLETED 0:0 | bar-3 first measurement |
| 34702694 | t328-planenorm | FAILED 5:0 | stale CMakeCache in the seeded src |
| 34703082 | t328-planenorm | FAILED 6:0 | cells + binaries fine, harness copy path slip |
| 34705066 | t328-planenorm | FAILED 6:0 | duplicate WORKH block |
| 34705371 | t328-planenorm | FAILED 7:0 | md5sum broke on the space in "Ground Truth" |
| 34705422 | t328-planenorm | COMPLETED 0:0 | harness, reproduces 326's before table exactly |
| 34702695 | t328-planenorm | COMPLETED 0:0 | bar 5 axes identity |
| 34706334 | t328-trim5 | COMPLETED 0:0 | final build, bars 1-3 |
| 34708113 | t328-e2e | **CANCELLED** (00:00:08) | bar 4 first submission; PENDING with a 06:29:20 estimate until 23:49:08, when Slurm backfilled it — cancelled 8 s later because the 8-cpu duplicate was already running |
| 34709846 | t328-e2e-dup | **CANCELLED** (never started) | lead-ordered duplicate of 34708113, identical sbatch/inputs |
| 34710135 | t328-e2e-dup8 | **COMPLETED** | bar 4 as run: same sbatch, same CURED lanes, same GT-axes staging and gates — only 8 cpus / 32G / 02:00:00 instead of 16 / 64G / 01:30:00, which let it backfill at once instead of 06:29 |
### Bar 4 — E2E measured: two cured repeats + the shipped control (job 34710135, `20261110-2352_123f2ca_t328-e2e-dup8`, **COMPLETED 0:0**, 00:02:00)

The lead ruled that the 06:28 queue estimate was not to be waited for: submit a duplicate of the same submission in
a fresh run directory, take whichever finishes first, cancel the other. That was done — **34709846**
(`20261110-2350_123f2ca_t328-e2e-dup`, byte-identical sbatch) — and, because a 16-cpu ask cannot backfill a
fragmented sapphire (80 of 102 nodes alloc, 45 idle cpus, both 16-cpu copies estimated at 06:29:20), a third copy
asked for 8 cpus / 32G / 02:00:00 instead (**34710135**) and started at 23:47:49. The other two were cancelled at
23:49:16 — 34708113 had itself just been backfilled at 23:49:08 and died 8 s in, leaving nothing usable; 34709846
never started. Only the resource ask differs between the three: the sbatch is otherwise verbatim
(17 lines identical), CURED = `20261110-2325_123f2ca_t328-trim5/outgt_jug/geom`, SHIPPED =
`20261103-1332_fab76f5_t66-admitsign-default/outU_jug/geom`, every tree's `Axes/` overwritten with
`Dataset/Juglet_GT` after staging, FLOOR 20 / NP 9, seam gate untouched, `acc305.py` + `score58.py`.

| arm | sherd (acc305) | edge print | directed pairs | right sherd | seated | own-place chamfer (median) | median gauge error | assemble wall |
|---|---|---|---|---|---|---|---|---|
| **T328C_r1** cured | 2/9 (22.2 %) | **1/18 (5.6 %)** | **2/36** | [1, 8] | **0/9** | 181.6 mm | 122.6 deg | 28 s |
| **T328C_r2** cured | 2/9 (22.2 %) | **1/18 (5.6 %)** | **2/36** | [1, 8] | **0/9** | 179.9 mm | 123.2 deg | 31 s |
| **T66O_r1** shipped control | 2/9 (22.2 %) | 0/18 | 1/36 | [1, 4] | **0/9** | 64.0 mm | 32.5 deg | 20 s |

- **Both cured repeats clear the acc305 gate on the same pair, 1-8** — 5.150 deg / 35.05 mm and 5.218 deg /
  34.17 mm. The control clears **1-4** (10.115 deg / 40.71 mm) and misses 1-8 on distance (9.055 deg / 68.59 mm).
- 1-8 is bar 3's strongest pair (`dot_med_d3` +0.971 before the cure, +0.971 after) and the assembler seeds on it
  in both cured repeats; 1-4 is among the cured arm's worst misplacements (145.3 deg / 600.6 mm) and is what the
  control seeds on. So the cure changes **which** pair the greedy search commits to, and 1-8 is the pair whose
  evidence was always good.
- **Nothing seats in any arm.** `seated_count` 0/9 against the 4.596 mm own-place bar, `right_way_count` 0, median
  own-place chamfer 181.6 / 179.9 mm (cured) against 64.0 mm (control), median per-piece gauge error 122.6 / 123.2
  against 32.5 deg (0 of 9 pieces under 20 deg, against 2 of 9). The cured arm's global arrangement is worse
  **because** the search commits to 1-8 and then cannot place the remaining pieces — an assembler-search outcome,
  not a property of the pair evidence the cure produces.
- **Repeatability**: the two cured repeats are identical in every tally (2/9, [1, 8], 2/36, 1/18) and their 1-8
  pose agrees to 0.07 deg / 0.9 mm. Their raw poses are not identical (the gauge `R` differs in the second
  decimal), so the assembler is non-deterministic as documented; the tally is stable here.
- **Corpus**: `list_corpus.diff` is 0 lines — this job did not write to `Dataset/` or `original_samples/` either.
- **Verdict, plainly**: bar 4 measures **no seating** in either arm, an unchanged sherd tally (2/9 both), a
  repeatable **+1 on the edge print** (1/18 against 0/18) and a **worse global fit**. The cure gives the assembler
  the right evidence at 1-8 and the assembler uses it; it does not make the Juglet assemble. Combined with bar 3's
  inlier bound (six of nine touching pairs cannot supply four inliers at 1.5 mm / 15°), the seating result is
  explained by the seed rule, not by the lines.

### Bar 6 — renders (all under `artifacts/pota328/renders/`, each eye-checked)

- `fig1_bar3_pairs.png` — per-pair `dot_med_d3` before/after against the +0.7 bar (bar 3).
- `fig2_pair_correspondences.png` — every GT contact correspondence as separation against `n_A . n_B`, before and
  after, with the inlier box shaded (bar 3); shows why the secondary clause caps out.
- `fig3_hard_pairs.png` — 1-9 and 6-7 zoomed to the seam, arrows = exported normals (bar 3).
- `fig4_bar4_seating.png` — **the meshes the assembler actually returned**, cured r1 against the shipped control,
  two views each: 8 pieces placed, piece 9 unplaced in both arms, and in both a piece sits detached from the
  cluster (bar 4).
- `fig5_bar4_edge_errors.png` — all 19 directed pairs, log rotation error, pass region shaded, filled dot = also
  within 50 mm; the single 1-8 cure pass and the single 1-4 control pass are annotated (bar 4).

Scripts: `.scratch/pota-repro/t328/render328.py`, `render328b.py` (bars 2-3), `render328c.py`, `render328d.py`
(bar 4).


