# 12: Which Pot J surfaces change the axes enough to recover joins?

**What to build:** Identify influential sherds by swapping one axis file at a time. Then compare those sherds' wall surfaces and test which measured difference reproduces the axis change.

**Answers:** E1
**Blocked by:** None. Frozen Ticket 03 inputs and the Ticket 08 surface audit are sufficient. Ticket 11 supplies trace context.
**Status:** ready-for-agent
**Worker:** unassigned
**Budget:** medium 5
**Hand-over:** DeepSeek. Independent acceptance held by lead.

## Baseline and scope

Ticket 03 held our breaklines and the assembler fixed. Its selector on our walls gave 5/21 and 4/21 scored joins. The same selector on the authors' walls gave 15/21 and 16/21. Use the selector at `2e951d9` and the exact executable/configuration resolved from `20261121-1319_2e951d9_t03-ship` and `20261121-1600_2e951d9_t03-jctl`. Use their own-wall and author-wall axis outputs (`axes03_own` and `axes03_tri`) as the two sources. Author-wall axes here means re-estimated by our selector on those walls. The authors' released axes and ground-truth axes are different artifacts. Use reference labels only for scoring and diagnosis.

Keep selector, assembler, flags, breaklines, assembler surface inputs, named sherd set and scorer fixed. Record hashes, actual binary SHA, input frames and units, and paired seed/thread settings where supported. Read the project corpus caveats. Keep unscored sherds out of denominators, but include them in the swap census if their axis files are read by the assembler.

## A. Identify influential sherds

1. Replay the all-own and all-author-wall axis controls in two matched attempts each. Save repeat-level and per-seam results. Confirm the contrast is reproduced in both paired attempts before interpreting swaps. If it fails, locate the input/configuration mismatch or report inadequate repeatability.
2. On the all-own axis baseline, make one arm per sherd whose loaded axis file differs between sources. Replace exactly that sherd's entire axis file with its author-wall counterpart, preserving candidate count, ordering, line positions and directions from that file. Prove a one-file diff, run the same two attempt settings, and report gained and lost seam IDs, pose errors, final seated counts and axis changes. Count gains anywhere in the graph. Record identical files as no-op arms without launching them. Use one run directory and an array or bounded batches for the cells.
3. Rank by net scored joins gained in the weaker repeat, then by fewer baseline joins lost. A reproducible positive swap gains at least one net join in both paired attempts. Show best-of-two and how often it was reached. For up to two leading positive sherds, run one reciprocal one-file swap on the all-author-wall background with the same two settings to test context dependence. If no positive swap reproduces, report that no individual swap reproduced the full contrast and examine the two most divergent axis files as exploratory cases. No combined swaps in this ticket.

## B. Compare the surfaces and isolate a cause

For up to three sherds, inspect the strongest two positives (or exploratory cases) and one nonresponding comparison. Use native-frame wall overlays with matched views and scale. Confirm same sherd, coordinate frame, interior/exterior identity and units before comparing. Record per wall point counts, distinct positions, footprint and missing regions, symmetric surface distances on shared support, local spacing, and signed normal-angle distributions at matched points with distance and unmatched fractions. Render both original and changed axis lines from fixed views and show where the surfaces differ. Report line angle, origin offset and candidate rank, keeping physical dimensions in mm.

Use the same selector settings and paired random draws across a raw-control repeat and at most three single-factor comparisons per selected sherd. Choose the comparisons from the observed contrasts before scoring the changed axes. Separate normal effects (matched normal transfer on fixed positions with unchanged points outside shared support), spatial coverage (restrict to matched support), and sampling effects (equalise density on the same support with normals carried, recording the reduction). Use paired controls if point count must change with coverage. Save the input transformation manifest and audit which attributes changed. A surface feature is implicated only when changing it reproducibly moves the estimated line toward the author-wall estimate beyond raw-repeat spread, with no contradictory change in line offset or sign left unexplained. Confirm the best supported factor on at most one sherd by substituting its newly estimated axes alone into the frozen assembly replay. If no test isolates a factor, report the surviving explanations and what evidence would separate them. Ticket 08 already tested simple duplicate removal.

## Acceptance

- [ ] Hash manifest demonstrates fixed inputs and one changed axis file per swap. Export per-arm and per-seam tables with the two controls and both repeats. State any missing cells or unstable controls.
- [ ] Surface comparison includes aligned paired renders and matched metrics, plus raw-repeat and single-factor axis results. Fetch the small evidence into `C:/PR/artifacts/axis-parity-12/`. Keep geometry and transformation scripts/patches in the Spartan run record.
- [ ] Every submitted job is polled and has a final sacct State/ExitCode, run ID and index record. Verify corpus manifests unchanged. Heavy work stays on compute nodes.
- [ ] Write factual evidence and End state on the ticket branch. Only the ticket write-back may change in git. Leave the merge, close and research verdict to the lead.

## Comments

One-shot experiment. Ticket 03 establishes the surface-source contrast. [PotSAC](https://openaccess.thecvf.com/content_ICCVW_2019/papers/EH/Hong_PotSAC_A_Robust_Axis_Estimator_for_Axially_Symmetric_Pot_Fragments_ICCVW_2019_paper.pdf) motivates checking wall positions and normals separately.
