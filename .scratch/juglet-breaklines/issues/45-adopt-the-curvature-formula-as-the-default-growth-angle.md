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

## Result (2026-10-30) — NOT adopted; the in-pipeline radius does not reproduce the calibration

Run `20261030-2128_f4a3559_t45-default`, job 34054302, `sacct` COMPLETED 0:0 in 00:04:56, commit
`f4a3559`. All 21 cells ran (17 no-env, 4 override), corpus and inputs unchanged, instruments md5
gated. The build and the source change are sound. **The angle the default produces is not the
formula's angle, and on the Juglet it destroys the piece.**

### What the run measured

| | delivered by the new default | ticket-43 reference | in tolerance |
|---|---|---|---|
| Juglet J1 | 10.37 | 10.29 | yes (+0.08) |
| Juglet J2 | 48.56 | 12.40 | no (+36.2) |
| Juglet J3 | 46.41 | 9.35 | no (+37.1) |
| Juglet J4 | 39.89 | 10.25 | no (+29.6) |
| Juglet J5 | 24.61 | 8.74 | no (+15.9) |
| Juglet J6 | 32.31 | 8.16 | no (+24.1) |
| Juglet J7 | 18.68 | 8.65 | no (+10.0) |
| Juglet J8 | 37.77 | 10.05 | no (+27.7) |
| Juglet J9 | 54.38 | 12.68 | no (+41.7) |
| Pot A PA01-PA06 | 5.71 / 4.58 / 4.43 / 3.57 / 4.22 / 4.08 | 4.36 / 3.30 / 3.76 / 2.92 / 3.50 / 3.17 | no (1.2-1.4x high) |
| Pot A PA07 | 2.88 | 2.66 | yes (+0.22) |
| Pot A PA08 | 3.93 | 3.61 | no (+0.32) |

`out/theta_check.tsv`: **within_0.30 = 2 of 17** (J1, PA07). Outcome class
(`out/cells-pipeline/pipeline_cells.tsv`): **8 of 9 Juglet pieces produced no surface at all**
(`status_outcome=none`); only J1 grew two (325 / 29,040 pts). Pot A grew two on 8 of 8 as always.
The 3.4 override arm reproduced today's path exactly on its 4 cells (J2 none, J5 two 143/2,304,
PA01 two, PA07 two).

### Why — measured, not inferred

The port is faithful. `foldcheck45.py` (dist43's `quadric_radii`, unchanged, k=30, run on a compute
node) applied to the **pipeline's own input clouds** reproduces the binary's numbers:

| piece | dist43 on pipeline cloud, k=30 | binary `[GROWTH-45]` R | calibrated R (mesh sample at S) |
|---|---|---|---|
| J2 | 0.7828 | 0.8355 | 3.2358 |
| J1 | 6.1476 | 6.2733 | 6.3736 |
| PA01 | 13.2829 (raw 1M cloud) | 20.2232 (0.6-downsampled cloud) | 26.2046 |

So the same code on the same cloud agrees with the C++ to 2-7 %. The disagreement is in the
**cloud**, and it is large: R swings 2-4x between point sets of the same piece (J2 0.78 vs 3.24;
PA01 13.3 vs 20.2 vs 26.2). A 4x low R gives a 4x high theta, which is exactly the 18-54 deg seen.

The Juglet input clouds are the reason they are hit hardest: 2,094-24,294 points per piece against
~1,000,000 for Pot A, and the mesh sample the calibration used at the same nominal spacing carries
about 2.5x more points (J2: 6,288 sampled vs 2,565 in the corpus cloud). Only J1, the one piece with
24k points, lands.

### What this does not say

It does not overturn ticket 44's evidence. Fed the **same thetas through `SFS_PAPER_THETA`**
(run `20261030-1511_fa92002_t44-formula`), all 9 Juglet pieces grew two surfaces and 6 of 8 ladder
wall pairs held. The formula's *values* work; its *estimator*, as the pipeline can compute it today,
is not stable enough to be the default. Reading R off a k=30 quadric at 0.2-0.6 mm spacing is not a
property of the sherd — it is a property of the point set.

### Options this leaves open (for the conservator)

1. **Do not ship the formula as a default**; keep 3.4 and pass per-piece thetas explicitly (proven in
   ticket 44). Cheapest, changes nothing today.
2. **Make R stable first**: fix the physical patch diameter instead of k (or sample the mesh at S as
   dist43 does), recalibrate, then re-test. A real ticket with its own spike.
3. **Densify the Juglet clouds** (2,565 points for a whole sherd is very sparse) and re-measure —
   separate from the formula, and it may matter for every Juglet result so far.

## Answers

- Answers: U19 (does the pipeline put the Juglet back together), E1 (do our breaklines let SfS find joins)

## Blocked by

- none (44 closed)

**Status:** ready-for-human
**Working in:** coordinating session, 2026-10-30 — run verified by the lead, verdict void, awaiting the conservator's choice between options 1-3
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