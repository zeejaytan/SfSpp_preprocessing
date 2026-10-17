# 77: Overlap-valley reweighting

**What to deliver:** 02-04 seated without the 17mm slide.

**Answers:** E1

**Blocked by:** 76 (landed WHY-NOT-MEASURED, 9 jobs COMPLETED: W1 halved inlier gate / W2 halved angle gate / R1 refinement ablated — all null, seat bit-identical 2.52deg/17.37mm; gate-tightening = wrong family, refinement exonerated; E2E holds 2/3+1/3 x9) + 74 (valley bound: fresh overlap 24.3% at GT vs 45.2% at search seat vs ORIG-at-GT 42.7%; pure single-axis slide; C01-independent).

**Status:** results-in (worker 2026-10-18, COMMIT NOTHING)

**Starting position:** reweight the beam score so the valley peak coincides with truth — one variable each: (a) volume-boost removal, (b) MatchingScore exponent, (c) max_overlap_area_ penalty, (d) symmetry-breaking of your own design. Search-side scratch copies; prep content (S24 swaps) taken as given from 73/74 bundles (read-only). Zero ORIG points in any fix; ORIG evidence-only.

**Rules:** land with 02-04 relative translation toward <=10mm at same rotation + E2E at or above 2/3+1/3 x3 same-binary + controls green (C ORIG 4/4+5/5, A 8/8+15/15) in same runs; renders (eye-check); E2E on cure-potA @ bffefb6 with LINK-SHIM-OK + DRIVER-SHIM-OK; no commits; sacct-direct polling; Comments-only ticket edits; repeats >=3 per condition; SingleOverlapTest@100/RP/CheckGraph-150 stay unless the valley mechanism names them.

- [x] Reweighting arms, one variable each
- [x] Gate + E2E rerun x3 or measured why-not
- [x] Job IDs + sacct states

## Comments (worker, 2026-10-18 — COMMIT NOTHING; lead to commit)

**Verdict: measured why-not — the 17.37mm slide is INSENSITIVE to all four beam-score reweighting arms. No arm moves the 02-04 seat toward ≤10mm (A/B/C bit-identical to base; D +0.03mm the wrong way, negligible). E2E holds 2/3+1/3 ×12 with all controls green on every variant binary. The valley is not a scoring-weight artefact: the slid seat wins the beam on raw rim-coincidence count under every weighting tried.**

**0. Work dir (NEW; 39–76 lanes read-only, untouched).** `/data/gpfs/projects/punim2657/pota77_repro/`: four one-variable search-side overlays over pristine bffefb6 SRC (p76 vehicle: file bind-mounted over `/p40/asm/class/<file>` in-container; SRC tree untouched, rev-parse bffefb6 asserts pass in every job; each overlay `diff`-verified single-hunk vs pristine):
- A-novl: `ranking_system.cpp` SortRoot tanh volume-weight removed (raw inlier sum; the `inlierCalculate` live path already runs volume_weight=false, so this was the only live volume term).
- B-exp10: `feature_matching.cpp` MatchingScore `pow(count,1.2)` → `pow(count,1.0)` (raises all RP scores, disproportionately punishing high-count slides).
- C-ovpen: `ranking_system.cpp` CheckGraphPlausibility extra gate `max_overlap_area_ > 75` (half of CheckGraph-150; S=150 param untouched — strictly tighter, no relaxation).
- D-density: `ranking_system.cpp` SortRoot scores inlier-density (1000×inlier/rim-points) instead of raw inlier — breaks the raw-count symmetry by design.
Prep content taken as given: `pota74_bundle_C_S24` referenced read-only (md5 bundle guards pass ×12). Zero ORIG points in any fix; ORIG evidence-only. SingleOverlapTest@100 / RP(score>10 kill) / CheckGraph-150 param untouched. Channel efficacy: new in-container assert `VARIANT-OVERLAY-OK <file>` ×5 in all 12 jobs (p76 lacked this); D additionally shifts the seat +0.03mm ×3 (live overlay, negligible effect).

**1. E2E ×3 per variant, same-binary within variant (p76 vehicle: k=5/b=3 shim, A STEPS=8, C STEPS=4, 5 arms/job; sacct-direct polling). All 12 jobs sacct COMPLETED 0:0, all 60 containers exit 0.**

| variant jobs (sacct COMPLETED 0:0) | A_orig | A_fresh | C_orig | C_1C | C_S24 |
|---|---|---|---|---|---|
| A: 33299407/08/09 (15:01/13:37/09:50) | 8/8+15/15 ×3 | 8/8+15/15 ×3 | 4/4+5/5 ×3 | 2/2+1/1 ×3 | 2/3+1/3 ×3 (212/17) |
| B: 33299591/604/605 (15:35/14:42/13:09) | 8/8+15/15 ×3 | 8/8+15/15 ×3 | 4/4+5/5 ×3 | 2/2+1/1 ×3 | 2/3+1/3 ×3 (212/17) |
| C: 33299606/07/08 (13:41/13:01/15:00) | 8/8+15/15 ×3 | 8/8+15/15 ×3 | 4/4+5/5 ×3 | 2/2+1/1 ×3 | 2/3+1/3 ×3 (212/17) |
| D: 33299609/10/11 (15:02/14:15/13:15) | 8/8+15/15 ×3 | 8/8+15/15 ×3 | 4/4+5/5 ×3 | 2/2+1/1 ×3 | 2/3+1/3 ×3 (212/17) |

Asserts per job: LINK-SHIM-OK ×5 + LINK-FORKMAIN-ABSENT-OK ×5 + DRIVER-SHIM-OK ×5 (all 12 jobs; spot-verified per variant + VARIANT-OVERLAY-OK ×5 in all 12). Bit-identical tallies ×3 within each variant (pruned-count noise only: A_fresh 119/119/119, C_orig 40). Snapshots: C_S24 T_0,T_1,T_3 + C_1C T_1,T_3 per RUNDIR. RUNDIRs `/data/gpfs/projects/punim2657/sfs_main/pota77_run_{33299407..33299611}/`, fetch tgz in each. (Vehicle note: C-arm dir is `C_1C_*`, the job-summary loop prints the `C_C1c` label empty — read `C_1C_binary.log`; same harmless label typo as p76.)

**2. 02-04 seat (probe77.py = probe76 logic repointed; relative-edge currency). Base from 74: rel-ang 2.521° / rel-tr 17.37mm.**

| variant | 02-04 rel-ang / rel-tr ×3 | vs base |
|---|---|---|
| A (novol) | 2.52°/17.37mm ×3 bit-identical | NULL |
| B (exp10) | 2.52°/17.37mm ×3 bit-identical | NULL |
| C (ovpen>75) | 2.52°/17.37mm ×3 bit-identical | NULL |
| D (density) | 2.56°/17.40mm ×3 bit-identical | +0.03mm/+0.04° wrong way, negligible |

C_orig relative edges SEATED in all 12 runs (02-04 ~0.4°/~2.8mm) — true-rim seating survives every reweight. C arm inference (sound, no log-read needed): the seated slide graph passed CheckGraph including the new >75 gate (killed graphs can't seat), so the slide's max 3D overlap area is ≤75 — the slide wins on rim-coincidence count (74's 45.2% share), NOT on 3D overlap area. Renders eye-checked (estimated pair same offset shape as GT pair in all variants): `artifacts/pota77/C77_{Anovol,Bexp10,Covpen,Ddensity}_seating_R1.png` (sources in `pota77_repro/`).

**3. Landing check vs the bar.** Residual toward ≤10mm ✗ (unmoved in all arms — the "or measured why-not" branch carries this ticket). E2E at/above 2/3+1/3 ×3 same-binary ✓ (×12). Controls green same runs ✓ (A 8/8+15/15 orig+fresh ×12; C ORIG 4/4+5/5 ×12). Repeats ≥3 ✓. Zero ORIG points ✓. No gate relaxation ✓. Renders eye-checked ✓ (4 PNGs). Spartan leftovers: `pota77_repro/` + 12 `pota77_run_*` dirs only.

**Mechanism read for lead:** with 76's result (coincidence-gate halving + refinement ablation all null) plus this ticket (volume-weight removal, RP-exponent flattening, overlap-area halving, density re-rooting all null — 21 same-vehicle repeats total), the reweighting family is exhausted: no per-edge/per-graph scalar reweight moves the seat because the slid configuration commands a strict-majority of tight rim coincidences at any gate and any weighting. Remaining directions: (i) change WHAT coincides — prep-side rim-shape correction (the fresh rim is the shifted content; 67/68 walk-level re-extraction for C01's lip shows the level that still moves things); (ii) a non-scalar beam criterion (e.g. multi-hypothesis diversity / slide-geometry detector), which is new method work, not a weight tweak. Thesis write-up: quote binary 2/3+1/3 WITH the 17.37mm single-axis-slide caveat; now add that the floor resists 7 remedy arms across 21 same-vehicle repeats (76: gates+refinement; 77: four score reweights).
