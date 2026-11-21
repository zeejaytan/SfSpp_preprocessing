# 11: Validate the early join poses and find where Pot J loses its joins

**What to build:** A calibrated pairwise replay that identifies the first stage losing usable joins with our own axes, then tests one bounded repair only if the evidence identifies that stage.

**Answers:** E1
**Blocked by:** None. Use frozen Ticket 03/10 inputs and Ticket 10 write-back at c031d97. No dependency on the Ticket 09 writer or fresh surfaces.
**Status:** ready-for-agent
**Worker:** unassigned
**Budget:** medium 5
**Hand-over:** DeepSeek. Independent acceptance held by lead.

## 1. Validate the ruler before testing the method

The Ticket 10 tables contain 52/58 own-axis and 75/75 released-axis Pot J states. All four show zero reference-good seams within the recorded pose tolerances. Pot A also shows zero early states with all seams within tolerance despite its 15/15 final assembly. The traced poses were exported after graph refinement, and the J1–3 seam close-up is blank. Establish frame, transform direction, member/edge identity, and stage before treating those rows as measurements of physical seating.

Use the exact assembler SHA/build flags and source for Ticket 10. Read the scorer and actual definitions of graph pose accumulation, initial axis alignment, transform composition and final export. Trace uniquely keyed events, with selected sherd IDs and the exact matched point ranges, at candidate creation, pairwise refinement, graph placement, group registration, shared-axis realignment, plausibility and beam selection. Reuse existing instrumentation around `ranking_system.cpp:1703–1781` where available. Establish whether an equal rigid realignment of both sherds preserves the decoded relative pose. Check one synthetic control with known noncommuting rotation and translation, initial sherd-to-axis transforms and a common graph-frame change. Require exact member and pair identities, recover the known relative pose within 0.01°/0.01 mm, and verify transformed native points agree with directly dumped working points within 0.01 mm. In one real final state each for Pot A and released-axis Pot J, compare decoded poses to scorer inputs for all scored sherds after matching gauge, and reproduce each scored seam verdict. Require an actual rendered seam with both sherds and nonempty matched intervals. If calibration fails, stop at the failed assertion and fix/report it before any method trial. Do not use the Ticket 10 table counts as a target.

## 2. Compare identical breaklines under different axes

Replay two matched attempts each for Pot J own-axis and released-axis controls, and one Pot A control. Hash breaklines and other invariant inputs, record exact sherd IDs, units, flags, seeds/thread counts and executed binary SHA. Compare the instrumented and baseline output with identical settings, logging any remaining instability. Use the existing scorer and corpus caveats. Keep reference seam/pose labels outside candidate generation, ranking and acceptance. Track all available hypotheses on the scored Pot J seams and all admitted false pairs. For each reference seam, report occupancy, best pose, candidate rank and survival across stages, with angle, translation and symmetric distance over the recorded matched intervals plus support length. List missing, wrong-pair and correctly paired but misposed outcomes separately. Use seam identity plus physical pose and rendered seating. Report where the successful released-axis final seams first become sound, including graphs larger than three sherds when relevant. Report any drift as a within-hypothesis before/after change.

## 3. Run one intervention only if the stage is isolated

Freeze settings before opening reference labels for the comparison. Follow the first reproducible own-axis deficit:

- Sound candidates missing or misposed before group registration: run an offline rigid pair fit from the existing matched point intervals, with the current correspondence ordering and its existing reverse alternative. Remove the axis penalty for initialization only. Keep current physical verification and use the existing hypothesis cap. If no adequate point intervals exist, report the missing coverage and stop before fitting.
- Sound candidates present but lost at pruning or beam insertion: retain one additional pose per affected candidate pair, within a fixed per-pair cap of two, keyed by runtime seam support and distinct pose. Use the existing plausibility checks. Choose candidates without reference labels.
- Sound poses drift during a solve: replay the same hypotheses with the implicated axis term disabled in that solve only. If the measurement shows a common-frame change masquerading as drift, fix the measurement and rerun the baseline.

Require the same two own-axis attempts to gain at least two distinct scored seams that pass the existing relative pose tolerances and survive the implicated stage, with no loss of previously sound seams and no additional accepted false seam in the Pot A control. Provide locked-view before/after renders at seam scale for one gain and one failure, with support length and distances in physical units. Report repeat-by-repeat and best-of-two with frequency. This gate earns a separate end-to-end trial. A later trial targets Pot J at 8/11 sherds and 16/21 joins on own inputs while preserving other pots and Juglet. Revisit Ticket 04 only after a calibrated replay shows a sound multi-sherd state and a reason to test pooled refinement.

## Acceptance

- [ ] Calibration assertions, unit/direction/source map, and final scorer cross-check. Export a stage-by-stage TSV and build/input manifest plus labeled renders to `C:/PR/artifacts/axis-parity-11/`. Preserve minimal source patches and commands in the Spartan run record.
- [ ] Record run IDs, index rows, per-job polling and final sacct State/ExitCode, and equality of before/after corpus manifests. Perform builds and geometry tests on Spartan compute nodes. Fetch small evidence only.
- [ ] One factual write-back with End state, including missing data and any intervention skipped by its gate. Only the ticket write-back may change in git. No production edits, corpus changes, writer rerun, merge, close, or edits to other tickets or intent.

## Comments

One-shot experiment. Prior work for this direction is the pinned SfS++ pairwise matching and verification sequence (arXiv 2502.13986v1 §IV-C) and [Huang et al.'s fracture registration followed by group constraints](https://doi.org/10.1145/1141911.1141925).
