# Ticket 42: the growth's angle should be set by the outcome, not shipped as a constant

**Answers:** U19, E1
**Blocked by:** none (ticket 41 merged as 8ee02a2)
**Blocks:** 07
**Status:** ready-for-agent

## The question

Ticket 41 located the last blocker: with own-mode admission shipped, the real-cloud tally is 1 genuine
pair (J1), 3 patch pairs (J5/J7/J8), 5 silent (J2/J3/J4/J6/J9). The loss is growth-side. Two mechanisms,
opposite directions:

- **Fusion (J3/J4/J6):** at adaptive spacing (~0.2 mm steps) the per-step normal turn across the broken
  edge falls below the 3.4 deg gate, so growPaper234 wraps the sherd into ONE band (retry sizes 289 /
  335 / 707) and the merge never has a second region. These pieces need a TIGHTER angle at fine spacing.
- **Fragmentation (J2/J9):** the largest floor-clearing region is 45 / 16 points against a floor of 50;
  the compliant set is shattered. Loosening the angle helps only if a larger region clears the floor.

Source facts (main at 8ee02a2):
- The retry loop at `mesh_processing_headless.cpp:3544-3559` already loosens an angle by +2 per retry,
  cap 45 deg — but ONLY `smoothnessAngleThreshold`, the PCL RegionGrowing dial. `paperTheta` (the
  paper-chain gate, angle test `pcl::getAngle3D(curN4, nn4, true) > thetaDeg` at `:3191`, printed in
  `[PAPER-234]` at `:3646`, env `SFS_PAPER_THETA` at `:4574`) NEVER moves inside the loop. That is why
  21 retries change nothing on any silent piece.
- The loop only loosens UPWARD. It cannot help a fused piece, which needs a smaller theta.

## What to build

**One switch, default today:** `SFS_GROWTH_MODE=angle|outcome` (default `angle` = exactly today's
behaviour; Proof 1 below).

In `outcome` mode, replace the loop's blind +2 loosening with a **bidirectional ladder search over
`paperTheta`**: for each piece, try thetas in degrees from the set {0.25, 0.5, 0.75, 1.0, 1.5, 2.0,
3.0} x 3.4 (i.e. 0.85, 1.7, 2.55, 3.4, 5.1, 6.8, 10.2), ordered to try the CURRENT default first,
then outward in both directions. For each theta, run the growth + floor and record:

- `[GROWTH-42] piece=<p> theta=<t> clusters=<n> ge_floor=<k> largest=<s> second=<s2> outcome=<none|one|two>`

**Selection rule (printed):** the LARGEST theta whose growth leaves >= 2 floor-clearing regions; if no
theta leaves 2, the theta with the LARGEST single region (so J2/J9 report their best fragment). Print
`[GROWTH-42-FINAL] piece=<p> chosen_theta=<t> rule=<two-regions|largest-region> clusters=... sizes=...`.
The chosen theta then flows into the rest of the pipeline unchanged (merge, own-mode admission, write
gate). The ladder search may reuse the existing retry loop or replace it locally in outcome mode — but
the PCL path's behaviour must be untouched.

Proofs:
1. `SFS_GROWTH_MODE=angle` (and unset) reproduces today's binary: identical SampledWithNormals md5 and
   identical [RETRY-23] sequences on Juglet 1/3/5/7 and Pot_A 07.
2. No environment without the new switch set reaches outcome mode (grep the logs for GROWTH-42 lines:
   zero when unset).

## Grid (real released clouds only — no synthetic)

All 9 Juglet + all 8 Pot A, arms:
- **A** today (SFS_GROWTH_MODE unset),
- **B** SFS_GROWTH_MODE=outcome.

Both arms of a piece in one job. At most 3 grid jobs (split by pot if needed, never by arm), plus at
most 3 dead plumbing submissions.

## Measurements per cell

- The full [GROWTH-42] ladder and the chosen theta per piece.
- Pipeline outcome ([STATUS-23]), cluster sizes, surfaces (points, diagonal mm, 2 mm coverage, folded
  angle to the ORIGINAL mesh).
- Corrected pair statistic on any two-surface outcome (signed-t variant, stage38 instruments): med_nn,
  med_along, med_across, coincidence, mean-normal dot — with the ticket-35 wall thickness beside it
  (J2 2.693, J9 2.595, J7 3.263 mm; measure the rest with measure35.py in the same job).
- **Anchor cells (hard expectations, must match to the point or explain):** J1 arm A 10800/15780;
  PA07 arm A 24636/26739; PA01 66763/57286; under arm A, J3/J4/J6 must stay one-cluster/silent and
  J2/J9 stay none — any deviation means arm A is not today's binary.

## Reference numbers to prove the instrument

- Ticket 41 run of record: /data/gpfs/projects/punim2657/SfSpp/runs/20261029-0017_bdbd8b8_t41-juglet
  and .../20261029-0111_1f68ae7_t41-measure (J1 B pair along 1.8152 / across 0.5282; J4 D dot +0.9785
  across 6.158; J6 D +0.5813 across 8.247; Pot A 32/32 shared 0 dot <= -0.9988).
- Ticket 37 pre-floor region sizes at the adaptive default: J2 largest 45, J9 largest 16.
- Ticket 30 ladder (0.6 mm clouds): theta 10-12 gives 2-5 regions on J2/J3/J5/J7 but costs Pot A two
  regions at 12 (8 -> 3, largest fused 4529). The Pot A arm here is the regression guard.

## Constraints

- Only `mesh_processing_headless.cpp` and `.scratch/juglet-breaklines/stage42/` may change; stop and
  report if anything else needs an edit.
- Corpus and /opt/sfs-pristine read-only, md5 before/after (/opt/sfs-pristine is ABSENT on this host —
  record that, do not create it).
- Compute nodes only; CRLF-check every script before submit (two grids died on `set: pipefail: invalid
  option name`); no `xargs -d`/`-n 2` on line-split input; grep binary PCDs with `grep -a`.
- Geometry deleted with a counted record written BEFORE the delete; cell surface PLYs and logs KEPT
  for the lead; index rows appended with verdict and human_note EMPTY.
- Report numbers and paths, not verdicts. No writes to intent/, no Status change, no merge.

## Evidence to return

1. The [GROWTH-42] ladder per piece (both arms, all 17 pieces).
2. Chosen theta and rule per piece, with the outcome it produced.
3. Surfaces and corrected pair statistics per two-surface cell, walls beside them.
4. Anchor-cell results vs the expectations above.
5. Proof 1 (defaults byte/sequence-identical) and Proof 2 (no GROWTH-42 lines when unset).
6. Corpus/inputs md5 before/after; /opt/sfs-pristine status.
7. Geometry deletion record; index rows; sacct for every job.
8. The exact diff of mesh_processing_headless.cpp (`git diff main...HEAD -- mesh_processing_headless.cpp`).

## Done when

The ladder exists in the pipeline, both proofs hold, and the lead can read for every one of the 17
pieces what theta the outcome chose and whether it produced two floor-clearing regions.