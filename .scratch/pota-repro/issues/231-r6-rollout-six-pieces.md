Status: ready-for-agent

## Goal
Uniform R6 leg table across all six 214-MIXED pieces (user order m03823): every piece's decisive faces scored under the frozen legs (balance 2nd/1st >= 0.5, gap-clean >= 2mm symmetric min, UN share <= 12%, loosest-first), filling the one real gap -- P25's fresh-default faces, which produced its 85.9/91.2 near-miss lanes but were never leg-scored (the ladder tested only its own angles). Ends at a table + verdict; changes nothing.

## Boundary
- Spartan READ-ONLY first: reuse ladder logs/faces (pota221_ladder/thr_*, sfs-potD-216/score, 227 cites) for P12@4.5 / P15@8 / P16@10 / P01@8 / P22-all-stops / P25-ladder-stops / P27@12 -- compile, do not re-segment. P25 fresh-default faces: locate the 214 pipe faces (pota214_pipe/Dataset/... surfaces or equivalent); if present, score the three legs on them; if absent, report ABSENT with the searched paths -- do NOT re-run segmentation without a lead go-ahead.
- Trace NO new lanes; run NO edge jobs; change NO thresholds. If any leg value on record fails to reproduce from the saved faces/logs, report REPRO-DIVERGENCE with both numbers instead of overwriting.
- MAY touch: fresh dir C:/PR/SfSpp_preprocessing/.scratch/pota231/ (table csv + notes) + this ticket's Comments. MUST NOT touch: other tickets, bundles, sources, binaries, bar, rules.

## Constraints
- Loosest-first reading throughout: a piece's row is its FIRST all-three-pass stop (or NONE with the blocking leg named per stop).
- P22 expectation: NONE (bridged everywhere) -- confirm, not re-litigate. P27 row: @12 passes legs + lane story pointer (229 OURS-AT-EDGE + 230 rescore state at time of writing).
- Slots per 209 pattern in any lane citation; lane numbers are context only (this ticket scores FACES, not lanes).

## Acceptance (lead judges; numbers + cites + paths)
- Six-row table: piece | decisive stop (or NONE) | bal | gap | UN | blocking leg if NONE | lane state (bar / near-miss + numbers / fail) | face/log provenance path.
- P25 fresh-default row filled (legs + provenance) or ABSENT with searched paths.
- Verdict: TABLE-COMPLETE (all six rows filled from verified faces/logs) / PARTIAL (name the missing cell + what it needs) / REPRO-DIVERGENCE (name it). One line per piece on whether the legs and the lanes agree.

## Required evidence to report
- Bottom line first (verdict + the P25 fresh-default legs or ABSENT). Then the table, provenance paths, any divergence numbers. No new runs to report (or the single proposed run if faces are absent).
