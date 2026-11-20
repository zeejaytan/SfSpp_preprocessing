# 05: Validate parallel dual-invariant axis selector (`A1 + B2`) on `141` GT pieces, `def_3x` Juglet, and 10-pot E2E

**What to build:** A prototype strictly inside Spartan `<run>/work/impl_t05/` (ZERO edits to tracked files in `SfSpp_preprocessing/` or `structure-from-sherds-pp/`, saved & verified as a clean `-p1` unified `impl_t05.diff` over `commit 9e0fe6a`, keeping `orient_base_axis` ON) implementing the **parallel dual-invariant axis selector (`arm_a1` calibrated Huber `width=0.05` on `e_hat_i` + `arm_b2` normal-consistent Hermite `(r, z)` profile, both with `line_shift <= 1 bbox diag`, deduped at `15°` with `A1` rank-0 first, capped at `K <= 2` or `K <= 3`, followed by `orient_base_axis`)** and validating:

1. **Phase 1 (Fast Offline Gate):** Evaluate **`dual_k2`** and **`dual_k3`** (plus standalone **`arm_a1`** and **`arm_b2`** on `def_3x` Juglet so all four selectors are benchmarked on Juglet) across all `141` GT-scored corpus pieces (on **both** Authors' `Surfaces/` and Our Own `MeshPreprocessingHeadless` surfaces including Pot H `/data/gpfs/projects/punim2657/SfSpp/runs/20261120-0227_2c14fe3_t01-diag-axis-parity/out_poth/geom`, reusing Ticket 01's cached 150-piece pools `/data/gpfs/projects/punim2657/SfSpp/runs/20261120-0227_2c14fe3_t01-diag-axis-parity/out/cache/*.npz` and Ticket 02's `work/run.json` Own-surface paths) AND `def_3x` Juglet (`9` pieces from `/data/gpfs/projects/punim2657/SfSpp/runs/20261117-0430_d272313_t80-default-on/out/cell_def_3x/geom/Juglet_Piece_{1..9}.S{0,1}`).
2. **Phase 2 (Conditional E2E Gate — ONLY if Phase 1 passes EVERY Part A bar):** Extract the winning variant end-to-end across **ALL `163` corpus pieces (`Pot A..J`)** + **all `9` `def_3x` Juglet pieces** (writing `.xyz` WITHOUT `canonicalize()` so `orient_base_axis` signs are preserved), then run full **10-pot E2E assembly (`Pot A..J`, 2 repeats each, `MOR1/2` + `K3R1/2`)** AND **`def_3x` Juglet (`4` repeats `r1..r4` + `cluster366.py` + `score58`)**.

**Answers:** E1
**Blocked by:** None (Ticket 02 resolved at `46f064c` / `4246c74`)
**Status:** in-progress
**Working in:** chat on Thinkbook16 (2026-11-20)
**Branch:** 05-parallel-a1-b2-selector-and-e2e, in /c/PR/worktrees/sfs/05
**Worker:** dsh one-shot subagent w05-axis-parity
**Budget:** large 8
**Hand-over:** DeepSeek — hidden acceptance check at `C:/PR/artifacts/dsh-handover/axis-parity-05/accept.py` to be staged before dispatch

---

## 1. Why Ticket 05 Exists (Verified in Ticket 02 `46f064c` / `4246c74`)

Ticket 02 (`20261120-1430_9e0fe6a_t02-cost-landscape`) proved:
- **Bug 1 fixed by `arm_a1`:** Calibrating `robustifier_huber(width=0.05)` on `e_hat_i` with `line_shift <= size` achieves **`110/141` `K1`**, **`2.7054°` median** (beats Authors `2.78°` & `axes335` `3.06°`), **`4.3383 mm` `d_gt_to_est`** (beats Authors `4.38 mm` & `axes335` `4.53 mm`), **`Pot A` `2.4733 mm`** (vs `6.97 mm` shipped), **`Pot_A_Piece_08 = 4.741°`**, and **`6/8` K3 recoveries** on Authors' surfaces (`116/141 K1`, `2.5631°`, `3.7781 mm` on Own surfaces). Standalone `arm_a1` missed only `K3 = 113/141` vs `121/141`.
- **Strong complementarity with `arm_b2` (normal-consistent Hermite `(r, z)` profile):** `arm_b2` independently reaches `112/141 K1`, `116/141 K3`, `4.3370 mm` `d_gt_to_est`, `Pot_A_Piece_08 = 3.42°`, and recovers `Pot_E_Piece_31 (5.35°)` + `Pot_E_Piece_14 (9.82°)`. Combining **`A1` + `B2` in parallel** (`min(A1_r0, B2_r0) <= 10°` at `K <= 2`) jumps to **`126/141` (`89.4%`)** on Authors' surfaces (`128/141` at `K <= 3`) and **`125/141` (`88.7%`)** on Own surfaces (`128/141` at `K <= 3`), recovering **`7/8` K3 losses** (`Pot_A_Piece_07`, `Pot_D_Piece_23`, `Pot_E_Piece_29`, `Pot_E_Piece_31`, `Pot_F_Piece_05`, `Pot_I_Piece_20`, `Pot_J_Piece_02`), while keeping **ALL `7/7` Pot G pieces at `K = 1`** (`15°` dedup merges `A1` and `B2` on every Pot G piece!).
- **Serial chaining rejected:** `Arm D` lost 21 `A1` pieces (`92/141`) when chaining joint NM and Cao re-ranking serially. Running `A1` and `B2` **in parallel** keeps `A1` rank-0's precision intact and uses `B2` strictly as a complementary hypothesis when they disagree by `>= 15°`.

---

## 2. Design Constraints & Critical Frame/Metric Rules (Non-Negotiable)

1. **Prototype boundary:** Create Spartan run dir `/data/gpfs/projects/punim2657/SfSpp/runs/<YYYYMMDD-HHMM>_<git7>_t05-dual-a1-b2/`. Populate `<run>/work/impl_t05/` from `git archive 9e0fe6a` of `sfs_axes/ tests/ scripts/run_benchmark_172.py`, apply `/data/gpfs/projects/punim2657/SfSpp/runs/20261120-1430_9e0fe6a_t02-cost-landscape/work/impl_t02.diff` cleanly (so `sfs_axes/t02/*` and `tests/test_t02_objectives.py` exist unchanged), and add new prototype files ONLY (`sfs_axes/t05/__init__.py`, `sfs_axes/t05/dual.py`, `tests/test_t05_dual.py`, plus runner helpers under `<run>/work/`). Export clean unified diff `<run>/work/impl_t05.diff` over `9e0fe6a` (`git apply --ignore-whitespace --check` must pass against clean `9e0fe6a`) and pass `>= 42` existing + new prototype unit tests. **Leave tracked files in `SfSpp_preprocessing/` and `structure-from-sherds-pp/` 100% untouched.**
2. **Exact parallel selector specification (keep `arm_a1` and `arm_b2` UNCHANGED from `sfs_axes/t02/arms.py`):**
   - Run `res_a1 = arm_a1(reps, sizes, walls_s, C, size)` and `res_b2 = arm_b2(reps, sizes, walls_s, C, size)` independently on the same 60-basin pool (`_cands(reps, sizes, basins=60)`), each keeping `line_shift <= size` (`_bounded`) and `keep_lines(tau=1.2, kmax=3)`.
   - **`dual_k2`:** Start with `A1` rank-0 (`vt_a1[:, 0]`). If `vt_b2` has `>= 1` column and unsigned `direction_angle_deg(vt_b2[0:3, 0], vt_a1[0:3, 0]) >= 15.0`, append `vt_b2[:, 0]`. Cap at `K <= 2`. Apply `orient_base_axis(lines, C)`.
   - **`dual_k3`:** Start with `dual_k2`'s ordered list, then scan remaining secondary candidates `[vt_a1[:, 1:], vt_b2[:, 1:]]` in order (`A1` secondaries before `B2` secondaries), appending any candidate whose unsigned `direction_angle_deg` is `>= 15.0` from every already-kept line until `K == 3`. Apply `orient_base_axis(lines, C)`.
   - Handle `res_a1 is None` or `res_b2 is None` safely. Zero per-pot, per-piece, or object-size constants.
   - New unit tests in `tests/test_t05_dual.py` must cover: `dual_k2` and `dual_k3` ordering & `A1` rank-0 precedence; `15°` dedup collapsing agreeing `A1`/`B2` to `K=1` while preserving disagreeing `B2` at rank-1; `orient_base_axis` sign preservation on inverted base disks (`dir_z < 0` not clobbered); normal-sign invariance (`N -> -N`); empty/None fallback safety.
3. **Dual radial metrics (report BOTH side-by-side in JSON, TSV, and ticket tables):**
   - `d_gt_to_est = radial_axial_errors(gt[3:6], vt[0:3], vt[3:6])[0]` (Primary physical vessel-frame bar: Authors `4.38 mm`, `Pot A 1.92 mm`).
   - `d_est_to_gt = radial_axial_errors(vt[3:6], gt[0:3], gt[3:6])[0]` (Secondary foot metric: Authors `11.64 mm`, `Pot A 8.97 mm`).
4. **`def_3x` Juglet frame & `SignAxisGuard` rules (learned in Ticket 02):**
   - `Dataset/Juglet_GT/Juglet_Piece_{1..9}_Axis.xyz` is ALREADY in `1x` mm — divide **ONLY the estimate `vt[3:6]` by `3.0`** before computing `d_gt_to_est` and `d_est_to_gt` (NEVER divide GT!).
   - **`SignAxisGuard`:** Apply each piece's `Dataset/Juglet_large/Juglet_Piece_N_T.txt` rotation before comparing the 18 adjacent pairs in `Dataset/Juglet_large/Juglet_simple_graph.txt`. Verify `pairs_gt_90 == 0/18 (0.00%)` on rank-0 AND also check/report worst-case sign alignment across all returned candidates (`k = 0..K-1`).
5. **NEVER `canonicalize()` when writing Phase 2 `.xyz` files:** `io_axes.write_axes` / `run_benchmark_172`-style writer must write `[v[3:6], v[0:3]]` directly from `orient_base_axis` output WITHOUT flipping `dir_z < 0` back to `dir_z >= 0` (`run_benchmark_172.py:115`).
6. **Heavy compute strictly on Spartan compute nodes (`sbatch` / `srun`):** Poll every `sbatch` (`sacct -X`), record EVERY job ID + final `State`/`ExitCode`, append rows to `/data/gpfs/projects/punim2657/SfSpp/runs/index.tsv` (`verdict` and `human_note` blank), and verify `CORPUS-UNCHANGED`.

---

## 3. Phase 1: Offline Validation & Part A Go/No-Go Gate

1. Using Ticket 01's cached pools (`20261120-0227_2c14fe3_t01-diag-axis-parity/out/cache/*.npz`) + Own `MeshPreprocessingHeadless` surfaces (`20261120-1430_9e0fe6a_t02-cost-landscape/work/run.json` paths + Pot H `20261120-0227_2c14fe3_t01-diag-axis-parity/out_poth/geom`) + `def_3x` Juglet (`20261117-0430_d272313_t80-default-on/out/cell_def_3x/geom/Juglet_Piece_{1..9}.S{0,1}`):
   - Evaluate **`dual_k2`** and **`dual_k3`** across all `141` GT pieces (Authors' & Own surfaces, per-pot `Pot A..J` tables including `K`-distribution per pot and `Pot G 7/7 K=1` check, plus all 14 Ticket 01 loss stems).
   - Evaluate **`arm_a1`**, **`arm_b2`**, **`dual_k2`**, and **`dual_k3`** on **`def_3x` Juglet** (`9` pieces, estimates `/ 3.0`, GT at 1x, `is_base_fragment`, `SignAxisGuard` with `T` rotations on rank-0 and multi-candidate worst case).
2. **Part A Go/No-Go Bar (must pass EVERY item on Authors' surfaces & `def_3x` Juglet to enter Phase 2):**
   - `K1 <= 10°`: `>= 109/141`
   - `K3 <= 10°`: `>= 121/141`
   - K3 recovery of Ticket 01's 8 K3 loss pieces (`Pot_A_Piece_07`, `Pot_D_Piece_23`, `Pot_E_Piece_25`, `Pot_E_Piece_29`, `Pot_E_Piece_31`, `Pot_F_Piece_05`, `Pot_I_Piece_20`, `Pot_J_Piece_02`): `>= 4/8`
   - Overall rank-0 angle median: `<= 2.78°`
   - Overall physical `d_gt_to_est` median: `<= 4.38 mm`
   - `Pot A` `d_gt_to_est` median: `<= 3.5 mm`
   - `Pot_A_Piece_08` rank-0 angle: `<= 10°`
   - `Pot G` (`7/7` pieces): `K = 1` on `7/7` pieces (multi-line decoy guard)
   - `def_3x` Juglet (`/ 3.0` on estimate only): `K1 >= 7/9`, `K3 >= 8/9`, `is_base_fragment=True` on `Juglet_Piece_7` only, `SignAxisGuard = 0/18 (0.00%)`
3. **Variant selection rule if both `dual_k2` and `dual_k3` pass Part A:**
   - Default to **`dual_k2`** (fewer candidates = lower beam-search decoy risk), **UNLESS** `dual_k3` beats `dual_k2` by **`>= 3` GT pieces on Authors' `K3`** OR strictly improves **`def_3x` Juglet `K3`** (e.g. `8/9 -> 9/9`) while holding `Pot G 7/7` at `K = 1` and overall `mean_K <= 2.0`.
4. **Early-Stop Rule:** If NEITHER `dual_k2` nor `dual_k3` clears EVERY Part A bar above, **DO NOT submit Phase 2 jobs**; fetch Phase 1 deliverables, visually inspect `render05_dual.png`, write up the bottleneck, and close with `Reading: dual-selector-misses-part-a-no-e2e`.

---

## 4. Phase 2 (ONLY when Phase 1 Passes): Full Extraction + 10-Pot & `def_3x` Juglet E2E Assembly

1. **Full `163`-piece corpus + `9`-piece `def_3x` Juglet axis extraction:**
   - Extract the winning variant (`dual_k2` or `dual_k3`) from `<run>/work/impl_t05/` end-to-end across **ALL `163` corpus pieces (`Pot A..J`)** into `<run>/out/axes05_dual/` (Ticket 01's cache covers only `150` stems, whereas `Pot A..J` has `163` pieces in `Surfaces/`, so Phase 2 must run fresh PotSAC union pools with `--seeds 10 --step 10 --cap 6` over all `163` pieces using Authors' `Surfaces/`, writing `[v[3:6], v[0:3]]` WITHOUT `canonicalize()`!).
   - Verify on the `141` GT subset that the freshly extracted `<run>/out/axes05_dual/` reproduces Phase 1's pass bars (no regression from fresh pool draw) and confirm `CORPUS-UNCHANGED`.
   - Write `<run>/out/axes05_juglet_def3x/Juglet_Piece_{1..9}_Axis.xyz` (plus `Pot_JUGLET_Piece_0N_Axis.xyz` if required by the stager) without `canonicalize()`.
2. **All 10 paper pots (`Pot A..J`, 2 repeats each, `MOR1/2` + `K3R1/2`) in parallel:**
   - For each `P` in `A B C D E F G H I J`, clone `/data/gpfs/projects/punim2657/SfSpp/runs/20261109-1426_ecd5bb8_t319-pot<P>` into `/data/gpfs/projects/punim2657/SfSpp/runs/<STAMP>_<git7>_t05-pot<P>` following `SfSpp_preprocessing/.scratch/pota-repro/t323/make_e2e_323.sh`:
     - Point `AX_318=<run>/out/axes05_dual`, update `--job-name=t05-pot<P>`, assert `grep -q "^AX_318=<run>/out/axes05_dual" submit.sbatch` and `grep -q "_MOR1" submit.sbatch`.
     - Run all 4 arms per pot (`${P}_MOR1`, `${P}_MOR2` authors' control; `${P}_K3R1`, `${P}_K3R2` winning `dual`), verify `CORPUS-UNCHANGED`, and score against both `t323` floors and `t323` achieved scores (`/data/gpfs/projects/punim2657/SfSpp/runs/20261110-0740_d628fc0_t323-pot<P>/score/acc.tsv`):
       - `Pot A`: `8/8, 15/15`
       - `Pot B`: `9/9, 15/15`
       - `Pot C`: `4/4, 5/5`
       - `Pot D`: floor `>=23/28, >=55/69` (target `26/28, 63/69`)
       - `Pot E`: `31/31, 62/62` (floor `>=29/31, >=57/62`)
       - `Pot F`: `5/5, 7/7`
       - `Pot G`: `7/7, 10/10`
       - `Pot H`: `11/11, 17/17`
       - `Pot I`: `>=25/26, >=59/62`
       - `Pot J`: `>=8/11, >=16/21`
     - Verify `MOR1/2` controls remain green on every pot.
3. **`def_3x` Juglet (`4` repeats `r1..r4` + controls):**
   - Run using `<run>/out/axes05_juglet_def3x/` on the exact `t363`/`t366` container & shim (`floor 10`, shim md5 `0c216463ae27fe4571b200cc2292da99`, `XY_BREAK=1`, `XY_STATE=1`, `SFS_AXIS_LOCK_ICP` unset, `SFS_AXIS_SIGN=1`; remember banner prints `on`).
   - Score with `score58` (`13.788` tree = `4.596 mm` real) AND `/data/gpfs/projects/punim2657/SfSpp/runs/20261119-0412_bf3fc0b_t368-bounded-4dof-cref/tools/cluster366.py` (md5 `81f347cc1f80b7b84a163337959ec073`).
   - Pass bar: best of 4 repeats `9/9` sherds, **`>= 10/18` edges**, vertex cluster `9/9 <= 0.50 mm`, `4/4` Piece 7 joins (`3-7, 6-7, 7-8, 7-9`).

---

## 5. Deliverables & Visual Inspection (`C:/PR/artifacts/axis-parity-05/`)

- **Always fetched:**
  - `axes05_summary.json` — `dual_k2` & `dual_k3` metrics on `141` GT pieces (Authors' & Own surfaces, per-pot `Pot A..J` including `Pot G` `K=1` counts, both `d_gt_to_est` and `d_est_to_gt`, all 14 loss stems), `def_3x` Juglet (`arm_a1`, `arm_b2`, `dual_k2`, `dual_k3`, `/ 3.0` on estimate only, `pairs_gt_90 = 0/18`, `Juglet_Piece_7` base), variant selection decision, `sacct` table, and (when Phase 2 runs) full `163`-piece extract consistency check + Phase 2 E2E summary.
  - `gate05.tsv` — Exact 7-column header `group\tpiece\tmetric\tvalue\treference\tverdict\tnote` covering `dual_k2`, `dual_k3`, `own`, `juglet`, `d_gt_to_est`, `d_est_to_gt`, and (when Phase 2 runs) `potA..potJ` + `juglet_e2e`.
  - `render05_dual.png` — 8-row 3D + `(r, z)` unfold visual comparison (`Pot_A_Piece_07`, `Pot_A_Piece_06`, `Pot_E_Piece_29`, `Pot_E_Piece_31`, `Pot_I_Piece_20`, `Pot_J_Piece_02`, `Pot_G_Piece_03`, `Pot_A_Piece_08`) showing GT, Authors, `axes335`, and winning `dual`. **Visually inspect before writing `Reading:`.**
  - `impl_t05.diff` — Clean unified diff against `9e0fe6a` verified with `git apply --ignore-whitespace --check`.
- **Also fetched when Phase 2 runs:**
  - `render05_tenpots.png` — 11-panel E2E assembly montage (`Pot A..J` + `def_3x` Juglet) visually inspected before writing `Reading:`.
  - `score/` — `acc_pot{A..J}.tsv` (10 files) plus `score/juglet/` (`score58` + `cluster366` JSONs).
- Update `## Comments` in this ticket in worktree `C:/PR/worktrees/sfs/05` with exact Spartan run dir(s), `sacct -X` table (`COMPLETED 0:0`), `CORPUS-UNCHANGED`, `runs/index.tsv` confirmation, visual inspection findings, one bare `Reading:` line, and `**End state:** ready`.

---

## 6. Readings (pick one verbatim on a bare `Reading:` line)

- `dual-selector-achieves-author-parity-and-passes-ten-pots` — Phase 1 clears EVERY Part A bar AND Phase 2 passes all `10/10` pots (meeting/beating `t323` floors with `MOR1/2` green) + `def_3x` Juglet (`9/9`, `>= 10/18` edges, `<= 0.50 mm` cluster, `4/4` Piece 7 joins, `0/18 SignAxisGuard`); ready to ship in Ticket 03.
- `dual-selector-improves-axes-but-misses-e2e-bar` — Phase 1 clears its gate (so Phase 2 runs), OR Phase 2 improves/holds most pots while missing one or more E2E `t323`/Juglet targets; report exact pot/edge regression.
- `dual-selector-misses-part-a-no-e2e` — Phase 1 early-stop triggered cleanly (neither `dual_k2` nor `dual_k3` cleared every Part A bar, so Phase 2 jobs were not submitted); report exact gap.
- `blocked: missing-or-failed-control` — Any `MOR1/2` control drops unexpectedly, required Ticket 01/02/319/366 inputs or containers are unavailable, or `CORPUS-UNCHANGED` fails.

## Out of scope

- Editing ANY tracked file in `SfSpp_preprocessing/` or `structure-from-sherds-pp/`, merging to `main`, pushing to `main`, or running `ticket_close.sh`.

## Acceptance

- [ ] Zero tracked source edits (`git diff origin/main --name-only` touches only this ticket); `<run>/work/impl_t05.diff` cleanly applies over `9e0fe6a` (`git apply --ignore-whitespace --check`) and unit tests pass (`>= 42` existing + new `tests/test_t05_dual.py` checks).
- [ ] Phase 1 benchmarks `dual_k2` and `dual_k3` on `141` GT pieces (Authors' & Own surfaces, both `d_gt_to_est` and `d_est_to_gt`, `Pot G 7/7 K=1` check) AND `def_3x` Juglet (`arm_a1`, `arm_b2`, `dual_k2`, `dual_k3`, `/ 3.0` on estimate only, `0/18 SignAxisGuard`, `Juglet_Piece_7` only base), with `sacct -X COMPLETED 0:0` and `CORPUS-UNCHANGED`.
- [ ] Phase 1 Go/No-Go gate enforced cleanly: when Phase 1 passes EVERY Part A bar, Phase 2 full `163`-piece + `9`-piece Juglet extraction and `10`-pot (`Pot A..J`) + `def_3x` Juglet E2E assembly complete (`COMPLETED 0:0`, `CORPUS-UNCHANGED`, `runs/index.tsv` appended); otherwise Phase 1 early-stop is documented with zero Phase 2 spend.
- [ ] `C:/PR/artifacts/axis-parity-05/{axes05_summary.json,gate05.tsv,render05_dual.png,impl_t05.diff}` (plus `render05_tenpots.png` & `score/acc_pot{A..J}.tsv` + `score/juglet/` when Phase 2 runs) fetched locally and visually inspected before writing bare `Reading:` and `**End state:** ready`.
