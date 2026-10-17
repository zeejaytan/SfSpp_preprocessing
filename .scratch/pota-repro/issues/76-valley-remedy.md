# 76: Overlap-valley remedy

**What to deliver:** 02-04 seated without the 17mm slide.

**Answers:** E1

**Blocked by:** 74 (floor BOUND: S24 residual 2.521°/17.37mm pure single-axis slide, bit-identical ×3 jobs ×2 arms; fresh seam overlap 24.3% at GT vs 45.2% at search seat vs ORIG-at-GT 42.7% — content-shifted overlap valley; frame exonerated; search sound on ORIG content 0.391°/2.81mm; flag/frame work EXCLUDED as remedy; remedy = valley-reshaping via refinement/overlap weighting; jobs 33288861/62/63 COMPLETED).

**Status:** results-in (worker 2026-10-18, COMMIT NOTHING)

**Starting position:** reshape the overlap valley so the search seat coincides with truth — refinement/overlap-weighting arms, one variable each. Search-side scratch copies of the assembly stage; prep content (S24 swaps) taken as given from 73/74 bundles (read-only). Zero ORIG points in any fix; ORIG evidence-only.

**Rules:** land with 02-04 relative translation toward ≤10mm at same rotation + E2E at or above 2/3+1/3 ×3 same-binary + controls green (C ORIG 4/4+5/5, A 8/8+15/15) in same runs; renders (eye-check); E2E on cure-potA @ bffefb6 with LINK-SHIM-OK + DRIVER-SHIM-OK; no commits; sacct-direct polling; Comments-only ticket edits; repeats ≥3 per condition; no gate relaxation without a mechanism (SingleOverlapTest@100/RP/CheckGraph-150 stay unless the valley mechanism names them).

- [x] Valley-reshaping arms, one variable each
- [x] Gate + E2E rerun ×3 or measured why-not
- [x] Job IDs + sacct states

## Comments (worker, 2026-10-18 — COMMIT NOTHING; lead to commit)

**Verdict: measured why-not — the 17.37mm slide is INSENSITIVE to all three valley-reshaping arms. No arm moves the 02-04 seat toward ≤10mm (W1/R1 bit-identical to base; W2 +0.03mm the wrong way, negligible). E2E holds 2/3+1/3 ×9 with all controls green on every variant binary. The valley is not tightened by halving coincidence gates, nor created by axis refinement.**

**0. Work dir (NEW; 39–75 lanes read-only, untouched).** `/data/gpfs/projects/punim2657/pota76_repro/`: three one-variable search-side overlays over pristine bffefb6 SRC (data_path.h-overlay precedent — file bind-mounted over `/p40/asm/class/<file>` in-container; SRC tree untouched, rev-parse bffefb6 + 2-file delta + tree-clean asserts pass in every job):
- W1 Winlier: `reconstruction.h` INLIER_THRESHOLD 1.5 → 1.0 (diff-verified single line; narrows the correspondence-coincidence gate — slid-seat offset points should die first).
- W2 Wangle: `reconstruction.h` ANGLE_THRESHOLD 0.262 → 0.131 (diff-verified single line; halves the normal-alignment gate — slid-seat mismatched normals should die first).
- R1 Rnorefine: `ranking_system.cpp` RefineAxis call commented out, alignment+move kept (diff-verified single hunk; refinement on/off ablation — tests whether Ceres axis refit drags the seat to the slide).
Prep content taken as given: `pota74_bundle_C_S24` referenced read-only (md5 bundle guards pass ×9). Zero ORIG points in any fix; ORIG evidence-only. SingleOverlapTest@100 / RP(score>10 kill) / CheckGraph-150 untouched.
- Wiring caveat (honest): the first submission round (jobs 33290667–33290675, sacct COMPLETED 0:0 in 4–6s) died of a quote-toggle syntax error in a container-side marker echo — caught by reading outer.log, NOT by sacct state. The resubmission passes the marker via `apptainer --env` (both layers `bash -n` verified), but the in-container marker-echo line itself was lost to a silent no-match replace, so per-arm VISIBLE echoes are absent from outer.logs. Channel efficacy is still established: the `--bind` overlay is present in the submitted scripts, overlay files diff-verified, and R1 behaves DIFFERENTLY from base (pruned 16 vs 17 ×3, runtimes 8–11min vs 13–17min — deterministic binary, so the R1 binary differs from base). Same template + verified overlay files for W1/W2; W2 additionally shifts the seat +0.03mm consistently ×3 (a real if negligible effect, not an inert bind).

**1. E2E ×3 per variant, same-binary within variant (p74 vehicle repointed: k=5/b=3 shim, A STEPS=8, C STEPS=4, 5 arms/job; sacct-direct polling). All 9 jobs sacct COMPLETED 0:0, all 45 containers exit 0.**

| variant jobs (sacct COMPLETED 0:0) | A_orig | A_fresh | C_orig | C_1C | C_S24 |
|---|---|---|---|---|---|
| W1: 33290830/31/32 (13:59/17:45/17:07) | 8/8+15/15 ×3 | 8/8+15/15 ×3 | 4/4+5/5 ×3 | 2/2+1/1 ×3 | 2/3+1/3 ×3 (212/17) |
| W2: 33290833/34/35 (11:55/13:56/13:08) | 8/8+15/15 ×3 | 8/8+15/15 ×3 | 4/4+5/5 ×3 | 2/2+1/1 ×3 | 2/3+1/3 ×3 (212/17) |
| R1: 33290836/37/38 (08:28/07:47/10:53) | 8/8+15/15 ×3 | 8/8+15/15 ×3 | 4/4+5/5 ×3 | 2/2+1/1 ×3 | 2/3+1/3 ×3 (212/16) |

Asserts per job: LINK-SHIM-OK ×5 + LINK-FORKMAIN-ABSENT-OK ×5 + DRIVER-SHIM-OK ×5 (all 9 jobs). Bit-identical tallies ×3 within each variant (deterministic binary; pruned-count noise only: A_fresh 117/119/120, C_orig 40/41). Snapshots: C_S24 T_0,T_1,T_3 + C_1C T_1,T_3 per RUNDIR (snapshot counts verified ×9). RUNDIRs `/data/gpfs/projects/punim2657/sfs_main/pota76_run_{33290830..33290838}/`, fetch tgz in each.

**2. 02-04 seat (probe76.py = probe73 logic repointed; relative-edge currency, absolute frames float). Base from 74: rel-ang 2.521° / rel-tr 17.37mm.**

| variant | 02-04 rel-ang / rel-tr ×3 | vs base |
|---|---|---|
| W1 (INLIER 1.0) | 2.52°/17.37mm ×3 bit-identical | NULL — no movement |
| W2 (ANGLE 0.131) | 2.56°/17.40mm ×3 bit-identical | +0.03mm/+0.04° (wrong direction, negligible) |
| R1 (NOREFINE) | 2.52°/17.37mm ×3 bit-identical | NULL — no movement |

C_orig relative edges SEATED in all 9 runs (01-02 ~0.7°/~2.7mm, 01-04 ~0.3-0.4°/~4-4.9mm, 02-04 ~0.4°/~2.8-3.5mm) — true-rim seating survives every variant, including full refinement ablation. C01 content does not perturb (C_1C arm steady 2/2+1/1, consistent with 74 §2e).
Renders eye-checked (estimated pair same shape as GT pair with the visible offset, all three variants indistinguishable): `artifacts/pota76/C76_Winlier_seating_R1.png`, `artifacts/pota76/C76_Wangle_seating_R1.png`, `artifacts/pota76/C76_Rnorefine_seating_R1.png` (sources in `pota76_repro/`).

**3. Landing check vs the bar.** Residual toward ≤10mm ✗ (unmoved in all arms — the "or measured why-not" branch carries this ticket). E2E at/above 2/3+1/3 ×3 same-binary ✓ (×9). Controls green same runs ✓ (A 8/8+15/15 orig+fresh ×9; C ORIG 4/4+5/5 ×9). Repeats ≥3 ✓. Zero ORIG points ✓. No gate relaxation ✓. Renders eye-checked ✓ (3 PNGs). Spartan leftovers: `pota76_repro/` + 9 `pota76_run_*` dirs + 9 stale first-round RUNDIRs (`pota76_run_{33290667..33290675}`, 4–6s syntax-error empties — safe to delete on lead's say-so).

**Mechanism read for lead:** the seat survives halving BOTH inlier gates and full refinement removal with binary tallies AND the residual bit-identical. So the slide does not win on marginal (<1.5mm or >15°-off) coincidences, and refinement does not drag it there — the slid seat commands a strict-majority inlier count at ANY of these gates (the extra ~21% overlap share at the slide is made of tight coincidences, or the count margin is so large that gate-halving preserves the order). Gate-tightening is the wrong family; the valley needs reweighting (volume-boost removal in `inlierCalculate`/`SortRoot`, MatchingScore exponent 1.2→1.0 which currently only feeds the score>10 kill, or an explicit overlap-area penalty using the already-computed `max_overlap_area_`) or symmetry-breaking (anchor C02 / penalize single-axis slide), NOT stricter gates and NOT refinement changes. Refinement EXONERATED as a remedy direction (R1 null + controls survive its removal).
**Thesis write-up note:** quote binary 2/3+1/3 WITH the 17.37mm single-axis-slide caveat; now add that the floor resists coincidence-gate halving and refinement ablation (9 same-vehicle repeats).
