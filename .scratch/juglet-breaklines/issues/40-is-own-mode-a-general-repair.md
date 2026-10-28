# 40: is own mode a general repair, or a two-piece coincidence?

**Status:** done
**Working in:** chat on Thinkbook16 (2026-10-29)
**Branch:** 40-is-own-mode-a-general-repair, in /c/PR/worktrees/sfs/40
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

2026-10-29, worker 221bbb8b (run 2 of 3 for this brief; worker 1, ca266a33, died before
submitting anything - untracked instruments only, no job, no index row).

Jobs: 33939133 FAILED 9:0 00:02:47 (spacing regex double-backslash in submit40.sbatch.tmpl;
no cell ran - the one dead plumbing submission). 33939160 t40-g1 COMPLETED 0:0 06:24
(9 pieces, dense synthetic, arms A+B). 33939253 t40-g2 COMPLETED 0:0 04:18 (9 pieces,
released clouds). 33939254 t40-g3 COMPLETED 0:0 12:04 (8 Pot A pieces).

Run dirs: 20261029-0337_668e969_t40-g1, 20261029-0355_08c3653_t40-g2, 20261029-0355_08c3653_t40-g3
under /data/gpfs/projects/punim2657/SfSpp/runs/. Branch commits 2268614 (instruments, inherited from
worker 1), 668e969 (spacing-regex fix), 08c3653 (switch-proof grep fix). Corpus md5 identical in all
three runs; /opt/sfs-pristine ABSENT (recorded, not created); geometry deleted with counted records;
cell surface PLYs kept (g1 36, g2 16, g3 32) per the ticket's keep list.

Tables at <run>/out/cells-pipeline/: pipeline_cells.tsv, surfaces.tsv, surface_pairs.tsv, nest.tsv,
walls.tsv, xyz_census.tsv, switch_proof.tsv, cloud_gate.tsv. Figures g1 28 / g2 13 / g3 25 PNG plus
f2 pair summaries.

Deviations disclosed by the worker: g1 switch-proof initially 0/9 from a leading-tab grep,
recomputed on the login node; g2 wall anchors only 1 of 6 within 5 percent (walls measured on the
downsampled SampledWithNormals clouds, not ticket 35's full released clouds); g2 J3 anchor_hit
mechanically no although the outcome was in fact one cluster; submit40.sh tee'd to logs/ before it
existed for g2/g3 (submission unaffected).

## Lead reading

2026-10-29. Every number below re-read by me from the run tables (nest.tsv, surface_pairs.tsv,
pipeline_cells.tsv, walls.tsv, switch_proof.tsv) and from sacct - not taken from the worker's report.

### The one-line answer

On a uniform covering at each sherd's own spacing, own mode is a GENERAL repair: it separates the
two faces on all nine Juglet sherds (9 of 9, shared points 0, mean dot -0.94 to -1.00, one wall
thickness apart) where today's radius mode nests on eight of nine. On the real released clouds it
is safe (Pot A 8 of 8 untouched, both arms shared 0, dot <= -0.9988) but only partly effective:
it stops the point-sharing everywhere, yet yields a genuine opposite-facing pair only on piece 1 -
on pieces 5, 7, 8 the two grown regions are patches in different places, which is a growth problem,
not an admission problem.

### Group 1 - dense synthetic covering, all nine sherds (job 33939160)

Control cells exact (the hard anchors from ticket 39): P2 A shared 2352, dot +0.9960; P2 B shared 0,
dot -0.99936; P9 A shared 1616, dot +0.99932; P9 B shared 0, dot -0.99995.

Arm A (radius, today's default) NESTS on eight of nine: the two surfaces share 3833-10112 of the
smaller surface's distinct points and their mean normals agree (+0.68 to +1.00) - one face written
twice, the ticket-38 finding reproduced across the whole vessel. Piece 7 is the exception, already
separated under both arms (shared 0, dot -0.998, med_along 2.96 mm).

Arm B (own mode) separates ALL NINE: shared 0 on every piece, mean dot -0.9355 (J1) to -0.99995,
med_along 1.88-2.96 mm (70-90 percent of each sherd's ray wall), med_across 0.16-0.28 mm,
coincidence 0.0-0.012. Per piece (med_along / med_across, mm): J1 1.961/0.229, J2 2.254/0.159,
J3 1.987/0.168, J4 2.243/0.187, J5 2.416/0.277, J6 2.392/0.184, J7 2.964/0.243, J8 1.882/0.180,
J9 2.134/0.188.

Caveat carried forward from ticket 39: these are synthetic coverings (the mesh sampled at its own
[SPACING-22] S, 4-10x the released clouds' downsampled densities). They prove the pipeline CAN
separate both faces when the points are there; they do not promise it on a scan.

### Group 2 - real released clouds, adaptive default (job 33939253)

NEW FINDING, a regression of ticket 37's default flip: pieces 4 and 6 produce ONE cluster and no
surface at all, in BOTH arms (clusters=1). At the old fixed 0.6 mm they wrote pairs (182/732 and
608/1016). They were never in the ticket-36/37 piece lists, so the adaptive-spacing default was
never measured on them - the flip silently lost two sherds that had worked. Pieces 2, 3, 9 remain
silent as known (0, 1, 0 clusters).

Own mode on the four pieces that do write two surfaces (arm A -> arm B, shared points both ways /
mean dot): J1 5497 / +0.347 -> 532 / -0.914; J5 34 / -0.482 -> 0 / -0.443; J7 336 / +0.515 ->
10 / +0.403; J8 200 / +0.849 -> 0 / +0.758. Corrected pair statistic: J1 B med_along 1.815 mm,
med_across 0.528 mm, coin 0.035 against a wall of ~2.06-2.35 mm - borderline genuine. J5 B
along 8.19, across 11.36 (worse than A); J7 B along 2.39, across 7.94; J8 B across 6.63 - patches
in different places, not two faces of one wall. So on real clouds the admission is no longer the
mixer; the growth/cluster layout is.

Walls on the downsampled clouds run 0.2-0.3 mm off ticket 35's full-cloud anchors (only J7 within
5 percent) - a method difference (SampledWithNormals cloud vs released cloud), recorded, not chased.

### Group 3 - Pot A control (job 33939254)

No regression from own mode: all 8 pieces have shared 0 and mean dot -0.99884 to -0.99967 in BOTH
arms, surface point counts within +-2 of the anchors (PA01 66764/57288 against 66763/57286, PA07
24636/26739 exact, PA08 26774/29286). PA01 A med_nn 7.0952, med_t_signed -7.0890, coin 0.0; arm B
nearly identical. Wall anchors HIT (PA01 8.2857 vs 8.2857; PA07 4.0574 vs 4.0561).

### What I take from it

1. Own mode is the right default for the admission step: 9 of 9 on uniform coverings, 0 damage on
the control pot. The radius admission's point-sharing is reproduced as a vessel-wide property,
not a two-sherd accident.
2. It is not sufficient on real clouds: only piece 1 gains a genuine pair. Pieces 5/7/8's two
regions lie in different places - the next blocker is upstream (growth/cluster layout), not the
window.
3. The ticket-37 default flip has an unmeasured cost: pieces 4 and 6 (and piece 3's single
cluster) are lost at the adaptive default. Any default change must be re-run over ALL nine
sherds before it ships - this grid is the first that covered all nine.
4. Weight: one vessel, one pot, synthetic coverings for the 9-of-9 claim, real clouds for the
safety claim. A lead with a strong direction, not a shipped repair.

### Where the jobs went wrong

33939133 died on a double-backslashed spacing regex before any cell ran (1 dead submission, void).
The g1 switch-proof grep had a leading-tab bug (recomputed on the login node); the g2 wall
comparison measured a different cloud class than ticket 35's anchors; submit40.sh tee'd to logs/
before it existed for g2/g3. Worker 1 (ca266a33) died before submitting anything - attempt 2 of 3.

### What this does not settle

- Whether own mode should ship as the default NOW, or after the pieces-4/6 regression is handled:
  the flip question is a decision for the conservator, with this grid as its evidence.
- Whether the growth on real clouds can be brought to two-place layout (pieces 5/7/8) - a
  different repair (growth criterion or a second pass), not this one.
- Whether a synthetic covering may stand in for a scan in any number on record - the standing
  caveat; the 9-of-9 is a capability statement, not a performance claim.
- finishImprovedSurface's copy-the-larger-cluster-over branch and the still-literal 3 mm window on
  the radius path remain named follow-ups.

### verified:

- sacct -j 33939133,33939160,33939253,33939254 -> FAILED 9:0 00:02:47 / COMPLETED 0:0 06:24 /
  COMPLETED 0:0 04:18 / COMPLETED 0:0 12:04.
- g1 out/cells-pipeline/nest.tsv, control rows read at the line: P2 A shared 2352 dot
  +0.9960274472338446; P2 B shared 0 dot -0.9993570511406065; P9 A 1616/+0.9993183797978673;
  P9 B 0/-0.9999474210970047 - exactly the ticket's hard anchors.
- g1 nest.tsv all nine arm-B rows: shared 0 everywhere; dots -0.9355 to -0.99995; med_along
  1.882-2.964 mm; med_across 0.159-0.277; coin <= 0.012.
- g2 pipeline_cells.tsv rows for pieces 2/3/4/6/9: status_outcome=none both arms, clusters
  0/1/1/1/0; pieces 4 and 6 clusters=1 (the regression).
- g2 nest.tsv arm A -> B: J1 5497/+0.347 -> 532/-0.914; J5 34/-0.482 -> 0/-0.443; J7 336/+0.515
  -> 10/+0.403; J8 200/+0.849 -> 0/+0.758.
- g2 surface_pairs.tsv: J1 B med_along 1.815 med_across 0.528 coin 0.035; J5 B 8.19/11.36;
  J7 B 2.39/7.94; J8 B across 6.63.
- g3 nest.tsv: 8 of 8 shared 0 both arms, dot -0.99884 to -0.99967; g3 pipeline_cells.tsv
  surface counts PA01 66764/57288, PA07 24636/26739, PA08 26774/29286 (anchors 66763/57286,
  24636/26739, 26774/29286).
- walls.tsv: PA01 8.285696 and PA07 4.057357 against ticket-35 anchors 8.2857 / 4.05609 (HIT);
  g2 first rows J1-J9 as quoted, only J7 within 5 percent of the full-cloud anchors.
- switch_proof.tsv: g1 A 9/9 B 9/9; g3 8/8 + 8/8; g2 4/9 + 4/9 with the five none-outcome cells
  genuinely carrying no [REASSIGN-22] line.
- git diff --stat main...HEAD -> 19 files, all under .scratch/juglet-breaklines/stage40/ and the
  ticket; corpus md5 identical before/after in all three runs; /opt/sfs-pristine ABSENT x3.
- index.tsv tail -> the three t40 rows present with verdict/human_note empty (filled by the lead
  in the close-out).

### What this does not settle
