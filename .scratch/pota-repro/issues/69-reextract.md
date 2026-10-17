# 69: Walk-level re-extraction — trace one loop, not two

**What to deliver:** regenerated C Bl_0 content sitting ~1-2mm off shipped — gate + E2E recovery.

**Answers:** E1

**Blocked by:** 68 (split-select NULL both arms: no in-file loop on shipped contour; in-file options exhausted; jobs 33279876/33279902/33279903 COMPLETED) + 67 (guilty stage getPointsInSequence greedy K=50 no heading guard; enabler PCL BoundaryEstimation r=4mm admitting both lip faces; repair direction: split-then-select before sequencing + forward-cone guard + inner-loop select) + 21 (RegionGrowing split precedent).

**Status:** results-in — walk-level guards only re-tile the offset (GUARD one loop hugging ORIG ~4mm off; SPLIT destructive n=18; RADIUS degenerates/explodes); offset lives UPSTREAM in boundary-estimator output; no E2E per Rules

**Starting position:** the true lip was never traced, so no re-sorting recovers it. Re-extract at the walk level: forward-cone guard in getPointsInSequence (heading/component guard), one-loop-per-component emission, BoundaryEstimation radius that admits one lip face. Fresh-only scratch prep copies; bundle references pota68/pota67/pota39 C bundles (read-only). Zero ORIG points in any fix (44-asterisk rule); ORIG evidence-only. C02 axle still finder-side (orthogonal). C03 is the green control (rotation-only piece — must stay seated).

**Rules:** land ONLY with fresh-vs-shipped ~1-2mm AND jumps→0 AND gate recovery toward ORIG per-edge AND E2E above 0 ×3 same-binary + controls green (C ORIG 4/4+5/5, A 8/8+15/15, C03 seated) in same runs; renders (eye-check); prep-side scratch copies; assembler E2E on cure-potA @ bffefb6 with LINK-SHIM-OK + DRIVER-SHIM-OK; no commits; sacct-direct polling; Comments-only ticket edits; repeats ≥3 per condition; no gate relaxation without a mechanism.

- [ ] Walk-level arms, one variable each
- [ ] Gate + E2E rerun ×3 or measured why-not
- [ ] Job IDs + sacct states

**Successor steer (from 68):** E/I/J — check GT-seated fresh-vs-shipped distance first; if ~5mm + doubled counts, skip to re-extraction.

**Comments (worker, 2026-10-17, measured why-not — bar not met, no E2E):**
- Vehicle: pota69_repro/src = PREP-COPY pipeline sources (adaptive BoundaryEstimation r≈6.5–7.2mm, K=spacing-adaptive, T13 second-chance), NOT the live sfs_preprocessing file. Env-gated patch only (POTA69_GUARD / POTA69_SPLIT, default off); RADIUS via existing SFSPP_BOUNDARY_RADIUS_MM hook. No other source touched; nothing committed.
- Jobs (all COMPLETED): build 33280869(FAILED-make, log-truncated)→33281040(FAILED, Eigen aligned_allocator swap)→33281127 OK; edge arms 33281444(FAILED, set-u local bug)→33281705(CANCELLED, binary run outside container, exit 127)→33281711 OK (BASE/GUARD/SPLIT/RADIUS); R4 leg 33282098; repeat 33282622 (16/16 STABLE).
- Reproduction proof: BASE Bl_0 byte-identical to p39 bundle all 4 pieces (cmp). BASE==p39 is repeat ×2 for baseline; arms ×2 via repeat job (all STABLE = deterministic walks).
- Gate (strict inliers per GT edge 1-2/1-3/1-4/2-3/2-4; jumps>5mm per piece p1–p4):
  BASE: jumps 3,3,1,2 / 0,1,4,0,16 | GUARD: jumps 1,0,0,2 / 0,0,1,0,14
  SPLIT: n=18,106,61,191, jumps 1,1,1,2 / 0,0,0,0,0 (p1 sphere-march retry blowup r=2144mm on 19-pt input)
  RADIUS=2.0: boundary explodes (9175 vs 343 pts), coverage 0.0002→0.036, 110 jumps / 0,0,0,0,0 — degenerate, not a loop isolation
  R4=4.0 (supplementary): boundary sane (411/178/240/219/243), jumps 1,1,1,2 / 3,2,1,0,0 — worse than BASE
- Fresh-vs-shipped at GT (full-contour NN median): C01/C02/C04 stay 5–6mm off ORIG in EVERY arm (BASE 5.61/6.07/5.48; GUARD 4.15/6.01/5.46; R4 5.04/5.91/5.46); C03 green control ~1mm seated in all arms (SPLIT kept-run 0.71mm/100%<2mm but n=61, gate 0 — fragment, not a loop).
- Eye-check (pota69_repro/C01_BASE|GUARD|R4|SPLIT.png, C04_BASE|GUARD.png): GUARD C01 traces ONE loop hugging ORIG's shape but offset ~4mm; BASE shows 4 concatenated runs wandering off-contour. Guard fixes the walk concatenation, not the ~4–6mm boundary-cloud offset feeding it.
- Verdict: no arm reaches jumps→0 AND gate recovery AND ~1–2mm, so per Rules no E2E×3 (GUARD's single edge 2-4:14 cannot assemble the graph; controls N/A without E2E). Mechanism: the offset lives UPSTREAM of the walk (boundary estimator output), walk-level guards only re-tile it. Next variable is boundary detection input (radius multiplier/clamp, or pre-walk cloud selection), not walk logic.
