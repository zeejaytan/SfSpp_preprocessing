# 43 — derive the growth angle from each sherd's own curvature

**Answers:** U19, E1
**Blocked by:** none (ticket 42 merged as 84de2ed; its run of record is reference only)
**Status:** in-progress
**Working in:** chat on Thinkbook16 (2026-10-30)
**Branch:** 43-derive-the-growth-angle-from-the-sherds-own-curvature, in /c/PR/worktrees/sfs/43

## The question

The growth accepts a neighbour only within `thetaDeg` of the front point's normal (mesh_processing_headless.cpp:3191; env SFS_PAPER_THETA at :4574, default 3.4). Tickets 29/30/32 established the neighbour turn tracks curvature (Pearson 0.941; turn per step ~ spacing / fold radius; Pot A ~21 mm radius -> ~1.2 deg, Juglet 0.67-5.25 mm -> 8-16 deg). Ticket 30 proved one global constant fitted on the pot cannot transfer (c=5.698 -> 28-103 deg, one cluster everywhere). Ticket 42 proved by outcome that a larger theta separates Juglet pieces 2-8 into genuine wall pairs (ladder chose 10.2 everywhere; the growth still refused the broken edge), so on those sherds within-face turns lie below 10.2 and edge turns above it.

Open: per sherd, WHERE does the gap sit, and does theta derived from each sherd's own within-face turn distribution land inside the gap without any outcome search?

## Part A — the two distributions, per sherd, labelled from the mesh

For Juglet pieces 1-9 and Pot A pieces 01-08, on the REAL released clouds at the pipeline's own adaptive spacing (today's default):

- Sample the sherd mesh analytically (stage42 instrument mesh38) at the spacing the pipeline resolves ([SPACING-22] S), each sample carrying its source triangle's face normal.
- For every sample pair within the pipeline's neighbourhood criterion, compute the turn angle between the two face normals.
- Label a pair WITHIN-FACE if the two source-triangle normals differ by less than 45 deg, ACROSS-FOLD otherwise. Report per sherd: n pairs, within-face p50/p90/p99, across-fold p10/p50, and the margin (across-fold p10 minus within-face p99).
- Mark on each distribution: the shipped 3.4, ticket 42's ladder-chosen theta (10.2 Juglet, 6.8 on PA01/03/07/08), the sherd's spacing and median fold radius (ticket 32 instrument).

## Part B — the derived rule

Two candidate rules, printed per sherd:

- R1: theta = k x within-face p90, with k fixed so Pot A's median lands at its known-good 3.4.
- R2: theta = geometric mean of within-face p90 and across-fold p10 (mid-gap by construction).

Report whether R1 and R2 land inside the measured margin, per sherd. A sherd where they do not is named, not hidden.

## Part C — the pipeline test

One cell per piece, arms: A today (no env overrides) / B SFS_PAPER_THETA set per sherd to R1's value / C same for R2. NO source change is needed - SFS_PAPER_THETA already exists. Pieces: Juglet 1-9, Pot A 01-08 (48 cells). Measure with the corrected signed-t pair statistic (stage42 instruments measure34.py pair_stats): med_along, med_across, coincidence, and per-surface points / diagonal / 2 mm coverage / fold-to-mesh.

Reference numbers (ticket 42 run of record 33989453): Juglet armB genuine pairs J2 1.88/0.67, J3 1.77/0.51, J4 2.14/0.45, J5 2.46/0.42, J6 2.28/0.48, J7 2.52/0.52, J8 1.86/0.38; J9 borderline 0.79/2.42; J1 armA genuine 1.82/0.53; Pot A armA clean 8/8 at 3.55-7.09 along / 0.13-0.27 across / coincidence 0. Wall thicknesses (ticket 35): J2 2.693, J3 2.452, J5 2.900, J7 3.263, J9 2.595, PA07 4.056 mm.

## Constraints

- No tracked pipeline change: instruments and tables under .scratch/juglet-breaklines/stage43/ only. If Part C seems to need a source edit, stop and report.
- Compute nodes only; at most 3 grid jobs plus at most 2 dead submissions; split by vessel, never by part.
- Corpus and canonical checkout read-only, md5 before/after; /opt/sfs-pristine absent is recorded, not created.
- CRLF-check every script before submit (two grids died on 'set: pipefail: invalid option name'); grep -a for binary PLY headers; no xargs -d.
- Geometry deleted with a counted record written BEFORE the delete; surfaces, logs and tables kept for the lead.
- Append index rows with 6 fields, verdict and human_note EMPTY.

## Evidence to return

1. Part A table (one row per sherd: the two distributions and the margin) plus one figure with the distributions per sherd, 3.4 and the ladder theta marked.
2. Part B table: R1 and R2 per sherd, inside-gap yes/no, the k R1 implies.
3. Part C cell table and signed-t pair table, 48 cells.
4. Pot A control outcome per arm, stated even if it regresses.
5. Defaults-unchanged proof: arm A SampledWithNormals md5 identical to a no-env rerun on 4 pieces.
6. Corpus/inputs md5 before/after; geometry deletion record.
7. Index rows appended with empty verdict.

Report numbers and paths, not verdicts.
