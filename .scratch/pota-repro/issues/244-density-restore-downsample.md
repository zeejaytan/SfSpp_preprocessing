Status: done

Lead verdict (R6 2026-10-22): PASS. Jobs 33663646/33663702/33663893/33663998 COMPLETED 0:0 (33663624 FAILED 1:0 = superseded quoting bug, no artifacts). Restore diff = downsamplePointCloud + call site only (21+/7-), grower/merge untouched. Render p244_P03_S0_compare.png lead eye-checked: restored 107109-dot face dense, green lane rides the full rim like OLD (0.71/100.0) vs gutted 6693 middle. P22 fork intact (trace class = 239). Guards: peak RSS 947MB stable; sample-match broken ~3.4x on P03 -- restoring density and matching the sample dataset are now in direct conflict, user call pending. Caveat carried: P03-Bl1 ridge-lock is tracer-side, own ticket. Restore NOT yet merged to main (lives in sfs-dense-244 + artifacts/pota244/restore244.diff); merge decision rides on the sample-match call.

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


## Comments (worker, 2026-10-22 -- PASS: fixed-0.6mm restore rejoins P03 at OLD-mesh scale, P22 fork intact)

**Verdict: PASS with one reported caveat (P03-Bl1 walker drift, face verified good). The 19k downsample was the scale killer (243 convicted); restoring the pre-48fb588 fixed-0.6mm radius cures P03 on the paper chain with the paper's own numbers, keeps P22's fork open, stays far from the 1M instability. Raised uniform target (164k) REFUTED as the restore shape -- it 9x-oversamples small pieces and degrades P22.**

**Divergence/STOP note (brief rule): Spartan live checkout behind (f4add97 vs origin/main 8f27cf0, 12 commits) + documented skip-worktree live file -- not history divergence (fetch clean). Left untouched per 239-243 precedent; fresh clone sfs-dense-244 @ 8f27cf0 (clean, origin/main). Laptop main == origin/main, no divergence. No main commits; restore lives only in sfs-dense-244 working tree (uncommitted) + artifacts/pota244/restore244.diff on laptop.**

**Restore diff (21+/7-, downsamplePointCloud + call site ONLY; grower/merge/old-path untouched): targetSamples==0 now runs the pristine fixed-radius path (UniformSampling 0.6mm, no target loop -- ported verbatim from origin/pristine-splitwalk); <0 keeps 48fb588 skip-raw; >0 keeps adaptive. Call site default 0, SFS_DOWNSAMPLE_TARGET=N overrides (19000 = current behavior). Rebuilt binary b8eb37599bb222764f789eabb5dd798c (bm171; md5 necessarily differs from d72979aa -- code changed).**

**Phase A -- old path 19k vs 164k (all COMPLETED 0:0; 19k arms on fresh origin/main binary d72979aa, 164k arms on pristine de8effd0, md5-gated in-job; same old-path env all four):**
- Identity: fresh-binary P03_19k faces md5-IDENTICAL to 243's instrumented-binary OLD run (491883c3/ba9661b3 full 32-hex) -- clean binary, behavior identity proven.
- P03: 19k -> input 17045, 7 clusters, S0/S1 11053/10873 (classification INVERTED vs OLD: S0 wide-footprint, dmin_cut 21.8, n_lt10 0), Bl0 348pts 13.53/0.0 LOST. 164k -> input 164403 EXACT (243's number), 14 clusters (53540+52493+31700+...), S0/S1 106939/107268, cut n_lt10 2391 / n_lt30 20679 (= 241's 2391/20679 EXACT class; S0 +97pts vs 241 rebuild -- thread-noise class, same verdict), Bl0 225pts 0.66/99.1 clean (= 241 0.53/97.3 class), Bl1 364pts 0.63/96.2 (= 241 0.64/96.1).
- P22: 19k -> input 18055 (leaf converged 0.60484 ~= 0.6 -- small piece already near natural density), 13 clusters, S0/S1 13218/13230, Bl0 0.88/82.0, Bl1 0.61/86.6. 164k -> input 18378, 13 clusters, S0/S1 13053/11835, Bl0 0.50/89.2, Bl1 0.77/88.2. Fork open both, scores same class.
- Phase A answers: YES the old path needs the density for P03 (19k shatters+inverts+loses Bl0; 164k whole+clean); NO for P22 (indifferent, fork open either way). Density verdict for the restore: fixed-0.6 gives P03 164403 / P22 18378 -- per-piece natural density, matching 243's chain numbers exactly.

**Phase B -- paper chain at restored density (binary b8eb3759, env = 241/243 paper: SFS_PAPER_CHAIN=1 RHO Table I SINGLE_SHOT=1):**
- P03_RST (default fixed 0.6): input 164403 (raw PCD 1616373 pts -- straight through the feared 1M regime, no instability), paper grow 9 clusters (56345+54075+31700+...), merge 0 joins, classify swaps correctly (face1 interior_frac 0.966 -> S0). S0 107109 (vs OLD 106842/REF214 106894: +0.2%), cut-region n_lt10 2396 (vs bar 2391 -- HIT), n_lt30 20827. Bl0 220pts 0.71/100.0, 0 jumps (OLD-mesh class 0.53/97.3 -- HIT, cov even better). S1 111534.
- P22_RST: 12 clusters, merge only frag 96->118, 2 faces 13471/12192, Bl0 136pts 0.80/86.0 (= 239 0.80/85.2 EXACT class), Bl1 157pts 0.50/91.1 (239 0.41/91.6 class). Fork intact. Faces NOT md5-identical to 239 (necessarily: 1.4x denser faces, 13471 vs 239-class ~6.5k grown) -- the bar's md5 clause is density-incompatible; fork-open + trace-class hold instead.
- P03_T164 (SFS_DOWNSAMPLE_TARGET=164000, adaptive): input converged 146312 @leaf 0.64, S0 95620 (n_lt10 2110), Bl0 0.64/96.5 clean -- also passes, but undershoots fixed-0.6 scale.
- P22_T164: FORCED 139811 input @leaf 0.127 (5x over-dense), faces explode to 103284/101840 (7.7x RST), 7 clusters, Bl0 1.50/77.3 + Bl1 0.96/61.4 DEGRADED vs RST. Uniform raised target distorts small pieces -> REFUTED; fixed-radius default stands (evidence decided).

**Caveat (reported, not hidden): P03_RST Bl1 357pts 0.97/52.7 with a 47mm concatenation jump (T164: 349pts 0.91/56.2). Face exonerated: author Bl1 lane sits ON RST-S1 at med 0.25mm / 100% cov2mm -- geometry correct, the dc472b0e walk locked onto a parallel ridge on the 2x-densified exterior face (systematic 2-10mm offset along the whole lane, not a cut). P22 dense faces trace clean, 19k-paper-S1 traced clean (0.86/95.4) -- dense-large-face walker behavior, follow-up belongs to the tracer, not this restore. Bl0 (the 239-regressed lane, this ticket's bar) is clean.**

**Guards: stability -- Phase B job (4 dense-paper mesh + 4 traces) 16:15 wall, peak RSS 969884K (~947MB, incl. 1.6M-pt raw input); Phase A job 3:07 / 788544K. P03_RST mesh 4:04, P03_T164 7:03, P22 arms seconds-minutes. No 1M blowup, 67x headroom under the 64G request. Sample-dataset match (48fb588's motive) -- BROKEN as predicted, numbers: sample P03 S0/S1 31179/30871 vs RST 107109/111534 (3.4-3.6x); sample P22 4083/4479 vs RST 13471/12192 (~3x). (Note 19k-paper undershoots P03-sample 4.6x the other way: 6693 vs 31179.) Lead + user decide.**

**Jobs (sacct): 33663624 FAILED 1:0 (my first build sbatch -- heredoc quoting bug, superseded, no artifacts); 33663646 COMPLETED 0:0 (Phase A build, bm063, d72979aa = PAPER ref EXACT); 33663702 COMPLETED 0:0 (Phase A, bm063, 3:07); 33663893 COMPLETED 0:0 (Phase B build, bm171, b8eb3759); 33663998 COMPLETED 0:0 (Phase B, bm171, 16:15). Edge dc472b0e reused (md5-gated in-job, not rebuilt). Binaries/jobs cite in bin244A_md5.txt / bin244B_md5.txt.**

**Evidence: artifacts/pota244/ (laptop) = p244_P03_S0_compare.png (eye-checked: restored lane hugs rim like OLD, paper-19k cuts interior) + render_p244.py + restore244.diff + stats244_all.txt + RST_S0.xyz/RST_Bl0.xyz. Spartan leftovers (all mine, sibling-safe): sfs-dense-244/ (clone @8f27cf0 + restore diff uncommitted, build-244/build-244B, sbatches, logs), pota244_P03_19k/_164k, pota244_P22_19k/_164k, pota244_P03_RST/_T164, pota244_P22_RST/_T164. 214/239/240/241/242/243 dirs untouched. No main commits anywhere.**

**Bar check: P03 S0 at OLD-mesh scale (107109 vs 106842, cut 2396 vs 2391) + OLD-mesh trace class Bl0 (0.71/100.0 vs 0.53/97.3) -- MET. P22 fork intact (2 faces, trace = 239 class both lanes) -- MET in substance (md5-identity superseded by density, stated). Rebuilt mesh md5 b8eb3759 cited. PASS.**

## Required evidence to report
Impact table; the restore diff; peak memory/runtime vs 19k path; sample-dataset match numbers; P03 S0 count + trace scores; P22 no-regression scores + face md5s; job IDs + sacct states; verdict in ticket Comments; Status results-in; self-contained completion message to parent agent session-1ca83938-6e86-4736-bb84-2f4e58807e35.
