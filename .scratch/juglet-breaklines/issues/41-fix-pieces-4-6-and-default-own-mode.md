# 41: fix the pieces-4/6 loss and make own mode the default

**Status:** in-progress
**Working in:** chat on Thinkbook16 (2026-10-29)
**Branch:** 41-fix-pieces-4-6-and-default-own-mode, in /c/PR/worktrees/sfs/41
**Answers:** U19
**Blocked by:** none
**Blocks:** 07 (the Juglet end-to-end run, PAUSED)

## Why this exists

Ticket 40 measured the whole vessel for the first time and found two things. Own admission
(`SFS_REASSIGN_MODE=own`) separates both faces on 9 of 9 sherds on a uniform covering where the radius
admission nests on 8 of 9, and Pot A is untouched by it (8/8, shared 0, dot <= -0.9988). But the
ticket-37 adaptive-spacing default silently loses Juglet pieces 4 and 6: at the adaptive default they
grow ONE cluster and write no surface (both arms), while at the old fixed 0.6 mm they wrote pairs of
182/732 and 608/1016 points. The conservator chose (2026-10-29): fix that regression, then make own
mode the shipped default, verified in one grid over all nine sherds at real density.

Hypothesis to test, not assume: at the finer adaptive spacing the paper merge's fixed 1.0 mm
boundary-pair distance (`SFS_PAPER_RHOD`, default 1.0) reaches more neighbours per boundary point and
fuses the two regions into one - the same fusion seen on piece 3 at 0.6 mm ([169,99] -> [268], ticket
25). The candidate repair is to scale the merge thresholds by the spacing actually used, which is also
the standing "hardcoded metric must be adaptive" rule.

## Changes to the code (two, both with defaults proofs)

1. **Flip the admission default:** `SFS_REASSIGN_MODE` default "radius" -> "own" at the env read
   (mesh_processing_headless.cpp:3903-3905 area). Proof 1: with SFS_REASSIGN_MODE=radius explicitly
   set, the new binary reproduces the pre-change binary's Surface_0/Surface_1 point counts and the
   nest statistics on Juglet 1,5,7,8 and Pot A 07,08,01 within the run-to-run spread.
2. **Add `SFS_MERGE_SCALE=literal|spacing`** (default literal = today). In spacing mode every
   paper-merge threshold that is a length in mm (RHOD only - check that RHON/RHOC/RHOINN/RHOINC are
   dot/corvature terms and are NOT scaled) is multiplied by (S / 0.6) where S is the spacing the run
   actually used (the [SPACING-22] S). Print `[MERGE-41] piece=... scale=... rhod_raw=... rhod_eff=...`.
   Proof 2: with SFS_MERGE_SCALE=literal the merge behaves exactly as today (same cluster counts on
   pieces 1,5,7 and Pot A 07).

The merge-scale DEFAULT stays literal in this ticket. Whether it ships as spacing is the lead's
decision from this grid's evidence, recorded in the reading, not the worker's.

## The grid (at most 2 jobs, split by pot)

All cells on REAL RELEASED clouds, no synthetic, no SFS_DOWNSAMPLE_TARGET override. Pieces: all nine
Juglet + all eight Pot A. Arms:

- **A** today exactly: adaptive spacing, radius admission, literal merge (baseline; must reproduce
  ticket 40's g2/g3 numbers: J1 5497 shared; PA01 66764/57288; PA07 24636/26739).
- **B** own admission only (SFS_REASSIGN_MODE=own, literal merge) - the default-flip arm.
- **C** own + SFS_MERGE_SCALE=spacing - the repair candidate for pieces 4/6.
- **D** fixed 0.6 mm spacing + own admission (SFS_SPACING_POLICY=fixed) - the revert arm that must
  restore pieces 4 and 6 to two surfaces (182/732 and 608/1016 at the old defaults; with own
  admission the counts may move - report them beside the recorded ones).

## Measurements per cell

1. [SPACING-22] S and the downsampled point count; pre-merge cluster count and sizes (from the
   pipeline's own cluster print), post-merge count and sizes, [MERGE-41] line.
2. [STATUS-23] outcome and written surface point counts, extent, 2 mm coverage of the piece cloud,
   folded angle to the mesh.
3. Nest statistics (shared distinct points both ways, mean-normal dot) and the corrected pair
   statistic (med_nn, med_along, med_across, coincidence, signed t) per ticket 38's fixed instrument
   (stage38/instruments/measure34.py, the corrected pair_stats).
4. Wall thickness per piece (measure35.py) beside each pair statistic.
5. The pieces 4 and 6 story in full: at which rung do they lose the second region in arm A (pre-merge
   sizes vs post-merge), and what each of B/C/D does to them.
6. Switch proof table: which cells ran which switches (grep the env echoes).

## Constraints

- Only mesh_processing_headless.cpp + .scratch/juglet-breaklines/stage41/ may change; stop and report
  if anything else must.
- Compute nodes only; CRLF-check every script; the xargs/-n-2, unbound-variable under set -u, and
  brace-stripping traps are already paid for - name them in the scripts' headers.
- Corpus, /opt/sfs-pristine (record ABSENT, do not create) and the canonical checkout read-only, md5
  before/after.
- Geometry deleted with a counted record written BEFORE the delete; keep cell surface PLYs, logs and
  tables.

## Evidence to report

1. The two proofs (radius-reproduces-old and literal-merge-reproduces-old) with numbers.
2. The four-arm table over 17 pieces x 6 measurements.
3. The pieces 4/6 rung-by-rung account.
4. Pot A regression check: 8/8 two surfaces in every arm, pair statistics within the ticket-40 band.
5. Index rows appended with verdict and human_note EMPTY; corpus/input md5; deletion record; squeue
   clear.

Numbers already on record to prove the instrument against: ticket 40's g2 (A: J1 shared 5497, J5 34,
J7 336, J8 200; B: 532/0/10/0; J1 B along 1.815 across 0.528 coin 0.035) and g3 (PA01 66764/57288,
PA07 24636/26739, PA08 26774/29286; walls PA01 8.2857, PA07 4.0574); fixed-0.6 pieces 4/6 pairs
182/732 and 608/1016 (ticket 23 arm A).
