# 48: Derivative agreement — the honest lip in a signature the matcher accepts

**What to deliver:** p2 LCS edges including p2-p1 from honest geometry — or the measured reason derivative-runs reject it.

**Answers:** E1

**Blocked by:** 45-honest-lip-discovery (SFS-T45 geometry recovered, zero ORIG; E2E negative 3/3: best honest inlier 22 vs frontier 45-65; lerp-smoothing hypothesis killed by texture probe).

**Status:** results-in

**Working in:** `/data/gpfs/projects/punim2657/pota48_repro/` (build_t48.py, gate_t48.py, run_pota48_stage_{A,B}.sbatch, pota48_bundle_B{a,b}/, t48_lip_check_{a,b}.png); E2E run dirs `/data/gpfs/projects/punim2657/sfs_main/pota48_run_33239830,33239917,33239918` (T48a) `{,33239919,33239920,33239921}` (T48b)

**Starting position:** the matcher compares quantized Lanczos/Gaussian derivative runs, not raw shapes. SFS-T45's lip is geometrically right (gate 1-2: 17/18, render eye-checked) but its derivative signature scores half the frontier. Untested options scoped in 45: (a) decimation-variant (resample the honest lip at ORIG-like 1.8mm uniform step — 46 H1 — so derivative quantization matches); (b) S1 re-walk (re-walk the S1 lip region with the ordering walk so the point sequence, not just the set, mirrors ORIG structure). Texture/smoothing is NOT the cause (probe-killed).

**Rules:** ZERO ORIG-derived points (ORIG is diagnosis-only); land ONLY with p2 LCS edges incl. p2-p1 + E2E lift ×3 same-binary runs + B ORIG 9/9+15/15 and A 8/8+15/15 green in same runs + B gate 15/15; seating render (eye-check); prep-side work in scratch copies; assembler E2E on cure-potA @ bffefb6 with LINK-SHIM-OK + DRIVER-SHIM-OK; no commits; sacct-direct polling; Comments-only ticket edits. NOTE ticket-43 metrology: repeats ≥3 per condition; count pairs not k/2.

- [x] Decimation-variant and/or S1 re-walk arms
- [ ] p2-p1 LCS edge + E2E lift ×3 + controls green
- [x] Job IDs + sacct states

## Comments (worker, 2026-10-17)

**Arms (both ZERO ORIG points; base T42 Bl0 149pts + OUR Bl1 lip rows 0-9/94-115, md5 dbce9e57 = pure T42 output).**
T48a = 1.8mm uniform resample (46-H1 ORIG step), T45 direction. T48b = 1.8mm + direction-mirror
(blocks reversed so traversal mirrors ORIG: asc run ascends 331→355, desc run descends — T45 ran both
opposite). Both 149→184 pts (+11 desc/+24 asc), 4 segs, junctions identical to T45 (asc 5.04mm, desc 42.75mm
detached). Non-p2 bundle rims byte-identical to T42; Bl1 untouched.

**Gate** (GT-placed strict d<2mm & |n·n|>0.85, login-node): 1-2: 17/18 (T45) → 19/19 (BOTH T48 arms);
2-8 9/9 unchanged; all non-p2 edges identical. Geometry renders eye-checked, both branches ride mating
rims, no v1-style divergence (`SfSpp_preprocessing/artifacts/t48_lip_check_{a,b}.png`).

**E2E ×3 same-binary per arm** (cure-potA @ bffefb6, BASE-env, LINK-SHIM-OK + DRIVER-SHIM-OK, all sacct COMPLETED 0:0):

| job | arm | B fresh | p2 VERBOSE | p2-p1 edge | controls |
|---|---|---|---|---|---|
| 33239830/17/18 | T48a | 4/9+2/15 ×3, seated {1,3,4,7} | gt3/ok0 ×3 | 0/3 runs | B ORIG 9/9+15/15, A 8/8+15/15 ×3 |
| 33239919/20/21 | T48b | 4/9+2/15, 4/9+2/15, 3/9+2/15* | gt3/ok0 ×3 | 1/3 runs each | all green ×3 |

*33239919's 3/9 (seated {1,3,4} vs {1,3,4,7}) is the ticket-43 3-7 50mm-gate knife-edge wobble, not an arm effect.

**Derivative-agreement findings.**
(1) Step size is NOT the lever: T48a's p2 LCS edges are near-copies of T45's (same 10 edges, inliers ±0–4,
best 24 vs 22) — a 5%-finer uniform step leaves quantized derivative runs unchanged. H1-step hypothesis KILLED.
(2) Direction IS load-bearing for existence: T48b produces an honest p2-p1 LCS edge 3/3 identical runs
(x=2 y=1 size9 score0.71 inlier16 axisang0.31) — the first honest 2-1 edge ever; T45/T48a have zero.
But it seats nothing: ORIG's 2-1 for scale is FIVE edges sizes 8–19, inliers 30–78. Honest size9/inlier16
sits ~40th+ globally vs the 45–65 expansion frontier → p2 starves deterministically 6/6.
(3) Measured reason derivative-runs reject the honest lip: direction-mirroring unlocks run agreement at one
position (the asc contact), but the honest runs stay short (max size 10–11 vs ORIG 19) and weak (max inlier
24 vs 78) — the desc branch is thin by material (11 pts, 42.75mm-detached) and contributes no 2-1/2-8 strength.

**Bottom line.** Partial delivery: p2-p1 LCS edge from honest geometry EXISTS (T48b 3/3) but E2E lift NOT
met (p2 ok0 6/6, B fresh 4/9+2/15 both arms, all controls green). No seating render (nothing seated — per
ticket-43 rule, no lucky-run renders). No commits; tickets 45/47 untouched (read-only). Full S1 re-walk
(re-traversing S1 surfaces with the ordering walk) remains untested — the direction result says sequence,
not set, is where the remaining signal lives.

**Successor:** cross-pot generalization of whatever seats p2 (D–J share the drowning shape); R1/R3/R4 + column-7 queued from 46.
