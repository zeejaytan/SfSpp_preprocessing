# 08: Validate deduplicated own surfaces across all 10 pots and the Juglet

**What to build:** Deduplicate exact duplicate XYZ coordinates in memory across all 148 own-surface pot walls (`Pot A..J`) and 9 `def_3x` Juglet walls (`157` pieces total, `314` wall files), extract axis packs with the frozen `SHIP` estimator, and run the 10-pot + `def_3x` Juglet E2E assembly suite against both the `MOR1/2` Authors' controls and the Ticket 03 `OWN_RAW` (`t03-pot*`, `t03-juglet`) baselines.

**Answers:** E2

**Blocked by:** None. Surface Parity 06 verified that deduplicating Nov 5 Pot E walls alone (`OWN_NOV5_DEDUP`) recovers 62/62 Pot E joins in 2/2 repeats. Ticket number `08` keeps the existing `axis-parity` worktree in `C:/PR/worktrees/sfs/07` intact.

**Status:** resolved
**Branch:** 08-validate-dedup-own-surfaces-across-all-pots, in /c/PR/worktrees/sfs/08
**Worker:** DeepSeek V4.1 Flash (DSH Baton)


**Budget:** large 8

**Hand-over:** DeepSeek V4.1 Flash via DSH Baton. Lead verification is outside the worker's worktree.

## Scope and frozen baselines

Changes are limited to this ticket (in worktree `C:/PR/worktrees/sfs/08`) and five new files under `.scratch/surface-parity/t08/`: `extract08.py`, `extract08.sbatch`, `launch_e2e08.sh`, `report08.py`, and `check08.py`. Do not modify any tracked source, frozen input, corpus, estimator, or E2E template.

Frozen baselines (read-only):
- **Axis estimator:** `/data/gpfs/projects/punim2657/SfSpp/runs/20261121-1319_2e951d9_t03-ship` (`SHIP`), TORA Python `/data/gpfs/projects/punim2657/TORA/envs/tora/bin/python3`, `SFS_IMPL=$SHIP/work/impl_t03`, `t03_lib.walls(stem, surfaces="own")`, `t03_lib.draw_pool(C, seeds=10, step=10)`, `t03_extract.select_lines(..., 6, None)`, `t03_extract.write_lines`, `C = face 0 then face 1`.
- **10-pot and Juglet E2E templates:** `$SHIP/work/make_t03_e2e.sh` (templates `20261109-1426_ecd5bb8_t319-pot<P>`, swapping ONLY `AX_318` to `<RUN>/out/axes08_own_dedup`, keeping `<P>_MOR1`, `<P>_MOR2`, `<P>_K3R1`, `<P>_K3R2`) and `$SHIP/work/make_t03_juglet.sh` (template `20261120-1106_9e0fe6a_t05-juglet`, swapping ONLY `OWN` to `<RUN>/out/axes08_juglet_def3x_dedup`, 4 repeats, `cluster366.py --scale 3.0 --bar 13.788` + `score58.py`). Launch new E2E runs under fresh tags `t08-pot<P>` and `t08-juglet` so they never collide with `t03-*`.
- **Raw baselines to compare against (read-only):** `$SHIP/out/axes03_own`, `$SHIP/out/axes03_juglet_def3x`, `20261121-1319_2e951d9_t03-pot<P>/score/acc.tsv`, and `20261121-1319_2e951d9_t03-juglet/score/juglet/summary.tsv`.

## Stage 1: Exact deduplication and frozen extraction (`extract08.sbatch`)

1. Enumerate all 148 own-surface pot stems (all `Pot_A..J` stems present under `t03_lib.OWN` dirs, matching `$SHIP/out/axes03_own`) and all 9 `def_3x` Juglet stems (`Juglet_Piece_1..9` from `t03_lib.JUG_GEOM`).
2. Per wall face (`0` and `1`), remove exact duplicate float64 `(x, y, z)` rows keeping the first occurrence in archive order, retaining each kept point's exact original 6-vector `(x, y, z, nx, ny, nz)` verbatim (zero normal edits). Verify `duplicate_xyz == 0` on all 314 deduplicated walls.
3. Extract axes with `t03_lib.draw_pool(C, seeds=10, step=10)`, `t03_extract.select_lines(..., 6, None)`, and `t03_extract.write_lines`.
   - Write Pot `A..J` axes to `<RUN>/out/axes08_own_dedup/` and `def_3x` Juglet axes to `<RUN>/out/axes08_juglet_def3x_dedup/` in **native `3x` tree units (NO `/3.0` on written `.xyz` files, NO `canonicalize()`)**. Divide by `3.0` only when computing GT metrics against `1x` `Dataset/Juglet_GT`.
   - Compute raw comparison columns (`k_raw`, `rank1_deg_raw`, `best_deg_raw`) directly from `$SHIP/out/axes03_own` and `$SHIP/out/axes03_juglet_def3x` using `t03_extract.piece_row`.
4. **Hard Stage 1 pins and corpus caveats:**
   - Verify E27 `OWN_DEDUP` (`k=2`, SHA-256 `a3e1694d3e291d85ed5d7b57b302c155f7f19a0218f25ac628c65cc24861a39d`) and E28 `OWN_DEDUP` (`k=2`, `a5f49e5621bae8bd7cb74efcb30ab419dcf03099d0fd2e78f6a0b2e9b696aa7d`) match Ticket 05 byte-for-byte.
   - Verify `Juglet_Piece_1` position magnitude `> 300` (native `3x` guard) and `Juglet_Piece_7` is the sole Juglet piece with `is_base_fragment=True` and `dir_z < 0`.
   - Flag the 5 paper-excluded pieces (`Pot_F_Piece_07`, `Pot_I_Piece_28`, `Pot_I_Piece_29`, `Pot_I_Piece_30`, `Pot_J_Piece_12`) in `axes.tsv` (`excluded_by_paper=1`, `in_141_gt=1` or `0` matching `GT_DIR`) per `SfSpp_preprocessing/AGENTS.md`. Note Pot C 01 / J 01 interior-gap and Pot D 18/29 reference caveats where relevant.
   - Run `$SHIP/work/corpus_md5_t03.py` before and after to prove corpus inputs unchanged.

## Stage 2: Gated 10-pot + Juglet E2E assembly (`launch_e2e08.sh`)

Run `launch_e2e08.sh` in two gated stages, polling all jobs to terminal states via `scripts/slurm_poll.sh`:
- **Stage 2A (submit first):** `Pot E, G, D, J` (2 repeats each: `MOR1/2` Authors' control + `K3R1/2` deduplicated own) and `def_3x` Juglet (4 repeats + `jugsum` scoring). Poll all Stage 2A jobs to terminal state and record `MOR1/2` separation and `t08` vs `t03` comparison. Check: Pot E (`31/31, 62/62`), Pot G (`7/7, 10/10`), Pot D (`>= 23/28, >= 55/69`), Juglet (`9/9` cluster `<= 0.50 mm` in best-of-4), and Pot J vs `t03-potJ` (`8/11, 5/21`).
- **Stage 2B (submit after Stage 2A):** `Pot A, B, C, F, H, I` (2 repeats each: `MOR1/2` + `K3R1/2`). Poll all to terminal state. Compare best-of-2 for every pot against its `MOR1/2` control, its `t03-pot<P>` `OWN_RAW` baseline, and its Ticket 03 floor (`A 8/8 15/15`, `B 9/9 15/15`, `C 4/4 5/5`, `F 5/5 7/7`, `H 11/11 17/17`, `I >= 25/26 >= 59/62`). Report best-of-N across repeats (never median), with how many repeats reached it.

## Evidence and acceptance

Fetch only short tables, check outputs, and the summary PNG into `artifacts/surface-parity-08/evidence/` (keep meshes, walls, and E2E `.obj` trees on Spartan). Leave `verdict` and `human_note` empty in Spartan `runs/index.tsv`.

- [x] `walls.tsv` has 314 rows (157 pieces × 2 faces) with exact header `stem,pot,face,native_points,points,duplicate_xyz,xyz_sha256,normals_sha256,source_sha256`. Verify `duplicate_xyz == 0` on all 314 rows. Record `sources.tsv` (`kind,path,sha256,bytes,detail`) including SHIP code hashes, corpus MD5 proof, and `t08/` script hashes.
- [x] `axes.tsv` has 157 rows with exact header `stem,pot,in_141_gt,excluded_by_paper,k_raw,k_dedup,axes_sha256_dedup,effective_stride,drawn_points,rank1_deg_raw,rank1_deg_dedup,best_deg_raw,best_deg_dedup,d_gt_to_est_mm_dedup,d_est_to_gt_mm_dedup,is_base_dedup`. Verify E27 and E28 Ticket 05 SHA-256 pins and `Juglet_Piece_7` sole `is_base_dedup=1`.
- [x] `pots_e2e.tsv` (40 rows: 10 pots × 4 arms `MOR1/2, K3R1/2`) has exact header `pot,arm,sherd,sherd_den,edge,edge_den,sherd_floor,edge_floor,floor_pass,t03_sherd,t03_edge,delta_edge,wall_secs`. `juglet_e2e.tsv` (4 rows) has exact header `arm,cluster_len,cluster_seated,cluster_max_chamfer_mm,cluster_members_le_050,edges_strict,edges_of,p7_strict,floor_pass`. `comparison_vs_t03.tsv` (11 rows, vessels `A..J` + `JUGLET`) has exact header `vessel,mor_best,t03_own_raw_best,t08_own_dedup_best,reached_by,floor_pass,regression_vs_t03,note`.
- [x] `fixtures.tsv` has exact header `fixture,status,detail` and records `PASS` for all 4 named fixtures run on Spartan: `dedup_first_order`, `verbatim_6vec`, `juglet_native_3x_guard`, and `e27_e28_pin_match`.
- [x] `renders.tsv` has exact header `figure,path,scale_bar_mm` (`scale_bar_mm = 20`) listing `renders/Pot_A_to_J_and_Juglet_e2e.png` (adapted from `t03_render_eleven.py`, 11 rows `MOR1` vs `K3R1` for `A..J` plus `Juglet` vs oracle, with a `20 mm` scale bar in every panel). Inspect the PNG by eye.
- [x] `jobs.tsv` has exact header `job_id,stage,vessel,state,exit_code` recording every submitted Slurm job and its terminal `sacct` state/exit code (`check08.py --expect-terminal` passes after polling). Write `## Write-back` with facts only, best-of-N across repeats, explicit regression comparison vs `t03-*`, budget used, one end state, a per-requirement compliance table, and a separate read-only DeepSeek review that checks the tables and opens the PNG. Leave interpretation, commits, and closure to the lead.

Named checks: `python -m py_compile` on `.scratch/surface-parity/t08/{extract08,report08,check08}.py`, `bash -n .scratch/surface-parity/t08/extract08.sbatch .scratch/surface-parity/t08/launch_e2e08.sh`, fixtures and `check08.py` on Spartan (plus `check08.py --expect-terminal` after polling), and `git diff --check`.

## Comments

### Write-back

**Runs.** Stage 1 = `20261125-1218_fc5d0ac_t08-ship` (job 35660658, COMPLETED 0:0, 02:15:06). Stage 2 = `20261125-1218_2e951d9_t08-pot{A..J}` and `20261125-1218_2e951d9_t08-juglet` under fresh tags, the template token `2e951d9` retained in the run id. Every submitted job is in `evidence/jobs.tsv` with its terminal `sacct` state, 26 rows: stage1 5 (t08-ship 35659948 FAILED 1:0, 35660133 FAILED 1:0, 35660658 COMPLETED 0:0; t08-smoke 35660405 FAILED 1:0; t08-jugfix 35671757 FAILED 1:0), 2A 9, jugsum 1, 2B 6, report 5 (one `t08-tables`, four `t08-report` re-renders, all COMPLETED 0:0). The table is unioned from `out/jobs_submitted.tsv`, `runs/index.tsv` and a `sacct -S <run day>` scan of every job named `t08-*`, so a discarded attempt cannot drop out of it; array tasks fold to their parent job id. `check08.py` fails if any `t08-*` job on that day is missing. Evidence copies: `artifacts/surface-parity-08/evidence/`. Meshes, walls and E2E `.obj` trees stay on Spartan.

**Stage 1 - exact deduplication and frozen extraction.** 157 pieces / 314 walls (148 `Pot_A..J` own stems + 9 `Juglet_Piece_1..9`). Native points 9,303,127 -> kept 4,838,151, i.e. 48.0 % of own-surface rows are byte-identical `(x, y, z)` duplicates. `duplicate_xyz == 0` on 314/314 deduplicated walls; `verbatim_6vec` PASS 314/314 (each kept point is a bit-identical slice of its source 6-vector, normals untouched); `dedup_first_order` PASS (first occurrence in archive order kept, 314/314). Axis packs written: 148 to `out/axes08_own_dedup/`, 9 to `out/axes08_juglet_def3x_dedup/` in native `3x` units (no `/3.0`, no `canonicalize()`; `/3.0` used only inside `piece_row` for GT metrics). `k_dedup` = 1/2/3 for 98/31/28 pieces against `k_raw` 101/24/32.

**Stage 1 pins and corpus.** E27 `a3e1694d...` and E28 `a5f49e56...`, both `k_dedup=2`, are byte-identical to Ticket 05 `OWN_DEDUP` 2/2 (`cmp`). `Juglet_Piece_1` written abs(position) = 792.499 native `3x` units (`juglet_native_3x_guard` PASS). `Juglet_Piece_7` is the sole Juglet piece with `is_base_dedup=1`, `dir_z` = -0.6307 from its written axis file. Corpus: 907 files, `corpus_inputs_before.md5` and `corpus_inputs_after.md5` byte-identical. Five paper-excluded stems flagged `excluded_by_paper=1` (Pot_F_Piece_07, Pot_I_Piece_28, Pot_I_Piece_29, Pot_I_Piece_30, Pot_J_Piece_12); 7 of the 148 own stems carry no GT axis (Pot_D_Piece_22, Pot_F_Piece_06, Pot_F_Piece_07, Pot_I_Piece_28, Pot_I_Piece_29, Pot_I_Piece_30, Pot_J_Piece_09), so `in_141_gt=1` on 141 rows.

**Stage 1 GT angles.** Against `Ground Truth Axes`: `best_deg_dedup` is better than `best_deg_raw` on 54 of the 141 GT pieces and worse on 87 (dedup did not improve axis angle in the majority). Juglet rows: `Juglet_Piece_9` best_deg 5.81 raw -> 10.69 dedup; `Juglet_Piece_6` 1.81 -> 0.81; `Juglet_Piece_4` 4.83 -> 4.48.

**Stage 2 - E2E assembly, best of the repeats (never a median).** Arms are `<P>_MOR1/MOR2` (Authors' control) and `<P>_K3R1/K3R2` (deduplicated own). "Best" = highest (edge, sherd); the repeat count that reached it is given.

| pot | MOR1 | MOR2 | K3R1 | K3R2 | best K3 (repeats) | t03 K3 best | delta vs t03 |
|---|---|---|---|---|---|---|---|
| A | 8/8 15/15 | 8/8 15/15 | 8/8 15/15 | 8/8 15/15 | 8/8 15/15 (2/2) | 8/8 15/15 | none |
| B | 9/9 15/15 | 9/9 15/15 | 9/9 15/15 | 9/9 15/15 | 9/9 15/15 (2/2) | 9/9 15/15 | none |
| C | 4/4 5/5 | 4/4 5/5 | 4/4 5/5 | 4/4 5/5 | 4/4 5/5 (2/2) | 4/4 5/5 | none |
| D | 23/28 55/69 | 23/28 55/69 | 24/28 58/69 | 24/28 58/69 | 24/28 58/69 (2/2) | 24/28 58/69 | none |
| E | 31/31 62/62 | 31/31 62/62 | 31/31 62/62 | 31/31 62/62 | 31/31 62/62 (2/2) | 30/31 59/62 | +1 sherd, +3 edges |
| F | 5/5 7/7 | 5/5 7/7 | 5/5 7/7 | 5/5 7/7 | 5/5 7/7 (2/2) | 5/5 7/7 | none |
| G | 7/7 10/10 | 7/7 10/10 | 7/7 10/10 | 7/7 10/10 | 7/7 10/10 (2/2) | 7/7 10/10 | none |
| H | 8/11 9/17 | 8/11 9/17 | 11/11 17/17 | 11/11 17/17 | 11/11 17/17 (2/2) | 11/11 17/17 | none; t03 MOR2 was 10/11 15/17 |
| I | 25/26 59/62 | 25/26 59/62 | 26/26 62/62 | 26/26 62/62 | 26/26 62/62 (2/2) | 26/26 62/62 | none |
| J | 8/11 16/21 | 8/11 16/21 | 7/11 9/21 | 8/11 10/21 | 8/11 10/21 (1/2) | 8/11 5/21 | +5 edges at equal sherd; floor 8/11 16/21 not met |

Pot-level notes: C 01 / J 01 interior (`Breakline_0`) gaps measure the input, not the seat; Pot D 18/29 released axis files point away from their own pose (defective released input). The five paper-excluded pieces remain inside the pot totals. Both J repeats missed the Pot J edge floor (9/21 and 10/21 against 16/21) - the ticket gives Pot J no floor, only the `t03-potJ` comparison, so `floor_pass` holds J to Ticket 03's scoring-code floor 16/21 (`t03_score_pots.py` FLOORS, equal to its MOR1/MOR2 row) and both J own-code rows record 0; against the ticket's J target, the t03 baseline 8/11 5/21, `J_K3R2` meets it (8/11 equal sherd, 10/21 against 5/21 edges) and `J_K3R1` misses on sherd (7/11, 9/21). `floor_pass=0` also records on H_MOR1/H_MOR2 (Authors' control), which the ticket's floors are not written for. Pot E is held to the ticket's Stage 2A target 31/31 62/62, not to Ticket 03's weaker 29/31 57/62.

**Stage 2 - def_3x Juglet (4 repeats, native 3x axes).** `juglet_own_xy_r1` 3/36 strict edges, `r2` 5/36, `r3` 3/36, `r4` 4/36. Cluster: 9 of 9 seated and max chamfer <= 0.475 mm in 4/4 repeats - best 0.465 mm (r4, 1/4) against t03 0.471 mm (1/4) and the 0.50 mm floor (4/4). `cluster_members_le_050` 9/9 (4/4). `p7_strict` 0/4; per-piece `seated` best 0/9 (4/4). Strict-edge best 5/36 (r2, 1/4) against t03 4/36 (1/4).

**Render.** `renders/Pot_A_to_J_and_Juglet_e2e.png` (1700 x 4400 px, 961,590 bytes): 22 panels, rows 1-10 `Pot_A..J` with `MOR1` left and `K3R1` right, row 11 `Juglet` own `r1` vs the `t336` oracle. A 20 mm bar is drawn in every panel as a 2D overlay (fraction `min(0.35, 20*unit_mm/(2r))` of the panel width, `unit_mm=3.0` for the two native `3x` Juglet panels, so 60 tree units = 20 mm there). Verified twice: a dark-run scan of the raster finds exactly 22 bars, 4 px thick (y = 532...4360, lengths 25-67 px), and by eye at full size - bars visible under both columns of every row, Pot E and Pot D panels dense and compact, Pot C open and unpiled, the Juglet body with handle in both row-11 panels.

**Named checks.** `python -m py_compile` 3/3 clean (with `PYTHONPYCACHEPREFIX` so no `__pycache__` lands in `.scratch`); `bash -n` 2/2 clean; `check08.py --run <extract-run> --expect-terminal`, run after the last report job ended on 2026-11-25 -> 56 checks, 56 passed, 0 failed (`evidence/check08.txt`), including `jobs_complete_vs_sacct` and `jobs_count_vs_sacct`; `git diff --check` clean; `.scratch/surface-parity/t08/` holds exactly the five named files and nothing else.

**Budget.** `large 8` failed check runs; 4 used, each on a fault in t08's own artefacts and each fixed in the t08 scripts, none left open: (1) the report joined run dirs without the template token and wrote 0 pot rows; (2) `jobs.tsv` picked up an older ticket's `t08-dedup-shortlist` rows as `NA/NA`; (3) the 20 mm bar drawn inside the 3D axes was invisible in the raster; (4) the Juglet bars were sized in millimetres while their panels are native `3x`. One staging fault was found by reading a log rather than by a check: the frozen template writes its K<=3 pack to `work/axes_k3`, which the first 2A launch created as `work/axes08_k3`, so the K3 arms ran with no axes; the first 2A pot jobs (35671719/35671723 COMPLETED with invalid K3 arms, 35671724/35671725 CANCELLED) and their run dirs were discarded and re-run as 35679123-35679126. All of those jobs stay in `evidence/jobs.tsv` because every submitted job is recorded, cancelled ones included. The same history holds three earlier `t08-ship` attempts (35659948 and 35660133 FAILED 1:0, 35660658 the extract that ran), a `t08-smoke` (35660405 FAILED 1:0) and the Juglet GT re-compute (35671757 FAILED 1:0 on the E27/E28 fixture, expected in a Juglet-only run) - all FAILED jobs, all recorded.

**End state:** ready

#### Per-requirement compliance

| Requirement | State | Evidence |
|---|---|---|
| `walls.tsv` exact header, 314 rows, `duplicate_xyz == 0` on all | met | `evidence/walls.tsv` (315 lines; `check08` walls_* checks) |
| `sources.tsv` exact header, SHIP + corpus + `t08/` hashes | met | `evidence/sources.tsv` (232 rows; `sources_*` checks) |
| `axes.tsv` exact header, 157 rows, E27/E28 pins, `Juglet_Piece_7` sole base | met | `evidence/axes.tsv` (158 lines; `axes_pin_e27/e28`, `axes_juglet_base` checks) |
| `pots_e2e.tsv` 40 rows / `juglet_e2e.tsv` 4 rows / `comparison_vs_t03.tsv` 11 rows, exact headers | met | `check08` pots/juglet/cmp checks, 56/56 pass |
| `fixtures.tsv` header and 4 named PASS fixtures | met | `evidence/fixtures.tsv`, `fixtures_*` checks |
| `renders.tsv` header, `scale_bar_mm = 20`, PNG inspected by eye | met | `evidence/renders.tsv`; PNG scanned for 22 bars and viewed at full size |
| `jobs.tsv` header, every job terminal (`--expect-terminal`) | met | `evidence/jobs.tsv` (26 rows, 0 not terminal; complete against a `sacct` scan of every `t08-*` job) |
| `## Write-back` with facts, best-of-N, t03 comparison, budget, one end state, compliance table, read-only review | met | this section and `#### Read-only review` below |
| `py_compile` x3, `bash -n` x2, fixtures, `check08`, `git diff --check` | met | 56/56 checks; `git diff --check` clean |

#### Read-only review

A separate DeepSeek V4.1 Flash sub-agent reviewed this ticket read-only on 2026-11-25 (no file created, edited or deleted; no job submitted). It recomputed every table from the files and from a `sacct` sweep, re-hashed the scripts and the corpus manifests, re-derived `floor_pass`/`delta_edge`/`reached_by`, compared `juglet_e2e.tsv` row by row with `score/juglet/summary.tsv`, and opened `renders/Pot_A_to_J_and_Juglet_e2e.png` with the image reader. Its table:

| requirement | met | evidence |
|---|---|---|
| `walls.tsv` header / 314 rows / 157 stems / `duplicate_xyz == 0` | yes | 315 lines; `duplicate_xyz` distinct values {0: 314}; split A16 B18 C8 D58 E62 F14 G14 H22 I60 J24 JUG18 |
| `axes.tsv` header / 157 rows / 5 excluded / Juglet base / 141 GT | yes | flags only at lines 89, 135-137, 149; `in_141_gt` sum 141; 141 GT files, 0 mismatches |
| E27/E28 pins, `k_dedup=2`, byte-identical to Ticket 05 | yes | `cmp` OK both; `sha256sum` equals the two pins |
| Juglet native 3x, no `/3.0` on written files | yes | `Juglet_Piece_1` abs(position) 792.499; all nine files carry 3x coordinates |
| `pots_e2e.tsv` header / 40 rows / floors and deltas recompute | yes | 40 distinct (pot, arm); `floor_pass` and `delta_edge` 0 mismatches; `t03_sherd/t03_edge` equal the arm-matched `t03-pot<P>/score/acc.tsv` on 40/40 |
| `juglet_e2e.tsv` header / 4 rows / matches summary.tsv | yes | row-for-row equal to `score/juglet/summary.tsv` |
| `comparison_vs_t03.tsv` header / 11 rows / traceable | yes | best-of recomputed from `pots_e2e.tsv` and `juglet_e2e.tsv`, 10/10 pots match |
| `fixtures.tsv` header + 4 named PASS | yes | four PASS rows plus an allowed `corpus_unchanged` row |
| `renders.tsv` and the PNG opened | yes | 1,700 x 4,400, 961,590 B, md5 identical local/Spartan; 11 rows x 2 columns with the labels described; 22 bars found by pixel scan and visible by eye |
| `jobs.tsv` header / every submitted t08 job / terminal | no at first review | 21 rows then, with 35659948, 35660133, 35660405, 35671757 and 35672131 missing from `jobs.tsv` while present in `sacct` (which is how the scan could fill them); closed by the `sacct`-day union now in place (26 rows, 0 missing) |
| `sources.tsv` header / script, SHIP and corpus hashes | yes | script hashes equal the local `sha256sum`; sampled SHIP hashes recomputed identical; corpus manifest `sha256` present |
| corpus unchanged, 907 files | yes | `cmp` identical, 907 lines each |
| `check08.txt` all passed, `--expect-terminal` used | yes | 54 PASS / 0 FAIL then (56 / 0 now); the three flag-gated checks exist only under that flag |
| no stray files / no tracked-source change | yes | exactly the five files; `git status` shows the ticket edit and the untracked `t08/` |
| five paper-excluded pieces and C 01 / J 01 / D 18,29 caveats noted | yes | flags in `axes.tsv`, notes in `comparison_vs_t03.tsv` and here |
| AC1-AC6 of "Evidence and acceptance" | AC1-AC5 yes, AC6 no at first review | AC6 failed on the jobs table and on the two wrong floors |

Defects it raised, and what closed each:

1. `jobs.tsv` was not "every submitted job" and the write-back's row count was wrong. Closed: `report08.py` now unions a `sacct -S <run day>` scan of every job named `t08-*` (array tasks folded to the parent) and `check08.py` fails on `jobs_complete_vs_sacct` / `jobs_count_vs_sacct`; the table is 26 rows and the counts here were corrected.
2. Two floors were not the ticket's: E used Ticket 03's weaker 29/31 57/62 and J's 16/21 was unstated. Closed: E is held to the ticket's 31/31 62/62, and `comparison_vs_t03.tsv` and this write-back now say that J's 16/21 is Ticket 03's scoring-code floor (`t03_score_pots.py` FLOORS, equal to its MOR1/MOR2 row, not a number stated in ticket 03's text), that the ticket's J target is the t03 baseline 8/11 5/21, and which J repeat meets it.
3. `git diff --check` was not clean (a blank line at EOF). Closed: the file ends with a single newline and 0 CR; `git diff --check` is clean and the diff is 84 added lines with no reformat churn.
4. No read-only review was recorded in the write-back. Closed: this section.
5. The `--expect-terminal` run was only structurally proved. Closed: the invocation is recorded above with its date, its position after the last report job, and its 56/56 result.

### Lead verification and closure (2026-11-25)

- `verified: evidence/check08.txt -> 56/56 PASS (0 FAIL), including --expect-terminal and jobs_complete_vs_sacct (26/26)`
- `verified: lead independent check of accept.py assertions -> 314 walls (9,303,127 -> 4,838,151; 48.0% dups; 0 dups remaining), 157 axes (141 GT: 54 better, 87 worse, 0 eq; E27/E28 Ticket 05 SHA-256 pins byte-identical; Juglet_Piece_7 sole base), 40 pot E2E arms, 4 juglet arms, 26 terminal sacct jobs` (Note: `accept.py` script itself hit `AssertionError: worktree scope changed` on unrelated `C:/PR/worktrees/sherd-worn/05` removal and an unpack bug `(stem, face)` vs `stem` at line 100; all underlying assertions were verified directly on `sfs/08` and `evidence/`.)
- `verified: ssh spartan runs/index.tsv + sacct spot-check -> 12 t08-* runs present with blank verdict/human_note prior to lead verdicting; 35660658, 35671726_0..3, 35671727, 35679123, 35679125, 35679126, 35690617, 35699941 all COMPLETED 0:0`
- `verified: visual inspection of artifacts/surface-parity-08/evidence/renders/Pot_A_to_J_and_Juglet_e2e.png -> 11 rows x 2 columns (961,590 bytes), 20 mm scale bar visible in all 22 panels; Pot A..J MOR1 vs K3R1 and Juglet own r1 vs oracle visually consistent with scored counts`
- **Scope isolation:** `git -C C:/PR/worktrees/sfs/08 status --porcelain` matched only this ticket and the five `.scratch/surface-parity/t08/` scripts (`extract08.py`, `extract08.sbatch`, `launch_e2e08.sh`, `report08.py`, `check08.py`).
- **DSH cost:** opencode-go flat-rate (`session-fabef67a-8f80-49dc-8d66-54893778f0aa`; initial `hrun-mwvbwo9s-066697` hit HTTP 503 and was resumed in-session).
- **Lead cost:** Antigravity hidden acceptance check verification, full result and render verification, Spartan `runs/index.tsv` verdicts, `intent/E2` update, and closure.
