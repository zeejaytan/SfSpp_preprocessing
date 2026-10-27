# 37: Make the adaptive step the default, take the floor away, and look at the regions

**Status:** in-progress
**Working in:** chat on Thinkbook16 (2026-10-28)
**Branch:** 37-adaptive-default-and-the-regions-under-the-floor, in /c/PR/worktrees/sfs/37
**Answers:** U19, E1
**Blocked by:** none
**Blocks:** none

## Why this ticket exists

Three things, all from the conservator's decisions on 2026-10-27:

1. **Adaptive spacing becomes the default.** Ticket 36 showed the rule costs the sample pot nothing (8 of 8
   two-surface, pairs unchanged or better) and more than doubles the samples on the small sherds. He asked for
   this change and it is one word in the parameter block.
2. **Test without the floor of 50.** "Number of clusters is equal to 0" is printed **after** the floor
   (`mesh_processing_headless.cpp:3668`), and the floor is applied inside `growPaper234`, which takes
   `dynMinCluster` as an argument. So the pipeline reports nothing about the regions it grew and then threw
   away. The conservator's reading is exactly right: we have been blind.
3. **Look at the regions that do get grown.** Not only count them: dump them as geometry and render them.

## Part A — the default change

- `mesh_processing_headless.cpp:4356`: `std::string spacingPolicy = "fixed";` -> `"piece"`.
- `SFS_SPACING_SAMPLES` already defaults to 200 (:4360). Leave it.
- `SFS_COUNT_SCALE` stays **off** (unscaled counts) - ticket 36 showed the scaled version is what empties small
  sherds.
- `SFS_SPACING_POLICY=fixed` must still restore today's behaviour exactly.
- Update the comment block beside the defaults so the next reader sees why.

Two proofs are required, both in the same run:
- **Proof 1 (the override still works):** with `SFS_SPACING_POLICY=fixed`, the new binary reproduces the
  pre-change binary exactly on `SampledWithNormals.ply` (md5) for **Pot_A 01, 02, 07, 08** and Juglet 1, 3, 7.
- **Proof 2 (the new default is ticket 36's arm B):** with no environment at all, the new binary reproduces
  ticket 36's arm B surface counts on Juglet 1 (10800/15780), 5 (229/2317), 7 (1753/1997) and keeps
  Pot A 8 of 8.

## Part B — take the floor away

Existing switches only: `SFS_COUNT_SCALE=auto` with `SFS_FLOOR_CEILING=0.005` caps the floor at 0.5 % of the
points, which on these clouds is **10-20 points** instead of 50, and `SFS_SINGLE_CLUSTER=write` writes a
one-region outcome as a surface. This is the "what comes out with no 50 floor" cell. No code change for it.

## Part C — what the growth produces before any floor

The **python emulator** is the only instrument that can see this: the pipeline cannot, by construction. The
replica lives in `.scratch/juglet-breaklines/stage28/` (ticket 28) and `stage29/` (ticket 29), and it was
validated **MATCH** against the pipeline's own rung-2 sidecars on pieces 3, 5, 7 and Pot_A 07 at the fixed
0.6 mm step with re-estimated normals.

For pieces **2, 9, 3, 5, 7** and **Pot_A 07**, at **adaptive spacing** (each sherd's native step) and with the
**honest nearest-carry normals** (the carry is described in tickets 33/34):
- the full region-size distribution **before any floor**: number of regions, largest, and how many reach
  >=10 / >=20 / >=30 / >=50 points and >=1 % / 5 % / 10 % of the cloud;
- angle refusals per point and the growth depth of the largest region;
- the same figures at the fixed 0.6 mm step, side by side, so the adaptive step's effect on the *unfloored*
  distribution is visible.
- **Re-validation is mandatory before any number is used:** the replica must reproduce the pipeline's own
  `[STATUS-23]`/rung-2 cluster sizes on pieces 3, 5, 7 and Pot_A 07 in the new default configuration. If it
  does not match there, say so and report the replica's numbers as unvalidated - do not quietly use them.

## Part D — the picture

- Dump the pre-floor regions for **Juglet 2, Juglet 9** and **Pot_A 07** as one PLY per piece with a per-point
  cluster id (int) and a reason code (uchar), plus a `.json` sidecar listing every region's size.
- Render each piece as **three orthographic views**, points coloured by region id with a **fixed colour map**
  (id 0 blue, 1 red, 2 green, 3 violet, 4 orange, 5 brown, 6 pink, 7 cyan, -1 grey for unclaimed), a **5 mm
  scale bar**, the scale in mm/px printed on the figure, and the same camera and scale for Pot_A 07 as the
  reference. Resolution must resolve 1 mm.
- The picture is the point: it must show whether piece 2 and 9's regions are many small patches spread over the
  face, or a few larger ones, and what shape they are.

## Acceptance criteria

1. The default change is in, with `SFS_SPACING_POLICY=fixed` still restoring today's behaviour; Proof 1 and
   Proof 2 above are both reported.
2. A per-cell table for the pipeline arms (A new default / B new default + single write / C new default + floor
   cap 0.005 + single write / D fixed-step control), pieces Juglet 1, 2, 3, 5, 7, 9 and Pot_A 01, 07, 08.
3. The pre-floor region distribution table, with the replica's re-validation verdict stated explicitly.
4. Figures exist for Juglet 2, Juglet 9 and Pot_A 07, three views each, with scale bars and mm/px.
5. Corpus and staged inputs md5 identical before and after; `/opt/sfs-pristine` recorded ABSENT.
6. Geometry deleted behind a counted record written before the delete; figures, tables, the region dumps' sidecars
   and logs kept.
7. Index rows appended, 6 fields, `verdict` and `human_note` EMPTY.

## Limits

Three jobs maximum, compute nodes only. CRLF-check every script. Do not use `xargs -n 2` over a two-field list.
Read binary PCD and varying-column PLY defensively. The unseeded 30-ray mesh stage means surface files differ
between two runs of one binary - compare normals files by md5 and surfaces by sorted point set, not by md5.

## What this cannot settle

It cannot say what the right floor is, and it cannot say whether a region is one wall or a patch of one wall -
that is the along/across test. It says what the growth actually produces, which is the thing we have never seen.
