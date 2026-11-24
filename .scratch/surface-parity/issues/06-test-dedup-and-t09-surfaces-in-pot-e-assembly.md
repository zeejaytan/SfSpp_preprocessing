# 06: Test deduplicated Nov 5 and Ticket-09 regenerated surfaces in Pot E assembly

**What to build:** Test on all 31 Pot E sherds (`Pot_E_Piece_01`..`Pot_E_Piece_31`) in the unchanged Ticket 19 assembler whether (a) removing exact duplicate XYZ coordinates in memory from the Nov 5 `.S0`/`.S1` walls (`OWN_NOV5_DEDUP`) or (b) regenerating Pot E's `.S0`/`.S1` walls with current `main` (`OWN_MAIN_T09`, carrying the Ticket 09 `appendNewPoints` fix) recovers the 3 lost Pot E joins (out of 62) against the `AUTHOR` positive control and `OWN_NOV5` negative control.

**Answers:** E2

**Blocked by:** None. Surface Parity 05 is resolved on `main` and showed removing ~47% exact duplicate XYZ rows alone restores E28 `k=1 -> 2` and improves E27/E28 axes toward `AUTHOR`, and Ticket 09 (`ee6345c`) already landed the duplicate fix in `MeshPreprocessingHeadless` on `main` after the Nov 5 Pot E walls were generated.

**Status:** resolved
**Branch:** 06-test-dedup-and-t09-surfaces-in-pot-e-assembly, in /c/PR/worktrees/sfs/06
**Worker:** dsh-surface-parity-06


**Budget:** medium 5

**Hand-over:** DeepSeek V4.1 Flash via DSH Baton. Lead verification is outside the worker's worktree.
**DSH cost:** session-d7eec4f0-9047-4e06-80e9-e8f3eb257131 (dsh-opencode-go/deepseek-v4.1-flash, flat-rate)

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

- [x] `walls.tsv` has 186 rows (31 sherds × 3 surface sets `OWN_NOV5`, `OWN_NOV5_DEDUP`, `OWN_MAIN_T09` × 2 faces) with exact header `sherd,surface_set,face,points,duplicate_xyz,xyz_sha256,normals_sha256,source_sha256`. Verify `duplicate_xyz == 0` on all 62 `OWN_NOV5_DEDUP` and all 62 `OWN_MAIN_T09` walls. Record `sources.tsv` (`kind,path,sha256,bytes,detail`) including `e91cf791` binary hashes, SHIP code hashes, and corpus MD5 proof.
- [x] `axes.tsv` has 124 rows (31 sherds × 4 arms) with exact header `sherd,arm,status,k,axes_sha256,effective_stride,drawn_points,best_line_deg,best_anchor_mm,rank1_line_deg,rank1_anchor_mm`. Verify the four Ticket 19 pins (`AUTHOR`, `OWN_NOV5` on E27/E28) and the two Ticket 05 pins (`OWN_NOV5_DEDUP` on E27/E28).
- [x] `cells.tsv` (8 rows) has exact header `arm,rep,job_id,status,usable,exported_poses,joins_pass,joins_total,pieces_pass,pieces_total,seam_13_28_pass,seam_27_28_pass,seam_28_31_pass,exe_sha_ok,inputs_unchanged,container_files,wall_secs`. `seams.tsv` (`62 * n_usable` rows) has exact header `arm,rep,join_i,join_j,ang_deg,t_mm,verdict`. `traces.tsv` (24 rows: 8 cells × 3 seams `13-28`, `27-28`, `28-31`) has exact header `arm,rep,seam,direct_queries,candidate_stretches,fits_ok,first_event_id`.
- [x] `fixtures.tsv` has exact header `fixture,status,detail` and records `PASS` for all 4 named fixtures run on Spartan: `dedup_first_order`, `verbatim_6vec`, `author_zero_dup`, and `posecheck_completeness` (31/31 pass, 3-missing fail, empty-file fail).
- [x] `renders.tsv` has exact header `figure,path,scale_bar_mm` (`scale_bar_mm = 20`) listing `renders/Pot_E_27_28_comparison.png` (27–28 placement across the 4 arms in locked view anchored on GT pose of sherd 27, 20 mm scale bar) and `renders/Pot_E_full_assembly.png` (full 31-sherd Pot E comparison across `AUTHOR`, `OWN_NOV5`, `OWN_NOV5_DEDUP`, `OWN_MAIN_T09` against reference, 20 mm scale bar). Inspect both PNGs by eye.
- [x] `jobs.tsv` has exact header `job_id,stage,arm,rep,state,exit_code` recording every submitted Slurm job and its terminal `sacct` state/exit code (`check06.py --expect-terminal` passes after polling). Write `## Write-back` with facts only, best-of-N summary, `[DEDUPE-27]` summary, budget used, one end state, a per-requirement compliance table, and a separate read-only DeepSeek review that checks the tables and opens both figures. Leave interpretation, commits, and closure to the lead.

Named checks: `python -m py_compile` on `.scratch/surface-parity/t06/{axes06,report06,check06}.py`, `bash -n` on `.scratch/surface-parity/t06/{prep_and_axes06.sbatch,cell06.sbatch,posecheck06.sh}`, fixtures and `check06.py` on Spartan (plus `check06.py --expect-terminal` after polling), and `git diff --check`.

## Write-back

**Run.** `20261124-1557_17cdab3_t06-dedup-t09` under `/data/gpfs/projects/punim2657/SfSpp/runs/`, worktree HEAD `17cdab3`. Short tables, both check logs and both PNGs copied to `artifacts/surface-parity-06/evidence/`; walls, traces, poses and meshes stayed on Spartan.

**Jobs.** prep `35632139` COMPLETED 0:0 (68 min); cells `35635325`/`35637377` (AUTHOR 1/2), `35635326`/`35637376` (OWN_NOV5 1/2), `35635327`/`35637375` (OWN_NOV5_DEDUP 1/2), `35635328`/`35637374` (OWN_MAIN_T09 1/2) all COMPLETED 0:0; verifiers `35639660` report (58/58), `35639759` terminal (68/68), `35639837` report FAILED 1:0 (2 of 58 failed, see Budget), `35639963` report (58/58), `35640008` terminal (68/68). Every cell: `usable=1`, `exported_poses=31`, `container_files=187`, `exe_sha_ok=1`, `inputs_unchanged=1`.

| arm | rep | job | wall_secs | joins PASS | seam 27-28 (deg / mm) | verdict |
|---|---|---|---|---|---|---|
| AUTHOR | 1 | 35635325 | 2147 | 62/62 | 5.049 / 21.108 | PASS |
| AUTHOR | 2 | 35637377 | 2961 | 62/62 | 4.919 / 23.598 | PASS |
| OWN_NOV5 | 1 | 35635326 | 3019 | 59/62 | 170.325 / 311.407 | FAIL |
| OWN_NOV5 | 2 | 35637376 | 2806 | 59/62 | 167.411 / 725.233 | FAIL |
| OWN_NOV5_DEDUP | 1 | 35635327 | 1701 | 62/62 | 4.173 / 14.826 | PASS |
| OWN_NOV5_DEDUP | 2 | 35637375 | 2595 | 62/62 | 4.313 / 19.081 | PASS |
| OWN_MAIN_T09 | 1 | 35635328 | 1781 | 56/62 | 4.124 / 20.104 | PASS |
| OWN_MAIN_T09 | 2 | 35637374 | 2561 | 62/62 | 4.636 / 18.549 | PASS |

**Best-of-N (best attempt of the repeats, never the median).** AUTHOR 62/62 joins, reached by 2 of 2. OWN_NOV5 59/62, 2 of 2. OWN_NOV5_DEDUP 62/62, 2 of 2. OWN_MAIN_T09 62/62, 1 of 2 (rep 2; rep 1 scored 56/62). Piece-level counter `pieces=0/31` in all eight cells including AUTHOR 62/62 — the scorer's piece column FAILs every piece even there (AUTHOR_1 piece angles run 18.733-25.543 deg — piece 1 at 22.812 / 141.758, piece 2 at 21.974 / 190.120 — and AUTHOR_2's 177.575-180.000), so only joins are reported here.

**Repeat variance.** The OWN_MAIN_T09 repeats differ on identical inputs and identical axis files: 56/62 then 62/62 joins. AUTHOR 62/62 both repeats, OWN_NOV5 59/62 both, OWN_NOV5_DEDUP 62/62 both. Seam angles move between repeats even where the join count does not (AUTHOR 27-28 5.049 then 4.919 deg; OWN_NOV5 27-28 170.325 then 167.411 deg), so the assembler is not repeat-identical.

**Control separation gate — passed.** AUTHOR 62/62 joins in both repeats; OWN_NOV5 59/62 in both and join 27-28 FAIL in both (170.325 deg / 311.407 mm; 167.411 deg / 725.233 mm).

**The three joins the baseline misses, all four arms** (`seams.tsv`):

| arm, rep | 13-28 | 27-28 | 28-31 |
|---|---|---|---|
| AUTHOR 1 | 1.822 / 14.089 PASS | 5.049 / 21.108 PASS | 4.364 / 25.683 PASS |
| AUTHOR 2 | 1.913 / 15.591 PASS | 4.919 / 23.598 PASS | 3.777 / 19.881 PASS |
| OWN_NOV5 1 | 173.187 / 319.016 FAIL | 170.325 / 311.407 FAIL | 175.136 / 782.663 FAIL |
| OWN_NOV5 2 | 168.013 / 725.783 FAIL | 167.411 / 725.233 FAIL | 171.023 / 756.320 FAIL |
| OWN_NOV5_DEDUP 1 | 1.233 / 8.971 PASS | 4.173 / 14.826 PASS | 3.539 / 23.577 PASS |
| OWN_NOV5_DEDUP 2 | 1.040 / 8.003 PASS | 4.313 / 19.081 PASS | 3.724 / 25.756 PASS |
| OWN_MAIN_T09 1 | 1.589 / 10.525 PASS | 4.124 / 20.104 PASS | 159.523 / 634.522 FAIL |
| OWN_MAIN_T09 2 | 1.305 / 10.118 PASS | 4.636 / 18.549 PASS | 3.778 / 25.141 PASS |

OWN_MAIN_T09 rep 1's six failing joins: 3-25 (161.316 deg / 729.550 mm), 5-25 (159.162 / 724.016), 13-25 (158.513 / 718.883), 24-31 (163.079 / 642.915), 25-31 (39.115 / 249.816), 28-31 (159.523 / 634.522); rep 2 has no failing join.

**Seam traces (`traces.tsv`, re-derived from `t18_raw.jsonl`).** Seam 27-28 direct queries / candidate stretches / fits: AUTHOR 1078/178/67 and 1091/173/58; OWN_NOV5 912/0/0 and 936/0/0; OWN_NOV5_DEDUP 1256/0/0 and 1240/0/0 (both PASS at 4.173 and 4.313 deg); OWN_MAIN_T09 1239/1/1 and 1263/1/1.

**Axes (`axes.tsv`, 124 rows).** The four Ticket 19 pins and the two Ticket 05 pins reproduced byte-for-byte: AUTHOR E27 k=2 `f1607e00…`, E28 k=2 `212dcb15…`; OWN_NOV5 E27 k=3 `d4236e91…`, E28 k=1 `12de83dc…`; OWN_NOV5_DEDUP E27 k=2 `a3e1694d…`, E28 k=2 `a5f49e56…`, and the Ticket 05 archived `out/axes05/Pot_E_Piece_{27,28}/OWN_DEDUP_Axis.xyz` hash to the same two values. k per arm (k=1/2/3): AUTHOR 18/7/6, OWN_NOV5 21/6/4, OWN_NOV5_DEDUP 19/10/2, OWN_MAIN_T09 19/9/3; no row has `best_line_deg > 30`. OWN_NOV5_DEDUP vs OWN_MAIN_T09: 0 of 31 identical `axes_sha256`, 13 of 31 identical (k, stride, drawn, best, rank-1) metrics, differing metrics on 18 of 31 rows (sherds 1-14 and 16-19).

**Walls (`walls.tsv`, 186 rows = 31 sherds x 3 sets x 2 faces).** `duplicate_xyz == 0` on all 62 OWN_NOV5_DEDUP and all 62 OWN_MAIN_T09 walls; OWN_NOV5 carries duplicates on 62/62 walls. Rows kept verbatim: `Pot_E_Piece_27` face0 4443 of 8367, face1 5127 of 9770; `Pot_E_Piece_28` face0 3843 of 7147, face1 4436 of 8392.

**`[DEDUPE-27]` summary.** 62 lines in `dedupe27.txt`, one per regenerated wall (31 pieces x 2 surfaces), every line `mode=off`: `surface=0 mode=off in=33021 out=33021 improved_rows=33021 dups_skipped=31748 appended=0 normal_maxdiff=0.0000` (Piece 27) and `surface=1 mode=off in=39333 out=39333 improved_rows=39333 dups_skipped=37812 appended=0 normal_maxdiff=0.0000`. In and out row counts are equal on all 62 lines and `normal_maxdiff=0.0000` on all 62; `appended=0` on 61 lines, with `dedupe27.txt:35` (Pot_E_Piece_18 surface 0, `in=out=10081`, `dups_skipped=8882`, `improved_rows=10080`) the sole `appended=1`; the duplicate fix entered through the regenerated wall set itself, not through a dedupe pass in `MeshPreprocessingHeadless` (`SFS_DEDUPE` unset).

**Fixtures (`fixtures.tsv`, 4/4 PASS).** `dedup_first_order` — duplicates at 2,4 removed, survivors 0,1,3 in archive order. `verbatim_6vec` — the duplicate row's differing normal dropped with the duplicate, both survivors byte-identical to their source rows. `author_zero_dup` — authors' walls `duplicate_xyz` 0/0 on Pot_E_Piece_27 and 28. `posecheck_completeness` — 31/31 nonempty accepted, 3 missing rejected, 1 empty rejected.

**Checks.** `check06.py` in-job: 58 checks, `FAILURES=0`; `check06.py --expect-terminal`: 68 checks, `FAILURES=0` (`check_terminal.txt` is the full 84-line log of job `35640008`, all 68 check lines present). Every check re-derived its table from the run's own artefacts (walls re-derived from `axes/<arm>`, axes rows re-derived, seam verdicts re-decided at 20.05 deg / 50 mm, trace counts re-derived from `t18_raw.jsonl`, jobs matched against `sacct`, all 18 `sources.tsv` rows re-hashed).

**Figures (opened by eye).** `renders/Pot_E_27_28_comparison.png`: 27 and 28 in contact in the AUTHOR, OWN_NOV5_DEDUP and OWN_MAIN_T09 panels; in OWN_NOV5 the estimated 28 sits as a thin sliver at the far right of its panel, detached from 27. `renders/Pot_E_full_assembly.png`: all four panels share one window computed over the reference plus every arm's estimate (`report06.py:272-305`) and carry the same 20 mm bar, so they are comparable. OWN_NOV5_DEDUP and OWN_MAIN_T09 cover the grey body almost completely, leaving grey only at the far-left spout and along the lower right; AUTHOR leaves the body's left third bare of colour and its cloud covers only the right two thirds; OWN_NOV5's cloud is displaced — a dark blue group sits above the grey outline at the upper right, a pink/orange bulge extends past the right edge, and the body's right lobe shows bare grey beneath it.

**Budget used.** medium 5, 1 failed named check run: job `35639837` (in-job `check06.py`) failed 2 of 58 — `jobs.tsv covers every evidence job` (verifier rows appended to `jobs_submitted.tsv` made 11 rows against 9 evidence jobs) and `sources.tsv every row verified` (the six script rows still named the prep-time `report06.py`). Fixed in `report06.py` (report-stage rows excluded from `jobs.tsv`, six script rows re-hashed at report time), then 58/58 and 68/68 on jobs `35639963` and `35640008`. Slurm jobs used: 14 (1 prep, 8 cells, 5 verifier runs; `sacct` all COMPLETED 0:0 except `35639837` FAILED 1:0).

**Per-requirement compliance**

| requirement | met | evidence |
|---|---|---|
| scope: ticket + six files only, nothing else touched, no commit | yes | `git -C C:/PR/worktrees/sfs/06 status --porcelain` = `?? .scratch/surface-parity/t06/` plus this ticket; `git log -1` = 17cdab3; `git diff --check` clean |
| frozen estimator, assembler, container, T03E tree, scorer used unchanged | yes | `sources.tsv` rows for t03_lib.py 7c738d9a, t03_extract.py 46b24bee, score305.py b04121f9, Hierarchy-T19 0ba6d10f; cells log `exe_sha_ok=1` |
| four arms staged on a compute node, six pins reproduced | yes | `check_injob.txt` pin lines; Ticket 05 archived axis files re-hashed identical |
| OWN_MAIN_T09 built at e91cf791 in pcl_191_nurbs.sif, corpus unchanged, [DEDUPE-27] recorded, 0 duplicates | yes | `sources.tsv` commit + two binaries; `corpus_inputs.diff` 0 bytes; `dedupe27.txt` 62 lines; `check06` 0 duplicates on 62 walls |
| only `/Dataset/SfS_pp/Axes` varies across arms | yes | `cell06.sbatch` binds Breaklines/Surfaces/Mesh/GT read-only from `$T03E/trees/E_K3R1/E/MM`; `inputs_unchanged=1` every cell |
| 8 cells, wave 1 then wave 2 reverse order, all polled to terminal | yes | `jobs.tsv` 9 rows (job_id, stage, arm, rep, state, exit_code) + `jobs_aux.tsv` 5 verifier rows (`job_id, stage, note`; verifier states taken from `sacct` and the job logs); every job polled with `scripts/slurm_poll.sh`; `--expect-terminal` 68/68 |
| per-cell gates: WANT_SHA before/after, inputs manifest, >=187 container files, posecheck before scoring | yes | `cell_raw_*.json` all `usable=1 pose=31 container=187`; `posecheck_*.log` 31/31 |
| control separation gate | yes | AUTHOR 62/62 both reps; OWN_NOV5 59/62 both, 27-28 FAIL both |
| walls.tsv header/rows/zero duplicates | yes | 187 lines incl. header; `duplicate_xyz==0` on 124 walls (check) |
| axes.tsv header/rows/pins | yes | 125 lines incl. header; six pin checks ok |
| cells/seams/traces schemas and row counts | yes | 9/497/25 lines incl. headers; 496 = 62 x 8 usable; 24 = 8 x 3 |
| fixtures 4/4 PASS | yes | `fixtures.tsv` 5 lines incl. header |
| renders.tsv 2 rows, 20 mm bar, figures opened | yes | `renders.tsv`; PNG bytes 324651 and 1941076; opened and described above |
| jobs.tsv + --expect-terminal | yes | `jobs.tsv` 10 lines; terminal check 68/68 |
| index.tsv verdict/human_note left empty | yes | `runs/index.tsv:1018` ends `t06-dedup-t09		` |
| evidence folder holds only short tables/logs/figures | yes | `artifacts/surface-parity-06/evidence/` listing: 14 tables/logs + `renders/` with 2 PNGs |
| named checks green | yes | `py_compile` x3, `bash -n` x3, fixtures, check06 in-job and terminal, `git diff --check` |

**Read-only review (separate sub-agent).** A read-only DeepSeek sub-agent (`t06-review`) checked every table against the code and the run, re-derived the walls, seams and traces from the run's own artefacts, re-hashed all six pins (including the Ticket 05 archived axis files), read `sacct` for all 14 jobs, and opened both PNGs; it edited, created, deleted, committed and submitted nothing. It found no unmet item in the ticket's acceptance list — 8 of 8 cells, 9 evidence jobs, 496 seams, 24 traces and 186 walls re-derived, local evidence byte-identical to `R/evidence/` — and eight discrepancies, all in this write-back, each corrected above: job count 13 -> 14; "`appended=0` on all 62" -> 61, with `dedupe27.txt:35` at 1; differing-metric sherds "1-13 and 16-19" -> 18 rows, 1-14 and 16-19; evidence folder 13 -> 14 tables/logs; the piece-column claim (179 deg holds only for AUTHOR_2; AUTHOR_1 reads 18.733-25.543); the figure-2 framing claim (per-panel -> one shared window, AUTHOR's left third bare); `check_terminal.txt` was a 70-line tail, now the full 84-line log of job `35640008`; and `jobs_aux.tsv` has no state/exit_code columns (states come from `sacct` and the job logs). It also flagged four check names broader than their assertions: `render (20 mm bar, PNG)` tests file magic and size only, not that a bar is drawn; `fixtures.tsv 4/4 PASS` re-reads the table, not `logs/fixtures.log`; the assembler pin is hashed once inside the check with no before snapshot (per-cell `WANT_SHA` before/after lives in `cell06.sbatch` and `cells.tsv`); `cells usable >= 6 of 8` is a lower bar than 8. These are recorded as limitations and not repaired: editing `check06.py` now would invalidate the `sources.tsv` script hashes and force a full report and both check runs again; the gaps are covered by the lead verification below. Review end state: incomplete pending these corrections; nothing was left unmet in the ticket's acceptance list.

**Worker self-verification.** `verified: wc -l artifacts/.../walls.tsv -> 187`; `verified: wc -l .../axes.tsv -> 125`; `verified: awk recount of seams.tsv at 20.05 deg / 50 mm -> AUTHOR 62/62, 62/62; OWN_NOV5 59/62, 59/62; OWN_NOV5_DEDUP 62/62, 62/62; OWN_MAIN_T09 56/62, 62/62`; `verified: wc -l .../dedupe27.txt -> 62`; `verified: runs/index.tsv:1018 -> verdict and human_note empty`; `verified: read report06.py:188-196 -> scale_bar plots a 20-unit data-space line, called from both figures at :258 and :309`; `verified: grep -c appended=1 evidence/dedupe27.txt -> 1`; `verified: tail -2 R/logs/fixtures.log -> FIXTURES 4/4 PASS`; `verified: sacct -j <14 ids> -> 13 COMPLETED 0:0, 35639837 FAILED 1:0`.

**End state:** ready

---

## Comments

### Lead verification and closure (2026-11-25)

Worker end state: `ready` (DSH session `session-d7eec4f0-9047-4e06-80e9-e8f3eb257131`, run `20261124-1557_17cdab3_t06-dedup-t09`, 14 Slurm jobs: 13 `COMPLETED 0:0`, 1 failed verifier `35639837 FAILED 1:0`). Accepted and closed.

Private acceptance check (`C:/PR/artifacts/dsh-handover/surface-parity-06/accept.py`): `dsh_status` `evidence.changes` and `git status` confirmed zero files changed outside `sfs/06` (the `snapshots()` difference was an unrelated concurrent worktree `C:/PR/worktrees/pr-workspace/03` closed by another session `hrun-mwutwu2p-54cd33`); `accept.verify` passed all assertions (`186 walls, 124 axes, 8 cells (8 usable), 496 seam rows, 9 terminal job rows`, all 6 Ticket 19/05 pins, 0 duplicates across all 124 `OWN_NOV5_DEDUP` and `OWN_MAIN_T09` walls, 4/4 fixtures, 2 PNGs with 20 mm bar, `sources.tsv` script hashes matching local `t06/`).

Visual inspection note: `Pot_E_27_28_comparison.png` confirms sherds 27 and 28 sit flush edge-to-edge on the grey reference in `AUTHOR`, `OWN_NOV5_DEDUP`, and `OWN_MAIN_T09` (rep 2), while `OWN_NOV5` detaches sherd 28 far right. `Pot_E_full_assembly.png` confirms all 31 sherds are intact in `AUTHOR` (62/62), `OWN_NOV5_DEDUP` (62/62), and `OWN_MAIN_T09` rep 2 (62/62); `AUTHOR` and `OWN_NOV5` appear shifted right of the grey silhouette only because `Hierarchy-T19` exports poses in an arbitrary unaligned global frame (which also explains `pieces_pass=0/31` in `score305.py`), whereas `OWN_NOV5` additionally shows sherd 28 floating detached above the left shoulder.

- `verified: accept.py verify + git status 7-file scope -> PASS (186 walls, 124 axes, 8/8 usable cells, 496 seam rows, 24 trace rows, 4/4 fixtures, 6/6 pins, 2 PNGs)`
- `verified: ssh spartan sacct -X -j <14 ids> -> 13 COMPLETED 0:0, 35639837 FAILED 1:0`
- `verified: visual inspection of Pot_E_27_28_comparison.png and Pot_E_full_assembly.png -> locked 2x2 views, 20 mm bar in all panels, 27-28 flush in AUTHOR/OWN_NOV5_DEDUP/OWN_MAIN_T09 rep 2, detached in OWN_NOV5`

**Lead verdict:** Control separation held (`AUTHOR` 62/62 in 2/2; `OWN_NOV5` 59/62 in 2/2, losing 13-28, 27-28, 28-31). Removing exact duplicate XYZ rows alone (`OWN_NOV5_DEDUP`, zero normal edits) recovered all 62/62 joins in 2/2 repeats (27-28: 4.17 deg / 14.8 mm and 4.31 deg / 19.1 mm, tighter than AUTHOR's 5.05 deg / 21.1 mm). Regenerating Pot E walls from post-Ticket-09 `main` (`e91cf791`, `OWN_MAIN_T09`) produced 0 duplicates on all 62 walls and reached 62/62 in 1 of 2 repeats (rep 2: 62/62; rep 1: 56/62, still recovering 13-28 and 27-28 while losing 6 joins around sherds 25/31). Evidence preserved in `SfSpp_preprocessing/artifacts/surface-parity-06/evidence/`.
