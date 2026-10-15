# 09: Pristine axle repair (smallest fix that finds the shipped axles)

**What to build:** the smallest change to the author's chain that makes it find the shipped Pot A axles — one repair variable at a time against the frozen 08 baseline, in the pristine tree (fork patch ported only by hand-read lines, never by copying fork files).

**Answers:** E1

**Blocked by:** 08-pristine-axle-repro.

**Status:** results-in — KILL VERDICT. Lead review 2026-10-15: repair table + diffs + job IDs all present; jobs 33067510/33067737/33069665/33069931/33070192 COMPLETED 0:0 per sacct (execution confirmed); held-out protocol honoured (calibrated 01–04, tested 05–08 frozen); scorer validated (P03 passes, shipped self-scores 0/0 — failures are finder failures). The author's path is fixable by repair: NO — 1/8. Redesign is the lead's call; ticket 10 waits on it.

**Pristine-only rule (binding):** work in a pristine-tree copy. Fork files stay unread; a repair idea that needs a fork line re-derive it from the paper + pristine code or drop it.

- [ ] Repairs tried one at a time, each with before/after per-piece direction + position errors vs shipped axles (same metric as 08)
- [ ] Stop rule: first repair set reaching ≤5° and ≤2mm on 8/8 wins; report it exactly (file:line diff). No second variable while the first is unmeasured
- [ ] Kill branch: if three single-variable repairs move nothing, stop and report the numbers — the path is then declared unfixable-by-repair and the finding routes to a redesign ticket (lead's call, not the worker's)
- [ ] Comments section: repair table (change → median/worst before → after) + winning diff or kill verdict

## Comments (worker, 2026-10-15)

Tree run: fresh clone upstream https://github.com/DominicoRyu/SfSpp_preprocessing @ d5ee6865
to Spartan /data/gpfs/projects/punim2657/Temp/potsac-p09-pristine (`git rev-parse HEAD` =
d5ee6865ab1e585d18175670a0cd834e846d4490). Pristine tree itself never modified — R1 is an
added shim + symlink farm, R2/R3 are overlay dirs shadowing pristine files on the MATLAB
path (order: shim, r3fix, r2fix, pristine). MATLAB R2025b, sapphire compute node.
Paper refs = C:\PR\papers\text\sfspp-2502.13986v1.md:169-177. No fork files opened, nothing
committed. Answer key = sfs_main/original_samples/SfS_pp/Axes/Pot_A_Piece_0i_Axis.xyz.
Metric: per shipped axis, direction error deg (sign-ambiguous angle) + radial position
error mm (perp distance from shipped pos to estimated line); piece passes iff ALL its
shipped axes are ≤5° AND ≤2mm. Bar: 8/8.

Repair table (pass counts = pieces fully within bar; errors = worst-over-shipped per piece):

| Stage | Change | 01 (derr,rerr) | 02 | 03 | 04 | 05 | 06 | 07 (3 axes) | 08 (2 axes) | Pass |
|---|---|---|---|---|---|---|---|---|---|---|
| 08 baseline | none | no axle (loader) | — | — | — | — | — | — | — | 0/8 |
| R1 | +shim/load_root_dir.m, 16 Plt_-name symlinks -> shipped Pot_A surfaces (no pristine file touched) | loader OK, vote crash | same | same | same | same | same | same | same | 0/8, blocker moved loader->vote |
| R2 | compute_cao_error.m:19-22 repmat axis slices before cross() (vote-only top-1 shown) | 0.63,2.89 | 0.94,3.94 | 0.16,1.10 PASS | 1.24,4.99 | 3.76,21.48 | 6.14,17.94 | 38.17,24.04 | 45.27,84.85 | 1/8 |
| R3 gm (frozen) | +r3fix/refine_axis.m, LM trust-region on GM-robustified biaxial Cao cost, cao_update_func retraction, R-only (no tmult); default gm | 0.62,2.96 | 0.94,3.94 | 0.77,1.12 PASS | 1.26,5.00 | 3.85,21.98 | 5.19,15.21 | [12.47,50.61,56.19],[6.12,200.41,166.08] | [8.68,26.22],[20.89,31.14] | 1/8 |

Median / worst across 8 pieces, refined gm (worst-per-piece): direction median ~2.6°,
worst 56.2°; position median ~10.6mm, worst 200.4mm (P07 third axis matched to a 56°-off
candidate). Vote-only R2 median/worst are nearly identical — refinement moves little.

Evidence notes:
1. R1 (job 33067510, COMPLETED 0:0): baseline re-verified pristine-only
   (load_root_dir undefined @ read_surfaces.m:15); with shim, all 8 pieces load and die at
   the vote cross crash @ compute_cao_error.m:21 — exactly the predicted reappearance.
2. R2 (job 33067737, COMPLETED 0:0): vote completes 1000/1000 finite costs on all 8 pieces.
   Semantics proof: n=1 patched-vs-pristine norm = 0.000e+00. Full run_potsac then stops at
   missing refine_axis @ run_potsac.m:34 — the next blocker, as predicted.
3. R3 calibration on 01-04 only: huber-refine passes P02 (0.60,0.77) but wrecks P03
   (2.00,5.85); gm-refine keeps P03 (0.77,1.12), 1/4 either way (job 33069931). Cost
   diagnostic (job 33069665): shipped is the GM-cost minimum (ship ≤ vote < huber-refined
   on all four) but NOT the Huber minimum — hence gm frozen (also matches vote-stage and
   optimizer defaults in-tree). Own bug caught by trace: first R3 build indexed the trailing
   args wrong (max-iters read as 1e-3, zero LM iters, refinement silent no-op); fixed,
   verified real iteration (first-stage 2-9 iters, full-data 18 iters, costs drop).
4. Held-out 05-08 (job 33070192, COMPLETED 0:0, frozen gm): 0/4. P05/P06 direction 3.9°/5.2°
   (worse than 01-04's <1.3°), position 15-22mm; P07 set (n=3) best matches 12.5°/6.1mm at
   best, other axes 50°+/160mm+; P08 set (n=6) best 8.7°/20.9mm. Small/multi-axis sherds are
   far off on direction, not just position — not closable by more LM iterations.
5. Debug jobs 33068582 (FAILED 1:0 — my trace-line MATLAB syntax error, fixed), 33068838
   and 33069376 (both COMPLETED 0:0).

Exact changes (all under /data/gpfs/projects/punim2657/Temp/potsac-p09-run/; pristine
clone untouched):
- R1: shim/load_root_dir.m (new, 12 lines: answers only Plt_A/SFS_BB_temp requests with the
  staging dir, errors otherwise) + ../potsac-p09-data/Surfaces/Plt_A_Piece_0{1-8}_Surface_{0,1}.xyz
  symlinks -> shipped Pot_A files.
- R2: r2fix/compute_cao_error.m differs from pristine only at lines 20-26: add
  Vpos_rep/Vdir_rep repmat + cross the replicated slices (diff recorded in run dir).
- R3: r3fix/refine_axis.m (new, ~100 lines: parses (vt,C,2,[],[],max_iters,func_tol),
  forward-difference LM, Triggs-weighted biaxial residuals, cao_update_func retraction;
  POTA09_ROBUST selects gm/huber, default gm). Run artifacts: r3gm-p01..p08.mat (frozen
  config outputs), r3cal-huber/gm mats, job logs r1/r2/r3cal/r3cal2/r3diag/r3dbg/r3test-*.out.

Kill verdict: the author's path is fixable by repair: NO — 1/8 pieces within ≤5° and ≤2mm
after all three single-variable repairs (frozen gm; huber variant also 1/8 with a different
piece). Direction is largely recovered on big sherds (≤1.3° on 01-04) but position stalls
at 3-5mm, and held-out small/multi-axis pieces fail on direction too (up to 56°/200mm).
Closing that needs new variables (surface weighting, search/dedup redesign) — the lead's
redesign call, not this ticket. Scorer sanity: the metric CAN show ~0 (P03 passes 0.77°/1.12;
shipped self-scores 0/0), so the failures are finder failures, not ruler failures. No
geometry renders were staged (ticket acceptance is numbers-only).
