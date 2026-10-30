# 48 — the method: curvature angle on corpus clouds, no densify

## What to build

The shipped method becomes: read the corpus-conforming input cloud, measure the sherd's own fold radius
on it, set the growth angle by the ticket-43 formula (theta = 3.3573 x S / R_fold), grow, and let the
growth split the cloud so the fracture boundary can be extracted — with **no densify, resample or
covering step anywhere in the path**. Ticket 46's even covering was a diagnostic instrument that stood
in for a working input; once ticket 47 installs real corpus clouds, the covering is retired and the
paper-compliance story simplifies with it.

**Answers:** U19

**Blocked by:** 47 (needs the corpus-conforming Juglet clouds installed).

**Status:** ready-for-agent

**Worker:** unassigned

## Three parts

1. **Verify arm (source unchanged).** Nine Juglet cells on the ticket-47 clouds with
   `SFS_GROWTH_FORMULA=1` and no other `SFS_*` set; eight Pot A cells on their released clouds in the
   same configuration as control. The prediction under test: the pipeline's own voxel downsample of a
   ~1 000 000-point corpus cloud produces an even layout — the mechanism the ticket-46 covering proved —
   so theta lands within ~2 % of the k43 predictions (J1 10.29, J2 12.40, J3 9.35, J4 10.25, J5 8.74,
   J6 8.16, J7 8.65, J8 10.05, J9 12.68 deg) and every piece grows two surfaces. If it does not,
   report where it lands and stop — that is the measurement speaking, not a tuning invitation.
2. **Default flip (source change, only if the verify arm holds).** No-env growth becomes the formula —
   ticket 45's intent, gated off since `2263532`. `SFS_PAPER_THETA=3.4` remains the paper-repro
   override. A default-check run proves no-env cells reproduce the verify arm exactly
   (`SampledWithNormals` md5 equality), the mirror of run `20261031-0200_2263532_t46-default-check`.
3. **Retire the covering.** `cover_cloud46.py` and the stage46 instruments get a DIAGNOSTIC-ONLY banner
   in their headers and a line in `COPIES.md`; confirm no pipeline source references them (none ever
   did — state the check). Ticket 16 (paper-compliance audit) is told in writing: the method's only
   deviation from the paper is the angle rule itself (the paper ships a flat 3.4 measured on Pot A;
   ours derives per sherd); the input side now follows README step 1 exactly, and the paper's IV-B1
   breakline resample at 1.9 mm (ticket 06) is a different, untouched step.

## Honesty lines this ticket carries

- The grown pair on Juglet sherds sits ~0.2-0.3 mm apart (tickets 44 and 46) — two layers of ONE face,
  not the wall's two faces (wall 2.4-3.3 mm). The fracture boundary comes from the breakline step on
  Surface_0; seating itself is judged in ticket 07, not here.
- Pot A thetas read 1.09-1.38x over the k43 predictions on its own released clouds — recorded beside
  the Juglet numbers, not hidden and not re-calibrated away.

## Acceptance

- [ ] Verify arm: 9 of 9 Juglet cells on ticket-47 clouds (corpus md5 equals ticket 47's MANIFEST),
      zero covering artifacts in any input; Pot A corpus unchanged.
- [ ] `theta_check` vs k43 at the 2 % band with per-piece deltas; outcome class and surface counts per
      piece; pair table for every two-surface cell.
- [ ] Pot A control: same config as t45 arm F expectations, counts within 2 %.
- [ ] Default flip: diff confined to `mesh_processing_headless.cpp` (the `2263532` gate inverted to
      default-on) + stage48 instruments + this ticket file; default-check run shows `[GROWTH-45]` lines
      with no env and md5-equal outputs vs the verify arm; `SFS_PAPER_THETA=3.4` re-proven on one piece.
- [ ] Covering retired (banner + COPIES.md note + reference check); ticket 16 notified.
- [ ] `run.json` and index rows for every job (verdicts left empty), poll + final `sacct` recorded.
- [ ] Worker reports numbers and paths; the lead runs its own hidden acceptance check before close.

**Needs-eye:** the 3x3 grown-surface panel on the new clouds, beside ticket 46's.

## Comments
