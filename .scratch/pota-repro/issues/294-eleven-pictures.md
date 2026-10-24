# 294 — Eleven pictures: our line and the authors' line, on the mesh and on the surface

Status: done (accepted: eleven figures, one mechanism, two symptoms)
Answers: E1
Working in: `C:/PR/worktrees/sfs/294` (branch `294-eleven-pictures`, HEAD `0f8a4a4`)
Created: 2026-10-25
Follows: 292 (the baseline), 293 (the two families this illustrates), 289 (the on-mesh overlay that worked)

## Why

Ticket 292 says eleven sound lanes are below bar. Ticket 293 is the measurement ticket. The conservator
asked for the pictures first, because the difference between "our line is displaced" and "we are tracing
a different edge" is visible in one glance and hard to read off a table.

## What to produce

For each of these eleven lanes, ONE PNG with two rows:

| row | content |
|---|---|
| top | the sherd MESH (shaded triangles) with our line and the authors' line laid on it |
| bottom | the extracted SURFACE point cloud with the same two lines |

Both rows: our line thick **green**, the authors' thick **black**, our/an author legend, three panels
each -- 3D view, a projection that resolves the failing stretch, and a zoom on that stretch. Title on
every figure naming pot, piece, lane, and the ticket-292 numbers (n, median, coverage both ways).

Lanes (nine pieces, both lanes of a piece only where both are below bar):

```
Pot_C_Piece_03  Bl1   11.281 mm  cov 17.99 / 50.00   2.23x length   known base-band partition (278/279)
Pot_D_Piece_22  Bl0    0.757 mm  cov 86.40 / 78.95   0.92x
Pot_D_Piece_27  Bl0    0.673 mm  cov 73.21 / 83.33   1.20x
Pot_D_Piece_27  Bl1    0.798 mm  cov 62.07 / 77.55   1.21x
Pot_E_Piece_16  Bl0    0.676 mm  cov 72.97 / 74.11   1.01x
Pot_H_Piece_02  Bl1    0.688 mm  cov 72.46 / 74.45   1.01x   (S) same face different contour (286)
Pot_H_Piece_10  Bl1    0.728 mm  cov 72.22 / 77.27   1.05x   (K) partition mismatch (286)
Pot_I_Piece_06  Bl1    0.883 mm  cov 70.22 / 70.95   1.01x
Pot_I_Piece_13  Bl1    0.734 mm  cov 82.61 / 85.62   1.02x
Pot_I_Piece_25  Bl0    6.910 mm  cov 0.00 / 0.00     0.84x   new, different contour
Pot_I_Piece_25  Bl1    6.951 mm  cov 0.00 / 0.00     1.13x   new, different contour
```

Write them to `C:/PR/SfSpp_preprocessing/artifacts/pota294/png/` as
`p294_<Pot>_<Piece>_Bl<k>.png` (2300 px wide or wider; the conservator reads these at full size).

## How

1. Reuse the renderer already in the repo: `C:/PR/SfSpp_preprocessing/artifacts/pota289/data/onmesh.py`
   (matplotlib `Poly3DCollection` with `LightSource` shading, dots lifted 0.45 mm along the nearest
   face normal). Generalise it; do not invent a second style. If a mesh is heavy for plotting,
   decimate FACES for display only and say so in the figure footer -- never for any measurement.
2. The lines and the surfaces must come from a real run of the shipped code on these nine pieces:
   stage with `scripts/stage_piece.sh` (symlink, never derive a cloud), mesh stage at theta 3.4 with
   `SFS_AXIS_FILE` set and the `[PAPER-234] classify` line quoted into the run's log, then the edge
   stage with no `SFS_*` override. Build with `git archive` + cmake + sbatch; never
   `build.sh --target nurbs` (ticket 282).
3. **Score the fresh run and put it beside the 292 column.** Pictures must be of the run that is scored.
   The mesh stage is piece-dependently non-deterministic (`mesh_processing_headless.cpp:1526-1527`), so
   a lane may not reproduce 292 exactly; report the difference per lane and mark any figure whose
   numbers moved enough to change the reading.
4. Draw the author line the pipeline was scored against (the same file `score292.py` reads), not a
   re-derived one.

## Constraints

- No code change, no default, no threshold, no retune. This is a picture ticket.
- Run directory under `/data/gpfs/projects/punim2657/SfSpp/runs/<YYYYMMDD-HHMM>_<git7>_p294-pictures/`
  with `run.json`, and an index row (verdict and human_note left for the lead).
- Geometry dies with the ticket: delete stage trees and every `.pcd/.xyz/.obj/.ply` before reporting,
  write `out/GEOMETRY_DELETED.txt`, keep the PNGs, the tables and the scripts.
- Copy the PNGs to the laptop path above; the run directory keeps the same files.
- Write results into this ticket in the main clone and leave it uncommitted; the lead commits.

## Acceptance

1. Eleven PNGs at the stated path, each showing both lines on both the mesh and the surface, with the
   failing stretch resolved by one panel per row.
2. A table listing, per lane: the fresh-run numbers, the 292 numbers, and whether the figure's reading
   is affected.
3. The classify line and theta quoted per piece, and the binary/source md5s of both stages.
4. An index row and a run directory that a later reader can follow, with no geometry left behind.

## Results

### What was run

Run directory `/data/gpfs/projects/punim2657/SfSpp/runs/20261025-0340_0f8a4a4_p294-pictures`, commit
`0f8a4a417221647e7d6e7f7d031a90109930d44d` (branch `294-eleven-pictures`), Spartan local time (AEDT, UTC+11).

| job | name | state | elapsed | what |
|---|---|---|---|---|
| 33752717 | p294run | COMPLETED 0:0 | 6:05 | build both stages from `git archive`, nine pieces staged + meshed + edged, two lanes scored each |
| 33752744 | p294render | COMPLETED 0:0 | 0:30 | eleven figures, then geometry deleted |
| 33752858 | p294ref | COMPLETED 0:0 | 0:13 | distance from every authors' line to the authors' own DS mesh (added, see below) |

Index row appended: `20261025-0340_0f8a4a4_p294-pictures` / 33752717 / `0f8a4a41...` / `p294-pictures` / (verdict empty) / (human_note empty).

Built with `git archive` of the commit into a node-local tree inside the apptainer container
(`pcl_191_nurbs.sif`, 312,520,704 B, apptainer 1.3.3), `cmake -DCMAKE_BUILD_TYPE=Release
-DCMAKE_EXPORT_COMPILE_COMMANDS=ON`, `make -j8 EdgeLineExtractionHeadless MeshPreprocessingHeadless`;
0 `.cpp` newer than `CMakeLists.txt` (no local edits). Never `build.sh --target nurbs`.

| stage | source md5 (LF) | lines | binary md5 | stage output md5 |
|---|---|---|---|---|
| `edgeline_extraction_headless.cpp` | `f0dbfe7032d90a04412d15bd1699a703` | 3739 | `a28d10afab2b50bbe750d599ee2b7214` | edge stage md5 in `out/source.md5` |
| `mesh_processing_headless.cpp` | `459dabe145056489829804292710b382` | 2618 | `0171f471d0558d2676df7c4b113c1e9d` | same |

Both binaries are byte-identical to the ones that produced ticket 287's after column, ticket 288's re-run,
ticket 290's frozen-cloud run and ticket 292's corpus table, so nothing here rests on a build difference.

### The nine pieces: theta and the classification line

All nine staged with `scripts/stage_piece.sh` (mesh and cloud symlinked into the frozen corpus, only the
Axi file copied), meshed at theta `3.40000` with `SFS_AXIS_FILE` set, then edged with **no** `SFS_*` variable in
the environment (`[RUN] SFS_ variables in this environment: 0`). Every piece printed its classify line; none missing.

| piece | `[PAPER-234] classify:` line | verdict line |
|---|---|---|
| Pot_C_Piece_03 | `face0 n=23898 interior_frac=0.8151 face1 n=17455 interior_frac=0.0000 satA=36934.0000 satB=4419.0000` | kept |
| Pot_D_Piece_22 | `face0 n=5642 interior_frac=1.0000 face1 n=5027 interior_frac=0.0000 satA=10669.0000 satB=0.0000` | kept |
| Pot_D_Piece_27 | `face0 n=2500 interior_frac=0.0000 face1 n=2237 interior_frac=1.0000 satA=0.0000 satB=4737.0000` | swapped -> Surface_0=interior |
| Pot_E_Piece_16 | `face0 n=14989 interior_frac=0.0000 face1 n=11081 interior_frac=0.9996 satA=4.0000 satB=26066.0000` | swapped |
| Pot_H_Piece_02 | `face0 n=17678 interior_frac=0.9996 face1 n=14614 interior_frac=0.0000 satA=32285.0000 satB=7.0000` | kept |
| Pot_H_Piece_10 | `face0 n=4872 interior_frac=0.8436 face1 n=3718 interior_frac=0.0301 satA=7716.0000 satB=874.0000` | kept |
| Pot_I_Piece_06 | `face0 n=23564 interior_frac=0.0000 face1 n=19380 interior_frac=0.9955 satA=88.0000 satB=42856.0000` | swapped |
| Pot_I_Piece_13 | `face0 n=16463 interior_frac=0.0000 face1 n=14442 interior_frac=0.9897 satA=149.0000 satB=30756.0000` | swapped |
| Pot_I_Piece_25 | `face0 n=3072 interior_frac=0.0000 face1 n=2321 interior_frac=0.9931 satA=16.0000 satB=5377.0000` | swapped |

`[SPLITTER-234]` defaults on every piece: `smoothDeg=4.50000 curv=1.50000 joinDeg=60.00000 distMM=2.00000 window=100 paper=PAPER-CHAIN theta=3.40000 kappa=1.00000 nb=10`; `[PAPER-234] paper grow: thetaDeg=3.40000 kappa=1.00000 nb=10`.

### Fresh run beside ticket 292, per lane

Bar = median <= 2.0 mm and `cov_ours` >= 90. `flag` is the pre-set rule `|d median| > 0.20 mm` or `|d cov_ours| > 3.0 pp`.

| lane | fresh n | fresh med | fresh cov o/a | 292 n | 292 med | 292 cov o/a | d med | d cov | at bar | flag |
|---|---|---|---|---|---|---|---|---|---|---|
| Pot_C_03 Bl1 | 337 | 11.327 | 18.40 / 50.83 | 339 | 11.281 | 17.99 / 50.00 | +0.046 | +0.41 | no | no |
| Pot_D_22 Bl0 | 125 | 0.757 | 86.40 / 78.95 | 125 | 0.757 | 86.40 / 78.95 | 0.000 | 0.00 | no | no |
| Pot_D_27 Bl0 | 56 | 0.673 | 73.21 / 83.33 | 56 | 0.673 | 73.21 / 83.33 | 0.000 | 0.00 | no | no |
| Pot_D_27 Bl1 | 58 | 0.798 | 62.07 / 77.55 | 58 | 0.798 | 62.07 / 77.55 | 0.000 | 0.00 | no | no |
| Pot_E_16 Bl0 | 111 | 0.651 | 72.97 / 74.11 | 111 | 0.676 | 72.97 / 74.11 | -0.025 | 0.00 | no | no |
| Pot_H_02 Bl1 | 138 | 0.676 | 72.46 / 74.45 | 138 | 0.688 | 72.46 / 74.45 | -0.012 | 0.00 | no | no |
| Pot_H_10 Bl1 | 90 | 0.728 | 72.22 / 77.27 | 90 | 0.728 | 72.22 / 77.27 | 0.000 | 0.00 | no | no |
| Pot_I_06 Bl1 | 180 | 0.867 | 72.78 / 73.18 | 178 | 0.883 | 70.22 / 70.95 | -0.016 | +2.56 | no | no |
| Pot_I_13 Bl1 | 160 | 0.707 | 83.12 / 85.00 | 161 | 0.734 | 82.61 / 85.62 | -0.027 | +0.51 | no | no |
| Pot_I_25 Bl0 | 58 | 6.910 | 0.00 / 0.00 | 58 | 6.910 | 0.00 / 0.00 | 0.000 | 0.00 | no | no |
| Pot_I_25 Bl1 | 67 | 6.951 | 0.00 / 0.00 | 67 | 6.951 | 0.00 / 0.00 | 0.000 | 0.00 | no | no |

Six of the eleven reproduce 292 to three decimals; five moved by at most 0.046 mm and 2.56 pp. **No figure's reading is
flagged**: the largest move (Pot I 06 Bl1, `cov_ours` 70.22 -> 72.78) does not change anything one can see in the picture.
The other seven lanes of these nine pieces (all at bar) reproduced 292 with deltas of 0.000-0.028 mm and 0.00-0.68 pp.

### The eleven figures

Written to `C:/PR/SfSpp_preprocessing/artifacts/pota294/png/` and kept in the run directory at `out/png/`.
Every figure is 2300x1340 px, two rows (mesh / extracted surface) x three panels (3D, a projection chosen to
resolve the failing stretch, and a zoom on that stretch).

| PNG | bytes | md5 | zoom resolves (our dot indices) | arc / mean gap | plane | face drawn |
|---|---|---|---|---|---|---|
| p294_C_03_Bl1.png | 950144 | 01999cd61eeed57f488b7839f7eb06df | 105-336 of 337 | 418.3 mm / 21.86 mm | X-Y | Surface_1 |
| p294_D_22_Bl0.png | 817713 | 5bc05daa4e7c13fa4f52781c3e27b31c | 39-49 of 125 | 18.0 mm / 4.33 mm | Y-Z | Surface_0 |
| p294_D_27_Bl0.png | 584506 | 310f2613c3b58f45819694fc8e745e69 | 16-28 of 56 | 21.6 mm / 6.38 mm | Y-Z | Surface_0 |
| p294_D_27_Bl1.png | 592050 | 3c9d1dfe296720871bff5de4ccb64212 | 0-10 of 58 | 18.0 mm / 9.76 mm | Y-Z | Surface_1 |
| p294_E_16_Bl0.png | 1073060 | a80271cdccbeb4b58bb7ffa294493b27 | 58-87 of 111 | 52.2 mm / 7.91 mm | X-Z | Surface_0 |
| p294_H_02_Bl1.png | 983904 | 94b8c43542be7efb16f30191567015ed | 0-35 of 138 | 64.9 mm / 5.54 mm | X-Z | Surface_1 |
| p294_H_10_Bl1.png | 734251 | 4d33ed8ecde9b0312c40ffbbf3c333a7 | 67-89 of 90 | 39.6 mm / 4.42 mm | X-Z | Surface_1 |
| p294_I_06_Bl1.png | 1067171 | 8d4a65b09fcda084359ba92fa09fe83f | 84-103 of 180 | 34.2 mm / 3.48 mm | X-Y | Surface_1 |
| p294_I_13_Bl1.png | 910432 | c52b9c84c633c0a8fa52a3ea13feb9eb | 72-92 of 160 | 36.0 mm / 4.59 mm | X-Z | Surface_1 |
| p294_I_25_Bl0.png | 645381 | 5a170883aec801bde6b52741c2f10dd1 | 0-57 of 58 (whole line) | 104.8 mm / 6.96 mm | X-Y | Surface_0 |
| p294_I_25_Bl1.png | 647922 | ac913587224fbc11bbf6cbf9bbaa4b0c | 0-66 of 67 (whole line) | 120.6 mm / 6.99 mm | X-Y | Surface_1 |

### What each picture shows (read by eye)

**Same edge, locally displaced — seven lanes.** In each of these, green and black run together round most of the
loop and separate over one stretch; neither is a stub, both close, and ours stays on our own face.

- **Pot_D_27 Bl0** — together the whole way round the long sliver; ours bulges about 6 mm outward over 13 dots at one shoulder.
- **Pot_D_27 Bl1** — same loop; at the pointed end ours carries on along the tip for 11 dots where theirs cuts the corner (9.8 mm mean gap).
- **Pot_H_02 Bl1** — together except the upper right, where ours steps about 5 mm outside theirs (36 dots, 65 mm of edge).
- **Pot_H_10 Bl1** — together almost everywhere; ours dips 2-4 mm below theirs along the bottom (23 dots, 40 mm).
- **Pot_I_06 Bl1** — together except the bottom, where ours drops below theirs in a visible step (20 dots, 34 mm).
- **Pot_I_13 Bl1** — together along the lower silhouette; at the upper left ours takes a fuller lobe where theirs cuts across (21 dots, 36 mm).
- **Pot_E_16 Bl0** — together over the lower half of the flat sherd; along the top third theirs runs 7-8 mm inside ours (30 dots, 52 mm).

**A chord where we follow the edge — one lane.** **Pot_D_22 Bl0**: ours goes into and out of the notch at the mouth of the
U; theirs bridges it with an 18 mm straight chord (11 of 125 dots). The rest of the loop is coincident.

**Different edge, not a displaced one — three lanes.** These are the ones where the picture changes the reading.

- **Pot_C_03 Bl1** — ours runs round the **outer rim** of the sherd (607.3 mm of edge); theirs is a much smaller closed
  ring on the flat of the face (273.7 mm), drawn about 11 mm inside ours on average. Two different closed edges of the
  same piece, which is what ticket 292 recorded as the known base-band partition; both lie on this piece's own mesh.
- **Pot_I_25 Bl0 and Bl1** — ours is a small closed triangle (104.8 / 120.6 mm); theirs is a larger loop (124.3 / 106.3 mm)
  that crosses ours twice **in projection**. In 3D the two lines are 6.9 mm apart and do not come within 2 mm anywhere
  (`cov 0.00 / 0.00` both ways). Both ride the authors' own DS mesh (0.015 / 0.013 mm median). So this is a different
  choice of closed edge on the same partition, not a walk that wandered or a reference that left the part.

**Reading trap, recorded:** a crossing in one projection is not contact. On Pot I 25 the two lines visibly cross in X-Y
and are 6.9 mm apart in 3D; only the 3D distance (the scorer) settles it.

### The references lie on their own mesh — measured, job 33752858

After the figures were drawn, every authors' line used here was measured against the authors' **own** DS mesh triangles
(exact point-to-triangle distance, `scripts/mesh_ref.py`, `out/authors_to_mesh.json`). 18 of 18 rows:
median **0.007-0.024 mm**, p95 <= 0.115 mm, max **1.386 mm** (Pot_D_Piece_22 lane 0), and **0.00%** of dots beyond 2 mm
on every lane. Pot I 25's two lanes sit 0.015 / 0.013 mm from their mesh.

So no disagreement in this set can be blamed on a reference that left its surface — the same conclusion ticket 279
reached on 163 of 163 pieces. What these eleven lanes show is where two pipelines chose different edges, or the same edge
with a local offset.

### Geometry deleted

`out/GEOMETRY_DELETED.txt` — `counts: stage files=508 geom files=36`, `STAGE_DIRS_REMAINING=0 GEOM_FILES_REMAINING=0`.
Deleted: the nine stage trees (Pot_C_Piece_03 84M, Pot_D_Piece_22 46M, Pot_D_Piece_27 36M, Pot_E_Piece_16 68M,
Pot_H_Piece_02 70M, and the four smaller), `out/geom/*.xyz` (18 surfaces), `out/geom/*.pcd` (18 exports), and the
node-local build tree. Kept: `run.json`, `submit*.sbatch`, `scripts/`, `logs/`, `out/*.tsv`, `out/*.json`,
`out/png/` (the eleven PNGs) and `bin/` (the two binaries, 6.8 MB). The corpus was not touched.
Two files over 1 MiB outside `bin/` remain and are **the deliverable, not geometry**: the two PNGs of 1,073,060 and
1,067,171 bytes.

### Deviations

1. **A third job was added** (33752858) after the figures, to turn the Pot I 25 eye-reading into a number. Read-only on the
   corpus, writes no geometry, records one table in `out/`.
2. **`manifest294.py` was called from the run root** while it lives in `$RUN/scripts/`: job A's comparison step exited 2
   after the lanes were already scored. Re-ran it by hand with the right path (`lanes=11 problems=0 flagged=0`) and fixed
   the submitted copy. No number changed.
3. **The renderer was fixed twice before the run** (the plane label read the wrong tuple column; the plane choice now also
   scores how far apart the stretch and the reference are in that projection, not only the stretch's length) and was
   dry-run on a synthetic tree first, where it reported exactly the stretch that had been planted.
4. **The ticket header said `Working in: unassigned`** when the worktree already existed on branch `294-eleven-pictures`;
   the header was corrected here rather than by `ticket_start.sh`.

### Acceptance, item by item

1. **Eleven PNGs at the stated path** — PASS. `C:/PR/SfSpp_preprocessing/artifacts/pota294/png/`, 2300x1340 px each, md5
   and size in the table above; every figure carries both lines on both rows, and one panel per row is a zoom on the
   stretch named in the table.
2. **A table of fresh-run vs 292 per lane, with whether the reading is affected** — PASS, eleven rows above, `flag` column
   empty for all; the largest move is 0.046 mm and 2.56 pp.
3. **Classify line and theta per piece, and the md5s of both stages** — PASS, quoted in full above; both binaries match
   the shipped ones byte for byte.
4. **An index row and a followable run directory with no geometry left behind** — PASS: index row appended with verdict
   and human_note empty; `run.json`, the submitted scripts, the helper scripts, the logs and the tables are all in the
   directory; the only files over 1 MiB are the two PNG deliverable.

### What this does not establish

- It shows **where** the two lines differ, not why our walk chose the edge it did. No code, default or threshold was changed.
- One draw per piece (the mesh stage draws 30 unseeded ray-cast points, `mesh_processing_headless.cpp:1526-1527`); five of
  the eleven moved slightly and are recorded beside 292 rather than assumed equal.
- Pot C 03's and Pot I 25's "different edge" readings are stated as what the pictures show; classifying them as partition
  mismatch `(K)` or same-face-different-contour `(S)` is ticket 293's job, not this one's.


## Lead verdict (2026-10-25) -- accepted

**Accepted.** Eleven figures at `C:/PR/SfSpp_preprocessing/artifacts/pota294/png/`, 2300x1340 each,
md5s identical to the run's `out/png.md5`; the run directory keeps the same files plus `run.json`,
the tables, the logs and the scripts. Geometry is gone (508 stage files + 36 geometry files deleted,
`STAGE_DIRS_REMAINING=0 GEOM_FILES_REMAINING=0`); the only files over 1 MiB left are two of the eleven
PNGs, which are the deliverable.

1. **The pictures are of the run that was scored.** I re-read `out/lanes_fresh.tsv` on Spartan against
   the ticket-292 column myself: six of the eleven reproduce 292 to three decimals, five moved by
   <= 0.046 mm and <= 2.56 pp, and none crosses the pre-set flag (|d med| > 0.20 mm or |d cov| > 3.0 pp).
   The largest mover, `Pot_I_Piece_06` Bl1 (coverage 70.22 -> 72.78), reads the same either way.
   All nine classify lines present, theta 3.40000, binaries `a28d10af...` / `0171f471...` byte-identical
   to the 287-292 pair.
2. **One mechanism, two symptoms.** In every one of the eleven, our line is the boundary of the surface
   we kept and the reference is the boundary of the surface the authors kept -- ticket 279's rule, now
   visible instead of inferred. What differs is whether the two run on the same face.
3. **Symptom A, eight lanes: same partition, a different reading of one stretch.** Ours goes round the
   whole boundary of the face; theirs leaves it over 18-65 mm and comes back. `Pot_D_Piece_22` Bl0 is
   the clearest and it inverts the usual story: **the chord is theirs, not ours** -- they bridge the mouth
   of the notch with an 18 mm straight segment (mean gap 4.33 mm) while our line follows the material
   round the notch. On `Pot_H_Piece_10` Bl1 theirs steps 4.42 mm inside our face for 39.6 mm.
4. **Symptom B, three lanes: different partition.** `Pot_C_Piece_03` Bl1 -- ours runs the sherd's outer
   rim (607 mm of edge), theirs a closed ring on the flat of the face 274 mm round and about 11 mm
   inside; two different closed edges of one piece. `Pot_I_Piece_25` both lanes -- ours a small closed
   triangle (105 / 121 mm), theirs a larger loop (124 / 106 mm); 6.9 mm apart in 3D, within 2 mm nowhere.
5. **The reference measurement changes the reading of symptom A.** Every author line used here was
   measured against the authors' *own* DS mesh by exact point-to-triangle distance: 18 of 18 rows at
   median 0.007-0.024 mm, p95 <= 0.115 mm, max 1.386 mm (`Pot_D_Piece_22` lane 0), **0.00% beyond 2 mm**.
   So no disagreement in this set can be blamed on a reference that left its part -- the same conclusion
   ticket 279 reached on 163 pieces. The eight lanes are therefore a **convention difference about where
   the edge is taken**, not a tracing error; that explains the bar rather than retiring it.
6. **Reading trap, recorded because it nearly caught the worker too**: `Pot_I_Piece_25`'s two lines cross
   in the X-Y panel and are 6.9 mm apart in 3D. A crossing in one projection is not contact; only the 3D
   distance settles it.
7. **Weight**: eleven lanes, nine pieces, one draw each, one binary, one commit. The pictures establish
   **where** the two lines differ and that no reference in this set left its mesh. They do not explain
   **why** the walk chose that edge rather than the other closed edge of the same face -- that is ticket
   293, whose Phase A and B are now largely answered and should be narrowed to the "why" (see the
   amendment there). `Pot_C_Piece_03` and `Pot_I_Piece_25` also present the conservator with a reference
   question of the kind he ruled on for `Pot_J_Piece_09`; the ticket states the case and does not close it.

Deviations accepted: the third job (33752858) turned an eye-reading into a number and is evidence, not
scope creep; the manifest helper's path error was fixed after the lanes were scored and changed nothing;
the renderer's two pre-run fixes were dry-run on a synthetic tree first.
