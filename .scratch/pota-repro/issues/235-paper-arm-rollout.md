Status: done
Answers: E1

# Ticket 235: paper-arm rollout to the remaining problem pieces

## Goal
Run the landed paper-arm binary (mesh v3 d72979aa, build 33616944 -- rebuild from the branch if it has moved on, same-source check first) on P15, P25, P27 (untested on the paper arm) plus P16 and P01 as regression controls (both at bar on the old chain).

## Boundary
- Spartan only, fresh experiment copy (do NOT touch sfs-fix-234 or the branch worktree).
- Read-only on tickets 234/214/215/228/229; edit only this ticket (append Comments, Status results-in).
- No commits, no pushes.

## Constraints
- Same exam protocol as 234: gap table + post-merge cluster sizes + merges fired + classify votes + slot-verified lanes vs author (bar med<2 + cov>=90).
- P16 control must reproduce its cure (Bl0 0.56/97.4-era numbers at bar); P01 must stay at bar. If either regresses, STOP and report -- do not retune.
- Watch items from 234: P22-style edge pinch near forks (measure and locate any symmin < 1mm); Jug-style resample dupes (count exact-dupe filed points per piece).

## Acceptance
Per-piece table (P15/P25/P27/P16/P01): post-merge top2 share, merges fired + which clusters, classify vote, both lane scores straight+matched, pinch/dupe watch numbers. Verdict line per piece: AT-BAR / NEAR-MISS / FAIL + whether the piece is resolved. sacct COMPLETED for every job; binaries md5 cited.

## Lead regrade (2026-10-22, user correction m04205)
P27 is a WIN, not a disease. 229 proved OURS-AT-EDGE (disputed 27 dots: ours 39.2deg vs author 1.4deg against the sharpness baseline); 230 kept the author-ruler score on record with the blindness noted. The 58-69% vs author measures the ruler, not the lane. P27 counts as resolved (true-edge win); the author-ruler number stays as evidence of where the author runs off-edge. The 4th-leg work (228 line) is therefore not 'fix P27's lanes' but 'tell true-edge-wins from real wanders author-free'.

## Lead verdict (2026-10-22)
ACCEPT: 5/7 resolved (P22/P12/P15/P25 + P16 control reproduces cure, P01 holds), P27 near-miss = known wandering-lane limitation (fits 229/230 ruler caveat). R6: 6/6 jobs sacct COMPLETED 0:0; binary byte-identical to 234 evidence binary (same-source check); lane numbers read verbatim; slots STRAIGHT + votes clean on all five (swap cured everywhere); merges only non-face tails; dupes 0. UN-share measurement note recorded (PLY headers, info-only). Merge decision put to user as numbered options.

## Required evidence to report
Job IDs + sacct states; binary md5s; the per-piece table with the numbers, not adjectives; verdict in ticket Comments; Status results-in; self-contained completion message to the parent.

## Comments (worker, 2026-10-22 -- paper-arm rollout v3-rebuild)

Binaries and jobs (all sacct COMPLETED 0:0). Mesh rebuilt from paper-split-chain @7035611 (source md5 556ef97aacedddadd4df283ccff01d15 = v3 record EXACT; same-source check: no main-side mesh changes since base f76797f, rebuild-only): binary md5 d72979aaa0055885a4dc88bb51a172e7 = build-33616944 binary BYTE-IDENTICAL. Fresh Spartan copy sfs-fix-235 (local clone plus fetch origin paper-split-chain, clean tree); pota234 trees untouched. Edge bin reused dc472b0e87c934b6c487ff8637209864. Build 33617723 (54s). Runs: 33617876 P15 (12s), 33617877 P25 (11s), 33617878 P27 (14s), 33617879 P16 (12s), 33617880 P01 (20s). Operating point = 234 v3 verbatim (grow min-curv seed, nb=10, theta=4, kappa=1; Appendix-A merge; axis-ray classify, S0=interior).

Per-piece table (Pot D; slots slot-verified, bar med<2 and cov>=90; gap on filed faces; top2 of clustered, 234 definition).

P15: grow 7 to 7 (8877/6572/721/652/570/330/72), top2 15449/17794 = 86.8%, merges none, classify 0.0/100.0 satB 15449 swapped, lanes Bl0-o0 0.68/98.4 Bl1-o1 0.54/99.3 max 4.8/3.8 0 jumps STRAIGHT, gap 6.634/6.83/0pct, dupes 0.

P25: grow 8 to 8 (5307/4907/1295/958/914/73/56/53), top2 10214/13563 = 75.3%, merges none, classify 0.0/100.0 satB 10214 swapped, lanes Bl0-o0 0.45/96.3 Bl1-o1 0.46/96.2 max 5.5/4.2 0 jumps STRAIGHT, gap 0.881/2.55/0.59pct, pinch 0.88mm at [5.64,37.72,463.57], dupes 0.

P27: grow 8 to 7 (6478/5607/2197/1768/2156/522/196), top2 12085/18924 = 63.9%, one merge 1046 into 2156 both non-face, classify 0.0/100.0 satB 12085 swapped, lanes Bl0-o0 0.89/71.4 Bl1-o1 0.91/57.1 max 9.9/17.2 0 jumps STRAIGHT, gap 2.997/3.90/0pct, no pinch, dupes 0.

P16 control: grow 9 to 7 (5760/5114/761/622/627/159/77), top2 10874/13120 = 82.9%, two merges 197 into 627 and 53 into 159 all non-face tail, classify 0.0/100.0 satB 10874 swapped, lanes Bl0-o0 0.46/97.1 Bl1-o1 0.45/99.3 max 6.7/2.1 0 jumps STRAIGHT, gap 5.861/6.17/0pct, dupes 0.

P01 control: grow 8 to 8 (8941/7983/129/106/81/70/66/58), top2 16924/17434 = 97.1%, merges none, classify 0.0/100.0 satB 16924 swapped, lanes Bl0-o0 0.75/98.8 Bl1-o1 1.01/94.2 max 2.7/2.9 0 jumps STRAIGHT, gap 5.747/6.03/0pct, dupes 0.

UN info-only (234 policy; eval234.py reads 0 pts from PLY so counts from vertex headers): P15 2511 (12.4pct), P25 2845 (17.3pct), P27 3561 (15.8pct), P16 2459 (15.8pct), P01 3691 (17.5pct).

Control gate: PASS, no STOP. P16 Bl0 0.46/97.1 reproduces the cure (0.56/97.4) at bar; P01 both lanes at bar (0.75/98.8, 1.01/94.2 vs gate 0.48/99.7 and 0.66/96.3). Bonus: P16 Bl1 0.45/99.3 beats the 215 honest-negative (0.62/78.7) -- the paper re-split recovers the corner arcs. All five pieces slot STRAIGHT -- swap disease cured everywhere including P25 (231 recorded its old-chain lanes SWAPPED near-miss).

Verdicts. P15: AT-BAR / resolved. P25: AT-BAR / resolved (0.88mm pinch watch carried, assembly-side). P27: NEAR-MISS / unresolved-known-limitation (meds sub-mm, cov 71.4/57.1; matches the 229/230 ruler caveat, weakest top2 63.9pct reported honestly). P16: AT-BAR / resolved. P01: AT-BAR / resolved.

Notable negatives. Zero exact-dupe filed points on all five (no Jug-style resample artifact). Merge fired only on P27/P16 tails, never on faces. No break swallowed: votes clean 0/100 all five; gaps open except the P25 local pinch; lane coverage 94-99pct on the four at-bar pieces.
