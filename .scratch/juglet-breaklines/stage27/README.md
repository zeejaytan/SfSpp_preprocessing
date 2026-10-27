# Ticket 27 — the unclaimed fraction, and what de-duplication changes

Two questions, one run directory.

**Part A** measures, on today's defaults, how much of a sherd reaches a written surface: points
entering the segmentation, the region sizes region growing produced, how many points are in no
region at all, and — at rung 5 — how many points ended on each written surface and how many of
those are *distinct positions*. Ten pieces: Pot A 01/02/07/08 and Juglet 1/2/4/6/7/9 (the four
Juglet pieces that write a surface, plus the two that do not).

**Part B** adds `SFS_DEDUPE=off|on` to `finishImprovedSurface` (`mesh_processing_headless.cpp:1163`).
Unset it and the written surface is byte-for-byte what today's binary writes; `on` assigns back the
de-duplicated cloud the function already built and never used, and keeps the last sorted element
its loop used to drop. One line per call reports the step:

    [DEDUPE-27] surface=0 mode=on in=1845 out=1022

## Arms

| tag | binary | switches |
|-----|--------|----------|
| `OLD` | pre-change commit | none — the reference the defaults must reproduce |
| `A` | this commit | none — the defaults arm |
| `A2` | **the same binary file** as `A`, copied | none — run-to-run control in the same units |
| `P` | `A` | `SFS_DUMP_STAGE`, `SFS_DUMP_PIECES` — Part A's sidecars |
| `B` | `A` | `SFS_DEDUPE=on` |

`A2` is a byte copy, not a rebuild, so `A` vs `A2` isolates the program's own nondeterminism: 30
unseeded ray casts (`mesh_processing_headless.cpp:1940-1950`) make every arm a different draw, which
is why no cross-arm comparison in this ticket is reported without that spread beside it.

## Instruments (copied into the run directory, and run from there)

| file | what it does |
|------|--------------|
| `stage_piece_p27.sh` | stages one piece: cloud and mesh symlinked from the frozen corpus (Pot A) or the repo `Dataset` tree (Juglet), only the 7 KB axis copied, `inputs.md5` recorded |
| `run_cell27.sh` | one mesh cell: run, keep `surfaces/*.ply`+`*.xyz`, grep the `[..-2x]` lines, delete the stage with a per-extension file+byte count |
| `run_edge27.sh` | one edgeline cell: our own `EdgeLineExtractionHeadless` on the surfaces that cell kept, then count the dots it wrote |
| `dedupe27.py` | `surfaces` / `seteq` / `partA` / `dots` measurements over the cell tree |
| `measure_pairs26.py` | ticket 26's corrected ruler for the Pot A pair statistics, unchanged |
| `selftest27.sh` | laptop-side unit test of `dedupe27.py` on synthetic cells (absolute paths are the author's) |

## What the tables answer

* `surfaces27.tsv` — points written vs distinct positions per (arm, piece, surface). The last two
  columns make the chain exact **within one run**: with the switch unset the PLY count must equal
  that run's `[DEDUPE-27] in=`, and with it on the PLY count must equal `out=`. A mismatch there is
  an instrument failure, not a finding.
* `seteq27.tsv` — the distinct-position set of one arm against another: exact equality, how many
  positions are on one side only, and nearest-neighbour distance in mm. `A` vs `A2` (and `P` vs `A`)
  is the baseline in the same units; `B` vs `A` is the claim. Both arms are separate draws, so the
  honest reading is "equal, or differing by no more than the same-binary spread".
* `partA27.tsv` — Part A: `npts`, `clusters`, `points_in_no_cluster`, its fraction, and the rung-5
  per-surface vertices/distinct positions. Read from the sidecars, computed not estimated.
* `dots27.tsv` — our own `Breakline_0`/`Breakline_1` dot counts per (arm, piece).

Geometry (staged trees and edgeline stages) is deleted at the end of the job; the counted record is
`out/GEOMETRY_DELETED.txt`. Logs, sidecars, tables, surfaces and breaklines are kept.

## Job 4 (item 7), authorised after the report

The lead authorised **one more job on this branch** for item 6/7 alone — our own `Breakline_0` dots off
against on — after the report showed all 32 edgeline cells had died on a *staging* bug. Scope: the eight
pieces that write a surface (Pot A 01/02/07/08, Juglet 1/4/6/7), arms A (`SFS_DEDUPE` unset) and B
(`SFS_DEDUPE=on`), and nothing else.

The fix is the one line the report named, and it is now in the instruments rather than in a note:

* `run_cell27.sh` keeps **every** `<piece>_*` file the mesh stage left in `Temp/Data/<pot>/`, not just
  `Surface_{0,1}` and `_SampledWithNormals.ply`. `<piece>_unclustered.ply` is written at
  `mesh_processing_headless.cpp:4007`, and the edgeline stage loads it at
  `edgeline_extraction_headless.cpp:1273` and builds a KD-tree on it at `:1275`. The per-cell count and
  bytes of what was kept are in that cell's `logs/kept_inputs.txt`.
* `run_edge27.sh` stages all of them into `$ES/Temp/Data/$POT/` and appends one line to
  `kept_inputs.txt` saying whether the unclustered cloud arrived.

Each cell is a mesh stage **then** an edgeline stage on that cell's own surfaces, because the edgeline pass
consumes the surfaces, the unclustered cloud and `SampledWithNormals.ply` — there is nothing to run the
edgeline stage on otherwise. A gate cell (`A` / Pot A 08) runs first: if it writes no `Breakline` file the
job stops, records the command and the first 20 lines of its `edge.log` in `out/EDGE_GATE_FAIL.txt`, and
does not iterate.

`dotsets27.tsv` (`dedupe27.py dotsets`) is the table this job exists for: per piece and surface, dots off,
dots on, distinct positions each, position-set equality, and the nearest-neighbour distance between the two
sets in mm — the same ruler the surface comparison uses. Self-tested both ways: an identical pair reports
`equal=yes nn_med=0`, and the same cloud shifted by 1 µm reports `equal=no` with `nn_med=0.001000`.

## Reading the numbers

Nothing here is a verdict. Rung-2 and rung-5 sidecars are written **inside the 30-retry loop**, so a
piece that retried keeps only its last retry; the per-retry history is in that cell's
`logs/lines27.log` `[RETRY-23]` lines.

## What ran (job ledger, 2026-10-27)

| job | sacct | wall | what happened |
|---|---|---|---|
| 33860135 | FAILED 1:0 | 3 s | one `local` line expanded `$name` before assigning it, so `set -u` killed the build step |
| 33860394 | COMPLETED 0:0 | 3:13 | ran no cell: the 50 `xargs` children did not inherit `CELLRUN` |
| **33860966** | **COMPLETED 0:0** | **5:44** | **the run of record** — `20261027-1534_df523dd_p27-dedupe-grid`: 50 of 50 mesh cells `stage=0 mesh=0`, every measurement step rc=0 |

The edgeline pass **failed in all 32 cells, exit 139 (SIGSEGV)**, so `dots27.tsv` holds only
`(none-written)` rows and item 6 of the ticket was not obtained. The cause is in
`out/cells/A/Pot_A/Pot_A_Piece_01/logs/edge.log`: the edgeline stage also reads
`Temp/Data/<pot>/<piece>_unclustered.ply`, and `run_cell27.sh` kept only the surfaces before deleting the
staged tree — `[pcl::PLYReader] ..._unclustered.ply:1: parse error: couldn't read the magic string`,
`Cannot create a KDTree with an empty input cloud!`, then the segfault. Fix for a future job (one line):
keep `${PIECE}_unclustered.ply` into `<cell>/surfaces/` and copy it into `$ES/Temp/Data/$POT/` in
`run_edge27.sh`. The brief caps the grid at three jobs, so no fourth job was submitted.

The numbers this grid produced are in `evidence/` and are written up under "Worker result" in the ticket
file. Deletion of the kept geometry after the tables were computed is recorded in the run directory's
`out/GEOMETRY_DELETED_cells.txt` (manifest of 210 cell surfaces plus 50 rung dumps, with the two
non-geometry files the sweep caught and restored named in it).
