# 09: Regenerate canonical own surfaces across all 10 pots and def_3x Juglet

**What to build:** Build `MeshPreprocessingHeadless`, `EdgeLineExtractionHeadless`, and `SurfaceDedupeTest` from pinned post-Ticket-09 `main` (`a50f8cc0ebe17621e2ce32424808c7414c2d7bbf`), regenerate all 148 own-surface pot pieces (`Pot A..J`) and 9 `def_3x` Juglet pieces (`157` pieces, `314` walls + `314` breaklines) into ONE canonical Spartan run directory (`t09-own-surfaces`), validate the regenerated walls through frozen `SHIP` axis extraction and the full 10-pot + `def_3x` Juglet E2E assembly suite against `MOR1/2`, `t03`, and `t08`, and write the canonical own-surface pointer manifest `sfs_axes/own_surfaces.json` with a schema test `tests/test_own_surfaces_manifest.py`.

**Answers:** E2

**Blocked by:** None. Surface Parity 08 validated deduplicating own surfaces across all 10 pots and the `def_3x` Juglet with zero assembly regressions (`31/31 62/62` on Pot E, `+5` edges on Pot J, `9/9 <= 0.465 mm` on Juglet), and Axis-parity Ticket 09 (`ee6345c`) already fixed duplicate point emission in `mesh_processing_headless.cpp`. Ticket number `09` uses free worktree `C:/PR/worktrees/sfs/09`.

**Status:** in-progress
**Working in:** C:/PR/worktrees/sfs/09 (2026-11-26)
**Branch:** 09-regenerate-canonical-own-surfaces, in /c/PR/worktrees/sfs/09
**Worker:** DeepSeek V4.1 Flash (DSH Baton)


**Budget:** large 8

**Hand-over:** DeepSeek V4.1 Flash via DSH Baton. Lead verification is outside the worker's worktree.

## Scope and frozen baselines

Changes are limited to `C:/PR/worktrees/sfs/09`: this ticket file (write-back), `sfs_axes/own_surfaces.json`, `tests/test_own_surfaces_manifest.py`, and seven new files under `.scratch/surface-parity/t09/`: `build09.sbatch`, `regen09.sbatch`, `extract09.py`, `extract09.sbatch`, `launch_e2e09.sh`, `report09.py`, and `check09.py`. Do NOT modify any tracked C++ source, `AGENTS.md`, `scripts/run_benchmark_172.py`, frozen input, corpus, archived `t66`/`t305-lane-*`/`t01`/`t80`/`t03`/`t08` run directory, estimator, or E2E template.

Frozen baselines (read-only):
- **Preprocessing source and container:** `$CANON=/data/gpfs/projects/punim2657/sfs_preprocessing`, pinned commit `a50f8cc0ebe17621e2ce32424808c7414c2d7bbf` (fetch `origin` first so `a50f8cc0ebe17621e2ce32424808c7414c2d7bbf` is present), container `$CANON/pcl_191_nurbs.sif`, Apptainer `/apps/easybuild-2022/easybuild/software/Compiler/GCCcore/11.3.0/Apptainer/1.3.3/bin/apptainer`, TORA Python `/data/gpfs/projects/punim2657/TORA/envs/tora/bin/python3`.
- **Pot `A..J` cell recipe (`148` pieces: `A 8, B 9, C 4, D 29, E 31, F 7, G 7, H 11, I 30, J 12`, exact stem list matching `$SHIP/out/axes03_own`):** `run_cell66.sh` archived from `a50f8cc`, `stage305.sh` copied read-only from `/data/gpfs/projects/punim2657/SfSpp/runs/20261105-0445_9c5eec2_t305-lane-e2/work/stage305.sh`, `SHIPPED="SFS_PAPER_CHAIN=1 SFS_PAPER_THETA=3.4 SFS_PAPER_KAPPA=1.0 SFS_PAPER_NB=10 SFS_SMOOTHNESS_DEG=3.4 SFS_CURVATURE_THRESH=1.0"`, `SFS_DEDUPE` unset/off, `SFS_WALL_PAIR_FILTER` unset (= Ticket 80 default ON), `_Mesh.obj` for `A, B` and `_Mesh_DS.obj` for `C..J`, corpus `$CORP=/data/gpfs/projects/punim2657/sfs_main/original_samples/SfS_pp`, per-pot manifest built from `$CORP/Point/MANIFEST_released.tsv` + `$CORP/Point/MANIFEST_derived.tsv`.
- **`def_3x` Juglet cell recipe (`9` pieces: `Juglet_Piece_1..9`):** exact `20261117-0430_d272313_t80-default-on` `def_3x` recipe (`POT=Juglet_large`, `WORNESS=0.7`, `MENV="SFS_NORMAL_MODE=radius SFS_NORMAL_RADIUS_MM=1.0 SFS_MERGE_CLUSTER_DOT=0.887 SFS_GROW_BASE_MM=1.5 SFS_GROW_BASE_THETA_DEG=25 SFS_TREE_UNITS_PER_MM=3.0"`, `SFS_DEDUPE` unset/off, `SFS_WALL_PAIR_FILTER` unset = default ON, `T331=/data/gpfs/projects/punim2657/SfSpp/runs/20261112-0218_b1e1580_t331-large`, `CL=$T331/cloud_mesh`, `MD=$T331/mesh_large`, `AX=/data/gpfs/projects/punim2657/Dataset/Juglet_large`, `MAN=$T331/pins/MANIFEST_JUGLET_LARGE.tsv`, `stage_synth_t73.sh` copied read-only from `/data/gpfs/projects/punim2657/SfSpp/runs/20261117-0430_d272313_t80-default-on/tools/stage_synth_t73.sh`).
- **Axis estimator and E2E baselines:** `$SHIP=/data/gpfs/projects/punim2657/SfSpp/runs/20261121-1319_2e951d9_t03-ship` (`t03_lib.draw_pool(C, seeds=10, step=10)`, `t03_extract.select_lines(..., 6, None)`, `t03_extract.write_lines`, `$SHIP/work/make_t03_e2e.sh`, `$SHIP/work/make_t03_juglet.sh`), comparing against both `$SHIP` (`t03`) and Ticket 08 (`T08=/data/gpfs/projects/punim2657/SfSpp/runs/20261125-1218_fc5d0ac_t08-ship`, `20261125-1218_2e951d9_t08-pot<P>`, `20261125-1218_2e951d9_t08-juglet`).
- **Trap (do NOT expect byte equality with Nov 5 walls):** `mesh_processing_headless.cpp` uses 30 unseeded ray casts AND now has Ticket 80's `SFS_WALL_PAIR_FILTER` ON by default, so regenerated walls are a fresh draw and will not hash-match Nov 5. Gate on structural invariants (`duplicate_xyz == 0`, `[DEDUPE-27]` `mode=off` & `in == out` & `normal_maxdiff <= 1e-6`, `nn_med_mm`/`nn_p90_mm` spread vs `t08`, and whole-vessel E2E assembly parity).

## Stage 1: Build pinned binaries and corpus snapshot (`build09.sbatch`)

1. Create canonical run dir `/data/gpfs/projects/punim2657/SfSpp/runs/<YYYYMMDD-HHMM>_a50f8cc_t09-own-surfaces/` on Spartan.
2. Fetch `origin` in `$CANON` and build `MeshPreprocessingHeadless`, `EdgeLineExtractionHeadless`, and `SurfaceDedupeTest` from pinned commit `a50f8cc0ebe17621e2ce32424808c7414c2d7bbf` inside `pcl_191_nurbs.sif`. Keep `build.log` and write `binaries.sha256`.
3. Run `./SurfaceDedupeTest` inside the build step (must exit 0 with all `CASE ... PASS`; save stdout to `logs/unit_test.txt`).
4. Write `run.json`, append to `/data/gpfs/projects/punim2657/SfSpp/runs/index.tsv` with blank `verdict` and `human_note`, and capture before-corpus MD5 (`$SHIP/work/corpus_md5_t03.py` plus `$T331/cloud_mesh/*.pcd` and `$T331/mesh_large/*.obj`).

## Stage 2: Parallel 11-vessel regeneration (`regen09.sbatch`, `--array=0-10`)

1. Run `regen09.sbatch` (`--array=0-10`) using the built binaries:
   - Tasks `0..9` = `Pot_A..Pot_J` (`148` pieces total) into `<RUN>/out/Pot_<P>/geom/`.
   - Task `10` = `Juglet_def3x` (`9` pieces `Juglet_Piece_1..9`) into `<RUN>/out/Juglet_def3x/geom/`.
2. Poll all 11 array tasks to terminal `sacct` states via `scripts/slurm_poll.sh`.
3. Verify every one of the `157` pieces has non-empty `.S0`, `.S1`, `.Bl0`, `.Bl1` (`314` walls + `314` breaklines), and parse all `314` `[DEDUPE-27]` lines verifying `mode=off`, `in == out`, and `0 <= normal_maxdiff <= 1e-6`.

## Stage 3: Axis extraction and gated E2E validation (`extract09.py`, `extract09.sbatch`, `launch_e2e09.sh`)

1. **`extract09.sbatch`:**
   - Verify `duplicate_xyz == 0` on all `314` regenerated `.S0`/`.S1` walls.
   - Compute per-wall nearest-neighbour spread (`nn_med_mm_vs_t08`, `nn_p90_mm_vs_t08`) against Ticket 08's deduplicated walls (dividing `def_3x` Juglet distances by `3.0` so all spread metrics are in mm).
   - Extract frozen `SHIP` axes to `<RUN>/out/axes09_own_regen/` (`148` pot stems) and `<RUN>/out/axes09_juglet_def3x_regen/` (`9` Juglet stems in native `3x` tree units — **NO `/3.0` on written `.xyz`, NO `canonicalize()`**; divide by `3.0` only when computing GT metrics against `1x` `Dataset/Juglet_GT`).
   - Verify `Juglet_Piece_1` `|position| > 300` and `Juglet_Piece_7` is sole Juglet piece with `is_base_t09=1` (`dir_z < 0`).
   - Flag the 5 paper-excluded pieces (`Pot_F_Piece_07`, `Pot_I_Piece_28`, `Pot_I_Piece_29`, `Pot_I_Piece_30`, `Pot_J_Piece_12`) in `axes.tsv` (`excluded_by_paper=1`), and note `Pot C 01` / `J 01` interior-gap and `Pot D 18/29` caveats.
   - Capture after-corpus MD5 and assert byte-identical match to before-corpus MD5.
2. **`launch_e2e09.sh` (gated 3A then 3B, fresh tags `t09-pot<P>` and `t09-juglet`):**
   - Swap ONLY `AX_318` in `$SHIP/work/make_t03_e2e.sh` to `<RUN>/out/axes09_own_regen` (keeping `<P>_MOR1`, `<P>_MOR2`, `<P>_K3R1`, `<P>_K3R2` and keeping the template's `work/axes_k3` path intact so `K3` arms receive the regenerated axes), and swap ONLY `OWN` in `$SHIP/work/make_t03_juglet.sh` to `<RUN>/out/axes09_juglet_def3x_regen` (4 repeats `juglet_own_xy_r1..4` + `jugsum`).
   - **Stage 3A first:** `Pot E, G, D, J` + `def_3x` Juglet + `jugsum`. Poll all Stage 3A jobs to terminal `sacct` states via `scripts/slurm_poll.sh` and check `MOR1/2` control separation and `t09` vs `t03`/`t08` parity.
   - **Stage 3B second:** `Pot A, B, C, F, H, I`. Poll all to terminal `sacct` states. Leave `verdict` and `human_note` blank in Spartan `runs/index.tsv`.

## Stage 4: Canonical pointer manifest and schema test

1. Create `sfs_axes/own_surfaces.json` pointing to the single canonical Spartan run directory from Stages 1–3:
   - Required top-level keys: `run_id`, `run_root`, `preprocessing_commit` (`"a50f8cc0ebe17621e2ce32424808c7414c2d7bbf"`), `binaries_sha256` (`MeshPreprocessingHeadless`, `EdgeLineExtractionHeadless`), `sfs_dedupe` (`"off"`), `sfs_wall_pair_filter` (`"default_on"`), `total_pieces` (`157`), `total_walls` (`314`), `duplicate_xyz` (`0`), `vessels` (exact 11 keys `"A".."J"` + `"JUGLET_DEF3X"`, each holding `geom_dir`, `pieces`, `units_per_mm`), `axes_own_regen`, and `axes_juglet_def3x_regen`.
   - Every `geom_dir` and axis dir must be rooted under `run_root` (no references to stale `t305-lane`, `t66-admitsign`, `t80-default-on`, or `out_poth` runs).
2. Create `tests/test_own_surfaces_manifest.py` using stdlib `unittest` verifying the JSON schema, 11 vessel keys, piece counts summing to `157`, `duplicate_xyz == 0`, valid 40-hex commit SHA and 64-hex binary hashes, all paths rooted under `run_root` containing `_t09-own-surfaces`, and absence of stale run substrings.

## Evidence and acceptance

Fetch only short TSV tables, check outputs, and the summary PNG into `artifacts/surface-parity-09/evidence/` (keep meshes, walls, breaklines, and E2E `.obj` trees on Spartan). Leave `verdict` and `human_note` empty in Spartan `runs/index.tsv`.

- [ ] `sources.tsv` (`kind,path,sha256,bytes,detail`) includes SHA-256 hashes of all 7 `t09/` scripts, both built binaries, `SurfaceDedupeTest` log, frozen `SHIP` code, and before/after corpus MD5 proof.
- [ ] `dedupe27.tsv` (314 rows) has exact header `stem,pot,face,mode,in_rows,out_rows,improved_rows,dups_skipped,appended,normal_maxdiff` with `mode == "off"`, `in_rows == out_rows > 0`, and `0 <= normal_maxdiff <= 1e-6` on all 314 rows. `walls.tsv` (314 rows) has exact header `stem,pot,face,points,duplicate_xyz,bl_points,nn_med_mm_vs_t08,nn_p90_mm_vs_t08,xyz_sha256,normals_sha256` with `duplicate_xyz == 0` and `bl_points > 0` on all 314 rows.
- [ ] `axes.tsv` (157 rows) has exact header `stem,pot,in_141_gt,excluded_by_paper,k_t08,k_t09,axes_sha256_t09,effective_stride,drawn_points,rank1_deg_t08,rank1_deg_t09,best_deg_t08,best_deg_t09,d_gt_to_est_mm_t09,d_est_to_gt_mm_t09,is_base_t09` with 141 GT rows, 5 paper-excluded pieces flagged, and `Juglet_Piece_7` sole `is_base_t09=1`.
- [ ] `pots_e2e.tsv` (40 rows: 10 pots × 4 arms `<P>_MOR1/2, <P>_K3R1/2`) has exact header `pot,arm,sherd,sherd_den,edge,edge_den,sherd_floor,edge_floor,floor_pass,t03_sherd,t03_edge,t08_sherd,t08_edge,delta_edge_vs_t03,delta_edge_vs_t08,wall_secs`. `juglet_e2e.tsv` (4 rows) has exact header `arm,cluster_len,cluster_seated,cluster_max_chamfer_mm,cluster_members_le_050,edges_strict,edges_of,p7_strict,floor_pass`. `comparison_vs_t08.tsv` (11 rows, vessels `A..J` + `JUGLET`) has exact header `vessel,mor_best,t03_own_raw_best,t08_own_dedup_best,t09_own_regen_best,reached_by,floor_pass,regression_vs_t03,regression_vs_t08,note`.
- [ ] `fixtures.tsv` has exact header `fixture,status,detail` (`PASS` on Spartan for `zero_dup_all_314`, `dedupe27_in_eq_out`, `juglet_native_3x_guard`, `manifest_schema_valid`). `renders.tsv` has exact header `figure,path,scale_bar_mm` (`scale_bar_mm = 20`) listing `renders/Pot_A_to_J_and_Juglet_t09_regen.png` (11 rows `MOR1` vs `K3R1` for `A..J` plus `Juglet` vs oracle, 20 mm bar in every panel). Inspect the PNG by eye.
- [ ] `jobs.tsv` has exact header `job_id,stage,vessel,state,exit_code` recording every submitted `t09-*` Slurm job (unioned against `sacct`) with terminal state/exit code (`check09.py --expect-terminal` passes after polling). `sfs_axes/own_surfaces.json` and `tests/test_own_surfaces_manifest.py` are written and `unittest` passes. Write `## Comments` / `### Write-back` with facts only, best-of-N across repeats (never median) with repeat counts, `[DEDUPE-27]` & `nn_med_mm`/`nn_p90_mm` spread summary, comparison vs `MOR`/`t03`/`t08`, budget used, one `**End state:**` line, per-requirement compliance table, and a separate read-only DeepSeek review checking tables and opening the PNG. Leave interpretation, commits, and closure to the lead.

Named checks: `python -m py_compile` on `.scratch/surface-parity/t09/{extract09,report09,check09}.py`, `bash -n` on `.scratch/surface-parity/t09/{build09.sbatch,regen09.sbatch,extract09.sbatch,launch_e2e09.sh}`, `python -m unittest tests/test_own_surfaces_manifest.py`, `check09.py --expect-terminal` on Spartan, and `git diff --check`.
