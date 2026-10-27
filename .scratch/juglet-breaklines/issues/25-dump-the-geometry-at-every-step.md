# 25: dump the geometry at every step, with the cluster label on each point

**Answers:** U19 (vessel level), E1 (preprocessing half)
**Blocked by:** none — ticket 26 is merged (`0902718`); this ticket edits the same file and builds on it
**Status:** ready-for-agent
**Working in:** chat on Thinkbook16 (2026-10-27)

A ticket on the **instrument**, not on the method. It adds a per-step dump behind one switch whose default
writes nothing extra, so that any later repair can be checked at the rung it acts on and a failure can be
located instead of argued about. **Report evidence; do not declare a winner.**

## Why a dump of the mesh is not enough — the label is the measurement

Every geometry write in `mesh_processing_headless.cpp` on main at `cba82cb` (grep over
`savePLYFile|savePCD`):

- `:778` `<piece>_SampledWithNormals.ply` — the last artefact before clustering;
- `:1119` `cloudForSpline.pcd` — the points sampled for the spline fit;
- `:2307` `<base>.ply`, `:3026` `_flipped_normal.ply` — intermediates of the boundary fit;
- `:3102-3103` and `:3150` `tmpSurfaceCluster_Improved_{0,1}.ply` — the final pair (or the single surface);
- `:3218` `<piece>_unclustered.ply`.

**Between the cloud going in and the surfaces coming out there is no per-point label anywhere.** Every
question argued this week is a question about *which points belong to which region*: did the growth find two
walls, did the merge fuse them, did the admission window swallow one. A picture of the raw cloud at each step
shows the same grey cloud at each step, because none of these steps moves the points — they only relabel them.

So each dump carries a **per-point cluster id** and the normal. Then one render coloured by id answers the
question at a glance, and one PLY parser answers it as a table.

## The rungs, and exactly where each is taken

One file per rung per piece, ASCII PLY with two extra scalar columns (`cluster` int, `reason` uchar), plus a
`.json` sidecar. Rungs 2-5 write the **same point set**, so they can be diffed point by point.

| rung | taken at | sidecar must carry |
|---|---|---|
| `r1_downsampled` | after the density call (`:3385` into `downsamplePointCloud` `:799`) | spacing policy and S actually used (the `[SPACING-22]` values), samples, points in and out |
| `r2_clusters_premerge` | after `growPaper234` (`:2906`; function `:2463`) | cluster sizes and the floor **actually applied** (`dynMinCluster` at `:2875`, and the ticket-23 cap at `:2890` if it fired), `-1` = never claimed |
| `r3_after_merge` | after `mergePaper234` (`:2958`; function `:2667`) and `classifyAndOrderPaper234` (`:2960`; function `:2742`) | every merge: which cluster into which, the pair count and the criteria values that fired |
| `r4_after_reassign` | after `improveSurfaceBoundaryByFittingBSplineSurface` (`:3076-3077` pair, `:3145` single; function `:1525`) | the window **actually used** (the `[WINDOW-26]` values), and per point: admitted-own / admitted-other / rejected-distance / rejected-normal |
| `r5_write` | at `savePLYFile` (`:3102-3103` / `:3150`) | which points reached `Surface_0`, which `Surface_1`, which neither; the write gate's decision (pair / single / none) |

Naming: `dump/<arm>/<piece>/r<N>_<name>.ply` + `.json`. ASCII, so an instrument can read it without a PCL
dependency — a binary PCD already killed one of our coverage scripts.

## Colour is the reading, so the colour is fixed

Cluster id 0 is always the same colour, id 1 always the next, `-1` (never claimed) always grey, and that
mapping is identical in every panel, every rung, every arm and every piece. If colours were assigned per
panel, a merge and a renumbering would look the same and the ladder would be unreadable. At rung 4 the
cluster colour stays primary — a point keeps the colour of the region it ended up in — with rejected points
drawn as small grey dots, so a swallow is visible as colour 1's points turning into colour 0's, and the
reason code read from the sidecar rather than from the picture. The camera, the scale and the legend are
identical across every panel of a figure, and the legend lists each colour with its cluster size at that rung.

## What we now know, so the ladder has a target

A ladder with no expectation is a photo album. These are the expectations from tickets 20, 23, 24 and 26, and
the picture is what either confirms or refutes each one:

| piece | at today's defaults (chain on, 0.6 mm) | with the chain off |
|---|---|---|
| `Juglet_Piece_2` | 1 031 points into clustering, **zero regions at all 21 retries** — the failure is upstream of every later rung | a pair is written (ticket 26, `W*L` rows) — so the older growth finds something here and the newer finds nothing |
| `Juglet_Piece_3` | two regions (169, 99) whose mean normals point the same way (dot +0.74, 0.52 mm apart = two patches of **one wall**), fused to one by one merge (5 boundary pairs, `pairDistMin` 0.520166) — then one surface or none | at native density the raw regions are **opposite** (dot −0.983, 1.90 mm = a real pair), and the merge still fires — the rung that shows whether a real pair survives |
| `Juglet_Piece_5` | **one region** (679 points of 3 021) — the second wall was never separated, nothing later can recover it | the only genuine wall pair at this density (2.28 mm through, 0.36 mm along, coincidence 0.0133) |
| `Juglet_Piece_7` | two regions and a written pair (1 012 / 829) that is **two coplanar patches** (0.230 mm apart through the normal) — the case that refuted my first wall test | the one clean pair at native density (3.14 mm through, 0.31 mm along) — the positive control the reader can calibrate colour against |

## Arms and pieces

Three dump arms over **four pieces** (`Juglet_Piece_2`, `_3`, `_5`, `_7`):

- **B** — today's defaults (`SFS_DUMP_STAGE` set): 0.6 mm density step, paper chain on.
- **D** — `SFS_PAPER_CHAIN=0`, 0.6 mm: the older region growing at today's density.
- **E** — `SFS_PAPER_CHAIN=0`, `SFS_DOWNSAMPLE_TARGET=-1`: the older growth at native density.
- **A** — defaults with `SFS_DUMP_STAGE` **unset**: the defaults proof (acceptance 1).

That is 3 x 4 x 5 = 60 rung files, a few hundred megabytes at most: each rung holds that cloud's own point
count, not a mesh. No 9-piece sweep, no per-piece arm matrix.

## The figures

One strip of panels per figure, left to right `r1 | r2 | r3 | r4 | r5` (r1 in grey is the reference cloud), a
scale bar in each panel, and one shared legend. The scale must resolve this material's wall gap (0.75-3.43 mm).
Six figures:

1. `F1` piece 3, arm B — the merge fusing two patches of one wall.
2. `F2` piece 3, arm E — the same sherd at native density, where the two regions are opposite.
3. `F3` piece 2, arm B — zero regions, for contrast with `F2`'s and `D`'s rows.
4. `F4` piece 5, arms B and D as two rows of one figure — one region versus the genuine pair.
5. `F5` piece 7, arm E — the known-good pair, the positive control.
6. `F6` piece 7, arm B — the two coplanar patches, for contrast with `F5`.

Two rows in one figure are allowed only when the colour map, camera and scale are identical across rows.
**Return the paths, do not attach the images.**

## Cost guard (this is the part that can sink the run)

- `SFS_DUMP_STAGE=<dir>` — **unset writes nothing at all** (acceptance 1).
- `SFS_DUMP_PIECES=<name,name,...>` — only the pieces named are dumped.
- The ladder dumps are the deliverable and stay until the lead has read them; **everything else** in the stage
  tree is deleted with a counted record. Do not delete the dumps before reporting.

## Constraints

- With the switch unset, output must be identical to today's: acceptance 1.
- No change to any threshold, tolerance, growth rule, merge rule, reassignment rule or write rule.
- Compute nodes only. Corpus and `/opt/sfs-pristine` read-only, md5 before and after (`/opt/sfs-pristine` is
  absent on this host — record ABSENT, do not create it).
- At most four jobs, split by pot not by arm; CRLF check on every uploaded script before `sbatch`.
- One appended `index.tsv` row per job with **verdict and human_note left EMPTY**.

## Acceptance criteria

1. **Defaults proof:** with `SFS_DUMP_STAGE` unset, every written surface is identical to the pre-change
   binary's (point set, not md5 — the curvature column is uninitialised), and no `dump/` directory is created.
2. Rungs 1-5 exist for every (arm, piece); each is a readable PLY carrying that step's point count; each
   sidecar names the floor, the window and the merge values **actually used**.
3. `out/ladder.tsv` has one row per (arm, piece, rung) with the expectation from the table above, the measured
   values, and pass/fail — evidence only.
4. The six figures of the section above, with the fixed colour map, scale and camera.
5. No tracked source changed except `mesh_processing_headless.cpp` (plus `.scratch/` instruments).
6. Corpus and `/opt/sfs-pristine` md5 before/after identical (or recorded ABSENT).
7. Stage geometry deleted with a counted record, the ladder dumps kept and their paths reported.

## What this cannot settle

- It shows where a decision changed, not whether the decision was right. A merge of two regions is **correct**
  when they are one wall and wrong when they are two, and the ladder alone cannot tell the difference — that
  is the through/along test on the surfaces.
- The wall gap is known from the mesh, so a label that looks wrong against a flat picture may still be right
  against the surface.
- The rung-2 picture is a flat projection of a curved sherd: two colours on one side of the picture are not
  automatically one wall — the sidecar's distances decide that, and the figure is there to show where to look.
- Four pieces and three arms is a sample of the ladder, not a survey of it.
