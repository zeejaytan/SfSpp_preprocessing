# 06: Test deduplicated Nov 5 and Ticket-09 regenerated surfaces in Pot E assembly

**What to build:** Test on all 31 Pot E sherds (`Pot_E_Piece_01`..`Pot_E_Piece_31`) in the unchanged Ticket 19 assembler whether (a) removing exact duplicate XYZ coordinates in memory from the Nov 5 `.S0`/`.S1` walls (`OWN_NOV5_DEDUP`) or (b) regenerating Pot E's `.S0`/`.S1` walls with current `main` (`OWN_MAIN_T09`, carrying the Ticket 09 `appendNewPoints` fix) recovers the 3 lost Pot E joins (out of 62) against the `AUTHOR` positive control and `OWN_NOV5` negative control.

**Answers:** E2

**Blocked by:** None. Surface Parity 05 is resolved on `main` and showed removing ~47% exact duplicate XYZ rows alone restores E28 `k=1 -> 2` and improves E27/E28 axes toward `AUTHOR`, and Ticket 09 (`ee6345c`) already landed the duplicate fix in `MeshPreprocessingHeadless` on `main` after the Nov 5 Pot E walls were generated.

**Status:** in-progress
**Working in:** DSH Surface Parity 06 (2026-11-25) (2026-11-25)
**Branch:** 06-test-dedup-and-t09-surfaces-in-pot-e-assembly, in /c/PR/worktrees/sfs/06
**Worker:** dsh-surface-parity-06


**Budget:** medium 5

**Hand-over:** DeepSeek V4.1 Flash via DSH Baton. Lead verification is outside the worker's worktree.

## Scope and frozen baselines

Changes are limited to this ticket (in worktree `C:/PR/worktrees/sfs/06`) and six new files under `.scratch/surface-parity/t06/`: `prep_and_axes06.sbatch`, `axes06.py`, `cell06.sbatch`, `posecheck06.sh`, `report06.py`, and `check06.py`.

Frozen baselines (read-only, never modify):
- **Axis estimator:** `/data/gpfs/projects/punim2657/SfSpp/runs/20261121-1319_2e951d9_t03-ship` (`SHIP`), TORA Python `/data/gpfs/projects/punim2657/TORA/envs/tora/bin/python3`, `SFS_IMPL=$SHIP/work/impl_t03`, `t03_lib.walls`, `t03_lib.draw_pool(C, seeds=10, step=10)`, `t03_extract.select_lines(..., 6, None)`, `t03_extract.write_lines`, `C = face 0 then face 1`.
- **Assembler and fixed Pot E tree:** Ticket 19 archived executable `$T19/work/t19/build/Hierarchy-T19` (`T19=/data/gpfs/projects/punim2657/SfSpp/runs/20261124-0443_21446b8_t19-decisions`, pinned `WANT_SHA=0ba6d10fa6885a67a92a92bb37ec7c138f25f32622368bfcafb5bfae3fa637c9`), container `$MAIN/sfs_pristine_assembly.sif` (`MAIN=/data/gpfs/projects/punim2657/sfs_main`), fixed `Breaklines`, `Surfaces`, `Mesh`, `Ground Truth` from `$T03E/trees/E_K3R1/E/MM` (`T03E=/data/gpfs/projects/punim2657/SfSpp/runs/20261121-1319_2e951d9_t03-potE`), piece list `$T03E/trees/E_K3R1/arm_pieces_E.tsv`, and pinned scorer `$T03E/work/score305.py`.
- **Preprocessing recipe for `OWN_MAIN_T09`:** `$CANON=/data/gpfs/projects/punim2657/sfs_preprocessing`, pinned commit `e91cf791` (fetch `origin` in `$CANON` first so `e91cf791` is present), container `$CANON/pcl_191_nurbs.sif`, `run_cell66.sh` archived from `9c5eec2`, `stage305.sh` copied read-only from `/data/gpfs/projects/punim2657/SfSpp/runs/20261105-0445_9c5eec2_t305-lane-e2/work/stage305.sh`, `SHIPPED="SFS_PAPER_CHAIN=1 SFS_PAPER_THETA=3.4 SFS_PAPER_KAPPA=1.0 SFS_PAPER_NB=10 SFS_SMOOTHNESS_DEG=3.4 SFS_CURVATURE_THRESH=1.0"` with `SFS_DEDUPE` unset/off, `_Mesh_DS.obj` symlink farm, and before/after corpus MD5 diff proving corpus inputs unchanged.

## Four arms and staging

Prepare four 31-file axis packs (`Pot_E_Piece_01_Axis.xyz`..`Pot_E_Piece_31_Axis.xyz`) on a Spartan compute node in `prep_and_axes06.sbatch`:

1. `AUTHOR`: byte-for-byte copy of `$T19/axes/AUTHOR`. Verify E27 (`k=2`, SHA-256 `f1607e000d563216aa8a3a962162ba3b7cfbddefa760b1a797e0d683e0732f8b`) and E28 (`k=2`, `212dcb15ae1291980c67bb3de4b9f01936e26c03a9de428c388a424c8c65ede5`).
2. `OWN_NOV5`: byte-for-byte copy of `$T19/axes/OWN` (from Nov 5 `20261105-0445_9c5eec2_t305-lane-e2/out/geom/`). Verify E27 (`k=3`, `d4236e9115f49b67872369d31fbd7953bd322513af49cfa9cbf30ce8074a4cc6`) and E28 (`k=1`, `12de83dc2cb91f525854347cc5cea6c34a11d5a65a3d274b91087b33d73d8acf`).
3. `OWN_NOV5_DEDUP`: load all 31 Nov 5 `.S0`/`.S1` wall pairs via `t03_lib.walls(stem, surfaces="own")`, remove exact duplicate float64 `(x, y, z)` rows per face keeping first occurrence in archive order (retaining exact 6-vectors verbatim, zero normal edits), verify `duplicate_xyz == 0` on all 62 walls, and extract 31 axis files with the frozen SHIP estimator (`seeds=10, step=10`, cap `6`, `tri=None`). Verify E27 (`k=2`, `a3e1694d3e291d85ed5d7b57b302c155f7f19a0218f25ac628c65cc24861a39d`) and E28 (`k=2`, `a5f49e5621bae8bd7cb74efcb30ab419dcf03099d0fd2e78f6a0b2e9b696aa7d`) match Ticket 05 byte-for-byte.
4. `OWN_MAIN_T09`: build `MeshPreprocessingHeadless` and `EdgeLineExtractionHeadless` from `e91cf791` inside `$CANON/pcl_191_nurbs.sif`, regenerate all 31 Pot E `.S0`/`.S1` walls on a compute node with the exact `t305-lane-e2` recipe, record `[DEDUPE-27]` log lines, verify `duplicate_xyz == 0` on all 62 regenerated walls, and extract 31 axis files with the same frozen SHIP estimator (`seeds=10, step=10`, cap `6`, `tri=None`). Note: do NOT bind the regenerated breaklines or surfaces into the assembler—ONLY `/Dataset/SfS_pp/Axes` changes across the four assembly arms.

## Assembly waves and gates

Run 8 cells total (2 repeats × 4 arms, 8 CPUs per cell via `cell06.sbatch`, same container mounts and `T18_TRACE`/`T19_TRACE` flags as Ticket 01):
- **Wave 1:** `AUTHOR 1`, `OWN_NOV5 1`, `OWN_NOV5_DEDUP 1`, `OWN_MAIN_T09 1`; poll all 4 to terminal states with `scripts/slurm_poll.sh` before submitting Wave 2.
- **Wave 2 (reverse order):** `OWN_MAIN_T09 2`, `OWN_NOV5_DEDUP 2`, `OWN_NOV5 2`, `AUTHOR 2`; poll all 4 to terminal states.
- **Per-cell completeness and provenance:** verify `WANT_SHA` before and after `Hierarchy-T19`, `: OK` from `sha256sum -c`, `inputs19.py` before/after manifest identity, `container_inputs.tsv` (`>= 187` Pot E entries), and `posecheck06.sh` requiring all 31 nonempty `T_<i>to_<i>.txt` pose exports before running `score305.py`. Record any incomplete cell (`usable=0`, missing piece IDs) without substituting.
- **Control separation gate:** interpret `OWN_NOV5_DEDUP` and `OWN_MAIN_T09` only if usable `AUTHOR` repeats score `62/62` joins and usable `OWN_NOV5` repeats miss join `27-28` (`< 62/62`). Report best-of-N across repeats (never median), along with how many repeats reached it.

## Evidence and acceptance

Fetch only short tables, check outputs, and the two PNGs into `artifacts/surface-parity-06/evidence/` (keep meshes, walls, traces, and pose matrices on Spartan). Leave `verdict` and `human_note` empty in Spartan `runs/index.tsv`.

- [ ] `walls.tsv` has 186 rows (31 sherds × 3 surface sets `OWN_NOV5`, `OWN_NOV5_DEDUP`, `OWN_MAIN_T09` × 2 faces) with exact header `sherd,surface_set,face,points,duplicate_xyz,xyz_sha256,normals_sha256,source_sha256`. Verify `duplicate_xyz == 0` on all 62 `OWN_NOV5_DEDUP` and all 62 `OWN_MAIN_T09` walls. Record `sources.tsv` (`kind,path,sha256,bytes,detail`) including `e91cf791` binary hashes, SHIP code hashes, and corpus MD5 proof.
- [ ] `axes.tsv` has 124 rows (31 sherds × 4 arms) with exact header `sherd,arm,status,k,axes_sha256,effective_stride,drawn_points,best_line_deg,best_anchor_mm,rank1_line_deg,rank1_anchor_mm`. Verify the four Ticket 19 pins (`AUTHOR`, `OWN_NOV5` on E27/E28) and the two Ticket 05 pins (`OWN_NOV5_DEDUP` on E27/E28).
- [ ] `cells.tsv` (8 rows) has exact header `arm,rep,job_id,status,usable,exported_poses,joins_pass,joins_total,pieces_pass,pieces_total,seam_13_28_pass,seam_27_28_pass,seam_28_31_pass,exe_sha_ok,inputs_unchanged,container_files,wall_secs`. `seams.tsv` (`62 * n_usable` rows) has exact header `arm,rep,join_i,join_j,ang_deg,t_mm,verdict`. `traces.tsv` (24 rows: 8 cells × 3 seams `13-28`, `27-28`, `28-31`) has exact header `arm,rep,seam,direct_queries,candidate_stretches,fits_ok,first_event_id`.
- [ ] `fixtures.tsv` has exact header `fixture,status,detail` and records `PASS` for all 4 named fixtures run on Spartan: `dedup_first_order`, `verbatim_6vec`, `author_zero_dup`, and `posecheck_completeness` (31/31 pass, 3-missing fail, empty-file fail).
- [ ] `renders.tsv` has exact header `figure,path,scale_bar_mm` (`scale_bar_mm = 20`) listing `renders/Pot_E_27_28_comparison.png` (27–28 placement across the 4 arms in locked view anchored on GT pose of sherd 27, 20 mm scale bar) and `renders/Pot_E_full_assembly.png` (full 31-sherd Pot E comparison across `AUTHOR`, `OWN_NOV5`, `OWN_NOV5_DEDUP`, `OWN_MAIN_T09` against reference, 20 mm scale bar). Inspect both PNGs by eye.
- [ ] `jobs.tsv` has exact header `job_id,stage,arm,rep,state,exit_code` recording every submitted Slurm job and its terminal `sacct` state/exit code (`check06.py --expect-terminal` passes after polling). Write `## Write-back` with facts only, best-of-N summary, `[DEDUPE-27]` summary, budget used, one end state, a per-requirement compliance table, and a separate read-only DeepSeek review that checks the tables and opens both figures. Leave interpretation, commits, and closure to the lead.

Named checks: `python -m py_compile` on `.scratch/surface-parity/t06/{axes06,report06,check06}.py`, `bash -n` on `.scratch/surface-parity/t06/{prep_and_axes06.sbatch,cell06.sbatch,posecheck06.sh}`, fixtures and `check06.py` on Spartan (plus `check06.py --expect-terminal` after polling), and `git diff --check`.
