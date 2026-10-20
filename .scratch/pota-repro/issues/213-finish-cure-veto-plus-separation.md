# 213 - Finish the cure: veto recalibration + per-surface loop separation (212 follow-up)

Status: ready-for-agent
Answers: E1-do-our-breaklines-let-sfs-find-joins

## Goal
User order (2026-10-20, option 1): finish the 154-port cure on the pristine
line so P01's second file carries the true rim and nothing else. 212 proved
the two gaps: (a) the Pot-C-calibrated face veto (align>0.5) drops 794/1139
P01-Surface_1 boundary dots and shatters the rim (largest kept component
113 < 214 needed -- count bet dead on arrival); (b) with the veto off the
walker covers the full rim 214/214 @ med 0.81 but files rim+ring mixed in
one slot (327 pts, 66.7% forward). Fix both, proved on P01 by the 211 bar.
175's rule STANDS (lead-verified 2026-10-20 from the port log: S0 -> 1x822
-> Bl0 207, S1 -> 8 comps -> Bl1 272, no pooling, slot filing clean) -- the
separation step works INSIDE one face's bag, never across faces.

## Boundary
Continue on branch pristine-splitwalk + worktree .scratch/.wt-pristine-
splitwalk + Spartan experiment copy sfs-splitwalk-212 (all exist from 212).
Do NOT touch: live main checkout, the 2 pre-E2E stashes (do NOT pop), 210's
v1 bundle and seating runs, bundle v0, the 208 pipe tree (read-only
reference). Port branch stays LOCAL until lead lands (COMMIT NOTHING).
Touch NO tracked file except this ticket. Fix scope ends at re-extract +
score -- NO assembly reseat here.

## Constraints
(a) Veto recalibration: Pot-A-geometry gate, ORIG-free (mesh-observable
only, 154 precedent). Target: rim survives as the largest connected
component at 5mm (veto-off shows the clean 2-group input: rim ~808 +
ring ~331 -- the gate must keep that whole, not shatter it). State the new
gate with numbers, not a tuned constant. (b) Loop separation: after the
walk, separate each face's loops into their own files (rim to Bl1, ring
aside -- never merged, never dropped silently); no choice at split time
means provenance first: which loop is rim-continuous vs step-circular is
decided by mesh-observable shape (closure, radius, wall-distance), stated
in the ticket before building. Minimal change to the 212 port; T24-pattern
discipline. Standing submit sign-off covers probe/rebuild/re-extract jobs;
held allocation for iterative work, sbatch only for long unattended runs
with laptop-side poll. Same-binary ORIG control in every scoring run.

## Acceptance
P01 fresh-Bl1 ~= author Bl1 (med <2mm, >=90% pts <2mm) AND fresh-Bl0
unchanged (still == author Bl0, med ~0.5/100%). Clean Spartan build from
the branch. Veto gate stated with keep/drop numbers; separation rule stated
with shape criteria; component table + picture paths filed. NO reseat.

## Required evidence
Comments: veto gate before/after (kept/dropped per surface), separation
rule + shape criteria, P01 before/after numbers both lanes, 212-bar
comparison (recipe 8.70/35%/42% -> now), picture paths, binary md5.
Final report: same, self-contained. Do NOT flip to done -- lead flips
after review.

## Comments (worker)
