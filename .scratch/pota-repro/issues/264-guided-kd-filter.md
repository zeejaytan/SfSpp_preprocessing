# Ticket 264: port the paper's guided K-D filter (distance to fitted edge line, not density)

**Answers:** E1

**Blocked by:** Ticket 263 LANDED 2026-10-23 (satellite judged removable noise; lead verdict in 263 ticket). 264 runs in the 248 worktree next, same sequential rule.

**Status:** ready-for-agent
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
