# 38: Does more resolution give the two silent sherds a face?

**Status:** in-progress
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
