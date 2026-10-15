# 15: Align refine cost with selection cost (GM refine)

**What to build:** the fix ticket 14 prescribed — make refinement optimize the same cost the vote selects with, so the truth the vote ranks #1 survives the polish instead of draining into a spurious pocket.

**Answers:** E1

**Blocked by:** 14-piece6-diagnosis (mechanism + protocol below).

**Status:** results-in

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

## Comments (worker, 2026-10-15)

**Attempt (a) PASSES its bar — stopped here; (b) and (c) not run.**
Change (residual only, `p15-stage/axle_finder/af_refine_raw.m` + Spartan
`potsac-p15-run/axle_finder/af_refine_raw.m`): Huber rho replaced by GM rho
`2*sq*tau2/(sq+tau2)` with `tau2 = W*W`; callers unchanged (W=1 = the
vote's `robustifier_gm` default width, so refine now optimises the same
robustifier the vote selects with). LM skeleton, frozen-rev handling,
signature all unchanged. `p12-stage/` + Spartan `potsac-p12-run/` untouched
(Spartan copy was `diff`-verified identical before the edit).

**Fit pieces 01–04 (job 33093376, COMPLETED 0:0, 00:02:00) — refine-from-shipped
bar 4/4 PASS (was walk-away on all four per V1f):** P01 (0.10deg,0.45mm),
P02 (0.16,0.67), P03 (0.24,0.04), P04 (0.02,0.06). GM selection-cost walk
check (10% subsample, vote protocol): P01 down-or-flat (5701→5693); P02/P03/P04
UP by 1–6 units in 2200–3400 (0.03–0.2% — flat within subsample noise, and
refine holds sub-degree/sub-mm regardless). Full-chain `af_find_all` alongside:
P02 (0.21,1.00) PASS, P03 (0.16,0.05) PASS, P04 (0.04,0.22) PASS;
P01 chain (0.54,2.59) — direction passes, position 0.59mm over the 2mm line
(P01 is the known curvature outlier per ticket 14: Rmed 38–44mm, S0 flat-like
0.94; cf P05's 2.77mm "material floor" precedent). The ticket's fit bar is the
refine-from-shipped bar, so (a) is a pass; P01-chain position is reported, not
tuned against.

**P06 confirmation, ONE run (job 33093867, COMPLETED 0:0, 00:01:51):**
refine-from-shipped (0.29deg,0.92mm) PASS — the 8.21deg/24.75mm walk-away is
gone. Chain: nset=3, counts=[6555 6540 6528] (truth holds 6529 — inside a
26-point three-way tie), matched derr=2.00deg, rerr=6.07mm. Under this
ticket's position-conditional rule (direction ≤5deg strict, position reported)
the direction bar is met (8.19→2.00deg); position is reported as-is.

**Honest remainder for the successor (not this ticket — stop rule holds):**
with refine fixed, the binding constraint moved to near-tie selection:
peel-by-inlier-count cannot separate modes 26 points apart, and the winner it
keeps sits 6mm off in position. That is attempt (b)'s question (winner by GM
cost, not inlier count) — left unrun per the stop rule, for the frozen
re-validation / ticket 10 to own. Sealed pieces 05/07/08 never run.

**Jobs:** 33093376 (p15a fit 01–04) COMPLETED 0:0; 33093867 (p15b P06)
COMPLETED 0:0. No commits. Staging: laptop `.scratch/pota-repro/p15-stage/`
(`axle_finder/` GM copy + `p15a/b_fit.m` + `p15a/b.sbatch`) mirrors Spartan
`potsac-p15-run/`.
