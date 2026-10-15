# 15: Align refine cost with selection cost (GM refine)

**What to build:** the fix ticket 14 prescribed — make refinement optimize the same cost the vote selects with, so the truth the vote ranks #1 survives the polish instead of draining into a spurious pocket.

**Answers:** E1

**Blocked by:** 14-piece6-diagnosis (mechanism + protocol below).

**Status:** ready-for-agent

**Starting position (from 14, job 33092580):** on P06 the vote ranks the shipped axle 1/6000 (GM cost 1477 vs 1516, +2.7%), but fixed-orient Huber-W=1 refine walks it to 8.21°/24.75mm — the selection minimum is not the refinement fixed point. Same walk-away on all four fit pieces (V1f). Frozen code: `.scratch/pota-repro/p12-stage/axle_finder/` (committed) + Spartan `potsac-p12-run/`.

**Order of attempts (stop at the first that passes):**
1. **(a) GM robustifier in refine** — replace Huber with GM in `af_refine_raw.m` residual only (smallest change, recommended first).
2. **(b) Multi-start refine** — refine top-K diverse vote modes, winner by GM cost not post-refine inlier count (touches `af_find_seq.m`). Only if (a) fails the bar.
3. **(c) GM-cost guard** — reject refine walks that increase GM cost beyond a tolerance. Only if (b) fails.

**Rules:** work on a COPY of the frozen finder (new `p15-stage/` staging, Spartan-side edits; `p12-stage/` stays pristine as the frozen record). Develop on fit pieces 01–04 with the new bar: refine-from-shipped stays ≤5°/≤2mm on all four. Then ONE confirmation run on P06. Pieces 05, 07, 08 stay sealed — do not run, do not tune against.

- [ ] Per-attempt fit numbers (01–04 refine-from-shipped + full-chain errors); stop rule honoured (no second attempt while the first is unmeasured)
- [ ] P06 confirmation (single run): direction + radial error vs shipped; bar under the position-conditional rule: direction ≤5° strict, position reported (narrow strip — floor family may apply)
- [ ] Job IDs + sacct states; no commits; Comments-only ticket edits

**Successor:** frozen re-validation on still-sealed 05/07/08, then ticket 10 (generalise B–J).
