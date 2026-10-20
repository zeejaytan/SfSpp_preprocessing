# 218 - Three-way shootout for the face-misfiled-as-edge fix (217 follow-up)

Status: done
Answers: E1-do-our-breaklines-let-sfs-find-joins

## Goal
Implement ALL THREE fix candidates for the 217 finding (89/230 P16 pre-snap dots sit on twisted-face interior, filed as edge by BoundaryEstimation) as separate code variants, test all three on P16, crown the winner by the bar below. User order (m02637): test all 3, winner gets chosen.

## The three arms (all in edgeline_extraction_headless.cpp, getInitialBoundary_UsingPCL_BoundaryAlgo ~line 937, adaptive radius rule ~line 968)
- ARM A (surround test): post-filter dropping boundary dots fully surrounded by same-patch dots in all directions (true edge dots have a real void beside them).
- ARM B (radius shrink): tighten the 6x-spacing / 3-50mm adaptive rule so neighborhoods stop wrapping around the twist.
- ARM C (normal gate): keep only boundary dots near a normal discontinuity (face/fracture transition).

## Boundary
- Code base: off the cure line (origin/pristine-splitwalk + 213 veto/separation). New branch exp-218, new Spartan experiment copy (e.g. sfs-fix-218); ONE copy may hold all 3 variants as 3 binaries -- your choice, state it.
- Do NOT touch: origin/pristine-splitwalk, main, stashes, holder 33516830 (adopt for steps ONLY if free; else request own), 214/215/216/217 records, visual-qa, any other ticket.
- ORIG lanes are RULER ONLY (scoring), never fix logic (ORIG-free gate, 212 pattern).

## Constraints
- P16 FIRST for all three arms (cheap edge-only runs, no reseat yet). Winner runs the regression set after.
- Keep the 217 pictures' frame for before/after (same views) so the lead can compare.

## Acceptance (the bar -- same for all three)
- [ ] P16 face-interior pre-dots 89 -> ~0 (recompute the 217 number per arm), the 141 rim riders kept (>=130).
- [ ] P16 Bl1 vs author-Bl1: med < 2mm AND >= 90% within 2mm. P16 Bl0 unchanged (0.50/100 within rounding).
- [ ] Regression (winner only): the five slid sherds no worse than 216 post (CSV in artifacts/pota216/p216_score.csv), 214 Pot D gate scores no worse (22 SWAP-clean + P03 AGREE stand).
- [ ] Winner declared by numbers: first arm to clear the bar with Bl0 unchanged and no regression; tie -> smallest diff. Losers documented (numbers + why they lost), code kept in branch (do NOT delete losing variants).
- [ ] Nothing committed or pushed by worker. Only this ticket file modified (Comments).

## Required evidence to report
- Per-arm: pre-dot split (face vs rim counts), Bl1 med/cov, Bl0 med/cov, before/after PNG paths, binary md5s, Spartan job IDs (sacct-verified), branch state. Winner line + landing recommendation (which files to port where).


## Results (worker 218, lead-verified 2026-10-21 from worktree artifacts/pota218/p218_numbers.txt)
Control (214-fresh, same input): S1 pre 230 = rim 141 / face 89; Bl0 0.80/76.2; Bl1 1.45/51.8.
- ARM A (surround K=12/120deg): S1 218 = 135/83; Bl0 0.78/79.5 ~unchanged; Bl1 1.17/51.8. Face barely moved (89->83). BELOW BAR.
- ARM B (radius 3x/clamp 1.5-8, both faces hit 1.5mm floor): S1 241 = 149/92 WORSE; Bl1 1.72/51.2 worse. Directionally wrong.
- ARM C (normal gate 30deg): S1 67 = 67/0 (face->0, rim halved 141->67); Bl1 0.86/68.0 best med but cov far short of 90; Bl0 1.63/55.7 DEGRADED vs control. BELOW BAR + harms good lane.
WINNER: NONE. No arm clears Bl1 med<2 AND cov>=90 with Bl0 unchanged. No regression set (winner-only rule), no retry (all exit 0).
Mechanism read: surround barely fires (twist dots not surrounded at K=12); shrink admits MORE boundary; normal gate has live signal (face->0) but 30deg eats rim too.

## Lead verdict (2026-10-21)
ACCEPT as HONEST NEGATIVE shootout. Numbers verified verbatim in p218_numbers.txt. RULINGS: (1) bar's Bl0 0.50/100 was my copy error (213's P01-Bl0); worker correctly judged vs same-input 214-fresh control 0.80/76.2 -- verdict unaffected, no arm beats control on coverage. (2) Skipping the regression set was correct per the winner-only rule. LAND NOTHING to the cure line. Variants preserved uncommitted->committed on branch exp-218 (pushed, not merged) with all losing numbers kept.
## Comments (worker, 2026-10-21 -- shootout run, NO commit)

BRANCH: exp-218 off origin/pristine-splitwalk @ e962159, worktree .scratch/.wt-218. One file changed (uncommitted): edgeline_extraction_headless.cpp +124 lines -- all three arms as `#ifdef POTA218_ARM_{A,B,C}` blocks in getInitialBoundary_UsingPCL_BoundaryAlgo (worktree lines ~780-953), one arm per binary via -D flag; no flag = control (cure-line byte-logic unchanged). Working files (untracked, worktree only): artifacts/pota218/{src,armA,armB,armC,p218_numbers.txt,p218_{A,B,C}_{before,after}.png,p218_score.py,r218_plot.py,slots218.py,check217.py}. Main checkout: ONLY this ticket touched. NOTHING committed or pushed.

BASELINE NOTE (deviation recorded): the ticket's ~line 937/~968 refs match MAIN, not the cure line. The cure line has NO adaptive rule -- BoundaryEstimation runs FIXED 4mm (worktree line ~795 pre-edit). ARM B therefore ports main's adaptive form in tightened parameters (3x spacing, clamp 1.5-8mm) instead of tightening in place. On P16 (S0 N=13767, S1 N=6134) both faces hit the 1.5mm floor (log: `[ARM-B radius] r=1.5mm` both faces) -- a real shrink vs 4mm control and vs main-adaptive's 3mm floor. All arms ORIG-free (input-cloud geometry + input normals only; no author data in fix logic). One shared diagnostic addition in all three arms (no logic effect): per-face `boundary_S0/S1.pcd` save (shared Temp_edge keeps ONE face only, last-writer-wins per 217 -- scoring needs both).

ARMS AS BUILT:
- ARM A (surround, -DPOTA218_ARM_A): for each veto-kept dot, K=12 same-patch neighbors projected on the tangent plane (input normal); max angular gap < 120deg => surrounded on all sides => face interior => drop. Sparse guard: keep if <6 neighbors or <5 valid angles.
- ARM B (radius, -DPOTA218_ARM_B): spacing = sqrt(400/N), r = 3x spacing clamped [1.5, 8]mm, replacing fixed 4mm.
- ARM C (normal gate, -DPOTA218_ARM_C): max input-normal deviation among K=12 same-patch neighbors < 30deg => coherent face interior => drop (30deg sits just above 215's measured face-p90 18deg vs fracture-p10 28deg split).

SPARTAN: new copy /data/gpfs/projects/punim2657/sfs-fix-218 (from sfs-potD-214, build dirs stripped; source md5 pre-upload 21fbb6b5 = exact 213-cure source per 214 R6; patched file uploaded LF-normalised, md5 89ab05b178ed6484e60a8a3da587ca13). Builds 33519560/61/62 (A/B/C) all sacct-COMPLETED 0:0, edge target only (~fast). Binaries: A 75bc3809a2e7be8c6b66d29d0b0eb551, B ad51383875ca1796a88a9576b2ea3100, C 822f4b1da4ca6fc9e33344fc6b2dcc22. Trees pota218_arm{A,B,C} staged from pota214_pipe P16 inputs + ORIGINAL unclustered.ply (no strip -- code fix test, not recipe test). Holder 33516830 WAS free (no active steps) so adopted for steps: 3 srun edge runs, all exit 0, no segfaults (P22 lesson did not recur); holder left RUNNING for lead. Logs: pota218_arm{X}/edgeline_218{X}.log (arm counts + radius lines verified per run).

RESULTS (same 209 ruler + 217 split metric, metric re-validated EXACT on 217 pre-dots: 230/141/89; slots verified AGREE x0-o0/x1-o1 all arms, cross-lane meds 8-10mm):
- CONTROL (217/214): S1 pre 230 (rim 141 / face 89). 214-fresh lanes: Bl0 0.80/76.2 (n=115), Bl1 1.45/51.8 (n=61).
- ARM A: S1 pre 218 (rim 135 / face 83 -- dropped 12); S0 pre 345 (rim 283 / face 62 -- dropped 22). Bl0 0.78/79.5 (n=122, ~unchanged vs 214-fresh). Bl1 1.17/51.8 (n=83, med better, cov stuck). Eye: cyan Bl0 rides green author rim; blue Bl1 partly on rim, partly drifts.
- ARM B: S1 pre 241 (rim 149 / face 92 -- MORE dots than control, face WORSE than 89); S0 pre 380 (rim 311 / face 69). Bl0 0.77/70.4 (n=135). Bl1 1.72/51.2 (n=86, med WORSE than fresh). Smaller radius admits more boundary, not fewer -- directionally wrong. Eye: blue Bl1 visibly off-rim.
- ARM C: S1 pre 67 (rim 67 / face 0); S0 pre 100 (rim 100 / face 0). Bl1 0.86/68.0 (n=50, best med, cov far short of 90). Bl0 1.63/55.7 (n=79, DEGRADED vs 0.80/76.2 -- interior shortcut). Face->0 achieved, but rim riders halved (141->67, bar needs >=130) and the good lane harmed. Eye: blue Bl1 rides the rim arc but stops short; cyan Bl0 cuts across the face.

VERDICT: NO WINNER (honest negative). No arm clears the bar (Bl1 needs med<2 AND cov>=90%; best cov is C's 68%). By the ticket's tie rule (first arm to clear the bar) nothing qualifies, so NO regression set was run (winner-only per brief) and no retry was triggered (no segfault/collapse -- all exit 0, all lanes walked). Closest on the face metric: ARM C (face 0 both faces) but disqualified on rim count + Bl0 + cov. Best-preserved: ARM A (Bl0 unchanged, rim 135>=130) but face barely moved (89->83). All three variants KEPT in branch exp-218 uncommitted, nothing deleted.

MECHANISM READ (for lead): the surround test barely fires (34/597 dots) -- twisted-face dots are NOT fully surrounded at K=12 (the strip is narrow; neighbors reach the patch edge/void). The radius shrink backfires (finer neighborhoods admit MORE boundary). The normal gate proves normals carry live signal (face->0) but 30deg cannot separate rim from face on this twist -- it eats half the rim too. None of the three isolates the 89 without rim cost.

BAR REFERENCE FLAG: `Bl0 unchanged (0.50/100 within rounding)` matches NO P16 measurement (214-fresh Bl0 = 0.80/76.2; 215-fixed = 0.56/97.4; 0.50/100 is 213's P01-Bl0). Judged Bl0-unchanged against the same-input 214-fresh control instead -- lead to rule on the reference.

PNGs (worktree .scratch/.wt-218/artifacts/pota218/, 217 frame el=18/az=-62 + el=8/az=38, all worker eye-checked): p218_{A,B,C}_before.png (red post-arm S1 pre-dots + green author rims), p218_{A,B,C}_after.png (blue arm Bl1 + cyan arm Bl0 + green author). Numbers: p218_numbers.txt. Scripts: p218_score.py (ruler+split), slots218.py (cross-lane check), r218_plot.py (renders). Status: worker done, lead to review/flip. Recommendation: land NOTHING yet -- all three arms lose; 217 finding stands.
