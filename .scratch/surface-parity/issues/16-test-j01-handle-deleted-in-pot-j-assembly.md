# 16 — Test J01 handle-deleted surfaces in Pot J end-to-end assembly

**Answers:** E2
**Status:** ready-for-review
**Working in:** chat on Thinkbook16 (2026-11-27)
**Branch:** 16-test-j01-handle-deleted-in-pot-j-assembly, in /c/PR/worktrees/sfs/16
**Worker:** DeepSeek

## Context

[Ticket 13](13-diagnose-pot-j-t09-drop-and-j01-surface-factors.md) showed that `t09`'s canonical Pot J axes (`J02..J12`) are healthy: swapping **only** `Pot_J_Piece_01`'s axis back to `AUTHOR` (`T09_WITH_AUTHOR_J01`) jumps Pot J from `6/21` joins (`T09_ALL`) to `17/21` (`[16, 17]`), beating the Authors' full-pot control (`MOR_CTL`, `16/21`).

[Ticket 14](14-diagnose-j01-s1-lobe-and-voxel-selector-split.md) showed *why* `J01` fails on our own walls:
1. Our `Surface_1` (`OWN_T09.S1`) grew onto an attached handle stub (`17,795` points, `42.2%`, curving `48.5 mm` off the body wall), whereas the Authors' `AUTHOR.S1` stopped at the body wall (`63.1%` vs `85.1%` mesh coverage).
2. Even after deleting the handle points (`OWN_SHARED_1MM` and `OWN_VOXEL_1MM`), the frozen `SHIP` selector (`select_joint_lines`) drops the good donor-close backup line because `select_joint_lines` only keeps `thickness_arm`'s rank-0 line (`73°–78°` off) and discards its `kept=True` secondary lines (`6.60°` at `1.173x` on `OWN_SHARED_1MM`, and `8.68°` at `1.168x` on `OWN_VOXEL_1MM`). Meanwhile `OWN_SHARED_1MM` through the unchanged `SHIP` selector reaches `27.11°` from donor (vs `58.58°` with the handle).

This ticket answers the conservator's direct question: **if we delete the handle on our own `J01` surface, does our Pot J match or beat the Authors' `16/21` control?** It runs five `J01` axis arms inside the exact pinned `Hierarchy-T13` Pot J assembler (with byte-identical `J02..J12` `t09` axes and `t09` breaklines, 2 repeats per arm).

## Exact Inputs & Environment (Spartan compute node only)

- **Saved `t13` `J01` walls (read-only):**
  `/data/gpfs/projects/punim2657/SfSpp/runs/20261126-1500_cf88609_t13-diagnose/j01/walls/`
  (`AUTHOR`, `OWN_T09`, `OWN_SHARED_1MM`, `OWN_VOXEL_1MM`, `.S0.xyz` and `.S1.xyz`)
- **Pinned `Hierarchy-T13` binary, Pot J `t09` axes/breaklines, and `t13` cell/scorer setup (read-only):**
  `/data/gpfs/projects/punim2657/SfSpp/runs/20261126-1500_cf88609_t13-diagnose/`
  Reuse the exact compiled `Hierarchy-T13` executable, `t09` `J02..J12` axis files, `t09` breaklines, and Ticket 13 scoring recipe (`t13` scripts / `score305` / `acc_*.tsv`). Zero recompilation and zero changes to `J02..J12`.
- **Frozen `SHIP` selector & corpus loader (read-only):**
  `/data/gpfs/projects/punim2657/SfSpp/runs/20261121-1319_2e951d9_t03-ship/work`
  (`t03_lib.py`, `t03_extract.py`, `impl_t03/sfs_axes/joint.py`, `impl_t03/sfs_axes/select.py`)
- **Donor reference (evaluation only; never fed to selector):**
  `DONOR_DIR = [0.992676, 0.042854, 0.112950]` (unit), `DONOR_PT = [-53.313366, -28.804402, 479.479140]`, `CENTROID = [30.107, 12.692, 452.566]`, plus `t03_lib.gt_axis("Pot_J_Piece_01")`.
- **Spartan run directory:**
  `/data/gpfs/projects/punim2657/SfSpp/runs/<YYYYMMDD-HHMM>_<git7>_t16-j01-handle-deleted`

## Deliverables

Create all new scripts under `.scratch/surface-parity/t16/` in `worktrees/sfs/16`:

1. **`prep_j01_axes16.py` (run on Spartan compute node, NOT login node):**
   Build 5 `Pot_J_Piece_01_Axis.xyz` files (exact `[position, direction]` format matching `t03_extract.write_lines`, unscaled):
   - **`CTL_T09_WITH_AUTHOR_J01`:** copy the exact `t13` `AUTHOR` `J01` axis (positive control).
   - **`OWN_NO_HANDLE_SHIP`:** `OWN_SHARED_1MM` through the unchanged frozen `SHIP` `select_joint_lines` (`dl.draw_pool(C, seeds=10, step=10)`).
   - **`OWN_NO_HANDLE_THICKSEC`:** `OWN_SHARED_1MM` through the exact same `normal_arm`, `thickness_arm`, `select_union_lines(..., tri_select=False)` calls, then merge in a helper `merge_with_thick_secondaries` that takes `normal rank-0`, `thickness rank-0`, `shipped rank-0`, then **`res_thickness[:, 1:]` in rank order BEFORE `res_shipped[:, 1:]` in rank order** (each subject to `direction_angle_deg >= 10.0` from kept lines and `kmax = 3`), followed by `orient_merged(..., C, base_orient=True)`. Keep `sfs_axes/` unmodified; define the 10-line merge helper cleanly inside `prep_j01_axes16.py`.
   - **`OWN_VOXEL_THICKSEC`:** `OWN_VOXEL_1MM` through the exact same `merge_with_thick_secondaries` rule (expected to admit `thickness_arm` rank 1 at `8.68°`).
   - **`OWN_S0_ONLY_SHIP`:** `OWN_T09.S0` alone (`C0 = S0, C1 = S0, C = S0`) through the unchanged frozen `SHIP` `select_joint_lines` (checks whether inner wall alone avoids the handle-bearing outer wall).
   - Write strictly tab-delimited (`\t`) `evidence/j01_axes16.tsv` with header:
     `arm	k	best_donor_deg	best_donor_mm	best_gt_deg	axes_sha256`

2. **`run_potj16.sbatch` (Slurm array job, `10` cells = 5 arms × 2 repeats, using `Hierarchy-T13`):**
   - For each `(arm, rep)` cell (`rep` in `1, 2`), verify before running that `Pot_J_Piece_{02..12}_Axis.xyz` and all `Breakline_0` files are byte-identical to Ticket 13 `T09_ALL`, and ONLY `Pot_J_Piece_01_Axis.xyz` is substituted.
   - Run `Hierarchy-T13` cleanly, score with the exact Ticket 13 `score305` / seam scorer, poll all jobs via `scripts/slurm_poll.sh`, and append the verbatim `sacct` output for all jobs to `logs/run_status.txt`.
   - Write strictly tab-delimited (`\t`) `evidence/potj_assembly16.tsv` with exact header:
     `arm	rep	sherds_ok	sherds_total	joins_ok	joins_total	j01_joins_ok	j01_joins_total	non_j01_joins_ok	non_j01_joins_total	jobid	state	exit_code`
     (`sherds_total = 11`, `joins_total = 21`, `j01_joins_total` = J01's GT edges out of 21, `non_j01_joins_total = 21 - j01_joins_total`, `state = COMPLETED`, `exit_code = 0:0`).

3. **`render_potj16.py` (run on Spartan compute node):**
   - Render `renders/Pot_J_handle_deleted_comparison.png` (`180+ dpi`, 1×5 or 2×3 locked-camera mesh layout of the best repeat of each arm with a `20 mm` scale bar in every panel, `Pot_J_Piece_01` highlighted, showing exact `X/21` joins and `J01`'s `Y/Z` seams per panel).
   - Write strictly tab-delimited (`\t`) `evidence/renders.tsv` listing the relative path `renders/Pot_J_handle_deleted_comparison.png`.

4. **Stage & write-back:**
   - Stage `evidence/` (`j01_axes16.tsv`, `potj_assembly16.tsv`, `renders.tsv`), `renders/Pot_J_handle_deleted_comparison.png`, and `logs/run_status.txt` into `C:/PR/worktrees/sfs/16/artifacts/surface-parity-16/`.
   - Write back the concise results (best-of-2 AND per-repeat `X/21` joins, `J01` seams vs non-`J01` seams, axis table, exact Spartan run dir + `sacct` State/ExitCode, and compliance table) into `.scratch/surface-parity/issues/16-test-j01-handle-deleted-in-pot-j-assembly.md`, set `Status: ready-for-review`, and **stop** (do not merge, edit `main`, or close the worktree).

## Must Not Change

- Do NOT modify `sfs_axes/`, `mesh_processing_headless.cpp`, `Data/`, `intent/`, `scripts/`, or any existing ticket/script outside `.scratch/surface-parity/t16/`, `.scratch/surface-parity/issues/16-test-j01-handle-deleted-in-pot-j-assembly.md`, and the worktree's gitignored `artifacts/surface-parity-16/` folder.
- All `.tsv` files MUST use literal `\t` tabs (never commas) and finite numbers; `renders.tsv` MUST use the relative path `renders/Pot_J_handle_deleted_comparison.png`.
- All heavy compute (`prep_j01_axes16.py`, `Hierarchy-T13` assembly cells, scoring, rendering) MUST run via `sbatch` on Spartan compute nodes, never on the laptop or Spartan login node.

## Results (worker write-back, 2026-11-27)

**Answer to the conservator's question: yes.** Delete the handle from our own `J01` surface and Pot J seats as well as the Authors' own `J01` axis does: `17/21` joins in **2 of 2** repeats with the thickness-secondary merge (`OWN_NO_HANDLE_THICKSEC`), against `16/21` for the Authors' axis control (`CTL_T09_WITH_AUTHOR_J01`: 16, 16) and `6/21` for our canonical `t09` axes in Ticket 13. All five seams the `J01` sherd takes part in seat in every handle-deleted arm (`5/5`, `1.5-3.8 deg`, `8.4-23.9 mm`), so the sherd is placed to within a few degrees and roughly a centimetre. The plain `SHIP` selector reaches `17/21` in one of two repeats (17, 16); the voxel-wall variant does the same (16, 17).

**Weight:** one pot (`Pot J`), 11 scored sherds, 21 reference joins, 10 cells (5 arms x 2 repeats) on the same walls and the same pinned binary. The `17/21` result repeats in `2/2` only for `OWN_NO_HANDLE_THICKSEC`; the other two handle-deleted arms each got `17` once and `16` once.

### Axis candidates (`evidence/j01_axes16.tsv`, 5 rows)

| arm | k | best donor deg | best donor mm | best GT deg |
|---|---|---|---|---|
| `CTL_T09_WITH_AUTHOR_J01` | 3 | 0.0000 | 0.0000 | 24.3045 |
| `OWN_NO_HANDLE_SHIP` | 2 | 27.1062 | 97.1698 | 27.1268 |
| `OWN_NO_HANDLE_THICKSEC` | 3 | 6.5997 | 3.6832 | 25.9920 |
| `OWN_VOXEL_THICKSEC` | 2 | 8.6828 | 1.6917 | 29.4152 |
| `OWN_S0_ONLY_SHIP` | 2 | 76.5360 | 381.4404 | 87.1929 |

The thickness-secondary merge admits the line the frozen selector dropped: `6.60 deg` from the donor on `OWN_SHARED_1MM` (k=3) and `8.68 deg` on `OWN_VOXEL_1MM` (k=2), matching what Ticket 14 predicted. The inner wall alone is not a substitute: `76.54 deg` off the donor and `0/5` J01 seams.

### Assembly results (`evidence/potj_assembly16.tsv`, 10 rows, all `COMPLETED` / `0:0`)

| arm | best of 2 | rep1 | rep2 | J01 seams | sherds seated (rep1, rep2) |
|---|---|---|---|---|---|
| `CTL_T09_WITH_AUTHOR_J01` | 16/21 | 16/21 | 16/21 | 5/5 in both | 8/11, 8/11 |
| `OWN_NO_HANDLE_SHIP` | 17/21 | 17/21 | 16/21 | 5/5 in both | 9/11, 8/11 |
| `OWN_NO_HANDLE_THICKSEC` | 17/21 | 17/21 | 17/21 | 5/5 in both | 9/11, 9/11 |
| `OWN_VOXEL_THICKSEC` | 17/21 | 16/21 | 17/21 | 5/5 in both | 8/11, 9/11 |
| `OWN_S0_ONLY_SHIP` | 5/21 | 5/21 | 5/21 | 0/5 in both | 6/11, 6/11 |

`j01_joins_total = 5` (the GT edges containing sherd 1), `non_j01_joins_total = 16`. The non-J01 split is `11/16` on the 16-join cells and `12/16` on the 17-join cells.

### Which joins fail, and why the extra one seats

Four joins fail in **all ten** cells, the positive control included: `2-8`, `5-12`, `8-11`, `8-12`. They are not caused by `J01` and are outside this ticket.

The single join that separates 17/21 from 16/21 is `6-11`: it fails in the control (`92.3 deg`, `703 mm` — piece 11 is placed elsewhere when the Authors' `J01` axis drives the chain), fails in the 16-join handle-deleted repeats, and passes at `3.3 deg` / `7.0 mm` in the 17-join ones. So the extra join is a chain effect of the different `J01` axis, not of the handle. `J01` itself is unaffected: 5/5 in every handle-deleted arm.

### Run and jobs

- Run dir: `/data/gpfs/projects/punim2657/SfSpp/runs/20261127-0300_af7974a_t16-j01-handle-deleted` (`run.json`, `submit.sbatch` = `prep16.sbatch`, scripts in `work/t16/`).
- Prep `35855468`: `COMPLETED`, `ExitCode 0:0`, elapsed `00:03:50`; it verified the tree pins, built the five axes, staged the five axis packs and submitted the array plus the report.
- Array `35855867` (10 cells, `--array=0-9%3`): `35855867_0`..`_9` all `COMPLETED` `0:0`, elapsed `00:08:15`-`00:13:57`.
- Report `35859454`: `COMPLETED`, `0:0`, elapsed `00:00:15` (superseded by the render fix below).
- Render fix `35861684` and final report `35861740`: both `COMPLETED`, `0:0`, elapsed `00:00:12` and `00:00:09`; `35861740` is the run that wrote the delivered PNG.
- Verbose `sacct` for the prep, the array and the report is appended verbatim to `logs/run_status.txt`; the per-cell block is in `logs/sacct16.txt`.

Exact commands (laptop, from `C:/PR/worktrees/sfs/16/.scratch/surface-parity/t16`):

```
mkdir -p artifacts/surface-parity-16/{evidence,renders,logs}
scp prep16.sbatch spartan:<RUN>/
scp prep_j01_axes16.py verify_tree16.py report16.py render_potj16.py run_potj16.sbatch spartan:<RUN>/work/t16/
ssh spartan 'cd <RUN> && sbatch prep16.sbatch'          # 35855468, submits 35855867 + report
bash C:/PR/scripts/slurm_poll.sh 35855468 20
bash C:/PR/scripts/slurm_poll.sh 35855867 20
ssh spartan 'cd <RUN> && sbatch work/t16/run_potj16.sbatch REPORT report'   # 35859454
bash C:/PR/scripts/slurm_poll.sh 35859454 20
scp spartan:<RUN>/evidence/*.tsv artifacts/surface-parity-16/evidence/
scp spartan:<RUN>/renders/Pot_J_handle_deleted_comparison.png artifacts/surface-parity-16/renders/
scp spartan:<RUN>/logs/run_status.txt artifacts/surface-parity-16/logs/
```

### Verification

- `verified: recomputed PASS sets from the ten out/score/*.tsv files, independent of report16.py -> joins 16,16,17,16,17,17,16,17,5,5 and J01 5/5,5/5,5/5,5/5,5/5,5/5,5/5,5/5,0/5,0/5, matching evidence/potj_assembly16.tsv`.
- `verified: sacct -j 35855867 -X -> 35855867_0.._9 COMPLETED 0:0` (block in `logs/sacct16.txt`).
- `verified: evidence/j01_axes16.tsv -> header arm,k,best_donor_deg,best_donor_mm,best_gt_deg,axes_sha256; 5 rows; 6 tab-separated fields; no NaN/Inf`.
- `verified: evidence/potj_assembly16.tsv -> header as specified; 10 rows; 13 tab-separated fields; every row state COMPLETED, exit_code 0:0`.
- `verified: evidence/renders.tsv -> 3 tab-separated fields; path field exactly renders/Pot_J_handle_deleted_comparison.png; no commas`.
- `verified: CTL axis sha256 = t13 axes/T09_WITH_AUTHOR_J01/Pot_J_Piece_01_Axis.xyz (byte copy)`; the two `SHIP` arms matched the frozen selector call (`np.array_equal` True) and the merge helper equals `joint.merge_lines` when the thickness secondaries are withheld (`np.array_equal` True), both logged in `logs/j01_axes16_detail.json`.
- `verified: walls pinned 8/8` to `t13/evidence/j01_walls.tsv` (`xyz_sha256`) before any axis was built.
- Looked at the render, and it forced a fix (see below): `renders/Pot_J_handle_deleted_comparison.png` now shows five posed vessels at a locked camera with a 20 mm bar each. `J01` (red) sits flush on the body with its handle sticking out in panels 1-4 and is visibly displaced into the vessel in panel 5 (`OWN_S0_ONLY_SHIP`, 5/21, J01 0/5). Measured: the red sherd centroid in panels 1-4 agrees with the control within `0.32 mm`, and in panel 5 it is `56.46 mm` away; `J01` median distance to the other sherds is `13.9-16.0 mm` because the joint surfaces overlap rather than touch, so the seam table stays the quantitative evidence.

### Render bug found in review, and the fix

Lead review rejected the first picture: all five panels looked identical, including the `5/21` arm, and the red `J01` faces interpenetrated the grey sherds.

- **Cause:** `Hierarchy-T13` writes `*_OBJ_<p>.obj` in **raw scan coordinates** (`z` near `440 mm`) and records the placement separately in `T_<p-1>to_<p-1>.txt`. The first `render_potj16.py` drew those OBJ files directly (its docstring wrongly claimed they were already in the assembly frame), so the panels were raw scans, all at the same coordinates.
- **Fix** (`render_potj16.py`, job `35861740`): load the decimated corpus meshes `sfs_main/original_samples/SfS_pp/Mesh/Pot_J_Piece_NN_Mesh_DS.obj`, apply each piece pose `V_asm = V_raw @ T[:3,:3].T + T[:3,3]`, anchor every panel to the control panel through the seated body sherd Piece 3 (`M = T_ctl(p3) @ inv(T_panel(p3))`, panel shifts `12.93 / 31.43 / 4.71 / 41.16 mm` for SHIP / THICKSEC / VOXEL / S0), then draw dense point clouds with `J01` in `#d62728` over muted greys and the same camera and 20 mm bar everywhere.
- **Guard:** the script now hard-fails unless panel 5 (`OWN_S0_ONLY_SHIP`) moves its posed `J01` centroid by more than `10.0 mm` against panel 1, and unless `max_panel_diff > 10.0`; the run measured `56.46 mm`, while panels 1-4 agree with the control within `0.32 mm`. Untransformed meshes give `0.0 mm` and can no longer pass.
- **Reading the picture:** the red object is the corpus sherd 1, which still carries its handle in every panel, placed by each arm's pose; the arm difference lives in the axis walls, not in the assembled mesh. So the picture argues about seating, not about the handle removal itself.

### Requirement compliance

| # | requirement | evidence | status |
|---|---|---|---|
| 1 | five `Pot_J_Piece_01_Axis.xyz` candidates, exact `[position, direction]` via `t03_extract.write_lines`, unscaled | `work/t16/prep_j01_axes16.py`, `axes16/<ARM>/Pot_J_Piece_01_Axis.xyz`, `logs/j01_axes16_detail.json` | met |
| 2 | `CTL` = exact t13 AUTHOR axis | byte-identical copy, sha `6dcfc83a...` | met |
| 3 | `OWN_NO_HANDLE_SHIP` through unchanged frozen `SHIP` (`draw_pool(C, seeds=10, step=10)`, `select_joint_lines`) | `ship_path_identical` True | met |
| 4 | `OWN_NO_HANDLE_THICKSEC` / `OWN_VOXEL_THICKSEC` through `normal_arm`, `thickness_arm`, `select_union_lines(..., tri_select=False)` + local `merge_with_thick_secondaries` (thickness secondaries before shipped, `>= 10.0 deg`, `kmax=3`) + `orient_merged(..., base_orient=True)`; `sfs_axes/` unmodified | helper in `prep_j01_axes16.py` (10 lines), fixture equals `joint.merge_lines` with secondaries withheld | met |
| 5 | `OWN_S0_ONLY_SHIP` = `OWN_T09.S0` alone (`C0 = C1 = C = S0`) through `SHIP` | axis built; `76.54 deg` off donor; `0/5` seams | met |
| 6 | `evidence/j01_axes16.tsv` tab-delimited, exact header, 5 rows | validated | met |
| 7 | array: 10 cells, 5 arms x 2 repeats, `Hierarchy-T13` | `35855867_0.._9` | met |
| 8 | each cell verifies `J02..J12` axes and all breaklines byte-identical to Ticket 13 `T09_ALL`, only `J01` substituted | `logs/identity16_<ARM>_<REP>.tsv` per cell, `identity ok=1` in every cell | met |
| 9 | `Hierarchy-T13` run cleanly, Ticket 13 `score305` / seam scorer | per-cell logs, `out/score/*.tsv` + `acc_*.tsv` | met |
| 10 | every job polled with `scripts/slurm_poll.sh`, verbatim `sacct` in `logs/run_status.txt` | see Run and jobs | met |
| 11 | `evidence/potj_assembly16.tsv` tab-delimited, exact header, 10 rows, `sherds_total=11`, `joins_total=21`, `state=COMPLETED`, `exit_code=0:0` | validated | met |
| 12 | `render_potj16.py` on a compute node: 180+ dpi, 1x5 locked-camera layout, 20 mm bar every panel, `Pot_J_Piece_01` highlighted, `X/21` and J01 seams per panel | report job `35861740`, `renders/Pot_J_handle_deleted_comparison.png` (`4860x1188`, 2317190 bytes); meshes posed by `T_<p-1>to_<p-1>.txt`, panels anchored on Piece 3, assertion `max_panel_diff_mm = 56.46 > 10.0` | met |
| 13 | `evidence/renders.tsv` tab-delimited with the relative path | validated | met |
| 14 | staged into `artifacts/surface-parity-16/` | `evidence/` (5 tsv), `renders/` (png), `logs/run_status.txt` | met |
| 15 | no change to `sfs_axes/`, `mesh_processing_headless.cpp`, `Data/`, `intent/`, `scripts/`, other tickets/scripts | `git status` / `git diff --stat` on the branch | met |
| 16 | write-back, `Status: ready-for-review`, stop (no merge, no `main`, no worktree close) | this section; branch only | met |

### Caveats

- One pot, one corpus, 21 joins: the `17/21` ceiling is Pot J-specific and the 16-vs-17 difference is one join (`6-11`), so treat the gap between the control and the handle-deleted arms as one seam, not a general advantage.
- `sherds_ok` in `potj_assembly16.tsv` is the `acc305` sherd-accuracy numerator (`8/11`, `9/11`, ...; the project convention used by Tickets 09 and 13). `score305`'s own piece block reads `FAIL` on all 11 pieces even for the positive control (piece angles 176-179 deg), so it is not used for that column; both `score` and `acc` files stay in `out/score/`.
- `Pot J 09` is unscored and off; `Pot J 12` is paper-excluded but inside the 11-piece denominator; `Pot J 01`'s interior breakline measures the input, per `SfSpp_preprocessing/AGENTS.md`.
- `renders.tsv` lost its commas as a `.tsv` hygiene fix in job `35859454`; job `35861740` rewrote it together with the corrected picture.
