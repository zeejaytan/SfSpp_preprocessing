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

## Required evidence to report
sacct COMPLETED for every Slurm job; binaries md5; the cutoff + window; gap table + UN/top2; control numbers; verdict in ticket Comments; leave Status for the lead.
