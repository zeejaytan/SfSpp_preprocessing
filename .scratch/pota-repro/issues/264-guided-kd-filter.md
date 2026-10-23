# Ticket 264: port the paper's guided K-D filter (distance to fitted edge line, not density)

**Answers:** E1

**Blocked by:** Ticket 263 LANDED 2026-10-23 (satellite judged removable noise; lead verdict in 263 ticket). 264 runs in the 248 worktree next, same sequential rule.

**Status:** results-in
**Working in:**

- [ ] Replace the blind density filter with the paper's guided filter, edge stage ONLY, default OFF
- [ ] Clean lanes keep ~100% cov (no real rim eaten) in the same job
- [ ] FIRST: diagnostic KDF+GATE+FULL_WALK lane (existing code, no new build) confirming the satellite is the sole P03-Bl1 blocker — expect bar if theory holds
- [ ] THEN: guided filter built; braid bags keep BOTH strands (strays/satellite only removed, nothing selected/discarded)
- [ ] Replication gate passes in the same job (CTL/VOTE numbers == 247b to the decimal)
- [ ] Evidence in ticket Comments + Status results-in; diffs left uncommitted (no main commit)

## Goal

Port the paper's K-D filter faithfully (SfSpp \u00a7 edge line, paper line 164: "Using a K-D tree-based search, points near the edge line are identified and filtered to remove noise and outliers"). The 248 port (SFS_KD_FILTER) is a STATED SUBSTITUTE — blind local density (ROR 2.5mm/6) — and it eats real rim (clean Bl0 100\u219267%). The paper's version is guided: distance to the B-spline-fitted edge line. Build that, behind its own flag, and test the idea: strays removed, real rim kept, braids left whole.

## Boundary

- Reuse 248 worktree C:/PR/SfSpp_preprocessing-248 (detached @4887348; verify edge file identical to main HEAD before building) + Spartan sfs-vote-248. Edge stage ONLY (edgeline_extraction_headless.cpp and its call sites). Mesh/splitter/classify untouched.
- Main pipeline untouched. No assembly. No main commits.
- Sequential with 263: same file, one worker at a time (workspace rule). Do not start implementation while 263's diff is unlanded in that worktree.

## Constraints

- Spartan: pull --ff-only first, STOP and report on divergence.
- Same node class for md5 comparisons. Source-changing build => rebuild + verify md5.
- Replication gate (CTL/VOTE numbers == 247b/261 to the decimal in the SAME job) before any new claim.
- The paper gives NO numeric distance gate: propose the knob yourself (one knob, e.g. max distance to fitted line in mm), test 2-3 settings maximum, report per-setting keep/drop counts.
- Use the repo's existing B-spline fit (fitBSplineSurfaceAndGetNormalsOnProjectedPoints) as the reference line — do not write a new smoother (that is a separate ticket).
- Default OFF; greedy path intact; no K-D filtering inside the 261 gate or vote arms unless explicitly armed for the test lane.
- Judgement stays with lead — stage evidence and STOP.

## Acceptance

- Clean lanes (P03-Bl0, P01 both) keep cov == unfiltered to the decimal (filter removes strays only, proves no real rim eaten) — else STOP, report, no braid claim.
- Braid bags (P03-Bl1, P22): kept count == full bag minus strays (no strand deletion — verify against 248's 433/1082 keep, which is the failure mode being fixed); walk still traces whole (cov bar is 263's job, not this ticket's).
- All guards hold (P03-Bl0 >=97% cov, P01 both == VOTE class, P22 intact-or-better, no segfault).
- Replication gate passes in the same job.

## Required evidence to report

Per-lane scores table (CTL/VOTE/GUIDED-FILTER med/cov/jumps) + per-lane keep/drop counts + distance-knob setting; diff summary; job IDs + sacct State/ExitCode; binary/edge md5s; overlay PNGs (author black, CTL blue, VOTE vermillion, GUIDED distinct); self-contained completion message.

## Comments (worker 264, interim Phase1 2026-10-23)

Phase1 diagnostic DONE (no new build): job 33703588 COMPLETED 0:0 on sapphire bm144, binary 2d435e9f (md5 2d435e9f6a2b6e78ede480b326861da5), edge blob 1505e320, 15 lanes pota264diag_* (P03/P22/P01 x CTL/VOTE/GATED/FULL/DIAG). Replication gate PASSES: VOTE/GATED/FULL == 263 to the decimal in the same job (P03-VOTE Bl1 8.69/11.0/21j; P03-GATED Bl1 0.99/78.2/3j; P03-FULL Bl1 3.18/41.9/1j n=463; P22-FULL Bl1 0.57/95.1/0j; P01 all at bar).

DIAG == FULL exactly on every lane (P03-DIAG Bl1 3.18/41.9/1j n=463 == FULL; P22/P01 identical), proving the predicted collapse: the gate temp recursion unsets KDF+LOOP_SELECT but NOT FULL_WALK, so temp diagnostics are FULL-equivalent (Bl1 turnSum 10.45/L896.9/corners7) which passes the clean gate (|turn|<20, L<1500, corners<=30) => BYPASS, ROR never fires. Log proof: [FULL-263] no-discard kept 1121/1121 chain maxjump=124.59mm, then [KD-GATE] BYPASS clean lane (turnSum=10.4522 L=896.873 corners=7 n=1121). So KDF+GATE+FULL never filtered anything on the exam lane.

Verdict: P03-Bl1 NOT at bar via DIAG (med 3.18>=2, cov 41.9<90, 1 jump 11.1mm>10mm). The satellite REMAINS in the output (1121/1121 kept, inter-comp bridge maxjump 124.59mm in chain, 120 far pts per 263 analysis). What remains is the satellite transit plus the braid (med/cov failure). Per the brief, no further tuning of the diagnostic; the real fix is Phase2 guided distance filter (removes off-line points so FULL never builds the bridge). Clean-lane guard: P03-Bl0 DIAG 0.52/100.0/0j, P01 Bl0/Bl1 0.75/98.8 and 0.98/95.4, all at bar; no segfault anywhere.

Keep/drop + gate log (P03-Bl1): VOTE raw comp kept 1045/1121 (2 comps, satellite 76 separated, both strands kept in main); GATED: BRAID (turnSum 44.8/L8695/corners118) -> ROR kept 1082/1121 -> comp kept 433/1082 (5 comps, strand-eating); FULL: no-discard 1121/1121; DIAG: same as FULL (bypass). Overlays: sfs-vote-248/overlays264diag/ (6 PNGs, author black/CTL blue/VOTE vermillion/GATED green/FULL purple/DIAG orange; P03-Bl1 shows DIAG orange overplotting FULL purple exactly, n=463 both).

Phase2 (in progress): guided filter code added in 248 worktree (SFS_GUIDED_FILTER + SFS_GUIDED_DIST knob, default OFF, K-D distance to vote-ordered largest-comp loop as stated-substitute reference; fitBSplineSurface per-bag infeasible, documented in code comment), source md5 0979fbc983ee47af28fbf674904b3c1f (laptop == Spartan). Build job 33704317 RUNNING on sapphire bm153. Next: 9-lane run (P03 CTL/VOTE/GATED/FULL replication + G3/G5/G8; P22/P01 G5), scoring, overlays, then final results-in.

## Comments (worker 264, final Phase2 2026-10-23) -- RESULTS-IN

Guided filter BUILT and TESTED at 3 knob settings. Job 33704453 COMPLETED 0:0 on sapphire (bm1xx class), new binary f3a2bcf5cdd1e90744034eef599695ce (build job 33704317 COMPLETED 0:0 on sapphire bm153; source md5 0979fbc983ee47af28fbf674904b3c1f laptop == Spartan). 9 lanes pota264g_* (P03 CTL/VOTE/GATED/FULL replication with new binary default-OFF + G3/G5/G8; P22/P01 G5). Replication gate PASSES in the same job: P03 CTL 0.72/97.8 + 0.98/52.8/1j, VOTE 0.58/100 + 8.69/11.0/21j, GATED 0.58/100 + 0.99/78.2/3j, FULL 0.52/100 + 3.18/41.9/1j -- all == Phase1/diag/263 to the decimal. No segfault anywhere.

Per-setting keep/drop (P03-Bl1, bag 1121 = main 1045 + satellite 76): G3 (3mm) kept 1045/1121 -- satellite EXACTLY removed, filtered set single-comp 1045/1045, both strands kept; G5 (5mm) kept 1068/1121 (3 comps, drops 53); G8 (8mm) kept 1106/1121 (3 comps, drops 15). Every setting keeps the full main 1045 (both strands intact -- compare 248 ROR+largest 433/1082 strand-eating failure mode, fixed). Clean lanes keep 100%: P03-Bl0 714/714 at all knobs (scores 0.52/100.0 == FULL); P22 G5 kept 490/490 + 423/423 (scores 0.69/87.7, 0.57/95.1 at bar, == FULL); P01 G5 kept 435/435 + 427/427 (0.75/98.8, 0.98/95.4, == FULL). Guards hold (P03-Bl0 100%, P01 VOTE-class, P22 at bar).

Scores (P03-Bl1 GUIDED+FULLWALK): G3 4.00/42.2/1j n=460; G5 3.58/41.9/1j n=461; G8 3.24/42.3/1j n=461 -- vs FULL 3.18/41.9/1j n=463. NOT at bar at any knob. Honest negative, mechanism nailed: even with the satellite EXACTLY removed (G3: filtered 1045 single-comp, zero satellite pts), the FULL chain still makes a 122.8mm leap ([FULL-263] chain=1045 maxjump=122.846mm) leaving 1 output jump 11.1mm>10mm and med/cov 4.00/42.2. The remaining failure is INTER-STRAND: the single walk must traverse both parallel braid strands, jumping between them. Distance-to-line keeps both strands BY DESIGN (both near the line -- the spec), so it cannot fix inter-strand ordering; the bar needs strand-aware ordering (263/out-of-scope), not filtering. Overlay proof: sfs-vote-248/overlays264g/ (6 PNGs; P03-Bl1 GUIDED5 orange n=461 tracks FULL purple n=463 on the author black loop, VOTE vermillion scribble n=4328, GATED green partial n=403).

Stated substitute (code comment, no new smoother, greedy untouched, default OFF): reference = vote-ordered resampled loop of the largest 5mm-comp via guarded recursion; fitBSplineSurface per-bag infeasible (NURBS surface fit to mesh xyz + 10k sample, 8 iters, temp files, surface points not rim bags). One knob SFS_GUIDED_DIST (tested 3/5/8, only knob). Diff: edgeline_extraction_headless.cpp +498/-1 in 248 worktree (263 base + guided block), uncommitted; new files (build264/run264g/stats264g/overlay264g + diag assets) uncommitted. 263 Spartan NEW trees untouched; Phase1 pota264diag_* + Phase2 pota264g_* kept as evidence. Judgement to lead.

## Lead verdict (R6 2026-10-23)

ACCEPTED: Phase 2 honest negative with nailed mechanism; overlay confirms GUIDED5 tracks FULL on the author loop, satellite transit gone, VOTE still scribble. Substitute reference ACCEPTED on evidence (G3 removes exactly the 76-pt satellite, clean lanes 100%, both strands kept — the reference only needs to define 'near the line', and it does). Phase 1 caveat RECORDED: DIAG==FULL because temp recursion unsets KDF but not FULL_WALK — the diagnostic gate never engaged, so Phase 1 tested nothing beyond replication; the satellite-sole-blocker theory was disproven by Phase 2 instead (satellite exactly gone, still 1x11.1mm jump + 122.8mm chain leap = inter-strand). Remaining blocker is ORDERING (strand-aware walk), out of scope for a filter ticket. Code stays default-OFF in the 248 worktree (uncommitted); nothing touches main.
