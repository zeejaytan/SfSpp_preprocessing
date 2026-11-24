# 01: Isolate E27’s surface-to-axis effect at join 27–28

**What to build:** Show where our E27 and E28 surfaces differ from the authors’ surfaces, and test whether the resulting difference in E27’s axis file is enough to remove or recover join 27–28.

**Answers:** E2

**Blocked by:** none. Uses the saved axis-parity Ticket 19 assembly inputs and Ticket 03 surface and axis evidence.

**Status:** resolved — reciprocal axis-file diagnostic
**Branch:** 01-isolate-e27-surface-axis-effect, in /c/PR/worktrees/sfs/01
**Worker:** dsh-surface-parity-01


**Budget:** medium 5

**Hand-over:** DeepSeek V4.1 Flash via DSH Baton. Lead acceptance lives outside the ticket worktree.

[Spec](../spec.md)

## Frozen inputs and files

Edit only this ticket and new experiment files under `.scratch/surface-parity/t01/` in the assigned worktree. Use `surface01.py` for measurement and rendering, `stage01.py` for axis-file staging and hash checks, `cell01.sbatch` for assembly and `report01.py` for summarising saved outputs. Store run outputs on Spartan and fetch only tables, logs and PNGs to the project’s ignored artifacts. Preserve corpus and application source. Follow the workspace run-index and Slurm polling rules. The lead fills the verdict.

On Spartan set `P=/data/gpfs/projects/punim2657`, `T19=$P/SfSpp/runs/20261124-0443_21446b8_t19-decisions`, and `SHIP=$P/SfSpp/runs/20261121-1319_2e951d9_t03-ship`. Load `Pot_E_Piece_27` and `Pot_E_Piece_28` on each surface source via `SHIP/work/t03_lib.py:walls(stem, surfaces)` with `surfaces=own` and `surfaces=authors`. The own source resolves to the Ticket 305 Pot E `.S0` and `.S1` files. The authors’ source resolves through the archived loader to the released surfaces. Use the archived TORA Python and `PYTHONPATH="$SHIP/work/impl_t03:$SHIP/work"`. Log the actual four file paths per sherd, hashes and load dimensions. Do not use the assembler’s mounted walls in place of the estimator’s wall inputs.

## 1. Compare the surfaces

- Work in native coordinates in millimetres. Use the frozen mesh and released pose as independent landmarks for both clouds. Show both faces on the same mesh from the same two views at a 20 mm scale. Check native-frame alignment without ICP or any estimated registration. Record the signed orientation of corresponding normals. Keep same-face and crossed-face comparisons separate. If correspondence or frame is indeterminate, report that and do not attribute any feature difference.
- For each sherd, face and direction between sources, use a same-face nearest-neighbour query. At 1 mm and 2 mm report counts and fractions paired and unpaired. Report point-to-point p50/p95 in mm and within-cloud non-self nearest-neighbour p50/p95 in mm. Keep exact duplicate counts separately and measure spacing on distinct XYZ. For matches within 1 mm report signed normal-angle p50/p95 in degrees, the fraction above 90°, and the count of invalid normals. A zero valid denominator gives a blank metric with a zero count.
- To avoid a dense patch concealing sparse coverage, also report occupied 2 mm XYZ cells on the shared fixed grid `floor(xyz_mm / 2)` per face, with own-only, author-only and shared counts. Use the point correspondence overlay to distinguish a sampling grid effect from a real gap. Render shared and unmatched points separately with fixed colours, and identify any differences near the fixed 27–28 fracture line. These are observations and may remain correlated.
- Compare every saved E27 and E28 candidate in `T19/axes/OWN` and `T19/axes/AUTHOR` and the released `Axes` separately. Row layout is position then direction. Report signed and unsigned angles, row order, and the distance in mm from the pose-derived reference axis anchor to each line. Use reference axes only in the readout. Preserve every packaged axis byte in the assembly trial.

## 2. Test E27 with all other inputs fixed

Stage four axis directories of 31 sherd files. Use exact source bytes from `T19/axes/{OWN,AUTHOR}`. The two hybrids change only `Pot_E_Piece_27_Axis.xyz`. In the own background use the authors’-surface E27 file, and in the authors’-surface background use our E27 file. Call the hybrids `OWN_E27_AUTHOR` and `AUTHOR_E27_OWN`. Preserve E28’s bytes relative to the corresponding background. If the E27 files are identical, report the hashes and do not submit redundant swap arms.

Use the archived `$T19/work/t19/build/Hierarchy-T19` with SHA-256 `0ba6d10fa6885a67a92a92bb37ec7c138f25f32622368bfcafb5bfae3fa637c9`. There is no build step. Fork the archived `$T19/work/t19/cell19.sbatch` into `cell01.sbatch`. Set `WORK="$T19/work/t19"`, `WANT_SHA` to the hash above, and `RUN` to the new run directory. Use the original Ticket 03 Pot E fixed tree `$P/SfSpp/runs/20261121-1319_2e951d9_t03-potE/trees/E_K3R1/E/MM` for `DATA` and its `Ground Truth` for `GT` in all cells. Bind `$RUN/axes/$ARM` read-only as the sole input that varies. Keep the archived Apptainer executable, SIF, `/panel` bind, input binds, environment, container hash check, `exec /panel/build/Hierarchy-T19 31` and scorer invocation. Set `T18_TRACE=/Dataset/SfS_pp/Result/t18_raw.jsonl` and `T19_TRACE=/Dataset/SfS_pp/Result/t19_decisions.jsonl`. Retain fresh writable Result and logs per cell. Change archived error exits to nonzero for duplicate result directories, input hash failures, missing poses, container failures and scorer failures. No scored rows for unusable cells. Use exact commands below from the prepared run directory and poll every returned ID:

```bash
for arm in OWN OWN_E27_AUTHOR AUTHOR AUTHOR_E27_OWN; do sbatch --parsable "$RUN/submit.sbatch" "$arm" 1; done
# Poll wave 1 to terminal states before submitting wave 2.
for arm in AUTHOR_E27_OWN AUTHOR OWN_E27_AUTHOR OWN; do sbatch --parsable "$RUN/submit.sbatch" "$arm" 2; done
```

Verify a stable positive AUTHOR control (62/62 twice) and that OWN loses 27–28 twice before interpreting the hybrids. Keep the released Ticket 19 62/62 twice as a benchmark record. For each cell read 27–28’s direct-query, first emitted interval and pair-fit events from the raw trace, and score the exported pose with the pinned scorer. Include the other two E28 joins as secondary rows and tally all 62 outcomes to identify collateral changes. Report no interval as a count of zero and leave its event ID blank. A final scoring result can be valid when a direct interval never forms. If a control fails, retain all evidence and label the experiment inconclusive. Do not report graph-pruning attribution.

## Acceptance

- [ ] Both walls on E27 and E28 have input hashes, matched/unmatched and valid/invalid denominators, same-frame surface measurements, candidate comparisons and inspected locked renders.
- [ ] Each executed cell records terminal Slurm State/ExitCode, a matching host and container executable hash, complete before/after input manifests, and its scorer status. Reciprocals differ from their parent at E27 alone. Failed controls or identical donor bytes are visible, and neither can be presented as a successful isolation.
- [ ] `replay.tsv` records arm, repeat, executable hash, execution status, scored joins and sherds. `seams.tsv` records the 62 distinct reference joins per scored cell with relative rotation error in degrees, offset in millimetres and scorer flag. `matching.tsv` gives query, interval and fit counts and first event IDs for the three target joins. `surfaces.tsv`, `axes.tsv`, `inputs.tsv`, `jobs.tsv`, `renders.tsv` and the raw traces carry the provenance above. Render scored 27–28 poses from each repeat against the fixed reference with a locked camera and a scale bar, including missing or off-frame cases. Judge the score using the pinned scorer, with the image for physical inspection.
- [ ] Write a per-requirement self-compliance table with met/not met and file:line evidence in this ticket. Obtain a separate read-only DeepSeek review with its own compliance table, including inspection of the surface and join renders. End with one end state from the delegation guide. Report the facts and the budget used. Leave interpretation, commits and closure to the lead.

**Worker checks:** `python -m py_compile .scratch/surface-parity/t01/surface01.py .scratch/surface-parity/t01/stage01.py .scratch/surface-parity/t01/report01.py`; `bash -n .scratch/surface-parity/t01/cell01.sbatch`; from the workspace root `python scripts/check_intent_links.py`. Run research measurements on Spartan compute nodes.

## Comments

### Worker report — `dsh-surface-parity-01`, 24 Nov 2026

**Run** `20261124-1431_1233d62_t01-surface-parity` on Spartan (`/data/gpfs/projects/punim2657/SfSpp/runs/`), worktree commit `1233d62`, branch `01-isolate-e27-surface-axis-effect`. Eight cells, four arms × two repeats, one job per cell, submitted in the ticket's wave order (line 41 wave 1, line 43 wave 2, wave 2 only after all four wave-1 jobs were terminal). Evidence is fetched to `artifacts/surface-parity-01/evidence/` (18 tables, 14 renders, plus `logs/` with 35 provenance files — `panel.tsv`, `cell_status.tsv`, `waves.tsv`, `polled.tsv`, `poll_final.tsv`, `sacct_final.tsv`, the axis manifest and swap list, `stage.json`, the executable hash files and both input manifests for every cell); the raw traces stay on Spartan with their sha256, byte and line counts in `traces.tsv`. Turn 2 adds a **supplement directory** — `artifacts/surface-parity-01/supplements/` here and `$RUN/supplements/t01-turn2/` on Spartan — holding the strict acceptance record, the re-made surface figures, the pose-check fixtures and the five new job records; nothing in `evidence/` and nothing in the run's `logs/` was changed by it.

| arm | repeat 1 | State/Exit | wall | node | repeat 2 | State/Exit | wall | node |
|---|---|---|---|---|---|---|---|---|
| OWN | 35601839 | COMPLETED / 0:0 | 00:49:26 | spartan-bm065 | 35604026 | COMPLETED / 0:0 | 00:49:15 | spartan-bm173 |
| OWN_E27_AUTHOR | 35601840 | COMPLETED / 0:0 | 00:39:38 | spartan-bm079 | 35604025 | COMPLETED / 0:0 | 00:40:53 | spartan-bm164 |
| AUTHOR | 35601841 | COMPLETED / 0:0 | 00:45:04 | spartan-bm085 | 35604024 | COMPLETED / 0:0 | 00:48:53 | spartan-bm065 |
| AUTHOR_E27_OWN | 35601842 | COMPLETED / 0:0 | 00:36:13 | spartan-bm137 | 35604023 | COMPLETED / 0:0 | 00:52:13 | spartan-bm065 |

Every cell recorded `ok=1`, `rc=0`, and the same executable hash before and after the run (`0ba6d10fa6885a67a92a92bb37ec7c138f25f32622368bfcafb5bfae3fa637c9`, i.e. the saved Ticket 19 binary, never rebuilt) — `artifacts/surface-parity-01/evidence/replay.tsv:2-9`, `jobs.tsv` for the two report jobs appended from `sacct` after the reduction.

#### 1. What was actually bound at `/Dataset/SfS_pp` (the archived trap)

The archived `inputs19.py` log lists both a fixed-tree `Axes/...` shadow and the real `axes/<ARM>/...` mount. Measured, not assumed:

- The fixed tree's own `Axes/` directory holds **our** candidate axes (E27 `d4236e91…4cc6`, E28 `12de83dc…`), so in every cell the shadow listing is the OWN set. `provenance_axes_shadow.tsv` gives one row per axis path per cell (248 rows): OWN 0/31 rows overridden (shadow = bound = container), AUTHOR 31/31 overridden, OWN_E27_AUTHOR 1/31 (E27 `f1607e00…2f8b` only, so its E28 stays our own `12de83dc…`), AUTHOR_E27_OWN 30/31 (every axis **except** E27, whose row keeps the shadow's own `d4236e91…`, so its E28 becomes the authors' `212dcb15…`). Each hybrid therefore preserves E28 relative to its parent: OWN_E27_AUTHOR keeps OWN's E28 bytes, AUTHOR_E27_OWN keeps AUTHOR's.
- The bind order in `cell01.sbatch:83-90` puts `$RUN/axes/$ARM` over `/Dataset/SfS_pp/Axes` **last**, and an inventory written inside the container (`cell01.sbatch:95-99` → `out/<cell>/container_inputs.tsv`) confirms it: E27/E28 at the container path are `d4236e91`/`12de83dc` in OWN_1, `f1607e00`/`212dcb15` in AUTHOR_1, `f1607e00`/`12de83dc` in OWN_E27_AUTHOR_1, `d4236e91`/`212dcb15` in AUTHOR_E27_OWN_1.
- Each cell binds 187 files — 31 Axes + 31 Breaklines + 62 Surfaces + 31 Mesh + 32 Ground Truth (the graph file included) — `cell01.sbatch:122-124` fails a cell below 187.
- Reciprocal contrast, `reciprocal_inputs.tsv:2-5`: OWN_E27_AUTHOR vs OWN and AUTHOR_E27_OWN vs AUTHOR each differ at exactly one path, `Pot_E_Piece_27_Axis.xyz`, with every other bound input identical, in both repeats.
- The donor bytes differ from the background (`stage01.py:108-111` refuses to run if they do not): E27 OWN `d4236e91…` vs AUTHOR `f1607e00…`; E28 OWN `12de83dc…` vs AUTHOR `212dcb15…`; released E27 `79147a0f…`, released E28 `8cea380f…`.

#### 2. The two E27/E28 walls, in their native frame, no registration

Loaded through the archived loader (`surface01.py:161,177-178` → `SHIP/work/t03_lib.py:walls(stem, surfaces)`); all four paths, sha256, byte counts and load dimensions in `loads.tsv:2-9`.

| piece | face | own points | authors points | paired_fraction_1mm own→auth | own→auth distance p50 / p95 | auth→own distance p50 / p95 | signed normal p50 (own→auth) | invalid normals |
|---|---|---|---|---|---|---|---|---|
| 27 | 0 | 8367 | 2455 | 0.999283 | 0.301 / 0.522 mm | 0.231 / 0.378 mm | −0.24° | 0 |
| 27 | 1 | 9770 | 2800 | 0.999693 | 0.303 / 0.527 mm | 0.236 / 0.374 mm | +0.41° | 0 |
| 28 | 0 | 7147 | 2061 | 1.000000 | 0.303 / 0.537 mm | 0.239 / 0.379 mm | −0.34° | 0 |
| 28 | 1 | 8392 | 2419 | 0.999881 | 0.300 / 0.535 mm | 0.237 / 0.376 mm | +0.35° | 0 |

(`surfaces.tsv:2-9`; the table carries the full brief column list — duplicates on distinct XYZ, spacing p50/p95 on distinct points, unsigned normal p50/p95, fraction above 90°, and the 2 mm cell counts.) Paired fractions at 2 mm are 0.9971–1.0000; the largest single-point distance is 2.63 mm, at an edge. Verified denominators: `invalid_normals` is 0 in every row of this table, so no blank-on-zero case arises on the same-face comparison. The rule is exercised one table away: in `surface_crossed.tsv` piece 28 has `valid_normals` = 0 on both faces from both sources, and its `normal_p50_deg`, `normal_p95_deg` and `normal_fraction_gt90` cells are blank, with the count left visible — the crossed-face pairing has too few usable normals to report an angle. The own clouds carry many exact duplicate rows (own face 0: 3924 duplicates of 8367; the authors' 2455-point cloud: 0) — the measurement uses distinct XYZ for spacing and reports duplicates as a count, so duplication does not inflate the pairing.

Same-frame check (`surface_frame.tsv:2-9`): centroid delta 0.20–0.90 mm, bbox-centre delta 0.16–1.35 mm, nearest frozen-mesh distance p50 0.16–0.29 mm / p95 0.33–0.61 mm, and **1.0** of every cloud inside the mesh bounding box (padded 2 mm). The two sources sit on the same frozen mesh in the same frame, so the comparison needs no ICP. Same-face and crossed-face are kept apart: `surface_crossed.tsv` pairs own face 0 against authors face 1 and the reciprocal, per piece (`surface01.py:232-247`).

Pictures (locked cameras, 20 mm bar, red = own-only, blue = authors-only, grey = shared within 1 mm, filled = face 0, hollow = face 1):

- [surface_piece27_views.png](worktrees/sfs/01/artifacts/surface-parity-01/evidence/renders/surface_piece27_views.png)
- [surface_piece28_views.png](worktrees/sfs/01/artifacts/surface-parity-01/evidence/renders/surface_piece28_views.png)

Both read as one grey surface, because almost every point has a partner within 1 mm: the unmatched counts at 1 mm are 6 own and 17 authors on piece 27 face 0 (fractions 0.000717 and 0.006925), 3 and 2 on face 1, 0 and 1 on piece 28 face 0, 1 and 0 on face 1 (`surfaces.tsv`, `unpaired_1mm` / `unpaired_fraction_1mm`). At print scale those few points are individual markers, not a visible region, so the figure shows a shared surface rather than a mappable difference. In the 15 mm band along the fixed 27–28 fracture line the own wall has 4 unmatched points on piece 27 and 0 on piece 28 (the band panels say so in their own words). On piece 28 the authors' band points sit visibly outside the own band edge — a sampling/edge gap, recorded as a picture, not a measurement. At print scale those few unmatched points are ~1 px markers, so the turn-1 figures show the shared surface rather than a readable difference; the supplement re-render (section 9.2) draws the frozen mesh as a pale plate under the clouds and enlarges every unmatched marker with a legend, with the measurement byte-identical.

#### 3. Joins, matching, and the benchmark record

Score rows are the pinned scorer's (`score305.py`, bar 20.05° / 50 mm). Pieces score 0/31 in every cell (`scores.tsv`, kind=piece), so the joins are what discriminate. `seams.tsv` now carries **all 62 reference joins per counted cell** (496 rows), not only the three named ones; `scores.tsv` carries 744 rows (8×31 pieces + 8×62 joins). One of the eight cells is **unusable** (section 9.1). Its 62 join rows stay in `seams.tsv` and its 31 piece rows in `scores.tsv` as the **historical diagnostic record** and are counted in no acceptance tally below.

| arm | repeat | joins | 27–28 angle / offset | 27–28 pass | 13–28 angle / offset | 28–31 angle / offset |
|---|---|---|---|---|---|---|
| OWN | 1 | 59/62 | 178.597° / 802.099 mm | no | 179.616° / 800.735 mm | 178.836° / 483.777 mm |
| OWN | 2 | 54/62 | 72.679° / 127.070 mm | no | 76.440° / 123.555 mm | 63.337° / 404.529 mm |
| AUTHOR | 1 | 62/62 | 4.624° / 19.641 mm | yes | 1.508° / 11.894 mm | 4.057° / 26.454 mm |
| AUTHOR | 2 | 62/62 | 4.832° / 24.761 mm | yes | 1.706° / 14.650 mm | 3.825° / 23.101 mm |
| OWN_E27_AUTHOR | 1 | 40/62 — **unusable, 28/31 poses** (section 9.1) | blank — no pose exported | no | blank — pieces 18, 28, 31 export no pose | blank |
| OWN_E27_AUTHOR | 2 | 44/62 | 165.904° / 722.006 mm | no | 168.186° / 723.857 mm | 171.834° / 738.700 mm |
| AUTHOR_E27_OWN | 1 | 62/62 | 4.338° / 18.116 mm | yes | 1.242° / 10.077 mm | 3.599° / 23.100 mm |
| AUTHOR_E27_OWN | 2 | 62/62 | 5.024° / 22.734 mm | yes | 1.619° / 12.597 mm | 4.164° / 24.200 mm |

Matching on 27–28, read from the raw trace (`matching.tsv`; query = `stage=query, disp=attempt`, interval = `interval, disp=emitted`, fit = `pair_fit, disp=fit`):

| arm | repeat | queries | intervals | fits | first query / interval / fit event |
|---|---|---|---|---|---|
| OWN | 1 | 468 | 0 | 0 | 3 / — / — |
| OWN | 2 | 447 | 0 | 0 | 3 / — / — |
| AUTHOR | 1 | 636 | 180 | 74 | 7 / 14 / 34 |
| AUTHOR | 2 | 628 | 176 | 73 | 7 / 14 / 34 |
| OWN_E27_AUTHOR | 1 | 244 | 0 | 0 | 7 / — / — |
| OWN_E27_AUTHOR | 2 | 272 | 0 | 0 | 7 / — / — |
| AUTHOR_E27_OWN | 1 | 936 | 25 | 27 | 7 / 4701 / 4723 |
| AUTHOR_E27_OWN | 2 | 936 | 24 | 31 | 7 / 4686 / 4710 |

Zero counts carry a blank event ID, as the ticket requires. The OWN cells' 27–28 line reaches the direct query and stops at `no_interval` before any pair fit; the AUTHOR_OWN hybrid is the other way round — an interval forms late (event ~4700) after a long query phase. The recent Ticket 19 benchmark, re-read from its own score sheets, is `t19_benchmark.tsv`: ORIG 62/62 (27–28 6.545°/40.061 mm and 4.920°/21.457 mm), OWN 59/62 (73.438°/113.177 mm, 170.325°/311.407 mm), AUTHOR 62/62 (4.687°/18.397 mm, 5.045°/17.790 mm), REVERSE 62/62 (4.292°/19.883 mm, 4.793°/21.408 mm); every cell 0/31 pieces.

What the E27 swap did, as the tables record it: at 27–28 the pass/fail was **unchanged in both backgrounds** — OWN background fail (178.597°/802.099 mm; 72.679°/127.070 mm) and OWN_E27_AUTHOR background fail (165.904°/722.006 mm in repeat 2; no pose at all in repeat 1), AUTHOR background pass (4.624°/19.641 mm; 4.832°/24.761 mm) and AUTHOR_E27_OWN pass (4.338°/18.116 mm; 5.024°/22.734 mm). What did change is the rest of the count: whole-pot joins 59/62 → 40/62 (repeat 1, unusable) and 44/62 (repeat 2) on the OWN background, 62/62 → 62/62 on the AUTHOR background; and the 27–28 search availability, intervals 0/0 → 0/0 (OWN background) and 180/176 → 25/24 (AUTHOR background), with fits 74/73 → 27/31 and queries 636/628 → 936/936. No cause is assigned to any of it here.

Two things the reader should not have to discover from the tables:

- **The piece column separates nothing here.** Every cell scores 0/31 pieces, exactly as the archived Ticket 19 sheets do, and the piece rows fail with different magnitudes in different cells (AUTHOR 177.7–180.0° / 345–1088 mm; AUTHOR_E27_OWN 28.4–34.5° / 68–258 mm; OWN repeat 1 48.3–180.0°; OWN repeat 2 24.9–110.2°) — the passing controls fail this check too. So the piece-level comparison could not tell the arms apart even if a reconstruction were right, and it is recorded as a fact about the scorer's piece column, not as a judgement about any cell. The join rows are the only discriminating score in this run.
- **`OWN` repeat 2 also loses five joins that do not touch the 27–28 pair**: 3-24 135.447°/145.139 mm, 5-25 8.739°/56.702 mm, 13-25 8.863°/58.339 mm, 23-24 134.026°/119.434 mm, 25-31 140.720°/736.663 mm — 8 of 62 fail there, not only the three E28 joins (`seams.tsv`). Repeat 1 loses only the three. The archived Ticket 19 `OWN` arm was 59/62 in both repeats, but that arm also varied the walls, so it is not a like-for-like comparison and no attribution is drawn from it.

#### 4. The locked join renders

Twelve join figures, three panels each: the final export for that seam with the moving piece anchored on the seam's first piece (locked camera, 40 mm bar), the fixed reference answer in the same camera, and a whole-pot plan overview. Eight figures are 27–28 and anchor on piece 27; the four secondary E28 figures anchor on piece 13 (13–28) and piece 28 (28–31), as their titles say. `renders.tsv:2-13` records kind, arm, repeat, path, camera centre and half-width, bar length and the labels; one figure per scored cell for 27–28, plus the two secondary E28 seams for the AUTHOR and OWN controls (`renders.tsv:3-4,7-8`).

| figure | what the picture shows | caption |
|---|---|---|
| [OWN_1_27-28](worktrees/sfs/01/artifacts/surface-parity-01/evidence/renders/OWN_1_27-28.png) | piece 27 where it belongs, piece 28 thrown to the lower-left corner, outside the window ("piece reaches outside the locked window") | 178.597° / 802.099 mm fail |
| [OWN_2_27-28](worktrees/sfs/01/artifacts/surface-parity-01/evidence/renders/OWN_2_27-28.png) | same shape of failure, 28 below and left of 27 | 72.679° / 127.070 mm fail |
| [AUTHOR_1_27-28](worktrees/sfs/01/artifacts/surface-parity-01/evidence/renders/AUTHOR_1_27-28.png) | 27 and 28 seated as in the reference panel, seam gap visible | 4.624° / 19.641 mm pass |
| [AUTHOR_2_27-28](worktrees/sfs/01/artifacts/surface-parity-01/evidence/renders/AUTHOR_2_27-28.png) | seated with a slightly wider gap than repeat 1 | 4.832° / 24.761 mm pass |
| [OWN_E27_AUTHOR_1_27-28](worktrees/sfs/01/artifacts/surface-parity-01/evidence/renders/OWN_E27_AUTHOR_1_27-28.png) | piece 27 drawn, panel 1 says "no exported pose recorded for piece 28" | blank, no pose |
| [OWN_E27_AUTHOR_2_27-28](worktrees/sfs/01/artifacts/surface-parity-01/evidence/renders/OWN_E27_AUTHOR_2_27-28.png) | the pair displaced out of position (the 165.904° / 722.006 mm row): the picture reads as mostly translation with some rotation, not a rotation about a shared point | 165.904° / 722.006 mm fail |
| [AUTHOR_E27_OWN_1_27-28](worktrees/sfs/01/artifacts/surface-parity-01/evidence/renders/AUTHOR_E27_OWN_1_27-28.png) | pair seated like the AUTHOR control | 4.338° / 18.116 mm pass |
| [AUTHOR_E27_OWN_2_27-28](worktrees/sfs/01/artifacts/surface-parity-01/evidence/renders/AUTHOR_E27_OWN_2_27-28.png) | pair seated like the AUTHOR control | 5.024° / 22.734 mm pass |

The four secondary figures — [AUTHOR_1_13-28](worktrees/sfs/01/artifacts/surface-parity-01/evidence/renders/AUTHOR_1_13-28.png), [AUTHOR_1_28-31](worktrees/sfs/01/artifacts/surface-parity-01/evidence/renders/AUTHOR_1_28-31.png), [OWN_1_13-28](worktrees/sfs/01/artifacts/surface-parity-01/evidence/renders/OWN_1_13-28.png), [OWN_1_28-31](worktrees/sfs/01/artifacts/surface-parity-01/evidence/renders/OWN_1_28-31.png) — carry their captions in `renders.tsv` and the numbers in `seams.tsv`. I opened the eight 27–28 figures and both surface figures; the read-only review opened all twelve join figures and both surface figures.

#### 5. Failed checks (turn-1 budget: five, used five distinct — six rows, because rows 1 and 2 are the same defect; turn-2 budget: two, none used)

| # | what failed | how it showed | fix |
|---|---|---|---|
| 1 | measure job 35601864 | FAILED 1:0, `KeyError: 2` at `surface01.py:310` as it then stood (that line is now a comment; the corrected expression is `surface01.py:313-314`) — the partner index was computed as `29 - p` instead of `55 - p` for the 27/28 pair | partner fixed to `55 - p`, resubmitted 35601898 (COMPLETED) |
| 2 | report job 35604009 | FAILED 1:0 on the same `KeyError`, before the partner fix reached the reduction | re-submitted after the fix; 35604054 onwards COMPLETED |
| 3 | measure job 35602042 | COMPLETED but wrote the renders to `$RUN/renders` instead of `$RUN/evidence/renders` (the batch default) | `measure01.sbatch` pinned to `--renders "$RUN/evidence/renders"`; PNGs moved; 35602150 re-ran clean |
| 4 | measure job 35602269 | COMPLETED but `surface_crossed.tsv` carried literal `None` strings in numeric cells | `num()` added for every numeric cell; 35602439 COMPLETED with `grep -c None` = 0 |
| 5 | `logs/axes_manifest.tsv` background column | the staged-axis manifest wrote the arm's **own final** hash into `background_sha256` (`stage01.py:95` read `hashes[arm].get(name)`), so `OWN_E27_AUTHOR`'s E27 row claimed background `f1607e00…` when its background is `d4236e91…`. Caught by the read-only review (D1 below), not by a job | `stage01.py:95-97` hashes the background file itself; `stage01.py` re-run 24 Nov 05:43Z regenerated the manifest (`OWN_E27_AUTHOR` E27 sha `f1607e00…` / background `d4236e91…`; `AUTHOR_E27_OWN` E27 sha `d4236e91…` / background `f1607e00…`). The re-run re-copied the same 124 files with the same hashes, so no cell input moved |
| 6 | report job 35607833 (REPORT8) | FAILED 2:0 in 2 s: it was submitted from `$RUN/logs` instead of `$RUN`, so the batched `--output=logs/...` and the relative evidence paths resolved under `logs/` (it created a `logs/logs/` directory) and the reduction died before writing any table. No evidence came from it | resubmitted from `$RUN` as 35607903 (REPORT9, COMPLETED 0:0, 11 s); the stray `logs/logs/` was emptied and removed; `poll_final.tsv` records that job as `1` with the reason, since `slurm_poll.sh` exits 0 on any terminal state |

Not counted in the budget, because each was visible only as a wrong-looking cell and fixed in the same pass:

- Report job 35606161 printed "fail" in every join title, passing rows included: `pass` is stored as an int and the title compared it with the string "1". Fixed (`str(pas) == "1"`), 35606228 COMPLETED with correct captions.
- Report job 35606390 dropped every piece row (the parser required 5 columns; the scorer prints 4) and wrote only the three named joins into `seams.tsv` instead of all 62 per cell. Fixed with a header-aware parser and all 62 joins; 35606481 COMPLETED — `scores.tsv` 744 rows, `seams.tsv` 496 rows.
- `first_loss.tsv` was written by the first reductions and then withdrawn. It recorded the first **rejected exploratory branch** of a seam, so a passing seam read "no_interval" — the opposite of what `matching.tsv` says. It was never a required table; it is gone from the evidence and its writer is replaced by a comment at `report01.py:318-320`.
- The two surface panels drew the **same** projection (both used the plane spanned by the released cloud's axis 2 and axis 3) and differed only in their titles, so the "two views" were one view twice. Fixed in `surface01.py:341-347`: one panel now views along the released mean normal, the other along released PC1, each labelled with the two axes it shows. Two follow-on defects showed in the first re-made pair and were fixed in the same file: `tight_layout` could not fit axes with `aspect='equal'`, so piece 27's x-axis titles were clipped off the bottom (now explicit `subplots_adjust` margins, `surface01.py:459-461`), and `renders_surface.tsv` claimed a green reference-partner series that neither figure draws (removed). Job 35607646 re-made both PNGs; the published figures are that run.
- **Superseded in turn 2 — see section 9.1.** The missing-pose guard as first delivered tested only `T_0to_0.txt` (`cell01.sbatch:106` at the time), so a cell that exported 28 of 31 poses still exited 0. `OWN_E27_AUTHOR` repeat 1 did exactly that (40/62, with pieces 18, 28 and 31 exporting no pose). This is a stated deviation from "nonzero exit for a missing pose": the guard is a required-pose check, not a completeness check, and the cell is reported as it scored with its missing poses named. No cell was scored from a directory lacking `T_0to_0.txt`.
- `jobs.tsv` carries four blank-role `COMPLETED` rows (35604054, 35604092, 35604240, 35604310) — 7–10 s dry runs of the reduction made while `surface01.py` was being fixed, before any evidence existed. They are left visible rather than deleted; they are not cells. Three further rows (35606228, 35606390, 35606481) were appended from `sacct` by hand because the reduction reads `logs/sacct_final.tsv`, which lagged the jobs, and 35606885/35606886 and 35606966 were appended the same way. Those hand rows and the four dry runs carry `polled=1` like every other row, so `jobs.tsv` does not by itself distinguish a script-polled job from an appended one; `logs/sacct_final.tsv` and `logs/waves.tsv` are the authoritative record.

Nothing in the cell path failed: all eight cells exited 0:0 first time, matched their executable hash before and after, and scored.

#### 6. Self-compliance

| requirement (ticket line) | met | evidence |
|---|---|---|
| load both walls through the archived loader, log 4 paths, hashes, load dimensions (25) | yes | `surface01.py:161,177-178`; `loads.tsv:2-9` (6 × N per cloud, sha256 each) |
| both faces, same mesh, same two locked views, 20 mm bar, native frame, no ICP, signed normal orientation, same-face vs crossed-face apart (29) | yes | `surface01.py:89-140,302-303,341-473`; `surfaces.tsv`, `surface_crossed.tsv` (target_face column), `surface_frame.tsv` (mesh NN p50 0.16–0.29 mm, inside fraction 1.0), the two surface PNGs |
| paired/unpaired counts and fractions at 1 and 2 mm, p50/p95, spacing on distinct XYZ, exact duplicates, signed normal p50/p95, fraction above 90°, invalid-normals count (30) | yes | `surfaces.tsv:1` — all brief columns plus `unpaired_fraction_1mm/2mm` and unsigned-normal columns; fractions to six decimals; duplicates counted separately so spacing is not inflated; `invalid_normals` = 0 on every same-face row, and the blank-on-zero case is exercised in `surface_crossed.tsv`, where piece 28 has `valid_normals` 0 on both faces from both sources and blank angle columns with the zero count left visible |
| 2 mm cell counts on `floor(xyz/2)`, shared/unmatched colours, differences near the fixed 27–28 fracture line (31) | yes | `surface01.py:85,302-303,400-452`; `surfaces.tsv` cell columns and the band panel, which counts and prints the unmatched own points in the 15 mm band |
| every saved E27/E28 candidate from OWN, AUTHOR and released, signed and unsigned angle, row order, anchor-to-line distance (32) | yes | `axes.tsv:1-13` (12 rows; header carries `pos_x…dir_z` as well as the angles and the anchor-to-line distance); `report01.py:124-146,470-490`; E27 OWN 35.44°/7.35°/156.49° on 3 rows, AUTHOR −66.38°/−2.87° on 2 rows, released −2.23°; E28 analogous. Two of the twelve rows are the released axis measured against its own ground-truth line — a self-check that the measurement reads a known pair as small — and ten are the OWN/AUTHOR candidates; the `source` column says which |
| four axis directories of 31 files, E27-only hybrids, E28 bytes preserved, hashes if identical (36) | yes | `stage01.py:74-111` asserts the diff equals `[E27]` exactly, asserts E28 unmoved, and refuses to continue if the donor bytes are identical; `logs/axes_swap.tsv`, `logs/stage.json` |
| archived Ticket 19 binary, no build, forked cell, fixed tree for DATA and GT, one varying bind, kept Apptainer/SIF/panel/env/hash check/exec/scorer, T18_TRACE and T19_TRACE, fresh Result (38) | yes | `cell01.sbatch:30-40,71-100`; `replay.tsv:2-9` (same hash pre and post, container_ok 1); `out/<cell>/t18_raw.jsonl` and `t19_decisions.jsonl` on Spartan, hashed in `traces.tsv` |
| nonzero exits for duplicate result dir, hash mismatch, missing pose, container and scorer failure (38) | yes | `cell01.sbatch:55-59` (`fail()` exits with its code) and the call sites in the 129-line script: 73 (7, duplicate result dir), 74 and 77 (8, executable missing or wrong hash before the run), 108 (8, after-run hash), 80 and 118 (9, input manifest), 109-110 (11, container hash check and container rc), **113-114 (12, all 31 poses)**, 126-127 (13, scorer rc and a missing SUMMARY), 119-121 (14, before/after manifest drift), 122-124 (15, container inventory missing or short); no cell needed one. The pose guard now requires all 31 nonempty `T_<i>to_<i>.txt` through `posecheck.sh:14-32` and exits 12 with the missing 1-based ids; the complete and missing-pose paths are validated on fixtures and on the archived cells (`fixtures_posecheck.sh:29-47`, `supplements/logs/fixtures_posecheck.tsv`, `supplements/logs/posecheck_real_cells.tsv`; section 9.1). The archived `OWN_E27_AUTHOR` repeat 1 (28/31) is retained as historical, not rescored |
| exact wave commands, wave 2 after wave 1 terminal, every job polled to a final `sacct` line (38) | yes | `logs/waves.tsv` (29 rows, one per submission), `logs/polled.tsv` (26 ids), `logs/poll_final.tsv` (31 ids with the poll exit code), `logs/sacct_final.tsv` (92 lines incl. sub-steps) and `jobs.tsv` (31 rows) — every id in `waves.tsv` has a `sacct` line, including 35606966, 35607410, 35607646, 35607833 and 35607903. Two bookkeeping points, visible rather than tidied: the `wave` column carries the job label for the non-cell rows (MEASURE9, MEASURE10, REPORT6-9) and `order` restarts at 0 for wave 2; and the earlier `sacct_final.tsv` on this ticket had not caught up with the last five submissions, so it was re-polled and re-appended before this table was fixed |
| no scored row for an unusable cell (38) | yes | the strict record treats `OWN_E27_AUTHOR` repeat 1 as unusable and gives it no scored join row (`supplements/strict_joins.tsv` 434 rows = 7 cells × 62, `strict_seams.tsv` 21 rows = 7 × 3, `strict_summary.tsv` row `usable=0`); its 40/62 archived rows stay in `seams.tsv`/`scores.tsv` marked historical in section 3. The only job failures were my own measure and report jobs (section 5) |
| stable AUTHOR control 62/62 twice, OWN loses 27–28 twice, before interpreting hybrids; T19 benchmark kept; per-cell trace read; other two E28 joins secondary; 62-outcome tally; zero interval as 0 with blank ID; failed control visible; no pruning attribution (46) | yes | `summary.tsv`, `seams.tsv`, `matching.tsv`, `t19_benchmark.tsv`; `OWN_E27_AUTHOR` is shown as 40/62 and 44/62 with its missing poses, not smoothed over; no attribution claim is made anywhere in this report |
| distinguish method failure, broken measurement and wrong reference | n/a for a worker | the brief forbids a verdict; the facts are above and the lead judges |
| both walls: hashes, denominators, same-frame measurement, candidate comparison, inspected locked renders (50) | yes | `loads.tsv`, `surfaces.tsv`, `surface_frame.tsv`, `axes.tsv`, `renders.tsv:14-15` and the two surface PNGs |
| each cell: terminal State/ExitCode, matching host and container executable hash, complete before/after manifests, scorer status; reciprocals differ at E27 alone; failed controls visible (51) | yes | `replay.tsv`, `jobs.tsv`, `provenance_axes_shadow.tsv` (container_sha256 column), `logs/inputs_before_*` and `logs/inputs_after_*` compared with `cmp` in `cell01.sbatch:119-121`, `reciprocal_inputs.tsv:2-5` |
| `replay.tsv`, `seams.tsv` (all 62 joins per cell), `matching.tsv` (counts and first events for the three target joins), `surfaces.tsv`, `axes.tsv`, `inputs.tsv`, `jobs.tsv`, `renders.tsv`, raw traces; locked renders incl. missing and off-frame cases (52) | yes | `replay.tsv` (8 rows), `seams.tsv` (496 rows), `matching.tsv` (24 rows), `surfaces.tsv`, `axes.tsv`, `inputs.tsv` (1 496 rows, container path per bound file), `jobs.tsv`, `renders.tsv` (14), `traces.tsv` (16) |
| self-compliance table with file:line evidence, separate read-only review with its own table and render inspection, one end state, facts and budget, no commit, no closure (53) | yes | this section; the review table below; the single End state line at the end |
| worker checks: `py_compile` on the three scripts, `bash -n` on the cell script, `check_intent_links.py` from the workspace root (55) | yes | `py_compile` → COMPILE-OK; `bash -n` → BASH-OK on `cell01.sbatch`, `submit.sbatch`, `measure01.sbatch`, `report01.sbatch`; `cd C:/PR && python scripts/check_intent_links.py` → **exit 1**: 58 questions / 947 ticket files, **10 errors, 549 warnings**, and all ten errors are in `uneven-wear`, `sherd-worn` and `tora`, none in `surface-parity` (the script lives in the umbrella root, not in the worktree; its non-zero exit is those unrelated tickets, not this one) |

`check_scratch_writer.py` reports "another session appears to be working here": the signs are my own untracked files under `.scratch/surface-parity/t01/` (the scripts, poll logs and `__pycache__` this ticket created after the last commit). Nothing of another session's is in the list, and no other session's paths were touched. Re-run at the start of turn 2, as the brief asked (`cd C:/PR && python scripts/check_scratch_writer.py C:/PR/worktrees/sfs/01`, exit 1 at 18:58): 45 signs, every one of them this ticket's own modified file or its own untracked `t01/` scripts and logs, including the `__pycache__` written by the `py_compile` check a minute earlier.

#### 7. Read-only review, first pass: findings and what happened to each

A separate read-only DeepSeek reviewer (own context, no write access) read the ticket, the evidence directory and every join and surface PNG. It returned its own compliance table (25 rows; the second, post-fix pass is reproduced in full in section 8) and its reading of the pictures agreed with every caption above: the passing arms seat both sherds on the reference, the failing arms throw piece 28 out of the window, and `OWN_E27_AUTHOR` repeat 1 says "no exported pose recorded for piece 28" instead of drawing a plausible lie. Its snapshot predated the Comments above and reduction REPORT5, so three of its "not met" rows (no compliance table, three joins in `seams.tsv`, stale `first_loss.tsv`) describe an earlier state; the tables in this report are the later ones. Its live findings:

| # | finding | disposition |
|---|---|---|
| D1 | `axes_manifest.tsv` background column held the arm's own hash, not the background's | fixed — defect 5 in section 5; manifest regenerated and the two hybrid rows now read as they should |
| D2 | `seams.tsv` had 24 rows instead of 496 | stale snapshot; 496 rows since 35606481 |
| D3 | `first_loss.tsv` reported a passing seam as `no_interval` | withdrawn and deleted before the review arrived |
| D4 | piece rows 0/31 everywhere, ~179–180° in the passing controls, so the piece column cannot discriminate | confirmed and stated in section 3 with the per-cell ranges; reproduces the archived Ticket 19 sheets. No attribution drawn |
| D5 | `OWN` repeat 2 also loses joins that do not touch 27–28 | confirmed; the five joins and their numbers are listed in section 3 |
| D6 | four blank-role `COMPLETED` rows in `jobs.tsv` | explained in section 5 — dry runs of the reduction, left visible |
| D7 | `check_intent_links.py` is not in the worktree | correct; the worker-check row now gives the exact command run from the umbrella root |
| D8 | ticket not closed out (no compliance table, no end state) | stale snapshot; both are in this report |
| D9 | `axes.tsv` had no direction columns and `surfaces.tsv` no unpaired fractions | both added and the tables re-made (jobs 35606885 measure, 35606886 and 35606966 report): `axes.tsv:1` carries `pos_x…dir_z`, `surfaces.tsv:1` carries `unpaired_fraction_1mm/2mm` |

Nothing was committed, pushed, merged or closed; `runs/index.tsv` has the new row with `verdict` and `human_note` left blank.

#### 8. Read-only review, second pass: the reviewer's own table

The same read-only reviewer (own context, no write access, nothing written) was asked again after the fix round. It re-opened both surface figures and measured them: the grey-mask overlap between the two left panels is now 0.239 for piece 27 and 0.159 for piece 28, against 1.0 for the identical pair it saw in pass 2, so the panels are two views. It returned this table; requirement numbers are the ticket's own lines.

| ticket line | requirement | met | evidence the reviewer cited |
|---|---|---|---|
| 23 | edit scope: this ticket + `t01/` only | yes | `git status`: only the ticket modified, `.scratch/surface-parity/t01/` untracked; no other path touched |
| 25 | loader, four paths, hashes, load dimensions | yes | `surface01.py:161,177-178`; `loads.tsv` 8 rows, dims "6 x N" |
| 29 | native frame, no ICP, both faces, two views, 20 mm bar, signed normals, same/crossed apart | yes | `surfaces.tsv` note; `surface_frame.tsv`; panel overlap 0.239 / 0.159; `surface_crossed.tsv` `target_face` |
| 30 | paired+unpaired at 1 and 2 mm, p50/p95, distinct-XYZ spacing, duplicates, signed normal stats, blank-on-zero | yes | `surfaces.tsv:1` incl. `unpaired_fraction_1mm/2mm`; the blank rule is exercised in `surface_crossed.tsv` piece 28 |
| 31 | 2 mm cells, own/author/shared colours, 27–28 band | yes, one gap | `surfaces.tsv` cell columns; band text "4 unmatched own points" / "0"; markers are ~1 px, so the colour encoding cannot be read off the picture (N5) |
| 32 | every E27/E28 candidate, signed+unsigned, row order, anchor-to-line mm | yes, one gap | `axes.tsv` 12 rows; the two released-GT self-check rows are included and declared (section 6) |
| 36 | four axis dirs of 31, hybrids, E28 bytes preserved, donor-identical refusal | yes | `stage01.py:74-111`; `logs/axes_swap.tsv`; `logs/stage.json`; `axes_manifest.tsv` 248 rows |
| 38 | archived binary, no build, forked cell, one varying bind, traces, fresh logs, nonzero exits, no scored unusable cell | partly | `replay.tsv`; `cell01.sbatch:83-127`; the pose guard is `T_0to_0` only while the cell row says "partly" after this pass |
| 41/43 | exact wave commands, wave 2 after wave 1 terminal | yes | `logs/waves.tsv`; last wave-1 end 04:20:19 vs first wave-2 submit 04:20:59 (arithmetic on wall times; `sacct` here carries no Start/End) |
| 46 | AUTHOR 62/62 twice, OWN loses 27–28 twice, benchmark, tally, zero-interval blank, no attribution | yes | `seams.tsv` 496 rows; `matching.tsv` blank IDs; `t19_benchmark.tsv`; section 3 |
| 50 | both walls measured and rendered | yes | `surfaces.tsv`, `surface_frame.tsv`, both surface PNGs |
| 51 | per-cell terminal state, hashes, before/after manifests, scorer, reciprocals | yes | `replay.tsv`, `jobs.tsv`, the 16 `inputs_before/after` files, `reciprocal_inputs.tsv` |
| 52 | named tables and locked renders incl. missing and off-frame | yes | 18 tables + logs + 14 PNGs present; `renders.tsv` 14 rows |
| 53 | compliance table, separate review with its own table, one end state, facts, budget, no commit | yes after this section | this table; the single End state line below |
| 55 | worker checks | yes | `py_compile` COMPILE-OK; `bash -n` BASH-OK on four scripts; `check_intent_links.py` exit 1 (10 errors, 549 warnings, none outside the three other projects — see row above) |

Its residual findings and what happened to each:

| # | finding | disposition |
|---|---|---|
| C1 | no `**End state:**` line | fixed — one line at the end |
| C2 | the "no instance of blank-on-zero" claim contradicted by `surface_crossed.tsv` | fixed in sections 2 and 6 |
| C3 | the review's table was not reproduced, only tallied, and the tally was wrong | fixed — both passes now give tables (section 7 points here; this is the table) |
| C4 | four citations missed their lines | fixed (161/177-178, 232-247, 108-111, the 310→313-314 note) |
| C5 | the exit list omitted `cell01.sbatch:69` | fixed in section 6 |
| C6 | the pose guard tests `T_0to_0` only, so 28/31 poses still exits 0 | disclosed as a deviation (section 5) and the cell row now reads "partly" |
| C7 | `logs/` was not delivered; `sacct_final.tsv` lacked the last jobs and `poll_final.tsv` stopped at 35604310 | fixed — 35 log files fetched, the missing ids re-polled and re-appended (`sacct_final.tsv` 92 lines, `poll_final.tsv` 31 ids) |
| C8 | `axes.tsv` mixes the released self-check rows with the candidates | declared in section 6 |
| C9 | `jobs.tsv` mixes dry runs and hand rows under `polled=1` | declared in section 5; `sacct_final.tsv` and `waves.tsv` named as authoritative. Its third point — that 35606966 was claimed in `jobs.tsv` but absent — was true of the earlier file; `jobs.tsv` now has 31 rows and includes it |
| C10 | "thin rim" and "rotated about 160°" overstated | fixed in sections 2 and 4 |
| C11 | anchor wording on line 141 and "opened all twelve" on line 154 | fixed; and the two surface panels were found to be the same projection — a real defect, fixed and re-rendered (section 5) |
| N4 | `waves.tsv` labels the non-cell rows in the `wave` column and `order` restarts at 0 | disclosed in section 6, not tidied — the file is the append-only submission record |
| N5 | `renders_surface.tsv` promised a green partner series that no figure draws | fixed — label corrected and both figures re-made (35607646) |
| N6 | the coloured-pixel counts on line 102 were not reproducible as pixel counts | fixed — replaced with the measured unpaired counts and fractions from `surfaces.tsv` |
| N7 | the `t01/` scripts are untracked | by design: this dispatch may not commit. They are also copied into `$RUN/work/t01/` on Spartan and listed in `logs/waves.tsv`, so the evidence is reproducible from the run directory |
| N8 | the piece-27 figure was vertically clipped | fixed — explicit margins; both figures re-made (35607646) and re-opened |

#### 9. Turn 2: the missing-pose rule enforced, the surfaces re-made, the write-back corrected

**9.1 Pose completeness: all 31 required, and one cell is unusable**

The pinned assembler writes one pose export per piece into the Result mount, `T_<i>to_<i>.txt` with `i = 0..30` — the exact names the pinned scorer reads (`score305.pinned.py:55`). Turn 1's wrapper tested only `T_0to_0.txt`, so a cell that exported 28 of 31 poses still exited 0. That is what `OWN_E27_AUTHOR` repeat 1 did (40/62, pieces 18, 28 and 31 exporting nothing).

- The check is one documented function: `posecheck.sh:14-32` (`check_poses <dir> [n]` prints `POSE-OK n/n` and returns 0, or `POSE-MISSING have/n pieces: <1-based ids>` and returns 1). The cell wrapper sources it at `cell01.sbatch:50`, runs it after the assembler and before the scorer at `cell01.sbatch:112` / `113-114`, and `fail 12` writes the missing ids into `logs/cell_status.tsv`; the clause is in the script header at `cell01.sbatch:24-25`.
- Fixtures run that same function, not a copy (`fixtures_posecheck.sh:29-47`): 31 nonempty files → `POSE-OK 31/31` rc 0; 28 files with 18, 28, 31 absent → `POSE-MISSING 28/31 pieces: 18 28 31` rc 1; 31 names with one zero-byte file → `POSE-MISSING 30/31 pieces: 7` rc 1. `FIXTURES-OK 3/3`, log `supplements/logs/fixtures_posecheck.tsv`.
- Read-only over the eight archived cells (`realcell_posecheck.sh`, log `supplements/logs/posecheck_real_cells.tsv`): seven `POSE-OK 31/31`, `OWN_E27_AUTHOR_1` `POSE-MISSING 28/31 pieces: 18 28 31` rc 1. **No other cell is short.**
- Nothing archived was touched: no assembly was rerun, and that cell's exports, raw traces and `sacct` line stand exactly as they were.

**Strict acceptance record**, derived from the archived exports (job 35611433, re-run as 35611465 after a column-formatting fix; both COMPLETED 0:0 and polled — `supplements/logs/polled.tsv`): `strict_poses.tsv` (8 cells: expected 31, present, missing ids, empty ids, status), `strict_joins.tsv` (434 rows = 7 usable cells × 62 recomputed joins, each with the archived verdict and the delta), `strict_seams.tsv` (21 rows = 7 cells × the three E28 joins), `strict_replay.tsv` (8 rows), `strict_summary.tsv`. The replay recomputes the pinned scorer's own arithmetic from the exports (`strict01.py:48-60,143`) and agrees with the archived sheets to **0.000498°** (`strict_replay.tsv:8`) and **0.000500 mm** (`strict_replay.tsv:6`) at worst  — the archived sheets' three-decimal rounding.

`OWN_E27_AUTHOR` repeat 1 is **unusable** and takes no scored join row in that record (`strict_summary.tsv` gives it `usable=0` with blank joins; `strict_joins.tsv` and `strict_seams.tsv` do not contain it). Its 40/62 sheet, its "no exported pose recorded for piece 28" figure and its trace stay in the run as the **historical diagnostic result**, labelled as such in section 3, and are counted in nothing below. Acceptance therefore rests on 7 cells, whose target joins read OWN 59/62 and 54/62, AUTHOR 62/62 twice, OWN_E27_AUTHOR 44/62 (repeat 2), AUTHOR_E27_OWN 62/62 twice.

**9.2 The two surfaces pictures, re-made**

The turn-1 figures were geometrically right and visually unreadable: the frozen mesh was drawn as sparse 0.74-grey dots that vanished into the shared cloud, and the unmatched markers were 1–3 px. That this was presentation and not measurement is checkable, and it checks: every re-render's tables are byte-identical to the frozen ones.

Six render jobs, all COMPLETED 0:0 and polled (`supplements/t01-turn2/logs/polled.tsv`, `supplements/t01-turn2/logs/sacct_turn2.tsv`): 35611434 and 35611512/35611528 enlarged the unmatched markers (s=11, black edge, legend) and darkened the plate (`surface01.py:351-362,380-386`), with the band markers at s=42 and the count in the panel title (`surface01.py:441-443,457-458`); looking at those two figures, the plate was still hidden under the dense cloud, so 35611692 added a mesh drawn every 3rd vertex plus the **convex hull of its projected vertices** as an outline (`surface01.py:354-362`), which makes the plate and its extent unmistakable in both locked views while leaving the clouds and colours on top. 35611512 also caught the panel titles reading "view None" (an edit had reused the label variable), fixed before the next run. The third-pass review then found a real defect in the band panel: its axes were limited by the **3-D** bounding box of the band cloud instead of the projected points, so three of piece 27's four own-only markers fell outside the frame (`surface01.py:408-414` as it then stood). 35611889 re-drew the panel from the projected band points, and 35611949 tightened those limits to the own band alone after the first attempt let the partner reference cloud stretch the panel with empty space below the sherd (`surface01.py:425-426,449-451`). The plate, the clouds, the colours and every measured number are unchanged across all six runs.

- [surface_piece27_views.png](worktrees/sfs/01/artifacts/surface-parity-01/supplements/renders/surface_piece27_views.png) and [surface_piece28_views.png](worktrees/sfs/01/artifacts/surface-parity-01/supplements/renders/surface_piece28_views.png).
- In the delivered pair the frozen mesh is visible as a filled pale plate with a grey outline in both locked views of both pieces, the clouds sit on it, and the own-only red (face 0 filled, face 1 hollow, black edge) and authors-only blue markers are legible; the 15 mm band panel on piece 27 reads 4 own-only points and now shows all four inside the frame, and piece 28's prints 0 with no red. Picture hashes (current, job 35611949): piece 27 `ccdf4908c8b45329bc1712804ce4012883428e2e7c26a8d0e535cea7fb18f0a1`, piece 28 `e818d0c91d9d42851c98a7610784a103edc8ce99b3600d674072f78b88c9e8af`.
- Measurement unchanged: `supplements/tables/surfaces.tsv` sha256 `0c1214b5e0d400aef7d24651069c754debdb3a65594e989fd29448b42aff2eef` is byte-identical to `evidence/surfaces.tsv` (likewise `surface_crossed.tsv` `6da0cfc4…`, `surface_frame.tsv` `693b2860…`), and the frozen run's own figures keep their hashes (`2efdad68…`, `cc4f96be…`).

**9.3 Corrections to the write-back, and the conventions behind the tables**

Provenance, corrected in section 1: the reciprocal overrides are **E27 only** for `OWN_E27_AUTHOR` (1/31 against the OWN background) and **every axis except E27** for `AUTHOR_E27_OWN` (30/31 against the OWN shadow, which is what the fixed tree carries, with E27 keeping `d4236e91…`). Both hybrids therefore preserve E28 relative to their parent — `OWN_E27_AUTHOR` keeps OWN's `12de83dc…`, `AUTHOR_E27_OWN` keeps AUTHOR's `212dcb15…`. The pinned scorer cited throughout, `supplements/score305.pinned.py`, hashes `b04121f95bef4739c3a1eeb3df13dfe1d4fc5da5c533fdf165d2f1252f6dddde` — the run's recorded `scorer_sha256` — and turn 2 did not touch it.

The E27 swap, stated as observed in section 3, one background at a time (each pair is the parent and then the hybrid, repeat 1 then repeat 2):

- **OWN background, 27–28 pass/fail unchanged (fail → fail).** Whole-pot joins 59/62 → 40/62, and that hybrid cell is unusable (28/31 poses); the repeat-2 pair is 54/62 → 44/62. On 27–28 the search's 27–28 queries fall 468/447 → 244/272, with intervals 0/0 → 0/0 and fits 0/0 → 0/0 in all four cells.
- **AUTHOR background, 27–28 pass/fail unchanged (pass → pass).** Whole-pot joins 62/62 → 62/62 twice. On 27–28 the queries rise 636/628 → 936/936, the available intervals fall 180/176 → 25/24 and the pair fits 74/73 → 27/31.
- So the whole-pot join count moves in both backgrounds even where the 27–28 verdict does not: down under the OWN background, unchanged at 62/62 under the AUTHOR background.

What the numbers mean and do not mean:

- **`t_mm` is a pose disagreement, not a gap between sherds.** The scorer takes the measured relative transform and the reference relative transform, both in the first piece's frame, and reports the norm of the difference of their translation vectors (`score305.pinned.py:92-96`). `722.006 mm` therefore means the exported placement of 28 relative to 27 sits 722 mm away from the reference placement; it says nothing about how far apart the two sherd surfaces physically sit. Seating is what the pictures show; the millimetre figure is a comparison of two 6-DoF poses.
- **Signed angle.** `signed_deg` lies in **[−180°, +180°]**: the unsigned angle between the candidate axis direction and the released ground-truth axis direction, given the sign of `dot(unit(candidate direction), released mean Surface_0 normal)` (`report01.py:125-141`; the reference normal is the mean of the released `Pot_E_Piece_<n>_Surface_0.xyz` point normals, `report01.py:483-485,490-493`). Positive means the candidate leans to the same side as the released wall's mean normal; 0° means it points along the released GT axis direction. `unsigned_deg` ∈ [0°, 180°] is the bare deviation. `distance_mm` is the perpendicular distance from the candidate's anchor point to the released GT axis line (`report01.py:119-122`).
- **Candidate source labels** (`axes.tsv`, column `source`): `OWN` = our estimator's saved axis in `T19/axes/OWN`; `AUTHOR` = the authors' in `T19/axes/AUTHOR`; `released` = the shipped sample's axis in `original_samples/SfS_pp/Axes`; `released-GT-axis` = the released GT axis measured against itself (the two self-check rows of the twelve).
- **Table formats.** `scores.tsv`: arm, repeat, kind (piece|join), i, j, angle_deg, translation_mm, verdict, primary (744 rows = 8×31 piece + 8×62 join). `seams.tsv`: arm, repeat, seam, angle_deg, translation_mm, pass, primary (496 rows = 8×62). `matching.tsv`: arm, repeat, seam, query_count, interval_count, fit_count and the three first-event ids (24 rows; blank id where the count is zero). `surfaces.tsv`: the brief's columns plus `unpaired_fraction_1mm/2mm`, unsigned-normal columns, `distance_max_mm`, `cells_total`, `note` (8 rows = 2 pieces × 2 faces × 2 directions). `axes.tsv`: piece, source, row, signed_deg, unsigned_deg, distance_mm, pos_x/y/z, dir_x/y/z (12 rows). `inputs.tsv`: arm, repeat, container path, before_sha256, after_sha256, container_sha256 (1 496 rows = 187 per cell). `replay.tsv`: arm, repeat, executable_sha256, pre/post hashes, container_ok, job_id, status, joins, sherds. `jobs.tsv`: job_id, run_id, role, state, exit_code, polled, wave/order. `renders.tsv`: kind, arm, repeat, relative path, camera centre and half-width, bar length, labels. Strict record: `strict_poses.tsv` (cell, expected, present, missing_ids, empty_ids, status), `strict_joins.tsv` (cell, i, j, recomputed angle and translation, pass, archived verdict, the two deltas), `strict_seams.tsv` (cell, seam, angle, translation, pass, primary, archived pass), `strict_replay.tsv` (cell, poses, rows matched, max deltas, status), `strict_summary.tsv` (cell, usable, joins, archived summary as one field, note).

**9.4 Counts**

- Failed **named** checks: **five distinct in turn 1 against a budget of five** (six table rows, because rows 1 and 2 are the same partner-index defect showing up in a measure job and in a report job — section 5); **none in turn 2** against a budget of two. The six surface re-render iterations, the strict-script column fix and the pose-check quoting slip were not named checks and are recorded above.
- Slurm failures: **3 of 39 job submissions** — 35601864, 35604009, 35607833, all in turn 1 and all in section 5 (turn 1 contributes the 31 rows in `jobs.tsv`, turn 2 the 8 jobs below). Turn 2's eight jobs (35611433, 35611465, 35611434, 35611512, 35611528, 35611692, 35611889, 35611949) are all COMPLETED 0:0 and polled (`supplements/t01-turn2/logs/polled.tsv`, `supplements/t01-turn2/logs/sacct_turn2.tsv`).

**9.5 Read-only review, third pass (turn 2)**

A separate read-only sub-agent (`reviewer3`, no write access) checked this turn's ticket text, scripts and the delivered surface figures on a snapshot taken while the file was still being edited (317 lines, sha256 `3ece6a0a…`; figures 18:46:21). Its table as returned:

| requirement | met | evidence |
|---|---|---|
| Missing-pose guard: exact names and indices, 31 non-empty poses before the scorer, failure exit with the missing ids | yes | `posecheck.sh:14-32` tests `T_${i}to_${i}.txt`, i = 0..30, the names `score305.pinned.py:55` reads; `cell01.sbatch:112` calls it and `113-114` fails with 12 before the scorer at 125-127; `strict_poses.tsv:8` records 18, 28, 31 missing |
| Archived `OWN_E27_AUTHOR` repeat 1: evidence untouched, strict replay, unusable with no join row, historical labels, no other cell short | yes | `strict01.py:123-132,178-189`; `strict_summary.tsv:8` usable=0 with blank joins; `strict_joins.tsv` 434 rows; the archived files keep their 17:15-17:17 mtimes; `fixtures_posecheck.tsv` shows only that cell short |
| Fixtures exercise both paths through the documented check; the pinned scorer is unchanged | yes | `fixtures_posecheck.tsv`: 31/31 rc 0; 28/31 with 18 28 31 rc 1; one empty file 30/31 with 7 rc 1; `sha256sum supplements/score305.pinned.py` = `b04121f9…` = the run's recorded `scorer_sha256` (identity with the run's own copy rests on that recorded hash, since the run directory was not re-read by the reviewer) |
| Surfaces: fixed mesh visible, near-fracture colours legible, Spartan re-render with poll records, original hashes kept | yes (was unclear at D10) | the pair from 35611949 shows the pale plate with its hull outline in all four locked views and every unmatched marker inside its panel, piece 27's band panel counting 4 and showing 4; `surfaces.tsv` `0c1214b5…` is byte-identical to the frozen table; the frozen run's own PNGs still hash `2efdad68…`/`cc4f96be…` |
| Reciprocal overrides are E27-only vs all-except-E27; E28 preserved relative to the parent | yes | `stage01.py:87-93,101-107`; `inputs.tsv` container hashes; `reciprocal_inputs.tsv` differs at `Pot_E_Piece_27_Axis.xyz` alone, four rows |
| E27 swap facts: verdicts unchanged, intervals and whole-pot counts move | yes | `matching.tsv` 27-28: OWN 468/447 queries → 244/272 with intervals 0/0 → 0/0; AUTHOR 636/628 → 936/936 with intervals 180/176 → 25/24 and fits 74/73 → 27/31; section 9.3 |
| Conventions: signed-angle range, candidate labels, table formats, translation vs seating | yes | `report01.py:125-141` (sign from `dot(dir, mean Surface_0 normal)`), `483-493`; `axes.tsv` 12 rows over four sources; headers match section 9.3 |
| Separate read-only review, one end state, named-check vs Slurm counts | yes (was no — this section) | this section; the single `**End state:** ready` line; section 9.4 |
| Scope: no commit, no assembly rerun, frozen run intact | yes | `git status` shows only the ticket modified and `.scratch/surface-parity/t01/` untracked; HEAD `1233d62`; turn-2 jobs are `t01-strict` and `t01-surf2`; the frozen `evidence/` files keep their mtimes |

**What became of each finding** (eleven items; every one is closed in this file):

| # | finding | disposition |
|---|---|---|
| D1 | the required review was the literal placeholder `REVIEWTABLE` | replaced by this section |
| D2 | the replay sentence gave `0.000495°` at `strict_replay.tsv:5,6` | corrected: the maximum angle is **0.000498°** at `strict_replay.tsv:8`, the maximum translation **0.000500 mm** at `strict_replay.tsv:6` |
| D3 | the `cell01.sbatch` exit-site citation list was from the 106-line version | rewritten against the 129-line script (sites 73, 74/77, 108, 80/118, 109-110, 113-114, 126-127, 119-121, 122-124; `fail()` 55-59) |
| D4 | `fail 12` cited as `112-113` | corrected to `112` (the call) and `113-114` (the block) |
| D5 | bind and inventory citations (`79-84`, `90-94`, `110-112`, `114-115`) were stale | corrected to `83-90`, `95-99`, `119-121`, `122-124` in sections 1, 6 and 8 |
| D6 | surface marker citations | corrected: locked-view markers `surface01.py:380-386`, band markers `441-443`, band limits `449-451` |
| D7 | section 9.2 called all own-only red markers hollow | corrected: face 0 filled, face 1 hollow |
| D8 | the frozen figures' `17:10:15` mtime claim did not match the local copies (17:15:24) | removed; the hashes stay |
| D9 | job 35602269 was counted as named check 4 and also listed as not counted | resolved: **five distinct defects in six rows** (rows 1-2 share the partner-index defect), so the turn-1 tally is five against a budget of five — the header, section 5 and 9.4 now say so |
| D10 | piece 27's band panel clipped three of its four own-only markers | real defect: the axes took the 3-D band bbox as their 2-D limits. Fixed from the projected points, jobs 35611889 and 35611949, all four markers in frame, every measured number unchanged |
| D11 | `sacct_turn2.tsv` cited without its directory | corrected to `supplements/t01-turn2/logs/sacct_turn2.tsv` |

Two rows of that table were `unclear` and `no` at the snapshot: the surface legibility (D10) and this section itself. Both are closed above, and the delivered pair is the 35611949 one.

**End state:** ready

### Lead disposition — 2026-11-24

Accepted as a Pot E diagnostic. The authors’ axis set seats 62 of 62 joins in both repeats, including both repeats with our E27 axis file in that set. Our axis set misses 27–28 in both repeats. The authors’ E27 file leaves 27–28 unseated in the complete repeat on our axis set, with zero candidate stretches. The other repeat exported no poses for E18, E28 and E31 and is unusable for scoring. The single E27 file is insufficient to explain or repair the loss in the tested backgrounds. The E28-only replacement in the authors’ background also passed twice in axis-parity Ticket 19. Test the two files together before perturbing the wall samples.

The placement drawings agree with the join scores. In the passing hybrid the relative rotation error is as low as 4.34°. In the usable reciprocal hybrid it is 165.90°, nearly a half turn. The all-zero absolute sherd scores, including in passing controls, remain a measurement problem. Weight is one pot, four axis sets, two attempted repeats per set and seven usable outputs. The revised wall overlays show where the sampling differs on the same physical sherds.

- verified: original replay, input manifests, container axis hashes and archived Ticket 19 manifests -> eight terminal assemblies, 1,496 mounted input comparisons, 248 verified container axis hashes and exactly one changed E27 file per reciprocal.
- verified: strict supplement against historical scorer flags, fixture output and scheduler logs -> seven complete cells, 434 join rows, zero flags changed, one incomplete cell excluded and eight supplemental jobs completed 0:0. Inspected both revised wall views and the passing, misplaced and missing-pose comparison views.
- The original private check stopped because the independently landed axis-parity Ticket 19 worktree had been retired. Separate verification compared the recorded snapshots with the current worktrees and checked the evidence using the delivered table formats, signed-angle range and two multi-view panels. The follow-up Baton file report was confined to the assigned worktree.
- **DSH cost:** DeepSeek V4.1 Flash. Original Harness session and one Baton follow-up, `hrun-mwudgihs-a3c0e2`. Token counts are unavailable in the handover.
- Spartan run `20261124-1431_1233d62_t01-surface-parity`. The strict tables and revised views are in its supplement and the laptop’s project artifact directory.
