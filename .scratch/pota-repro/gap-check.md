# Gap check — paper vs code (recheck, both audits back)

Full recheck done — both audits back, load-bearing cites spot-checked by me (vote 0 hits in main, sphere 1.8, descriptor boost-only). No hedging. What runs is origin/main @ 9a0f4af, default flags.

## A. Surface chain (mesh_processing_headless.cpp, paper §IV-B1 :147–162)

The file has two paths. Default (paperChain=false, :2557) is what baked Pots A–C. Paper arm (SFS_PAPER_CHAIN=1) is opt-in.

| Paper asks | Paper arm | Default live (what runs) |
|---|---|---|
| Grow from lowest-curvature dot, 10 neighbours, curve<1, angle<4° | Ported — growPaper234 :1725, seed sort :1735, nb+1 KNN :1762, rejects :1766/:1770; defaults 4.0/1.0/10 (:2559–2560) | Wrong numbers — PCL grower :2135, angle 4.5 vs 4, curve 1.5 vs 1, neighbours 15–40 vs 10 |
| Merge over-splits to fixpoint (k-NN pairs + normal sim + boundary-curve + interior verify, repeat) | Structure ported — tryMergePair234 :1861, fixpoint loop :1942, cap 25 :1982; cut numbers 1.0/0.95/0.1/0.75/0.25 (:2040) have no paper counterpart in :147–162 | Single pass — mergeClusters :1384, pairs once :1491, merge once :1498, no fixpoint |
| B-spline per patch + resample | improveSurfaceBoundaryByFittingBSplineSurface :810, both faces :2250/:2255 — dedup, not an even resample; fit constants (order 3/refine 3/iter 8/res 128, 0.2/1.0/0.4/0, 3mm + 140°/40°) have no paper counterpart | Same (shared) |
| Two biggest = in/out | Ported both paths (:2151, :2177) | Same |
| Ray-to-axis vote, both ways, most wins | Ported in structure — classifyAndOrderPaper234 :1990, satA/satB :2022, interior-first :2027; needs SFS_AXIS_FILE, else keeps size order; top-2 only | Different test — checkNormalsIntersection :1514, face-to-face march, no axis, no two-way vote |

## B. Edge / axis / rim / descriptor (paper :164–196)

Main = edgeline_extraction_headless.cpp (3421 lines). Vote/KD-filter = patch-only, 0 hits in main (verified).

| # | Paper asks | Verdict — code file:line |
|---|---|---|
| 1 | PCL boundary on interior | Ported — BoundaryEstimation :775–800, radius 4mm :795, angle 0.6π :798 |
| 2 | "B-spline" smooth of lane | Name only — smoothAndSampleBreaklinesVer4UsingBSpline :474 is a sphere-marcher, radius 1.8 :476, not a spline fit |
| 3 | B-spline surface + normals | Ported — fitBSplineSurfaceAndGetNormalsOnProjectedPoints :1065, order/refine/iter/res 3/3/8/128 :1148–1151, smooth/weight 0.2/1.0/0.4/0.0 :1154–1157 |
| 4 | K-D clean wired into walk | Not wired — ROR 2.5/6 exists :989 but diagnostic-only; walk eats the unfiltered bag :1000; SOR 50/9.0 :2197 |
| 5 | The 248 filter | Missing in main — 248 diff only (SFS_KD_FILTER, ROR 2.5/6, OFF default); main 0 hits |
| 6 | Resample d=1.9mm | Wrong value + algorithm — main 1.8 (:476, :1942); 1.9 + arc-length lives only in vote247.diff:34/:146 behind flag |
| 7 | CCW vote-order Fig.6 | Missing in main — no Vote fn, no flag; substitute Matrix_Rearrange :359 is one global flip (:389, :406), called once :2108. Full vote (PCA :111, angular sort :121, turn vote :132) only in vote247.diff:31 behind SFS_VOTE_ORDER, OFF |
| 8 | Corner-split by peak | Mechanism ported, gate differs — detectSeparateLineSegments(10) :1600, chord :1712, findPeaks :1452/:1750, split :1797; main len 10 vs patch W 8; main no threshold vs patch max(2.0, 3×med) logged-only |
| 9–11 | PotSAC top-10, prune ≤10°, 10%-refine + Cao–Mumford | Ported — 10 (run_potsac.m:34, cpp :74); prune cos>0.9848 (:65/:86, cpp :96/:113); 1.1× + 300/1e-3 then 300/1e-9 (:73/:47/:79, cpp :99/:84/:109); cpp keeps top-50 :184 vs m full-sort, Huber-vs-GM split noted |
| 12–13 | Rim 1.0/0.1/20/steadiest + base gate | Ported exact — check_base_and_rim.m:13–16 (1.0, 0.1), :116 (20), :121/:125 (rule + steadiest); base 25/10/30/5 :52–55, 100-count :99, std 0.25 :100 |
| 14 | NURBS-path classify | Vote ported, growing missing by declaration — original_nurbs_preprocessing/surface_classify.h:1 (vote), :22 (tau 4/1 explicitly untouched) |
| 15–16 | Descriptor [dh,dr,r·da,t] S-G 7 + σ2.0; thickness 1mm back-ray | Missing — main S-G/Gauss/descriptor hits are boost typedefs + header comment only; thickness hits are comments only; no 7-pt, no σ, no 1mm opposite-normal ray |

## Bottom line

In on the default path: PCL boundary, B-spline surface, corner-split mechanism, PotSAC, rim/base numbers. Paper-exact surface grow/merge/vote, resample 1.9, K-D clean wired in, corner gate, descriptor smoothing + thickness: not in main (vote + resample + KD-filter exist only as OFF-by-default patches in the 247/248 worktrees; grow/merge paper arm only under SFS_PAPER_CHAIN=1). The three you flagged are real code — they sit in the paper arm / shared postamble, not in the legacy defaults that baked the pots.
