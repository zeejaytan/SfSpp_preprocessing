# 08: Validate deduplicated own surfaces across all 10 pots and the Juglet

**What to build:** Deduplicate exact duplicate XYZ coordinates in memory across all 148 own-surface pot walls (`Pot A..J`) and 9 `def_3x` Juglet walls (`157` pieces total, `314` wall files), extract axis packs with the frozen `SHIP` estimator, and run the 10-pot + `def_3x` Juglet E2E assembly suite against both the `MOR1/2` Authors' controls and the Ticket 03 `OWN_RAW` (`t03-pot*`, `t03-juglet`) baselines.

**Answers:** E2

**Blocked by:** None. Surface Parity 06 verified that deduplicating Nov 5 Pot E walls alone (`OWN_NOV5_DEDUP`) recovers 62/62 Pot E joins in 2/2 repeats. Ticket number `08` keeps the existing `axis-parity` worktree in `C:/PR/worktrees/sfs/07` intact.

**Status:** ready-for-agent

**Worker:** unassigned

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

- [ ] `walls.tsv` has 314 rows (157 pieces × 2 faces) with exact header `stem,pot,face,native_points,points,duplicate_xyz,xyz_sha256,normals_sha256,source_sha256`. Verify `duplicate_xyz == 0` on all 314 rows. Record `sources.tsv` (`kind,path,sha256,bytes,detail`) including SHIP code hashes, corpus MD5 proof, and `t08/` script hashes.
- [ ] `axes.tsv` has 157 rows with exact header `stem,pot,in_141_gt,excluded_by_paper,k_raw,k_dedup,axes_sha256_dedup,effective_stride,drawn_points,rank1_deg_raw,rank1_deg_dedup,best_deg_raw,best_deg_dedup,d_gt_to_est_mm_dedup,d_est_to_gt_mm_dedup,is_base_dedup`. Verify E27 and E28 Ticket 05 SHA-256 pins and `Juglet_Piece_7` sole `is_base_dedup=1`.
- [ ] `pots_e2e.tsv` (40 rows: 10 pots × 4 arms `MOR1/2, K3R1/2`) has exact header `pot,arm,sherd,sherd_den,edge,edge_den,sherd_floor,edge_floor,floor_pass,t03_sherd,t03_edge,delta_edge,wall_secs`. `juglet_e2e.tsv` (4 rows) has exact header `arm,cluster_len,cluster_seated,cluster_max_chamfer_mm,cluster_members_le_050,edges_strict,edges_of,p7_strict,floor_pass`. `comparison_vs_t03.tsv` (11 rows, vessels `A..J` + `JUGLET`) has exact header `vessel,mor_best,t03_own_raw_best,t08_own_dedup_best,reached_by,floor_pass,regression_vs_t03,note`.
- [ ] `fixtures.tsv` has exact header `fixture,status,detail` and records `PASS` for all 4 named fixtures run on Spartan: `dedup_first_order`, `verbatim_6vec`, `juglet_native_3x_guard`, and `e27_e28_pin_match`.
- [ ] `renders.tsv` has exact header `figure,path,scale_bar_mm` (`scale_bar_mm = 20`) listing `renders/Pot_A_to_J_and_Juglet_e2e.png` (adapted from `t03_render_eleven.py`, 11 rows `MOR1` vs `K3R1` for `A..J` plus `Juglet` vs oracle, with a `20 mm` scale bar in every panel). Inspect the PNG by eye.
- [ ] `jobs.tsv` has exact header `job_id,stage,vessel,state,exit_code` recording every submitted Slurm job and its terminal `sacct` state/exit code (`check08.py --expect-terminal` passes after polling). Write `## Write-back` with facts only, best-of-N across repeats, explicit regression comparison vs `t03-*`, budget used, one end state, a per-requirement compliance table, and a separate read-only DeepSeek review that checks the tables and opens the PNG. Leave interpretation, commits, and closure to the lead.

Named checks: `python -m py_compile` on `.scratch/surface-parity/t08/{extract08,report08,check08}.py`, `bash -n .scratch/surface-parity/t08/extract08.sbatch .scratch/surface-parity/t08/launch_e2e08.sh`, fixtures and `check08.py` on Spartan (plus `check08.py --expect-terminal` after polling), and `git diff --check`.
