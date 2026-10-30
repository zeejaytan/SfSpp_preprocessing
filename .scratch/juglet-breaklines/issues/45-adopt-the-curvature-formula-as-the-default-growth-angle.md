# 45 — adopt the curvature formula as the default growth angle

## What to build

Make the pipeline compute the growth angle from each piece's own curvature by default, replacing the tuned
constant 3.4. The law (ticket 43, run of record `20261030-0416_390068c_t43-ab2`):

    theta_deg = 3.3573 x (S / R_fold) x (180 / pi)

- `k = 3.3573` (dimensionless; calibrated so Pot A median S/R lands on 3.4). Units gotcha: k multiplies
  S/R **expressed in degrees** (ratio x 180/pi), not the raw ratio.
- `S` = the run's resolved spacing, already in the binary: `g_effectiveSpacingMM` (declared
  `mesh_processing_headless.cpp:1234`, set :4454 adaptive / :4463 fixed, logged `[SPACING-22]` :4468).
- `R_fold` = median fold radius of the piece, by the ticket-43 instrument's rule
  (`.scratch/juglet-breaklines/stage43/instruments/dist43.py:140-180`, `quadric_radii`): per point, 30
  nearest neighbours, PCA tangent frame, bivariate quadric fit, principal curvatures k1/k2, radius
  1/kmax capped to [0, 60] mm (RHO_CAP_MM = 60), median over the cloud (a random subsample of at most
  20000 points is acceptable for speed — MAX_PTS_RHO, dist43.py:67). Compute it on the same downsampled
  cloud growth runs on.

### Where it goes in the source

At the caller block `mesh_processing_headless.cpp:4647-4649`: today `double paperTheta = 3.4` then env
override. New behaviour:

- `SFS_PAPER_THETA` **set** -> explicit override, byte-for-byte today's path (this is how legacy 3.4 runs
  and the J2 fallback at 10.2 are reproduced; do not change it).
- `SFS_PAPER_THETA` **unset** -> compute from the formula above and print one log line per piece:

      [GROWTH-45] piece=<fileNameOnly> S=<mm> R_med=<mm> theta=<deg>

  so a proof can read the binary's own theta back out of the log (mirror the `[MERGE-41]` line's style).

- `SFS_GROWTH_MODE=outcome` (ticket 42 ladder, opt-in audit) unchanged. The default in the
  `surfaceSegmentation` signature (:3531) may stay 3.4 — the caller always passes explicitly.
- **No per-vessel or per-piece tables, no special cases.** Pure geometry at runtime, one rule both
  vessels. J2 is NOT special-cased: at its own 12.40 it fragments (accepted, evidence below); the
  documented J2 fallback is running that piece with `SFS_PAPER_THETA=10.2`.

### Evidence this rests on (do not re-litigate, cite it)

Ticket 44, run `20261030-1511_fa92002_t44-formula` (job 34028966): the formula's angles, through the
shipped env switch, kept Pot A 8/8 two clean surfaces (within 1-2 % of today) and reproduced 6 of 8
ladder wall pairs on the Juglet (J3-J8, across 0.38-0.63 mm, angle 13-19 deg); J2 lost at its own 12.40;
J1/J9 unchanged. Decision to adopt: conservator, 2026-10-30 ("adopt the formula as the default now and
now that we have evidence").

### Prove-out (one run, mirrors stage44's machinery)

Build `stage45/instruments` from `stage44/instruments` (same gates: CRLF, py_compile, bash -n, dry-render).
One run `runs/<YYYYMMDD-HHMM>_<git7>_t45-default`:

- 17 no-env cells (all released Pot A + Juglet pieces) — the new default path;
- 4 override cells `SFS_PAPER_THETA=3.4` on the proof pieces (Juglet_Piece_2, Pot_A_Piece_01,
  Juglet_Piece_5, Pot_A_Piece_07) — the legacy path;
- corpus md5 gate before==after, as every stage run.

## Answers

- Answers: U19 (does the pipeline put the Juglet back together), E1 (do our breaklines let SfS find joins)

## Blocked by

- none (44 closed)

**Status:** in-progress
**Working in:** chat on Thinkbook16 (2026-10-30)
**Branch:** 45-adopt-the-curvature-formula-as-the-default-growth-angle, in /c/PR/worktrees/sfs/45

## Acceptance

- [ ] Source change confined to the formula + log line at the caller; env-override path untouched
      (`git diff origin/main` shows no other behaviour change).
- [ ] Builds clean (`build_bin` in the sbatch template, apptainer cmake).
- [ ] Per piece (17/17): no-env `[GROWTH-45]` theta within **0.30 deg** of the committed reference
      (`stage44/instruments/thetas44.tsv`, copied into stage45 as reference); the exact delta per piece
      is reported in the ticket. Reference values: PA01 4.36, PA02 3.30, PA03 3.76, PA04 2.92, PA05 3.50,
      PA06 3.17, PA07 2.66, PA08 3.61; J1 10.29, J2 12.40, J3 9.35, J4 10.25, J5 8.74, J6 8.16, J7 8.65,
      J8 10.05, J9 12.68.
- [ ] Outcome class matches the t44 formula arm per piece (17/17): Pot A 8/8 two clean surfaces; Juglet
      J3-J8 two, J2/J1/J9 fragment/none per the t44 record.
- [ ] Override proof: the 4 `SFS_PAPER_THETA=3.4` cells reproduce the t44 arm-A (today) outputs —
      sampled-cloud md5 equal, or surface point counts equal where md5 is not deterministic.
- [ ] Corpus md5 before == after (0 bytes diff).
- [ ] `run.json`, index row appended (verdict/human_note left for the lead), poll + final `sacct`
      recorded in the ticket.
- [ ] Worker reports numbers and paths; the lead runs its own acceptance check before merge (hidden
      before hand-over), verifies, merges, closes, rebuilds the board.
