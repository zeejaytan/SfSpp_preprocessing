# Ticket 261: gate the 248 K-D filter so it fires ONLY on braid/tail tangles (clean loops bypass byte-identically)

**What to build:** first retune the 248 filter (ROR radius/min, COMP gap, largest-vs-keep-all) per setting on P03-Bl1+Bl0; if no point holds both bars, add a pre-filter diagnostic gate (|turnSum|<20 AND L<1500mm AND corners<=30 = clean bypass, else aggressive S0 filter). Ends at re-extract + score; no assembly; nothing committed to main.

**Answers:** E1

**Blocked by:** Tickets 247 (vote arm) + 248 (KDF filter; vote248-filter.diff is the base).

**Status:** results-in
**Working in:** subagent session-61c820f6 (2026-10-22/23)

- [x] Retune sweep first (lead steer 2026-10-22): ROR radius/min, COMP gap, largest-vs-keep-all, per-setting P03-Bl1+Bl0 scores reported
- [x] Gate built only after retune verdict (no single point holds both) — pre-filter diagnostic gate, edge stage ONLY, greedy intact, default OFF (SFS_KD_GATE OFF default; KDF still behind SFS_KD_FILTER)
- [x] P03-Bl1 exam at bar via gated lane (S0-class cure); clean-lane bypass verified positionally identical + scores identical
- [x] Guards hold (P03-Bl0 100% cov, P01 both lanes == VOTE, P22 intact-or-better, no segfault)
- [x] Evidence in ticket Comments; diffs left uncommitted (vote261-retune.diff + gate in 248 worktree; no main commit)
## Retune verdict (lead steer: parameters before detector)

Sweep job 33697789 (bm162, COMPLETED 0:0, ~13min), P03-only CTL/VOTE/S0-S5, scored med/cov<2mm/jumps>10mm. Replication PASSES: CTL 0.72/97.8 + 0.98/52.8; VOTE 0.58/100 + 8.69/11.0/21j (exact 247b).

- S0 (=248 KDF: ROR 2.5/6, gap 5.0, largest): Bl0 0.86/67.2, Bl1 0.99/78.2/3j — cures exam, cuts guard.
- S1 (gentle ROR): byte-identical to VOTE (Bl0 100%, Bl1 8.69/11.0/21j) — holds guard, exam untouched.
- S2 (gap 8.0): Bl0 0.48/100, Bl1 3.24/24.9/15j. S3/S4: Bl0 100%, Bl1 5.34/14.7/19j. S5 (keep-all) = S2 numbers.
- CONCLUSION (reported to lead, gate authorized): no single point holds both bars. Every guard-holding point degrades the exam to VOTE-class; only S0 cures the exam but cuts the guard. Gate required.

Knobs added (defaults replicate 248 KDF exactly): SFS_ROR_RADIUS (2.5), SFS_ROR_MIN (6), SFS_COMP_GAP (5.0), SFS_COMP_KEEP (largest|all); crash guard FALLBACK when ROR keeps <50 pts or <25% (covers the P01 20/435 segfault case). Diff: C:/PR/SfSpp_preprocessing-248/vote261-retune.diff.
## Gate design (v2 — v1 post-filter decision discarded)

v1 (decide on POST-filter diagnostics) was WRONG and discarded: S0-filtered Bl1 already looks clean-ish (turnSum 13.08/L928/corners16), so post-filter thresholds would bypass the improved lane and lose the exam gain. v2 decides on PRE-filter (VOTE-equivalent) diagnostics via one guarded recursion inside getPointsInSequence_Vote247: when SFS_KD_GATE=1 and KDF on, recurse with KDF unset into a temp cloud, stash gateDiag_turnSum/L/corners at the corners-log site; clean (|turnSum|<20 AND L<1500 AND corners<=30) => copy temp to output + return; braid => fall through to the S0 filter. VOTE arm (KDF=0) never enters. Clean lanes cost 1 pipeline run, braid lanes 2. Gate diff: +254/-1 in edgeline_extraction_headless.cpp (248 worktree); cpp md5 254cdfa62e517da677ece102d8dc5685.
## Gated exam+guards (job 33698341, bm152, COMPLETED 0:0, RUN261GATE-DONE, build 33698295 COMPLETED 0:0, bin md5 6362697cf06280df2686c3630ee2caaf)

Replication in same job: CTL P03 0.72/97.8 + 0.98/52.8; VOTE P03 0.58/100 + 8.69/11.0/21j (exact 247b). Gate log: P03-Bl0 BYPASS (8.97/499/4), P03-Bl1 BRAID=>filter (44.8/8695/118, kept 433/1082), P22 all BRAID (turnSum 49-64), P01 both BYPASS (4.56/700/8, 7.10/759/7). No EDGE-EXIT anywhere (P01 segfault gone: BYPASS skips ROR; FALLBACK covers any future ROR collapse).

Scores med/cov<2mm/jumps>10mm, GATED arm:
- P03-Bl0 (guard): 0.58/100.0/0j == VOTE to the decimal. HOLD.
- P03-Bl1 (exam): 0.99/78.2/3j == S0/KDF cure (was 8.69/11.0/21j). CURED (248-class; cov bar 90% unchanged from 248 verdict).
- P22-Bl0: 4.87/14.7/37j vs VOTE 4.79/14.4/38j (filter fired, single-comp scribble: no harm, no cure — filter limit, not gate error).
- P22-Bl1: 2.40/41.8/2j vs VOTE 4.43/15.8/17j (bonus cure).
- P01-Bl0/Bl1: == VOTE exactly (0.72/98.8, 0.93/95.7). HOLD, no segfault.
## Byte-identical bypass — precise claim

Clean-lane GATED vs VOTE point positions: maxptdiff = 0.00000000 (P03-Bl0 n=228, P01-Bl0 n=336, P01-Bl1 n=347). Scores identical to the decimal. PCD md5s differ ONLY in normal columns (up to 0.05); determinism probe (job 33698615, P01 VOTE x2 identical reruns A/B): positions maxdiff 0.0, normals maxdiff 0.08/0.01, md5 all differ. So normal-column variation is inherent pipeline nondeterminism (NURBS-stage, run-to-run), NOT a gate artifact. Bypass is geometrically byte-identical; strict PCD-md5 identity is unachievable for ANY two runs of this pipeline.

## Boundary / Constraints (kept)

- Edge stage only (248 worktree C:/PR/SfSpp_preprocessing-248, detached @4887348; edge file identical to main a23159e, no divergence; origin/main moved 4887348..a23159e left untouched per 239-245 precedent). Main worktree touched ONLY by this ticket file. No assembly. MSYS2_ARG_CONV_EXCL='*' on laptop ops. Same node class (sapphire/bm15x) for md5s.

## Required evidence

Design + scores + gate log lines above; jobs 33697789 (sweep), 33698295 (build), 33698341 (gated run), 33698615 (det probe) all COMPLETED 0:0; binaries bin261 1546bc3bee7318de8119df3112f14ede (retune) / 6362697cf06280df2686c3630ee2caaf (gate); run script C:/PR/SfSpp_preprocessing-248/run261gate.sbatch; stats C:/PR/SfSpp_preprocessing-248/stats261gate.py. Judgement stays with lead: evidence staged, STOP — no main commit, no further work proposed.
