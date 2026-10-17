# 50: Full S1 surface re-walk — sequence, not set, holds the signal

**What to deliver:** honest piece-2-to-1 matches at author-like strength — or the measured reason the surface cannot give them.

**Answers:** E1

**Blocked by:** 48-derivative-agreement (T48b direction-mirror: first honest 2-1 edge size9/inlier16 3/3, but 2-5× below ORIG strength sizes 8-19/inliers 30-78; T48a 1.8mm step KILLED; desc branch thin: 11 pts, 42.75mm-detached).

**Status:** results-in

**Working in:** `/data/gpfs/projects/punim2657/pota50_repro/` (build_t50.py, gate_t50.py, render_t50_check.py, run_pota50_stage_B.sbatch, pota50_bundle_B/, t50_lip_check.png — read-only ref: Spartan pota48_repro/ T48b bundle + exp4 S1 Surface_1); E2E run dirs `/data/gpfs/projects/punim2657/sfs_main/pota50_run_3324124{1,3,5}/`

**Starting position:** 48's direction result says SEQUENCE not SET holds the signal — but T48b only re-sequenced the existing 149+35 rows. A full re-walk of OUR S1 surface (Spartan exp4 dirs / pota48 T48b bundle as read-only reference; T48b work dir pota48_repro/) may recover a denser/longer desc branch the greedy walk dropped. Zero ORIG points (44-asterisk rule); ORIG diagnosis-only.

**Rules:** land ONLY with honest p2-p1 edges at ORIG-like strength AND/OR E2E lift ×3 same-binary runs + B ORIG 9/9+15/15 and A 8/8+15/15 green in same runs + B gate 15/15; gate-clean (GT-placed strict must not regress 19/19); lip render (eye-check); prep-side scratch copies; assembler E2E on cure-potA @ bffefb6 with LINK-SHIM-OK + DRIVER-SHIM-OK; no commits; sacct-direct polling; Comments-only ticket edits; repeats ≥3 per condition; count pairs not k/2.

- [x] S1 re-walk arm(s) + gate + E2E ×3 + render
- [x] ORIG-strength honest edges or measured why-not — MEASURED WHY-NOT (surface holds no further lip material)
- [x] Job IDs + sacct states

## Comments (worker, 2026-10-17)

**Arm T50 — full S1 surface re-walk, ZERO ORIG points.** Source: OUR S1 surface
(`pota48_bundle_Bb/SfS_pp/Surfaces/Pot_B_Piece_02_Surface_1.xyz`) + OUR Bl1 lip runs
(rows 0-9 desc, 94-115 asc, md5 dbce9e57 = pure T42 output). Method: ridge-consistent
extension past each Bl1 run end through the S1 cloud (step ≤2.5mm, local-PCA
linearity ≥0.5, |n·n_end| ≥0.7, z < 355.5 seam), then the T48b pipeline (1.8mm uniform
resample, direction-mirror, 1.2mm dedup vs T42 Bl0). 149→187 pts (+3 vs T48b's 184),
4 segs. Non-p2 bundle rims byte-identical to T42; Bl1 untouched.

**Extension measured, not forced.** desc-hi extension terminated immediately with +0:
the 42.75mm desc gap corridor is sheet (ball linearity 0.09–0.32, no ridge spans it).
Only margin growth: desc-lo +5 pts (z 332.5→333.3), asc-hi +6 pts (z 331.6→333.3) —
mostly re-walked ground. Build deterministic (md5 7edce8bc stable across reruns).

**Gate** (GT-placed strict d<2mm & |n·n|>0.85, login-node): 1-2: 19/19 (T48b level,
no regression from 19/19); full-B strict total 592, edge-for-edge identical to T48b;
all non-p2 edges byte-identical. Render eye-checked
(`SfSpp_preprocessing/artifacts/t50_lip_check.png`): new rows ride the p1/p8 mating
rims, no v1-style divergence (note: plot title says "T44" — stale label from the
copied render script; geometry is T50).

**E2E ×3 same-binary** (cure-potA @ bffefb6, BASE-env, LINK-SHIM-OK +
LINK-FORKMAIN-ABSENT-OK + DRIVER-SHIM-OK on all 4 arms ×3 runs, all sacct
COMPLETED 0:0):

| job | B fresh | p2 VERBOSE | 2-1 edge | controls |
|---|---|---|---|---|
| 33241241/43/45 | 4/9+2/15 ×3 identical, seated {1,3,4,7} | gt3/ok0 ×3 | 3/3 runs | B ORIG 9/9+15/15, A ORIG + A fresh 8/8+15/15 ×3 |

**Honest edge strengths (B_fresh_binary.log P43-LCS, 3/3 identical modulo last-bit
FP score noise), T50 vs T48b (job 33239919):**

| edge | T50 | T48b | ORIG scale (ticket 48) |
|---|---|---|---|
| 2-1 | size9/inlier16 (score 0.83) | size9/inlier16 (score 0.71) | FIVE edges, sizes 8–19, inliers 30–78 |
| best honest (8-2) | size11/inlier22 | size11/inlier22 | — |
| p2 edge count | 10 (+1: extra 3-2 size7/inlier18) | 9 | — |

Max honest strength unchanged (size11/inlier22 both); the extra edge inliers 18 vs
the 45–65 beam expansion frontier. p2 starves deterministically 3/3.

**Bottom line.** S1 re-walk NEGATIVE with mechanism: the S1 surface holds no further
lip material beyond what Bl1 already captured — the desc gap corridor is sheet, not
a walkable ridge. Sequence signal (ticket 48's direction result) is now exhausted:
T48b unlocked existence (first honest 2-1 edge), T50 proves no further sequence-side
growth. The remaining gap is edge STRENGTH (honest ≤22 vs frontier 45–65), not
existence — levers live content-side (R1/R3/R4 + column-7 queued from 46) or
beam-side, not in re-walking. No commits; tickets 45/47/49 untouched (read-only);
no lucky-run renders (nothing seated — per ticket-43 rule).

**Successor:** R1/R3/R4 + column-7 queued from 46 (content-side fingerprint levers);
beam-side rerouting held as backup.

**Successor:** R1/R3/R4 + column-7 queued from 46 (order+clip, curvature-slot, thickness semantics).
