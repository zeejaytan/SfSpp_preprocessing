# 45: Honest lip discovery — find p2's lower lip in OUR data, no ORIG template

**What to deliver:** p2's lower lip from OUR chain only — or the measured reason it isn't there.

**Answers:** E1

**Blocked by:** 44-p2-wall-lip (v2 proves the beam seats p2 GIVEN the lip; v1 proves the S0 face-walk is the wrong search).

**Status:** results-in

**Working in:** `/data/gpfs/projects/punim2657/pota45_repro/` (build_t45_honest.py, gate_t45.py, probe_texture.py, run_t45_*.sbatch, pota45_bundle_B/, t45_lip_check.png); E2E run dirs `/data/gpfs/projects/punim2657/sfs_main/pota45_run_3323923{0,1,2}/`

**Starting position:** v2's winning lip was traced from shipped ORIG Bl0 (gap-clean ≤1.8mm) — reference geometry, not discovery. Our chain's own p2 Bl0 (149 pts, T42) lacks the lower lip entirely: asc-bottom rows 0–21 + desc-bottom rows 122–149 exist in ORIG but not in fresh. v1 showed S0 (= wall face after T21 split) cannot be walked into a lip. Open hypotheses: (a) walk terminates early at the T21 split boundary — the lip points may sit in S1 or in the discarded fused region; (b) the ordering walk never descends to the lip rows (termination condition); (c) the points are genuinely absent from our surfaces (extraction-stage loss — check S0/S1 clouds at the lip location against ORIG surface points).

**Rules:** ZERO ORIG-derived points in any claimed fix (ORIG data is diagnosis-only: locate-compare, never copy); land ONLY with B gate 15/15 + B fresh E2E improvement ×3 same-binary runs + B ORIG 9/9+15/15 and A 8/8+15/15 green in same runs; seating render (eye-check); prep-side work in scratch copies; assembler E2E on cure-potA @ bffefb6 with LINK-SHIM-OK + DRIVER-SHIM-OK; no commits; sacct-direct polling; Comments-only ticket edits.

- [x] Lip-loss diagnosis: where OUR chain drops p2's lower lip (S0/S1 clouds vs ORIG at lip rows)
- [x] Honest recovery built + gate-verified (SFS-T45, zero ORIG points) — geometry recovered
- [ ] B fresh E2E improvement ×3 + controls green — NOT MET (measured limit instead, 3/3 + all controls green)
- [x] Job IDs + sacct states

**Successor:** cross-pot generalization (C–J share the drowning shape); axisang scoring term held as backup.

## Comments (worker results, 2026-10-17)

**Diagnosis (all sacct-verified sbatch probes).** ORIG sub-seam lip (z<355.5, n=50): S1 covers 100% within 2mm
(med 0.59, max 1.32) vs S0 only 22% (med 4.04) → hypothesis-(a) PROVEN: the lip geometry lives in S1, the S0
face-walk (v1) searches the wrong surface. p2 Bl1 (S1-derived, 116 pts, md5 dbce9e57 identical in pota42_B and
pota44_B = pure T42 output, zero ORIG) holds both lip branches as unordered runs: rows 0–9 (desc lip,
z 332.5→336.7) + rows 94–115 (asc lip, z 354.9→331.6); rows 9→10 teleport 38mm (336.7→374.7) inside Bl1 seg 4–14.
Junctions to T42 Bl0: asc run high-z end 5.04mm off (v2 ORIG asc was 4.9mm); desc run 42.75mm detached.
Assembler reads ONLY `Breaklines/*_Breakline_0.pcd` (Bl1 invisible) — so the lip existed in OUR data all along,
filed where the assembler never looks.

**Honest recovery SFS-T45** (build_t45_honest.py, cp-a tree pota45_B from pota42_B): appended both Bl1 runs
resampled 1.9mm (T42 algorithm: lerp/nlerp/curvature central-diff cap 1.0), dedup 1.2mm, one segment per run.
Bl0 149→183 pts (+11 desc rows 149–159, +23 asc rows 160–182), 4 segs, md5 be0b15e4. Seating render
t45_lip_check.png eye-checked: both branches ride the mating rims, no v1-style divergence
(copy: `C:\PR\SfSpp_preprocessing\artifacts\t45_lip_check.png`).

**Gate** (gate_t45.py, job 33239147 COMPLETED): 1-2: 1/1→17/18 (≈ v2's 17/17); 2-8: 0/0→9/9 (v2 26/26, partial —
Bl1 holds no more sub-seam desc rows); 2-4 7/7 unchanged; all 12 non-p2 edges byte-identical.

**E2E ×3 same-binary** (run_pota45_stage_T45.sbatch, BUN pota45_bundle_B, P43 VERBOSE BASE-env; cure-potA @ bffefb6,
LINK-SHIM-OK + DRIVER-SHIM-OK; new LCS edges in run 1 prove the T45 bundle loaded):

| job (sacct) | B fresh | p2 VERBOSE | B orig | A orig | A fresh |
|---|---|---|---|---|---|
| 33239230 COMPLETED 0:0 | 4/9+2/15 | gt3/ok0 NOT seated | 9/9+15/15 | 8/8+15/15 | 8/8+15/15 |
| 33239231 COMPLETED 0:0 | 4/9+3/15 | gt3/ok0 NOT seated | 9/9+15/15 | 8/8+15/15 | 8/8+15/15 |
| 33239232 COMPLETED 0:0 | 4/9+2/15 | gt3/ok0 NOT seated | 9/9+15/15 | 8/8+15/15 | 8/8+15/15 |

(Seated sets identical all 3 runs {1,3,4,7}; run 2's printed 3/15 vs 2/15 is the known T43 last-bit FP tally noise,
not an extra seating. T42 BASE for scale: 4/9+2/15 ×2.)

**Measured wall (why geometry ≠ seating).** LCS dump, T45 vs T42-BASE (job 33218437): p2 edges 8→10
(new 5-2 size7/inlier16, new 7-2 size8/inlier18; 3-2 inlier 16→18; total p2 inliers 104→140, +35%) — but ZERO
p2-p1 edges and no new p2-p8 edge (8-2 size11/inlier22 unchanged = T42's patch remnant). Best honest edge inlier 22
vs beam frontier top-10 45–65 → p2 still starves deterministically 3/3. v2's ORIG branches for comparison: 9 p2
edges with 8-2 size14/inlier51, 4-2 size10/inlier46 — LONG+STRONG true edges the honest runs never produce
(honest max size 10). Note: okpair verdicts reflect final placement vs GT, not dumped-edge existence — v2 seated
2-1 with no 1-2/2-1 line in its own dump (64 lines, zero x=1), so the gap is beam-level edge strength, not one
missing match. Root cause at feature level (filter.cpp CalculateFeatureAxisless): LCS matches quantized
DERIVATIVES (7-tap LanczosDiffLow + Gaussian on Dist/Height/Theta); gate-strict proximity does not imply
derivative-run agreement. Texture-roughness probe (job 33239481 COMPLETED): honest-asc ≈ Bl1-native ≈ ORIG
(d2z 0.223/0.233/0.269, d2r 0.153/0.161/0.249) → the lerp-smoothing hypothesis is KILLED; resample preserved
texture because Bl1 native steps were already ~1.9mm. Standing: honest true-runs fragment at ≤10 (same ~1-in-5
out-of-bin disease as T42: 9–15 vs ORIG 18–34); desc side is thin by material (11 pts), not by technique.

**Bottom line for the lead.** Half (a) of the ticket question is answered honestly: the lip IS in OUR chain (S1/Bl1)
and IS geometrically recoverable with zero ORIG points. Half (b) is a measured negative: the recovered lip does
not seat p2 3/3 with all controls green — the beam needs long/strong true edges (size ~14/inlier ~45+) that
Bl1-derived rows don't yield. Untested, explicitly NOT claimed: decimation-instead-of-lerp (preserve native
sampling), or an S1 re-walk with edge-aware termination to grow longer desc material — ticket-46 material with
its own ×3 bar. No commits made; ticket-44 run dirs untouched (read-only).
