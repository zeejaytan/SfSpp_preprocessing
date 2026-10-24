# 294 — Eleven pictures: our line and the authors' line, on the mesh and on the surface

Status: ready-for-agent
Answers: E1
Working in: unassigned (open with `scripts/ticket_start.sh SfSpp_preprocessing .scratch/pota-repro/issues/294-eleven-pictures.md`)
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
