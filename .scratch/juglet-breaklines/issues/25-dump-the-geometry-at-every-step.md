# 25: dump the geometry at every step, with the cluster label on each point

**Answers:** U19 (vessel level), E1 (preprocessing half)
**Blocked by:** none — ticket 26 is merged (`0902718`); this ticket edits the same file and builds on it
**Status:** done
**Working in:** chat on Thinkbook16 (2026-10-27)
**Branch:** 25-dump-the-geometry-at-every-step, in /c/PR/worktrees/sfs/25

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

## Lead reading — 2026-10-27 (verified first-hand, not taken from the worker's report)

### The one sentence

The second surface is not lost at one step, and the step that loses most of it is the region growing itself:
on today's defaults it puts **78–82 % of each sherd's points into no region at all** (piece 3: 1 199 of
1 467; piece 5: 2 342 of 3 021; piece 7: 3 455 of 4 254) and 100 % of piece 2, and the regions it does grow
begin life as **narrow bands along an edge**, not as faces. Everything written afterwards — the merge, the
3 mm reassignment, the pair gate — acts on those bands.

### Rung by rung (all twelve cells, the numbers as they came out of the run)

"unclaimed" is the count of points that belong to no region; it is exactly the complement of the region
sizes, which is why it is the number to watch.

| piece | arm | r1 in → out | r2 regions (unclaimed) | r3 after merge | r4 fit | r5 written |
|---|---|---|---|---|---|---|
| 2 | B defaults | 2 565 → 1 031 | **none**, 21 retries (1 031 = 100 %) | none | not fitted | nothing |
| 3 | B defaults | 3 493 → 1 467 | 169 + 99 (1 199 = 82 %) | **268**, one merge, 5 boundary pairs | single, not fitted | nothing (gate single-off) |
| 5 | B defaults | 6 211 → 3 021 | 679 (2 342 = 78 %) | 679 | single, not fitted | nothing |
| 7 | B defaults | 8 421 → 4 254 | 326+263+77+68+65 (3 455 = 81 %) | 403+263+68+65, merged 77 into 326 | pair | 1 012 / 829 |
| 2 | D chain off | 2 565 → 1 031 | 174 + 65 (792 = 77 %) | unchanged | pair | 345 / 178 |
| 3 | D chain off | 3 493 → 1 467 | 343 (1 124 = 77 %) | unchanged | single | nothing |
| 5 | D chain off | 6 211 → 3 021 | 828 + 63 (2 130 = 71 %) | unchanged | pair | 1 845 / 300 |
| 7 | D chain off | 8 421 → 4 254 | 809+553+84+84+53 (2 671 = 63 %) | unchanged | pair | 2 005 / 1 462 |
| 2 | E native, chain off | 2 565 → 2 565 | 94+80+61 (2 330 = 91 %) | unchanged | pair | 434 / 342 |
| 3 | E native, chain off | 3 493 → 3 486 | 487 (2 999 = 86 %) | unchanged | single | nothing |
| 5 | E native, chain off | 6 211 → 6 208 | 1 000+60+58 (5 090 = 82 %) | unchanged | pair | 2 584 / 317 |
| 7 | E native, chain off | 8 421 → 8 421 | ten regions, 1 701 down to 50 (5 619 = 67 %) | unchanged | pair | 4 204 / 2 638 |

No fitted surface in any arm used anything but the literal 3 mm window ("clamp=3.0 rule=literal reason=ok"
in every rung-4 sidecar): ticket 26's switches are off by default and this run did not change them.

### What each picture shows

Paths are in this repo under .scratch/juglet-breaklines/stage25/figures/. Every strip is r1|r2|r3|r4|r5,
identical camera and scale, one fixed colour per cluster id, scale bar in every panel.

- **F1 piece 3, defaults.** r2 shows the two regions as **two strips side by side along one band** of the
  sherd, blue (169) and red (99). r3 is one blue band (268) — the merge joined them, and it was right to:
  the panel shows two strips of one surface, not two faces. r5 is the bare sherd with nothing coloured.
- **F2 piece 3, chain off at native density.** One blue region (487) covering part of the face, unchanged
  through r3, nothing written. This is the cell that refuted my expectation table (below).
- **F3 piece 2, defaults.** All five panels grey. There is no coloured point anywhere at any rung. The
  silence is visible, and it starts at r2: the region growing never produces a region for this sherd.
- **F4 piece 5, defaults (upper row) against chain off (lower row).** The defaults' one region is a band
  along the left edge (679 points). With the chain off the same band splits into 828 + 63, and after
  reassignment the small one grows to 237 distinct points — that is the pair the corrected test calls
  genuine (2.276 mm through the face, 0.361 mm across). Both rows are coloured along **the same edge**: the
  pair is the two faces of that band, not two different parts of the sherd.
- **F5 piece 7, chain off at native density.** Ten slivers spread over the whole shell; the two largest
  (1 701 and 453) become the written pair, the second grown 4.8× by the reassignment. The genuine pair
  (3.140 mm through, 0.306 across) is real, and it is built out of a fifth of the cloud.
- **F6 piece 7, defaults.** r2 shows a red band along the upper edge and a blue band along the left edge,
  clearly apart. After the merge and the reassignment both bands thicken and, in this flat projection,
  cover the middle — which is exactly the 0.230 mm through-offset measured on the kept surfaces: two bands
  of one shell, made to look like two faces by a view that cannot see through the wall.

**The pictures cannot separate two faces on a 2–3 mm wall.** That is not a criticism of the figures: it is
why the through/along statistic exists, and why the same flat view misled me in ticket 24. The figures
answer the question they were drawn for — *where* along the ladder each sherd stops — and they answer it
clearly.

### The two rows where my own expectation was wrong

The ticket carried an expectations table; the run checked it. Two rows disagree, and both are my errors,
not the pipeline's:

1. **B piece 7 r2.** I wrote "two regions (1 012, 829)". Those are the **sizes of the written surfaces at
   r5**, read off a different ticket; the pre-merge regions are five, 326 down to 65. What the table should
   have said is "several patches, two of which are joined by the merge and end up written".
2. **E piece 3 r2.** I wrote "two opposite regions, dot −0.983 at 1.90 mm". That measurement belongs to the
   **September binary replayed in ticket 21**, not to today's SFS_PAPER_CHAIN=0 path: today's chain-off
   growth gives this sherd **one** region (487) at native density. **The chain-off switch is not a time
   machine** — the old binary used PCL RegionGrowing with 15–40 neighbours and different seeds, today's
   chain-off path is still today's code with the merge rule swapped out.

I am recording both because an expectation table only has value if its misses are published.

### What the reassignment does, measured

The 3 mm admission step multiplies a region: 326 → 609 distinct points and 263 → 566 (piece 7, defaults);
828 → 1 022 and 63 → 237 (piece 5, chain off); 1 701 → 2 503 and 453 → 2 185 (piece 7, chain off);
94 → 340 and 80 → 262 (piece 2, chain off). That is **1.2× to 4.8×**. A 63-point sliver can come out of it as
a 237-point "surface" — which is precisely why a size, a dot product or a flat picture cannot call a wall
pair, and why ticket 26's through/along test is the one to keep.

### The duplication defect is visible in this run too

Every rung-5 sidecar carries vertices and distinct positions: piece 5 chain off 1 845 / 1 022 (45 % duplicates),
piece 7 defaults 1 012 / 609 and 829 / 566, piece 5 at native 2 584 / 2 556 (1 %). So the dead de-duplication
block found in ticket 26 is not theoretical: most of these surfaces carry their own cluster between 1.2× and
1.45× over.

### Where this leaves the repair

- **The normals are not the next repair** (ticket 24 settled that) and **the window is not either** (ticket 26).
- **The merge is doing its job** — F1 and F6 show it joining patches that belong together.
- **The pair-only write gate is now visible but is the smaller half**: since ticket 23 a one-region sherd can
  be written as one surface; the deeper problem is that on the Juglet the growth usually finds ONE band
  where two faces are needed. Of the four sherds dumped here, piece 2 finds nothing at all in one of three
  arms; across the earlier grids pieces 1, 4, 6, 7 write pairs at defaults, 2, 3, 5 and 8 produce regions in
  some arm, and piece 9 has never been given a surface (its best case was a single region of 21 points).
- So the next repair is **the growth's single pass and its permanent claiming**: 63–100 % of every sherd is
  never in a region, a region that fails the floor burns its points for good, and nothing ever re-seeds on
  what is left. A second pass over the unclaimed points is the change the ladder points at, and pieces 5
  (chain off) and 7 (native) show the opposite face is reachable when a seed survives there.

### verified: the command or file behind each load-bearing claim

- awk over out/ladder.tsv → 60 rows, 12 cells, the region sizes and unclaimed counts in the table above.
- a second awk restricted to ($1=="D"||$1=="E") && ($3=="r2"||$3=="r5") → the D and E rows re-read directly, e.g. "D 5 r2 clusters=2 sizes=[828, 63] ... unclaimed=2130"; "E 7 r5 vertices=[{'surface': 0, 'vertices': 4204, 'distinct_positions': 2503}, ...]".
- python3 json.load on the rung-3 sidecars → "D merge_tracking= unavailable-mergeclusters clusters= [828, 63]" and "E ... clusters= [1000, 60, 58]", so the chain-off arms genuinely bypass mergePaper234.
- ls of out/dump/{B,D,E}/Juglet_Piece_{2,3,5,7}/r[1-5]_* → 60 PLY + 60 sidecars; jsoncheck reports sidecars=60 bad=0, plys=60 bad=0.
- grep PROOF25 out/proof.log → the two piece-7 lines with pointset_equal=yes only_a=0 only_b=0 for new-vs-pre-change and new-vs-new-rerun; the eight differing comparisons are the chain-off arms and differ by construction.
- git diff --stat a398d8a d543e18 → the ticket file only (2 insertions, 1 deletion), so the OLD binary is the same source.
- figures fetched to C:/PR/SfSpp_preprocessing/artifacts/juglet-p25/ and **opened one at a time** (F1 86 174 B, F2 72 142, F3 66 737, F4 147 041, F5 121 378, F6 150 410); the readings above are of the images, not of the worker's description of them.
- wall thicknesses quoted against the pairs (piece 5 2.900 mm, piece 7 3.263 mm) are ticket 20's mesh ray test, not this run.

### What this does not settle

- **The unclaimed fraction on Pot A was not measured.** Without it, "78–82 % unclaimed" is a property of
  these three Juglet sherds, not yet a contrast with the sample that works. It is the first cell of the next
  ticket, and until it exists I will not call the number a defect.
- Chain-off arms never enter mergePaper234, so no merge decision is on record for D or E.
- The rung files are written inside the 30-retry loop, so a piece that retried keeps only its last retry.
- No direct D-against-DOLD point-set comparison exists (the job budget ran out at four jobs).
- Four pieces and three arms is a sample of the ladder, not a survey: pieces 1, 4, 6, 8 and 9 were not dumped.
- Nothing here says which of the two arms is right; the ticket was an instrument.
