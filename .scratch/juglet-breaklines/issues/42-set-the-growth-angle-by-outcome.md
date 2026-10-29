# Ticket 42: the growth's angle should be set by the outcome, not shipped as a constant

**Answers:** U19, E1
**Blocked by:** none (ticket 41 merged as 8ee02a2)
**Blocks:** 07
**Status:** done
**Working in:** chat on Thinkbook16 (2026-10-29)
**Branch:** 42-set-the-growth-angle-by-outcome, in /c/PR/worktrees/sfs/42

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

## Lead reading — 2026-10-29 (verified first-hand from all three run dirs, not from the reports)

**One-line answer:** setting the growth angle by outcome produces genuine wall pairs on Juglet pieces
2-8 — seven sherds that today write nothing or patches — but the selection rule as built (largest
theta leaving >= 2 floor-clearing regions) is wrong: it also rewrites pieces whose default already
works, damaging Pot A on 5 of 8 pieces and Juglet 1. The repair is one gate away: run the ladder
only when the default angle fails to leave two regions, which the pipeline's own retry loop already
detects.

### The runs

1. Grid run 33959417 (commit 41321a2): ladder, proofs and cells valid, BUT its cell script pinned
   `SFS_REASSIGN_MODE=radius` on every arm (run_cell42.sh:117-119 in that commit) — since ticket 41
   the shipped default is **own**, so that run's arm A was not today and every post-admission number
   in it measured the retired rule. I caught it from the J1 anchor miss (0.0072 along, coin 0.46 =
   the radius nesting signature of tickets 36/37); the Pot A anchor still hit because radius and own
   agree on Pot A. Post-admission tables from 33959417 are VOID; its ladder lines, Proof 1 and
   Proof 2 stand.
2. Measurement rerun 33988274 (commit 676e37c): root cause of the header-only tables was the shipped
   instruments lacking replica37.py/measure34.py/mesh38.py (ModuleNotFoundError at every measurement
   call). Fixed; tables filled; its exit 10 was the designed J1 anchor miss, itself the radius-pin
   symptom above.
3. **Run of record 33989453** (commit f864f3f, spartan-bm069, COMPLETED 0:0, 24:15): arm A carries
   no env overrides (true today), arm B adds only SFS_GROWTH_MODE=outcome, measurement inline.
   Anchors hit exactly (J1 armA 2.0146/1.8152/0.5282; PA01 7.0952/7.0890/0.2709); reassign proof:
   zero mode=radius, the 12 surfacing armA cells log mode=own; zero theta=0.0 rungs (8f9eb29 fix).
   The recorded nest miss (J1 armA shared 532 vs ticket-40's 5497) is expected: 5497 was under
   radius; under own it is 532 (ticket 41's own-mode value). Not a defect.

### What outcome mode does (run of record, signed-t pair statistic)

Juglet armB (chosen theta 10.2 everywhere; walls in brackets): J2 1.88/0.67 [2.92]; J3 1.77/0.51
[2.68]; J4 2.14/0.45 [2.76]; J5 2.46/0.42 [3.10]; J6 2.28/0.48 [2.73]; J7 2.52/0.52 [3.35];
J8 1.86/0.38 [2.26] — med_along/med_across in mm, coincidence 0.00-0.015: **seven genuine inner/
outer pairs**, through-distance 0.65-0.95 of the ray-cast wall. J9 is borderline (0.79/2.42);
J1 REGRESSES (theta 10.2 grows one 28 980-point band plus a 295-point sliver; pair 7.86/18.97 =
patches), because J1's default 3.4 was already right.

Pot A armB (chosen 6.8 on 01/03/07/08, 10.2 on 02/04/05/06): 5 of 8 damaged — PA02 16.16/16.27,
PA04 8.63/39.85, PA06 23.46/33.06, PA05 a 1 173-point sliver, PA07 13.93/5.40, PA08 8.20/7.80.
Pot A armA is clean 8 of 8 (3.55-7.09 along, 0.13-0.27 across, coin 0).

### What I take from it

1. The outcome-set idea is confirmed where it applies: on every Juglet sherd whose default angle
   fails, a larger angle grows two face-sized regions that own-mode admission then keeps apart.
2. The rule's scope is the defect, not the ladder: it must fire only when the default leaves fewer
   than two regions — exactly the retry loop's existing condition (`numberOfClustersCreated < 2`,
   mesh_processing_headless.cpp:3544). Default-first would keep J1 and all of Pot A untouched and
   still rescue J2-J8: a projected 8 of 9 genuine pairs on the Juglet (J9 borderline).
3. The second-region test should also require face size (e.g. >= 1% of the cloud), so a 295-point
   sliver cannot satisfy it the way it did on J1 armB and Pot A armB here.
4. Weight: one vessel, nine sherds, one run per cell; the 7-pair result is a lead until the
   default-first variant is run. No edgeline was scored — no weight on the 281/292 tally.

### What this does not settle

Whether default-first outcome mode holds on a second run (determinism of the ladder), whether J9's
borderline pair is real, and whether the surfaces the ladder writes carry breaklines the assembler
can use — that is the e2e question (ticket 07, still paused).

verified: anchors.tsv (run 33989453) -> J1 0.0000/0.0000/0.0000 diff, PA01 0.0000/0.0002/0.0000, all yes
verified: reassign_proof.tsv -> 12 own / 5 no-line (J2/3/4/6/9 wrote no surfaces) / 0 radius
verified: surface_pairs.tsv armB rows read directly -> J2 1.882/0.670/0.0146 ... J8 1.861/0.380/0.0 as quoted
verified: surface_pairs.tsv PotA armB -> PA04 8.628/39.848, PA06 23.457/33.065 as quoted; armA all clean
verified: pipeline_cells.tsv chosen_theta -> Juglet 9x 10.2; PA 6.8 on 01/03/07/08, 10.2 on 02/04/05/06
verified: run 33959417 run_cell42.sh:117-119 -> 'SFS_REASSIGN_MODE=radius' on arms A/B/R (the defect)
verified: sacct 33957458/33957459 CANCELLED 41:24 (ladder-advance bug), 33959417 COMPLETED 14:23, 33988274 FAILED 5:28 exit 10 (designed anchor miss), 33989453 COMPLETED 24:15
verified: nest.tsv J1 armA shared=532 == ticket 41's own-mode value; the 5497 anchor belonged to radius
verified: corpus/inputs md5 identical before/after in all three run dirs; geometry deletions counted and written before the delete
