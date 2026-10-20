# 220 - Top-down split trial (user idea m02896): loose-to-tight on P16

Status: done
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

## Lead verdict (2026-10-21)
ACCEPT. Re-ran p220_score locally: @14 (0.71/95.1 + 0.63/95.6) and @4.5 (0.59/95.9 + 0.49/99.3) EXACT; 9 sacct jobs COMPLETED 0:0 (10th disclosed stillborn, superseded); exp-220 = 3-line patch, pushed unmerged; main untouched except this ticket. Strong-form (breakface-off-first) REFUTED as predicted-order, but R2 stops land all lanes at bar -- trial still moves the line forward. RED FLAG verified as numbers (current-line @4.5 >> 214-fresh) but NOT the mechanism: curvature-noise seed-chaos stays hypothesis. Consequences recorded: (1) 214-P16 gate numbers STALE, re-baseline before any P16 landing; (2) R2 is n=2 candidate, needs the 5 MIXED pieces before port talk. Nothing merged.

## Comments (worker 220, 2026-10-21, NO main commit; branch exp-220 pushed, unmerged)

### What was run
- Branch exp-220 off origin/pristine-splitwalk @ e962159 (+3-line env-gated patch: SFS_SINGLE_SHOT=1 caps the tighten loop at 1 iteration; default path byte-identical, verified base md5 == pristine-splitwalk). Pushed to origin, unmerged.
- Spartan fresh copy /data/gpfs/projects/punim2657/sfs-fix-220 (from sfs-fix-218 minus builds/logs, .git removed, patched file uploaded LF-normalised md5 b9a329fb == worktree blob). No main-checkout/stash/bundle touched.
- Binaries (Release, same .sif): MeshPreprocessingHeadless 9a0386f54b0ecc70605f9f26371a789e, EdgeLineExtractionHeadless dc472b0e87c334b6c487ff8637209864.
- Ladder (single-shot per threshold, P16+P01 staged from 214 inputs): thresholds 90/60/45/30/20/18/16/14/12/10/8/4.5. Stretch: P16 edge at 14 + 4.5 + 12; P01 edge at 10 + 8 + 4.5. All jobs sacct-COMPLETED 0:0: build 33521644, ladder 33521729, refine 33521923, repro2 33522045, edge-build 33522153, stretch 33522367, P01@10 33522402, P01@8/4.5 33522472, P16@12 33522620 (33521950 completed at Slurm level but ran nothing -- bad apptainer path in my script, superseded by 33522045).

### Threshold tables (cloud totals: P01 = 149013 pts, P16 = 29719 pts; sizes = region clusters desc; UN = unclustered verts; every row sums to exactly 100%)
- P01: 90/60/45/30/20/18/16 = 1 cluster (149013/149008/148993/148942/148497/148150/147594, residual UN 0/5/20/71/516/863/1419). 14 = 3 (144980/1127/768, top2 98.05%, third 0.52%, 2nd/1st 0.008, UN 2138 derived). 12 = 4 (142108/2031/1106/726, top2 96.73%, third 0.74%, 2nd/1st 0.014, UN 3042). 10 = 5 (75628/65579/1976/1092/677, top2 94.76%, third 1.33%, 2nd/1st 0.867, UN 4061). 8 = 8 (68197/60469/6906/2866/1913/1902/1075/642, top2 86.35%, third 4.63%, 2nd/1st 0.887, UN 5043). 4.5 = 12 (67590/59679/3906/..., top2 85.41%, third 2.62%, 2nd/1st 0.883, UN 8187).
- P16: 90/60/30/20/18/16 = 1 cluster (29719/29719/29687/29484/29322/29119); 45 = 1 (25954, residual 3765 -- dip, unclustered by-product, not a split). 14 = 5 (12198/10430/2262/2138/1712, top2 76.14%, third 7.61%, 2nd/1st 0.855, UN 979). 12 = 6 (12026/10308/2196/1669/1053/1002, top2 75.15%, third 7.39%, 2nd/1st 0.857, UN 1465). 10 = 6 (11681/10301/2137/2002/1552/236, top2 73.97%, third 7.19%, 2nd/1st 0.882, UN 1810). 8 = 6 (11569/10245/..., top2 73.40%, third 6.79%, 2nd/1st 0.885, UN 2215). 4.5 = 9 (11261/10124/1799/1399/883/408/324/165/53, top2 71.96%, third 6.05%, 2nd/1st 0.899, UN 3303).
- Run-to-run determinism (2 reps @4.5): big-2 stable to +-4 pts (0.04%), order stable; crumbs <= ~300 pts jitter membership. Stopping rules below depend only on big clusters -- valid.

### Verdict: NO clean 2-big step exists
- Neither piece ever yields exactly 2 clusters: P16 jumps 1 -> 5 (at 14), P01 goes 1 -> 1-giant+crumbs (14/12) -> 2 faces + crumbs (10/8). The strong-form prediction (breakface off FIRST as its own step) is REFUTED -- faces and crumbs appear together at the first multi step (P16@14 crumbs = 6112 pts / 20.6%, third 7.6%).
- Stopping-rule candidates (recorded, n=2 pieces -- do not overfit): R1 = first threshold with top2>=70% AND third<=8% AND 2nd/1st>=0.5 (the balance term rejects P01@14/@12 one-giant steps). R1 stops P16@14, P01@10. R2 = R1 satisfied at TWO CONSECUTIVE thresholds (stability). R2 stops P16@12, P01@8. R2 is the better candidate: both R2 stops score AT-BAR on every lane (below), while R1's P01@10 leaves one lane below-bar.
- Same rule both pieces (P01 control satisfies R1/R2 at 10/8 with 2-face balance 0.867/0.887).

### Stretch: P16 edge + score vs author (209 pattern, slots flip per piece -- ourBl0->o1, ourBl1->o0 throughout; no blanket swap)
- @14 (R1 stop): ourBl0->o1 0.71/95.1 AT-BAR (1 jump 80.3mm, max 7.3); ourBl1->o0 0.63/95.6 AT-BAR (1 jump 44.3mm). Pre-dots n=586, ALL rim riders, 0 face-interior.
- @12 (R2 stop): ourBl0->o1 0.86/92.5 AT-BAR (0 jumps); ourBl1->o0 0.52/100.0 AT-BAR (0 jumps). Cleanest.
- @4.5 (status quo): ourBl0->o1 0.59/95.9 AT-BAR; ourBl1->o0 0.49/99.3 AT-BAR. Pre-dots n=433, all riders, 0 face-interior.
- Bl0 unchanged-question: no Bl0 harm at any stop (all AT-BAR). 214-fresh was 0.80/76.2 + 1.45/51.8.
- P01 control lanes: @10 ourBl0->o1 0.72/99.7 AT-BAR, ourBl1->o0 0.79/63.6 below-bar (med fine, coverage short, max 11.5). @8 both AT-BAR (0.61/100.0, 0.61/96.6). @4.5 both AT-BAR (0.48/98.0, 0.62/92.6). So R1's P01 stop (@10) is one step too early for lane quality; R2's (@8) is fully at bar.

### RED FLAG for lead: 214's P16 mesh does not reproduce on this line
- My @4.5 (default-path identical: same source, same threshold, SFS_SINGLE_SHOT a proven no-op here) gives P16 = 9 clusters/biggest 11261/S0 23309/S1 20720/UN 3303; 214's pipe logged 43 clusters/biggest 4799/S0 13767/S1 6134/UN 16569. GROW-DIAG mean angle identical (6.623 both) but max curvature garbage differs wildly (214: 39.65; mine: 2e14~4e19 across reps). Mechanism hypothesis: degenerate PCA curvature magnitudes drive PCL seed ordering, so seed order (hence segmentation) is hostage to curvature noise -- big-2 stable, crumbs jitter run-to-run, and build-to-build it can flip wholesale. Consequence: 214's P16 gate numbers are stale on the current line (my @4.5 lanes: 0.59/95.9 + 0.49/99.3, far above 214-fresh 0.80/76.2 + 1.45/51.8). Recommend lead re-baselines P16 (and treats 214 mesh-era numbers as suspect) before any landing decision. ORIG-free throughout (author used as ruler only).

### Paths
- Spartan: sfs-fix-220 (code+builds+scripts), ladder tree pota220_ladder (thr_*/ per-threshold logs+surfaces+UN), stretch trees pota220_edge{14,4p5}, pota220_edgeP01, pota220_ep01_{8,4p5}, pota220_edgeP16_12.
- Laptop worktree .scratch/.wt-220/artifacts/pota220/: fetched lanes/boundaries/surfaces + p220_score.py, p220_p01score.py, p220_p01bscore.py, p220_p16bscore.py (re-run locally to verify every number above).
