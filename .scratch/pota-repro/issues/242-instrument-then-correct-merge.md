Status: ready-for-agent

# Ticket 242: instrument the merge gate, then correct it (P03)

Answers: merge-gate correction for the paper chain (follows 241 mesh-verdict + Appendix A audit m04671).
Needs-eye: no.

## Goal
Find which step of the merge gate kills same-face pairs, then correct the algorithm so P03's face re-joins -- while P22's fork still opens.

## Boundary
- Fresh worktree of origin/main + fresh Spartan copy. Work in the paper path only (mergePaper234 / tryMergePair234); old path untouched.
- Phase A (instrument, NO behavior change): log every candidate pair's Step 1 (pair count vs rhoD), Step 2 (seam-normal dot vs rhoN 0.95, curvature gap vs rhoC), Step 3 (interior dot vs rhoInN, curvature vs rhoInC) on P03's 61 fragments. One mesh job. Report which step kills same-face pairs with the numbers.
- Phase B (correct): change ONLY the step Phase A convicts, with the Phase A numbers cited as the reason. Deviation from Table I is allowed ONLY with that evidence (lead+user rule m04671).
- Rebuild, re-run P03 mesh, re-trace. Main worktree (user 204-edit) off limits except ticket commit+push (lead lands).
- No commits to main. No other pieces touched.

## Constraints
- Spartan: pull --ff-only first, STOP and report on divergence. Same build node for md5 comparisons (239 lesson: -march=native differs per node).
- Do NOT touch thresholds Phase A clears. Do NOT rewrite the grower.

## Acceptance
- Phase A table: per-step rejection counts on P03's pairs, convicting one step with numbers.
- Phase B bar: P03 S0 occupancy back at OLD-mesh scale (cut-region ~2400-class, not 129) AND trace at OLD-mesh class (0.53/97.3-class) with the same dc472b0e edge binary; P22 fork still opens (Bl1 at-bar, no re-bridge) -- the cure must survive its own fix.
- sacct COMPLETED for every job; rebuilt mesh md5 cited.

## Required evidence to report
Per-step rejection table; the corrected code diff (1 gate step); rebuilt mesh md5; P03 S0 count + trace scores; P22 no-regression scores; job IDs + sacct states; verdict in ticket Comments; Status results-in; self-contained completion message to parent agent session-1ca83938-6e86-4736-bb84-2f4e58807e35.
