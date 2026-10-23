# 268 — Where does P03-Bl1's 4 mm come from: the wood, the walk, or the reference?

Answers: E1
Status: ready
Working in: C:/PR/SfSpp_preprocessing-248 (diagnostic scripts only; NO build, NO pipeline run, NO commits)
Needs-eye: no

## Why

Ticket 267 exonerated the walk on P03-Bl1. The rule-ON export is 333 dots, med 0.90 mm, cov 57.4%, zero jumps, loop closed over 1.80 mm — and the WHOLE remaining miss is one contiguous 255.6 mm run (exported idx 124-265, 142 dots) that rides a parallel line at mean 4.13 mm / max 5.67 mm from the author's lane, mirrored by a 266.4 mm author stretch (idx 157-304) at mean 4.18 mm. 149 of 343 author dots are >2 mm from our loop. No dot anywhere is farther than 5.67 mm, so the route agrees and the POSITION does not.

A 4 mm lateral offset has three completely different causes and three different fixes. Guessing costs a build and a run; measuring costs a script. That is this ticket.

## Goal

Classify the offset as exactly one of:

- **(A) EDGE-STAGE / upstream** — the extracted dot bag is itself ~4 mm inside the author's line over that stretch. Nothing the walk does can move it.
- **(B) WALK SELECTION** — the bag contains dots within ~1 mm of the author's line over that stretch and the walk took the far row instead.
- **(C) REFERENCE MISMATCH** — our reconstructed surface does not reach the author's line there, so the author traced something our geometry does not have.

Report A, B or C with the numbers that decide it, and say plainly if the evidence is mixed or if two causes are present in different sub-stretches.

## Instruments (all read-only; everything below already exists on disk)

Use the SAME inputs and paths the earlier workers used, and say which file each number came from:

- bag: `Temp/Temp_edge/Pot_D/boundaryImproved.pcd` in the rule-ON tree `pota267R_P03_FULL` (1121 dots = 1045 + 76). NOT `boundary.pcd` — that is a different cloud that replays to maxjump 1.499 mm / L = 660.803 and is a convincing wrong answer.
- export: the same tree's `Dataset/Breaklines/Pot_D/Pot_D_Piece_03_Breakline_1.pcd` (333 dots).
- author: `sfs_main/original_samples/SfS_pp/Breaklines/Pot_D_Piece_03_Breakline_1.pcd` (343 dots), the path used by C:/PR/SfSpp_preprocessing-248/pota266_score.py:43.
- extracted faces: the Surface_0 / Surface_1 PLYs that C:/PR/SfSpp_preprocessing-248/pota265_final.py used for P03 (its own header records the paths). Surface_1 is the exterior sheet held by both strands.
- helper code already written: pota267_profile.py (offset profile), pota266_score.py (lanescore), pota265_final.py (face membership). Reuse rather than rewrite.

1. **Bag to author, on the arc and off it.** For the bag dots in the arc's parameter range and for the whole bag: distance to nearest author dot — min / med / max, and the fraction under 1 mm and under 2 mm. If the bag's own median is ~4 mm there, that is (A) unless instrument 2 contradicts it.
2. **Author to bag, on the mirrored author stretch (idx 157-304).** For each author dot: distance to the nearest BAG dot (not to our export). Same statistics. If every author dot has bag company within ~1 mm, the bag straddles both lines and the walk chose the far one -> (B). If nothing in the bag is within 2 mm of the author's line, the bag does not reach it -> (A) or (C), decided by instrument 3.
3. **Surface to author.** Using the extracted surface points/triangles, is there surface within 1 mm of the author's line along that stretch? Report the minimum distance from the author's stretch to the surface, and the distance profile along it. Surface present -> the geometry is fine and the boundary extraction is the culprit (edge-stage, name the step). Surface stops ~4 mm short -> our reconstruction does not cover the author's line there ((C) or a mesh-side fault), and say which.
4. **Rows, not averages.** Along the arc, histogram the bag-to-author offsets into rows (cluster on distance, report each row's offset and dot count). Two rows ~4 mm apart with the walk on the outer one is (B) with a nameable selection fault; one row only is (A).
5. **Sign and direction.** Is the 4 mm a uniform inward/outward shift, a progressive drift, or a widening? Report the signed offset along the arc (use the surface normal at the nearest face point or the loop's own left/right sense, and say which you used).

## Boundary

- C:/PR/SfSpp_preprocessing-248 worktree: new untracked scripts only (`pota268_*.py`), plus whatever read-only inputs you need.
- No build. No pipeline run. No new Spartan job unless a query genuinely cannot run on the laptop (reading JSON/PCD and small Python is a laptop-only exception; anything heavier goes to a compute node, never the login node).
- Touch nothing in main; commit nothing anywhere.
- Do not re-litigate the walk, the stop rule, or the guided filter. Their verdicts stand.

## Constraints

- Quote the file path behind every number.
- If a needed artifact is missing from disk, say so and stop — do not regenerate it by re-running the pipeline. Missing evidence is a finding.
- Convert millimetres into plain geometry at least once: 4 mm on a seam of ~617 mm length, on a loop of roughly 100 mm radius.
- Keep the output small and tabular. No multi-hundred-line dumps.

## Acceptance criteria

1. A one-line verdict: (A), (B), (C), or an explicit mixed answer naming which sub-stretches fall where.
2. Instrument 1-5 tables, each citing its input file.
3. A named suspect step for the winning cause — for (A) the boundary/edge step in edgeline_extraction_headless.cpp, for (B) the chaining choice, for (C) what the surface is missing.
4. One PNG: top view, author black, our export coloured by local offset, bag dots in light grey, so the lead can see whether the grey reaches the black line without reading a number.
5. One line: what evidence would overturn your verdict.

## Required evidence to report

Ticket Comments with the verdict, the five tables, the PNG path, the suspect step, and what would overturn it. No accept/reject verdict — judgement is the lead's.

## Comments

### Worker run — ticket 268 (2026-10-23). Measurements only; no verdict (lead's call).

**Verdict, one line: (A) — the offset is already in the extracted dot bag.** It is present, unchanged, in the FIRST breakline artifact the edge stage writes (`_breakLineFromConcaveHull.pcd`, 341 dots, 139 of them on the mirrored stretch at median 4.12 mm), and no later link moves it; (B) is dead (no bag dot within 2 mm of the author's lane anywhere on the stretch) and (C) is dead (the extracted exterior sheet runs 0.23 mm median from the author's lane, 100% within 1 mm).

#### Inputs, exactly (read-only; copied from `$B/pota267R_P03_FULL` and `sfs_main`, md5 verified)

| role | file | dots | md5 |
|---|---|---|---|
| bag | artifacts/pota268/bag_boundaryImproved.pcd (= `Temp/Temp_edge/Pot_D/boundaryImproved.pcd`) | 1121 | b79c25b051fadba82e1772a50754584b |
| export | artifacts/pota268/export_P03_Bl1.pcd (= `Dataset/Breaklines/Pot_D/Pot_D_Piece_03_Breakline_1.pcd`) | 333 | ddaeb48e5daecceeeffc86baf1177f27 |
| author | artifacts/pota268/author_P03_Bl1.pcd (= `sfs_main/original_samples/SfS_pp/Breaklines/Pot_D_Piece_03_Breakline_1.pcd`, the path in pota266_score.py:43) | 343 | bbb490fc5b7b583445eb0809bc2b6c3c |
| exterior sheet | artifacts/pota268/Surface_1.xyz (= the `urface_1_Cleaned.xyz` that pota265_final.py:90-91 reads for P03; face count 0, it is a PCL cloud) | 111564 | e0e4bfb0fa682b9087190869c931f58f |
| interior sheet | artifacts/pota268/Surface_0.xyz | 107304 | 56d8fb75158caa1aa36306b320af8467 |
| retained cloud (boundary input) | artifacts/pota268/Pot_D_Piece_03_unclustered.ply | 9259 | 21f8f85c227a6942213f87c64904a3fe |

Replication gate first (pota268_measure.py): the off-line run is exported idx 124-265, 142 dots, arc 253.8 mm, mean 4.13 / max 5.67 mm; 149 of 343 author dots >2 mm by point-to-point and by point-to-segment; author closed 616.77 mm, our export 601.69 mm (-15.08 mm). Same numbers as ticket 267, so the loader is sound.

**Frame used for every signed number.** At the author's dot j: t = author tangent, n = normal of a local PCA over the 25 nearest `Surface_1.xyz` points (orthogonalised against t), s = t x n (in-sheet, cross-lane). Method note: an earlier cylinder frame around the loop's own PCA axis was discarded — this loop is not planar (its own dots span -49.4..+35.4 mm along that axis), so the axial/radial split it produced is not reported. The sign of s is certified by instrument 8 (below), not by a global handedness claim. Frame control: for our export dots OUTSIDE the arc, s = +0.09 mm mean, 98% within 1 mm — the frame is not biased.

#### Instrument 1 — bag to the author's lane (bag: bag_boundaryImproved.pcd, 1121; author: author_P03_Bl1.pcd, 343)

| bag subset | n | min | med | mean | max | <1 mm | <2 mm |
|---|---|---|---|---|---|---|---|
| whole bag | 1121 | 0.036 | 0.892 | 2.081 | 5.674 | 53.8% | 56.4% |
| in the arc's author range (nearest author idx 156-304) | 485 | **2.055** | **4.105** | 4.006 | 5.674 | **0.0%** | **0.0%** |
| — main strand (1045-dot component) | 409 | 2.508 | 4.336 | 4.221 | 5.674 | 0% | 0% |
| — 76-dot satellite | 76 | 2.055 | 2.901 | — | 3.317 | 0% | 0% |
| control, outside the arc | 636 | 0.036 | 0.598 | 0.612 | — | 94.8% | 99.4% |

The bag's own median over the arc is 4.1 mm while 94.8% of it is inside 1 mm elsewhere: the ~4 mm is a property of the bag, on that stretch only.

#### Instrument 2 — the author's stretch to the BAG (the discriminator; author idx 157-304, 148 dots)

| query set | n | min | med | mean | max | <1 mm | <2 mm |
|---|---|---|---|---|---|---|---|
| author stretch -> nearest bag dot | 148 | 1.394 | 4.140 | 4.014 | 5.403 | **0.0%** | **0.7%** |
| -> nearest main-strand dot | 148 | — | 4.680 | — | — | 0% | — |
| -> nearest satellite dot | 148 | — | 65.120 | — | — | 0% | — |
| control: author outside the stretch -> bag | 194 | — | 0.314 | — | 1.821 | 98.5% | — |

The single sub-2 mm value (1.394 mm) is author idx 304, the last dot of the stretch. Per-21-dot bin medians along the stretch: 3.01 / 2.92 / 4.15 / 5.00 / 5.02 / 4.59 / 3.29 (+1.39 at idx 304), and every bin has 0 of 21 dots under 1 mm. **No bag dot reaches the author's lane anywhere on the stretch, so there is no near row for the walk to have preferred: (B) is dead.**

#### Instrument 3 — the author's stretch to the extracted surface

| target | n | min | med | mean | p90 | max | <1 mm | <2 mm |
|---|---|---|---|---|---|---|---|---|
| `Surface_1.xyz` (exterior sheet) | 148 | 0.015 | **0.233** | 0.232 | 0.355 | 0.453 | **100%** | 100% |
| `Pot_D_Piece_03_unclustered.ply` (retained cloud) | 148 | 0.015 | 0.507 | 0.944 | 2.734 | 3.595 | 68.9% | 83.1% |
| `Surface_0.xyz` (interior sheet) | 148 | 24.789 | 25.776 | — | — | — | 0% | 0% |
| control: author outside the stretch -> unclustered | 195 | — | — | — | — | 0.628 | 100% | 100% |

The exterior sheet is *under* the author's line to a quarter of a millimetre; the material the boundary step was allowed to snap to is also there (max 3.6 mm, with the 3.6 mm being the rim itself). Our export arc dots sit 0.153 / 0.606 / 1.291 mm from `Surface_1`, and the bag dots on the arc 0.135 / 0.520 / 0.819 mm — everything is on the sheet, so the surface is not missing. **(C) is dead as defined.** Also confirmed: bag_boundaryImproved.pcd is an exact subset of the unclustered cloud (max distance 0.0000 mm), i.e. the K=1 snap described below.

#### Instrument 4 — rows, not averages (1 mm bins of s; export = export_P03_Bl1.pcd arc dots, bag = bag dots whose nearest author dot lies in 157-304)

| bin | our export (n=142) | bag on the stretch (n=482) |
|---|---|---|
| [-1, +1) | 0 | 0 |
| [+1, +2) | 0 | 0 |
| [+2, +3) | 31 | 135 |
| [+3, +4) | 49 | 144 |
| [+4, +5) | 53 | 183 |
| [+5, +6) | 9 | 20 |
| outside those | 0 | 0 |

Both distributions are single unimodal rows in [+2, +6); there is no companion row near 0 and nothing below +2 mm in the bag.

#### Instrument 5 — sign and shape along the arc (export_P03_Bl1.pcd, 21 export dots per station, s med / min / max / spread)

| export idx | author idx | med | min | max | spread |
|---|---|---|---|---|---|
| 124-144 | 156-178 | +2.83 | +0.00 | +3.45 | 3.45 |
| 145-165 | 179-200 | +3.07 | +2.49 | +3.79 | 1.30 |
| 166-186 | 201-222 | +3.86 | +3.36 | +4.68 | 1.32 |
| 187-207 | 223-244 | +4.87 | +4.39 | +5.15 | 0.75 |
| 208-228 | 245-266 | +4.84 | +4.43 | +5.31 | 0.88 |
| 229-249 | 267-288 | +4.25 | +3.43 | +4.77 | 1.35 |
| 250-265 | 289-304 | +2.91 | +2.19 | +3.42 | 1.23 |

One smooth lens-shaped bulge: peak ~+4.9 mm at author idx 222-266, tapering to ~+2.8-2.9 at both ends, spread inside a station 0.75-1.45 mm. Progressive, single-signed, no step, and no widening beyond a station. The 4.13 mm distance decomposes (5b, export dots 124-265) into 2% along-lane (mean -0.03 mm), 12% off-surface (mean -1.36 mm, i.e. slightly below the tangent plane) and 86% cross-lane (mean +3.81 mm, min 0.00, max +5.31) — a parallel in-sheet line, not a radial or a longitudinal error.

#### Extra instrument 6 — where in the chain the 4 mm first appears (tree `pota267R_P03_FULL`, `Temp/Temp_edge/Pot_D/`; md5 of the files read: `_breakLineFromConcaveHull.pcd` db3e8b07e6d82159e7daf378b0a1bedd, `CompleteBreakline.pcd` = `smoothed.pcd` 1804b3b5c71ff1b14aa749a147211d77, `cloud_Filtered.pcd` c80f85147b7755f22f7231d58c33d507, `cloudForSpline.pcd` 120d6ea8e3b6c6bfc33256dfb7f7623f)

| artifact | dots | distance to author (whole loop) med | >2 mm | on the stretch: n / med / max |
|---|---|---|---|---|
| `_breakLineFromConcaveHull.pcd` | 341 | 0.846 | 141 | 139 / **4.119** / 5.601 |
| `CompleteBreakline.pcd` | 333 | 0.904 | 142 | 141 / **4.320** / 5.671 |
| `smoothed.pcd` | 333 | 0.904 | 142 | 141 / 4.320 / 5.671 |
| `cloud_Filtered.pcd` | 1082 finite | 0.896 | — | — |
| `boundaryImproved.pcd` (bag) | 1121 | 0.892 | — | — |
| our export | 333 | 0.905 | 142 | 141 / 4.320 / 5.671 |

`_breakLineFromConcaveHull.pcd` IS `cloud_sequenced` (written at edgeline_extraction_headless.cpp:1604-1605, reloaded at :1607 as `cloud_BorderPointsCombined`) and it is already 4.12 mm off on the stretch; `CompleteBreakline.pcd` -> `smoothed.pcd` are identical to 0.0000 mm and the export to 0.0005 mm. Nothing between the first sequenced breakline and the export changes the position. Pure hygiene, not a new link: `cloud_Filtered.pcd` has 1121 rows of which 39 are `nan nan nan`, and its other 1082 rows are byte-identical, at the same line index, to the bag.

#### Extra instrument 8 — why the bag sits there: a crease, and our row is up the roll-over (8388 `unclustered.ply` samples within 6 mm of the stretch and |n| < 2.5 mm; tilt = angle between the local PCA normal and the sheet normal at the author's dot)

| s band (mm) | n | tilt |
|---|---|---|
| [-6,-3) | 10 | 55.4 deg |
| [-3,-2) | 25 | 34.3 deg |
| [-2,-1) | 482 | 13.3 deg |
| [-1, 0) | 2829 | 8.1 deg |
| [0, +1) | 1316 | **6.8 deg** |
| [+1, +2) | 121 | 17.8 deg |
| [+2, +3) | 672 | 33.8 deg |
| [+3, +4) | 1455 | 43.1 deg |
| [+4, +6) | 1478 | 45.2 deg |

The author's line sits exactly where the local face is flattest; inboard of it the sheet stays flat, outboard of it the material rolls over to ~45 deg within 4 mm — and the point counts show the mass of that roll-over is on the +s side (1455 + 1478 samples at +3..+6 mm vs 35 samples in total beyond -2 mm). That is what certifies the sign of s: +s = toward the rolled-over rim. An independent check (4c) shows the row we took is not even the outermost material: 88.4% of the bag dots on the stretch have further cloud material beyond them within 3 mm (median 10 such neighbours), so the boundary set samples the middle of the rim, not its silhouette.

#### Physical scale

The author's seam is a closed loop of 616.77 mm; its equivalent circle radius is 98.2 mm. The 4.13 mm offset is 0.67% of the seam but 4.2% of that radius, 2.4 deg of arc, and 2.3x the author's own 1.80 mm dot spacing — on a rim that rolls over 90 deg of surface orientation within ~5 mm, 4 mm is most of the way round the roll-over. The 15.08 mm closed-length deficit of our export is 2 x pi x 2.40 mm, the length change expected from a radial shift of that size on a wall inclined ~50 deg.

#### Named suspect step

The **boundary/edge step**: the PCL `BoundaryEstimation` boundary point set together with the `FACE_ALIGN_VETO` gate (normal . radial from `surfCentroid`), edgeline_extraction_headless.cpp:1380-1540, whose output is saved as `cloud_sequenced` -> `_breakLineFromConcaveHull.pcd`. It selected a curve on the rolled-over rim, ~4 mm to the +s side of the curvature break the author traced, and the K=1 snap to `Pot_D_Piece_03_unclustered.ply` (:1525-1535) then preserved that position unchanged in the bag. Not the walk (settled, and instrument 2 leaves it nothing to choose), not the stop rule, not the guided filter, not the surface (instrument 3).

#### Figure

C:/PR/SfSpp_preprocessing-248/pota268_P03_Bl1_offset.png — left: whole loop in the plane of the author's loop, author black, our export coloured by s (dark = on the lane, yellow = +5.5 mm), bag light grey; right: zoom on exported idx 124-265. The coloured export visibly parts from the black line over the arc while the grey bag dots stay with it, i.e. the grey never reaches the black line where the export leaves it.

#### What would overturn this

A pre-sequencing P03-Bl1 boundary cloud that already lay on the author's line would move the fault from the boundary set into the sequencing step — the tree retains no such file (`boundary.pcd` belongs to the per-surface pass and replays to a 660.803 mm loop, so it cannot answer this), and the settled walk verdict rules the sequencing step out; failing that, evidence that the author's lane is a deliberate inboard offset from the piece silhouette would move the 4 mm into the reference rather than our extraction.
## Lead verdict (R6, 2026-10-23)

Independently recomputed the discriminating numbers myself, in plain numpy, from the copies in C:/PR/SfSpp_preprocessing-248/artifacts/pota268 (script pota268_leadcheck.py, since deleted from the report path but reproducible in two minutes). Loaded counts: bag 1121, export 333, author 343, Surface_1.xyz 111564.

- author[157:305] -> nearest BAG dot: min 1.394, med 4.140, max 5.403, under 1 mm 0.0%, under 2 mm 0.7%.
- author[157:305] -> Surface_1: min 0.015, med 0.233, max 0.453, under 1 mm 100.0%.
- export -> author: med 0.905, cov 57.4%, 142 dots over 2 mm, MAX 5.671 mm, none over 6 mm.
- bag -> author (whole bag): med 0.892, mean 2.081, under 1 mm 53.8%.

Every figure matches the ticket to the digit, so the discriminator stands on my own arithmetic, not only on the worker's.

VERDICT (A) ACCEPTED — the offset is already in the extracted dot bag, and it is present unchanged in the first breakline artifact the edge stage writes.

- (B) is dead, quantitatively: over the whole mirrored stretch there is NO bag dot within 2 mm of the author's lane (min 1.394 mm; the single 0.7% value is the stretch's last dot at 1.394-2.0 mm). A single unimodal row of bag dots at +2..+6 mm with nothing at 0..+2 mm means the walk had no nearer row to prefer. This is not a selection fault and no ordering rule can recover it.
- (C) is dead: the exterior sheet runs 0.233 mm median from the author's lane, 100% within 1 mm. Our geometry does cover the line the author traced — it is our boundary set that declines to use it.
- The chain is closed from both ends: _breakLineFromConcaveHull.pcd (= cloud_sequenced, written at edgeline_extraction_headless.cpp:1604-1605 — verified present) already carries 4.119 mm median over the stretch, and CompleteBreakline / smoothed / our export agree to 0.0005 mm. So the defect is created at the boundary/edge step and nothing downstream moves it: PCL BoundaryEstimation (:1330) with FACE_ALIGN_VETO (:1365, tested :1387) and the K=1 snap at :1525-1535.

MECHANISM, which is the useful part: the author's line sits where the face is flattest (local tilt about 7 deg) and the roll-over runs outward from there to +6 mm (43-45 deg of tilt by +3..+4 mm). Our boundary sits at +4.1 mm, i.e. in the middle of the roll-over, and 88.4% of bag dots on the stretch have further material beyond them within 3 mm. So the point set we call the boundary is not the edge of the material at all — it is a curvature feature well inside the surface. A boundary detector that keys on local geometry (angular gaps, normal direction relative to the surface centroid) will do exactly that on a rounded rim, and this rim rolls 90 deg in about 5 mm.

WHY THIS MATTERS BEYOND P03: this is the first mechanism on the table that could explain the "parallel ridge" miss family (Pot H, four misses, all Bl1-side) and the P07/P12 coverage losses in Pot D — all of them lines that came out complete but a few millimetres off. That is a hypothesis, not a finding: it must be tested on those lanes before anything is claimed. But it points at the edge stage rather than the walk, which is where the last five tickets have all pointed.

Consequence: P03-Bl1 is retired from the walk family. The remaining 4 mm is an edge-stage boundary-POSITION fault, and the next ticket is about the boundary step — starting by reading what the paper's boundary rule actually is, since this is the second time our substitute has been caught standing in for the author's method.

Nothing committed by the worker; diagnostic scripts remain untracked in the 248 worktree, as briefed.
