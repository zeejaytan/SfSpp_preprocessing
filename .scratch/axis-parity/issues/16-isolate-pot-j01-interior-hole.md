# 16: Does the interior scan hole drive the Pot J 01 axis turn?

**What to build:** Locate the documented J01 interior hole and measure whether omitting the already-sampled points around its rim changes axis refinement. Keep the exterior, original sampling pass, seeds, refiner and scoring panels fixed. No assemblies.

**Answers:** E1
**Blocked by:** None. Use Ticket 15's frozen own-stock evidence and the defect note in pota-repro ticket 285. A hole that cannot be identified unambiguously blocks the intervention.
**Status:** resolved
**Branch:** 16-isolate-pot-j01-interior-hole, in /c/PR/worktrees/sfs/16
**Worker:** DeepSeek
**Budget:** medium 5
**Hand-over:** DeepSeek, one-shot diagnostic. Return both self-compliance and a separate read-only review.

## Pins and location gate

- Use the native `Pot_J_Piece_01_Mesh_DS.obj` in the frozen corpus and the ordered J01 wall rows from Ticket 15 run `20261123-0106_2e951d9_t15-j01-refine-objectives`. Reuse `work/t15/samples/own_stock.npz`, `work/t15/seeds/{raw620,raw1110,donor2}.npy` and the clean selector at `2e951d9`. Validate sample, seed and ordered wall SHA-256 against Ticket 15 `evidence/provenance.tsv`. Read `SfSpp_preprocessing/AGENTS.md` and `285-pot-c-01-scan-gap.md`. Use the existing TORA Python on a compute node. Ticket 15's accepted-step logging is optional here. Use the unchanged `sfs_axes.normalized.refine_axis_normalized` with `max_iters=60,tolerance=1e-6`; baseline endpoints must match Ticket 15 for all three seeds within 0.01° and 0.01 mm using its centroid-foot metric.
- In run-local `work/t16/hole_mask.py`, enumerate undirected edges incident on exactly one triangle in the frozen OBJ (triangulate polygon faces by a fan if needed). Use connected boundary components. List component vertex/edge counts, closed-loop status, centre, diameter, closest distance to the largest perimeter component, and signed interior/exterior assignment from median nearest wall distance to ordered S0 and S1. Break perimeter-size ties by smallest vertex index. Candidate hole must be a closed degree-two component distinct from the largest perimeter, at least 4 mm away from it, and its median nearest-wall distance to S0 must be at least 0.5 mm smaller than to S1. Require exactly one qualifying component. Verify same-native-frame placement and inspect the mesh overlay before naming it. Preserve candidate census and boundary JPEG/PNG regardless of outcome; if no unique qualifying component, record blocked and stop before intervention. Do not infer a hole from a point-density void or use normal residuals or axis outcomes to select the location.

## Fixed-sample intervention

- In run-local `work/t16/diagnose.py`, reproduce the exact concatenation and stock stride in `sfs_axes/select.py:select_union_lines` and verify byte identity with Ticket 15's saved little-endian `normal` array. Derive a source-wall label and original row index for every sampled column from the full ordered wall lengths and stride indices. The donor axis is scoring/diagnostic only.
- For each original interior sample, compute the exact minimum 3D Euclidean distance to the confirmed hole's boundary **segments** using point-to-segment projection clamped to the segment, with zero-length segments treated as points. Do not mask by distance to the hole centroid. Create conditions `stock`, `rim1`, `rim2`, `rim4` and `restored`. In the three rim arms omit only sampled interior columns at distance ≤1, ≤2 or ≤4 mm respectively **after** the stock stride. Keep the remaining column order and bytes. `restored` puts the exact masked 4 mm rows back at their original indices, with no refilling, normals recomputation, or re-striding. Assert input bytes and outputs identical to stock for restored. If a mask is empty, record an explicit no-op and reuse the stock result for that condition. Flag identical adjacent masks; no dose trend may be claimed from identical masks.
- Run all three seeds under the five conditions. Keep the exterior column set, order and six-vector bytes identical in every fit; assert this on the actual solver argument. Keep the original Ticket 15 profile scoring arrays **byte-identical** in every condition. Report endpoint turn from seed, sign-free angle and foot offset to donor at (30.107,12.692,452.566) mm, and normal per point on the common full stock sample and profile mm on the fixed walls. Also report normal cost per point on the fit's own sample, separately. If fallback occurs report it by cell without treating it as a clean solver comparison.
- Pre-registered evidence for a hole-adjacent effect: at least two seeds (one must be raw) have ≥10° less turn **and** ≥10° smaller endpoint angle to donor in the 4 mm arm, while centroid-foot offset worsens by no more than 2 mm. Require the smaller nonempty masks to show no reversal exceeding 2° in the same direction metric for those seeds. Report the full results even if the threshold fails. With this design the conclusion is about the influence of the existing interior samples near the hole, not a prediction for a repaired mesh or proof that missing material alone caused the turn.

## Evidence contract and checks

- `boundary.tsv` columns component, vertices, edges, closed, diameter_mm, perimeter_distance_mm, inner_median_mm, outer_median_mm, chosen (closed/chosen 0/1). Include the full boundary overlay and an interior/exterior zoom locating the loop relative to the ordinary broken edge. `phase.tsv` columns state, reason, with one row (ran or blocked). A blocked location requires the census and visual evidence, with no result cells.
- For a located hole export `mask.tsv` columns sample_idx, wall, source_idx, distance_mm (blank for exterior), rim1, rim2, rim4 (0/1). Export every sampled column, including untouched ones. `fits.tsv` columns condition, seed, state (ran/noop), normal_n, omitted_n, exterior_sha256, fixed_profile_sha256, fit_sha256, endpoint_sha256, fallback (0/1), turn_deg, donor_angle_deg, donor_offset_mm, normal_fit_per_point, normal_stock_per_point, profile_mm. `matches.tsv` columns seed, angle_deg, offset_mm for stock vs Ticket 15. `renders.tsv` columns kind, path (relative to evidence directory), with kinds boundary, mask, and axes. Render stock and each nonempty mask with common camera and mm scale; baseline and endpoint line feet must be visible at the zoom scale. Keep geometry and code on Spartan. Fetch small evidence to `C:/PR/artifacts/axis-parity-16/`.
- Preserve exact command/provenance and source of each fingerprint in `repro.txt`. Save `corpus_before.md5` and `corpus_after.md5` and `jobs.tsv` (job_id, run_id, state, exit_code in sacct form, polled/indexed 1/0); poll every submitted job. On a compute node run pinned `python -m pytest tests -q`, retain `pytest.log` and `pytest.exit`. Review figures and tests before returning.
- Ticket write-back must contain one End state and one self-compliance row per requirement with status (met/not met/unverified) and file:line evidence. Require a separate read-only DeepSeek compliance table covering the same requirements, especially the actual renders, provenance and phase gate. On the laptop leave only the ticket write-back modified in this worktree; do not commit, merge or close. No selector changes, mesh repairs, corpus writes, or assembly runs.

## Comments

One-shot diagnostic. Ticket 285 records the interior defect and leaves its location open. [PotSAC](https://openaccess.thecvf.com/content_ICCVW_2019/papers/EH/Hong_PotSAC_A_Robust_Axis_Estimator_for_Axially_Symmetric_Pot_Fragments_ICCVW_2019_paper.pdf) identifies surface artifacts and break-surface normals as possible sources of error in sherd axis estimates.

## Report (worker: DeepSeek, 2026-11-23)

Run `20261123-0305_2e951d9_t16-isolate-j01-interior-hole` on Spartan. Code (run-local, never in the worktree): `work/t16/hole_mask.py`, `work/t16/diagnose.py`, `submit_t16.sbatch`. Evidence fetched to `C:/PR/artifacts/axis-parity-16/evidence/`; all paths below are relative to that directory unless marked SPARTAN.

### 1. Location gate: one qualifying interior hole

Census of the frozen OBJ (`evidence/boundary.tsv`, 10463 triangles, all triangular, fan triangulation not needed; 583 single-triangle edges; 3 boundary components, every one closed and degree-two):

| component | vertices | edges | closed | diameter mm | distance to largest mm | median to S0 mm | median to S1 mm | chosen |
|---|---|---|---|---|---|---|---|---|
| 0 | 95 | 95 | 1 | 11.265551 | 28.326850 | 47.092773 | 4.131341 | 0 |
| 1 | 276 | 276 | 1 | 35.521022 | - (is the largest) | 13.734334 | 3.396700 | 0 |
| 2 | 212 | 212 | 1 | 27.390484 | 8.446432 | 0.376799 | 9.453676 | 1 |

Component 2 is the only candidate that passes all four tests: it is not the largest perimeter (that is component 1, 276 vertices), it is 8.446 mm from that perimeter (> 4 mm), and its median nearest-wall distance is 0.377 mm to the inner sheet against 9.454 mm to the outer sheet, i.e. 9.08 mm smaller (rule asks for 0.5 mm). `evidence/phase.tsv` holds one row, `ran`.

Placement, checked before naming it: SPARTAN check on both wall clouds around the loop centre (29.48414661, 13.5492866, 448.8459955) mm gives a nearest S0 sample at 11.749 mm with 2275 samples inside 16 mm and 5773 inside 20 mm, and a nearest S1 sample at 17.810 mm with none inside 16 mm. The loop therefore sits in the concave inner (S0) sheet, and the outer sheet is a separate surface more than 17 mm away, so the hole is not a slit through both surfaces.

Renders, opened and described in section 7: `renders/boundary_overlay.png` (chosen loop in red inside the blue inner cloud, the black 276-vertex ordinary break below it), `renders/boundary_zoom_a.png`, `renders/boundary_zoom_b.png`.

### 2. Fixed-stock rebuild and the masks

`sfs_axes/select.py:194-198` reproduced: concatenate S0 then S1 (124980 rows), `step = ceil(124980/12000) = 11`, `Cr = C[:, 0:n:11]` gives 11362 columns, and `Cr.tobytes()` is byte-identical to Ticket 15's saved little-endian `normal` (True). The profile walls also match the pinned recipe (w0 stride 19 -> 2388 rows, w1 stride 32 -> 2489 rows, both byte-identical). Sampled columns split 4124 inner / 7238 outer.

Exact distance from each sampled inner column to the 212 boundary **segments** (point-to-segment, clamped; no centroid distance) gives the masks: 43 columns within 1 mm, 87 within 2 mm, 230 within 4 mm. All 11362 columns are listed in `evidence/mask.tsv` (distance blank on the 7238 exterior rows, e.g. line 4126 `4124 outer 8`).

The three masks are not identical to each other (rim1 != rim2 != rim4), so a dose contrast is admissible in principle; the arms are 43 / 87 / 230 omitted of 4124 interior columns (1.0% / 2.1% / 5.6% of the interior sample; 0.4% / 0.8% / 2.0% of all 11362).

### 3. Fit results, all 15 cells `ran`, fallback 0 in every cell

Turn is the sign-free angle from the seed; donor angle and foot offset are to the donor at (30.107, 12.692, 452.566) mm; `normal/point (own)` is on each fit's own sample and `normal/point (stock)` on the common full stock sample; profile mm on the fixed walls.

| condition | seed | turn deg | donor angle deg | donor offset mm | normal/point (own) | normal/point (stock) | profile mm |
|---|---|---|---|---|---|---|---|
| stock | raw620 | 55.023883 | 61.253649 | 14.965343 | 0.030375 | 0.060750 | 0.336235 |
| stock | raw1110 | 62.813889 | 61.252215 | 14.968874 | 0.030375 | 0.060750 | 0.336237 |
| stock | donor2 | 61.251772 | 61.251772 | 14.970038 | 0.030375 | 0.060750 | 0.336252 |
| rim1 | raw620 | 55.055006 | 61.284391 | 14.952521 | 0.030456 | 0.060750 | 0.337437 |
| rim1 | raw1110 | 62.844130 | 61.282953 | 14.956075 | 0.030456 | 0.060750 | 0.337460 |
| rim1 | donor2 | 61.282480 | 61.282480 | 14.957316 | 0.030456 | 0.060750 | 0.337521 |
| rim2 | raw620 | 55.045328 | 61.264851 | 14.981458 | 0.030560 | 0.060751 | 0.338220 |
| rim2 | raw1110 | 62.818938 | 61.263384 | 14.985116 | 0.030560 | 0.060751 | 0.338208 |
| rim2 | donor2 | 61.262899 | 61.262899 | 14.986398 | 0.030560 | 0.060751 | 0.338196 |
| rim4 | raw620 | 55.048469 | 61.266176 | 14.978812 | 0.030937 | 0.060751 | 0.338883 |
| rim4 | raw1110 | 62.819186 | 61.264710 | 14.982479 | 0.030937 | 0.060751 | 0.338841 |
| rim4 | donor2 | 61.264191 | 61.264191 | 14.983845 | 0.030937 | 0.060751 | 0.338865 |
| restored | raw620 | 55.023883 | 61.253649 | 14.965343 | 0.030375 | 0.060750 | 0.336235 |
| restored | raw1110 | 62.813889 | 61.252215 | 14.968874 | 0.030375 | 0.060750 | 0.336237 |
| restored | donor2 | 61.251772 | 61.251772 | 14.970038 | 0.030375 | 0.060750 | 0.336252 |

Guards asserted on the actual solver argument, not on a copy (`evidence/fits.tsv` columns 6 and 7): `exterior_sha256` is the same value `f2f64a24046f08185c2792e96bb6b956943714ab238c4d8c2afc58ab1e7c6e1d` in all 15 cells (the 7238 exterior columns, their order and six-vector bytes), and `fixed_profile_sha256` is the same `a44deefe6655c762648a2370c1818f1e58200d12503a330f3183b1a91c7827ee` in all 15. `restored` reproduces the stock endpoints and every cost row exactly, so the omit-and-restore path is byte-exact.

### 4. Baseline match to Ticket 15

`evidence/matches.tsv`: all three seeds 0.00000000 deg and 0.00000000 mm from Ticket 15's `own_stock` endpoints, inside the 0.01 deg / 0.01 mm tolerance. This is the check that the replay is the same pipeline, not a similar one.

### 5. Pre-registered criterion: NOT MET

The 4 mm arm was required to give, for at least two seeds of which one raw, at least 10 deg less turn **and** at least 10 deg smaller donor angle, with the foot offset worsening by no more than 2 mm.

| seed | d turn deg | d donor angle deg | d offset mm |
| (positive = condition minus stock; `diagnose.json` stores stock minus condition, hence its negative signs) | | | |
|---|---|---|---|
| raw620 | 0.024586 | 0.012527 | 0.013469 |
| raw1110 | 0.005297 | 0.012495 | 0.013605 |
| donor2 | 0.012419 | 0.012419 | 0.013807 |

No seed hits (`hit_seeds` empty, `criterion_met` false). The response is two to four orders of magnitude below the threshold and it goes the wrong way: with 230 hole-rim columns removed the axis turns 0.025 deg further from its seed and sits 0.013 deg and 0.014 mm further from the donor, not closer. The smaller arms behave the same way (rim1 is the largest shift: donor angle +0.0307 deg on raw620), so the effect is not monotone in mask size and no dose trend is claimed even though the masks differ. The reversal guard passes: the largest reversal on any smaller mask is 0.031 deg (rim1, raw620), against the 2 deg allowance (`evidence/diagnose.json`, `prereg.reversal_ok: true`).

What this does and does not say: within this one object and this one frozen sample, omitting every already-sampled interior point within 4 mm of the hole's rim (5.6% of the interior sample) does not change the ~61 deg turn that refinement makes. The claim is about the influence of the existing interior samples near the hole. It is not a prediction for a repaired mesh and it does not identify what does drive the turn.

### 6. Pins, provenance and corpus

- `pin.tar` sha256 `ae7af754785d1060fec5f8bfa27d592e93a6aad20fc22ee112ecf0a6f5936762`, equal to the Ticket 15 record (`evidence/pin.sha256`); `plain/` materialised from it and the refiner is the unchanged `sfs_axes.normalized.refine_axis_normalized` with `max_iters=60, tolerance=1e-6`.
- Inputs recomputed now and equal to Ticket 15 `evidence/provenance.tsv`: own_stock.npz `3e6f7961...f2b3`, raw620 `544b464b...af8d`, raw1110 `08ae07dd...20e7`, donor2 `3d15e494...0225`, S0 `54f73b93...ecd53`, S1 `64f5c95d...41d1c`.
- Run-local code: `hole_mask.py` `007162b2...033d6`, `diagnose.py` `63436b29...33c1` (`evidence/code.sha256`).
- Corpus: 7 files (mesh, S0, S1, own_stock.npz, three seeds) md5 identical before and after (`evidence/corpus_before.md5` == `corpus_after.md5`, `evidence/corpus_check.txt` = `corpus_unchanged=1`). No mesh repair, no assembly, no selector change.
- `evidence/repro.txt` holds the sbatch, both python command lines and the fingerprint sources.

### 7. Renders, each opened before this report was written

11 PNGs, `evidence/renders.tsv` 11 data rows. Common camera (elev 25, azim 40); a 10 mm scale bar on the two boundary zooms, the three mask figures and the axes figures. `boundary_overlay.png` carries **no** scale bar — it is the locational view, and the two zooms at +-1.6 x diameter give the scale (corrected on review; the first version of this paragraph claimed a bar on every boundary figure). The mask legends say "kept inner sample", which is the 2462 inner columns inside that view, not all 4124.

- `boundary_overlay.png`: red chosen loop inside the blue inner cloud; the black ordinary break (component 1) below and to the left; the faint grey third component at the left edge.
- `boundary_zoom_a.png`, `boundary_zoom_b.png`: the red oval clean and closed, the black ordinary broken edge 8.4 mm away, 10 mm bar.
- `mask_rim1/2/4.png`: the blue inner sheet with the red ring of omitted columns hugging the black loop, the light-grey outer sheet below and separated, counts in the title (43/87/230 of 4124).
- `axes_stock.png`: stock feet (x) and endpoint feet (o) exactly coincident, max foot displacement 0.000 mm; magnified +-1 mm panel labelled "not a to-scale view"; donor foot as the black star, 14.97 mm away.
- `axes_rim1/2/4.png`: the same camera and scale with 0.034 / 0.079 / 0.100 mm maximum foot displacement as printed in their titles, visible only in the magnified panel; recomputed here from the projection of the reference point (30.107, 12.692, 452.566) mm onto each fitted axis it is 0.0338 / 0.0787 / 0.0996 mm. The 0.031 / 0.021 figures are the *reversal in degrees* from section 5, a different quantity — the first version of this line conflated them. `axes_restored.png` plots data identical to stock (its PNG bytes differ only because the title does).

The foot metric and the donor reference were checked against the figures: the star in the axes renders is the donor's own foot (the point the offsets are measured from), and a small grey dot marks the fixed reference point (30.107, 12.692, 452.566) mm used to define the feet.

### 8. Tests, jobs and determinism

- Pinned `python -m pytest tests -q` in `plain/` on the compute node: `79 passed, 1 warning in 33.97s` (`evidence/pytest.log:12`; `evidence/pytest.exit` = 0). The log carries no host line, so the node is shown by `evidence/env.txt:1` `spartan-bm178.hpc.unimelb.edu.au`, python 3.10.20, numpy 2.2.6, scipy 1.15.2, matplotlib 3.10.3. (The first version of this line said 34.82 s; the log says 33.97 s.)
- `evidence/jobs.tsv` 6 rows, every one sacct-final and polled: 35521507 FAILED 1:0 (diagnose crashed on a numpy broadcast in a print of the interior counts after the gate had passed; the gate output in that job was identical to the final one), 35521553 COMPLETED 0:0, 35521693 COMPLETED 0:0, 35521762 COMPLETED 0:0, 35521798 COMPLETED 0:0, and srun 35521644 COMPLETED 0:0 for the wall-distance check. The file's header is `job_id run_id state exit_code polled indexed kind`: `polled` is 1 on all six rows, `indexed` is 0 on all six (section 11.1), and the `kind` column separates the five Slurm array submissions from the `srun` allocation used for the wall-distance check.
- Determinism: `fits.tsv` (`9e049cfd...48ac`), `mask.tsv` (`078b8342...16af`), `boundary.tsv` (`af7ef55f...7fd5`) and `matches.tsv` (`e82c0e46...b13e`) are identical across the last three job runs; reruns changed only figures.

### 9. Self-compliance

One row per requirement in the ticket, evidence as file:line. Run-local paths are relative to SPARTAN `runs/20261123-0305_2e951d9_t16-isolate-j01-interior-hole/`.

| # | requirement | evidence | status |
|---|---|---|---|
| S1 | native OBJ, Ticket 15 ordered walls, reused `own_stock.npz`, three seeds and the `2e951d9` selector; TORA python on a compute node | `evidence/repro.txt:3-6`, `evidence/pin.sha256:1` | met |
| S2 | sample, seed and ordered-wall SHA-256 validated against Ticket 15 `evidence/provenance.tsv` | `evidence/provenance_t16.tsv:2-8` — path, recomputed sha256 and the Ticket 15 row side by side, `match`=yes on all six (own_stock `3e6f7961`, raw620 `544b464b`, raw1110 `08ae07dd`, donor2 `3d15e494`, inner `54f73b93`, outer `64f5c95d`); the mesh has no Ticket 15 row and is matched by md5 in `corpus_before.md5` | met |
| S3 | corpus caveats read (AGENTS.md, `285-pot-c-01-scan-gap.md`) | `AGENTS.md:17` ("Corpus caveats — read before scoring") and `AGENTS.md:28` (Pot J 01 interior Bl0); `.scratch/pota-repro/issues/285-pot-c-01-scan-gap.md:39` and `:72-75` (interior lanes compromised, exterior still evidence); the run treats J01 interior as a defective input and makes no scoring claim | met |
| S4 | unchanged `refine_axis_normalized` with `max_iters=60, tolerance=1e-6` | SPARTAN `work/t16/diagnose.py:27-28` (`MAX_ITERS = 60`, `TOL = 1e-6`) and `:217` `vt = NZ.refine_axis_normalized(seed, X, max_iters=MAX_ITERS, tolerance=TOL)`; the solver itself is the pinned one, `plain/sfs_axes/normalized.py:210` `def refine_axis_normalized(vt_initial, X, max_iters=300, tolerance=1e-9, verbose=False)`, from `pin.tar` sha256 `ae7af754…6762` | met |
| S5 | baseline endpoints match Ticket 15 within 0.01 deg / 0.01 mm for all three seeds | `evidence/matches.tsv:2-4` (0.00000000 / 0.00000000) | met |
| S6 | boundary enumeration, fan triangulation if needed, connected components, census fields, tie-break by smallest vertex index | `work/t16/hole_mask.py:24-112`; `evidence/boundary.tsv:2-4` (counts, closure, diameter, distance, medians) and `evidence/census_centre.tsv:2-4` (centroid per component, recomputed from `hole.json` vertex lists and the OBJ, section 11.4); no perimeter tie occurred, so the tie-break is implemented but not exercised | met |
| S7 | qualifying rule (closed degree-two, not the largest, >=4 mm away, S0 median >=0.5 mm smaller than S1) and exactly one | `evidence/boundary.tsv:4`; `evidence/phase.tsv:2` | met |
| S8 | same-native-frame placement verified and the mesh overlay inspected before naming the hole | section 1 wall-distance check ran as srun 35521644, `evidence/sacct_final.txt:7` COMPLETED 0:0; overlay and both zooms opened (`renders/boundary_overlay.png`, `boundary_zoom_a/b.png`). Its printed distances were not captured to a file, so the numbers in section 1 rest on that run's stdout only — the gap the external reviews flagged (section 11.4) | met (numbers not retained) |
| S9 | census and boundary renders preserved regardless; blocked path only if no unique component | `evidence/boundary.tsv`, `renders.tsv:2-4`; phase is `ran`, so no blocked row needed | met |
| S10 | no hole inferred from point density, normal residuals or axis outcomes | `work/t16/hole_mask.py:59-112` uses mesh topology only; the wall clouds are used for the interior/exterior median only, after the topology decision | met |
| S11 | exact concatenation and stock stride reproduced, byte identity with Ticket 15 `normal` | `evidence/diagnose.json` `steps.byte_identical_stock: true`, `steps.w0_w1_pinned_stride: true` | met |
| S12 | wall label and original row index per sampled column from full wall lengths and stride indices | `evidence/mask.tsv:2-11363` (all 11362 columns; 4124 inner, 7238 outer) | met |
| S13 | point-to-segment distance to boundary segments, clamped, zero-length as point, not centroid | `work/t16/diagnose.py:84-93`; `evidence/mask.tsv` distances | met |
| S14 | five conditions; omit only inner columns at <=1/2/4 mm after the stride; keep order and bytes; restored exact with no refill or re-stride | `work/t16/diagnose.py:30`, `evidence/fits.tsv:14-16` (restored identical to `fits.tsv:2-4`) | met |
| S15 | empty mask = explicit no-op reusing stock; identical adjacent masks flagged | no mask is empty (43/87/230); masks differ, recorded in `evidence/diagnose.json` `prereg.masks_identical` | met (n/a) |
| S16 | three seeds x five conditions; exterior column set, order and bytes identical in every fit, asserted on the solver argument | `evidence/fits.tsv:2-16`, column `exterior_sha256` constant `f2f64a24...6e1d` | met |
| S17 | Ticket 15 profile scoring arrays byte-identical in every condition | `evidence/fits.tsv` column `fixed_profile_sha256` constant `a44deefe...77ee` | met |
| S18 | report turn, donor angle, offset, normal per point on the common stock sample, profile mm, and normal per point on the fit's own sample separately | `evidence/fits.tsv:2-16` columns 11-16; section 3 table | met |
| S19 | fallback reported by cell | `evidence/fits.tsv` column `fallback` = 0 in all 15 cells | met |
| S20 | pre-registered criterion evaluated, full results reported even on failure, smaller-mask reversal guard | section 5; `evidence/diagnose.json` `prereg` | met (criterion not met) |
| S21 | conclusion limited to the influence of existing interior samples near the hole | section 5 last paragraph | met |
| S22 | `boundary.tsv`, `phase.tsv` (one row), `mask.tsv` (every column), `fits.tsv`, `matches.tsv` with the stated columns | `evidence/boundary.tsv:1`, `phase.tsv:1`, `mask.tsv:1`, `fits.tsv:1`, `matches.tsv:1` | met |
| S23 | `renders.tsv` kinds boundary, mask, axes; common camera and mm scale; stock and each nonempty mask; baseline and endpoint feet visible at the zoom scale | `evidence/renders.tsv:2-12`; section 7 — all 11 files opened; 10 mm bar on both zooms, the three masks and the axes figures, and **none** on `boundary_overlay.png` (locational view only; section 7 records the correction) | met (overlay has no bar) |
| S24 | geometry and code on Spartan, small evidence fetched to `C:/PR/artifacts/axis-parity-16/` | SPARTAN `work/t16`; `C:/PR/artifacts/axis-parity-16/evidence/` (tables, JSON, logs, `renders/` 11 PNGs; no mesh or HDF5 fetched) | met |
| S25 | `repro.txt`, `corpus_before.md5`/`corpus_after.md5`, `jobs.tsv` with polled flag, every job polled | `evidence/repro.txt`, `evidence/corpus_*.md5` (identical), `evidence/jobs.tsv:1-7` — header `job_id run_id state exit_code polled indexed kind`, six rows, `polled`=1 on every row, `indexed`=0 on every row (no index row exists; blocker in section 11.1) | met |
| S26 | pinned pytest on a compute node with `pytest.log` and `pytest.exit` | `evidence/pytest.log:12` `79 passed, 1 warning in 33.97s`; `evidence/pytest.exit` = 0; node `spartan-bm178` in `evidence/env.txt:1`; the pinned `tests/` come from `plain/`, the `pin.tar` at `2e951d9` | met |
| S27 | figures and tests reviewed before returning | section 7 lists the 11 PNGs opened; `evidence/pytest.log:12` read; an act, not a recordable output — an external reviewer opened 9 of 11 and found them consistent with their captions (section 11.3) | met (act) |
| S28 | one End state, self-compliance rows, a separate read-only table | this section; section 10 (same worker, R13 not met) and section 11.3 (a genuinely separate read-only reviewer, a fresh sub-agent that never saw this worker's reasoning); End state below | met |
| S29 | only the ticket write-back modified in this worktree; no commit, merge or close | `git status --short` in `C:/PR/worktrees/sfs/16` lists only this file | met |
| S30 | no selector changes, mesh repairs, corpus writes or assembly runs | `evidence/corpus_check.txt` = `corpus_unchanged=1`; no assembly submission in `evidence/jobs.tsv` | met |

### 10. Read-only DeepSeek compliance pass

Same requirement groups, checked a second time from the **fetched evidence only** (tables, hashes, PNGs opened here), not from the run logs and not from the code's own assertions. **This pass is by the same worker; it is not an independent review.** The lead's own verification and any independent reviewer remained to be done at that point; the independent reviewer arrived afterwards as section 11.3 — a separate sub-agent, not this worker.

| # | what was re-checked from the fetched evidence | how | status |
|---|---|---|---|
| R1 | phase gate: one qualifying component, all tests, not the largest, >=4 mm, S0 median smaller | `evidence/boundary.tsv:2-4` recomputed by eye from the row values; `evidence/phase.tsv:2` | holds |
| R2 | census complete: all three components present with vertex/edge counts and the largest marked | `evidence/boundary.tsv:1-4` | holds |
| R3 | mask completeness: one row per sampled column, exterior distances blank | `evidence/mask.tsv` 11363 lines; sample at line 4126 has an empty distance | holds |
| R4 | omit counts agree with the condition names | `evidence/fits.tsv` `omitted_n` 43/87/230 | holds |
| R5 | restored is the same fit as stock | `evidence/fits.tsv:14-16` equals `evidence/fits.tsv:2-4` on every numeric column and both hashes | holds |
| R6 | exterior and profile arrays frozen across conditions | two constant hash columns in `evidence/fits.tsv` | holds |
| R7 | baseline identical to Ticket 15 | `evidence/matches.tsv:2-4` all zeros | holds |
| R8 | criterion not met and no dose trend | `evidence/diagnose.json` `prereg.criterion_met: false`, `hit_seeds: []`; section 5 deltas non-monotone | holds |
| R9 | renders actually exist, are non-trivial and show what is claimed | opened `boundary_overlay`, `boundary_zoom_a`, `boundary_zoom_b`, `mask_rim1`, `mask_rim4`, `axes_stock`, `axes_rim4` at full size; the first two iterations of the axes figures had the feet outside the plotted window (only the scale bar showed); the third was complete but its star marked the fixed reference point rather than the donor foot, and the fourth (shipped) draws the donor foot as the star with the reference as a grey dot (an external reviewer checked these earlier files; see section 11.3) | holds |
| R10 | provenance: pins and inputs match Ticket 15 | recomputed sha256 of the six inputs and of `pin.tar` against `evidence/pin.sha256` and Ticket 15 `provenance.tsv` | holds |
| R11 | tests and jobs terminal | `evidence/pytest.log` tail `79 passed`, `evidence/pytest.exit` 0; `evidence/jobs.tsv:2-7` all COMPLETED except the stated FAILED 1:0 | holds |
| R12 | corpus untouched | `diff corpus_before.md5 corpus_after.md5` empty, 7 files | holds |
| R13 | independence of this pass | performed by the ticket worker | **not met** |

## Follow-up (evidence only, 2026-11-23)

Scope: evidence repair and verification. No fit, build, test, Slurm submission or assembly was rerun; on Spartan `boundary.tsv` is still `af7ef55f28238d3c04aa6cc39eeb7fd5`, `fits.tsv` `9e049cfd28af0ff95e5d7577e97048ac`, `mask.tsv` `078b8342c1e426a93aabe926943116af`, `matches.tsv` `e82c0e469e626b71363f16987dfbd13e`, `phase.tsv` `9e374dc97a630d4739fe29cfd4fefb3c`, `diagnose.json` `c97863cb5ac31f246ca3d52e60e665e1` — the write-back's values, and the renders were not re-rendered. `jobs.tsv` was rewritten and now hashes `f62fd3352afd9e4315386b628f348690`; the repaired copy was fetched over the stale local one.

### 11.1 `jobs.tsv` schema and the run index

`evidence/jobs.tsv` now carries `job_id run_id state exit_code polled indexed kind`, six rows, `polled`=1 and `indexed`=0 on every row, `kind`=`array` for 35521507 (FAILED 1:0) and 35521553 / 35521693 / 35521762 / 35521798 (COMPLETED 0:0), `kind`=`srun` for 35521644 (COMPLETED 0:0; sacct JobName `python3`, elapsed 00:00:03). `kind` is the only column beyond the six the ticket names; it keeps the six terminal records distinguishable without prose in `state`.

`indexed`=0 was checked on Spartan rather than assumed: `grep -c t16 /data/gpfs/projects/punim2657/SfSpp/runs/index.tsv` = 0; the newest index rows are the four Ticket 15 runs (jobids 35516494, 35516607, 35517358, 35517466). No row for this run exists.

No row was appended. Blocker, in the guide's own terms (`docs/agents/runs-and-worktrees.md:32-42`): the row is written at submission by `scripts/new_run.sh`, and this run used bare `sbatch` at 03:04; the run directory has no `run.json`, so `commit` and `tag` would be reconstructed from the directory name; one row carries a single `jobid` while this run has six sacct records; and the guide assigns `verdict` and `human_note` to a person or the coordinating session, never to the job. If the lead wants it, the row to append is:

```
20261123-0305_2e951d9_t16-isolate-j01-interior-hole<TAB>35521553<TAB>2e951d9<TAB>t16-isolate-j01-interior-hole<TAB>(verdict)<TAB>(human_note)
```

The convenience checker cannot reach this directory from here: `scripts/check_runs_index.py` exists at `C:/PR/scripts/check_runs_index.py` in the laptop repo only, `/data/gpfs/projects/punim2657/sfs_preprocessing/scripts/` has no copy (`grep -i index` returns nothing), and the laptop cannot see `/data/gpfs`. The index state above was read directly instead.

### 11.2 Attribution of the two other worktrees in the initial snapshot

Neither worktree belongs to the `C:/PR` repository: `git worktree list` in `C:/PR` shows `C:/PR` and two copilot worktrees, and the other two are worktrees of different repositories — `C:/PR/worktrees/sfs/15/.git` = `gitdir: C:/PR/SfSpp_preprocessing/.git/worktrees/15` (the same repository as this ticket's `C:/PR/worktrees/sfs/16`, `.git/worktrees/16`), and `C:/PR/worktrees/sherd-worn/05/.git` = `gitdir: C:/PR/sherd-worn/.git/worktrees/05`.

State of each at the time of writing, from read-only git queries (`status`, `log`, `cat .git`); nothing was written in either:

- `sfs/15`: `M .scratch/axis-parity/issues/15-trace-j01-refinement-objectives.md` and `?? work/`; that ticket's mtime is 2026-11-23 02:58; HEAD `47d10db` 2026-11-22 23:57:26 `Ticket 15-trace-j01-refinement-objectives: start`. The modification predates this ticket's first write (submit script 03:04, run directory 03:05, ticket write-back 03:26); its shape — Ticket 15's ticket file modified plus an untracked run-local `work/` — matches a Ticket 15 write-back in that worktree, which is an inference from file shape and timestamps, not an identity.
- `sherd-worn/05`: clean; HEAD `7c01ca5` 2026-11-23 03:39:22 +1100 `uneven-round-fix 05: scripts to measure abrade on Spartan`, a commit made after this ticket's write-back.

What the evidence supports: activity in two other repositories' worktrees overlapped this run in time, which is consistent with the shared-session report; it does not identify which session owned that activity, and no evidence here ties it to this worker. This worker's writes are the ticket file, `C:/PR/artifacts/axis-parity-16/` (03:20 and 03:23) and the Spartan run directory.

### 11.3 Separate read-only review (external reviewer, not this worker)

A fresh sub-agent was given the ticket and the fetched evidence only — no Spartan access, no write access, no sight of this worker's transcript — and asked to check the evidence against the requirements and to report only what the files show. Its table, verbatim:

| # | requirement | status | evidence |
|---|---|---|---|
| 1 | boundary.tsv: exactly one qualifying component; phase.tsv agrees, one row | met | 3 components, all `closed=1`; every vertex degree 2, V=E, edge sum 95+276+212 = 583 = `hole.json` `n_boundary_edges`; largest = component 1 (276 v, only blank `perimeter_distance_mm`); comp 0 fails the wall rule (`inner 47.092773` vs `outer 4.131341`, S0 42.96 mm **larger**); comp 2 `boundary.tsv:4` 8.446432 ≥ 4.0 and 9.076877 ≥ 0.5; `phase.tsv` header + one `ran` row |
| 2 | mask.tsv: 11362 rows, idx 0..11361, exterior blanks, flags 43/87/230, no exterior flags | met | 11362 rows, every `sample_idx` once, inner 4124 / outer 7238, all outer rows blank distance and 0 flags, flag totals = `fits.tsv` `omitted_n`, thresholds nested with 0 violations (rim1 max 0.997592 / min non 1.049542; rim2 1.944399 / 2.040936; rim4 3.978999 / 4.002402) |
| 3 | fits.tsv: 15 rows; hashes constant; fallback 0; restored = stock numerically | met | 15 rows, all `state=ran`, all `fallback=0`, `normal_n` = 11362 − `omitted_n`, one `exterior_sha256` `f2f64a24…6e1d`, one `fixed_profile_sha256` `a44deefe…77ee`, each restored row equals its stock row on all 16 columns except the label |
| 4 | matches.tsv: three seeds at 0 / 0 | met | `matches.tsv:2-4` all `0.00000000` deg and mm |
| 5 | diagnose.json prereg and deltas vs fits | met | `criterion_met=false`, `hit_seeds=[]`, `reversal_ok=true`, `masks_identical` false both ways; deltas agree with fits to 1e-6 up to sign (`diagnose.json` stores stock−condition) |
| 6 | corpus_before vs corpus_after | met | byte-identical, 7 lines each; `corpus_check.txt` = `corpus_unchanged=1` |
| 7a | pytest.log tail 79 passed | met (minor) | `79 passed, 1 warning in 33.97s`; report said 34.82 s — corrected in section 8 |
| 7b | pytest.exit / gate.exit / fit.exit = 0 | met | each file contains `0` |
| 8 | sha256 digests real; pin matches report | met | `code.sha256` two well-formed 64-hex values; `pin.sha256` `ae7af754…6762`, repeated on the Ticket 15 line |
| + | jobs.tsv final sacct states | **not met at the time** | `sacct.txt` showed the five jobs RUNNING and had no 35521644 line — closed in section 11.4 by `sacct_final.txt` |
| F1 | boundary_overlay.png | supports, partial | red chosen loop, black break and a faint third loop visible; **no 10 mm bar** — section 7 corrected |
| F2 | boundary_zoom_a.png | supports | red oval, black break below-left, 10 mm bar present but drawn across the black loop |
| F3 | boundary_zoom_b.png | supports (presence only) | both loops and a clear bar; in this projection the loops nearly touch, so the 8.4 mm gap is a table fact, not a figure fact |
| F4 | mask_rim1.png | supports, partial | 43 red ×, legend "kept inner sample (2419)" is the in-view subset, not all 4124 — noted in section 7 |
| F5 | mask_rim2.png | supports | 87, legend 2375 |
| F6 | mask_rim4.png | supports | 230, legend 2232, same camera and layout |
| F7 | axes_stock.png | partial | two panels and the 0.000 mm title, but stock (x) and endpoint (o) collapse into one marker, so x/o and the three seed colours are not individually legible |
| F8 | axes_rim1.png | supports, number corrected | title says **0.034 mm**; the report's 0.031 was the reversal in degrees — section 7 corrected |
| F9 | axes_rim2.png | supports, number corrected | title says **0.079 mm**; 0.021 was the reversal in degrees |
| F10 | axes_rim4.png | supports | 0.100 mm, green segment between circle and × |
| F11 | axes_restored.png | supports | 0.000 mm, same markers as stock; PNG bytes differ only by the title |

Its "not verifiable from these files alone" list: the underlying geometry (diameters, 8.446 mm, medians taken as stated), the srun 35521644 placement numbers, the byte-identity assertions (arrays not fetched), the code against its hashes (not fetched then), the final Slurm states (`sacct.txt` a mid-run capture), and figure provenance. Its internal-consistency finding: the five tables and JSON reconcile exactly, and the prose carried three real inconsistencies — the axes displacements, the pytest time, and the poll record — plus the missing bar on the overlay. All four are corrected in sections 7 and 8 and 11.4.

### 11.4 What the two reviews changed, and what remains open

Fixes applied after the reviews. Evidence-only work: no fit, build, test, Slurm submission or assembly was rerun, and `boundary.tsv`, `fits.tsv`, `mask.tsv`, `matches.tsv` keep their write-back hashes (section 11 preamble).

1. **Post-run sacct capture.** `evidence/sacct_final.txt` (19 lines) was taken after the run: 35521507 FAILED 1:0 ended 03:06:37, 35521553/35521693/35521762/35521798 COMPLETED 0:0, 35521644 COMPLETED 0:0. `sacct.txt` is labelled in section 8 as an in-flight capture, not a final state.
2. **Retained cause for the FAILED job.** `logs/slurm-35521507.out:23` `Traceback (most recent call last)` and `:28` `ValueError: operands could not be broadcast together with shapes (11362,) (4124,)`; the file is fetched to `evidence/logs/`.
3. **pytest duration and host.** Section 8 now says 33.97 s (from `pytest.log:12`), with the node from `evidence/env.txt:1`.
4. **Render claims.** Overlay bar caveat, the 0.034/0.079/0.100 mm displacements (recomputed here as 0.0338/0.0787/0.0996 from the axis projection), restored "plots identical, not byte-identical", mask-legend subset note (section 7).
5. **Census centre.** `evidence/census_centre.tsv` holds a centroid per component, recomputed from `hole.json` vertex lists and the native OBJ: component 0 (79.406073, 44.780439, 447.305022), component 1 (34.798990, 20.293291, 439.011839), component 2 (29.484147, 13.549287, 448.845996) mm — the chosen loop's centre, matching the figure title to 1e-5 mm.
6. **Provenance revalidated.** `evidence/provenance_t16.tsv` lists path, recomputed sha256 and the Ticket 15 row side by side; six of six match. The mesh has no Ticket 15 row (it is matched by md5 in `corpus_before.md5`).
7. **`plain/` is the pin.** `evidence/plain_vs_pin.txt`: 21 files compared against the T15 `pin.tar` members, 0 mismatches; the tar's sha256 is `ae7af754…6762`, the value the ticket pins.
8. **Rows and wording.** S2, S3, S4, S6, S8, S23, S24, S26, S27, S28 now carry file:line pointers and an honest qualifier where the evidence is partial; section 5 states the sign convention; R9's "earlier iterations were empty" is corrected to the actual three-iteration history.
9. **Run-local code fetched.** `evidence/code/` holds `hole_mask.py`, `diagnose.py`, `census_centre.py`, `plain_vs_pin.py` and `submit_t16.sbatch`, so a reviewer can read the implementation behind S6, S10, S13 and the `plain/` claim instead of trusting hashes.

A second, fresher read-only auditor (a different sub-agent again, given this file and the fetched evidence and nothing else) returned 29 rows: 28 `yes`, one `unclear` — the same-native-frame placement row, for the reason recorded under the first item below. Its table is in the worker's reply to the lead.

Still open, and why:

- **srun 35521644's printed distances** (nearest S0 11.749 mm, 2275 points within 16 mm, no S1 point within 16 mm) exist only in the section 1 prose. The srun's stdout was never redirected and is gone; the sacct row is its only record. Closing this needs the check re-run, which this follow-up is not allowed to do.
- **`plain_vs_pin.txt` holds only its summary line** (`files_compared 21 mismatches 0`), not the per-file list; the script that prints per-file detail is in `evidence/code/plain_vs_pin.py`, and re-running it would mean another Spartan job, which this follow-up does not do.
- **The run index row.** Still absent; the guide gives that row to the submission script and its `verdict`/`human_note` to a person or the coordinating session (section 11.1).
- **pytest.log records no host and no commit.** The host is supplied by `env.txt`; the pinned `tests/` are shown by `plain_vs_pin.txt`.
- **Three extra PNGs in the laptop artifacts root** (`axes_rim4_v3.png`, `axes_rim4_v4.png`, `axes_stock_v4.png`) are earlier iterations, not evidence rows; `md5sum` confirms both v4 files are byte-identical to the shipped `renders/axes_rim4.png` / `renders/axes_stock.png`. They are declared here rather than deleted.
- **The self-compliance table is the worker's own.** The independent table is 11.3; a second, fresh read-only auditor re-checked the whole ticket after these fixes and its table is in the worker's reply to the lead.

**End state:** ready

### Lead acceptance — 2026-11-23

Accepted the completed diagnostic as a negative result. The samples already present around the hole did not account for the roughly 61° drift. Across three seeds and three removal radii, the donor-angle difference changed by at most 0.031°. The effect of restoring the missing surface remains open.

- Spartan `runs/index.tsv:1011` records `20261123-0305_2e951d9_t16-isolate-j01-interior-hole` once, under the first successful fit job `35521553`. The final job table and index row are `evidence/jobs_indexed.tsv` and `evidence/index_verified.tsv`.
- Frame verification job `35551072` finished `COMPLETED 0:0`. The frozen OBJ and both wall samples were compared in their native coordinates without applying a transform. The hole's 212 rim vertices had median nearest-sample distances of 0.376799 mm to the inner wall and 9.453676 mm to the outer wall. Both other boundary components were nearer the outer wall. `evidence/frame-verify/boundary.tsv`, `phase.tsv`, and `hole.json` matched the originals byte for byte. The lead inspected the new boundary zoom. These retained measurements establish placement at the tested rim. The earlier unretained centre-distance output was not used.
- The initial Baton snapshot covered overlapping sessions in the shared parent directory. Ticket 15's and sherd-worn 05's own Baton records corroborate the sibling changes. The 16 worktree contained only its own write-back and the scoped whitespace check passed after the follow-up.
- verified: `artifacts/dsh-handover/axis-parity-16/accept.py` -> exit 0, `Verified phase ran, 3 boundary components and 7 jobs`.

**DSH cost:** Opencode Go flat-rate. Session log recorded 12,232,749 tokens including cache reads (157,539 output).
