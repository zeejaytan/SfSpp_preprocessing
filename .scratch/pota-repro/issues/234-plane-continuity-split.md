# Ticket 234: plane-continuity split rule (user-specified)

Status: ready-for-agent
Answers: none (splitter repair; P22 bridge class; curvature-gate candidate from ledger)

## Goal
Replace the splitter's distance-blind angle gate ('do these two neighbouring dots agree within 4.5deg') with a plane-continuity rule the user specified (2026-10-22): keep growing along the SAME PLANE through gradual turns (curves, twists); SPLIT where the turn is sharp (~90deg = a break). Formalized: a dot joins the region if it agrees with the region's fitted plane (seed-plane reference, not last-dot -- so accumulated twist stays inside tolerance); a sharp departure from the plane opens a new face. Test piece: Pot D P22 (fork touch, tab bridge, 232 evidence).

## Boundary
Spartan experiment copy (fresh sfs-fix-234, off main + cure branches); the splitter settings File(s) + rebuild + P22 mesh re-split at the rule's natural operating point(s) + gap table (222 method) + UN/top2 health. No walk changes, no lane changes, no other pieces unless the rule needs a sanity second (P12@4.5 as control only). Do not touch: main worktree, cure branches, .scratch evidence of other tickets, any ticket but this one.

## Constraints
Compare against the region plane, not the last dot (else the twist re-shatters -- this is the load-bearing detail). Report the sharp-turn cutoff used and the plane-fit window. Slot-verify before grading any lane (231 amendment). If the rule cannot separate P22's fork without shattering (UN explodes, top2 collapses), report HONEST-NEGATIVE with the tradeoff numbers, don't tune past it.

## Acceptance criteria
- [ ] P22 fork zone single-face (0 S0 dots within 5mm of the 232 turn dot, 85-S1 pattern or better)
- [ ] Faces not shattered (UN share + top2 within the R6-healthy band: UN<=12%-class, top2>=70%-class -- or report the miss honestly)
- [ ] Control P12@4.5 still selects (no regression on the honest stop)
- [ ] Verdict line: SPLIT-CLEAN / HONEST-NEGATIVE-<tradeoff>

## Lead redirect (2026-10-22, user order -- overrides the plane-continuity spec above)
Park the plane-continuity code on your branch (do not delete). Implement the paper chain (SfS++ Sec IV-B1, lead-read verbatim): (1) region growing from the min-curvature point, n_b=10 neighbours, curvature < tau_kappa=1, normal angle < tau_theta=4deg -- separates interior/exterior/fractured; (2) cluster merging to fixpoint: kNN close pairs between clusters, patch-average normal similarity + boundary-point curvature comparison + internal-point verification, merge all passing pairs, repeat; then B-spline boundary refine + resample; then TWO LARGEST clusters = inner/outer; (3) axis-ray classification: per point, ray along normal to the symmetry axis; intersection on the positive normal side = interior; try both assignments, keep the one with most points satisfying. The paper's own over-segmentation answer is merging, not looser angles. The missing classification IS the swap disease: slot 0 must be interior (assembler reads only slot 0); the fork files surfaces arbitrarily. Acceptance amends: P22 fork single-face + classification labels P22 faces interior/exterior with the majority-vote count + ring control (annulus inner/outer stay the two largest, unmerged). Report which of the three steps carried P22.

## Required evidence to report
sacct COMPLETED for every Slurm job; binaries md5; the cutoff + window; gap table + UN/top2; control numbers; verdict in ticket Comments; leave Status for the lead.
