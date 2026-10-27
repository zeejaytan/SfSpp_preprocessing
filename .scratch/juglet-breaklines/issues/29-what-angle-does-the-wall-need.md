# 29 — What angle does each vessel's wall actually need?

**Status:** ready-for-agent
**Answers:** U19
**Blocked by:** none (read-only measurement; the replica instrument is on main at
`.scratch/juglet-breaklines/stage28/replica234.py`)
**Blocks:** any change to the growth rule

## Why this exists

Ticket 28 established, on the replica that reproduces the pipeline's regions exactly, that the
region growing is not stuck and not floor-limited: it shatters the sherd. Piece 2's 1 031 points
become **661 regions averaging 1.6 points**, largest 36, and the only gate that ever refuses
anything is the angle test (`fail_curv = 0` in all 36 cells; the curvature gate compares
`kappa >= 1.0` against a PCA surface variation that cannot exceed 1/3). Pot A also fragments
(1 276 regions) and survives because its largest region is **36 % of the cloud** against 3.5 % on
piece 2.

Ticket 28 also measured the one obvious dial: the paper's own `paperTheta = 4.0` (we ship 3.4)
gives piece 2 a largest region of 41 — still under the 50-point floor — and costs piece 7 two of
its five regions and Pot A two of its eight. So neither 3.4 nor 4.0 is a figure that serves both
vessels, and nobody has asked the prior question: **what angle separates neighbouring normals on
each of these clouds at all?**

That is what this ticket measures, and nothing else. It changes no code and rebuilds no binary.

## What to measure

All figures come from clouds the pipeline itself produced, so the angles are the angles the
growth sees, not an estimate from the mesh.

### A — the neighbour-normal angle distribution

For every cloud: for each point, the angle between its own normal and the normal of each of its
`k = 10` nearest neighbours (the growth's own `nb`). Report per cloud:

- percentiles p10, p25, p50, p75, p90, p99 and the mean, in degrees;
- the fraction of neighbour pairs at or below each of 2.0, 3.4, 4.0, 5.0, 6.0, 8.0, 10.0, 12.0
  degrees.

Clouds: `Juglet_Piece_{2,3,5,7}` in arms B (defaults, 0.6 mm), D (chain off, 0.6 mm) and E
(chain off, native) from `/data/gpfs/projects/punim2657/SfSpp/runs/20261027-0337_d69f76f_t25-dump-grid2`,
and `Pot_A_Piece_07` at defaults from
`/data/gpfs/projects/punim2657/SfSpp/runs/20261027-1537_5227f8f_t28-pota07-dump`.

### B — the theta ladder

Run the calibrated replica at `theta in {2.0, 3.4, 4.0, 5.0, 6.0, 8.0, 10.0, 12.0}` on every
cloud above, with `kappa = 1.0`, `nb = 10`, `floor = 50` (today's values). Per (cloud, theta)
report: number of regions, size of the largest, size of the second largest, the **share of the
cloud claimed by regions at or above the floor** ("kgate"), the number of angle rejections, and
the largest region's depth.

### C — the calibration gate, before anything else is reported

At `theta = 3.4` the replica must reproduce the pipeline's own rung-2 sizes from each cloud's
`r2_clusters_premerge.json`. State, per cloud, the pipeline sizes and the replica sizes side by
side. Ticket 28 got seven of eight identical on Pot A 07 and one region ten points short; the
same tolerance applies here. **If the gate fails on any cloud, stop and report that** — no ladder
figure from an uncalibrated replica.

### D — the comparison that decides

One table: for each theta, the Juglet's four clouds (arms B and, separately, D and E) against
Pot A 07. The two things a repair has to do at once:

- give the Juglet **at least two regions at or above the floor** and a kgate of at least 0.5;
- leave Pot A with **at least eight regions at or above the floor**, its two largest (3 093 and
  2 850 points) intact.

If no single theta does both, say so and say which theta comes closest on each side. That is a
result, not a failure.

## Where the inputs come from, and what happens to them

The dumps above are geometry from tickets 25 and 28, both closed. Read them **read-only**; do not
write into those run directories. Their geometry is **borrowed by this ticket and deleted when it
closes**, with a counted record, under the standing rule that geometry dies with the ticket that
last needed it. Do not delete them inside the job — the lead deletes them at close, so the count
appears in the ticket.

## What this ticket must not do

- No change to `mesh_processing_headless.cpp` or any other tracked source, no rebuilt binary, no
  environment-variable tuning of the production path.
- Do not touch the corpus (`/data/gpfs/projects/punim2657/sfs_main/original_samples/SfS_pp`),
  `/opt/sfs-pristine` (record it ABSENT; do not create it), or the canonical checkout.
- Do not lower the floor to make a region count as big: ticket 23 measured 21-32 point surfaces
  and they are 28-42 % corner patch. The floor stays 50 and `theta` is the only dial.
- No verdicts. Report numbers, per-piece tables and the figure; the lead reads them.

## Acceptance

1. The calibration gate (part C) is reported per cloud, with pipeline and replica sizes side by
   side, and the run stops if it fails.
2. `out/angles.tsv` — one row per (cloud, percentile/threshold), with the cloud's point count and
   `k` on every row.
3. `out/theta_ladder.tsv` — one row per (cloud, theta) with every field in part B named in the
   header.
4. The part D table, Pot A included, with both conditions stated per theta.
5. One figure: a panel per cloud showing the angle histogram, and one panel showing kgate against
   theta with the Juglet and Pot A curves distinguishable by colour and labelled in the legend.
   State the figure's size, mm-per-pixel and scale bar. Fixed colours, one legend.
6. A run directory under `/data/gpfs/projects/punim2657/SfSpp/runs/` with `run.json`,
   `submit.sbatch`, `logs/`, `out/`; one `index.tsv` row with `verdict` and `human_note`
   **empty**.
7. A statement of the replica's own limits in the run's `out/summary.md`: it reproduces the
   region growing only, and knows nothing about the merge step or the 3 mm reassignment, so a
   theta that looks good here is a candidate for a pipeline run, not a result.

## Evidence to report back

1. Job ids with `sacct` state and exit code, and the run directory paths.
2. The part C calibration table, per cloud.
3. The part A percentiles and threshold fractions, per cloud.
4. The part B ladder, per cloud.
5. The part D comparison table.
6. The figure's path, size and scale.
7. The borrowed dumps' paths and sizes, so the lead can delete them with a count.
8. Anything not done, with the command that failed and what it said.

## What this cannot settle

- A theta that separates the clouds in the replica is not a pipeline result: the merge step and
  the 3 mm reassignment sit between the growth and any surface. The ticket after this one runs the
  winning theta through the pipeline on the same pieces, Pot A beside it.
- Five clouds on two objects. A ladder is a lead about where to look, not a rate.
- It says nothing about the other repair on the table — a second growth pass over the points no
  region kept (78-82 % of a Juglet sherd, 10-22 % of a Pot A one). Both are live; this ticket is
  the cheaper one and it is the one the conservator's "tune the figure" question asks first.
