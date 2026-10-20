# 220 - Top-down split trial (user idea m02896): loose-to-tight on P16

Status: ready-for-agent
Answers: none (splitter-method trial; context from 219, ruler from 214/217)

## Goal
Test the user's top-down proposal: start region-growing at 90 deg (everything merges), then TIGHTEN stepwise and stop at the first step yielding 2 dominant faces. Prediction: splits appear in sharpness order -- breakface off first, faces apart, twist-bands last -- so stopping at 2-big lands on the two faces with the breakface off by construction (nothing re-attached, answering the m02894 objection).

## Boundary (worker: read-only except where named)
- MAY touch (Spartan experiment copy ONLY, fresh dir sfs-fix-220): a COPY of the mesh-splitting code for the trial (do not edit main checkout directly; branch exp-220 off origin/pristine-splitwalk, unmerged).
- MAY run: mesh-splitting stage on P16 (+ P01 as control, expecting the same 2-face outcome without breaking its current good split); edge stage + score for P16 ONLY if splitting lands (stretch).
- Do NOT touch: main worktree (user 204-edit live), .wt-*, dchain-port, pristine branches, stashes, v0/v1 bundles, tickets other than this one (append Comments here only).
- ORIG-free: no author-cloud input beyond the existing lanes-as-ruler comparisons.

## Constraints
- Current schedule (to invert): mesh_processing_headless.cpp surfaceSegmentation growth starts smoothness 4.5 deg / curvature 1.5 / 10 neighbours / minCluster 50, loop LOOSENS +2 while clusters<2 up to 45 deg (lines 1580-1672; call site 2068; values 2065-2066). Trial: start 90 deg, tighten stepwise (schedule yours, e.g. 90-60-45-30-20-12-8-4.5 or adaptive).
- Keep: only clusters[0]/[1] become faces (1372 area); record where every dot goes (kept face / crumb / dropped) -- the 216 table showed only 23.56% of P16 dots enter faces; the trial must account 100%.
- Stopping-rule candidates (record, do not overfit to P16): e.g. top-2 share of dots + third-cluster cap. P01 control must satisfy the same rule.
- Report channel = this ticket's Comments + completion notice (no send_message downward).

## Acceptance (lead judges; numbers + cites + paths)
- Table: threshold -> (cluster count, sizes, top-2 share, third share) for P16 and P01.
- Verdict: does a clean 2-big step exist on P16 (faces = inner/outer, breakface off)? Same rule on P01?
- Stretch (if splitting lands): P16 edge + Bl1 vs author (bar med<2, cov>=90%), Bl0 unchanged.

## Required evidence to report
- Branch exp-220 (unmerged), Spartan job IDs + sacct State/ExitCode, the threshold table, face-dot accounting (100%), P01 control table, stretch scores if run.
