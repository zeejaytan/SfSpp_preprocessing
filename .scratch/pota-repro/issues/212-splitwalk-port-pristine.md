# 212 - Port the 154 split-walk cure to the pristine line (211 follow-up)

Status: done
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

## Lead verdict (2026-10-20)
HONEST NEGATIVE with mechanism (189 pattern). R6: all 4 Spartan jobs COMPLETED 0:0; main worktree untouched (main @ e9b2d57, only this ticket + pre-existing 204 mod); branch pristine-splitwalk + worktree exist, nothing committed by worker; 14 artifact files on disk; before-leg reproduces 211. Port is clean and Bl0 unmoved, but Bl1 bar FAILS both variants: recipe veto shatters the rim (largest kept comp 113 < 214, count bet dead with C-calibrated veto), veto-off covers the rim 214/214 @ 0.81 but mixes rim+ring in one slot (66.7%). Walker exonerated; missing pieces are veto recalibration for Pot-A geometry + per-surface two-loop selection/second-slot emission. Fix scope stays closed -- reseat and next-step port are separate tickets on user nod.

## Comments (worker)
## Comments (worker)

(worker, 2026-10-21 -- PORT APPLIED + BUILT + RE-EXTRACTED + SCORED, COMMIT NOTHING, Status left ready-for-agent)

**Verdict in one line:** the 154 cure ports cleanly and Bl0 is untouched, but the
bar is NOT met on Bl1: the Pot-C-calibrated face veto (align>0.5) drops 794/1139
P01-Surface_1 boundary dots including most of the true rim, so the count bet
FAILS with the recipe as specified (largest kept component 113 vs 214 author
pts). A same-tree veto-off ablation isolates the killer: without the veto the
walker covers the full author rim (214/214 contiguous, rev 100%, med 0.81) --
but the single-slot file then carries rim + step ring (327 pts, fwd 66.7%), so
the >=90% leg still needs a per-surface loop-selection step (separate ticket).

**1. Applied-diff vs staged-diff reconciliation (4/4 MATCH).**
Branch pristine-splitwalk off origin/pristine@b1ed4d1; worktree
.scratch/.wt-pristine-splitwalk (main worktree/files otherwise untouched).
Pristine anchors vs staged (73c3e9e/4accb8d-era) anchors:
- hunk 0 includes: staged adds functional/map/limits/algorithm after
  <vector> -- pristine :16 identical context, applied verbatim.
- walker: staged :806-892 (seed cloud[0], greedy K=50, dead iterations) <->
  pristine :533-613 (same disease: seed cloud->points[0] L548-549, K=50 L553,
  dead iterations L550-582). Whole-function replace incl. union-find @5mm,
  largest-first, forward cone + 6mm gate, cuts, adaptive K(5-50). Only the
  header comment differs (port note with both anchors).
- hunk 1 face veto: staged boundary loop :954-965 <-> pristine :655-662 (same
  shape; pristine adds an N=min() guard). Veto adapted line-by-line
  (surfCentroid, align<=0.5, [FACE VETO] log). One deliberate hardening:
  N=min(N, normals size).
- hunk 2 DELETE reload-over: staged :1032 <-> pristine :717-718
  (loadPCDFile(boundary.pcd)->boundaryCloud_Improved). Deleted; sequencing
  consumes the face-vetoed, unclustered-snapped cloud.
git diff --stat on the branch: 1 file, +129/-64 (staged part1 was +135/-65
against a larger function incl. its own context -- same hunks). ORIG-free
recheck: PASS (added-line grep ORIG/author/Bl_0 = 2 hits, both comment prose).

**2. Build (clean, bit-reproducible).**
New Spartan experiment copy /data/gpfs/projects/punim2657/sfs-splitwalk-212
(cp of sfs-e2e-pristine@b1ed4d1; live main checkout untouched @eac8482, both
pre-E2E stashes still shelved). Ported source transferred + LF-normalised
(diff vs e2e-pristine source = hunks only, 189 lines). Direct host cmake fails
(no PCL -- same failure 208 hit, job 33504601); built INSIDE pcl_191_nurbs.sif
per container recipe: job 33511999 FAILED (host cmake), job 33512116
COMPLETED 0:0 (warnings only, incl. benign old-style-cast notes on new lines).
Binary: .../sfs-splitwalk-212/build-212/EdgeLineExtractionHeadless,
md5 33a1e402a10ac0d930c217f00f102a66. Restore-rebuild job 33512959 =>
identical md5 (bit-reproducible). Mesh binary rebuilt too (sources untouched).

**3. Re-extract (edge stage only, mesh inputs reused).**
New pipe tree /data/gpfs/projects/punim2657/pota212_pipe (byte-identical copy
of pota208_pipe, file list + du -b verified). Job 33512282 COMPLETED 0:0
(~1 min). Guards in-job: 189-line source diff, SPLIT-WALK + FACE VETO markers
present, reload-over absent, edge binary present + md5 recorded.

**4. P01 numbers (same numpy ruler for all pairs; before numbers reproduce
211 exactly: Bl1 med 27.60/0%, Bl0 med 0.52/100%, 2 jumps max 36.2 eg 27.2).**
| lane | before (208/v0) | port recipe | veto-off ablation | author |
| Bl1 pts | 92 | 272 | 327 | 214 |
| Bl1 vs author med / fwd<2mm / rev | 27.60 / 0.00% / 0.00% | 8.70 / 35.29% / 41.59% | 0.81 / 66.67% / 100.00% | -- |
| Bl0 pts | 207 | 207 | 207 | 208 |
| Bl0 vs author med / cov | 0.52 / 100% | 0.52 / 100% | 0.50 / 100% | -- |
| Bl1 jumps>10mm / max / endgap | 2 / 36.2 / 27.2 | 1 / 58.4 / 1.8 | 1 / 35.0 / 1.8 | 0 / 0 / 1.8 |
| cross-lane (fresh Bl1 vs author Bl0) | -- | 7.15 / 1.84% (not merged) | 5.51 / 0.00% (not merged) | -- |
| before-Bl0 vs fresh-Bl0 | -- | 0.30 / 100% (drawn lane unmoved) | same binary family | -- |
Author-rim walk-order coverage: recipe 89/214 in 3 runs (20+7+62); ablation
214/214 in ONE run (0-213). Bl0 acceptance leg: PASS (unchanged). Bl1 bar
(med<2 + >=90%): FAIL both variants (35.3% / 66.7% fwd).

**5. Count-bet component table (P01, from edgeline logs; mapping verified:
log L3-6 Piece_01 Surface_0 first, Surface_1 second).**
- Recipe (align<=0.5): S0 veto kept=822 dropped=7 (of 829) -> components 1x822
  -> Bl0 file 207 (unchanged lane). S1 veto kept=345 dropped=794 (of 1139)
  -> components 8: 113 78 75 33 21 13 7 5 (sum 345) -> sequenced 341, 13 cuts
  -> Bl1 file 272. BET VERDICT: FAILS -- largest kept component (113) < author
  rim (214); the veto shatters the rim before the walker starts.
- Ablation (align<=2.0, keep-all, diagnostic only; laptop branch keeps 0.5):
  S1 boundary 1139 -> components 2: 808 + 331 -> sequenced 1139, 11 cuts ->
  Bl1 file 327. Binary md5 690b6a873974dd24eb81429d0aca6ca5 (rebuilt after).
  BET VERDICT: HOLDS weakly -- rim walked whole (214/214 contiguous cover).
  But file = rim + step ring (picture: green inner circle r~26 + full outer
  loop), hence fwd only 66.7%.
- Full-tree side effect (all 8 pieces re-extracted in both runs; P01 scope
  only scored): S0 lanes all single-component (822/584/598/613/554/564/278/
  275/151/245 pattern per piece), S1 lanes split 2-11 components. Untouched
  by design; data retained in results_port/ + pipe tree.

**6. Picture paths (laptop artifacts/pota212/, eye-checked by worker).**
- p212_P01_bl1_vs_author.png -- 2x2 side+top: port-orange vs author-blue
  (fragmentary outer + chord + inner bit) and veto-off-green vs author-blue
  (full outer loop + second inner ring).
- p212_P01_bl0_vs_author.png -- side+top: port-red hugs author-blue exactly.
Scoring scripts (same ruler): score_p01.py, score_noveto.py,
coverage_walk.py, render_p01.py (laptop python/numpy + conda matplotlib).

**7. Spartan-side evidence retained.**
sfs-splitwalk-212/results_port/ (all 16 port-run breaklines + port stage log;
port log P01 lines L16/L28/L30, L213/L225/L227), edge_binary_md5.txt (port
md5; ablation md5 in job 33512749 .out), build logs build-212_33512116.out
(+33512959 restore), edge logs pota212_edge_33512282.out (recipe census:
p01 Bl0 207 / Bl1 272) + pota212_edge_33512749.out (ablation census).
Experiment copy source restored to the true recipe (veto 0.5) and rebuilt to
the identical md5 (login-node /tmp backup copy retained outside the tree). Laptop sbatch texts:
.scratch/pota212_build.sbatch + .scratch/pota212_edge.sbatch (untracked).

**8. Boundary held.** Live main checkout untouched (still @eac8482, Juglet
residue as before), both pre-E2E stashes shelved, bundle v0 + 210 v1 +
seating runs + 208 pipe tree read-only (only read: md5/file-list compares),
main tracked files untouched except this ticket, COMMIT NOTHING (lead lands:
pristine-splitwalk has the uncommitted port; experiment copy is NOT a git
checkout commit -- file transfer only).

**Proposed next (not started):** separate ticket for a per-surface
two-loop selection (or second-slot emission) + veto recalibration for Pot-A
geometry (Pot-C 0.5 gate misfires here: P01-S1 true-rim dots read align>0.5).
NO assembly reseat attempted per scope. Status left ready-for-agent -- lead
flips after review.
