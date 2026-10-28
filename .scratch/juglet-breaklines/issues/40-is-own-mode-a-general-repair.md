# 40: is own mode a general repair, or a two-piece coincidence?

**Status:** ready-for-agent
**Branch:**
**Answers:** U19
**Blocked by:** none
**Blocks:** 07 (the Juglet end-to-end run, currently PAUSED)

## Why this exists

Ticket 39 found that on the two sherds that give the pipeline nothing, the growth HAD already found both faces,
and the literal 3 mm radius admission then mixed them into one another. Switching only the admission mode
(`SFS_REASSIGN_MODE=own`, already in the binary, default `radius`) separated them: shared distinct points went
from 2 352 to 0 on Juglet piece 2 and from 1 616 to 0 on piece 9, the mean normal dot flipped from +0.9960 /
+0.9993 to -0.9993570511406065 / -0.9999474210970047, and the two surfaces came to sit 2.2541 mm / 2.1345 mm
apart along the normal against 800-ray wall thicknesses of 2.693 mm / 2.595 mm.

That is a repair on two sherds of one vessel, and both of those clouds were SYNTHETIC: the sampler laid a
uniform covering over the mesh at the pipeline's own spacing (6 259 points on piece 2, 5 257 on piece 9, against
the released clouds' 1 031 and 787). So two questions are open and they lead to opposite decisions:

1. Is own mode a general repair — does it separate the faces on the other seven sherds too?
2. Or is it a two-piece coincidence, and does it DAMAGE the pieces that already work (Pot A is 8 of 8 clean
   pairs today, and four Juglet sherds already write a pair at the shipped density)?

If own mode generalises and Pot A is untouched, it becomes the candidate default. If it damages Pot A, it stays
a switch. If it works only on the synthetic clouds, then what we have learned is that the radius admission is
what destroys a face, and the next repair is the admission window itself, not the mode.

## What must be built

Nothing in the pipeline. `SFS_REASSIGN_MODE` already exists at `mesh_processing_headless.cpp:3903-3905`
(`radius` | `own`, default `radius`), the `own` branch is at `:3923-3925` calling
`improveSurfaceBoundaryByFittingBSplineSurfaceOwn` at `:2365`. Ticket 39's driver
`.scratch/juglet-breaklines/stage39/instruments/run_cell39.sh` already stages a piece, samples a synthetic cloud,
runs both arms of one piece in one job and copies the written surfaces out. This ticket extends the CELL_LIST,
lifts its hardcoded ticket-39 anchors into a per-piece table, and adds the two measurements ticket 39 did not
need.

## Design

Three groups, arms A = `radius` (today) and B = `own`, both arms of a piece in the same job so they share one
staging and one cloud.

### Group 1 — dense synthetic (the generalisation test), all nine Juglet sherds

Sample each sherd's mesh with `mesh38.py` at the pipeline's own spacing for that piece (level 1, sample-from 1),
i.e. the same recipe that produced ticket 39's clouds: piece 2 at 0.209043 mm / 6 259 points, piece 9 at
0.201511 mm / 5 257 points. The other seven take their own `[SPACING-22] S` from the pipeline's log line for
their own mesh.

Pieces 2 and 9 are included as CONTROL CELLS with hard anchors — the whole grid must reproduce ticket 39's
numbers exactly before any other piece's number is used:

| piece | cloud points | achieved mm | arm A surf0/surf1 | arm B surf0/surf1 | A shared | B shared | A dot | B dot |
|---|---|---|---|---|---|---|---|---|
| Juglet 2 | 6 259 | 0.209043 | 4 155 / 3 979 | 4 155 / 3 762 | 2 352 | 0 | +0.9960 | -0.9993570511406065 |
| Juglet 9 | 5 257 | 0.201511 | 2 229 / 3 512 | 2 087 / 3 510 | 1 616 | 0 | +0.9993 | -0.9999474210970047 |

### Group 2 — as shipped, real released clouds, all nine Juglet sherds

The corpus `.pcd` clouds with **no** `SFS_DOWNSAMPLE_TARGET` override, so the pipeline downsamples itself
(`SFS_SPACING_POLICY=piece`, the shipped default). This is the honest "what would own mode do today" answer and
it is the regression test for the four sherds that already write a pair — 1, 4, 6 and 7. Pieces 2 and 9 are
expected to write nothing in either arm; a cell that writes nothing is a result, not a failure.

Anchors to prove the instrument against (ticket 37 arm A, new default): Pot A is not in this group, but
Juglet 1 = 10 800 / 15 780, Juglet 3 = one cluster not written, Juglet 5 = 229 / 2 317, Juglet 7 = 1 753 / 1 997.

### Group 3 — the control, all eight Pot A pieces at the shipped density

The released `.pcd` clouds, pipeline defaults, no override — the same configuration that gives 8 of 8 clean
pairs today. Anchors: Pot A 07 = 24 636 / 26 739, Pot A 08 = 26 774 / 29 286, Pot A 01 = 66 763 / 57 286.
**A Pot A pair whose shared-point count rises above 0, or whose mean normal dot rises above -0.9, is a
regression and is the most decision-relevant number this ticket can produce.**

### Wall thickness for every piece in the grid

Run `measure35.py` (the 800-ray instrument, ticket 35) over every cloud in groups 1-3 in the same job, so every
`med_along` can be stated as a fraction of that piece's own wall. Rows currently on record
(`.scratch/juglet-breaklines/stage35/tables/thickness.tsv`) to prove the instrument against: Juglet 2
2.69305 mm, 9 2.59484, 1 2.35376, 3 2.4516, 5 2.8998, 7 3.26316, Pot_A 7 4.05609, 1 8.2857. Pieces with no row
today are Juglet 4, 6, 8 and Pot A 02, 03, 04, 05, 06, 08 — this run creates their first.

### Per cell, measured and printed

1. `[SPACING-22]` policy / S / achieved spacing, and the cloud's own point count, so the requested spacing is
   proved against the achieved one.
2. `[REASSIGN-22] mode=` from the pipeline's own log — the switch proof: every A cell must print `radius`, every
   B cell `own`.
3. `Number of clusters`, `[RETRY-23]` cluster sizes after the merge, `[STATUS-23] outcome=` and the written
   surface point counts — from the pipeline's log, not from a replica.
4. Per written surface: point count, distinct point count, bounding-box extents in mm, diagonal in mm, the
   fraction of the piece's own cloud within 2 mm of it, and the median folded angle to that piece's mesh.
5. The corrected pair statistic between the two written surfaces (`measure34.py` `pair_pointwise`, ticket 38's
   fix — a signed through-component; the old `pair_stats` abs() defect must not appear anywhere): number of
   Surface_1 points, their nearest Surface_0 distance median, signed through-component median, across-component
   median, coincidence at 1 micron, shared distinct points and mean normal dot (`nest39.py pair`).
6. `med_along / wall_med` as a ratio, beside the wall from the same run's thickness step.

### Figures

Fixed colour map as in ticket 25/39 (id 0 blue, 1 red, 2 green, 3 violet, 4 orange, 5 brown, 6 pink, 7 cyan,
-1 grey), same camera within a figure, a scale bar in mm and the mm/px printed on each panel. Required:

- F1 — for every piece that writes two surfaces in either arm, four panels: edge-on, and three orthographic
  views, arm A above arm B on the SAME camera and scale.
- F2 — a summary chart across all pieces in all three groups: shared-points fraction and mean normal dot, arm A
  against arm B, with Pot A flagged.
- F3 — the signed through-distance histogram of Surface_1 against Surface_0 for the two arms of one Juglet
  piece and of Pot A 07, so the separation (or the nesting) is visible rather than tabulated.

## What counts as the answer

A row per (group, piece, arm) carrying items 1-6, the three figures, and the plain statements:

- on how many of the seven other sherds own mode separates the two faces (shared = 0, dot below -0.9,
  `med_along` within ~30 % of that piece's wall);
- whether own mode changes any of the four as-shipped pairs that already work, and which way;
- whether all eight Pot A pieces stay 8 of 8 with shared = 0 (the regression line);
- and the honest statement of weight: the group-1 clouds are INTERPOLATED from the mesh at a uniform spacing,
  not measured, so a success there proves the pipeline can separate the faces when it is handed a uniform
  covering — it does not prove own mode repairs a real scan, and it must be said in exactly those terms.

## Constraints

- **No tracked source change.** Everything lives under `.scratch/juglet-breaklines/stage40/` plus the ticket
  file. If any file other than those must change, STOP and report before touching it.
- **Compute nodes only** (no login-node work, no laptop work). `sacct`-visible jobs under the project.
- **At most three jobs**, split by group — one job per group, never by arm and never by piece. Groups 1 and 2
  are cheap; give each a 30-minute wall and let the driver's own budget stop it.
- **Do not set `SFS_DOWNSAMPLE_TARGET` for groups 2 and 3** — let the pipeline downsample itself. (Ticket 38's
  Pot A cell was killed at the wall clock only because its driver bypassed downsampling on a 1 000 000-point
  cloud.)
- **CRLF check every generated script before submitting** (`file`, or `grep -c $'\\r'`). Two grids have died on
  `set: pipefail: invalid option name`; the stage trees carry `.gitattributes '* -text'` for exactly this.
- The `[xyz, not ply]` trap: the pipeline writes some surfaces as `.xyz` beside the `.ply`. Measure whichever
  exists and record which extension was measured; do not silently skip a surface.
- Corpus `$CORP`, the canonical checkout and `/opt/sfs-pristine` are read-only. Record `/opt/sfs-pristine` as
  ABSENT if it is absent; do not create it. md5 the corpus and the inputs before and after every job.
- **Geometry is deleted with a record written before the delete** (per-class counts and bytes, one row per
  path); surfaces, logs, tables and figures are KEPT for the lead. Nothing large survives the ticket.
- **Rows appended to `/data/gpfs/projects/punim2657/SfSpp/runs/index.tsv` with `verdict` and `human_note` EMPTY.**
  Exactly six tab-separated fields.
- **No verdicts, no `Status:` edits, no `intent/` writes, no merge.** Report numbers, paths and job IDs.
- Do not ask the lead to decide whether a result is good; report what was measured.

## Evidence to report

1. Branch and head sha, `git diff --stat main...HEAD`, and the proof that nothing outside `.scratch/juglet-breaklines/`
   and the ticket file changed.
2. The run directory (or directories) of record with their job IDs and `sacct` State/ExitCode, plus every
   submission that failed and why.
3. The per-cell table for all three groups, every item 1-6 column present.
4. The control-cell comparison for Juglet 2 and 9 against the anchors above, stated as equal or not, column by
   column.
5. The switch proof: the count of A cells printing `mode=radius` and B cells printing `mode=own`, against the
   number of cells planned. (Ticket 36 lost a whole grid to empty switch strings — prove the switches took.)
6. The wall-thickness table for every cloud in the grid, with the eight recorded rows reproduced beside it.
7. The three figures, with their pixel sizes, mm/px and the measured ink/grey fractions where they carry colour.
8. The `xyz`-vs-`ply` census: how many surfaces were measured and from which extension.
9. Corpus and inputs md5 before/after (row counts), `/opt/sfs-pristine` status, and the geometry deletion record
   (per-class counts and bytes) with the count of geometry files left.
10. The index rows appended, quoted.

## Progress (work in progress)

(the worker appends here)

## Lead reading

(the lead writes this after verifying first-hand)

### verified:

### What this does not settle
