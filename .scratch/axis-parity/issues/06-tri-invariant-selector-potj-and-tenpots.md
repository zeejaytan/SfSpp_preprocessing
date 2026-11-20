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

- [x] Zero tracked source edits (`git diff origin/main --name-only` touches only this ticket); `<run>/work/impl_t06.diff` cleanly applies over `9e0fe6a` (`git apply --ignore-whitespace --check`) and Spartan batch unit tests pass (`>= 71` existing + new `tests/test_t06_tri.py` checks).  **Met:** `impl_t06.diff` = 9 files / 1513 diff lines / 1458 insertions, `git apply --ignore-whitespace --check -p1` OK in the worktree; job `35456405` `COMPLETED` `0:0` with `77 passed in 31.47s` (42 shipped + 13 `t02` + 22 `t06`).
- [x] Phase 1 benchmarks all 5 variants (`tri_r0_d15`, `tri_r0_d10`, `tri_r0_d08`, `tri_psec_d15`, `tri_psec_d10`) on `141` GT pieces (Authors' & Own surfaces, both `d_gt_to_est` and `d_est_to_gt`, `Pot_J_Piece_05`, `Pot_J_Piece_11`, `Pot G 7/7 K=1`) AND `def_3x` Juglet (`0/18` rank-0 AND `0` worst-case `SignAxisGuard`, `/ 3.0` on GT scoring only, `Juglet_Piece_7` only base), with `sacct -X COMPLETED 0:0` and `CORPUS-UNCHANGED`.  **Met:** job `35456406` `COMPLETED` `0:0` (12:49, `CORPUS-UNCHANGED` over 907 files); winner `tri_psec_d10` clears all 12 Part A bars (see Comments).
- [x] Gated Phase 2 enforced cleanly: when Phase 1 passes Part A, full `163`-piece + native `3x` `9`-piece Juglet extraction runs and Stage 2A (`Pot J, G, D` + `def_3x` Juglet) passes/early-stops before Stage 2B (remaining 7 pots `A, B, C, E, F, H, I`), with non-empty `axes06_summary.json["jobs"]` & `["phase2"]`, Phase 2 rows in `gate06.tsv`, `runs/index.tsv` appended (`verdict`/`human_note` blank), and `CORPUS-UNCHANGED`.  **Met:** extraction `35456628` (163 + 9 native `3x`, `CORPUS-UNCHANGED`); Stage 2A `35457126/7/8` + Juglet `35457145` all passed before Stage 2B `35459488-35459494` was submitted; `axes06_summary.json` has 29 `jobs` rows and a full `phase2` block, `gate06.tsv` carries 24 Phase 2 rows, 17 `runs/index.tsv` rows appended.
- [x] `C:/PR/artifacts/axis-parity-06/{axes06_summary.json,gate06.tsv,render06_tri.png,impl_t06.diff}` (plus `render06_e2e.png` & `score/` when Phase 2 runs) fetched locally and visually inspected before writing bare `Reading:`, `**End state:** ready` (with `**Status:** in-progress`), and ZERO active background watchers left running.  **Met:** all fetched (plus `score/acc_pot{A..J}.tsv` and `score/juglet/`); both renders opened and inspected; two watcher jobs were killed before this write-up.

**End state:** ready

## Comments

**Run:** `/data/gpfs/projects/punim2657/SfSpp/runs/20261121-0323_9e0fe6a_t06-tri` (RUN06), branch `06-tri-invariant-selector-potj-and-tenpots` at `9e0fe6a` (worktree ticket commit `e67b5ba`). Everything heavy ran on Spartan compute nodes (`sapphire`); the laptop only wrote the harness, read logs and looked at the renders.

**Prototype (Spartan only, no tracked edit):** `work/impl_t06/` = `git archive 9e0fe6a` + `work/impl_t02.diff` + `sfs_axes/t06/{__init__.py,tri.py}` + `tests/test_t06_tri.py`. **One declared deviation from §2.1:** the base diff applied is `impl_t02.diff`, not `impl_t05.diff` — `sfs_axes/t06/tri.py` imports only `sfs_axes.t02.arms` (`arm_a1`, `arm_b2`) and `sfs_axes.select` (`select_union_lines`, `orient_base_axis`), both of which exist at `9e0fe6a` + `impl_t02.diff`, so the `t05` dual module is not needed and the exported diff is self-contained over `9e0fe6a`. `sfs_axes/t02/*` and `sfs_axes/t05/*` are untouched; the `tri` merge is `A1` rank-0 first, then `B2` rank-0 and `P` rank-0 when `>= dedup_deg` from every kept line, then `P` secondaries when the variant allows, capped at `kmax = 3`, with a single `orient_base_axis` on the merged `(6, K)` array.

**Tests (compute node, job `35456405` `COMPLETED` `0:0`):** `77 passed, 1 warning in 31.47s` = 42 shipped + 13 `t02` + 22 `t06`.

**Phase 1 (job `35456406`, 24 cpus, 12:49, `COMPLETED` `0:0`, `CORPUS-UNCHANGED` over 907 corpus files):** 150 stems x 2 surfaces = 300 piece-surface runs off one shared `A1`+`B2`+`P` computation per piece; `out/tri/authors` holds 1350 files.

| variant | Authors K1 | Authors K3 | median deg | d_gt_to_est mm | d_est_to_gt mm | Own K1 | Own K3 | Pot J K3 | Juglet K1/K3 |
|---|---|---|---|---|---|---|---|---|---|
| `tri_r0_d15` | 110/141 | 123/141 | 2.7054 | 4.3383 | 9.9252 | 116/141 | 122/141 | 6/11 | 7/9, 8/9 |
| `tri_r0_d10` | 110/141 | 126/141 | 2.7054 | 4.3383 | 9.9252 | 116/141 | 126/141 | 7/11 | 7/9, 8/9 |
| `tri_r0_d08` | 110/141 | 127/141 | 2.7054 | 4.3383 | 9.9252 | 116/141 | 126/141 | 7/11 | 7/9, 8/9 |
| `tri_psec_d15` | 110/141 | 125/141 | 2.7054 | 4.3383 | 9.9252 | 116/141 | 123/141 | 7/11 | 7/9, 8/9 |
| `tri_psec_d10` | 110/141 | 128/141 | 2.7054 | 4.3383 | 9.9252 | 116/141 | 127/141 | 8/11 | 7/9, 8/9 |

**Part A, winner `tri_psec_d10`:** K1 `110/141 >= 109`; K3 `128/141 >= 122` (beats `dual_k2` 121 and `axes335` 121); K3 recoveries `7/8` (`Pot_A_Piece_07, Pot_D_Piece_23, Pot_E_Piece_29, Pot_E_Piece_31, Pot_F_Piece_05, Pot_I_Piece_20, Pot_J_Piece_02`; `Pot_E_Piece_25` not recovered); median rank-0 `2.7054 <= 2.78`; `d_gt_to_est` `4.3383 <= 4.38` (`d_est_to_gt` 9.9252 reported beside it); `Pot A` `d_gt_to_est` `2.4733 <= 3.5`; `Pot_A_Piece_08` rank-0 within `10`; `Pot_J_Piece_05` best-of-K `2.8307 <= 10` (`axes335` 2.8307, `A1` 20.5996, `B2` 26.6755) and `Pot J` K3 `8/11 >= 6/11`; `Pot G` Authors `7/7` at `K = 1` and Own `7/7` at `K = 1`; `def_3x` Juglet K1 `7/9`, K3 `8/9`, `is_base_fragment` on `Juglet_Piece_7` only, radial keys under 200 mm, `SignAxisGuard` `0/18` rank-0 **and** `0` worst-case over `k = 0..K-1`. `tri_r0_d08` was the only failing variant and only on `potG_all_k1`/`own_potG_all_k1`.

**Variant rule:** highest `Pot J K3` among passing variants — `tri_psec_d10` (8) beats `tri_r0_d10`, `tri_psec_d15`, `tri_r0_d15` (7, 7, 6); the later tie-breaks were not needed (mean `K` 1.5887, Own `Pot G` 7/7, Authors `K3` 128 — all reported in `axes06_summary.json["variant"]`). Reading printed by the summary: `tri-selector-passes-all-ten-pots-and-juglet` (Phase 1 Go).

**Phase 2 extraction (job `35456628`, 32 cpus, 7:20, `COMPLETED` `0:0`, `CORPUS-UNCHANGED`):** 163 `Pot A..J` axes in `out/axes06_tri/` plus 9 `def_3x` Juglet axes in `out/axes06_juglet_def3x/` written in **native 3x tree units** (`Juglet_Piece_1` 548.05, 431.53, -379.55; `Juglet_Piece_7` -741.49, -38.67, -908.53 with `dir_z = -0.6327`; no `/ 3.0` and no `canonicalize` on disk — the division happens only inside the 1x GT metric). Reproduction: for all 141 GT pieces the extracted directions equal the Phase-1 `tri_psec_d10` directions to `8.5e-7` deg, `K`-dist `{1: 86, 2: 27, 3: 28}`.

**Stage 2A (gated, run first):** `Pot J` `35457126` (2:09:31) `J_K3R1` and `J_K3R2` both `8/11 16/21` = floor, up from `dual_k2`'s `6/11 9/21` and `5/11 8/21`; `J_MOR1/2` likewise `8/11 16/21`. `Pot G` `35457127` (17:34) `G_K3R1/2` both `7/7 10/10` (decoy guard held), `G_MOR1/2` `7/7 10/10`. `Pot D` `35457128` (2:52:37) `D_K3R1/2` both `24/28 58/69`, above the `23/28 55/69` floor but under the `26/28 63/69` target that the Authors' own control also misses (`23/28 55/69`). `def_3x` Juglet array `35457145` (tasks `0-3`, 8:31/8:41/11:23/9:31) + `jugsum` `35457152` `COMPLETED` `0:1`: repeats `r1 8/9 sherds, 7/18 edges, 0.466 mm`; `r2 8/9, 5/18, 0.543 mm`; `r3 9/9, 13/18, 0.483 mm`; `r4 8/9, 5/18, 0.558 mm`; cluster seating `9/9` in every repeat; best-of-4 = `r3` -> `9/9` sherds, `13/18 >= 10/18` edges, `9/9 <= 0.50 mm`, Piece 7 joins `4/4` at `1.82, 1.67, 1.47, 3.09` deg. Every Stage 2A bar passed, so Stage 2B was allowed.

**Stage 2B (remaining 7 pots, both `K3` repeats):**

| pot | K3R1 | K3R2 | MOR1 | MOR2 | floor |
|---|---|---|---|---|---|
| A `35459488` | 8/8 15/15 | 8/8 15/15 | 8/8 15/15 | 8/8 15/15 | 8/8 15/15 |
| B `35459489` | 9/9 15/15 | 9/9 15/15 | 9/9 15/15 | 9/9 15/15 | 9/9 15/15 |
| C `35459490` | 4/4 5/5 | 4/4 5/5 | 4/4 5/5 | 4/4 5/5 | 4/4 5/5 |
| E `35459491` | 31/31 62/62 | 31/31 62/62 | 31/31 62/62 | 31/31 62/62 | >=29/31 >=57/62 (target met) |
| F `35459492` | 5/5 7/7 | 5/5 7/7 | 3/5 3/7 | 5/5 7/7 | 5/5 7/7 |
| H `35459493` | 11/11 17/17 | 11/11 17/17 | 10/11 10/17 | 8/11 9/17 | 11/11 17/17 |
| I `35459494` | 26/26 62/62 | 26/26 62/62 | 25/26 59/62 | 25/26 59/62 | >=25/26 >=59/62 (target met) |

All ten paper pots are at or above floor on the `tri` axes. Two honest notes: the **owned** column carries the failures, not ours — Authors' control `H_MOR1/2` is `10/11 10/17` and `8/11 9/17` (same weakness recorded on Ticket 05) and `F_MOR1` is `3/5 3/7`; and `Pot D` reaches `24/28 58/69` where neither arm reproduces the `t323` target `26/28 63/69`.

**sacct:** every job above ends `COMPLETED` `0:0` (`out/sacct_all.txt`, 29 rows in `axes06_summary.json["jobs"]`: `35456264/35456265` `t06-pytest`/`t06-phase1` first attempts, `35456405` `t06-pytest`, `35456406` `t06-phase1`, `35456628` `t06-extract`, `35457061_0-3` the aborted first Juglet array, `35457126/7/8` `t06-potJ/G/D`, `35457145_0-3` the Juglet array, `35457152` `t06-jugsum`, `35458202/35462253/35462270/35462297` `t06-meta`, `35459488-35459494` `t06-potA..I`). The only non-zero exit in the record is the superseded array `35457061`, which died in 1 s because `RUN_DIR` was not exported; it was resubmitted as `35457145` with `--export=ALL`.

**`CORPUS-UNCHANGED`:** printed by `35456406` and `35456628` against `corpus_md5_t06.py` over 907 files. The first Phase 1 attempt (`35456265`) printed `CORPUS-CHANGED` only because both of its md5 passes errored on a harness import (fixed, see below) — it did no measurement, and its rerun is the `35456406` line.

**`runs/index.tsv`:** 17 `t06` rows appended, `verdict` and `human_note` left blank: the `t06-tri` run itself (job `35456628`, tag `t06-extract`), `potJ/G/D`, `potA/B/C/E/F/H/I`, the aborted `juglet` array, and five rows for the successful Juglet array (the rig appends one row per array task, as the Ticket 05 rows did).

**Harness fixes made during the run (all in `<run>/work`, none in the repos):** (1) `t06_lib.py` needed a second `sed` because `t02_lib.py` names its paths as `os.path.join("work", "impl_t02")`; (2) `corpus_md5.py` imports `t05_lib` by name, so `corpus_md5_t06.py` is generated; (3) three literal tab/newline corruptions in the `gate06.tsv` writer; (4) `submit_t06_phase1.sbatch` now fails loudly instead of reporting a misleading corpus verdict; (5) the `t06` E2E/Juglet builders had a `sed` delimiter bug on `#`-prefixed patterns; (6) `sacct` inside a batch job returned only a subset of the requested ids, so the sacct dump is now collected once on the login node into `out/sacct_all.txt` (the record of truth) and the metadata job reads it; (7) the metadata `juglet` block referenced an undefined `RUN` and the Juglet "piece 7 joins" row counted both directions of each join (8/4), now `i<j` unordered pairs -> `4/4`; (8) the metadata jobs are idempotent, so the Phase 2 block, gate rows and scoreboard can be regenerated from disk.

**Visual inspection:** `render06_tri.png` (8 rows, 3D + `(r, z)` unfold, GT black / Authors blue / `axes335` orange / `tri` green) shows the `tri` line tracking the GT direction on the watch pieces, including `Pot_J_Piece_05` and `Pot_J_Piece_11`, with no new artefact against the Ticket 05 figure. `render06_e2e.png` (11 rows: `MOR1 [Authors control]` left, `K3R1 [tri]` right for pots A..J, then native 3x Juglet vs oracle) shows the same gross assembled geometry on both sides at every pot; the renders are point clouds with per-arm labels and the seating difference of one sherd (e.g. D `23/28` vs `24/28`, H `10/11` vs `11/11`) is not visible by eye, so that part of the record rests on `score/acc_pot*.tsv` and `out/<arm>/1. Acc.txt`. One cosmetic quirk left as is: the `Pot_J_Piece_05` gate rows are labelled `tri_r0_d10_best3_deg` for every variant because that piece's best-of-K angle does not depend on the variant.

**Artifacts fetched to `C:/PR/artifacts/axis-parity-06/`:** `axes06_summary.json` (968 363 B), `gate06.tsv` (17 933 B, 228 rows, header `group\tpiece\tmetric\tvalue\treference\tverdict\tnote`), `render06_tri.png`, `render06_e2e.png`, `impl_t06.diff`, `score/acc_pot{A..J}.tsv`, `score/juglet/` (4 score json + 4 cluster json + `summary.tsv` + `best_of_4.json`), `sacct_all.txt`.

**Not done, by design:** no tracked change in `SfSpp_preprocessing` or `structure-from-sherds-pp`, no merge, no push, no `ticket_close.sh`, `**Status:**` left `in-progress`, and both watcher jobs were killed before this write-up.

Reading: tri-selector-passes-all-ten-pots-and-juglet

