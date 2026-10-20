# 212 - Port the 154 split-walk cure to the pristine line (211 follow-up)

Status: ready-for-agent
Answers: E1-do-our-breaklines-let-sfs-find-joins

## Goal
User green-lit (2026-10-20): port the landed POTA-154 split-walk cure to the
pristine line so P01's second lane walks the true rim instead of the foot
step. 211 proved the failure: pristine walker seeds on file-order point 0,
greedy K=50 walk locked onto the wall-base step ring (92 pts, unclosed, 27mm
end gap), true second rim (author Bl1, 214) never walked though its dots were
100% present at input (p212_P01_both_lanes_input.png: 5475 blue rim dots vs
2243 red ring dots). Cure recipe (staged, ORIG-free, in
.scratch/pota153_repro/: pota153_walker_new_function.cpp + face veto +
DELETE reload-over): union-find components at 5mm gaps, walk largest-first
(dot count, NOT geometric size), forward cone + 6mm gate, cuts, no dead
iterations. 154 proved it on Pot C; this ticket ports it to pristine,
proved on Pot A P01.

## Boundary
New branch off origin/pristine (name: pristine-splitwalk), new Spartan-side
experiment copy (154 pattern -- NEVER build in the live main checkout at
/data/gpfs/projects/punim2657/sfs_preprocessing). Do NOT touch: main
checkout tracked files, the 2 pre-E2E stashes (do NOT pop), 210's v1 bundle
and seating runs, bundle v0, 208 pipe tree (read-only reference). Touch NO
tracked file except this ticket. COMMIT NOTHING (lead lands).

## Constraints
Follow the T24-pattern discipline (27 precedent): prove the walk guilty vs
its appendages first (already done in 211 -- start from it, do not redo),
then the minimal port. Staged hunks are anchored to 73c3e9e-era sources;
reconcile against the pristine-line edgeline source (e2e-pristine lineage)
line by line -- pristine picked function may differ. Prove the count bet on
P01 explicitly: the true rim must survive boundary detection as the LARGEST
connected component at 5mm (if the rim is gap-split and loses the count,
report that instead of forcing the port). Standing submit sign-off covers
probe/rebuild/re-extract jobs; held allocation for iterative build+extract,
sbatch only for long unattended runs with laptop-side poll. Same-binary ORIG
control in every scoring run.

## Acceptance
P01 fresh-Bl1 ~= author Bl1 (med <2mm, >=90% pts <2mm) AND fresh-Bl0
unchanged (still == author Bl0, med ~0.5/100% -- the drawn lane must not
move). Build clean on Spartan from the new branch. Score vs the 211
baselines with 148/150-style counters (bar talk: state med/coverage/jumps).
Fix-ticket scope ends at the re-extract + score; NO assembly reseat here
(separate ticket on acceptance). A picture suffices for visual evidence.

## Required evidence
Comments: applied-diff vs staged-diff reconciliation, build result (binary
path), P01 before/after numbers (both lanes), component-size table proving
the count bet, picture paths. Final report: same, self-contained. Do NOT
flip to done -- lead flips after review.

## Comments (worker)
