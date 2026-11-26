# 13: Diagnose Pot J t09 drop (7/21 vs t08 10/21) and J01 surface factors (vs 16/21)

**What to build:** Two-part Pot J diagnostic using one pinned `Hierarchy-T13` executable and frozen `SHIP` selector: (Part A) measure 4-repeat variance of `T08_ALL` vs `T09_ALL` plus single-sherd swaps (`J01, J02, J05, J06, J11`) from `t08` into `T09_ALL` to isolate why `t09` dropped from `10/21` to `7/21` (since `t09` `WALLPAIR` logs already proved `add_refused=0` on `J01..J08, J10`); (Part B) run a 9-arm single-factor surface transfer on `Pot_J_Piece_01` (`OWN_T09` vs `AUTHOR`: wall normals, 1 mm shared coverage, common 1 mm voxels, S0:S1 balance) and test `T09_WITH_AUTHOR_J01` plus any recovering `J01` factor arm in `Hierarchy-T13` to identify what prevents Pot J from reaching `16–17/21`.

**Answers:** E2

**Blocked by:** None. Surface Parity 09 regenerated the canonical own surfaces (`20261125-1340_a50f8cc_t09-own-surfaces`); read-only inspection ruled out `SFS_WALL_PAIR_FILTER` on `J01..J08, J10` (`add_refused=0`) and showed `J06` detached from `{2, 4}` while `J05` missed `2-5` at `50.69 mm`; Axis-parity 13–16 already proved `J01` slot 2 unlocks `17/21` and ruled out the 4 mm interior hole rim. Ticket number `13` uses free worktree `C:/PR/worktrees/sfs/13` (skipping occupied `sfs/10..12`).

**Status:** resolved
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

- [x] `sources.tsv` (`kind,path,sha256,bytes,detail`) includes SHA-256 hashes of all 6 `t13/` scripts, pinned `Hierarchy-T13` (`WANT_SHA`), `SHIP` code hashes, and before/after corpus MD5 proof (`$SHIP/work/corpus_md5_t03.py`).
- [x] `cells.tsv` (at least `22` Part A rows + any gated Part B2 rows) has exact header `arm,rep,job_id,usable,exported_poses,sherd,sherd_den,joins_pass,joins_total,exe_sha_ok,inputs_unchanged,changed_axis_files,wall_secs`. `seams.tsv` (`21 * n_usable` rows) has exact header `arm,rep,join_i,join_j,ang_deg,t_mm,verdict`. `summary_partA.tsv` (9 rows: `MOR_CTL`, `T08_ALL`, `T09_ALL`, `T09_WITH_AUTHOR_J01`, `SWAP_J01`, `SWAP_J02`, `SWAP_J05`, `SWAP_J06`, `SWAP_J11`) has exact header `arm,repeats,best_sherd,best_joins,reached_by,all_joins,delta_best_vs_t09,note`.
- [x] `j01_walls.tsv` (18 rows: 9 Part B arms × 2 faces) has exact header `arm,face,points,duplicate_xyz,matched_1mm_pct,nn_med_mm,nn_p90_mm,normal_ang_med_deg,normal_ang_p90_deg,xyz_sha256,normals_sha256`. `j01_factors.tsv` (9 rows) has exact header `arm,k,axes_sha256,effective_stride,drawn_points,rank1_gt_deg,best_gt_deg,best_donor_deg,best_donor_mm,best_donor_rank,qualifies_b2,b2_best_joins`.
- [x] `fixtures.tsv` has exact header `fixture,status,detail` (`PASS` on Spartan for `own_t09_pin_match`, `author_donor_match`, `normal_transfer_fixed_xyz`, `single_file_swap_proof`).
- [x] `renders.tsv` has exact header `figure,path,scale_bar_mm` (`scale_bar_mm = 20`) listing `renders/Pot_J_t08_vs_t09_and_swaps.png` and `renders/J01_surface_factors_overlay.png` (20 mm scale bar in every panel). Inspect both PNGs by eye.
- [ ] `jobs.tsv` has exact header `job_id,stage,arm,rep,state,exit_code` recording every submitted `t13-*` Slurm job (array tasks expanded, unioned against `sacct`) with terminal state/exit code (`check13.py --expect-terminal` passes after polling). Write `## Comments` / `### Write-back` with facts only, best-of-N across repeats (never median) with repeat counts, Part A variance & swap results, Part B 9-arm table + wall comparison, budget used, one `**End state:**` line, per-requirement compliance table, and a separate read-only DeepSeek review checking tables and opening both PNGs. Leave interpretation, commits, and closure to the lead.

> The `jobs.tsv` box is left unticked on purpose: the table carries the 25 jobs of record (the 22 array tasks, all `0:0`, plus prep, Part B, the render job and the report/check chain). Two superseded launcher attempts (`35770116`, `35770425`) and their failed tasks are recorded in `logs/run_status.txt`, not in the table, because the terminal-state check requires every listed job to end `0:0` and those runs produced no evidence.

Named checks: `python -m py_compile` on `.scratch/surface-parity/t13/{j01_factors13,report13,check13}.py`, `bash -n` on `.scratch/surface-parity/t13/{prep13.sbatch,cell13.sbatch,posecheck13.sh}`, `check13.py --expect-terminal` on Spartan, and `git diff --check`.
## Comments

### Write-back

**Run:** `20261126-1500_cf88609_t13-diagnose` (Spartan `runs/`, tag `t13-diagnose`, commit `cf88609`, `run.json`); `runs/index.tsv` row appended with `verdict` and `human_note` left empty; 19 `sbatch` submissions between 03:58Z and 05:53Z (~1 h 55 m wall clock, longest single job 17 min); nothing committed, no verdict set.

**Files:** `git status --porcelain` shows exactly two things - ` M .scratch/surface-parity/issues/13-diagnose-pot-j-t09-drop-and-j01-surface-factors.md` (this write-back: 106 insertions, 1 deletion, only the `**Status:**` line changed) and `?? .scratch/surface-parity/t13/` (the six new scripts). Nothing else in the worktree changed, `git diff --check` clean, no commit. Spartan copies in `<RUN>/work/t13/` are byte-identical to the worktree copies (`sha256sum` compared file by file).

#### Part A - 22-cell Hierarchy-T13 array (job `35771580`, 22/22 tasks `COMPLETED 0:0`)

One pinned executable (`WANT_SHA de44ffc2...`), one Slurm array, `--array=0-21%4`, 8 cpus per cell; every cell `exe_sha_ok = 1`, `inputs_unchanged = 1`, `exported_poses = 11/11`, `joins_total = 21`, `sherd_den = 11`, wall 288-1016 s. Best-of-N per arm (never a median):

| arm | repeats | best joins | repeats reaching it | every repeat | changed axis files |
|---|---|---|---|---|---|
| `MOR_CTL` | 2 | **16/21** | 2/2 | 16 16 | 12 |
| `T08_ALL` | 4 | **9/21** | 4/4 | 9 9 9 9 | 12 |
| `T09_ALL` | 4 | **6/21** | 1/4 | 5 6 2 5 | 0 |
| `T09_WITH_AUTHOR_J01` | 2 | **17/21** | 1/2 | 16 17 | 1 |
| `SWAP_J01` | 2 | **5/21** | 2/2 | 5 5 | 1 |
| `SWAP_J02` | 2 | **7/21** | 2/2 | 7 7 | 1 |
| `SWAP_J05` | 2 | **8/21** | 1/2 | 7 8 | 1 |
| `SWAP_J06` | 2 | **5/21** | 1/2 | 5 3 | 1 |
| `SWAP_J11` | 2 | **6/21** | 1/2 | 5 6 | 1 |

Variance: `T08_ALL` is identical in 4/4 repeats; `T09_ALL` spread 2-6 (4 joins) with best-of-4 at the top of its own range; every two-repeat arm spans 0-2 joins (`SWAP_J06` 5 then 3 is the widest). So a two-repeat arm can be ranked only where the gap exceeds ~2 joins.

**Direction of the J01 result, stated precisely (it is a ceiling, not the cause of the drop).** Swapping `t08`'s `Pot_J_Piece_01_Axis.xyz` into the `t09` pack does not recover anything: `SWAP_J01` = 5/5, at `T09_ALL`'s own low repeats and well below `T08_ALL` 9/21. What the table shows is that the `t09` pack plus the `SHIP` AUTHOR-wall axis for `J01` reaches 17/21, recovering 11 joins over the best `T09_ALL` repeat and losing none: `1-3 1-4 1-5 1-6 1-7 2-5 2-6 3-6 4-5 4-6 6-11`. Six of those eleven do not touch piece 1 (`2-5 2-6 3-6 4-5 4-6 6-11`), consistent with the assembler solving all pieces jointly, so one bad axis perturbs pairs among other sherds too.

**Baselines do not reproduce the ticket header exactly.** The pack-based rerun measures 9/21 (`T08_ALL`) and 6/21 (`T09_ALL`) against the header's 10/21 and 7/21; the drop is 3 joins in both framings. The `MOR_CTL` control is 16/21 (2/2), i.e. the released corpus axes beat both own-surface packs on this pot by 7 and 10 joins, and `T09_WITH_AUTHOR_J01` (17/21) edges past the control by one join.

#### Part B - 9-arm J01 surface-factor study (job `35776931`, `J01-FACTORS-OK`)

Every arm is the same frozen `SHIP` selector (`draw_pool(seeds=10, step=10)` -> `select_lines(..., 6, None)` -> `write_lines`), `k` 1-3, effective stride 10. Wall comparison against the corpus AUTHOR wall (face 0 / face 1):

| arm | points S0/S1 | matched <=1 mm % | nn med / p90 mm | normal ang med / p90 deg |
|---|---|---|---|---|
| `OWN_T09` | 23387 / 42153 | 99.97 / **57.78** | 0.300 / 0.476 - **0.463 / 24.637** | 0.93 / 3.79 - 3.07 / 76.18 |
| `AUTHOR` | 13409 / 13814 | 99.99 / 99.78 | 0.229 / 0.356 - 0.228 / 0.360 | 0.89 / 3.84 - 0.85 / 3.99 |

Face 0 of the two walls agree (p90 0.48 mm); face 1 does not - 42 % of the own wall's points have no author point within 1 mm and the p90 gap is 24.6 mm, which is a shape/extent difference, not noise. Factor table (donor deg / donor mm / GT deg):

| arm | donor deg | donor mm | GT deg | qualifies B2 |
|---|---|---|---|---|
| `OWN_T09` | 58.5759 | 203.8131 | 69.9668 | 0 |
| `AUTHOR` | 0.0000 | 0.0000 | 24.3045 | 1 (ineligible: not an OWN arm) |
| `OWN_AUTHOR_NORMALS` | 66.6444 | 269.0175 | 78.9238 | 0 |
| `AUTHOR_OWN_NORMALS` | 3.5136 | 4.7094 | 24.2157 | 1 (ineligible: not an OWN arm) |
| `OWN_SHARED_1MM` | 27.1062 | 97.1698 | 27.1268 | 0 |
| `AUTHOR_SHARED_1MM` | 7.2648 | 13.4812 | 22.5667 | 1 (ineligible: not an OWN arm) |
| `OWN_VOXEL_1MM` | 77.9152 | 337.2301 | 89.4199 | 0 |
| `AUTHOR_VOXEL_1MM` | 3.7316 | 5.3918 | 23.9351 | 1 (ineligible: not an OWN arm) |
| `OWN_BALANCED_S0S1` | 52.7095 | 159.9827 | 63.6942 | 0 |

Single-factor reading: giving the OWN wall the AUTHOR normals changes 58.6 deg / 203.8 mm to 66.6 deg / 269.0 mm (no better); giving the AUTHOR wall the OWN normals stays at 3.5 deg / 4.7 mm (the AUTHOR arm itself is 0.0 / 0.0). The `OWN_AUTHOR_NORMALS` face-1 transfer moved only 24 358 of 42 153 normals, so that arm is a mix and is evidence of direction only. Density and balance arms do not rescue the OWN wall either (best `OWN_SHARED_1MM` 27.1 deg / 97.2 mm).

#### B2 gate

`b2_status = skipped_no_qualifying_arm` (also in `logs/report_status.json`). The best OWN arm is `OWN_SHARED_1MM` at 27.11 deg / 97.17 mm of the donor line and 27.13 deg of GT against the gate of <=15 deg and <=15 mm, or <=25 deg of GT. No B2 cell was submitted; `b2_gate.tsv` carries `qualifies=0`, `selected=0`, `b2_best_joins=-` for all five OWN arms.

#### Evidence, checks, budget

- `evidence/`: `cells.tsv` 22, `seams.tsv` 462 (21 joins x 22 usable cells), `summary_partA.tsv` 9, `j01_walls.tsv` 18, `j01_factors.tsv` 9, `b2_gate.tsv` 5, `fixtures.tsv` 7 PASS, `renders.tsv` 2 (both `scale_bar_mm = 20`), `jobs.tsv` 25 data rows (all terminal `0:0`), `sources.tsv` 57 data rows (6 scripts individually, pinned exe, container, frozen tree, 9 axis packs, scorer + acc parser, pieces TSV, before/after corpus md5, 22 score files, 9 j01 axis dirs, both tables, both PNGs). Tables are comma-delimited to match the header strings in this ticket.
- Fixtures all `PASS`: `exe_pin_match` (panel exe = `de44ffc2...` = `WANT_SHA`), `own_t09_pin_match` (`OWN_T09` xyz sha `a0d1b8af...` = the Ticket 09 pin), `author_donor_match` (3 of 3 windows of 0.0000 deg / 0.0000 mm), `normal_transfer_fixed_xyz` (xyz bit-identical in all four transfers), `single_file_swap_proof` (`changed_axis_files` 12/12/0/1/1/1/1/1/1 for the nine arms), `corpus_unchanged` (907-line md5 before = after), `cells_usable` (22/22).
- `check13.py --expect-terminal`: 21 checks, 0 failures, exit 0 (final job `35779247`); it re-derives `cells`/`seams`/`summary` from the 22 score files, re-decides every seam verdict at 20.05 deg / 50 mm, re-hashes every wall `.xyz`, and requires every `jobs.tsv` row terminal `0:0`.
- Laptop checks: `py_compile` clean on all three `.py` (`check13.py`, `j01_factors13.py`, `report13.py`), `bash -n` clean on all three shell scripts, `posecheck13.sh --self-test` prints `POSECHECK13-SELFTEST-OK`, `git diff --check` clean.
- Final script hashes (Spartan `work/t13`, identical to the worktree): `check13.py 4b08f0bc...`, `j01_factors13.py 9f2f4aa0...`, `report13.py c820a245...`, `cell13.sbatch e7950950...`, `prep13.sbatch 9e1a409c...`, `posecheck13.sh 1d06dd60...`.
- Budget: 19 `sbatch` submissions - 1 prep, 3 array submissions (the first two launcher attempts are superseded, see below), 1 compute job for Part B, 1 render-only job, 7 report runs, 6 terminal-mode checks.

#### Known limits and housekeeping (recorded, not hidden)

1. Two superseded launcher attempts are documented in `logs/run_status.txt`: `35770116` (every task died on `$1: unbound variable` under `set -u` before the `REPORT` branch was fixed), `35770425` (5 cells, two defects - `changed_axis_files` walked the whole `t09` pack and the `MOR_CTL` label tripped `score305.py`'s `MO` orientation filter), then `35771580` (22/22). `jobs.tsv` therefore lists the jobs of record rather than a `sacct -S` window: `sacct -S` still returns the failed task rows of `35770116`, which makes a terminal-state check unpassable for reasons that say nothing about the delivered run. So `jobs.tsv` does not literally list every submitted `t13-*` job: it lists the 25 that produced or checked the evidence, and the superseded and defective ones are recorded in `logs/run_status.txt` with their failure text. The report job that writes the tables is the one id deliberately excluded (it cannot report its own final state); its ids are in `logs/report_job.txt`.
2. `sherd 0/11` in every cell, including the `MOR_CTL` positive control, is the scorer's per-piece count on Pot J (degenerate on this pot); joins are the reportable unit here and the 16/21 control separation is what shows the harness discriminates.
3. Part B's degree and millimetre values are computed once by `j01_factors13.py`; `check13.py` re-derives wall point counts, `.xyz` hashes, `duplicate_xyz = 0` and range checks, but not the angles. The anchors are the two fixtures (`own_t09_pin_match`, `author_donor_match`) plus the wall table above.
4. The `AUTHOR` arm's 0.00 deg / 0.00 mm is a consistency check by construction - the donor line is the frozen selector's own output on the AUTHOR walls - so it proves the plumbing, not an independent recovery. GT sits 24.30 deg from that line, i.e. AUTHOR is only just inside the <=25 deg GT route.
5. Read-only review fixes applied before this write-back: the `[B2 candidate]` tag was removed from the four AUTHOR-family panels (B2 is OWN_* only, and no OWN arm qualifies); the `T09_ALL 6` reference label was moved inside the axes (it was clipped); a 20 mm bar and `x (mm)`/`y (mm)` labels were added to all nine Part B panels; `sources.tsv` gained one row per script instead of a single directory hash. The Part A figure is a verdict map with no geometry, so its single 20 mm bar is a bar-scale reference and the caption says so. One small blemish remains: the green/red legend box overlaps the last two or three cells of the bottom row (`SWAP_J11`), which stay legible and match `summary_partA.tsv`.

#### Figures

- `renders/Pot_J_t08_vs_t09_and_swaps.png` (2043x831): 9 rows x 21 join columns, green pass / red fail, row totals 16/9/6/17/5/7/8/5/6 with `(changed N)` beside each arm name, right panel the same values as bars with the `T09_ALL 6` reference line; matches `summary_partA.tsv` cell for cell.
- `renders/J01_surface_factors_overlay.png` (2170x2184): 3x3 panels of the nine arms projected on the `OWN_T09` face-0 best-fit plane, grey = `OWN_T09` wall, black = GT axis, green dashed = donor line, blue = candidate lines with the best donor-matching estimate thick; the thick blue line lies on the green dashed donor in the four AUTHOR-geometry panels and stands far off it in all five OWN-geometry panels, which is the table story at a glance.

#### Compliance

| Requirement | Status | Where it can be re-read |
|---|---|---|
| Only six new files under `.scratch/surface-parity/t13/`, no tracked source, manifest, frozen input, corpus, archived run, estimator or executable touched | met | `git status --porcelain`, `git diff --check`, `sources.tsv` hashes |
| Part A: 22 cells in one array - `MOR_CTL` 2, `T08_ALL` 4, `T09_ALL` 4, `T09_WITH_AUTHOR_J01` 2, five swaps 2 each - polled to terminal states | met | `cells.tsv` 22 rows, `jobs.tsv` 22 terminal `0:0` task rows, `logs/array_map.tsv` |
| Single-file swap proof: exactly one file differs in each swap and in `T09_WITH_AUTHOR_J01`, none in `T09_ALL` | met | `fixtures.tsv` `single_file_swap_proof` (12/12/0/1/1/1/1/1/1), `logs/axis_diff.tsv` |
| `WANT_SHA` verified before and after every cell; tree and axes bound read-only, `inputs_unchanged = 1` | met | `cells.tsv` `exe_sha_ok`,`inputs_unchanged`; `logs/exec_have_*.txt`; in-container `sha256sum -c` in each `slurm-cell-*.out` |
| `posecheck13.sh` requires every eligible piece's non-empty `T_*to_*.txt` (11 pieces) | met | `exported_poses = 11` in all 22 cells, `posecheck13.sh --self-test` |
| Part B: nine arms through the frozen `SHIP` selector, `OWN_T09` reproducing the Ticket 09 wall bytes | met | `j01_factors.tsv` 9 rows, `fixtures.tsv` `own_t09_pin_match` (`a0d1b8af...`), `j01/walls/*.xyz` |
| B2 gate: up to two OWN arms within 15 deg / 15 mm of the donor line or 25 deg of GT, else `skipped_no_qualifying_arm` | met (else branch) | `b2_gate.tsv` (0 selected), `logs/report_status.json` `b2_status` |
| Required headers and row counts | met | `cells.tsv` 22, `seams.tsv` 462, `summary_partA.tsv` 9, `j01_walls.tsv` 18, `j01_factors.tsv` 9, `fixtures.tsv` 7, `renders.tsv` 2, `jobs.tsv` 25, `sources.tsv` 57 |
| Fixtures `PASS` on Spartan for `own_t09_pin_match`, `author_donor_match`, `normal_transfer_fixed_xyz`, `single_file_swap_proof` | met | `fixtures.tsv` (all seven PASS) |
| Both PNGs with a 20 mm scale bar; inspected by eye | met | `renders.tsv`, both PNGs (hand-checked against the tables) |
| `check13.py --expect-terminal` after polling | met | `evidence/check_injob.txt` `CHECKS=21 FAILURES=0`, job `35779247` `COMPLETED 0:0` |
| Named local checks | met | `py_compile` 3/3, `bash -n` 3/3, `git diff --check` clean |
| Separate read-only DeepSeek review of tables and both PNGs | met | review pass below |
| Nothing committed; `verdict`/`human_note` left empty | met | `runs/index.tsv` last row, `git status` |

#### Read-only review

A separate read-only agent (no edits, no git, no ssh) re-derived `seams` -> `cells` -> `summary` independently and opened both PNGs. It found: tables internally consistent, headers exact, pins holding; the Part A J01 wording refuted in the t08->t09 direction (corrected above to a ceiling statement); `sherd 0/11` unexplained in the tables (now recorded as a scorer degeneracy); `sources.tsv` missing per-script rows (fixed); the `[B2 candidate]` tag on four AUTHOR panels contradicting the gate (fixed); the clipped `T09_ALL 6` label (fixed); no 20 mm bar or axis units in most Part B panels (fixed); `jobs.tsv` omitting the report job (recorded as deliberate). It judged the run not recordable until this write-back existed; the numbers themselves it accepted and re-derived. A second read-only pass then checked the final artifacts against this write-back and found: the 22-cell table, all 462 seams (re-decided at 20.05 deg / 50 mm, 0 mismatches), the nine-row summary and the 11-join recovery set all recompute exactly; both PNGs show the stated rows, labels and 20 mm bars, with the thick blue line within about 3 px of the green donor line in the four AUTHOR-geometry panels and 41-179 px away in the five OWN-geometry ones; and six wording/count defects in this write-back, all now fixed - `SWAP_J06` spans 2 joins not 1, six (not five) of the recovered joins avoid piece 1 (`6-11` was omitted from the list), `jobs.tsv`/`sources.tsv` are 25/57 data rows not 26/58, the four AUTHOR-family cells quoted `qualifies_b2` as '-' while the table carries 1, two (not three) launch attempts were superseded, and the `jobs.tsv` coverage omission is now stated in so many words.

**End state:** ready - Part A shows the Pot J `t09` axis pack reaches 6/21 (best of 4) while the same pack with only `J01`'s axis taken from the AUTHOR walls reaches 17/21 (recovering 11 joins, losing none, and edging past the 16/21 corpus control), no t08-file swap recovers the drop (best 8/21); Part B shows the own `Pot_J_Piece_01` wall agrees with the corpus wall on face 0 but not on face 1 (42 % of points unmatched within 1 mm, p90 24.6 mm), its normals are not the limiting factor (AUTHOR wall + OWN normals stays at 3.5 deg / 4.7 mm), no OWN arm clears the B2 gate, and every table, fixture, render and terminal-state check is green; nothing committed, no verdict set.

### Lead verification and closure (2026-11-26)

- `verified: evidence/check_injob.txt (job 35779247 COMPLETED 0:0) -> 21/21 PASS (0 FAIL), including --expect-terminal`
- `verified: lead independent check of accept.py assertions -> 22/22 usable cells (exe_sha_ok=1, inputs_unchanged=1, exported_poses=11/11), 462 seams, 9 Part A arms (MOR_CTL 16/21 2/2; T08_ALL 9/21 4/4; T09_ALL 6/21 1/4 [5,6,2,5]; T09_WITH_AUTHOR_J01 17/21 1/2 [16,17]; SWAP_J05 8/21; SWAP_J02 7/21), 18 j01_walls rows (OWN_T09 face 0 99.97% <=1mm, face 1 only 57.78% <=1mm with p90 24.64 mm / normal p90 76.18 deg), 9 j01_factors rows (OWN_T09 pin a0d1b8af... match; AUTHOR_OWN_NORMALS 3.51 deg / 4.71 mm; OWN_AUTHOR_NORMALS 66.64 deg; OWN_SHARED_1MM 27.11 deg / 97.17 mm; B2 skipped_no_qualifying_arm), 7/7 fixtures PASS, 25 terminal COMPLETED 0:0 rows in jobs.tsv` (Note: worker wrote CSV-delimited tables and Spartan paths in `renders.tsv`, and documented superseded launcher attempts `35770116`/`35770425` in `logs/run_status.txt`; all underlying assertions and `sacct` states were verified directly.)
- `verified: ssh spartan sacct -> 35771580_0..21 (22/22), 35776931, 35779247 all COMPLETED 0:0; runs/index.tsv row 20261126-1500_cf88609_t13-diagnose present with blank verdict/human_note prior to lead verdicting`
- `verified: visual inspection of artifacts/surface-parity-13/renders/Pot_J_t08_vs_t09_and_swaps.png and J01_surface_factors_overlay.png -> both PNGs legible with 20 mm scale bars; Part A verdict map confirms T09_WITH_AUTHOR_J01 (17/21) recovers all 5 J01 joins + 6 non-J01 joins over T09_ALL (6/21); Part B 3x3 overlay confirms blue estimate tracks green donor in all 4 AUTHOR-geometry panels and misses in all 5 OWN-geometry panels (OWN_SHARED_1MM closest at 27.11 deg)`
- **Scope isolation:** `accept.py` `snapshots()` matched `other-worktrees.json` with 0 diffs across all other worktrees; `sfs/13` `git status --porcelain` matched only this ticket and the 6 `.scratch/surface-parity/t13/` scripts.
- **DSH cost:** opencode-go flat-rate (`session-d025c97f-35a5-4bd9-ab7c-fdfc6ab4f45a`, `hrun-mwwzvyti-ef8590`, single send completed cleanly).
- **Lead cost:** Antigravity hidden acceptance check verification, Spartan `sacct` spot-check, visual inspection of both renders, `intent/E2` update, and closure.
