# 29 — What angle does each vessel's wall actually need?

**Status:** done
**Branch:** 29-what-angle-does-the-wall-need, in /c/PR/worktrees/sfs/29
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

## Lead reading — 2026-10-27 (verified first-hand, not taken from the worker's report)

**The answer in one sentence: the pot's neighbouring normals agree to a median of 1.20°, the vessel's to
8.21–15.80°, so the shipped 3.4° admits 72.4 % of the pot's neighbour pairs and only 7.9–19.5 % of the
vessel's — and no single threshold from 2° to 12° lets both work.**

### The two halves of the measurement

Angle between neighbouring normals, k = 10, the growth's own candidate set:

| cloud | points | p50 | p90 | ≤ 3.4° | ≤ 12° |
|---|---|---|---|---|---|
| Pot A 07 | 8 598 | **1.20°** | 21.81° | **72.4 %** | 84.3 % |
| Juglet 2 (0.6 mm) | 1 031 | 15.80° | 50.57° | 10.8 % | 40.6 % |
| Juglet 3 (0.6 mm) | 1 467 | 13.46° | 50.18° | 15.0 % | 46.4 % |
| Juglet 5 (0.6 mm) | 3 021 | 9.30° | 41.23° | 19.2 % | 58.1 % |
| Juglet 7 (0.6 mm) | 4 254 | 8.21° | 35.54° | 19.5 % | 63.8 % |
| Juglet 7 (native) | 8 421 | 8.73° | 27.93° | 18.6 % | 62.7 % |

The ladder, on the replica that reproduces the pipeline's own region sizes exactly at 3.4°:

| theta | Juglet clouds passing (of 4, arm B) | Juglet min kgate | Pot A regions ≥ floor | Pot A 3 093/2 850 |
|---|---|---|---|---|
| 2.0 | 0 | 0.000 | 6 | broken (3 043/2 761) |
| 3.4 | 0 | 0.000 | **8** | **intact** |
| 4.0 | 0 | 0.000 | 6 | intact |
| 6.0 | 1 | 0.125 | 7 | intact |
| 8.0 | 2 | 0.274 | 6 | intact |
| 10.0 | 2 | 0.453 | 5 | intact |
| 12.0 | **4** | 0.502 | 3 | intact but fused (4 529/3 103) |

A Juglet piece "passes" at a theta when it yields at least two regions at or above the 50-point floor and
those regions hold at least half the cloud. The pot "passes" at eight regions at or above the floor with its
two 3 093 and 2 850 regions intact.

### What I take from it

1. **The shipped threshold is calibrated on the pot, and it is the pot's unique optimum.** Pot A is the only
   vessel of the two that passes at 3.4°, and 3.4° is the only theta at which it passes. That is not a
   coincidence of the grid: at 4.0° the pot already loses two of its eight regions, at 2.0° it loses its two
   big ones.
2. **The vessel needs about 3.5× more, and at 12° it is only just beginning to work** — the top of the
   ladder is where it first passes, so the best value for the vessel may lie above 12°, where the pot cannot
   follow. The two requirements do not overlap at any point in the tested range.
3. **The gap is in the input, not in the algorithm.** The growth is applying one number to two clouds whose
   neighbour-angle distributions differ by an order of magnitude. Any single global constant must therefore be
   wrong for one of them, and this explains, in one line, why the same code segments a pot and shatters a
   sherd.

### Why the two clouds differ — a hypothesis, not a measurement

A curved surface turns by roughly (point spacing ÷ local radius of curvature) per neighbour step. At 0.6 mm
spacing, a sherd curving over 5–15 mm turns 2–7° between neighbours before any noise, while a flat stretch of
pot wall turns far less. That would make the correct angle a property of the sherd's *curvature*, not of the
material, and it would explain why the curvature gate at `mesh_processing_headless.cpp:1959` (which rejects
`kappa >= 1.0` against a PCA surface variation that cannot reach 1/3) never fires, while the angle gate does
all the work. **To verify**: measure each cloud's mean curvature radius and check whether p50 × radius ÷
spacing is roughly constant across the two vessels. I have not done this and the ticket does not claim it.

### What this ladder cannot say

- It tests **region growing only**. The merge step, the 3 mm boundary reassignment and the classification all
  sit between these regions and any exported surface, so "two regions at or above the floor" is **not** "two
  faces of the wall". A theta that looks good here is a candidate for a pipeline run, not a result.
- It counts points, not surfaces. Whether the two regions at 12° are the inner and outer face of a 2–3 mm
  wall, or two patches of one face, cannot be answered from this instrument.
- Five distinct clouds on two objects (see the first defect below). A ladder is a lead about where to look.

### Three defects in the evidence, found while checking it

1. **The D arm is a duplicate of the B arm, and the worker reported it as "bit-identical ... expected".** It is
   expected, and it also means the ladder has **nine distinct clouds, not thirteen**: the replica grows the
   same rung-1 cloud whatever `SFS_PAPER_CHAIN` says, so the chain-off arm adds nothing to a theta sweep.
   The D rows stay in the tables as a consistency check, not as evidence.
2. **The figure in the run directory is not the figure that was committed.** The job's render annotates
   "above 83 deg" while its histogram stops at 60°; the committed file is a redraw from the run's own tables
   with the axis and the label at 60°. Same numbers, different pictures — I opened both. The committed one is
   the figure of record; the run directory's copy is the uncorrected render it replaced.
3. **A compiled `.pyc` was committed** under `stage29/__pycache__/`. Removed in the write-back commit.

A fourth, harmless: two index rows exist for this ticket because the first submission failed before measuring
anything ("unrecognized arguments: survey" — the batch line passed a subcommand to a flat CLI). The index is
append-only, so the failed row stays, marked void by the lead.

### verified: the command or file behind each load-bearing claim

- verified: `awk -F'\t' '$8=="percentile" && $9=="p50"'` over `out/angles.tsv` → 15.80 / 13.46 / 9.30 /
  8.21 degrees for `B/Juglet_Piece_{2,3,5,7}`, and 1.20 for `PA/Pot_A_Piece_07`.
- verified: `awk ... '$8=="fraction_le_deg" && $9=="3.4"'` over the same file → 0.7237 on Pot A 07 against
  0.0789–0.1953 on the eight Juglet clouds.
- verified: `out/theta_ladder.tsv`, arm B, theta 3.4 → regions 661 / 825 / 1 467 / 1 951 with largest 36 /
  169 / 679 / 326, exactly ticket 28's numbers for the same clouds.
- verified: `out/theta_ladder.tsv`, arm B, theta 12.0 → `regions_ge_floor` 3 / 2 / 5 / 5 and `kgate`
  0.501 / 0.515 / 0.772 / 0.808; theta 10.0 → 0.478 / 0.453 / 0.657 / 0.737, so two of the four fall below
  0.5 there.
- verified: `out/theta_ladder.tsv`, arm PA, every theta → `regions_ge_floor` 6, **8**, 6, 6, 7, 6, 5, 3 for
  2.0, 3.4, 4.0, 5.0, 6.0, 8.0, 10.0, 12.0, with largest/second 3 093/2 850 only at 3.4 and 4 529/3 103 at 12.0.
- verified: `out/calibration.tsv` → the four arm-B rows are MATCH with replica sizes identical to the
  pipeline's own rung-2 sidecars (169,99 / 679 / 326,263,77,68,65); `sidecar_paper_chain` is False on every D
  and E row, which is why those carry `NOT-GATED-sidecar-is-pcl-region-growing`.
- verified: `sacct -j 33864736,33865557` → FAILED 2:0 in 00:00:14 and COMPLETED 0:0 in 00:00:18, both on
  `spartan-bm*` compute nodes.
- verified: `git diff --stat main..origin/29-what-angle-does-the-wall-need` → 15 files, +1 706/−1, every path
  under `.scratch/juglet-breaklines/stage29/` plus the ticket's own four claim lines; no tracked source.
- verified: `read_image` of both PNGs → the run directory's copy reads "above 83 deg" with the x axis to 83;
  the committed copy reads "above 60.00 deg" with the axis to 60.
- verified: `awk` over `/data/gpfs/projects/punim2657/SfSpp/runs/index.tsv` → lines 285 and 286, both six
  fields with the verdict column empty, 286 lines in the file.
- verified: `du -sh` of the borrowed dumps and `cmp` of `out/dump_inventory.diff` / `out/dump_md5.diff` →
  both empty; 130 files, 15 935 977 B, read-only and unchanged.

### What this does not settle

- Whether the theta that helps the region growing survives the merge, the 3 mm reassignment and the
  classification. That needs a pipeline run, not a replica.
- Whether a per-cloud theta chosen from the cloud's own distribution is a good rule, or whether the angle is
  the wrong criterion entirely for a curved sherd (see the curvature hypothesis).
- Anything about the second repair on the table: a second growth pass over the points no region keeps.
- The paper's own 4.0° sits between the two vessels' needs, and the reason it was published is that the
  authors' sample is Pot-A-like. That is a reading of these numbers, not a claim about the paper's intent.
