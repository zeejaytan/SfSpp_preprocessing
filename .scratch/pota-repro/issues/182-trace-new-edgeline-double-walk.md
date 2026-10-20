# 182 — Trace the double-walk on the NEW edgeline (post-176)

Status: dispatched
Answers: E1-do-our-breaklines-let-sfs-find-joins

## Goal
Trace HOW the walker double-walks C01's edge on the new (post-split, post-trace-fix,
single-surface, densified) edgeline, and name WHY it walks twice. Ticket 67's face-hop
witness is pre-split old edgeline and does NOT count here -- this ticket re-derives the
mechanism from scratch on the new input.

## Input (read-only, laptop-side, no Spartan)
- The 439-pt open doubled C01 walk from 179's comparison (see 179 ticket s-files for paths).
- Walker: p176_lib.py walk_m144 (greedy + recovery, stops only at full coverage, NO closure check).
- Reference: p180_C01_single_walk.npy (the hand de-doubled 220-pt loop, .scratch/pota180_repro/).

## Method
1. Replay the walk's visit order over the dot bag; colour dots by visit index; render.
2. Locate: does the walk close the loop then continue? Where does the second pass begin
   (dot index)? Is there a hop, a spur, a branch point? Measure walk length vs author 380mm.
3. State the trigger: what rule (or missing rule) sends it around a second time?

## Constraints
- Read-only: COMMIT NOTHING, no dataset writes. Renders eye-checked by worker, staged under
  artifacts/pota182/.
- Distinguish explicitly from the 67 pre-split face-hop: same shape or different mechanism?
- One paragraph mechanism statement, with file:line cites for the walk logic involved.

## Acceptance
- Order-coloured trace render (PNG, path cited) showing the revisit/second-pass start.
- Named revisit point (dot index + coordinates) and the rule/missing rule that causes it.
- Verdict: does a closure check (stop at return-to-start) cure THIS doubling, yes or no, with the number.

## Required evidence to report back
Render paths, revisit index/coords, walk-length numbers, mechanism paragraph, closure verdict.
