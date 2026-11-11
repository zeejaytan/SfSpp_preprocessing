# Ticket 331 — juglet_large: build the vessel at 3x and run the whole chain

**Status:** ready-for-agent
**Working in:** unassigned
**Branch:** none yet (the start script makes it)
**Answers:** S1
**Depends on:** 328 (merged to main 2026-11-12, commit `3ec34bd` — the wall side is cured, all nine joins face the same way)
**Blocks:** 332 (the assembly run on this input; not written yet)
**Worker:** unassigned
**Budget:** large (8 failed acceptance runs; waiting on Slurm costs none)

> **In one line.** The conservator's proposal (2026-11-11): the Juglet fails because its break edges are
> physically shorter than the matcher's window, so enlarge the source mesh 3x, call the new input
> `juglet_large`, and run the whole sampling / meshing / edgeline chain on it. This ticket builds that
> input and runs the chain. It does **not** run the assembler; 332 does, on these outputs.

## Why this is the right shape of test (read before starting)

The matcher recognises a join by walking along two edgelines and requiring a stretch of at least 7 dots
(`structure-from-sherds-pp class/feature_matching.cpp:294`, the LCS run-length floor). Dot spacing is a
fixed 1.9 mm (`edgeline_extraction_headless.cpp:574`, `RESAMPLE_D_MM`), so that window is about 12.6 mm of
real edge. On the curred Juglet four of the nine touching pairs never produce a candidate at all because
the matched run is 1-4 dots (ticket 329 bar 2, job 34725192: 1-2, 2-5, 2-9, 7-9), and the authors' own rule
excludes pieces under 50 points — nine-tenths of a 9 cm perimeter
(`papers/text/sfspp-2502.13986v1.md:329`). The vessel's 59/32/44/31/43/45/54/40/22 dots are below that.

Enlarging the mesh 3x raises the dot count ~3x while the spacing stays 1.9 mm, so the 7-dot window becomes
4.2 mm **of the original vessel** — the quantity that is currently binding.

It also makes every millimetre and area gate 3x stricter relative to the vessel (1.5 mm agreement becomes
0.5 mm at the original scale; 50 mm2 overlap becomes 5.6 mm2; 20 mm merge becomes 6.7 mm). That is the cost
side of the trade and it is why part C measures the matched stretch, not the seat count, before anything
is submitted to the queue.

## What is already known — numbers to reproduce, not re-derive

- Source meshes: `/data/gpfs/projects/punim2657/Dataset/Juglet/Piece01.obj` .. `Piece09.obj` (the nine
  real sherds; this is the "source obj file" the conservator means). Never write into that directory.
- Answer key: `Dataset/Juglet_GT/` holds `Juglet_Piece_<i>_T.txt` (9 rigid transforms into the assembled
  vessel frame) and `Juglet_Piece_<i>_Axis.xyz` (point + direction; **the last 6 numbers of the file are
  point xyz then direction xyz**), plus `Juglet_simple_graph.txt` (the touching pairs) and
  `README-axes.md`.
- Today's dot counts, pieces 1..9: **59, 32, 44, 31, 43, 45, 54, 40, 22** (ticket 68 Part C, job 34268623,
  run `runs/20261103-1546_6761aed_t68-densify2x`). Expect ~3x these at 3x scale.
- The chain's shipped defaults are still the sparse ones: `sphereRadius 1.8`
  (`edgeline_extraction_headless.cpp:485`) and `RESAMPLE_D_MM 1.9` (:574). Ticket 69's densification
  switches (`SFS_SPHERE_RADIUS_MM`, `SFS_RESAMPLE_D_MM`) exist and are **default off**; leave them off.
  This ticket tests size, not density; if the switches are also turned on the two effects are confounded
  and the result answers neither question.
- The wall side is cured (328): the interior face is filed by measured curvature, and the exported line's
  normals are re-derived against the wall it sits on. All nine touching pairs face the same way
  (dot_med_d3 +0.786..+0.997). Use main, not a branch.

## Part A — build the input (no queue time)

1. Create `/data/gpfs/projects/punim2657/Dataset/Juglet_large/` and write, **derived, never edited from
   the original**: `Piece01.obj` .. `Piece09.obj` with every vertex coordinate multiplied by **3.0**
   about the vessel's own origin, faces and vertex count unchanged. Record the md5 of each source obj and
   of each written obj in `scale_census.tsv`.
2. Write the scaled answer key in the same directory: `Juglet_Piece_<i>_T.txt` with the translation column
   multiplied by 3.0 and the rotation block unchanged (this is the only correct scaling of a rigid
   transform; verify by checking that the scaled transform maps the scaled piece onto the scaled vessel
   with the same residual as the original), and `Juglet_Piece_<i>_Axis.xyz` with the point multiplied by
   3.0 and the direction **unchanged**. Copy `Juglet_simple_graph.txt` unchanged.
3. Prove the scale is uniform and no axis was left unscaled: report, per piece, the bounding-box diagonal
   ratio written/source (must be 3.000 +/- 0.001) and the axis point / axis direction norms before and
   after.

## Part B — run the chain (queue time, small)

Run the standard preprocessing chain on `Juglet_large` — sampling, mesh, edgeline extraction and axes —
with the shipped defaults, in a run directory `runs/<YYYYMMDD-HHMM>_<git7>_t331-large`. Use the same
entry point and container the current main branch uses for the Juglet lane (read `hpc/` for the submit
scripts; do not invent a second path).

Report:
- **Dot counts per piece**, against today's 59/32/44/31/43/45/54/40/22. Acceptance: every piece above 50
  and the nine counts within 2.7-3.3x of the originals.
- **Axis sanity at 3x**: each piece's axis direction against the GT axis direction — the angles must match
  today's within 1 degree (scaling is a similarity; a change means the axis stage is size-dependent and
  that is a finding in its own right).
- **The matched stretch per touching pair, measured geometrically under the GT transform** (this is the
  number this ticket exists for): for each of the nine touching pairs, take the two breaklines, apply the
  GT transforms so both sit in the vessel frame, and measure the longest contiguous stretch where the two
  lines are within **1.5 mm** of each other. Report it in **mm and in dots**. Report the same two numbers
  for the unscaled Juglet, recomputed the same way, as the control.
  Acceptance: **at least 7 of 9 pairs reach a 12.6 mm matched stretch** (>= 7 dots at 1.9 mm). If they do
  not, say so plainly — that falsifies the seam-length explanation before any assembly run is spent.

## Part C — stop and hand over

Do not submit an assembly run. Part B's numbers decide whether 332 is worth the queue. Record everything
in the ticket Comments and end with your end state.

## Must not

- Write into `Dataset/Juglet/`, `Dataset/Juglet_GT/` or any existing corpus directory. The new input is a
  new directory; the originals are read-only inputs.
- Change any constant in the code. No `SFS_SPHERE_RADIUS_MM`, no `SFS_RESAMPLE_D_MM`, no edits to
  `RESAMPLE_D_MM` or `sphereRadius`. The point is that only the object's size changes.
- Touch the ten pots, or re-run any pot lane.
- Commit or push. The lead verifies from artefacts and lands.

## Deliverables

- `scale_census.tsv`, the run directory with logs and `out/`, the dot-count table, the axis-angle table,
  and the matched-stretch table with its control — in the ticket Comments, with the exact paths.
