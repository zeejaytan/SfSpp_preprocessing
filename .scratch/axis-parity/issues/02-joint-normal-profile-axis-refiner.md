# 02: Fix axis cost landscape (robust normalized residual, Hermite profile, scale-free Cao LM) & validate on 10 pots

**What to build:** A prototype strictly inside Spartan `<run>/work/impl_t02/` (ZERO edits to tracked files in `SfSpp_preprocessing/` or `structure-from-sherds-pp/`, saved & verified as `impl_t02.diff` cleanly applying over `commit 9e0fe6a`, keeping `orient_base_axis` ON by default) that fixes the three underlying cost-landscape and optimization defects isolated in Ticket 01 and validates across:
1. **Phase 1 (Fast Offline Ablation & Gate):** First, a GT-vs-decoy landscape check on the `14` loss pieces + `Pot_A_Piece_08` + `Pot_G_Piece_03` + `def_3x` Juglet; then full candidate selection across all `141` GT-scored corpus pieces (on **both** Authors' `Surfaces/` and Our Own `MeshPreprocessingHeadless` surfaces from Ticket 01's Stage C manifest including Pot H `out_poth/geom`) + `def_3x` Juglet (`9` pieces, radial offsets scaled by `1/3.0`).
2. **Phase 2 (Conditional E2E Gate — ONLY if Phase 1 passes its Pre-Registered Gate):** Full 10-pot E2E assembly (`Pot A..J`, 2 repeats each, `MOR1/2` + `K3R1/2`) + `def_3x` Juglet (`4` repeats + controls).

**Answers:** E1
**Blocked by:** None (Ticket 01 resolved at `62ff33c`)
**Status:** in-progress
**Working in:** chat on Thinkbook16 (2026-11-20)
**Branch:** 02-joint-normal-profile-axis-refiner, in /c/PR/worktrees/sfs/02
**Worker:** unassigned
**Budget:** large 8
**Hand-over:** DeepSeek — hidden acceptance check at `C:/PR/artifacts/dsh-handover/axis-parity-02/accept.py` to be staged before dispatch

---

## 1. Root Causes Verified from Ticket 01 + Code/Math Audit (Why Ticket 02 Was Revised)

Ticket 01 (`20261120-0227_2c14fe3_t01-diag-axis-parity`, `b432fb9`/`62ff33c`) proved:
- **Zero pool-coverage gaps (`M1 = 0/14`):** every one of the 14 loss pieces already has a `1.41°–7.71°` candidate inside the 60-basin pool. Losses occur downstream: `M2 = 7` (`Pot_A_Piece_07`, `Pot_E_Piece_25`, `Pot_E_Piece_29`, `Pot_E_Piece_31`, `Pot_F_Piece_05`, `Pot_E_Piece_26`, `Pot_J_Piece_07`), `M4 = 3` (`Pot_D_Piece_23`, `Pot_I_Piece_20`, `Pot_J_Piece_02`), `M3 = 2` (`Pot_A_Piece_06`, `Pot_E_Piece_14`), `M5 = 2` (`Pot_D_Piece_20`, `Pot_D_Piece_27`).
- **Rim coplanarity does not help on these 14 (`0/14`):** best breakline plane-normal vs GT is `24.85°–86.05°`.
- **Stage C own surfaces are at parity (`113/141 K1`, `118/141 K3` vs `109/141`, `121/141` on Authors' surfaces):** upstream surface segmentation is not blocking axis parity.
- **Naive blending of existing scalars fails (`joint-both-lm-11` is net zero):** `109/141 K1` and `121/141 K3` with worse overall median (`3.317°` vs `3.064°`) and worse `Pot A` origin radial (`9.501` vs `8.113 mm`), while guarded LM rejected `187/219` refinements (`32/219` accepted).

Auditing `sfs_axes/{normalized.py,profile.py,select.py,cao.py,robust.py}` against Ticket 01's diagnostics isolated **three concrete mathematical/implementation bugs** that explain both Stage B's wash and why Authors' `Axes/` achieve `0.91°` (`E29`), `0.97°` (`I20`), `0.95°` (`A06`), `1.79°` (`J07`), and `1.92 mm` `Pot A` radial:

1. **`robustifier_huber(width=1.0)` NEVER activates on `compute_normalized_residual` (`sfs_axes/normalized.py:176-180, 219-221`, `robust.py:24-25`):**
   - `e_hat_i = ((p_i - p_0) · (n_i × a)) / ||(p_i - p_0) × a||` is bounded by `|e_hat_i| <= 1.0`, so `s = e_hat_i^2 <= 1.0` for 100% of points.
   - Because `robustifier_huber(..., width=1.0)` sets `tau_sq = 1.0` and only robustifies `out = s > 1.0`, **both `normalized_huber_cost` and `refine_axis_normalized` run pure unrobustified L2 least squares**. Boundary/chip/normal outliers rip `7/14` good pool seeds (`1.4°–7.7°`) out to `14.8°–72.2°` in `refine_axis_normalized` (`M2`) and cause wild `10°–88.9°` LM walks (`Pot_D_Piece_23 88.922°`, `Pot_A_Piece_08 48.05°/66.88°`).
2. **Normal-tilt nullspace (`||n_i × a|| -> 0`) and outward radial runaway in `e_hat_i` (`normalized.py:67-69` vs `cao.py:28-33`):**
   - Because `e_hat_i = ||n_i × a|| sin(phi_i)`, tilting `a` toward the mean sherd normal shrinks `||n_i × a||`, artificially lowering `e_hat_i` without reducing azimuthal error, while leaving outward radial runaway (`r -> inf`) unpenalized (`Pot_I_Piece_20 133.5 mm`, `Pot_D_Piece_27 145.8 mm`, `Pot_J_Piece_07 116.3 mm`, `Pot_G_Piece_03 53.2 mm`).
   - By contrast, Authors' `compute_cao_error` divides out `||n_i × a||` (`ratio = sqrt(||T2||^2 / ||T3||^2)`) and applies real Huber (`width = 1.0 mm`) / Geman-McClure outlier clipping (`run_potsac.m`).
3. **Normal-blind `profile_cost` (`profile.py:38-51`) beats GT by `1.7×–3.3×` on ALL `14/14` loss pieces:**
   - Pure `(r, z)` kNN PCA ignores `n_i`: projecting a curved sherd edge-on or sliding the axis radially flattens `(r, z)` thickness even when colliding points have incompatible surface normals (`Pot_A_Piece_06` `0.0374` vs GT `0.1220 mm`; `Pot_I_Piece_20` `0.0383` vs GT `0.0931 mm`; `Pot_D_Piece_23` `0.0258` vs GT `0.0688 mm`; `Pot_A_Piece_07` `0.0319` vs GT `0.0542 mm`), and unconstrained 4-DoF NM walks good seeds off target (`M4 = 3/14` + `Pot_G_Piece_03 2.56° -> 7.98°`).

### Exact Radial Metrics & `def_3x` Juglet Scaling (Verified on `C:/PR/artifacts/axis_audit/`, `141` GT pieces)
Both radial definitions must be reported explicitly without mixing them:
- **Physical vessel-frame radial offset `d_gt_to_est` (Primary precision gate):** `radial_axial_errors(gt[3:6], vt[0:3], vt[3:6])[0]` (orthogonal distance from true vessel axis point `gt[3:6]` to estimated axis line `vt`). On `141` GT pieces: `Authors` median `4.38 mm` (`Pot A 1.92 mm`), `axes335` median `4.53 mm` (`Pot A 6.97 mm`).
- **Origin-projected foot offset `d_est_to_gt` (`io_axes` metric):** `radial_axial_errors(vt[3:6], gt[0:3], gt[3:6])[0]`. On `141` GT pieces: `Authors` median `11.64 mm` (`Pot A 8.97 mm`), `axes335` median `11.88 mm` (`Pot A 8.11 mm`).
- **`def_3x` Juglet scaling:** Divide estimated position `vt[3:6]` by `3.0` before computing `d_gt_to_est` / `d_est_to_gt` against 1x `Dataset/Juglet_GT` so radial errors are reported in physical 1x mm (preventing Ticket 01's unscaled `700–1400 mm` mismatch).

---

## 2. Design Constraints (Non-Negotiable)

1. Prototype strictly inside `/data/gpfs/projects/punim2657/SfSpp/runs/<YYYYMMDD-HHMM>_<git7>_t02-cost-landscape/work/impl_t02/` on top of `9e0fe6a`. Verify `git diff` reproduces `impl_t02.diff` cleanly (`patch -p1 --dry-run` against a clean copy of `9e0fe6a`) and `python -m pytest` passes all `>= 42` existing tests plus new prototype unit tests inside `<run>/work/`. Leave tracked files in `SfSpp_preprocessing/` and `structure-from-sherds-pp/` untouched.
2. Keep Ticket 335's `orient_base_axis` (`BASE_ORIENT=1`) intact at the end of `select_union_lines`.
3. **Zero per-pot, per-piece, or object-size constants:** all robust scales and normalizations must be dimensionless or normalized by the piece's own intrinsic geometry (`r_med(L)`, cloud bounding-box `size`, or robust `MAD`), scaling cleanly across `33 mm` Juglet and `300 mm` vessels.
4. Preserve full `4-DoF` search/polish freedom where `Pot_A_Piece_06` (`0.95°`) and `Pot_A_Piece_08` (`<= 10°`) need large basin walks — never re-test closed dead-ends from `spec.md §4` (including unrobustified `(pc, cn)` weight blending from Ticket 01).
5. **All heavy work on Spartan compute nodes (`sbatch`) only**; poll every job, record every `sacct -X` (`COMPLETED 0:0`), append `runs/index.tsv` (leave `verdict` and `human_note` blank), and verify `CORPUS-UNCHANGED`.

---

## 3. Phase 1: Offline Cost-Landscape & Refiner Ablation (Fast Compute Loop)

Reuse Ticket 01's cached 150-piece draw/basin pools (`/data/gpfs/projects/punim2657/SfSpp/runs/20261120-0227_2c14fe3_t01-diag-axis-parity/out/cache/*.npz`) plus full surface clouds (`C0, C1`).

1. **GT-vs-decoy landscape audit first:** For each candidate objective below, evaluate on the `14` loss pieces + `Pot_A_Piece_08` + `Pot_G_Piece_03` + `def_3x` Juglet (`9` pieces): how many of the `14` losses now have `cost(GT) < cost(axes335_winner)`? Verify `cost(GT)` vs `cost(decoy)` directly before running full 150-piece sweeps.
2. **Test the three targeted fixes + unified synthesis across all `141` GT pieces (Authors' `Surfaces/` AND Own `MeshPreprocessingHeadless` surfaces using Ticket 01's verified Stage C paths + Pot H `20261120-0227_2c14fe3_t01-diag-axis-parity/out_poth/geom`) + `def_3x` Juglet (`9` pieces):**
   - **Arm A — Fix `normalized.py` robustification & tilt nullspace:**
     - `A1` (**Calibrated scale-free robustifier on `e_hat_i`**): Replace dead `width=1.0` with dimensionless `robustifier_huber` / `robustifier_gm` (`width in {0.03, 0.05, 0.08, 0.12}` and/or adaptive `1.4826 * MAD`) in both `refine_axis_normalized` (solving why `M2` 7/14 pool seeds drifted) and candidate scoring.
     - `A2` (**Tilt-normalized azimuthal residual & scale-free Cao**): Test (i) `e_az,i = ((p_i - p_0) · (n_i × a)) / (||(p_i - p_0) × a|| · sqrt(||n_i × a||^2 + eps_n^2))` with `eps_n = 0.1` (eliminating `||n_i × a|| -> 0` pole bias) and (ii) median-radius-normalized biaxial Cao `R_cao,i / r_med(L)` with calibrated Huber/GM scale `width ~ 0.03–0.08` and analytical LM Jacobian.
   - **Arm B — Normal-consistent Hermite `(r, z)` profile objective (fixing 14/14 GT-vs-decoy inversion & `M4` NM drift):**
     - `B1` (**Hermite tangent-plane `(r, z)` thickness**): For each strided wall `C0, C1`, project each point's unit surface normal into the `(r, z)` meridional plane: `m_i = (n_i · r_hat_i, n_i · a)` normalized to `m_hat_i` (with floor `eps = 1e-6`), and evaluate trimmed mean of `|(q_j - q_i) · m_hat_i|` over its `k` nearest `(r, z)` neighbours `j` (optionally with in-plane normal agreement `(1 - |m_hat_i · m_hat_j|)` and/or robust `e_az,i`), replacing or gating blind PCA `wall_thickness`. Verify whether it eliminates the `M4` NM walks (`D23, I20, J02, G03`) and puts `cost(GT) < cost(decoy)` on the `14` losses.
     - `B2` (**Chord-normalized profile + normal consistency**): Also check local arc-chord normalization / bounded `(r, z)` neighbourhood curvature so outward radial blow-up (`Pot_A_Piece_07 36–66 mm`, `I20 133.5 mm`) does not earn artificially thinner `(r, z)` slices.
   - **Arm C — Scale-free analytical biaxial Cao LM (`compute_biaxial_cao_error`) in pool & guarded full-cloud polish:**
     - `C1` (**Scale-free Cao LM in the 60-basin pool**): Add scale-free `compute_biaxial_cao_error` refinement (`width = alpha * size`, `alpha in {0.008, 0.012, 0.015}`, scaling `X` or `width` cleanly without hardcoding mm) alongside `raw` & robust-`nref` into the candidate pool before `[:8]` / `15°` dedup — supplying true sub-degree analytical minima (`0.91° E29`, `0.97° I20`, `0.6° G03`, `1.92 mm` `Pot A`) while letting the normal-consistent Arm A/B selector reject centroid-collapsed basins.
     - `C2` (**Guarded full-cloud `100%`-point `tol=1e-9` polish**): Starting from top distinct surviving candidates, run full-cloud (`100%` points, `tol=1e-9`) scale-free analytical LM polish (Cao or Arm A2) **guarded against centroid collapse on non-base sherds and Hermite/profile inflation**; test both overall `141`-piece precision (`<= 2.78°`, `d_gt_to_est <= 4.38 mm`, `Pot A d_gt_to_est <= 3.5 mm`) and `K3` recovery.
   - **Arm D — Unified scale-free synthesis (`impl_t02`):** Combine the winning scale-free A + B + C components (cleanly parameterized, no pot-specific tuning), keeping `keep_lines(tau=1.2, kmax=3)` (or verifying any justified adjustment preserves Pot G `10/10`) and `orient_base_axis`. Evaluate Arm D on Authors' surfaces (`141` GT), Own surfaces (`141` GT), and `def_3x` Juglet (`9` pieces).

---

## 4. Phase 1 -> Phase 2 Go/No-Go Gate (Part A Axis Parity Bar)

Arm D must pass **ALL** bars below on Phase 1 before submitting any Phase 2 E2E assembly job:
- **`K1 <= 10°`:** `>= 109/141` (match/beat `axes335` AND strictly beat Authors' `105/141` on Authors' surfaces); report own-surfaces `K1/K3` beside baseline `113/118`.
- **`K3 <= 10°`:** `>= 121/141` (match/beat `axes335` AND strictly beat Authors' `116/141`).
- **Recovery of Ticket 01 losses:** Recover at least **`4` of the `8`** `K3` loss pieces (`Pot_A_Piece_07`, `Pot_D_Piece_23`, `Pot_E_Piece_25`, `Pot_E_Piece_29`, `Pot_E_Piece_31`, `Pot_F_Piece_05`, `Pot_I_Piece_20`, `Pot_J_Piece_02`) into `K3 <= 10°` with no net regression elsewhere.
- **Precision parity (`Gap 1`):** Overall `141`-piece median rank-0 angle **`<= 2.78°`**, overall physical `d_gt_to_est` median **`<= 4.38 mm`**, AND **`Pot A` `d_gt_to_est` median `<= 3.5 mm`** (down from `axes335`'s `6.97 mm` toward Authors' `1.92 mm`).
- **Safeguards:** `Pot_A_Piece_08 <= 10°`; **`def_3x` Juglet (radial scaled `/ 3.0`)**: `K1 >= 7/9`, `K3 >= 8/9`, `is_base_fragment=True` on `Juglet_Piece_7` only, **`SignAxisGuard = 0/18 (0.00%)`**.

> **Early-Stop Rule (Mandatory):** If NO tested formulation clears EVERY Phase 1 gate above, **DO NOT submit the Phase 2 10-pot E2E Slurm jobs**. Fetch all Phase 1 deliverables (`axes02_summary.json`, `gate02.tsv`, `render02_landscape.png`, `impl_t02.diff`), visually inspect `render02_landscape.png`, write up the exact bottleneck & best partial arm, and finish cleanly with `Reading: cost-landscape-ablation-partial-no-e2e`.

---

## 5. Phase 2 (ONLY if Phase 1 Gate Passes): 10-Pot + `def_3x` Juglet E2E Assembly

Using Arm D's extracted axes from `<run>/work/impl_t02/`:
- **All `10/10` paper pots (`Pot A..J`, 2 repeats each, `MOR1/2` + `K3R1/2`)** at or above BOTH `t323` floors AND Ticket 323 achieved scores:
  - `Pot A 8/8 15/15`, `Pot B 9/9 15/15`, `Pot C 4/4 5/5`, `Pot D >=23/28 >=55/69` (targeting `26/28 63/69`), `Pot E 31/31 62/62`, `Pot F 5/5 7/7`, `Pot G 7/7 10/10`, `Pot H 11/11 17/17`, `Pot I >=25/26 >=59/62`, `Pot J >=8/11 >=16/21`
  - `MOR1/2` controls green; `CORPUS-UNCHANGED`.
- **`def_3x` Juglet (`4` repeats, `cluster366.py` + `score58` at real `4.596 mm`):** Best of 4 repeats `9/9` sherds, **`>= 10/18` edges**, vertex cluster `9/9 <= 0.50 mm`, `4/4` Piece 7 joins (`3-7, 6-7, 7-8, 7-9`).

---

## 6. Deliverables & Visual Inspection (`C:/PR/artifacts/axis-parity-02/`)

- **Always fetched:**
  - `axes02_summary.json` — GT-vs-decoy cost audit, Arms A/B/C/D metrics on `141` GT pieces (Authors' & Own surfaces, both `d_gt_to_est` and `d_est_to_gt`), `def_3x` Juglet (scaled `/ 3.0`, `0/18 SignAxisGuard`), all `sacct -X` IDs, and (if run) Phase 2 E2E tables.
  - `gate02.tsv` — 7-column TSV (`group\tpiece\tmetric\tvalue\treference\tverdict\tnote`) covering GT-vs-decoy, Arms A..D, Own-surfaces comparison, `def_3x` Juglet, and (if run) Phase 2 `potA..potJ` + `juglet`.
  - `render02_landscape.png` — 8-row 3D + `(r, z)` visual comparison (`Pot_A_Piece_07`, `Pot_A_Piece_06`, `Pot_E_Piece_29`, `Pot_I_Piece_20`, `Pot_J_Piece_02`, `Pot_J_Piece_07`, `Pot_G_Piece_03`, `Pot_A_Piece_08`) showing GT, Authors, `axes335`, and Arm D. **Visually inspect before writing `Reading:`.**
  - `impl_t02.diff` — Clean unified diff against `9e0fe6a` verified with `patch -p1 --dry-run`.
- **Also fetched when Phase 2 runs:**
  - `render02_tenpots.png` — 11-panel assembly montage (`Pot A..J` + `def_3x` Juglet) + close-up crops on any borderline pot, visually inspected before `Reading:`.
  - `score/` — `acc_pot{A..J}.tsv` and `juglet/`.

---

## 7. Readings (pick one verbatim on a bare `Reading:` line)

- `joint-refiner-achieves-author-parity-and-passes-ten-pots` — Phase 1 clears EVERY Part A parity bar AND Phase 2 passes all `10/10` pots + `def_3x` Juglet (`>= 10/18`, `4/4` Piece 7, `0/18 SignAxisGuard`); ready to ship in Ticket 03.
- `joint-refiner-improves-axes-but-misses-bar` — Phase 1 clears its gate (so Phase 2 runs) OR both phases show net gain but miss one or more pre-registered Part A/B bars; report exact trade-off.
- `cost-landscape-ablation-partial-no-e2e` — Phase 1 early-stop triggered cleanly (no Arm D candidate cleared the full Part A parity gate, so Phase 2 E2E jobs were skipped per Section 4); report exact gains/limits and revised Ticket 03/followup scope.
- `blocked: missing-or-failed-control` — `MOR` control drops below floor or required Ticket 01 / corpus inputs are unavailable.

## Out of scope

- Editing ANY tracked file in `SfSpp_preprocessing/` or `structure-from-sherds-pp/`.

## Acceptance

- [ ] Zero tracked source edits (`git status --short` modifies only this ticket); `<run>/work/impl_t02.diff` cleanly reproduces prototype from `9e0fe6a` and unit tests pass (`>= 42` existing + new prototype checks in work area).
- [ ] Phase 1 GT-vs-decoy landscape audit and Arms A..D benchmarked on `141` GT pieces (Authors' & Own surfaces, reporting both `d_gt_to_est` and `d_est_to_gt`) + `def_3x` Juglet (`0/18 SignAxisGuard`, 1x `/ 3.0` scaling), with `sacct -X COMPLETED 0:0` and `CORPUS-UNCHANGED`.
- [ ] Phase 1 Go/No-Go gate checked cleanly: either Arm D passes EVERY Part A bar (`K1 >= 109`, `K3 >= 121`, `>= 4/8` K3 recoveries, med `<= 2.78°`, `d_gt_to_est <= 4.38 mm`, `Pot A <= 3.5 mm`, `A08 <= 10°`, Juglet `>= 7/9` & `0/18`) and Phase 2 E2E (`10/10` pots + `def_3x` Juglet) completes (`COMPLETED 0:0`, `CORPUS-UNCHANGED`), OR Phase 1 early-stop rule is documented accurately without spurious E2E runs.
- [ ] `C:/PR/artifacts/axis-parity-02/{axes02_summary.json,gate02.tsv,render02_landscape.png,impl_t02.diff}` (plus `render02_tenpots.png` & `score/` if Phase 2 ran) fetched and visually inspected before writing bare `Reading:` and `**End state:** ready`.
