Status: done

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

## Comments (worker, 2026-10-22 -- instrumented, convicted Step 1, correction explored and MEASURED: bar unreachable merge-only, no code landed)

**Verdict: Step 1 (rhoD=1.0mm, >=3 pairs) convicted as the Table-I total block -- 28/28 P03 pairs die there with zero reaching Step 2/3. But opening it does NOT restore P03: at rhoD=50 only 1 same-face pair merges, Step 2 correctly rejects 20/24 (face-core pair dot 0.9266 <0.95 must stay split -- faces verified opposite), and S0 stays 6567 (vs OLD 106842). No single merge-step change meets the bar; the scale loss is grow-side (paper grow keeps 12.8k of ~25k pts in 8 clusters + 61 frags vs OLD's 2 faces; B-spline then yields 6.7k vs 106k). Worse: rhoD=50 churns S0 content and Bl0 regresses 2.43/45.5 -> 30.31/13.4. No threshold touched in the repo; nothing committed. P22 fork provably intact (faces bit-identical across all rhoD, Bl1 0.41/91.6 = 239 exactly).**

**Divergence/STOP note (brief rule): Spartan main checkout cannot ff-pull -- mesh_processing_headless.cpp carries a live skip-worktree edit (worktree md5 645b0b86 vs HEAD blob 22264da5), pull aborts. Left untouched per 239/240 precedent. Fresh clone sfs-merge-242 @ a8df62b (= origin/main, mesh src md5 556ef97a = PAPER ref). Local main == origin/main, no divergence.**

**Phase A -- behavior-identity + per-step table (instrumented binary 50c9fc95, job 33653460 COMPLETED bm175; mesh 33659758 COMPLETED; P03 @ Table I):**
- Instrumented (logging-only) mesh reproduces PAPER EXACTLY: S0=6693/S1=10935 (241 PAPER ref EXACT), 8 grow-clusters. Verdict logic untouched (diff: counters + fprintf only).
- Gate @ Table I (rhoD=1.0 rhoN=0.95 rhoC=0.1 rhoInN=0.75 rhoInC=0.25): cand=28 rejPre=0 rejS1=28 rejS2d/n/c=0 rejS3m/d/n/c=0 acc=0. All 28 pairs nPairs=0, boundary dmins 1.6-104mm. NOTHING reaches Step 2. Step 1 convicted.
- (Brief said "P03's 61 fragments": the gate actually evaluates 8 grow-clusters; the 61 are sub-minCluster leftover frag files that never enter the merge. Census: OLD S0+S1=214109 + 7 frags/21547pts; PAPER S0+S1=17628 + 61 frags/7781pts; grow assigns only 12802 pts to clusters.)

**Phase B exploration -- rhoD sweep, same instrumented binary (dmin build 1389c0e0, jobs 33660818/33660929/33660979 all COMPLETED):**
- P03: rd2: 0 merges S0=6693; rd3: 0 S0=6693; rd5: 1 merge (2261+1456 frags, seam dot 0.9897/inDot 0.9974, clean) S0=6567; rd50: 1 merge, S0=6567. Cut occupancy n_lt10mm of (28.9,-1.4,501.8): OLD 2391 / PAPER 129 / rd50 102.
- P03 @ rd50 full Step-2 dots (ordered): cut pair (326+65) 0.9552 passes S2, fails S3 inDot 0.7405 (<0.75 by 0.01, 391 pts -- immaterial); face cores (5120+3386) 0.9266 <0.95 S2-reject; remaining 20 pairs dots 0.80 down to -0.97 (cross-face/curvature, correct rejects).
- Face identity (sampled NN): PAPER-S0 -> OLD-S0 1.15mm (vs 11.13 to S1); PAPER-S1 -> OLD-S1 1.14mm. The two cores are OPPOSITE faces: merging them (rhoN<=0.92) = face re-bridge, catastrophic. S2 (0.95) correctly guards with 0.02 margin -- S2/S3 CLEARED, must not touch.
- Trace (same dc472b0e edge binary, job 33661275 COMPLETED): rd50-mesh Bl0 335pts f0-o0 30.31/13.4 (WORSE than PAPER 2.43/45.5 -- S0 content churned to top-region cluster), Bl1 348pts 0.86/95.4 (= PAPER, clean). Correction direction proven harmful/ineffective.

**P22 no-regression (fork guard): faces S0/S1 md5-IDENTICAL across rd = 1.0/1.0b/3.0/5.0/50 (5903ff46/bb2c048e pair); cores dot -0.9991 at rd50 (opposite faces, structural guard); only merge @50 = two 101+70pt frags (faces unaffected). Trace @ rd50: Bl0 135pts 0.80/85.2, Bl1 155pts 0.41/91.6 -- BOTH = 239 EXACTLY. Fork opens, Bl1 at-bar.**

**Binaries/jobs: mesh-PhaseA 50c9fc95 (bm175), mesh-dmin 1389c0e0; edge dc472b0e re-verified in-run. Jobs COMPLETED 0:0: 33653460 build, 33659758 run-A, 33660704 rebuild, 33660818 sweep, 33660929 P03@1-dmin, 33660979 rho50, 33661275 trace. Superseded: 33655458/33658147 (my apptainer-path typo, MESH-EXIT-127, rerun clean); 33659917 scancelled (bm175 queue, rebuilt unpinned). No main commits (ticket file + artifacts/pota242/ new only).**

**Follow-up recommendation: grow-side density-restore ticket (241 pointer stands). Candidate: paper grow (theta/kappa/nb) leaves ~half the input points unclustered in 8 shards + 61 frags; merge gate cannot reconstitute faces from that. Spartan leftovers: sfs-merge-242/ (clone @a8df62b, build242A, run242{A,B,C,D,E,F}.sbatch + logs), pota242_P03_{A,d_RD10b,RD99} + pota242_P22_{RD10,d_RD10,d_RD30,d_RD50,RD99}/, all sibling-safe. Laptop: artifacts/pota242/ (4 mergetrace CSVs, author P03/P22 lanes, rd50 lanes).**

## Lead verdict (2026-10-22)
ACCEPT as HONEST NEGATIVE on the merge side, POSITIVE as diagnosis. R6: 7/7 jobs sacct COMPLETED 0:0; Comments read; instrumented binary reproduces PAPER exactly (S0=6693 EXACT). The merge gate is INNOCENT: Step 2/3 correctly reject cross-face pairs (face cores verified opposite faces, dot 0.9266 must stay split); opening Step 1 to rhoD=50 merges 1 pair, leaves S0 at 6567, and REGRESSES the trace (Bl0 2.43/45.5 -> 30.31/13.4). Scale loss is grow-side (paper grow keeps 12.8k/~25k in 8 clusters + 61 frags; OLD kept 2 faces). P22 fork intact at every rhoD. Correction of Table I REFUSED on evidence. Follow-up belongs grow-side, not merge-side.

## Required evidence to report
Per-step rejection table; the corrected code diff (1 gate step); rebuilt mesh md5; P03 S0 count + trace scores; P22 no-regression scores; job IDs + sacct states; verdict in ticket Comments; Status results-in; self-contained completion message to parent agent session-1ca83938-6e86-4736-bb84-2f4e58807e35.
