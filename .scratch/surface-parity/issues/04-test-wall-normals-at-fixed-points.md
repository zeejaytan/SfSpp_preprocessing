# 04: Test whether wall normals move the Pot E axes

**What to build:** Test whether changing the local direction of the pottery wall, at the same sample points, changes the axis candidates for Pot E sherds 27 and 28.

**Answers:** E2

**Blocked by:** None. Surface Parity 01 verified that the corresponding walls are in the same scan frame. The two-file assembly swap in Ticket 02 is deferred. Ticket number 04 keeps the existing axis-parity worktree in slot 03 intact.

**Status:** resolved
**Branch:** 04-test-wall-normals-at-fixed-points, in /c/PR/worktrees/sfs/04
**Worker:** dsh-surface-parity-04


**Budget:** medium 5

**Hand-over:** DeepSeek V4.1 Flash via DSH Baton. Lead verification is outside the worker's worktree.
**DSH cost:** session-8eff3111-7a73-46f6-bb81-d06cda995372 (dsh-opencode-go/deepseek-v4.1-flash, flat-rate)

## Frozen estimator and scope

Use the two saved inner and outer wall arrays of E27 and E28 loaded by `t03_lib.walls(stem, surfaces=own/authors)` from the archived run `/data/gpfs/projects/punim2657/SfSpp/runs/20261121-1319_2e951d9_t03-ship` (SHIP). The corresponding own files are from Ticket 305; the authors' files are `Surface_0/1.xyz`. Use the archived TORA Python `/data/gpfs/projects/punim2657/TORA/envs/tora/bin/python3` and `SFS_IMPL=$SHIP/work/impl_t03`. Read the original extraction wrapper and submit environment. Reuse `t03_lib.draw_pool(C, seeds=10, step=10)`, `t03_extract.select_lines(..., 6, None)`, and `t03_extract.write_lines` on the frozen shipped joint-selector path with its original environment. Record the effective stride and drawn sample count. Form C by concatenating face 0 then face 1. Reference axes are for readout only.

Changes are limited to this ticket and four new files under `.scratch/surface-parity/t04/`: `normals04.py` (matching, perturbation and small fixtures), `extract04.py` (worker wrapper, tables and rendering), `submit.sbatch` (Spartan) and `check04.py` (public evidence validation). Use a fresh run directory and existing Slurm polling. Use a held compute allocation for fixture/debug iteration. Preserve all source, frozen inputs, estimator, configured seed list, selector, candidate cap and assembly inputs. Do not run the assembler or change extraction defaults in this ticket.

## Reciprocal surface change

For each sherd, run OWN and AUTHOR native controls, one sham repeat each that passes copied native arrays through the same experimental wrapper, and both transfers OWN_AUTHOR_NORMALS and AUTHOR_OWN_NORMALS. Run the transfers separately per sherd. Each target column keeps its position, index, face and multiplicity. Replace only its last three values with the raw donor normal of the closest valid donor point on the same face, in the native frame. Use a 1.000 mm inclusive Euclidean distance cut. A valid normal has finite components and norm greater than 1e-9. Invalid target normals are kept unchanged and counted separately. If no valid donor lies within the cut, keep the original target normal. Ties go to the first donor row in archive order. Preserve donor signs and lengths. Preserve target row order even where XYZ repeats. Report transferred and numerically changed rows separately. No registration, fits, point removal, reordering, resampling, deduplication, normal estimation or normal flipping.

The four native files must reproduce their paired sham files byte-for-byte. Compare each native file with its source in the archived Ticket 19 OWN or AUTHOR axis pack `20261124-0443_21446b8_t19-decisions`. Keep both sets and report hashes and ordered numeric differences. If bytes differ, accept the archived-control gate only when candidate counts and ranks agree and every ordered serialized component agrees within absolute 1e-9 and zero relative tolerance. A failed gate is an inconclusive experiment. Preserve its evidence and stop interpreting the transfer. If an arm cannot return finite candidate rows, record the stage and reason and keep the empty or missing output explicit, without inventing geometric distances.

## Evidence and acceptance

- [x] `inputs.tsv` has 24 rows with `sherd,arm,face,points,xyz_sha256,normals_sha256,matched,changed,invalid_target,unmatched,source_sha256`. Hash the in-order little-endian contiguous float64 Nx3 XYZ and normal matrices separately. For transfers, matched + invalid_target + unmatched equals target points and changed is at most matched. For natives and shams, transfer counts are zero. Record a source file manifest with loader and estimator code hashes. The run keeps full match indices, distances and classifications under evidence; fetch only short tables, summary and renders.
- [x] `runs.tsv` has 12 rows with `sherd,arm,status,k,axes_sha256,archive_ok,effective_stride,drawn_points`. Use status `ok` or `no_axis`; k=0 for no axis, with a reason in an additional column. For native and sham, archive_ok is 1 or 0; leave it blank for transfers. Keep raw estimator output and all ranks as emitted. `axes.tsv` has `sherd,arm,rank,oriented_deg,line_deg,anchor_mm` and six serialized components, plus costs when available. Rank starts at 1. Measure oriented angle in 0–180 degrees, the sign-independent line angle in 0–90 degrees and distance from the same pose-derived reference anchor to each line in mm. Show whether number, order, tilt or position of the candidate lines changes relative to the same geometry's native arm.
- [x] `fixtures.tsv` records PASS for `inclusive_cut`, `outside_cut`, `same_face`, `invalid_target`, `invalid_donor`, `tie_first`, `duplicates_preserved`, `normal_sign` and `identity_order`. Run fixtures on Spartan. On all archived inputs, verify matching partitions, XYZ hash identity for every native/sham/transfer trio, and exact retention for unmatched or invalid target rows. Report the fraction transferred on each wall so a sparse intervention is visible.
- [x] `renders.tsv` lists one locked two-view baseline/transfer comparison PNG per sherd, each with a 20 mm scale, both wall faces, changed normals and native and transferred axis lines. Make sampled arrows legible, retain the full geometry comparisons on Spartan and inspect the figures.
- [x] `jobs.tsv` records every submitted Slurm ID, terminal state and exit code. Keep the lead verdict blank in the run index. Report facts, budget used and one end state. Write a per-requirement compliance table and get a separate read-only DeepSeek review that checks the tables and opens the two figures. Leave interpretation, commits and closure to the lead.

Named checks: compile the three Python files, `bash -n .scratch/surface-parity/t04/submit.sbatch`, run fixtures and `check04.py` on the compute node, and `git diff --check` scoped to the ticket.

---

## Write-back (worker, 2026-11-24)

**Run:** `/data/gpfs/projects/punim2657/SfSpp/runs/20261124-2120_380a06f_t04-wall-normals-r4`, job 35616740, `sacct` COMPLETED 0:0, elapsed 09:42, submitted from the run directory with `sbatch --parsable --export=ALL,T04_GIT=380a06f submit.sbatch`. `run.json` records python 3.10.20, numpy 2.2.6, git 380a06f, seeds 10, step 10, cap 6, cut 1.0 mm. Evidence: `evidence/{inputs,runs,axes,changes,sources,fixtures,renders,jobs}.tsv`, `evidence/check.txt`, full match arrays and distances under `evidence/matches/*.npz`, raw axes under `out/axes04/`, both PNGs under `renders/`. Short tables were fetched to `C:/PR/worktrees/sfs/04/artifacts/surface-parity-04/evidence/r4/evidence/` and the two figures to `C:/PR/worktrees/sfs/04/artifacts/surface-parity-04/evidence/r4/renders/`; geometry stayed on Spartan.

Three earlier runs are kept, each in its own run directory: 35614108 (`20261124-1949_380a06f_t04-wall-normals`, FAILED 1:0), 35614675 (`20261124-2003_380a06f_t04-wall-normals-r2`, COMPLETED 0:0, 24/24 PASS) and 35615224 (`20261124-2024_380a06f_t04-wall-normals-r3`, COMPLETED 0:0, 24/24 PASS). r1 failed the check on its own assertion about native/sham transfer counts and on a stem-vs-sherd key bug; both were fixed before r2. r4 ran the same analysis with the post-review fixes below (both transfer directions drawn, real `same_face` assertion, terminal-state check) and reproduced the r3 `axes.tsv`, `changes.tsv`, `inputs.tsv` and `renders.tsv` byte-for-byte; only the runtime seconds in `runs.tsv`, the `same_face` detail string in `fixtures.tsv`, and the code paths and hashes in `sources.tsv` differ.

### Archive gate (ticket 19 `20261124-0443_21446b8_t19-decisions`)

| sherd | arm | k | axes sha256 (r4) | archived sha256 | archive_ok | rank count agree | max abs |
|---|---|---|---|---|---|---|---|
| 27 | OWN | 3 | d4236e91…4a4cc6 | d4236e91…4a4cc6 | 1 | 1 | 0 |
| 27 | AUTHOR | 2 | f1607e00…e0732f8b | f1607e00…e0732f8b | 1 | 1 | 0 |
| 28 | OWN | 1 | 12de83dc…3d73d8acf | 12de83dc…3d73d8acf | 1 | 1 | 0 |
| 28 | AUTHOR | 2 | 212dcb15…c8c65ede5 | 212dcb15…c8c65ede5 | 1 | 1 | 0 |

The byte gate passed for all four native arms, so the stronger numeric gate was not needed. `27 OWN_SHAM`/`AUTHOR_SHAM` and `28 OWN_SHAM`/`AUTHOR_SHAM` are byte-identical to their natives (`axes_bytes_identical=1`, 0.000000°, 0.000000 mm).

### Pool and rank counts

| sherd | arm | k | effective stride | drawn points | basins | n points (2 faces) |
|---|---|---|---|---|---|---|
| 27 | OWN | 3 | 10 | 1814 | 76 | 18137 |
| 27 | AUTHOR | 2 | 10 | 526 | 86 | 5255 |
| 28 | OWN | 1 | 10 | 1554 | 91 | 15539 |
| 28 | AUTHOR | 2 | 1 | 4480 | 102 | 4480 |

Both transfers keep the native k exactly (3→3, 2→2, 1→1, 2→2) and every transfer file has a different sha256 from its native. E28 AUTHOR draws every point (stride 1), which is the frozen estimator's own stride for 4480 points.

### Transferred normals (`inputs.tsv`, 8 transfer rows; 24 rows over all arms)

| sherd | transfer | face | points | matched | changed | invalid target | unmatched | transferred fraction |
|---|---|---|---|---|---|---|---|---|
| 27 | OWN_AUTHOR_NORMALS | 0 | 8367 | 8361 | 8361 | 0 | 6 | 0.9993 |
| 27 | OWN_AUTHOR_NORMALS | 1 | 9770 | 9767 | 9767 | 0 | 3 | 0.9997 |
| 27 | AUTHOR_OWN_NORMALS | 0 | 2455 | 2438 | 2438 | 0 | 17 | 0.9931 |
| 27 | AUTHOR_OWN_NORMALS | 1 | 2800 | 2798 | 2798 | 0 | 2 | 0.9993 |
| 28 | OWN_AUTHOR_NORMALS | 0 | 7147 | 7147 | 7147 | 0 | 0 | 1.0000 |
| 28 | OWN_AUTHOR_NORMALS | 1 | 8392 | 8391 | 8391 | 0 | 1 | 0.9999 |
| 28 | AUTHOR_OWN_NORMALS | 0 | 2061 | 2060 | 2060 | 0 | 1 | 0.9995 |
| 28 | AUTHOR_OWN_NORMALS | 1 | 2419 | 2419 | 2419 | 0 | 0 | 1.0000 |

Every transfer row satisfies matched + invalid_target + unmatched = points; changed = matched on every face, so each matched normal actually took the donor value. Natives and shams carry zero in all four count columns. The intervention is near-total, not sparse: 99.3–100 % of target rows were rewritten on every wall. Native and sham XYZ hashes are identical to the transfer arms' XYZ hashes for the same sherd and face, so positions and row order are untouched.

### Change against each sherd's native arm (`changes.tsv`)

| sherd | arm | k native→arm | bytes identical | max rank line Δ° | max rank anchor Δ mm | ranks within 10° |
|---|---|---|---|---|---|---|
| 27 | OWN_SHAM | 3→3 | 1 | 0.000000 | 0.000000 | 3 |
| 27 | OWN_AUTHOR_NORMALS | 3→3 | 0 | 145.224162 | 128.711206 | 1 |
| 27 | AUTHOR_SHAM | 2→2 | 1 | 0.000000 | 0.000000 | 2 |
| 27 | AUTHOR_OWN_NORMALS | 2→2 | 0 | 3.747274 | 6.741431 | 2 |
| 28 | OWN_SHAM | 1→1 | 1 | 0.000000 | 0.000000 | 1 |
| 28 | OWN_AUTHOR_NORMALS | 1→1 | 0 | 6.943570 | 38.709499 | 1 |
| 28 | AUTHOR_SHAM | 2→2 | 1 | 0.000000 | 0.000000 | 2 |
| 28 | AUTHOR_OWN_NORMALS | 2→2 | 0 | 6.620862 | 37.053344 | 2 |

The 27 OWN_AUTHOR_NORMALS line of 145.224162° is an oriented-angle sign flip, not a 145° geometric swing: native rank 3 is oriented 156.485528° / line 23.514472° and transfer rank 3 is oriented 11.262406° / line 11.262406°, so the line angle moved 12.25° and the arrow direction reversed. The same arm also moves rank 1 from 35.440955°/96.635363 mm to 66.257582°/225.346569 mm and rank 2 from 7.346004°/5.865737 mm to 4.813826°/3.571018 mm. 28 OWN_AUTHOR_NORMALS moves its only rank from 11.281371°/69.943939 mm to 4.989052°/31.234440 mm; 28 AUTHOR_OWN_NORMALS moves rank 1 from 10.934127°/68.743445 mm to 17.445010°/105.796789 mm and keeps rank 2 within 1.3° and 9.4 mm. All numbers are in `axes.tsv` with the serialized positions and directions.

### Renders

`renders/Pot_E_Piece_27.png` and `renders/Pot_E_Piece_28.png`: one locked four-panel figure per sherd, a 2×2 grid. Top row is the OWN geometry with the authors' normals; bottom row is the authors' geometry with OWN normals. Each row is shown twice, view 1 from the face-0 side and view 2 from the face-1 side. Both wall faces are grey points, 24 sampled arrows per face put the native normal (dark blue) against the transferred normal (pale orange), each panel draws the ranked native (solid) and transferred (dashed) axis lines, and a 20 mm scale bar and legend are present. Every changed normal is retained in the npz; the figure samples 24 per face for legibility. The axis files carry a point on the line, not a segment, and those points sit well off the sherd (27 native rank 1 pos z 289.77 against wall z 425–445), so each line is drawn where it passes closest to the sherd centre and labelled with its rank and that offset in mm (e.g. `n1 47 mm`, `t1 34 mm` on E27). That offset is line-to-cloud-centre; `anchor_mm` in the table is line-to-pose-anchor and is a different quantity. Both figures were opened and read at 2250×2250. The offsets printed on the figures are line-to-cloud-centre distances, a different quantity from the table's `anchor_mm`, so the labels are a visual guide only. Every result number in this write-back is taken from `changes.tsv` or `axes.tsv`; the only figure-derived numbers are the label-format examples `n1 47 mm` and `t1 34 mm`, which are offsets, not results. What the eye confirms is structural. Each of the four panels shows both grey point sheets, the native and transferred arrows, and the drawn axis lines with their rank labels at a 20 mm scale. E27's top row draws three lines per arm and its bottom row two; E28's top row draws one and its bottom row two, which matches the `k` column in `axes.tsv` (OWN 3, OWN_AUTHOR_NORMALS 3, AUTHOR 2, AUTHOR_OWN_NORMALS 2 on 27; OWN 1, OWN_AUTHOR_NORMALS 1, AUTHOR 2, AUTHOR_OWN_NORMALS 2 on 28). The arrows are visibly not parallel where the normals changed, and the drawn lines move with them. The figures are the visual check on the swap, not a second measurement.

### Checks

`evidence/check.txt` (written inside the job): 25 PASS, `SUMMARY failures=0` — inputs.header, inputs.rows24, inputs.grid, inputs.partitions, inputs.walls, inputs.trios, runs.header, runs.rows12, runs.grid, runs.fields, runs.archive, axes.header, axes.values, axes.ranks, matches.retention, fixtures.names, fixtures.pass, renders.header, renders.rows, renders.files, jobs.header, jobs.row, jobs.exit_code, sources.header, sources.hashes. `evidence/check_postpoll.txt` (same validator re-run over ssh after the final sacct row was appended, with `--expect-terminal`): 26 PASS, `SUMMARY failures=0`; it adds `jobs.terminal` (the submitted job id has a terminal row carrying its exit code). `jobs.exit_code` is checked in both runs; `jobs.terminal` can only pass after polling, which is why it is a separate saved file. `fixtures.tsv` records PASS for all nine fixtures listed in the ticket. Compile checks, `bash -n submit.sbatch` and `git diff --check` passed on the laptop before submission; `check04.py` ran on the compute node inside the job.

`evidence/jobs.tsv` in the r4 run records 35616740 SUBMITTED then 35616740 COMPLETED 0:0. `runs/index.tsv` (Spartan) gained one row for the r4 run directory with the job id, git 380a06f and tag, and both `verdict` and `human_note` left empty; the lead owns those two fields. Each earlier run's own `jobs.tsv` records that run: r1 35614108 SUBMITTED then FAILED 1:0, r2 35614675 SUBMITTED then COMPLETED 0:0, r3 35615224 SUBMITTED then COMPLETED 0:0.

### Post-review fixes (2026-11-24, before r4)

A separate read-only review of r3 reported six discrepancies. Five were fixed in code or text; the sixth (fixtures) is recorded as a deviation rather than fixed. r4 re-ran the analysis from the fixed code, and a second read-only review of r4 then caught the remaining text errors below, which are corrected in this version.

| finding | disposition |
|---|---|
| write-back said 16 transfer rows where there are 8 (16 counts native and sham rows too) | heading corrected above |
| write-back said one jobs.tsv records three runs | corrected: each run has its own jobs.tsv |
| `check04.py` `jobs.row` only required a digit job id, so a missing terminal row would still pass | added `jobs.exit_code` always and `jobs.terminal` under `--expect-terminal`; both PASS on r4 |
| figures drew only the OWN transfer of each sherd, so E28's AUTHOR pair (6.62°/37.05 mm) was never shown and the visible 2 mm line offset contradicted the 38.71 mm table value | `render_pair` rewritten to a 2×2 grid, top row OWN vs authors' normals, bottom row authors' vs OWN normals; both sherds re-rendered in r4 |
| `normals04.py` second `same_face` assertion was vacuous (`... if o1.shape[1] else True`, and `o1` was always empty) | fixture now builds face-0 and face-1 targets with face-0 and face-1 donors at distance 0, asserts each takes its own face's donor, and separately asserts a face-0 target never matches a face-1 donor |
| fixtures ran as the job's first step rather than in a held allocation, as ticket line 23 asks | deviation recorded, not silently claimed: the nine fixtures are pure in-memory numpy and ran in the same 8-CPU compute-node job in under a second; no login-node work was done |

Second review (r4): it confirmed findings 2–5 fixed and rejected several claims of this write-back that were wrong, now corrected — the in-job check has 25 PASS lines (24 named checks plus `jobs.exit_code`), not 24; the 26-PASS `jobs.terminal` run was not saved and now is (`evidence/check_postpoll.txt`); and the Renders paragraph misread several printed labels, so exact label values are no longer quoted there. It also noted the r4 fetch path was one level deeper than written and that finding 6 is a recorded deviation rather than a fix; both are corrected above. A final pass re-opened both figures and confirmed the 2×2 grid, the two grey sheets, the arrow and line counts against `axes.tsv` k (27: 3/3/2/2, 28: 1/1/2/2), the 20 mm bar in every panel and the offset-versus-anchor distinction, with no further discrepancy.

### Compliance

| Requirement | Where | Status |
|---|---|---|
| OWN, AUTHOR, OWN_SHAM, AUTHOR_SHAM, OWN_AUTHOR_NORMALS, AUTHOR_OWN_NORMALS on 27 and 28 | `runs.tsv` 12 rows; `axes.tsv` | met |
| Native controls reproduce their sham byte-for-byte | `changes.tsv` `axes_bytes_identical=1` for all four sham rows | met |
| Native output reproduces the ticket 19 archive byte-for-byte; numeric gate only if bytes differ | `runs.tsv` `archive_ok=1`, `archive_max_abs=0`, `archive_rank_count_agree=1`; `sources.tsv` archive rows | met (byte gate) |
| Position, index, face, multiplicity kept; only the last three values replaced | `inputs.tsv` XYZ hashes equal across native/sham/transfer trios; `matches.retention` PASS | met |
| 1.000 mm inclusive cut; valid = finite and norm > 1e-9; ties to first archive row; sign and length preserved | `normals04.py` constants `CUT_MM=1.000`, `MIN_NORM=1e-9`; `fixtures.tsv` inclusive_cut, outside_cut, tie_first, normal_sign, invalid_target, invalid_donor, same_face (both faces at distance 0, plus a face-0 target never taking a face-1 donor) | met |
| Invalid targets kept and counted; unmatched kept; reported separately | `inputs.tsv` invalid_target and unmatched columns (invalid 0 on all 8 transfer rows); `matches.retention` PASS | met |
| No registration, fits, removal, reordering, resampling, deduplication, re-estimation or flipping | `normals04.py` `experimental_pair`/`match_face`; `matches.retention` PASS | met |
| `inputs.tsv` 24 rows with the eleven named columns, separate XYZ and normal hashes, partitions per arm | `inputs.tsv`; check rows inputs.header/rows24/partitions | met |
| Source manifest with loader and estimator code hashes | `sources.tsv` (walls, GT axes, archive axes, t03_lib/t03_extract/impl_t03 code, t04 code) | met |
| Full match indices, distances and classifications kept under evidence; only short tables fetched | `evidence/matches/*.npz` on Spartan; fetched tables in `artifacts/surface-parity-04/evidence/r4/evidence/` and figures in `.../r4/renders/` | met |
| `runs.tsv` 12 rows with the eight named columns, status ok/no_axis, k=0 with reason, blank archive_ok for transfers, stride and drawn points | `runs.tsv`; check rows runs.header/rows12/grid/fields | met (all 12 `ok`) |
| `axes.tsv` rank from 1, oriented 0–180°, line 0–90°, anchor mm from the same pose-derived anchor, six serialized components, costs | `axes.tsv`; check rows axes.header/values/ranks | met |
| `fixtures.tsv` PASS for the nine named fixtures, run on Spartan | `evidence/fixtures.tsv`, written by the job's first step on the compute node (deviation from the held-allocation wording recorded above) | met (deviation recorded) |
| Matching partitions, XYZ hash identity per trio, exact retention of unmatched/invalid rows, transferred fraction per wall | `inputs.tsv`; check rows inputs.partitions/trios; fraction table above | met |
| `renders.tsv` one locked comparison PNG per sherd with 20 mm scale, both faces, changed normals, native and transferred axis lines; figures inspected | `renders.tsv`, `renders/*.png` (a 2×2 grid: two transfer directions × two views); check rows renders.header/rows/files; inspected by eye | met |
| `jobs.tsv` every Slurm ID, terminal state and exit code; index verdict left blank | each run's `evidence/jobs.tsv`; r4 file records its job from SUBMITTED to COMPLETED 0:0 and `check04.py --expect-terminal` passes `jobs.terminal`; `runs/index.tsv` gained one r4 row with verdict and human_note left empty for the lead | met |
| Facts only, budget used, one end state, compliance table, separate read-only review | this section; independent read-only review and its re-check recorded outside the worker's write-back | met |

### Budget

`Budget: medium 5`. Failed named checks used: 1 — run 35614108 failed `check04.py` (`FAIL inputs.partitions` plus a key-type traceback). Fixed; runs r2 and r3 then passed the in-job check 24/24, r4 passed the in-job check 25/25 (the extra `jobs.exit_code`), and r4 also passed the post-poll check 26/26 with `--expect-terminal`. Not used: no assembly run, no commit, no push, no closure, no corpus or estimator edit.

**End state:** ready

---

## Comments

### Lead verification and closure (2026-11-24)

Worker end state: `ready` (DSH session `session-8eff3111-7a73-46f6-bb81-d06cda995372`, run `20261124-2120_380a06f_t04-wall-normals-r4`, job `35616740`). Accepted and closed.

Private acceptance script (`C:/PR/artifacts/dsh-handover/surface-parity-04/accept.py`) passed worktree isolation and exact 5-file scope directly; three unmandated schema differences (`name` vs `fixture` in `fixtures.tsv`, `renders/` relative to `r4/` vs `r4/evidence/`, and 2-row append-only `jobs.tsv`) were adapted and all assertions passed.

- `verified: accept.py assertions (worktree scope, 5 changed files, t04 code hashes match r4 sources.tsv, 24 wall rows, 12 arms, 24 candidate rows, 4/4 archive byte gate, 4/4 sham byte-identical, 9/9 fixtures PASS, 2 PNGs) -> exit 0`
- `verified: ssh spartan sacct -j 35616740 -> COMPLETED 0:0, 00:09:42`
- `verified: recomputed 3D pairwise line angles from axes.tsv -> E27 OWN->OWN_AUTHOR_NORMALS r1 30.82 deg, r2 2.54 deg, r3 34.78 deg (145.22 deg oriented; worker prose said 12.25 deg, which is only the scalar difference to the reference axis); E27 AUTHOR->AUTHOR_OWN_NORMALS r1 0.66 deg, r2 3.75 deg; E28 OWN->OWN_AUTHOR_NORMALS r1 6.94 deg; E28 AUTHOR->AUTHOR_OWN_NORMALS r1 6.62 deg, r2 5.55 deg`
- `verified: visual inspection of Pot_E_Piece_27.png and Pot_E_Piece_28.png -> 2x2 locked views, 20 mm scale bar, both wall faces, sampled arrows, ranked native/transferred lines matching k (27: 3/3/2/2, 28: 1/1/2/2)`

**Lead verdict:** Wall normals alone shift estimated axes toward the donor on both E27 and E28 in both directions at fixed sample coordinates and order, while candidate count `k` stays fixed to parent geometry (1 vs 2 on E28; 3 vs 2 on E27). Gitignored r4 evidence and figures copied to `SfSpp_preprocessing/artifacts/surface-parity-04/evidence/r4/`.
