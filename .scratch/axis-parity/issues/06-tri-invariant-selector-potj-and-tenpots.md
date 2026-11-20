# 06: Validate tri-invariant parallel axis selector (`A1 + B2 + shipped profile_cost`) to recover `Pot J` and pass `10/10` pots + `def_3x` Juglet

**What to build:** A prototype strictly inside Spartan `<run>/work/impl_t06/` (ZERO edits to tracked files in `SfSpp_preprocessing/` or `structure-from-sherds-pp/`, exported as a clean `-p1` unified `impl_t06.diff` over `commit 9e0fe6a` passing `git apply --ignore-whitespace --check`, keeping `orient_base_axis` ON) implementing the **tri-invariant parallel selector (`arm_a1` calibrated Huber `width=0.05` on `e_hat_i` + `arm_b2` normal-consistent Hermite profile + `arm_p` shipped position-only `select_union_lines` from `sfs_axes/select.py`, merged with `A1` rank-0 first, capped at `K <= 3`, followed by `orient_base_axis`)** and validating across:

1. **Phase 1 (Fast Offline Gate):** Benchmark 5 clean zero-magic-number variants (`tri_r0_d15`, `tri_r0_d10`, `tri_r0_d08`, `tri_psec_d15`, `tri_psec_d10`) sharing a single `A1` + `B2` + `P` computation per piece across all `141` GT pieces (on **both** Authors' `Surfaces/` and Our Own `MeshPreprocessingHeadless` surfaces including Pot H `/data/gpfs/projects/punim2657/SfSpp/runs/20261120-0227_2c14fe3_t01-diag-axis-parity/out_poth/geom`, reusing Ticket 01's cached pools `/data/gpfs/projects/punim2657/SfSpp/runs/20261120-0227_2c14fe3_t01-diag-axis-parity/out/cache/*.npz` and Ticket 02's `work/run.json` Own-surface paths) AND `def_3x` Juglet (`9` pieces from `/data/gpfs/projects/punim2657/SfSpp/runs/20261117-0430_d272313_t80-default-on/out/cell_def_3x/geom/Juglet_Piece_{1..9}.S{0,1}`).
2. **Phase 2A (Targeted E2E Pre-Gate — ONLY if Phase 1 passes Part A):** Extract the winning variant across all `163` corpus pieces (`Pot A..J`) + `9` `def_3x` Juglet pieces (writing Juglet `.xyz` in **native `3x` tree units — NO `/ 3.0` on written `.xyz` files!**, NO `canonicalize()`), and run **`Pot J`**, **`Pot G`** (decoy guard), **`Pot D`** (`t323` target `26/28`), and **`def_3x` Juglet (`4` repeats, native `3x`)** FIRST.
3. **Phase 2B (Remaining 7 Pots `A, B, C, E, F, H, I` — ONLY if Stage 2A passes all 4 targets):** Run the remaining 7 pots (`2` repeats each, `MOR1/2` Authors' control + `K3R1/2` ours) to complete the full `10/10` paper pots + `def_3x` Juglet E2E gate.

**Answers:** E1
**Blocked by:** None (Ticket 05 resolved at `e1cf772` / `277a754`)
**Status:** in-progress
**Working in:** chat on Thinkbook16 (2026-11-21)
**Branch:** 06-tri-invariant-selector-potj-and-tenpots, in /c/PR/worktrees/sfs/06
**Worker:** dsh one-shot subagent w06-axis-parity
**Budget:** large 8
**Hand-over:** DeepSeek — hidden acceptance check at `C:/PR/artifacts/dsh-handover/axis-parity-06/accept.py` to be staged before dispatch

---

## 1. Why Ticket 06 Exists (Verified Lead Audit of Ticket 05)

Ticket 05 (`e1cf772` / `277a754`) proved that `dual_k2` (`A1 + B2`, `15°` dedup, `K <= 2`) clears all 12 Part A bars, passes **9 of 10 paper pots** (`A, B, C, D, E, F, G, H 11/11 17/17, I 26/26 62/62`), and passes **4/4 native 3x `def_3x` Juglet repeats** (`9/9` sherds, `11–13/18` edges, `0.465–0.477 mm` cluster, `4/4` Piece 7 joins `1.79°–3.05°`).

Lead per-piece audit across all `141` GT pieces isolated **both** exact reasons `Pot J` was the sole pot below floor (`6/11 9/21`, `5/11 8/21` vs `MOR1/2 8/11 16/21`):
1. **`Pot_J_Piece_05` (`axes335 = 2.8°` vs `A1 = 20.6° / B2 = 26.7°`):** the **only** piece of `141` where position-only `axes335` (`select_union_lines` using `profile_cost`) succeeds while both normal-based arms (`A1`, `B2`) are fooled by noisy normals.
2. **`15°` dedup clipping (`5` pieces across the corpus):** `Pot_J_Piece_11` (`B2 = 3.4°` dropped behind `A1 = 11.0°` because their mutual angle is `< 15°`), plus `Pot_E_Piece_03` (`2.9°` vs `10.4°`), `Pot_E_Piece_23` (`3.2°` vs `14.3°`), `Pot_E_Piece_28` (`4.9°` vs `10.9°`), and `Pot_H_Piece_04` (`1.0°` vs `10.0°`).
3. **Why adding `P` (`axes335` rank-0) and testing `8°–10°` dedup is geometrically safe on `Pot G`:** On Authors' surfaces, all `7/7` Pot G pieces satisfy `A1 <= 4.65°`, `B2 <= 6.59°`, and `axes335 <= 7.98°` (`G03`: `A1 = 1.49°`, `B2 = 1.80°`, `335 = 7.98°` [distance between `1.49°` and `7.98°` may stay `< 8°` or add `<= 1` close candidate]; on `6/7` pieces all three are within `< 5°`). Testing `8°`, `10°`, and `15°` dedup in Phase 1 directly checks `Pot G 7/7` (`K=1`) before touching E2E!

---

## 2. Exact Algorithm, Prototype Rules, and Anti-Trap Checklist

1. **Prototype boundary:** Create Spartan run dir `/data/gpfs/projects/punim2657/SfSpp/runs/<YYYYMMDD-HHMM>_<git7>_t06-tri-invariant/`. Populate `<run>/work/impl_t06/` from `git archive 9e0fe6a` of `sfs_axes/ tests/ scripts/run_benchmark_172.py`, apply `/data/gpfs/projects/punim2657/SfSpp/runs/20261120-2135_9e0fe6a_t05-dual-a1-b2/work/impl_t05.diff` cleanly (keeping `sfs_axes/t02/*` and `sfs_axes/t05/*` unmodified), and add ONLY `sfs_axes/t06/__init__.py`, `sfs_axes/t06/tri.py`, and `tests/test_t06_tri.py` (plus runner helpers under `<run>/work/`). Export clean `-p1` unified diff `<run>/work/impl_t06.diff` over `9e0fe6a` (`git apply --ignore-whitespace --check` passes) and run ALL existing + new tests in a Spartan batch job (`>= 71` existing + new `t06` tests passing; record job ID and log path!). **Leave tracked files in `SfSpp_preprocessing/` and `structure-from-sherds-pp/` 100% untouched.**
2. **Exact `sfs_axes/t06/tri.py` formulation (zero per-pot, per-piece, or object-size constants):**
   - `res_a1 = arm_a1(reps, sizes, walls_s, C, size)` (from `sfs_axes.t02.arms`),
   - `res_b2 = arm_b2(reps, sizes, walls_s, C, size)` (from `sfs_axes.t02.arms`),
   - `res_p = select_union_lines(reps, sizes, C0, C1, C, max_candidates=6, line_rule=True, base_orient=True)` (from `sfs_axes.select` — exact shipped `axes335`), all on the same `60`-basin pool (`_cands` for `A1`/`B2`; `select_union_lines` uses `PROFILE_BASINS = 30` internally on `reps, sizes`).
   - `merge_tri(res_a1, res_b2, res_p, dedup_deg=10.0, kmax=3, include_p_secondaries=False)`:
     1. Append `res_a1[:, 0]` first (preserving `A1`'s `2.705° / 4.338 mm / 2.473 mm Pot A` rank-0 precision).
     2. Append `res_b2[:, 0]` if `direction_angle_deg >= dedup_deg` from every kept line and `len < kmax`.
     3. Append `res_p[:, 0]` if `direction_angle_deg >= dedup_deg` from every kept line and `len < kmax`.
     4. If `include_p_secondaries`: scan `res_p[:, 1:]` in order, appending any line with `direction_angle_deg >= dedup_deg` from every kept line until `len == kmax`.
   - Apply `orient_base_axis(lines, C)` once on the merged `(6, K)` array (handle `None` / empty arm outputs safely).
   - **Unit tests (`tests/test_t06_tri.py`):** Cover `A1` rank-0 precedence, `B2` and `P` append order, `dedup_deg` filtering (`8°`, `10°`, `15°`), `include_p_secondaries=False` vs `True`, `K <= 3` cap, `None`/empty arm fallbacks, `orient_base_axis` upright preservation on inverted base disks (`dir_z < 0`), and normal-sign invariance (`N -> -N`).
3. **Mandatory Anti-Trap Rules (Learned on Tickets 02 & 05):**
   - **Native `3x` `.xyz` files for `def_3x` Juglet:** NEVER divide `v[3:6]` by `3.0` when writing `out/axes06_juglet_def3x/*.xyz` (`Juglet_Piece_1` MUST sit at `~548, 431, -380` in `3x` tree units; `Juglet_Piece_7` MUST sit at `~-741, -39, -909` with `dir_z < 0`, no `canonicalize()`). Divide `v[3:6]` by `3.0` ONLY inside the `1x` `Dataset/Juglet_GT` scorer!
   - **Arm attribution on Pots `A..J`:** `AX_MO` (`<P>_MOR1/2`) = **Authors' released `Axes/` control**; `AX_318` (`<P>_K3R1/2`) = **our `tri` selector**. Label renders `MOR1 [Authors control]` left vs `K3R1 [tri]` right.
   - **`SignAxisGuard` with `T` rotations:** Check BOTH rank-0 (`0/18`) AND worst-case across ALL returned candidates `k = 0..K-1` (`0` worst-case flips required for the winning variant!).
   - **`score58` vs `cluster366` on `3x` Juglet:** Read seating & vertex cluster from `cluster366.py --scale 3.0 --bar 13.788` (md5 `81f347cc1f80b7b84a163337959ec073`), sherd/edge accuracy from `1. Acc.txt`, and Piece 7 join angles (`< 5°`) from `score58`'s `tables.per_edge`.
   - **Ticket & metadata hygiene:** Keep `**Status:** in-progress` in line 10 (`Status:` stays with the lead per `docs/agents/delegation.md`), populate non-empty `axes06_summary.json["jobs"]` & `["phase2"]` and Phase 2 rows in `gate06.tsv`, verify `CORPUS-UNCHANGED`, append `runs/index.tsv` rows with blank `verdict` / `human_note`, and leave ZERO background watcher jobs running at turn end.

---

## 3. Phase 1: Offline Benchmark & Part A Go/No-Go Gate

Benchmark all **5 variants** (`tri_r0_d15`, `tri_r0_d10`, `tri_r0_d08`, `tri_psec_d15`, `tri_psec_d10`) from one shared `A1` + `B2` + `P` evaluation per piece across all `141` GT pieces (Authors' & Own `MeshPreprocessingHeadless` surfaces) and `def_3x` Juglet (`9` pieces):
- **Mandatory Part A Pass Bars (on Authors' surfaces `141` GT & `def_3x` Juglet `9` pieces):**
  - `K1 <= 10°`: `>= 109/141`
  - `K3 <= 10°`: **`>= 122/141`** (strictly beating both `dual_k2` `121` and `axes335` `121`)
  - K3 recoveries of Ticket 01's 8 K3 losses: **`>= 7/8`**
  - Median rank-0 angle: `<= 2.78°`
  - Physical `d_gt_to_est` median: `<= 4.38 mm` (always report `d_est_to_gt` beside it)
  - `Pot A` `d_gt_to_est` median: `<= 3.5 mm`
  - `Pot_A_Piece_08` rank-0 angle: `<= 10°`
  - **`Pot_J_Piece_05` best-of-K `<= 10°`** AND **`Pot J K3 >= 6/11`** (up from `dual_k2`'s `5/11`)
  - **`Pot G` (`7/7` pieces) Authors' `all_k1 == 7/7` (`K = 1` on every Pot G piece)** (report Own `Pot G` `all_k1` too)
  - `def_3x` Juglet: `K1 >= 7/9`, `K3 >= 8/9`, `is_base_fragment=True` on `Juglet_Piece_7` only, `SignAxisGuard = 0/18` on rank-0 **AND `0` worst-case across ALL candidates `k = 0..K-1`!**
- **Variant selection rule among passing variants:** Pick the passing variant with the **highest `Pot J K3`**, breaking ties by (1) lowest `mean_K` (fewer lines = lower beam-search decoy risk), (2) Own `Pot G 7/7 K=1`, (3) highest Authors `141`-piece `K3`, (4) `tri_r0_*` over `tri_psec_*`.
- **Early-Stop Rule (Phase 1):** If NO variant clears every Part A bar above, skip Phase 2 cleanly and close with `Reading: tri-selector-misses-part-a-no-e2e`.

---

## 4. Phase 2: Two-Stage E2E Gate (2A `Pot J, G, D` + Juglet -> 2B Remaining 7 Pots)

1. **Full Extraction (if Phase 1 passes):** Extract winning variant over all `163` Pot `A..J` pieces (`<run>/out/axes06_tri/`) and `9` `def_3x` Juglet pieces (`<run>/out/axes06_juglet_def3x/` in **native `3x` coords**, no `canonicalize()`), verify `141` GT metrics reproduce Part A cleanly, and verify `CORPUS-UNCHANGED`.
2. **Stage 2A (Targeted E2E Pre-Gate — Submit ONLY `Pot J`, `Pot G`, `Pot D`, and `4`-repeat `def_3x` Juglet first):**
   - Clone `t319-pot{J,G,D}` per `make_e2e_323.sh` (`AX_318=<run>/out/axes06_tri`; use `32` cpus / `64G` on `D`, `16` cpus / `32G` on `G, J` so queue wait is short) + `t363` `4`-repeat `def_3x` Juglet array.
   - **Stage 2A Pass Bar (gates Stage 2B):**
     - `Pot J K3R1/2`: best-of-2 **`>= 8/11, >= 16/21`** (report BOTH repeats!)
     - `Pot G K3R1/2`: **`7/7, 10/10`** (both repeats; decoy guard!)
     - `Pot D K3R1/2`: both repeats **`>= 23/28, >= 55/69`** (targeting `26/28, 63/69`)
     - `def_3x` Juglet (`4` repeats): best-of-4 **`9/9` sherds**, **`>= 10/18` edges**, **`9/9` cluster `<= 0.50 mm`**, **`4/4` Piece 7 joins (`< 5°`)**.
     - `MOR1/2` Authors controls verified; `CORPUS-UNCHANGED`.
   - **Stage 2A Early-Stop Rule:** If Stage 2A fails any target above, **DO NOT submit Stage 2B (the remaining 7 pots)**; fetch deliverables, inspect `render06_e2e.png`, and finish with `Reading: tri-selector-fails-stage2a-pregate`.
3. **Stage 2B (Remaining 7 Pots `A, B, C, E, F, H, I` — ONLY if Stage 2A passes every bar):**
   - Run `Pot A, B, C, F, H` (`16` cpus / `32G`) and `Pot E, I` (`32` cpus / `64G`), `2` repeats each (`MOR1/2` Authors control + `K3R1/2` ours), checking every `t323` floor & target:
     - `A 8/8 15/15`, `B 9/9 15/15`, `C 4/4 5/5`, `E >=29/31 >=57/62` (target `31/31 62/62`), `F 5/5 7/7`, `H 11/11 17/17`, `I >=25/26 >=59/62` (target `26/26 62/62`).

---

## 5. Deliverables & Visual Inspection (`C:/PR/artifacts/axis-parity-06/`)

- **Always fetched:**
  - `axes06_summary.json` — Non-empty `jobs` list (`sacct -X`), all 5 variants on `141` GT pieces (`Authors` & `Own`, both `d_gt_to_est` and `d_est_to_gt`, per-pot `K`-dists, all 14 loss stems + `Pot_J_Piece_05`/`Pot_J_Piece_11`), `def_3x` Juglet (`sign_guard` rank-0 `0/18` & `per_k` worst-case), winner selection decision, and (when Phase 2 runs) full `phase2` E2E block.
  - `gate06.tsv` — Exact 7-col header `group\tpiece\tmetric\tvalue\treference\tverdict\tnote` covering all 5 variants, `own`, `juglet`, `d_gt_to_est`, `d_est_to_gt`, `Pot_J_Piece_05`, and Phase 2A/(2B) rows (`potJ, potG, potD`, `juglet_e2e`, and `pot{A,B,C,E,F,H,I}` when Stage 2B runs).
  - `render06_tri.png` — 8-row 3D + `(r, z)` unfold comparison (`Pot_J_Piece_05`, `Pot_J_Piece_07`, `Pot_J_Piece_11`, `Pot_A_Piece_07`, `Pot_E_Piece_31`, `Pot_I_Piece_20`, `Pot_G_Piece_03`, `Pot_A_Piece_08`) showing GT, Authors, `axes335`, and winning `tri`. Inspect visually before writing `Reading:`.
  - `impl_t06.diff` — Clean unified diff against `9e0fe6a` verified with `git apply --ignore-whitespace --check`.
- **When Stage 2A / 2B runs:**
  - `render06_e2e.png` — Labelled E2E comparison (`MOR1 [Authors control]` left vs `K3R1 [tri]` right for all executed pots + native 3x Juglet vs oracle row), visually inspected before writing `Reading:`.
  - `score/acc_pot{J,G,D}.tsv` (plus `acc_pot{A,B,C,E,F,H,I}.tsv` when Stage 2B runs) and `score/juglet/` (native 3x `cluster.json`, `score58`, `summary.tsv`).

---

## 6. Readings (pick one verbatim on a bare `Reading:` line)

- `tri-selector-passes-all-ten-pots-and-juglet` — Phase 1 clears Part A AND Stage 2A + Stage 2B clear ALL `10/10` paper pots + `def_3x` Juglet (`9/9`, `>= 10/18`, `<= 0.50 mm` cluster, `4/4` Piece 7 joins, `0/18` rank-0 & `0` worst-case `SignAxisGuard`).
- `tri-selector-passes-stage2a-misses-stage2b` — Phase 1 and Stage 2A (`Pot J, G, D` + `Juglet`) pass, and one or more Stage 2B pots fall below floor; report exact pot/edge regression.
- `tri-selector-fails-stage2a-pregate` — Phase 1 clears Part A, Stage 2A fails on `Pot J`, `Pot G`, `Pot D`, or `Juglet`, so Stage 2B (remaining 7 pots) was skipped cleanly per Section 4.
- `tri-selector-misses-part-a-no-e2e` — Phase 1 early-stop triggered cleanly (zero Phase 2 spend).
- `blocked: missing-or-failed-control` — Required input, container, `MOR` control, or `CORPUS-UNCHANGED` check fails.

## Out of scope

- Editing ANY tracked file in `SfSpp_preprocessing/` or `structure-from-sherds-pp/`, changing `**Status:**` away from `in-progress`, merging to `main`, pushing to `main`, or running `ticket_close.sh`.

## Acceptance

- [ ] Zero tracked source edits (`git diff origin/main --name-only` touches only this ticket); `<run>/work/impl_t06.diff` cleanly applies over `9e0fe6a` (`git apply --ignore-whitespace --check`) and Spartan batch unit tests pass (`>= 71` existing + new `tests/test_t06_tri.py` checks).
- [ ] Phase 1 benchmarks all 5 variants (`tri_r0_d15`, `tri_r0_d10`, `tri_r0_d08`, `tri_psec_d15`, `tri_psec_d10`) on `141` GT pieces (Authors' & Own surfaces, both `d_gt_to_est` and `d_est_to_gt`, `Pot_J_Piece_05`, `Pot_J_Piece_11`, `Pot G 7/7 K=1`) AND `def_3x` Juglet (`0/18` rank-0 AND `0` worst-case `SignAxisGuard`, `/ 3.0` on GT scoring only, `Juglet_Piece_7` only base), with `sacct -X COMPLETED 0:0` and `CORPUS-UNCHANGED`.
- [ ] Gated Phase 2 enforced cleanly: when Phase 1 passes Part A, full `163`-piece + native `3x` `9`-piece Juglet extraction runs and Stage 2A (`Pot J, G, D` + `def_3x` Juglet) passes/early-stops before Stage 2B (remaining 7 pots `A, B, C, E, F, H, I`), with non-empty `axes06_summary.json["jobs"]` & `["phase2"]`, Phase 2 rows in `gate06.tsv`, `runs/index.tsv` appended (`verdict`/`human_note` blank), and `CORPUS-UNCHANGED`.
- [ ] `C:/PR/artifacts/axis-parity-06/{axes06_summary.json,gate06.tsv,render06_tri.png,impl_t06.diff}` (plus `render06_e2e.png` & `score/` when Phase 2 runs) fetched locally and visually inspected before writing bare `Reading:`, `**End state:** ready` (with `**Status:** in-progress`), and ZERO active background watchers left running.
