Status: ready-for-agent

# Ticket 243: grow-side density restore (P03 must join, P22 must stay split)

Answers: why the paper grower shatters P03 + correction that keeps P22's fork open.
Needs-eye: no.

## Goal
Find why the paper grow stage keeps only ~12.8k/~25k of P03's dots in 8 clusters + 61 frags (OLD: 2 faces, ~214k), then correct the grow so P03's face re-joins -- while P22's fork still opens.

## Boundary
- Fresh worktree of origin/main + fresh Spartan copy. Work in the GROW stage only (region-growing reference fix / growRegionsPlaneContinuity234 / dynMinCluster / dynK / planeJoinDeg / planeDistMM / planeWindow / curvatureThreshold). Merge gate (Table I, acquitted in 242) and old path untouched.
- Phase A (instrument, NO behavior change): log why P03's face stops growing -- seed order, per-cluster stop reasons (smoothness vs curvature vs min-size vs plane gate), fragment-size histogram on P03 vs P22. Report the convicting mechanism with numbers.
- Phase B (correct): change ONLY the convicted mechanism, with Phase A numbers cited. The paper's grow parameters may be deviated from ONLY with that evidence.
- Rebuild mesh, re-run P03 + P22 mesh, re-trace P03 with dc472b0e. Main worktree (user 204-edit) off limits except ticket commit+push (lead lands).
- No commits to main. No other pieces touched.

## Constraints
- Spartan: pull --ff-only first, STOP and report on divergence. Same build node for md5 comparisons (-march=native differs per node).
- P22 is the guard: fork must still open (faces bit-identical to 239 ref, Bl1 0.41/91.6 at-bar). P03 is the target: S0 back at OLD-mesh scale (cut-region ~2400-class) with OLD-mesh trace class (0.53/97.3-class).
- 242's acquittal stands: do NOT touch mergePaper234 / tryMergePair234 / Table I values.

## Acceptance
- Phase A table: P03 vs P22 grow comparison (cluster counts, kept-dot shares, stop-reason breakdown), convicting one mechanism with numbers.
- Phase B bar: P03 S0 at OLD-mesh scale + OLD-mesh trace class (same dc472b0e); P22 fork intact (faces md5-identical to 239, trace = 239 exactly).
- sacct COMPLETED for every job; rebuilt mesh md5 cited.

## Required evidence to report
Grow comparison table; the corrected grow diff (1 mechanism); rebuilt mesh md5; P03 S0 count + trace scores; P22 no-regression scores + face md5s; job IDs + sacct states; verdict in ticket Comments; Status results-in; self-contained completion message to parent agent session-1ca83938-6e86-4736-bb84-2f4e58807e35.
