Status: done

## Lead verdict (2026-10-21)
TABLE-COMPLETE accepted + P25 slot correction. R6: r6_table.csv on disk (6 rows, zero divergence claimed -- spot values match 227 record); 231 Comments verified; only this ticket touched among tracked. AMENDMENT to worker's P25 row: the '85.9/91.2 appears nowhere' challenge is resolved BOTH-WAYS -- straight slots on the fetched 214 pipe lanes give 7.07/0.0 + 6.96/0.0 (== gate_table.csv EXACT), matched slots give 0.81/85.9 + 0.79/91.2 (lead p25_slots.py). The gate_table recorded the straight-slot misread; P25 fresh lanes are SWAPPED + near-miss (Pot A P02-P08 analogue). P25 legs-vs-lanes: DISAGREE (faces UN 39.52% FAIL, lanes near-miss when slot-corrected) -- milder P27, not bridge. P22 stands: NONE + stub lanes. Net per-piece: P15/P16 solved, P12 answered, P25 swapped-near-miss, P27 sharpness-story, P22 bridge.

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
## Comments (worker 2026-10-21 — run once, Spartan READ-ONLY, nothing committed)

### Verdict: TABLE-COMPLETE

All six rows filled from verified faces/logs. Zero repro-divergence on any leg.
Fresh dir: `.scratch/pota231/` (`r6_table.csv` + `notes.md`). Touch log: those
two new files + this Comments section only.

### Six-row table (R6 = loosest 90->4.5 stop with bal>=0.5 AND gap>=2mm AND UN<=12%)

| piece | R6 stop | bal | gap (mm) | UN | lane state | legs-vs-lanes |
|---|---|---|---|---|---|---|
| P12 | @4.5 | .955 (15887/15176) | 5.2629 | 9.78% (4859/49702) | near-miss 0.63/89.0 + 0.77/98.8 (227) | legs pass, Bl0 cov 1pp short — complicate |
| P15 | @8 | .737 (17639/12993) | 5.2864 | 5.02% (1934/38542) | GOOD 0.43/97.2 + 0.75/97.6 (227) | agree |
| P16 | @10 | .883 (11663/10302) | 5.8879 | 6.07% (1805/29719) | GOOD 0.61/97.2 + 0.49/100 (227) | agree |
| P22 | NONE | best @14 .960 | @14/@12 0.00; @10 0.68; @8 0.00; @4.5 0.17 | @14 4.67%; @12 7.49%; @10 72.7%; @8 34.3%; @4.5 29.4% | fresh-default Bl1 0.77/89.7 near-miss (216/score); no legal stop | complicate (good lane, no passing stop) |
| P25 | NONE | fresh .805; ladder best .94 (@10/@8) | fresh 4.2766; ladder @10/@8 0.68, @4.5 0.79 | fresh 39.52% FAIL; ladder @10 9.59% ok, @8 12.51%, @4.5 18.96%, @12 hole | 214 slid 7.07/0.0 + 6.96/0.0; ticket premise 85.9/91.2 NOT in repo record (flagged) | agree vs recorded scores (both bad); premise unverified |
| P27 | @12 | .855 (2591/2216) | 2.7538 | 8.89% (753/8470) | BAD 0.83/58.5 + 0.91/68.9 (229 OURS-AT-EDGE; 230 new==old) | disagree, explained downstream |
| P01 (control, not a row) | @8 | .887 (60469/68197) | 4.9637 | 3.38% (5043/149013) | GOOD (227) | gate passes |

P25 fresh-default gate: PRESENT faces
(`pota214_pipe/Dataset/Surfaces/Pot_D/Pot_D_Piece_25_Surface_{0,1}.xyz`,
md5-identical to Temp/Data copies 7143065f/93a27ecd), bal 2342/2911=.8046 PASS,
gap 4.2766 PASS (computed this ticket, 225/226-pattern algorithm, P25@4.5-ladder
control 0.7906 EXACT), UN 4419/11182=39.52% FAIL -> gate FAIL. Not ABSENT.

P22 blockers per stop: @14/@12 gap 0.00 FAIL (bal+UN pass); @10 gap 0.68 + UN
72.7% FAIL; @8 gap 0.00 + UN 34.3% FAIL; @4.5 gap 0.17 + UN 29.4% FAIL.
P25 ladder blockers: @16/@14 bal .116 FAIL; @12 zero-cluster hole (ncl=0);
@10 gap 0.68 FAIL (UN 9.59% passes); @8 gap 0.68 + UN 12.51% FAIL;
@4.5 gap 0.79 + UN 18.96% FAIL.

### Reproduction statement

Every 227 STEP2 leg number reproduced EXACT from primary sources (log cluster
parses, "element vertex" UN headers with clusters+UN=cloud EXACT for all seven
pieces, saved 222/225/226 gap outputs). No REPRO-DIVERGENCE.
Lane numbers cited from 227 (lead local rescore) + 214 gate_table.csv +
216/score before-columns + 229/230; no lane rescoring done here per Boundary.

### One open item for the lead (changes no R6 cell)

Ticket Goal premise "P25 fresh-default 85.9/91.2 near-miss lanes" appears
NOWHERE in .scratch + artifacts (searched 85.9 / 91.2 / 91.20; only hit is
unrelated 147-parity). Repo record says P25 fresh = slid (7.07/0.0 + 6.96/0.0).
If 85.9/91.2 came from the live session, source it into the record; until then
the P25 lane state stands as slid.



**Evidence-path note (2026-10-23):** paths under .scratch/pota1xx_repro/ and .scratch/pota22x/ cited above were removed by the scratch cleanup of this date (untracked intermediates; not recoverable). The numbers, quotes and verdicts in this ticket stand as recorded -- do not chase those paths or re-derive from them.
