# 218 - Three-way shootout for the face-misfiled-as-edge fix (217 follow-up)

Status: ready-for-agent
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
