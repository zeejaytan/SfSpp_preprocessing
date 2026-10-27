# 30 — Should the growth's criterion be an angle at all?

**Status:** in-progress
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
