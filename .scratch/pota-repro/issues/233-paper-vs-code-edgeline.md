# Ticket 233: paper-vs-code edgeline method

Status: done

## Lead verdict (2026-10-22)
CONTRADICTS-4 accepted. R6: spot-verified the load-bearing claims on origin/pristine-splitwalk (zero vot/ccw/counter-clockwise/ballot tokens; GUARD_GATE_MM=6.0 with 'guard starved... records a cut' -- the P22 starvation engine verbatim); report internally coherent across all five stages. The paper never described P22's corner: the fork's greedy seed-arbitrary walk with log-only cuts IS the P12-teleport / P27-flip / P22-starvation engine. Repair order stands: walk continuity first, rim-gate second, input-split last. Only this ticket touched among tracked.
Answers: none (method provenance; feeds the splitter/walker repair decisions)

## Goal
How does the paper describe finding the edgeline (breakline), and how does that differ -- or not -- from what the pristine-line code actually does? Per-stage verdicts with quotes on the paper side and file:line on the code side.

## Boundary
Read-only. Paper side: C:/PR/papers (find the SfS reassembly paper; the repo README/docs cite it). Code side: the pristine-live edgeline path (edgeline_extraction_headless.cpp + pota153_walker_new_function.cpp lineage on origin/pristine-splitwalk, i.e. boundary estimation -> face separation -> walk -> rim gate). Do not edit code, run jobs, or touch any ticket but this one.

## Constraints
Quote the paper (section + page/column), cite the code (file + line numbers). Stage list to cover: (1) input cloud formation, (2) boundary/edge detection, (3) face separation/split, (4) the walk/trace itself, (5) loop selection / rim gate. For each: PAPER-SAYS / CODE-DOES / SAME / DIFFER (one line each).

## Acceptance criteria
- [ ] The paper's edgeline section identified (title/section/page)
- [ ] All five stages covered with PAPER-SAYS / CODE-DOES / verdict
- [ ] Every DIFFER names the exact behavioral consequence (which P22/P12/P27 symptom it explains, if any)
- [ ] Verdict line: FAITHFUL / DRIFTED-<stages> / CONTRADICTS-<stage>

## Required evidence to report
Paper quotes + code cites in ticket Comments; verdict line; self-contained report; leave Status for the lead.

## Comments (worker, 2026-10-21)

Paper leg is SfS++ text/sfspp-2502.13986v1.md Sec IV-B/IV-C (the SfS-2021 conference text is not in C:/PR/papers; SfS++ restates the SfS [9] edge-line method plus its enhancement delta). Code leg is origin/pristine-splitwalk:edgeline_extraction_headless.cpp, cited P:<n> (main copy drifted +802/-356 vs branch, so branch lines rule). Symptom key: P22 = Pot-D P22 turn-away/stub lanes (ticket 232); P12 = locally-wrong stretch class (ticket 215); P27 = rim-ordering (ticket 27).

Stage 1 input cloud: DIFFER. PAPER (text:149/151/155): sample S from mesh, region-grow from min-curvature point (n_b=10, tau_theta=4, tau_kappa=1), cluster-merging upgrade vs SfS [9], two largest clusters = inner/outer. CODE: no region growing/merging/two-largest anywhere; main consumes pre-split Surface_0/1 xyz per fragment (P:3270-3277); cleanSamples only SOR MeanK=50 StdMul=9 into cloud_Surface_AllSamples_Cleaned.pcd (P:2018-2080), loaded straight to boundary estimator (P:1875-1877). Consequence: face separation is an upstream MATLAB precondition, ungated here; the tau/cluster-merging enhancement has no code counterpart.

Stage 2 boundary detection: SAME-method/DIFFER-gates. PAPER (text:164): PCL boundary-estimation [30] on interior cloud, B-spline refine, KD-tree denoise, equidistant d=1.9mm resample, CCW reorder by normals+voting. CODE: same PCL BoundaryEstimation core, radius 4 fixed, angle 0.6pi (P:777-783,791-793); then paper-absent fix-ups: FACE VETO keep-all ALIGN=2.0 always passes (P:799-820; comment: 0.5 gate kept 345/dropped 794 and shattered rim to 8 fragments on P01-S1), snap-to-unclustered-ply refill (P:839-855), outlier radius 2.5 (P:868); no 1.9mm resample on branch. Consequence: estimator faithful; keep-all trades doubling for whole-bag dirt pushed downstream (stages 3-4).

Stage 3 face separation/split: DIFFER. PAPER: axis-ray sign test picks interior/exterior config with most satisfying points (text:160-162); edge line cut at corner peaks of distance-score distribution (text:164 tail). CODE: corner-peak cut IS faithful (detectSeparateLineSegments len=10 + findPeaks, P:1476+); but no axis-ray test in file (MATLAB check_base_and_rim.m upstream); instead LOOP-SELECT splitRimVsStepRing_213: RING iff 20<=r_med<=35 AND r_std<2 AND h_span<4 AND 50<=count<=500 else RIM, logged whole-bag/all-ring fallbacks (P:~700-750). Consequence: Pot-A-calibrated constants with no paper basis; misfire parks true rim in the ring sidecar (Bl loses it) - stub-lane candidate for the P22 class.

Stage 4 walk/trace: CONTRADICTS. PAPER (text:164): single ordered loop, reordered counter-clockwise using normals and a voting algorithm. CODE getPointsInSequence (P:541-650): greedy walk, no normals/voting/CCW; union-find comps at 5mm largest-first, seed comp[0] (insertion order, arbitrary), adaptive K=clamp(n/10,5,50), GUARD 6mm + forward-dot gate; on starvation TELEPORTS to nearest unvisited dot, cuts only logged (P:640-650), output one concatenated cloud_sequenced never split; zero vote/CCW/equidistant tokens in branch (grep-verified). Consequence: the P22/P12 engine - teleports stitch disjoint pieces into fake-continuous lanes (P12 wrong stretches), arbitrary seed and no CCW give direction flips (P27 class), guard starvation gives stub lanes (P22 turn-away; cf 232 S1 bag=206 cuts at 121/191).

Stage 5 loop selection/rim gate: DIFFER. PAPER (text:177): rim gates std(h,r)<=1.0mm, adjacent variation<=0.1mm, >=20 pts, most-stable wins; enforcement matching-side: rim-interval match is false, discard (text:209). CODE isBreaklineSegARim (P:2512+): clip 3 pts/end, 3mm patch per point, normal-cluster CV, rim iff mean(CV1+CV2)/2>0.12 (P:~2655-2663); DistanceFromAxis variant with axis file (P:2724+, used P:3036); per-segment start/end/isRim index flags (P:3033-3057); labelling only, no in-code discard. Consequence: curvature gate vs h+r gate (0.12 unexplained) over/under-labels; mislabelled rim enters matching (false-positive fuel) or breakline distrusted downstream - P27 class from the labelling side.

Verdict: CONTRADICTS-4 (walk/trace). Stages 1/3/5 DRIFTED; stage 2 SAME-method. Repair order: walk continuity first (split at cuts, seed+direction discipline), then rim-gate recalibration, last input-split hardening; tighter LCS/ICP gates alone treat the symptom.
