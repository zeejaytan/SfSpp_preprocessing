# 62 — Fix the per-rung normal estimation so a full-round shell stops flipping

**What to build:** a diagnosis of **why** the pipeline's own normal re-estimate inverts one whole
sheet on a round piece, and a measured candidate fix that a person can then decide to adopt. The
fix must be opt-in: no shipped default changes in this ticket.

**Answers:** U19, E1

**Blocked by:** 61 (same source file; run 61 first, its run directory is this ticket's baseline)

**Status:** resolved
**Working in:** chat on Thinkbook16 (2026-11-02)
**Branch:** 62-fix-normal-estimation, in /c/PR/worktrees/sfs/62
**Worker:** DeepSeek (cursor_code, model grok-4.7), 2026-11-03; verified by the lead

## Spec

### Given (measured facts this stands on)

1. On J1 the per-rung re-estimate is sign-flipped on **41.63 %** of 19312 points against the mesh;
   the other eight sit at 0.18–1.70 % (ticket 60, `out/analysis2/B_normals.tsv`). The corpus
   cloud's own stored normals on J1 are 0.40 % flipped — the pipeline's field is worse than the
   one it was handed.
2. The split is **per sheet, not per point**: S0 89.75 % flipped, S1 2.40 %, and the wall-like
   rate differs the same way (0.020 vs 0.141). That is the signature of an orientation pass that
   decided a hemisphere once and propagated it, not of per-point noise.
3. The default path is CGAL `pca_estimate_normals` with `nb_neighbors = max(5, min(20, n/1000))`
   (`mesh_processing_headless.cpp:680`), then `CGAL::mst_orient_normals` at `n24orientK`
   (`:806-809`). For J1's 19312 points that is **k = 19**, and the printed line for the run of
   record reads `[NORMAL-24] ... n=19312 k=19`.
4. The wall is ~2.1 mm (ticket 60's per-piece thickness, J1 1.876 mm) and the rung spacing is
   0.45 mm-ish, so a 19-neighbour ball has a radius of several millimetres — **wider than the
   wall**. On a full-round shell the kNN graph therefore bridges the two faces, and MST orientation
   over a bridged graph can only give the two faces one consistent direction: exactly what is
   observed. This is the prime suspect, not yet measured.
5. A radius path exists (ticket 24): `SFS_NORMAL_MODE=radius` with `SFS_NORMAL_RADIUS_MM` or
   `SFS_NORMAL_RADIUS_AUTO=1` and `SFS_NORMAL_RADIUS_MULT` (multiple of the cloud's own spacing).
   It is untested against this failure.

### Stage 1 — measure the bridging (read-only, no pipeline change)

On J1 and, as controls, J2 (the nearest-resolution piece) and J7 (the other wrapping piece):

- the distribution of the 19th-neighbour distance, against the piece's wall thickness;
- the fraction of kNN-graph edges that cross the wall (an edge crosses when its two endpoints' mesh
  normals are opposed, `dot < -0.4`, and their separation is below twice the wall);
- which MST component the flipped sheet belongs to: is S0's flipped region one connected component
  of the bridged graph, or many small ones?
- the same three numbers at k = 6, 8, 10, 12, 19 and at radius 0.6 / 0.8 / 1.0 / 1.4 mm, so the
  threshold where bridging stops is bracketed by measurement rather than guessed.

Deliverable: a table and one figure (crossing fraction against neighbour scale, with the wall
thickness drawn as a vertical line).

### Stage 2 — the candidate fix, judged end to end

Take the smallest neighbour scale at which J1's bridging collapses (the knee). Run the nine pieces
at `SFS_WORNESS=0.7` with the t59 patch applied, in two cells:

- **F** — that normal setting, stop **disarmed**: does the field fix itself, and do the surfaces
  stay as t55's?
- **FA** — that normal setting, `SFS_BREAK_STOP=1`: does the stop then work (this duplicates
  ticket 61's IA cell on a different field; report both, they are different fields and must not be
  conflated).

Per piece: the consumed-field flip fraction and folded angle (against the mesh, as ticket 60 did),
`nS0`, `blindDeg`, `farS0`, `dc_ge1`, `bl0`, `genuine` from `check_separation.py`
(`--geom --mesh-dir --walls --pieces`, full names, comma-joined).

### Gates

1. `[NORMAL-24]`/equivalent line shows the intended neighbour scale took effect on every piece
   (radius mode and count mode print different fields — quote the line).
2. The fix must **not** move the other eight: each of J2–J9 within 2 percentage points of its
   current flip rate and its `nS0` within 10 % of t55's, or the fix is a regression and the
   ticket says so.
3. Nothing is adopted on the strength of J1 alone; a fix that only works on the wrapping piece is
   recorded as such.

### The outcome this ticket exists to reach

- **A usable setting** — J1's flip rate falls to at most 5 %, folded median stays at or below 5°,
  the eight do not regress, and the armed stop behaves better than in ticket 59: propose the
  setting as opt-in (a named switch with its measured numbers), give the exact call line, and put
  the proposal in the ticket for the conservator — **do not change a default**.
- **No usable setting** — say so with the bracketing numbers, and recommend either carrying the
  corpus normals as a documented pre-step or leaving the field alone.

### Deliverables

- Run directory `/data/gpfs/projects/punim2657/SfSpp/runs/<YYYYMMDD-HHMM>_<git7>_t62-normalfix`,
  `run.json`, `submit*.sbatch`, `logs/`, `out*/`, index row appended.
- `stage1_bridging.tsv`, `stage2_pieces.tsv`, `decision_table.tsv`, and the bridging figure.
- `## Results` in this ticket: jobs with `sacct`, the gates with command and value, the tables,
  the verdict, what was not measured.
- **No commits, no tracked source edits, no default changed.** Any patch stays in the run
  directory.

### Budget and discipline

Three sbatch jobs, wall time 2 hours total. Compute nodes only; corpus read-only; poll each job
with `scripts/slurm_poll.sh <JOBID>` and record `sacct` State/ExitCode. If Stage 1 shows no
bridging at all, the hypothesis is dead — stop, report that, and do not spend Stage 2's jobs.

## Results

Two runs, both from commit `ca520fef1be3a2f6bd9e8e8e8ef904ca54aed25b`. No tracked source was edited and no default was changed. The stop patch is the t61 copy of `work/t59-stop.patch` (md5 `54cb4e79dab0ecd1a8a44bdca00dc679` on both sides). It applied as 109 added lines and 0 removed.

The wall-bridging suspect is refuted: the neighbour ball never reaches across the wall. A different threshold was found in its place. Run with `SFS_NORMAL_MODE=radius SFS_NORMAL_RADIUS_MM=1.0`, the pipeline's own field on J1 falls from **41.63 %** flipped to **0.20 %**, and none of the other eight regresses on any gate. The armed stop no longer collapses J1. It still does not stop at the break edge.

### Jobs

| job | name | sacct State | ExitCode | elapsed | what |
|-----|------|-------------|----------|---------|------|
| 34228689 | t62S1 | COMPLETED | 0:0 | 00:00:21 | Stage 1, read-only bridging measurement |
| 34228768 | t62S2 | COMPLETED | 0:0 | 00:04:54 | Stage 2, patched build plus cells F and FA, nine pieces |
| 34228890 | t62S3 | COMPLETED | 0:0 | 00:00:51 | scoring, ticket 61's `measure61.py` method unchanged |

- Stage 1 run: `/data/gpfs/projects/punim2657/SfSpp/runs/20261103-0028_ca520fe_t62-normalfix`.
- Stage 2 run: `/data/gpfs/projects/punim2657/SfSpp/runs/20261103-0035_ca520fe_t62-normalfix-s2`.
- `index.tsv` rows 371–374. **Row 371 has an empty jobid.** It was written for the first Stage 1 submission, which `sbatch` rejected for DOS line breaks; that submission never ran. Row 372 is the same run with its real job, 34228689. Rows 373 and 374 are 34228768 and 34228890. `verdict` and `human_note` are empty on all four.
- Three jobs, within the budget of three. Total compute was 6 m 06 s.
- The S2 job checked the frozen corpus inputs before and after (`inputs-S2.diff` is empty). Stage 1 did the same for its three meshes.

### Stage 1 — the bridging is not there

Instrument: `work/stage1_bridging.py` in the Stage 1 run.
- **Input:** t61 cell U's growth-call rung, `outU/normals/<piece>_call1.ply`, which is the k=19 re-estimated field the stop consumed.
- **Mesh normal per point:** from the exact nearest triangle.
- **Sheet per point:** whichever of t61 U's S0 and S1 is nearer.
- **Flipped set:** ticket 60's majority-sign rule.
- **Crossing edge:** the two endpoints' mesh normals have dot < -0.4 and are less than 2 × wall apart.
- **Walls:** ticket 59's `t_piece`, J1 1.876, J2 2.178, J7 2.839 mm.
- **Calibration:** the instrument reads J1's field as 41.64 % flipped (ticket 60: 41.63 %), with S0 93.23 % flipped and S1 3.56 %.

Verdict: **wall bridging is refuted** as the cause of J1's flip. This is a claim about the method's suspected mechanism: the suspect was wrong.

- **The ball never spans the wall.** On all three pieces, at every k, **0 %** of points have their k-th neighbour beyond the wall. J1 at k=19 has a 19th-neighbour distance of median **1.26 mm** (p95 1.37, max **1.63 mm**), against a 1.876 mm wall. J2 at k=19 has median 1.24 mm against 2.178; J7 has 1.26 mm against 2.839.
- **J1 crosses the wall less than the controls do.** Across all thirteen neighbour settings, J1's crossing-edge fraction is **0.26–0.55 %**, against **0.93–1.42 %** on J2 and **0.42–1.00 %** on J7. The share of points touching at least one crossing edge is 0.53–3.61 % on J1, 1.75–12.69 % on J2 and 1.04–6.59 % on J7.
- **No knee.** On J1, going from k=6 to k=19 moves the crossing fraction only from 0.27 % to 0.38 %, a smooth drift.
- **The flip is one connected sheet.** At every scale except the bare 0.6 mm ball (which breaks J1's graph into 1024 components), the graph is one component. J1's flipped points form 9–13 components, with **99.61–99.69 %** of them in the largest. Within S0 they form 2–4 components, with **99.96–99.99 %** in the largest.

The crossing fraction per scale is in `out/stage1_bridging.tsv` (also `.json`), with `work/plot_stage1.py` beside it. The figure is `out/stage1_bridging.png` (md5 `f6ab510257612c96a8dc62d94a21018f`): crossing fraction against neighbour scale, one panel per piece, wall thickness drawn as a vertical line. All three curves are flat at 10⁻³–10⁻², and all sit well left of the wall line.

### The threshold that replaced it (replica, not the pipeline)

The same script also runs a **replica** of the pipeline's normal step at each scale: a plane fitted over each neighbourhood, then minimum-spanning-tree orientation over the same graph, weighted by 1 − |nᵢ·nⱼ|, seeded at the max-z point and oriented toward +z, as CGAL `mst_orient_normals` does. It is **not bit-identical to CGAL**. It agrees with the pipeline at k=19: 41.88 % flipped against the pipeline's 41.63 %, with S0 93.33 % flipped against 93.23 %.

| J1, replica | k=6 | k=8 | k=10 | k=12 | **k=19** | r 0.8 | r 1.0 | **r 1.4** | r 0.6 clamped | r 0.8 clamped | r 1.0 clamped | **r 1.4 clamped** |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| flipped | 0.24 % | 0.24 % | 0.22 % | **0.19 %** | **41.88 %** | 0.25 % | **0.21 %** | **42.06 %** | 0.25 % | 0.25 % | 0.21 % | **41.56 %** |

"Clamped" means the radius ball limited to the pipeline's 5-to-20-neighbour range. The bare 0.6 mm ball is left out of the table: only 1 point is reached from the seed, so its rate means nothing. The replica's J2 rates are 0.53–0.85 % and J7's are 0.26–0.37 % at every setting from k=6 up. The controls are flat.

So in the replica the flip appears between k=12 and k=19, and between a 1.0 and 1.4 mm radius. **The cause of that threshold is not measured.** It is not wall bridging (above). This is a claim about the mechanism, and it rests on the replica.

### Stage 2 — configuration proof

Both cells were built from the S2 job's own patched tree. Binary md5s: `MeshPreprocessingHeadless` `05d8d624f3c2bc588b1f8f8e2d209277` (1621216 B) and `EdgeLineExtractionHeadless` `cbf747dc3172fe0bbd188822df14092a` (`binaries-S2.md5`). `mesh_processing_headless.cpp`, `CMakeLists.txt` and `stage55/` are identical between `f1e876d` (t61) and `ca520fe` (`git diff --quiet`).

- **Setting line, 9 of 9 pieces in both cells:** `[NORMAL-24-SWITCH] mode=radius radiusMMraw=1.0 radiusMM=1.000000 ... minK=5 maxK=20`.
- **Growth call, J1:** `[NORMAL-24] piece=Juglet_Piece_1 call=1 mode=radius n=19312 radiusMM=1.00000 radiusFrom=fixed ... minK=5 maxK=20 nbrMin=5 nbrMedian=13 nbrP90=16 nbrMax=20 nbrMean=12.89752 flooredToMinK=0 cappedAtMaxK=29 orientK=13 cloudSpacingMM=0.27137`.
- **Growth call, all nine:** median neighbours 13–14, orientK 13–14.
- **The clamp hardly fired.** The upper limit cut 15–51 points per piece to 20 neighbours (J1 29, J2 28, J3 37, J4 15, J5 24, J6 23, J7 36, J8 51, J9 17), which is 0.15–1.5 % of points. The lower limit fired on one point on one piece (J7, `flooredToMinK=1`).
- **The mode ran in both normal calls**, the downsampling call 0 and the growth call 1, exactly as the mode ships. Call 1 is the one scored below.
- **The stop fired only in FA.** `[BREAK-59] piece=` appears on 9 of 9 pieces in FA and on 0 in F.
- **Outputs:** outF and outFA each hold 36 geometry files (9 × S0/S1/Bl0/Bl1), 9 piece directories and 18 normals PLYs.

### The field the stop consumes (call 1 against the mesh, F against t61 U)

Method: ticket 60's, unchanged (`work/measure62.py`, derived from t61's `measure61.py` by `work/make_measure62.py`). `fields.tsv`. Flip is the majority-sign rate.

| piece | flip U | flip F | folded median U | folded median F |
|---|---|---|---|---|
| J1 | 41.63 % | **0.20 %** | 3.93° | 3.53° |
| J2 | 1.59 % | 1.49 % | 5.82° | 7.20° |
| J3 | 1.34 % | 1.23 % | 4.02° | 4.75° |
| J4 | 1.70 % | 1.41 % | 4.75° | 5.30° |
| J5 | 0.55 % | 0.41 % | 3.54° | 3.93° |
| J6 | 0.18 % | 0.11 % | 3.65° | 4.21° |
| J7 | 0.26 % | 0.22 % | 3.92° | 4.31° |
| J8 | 1.30 % | 0.89 % | 4.34° | 4.87° |
| J9 | 0.68 % | 0.47 % | 5.24° | 6.14° |

- FA's field is byte-for-byte the same measurement as F's on all nine, as expected: the stop does not touch the normals.
- The flip rate falls on every piece.
- The cost is the folded median, which rises **0.4–1.4°** on J2–J9. A plane fitted over about 13 neighbours is noisier than one over 19. It stays under 5° except on J2 (7.20°), J4 (5.30°) and J9 (6.14°).
- J1's folded median falls, from 3.93° to 3.53°.
- J1's flip draw changed: t55 and U print `Normals flipped: true`, while F and FA print `false`. Theta is the same as t61 on all nine (`s0_vs_t61.tsv`).

### Separation, F against t55

`sep_all.tsv`, from `check_separation.py --geom outF/geom --mesh-dir Dataset/Mesh/Juglet --walls <t54>/out/wall40 --pieces Juglet_Piece_1,...,Juglet_Piece_9 --k 15`. The t55 columns are t55's own `baseline_t55.tsv`; t61 U has the same `nS0` on all nine.

| piece | nS0 t55 | nS0 F (Δ) | blindDeg t55 → F | farS0 t55 → F | dc_ge1 t55 → F | bl0 t55 → F | genuine F |
|---|---|---|---|---|---|---|---|
| J1 | 13850 | 13027 (−5.9 %) | 85.49 → 68.38 | 0.8624 → 0.6729 | 0.1205 → 0.043 | 28 → 59 | True |
| J2 | 1390 | 1410 (+1.4 %) | 18.14 → 18.64 | 0.8182 → 0.8824 | 0.0129 → 0.0029 | 32 → 32 | True |
| J3 | 2063 | 2212 (+7.2 %) | 22.06 → 14.57 | 0.7714 → 0.6923 | 0.0027 → 0.0262 | 38 → 44 | True |
| J4 | 2033 | 1860 (−8.5 %) | 11.03 → 11.6 | 0.7059 → 0.7941 | 0.0245 → 0.0011 | 32 → 31 | True |
| J5 | 4066 | 3834 (−5.7 %) | 7.7 → 7.57 | 0.7544 → 0.7447 | 0.0163 → 0.0 | 47 → 43 | True |
| J6 | 3870 | 3804 (−1.7 %) | 11.94 → 9.9 | 0.8824 → 0.8333 | 0.1388 → 0.0013 | 46 → 45 | True |
| J7 | 5703 | 5648 (−1.0 %) | 5.92 → 5.51 | 0.8039 → 0.7059 | 0.0502 → 0.0365 | 54 → 54 | True |
| J8 | 2770 | 2833 (+2.3 %) | 11.93 → 7.96 | 0.6512 → 0.7429 | 0.0556 → 0.0312 | 41 → 40 | True |
| J9 | 1051 | 1040 (−1.0 %) | 12.32 → 13.1 | 0.7 → 0.8065 | 0.0777 → 0.0691 | 23 → 22 | True |

Genuine pairs hold on 9 of 9. farS0 improves on J1, J3, J5, J6 and J7, and worsens on J2, J4, J8 and J9.

### FA — the stop armed on the new field

From `sep_all.tsv` and `armed_counts.tsv`. The UA and IA columns are t61's.

| piece | nS0 UA / F / **FA** | genuine UA / **FA** | blindDeg UA / IA / **FA** | farS0 UA / IA / F / **FA** | wall_like UA / IA / **FA** (npts) |
|---|---|---|---|---|---|
| J1 | 351 / 13027 / **13271** | False / **True** | 22.6 / 40.92 / **132.51** | 0.1429 / 0.5926 / 0.6729 / **0.7731** | 1674 / 18074 / **18194** (19312) |
| J2 | 1377 / 1410 / **1404** | True / **True** | 18.14 / 23.06 / **18.52** | 0.8182 / 0.7667 / 0.8824 / **0.8824** | 1647 / 1663 / **1686** (1883) |
| J3 | 2055 / 2212 / **2088** | True / **True** | 20.17 / 15.88 / **14.56** | 0.8 / 0.8636 / 0.6923 / **0.7879** | 2475 / 2485 / **2533** (2841) |
| J4 | 1921 / 1860 / **1850** | True / **True** | 10.7 / 10.33 / **11.6** | 0.7576 / 0.7812 / 0.7941 / **0.8485** | 2407 / 2381 / **2449** (2768) |
| J5 | 3980 / 3834 / **3821** | True / **True** | 12.35 / 5.22 / **7.57** | 0.7321 / 0.9388 / 0.7447 / **0.8085** | 5121 / 5149 / **5183** (5671) |
| J6 | 3870 / 3804 / **3794** | True / **True** | 12.04 / 9.23 / **9.9** | 0.82 / 0.7674 / 0.8333 / **0.8333** | 3921 / 3896 / **3971** (4373) |
| J7 | 5491 / 5648 / **5439** | True / **True** | 7.19 / 5.67 / **5.48** | 0.8776 / 0.8462 / 0.7059 / **0.66** | 6926 / 6956 / **6962** (7633) |
| J8 | 2577 / 2833 / **2755** | True / **True** | 11.74 / 10.49 / **8.3** | 0.75 / 0.6579 / 0.7429 / **0.75** | 3136 / 3117 / **3168** (3464) |
| J9 | 1050 / 1040 / **1039** | True / **True** | 12.32 / 9.35 / **13.1** | 0.7 / 0.7692 / 0.8065 / **0.8065** | 1231 / 1235 / **1271** (1475) |

**The armed stop no longer collapses J1, and it still does not stop at the break edge.**
- J1 keeps 13271 points and its genuine pair. In ticket 59's armed run it kept 351 and lost the pair.
- The test now calls 18194 of 19312 points wall-like (94.2 %), close to IA's 18074 (93.6 %).
- But nothing is trimmed. FA's S0 is 244 points *larger* than F's, blindDeg rises from 68.38 to 132.51, and farS0 rises from 0.6729 to **0.7731**, worse than IA's 0.5926.
- On J2–J9 the armed wall-like count moves by at most 64 points against UA, and FA's nS0 is within 5.6 % of F's (J3 −5.6 %, J7 −3.7 %, J8 −2.8 %, the rest under 1 %).

### Gates

1. **The intended neighbour scale took effect on every piece: PASS.** The setting line and the call-1 `mode=radius radiusMM=1.00000` line are present on 9 of 9 pieces in both cells (quoted above).
2. **The other eight do not move: PASS on both tests.**
   - Flip within 2 percentage points: every J2–J9 rate falls, by 0.04–0.41 points.
   - `nS0` within 10 % of t55: worst is J4 at −8.5 %, next J3 at +7.2 %.
3. **Not adopted on J1 alone: PASS for the field.** The flip rate falls on all nine and genuine pairs hold on 9 of 9. **It does not pass for the stop**, which is no better localised on any piece (FA farS0 above).
4. **The outcome bar.** J1 flip ≤ 5 %: **PASS** at 0.20 %. Folded median ≤ 5°: **PASS** at 3.53°. Eight do not regress: **PASS** (gate 2). The armed stop behaves better than in ticket 59: **partial**. It no longer collapses J1, but it does not stop at the break.
5. **No default changed: PASS.** Radius mode is opt-in (`SFS_NORMAL_MODE` unset = `count`). With it unset the code takes the k=19 CGAL path byte-for-byte, as t61's U cell reproduced t55 on 8 of 9 S0 files.

### Not measured

- **Why the orientation pass flips one whole sheet past the threshold** (k > 12, or radius > 1.0 mm): the mechanism inside `CGAL::mst_orient_normals`. The threshold itself rests on the replica, not on CGAL. In the pipeline only the 1.0 mm point was run.
- **The distance from S0 points to the true break edge.** `farS0` is the fold far-skin share, not that distance.
- **Any effect outside the Juglet.** No Pot A–J piece was run.
- **Run-to-run spread of `nS0` at this setting.** One run per cell. J1's flip draw is known not to be deterministic.
- **Pictures.** No surface or field render was made in this ticket, only the Stage 1 figure. The J1 surface (F beside FA) and the sign colouring should be rendered before this is read as a seating result.

### Verdict

- **J1:** radius 1.0 mm **fixes the field** (41.63 % → 0.20 %, measured) and keeps the genuine pair. It does **not** make the stop work: armed, the surface still reaches the break (farS0 0.7731).
- **J2–J9:** the field gets slightly cleaner (flip down 0.04–0.41 points) at a folded cost of 0.4–1.4°. `nS0` stays within 10 % and genuine pairs hold on every piece. The armed stop changes `nS0` by at most 5.6 % against F.

**Overall:** the setting is a measured fix for the normal field, and it is not a fix for the stop rule. This is a claim about the method on both counts: the field step works at 1.0 mm, and the stop rule does not localise the break even with a sound field. That repeats ticket 61's finding with a second, independently produced field.

**The two candidate field fixes, side by side** (both measured, both opt-in):
- **Radius 1.0 mm, this ticket.** J1 flip 0.20 %. Costs: folded median +0.4–1.4° on J2–J9; farS0 worse on four of the eight others (J2 0.818 → 0.882, J4 0.706 → 0.794, J8 0.651 → 0.743, J9 0.700 → 0.807); `nS0` within 10 % on all eight.
- **Carrying the input normals, ticket 61 cell I** (`SFS_NORMAL_SOURCE=input SFS_NORMAL_CARRY=nearest`). J1 flip 0.145 %, folded medians *lower* (2.45–3.71° on all nine). Costs: farS0 worse on **seven** of the eight others (J2 0.818 → 0.867, J3 0.771 → 0.844, J4 0.706 → 0.800, J5 0.754 → 0.939, J7 0.804 → 0.942, J8 0.651 → 0.783, J9 0.700 → 0.920; only J6 improves). Ticket 61's lead note lists four of these; the table has seven. `nS0` moves more than 10 % on five of the eight (J2 −10.9 %, J5 +31.5 %, J7 +29.3 %, J8 +23.8 %, J9 +36.0 %), so by this ticket's gate 2 the carry would count as a regression.

No recommendation is made here. Whether to adopt either fix, or to park the field and the stop rule, is the conservator's decision.

## Lead verification (2026-11-03)

Every headline number was re-read from the run's own tables, not from the worker's report
(`fields.tsv`, `sep_all.tsv`, `armed_counts.tsv` at
`/data/gpfs/projects/punim2657/SfSpp/runs/20261103-0035_ca520fe_t62-normalfix-s2`):

- verified: fields.tsv F rows -> J1 flip 0.002019 (0.20 %), folded 3.532 deg; J2-J9 flip 0.0011-0.0149,
  folded 3.932-7.205 — the ticket's field table is a faithful copy.
- verified: sep_all.tsv F rows -> J1 nS0 13027, blindDeg 68.38, farS0 0.6729, dc_ge1 0.043, bl0 59,
  genuine True; J4 the worst nS0 move at 1860 (-8.5 %); genuine True on 9 of 9.
- verified: sep_all.tsv FA rows -> J1 nS0 13271, genuine True, blindDeg 132.51, farS0 0.7731;
  J2-J9 nS0 within 5.6 % of F (J3 2088 vs 2212).
- verified: md5 of out/stage1_bridging.png = f6ab510257612c96a8dc62d94a21018f; the figure (inspected
  after download to artifacts/62/) shows all three curves flat at 1e-3..1e-2 and left of each piece's
  wall line — matching the refutation text.
- verified: index.tsv rows 371-374 verdicts filled by the lead (371 void — the rejected submission).

Two points the Results leave implicit, for whoever reads this ticket later:

1. **The 1.0 mm setting has no safety margin.** The threshold curve is replica-only, and it says the
   sheet re-flips between 1.0 and 1.4 mm (and between k=12 and k=19). The pipeline itself was run at
   one point only. Adopting radius 1.0 mm is adopting a calibration sitting just under an unexplained
   cliff, not a "smaller neighbourhoods are safer" rule — the cause inside the orientation pass is
   still unmeasured.
2. **The gate evidence for "no default changed" is inherited, not fresh.** It rests on t61's U cell
   reproducing t55 (8 of 9 S0 md5 equal, J8 differing by the known flip-draw nondeterminism), plus
   the unset path being untouched in this ticket's diff (no tracked source changed at all). Same
   evidence class as ticket 61; acceptable, but it is one run, not a proof of byte-identity.

Verdict: the field fix is measured on the pipeline itself and the gates hold as stated. The stop rule
fails its positive bar a second time, on an independently produced field — with a sound field the
armed test accepts 94.2 % of J1's points as wall-like and trims nothing. No tracked source changed;
nothing to merge but this ticket. Adopt-or-park is the conservator's.

