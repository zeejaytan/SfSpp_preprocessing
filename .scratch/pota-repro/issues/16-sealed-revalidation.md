# 16: Frozen re-validation on sealed 05/07/08 (+ near-tie selection if needed)

**What to build:** the unsealing run — score the GM-refine finder on the three pieces it has never touched, then decide the near-tie question with data instead of forecasts.

**Answers:** E1

**Blocked by:** 15-gm-refine-align (frozen GM finder + P06 confirmation below).

**Status:** results-in

**Starting position (from 15, jobs 33093376/33093867):** one-line GM change in `af_refine_raw.m` (p15-stage, committed after landing; `p12-stage/` remains the pre-fix record). Refine-from-shipped 4/4 on fit; P06 chain direction 8.19°→2.00° (position 6.07mm reported). Standing score: 6/8 under the position-conditional bar (P01–P06 direction-pass; P01/P05 at the material floor). Honest remainder: near-tie selection — peel-by-inlier-count can't split modes 26 points apart (P06 counts [6555 6540 6528]).

**Two phases, in this order:**
1. **Frozen baseline (no tuning):** run the (a)-finder exactly as frozen, ONCE, on sealed 05/07/08. Report per-piece direction + radial errors + nset vs shipped nAns under the position-conditional bar. Whatever it scores is recorded before any further change.
2. **Near-tie selection (only if baseline misses on selection):** attempt (b) from ticket 15 — multi-start refine of top-K diverse vote modes, winner by GM cost not post-refine inlier count (touches `af_find_seq.m`). Develop against 05/07/08 openly now (they are unsealed by phase 1); no new sealed set is created in this ticket.

**Rules:** work on a COPY (new `p16-stage/`; `p15-stage/` stays as the phase-1 record). Phase 2 stops at the first change that moves the 05/07/08 score with direction ≤5° strict.

- [ ] Phase-1 frozen numbers (per-piece errors, nset, pass/fail under the bar)
- [ ] Phase-2 (if run): exact change + file + before/after numbers on 05/07/08
- [ ] Job IDs + sacct states; no commits; Comments-only ticket edits

**Successor:** ticket 10 (generalise B–J) runs on whatever this ticket freezes.

## Comments (worker, 2026-10-15)

**Phase 1 — frozen baseline, ONCE on sealed 05/07/08 (job 33094712, COMPLETED 0:0,
00:01:26).** Finder = p15-stage EXACTLY as frozen (GM refine); Spartan
`potsac-p16-run/axle_finder` was `cp`'d from `potsac-p15-run` and `diff -r`
verified identical before the run. Shipped axle counts (nans): P05=1, P07=3, P08=2.
Judged under the position-conditional bar (direction ≤5° strict, position reported):

- P05: refine-from-shipped (0.23°,1.35mm) PASS. Chain nset=3 vs nans=1,
  counts=[7998 7881 7874], matched derr=0.43° PASS strict, rerr=2.24mm
  (0.24mm over the 2mm line — material-floor family, cf P01's 2.59mm).
  Near-tie trio kept (counts within ~1.5%); 2 extra modes vs truth.
- P07: refine-from-shipped probe FAIL is an artifact (single refined axle scored
  against 3 shipped axles). Chain nset=1 vs nans=3, counts=[1375]: matched axle
  0.34°/0.06mm excellent, other two shipped axles unmatched (58.92°, 61.30°
  placeholders). Genuine count MISS — peel/dedup never seats 2 of 3 axles.
- P08: refine-from-shipped on axle 1 walks 16.81°/35.13mm — truth is NOT a
  GM-refine fixed point here. Chain nset=2 (= nans), derr=[16.79 10.88],
  rerr=[34.60 14.91]: count right, BOTH axles direction-FAIL. Genuine MISS.
- (P06 not run in phase 1; t15 value stands: derr=2.00°, rerr=6.07mm.)

Baseline misses on selection/count (P07) and direction (P08) → phase-2 gate met.

**Phase-2 diagnostic p16b (job 33094985, COMPLETED 0:0, 00:01:40, no finder
changes)** — headroom check before editing: round-1 vote → 6 diverse modes,
each refined, GM cost + inliers + vs-shipped reported; plus P07 peel trace:

- P07: modes cover sh1 (GM 424, inl ~1377, 0.52°) and an sh2-pocket (GM 436.4,
  inl ~1220, 4.62°/27.4mm); nothing near sh3 (GMship 444.5, never surfaces).
  Refine-from-sh2 walks UP +0.2 GM units into the 4.62°/27mm pocket (flat
  valley — truth not holdable); refine-from-sh3 stays (0.05°/0.36mm, +0.2 flat).
  Peel trace (M=1): round winners 1376 → 729 → 374 → 284, round 4 STOP-minfrac
  (284 < 0.10×3541=354); rounds 2–3 winners killed by final x1.1 dedup
  (729 < 1376/1.1), hence chain nset=1.
- P08: NO vote mode near sh1. Refine-from-sh1 walks DOWN 424.1→412.5 into a
  spurious pocket 10.86°/14.4mm off — GM landscape prefers wrong pocket by
  11.6 units (~2.7%, same size as P06's old vote margin, opposite direction).
  sh2: truth 413.7 → 413.3 pocket at 4.35°/5.98mm (mode2, inl 1328 = highest);
  mode1 (GM 412.5, 10.86°) is the GM minimum. So a GM-cost winner picks the
  WORSE mode here — (b) as ticketed cannot take round 1 on P08.

**Phase 2 — attempt (b) implemented and measured; STOP here (score moved).**
Change (p16-stage COPY only; `p15-stage/` + `potsac-p15-run/` untouched,
`diff -rq` confirms only these two files differ from frozen):
`axle_finder/af_find_seq.m` — round winner = min full-residual GM cost
(`compute_biaxial_cao_error` + `robustifier_gm` on the round's residual clouds)
instead of max tight inlier count; peel/minfrac machinery unchanged.
`axle_finder/af_find_all.m` — peel call M 1→6 diverse modes/round.
Job 33095278 (p16c, COMPLETED 0:0, 00:02:27), before → after:

- P05: [0.43]/[2.24] → [0.43]/[2.19], nset 3→3. Unchanged PASS.
- P07: [0.35 58.91 61.29] → [0.35 58.91 61.29], nset 1→1. Unchanged MISS.
- P08: [16.79 10.88]/[34.60 14.91] nset 2 → [17.76 4.31]/[36.49 6.14] nset 3.
  sh2 10.88°→4.31° now direction-PASSES (rerr 6.14mm reported); sh1 still
  missed; one extra mode kept (counts 1333/1305/1300 all pass x1.1). MOVED.
- P06 guard (regression watch, same job): t15 [2.00]/[6.07] → [4.10]/[12.39],
  counts [6555 6540 6528] → [6554 6546 6536] (even tighter tie; GM winner
  picks a worse mode). Direction still ≤5° but REGRESSED 2× in both errors.

**Worker recommendation (for session, not frozen): do NOT freeze (b) as-is.**
It trades P06 (2.00°→4.10°) for P08-sh2 (10.88°→4.31°) and leaves P05/P07
unchanged; per-piece mechanisms point elsewhere: P08-sh1 = GM-landscape
failure (truth 11.6 units above spurious pocket — no selection rule among
these modes recovers it); P07 = missing modes (sh3 never surfaces; sh2 pocket
itself 4.62°/27mm off); P06 = GM-winner actively worse than inlier-winner on
a 26-point tie. Candidates for the successor: (b)-variant winner = inlier
count over K modes (P08 mode2 has max inl AND 4.35°), peel-continuation/dedup
rule for P07's killed 729/374 winners, or a new ticket on P08-sh1's spurious
pocket. Freezing decision belongs to ticket 10's owner.

**Jobs:** 33094712 (p16a frozen 05/07/08) COMPLETED 0:0; 33094985 (p16b diag)
COMPLETED 0:0; 33095278 (p16c attempt-b 05/06/07/08) COMPLETED 0:0. No commits.
Staging: laptop `.scratch/pota-repro/p16-stage/` mirrors Spartan
`potsac-p16-run/` (axle_finder + p16a/b/c scripts); `p15-stage/` +
`potsac-p15-run/` pristine as the phase-1 record.
