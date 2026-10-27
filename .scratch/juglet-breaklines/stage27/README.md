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

## Reading the numbers

Nothing here is a verdict. Rung-2 and rung-5 sidecars are written **inside the 30-retry loop**, so a
piece that retried keeps only its last retry; the per-retry history is in that cell's
`logs/lines27.log` `[RETRY-23]` lines.
