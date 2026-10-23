Status: done

# Ticket 243: grow-side density restore (P03 must join, P22 must stay split)

Answers: E1 — why the paper grower shatters piece 3, and the correction that keeps piece 22 fork open.
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

## Lead verdict (2026-10-22)
ACCEPT as HONEST NEGATIVE with a convicted first cause. R6: 10/10 jobs sacct COMPLETED 0:0; Comments read (Phase A table + density chain + Phase B numbers all in-ticket). Merge acquitted (242), grow levers measured dead (theta=12 joins P03 but over-joins into one face + closes P22's fork; fabs fix immaterial 0.3%). Scale killer = 9.65x input-density collapse from the 19k-target downsample (48fb588, pre-paper, both paths): at 17k even the old PCL path shatters; OLD-mesh density came from 164k input. B-spline densify is proportional (~1.3x), so the bar is unreachable at 17k by construction. Follow-up belongs to the downsample, not the grower. (Note: artifacts/pota243/grow_table.md never reached the laptop -- numbers survive in-ticket; lead to fetch or accept as-is.)

## Required evidence to report
Grow comparison table; the corrected grow diff (1 mechanism); rebuilt mesh md5; P03 S0 count + trace scores; P22 no-regression scores + face md5s; job IDs + sacct states; verdict in ticket Comments; Status results-in; self-contained completion message to parent agent session-1ca83938-6e86-4736-bb84-2f4e58807e35.

## Comments (worker, 2026-10-22 -- instrumented, convicted, correction probed and MEASURED: bar unreachable grow-side, no code landed)

**Verdict: HONEST NEGATIVE on the grow-side cure (242's merge-negative now has a grow-side twin). Scale killer convicted with numbers = 9.65x input-density collapse (164403 -> 17045), which predates the paper chain and is shared with the old path, hence out of scope and untouched. Best in-scope lever (theta) measured: joins P03 (8->3 clusters, 95.5% kept) but over-joins into ONE face (both opposites bridged, classification inverts, S0 = 452-pt frag) AND closes P22's fork (11->1). No repo change landed; no main commits.**

**Divergence/STOP note (brief rule): Spartan live checkout cannot ff-pull (mesh_processing_headless.cpp live skip-worktree edit, same as 239/240/242) -- not history divergence (fetch clean, origin/main = cbf4c58 both sides). Left untouched; fresh clone sfs-grow-243 @ cbf4c58 (= origin/main, mesh md5 556ef97a = PAPER ref). Laptop main == origin/main, no divergence.**

**Phase A -- behavior-identity + P03 vs P22 table (instrumented binaries bc52a238 (A) / 06a3fa21 (A2, +angle hist); all runs COMPLETED 0:0):**
- Identity: P03 S0/S1 = 6693/10935 EXACT (242 PAPER ref); P22 faces md5-IDENTICAL to 239/242 pair (S0 5903ff465e14623099176214b686a8d6 / S1 bb2c048e4f0766497f78ba4c659e3458, full 32-hex match vs pota242_P22_RD10).
- P03 paper (N=17045, theta4/kappa1/nb10/min50): 8 clusters (5120+3386+2261+1456+326+125+65+63), kept 12802 (75.1%), uncl 4243 in 2510 sub-min regions. eval 170450: accept 8.5%, rejClaimed 76.9%, rejCurv 0 (kappa DEAD -- max input curv <0.5), rejTheta 14.6% (24916). Theta-reject angles: 4-6deg 3098 / 6-10 5255 / 10-30 12220 / 30-90 2782 / 90-150 1115 / 150-180 446.
- P22 paper (N=18055): 11 clusters (6552+5240+9 frags), kept 12930 (71.6%), uncl 5125. rejTheta 18.5% (33383); angles 6525/9060/14296/3499/3/0 -- flip-class (>=90deg) THREE evals (0.009%) vs P03's 1561 (6.3%).
- Kept-cluster seeds all curv <= 0.004 (P03) -- flat ground first; growPaper234 has no seed curvature gate (differs from PCL reference, which gates seeds but lets high-curv points JOIN as non-expanding fill).
- PCL ground truth (container headers): smooth-mode validatePoint compares neighbor normal to CURRENT-front normal (drifting, like paper) with fabsf (orientation-invariant); two-tier join (curv>thresh joins but does not expand). Paper deviations: (i) single-tier + kappa=1.0 (inert here), (ii) signed angle via getAngle3D(...,true) where 3rd arg is in_degree, NOT abs (header signature confirmed) -- real deviation, but A2 caps its effect at ~446 P03 evals (0.3%), zero P22 effect.

**Density chain (the conviction): OLD downsample = UniformSampling 0.6mm no-target (164403 pts, 214 era); current = adaptive leaf targeting 19000+-20% (P03: 17045) from 48fb588, which PREDATES the paper chain (7035611) and feeds both paths. At fixed 17k the PCL old path ALSO shatters (7 clusters 5244+5169+3172+..., S0/S1 11053/10873) vs 241-OLD at 164k: 14 clusters incl 53k+52k+31k faces, old-merge -> S0/S1 106842/107267. B-spline densify is proportional (~1.3x both eras), so S0 ~= 1.3x grown-face <= 1.3x N: cut-region ceiling at 17k is ~490 vs bar 2391 (OLD share 2.2%). Density is the binding constraint; it lives in shared pre-grow sampling, outside the listed grow knobs, and the old path is off limits -> not touched.**

**Phase B probe -- theta=12 env-only (SFS_PAPER_THETA, NO code change, B binary, jobs 33662945/33662946 COMPLETED):**
- P03: 3 clusters (15958+211+120, 95.5% kept), merge 0 joins, classify INVERTS (giant bridged both opposite faces during growth, interior_frac 0.127 vs frag 0.72 -> S0 = B-spline of 211-pt frag = 452 pts, S1 = 23109). Cut10: 0 / 170 vs OLD 2391. Joining lever works, scale does not follow, content inverts.
- P22: 1 cluster (17531, 97.1%) -- fork CLOSED, faces destroyed, md5 guard dead. Any global theta change alters P22 growth (6525 P22 rejects sit in 4-6deg alone), so the bit-identical guard is incompatible with any theta deviation.
- fabs fix assessed from A2 numbers: P22-safe (3 evals, verdicts unchanged) but recovers ~0.3% for P03 -> immaterial, not landed (242 precedent: no bar, no landing). No trace run: T12 S0 is a 211-pt frag with inverted classification, trace med/cov would be misreadable; counts + fork-death + scale arithmetic are the measurement.

**Binaries/jobs: mesh-A bc52a238 (33661994 bm021), mesh-B 06a3fa21 (33662791 bm179); runs P03-A 33662152 (bm176) / P22-A 33662153 (bm142) / P03-OLD 33662583 / P22-OLD 33662584 / P03-B 33662856 / P22-B 33662857 / P03-T12 33662945 / P22-T12 33662946 -- ALL sacct COMPLETED 0:0. Edge dc472b0e not re-run (no landable mesh to trace). No main commits (ticket file + artifacts/pota243/ only).**

**Follow-up recommendation: density-restore ticket owning the 19k-target downsample (48fb588 lineage) with old-path impact analysis -- that is the only route to cut-region ~2400-class. Grow-side is exhausted: merge acquitted (242), growlevers measured dead (this ticket). Spartan leftovers: sfs-grow-243/ (clone @ cbf4c58, build-243A/B, run*.sbatch, patch_phaseA{,2}.py), pota243_Piece_{03,22}_{A,OLD,B,C}/. Laptop: this ticket + artifacts/pota243/ (grow_table.md, patches, sbatches).**

Completion delivery: send_message to dispatch parent session-f43ebd6e-a4fd-4a68-ac04-efdb71330 AND to ticket-named lead session-1ca83938-6e86-4736-bb84-2f4e58807e35 BOTH hard-rejected (subagent unavailable; worker depth has no children, list_agents empty). Report rests in this ticket + artifacts/pota243/ -- lead picks up via Status results-in per worker discipline.

