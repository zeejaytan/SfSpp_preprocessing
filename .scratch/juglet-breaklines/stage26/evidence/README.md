# Ticket 26 evidence — the 3 mm admission window, measured

Source run: `/data/gpfs/projects/punim2657/SfSpp/runs/20261027-1313_583c952_win26-grid116`
job `33855784` COMPLETED 0:0, 00:04:16, commit `583c952a1e5641a6d97aab3ef8f7309ff2b6aa7f`
(pre-change binary built from `34d2867615e7ba7d1f8ceac29d38d11cd6595ce4`).

These files are copies of that run's own outputs. The run directory is the record; this
directory is for reading without the cluster.

| file | what it is |
|---|---|
| `cells26.tsv` | one row per cell (116), 46 columns: role/tag/scheme/pot/piece/paper/envs, the mesh exit code and elapsed time, the number of `[WINDOW-26]` lines, the admitted width per surface, the measured residual and other-distance, the rule that fired and its reason, the clamped-from value, the admitted own/other counts, the final surface sizes, the cluster counts and sizes, the outcome and the full `[STATUS-23]` line |
| `window26_all.tsv` | every `[WINDOW-26*]` line from all 116 cells, prefixed with tag/pot/piece (523 lines) |
| `measure26.tsv` | the corrected ruler, one row per cell that wrote two surfaces (76): n0/n1, median nearest-neighbour, median/p90/max of the component ALONG the Surface_0 normal, the same ACROSS it, and the coincidence share at 1 micron |
| `defaults_proof26_Juglet.tsv`, `defaults_proof26_Pot_A.tsv` | the default run against the pre-change binary (`A_old`) and against a second run of the same new binary (`A2`): point counts, md5 equality, nearest-neighbour displacement in both directions |
| `GEOMETRY_DELETED.txt` | per-cell deleted geometry by extension, with counts and bytes, plus the survivor census |
| `inputs_before.md5` | the 51 staged inputs (cloud, mesh, axis per piece) with md5 and point count |

Two caveats that the tables make visible and that a reader must not smooth over:

1. `md5_equal=no` everywhere even where the geometry is identical: the exported PLY's last
   column (`curvature`) is uninitialised, so its values vary run to run (measured values
   include `-3.63e-36` and `-4.02e+33`). Sorting x, y, z, nx, ny, nz gives a zero-line diff
   between the new default and the pre-change binary on Juglet piece 1, surface 0.
2. On Pot A the exported surface is not reproducible run to run: two runs of the SAME new
   binary differ by up to 0.58 mm and by 1-6 points out of 40k-67k, because
   `checkNormalsIntersection` draws 30 points from an unseeded `std::random_device`
   (`mesh_processing_headless.cpp:1940-1950` in `34d2867`) and the drawn indices differ in
   every run (the line `Sampled indices: ...` is in each cell's `logs/mesh.log`). The
   old-vs-new difference there (up to 0.71 mm) is the same size as that control.
   On the four Juglet pieces both directions are 0.000000 mm with identical counts.

Runs that are not evidence about the window but are on the record:

* `20261027-1303_583c952_win26-grid` job `33855418` COMPLETED 0:0, 00:02:27 — ran 0 cells:
  `STAGER` was not exported to the per-cell script. See that run's `out/RUN-FAILED.txt`.
* `20261027-1309_583c952_win26-smoke` job `33855584` COMPLETED 0:0, 00:01:51 — 4 cells,
  used to prove the instruments end to end before the grid.
