# 219 - Flat-screen of the face-vs-edge fixes (user flatten idea, run BY LEAD)

Status: done
Answers: E1-do-our-breaklines-let-sfs-find-sjoins

NOTE: Answers line has a typo (sjoins); accepted as-is, meaning E1.

## Goal
Screen fix ideas for the 217 finding OFFLINE on the laptop in minutes, before any Spartan build. First idea screened: the user's m02716 flatten idea (true edge is empty on one side once unfolded) in its local form -- per-dot tangent-plane projection + 2D angular-gap test.

## Method (all in artifacts/pota219/)
- Labels: 230 S1 pre-dots split by 217 author ruler (<=2mm author Bl1 = rim rider): reproduces 141/89 EXACTLY (step1).
- step2_flat.py: neighbors within r, PCA plane, max angular gap around the DOT (centering bug found+fixed mid-run).
- step3_combine.py: + normal agreement. step4_depth.py: distance to patch edge (dead). step5_otherface.py: distance to S0. step6_combine2.py: gap x dS0.
- Cloud caveat: mesh-sampled S1 (6134 pts), not the true 1139-dot edgeline input bag. Structural conclusion should hold; exact numbers must be re-verified on the true bag before porting anything.

## Results (full tables: artifacts/pota219/p219_results.txt)
- Flatten+gap is the best SINGLE signal found so far (rim retention 137/141 vs 218C's 67) but no cutoff clears the bar (89 face -> ~0 AND >=130 rim kept).
- +smoothness best trade 125/51. Depth dead. Other-face inverted and weak. Combinations add nothing.
- Structural lesson: near-rim riders are locally identical to face-interior dots (smooth, surrounded, same S0 distance). Local features cannot finish the job; the separator must be global (iterative peeling / boundary-depth -- the global version of the flatten idea) or walk-contextual (215 strip precedent: avoid the old locus).

## Lead verdict (2026-10-21, lead-run, self-checked)
ACCEPT as screened-negative-with-signal. Checks: labels reproduce 217 exactly; centering bug caught by insane first output (0 rim kept at every threshold) and fixed with sane behavior change; sweeps mutually consistent (larger r, more neighbors, same curve shape). NOTHING ported (no rule clears the bar). Durable win: the harness -- every future fix idea screens here in minutes before Spartan. Next idea to screen: iterative peeling (boundary-depth). Suggested bar for port: rule clears 217 numbers on the TRUE input bag first.


## Addendum 2026-10-21 (sparsity check, step7_sparse.py)
User's question (m02820) exposed a premise flaw: 'surrounded' was measured on the dense proxy cloud (6134 pts), but the estimator saw ~1139. Downsample test (3 reps): face-dot gaps p50 140 -> ~195; 88-89/89 fire at estimator-like >=100 deg -- but rim fires 136-139/141 too. So sparsity opens fake voids EVERYWHERE (plus strip-narrow regions give fore-and-aft-only neighbors); the exact true 230 cannot be replayed without the true input bag (Spartan-only). Why strays SURVIVE: estimator fires on gap; K=1 snap proven no-op (211/217); walk obeys its input; rim gate advisory-only. No stage downstream re-checks the boundary -- full chain of trust with no audit.

## Addendum 2 (user's unbend-then-estimate, step8_unroll.py)
User correction (m02840): estimator finds true edges fine; the CURVATURE misleads it -- unbend first, then estimate. Tested literally: Isomap unroll of S1 to 2D (k=12), identical k=30 gap test curved-vs-flat. Result: CURVED rim p50 163 / face 169; FLAT rim 162 / face 167; keep/kill rows within noise at every threshold. Unbending changes NOTHING. Why (intrinsic geometry): bending without stretching preserves every millimeter-scale patch, and the estimator only ever sees millimeter-scale patches -- the gaps it fires on are local roughness + sampling holes, both preserved by any unrolling. So the confounder is NOT the global twist. Combined with 218C (face dots normal-smooth at 0.9993 yet position-gappy) the evidence points at HOLES in the input bag (dropped small clusters from twist-shattering + sparse sampling): holes look exactly like boundary to any gap test, curved or flat. Consequence: separator must be hole-immune -- global (peeling/boundary-depth from outside) or walk-contextual (215 strip). Smoothing (not unbending) is the remaining local test, unrun.
## Required evidence
- Scripts + p219_results.txt committed under artifacts/pota219/. No Spartan, no jobs, no other files touched.
