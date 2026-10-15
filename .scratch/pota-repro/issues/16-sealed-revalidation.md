# 16: Frozen re-validation on sealed 05/07/08 (+ near-tie selection if needed)

**What to build:** the unsealing run — score the GM-refine finder on the three pieces it has never touched, then decide the near-tie question with data instead of forecasts.

**Answers:** E1

**Blocked by:** 15-gm-refine-align (frozen GM finder + P06 confirmation below).

**Status:** ready-for-agent

**Starting position (from 15, jobs 33093376/33093867):** one-line GM change in `af_refine_raw.m` (p15-stage, committed after landing; `p12-stage/` remains the pre-fix record). Refine-from-shipped 4/4 on fit; P06 chain direction 8.19°→2.00° (position 6.07mm reported). Standing score: 6/8 under the position-conditional bar (P01–P06 direction-pass; P01/P05 at the material floor). Honest remainder: near-tie selection — peel-by-inlier-count can't split modes 26 points apart (P06 counts [6555 6540 6528]).

**Two phases, in this order:**
1. **Frozen baseline (no tuning):** run the (a)-finder exactly as frozen, ONCE, on sealed 05/07/08. Report per-piece direction + radial errors + nset vs shipped nAns under the position-conditional bar. Whatever it scores is recorded before any further change.
2. **Near-tie selection (only if baseline misses on selection):** attempt (b) from ticket 15 — multi-start refine of top-K diverse vote modes, winner by GM cost not post-refine inlier count (touches `af_find_seq.m`). Develop against 05/07/08 openly now (they are unsealed by phase 1); no new sealed set is created in this ticket.

**Rules:** work on a COPY (new `p16-stage/`; `p15-stage/` stays as the phase-1 record). Phase 2 stops at the first change that moves the 05/07/08 score with direction ≤5° strict.

- [ ] Phase-1 frozen numbers (per-piece errors, nset, pass/fail under the bar)
- [ ] Phase-2 (if run): exact change + file + before/after numbers on 05/07/08
- [ ] Job IDs + sacct states; no commits; Comments-only ticket edits

**Successor:** ticket 10 (generalise B–J) runs on whatever this ticket freezes.
