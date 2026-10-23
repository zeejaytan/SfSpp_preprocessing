# Ticket 262: move the 247 vote-order arm toward the P03-Bl1 bar via one order-of-visit repair (gated K-D + 2-opt)

**What to build:** diagnose WHY the vote still scribbles on the S0-cleaned loop (3 chord jumps remain) across strand-selection scoring vs ballot weighting vs order-of-visit, then fix ONE mechanism (order-of-visit 2-opt chord repair) in the edge stage, keeping VOTE+GATED engaged. Ends at re-extract + score; no assembly; nothing committed to main.

**Answers:** E1

**Blocked by:** Tickets 247 (vote arm SPLIT) + 248 (KDF filter) + 261 (gated K-D filter; vote261 gate is the base).

**Status:** results-in
**Working in:** subagent session-262 (2026-10-23)

- [x] Diagnose 3-jump blocker across the three mechanisms with numbers (strand L/turnSum/corners vs ballot stability vs angular-sort chords)
- [x] Order-of-visit fix ported in edge stage ONLY (2-opt chord repair behind SFS_VOTE_REPAIR, greedy intact, default OFF)
- [x] P03-Bl1 exam at bar via vote+gated-KD+repair lane (med<2, cov>=90, zero jumps>10mm, walk order verified one loop) OR honest negative nailing the blocking mechanism — HONEST NEGATIVE (see verdict)
- [x] Guards hold (P03-Bl0 >=97% cov, P01 both == VOTE class, P22 intact-or-better, no segfault) else STOP + report
- [x] Replication gate passes in the same job (CTL/VOTE numbers == 247b/261 to the decimal) before any new claim
- [x] Evidence in ticket Comments + Status results-in; diffs left uncommitted (no main commit); overlay PNGs with NEW distinct colour; per-lane scores table; job IDs + sacct

## Boundary

- Reuse 248 worktree C:/PR/SfSpp_preprocessing-248 (detached @4887348; edge file identical to main HEAD b0fff04 for edgeline_extraction_headless.cpp, verified via git log 4887348..HEAD -- edge file empty; not stale, so no fresh worktree). Edge stage ONLY (edgeline_extraction_headless.cpp vote fn + call site). Mesh/splitter/classify/assembly untouched.
- Spartan reuse /data/gpfs/projects/punim2657/sfs-vote-248 (detached @4887348, origin repointed to github; left untouched per 239-245 precedent after verifying edge file has no upstream change). Main worktree touched ONLY by this ticket file.
- Main pipeline untouched. No assembly.

## Constraints

- Spartan: git pull --ff-only first, STOP on divergence; same node class (sapphire/bm15x) for md5 comparisons; source-changing build => rebuild + verify md5.
- MSYS2_ARG_CONV_EXCL='*' on laptop ops.
- Replication gate (CTL/VOTE numbers == 247b/261 to the decimal) before any new claim.
- Judgement stays with lead — stage evidence and STOP.

## Diagnosis (pre-build, from 261 evidence)

- Input bag P03-Bl1 n=1121 rim pts. VOTE raw: comp kept 1045/1121 (2 comps), chain 1045, turnSum 44.8, L 8694mm (17x clean 499mm), resampled 4576. Braid confirmed.
- GATED S0 path: ROR kept 1082/1121 (only 39 removed — ROR is NOT the cutter), comp split 2->5 comps, largest kept 433/1082 (40%), chain 433, turnSum 13.08 (vs clean Bl0 8.97, vs ideal 2pi 6.28 — ~2x), L 927mm (vs clean 499mm — 1.86x), corners 16 vs clean 4. Largest comp still double-cover: strand-selection scoring (largest != loop) is the upstream suspect.
- Ballot RULED OUT as blocker: turnSum sign stable CCW-kept on clean (8.97) and braid (44.8 raw, 13.08 filtered); ballot only reverses direction, preserves adjacencies so cannot create/remove 3 jumps. Verified in logs.
- Order-of-visit suspect: overlay P03_Bl1.png shows KDF green as coherent loop with 3 long chord shortcuts (X-Y waist chord, X-Z diagonal, Y-Z vertical) — classic angular-sort radial misorder on concave/tilted loop. Resample preserves loop order, so chords in final trace to long edges in angular loop[]. A closed-loop 2-opt (uncrossing always shortens L) repairs exactly this without changing population/ballot/resample. Test FIRST (smallest change, directly targets jumps>10mm). If L stays ~900mm and cov stays <90 after repair, strand-selection is nailed as blocker (honest negative path).

## Fix (one mechanism: order-of-visit)

- SFS_VOTE_REPAIR=1 enables closed-loop 2-opt best-improvement (<=20 passes) on loop[] AFTER ballot reversal and BEFORE arc-length resample. Reverses segment bi+1..bj when (cc-aa)+(dd-bb) < (bb-aa)+(dd-cc). Logs [VOTE-262] repairs + L/max before->after. Behind env ONLY; CTL/VOTE/GATED with REPAIR=0 replicate 261 exactly.
- Untouched: ROR(2.5/6)+FALLBACK, COMP_GAP 5.0 largest (SFS_COMP_KEEP), PCA-plane angular sort, turn-sign vote, resample d=1.9, corner logging, KD-GATE recursion (repair flag preserved through recursion; clean lanes see 0 repairs so BYPASS decision unchanged).

## Required evidence to report

Per-lane scores table (CTL/VOTE/KDF-gated/NEW med/cov/jumps); diff summary; job IDs + sacct State/ExitCode; binary/edge md5s; overlay PNGs (author black, CTL blue #0072B2, VOTE vermillion #D55E00, NEW purple #9467BD distinct + KDF green retained for reference where free); walk-order verification (consecutive gaps, one loop); self-contained completion message. Judgement stays with lead: stage evidence and STOP.

## Comments (worker, 2026-10-23 — job 33699272 gated+repair scored; raw-repair job 33699581 submitted)

Lead steer (2026-10-23): raw-braid vote fix first, no K-D in the loop; 261 gate is a bridge workaround to drop if raw vote turns clean. ACKed to parent. Current job tests GATED+REPAIR (fallback); raw-repair (VOTE_ORDER=1/KDF=0/GATE=0/REPAIR=1) follows in job 33699581 with the same binary.

Build 33698873 COMPLETED 0:0 (bm138). Edge cpp md5 78fb274df99f6b3e557133961ce58f44; binary md5 9d215d1cf30483462d017d2dcdf4f141. HEAD-pin 4887348 verified; REPAIR+GATE markers present. Spartan fetch showed origin/main a23159e..b0fff04 (ticket 261 file only, no edge change) — no divergence in edge stage, detached left untouched per 239-245 precedent.

Run 33699272 COMPLETED 0:0 in 6:21 (bm138, 12 lanes P03/P22/P01 x CTL/VOTE/GATED/NEW). Replication PASSES to the decimal in the same job: CTL P03 0.72/97.8 + 0.98/52.8/1j, P22 0.80/86.0 + 0.50/91.1/1j, P01 0.75/98.8 + 1.01/94.2; VOTE P03 0.58/100 + 8.69/11.0/21j, P22 4.79/14.4/38j + 4.43/15.8/17j, P01 0.72/98.8 + 0.93/95.7; GATED P03-Bl0 0.58/100 BYPASS, Bl1 0.99/78.2/3j, P22 4.87/14.7/37j + 2.40/41.8/2j, P01 ==VOTE. No EDGE-EXIT (no segfault).

Per-lane NEW (GATED+REPAIR) med/cov<2mm/jumps>10mm: P03-Bl0 0.82/100.0/0j n=216 (vs VOTE 0.58/100 n=228 — repair fired on clean lane, see below); P03-Bl1 EXAM 0.76/61.5/1j maxjump 11.3 n=208 (vs GATED 0.99/78.2/3j maxjump 137.9 n=403 — jumps 3->1 and med better, but coverage 78->61 FAIL); P22-Bl0 4.57/17.7/29j; P22-Bl1 0.75/76.4/0j n=106 (vs GATED 2.40/41.8/2j — bonus improvement, still <90); P01-Bl0 0.59/99.1, Bl1 1.01/96.2 (==VOTE class, no segfault). Guards: P03-Bl0 cov 100 holds; P01 holds; P22 intact-or-better (Bl1 better, Bl0 ~same); no segfault.

Repair logs (edge262_NEW.log): P03-Bl0 clean 2opt repairs=20 (CAPPED) L 499.4->431.1 max 8.5->2.0 resampled 227 — clean lane NOT untouched, angular order not L-optimal; P03-Bl1 pre-filter raw 2opt repairs=20 (CAPPED) L 8695->5408 max 96->80 corners 118->92 (still scribble, gate still BRAID); P03-Bl1 filtered 2opt repairs=20 (CAPPED) L 927.9->483.7 max 122->122 (longest chord UNFIXABLE by uncrossing) resampled 255 corners 16->8; P22 lanes all repairs=20 capped, max unchanged 30.7->30.7. Ballot stable (CCW-kept everywhere) — ballot ruled out. TurnSum unchanged by repair (vote before repair): clean 8.97, braid raw 44.8, filtered 13.08.

Overlay viewed: C:/PR/SfSpp_preprocessing-248/artifacts/pota262_P03_Bl1.png (Spartan overlays262/P03_Bl1.png, 5 series + NEW purple) — purple follows top lobe then shortcuts the bottom-right lobe (1 chord) where green completes more of the loop (3 chords); matches numbers (coverage for jumps trade). P03_Bl0 + P22_Bl1 PNGs alongside.

Interim mechanism verdict: order-of-visit 2-opt contributes (jumps 3->1, maxjump 138->11, L halved to single-cover length 484~=499) but length-minimization is the WRONG objective on a double-cover point set — minimal tour cuts the lobe instead of completing it (cov 78->61). Blocking mechanism nailed as strand-selection scoring (largest-comp 433/1082 still double-cover: L 928 vs 499, turnSum 13.1 vs 2pi, corners 16 vs 4); no reorder of the mixed set reaches cov>=90. Raw-repair attempt pending in job 33699581 (same binary, pota262b trees, CTL/VOTE/GATED/RAWREPAIR) — will score and overlay the exam on arrival, then set Status results-in and deliver the gate recommendation (drop vs keep) with numbers.

## Comments (worker, 2026-10-23 — FINAL: honest negative, both repair arms scored, overlays viewed)

Raw-repair job 33699581 COMPLETED 0:0 in 6:12 (bm057, 12 lanes pota262b P03/P22/P01 x CTL/VOTE/GATED/RAWREPAIR, same binary 9d215d1cf30483462d017d2dcdf4f141). Replication PASSES again in the same job: CTL P03 0.72/97.8 + 0.98/52.8/1j, P22 0.80/86.0 + 0.50/91.1/1j, P01 0.75/98.8 + 1.01/94.2; VOTE P03 0.58/100 + 8.69/11.0/21j, P22 4.79/14.4/38j + 4.43/15.8/17j, P01 0.72/98.8 + 0.93/95.7; GATED P03-Bl0 0.58/100, Bl1 0.99/78.2/3j maxjump 137.9, P22 4.87/14.7/37j + 2.40/41.8/2j, P01 ==VOTE. (Superseded: 33698899 FAILED 1:0 in 1s and 33699532 FAILED 1:0 in 1s, both run-script PIECE_ unbound-variable under set -u before any lane — fixed to braced form, no lanes affected.)

Per-lane RAWREPAIR (VOTE_ORDER=1/KDF=0/GATE=0/REPAIR=1) med/cov<2mm/jumps>10mm: P03-Bl0 0.82/100.0/0j n=216 (same as NEW clean lane); P03-Bl1 EXAM 5.96/18.8/16j maxjump 135.6 n=2635 (vs VOTE 8.69/11.0/21j — modest improvement, NOWHERE near bar); P22-Bl0 4.55/15.9/32j; P22-Bl1 4.20/18.7/9j (vs VOTE 4.43/15.8/17j — jumps halved, still failing); P01-Bl0 0.59/99.1, Bl1 1.01/96.2 (==VOTE class). Guards for the candidate arms: P03-Bl0 cov 100 holds in both jobs; P01 holds; P22 intact-or-better-or-same (NEW Bl1 much better, RAWREPAIR Bl1 slightly better, Bl0 about same); no EDGE-EXIT anywhere (no segfault). Walk order verified via consecutive-gap jumps in emitted order (scorer) + resampled one-loop counts (227-2847) + overlays viewed (see below).

RAWREPAIR logs (edge262b_RAWREPAIR.log): P03-Bl0 2opt repairs=20 CAPPED L 499.4->431.1 max 8.5->2.0 resampled 227; P03-Bl1 raw 2opt repairs=20 CAPPED L 8695->5408 max 96->80 corners 118->92 resampled 2847 (still 10x clean length, still scribble). Combined with job-1 logs (filtered 2opt 20 CAPPED L 928->484 max 122->122 UNCHANGED resampled 255), the 20-pass cap binds on EVERY lane and the longest chord is structurally unfixable by uncrossing.

Overlays viewed (author black / CTL blue #0072B2 / VOTE vermillion #D55E00 / GATED green #009E73 / candidate purple #9467BD): C:/PR/SfSpp_preprocessing-248/artifacts/pota262_P03_Bl1.png (job-1 NEW: purple top lobe + 1 shortcut chord cutting the bottom-right lobe vs green fuller 3-chord loop — matches cov-for-jumps trade); C:/PR/SfSpp_preprocessing-248/artifacts/pota262b_P03_Bl1.png (job-2 RAWREPAIR: purple still a scribble, 16 jumps, slightly thinner than vermillion — matches numbers); P03_Bl0 + P22_Bl1 PNGs alongside in both overlay dirs (Spartan sfs-vote-248/overlays262 + overlays262b, all 6 pieces each). No similar colours for different things; equal aspect.

Diff summary (edge stage ONLY, greedy intact, defaults OFF): Spartan + laptop-248 worktrees carry +283/-1 vs 4887348 in edgeline_extraction_headless.cpp (= 254-line 247-vote + 261-gate base and 29-line POTA-262 2-opt block after ballot reversal, before resample; SFS_VOTE_REPAIR-gated, zero impact when 0). Untracked scripts alongside (build262/run262/run262b/stats262/stats262b/overlay262/overlay262b, vote261-retune.diff, LF copy). Nothing committed to main; main worktree touched ONLY by this ticket file.

VERDICT: HONEST NEGATIVE — exam bar NOT met by order-of-visit repair on either population (gated+repair 0.76/61.5/1j; raw+repair 5.96/18.8/16j vs bar med<2/cov>=90/zero jumps). Blocking mechanism nailed as STRAND-SELECTION SCORING: ROR removes only 39/1121 (not the cutter); largest-comp 433/1082 is still double-cover (L 928 vs clean 499, turnSum 13.1 vs 2pi 6.28, corners 16 vs 4); 2-opt halves L to 484 (~= clean length, proving a single-cover subset exists) yet covers only 61% — the minimal tour cuts the lobe instead of completing it, and on raw braid 20 capped passes still leave L 5408 (10x). Ballot ruled out (CCW-kept on all 24 lanes; flip preserves adjacencies). Gate recommendation EXPLICIT per lead steer: DO NOT drop the 261 gate — raw vote proved unfixable by reorder after a real 20-pass mechanism attempt, so the gate (S0: 0.99/78.2/3j) remains the best bridge, still below bar; do NOT land 2-opt (hurts the gated cure 78.2->61.5 and perturbs clean lanes 0.58->0.82). Next ticket should score comps by loop-ness (|turnSum-2pi| + L/n + corners, keep best not largest) with REPAIR=0, then optionally re-apply order repair. Judgement with lead: evidence staged, STOPPING — no main commit, no further work.
