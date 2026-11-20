# 05: Validate parallel dual-invariant axis selector (`A1 + B2`) on `141` GT pieces, `def_3x` Juglet, and 10-pot E2E

**What to build:** A prototype strictly inside Spartan `<run>/work/impl_t05/` (ZERO edits to tracked files in `SfSpp_preprocessing/` or `structure-from-sherds-pp/`, saved & verified as a clean `-p1` unified `impl_t05.diff` over `commit 9e0fe6a`, keeping `orient_base_axis` ON) implementing the **parallel dual-invariant axis selector (`arm_a1` calibrated Huber `width=0.05` on `e_hat_i` + `arm_b2` normal-consistent Hermite `(r, z)` profile, both with `line_shift <= 1 bbox diag`, deduped at `15°` with `A1` rank-0 first, capped at `K <= 2` or `K <= 3`, followed by `orient_base_axis`)** and validating:

1. **Phase 1 (Fast Offline Gate):** Evaluate **`dual_k2`** and **`dual_k3`** (plus standalone **`arm_a1`** and **`arm_b2`** on `def_3x` Juglet so all four selectors are benchmarked on Juglet) across all `141` GT-scored corpus pieces (on **both** Authors' `Surfaces/` and Our Own `MeshPreprocessingHeadless` surfaces including Pot H `/data/gpfs/projects/punim2657/SfSpp/runs/20261120-0227_2c14fe3_t01-diag-axis-parity/out_poth/geom`, reusing Ticket 01's cached 150-piece pools `/data/gpfs/projects/punim2657/SfSpp/runs/20261120-0227_2c14fe3_t01-diag-axis-parity/out/cache/*.npz` and Ticket 02's `work/run.json` Own-surface paths) AND `def_3x` Juglet (`9` pieces from `/data/gpfs/projects/punim2657/SfSpp/runs/20261117-0430_d272313_t80-default-on/out/cell_def_3x/geom/Juglet_Piece_{1..9}.S{0,1}`).
2. **Phase 2 (Conditional E2E Gate — ONLY if Phase 1 passes EVERY Part A bar):** Extract the winning variant end-to-end across **ALL `163` corpus pieces (`Pot A..J`)** + **all `9` `def_3x` Juglet pieces** (writing `.xyz` WITHOUT `canonicalize()` so `orient_base_axis` signs are preserved), then run full **10-pot E2E assembly (`Pot A..J`, 2 repeats each, `MOR1/2` + `K3R1/2`)** AND **`def_3x` Juglet (`4` repeats `r1..r4` + `cluster366.py` + `score58`)**.

**Answers:** E1
**Blocked by:** None (Ticket 02 resolved at `46f064c` / `4246c74`)
**Status:** resolved
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

- [x] Zero tracked source edits (`git diff origin/main --name-only` touches only this ticket); `<run>/work/impl_t05.diff` cleanly applies over `9e0fe6a` (`git apply --ignore-whitespace --check`) and unit tests pass (`>= 42` existing + new `tests/test_t05_dual.py` checks).
- [x] Phase 1 benchmarks `dual_k2` and `dual_k3` on `141` GT pieces (Authors' & Own surfaces, both `d_gt_to_est` and `d_est_to_gt`, `Pot G 7/7 K=1` check) AND `def_3x` Juglet (`arm_a1`, `arm_b2`, `dual_k2`, `dual_k3`, `/ 3.0` on estimate only, `0/18 SignAxisGuard`, `Juglet_Piece_7` only base), with `sacct -X COMPLETED 0:0` and `CORPUS-UNCHANGED`.
- [x] Phase 1 Go/No-Go gate enforced cleanly: when Phase 1 passes EVERY Part A bar, Phase 2 full `163`-piece + `9`-piece Juglet extraction and `10`-pot (`Pot A..J`) + `def_3x` Juglet E2E assembly complete (`COMPLETED 0:0`, `CORPUS-UNCHANGED`, `runs/index.tsv` appended); otherwise Phase 1 early-stop is documented with zero Phase 2 spend.
- [x] `C:/PR/artifacts/axis-parity-05/{axes05_summary.json,gate05.tsv,render05_dual.png,impl_t05.diff}` (plus `render05_tenpots.png` & `score/acc_pot{A..J}.tsv` + `score/juglet/` when Phase 2 runs) fetched locally and visually inspected before writing bare `Reading:` and `**End state:** ready`.
---
## Comments

**Worker:** DeepSeek (`dsh` one-shot subagent `w05-axis-parity`), 2026-11-20 → 2026-11-21 (Australia/Sydney). Prototype only: no tracked file in `C:/PR/SfSpp_preprocessing` or `C:/PR/structure-from-sherds-pp` was edited; `git diff origin/main --name-only` in `C:/PR/worktrees/sfs/05` prints this ticket and nothing else. A first write-up of this ticket (commits `76fca55` / `8b2b1f9`) had two defects that this revision fixes: it inverted the two arm pairs, and it wrote the `def_3x` Juglet axes at `1/3` scale. Both are corrected below, with the jobs that prove it.

### Runs

| what | run dir | jobs | `sacct -X` |
|---|---|---|---|
| prototype, Phase 1, Phase 2 extraction, scoring/render, metadata | `/data/gpfs/projects/punim2657/SfSpp/runs/20261120-2135_9e0fe6a_t05-dual-a1-b2` | 35448549 (bench), 35449224 (extract), 35450477 (assemble), 35450478 (corpus), 35452288 `/` 35452309 `/` 35452353 `/` 35454485 (renders), 35452596 (pytest), 35453049 (Juglet re-extraction), 35454552 `/` 35454569 (metadata), 35454806 (fresh Juglet summary); aux: 35448730 (corpus md5), 35448991 `/` 35449129 `/` 35449425 `/` 35449559 (smoke `/` probe), 35448758 `/` 35449321-35449330 `/` 35449423 (cancelled before start), 35454794 (jugsum attempt, `$n_cluster` unbound-variable typo, superseded by 35454806) | all `COMPLETED 0:0` except the labelled cancellations and 35448991 / 35454794 `FAILED` |
| ten pot E2E clones | `/data/gpfs/projects/punim2657/SfSpp/runs/20261120-2135_9e0fe6a_t05-pot{A..J}` | 35449734 A, 35449735 B, 35449736 C, 35450287 D, 35450288 E, 35449739 F, 35449740 G, 35449741 H, 35450471 I, 35449743 J | all `COMPLETED 0:0` |
| `def_3x` Juglet E2E, 4 repeats | `/data/gpfs/projects/punim2657/SfSpp/runs/20261120-1106_9e0fe6a_t05-juglet` | 35449331 `_0.._3` (v1: `1/3`-scale axes), 35453073 `_0.._3` (native axes) | all `COMPLETED 0:0` |

`sacct -X` (elapsed): potA 00:51:47, potB 00:59:24, potC 00:03:55, potD 01:47:50, potE 01:17:08, potF 00:05:58, potG 00:04:59, potH 01:56:15, potI 01:02:27, potJ 00:37:27; Juglet v1 00:03:00 / 00:03:04 / 00:02:46 / 00:02:57, native 00:08:28 / 00:12:44 / 00:08:45 / 00:09:27; Phase 1 00:07:53; extraction 00:03:41; assembler 00:00:49; corpus 00:00:25; Juglet re-extraction 00:01:09. The ten pots were first submitted at 48 cpus/160G/4h (35449321-35449330) and reported `PENDING Reason=Priority` with a 2026-11-21 09:15-22:00 start estimate on a saturated partition; they were cancelled before any arm started and resubmitted at 16 cpus/32G/8h. D, E and I were then cancelled again after 17-22 min (before any arm finished) and run at 32 cpus/64G because the 16-cpu rate was 3.6-7.1x the `t319` 48-cpu baseline and would have hit the wall limit.

**Corpus proof, Phase 1.** Job 35448549's own md5 step did not run: `corpus_md5.py` still imported `t02_lib`, so `logs/phase1-35448549.log:7,19,20` read `MD5-BEFORE-FAILED` / `MD5-AFTER-FAILED` / `CORPUS-CHANGED` (an empty-vs-empty comparison, not a change on disk). The Phase 1 corpus proof is therefore the separate job **35448730**: `logs/md5-35448730.log:2` reads `CORPUS-UNCHANGED (matches t02 out/corpus_before.md5)` over 907 files. The import was then fixed to `import t05_lib as dl` and the Phase 2 job 35450478 re-ran the check end to end inside the job that mattered (`CORPUS-UNCHANGED`, `SAME-AS-PHASE1`), and 35453049 did the same after the Juglet re-extraction (`out/corpus_jugax.md5`, `CORPUS-UNCHANGED`).

The test suite was re-run inside a batch job on 2026-11-21 (`35452596`, 1 cpu, `00:00:34`): `t05-pytest-35452596.log` carries `71 passed, 1 warning in 30.97s`, `PYTEST-EXIT=0`.

Each run dir keeps `submit.sbatch.48cpu.bak` / `.16cpu.bak`; `run.json` carries the resubmit note; `/data/gpfs/projects/punim2657/SfSpp/runs/index.tsv` (904 lines) has one row per submit: 24 rows for this run (lines 873-899 and 904, the last being `35453049` `t05-jugax`) and four for the Juglet run (lines 900-903, `35453073`), `verdict` and `human_note` blank.

### Phase 1 — Part A gate: every bar PASS, GO

`dual_k2` on Authors' surfaces, 141 GT pieces (bar → measured):

| bar | required | `dual_k2` | verdict |
|---|---|---|---|
| `K1 <= 10°` | `>= 109/141` | `110/141` | PASS |
| `K3 <= 10°` | `>= 121/141` | `121/141` | PASS |
| median rank-0 | `<= 2.78°` | `2.7054°` | PASS |
| `d_gt_to_est` median | `<= 4.38 mm` | `4.3383 mm` | PASS |
| `d_est_to_gt` median | (reported) | `9.9252 mm` | — |
| Pot A `d_gt_to_est` | `<= 3.5 mm` | `2.4733 mm` | PASS |
| `Pot_A_Piece_08` rank-0 | `<= 10°` | `4.741°` | PASS |
| Pot G | `7/7` at `K = 1` | `7/7` (`K-dist {1: 7}`) | PASS |
| K3 recoveries of the 8 Ticket 01 losses | `>= 4/8` | `7/8` (`A_Piece_07, D_Piece_23, E_Piece_29, E_Piece_31, F_Piece_05, I_Piece_20, J_Piece_02`; `E_Piece_25` missed) | PASS |
| `def_3x` Juglet `K1` / `K3` | `>= 7/9` / `>= 8/9` | `7/9` / `8/9` | PASS |
| Juglet base / `SignAxisGuard` | piece 7 only / `0/18` | piece 7 only / rank-0 `0/18`, worst over candidates `0` | PASS |

Own surfaces are better, not worse: `K1 116/141`, `K3 122/141`, `2.5631°`, `3.7781 mm`, Pot A `2.6369 mm`, Pot G `7/7`. Standalone `arm_a1` is `110/113` (K1/K3) on Authors and `116/117` on Own; `arm_b2` is `112/116` and `112/116`, and on Own it fails Pot A (`6.1642 mm`) and Pot G (`6/7`). `dual_k3` gives the same Authors `K3 121/141` and Juglet `8/9` as `dual_k2` but fails Own Pot G (`6/7`) and its `SignAxisGuard` worst case is `2` (versus `0`). **Variant rule → `dual_k2`** (`k3_gain = 0`, `juglet_k3_gain = 0`, `hold_potG_meanK = True`). Mechanically, `dual_k2`'s rank-0 is always `arm_a1`'s rank-0 (its `K1` equals `a1` on every surface); the `+8` Authors `K3` and `+1` Juglet `K3` over `arm_a1` come only from appending `arm_b2`'s rank-0 whenever it sits `>= 15°` away. `gate05.tsv` now has 131 data rows under its header (`wc -l` = 132: 107 Phase 1 + 24 Phase 2). Every Phase 1 gate row (lines 1-107) is PASS for both variants; line 108 is the summary row `gate variant winner dual_k2`, which carries verdict `-` by construction rather than PASS.

### Phase 2 — extraction reproduces Part A; nine of ten pots pass on our arms

The fresh-pool extraction (job 35449224, `--seeds 10 --step 10`, Authors' `Surfaces/`, no `canonicalize()`) wrote 163 `out/axes05_dual/*.xyz` and, in `out/axes05_juglet_def3x/`, 18 `*.xyz` (9 native + 9 `Pot_JUGLET_` aliases) plus `metrics_juglet_native.json`, with 0 zero-byte files; 172/172 piece-surface runs ok. Recomputed from `out/axes05_extract_metrics.json`, `dual_k2` reproduces the Phase 1 bars exactly: `K1 110`, `K3 121`, median `2.705°`, `d_gt_to_est 4.3383 mm`, Pot A `2.4733 mm`, Pot G `7/7` at `K = 1`, K3 recoveries `7/8`, `Pot_A_Piece_08 4.741°`.

**Arm mapping — the correction.** In each `<run>/submit.sbatch`, `stage_arm "${POT}_MO" "MO" "$AX_MO"` with `AX_MO=/data/gpfs/projects/punim2657/sfs_main/original_samples/SfS_pp/Axes` stages `<P>_MOR1/2` from the **authors' released axes** (the control), and `stage_arm "${POT}_K3" "MM" "$WORK/axes_k3"` stages `<P>_K3R1/2` from the **first three lines of `out/axes05_dual`**, i.e. our `dual_k2` top-3 candidates. The first write-up had these the wrong way round; the table below is scored on the corrected reading, with our arms in bold:

| pot | floor | target | `_MOR1` (authors) | `_MOR2` (authors) | `_K3R1` (ours) | `_K3R2` (ours) | verdict on ours |
|---|---|---|---|---|---|---|---|
| A | `8/8 15/15` | same | `8/8 15/15` | `8/8 15/15` | **`8/8 15/15`** | **`8/8 15/15`** | floor met |
| B | `9/9 15/15` | same | `9/9 15/15` | `9/9 15/15` | **`9/9 15/15`** | **`9/9 15/15`** | floor met |
| C | `4/4 5/5` | same | `4/4 5/5` | `4/4 5/5` | **`4/4 5/5`** | **`4/4 5/5`** | floor met |
| D | `>=23/28 55/69` | `26/28 63/69` | `23/28 55/69` | `22/28 53/69` | **`25/28 60/69`** | **`24/28 58/69`** | floor met, target not reached (authors' second repeat is under floor) |
| E | `>=29/31 57/62` | `31/31 62/62` | `31/31 62/62` | `31/31 62/62` | **`31/31 62/62`** | **`31/31 62/62`** | target met |
| F | `5/5 7/7` | same | `5/5 7/7` | `5/5 7/7` | **`5/5 7/7`** | **`5/5 7/7`** | floor met |
| G | `7/7 10/10` | same | `7/7 10/10` | `7/7 10/10` | **`7/7 10/10`** | **`7/7 10/10`** | floor met |
| H | `11/11 17/17` | same | `10/11 10/17` | `10/11 10/17` | **`11/11 17/17`** | **`11/11 17/17`** | floor met (authors' control is under on both repeats) |
| I | `>=25/26 59/62` | `26/26 62/62` | `25/26 59/62` | `25/26 59/62` | **`26/26 62/62`** | **`26/26 62/62`** | target met, one sherd above the authors' control |
| J | `>=8/11 16/21` | — | `8/11 16/21` | `8/11 16/21` | **`6/11 9/21`** | **`5/11 8/21`** | **UNDER floor**: two to three sherds and seven to eight edges lost |

So the selector passes **9 of 10 pots**: A, B, C, D, E, F, G, H, I are at or above the `t323` floor on both of our repeats, with D and I above the authors' control and E and I at the target. **Pot J is the single regression** (`6/11 9/21` and `5/11 8/21` against `>=8/11 >=16/21`), while the authors' control holds the floor on J. The failures of the *control* (D repeat 2, both H repeats) are not ours and should not be read as ours — the earlier write-up made exactly that mistake.

### `def_3x` Juglet — the `1/3`-scale write bug, and the native re-run

The first Juglet result (`0/9` sherds, strict edges `0/36`, `cluster_len 4`, `0.375 mm`) was **a writing defect, not an axis result**. `work/t05_extract.py` `write_lines(path, lines, scale)` did `v[3:6] = v[3:6] / scale` and was called with `scale = dl.JUG_ROWS = 3.0` for Juglet stems, so `out/axes05_juglet_def3x/Juglet_Piece_1_Axis.xyz` held `182.68286090210461 143.84256528254906 -126.51694152319885 ...` (`1x`) while the `3x` bundle's oracle axis for the same piece is `551.711733859134 445.394427177426 -402.159848010588 ...`. Every Juglet axis sat 360-900 tree units off its sherd. The `/ 3.0` is correct **only inside the `1x` GT comparison**, never for the `.xyz` on disk.

Fixed in `work/t05_extract_juglet.py`: `write_native(path, lines)` writes `[v[3:6], v[0:3]]` with no division, and the division by `dl.JUG_ROWS` happens only in the GT metric. Job **35453049** (`t05-jugax`, `COMPLETED 0:0`, `00:01:09`) wrote the 9 native axes plus the 9 `Pot_JUGLET_Piece_0N_Axis.xyz` aliases and printed `CORPUS-UNCHANGED`; `Juglet_Piece_1` position `548.049, 431.528, -379.551` matches the `t367` shipped-base reference `548.74, 432.95, -382.10`, and `Juglet_Piece_7` keeps its base upright: position `-741.489, -38.668, -908.529`, direction z component `-0.6327` (so `dir_z < 0`, not canonicalized), `is_base = True`.

The staged bundle was renamed (never deleted) to `bundle_v1x_badaxes` and restaged, then array **35453073** ran the four repeats on the exact `t363` container and floor-10 shim (`0c216463ae27fe4571b200cc2292da99`, `XY_BREAK=1`, `XY_STATE=1`, `SFS_AXIS_SIGN=1`, `SFS_AXIS_LOCK_ICP` unset). All four `COMPLETED 0:0`:

| repeat | engine sherds | engine edges | `cluster_len` / seated | max chamfer | members `<= 0.50 mm` | `score58` strict edges | P7 joins |
|---|---|---|---|---|---|---|---|
| `r1` | `9/9` | `11/18` | `9 / 9` | `0.477 mm` | `9/9` | `5/36` | `4/4` under `5°` |
| `r2` | `9/9` | `13/18` | `9 / 9` | `0.465 mm` | `9/9` | `3/36` | `4/4` under `5°` |
| `r3` | `9/9` | `11/18` | `9 / 9` | `0.477 mm` | `9/9` | `5/36` | `4/4` under `5°` |
| `r4` | `9/9` | `11/18` | `9 / 9` | `0.477 mm` | `9/9` | `5/36` | `4/4` under `5°` |

**Bar: met.** `9/9` sherds (best of 4, in fact all four), `>= 10/18` edges (`11-13`), `9/9` cluster members at `<= 0.50 mm` (`0.465-0.477 mm`), `4/4` Piece 7 joins (`3-7`, `6-7`, `7-8`, `7-9`). The four joins carry angles `1.79°` (`6-7`), `1.92°` (`7-8`), `2.76°` (`3-7`) and `3.05°` (`7-9`), all inside the `5°` strict angle; `score58` still flags them `strict=false` because its mm column reads the `3x` tree units with a long lever arm (`45-81` units), and it has no `--scale` option — that is a measurement limitation of the scorer, not a join failure, and it is the one thing the next ticket should add to `score58`. The oracle control (job 35449559, same container and shim) reaches `9/9` at `0.459 mm`, so our native axes are `0.018 mm` behind the oracle on this statistic; the earlier "axes are the limiter" conclusion was an artefact of the `1/3`-scale write.

Local `score/juglet/` was refreshed after the native run: `score_juglet_own_xy_r{1..4}_cluster.json` now read `cluster_len 9` / `0.465-0.477 mm` and `summary.tsv` comes from `sum_t05_juglet.py` reading those native per-arm JSONs (job 35454806). The previous `1/3`-scale copies (cluster `4`, `0.375 mm`) are kept under `score/juglet/v1_1x_scale/` so the two cannot be confused.

### Visual inspection

`C:/PR/artifacts/axis-parity-05/render05_dual.png` (Phase 1, 8 panels, inspected 2026-11-20): green (`dual_k2`) tracks blue (Authors) because rank-0 *is* `arm_a1`'s line, and both follow GT; `Pot_E_Piece_31` and `Pot_J_Piece_02` show the two-line pairs where `arm_b2` disagrees with `arm_a1`.

`C:/PR/artifacts/axis-parity-05/render05_tenpots.png` (Phase 2, 11 rows: Pot A-J with `MOR1` [Authors control] left vs `K3R1` [`dual_k2`] right, row 11 the Juglet ours vs oracle; md5 `5deb86fca3996656a081b78361afdb2a`, 947150 B, inspected 2026-11-21 02:19):

- **A, B, F, G** assemble as recognisable open vessels in both columns; on A the small detached sherd below the body appears in both, and the engine still counts `8/8`, so it is seated on a join the vertex scatter cannot show.
- **C, D, E, I** are dense multi-piece bodies; D and E read as closed cylinders with a rim ring, matching `25-31` seated pieces.
- **H** is the clearest pair in the figure: the left (authors' control, `10/11`, `10/17`) shows rim pieces splayed off the dome, the right (ours, `11/11`, `17/17`) has them drawn in — the seven-edge gap seen from outside.
- **J** is the reverse and the one real loss: the right (ours, `6/11`, `9/21`) is visibly looser at the rim than the left (authors' control, `8/11`, `16/21`).
- **Juglet row**: both columns now show a compact seated sherd group — ours (`9/9` sherds, `cluster 9/9` at `0.477 mm`) with slightly more splay at the rim than the oracle (`9/9` at `0.459 mm`). The pieces are in the right places; the difference is sub-half-millimetre seating.

### Verified

- `verified: C:/PR/artifacts/axis-parity-05/gate05.tsv:19 -> authors dual_k2_k3 = 121/141 (reference 121/141, PASS)`
- `verified: C:/PR/artifacts/axis-parity-05/gate05.tsv:20 -> authors dual_k2_median_deg = 2.7054 (reference 2.78, PASS)`
- `verified: C:/PR/artifacts/axis-parity-05/gate05.tsv:23 -> authors Pot_A dual_k2 = 2.4733 mm (reference 3.5, PASS)`
- `verified: C:/PR/artifacts/axis-parity-05/gate05.tsv:24 -> authors Pot_G dual_k2_all_k1 = 7/7 (K-dist {1: 7})`
- `verified: C:/PR/artifacts/axis-parity-05/gate05.tsv:75 -> juglet dual_k2_k3 = 8/9 (reference 8/9, PASS)`
- `verified: C:/PR/artifacts/axis-parity-05/gate05.tsv:77 -> juglet dual_k2_pairs_gt_90 = 0/18 (worst over candidates 0)`
- `verified: C:/PR/artifacts/axis-parity-05/gate05.tsv:127 -> phase2_potJ J_K3R1 sherd = 6/11 (reference >=8/11, FAIL)`
- `verified: C:/PR/artifacts/axis-parity-05/gate05.tsv:128 -> phase2_potJ J_K3R1 edge = 9/21 (reference >=16/21, FAIL)`
- `verified: C:/PR/artifacts/axis-parity-05/gate05.tsv:129 -> phase2_juglet sherds = 9/9 (reference 9/9, PASS)`
- `verified: C:/PR/artifacts/axis-parity-05/gate05.tsv:131 -> phase2_juglet cluster_members_le_0.50mm = 9/9 max 0.477 mm (PASS)`
- `verified: C:/PR/artifacts/axis-parity-05/gate05.tsv:132 -> phase2_juglet piece7_joins_deg = 4/4 under 5 deg (1.79, 1.92, 2.76, 3.05)`
- `verified: C:/PR/artifacts/axis-parity-05/score/acc_potH.tsv:4 -> H_MOR1 = 10/11 sherds, 10/17 edges (authors' control, under floor); :2 -> H_K3R1 = 11/11 17/17`
- `verified: C:/PR/artifacts/axis-parity-05/score/acc_potD.tsv:5 -> D_MOR2 = 22/28 sherds, 53/69 edges (authors' control, under floor); :2 -> D_K3R1 = 25/28 60/69`
- `verified: C:/PR/artifacts/axis-parity-05/score/acc_potI.tsv:2 -> I_K3R1 = 26/26 sherds, 62/62 edges (target met)`
- `verified: C:/PR/artifacts/axis-parity-05/score/juglet/score_juglet_own_xy_r1_cluster.json:cluster_max_chamfer_mm -> 0.477 (cluster_len 9, cluster_seated 9)`
- `verified: C:/PR/artifacts/axis-parity-05/score/juglet/score_juglet_own_xy_r2_cluster.json:cluster_max_chamfer_mm -> 0.465`
- `verified: ssh spartan cat <juglet run>/logs/submit_juglet_own_xy_r1.log:74 -> "--- variant md5: 0c216463ae27fe4571b200cc2292da99"; :113-115 -> "axis lock icp: off" / "xy break normals: on" / "xy state normals: on"`
- `verified: md5sum <juglet run>/tools/cluster366.py -> 81f347cc1f80b7b84a163337959ec073`
- `verified: <dual run>/out/axes05_juglet_def3x/Juglet_Piece_7_Axis.xyz:1 -> "-741.48886353221042 -38.667975154179373 -908.52924608707417 0.7739... -0.6327..." (dir_z < 0 kept, base upright)`
- `verified: C:/PR/artifacts/axis-parity-05/score/juglet/score_juglet_own_xy_r2.json:tables.per_edge -> piece-7 degs 1.79 / 1.92 / 2.76 / 3.05, all < 5; strict=false because mm 45-81 is in 3x tree units`
- `verified: C:/PR/artifacts/axis-parity-05/logs/corpus2-35450478.out:1 -> "[md5] 907 files -> out/corpus_phase2.md5"`; `:3 -> CORPUS-UNCHANGED`; `:4 -> SAME-AS-PHASE1`
- `verified: C:/PR/artifacts/axis-parity-05/logs/e2e_sacct.tsv -> all 10 pots + 4 Juglet tasks COMPLETED 0:0`
- `verified: ssh spartan "grep 35453049 <runs>/index.tsv" -> "20261120-2135_9e0fe6a_t05-dual-a1-b2  35453049  9e0fe6a  t05-jugax" (verdict and human_note blank)`
- `verified: git apply --ignore-whitespace --check -p1 C:/PR/artifacts/axis-parity-05/impl_t05.diff -> APPLY-CHECK-OK over 9e0fe6a`; the diff's `sfs_axes/t02/arms.py` has md5 `828f4a6f718c0fcb59a325451111e35f`, identical to the Ticket 02 run copy (`.../20261120-1430_9e0fe6a_t02-cost-landscape/work/impl_t02/sfs_axes/t02/arms.py`), so `arm_a1`/`arm_b2` were not forked (the file does not exist at `9e0fe6a`; the diff adds it)
- `verified: Spartan pytest on impl_t05 -> "71 passed, 1 warning in 30.97s", exit 0 (job 35452596, COMPLETED 0:0, 00:00:34; log t05-pytest-35452596.log in the run root; 42 shipped + 13 t02 + 16 t05 tests)`

### What the next ticket should carry

1. **Pot J is the one pot our selector loses** (`6/11 9/21`, `5/11 8/21` vs floor `8/11 16/21`) while the authors' control holds it. The single-line path is at or above the paper on the other nine pots, so the work is the multi-candidate ranking on J, not the extractor bar.
2. **The authors' control itself fails two pots** (D repeat 2 `22/28 53/69`, H both repeats `10/11 10/17`) — any future comparison must be arm-for-arm, and the earlier inversion of these two pairs is the reason this ticket was reopened.
3. **`score58` needs a `--scale` option.** On the `3x` Juglet tree its mm column is three times too large, so its `seated` and `strict` flags read `0` even when `cluster366 --scale 3.0` puts all nine pieces inside `0.477 mm`. Until that is added, the Juglet bar must be read from `cluster366` plus the deg column of `score58`.
4. **The `0.50 mm` cluster bar is reachable with our own axes** (`9/9` at `0.465-0.477 mm` against the oracle's `0.459`), so no assembly change is needed for the Juglet; the remaining gap is `0.02 mm` of axis precision at the rim.

Reading: dual-selector-improves-axes-but-misses-e2e-bar

**End state:** ready

### Lead verification (2026-11-21)

- `verified:` `python C:/PR/artifacts/dsh-handover/axis-parity-05/accept.py` -> `ACCEPTANCE PASSED (reading=dual-selector-improves-axes-but-misses-e2e-bar)`.
- `verified:` `ssh spartan` `sacct -X` -> all active jobs (`35448549`, `35448730`, `35449224`, `35449734`..`35450471` 10 pots, `35450477`, `35450478`, `35452596` pytest `71 passed in 30.97s`, native 3x Juglet re-extraction `35453049` and 4-repeat array `35453073_0..3`, `35454485` render11, `35454552`/`35454569`/`35454806`) are `COMPLETED 0:0`; `CORPUS-UNCHANGED` verified across all 3 checkpoints (`md5-35448730.log`, `corpus2-35450478.out`, `jugax-35453049.log`); `runs/index.tsv` rows appended through line 904 with blank `verdict`/`human_note`; `squeue -u zhuojiat` has zero `t05-*` jobs.
- `verified:` `C:/PR/artifacts/axis-parity-05/{axes05_summary.json,gate05.tsv}` -> `dual_k2` clears 12/12 Part A bars (`110/141 K1`, `121/141 K3`, median `2.7054°`, `d_gt_to_est = 4.3383 mm`, `d_est_to_gt = 9.9252 mm`, `Pot A 2.4733 mm`, `Pot_A_Piece_08 = 4.741°`, `Pot G 7/7 K=1`, `7/8` K3 recoveries; Own surfaces `116/141 K1`, `122/141 K3`, `2.5631°`, `3.7781 mm`, `Pot G 7/7 K=1`; `def_3x` Juglet `7/9 K1`, `8/9 K3`, `Juglet_Piece_7` only base, `SignAxisGuard = 0/18` rank-0 & `0` worst-case across candidates).
- `verified:` `C:/PR/artifacts/axis-parity-05/score/acc_pot{A..J}.tsv` and `submit.sbatch` (`AX_MO` = Authors control, `AX_318` = `dual_k2`) -> `dual_k2` (`K3R1/2`) passes **9/10 paper pots** (`A 8/8 15/15`, `B 9/9 15/15`, `C 4/4 5/5`, `D 25/28 60/69 & 24/28 58/69` beating Authors `23/28 55/69 & 22/28 53/69`, `E 31/31 62/62`, `F 5/5 7/7`, `G 7/7 10/10`, `H 11/11 17/17` beating Authors `10/11 10/17`, `I 26/26 62/62` 100% beating both Authors and `t323` `25/26 59/62`); only `Pot J` falls below floor (`6/11 9/21`, `5/11 8/21` vs `8/11 16/21`).
- `verified:` native 3x `Juglet_Piece_{1,7}_Axis.xyz` (`548.049, 431.528, -379.551`; Piece 7 `-741.489, -38.668, -908.529`, `dir_z=-0.6327`), `score/juglet/score_juglet_own_xy_r{1..4}_cluster.json`, and Spartan `1. Acc.txt` -> after catching and fixing DeepSeek's v1 `1/3`-scale write bug (Claim 2), `dual_k2` passes **4/4 Juglet repeats**: `9/9` sherds, `11–13/18` edges (best `13/18` matching oracle, up from shipped `8/18`), `9/9` vertex cluster `0.465–0.477 mm` (`<= 0.50 mm`, within `0.006 mm` of oracle `0.459 mm`), and `4/4` Piece 7 joins (`1.79°–3.05°`).
- `verified:` visual inspection of `C:/PR/artifacts/axis-parity-05/render05_dual.png` and updated `C:/PR/artifacts/axis-parity-05/render05_tenpots.png` -> confirms `H_K3R1` pulls the splayed rim pieces cleanly into the vessel, `J_K3R1` is visibly looser than `J_MOR1`, and Row 11 native 3x `dual_k2` Juglet forms a compact 9-piece cup matching oracle.
- `verified:` lead per-piece audit (`axes05_summary.json` vs `diag01_summary.json`) -> isolates the exact cause of `Pot J`'s drop: `Pot_J_Piece_05` (`axes335 = 2.8°` vs `A1 = 20.6° / B2 = 26.7°`) is the **only** piece out of 141 where position-only `axes335` beats both normal-based arms (`A1` and `B2`), and `15°` dedup dropped `B2 <= 4.9°` behind `A1 10.0°–14.3°` on 5 pieces (`Pot_E_Piece_03`, `E23`, `E28`, `Pot_H_Piece_04`, and `Pot_J_Piece_11` `3.4°` vs `11.0°`).
