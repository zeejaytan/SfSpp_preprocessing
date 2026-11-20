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

- [x] Zero tracked source edits (`git status --short` modifies only this ticket); `<run>/work/impl_t02.diff` cleanly reproduces prototype from `9e0fe6a` and unit tests pass (`>= 42` existing + new prototype checks in work area).
- [x] Phase 1 GT-vs-decoy landscape audit and Arms A..D benchmarked on `141` GT pieces (Authors' & Own surfaces, reporting both `d_gt_to_est` and `d_est_to_gt`) + `def_3x` Juglet (`0/18 SignAxisGuard`, 1x `/ 3.0` scaling), with `sacct -X COMPLETED 0:0` and `CORPUS-UNCHANGED`.
- [x] Phase 1 Go/No-Go gate checked cleanly: either Arm D passes EVERY Part A bar (`K1 >= 109`, `K3 >= 121`, `>= 4/8` K3 recoveries, med `<= 2.78°`, `d_gt_to_est <= 4.38 mm`, `Pot A <= 3.5 mm`, `A08 <= 10°`, Juglet `>= 7/9` & `0/18`) and Phase 2 E2E (`10/10` pots + `def_3x` Juglet) completes (`COMPLETED 0:0`, `CORPUS-UNCHANGED`), OR Phase 1 early-stop rule is documented accurately without spurious E2E runs.
- [x] `C:/PR/artifacts/axis-parity-02/{axes02_summary.json,gate02.tsv,render02_landscape.png,impl_t02.diff}` (plus `render02_tenpots.png` & `score/` if Phase 2 ran) fetched and visually inspected before writing bare `Reading:` and `**End state:** ready`.


## Comments

**Worker run 2026-11-20** (DeepSeek, one-shot subagent `w02-axis-parity`, ticket authorisation m00002). Phase 1 ran to completion on Spartan; Arm D did **not** clear the Part A gate, so **no Phase 2 E2E job was submitted** (Section 4 early-stop). Net result: two of the three diagnosed bugs are fixed and visible, one (the profile-cost inversion) is only half-fixed, and no A/B/C/D formulation reaches the `K3 >= 121/141` bar.

### Run and prototype

- Run directory: `/data/gpfs/projects/punim2657/SfSpp/runs/20261120-1430_9e0fe6a_t02-cost-landscape` (`work/run.json` records the base commit, the Ticket 01 pool cache and the Own-surface dirs per pot).
- Prototype `work/impl_t02/` = `git archive 9e0fe6a` of `sfs_axes/ tests/ scripts/run_benchmark_172.py` plus **new files only**: `sfs_axes/t02/{__init__,objectives,refiners,arms,metrics}.py` and `tests/test_t02_objectives.py`. No tracked file is edited; `orient_base_axis` stays ON (it was already ON at `9e0fe6a`).
- `work/impl_t02.diff` (fetched, 43224 B): 6 files created, 1060 insertions. Verified in `C:/PR/worktrees/sfs/02`: `git apply --ignore-whitespace --check /c/PR/artifacts/axis-parity-02/impl_t02.diff` → `APPLY-OK` (6 `diff --git` sections).
- Tests: `python -m pytest tests -q` in the worktree → `42 passed in 33.13s`; inside `work/impl_t02` on a compute node → `56 passed, 1 warning in 38.50s` (42 shipped + 14 new prototype tests).

### Two corrections found mid-run (recorded because the next ticket needs them)

1. **Juglet GT is already 1x — never divide it.** `Dataset/Juglet_GT/Juglet_Piece_1_Axis.xyz` = `(183.904, 148.465, -134.053, 0.3455, 0.3560, 0.8683)`; the `def_3x` estimate for the same piece is 3x that (`551.6, 429.5, -382.0`), so the geometry is the 3x copy and **only the estimate** is divided by `3.0`. Pass 1 divided the GT as well and reported a 236.96 mm median `d_gt_to_est`; with the frame fixed the same records score 25-41 mm.
2. **Unbounded refinement of a short line is the radial-runaway mechanism.** `Pot_A_Piece_7` (33 mm across) had its line moved 322.99 mm by the azimuthal residual, because the residual has a nullspace through a near-planar base. Every arm now accepts a refinement only if the two lines' closest points to the cloud centroid move by `<= 1` bbox diagonal (`arms._bounded` + `objectives.line_shift`). A first attempt measured foot-to-line distance instead and made A1 *worse* (Piece 1: 1.07° → 9.39°), because a pot-axis foot is legitimately hundreds of mm from a 33 mm sherd.

### Commands (exact)

```bash
# Phase 1 arms + corpus md5  (job 35435516, 8 cpus / 32G / 03:00:00)
sbatch <run>/work/submit_arms3.sbatch        # -> work/rerun_arms.sh: pytest -> Juglet pre-gate -> arms -> corpus md5
ssh spartan "sacct -X -j 35435516 --format=JobID,State,ExitCode,Elapsed"

# summary + render (job 35440806, compute node)
srun --account=punim2657 --partition=sapphire -t 00:30:00 -c 2 --mem=16G --job-name=t02-post \
     bash <run>/work/post.sh                # t02_summary.py --out <run>/out ; t02_render.py --out <run>/out

# deliverables
scp spartan:<run>/out/axes02_summary.json spartan:<run>/out/gate02.tsv \
    spartan:<run>/out/render02_landscape.png C:/PR/artifacts/axis-parity-02/
scp spartan:<run>/work/impl_t02.diff C:/PR/artifacts/axis-parity-02/

# index rows appended (verdict / human_note left blank)
printf '%s\t%s\t%s\t%s\t\t\n' 20261120-1430_9e0fe6a_t02-cost-landscape 35432092 9e0fe6a t02-phase1  >> runs/index.tsv   # + 35433021 t02-jugpre, 35435516 t02-arms3, 35440806 t02-post
```

### `sacct -X` (every job of this ticket)

| job | name | state | exit | elapsed | note |
|---|---|---|---|---|---|
| 35426637 | t02-phase1 | FAILED | 1:0 | 00:00:03 | pytest not installed on the node |
| 35427826 | t02-phase1 | FAILED | 1:0 | 00:00:25 | prototype test called `arm_d` with a surplus positional arg |
| 35428910 | t02-phase1 | FAILED | 1:0 | 00:00:32 | pytest passed (55) then `ModuleNotFoundError: run_benchmark_172` (sys.path) |
| 35430640 | t02-phase1 | FAILED | 1:0 | 00:20:53 | Pot H own-surface path wrong (11 pieces) + my mid-run `t02_lib` edit changed the md5 manifest (artefactual CORPUS-CHANGED) |
| 35432092 | t02-phase1 | COMPLETED | 0:0 | 00:03:43 | Pot H repointed; 11/11 arms ok; `CORPUS-UNCHANGED` |
| 35428838 | t02-dbg | COMPLETED | 0:0 | 00:00:08 | debug srun |
| 35432410 / 35432430 | t02-sum | COMPLETED | 0:0 | 00:00:05 | summary passes |
| 35432459 / 35432517 | t02-rend | FAILED | 2:0 | 00:00:07 / 00:00:05 | render bugs: (6,N) cloud indexing, then `np.outer` shape |
| 35432530 / 35432581 | t02-rend | COMPLETED | 0:0 | 00:00:05 / 00:00:07 | render fixed |
| 35432689 / 35432717 | t02-jugfix | COMPLETED | 0:0 | 00:00:03 / 00:00:07 | Juglet GT-frame rescore + summary |
| 35432841 | t02-jugdiag | COMPLETED | 0:0 | 00:00:04 | sign-guard diagnosis (T rotation required; all flips were Piece 7) |
| 35433021 | t02-jugpre | COMPLETED | 0:0 | 00:16:27 | single-process Juglet pre-gate (63 arm runs) |
| 35434434 | t02-arms2 | CANCELLED | 0:0 | 00:00:00 | 24 cpus/96G sat PENDING ~25 min; scancelled |
| **35435516** | **t02-arms3** | **COMPLETED** | **0:0** | **01:20:56** | **Phase 1 rerun: pytest 56 passed, Juglet pre-gate GATE-OK, 300/300 arms ok, `CORPUS-UNCHANGED`** |
| 35440563 | t02-post | FAILED | 2:0 | 00:00:08 | `t02_summary.py` needs `--out` |
| 35440612 | t02-post | FAILED | 2:0 | 00:00:08 | summary ok, `t02_render.py` needs `--out` |
| 35440662 | t02-render | COMPLETED | 0:0 | 00:00:10 | render-only pass |
| 35440806 | t02-post | COMPLETED | 0:0 | 00:00:14 | summary + render pass |
| **35441467** | **t02-post** | **COMPLETED** | **0:0** | **00:00:11** | **regenerated the three deliverables with the corrected Juglet note — these are the fetched files** |

No Phase 2 `sbatch` exists — the early-stop rule fired, so nothing was submitted beyond Phase 1 and its post-processing.

### `CORPUS-UNCHANGED`

`work/corpus_md5.py` hashes 907 files (GT axes, released axes, every Authors' and Own `S0/S1` mesh, `Juglet_GT/*`) into `out/corpus_before.md5` and `out/corpus_after.md5`; job 35435516 printed `CORPUS-UNCHANGED` (and would have exited 3 otherwise). The earlier `CORPUS-CHANGED` on 35430640 was my own mid-run library edit changing which files the manifest enumerated (885 → 907 lines), not a corpus change.

### Phase 1A — GT vs the shipped decoy (150 stems, Authors' surfaces)

Decoy = the `axes335` rank-0 line from Ticket 01's stage cache. "decoy cheaper" counts pieces where `cost(decoy) < cost(GT)`.

| cost | decoy cheaper | of the 8 K3 losses | median decoy/GT ratio |
|---|---|---|---|
| pca (shipped `profile_cost`) | 150/150 | 8/8 | 0.5304 |
| hermite (median `(r,z)` thickness) | 150/150 | 8/8 | 0.5341 |
| hermite_nc (normal-consistent) | 150/150 | 8/8 | 0.5338 |
| az (tilt-normalized azimuthal) | 125/150 | 5/8 | 0.8910 |
| cao (scale-free biaxial) | 125/150 | 8/8 | 0.9013 |

The inversion in Ticket 01's §1.3 is therefore **corpus-wide, not a property of the 14 losses**, and it survives every profile cost I built (Hermite, normal-consistent Hermite, scale-free Cao). Only the tilt-normalized azimuthal residual is much less permissive — but it is the one that runs away on short base pieces (correction 2 above).

### Phase 1B — arms, 141 GT pieces

| arm | surfaces | K1 (<=10°) | K3 (best of 3) | median ° | median `d_gt_to_est` mm | median `d_est_to_gt` mm | Pot A `d_gt_to_est` mm | K3 recovery /8 | K1 recovery /6 |
|---|---|---|---|---|---|---|---|---|---|
| **A1** live Huber on `e_hat` | Authors | **110/141** | 113/141 | **2.71** | **4.338** | 9.925 | **2.473** | **6** | 1 |
| A1 | Own | 116/141 | 117/141 | 2.56 | 3.778 | 9.255 | 2.637 | 5 | 1 |
| A2 azimuthal + scale-free Cao | Authors | 62/141 | 64/141 | 18.26 | 17.086 | 44.033 | 58.232 | 0 | 1 |
| A2 | Own | 74/141 | 75/141 | 8.49 | 7.782 | 28.332 | 30.875 | 1 | 1 |
| B1 Hermite absolute | Authors | 107/141 | 115/141 | 3.41 | 4.848 | 12.907 | 2.909 | 3 | 2 |
| B1 | Own | 110/141 | 117/141 | 3.32 | 4.810 | 13.579 | 6.259 | 2 | 1 |
| B2 hermite + chord normalisation | Authors | 112/141 | 116/141 | 3.39 | 4.337 | 11.422 | 2.786 | 2 | 2 |
| B2 | Own | 109/141 | 116/141 | 3.28 | 4.683 | 12.436 | 6.164 | 3 | 1 |
| C1 scale-free Cao in the pool | Authors | 72/141 | 80/141 | 8.98 | 13.861 | 32.383 | 8.578 | 0 | 0 |
| C1 | Own | 77/141 | 83/141 | 6.71 | 9.373 | 29.263 | 5.423 | 1 | 1 |
| C2 guarded full-cloud polish | Authors | 68/141 | 73/141 | 12.22 | 11.236 | 40.531 | 8.578 | 0 | 0 |
| C2 | Own | 76/141 | 80/141 | 7.18 | 8.853 | 26.940 | 5.423 | 0 | 1 |
| **D unified synthesis** | **Authors** | **92/141** | **94/141** | **4.00** | **5.661** | **14.505** | **2.724** | **3** | 1 |
| D unified synthesis | Own | 102/141 | 102/141 | 3.41 | 4.976 | 12.221 | 2.514 | 4 | 3 |

Baselines to beat: shipped `axes335` 109/141 K1, 121/141 K3, median 3.06°, `d_gt_to_est` 4.53 mm; Authors' own axes 105/141, 116/141, 2.78°, 4.38 mm.

Reading of this table:

- **A1 is the best partial arm and it fixes bug 1 on its own**: 110/141 K1 (beats shipped 109 and Authors' 105), median 2.71° (beats 2.78°), `d_gt_to_est` 4.338 mm (beats 4.38 mm), Pot A 2.473 mm (bar 3.5), `Pot_A_Piece_08` 4.74° (bar 10), and it recovers 6 of the 8 K3 losses. It **misses one bar**: `K3 = 113/141` against 121.
- **B2 is the best K1/K3 compromise**: 112/141 K1, 116/141 K3, median 3.39°, but only 2/8 K3 recoveries.
- **A2 alone is destructive** (62/141): the azimuthal residual's near-nullspace on short, near-planar sherds is not cured by `eps_n = 0.1`; the bounding rule keeps it from moving a line out of the piece but does not make the minimum right.
- **C1/C2 alone are the weakest** (68-77/141): scale-free Cao in a 60-basin pool picks centroid-collapsed basins, exactly as Ticket 01 predicted.
- **Arm D as built underperforms its own first stage** (92 vs A1's 110). Counted per piece on Authors' surfaces: Arm D loses 21 pieces that A1 returned within 10° (`Pot_A_Piece_06`, `Pot_A_Piece_08`, `Pot_B_Piece_05`, `Pot_B_Piece_07`, `Pot_C_Piece_04`, `Pot_D_Piece_18`, `Pot_D_Piece_23`, `Pot_E_Piece_02`, `Pot_F_Piece_04`, `Pot_F_Piece_05`, `Pot_G_Piece_01`, `Pot_G_Piece_02`, `Pot_G_Piece_03`, `Pot_H_Piece_08`, `Pot_H_Piece_09`, `Pot_I_Piece_07`, `Pot_I_Piece_16`, `Pot_I_Piece_17`, `Pot_I_Piece_20`, `Pot_I_Piece_23`, `Pot_J_Piece_02`) and gains only 3 (`Pot_D_Piece_27`, `Pot_E_Piece_03`, `Pot_I_Piece_26`). Stage 1 is A1; the later stages (joint thickness+azimuth NM, then Cao re-ranking, then `polish_guarded`) are what move the line away. That is a composition defect, not evidence that the components are wrong.

### Phase 1C — `def_3x` Juglet (9 pieces, estimates /3.0, GT at 1x)

| arm | surfaces | K1 | K3 | median ° | median `d_gt_to_est` mm | median `d_est_to_gt` mm | base piece |
|---|---|---|---|---|---|---|---|
| A2 | Authors = Own | **9/9** | **9/9** | 6.80 | 41.42 | 40.47 | `Juglet_Piece_7` |
| B1 | Authors = Own | 8/9 | 9/9 | 4.75 | 27.99 | 28.59 | `Juglet_Piece_7` |
| **D** | Authors = Own | 7/9 | 7/9 | 6.98 | 25.06 | 49.72 | `Juglet_Piece_7` |

**`SignAxisGuard = 0/18 (0.00%)`** for every arm and for the shipped lines. The 18 pairs are the GT join graph (`Juglet_large/Juglet_simple_graph.txt`) with each piece's `Juglet_Piece_N_T.txt` rotation applied; the guard was 4/18 in pass 1 and **all four flips came from `Juglet_Piece_7`** (base sherd, 33 mm across), which the `line_shift` bound removed. Applied without `T` every arm scores 6/18, so the `T` files are required — the pieces are not in one frame. `is_base_fragment` is true on `Juglet_Piece_7` only, for every arm.

### Part A gate — Arm D against every bar

| bar | required | Arm D (Authors) | verdict |
|---|---|---|---|
| K1 <= 10° | >= 109/141 | 92/141 | FAIL |
| K3 <= 10° | >= 121/141 | 94/141 | FAIL |
| K3 recovery of the 8 Ticket 01 losses | >= 4/8 | 3/8 | FAIL |
| median rank-0 angle | <= 2.78° | 3.995° | FAIL |
| `d_gt_to_est` median | <= 4.38 mm | 5.6613 mm | FAIL |
| Pot A `d_gt_to_est` | <= 3.5 mm | 2.724 mm | PASS |
| `Pot_A_Piece_08` rank-0 | <= 10° | 15.4651° | FAIL |
| Juglet K1 | >= 7/9 | 7/9 | PASS |
| Juglet K3 | >= 8/9 | 7/9 | FAIL |
| Juglet base | piece 7 only | piece 7 only | PASS |
| `SignAxisGuard` | 0/18 | 0/18 | PASS |

4 of 11 bars pass; **ALL = False** → early stop, Phase 2 not submitted. Own surfaces are uniformly better than Authors' (102 vs 92 K1) but still short of every count bar; the gate number is the Authors' one, as specified.

### Visual inspection of `C:/PR/artifacts/axis-parity-02/render02_landscape.png` (8 panels, inspected 2026-11-20 19:24)

Panels: `Pot_A_Piece_07` (57 mm), `Pot_A_Piece_06` (131 mm), `Pot_E_Piece_29` (61 mm), `Pot_I_Piece_20` (97 mm), `Pot_J_Piece_02` (122 mm), `Pot_J_Piece_07` (97 mm), `Pot_G_Piece_03` (79 mm), `Pot_A_Piece_08` (53 mm). Left column is the 3D edge cloud with the four axes; right column is the cylinder unfold about the GT axis, so a vertical black line at `x = 0` is the reference.

- In every panel the GT line is the vertical black line, and the blue (Authors), orange (`axes335`) and green (Arm D) lines sit **5-36° off it** — the picture agrees with the 3-5° median and the 15-63° tails in the tables.
- The dominant disagreement is **azimuthal foot placement, not tilt**: the estimator lines are displaced tens to hundreds of mm sideways in the unfold while staying roughly parallel to vertical. On a 53-131 mm sherd that is several object widths — consistent with `Pot_A_Piece_08` at 15.5° (Arm D) and `Pot_E_Piece_31` at 61.4°.
- **Arm D is visibly not better than the shipped lines.** On `Pot_I_Piece_20` and `Pot_J_Piece_02` the green line sits alongside the orange shipped line, both far from GT; on `Pot_A_Piece_07` the orange `axes335` line is the furthest displaced of the three while green is the closest; on `Pot_E_Piece_29` blue, orange and green nearly coincide (1-6°), which is where `d_gt_to_est` stays near 3 mm. On `Pot_J_Piece_07` all three estimators are displaced in different directions (`Authors` ≈ -340 mm, `axes335` ≈ +200 mm, `Arm D` ≈ +500 mm unfolded azimuth), i.e. the piece is small enough that each cost picks a different wall patch.
- Where the estimators agree with each other (`Pot_E_Piece_29`) they still sit a few degrees from GT: the agreement is not evidence of correctness, which is the same warning the 3D views give.

### Bottleneck (what the next ticket should carry)

1. **K3 is the wall, not K1.** A1 alone already matches or beats the shipped K1, median and `d_gt_to_est`; the shortfall is entirely "second and third returned lines are worse than shipped" (`K3 113` vs `121`). `keep_lines(tau=1.2, kmax=3)` keeps up to 3 lines, and on the 8 loss pieces A1's `best3 == rank0` in 7/8 cases — i.e. **the pool rarely contains the right line at all once the refinement bound is on**. The fix is pool/refinement diversity (more basins surviving refinement), not another cost.
2. **The profile cost cannot separate GT from decoy even in Hermite form** (150/150 pieces). Since the decoy is cheaper under every profile cost, ranking by thickness alone will keep choosing it; the ranking must be dominated by a residual that *is* discriminative. The azimuthal residual is discriminative on 25/150 pieces but has a near-nullspace on short planar sherds, so it can only be used **bounded** (as A1 does through the refinement, or as a tie-break), never as the ranking cost.
3. **Concrete next step**: ship A1's refinement + ranking (110/141 K1, 6/8 K3 recoveries) with `keep_lines` unchanged, and raise K3 by keeping more refined candidates per basin (e.g. refine the top 8 then keep the best 3 *by azimuthal residual*, not by thickness), plus a `line_shift`-bounded azimuthal polish. Arm D's current composition (joint NM then Cao re-rank) should be dropped rather than tuned: it loses a net 18 pieces of K1 (21 lost, 3 gained) for no K3 gain.

### Verified

- `verified: /c/PR/artifacts/axis-parity-02/gate02.tsv:12 -> authors arm_d_k1 = 92/141 (reference 109/141, FAIL)`
- `verified: /c/PR/artifacts/axis-parity-02/gate02.tsv:13 -> authors arm_d_k3 = 94/141 (reference 121/141, FAIL)`
- `verified: /c/PR/artifacts/axis-parity-02/gate02.tsv:15 -> authors arm_d_d_gt_to_est_median = 5.6613 mm (reference 4.38, FAIL)`
- `verified: /c/PR/artifacts/axis-parity-02/gate02.tsv:17 -> authors Pot_A arm_d = 2.724 mm (reference 3.5, PASS)`
- `verified: /c/PR/artifacts/axis-parity-02/gate02.tsv:24 -> Pot_A_Piece_08 arm_d_rank0 = 15.4651 deg (reference <=10, FAIL)`
- `verified: /c/PR/artifacts/axis-parity-02/gate02.tsv:25 -> juglet arm_d_k1 = 7/9 (PASS)`
- `verified: /c/PR/artifacts/axis-parity-02/gate02.tsv:27 -> juglet pairs_gt_90 = 0/18 (PASS)`
- `verified: /c/PR/artifacts/axis-parity-02/gate02.tsv:28 -> gate arm_d_all_bars = 4 (FAIL, early-stop)`
- `verified: axes02_summary.json bars->ALL = false; arms->arm_a1->authors K1 110/141, median 2.71, d_gt_to_est 4.338`
- `verified: ssh spartan sacct -X -j 35435516 -> COMPLETED 0:0 01:20:56; log line CORPUS-UNCHANGED`
- `verified: cd /c/PR/worktrees/sfs/02 && git apply --ignore-whitespace --check /c/PR/artifacts/axis-parity-02/impl_t02.diff -> APPLY-OK (6 files)`
- `verified: cd /c/PR/worktrees/sfs/02 && python -m pytest tests -q -> 42 passed in 33.13s`

Reading: cost-landscape-ablation-partial-no-e2e

**End state:** ready

