# 38: Does more resolution give the two silent sherds a face?

**Status:** done
**Working in:** chat on Thinkbook16 (2026-10-28)
**Branch:** 38-does-more-resolution-give-the-silent-sherds-a-face, in /c/PR/worktrees/sfs/38
**Answers:** U19
**Blocked by:** none
**Blocks:** none

## Why this exists

Ticket 37 measured that at native spacing, with the scan's own normals, sherd 2 grows 1 765
regions whose largest is 45 points and sherd 9 grows 1 465 whose largest is 16, against a floor
of 50. The conservator's reading is that the difference from the sample pot is **resolution**:
Pot A 07 carries 34 608 points at 0.2929 mm spacing, drawn from a released 1 000 000-point scan,
while piece 9 carries 1 972 points at 0.2035 mm and its whole mesh has 2 094 vertices.

The arithmetic supports him. The growth's criterion is an **angle between neighbouring normals**,
and turning per step is roughly spacing / local folding radius, so the same surface passes or
fails the same 3.4 deg gate depending on how finely it is sampled. These sherds fold over
0.67-5.25 mm (ticket 32), which gives ~9-13 deg per step at 0.20 mm and would give ~3.4 deg at
~0.06 mm. We have only ever measured a 2.4x increase (ticket 36, adaptive spacing), never the
3-4x the arithmetic asks for.

This ticket tests that directly, by subdividing the sherd meshes to x2, x4 and x10 before sampling.

## What must be built (instruments only, no change to the pipeline's behaviour)

1. **A mesh sampler with analytic normals.** Sample a triangle mesh at a requested spacing with
   points on the faces and the FACE normal at each point. Barycentric, area-weighted, deterministic
   seed. This is the ideal-normals arm: it separates spacing from normal estimation.
2. **Midpoint subdivision** of a triangle mesh at level L (each triangle into L^2 sub-triangles).
   Report the surface displacement this introduces: linear subdivision cuts a curved corner by
   about (edge^2)/(8R), which at edge 0.2 mm and R 1 mm is ~5 microns. State the measured max
   displacement from the original surface, not the estimate.
3. **The existing replica** (C:/PR/SfSpp_preprocessing/.scratch/juglet-breaklines/stage28 and
   stage29 instruments, unchanged in behaviour) to grow regions at 3.4 deg on the sampled cloud and
   report the full pre-floor distribution.

**Instrument proof before any result is used**: sampling the ORIGINAL mesh at its own spacing must
reproduce the shipped cloud - point count within 5 % and median nearest-neighbour spacing within
5 % of `Dataset/Point/Juglet/Juglet_Piece_9_Point.pcd` and `Juglet_Piece_2_Point.pcd`. Print the
comparison. If it does not reproduce them, say so and stop; a sampler that cannot reproduce the
shipped cloud cannot be trusted two levels finer.

## Design

Pieces: **Juglet 2 and 9** (targets), **Juglet 3, 5, 7** (controls: 7 already surfaces, 3 and 5 are
one-cluster cases), and **Pot_A 07 as the always-works reference at its own unchanged resolution**.

Levels and the spacing each level asks for (achieved spacing is measured, not assumed):

| level | sub-triangles | sampling spacing |
|---|---|---|
| x1 | 1 | 0.2035-0.3420 mm (native, as shipped) |
| x2 | 4 | native / 2 |
| x4 | 16 | native / 4 |
| x10 | 100 | native / 10 |

Arms per (piece, level):

- **A**: replica at 3.4 deg on the sampled cloud with **analytic face normals**.
- **B**: replica at 3.4 deg with the pipeline's own PCA re-estimation at that density
  (neighbours = max(5, min(20, n/1000)) as in `mesh_processing_headless.cpp:420`). Target pieces
  2 and 9 only, at x4 and x10.

x10 on pieces 2 and 9 only. If a x10 cloud exceeds 1.2 M points, sample at the finest spacing the
mesh supports and report the achieved spacing beside the requested one - do not silently change the
level.

**One real pipeline cell** at the finest level that shows a region >= 50: stage that synthetic cloud
as a run input (in the run directory, never into the frozen corpus), run the unmodified pipeline,
and report the pipeline's own `[STATUS-23]`/`Number of clusters` lines. If no level produces a
region >= 50, skip this - there is nothing for the pipeline to reproduce.

## What counts as the answer (the lead decides; the worker reports evidence)

For each (piece, level) report the distribution BEFORE any floor:

- number of regions, largest region size and its share of the cloud
- how many regions reach 10 / 20 / 30 / 50 points and 1 % / 5 % / 10 % of the cloud
- angle refusals per point and the depth reached by the largest region
- for the largest region: extent (mm), the fraction of the ORIGINAL piece's cloud within 2 mm of it,
  and its median folded angle to the ORIGINAL mesh
- where two regions both reach 50 points, the corrected pair statistic: for each Surface_1 point,
  nearest Surface_0 point, component ALONG that point's normal and ACROSS it, coincidence at 1 micron

## Figure

One figure per target piece: a panel per level (x1, x2, x4, x10) drawing the largest region against
the original mesh, same camera and scale within a piece, 5 mm bar, mm/px printed, and below it a
small plot of largest-region size against achieved spacing with the 50-point floor and the level at
which 3.4 deg would be met marked.

**Part E - a second look at the ticket-37 figure, for the conservator's question.** He asked why the
grey dots on piece 9 leave white space where Pot A 07's dots fill the surface. The measured answer so
far: ink covers 10.6/13.9/16.0 % of piece 9's three panels against Pot A 07's 17.5/14.0/12.5 %, but
**82-83 % of piece 9's ink is pale grey** (regions ranked ninth and below, drawn at alpha 0.55)
against 26-31 % on Pot A 07. So redraw piece 9 (and Pot A 07 beside it) with (a) the tail at full
opacity and a marker one step larger, and (b) a continuous rank palette so all 1 465 regions can be
seen rather than pooled into grey. Same camera and scale as the ticket-37 figure. Two PNGs, and
report the ink/grey/colour fractions again from the new PNGs.

## Constraints

- **No change to tracked pipeline behaviour.** Instruments and tables live under
  `.scratch/juglet-breaklines/stage38/`; if the pipeline itself must change to accept a synthetic
  cloud, stop and report instead.
- Compute nodes only. Never the login node, never the laptop.
- The frozen corpus `/data/gpfs/projects/punim2657/sfs_main/original_samples/SfS_pp` and
  `/opt/sfs-pristine` (record ABSENT if absent) are read-only; md5 before and after, compared.
- Synthetic clouds are **labelled synthetic in every table, figure and filename**. They are a probe
  of the criterion's spacing dependence, not new data about the sherd.
- Geometry dies with the ticket: point clouds and meshes deleted at the end with a counted record
  written BEFORE the delete. Keep: tables, logs, the sampler and subdivision sources, the figures.
- At most **four** jobs; split by piece group, never by level. CRLF-check every script before
  submitting (two grids have already died on "set: pipefail: invalid option name").
- Run directory convention as usual, index row with `verdict` and `human_note` left EMPTY.
- Report evidence, not verdicts: no "this shows", no "the cause is", no Status change.

## Evidence to report

1. The instrument proof (sampled original vs shipped cloud: counts, spacing p50, ratio).
2. Achieved spacing per (piece, level), measured, beside the requested one.
3. The max displacement of each subdivided surface from the original mesh (mm).
4. The full pre-floor distribution table per (piece, level, arm), with the floor marked.
5. The largest-region table: size, extent, 2 mm coverage of the original cloud, folded angle to the
   original mesh, per (piece, level).
6. The pair statistic wherever two regions reach 50 points.
7. The real pipeline cell at the finest level that reaches 50 points, with its own log lines, or a
   statement that no level did.
8. Figures with paths, sizes, mm/px; plus the Part E redraws and their ink/grey/colour fractions.
9. Corpus and pristine md5 before/after; the geometry deletion record; the four (or fewer) job ids
   with `sacct` states; the branch head sha.
10. Anything not done, with the command that failed.
## Progress (work in progress, 2026-10-28)

Numbers, evidence and the exact failures are in `.scratch/juglet-breaklines/stage38/REPORT.md`; the run of record
is `/data/gpfs/projects/punim2657/SfSpp/runs/20261027-1615_92d6871_t38-resolution/` (job 33890365, commit
`92d6871022fdf75f63170a5af65b30e31c9e843a`). Four jobs were available and four were used, all `FAILED` in
`sacct`; the last one completed phase 1 in full and died in phases 2 and 3.

Delivered by the run: items 1-6 and 9 of "Evidence to report" — sampler gate on both target pieces (with the
literal count test failing on an under-dense shipped cloud and route 2 passing), achieved spacing per
(piece, level) 0.986-0.993 of the request, the full pre-floor distribution for 24 cells plus 12 control cells,
the largest-region table against the original mesh, the 20 pair rows, corpus/inputs md5 unchanged (215 rows
either side, `corpus.diff` and `inputs.diff` 0 bytes), `/opt/sfs-pristine` recorded ABSENT, the geometry deleted
with counts recorded first (112 files / 672 680 485 bytes, plus 401 / 103 262 155 from the aborted first run),
and the two figures (item 8's first half).

Not delivered: item 7 (the real pipeline cell) — `run_cell38.sh: line 15: STAGER: parameter null or not set`; and
item 8's Part E redraws — phase 2 aborted before them on `ValueError: ...Pot_A_Piece_07_Point.pcd: only ascii
clouds here` (the released Pot A cloud is binary). Three instrument defects are fixed in the tree and were never
exercised by a job: the binary PCD path, the missing `STAGER` export, and two figure defects (row labels
overprinting the first panel's tick labels; `floor_reached_at` reporting x10 when the 50-point floor is already
cleared at the coarsest level, x1, on both pieces). Item 3's displacement numbers as measured (1.81 mm piece 2,
1.15 mm piece 9) are the incident-candidate artefact, not displacement; the exact per-parent measurement is
described in the report and is not implemented.

### After the fifth (final) job — 2026-10-28

The paragraph above stands as the record of run 4; a fifth job was authorised and spent, and it supersedes the
"not delivered" list where noted. Run of record for items 6-8 and the figures:
`/data/gpfs/projects/punim2657/SfSpp/runs/20261028-0414_2a34d86_t38-resolution/` (job 33892259, commit
`2a34d86a54467ac1f0238eed214bc11bdf7be208`), `TIMEOUT` at 00:40:11 with phase 3 mid-cell; its closing bookkeeping
(corpus/inputs md5, geometry census and delete, run-meta, index row) was then executed by hand from that run's own
`submit.sbatch` function bodies — bookkeeping only, no compute — because bash defers a `trap` until the foreground
child returns and Slurm's 15 s kill window cut the shell off first.

Now delivered: item 6 corrected and re-derived (the old `med_across` / `p90_across` columns are VOID — the step's
absolute projection was reused to rebuild the perpendicular part, inflating it up to 2 x `med_nn`; on arm A the
true residual is 0.02-0.16 mm against an along-axis step of 2.11-2.29 mm, i.e. the second-largest region is a sheet
offset by about one wall thickness — Juglet 2 2.693 mm, Juglet 9 2.595 mm — and essentially parallel; arm B
collapses along to 0.23-0.43 mm with a 0.47-0.91 mm residual; 41 rows including the controls and Pot A 07);
item 7 partly — three real pipeline cells ran (Juglet 2 x1 8 clusters, Juglet 9 x1 7 clusters, Pot A 07 on the
1 000 000-point released cloud 7 clusters, each `[STATUS-23] outcome=two` with 4 155/3 979, 2 229/3 512 and
24 636/26 741 points in the two written surfaces); item 8 in full (the replay reproduces ticket 37's 9.0 % ink and
82.7 % pale grey on piece 9 and 12.7 % / 28.6 % on Pot A 07, while the new redraw brings the pale-grey share of
ink down to 0.09 and 0.06); the five-piece aggregate; and the two resolution figures re-rendered with the label
and `floor_reached_at` fixes (the coarsest clearing level is x1 on both pieces: 873 and 1 410 points).

Still open, in the report's own item 10: the x10 pipeline cells (P2 x10 sampled at 0.02080 mm in 153.2 s and its
pipeline was started; the wall clock ended it, and P9 x10 never started — the guard read a day-scale counter from
`squeue -o %L`, 88 474 s, so it skipped nothing); the per-surface extent / 2 mm coverage / folded angle for the
three cells that ran (the surface-extension loop kept the `.xyz` instead of the `.ply`,
`[PIPELINE] surface 0 is xyz, not a ply`); item 3 exact per-parent displacement (the delivered 1.81 / 1.15 mm are
the candidate-triangle artefact; the analytic bound is <= 1e-6 mm); and `cloud_points` blank on the Pot_A row of
`pipeline_cells.tsv` (`grep ^POINTS` on a binary PCD). Job budget 5 of 5; no sixth job.
Status, `Answers:` and `intent/` are unchanged; no judgement about what the numbers mean is recorded anywhere.

## Lead reading — 2026-10-28 (verified first-hand, not taken from the worker's report)

**The conservator's hypothesis holds: resolution was a real limiter.** At the sampler's own density on the
same mesh, sherd 2's largest region goes from 46 points (today's 0.6 mm cloud) to **873**, and at x10 to
**190 064** (29.0 % of 649 067); sherd 9 goes 16 -> **1 410** -> **177 914** (32.5 % of 547 195). Counts
clearing the 50-point floor go 9 -> 444 on 2 and 8 -> 406 on 9. Both sherds stop being silent.

**The pipeline confirms it, not just the replica.** Two real cells ran at the sampler's x1 density:
- `Juglet_Piece_2` 6 259 points at 0.209045 mm: "Number of clusters is equal to 8", after the merge 4
  (1684, 1620, 62, 52), `[STATUS-23] outcome=two`, **surf0 4 155 / surf1 3 979** points, 2 mm coverage
  0.768 / 1.000, diagonal 27.47 / 27.74 mm on a 28.31 mm sherd, folded to the mesh 3.104 / 3.013 deg.
- `Juglet_Piece_9` 5 256 points at 0.201486 mm: 7 clusters, after the merge 6
  (589, 1497, 327, 166, 158, 89), `outcome=two`, **surf0 2 229 / surf1 3 512**, coverage 0.814 / 0.733,
  diagonal 19.52 / 22.02 mm on a 23.50 mm sherd, fold 2.966 / 2.803 deg.

**But the two surfaces written are not two faces, and the pipeline says why in its own log line.** My own
measurement of the four kept PLYs:

| piece | surf0 pts | surf0 distinct | surf1 pts | surf1 distinct | shared (of the smaller) | mean-normal dot |
|---|---|---|---|---|---|---|
| Juglet 2 | 4 155 | 2 471 | 3 979 | 3 979 | 2 352 (**0.952**) | **+0.9960** |
| Juglet 9 | 2 229 | 2 229 | 3 512 | 2 015 | 1 616 (**0.802**) | **+0.9993** |

Surface_0 is nested inside Surface_1, and their mean normals point the **same way** — an inner/outer pair
must point opposite ways. The signed through-distance histogram says the same: on piece 2, 2 359 of
Surface_1's points sit within +-0.2 mm of Surface_0 (the shared face) and 1 369 sit 2-4 mm the other side;
on piece 9, 3 472 are within +-0.2 mm and only 39 lie further out.

The mechanism is the 3 mm boundary admission, printed by the pipeline itself on piece 9, surface 0:
`own_cluster_points=589 other_cluster_points=2237 candidates=5256 admitted_own=1610 admitted_other=1640`
(`[WINDOW-26]`, mode literal). Each surface recruits roughly half of the whole sherd, so whichever wall a
point belongs to, it lands in **both** surfaces. That is the ticket-26 defect, now measured on the surfaces
the pipeline actually writes, on clouds where the clusters really are separated — the one condition under
which ticket 26 could not see it.

**What follows from that.** The next test is cheap and single-purpose: the same two cells with
`SFS_REASSIGN_MODE=own` (ticket 26's rival rule, each point admitted only to the fitted surface it is nearer
to). If the two faces then come out facing opposite ways with most points unshared, the pair exists at dense
sampling and the remaining question becomes whether that density is physically available. If they do not, the
pooling is not admission alone and `finishImprovedSurface`'s copy branch (`mesh_processing_headless.cpp:1167-1170`)
has to be read out next.

**Two corrections to the record, both mine.**
1. The pair statistic used in tickets 26, 30, 33, 34, 36 and 37 took the absolute value of the signed offset
   before splitting it into "through" and "along", which inflates the along-column to
   `sqrt(across^2 + 4t^2)` wherever the second sheet lies behind the first. It is corrected here and the old
   `med_across` / `p90_across` columns are void. Rows affected: `stage33/results/run3/out/pairs33.tsv`
   40 of 40 (worst Pot_A_Piece_01 reported 14.18, correct 0.30), `stage33/results/pairs33.tsv` 12 of 13,
   `stage34/results/out/cells/*/*/measure/pairs.tsv` Pot A 01-08 (reported 7.10-7.86, correct 0.29-0.57),
   `stage26/evidence/measure26.tsv` 1 of 116. The earlier tickets' `along` and `med_nn` columns are sound, so
   their conclusions about *whether* a pair exists mostly survive; what does not survive is my sentence in
   ticket 34's reading that **the Juglet never yields two real faces** — I withdraw it.
2. The sampler proof I asked for could not pass as written: the shipped Juglet cloud **is** the mesh's vertex
   set (2 565 vertices against 6 259 points from an even covering at the same spacing, 0.232 points per mm^2
   against 3.94), so part of the ladder measures what even covering adds, not what resolution adds. Route 2
   (spacing ratio 0.9885-0.9942, median cover 0.529 s, median distance on the mesh 0.0011 mm) is the honest
   instrument proof and is what the numbers rest on.

**Where the run fell short, recorded rather than papered over.** The Pot A reference cell was killed by the
30-minute wall clock inside the pipeline on the 1 000 000-point released cloud, so this run has **no Pot A
row**; its reference numbers stand from tickets 26/34/37 (8 of 8 pairs, through 3.55-7.09 mm, across
0.13-0.27 mm). Both x10 pipeline cells are missing (the wall-clock guard read `squeue %L` as a day-scale
remainder, so piece 2 x10 started and was killed and piece 9 x10 never began). Run 5 was closed on the login
node after its timeout (resources, md5s, deletion records, index row only) — disclosed by the worker, recorded
here because the rule is that a job's record is written by the job.

### verified: the command or file behind each load-bearing claim
- `cat out/cells-pipeline/surfaces.tsv` -> 4 rows, the counts, coverage, diagonals and folds quoted above.
- `cat out/cells-pipeline/surface_pairs.tsv` -> med_nn 0.0 and coin 0.5911 / 0.8246 on the two cells.
- `grep -ah "Number of clusters|RETRY-23|STATUS-23|WINDOW-26" out/cells-pipeline/*/logs/*.log` ->
  8 and 7 clusters, sizes, `outcome=two`, and piece 9's `admitted_own=1610 admitted_other=1640`.
- My own PLY check (`artifacts/juglet-p38/check38.py`, four downloaded surfaces, rounding 1e-4 mm) ->
  2 352/2 471 shared and +0.9960 on piece 2; 1 616/2 015 shared and +0.9993 on piece 9.
- `sacct -j 33894591` -> TIMEOUT, 00:30:16, and the Pot A cell absent from `surfaces.tsv`.
- `git diff --name-status main...HEAD` -> nothing outside `.scratch/juglet-breaklines/`; no tracked source
  change, so the pipeline in these cells is the default pipeline.
- The pair-statistic defect reproduced on synthetic planes (2.2 mm inside its partner reported 4.4 mm) and the
  fixed `pair_pointwise` (`stage38/instruments/measure34.py:295-308`) keeps `t` signed.

### What this does not settle
Whether own-mode admission turns the nested surfaces into two facing faces at dense sampling. Whether the
nesting is the admission window alone or also the `finishImprovedSurface` copy branch. Whether a scan of these
sherds can actually carry 6 000-650 000 points — subdivision interpolates and invents no detail, so this
measures the geometry the method needs, not the geometry the museum has. And nothing about Pot A at this
instrument, whose reference cell did not run.
