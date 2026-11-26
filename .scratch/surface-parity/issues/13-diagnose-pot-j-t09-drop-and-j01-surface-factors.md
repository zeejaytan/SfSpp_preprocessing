# 13: Diagnose Pot J t09 drop (7/21 vs t08 10/21) and J01 surface factors (vs 16/21)

**What to build:** Two-part Pot J diagnostic using one pinned `Hierarchy-T13` executable and frozen `SHIP` selector: (Part A) measure 4-repeat variance of `T08_ALL` vs `T09_ALL` plus single-sherd swaps (`J01, J02, J05, J06, J11`) from `t08` into `T09_ALL` to isolate why `t09` dropped from `10/21` to `7/21` (since `t09` `WALLPAIR` logs already proved `add_refused=0` on `J01..J08, J10`); (Part B) run a 9-arm single-factor surface transfer on `Pot_J_Piece_01` (`OWN_T09` vs `AUTHOR`: wall normals, 1 mm shared coverage, common 1 mm voxels, S0:S1 balance) and test `T09_WITH_AUTHOR_J01` plus any recovering `J01` factor arm in `Hierarchy-T13` to identify what prevents Pot J from reaching `16–17/21`.

**Answers:** E2

**Blocked by:** None. Surface Parity 09 regenerated the canonical own surfaces (`20261125-1340_a50f8cc_t09-own-surfaces`); read-only inspection ruled out `SFS_WALL_PAIR_FILTER` on `J01..J08, J10` (`add_refused=0`) and showed `J06` detached from `{2, 4}` while `J05` missed `2-5` at `50.69 mm`; Axis-parity 13–16 already proved `J01` slot 2 unlocks `17/21` and ruled out the 4 mm interior hole rim. Ticket number `13` uses free worktree `C:/PR/worktrees/sfs/13` (skipping occupied `sfs/10..12`).

**Status:** in-progress
**Working in:** C:/PR/worktrees/sfs/13 (2026-11-26)
**Branch:** 13-diagnose-pot-j-t09-drop-and-j01-surface-factors, in /c/PR/worktrees/sfs/13
**Worker:** DeepSeek V4.1 Flash (DSH Baton)


**Budget:** large 8

**Hand-over:** DeepSeek V4.1 Flash via DSH Baton. Lead verification is outside the worker's worktree.

## Scope and frozen baselines

Changes are limited to `C:/PR/worktrees/sfs/13`: this ticket file (write-back) and six new files under `.scratch/surface-parity/t13/`: `j01_factors13.py`, `prep13.sbatch`, `cell13.sbatch`, `posecheck13.sh`, `report13.py`, and `check13.py`. Do NOT modify any tracked source, manifest, frozen input, corpus, archived run, estimator, or executable.

Frozen baselines (read-only):
- **Pinned Pot J assembler executable and container:** `/data/gpfs/projects/punim2657/SfSpp/runs/20261122-1612_651fee0_t13-j01-recip/work/build/Hierarchy-T13`, pinned `WANT_SHA=de44ffc23c8db5208bd5f6f9c9f57d819bed7805f0330526bcb2750487bfd727`, container `/data/gpfs/projects/punim2657/sfs_main/sfs_pristine_assembly.sif`, Apptainer `/apps/easybuild-2022/easybuild/software/Compiler/GCCcore/11.3.0/Apptainer/1.3.3/bin/apptainer`, TORA Python `/data/gpfs/projects/punim2657/TORA/envs/tora/bin/python3`.
- **Fixed Pot J non-axis tree (`Breaklines`, `Surfaces`, `Mesh`, `Ground Truth`):** `/data/gpfs/projects/punim2657/SfSpp/runs/20261125-1451_a50f8cc_t09-potJ/trees/J_K3R1/J/MM`, piece list `/data/gpfs/projects/punim2657/SfSpp/runs/20261125-1451_a50f8cc_t09-potJ/trees/J_K3R1/arm_pieces_J.tsv`, scorer `/data/gpfs/projects/punim2657/SfSpp/runs/20261125-1451_a50f8cc_t09-potJ/work/score305.py`, `acc305.py`. ONLY `/Dataset/SfS_pp/Axes` varies across assembly arms.
- **Axis packs, walls, and frozen selector:** `T08_AX=/data/gpfs/projects/punim2657/SfSpp/runs/20261125-1218_fc5d0ac_t08-ship/out/axes08_own_dedup`, `T09_AX=/data/gpfs/projects/punim2657/SfSpp/runs/20261125-1340_a50f8cc_t09-own-surfaces/out/axes09_own_regen` (`Pot_J_Piece_01_Axis.xyz` SHA-256 `a0d1b8af0143dfc71271701a16295d1db5bdc3236ab5361d4bcc796d0786de79`), `T09_WALLS=/data/gpfs/projects/punim2657/SfSpp/runs/20261125-1340_a50f8cc_t09-own-surfaces/out/Pot_J/geom`, `CORP=/data/gpfs/projects/punim2657/sfs_main/original_samples/SfS_pp`, `MOR_AX=$CORP/Axes`, `AUTHOR_WALLS=$CORP/Surfaces`, `SHIP=/data/gpfs/projects/punim2657/SfSpp/runs/20261121-1319_2e951d9_t03-ship` (`t03_lib.draw_pool(C, seeds=10, step=10)`, `t03_extract.select_lines(..., 6, None)`, `t03_extract.write_lines`).
- **Diagnostic donor reference for `Pot_J_Piece_01` (evaluation only, never fed to selector):** Ticket 13 donor line direction `(0.992676, 0.042854, 0.112950)`, point `(-53.313366, -28.804402, 479.479140)`, fixed `J01` centroid `(30.107, 12.692, 452.566)` mm.
- **Caveats:** `Pot_J_Piece_01` interior `Bl0` gap measures the input; `Pot_J_Piece_09` has no GT axis and wrong breakline reference (excluded from the 11-piece scored denominator); `Pot_J_Piece_12` is paper-excluded (remains inside the 11-piece `arm_pieces_J.tsv` denominator matching `t03`/`t08`/`t09`, noted in outputs).

## Part A: Isolate `t09` (`7/21`) vs `t08` (`10/21`) in `Hierarchy-T13` (`cell13.sbatch`)

Run all Part A arms with the single pinned `Hierarchy-T13` binary inside `$MAIN/sfs_pristine_assembly.sif` (verifying `WANT_SHA` before and after every run, `posecheck13.sh` requiring all 11 eligible pieces' non-empty `T_*to_*.txt` pose exports before scoring, and before/after input manifest equality):
1. `MOR_CTL`: 2 repeats (`MOR_AX`, positive control; check separation).
2. `T08_ALL`: 4 repeats (`T08_AX`, 11 loaded axes).
3. `T09_ALL`: 4 repeats (`T09_AX`, 11 loaded axes).
4. `T09_WITH_AUTHOR_J01`: 2 repeats (`T09_AX` with ONLY `Pot_J_Piece_01_Axis.xyz` replaced by the frozen `SHIP` selector's `AUTHOR` wall axis for `J01` — positive ceiling check on `t09` background).
5. Five single-sherd `t08 -> t09` swaps (`SWAP_J01`, `SWAP_J02`, `SWAP_J05`, `SWAP_J06`, `SWAP_J11`), 2 repeats each (`T09_AX` with ONLY that one sherd's axis file replaced by its `T08_AX` counterpart; assert exact 1-file diff per arm).

Total Part A cells = `2 + 4 + 4 + 2 + 10 = 22` cells, run via Slurm array in `cell13.sbatch` and polled to terminal `sacct` states via `scripts/slurm_poll.sh`. Report best-of-N across repeats (never median), with how many repeats reached it, plus all 21 per-seam verdicts in `seams.tsv`.

## Part B: Isolate `Pot_J_Piece_01` surface factors (`j01_factors13.py`, `prep13.sbatch`, gated B2)

1. Compare `OWN_T09` (`Pot_J_Piece_01.S0/.S1`, `duplicate_xyz == 0`) vs `AUTHOR` (`Pot_J_Piece_01_Surface_{0,1}.xyz`) in the native scan frame: record per-face point counts, `duplicate_xyz`, `%` within `1.0 mm`, `nn_med_mm`, `nn_p90_mm`, and matched-point unsigned normal-angle median and p90 (`deg`).
2. Run **9 deterministic arms** through the exact frozen `SHIP` selector (`t03_lib.draw_pool(C, seeds=10, step=10)`, `t03_extract.select_lines(..., 6, None)`, `t03_extract.write_lines`, `C = face 0 then face 1`):
   - `OWN_T09`: untouched `t09` `J01` walls (must match `T09_AX/Pot_J_Piece_01_Axis.xyz` SHA-256 `a0d1b8af...` byte-for-byte).
   - `AUTHOR`: untouched Authors' `J01` walls (verify a candidate within `1°` and `1 mm` of the Ticket 13 donor line).
   - `OWN_AUTHOR_NORMALS`: fixed `OWN_T09` XYZ points, 1-NN matched normals transferred from `AUTHOR` per face where `d <= 1.0 mm` (untouched where `d > 1.0 mm`).
   - `AUTHOR_OWN_NORMALS`: fixed `AUTHOR` XYZ points, 1-NN matched normals transferred from `OWN_T09` per face where `d <= 1.0 mm` (untouched where `d > 1.0 mm`).
   - `OWN_SHARED_1MM`: `OWN_T09` points within `1.0 mm` of `AUTHOR` on the same face, untouched normals.
   - `AUTHOR_SHARED_1MM`: `AUTHOR` points within `1.0 mm` of `OWN_T09` on the same face, untouched normals.
   - `OWN_VOXEL_1MM`: common `1.0 mm` occupied voxels shared by `OWN_T09` and `AUTHOR` per face (1 point per voxel closest to voxel centre, tie-break lowest index), from `OWN_T09` with untouched normals.
   - `AUTHOR_VOXEL_1MM`: same common `1.0 mm` voxels per face, from `AUTHOR` with untouched normals.
   - `OWN_BALANCED_S0S1`: downsample `OWN_T09` `S1` uniformly by integer linspace to match `S0`'s point count (`23,387` each, matching Authors' ~1:1 inner/outer balance), untouched normals.
3. **Gated Part B2 E2E confirmation:** For up to the top 2 `OWN_*` factor arms (excluding `OWN_T09`) that export a candidate within `15°` and `15 mm` of the Ticket 13 donor line (at centroid `(30.107, 12.692, 452.566)` mm) OR within `25°` of GT, run 2 repeats each in `Hierarchy-T13` on `T09_ALL` background (swapping ONLY `Pot_J_Piece_01_Axis.xyz`) and record them in `cells.tsv` / `seams.tsv` (`B2_<ARM>`). If no `OWN_*` arm meets the gate, record `b2_status=skipped_no_qualifying_arm` in `j01_factors.tsv` / write-back without inventing a pass.

## Evidence and acceptance

Fetch only short TSV tables, check outputs, and the two PNGs into `C:/PR/worktrees/sfs/13/artifacts/surface-parity-13/evidence/` (keep meshes, walls, and pose trees on Spartan). Leave `verdict` and `human_note` empty in Spartan `runs/index.tsv`.

- [ ] `sources.tsv` (`kind,path,sha256,bytes,detail`) includes SHA-256 hashes of all 6 `t13/` scripts, pinned `Hierarchy-T13` (`WANT_SHA`), `SHIP` code hashes, and before/after corpus MD5 proof (`$SHIP/work/corpus_md5_t03.py`).
- [ ] `cells.tsv` (at least `22` Part A rows + any gated Part B2 rows) has exact header `arm,rep,job_id,usable,exported_poses,sherd,sherd_den,joins_pass,joins_total,exe_sha_ok,inputs_unchanged,changed_axis_files,wall_secs`. `seams.tsv` (`21 * n_usable` rows) has exact header `arm,rep,join_i,join_j,ang_deg,t_mm,verdict`. `summary_partA.tsv` (9 rows: `MOR_CTL`, `T08_ALL`, `T09_ALL`, `T09_WITH_AUTHOR_J01`, `SWAP_J01`, `SWAP_J02`, `SWAP_J05`, `SWAP_J06`, `SWAP_J11`) has exact header `arm,repeats,best_sherd,best_joins,reached_by,all_joins,delta_best_vs_t09,note`.
- [ ] `j01_walls.tsv` (18 rows: 9 Part B arms × 2 faces) has exact header `arm,face,points,duplicate_xyz,matched_1mm_pct,nn_med_mm,nn_p90_mm,normal_ang_med_deg,normal_ang_p90_deg,xyz_sha256,normals_sha256`. `j01_factors.tsv` (9 rows) has exact header `arm,k,axes_sha256,effective_stride,drawn_points,rank1_gt_deg,best_gt_deg,best_donor_deg,best_donor_mm,best_donor_rank,qualifies_b2,b2_best_joins`.
- [ ] `fixtures.tsv` has exact header `fixture,status,detail` (`PASS` on Spartan for `own_t09_pin_match`, `author_donor_match`, `normal_transfer_fixed_xyz`, `single_file_swap_proof`).
- [ ] `renders.tsv` has exact header `figure,path,scale_bar_mm` (`scale_bar_mm = 20`) listing `renders/Pot_J_t08_vs_t09_and_swaps.png` and `renders/J01_surface_factors_overlay.png` (20 mm scale bar in every panel). Inspect both PNGs by eye.
- [ ] `jobs.tsv` has exact header `job_id,stage,arm,rep,state,exit_code` recording every submitted `t13-*` Slurm job (array tasks expanded, unioned against `sacct`) with terminal state/exit code (`check13.py --expect-terminal` passes after polling). Write `## Comments` / `### Write-back` with facts only, best-of-N across repeats (never median) with repeat counts, Part A variance & swap results, Part B 9-arm table + wall comparison, budget used, one `**End state:**` line, per-requirement compliance table, and a separate read-only DeepSeek review checking tables and opening both PNGs. Leave interpretation, commits, and closure to the lead.

Named checks: `python -m py_compile` on `.scratch/surface-parity/t13/{j01_factors13,report13,check13}.py`, `bash -n` on `.scratch/surface-parity/t13/{prep13.sbatch,cell13.sbatch,posecheck13.sh}`, `check13.py --expect-terminal` on Spartan, and `git diff --check`.
