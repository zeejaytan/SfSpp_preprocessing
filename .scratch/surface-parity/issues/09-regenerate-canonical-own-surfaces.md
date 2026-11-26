# 09: Regenerate canonical own surfaces across all 10 pots and def_3x Juglet

**What to build:** Build `MeshPreprocessingHeadless`, `EdgeLineExtractionHeadless`, and `SurfaceDedupeTest` from pinned post-Ticket-09 `main` (`a50f8cc0ebe17621e2ce32424808c7414c2d7bbf`), regenerate all 148 own-surface pot pieces (`Pot A..J`) and 9 `def_3x` Juglet pieces (`157` pieces, `314` walls + `314` breaklines) into ONE canonical Spartan run directory (`t09-own-surfaces`), validate the regenerated walls through frozen `SHIP` axis extraction and the full 10-pot + `def_3x` Juglet E2E assembly suite against `MOR1/2`, `t03`, and `t08`, and write the canonical own-surface pointer manifest `sfs_axes/own_surfaces.json` with a schema test `tests/test_own_surfaces_manifest.py`.

**Answers:** E2

**Blocked by:** None. Surface Parity 08 validated deduplicating own surfaces across all 10 pots and the `def_3x` Juglet with zero assembly regressions (`31/31 62/62` on Pot E, `+5` edges on Pot J, `9/9 <= 0.465 mm` on Juglet), and Axis-parity Ticket 09 (`ee6345c`) already fixed duplicate point emission in `mesh_processing_headless.cpp`. Ticket number `09` uses free worktree `C:/PR/worktrees/sfs/09`.

**Status:** resolved
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

- [x] `sources.tsv` (`kind,path,sha256,bytes,detail`) includes SHA-256 hashes of all 7 `t09/` scripts, both built binaries, `SurfaceDedupeTest` log, frozen `SHIP` code, and before/after corpus MD5 proof.
- [x] `dedupe27.tsv` (314 rows) has exact header `stem,pot,face,mode,in_rows,out_rows,improved_rows,dups_skipped,appended,normal_maxdiff` with `mode == "off"`, `in_rows == out_rows > 0`, and `0 <= normal_maxdiff <= 1e-6` on all 314 rows. `walls.tsv` (314 rows) has exact header `stem,pot,face,points,duplicate_xyz,bl_points,nn_med_mm_vs_t08,nn_p90_mm_vs_t08,xyz_sha256,normals_sha256` with `duplicate_xyz == 0` and `bl_points > 0` on all 314 rows.
- [x] `axes.tsv` (157 rows) has exact header `stem,pot,in_141_gt,excluded_by_paper,k_t08,k_t09,axes_sha256_t09,effective_stride,drawn_points,rank1_deg_t08,rank1_deg_t09,best_deg_t08,best_deg_t09,d_gt_to_est_mm_t09,d_est_to_gt_mm_t09,is_base_t09` with 141 GT rows, 5 paper-excluded pieces flagged, and `Juglet_Piece_7` sole `is_base_t09=1`.
- [x] `pots_e2e.tsv` (40 rows: 10 pots × 4 arms `<P>_MOR1/2, <P>_K3R1/2`) has exact header `pot,arm,sherd,sherd_den,edge,edge_den,sherd_floor,edge_floor,floor_pass,t03_sherd,t03_edge,t08_sherd,t08_edge,delta_edge_vs_t03,delta_edge_vs_t08,wall_secs`. `juglet_e2e.tsv` (4 rows) has exact header `arm,cluster_len,cluster_seated,cluster_max_chamfer_mm,cluster_members_le_050,edges_strict,edges_of,p7_strict,floor_pass`. `comparison_vs_t08.tsv` (11 rows, vessels `A..J` + `JUGLET`) has exact header `vessel,mor_best,t03_own_raw_best,t08_own_dedup_best,t09_own_regen_best,reached_by,floor_pass,regression_vs_t03,regression_vs_t08,note`.
- [x] `fixtures.tsv` has exact header `fixture,status,detail` (`PASS` on Spartan for `zero_dup_all_314`, `dedupe27_in_eq_out`, `juglet_native_3x_guard`, `manifest_schema_valid`). `renders.tsv` has exact header `figure,path,scale_bar_mm` (`scale_bar_mm = 20`) listing `renders/Pot_A_to_J_and_Juglet_t09_regen.png` (11 rows `MOR1` vs `K3R1` for `A..J` plus `Juglet` vs oracle, 20 mm bar in every panel). Inspect the PNG by eye.
- [x] `jobs.tsv` has exact header `job_id,stage,vessel,state,exit_code` recording every submitted `t09-*` Slurm job (unioned against `sacct`) with terminal state/exit code (`check09.py --expect-terminal` passes after polling). `sfs_axes/own_surfaces.json` and `tests/test_own_surfaces_manifest.py` are written and `unittest` passes. Write `## Comments` / `### Write-back` with facts only, best-of-N across repeats (never median) with repeat counts, `[DEDUPE-27]` & `nn_med_mm`/`nn_p90_mm` spread summary, comparison vs `MOR`/`t03`/`t08`, budget used, one `**End state:**` line, per-requirement compliance table, and a separate read-only DeepSeek review checking tables and opening the PNG. Leave interpretation, commits, and closure to the lead.

Named checks: `python -m py_compile` on `.scratch/surface-parity/t09/{extract09,report09,check09}.py`, `bash -n` on `.scratch/surface-parity/t09/{build09.sbatch,regen09.sbatch,extract09.sbatch,launch_e2e09.sh}`, `python -m unittest tests/test_own_surfaces_manifest.py`, `check09.py --expect-terminal` on Spartan, and `git diff --check`.

## Comments

### Write-back

**End state:** one canonical Spartan run, `20261125-1340_a50f8cc_t09-own-surfaces`, holds 157 regenerated own-surface pieces (628 geom files = 314 walls + 314 breaklines) and 157 axes extracted by the frozen `SHIP` code; the wall invariants are green (`duplicate_xyz = 0` on 314/314, 314/314 `[DEDUPE-27]` `mode=off` with `in == out` and `normal_maxdiff = 0`), 9 of 10 pots reproduce Ticket 08's deduplicated E2E result exactly, Pot J's two `K3` arms regress (best 7/21 edges against t08's 10/21, floor 16/21), and the `def_3x` Juglet seats 9/9 at a best-of-4 max chamfer of 0.456 mm; `sfs_axes/own_surfaces.json` and a 12-test schema test are written; nothing is committed and no verdict is set.

#### Stage 1 — build (job 35713682, COMPLETED 0:0, 2 m 23 s)

- Run dir `/data/gpfs/projects/punim2657/SfSpp/runs/20261125-1340_a50f8cc_t09-own-surfaces`; commit `a50f8cc0ebe17621e2ce32424808c7414c2d7bbf` (fetch ok; `logs/build_step1.txt` records `%H`).
- Binaries (`binaries.sha256`): `MeshPreprocessingHeadless e80f8d0d41daec9925dcbe9c504e7bb1a004ef44997498597034a159ae3f0658`, `EdgeLineExtractionHeadless 0e973ba493b35eba633c784544acf6168160549222828f315191b59b4282767a`, `SurfaceDedupeTest 6e1c12dc8054080e72c9537fe2bdd959de3e8c43b7fee7992064c67151743477`.
- `logs/unit_test.txt`: `CASE U1..U5 PASS`, last line `[SURFACE-DEDUPE-09] cases=5 pass=5 fail=0`.
- Before-corpus MD5: `logs/corpus_inputs_before.md5` 907 files; `logs/t331_inputs_before.md5` 18 files (9 `cloud_mesh/*.pcd`, 9 `mesh_large/*.obj`).
- Stagers (`logs/stagers.sha256`): `stage305.sh 17360979…`, `stage_synth_t73.sh 5b1b2b9f…`, `run_cell66.sh 2020c554…` (from `build/src` at the pinned commit).

#### Stage 2 — regeneration (`--array=0-10`)

- First submission 35713837 FAILED 8:0: its `env` line passed the piece list as one unquoted string, so `env` exec'd `Pot_A_Piece_02` (cell rc 127). Fixed by writing one explicit `env …` line per branch with every value quoted (same script, `446f0f45…`).
- 35713969 (tasks 0–4, 6, 7, 10) and retry 35714095 (tasks 5, 8, 9, after the per-pot manifest fix) both COMPLETED 0:0. The retry was needed because the frozen `t305` derived-manifest awk, `index($1,"Pot_" pot "_")==1` with `pot="Pot_<P>"`, builds the pattern `Pot_Pot_<P>_` and is a silent no-op — so the five paper-excluded pieces never entered `pins/MANIFEST_<P>.tsv` and `run_cell66.sh`'s corpus gate exited 9. Correct form `index($1, pot "_")==1`. Corpus: `MANIFEST_released.tsv` 143 rows + `MANIFEST_derived.tsv` 5 rows = 148, no overlap.
- Geom files per vessel (4 per piece): A 32, B 36, C 16, D 116, E 124, F 28, G 28, H 44, I 120, J 48, Juglet_def3x 36 → 628 = 157 × 4. Every piece has non-empty `.S0 .S1 .Bl0 .Bl1` (`logs/regen_<vessel>.txt`: `cell_rc=0`, `geom_missing_or_empty=0`).
- `[DEDUPE-27]` lines: 16/18/8/58/62/14/14/22/60/24/18 per vessel = 314, all `mode=off`, all `in == out`, `normal_maxdiff = 0.000e+00` (`dedupe27.tsv`, 314 rows).

#### Stage 3 — axes and gated E2E

- `extract09.sbatch` 35716587 COMPLETED 0:0, 10 m 52 s (two earlier attempts CANCELLED after `t03_extract.job` called `dl.gt_axis` on stems with no reference line). Final script decides by file existence: 7 of the 148 pot stems have no `Ground Truth Axes` file — `Pot_D_Piece_22`, `Pot_F_Piece_06`, `Pot_F_Piece_07`, `Pot_I_Piece_28/29/30`, `Pot_J_Piece_09` (`Pot_F_Piece_07`, `Pot_I_28/29/30`, `Pot_J_12` are the paper-excluded five; `Pot_J_12` does have a GT file, so the paper flag and the GT presence are different sets). 148 − 7 = 141 GT rows, matching the ticket.
- `walls.tsv` 314 rows, `duplicate_xyz = 0` on all, `bl_points > 0` on all. `walls_nn_detail.tsv`: nearest-neighbour spread against Ticket 08's deduplicated walls, median |Δ| = 0.0 mm, max |Δ `nn_med`| = 0.02756 mm, max |Δ `nn_p90`| = 0.03349 mm (worst |Δ `nn_med`| `Pot_D_Piece_28`, worst |Δ `nn_p90`| `Pot_J_Piece_08`) — the `SFS_WALL_PAIR_FILTER` drop leaves the same point geometry as the deduplicated walls, with a fresh unseeded draw on top.
- Axes: `out/axes09_own_regen` 148 `*_Axis.xyz`, `out/axes09_juglet_def3x_regen` 9, written native (`Juglet_Piece_1` first row `550.211 427.223 −377.342`, |pos| = 550.2 tree units, un-divided). `Juglet_Piece_7` is the only Juglet piece with `is_base_t09 = 1` (seven pot pieces legitimately carry it too).
- Median `rank1_deg` per pot, t08 dedup → t09 regen (n = GT pieces): A 2.546→2.553 (8), B 4.943→4.881 (9), C 2.464→2.460 (4), D 1.872→1.877 (28), E 3.595→3.591 (31), F 4.294→4.278 (5), G 2.057→2.057 (7), H 1.131→1.126 (11), I 2.729→2.729 (27), J 23.454→22.985 (11); J's `best_deg` median 7.714→6.822. `axes.tsv` 157 rows, 141 GT, 5 paper-excluded flagged, and the `Pot C 01` / `Pot J 01` interior-gap, `Pot D 18/29` axis (`rank1` 15.83° and 77.84°) and `Pot J 09` caveats are carried in `comparison_vs_t08.tsv` notes and `logs/extract09_summary.json` `caveats`.
- After-corpus MD5 byte-identical to before (`sources.tsv`: "identical to after: yes"), ticket-331 inputs unchanged.
- E2E stage 3A (`20261125-1451`): E 35717306 1:20:41, G 35717307 18:54, D 35717308 2:17:22, J 35717309 1:36:24, Juglet 35717310 (4 tasks) + jugsum 35717311 — all COMPLETED 0:0. Stage 3B (`20261125-1725`): A 35724430, B 35724431, C 35724432, F 35724433, H 35724434, I 35724435 — all COMPLETED 0:0.

- Make-script swap verified by diff: `make_t09_e2e.sh` differs from the frozen `make_t03_e2e.sh` only in the header comment, `GIT7=a50f8cc`, `AX03=<RUN>/out/axes09_own_regen`, the `t09-pot<P>` run-dir tag, the job-name/comment sed and the axes echo; `make_t09_juglet.sh` likewise swaps `OWN` to `<RUN>/out/axes09_juglet_def3x_regen`. The `K3` arms really carried the regenerated axes: `..._t09-potA/work/axes_k3/Pot_A_Piece_01_Axis.xyz` line 1 is byte-identical (`cmp`) to `out/axes09_own_regen/Pot_A_Piece_01_Axis.xyz` line 1.

**Per-pot E2E, best-of-N (t09 `K3R1/K3R2` = 2 repeats; `MOR` = the authors' control, best of 2). `wall_secs` is the arm's own `wall_s` from its run's `logs/panel.tsv` — the seconds that arm actually spent in the panel (`A_MOR1 193.0`, `D_K3R2 8192.0`, `E_K3R1 4798.0`), not a queue-inclusive wall time. `score/acc.tsv` `time_s` is not usable for this column: it is blank for both `MO` arms and inconsistent for the `K3` arms (Pot E `K3R1 12708` vs `K3R2 1.16`), so the reporter only falls back to it when `panel.tsv` is missing:**

| pot | MOR best | t09 K3 best | t08 K3 best | t03 K3 best | floor (sherd/edge) | floor met |
|---|---|---|---|---|---|---|
| A | 8/8 15/15 | 8/8 15/15 | 8/8 15/15 | 8/8 15/15 | 8/8 15/15 | yes |
| B | 9/9 15/15 | 9/9 15/15 | 9/9 15/15 | 9/9 15/15 | 9/9 15/15 | yes |
| C | 4/4 5/5 | 4/4 5/5 | 4/4 5/5 | 4/4 5/5 | 4/4 5/5 | yes |
| D | 23/28 55/69 | 24/28 58/69 | 24/28 58/69 | 24/28 58/69 | 23/28 55/69 | yes |
| E | 31/31 62/62 | 31/31 62/62 | 31/31 62/62 | 30/31 59/62 | 31/31 62/62 | yes |
| F | 5/5 7/7 | 5/5 7/7 | 5/5 7/7 | 5/5 7/7 | 5/5 7/7 | yes |
| G | 7/7 10/10 | 7/7 10/10 | 7/7 10/10 | 7/7 10/10 | 7/7 10/10 | yes |
| H | 8/11 9/17 | 11/11 17/17 | 11/11 17/17 | 11/11 17/17 | 11/11 17/17 | yes |
| I | 25/26 59/62 | 26/26 62/62 | 26/26 62/62 | 26/26 62/62 | 25/26 59/62 | yes |
| J | 8/11 16/21 | 8/11 7/21 | 8/11 10/21 | 8/11 5/21 | 8/11 16/21 | **no** (edges) |

- J detail, all four arms: `MOR1 8/11 16/21`, `MOR2 8/11 16/21`, `K3R1 8/11 7/21`, `K3R2 6/11 5/21` (t08: `8/11 16/21`, `8/11 16/21`, `7/11 9/21`, `8/11 10/21`). The MO control reproduces t08 exactly, so the assembler is unchanged; only the regenerated axes move, and on J they cost edges. `comparison_vs_t08.tsv` records `floor_pass = 0` and `regression_vs_t08 = regressed` for J alone.
- Juglet, 4 repeats (`juglet_own_xy_r1..r4`): `cluster_len 9`, `cluster_seated 9/9`, `cluster_members_le_050 9/9`, max chamfer 0.473 / 0.468 / 0.459 / **0.456** mm (limit 0.50), strict edges 2 / 3 / 1 / 3 of 36, `p7_strict 0`, per-piece seated 0/9 in every repeat. t08 0.468 / 0.475 / 0.468 / 0.465 with strict edges 3 / 5 / 3 / 4; t03 0.472 / 0.472 / 0.471 / 0.477 with 2 / 3 / 3 / 4. Best-of-4 chamfer is the lowest of the three; best strict edges (3/36) is below t08's 5/36.

#### Stage 4 — manifest and test

- `sfs_axes/own_surfaces.json`: `run_id 20261125-1340_a50f8cc_t09-own-surfaces`, `run_root` = the run dir, `preprocessing_commit a50f8cc0…`, both binary hashes, `sfs_dedupe "off"`, `sfs_wall_pair_filter "default_on"`, `total_pieces 157`, `total_walls 314`, `duplicate_xyz 0`, `vessels` = 11 keys (`A..J` + `JUGLET_DEF3X`, counts 8/9/4/29/31/7/7/11/30/12/9, `units_per_mm` 1.0 for pots and 3.0 for the Juglet), `axes_own_regen`, `axes_juglet_def3x_regen`. Verified on Spartan: every `geom_dir` exists with 4 files per piece, axes dirs hold 148 and 9 files, no path outside `run_root`, no `t305-lane`/`t66-admitsign`/`t80-default-on`/`out_poth` reference.
- `tests/test_own_surfaces_manifest.py`: 12 stdlib `unittest` tests, `Ran 12 tests … OK` (schema, 11 vessels, counts sum 157, `duplicate_xyz == 0`, 40-hex commit, 64-hex hashes, 13 paths under `run_root` containing `_t09-own-surfaces`, no stale substring, `units_per_mm`).

#### Evidence, checks and budget

- `evidence/`: `dedupe27.tsv` 314, `walls.tsv` 314, `walls_nn_detail.tsv` 314 (companion), `axes.tsv` 157, `fixtures.tsv` 4 PASS, `pots_e2e.tsv` 40, `juglet_e2e.tsv` 4, `comparison_vs_t08.tsv` 11, `jobs.tsv` 44, `renders.tsv` + `renders/Pot_A_to_J_and_Juglet_t09_regen.png` (974 272 B), `sources.tsv` 43 rows (all 7 ticket scripts, both binaries, `unit_test.txt`, three frozen `SHIP` files, before/after corpus and ticket-331 hashes, every table and the PNG), `check09.txt`.
- `check09.py --expect-terminal`: 36 checks, 0 failed, exit 0 (`dedupe27` 314/314 off and `in == out`, `zero_dup_all_314`, `juglet_piece1_native_3x` |pos| = 550.2, papers 5 excluded, `sources_seven_scripts`, `sources_corpus_identical`, `pots_e2e` 40 rows, `pots_wall_secs_vs_panel` 40/40, `jobs_all_terminal` empty).
- `jobs.tsv`: 44 rows for 19 submissions (the four array submissions are expanded into their 29 task rows, because a parent can read COMPLETED while individual tasks failed); every row a terminal `sacct` state — 14 FAILED task rows (all 11 of the superseded 35713837 and tasks 5/8/9 of 35713969, each 8:0), 2 CANCELLED (the superseded extract attempts), 28 COMPLETED 0:0.
- Superseded-attempt housekeeping: the 11 `RUN-FAILED-regen-<task>.txt` markers the first regen attempt left in the run root were moved to `logs/superseded/` with a `logs/superseded/INDEX.md` that names the class kept, the source job (35713837), the reason, and the sha256 of every file before and after the move; nothing was deleted. The 824-line `logs/regen_missing.txt` written by the failed attempts was moved in the same way and recorded in the same `INDEX.md`; the final state has 628/628 geom files present and 0 empty.
- `check09.py` also cross-checks the delivered E2E wall times: `pots_wall_secs_vs_panel` re-reads each stage's `logs/panel.tsv` and requires all 40 `wall_secs` values to equal that arm's `wall_s` within 0.6 s (40/40 match). This was added after the read-only review noted the column had no check of its own.
- Render inspected by eye (1700×4400, 11 rows × 2 panels, 20 mm bar in every panel, left `MOR1` control vs right `K3R1` regenerated; titles agree with `acc.tsv`; every vessel reads as a coherent pot, D dense, J visibly the weakest in the `K3` panel; no collapse or mirroring).
- Budget: 19 `sbatch` submissions (1 build, 3 regen array submissions totalling 25 array tasks — 11 + 11 + 3, 3 extract submissions, 12 E2E jobs: 4 pots + `juglet` + `jugsum` in Stage 3A and 6 pots in Stage 3B); longest single job 2 h 17 m (Pot D); two failed/superseded chains cost 3 submissions (Stage 2 first attempt, two extract attempts).
- Laptop checks: `py_compile` clean on all three `.py`, `bash -n` clean on all four shell scripts, `unittest` 12/12, `git diff --check` clean (a trailing blank line the read-only review flagged at `:166` was removed), `git status` shows only `.scratch/surface-parity/t09/`, `sfs_axes/own_surfaces.json`, `tests/test_own_surfaces_manifest.py`, no `__pycache__` (built with `PYTHONPYCACHEPREFIX`), nothing committed.
- Final script hashes (`work/t09`, identical to the worktree copies): `build09.sbatch cab645e1…`, `regen09.sbatch 446f0f45…`, `extract09.py 9b9a3b3c…`, `extract09.sbatch a3c9d1c6…`, `launch_e2e09.sh 60ffcf54…`, `report09.py 0a5980fc…`, `check09.py c0253dd4…`.

#### Compliance

| Requirement | Status | Where it can be re-read |
|---|---|---|
| Seven new files under `.scratch/surface-parity/t09/` only, plus the manifest and the test; no tracked source, template or archived run touched | met | `git status --porcelain` shows exactly the three paths; `git diff --check` clean |
| Build the three targets from `a50f8cc…` inside the SIF, keep `build.log`, write `binaries.sha256` | met | `logs/build.log`, `binaries.sha256`, `run.json`, `logs/fetch/build_step1.txt` |
| `SurfaceDedupeTest` exits 0 with every `CASE … PASS` | met | `logs/unit_test.txt` (`cases=5 pass=5 fail=0`) |
| 157 pieces regenerated into one canonical run dir, 314 walls + 314 breaklines, all non-empty | met | `out/Pot_*/geom`, `out/Juglet_def3x/geom`, `logs/regen_*.txt` |
| `[DEDUPE-27]` `mode=off`, `in == out`, `0 <= normal_maxdiff <= 1e-6` on all 314 | met | `evidence/dedupe27.tsv` (max `normal_maxdiff` 0) |
| `duplicate_xyz == 0` on all 314 walls, `nn_med`/`nn_p90` spread vs t08 | met | `evidence/walls.tsv`, `evidence/walls_nn_detail.tsv` (median Δ 0.0 mm, max 0.0276 / 0.0335 mm) |
| Frozen `SHIP` axes to the two regen dirs, Juglet native 3x, `Juglet_Piece_1` abs(position) > 300 tree units, `Piece_7` sole Juglet base | met | `out/axes09_own_regen` (148), `out/axes09_juglet_def3x_regen` (9), `check09` `juglet_piece1_native_3x` = 550.2 |
| 141 GT rows, 5 paper-excluded flagged, `Pot C 01`/`J 01` and `Pot D 18/29` caveats noted | met | `evidence/axes.tsv` (157 rows, 141 GT, 5 flagged), `evidence/comparison_vs_t08.tsv` notes |
| Corpus MD5 before == after | met | `evidence/sources.tsv` corpus rows ("identical to after: yes"), `logs/corpus_inputs_after.md5` |
| Gated E2E 3A then 3B, only `AX_318`/`OWN` swapped, 4 arms per pot, 4 juglet repeats + `jugsum`, every job polled to terminal | met | `jobs.tsv` 44 rows all terminal, `evidence/pots_e2e.tsv` 40 rows, `evidence/juglet_e2e.tsv` 4 rows |
| Every pot's own-code arm meets its floor | met for A–I; **not met for J on edges** (8/11 7/21 vs floor 8/11 16/21) | `evidence/comparison_vs_t08.tsv` row J (`floor_pass = 0`, `regression_vs_t08 = regressed`) |
| Manifest with the required keys, all paths under `run_root`, no stale run reference | met | `sfs_axes/own_surfaces.json`, `check09` `manifest_*` 3 checks |
| Schema test passes | met | `python -m unittest tests/test_own_surfaces_manifest.py` → 12 tests OK |
| `sources.tsv` carries the 7 scripts, both binaries, the unit-test log, frozen `SHIP` code and the before/after corpus proof | met | `evidence/sources.tsv` 43 rows, `check09` `sources_*` 5 checks |
| `renders.tsv` with `scale_bar_mm = 20`, PNG inspected by eye | met | `evidence/renders.tsv`, `evidence/renders/Pot_A_to_J_and_Juglet_t09_regen.png` |
| `jobs.tsv` with `check09.py --expect-terminal` passing | met | `evidence/jobs.tsv` (44 rows, array tasks expanded), `check09` `jobs_all_terminal` / `jobs_completed_exit_zero` empty, `jobs_failed_tasks_recorded` PASS |
| Leave `verdict` and `human_note` blank in Spartan `runs/index.tsv`; no commit | met | rows appended for every submission with two empty trailing fields; worktree uncommitted |
| Named checks (`py_compile`, `bash -n`, `unittest`, `check09 --expect-terminal`, `git diff --check`) | met | all clean; `check09` 36 checks 0 failed |

Facts a reviewer may want beside the J result: J is the pot with the worst own-surface axes in both runs (`rank1` median 22.99°, `best_deg` 6.82° in t09; 23.45° / 7.71° in t08), its `MOR` control is identical to t08 to the join, and its `K3` arms were already the weakest in t03 (5/21). No interpretation of that is offered here.
### Read-only review (t09-review)

A separate read-only reviewer (spawned by the worker; it wrote nothing, submitted nothing, committed nothing) re-derived the tables from the files, reconciled `pots_e2e.tsv` cell by cell against every `score/acc.tsv`, recomputed the `dedupe27`/`walls`/`axes` invariants, checked the Spartan directories and `sacct`, and opened the PNG. Its verdict was **5 requirements not met**; four were worker-side defects and one is the Pot J result. Each defect and what was done:

| Review finding | Status after the fix |
|---|---|
| The fetched `sources.tsv` (35 rows) and `check09.txt` (28 checks) were stale copies of an earlier run, not the current ones | fixed: evidence re-fetched; all 12 files now hash-identical to `RUN/evidence`, checked per file |
| The fetched `sources.tsv` listed the two generated make-scripts instead of `build09.sbatch` and `regen09.sbatch`, and had no `unit_test` or `ship_code` rows | fixed before the re-fetch: `sources.tsv` now lists all seven ticket scripts, `unit_test.txt` and three frozen `SHIP` files (43 rows); `check09` gained `sources_seven_scripts`, `sources_ship_code`, `sources_unit_test`, `sources_corpus_identical`, `sources_no_missing` |
| `git diff --check` failed with `09-…md:166: new blank line at EOF` | fixed: trailing blank line removed, `git diff --check` exits 0 |
| `jobs.tsv` recorded `35713969 COMPLETED 0:0` while `sacct` shows its tasks 5/8/9 FAILED 8:0 — a parent state hiding failed tasks | fixed: `report09.jobs()` expands array submissions into per-task rows via a new `sacct_tasks(jid)` (`.batch` step rows excluded); `jobs.tsv` now 44 rows for 19 submissions with the three failures visible; `check09` gained `jobs_array_tasks_expanded` and `jobs_failed_tasks_recorded` |
| `pots_e2e.tsv` `wall_secs` carried per-arm panel wall seconds (e.g. `193.0`) with no stated definition, so it could not be checked | fixed: the column is confirmed as the arm's `logs/panel.tsv` `wall_s` and the write-back now names the definition; a first attempt to switch it to `score/acc.tsv` `time_s` was reverted because that field is blank for the `MO` arms and inconsistent for the `K3` arms (Pot E `K3R1 12708` vs `K3R2 1.16 s`), which would have made the column uninterpretable |
| Pot J: `K3` edges `8/11 7/21` against t08 `8/11 10/21`, floor `8/11 16/21` | not fixed — it is the measured result; recorded as `floor_pass = 0`, `regression_vs_t08 = regressed` in `comparison_vs_t08.tsv` |

The reviewer independently re-read and confirmed: 628 geom files with none empty and no zero-size file, `dedupe27` 314/314 `mode=off` with `in==out` and `max = min = 0` `normal_maxdiff`, `walls` 314 rows with no duplicate xyz and `bl_points > 0`, spot-checked PLY vertex counts (A 01 S0 33 985 verts / 33 986 unique, J 12 S1 2 590 / 2 591, Juglet 7 S0 22 809 / 22 810), 141 GT rows, the five excluded stems, `Juglet_Piece_7` as the sole Juglet base, `Juglet_Piece_1` at 550.2 native units, corpus md5 identical before/after, all 40 `pots_e2e` rows matching their `acc.tsv`, all 4 `juglet_e2e` rows matching `summary.tsv`, the manifest schema, 12/12 unit tests, and the PNG's 11 rows × 2 panels × 20 mm bar with titles matching `acc.tsv`. Its eye reading matched the worker's, with the same limit: at the delivered resolution individual seams are not resolvable, so "no broken geometry" is a whole-panel statement, not a seam-level one.

Two residual notes from the re-check, both closed: the ticket's `wall_secs` illustration named the value without its arm (it now reads `A_MOR1 193.0`, `D_K3R2 8192.0`, `E_K3R1 4798.0`), and the delivered `wall_secs` column had no check of its own — `check09.py` gained `pots_wall_secs_vs_panel`, which re-reads each stage's `logs/panel.tsv` and requires all 40 values to match that arm's `wall_s` (40/40 match, 36 checks total, 0 failed).

### Lead verification and closure (2026-11-26)

- `verified: evidence/check09.txt -> 36/36 PASS (0 FAIL), including --expect-terminal, pots_wall_secs_vs_panel 40/40, jobs_array_tasks_expanded 29/4`
- `verified: lead independent check of accept.py assertions -> 314 dedupe27 rows (4,475,469 dups skipped at emission, 314/314 mode=off, in==out, normal_maxdiff=0), 314 walls (0 duplicate_xyz, bl_points>0, walls.tsv nn_med_mm_vs_t08 max=0.3692 mm, nn_p90_mm_vs_t08 max=0.5921 mm), 157 axes (141 GT, 5 paper-excluded flagged, Juglet_Piece_7 sole base), 40 pot E2E arms, 4 juglet arms, 44 terminal sacct job rows, 12/12 unittest tests/test_own_surfaces_manifest.py OK` (Note: worker staged fetched evidence under `C:/PR/artifacts/surface-parity-09/evidence/` rather than inside `worktrees/sfs/09`, and `sources.tsv` records `binaries.sha256` file hash `abf2f644...` rather than separate binary rows; verified `ssh spartan binaries.sha256` directly below.)
- `verified: ssh spartan binaries.sha256 + sacct + runs/index.tsv -> binaries.sha256 sha256 abf2f644... matches sources.tsv row 11, binary hashes match sfs_axes/own_surfaces.json byte-for-byte; all active build/regen/extract/E2E jobs COMPLETED 0:0; runs/index.tsv rows present with blank verdict/human_note prior to lead verdicting`
- `verified: visual inspection of artifacts/surface-parity-09/evidence/renders/Pot_A_to_J_and_Juglet_t09_regen.png -> 11 rows x 2 columns (974,272 bytes), 20 mm scale bar visible in all 22 panels; Pot A..I MOR1 vs K3R1 and Juglet own r1 vs oracle coherent and matching scored counts; Pot J K3R1 visibly sparser`
- **Scope isolation:** `accept.py` `snapshots()` matched `other-worktrees.json` with 0 diffs across all other worktrees; `sfs/09` `git status --porcelain` matched the exact allowed set (`09-regenerate-canonical-own-surfaces.md`, `sfs_axes/own_surfaces.json`, `tests/test_own_surfaces_manifest.py`, and the 7 `.scratch/surface-parity/t09/` scripts).
- **DSH cost:** opencode-go flat-rate (`session-83d4ed2c-6802-4b1e-b4c1-7824f9e4fac8`, `hrun-mww5vb9s-2bc49f`, single send completed cleanly).
- **Lead cost:** Antigravity hidden acceptance check verification, Spartan binary/`sacct` spot-checks, render inspection, `AGENTS.md`/`intent/E2` updates, and closure.
