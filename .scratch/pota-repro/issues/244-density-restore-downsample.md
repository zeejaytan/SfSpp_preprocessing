Status: ready-for-agent

# Ticket 244: density restore -- feed the paper grower 164k-scale input (owns the 19k downsample)

Answers: whether restoring input density cures P03 with the paper's own numbers.
Needs-eye: no.

## Goal
Restore the grower's input density toward the pre-48fb588 scale (0.6mm no-target path, ~164k) and re-run the paper grow on P03 vs P22: P03's face must re-join whole, P22's fork must stay open.

## Boundary
- Fresh worktree of origin/main + fresh Spartan copy. Work in downsamplePointCloud() and its targetSamples plumbing ONLY (48fb588 lineage). Grower, merge gate (Table I, acquitted), old path logic untouched.
- Why the downsample exists (lead record 2026-10-22): 48fb588 (2025-11-18) set 19k target to match the sample dataset's density; no-downsampling was unstable at 1M points. The restore must respect BOTH original motives: keep runtime stable AND test dataset-match impact explicitly.
- Phase A (measure, NO behavior change): old-path impact analysis -- what the 19k target changed for the old path (density, cluster counts, trace class on P03/P22 at 19k vs 164k). Report whether the old path also needs the density.
- Phase B (restore): raise/restore input density (old 0.6mm path or raised target -- worker's evidence decides), rebuild mesh, re-run P03 + P22, re-trace P03 with dc472b0e.
- Main worktree (user 204-edit) off limits except ticket commit+push (lead lands). No commits to main. No other pieces touched.

## Constraints
- Spartan: pull --ff-only first, STOP and report on divergence. Same build node for md5 comparisons (-march=native differs per node).
- Stability guard: the restore must not reintroduce the 1M-point instability (cap or target, measured -- report peak memory/runtime vs the 19k path).
- Dataset-match guard: report the resulting points-per-surface vs the sample dataset (48fb588's motive); if restore breaks the match, say so with numbers -- lead + user decide, worker does not.

## Acceptance
- Phase A table: old path at 19k vs 164k (P03/P22 density, clusters, trace class).
- Phase B bar: P03 S0 at OLD-mesh scale (cut-region ~2400-class) + OLD-mesh trace class (0.53/97.3-class, same dc472b0e); P22 fork intact (faces md5-identical to 239, trace = 239 exactly).
- sacct COMPLETED for every job; rebuilt mesh md5 cited.

## Required evidence to report
Impact table; the restore diff; peak memory/runtime vs 19k path; sample-dataset match numbers; P03 S0 count + trace scores; P22 no-regression scores + face md5s; job IDs + sacct states; verdict in ticket Comments; Status results-in; self-contained completion message to parent agent session-1ca83938-6e86-4736-bb84-2f4e58807e35.
