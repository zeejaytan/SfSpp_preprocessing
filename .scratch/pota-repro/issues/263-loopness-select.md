# Ticket 263: fix strand SELECTION in the 247 vote arm — score connected components by loop-ness and keep the best, not the largest

**What to build:** among the post-ROR connected components, keep the one that looks most like a single closed loop instead of the one with the most points. Candidate loop-ness score per comp (one knob at a time): e.g. turnSum closeness to 2pi combined with length-vs-bounding-scale, corner count, or self-crossing count from the PCA-plane angular order — pick the comp minimizing loop deviation, then run the existing vote walk on it with REPAIR=0.

**Answers:** E1

**Blocked by:** Tickets 247 (vote arm SPLIT) + 248 (KDF filter) + 261 (gated K-D filter) + 262 (2-opt honest negative; strand-selection nailed as blocker).

**Status:** results-in
**Working in:** subagent session-263 (2026-10-23)

- [ ] Loop-ness comp selection ported in edge stage ONLY (env-gated, greedy intact, default OFF; REPAIR=0 on the NEW lane)
- [ ] P03-Bl1 exam at bar via vote+loopness lane with REPAIR=0 (med<2, cov>=90, zero jumps>10mm, walk order verified one loop) OR honest negative nailing why loop-ness can't separate the strand
- [ ] Guards hold (P03-Bl0 >=97% cov, P01 both == VOTE class, P22 intact-or-better, no segfault)
- [ ] Replication gate passes in the same job (CTL/VOTE/GATED numbers == 247b/261 to the decimal)
- [ ] Evidence in ticket Comments + Status results-in; per-lane scores table (CTL/VOTE/GATED/NEW); comp-level diagnostics table for P03-Bl1 (per-comp n, L, turnSum, corners, loop-ness score, kept/dropped); diff summary; job IDs + sacct; overlay PNGs (author black, CTL blue, VOTE vermillion, GATED green, NEW distinct)

## Boundary

- Edge stage ONLY. Reuse 248 worktree C:/PR/SfSpp_preprocessing-248 (detached @4887348; edge file identical to main HEAD — verified via git log 4887348..HEAD -- edgeline_extraction_headless.cpp empty in both 248 worktree and main) + Spartan sfs-vote-248 (detached @4887348, origin repointed to github; fetch shows origin/main e32cf9c = ticket-262 file only, edge diff empty — left untouched per 239-245 precedent).
- NEVER touch main worktree except this ticket file. Main pipeline untouched. No assembly.

## Constraints

- Spartan git pull --ff-only + STOP on divergence (fetch-verified: edge diff empty, detached left untouched per precedent); same node class for md5 comparisons (sapphire/bm15x); source-changing build => rebuild + verify md5.
- MSYS2_ARG_CONV_EXCL='*' on laptop ops.
- Replication gate (CTL/VOTE/GATED numbers == 247b/261 to the decimal) in the SAME job before any new claim.
- Judgement stays with lead — stage evidence and STOP. Do NOT land or gate anything; one mechanism, honest negative acceptable.

## Diagnosis (pre-build, from 262 evidence)

- Input bag P03-Bl1 n=1121 rim pts. VOTE raw: comp kept 1045/1121 (2 comps), chain 1045, turnSum 44.8, L 8694mm (17x clean 499mm), resampled 4576. Braid confirmed.
- GATED S0 path: ROR kept 1082/1121 (only 39 removed — ROR is NOT the cutter), comp split 2->5 comps, largest kept 433/1082 (40%), chain 433, turnSum 13.08 (vs clean Bl0 8.97, vs ideal 2pi 6.28 — ~2x), L 927mm (vs clean 499mm — 1.86x), corners 16 vs clean 4. Largest comp still double-cover: strand-selection scoring (largest != loop) is the upstream suspect.
- Ballot RULED OUT (turnSign stable CCW-kept everywhere; flip preserves adjacencies). 2-opt RULED OUT by 262 (gated+repair 0.76/61.5/1j — jumps 3->1 but cov 78->61; raw+repair 5.96/18.8/16j; longest chord unfixable by uncrossing; 20-pass cap binds everywhere).

## Design (one knob: equal-weight turn + length-vs-scale; corners logged not scored)

- New env SFS_LOOP_SELECT=1 replaces largest-comp with best-loop-comp when KDF path reaches the comp filter (works with/without ROR; skipped when SFS_COMP_KEEP=all; tiny comps n<8 score INF and are excluded; fallback to largest if none score). Default OFF so CTL/VOTE/GATED replicate exactly.
- Per-comp score (stated assumption, no paper constant): for each comp, PCA-plane angular sort about its own centroid, turnSum (signed, abs), closed length L, mean radius R (mean distance to centroid), D-free length term |L/(2πR)-1|, turn term ||turnSum|-2π|/(2π). Score = turn term + length term (equal weights, dimensionless). Corners (same W=8 chord-deviation rule as vote lane, W=min(8,n/4) for small comps) LOGGED per comp but NOT scored — one knob at a time.
- Rationale: clean circle radius r gives L/(2πR)~1.00 and |turn|~2π (score~0.4 on Bl0 from observed 8.97 turn bias); double-cover gives L ratio~1.8 + turn 2x (score~1.9); scribble gives both >>1. Corners separate too (16 vs 4) but scale with n, so kept as diagnostic.
- Gate interaction: gate temp recursion disables BOTH KDF and LOOP_SELECT (like 248 KDF handling) so BYPASS/BRAID decision stays exactly 261-diagnostic (VOTE-equivalent turnSum/L/corners); real path then applies ROR + loop-select. VOTE arm (KDF=0) never enters gate; LOOP_SELECT on VOTE arm scores raw comps directly.
- NEW lane for this ticket: SFS_VOTE_ORDER=1 SFS_KD_FILTER=1 SFS_KD_GATE=1 SFS_LOOP_SELECT=1 SFS_VOTE_REPAIR=0 (GATED + loop-select, no repair). Plus diagnostic RAWLOOP arm in the same job? No — one mechanism: 4 arms CTL/VOTE/GATED/NEW only, matching acceptance table.

## Required evidence to report

Per-lane scores table (CTL/VOTE/GATED/NEW med/cov/jumps); comp-level diagnostics table for P03-Bl1 (per-comp n, L, turnSum, corners, loop-ness score, kept/dropped); diff summary; job IDs + sacct State/ExitCode; binary/edge md5s; overlay PNGs (author black, CTL blue #0072B2, VOTE vermillion #D55E00, GATED green #009E73, NEW purple #9467BD); walk-order verification (consecutive gaps, one loop); self-contained completion message. Judgement stays with lead: stage evidence and STOP.

## Comments (worker, 2026-10-23 — )

## Lead steer (2026-10-23, overrides strand-selection brief)
Lead (session-61c820f6): the braid is NOT two strands to choose between — the surface is MERGED, every dot is real rim. The walk must trace the WHOLE bag as one walk (out one side, around the tip, back the other), discarding nothing. Largest-keep (248) and best-loop-keep (263 as briefed) both cap coverage by construction — wrong direction. STOP the select-a-pile approach.
New task: order the full point set as ONE closed walk with no discard. Step-1 NN chain already covers all n — work from that, fix its cross-jump failure mode instead of replacing its order with the clock sort (which cannot traverse a hairpin). Bar unchanged (med<2, cov>=90, zero jumps>10mm; cov>=90 PROVES nothing may be discarded). Guards + replication gate unchanged.
## Pivot evidence (why the steer is right)
Unguarded LOOP_SELECT on P03-Bl1 picked an 8-pt round satellite (score 0.20) over the true 433-pt strand (score 3.38) and segfaulted downstream — size-free loop-ness prefers tiny satellites. Logs: SfSpp_preprocessing-248/artifacts/pota263_P03_NEW_edgeUnguarded.log (+ run .out/.err). Select-a-pile code (SFS_LOOP_SELECT + 50pts/25% guard) stays in-source dormant (default OFF); exam lane retargeted to SFS_FULL_WALK.
## FULL_WALK mechanism (SFS_FULL_WALK=1, one knob)
(1) Comp-filter bypassed: kept n/n, logged [FULL-263] no-discard. (2) Chain build with heading guard: from 3rd point, among K=50 nearest unvisited pick min dist*(1+2*(1-cos)) (alpha=2 stated knob); exhaustive fallback same score; first 2 pts + degenerate heading use pure NN. (3) Clock sort SKIPPED: loop = chain order; CCW ballot (turnSum vote) unchanged. (4) [FULL-263] chain maxjump logged. NEW lane env: VOTE_ORDER=1/FULL_WALK=1, KDF=GATE=LOOP_SELECT=REPAIR=0 (truly no discard, incl. no ROR).

## Replication (binary 2d435e9f..., blob 1505e320, FULL_WALK defaults OFF)
CTL arm job 33702054 COMPLETED 0:0 (bm139, 42s): P03-Bl0 n=225 med=0.72 cov=97.8; Bl1 n=358 med=0.98 cov=52.8 jumps=1; P22-Bl0 0.80/86.0, Bl1 0.50/91.1/1j; P01-Bl0 0.75/98.8, Bl1 1.01/94.2 — ALL match 262 inherited numbers exactly. Replication gate part 1 PASSES (greedy intact, new code dormant under defaults).
Staging incident: cp of 6 CTL PCDs + 3 logs to pota263_stage/ produced 0-byte files though scorer read full content minutes earlier from identical paths; cp verified working afterwards. Cause unknown (suspect GPFS hiccup). Mitigation: verify-after-copy (test -s) before any rm; CTL trees deleted so CTL arm will be re-run once at end for overlay PCDs. Scores above are preserved as primary evidence.
VOTE arm job 33702321 submitted (avail 1.5G after accounting lag settled).

## VOTE arm replicates (job 33702321 COMPLETED 0:0, bm179, 3:31)
P03-Bl0 n=228 med=0.58 cov=100.0; Bl1 n=4328 med=8.69 cov=11.0 jumps=21; P22-Bl0 4.79/14.4/38j, Bl1 4.43/15.8/17j; P01-Bl0 0.72/98.8, Bl1 0.93/95.7 — ALL match 262 inherited numbers exactly. Gate part 2 PASSES. Evidence on laptop: SfSpp_preprocessing-248/artifacts/pota263_{P03,P22,P01}_VOTE_{edge.log,Bl0.pcd,Bl1.pcd} + author_P{03,22,01}_Bl{0,1}.pcd.
Disk saga: project fs effectively full for writes >~50KB despite df avail ~1G (others filling ~100MB/min; 1KB ok / 100KB fail; cp RC=1 + 'Disk quota exceeded'; downloads flaky but succeed on retry). VOTE trees deleted after laptop backup. GATED job 33702695 submitted.

## FULL_WALK results (job 33702912 COMPLETED 0:0, bm174, 32s, no crash; bin 2d435e9f)
No-discard holds: kept 714/714, 1121/1121 (2 comps), 490/490, 423/423, 435/435, 427/427. Chain order kept (clock sort skipped), CCW ballot on chain turnSum.
Scores NEW vs (VOTE / GATED): P03-Bl0 0.52/100.0/0j (0.58/100; =VOTE, slightly better med); P03-Bl1 EXAM 3.18/41.9/1j-max11.1 (8.69/11.0/21j; 0.99/78.2/3j) — chain maxjump=124.59mm (inter-comp bridge: 76-pt satellite far from main bag), turnSum=10.45, L=896.9. FAILS bar (med, cov, and spirit). P22-Bl0 0.69/87.7/0j (4.79/14.4; 4.87/14.7); P22-Bl1 0.57/95.1/0j (4.43/15.8; 2.40/41.8) — full-walk TRANSFORMS P22 (both lanes near/at bar). P01-Bl0 0.75/98.8 (=VOTE); Bl1 0.98/95.4 (~VOTE 0.93/95.7). Guards (clean loops) HOLD: no lane regressed vs VOTE except P03-Bl1 where both VOTE and FULL fail differently.
Read: heading guard fixes strand-crossing on single-comp bags (P22 proof) but the exam lane's killer is the 124mm inter-comp bridge — a no-discard walk MUST transit out and back (248mm of trail), capping cov. Open Q for lead: is the 76-pt satellite real rim that must be traced (then bar unreachable by construction?), or distant noise ROR would have removed (then KDF+GATE+FULL_WALK combined is the honest lane)? RENDER of P03-Bl1 walk order needed before concluding. Laptop has Python 3.13.2 + matplotlib (verifying); NEW PCDs pending download (quota lottery, 0/9 this round — trees kept on Spartan).
GATED arm job 33702695 COMPLETED 0:0 (bm174, 1:01, no EDGE-EXIT): P03-Bl1 0.99/78.2/3j-max137.9; P22 4.87/14.7/37j + 2.40/41.8/2j; P01 0.72/98.8 + 0.93/95.7 — ALL match inherited. Gate part 3 PASSES. (GATED trees deleted before laptop backup due to disk pressure — scores above are the record; VOTE-equivalent lanes re-runnable.)

## Rendered diagnosis (2026-10-23, worker)
Renders (laptop, matplotlib 3.11.1): SfSpp_preprocessing-248/artifacts/pota263_P03Bl1_exam.png (author/VOTE/NEW + rainbow walk order), pota263_P03Bl1_diag.png (per-point author-distance vs sequence; gaps; walk coloured by distance; far-pts map), pota263_all_lanes.png (6 lanes X-Y). Scripts: render263_local.py, diag263_local.py.
Findings: the no-discard walk DOES what the steer prescribed — rainbow order runs violet start along lower strand, around bottom loop, up the right side, around the top tip, back along the upper strand (out one side, around tip, back the other). ~340/463 emitted pts track author (<2mm mostly, 2-5mm on parallel strand). The failure is the satellite transit: ~120 emitted pts (indices 0-60 out, 400-463 back) form a straight diagonal trail to a satellite tuft ~47mm off-rim, plus ONE 11.1mm bridge leap (idx 62; chain maxjump 124.59mm — heading guard overshoots the bridge, hypothesis unverified). Middle section turnSum=10.45 (extra winding vs 6.28) but harmless.
P22 proof of mechanism: single-comp bags, NEW 0.69/87.7 + 0.57/95.1 vs VOTE scribble — heading-guarded chain order fixes strand-crossing. Clean loops unharmed (P03-Bl0 0.52/100, P01 =VOTE). Overview render confirms visually on all 6 lanes.
## Lead verdict (R6 2026-10-23)

ACCEPTED: honest negative on P03-Bl1 with rendered mechanism; mechanism PROVEN on P22-Bl1 (0.57/95.1/0j, first braid-class cure). Satellite is REMOVABLE NOISE, not real rim: (1) the entire out-and-back transit traverses empty space — zero author dots within 5mm of the red transit in pota263_P03Bl1_diag.png; (2) 47mm off-loop is ~25x the scoring band on a ~100mm-scale loop; (3) walk order on the main loop hugs author (340/463 pts on-rim). Overturn condition: mesh shows the 76-pt comp face-connected to the main surface AND rim-character per the rim detector — then bar/metric gets revisited, not the walk.

Next: 264 guided filter becomes the principled satellite remover (density KDF stays wrong tool); diagnostic KDF+GATE+FULL_WALK lane first to confirm the satellite is the SOLE blocker.

## Worker verdict request (honest negative + one question)
Mechanism works (P22); exam lane fails the bar for a_RENDERED_reason, not a tuning reason: a closed walk that must visit a 47mm-off satellite necessarily paints ~25% far trail points under fresh→auth cov, capping cov ≈ 42-74% < 90, plus the bridge leap breaks zero-jumps. UNLESS the 76-pt satellite is noise ROR would remove (KDF was deliberately NOT run — steer says discard nothing). Question for lead (decision, not fact): is the P03-Bl1 second comp real rim that must be traced (then bar unreachable by construction — needs bar/metric revisit), or removable noise (then KDF+GATE+FULL_WALK is the next lane)? Worker stopped here per steer; did not run any discard lane. Replication gate: CTL/VOTE/GATED all match inherited numbers exactly (see above). Binary 2d435e9f (blob 1505e320, +443/-1 vs 4887348); FULL_WALK dormant under defaults. Spartan: NEW trees kept (pota263_P{03,22,01}_NEW, 557M) for inspection; project fs effectively full for writes (others filling ~100MB/min at 13:3x-13:4x) — coordinate cleanup before next arms. Laptop evidence: artifacts/pota263_{P03,P22,P01}_{VOTE,NEW}_{edge.log,Bl0.pcd,Bl1.pcd} + author_P{P03,P22,P01}_Bl{0,1}.pcd + 3 PNGs + run .out/.err (pota263_run33700442). Uncommitted: ticket file, worktree source+scripts (session to commit).
