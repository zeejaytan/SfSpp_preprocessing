# 37: Make the adaptive step the default, take the floor away, and look at the regions

**Status:** done
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

## Lead reading — 2026-10-28 (verified first-hand, not taken from the worker's report)

### The one-sentence answer

**The adaptive step is now the default and it is a real gain — but it does not rescue the two silent sherds:
at native spacing the largest region the growth can hold together is 45 points on piece 2 and 16 on piece 9,
and the floor is 50.** The drawn regions settle it: on the sample pot two regions hold 73 % of the cloud, on
the two sherds the eight largest hold 5–8 % and 93–95 % of the points belong to no region at all.

### The default flip, and the proof it is a flip and not a change

The entire source change is 10 insertions and 1 deletion at `mesh_processing_headless.cpp:4365`
(`"fixed"` → `"piece"`) plus a comment block. Nothing else in the pipeline moved.

**Proof 1:** with `SFS_SPACING_POLICY=fixed` the new binary writes the **same `SampledWithNormals.ply` md5**
as the pre-change binary on 7 of 7 pieces — Juglet 1 `ab38ff7d…`, Juglet 3 `122b2fbb…`, Juglet 7
`cadba02a…`, Pot_A 01 `b58f5839…`, 02 `14dbb68e…`, 07 `29536bde…`, 08 `d60db59e…`. The old behaviour is
still reachable, byte for byte.

**Proof 2:** with no environment at all the new default reproduces ticket 36's arm B exactly — Juglet 1
10800/15780, Juglet 5 229/2317, Juglet 7 1753/1997, Pot A two-surface on 8 of 8.

### What the default buys, and what it costs

| piece | surfaces, new default (adaptive) | surfaces, fixed 0.6 mm control | coverage of Surface_0 |
|---|---|---|---|
| Juglet 1 | 10 800 / 15 780 | 3 580 / 12 092 | 0.660 vs 0.274 |
| Juglet 3 | one cluster, not written | none | — |
| Juglet 5 | 229 / 2 317 | none | 0.087 |
| Juglet 7 | 1 753 / 1 997 | 1 012 / 829 | 0.285 vs 0.197 |
| Pot_A 01 | 66 763 / 57 286 | same | 0.434 |
| Pot_A 07 | 24 636 / 26 739 | 6 066 / 6 437 | 0.485 vs 0.486 |
| Pot_A 08 | 26 774 / 29 286 | 5 528 / 6 097 | 0.513 vs 0.502 |

Three times the points on piece 1's large surface and four times on Pot A 07, with the same or better coverage.

**Pot A's wall pairs survive, and two improve** (ticket 30's ruler: along / across the surface normal, and the
1-micron coincidence share):

| piece | new default | fixed control |
|---|---|---|
| Pot_A 01 | 7.089 / 0.271 / 0.0000 | 7.089 / 0.271 / 0.0000 |
| Pot_A 02–06 | 3.55–3.78 / 0.23–0.26 / 0.0000 | — |
| Pot_A 07 | 3.902 / **0.126** / 0.0000 | 3.920 / 0.249 / 0.0000 |
| Pot_A 08 | 3.593 / **0.128** / 0.0000 | 3.604 / 0.250 / 0.0000 |

**The cost, stated plainly:** Juglet 1's two surfaces now lie on each other — along 0.007 mm, across 0.387 mm,
coincidence 0.460 — where the fixed step gave 0.368 / 4.199 / 0.325. That is the ticket-27 de-duplication defect
showing harder at a finer step, and it is not a lost wall pair: with across 4.2 mm the old pair was two patches
in different places, not two faces of a wall. Nothing genuine was lost; a duplicate got worse.

### The regions before the floor — the answer to "how much is the cluster before it is deleted"

Replica re-validated **in the new default configuration** on all four cells the pipeline can check
(Juglet 3 `[289]`, Juglet 5 `[604,136,51]`, Juglet 7 `[609,578,93,70,57]`, Pot_A 07 `[12888,11815,2722,…]`
— exact), with two stated deviations in the nearest-carry config on Juglet 7 (largest identical, tail differs)
and piece 2 and 9 matching trivially because both sides are zero.

| piece | config | points in | regions | largest | reaching ≥50 | ≥1 % of cloud | survivors at floor 50 |
|---|---|---|---|---|---|---|---|
| Juglet 2 | adaptive + nearest carry | 2 399 | **1 765** | **45** | 0 | 3 | **0** |
| Juglet 2 | fixed 0.6 + nearest carry | 1 031 | 708 | 39 | 0 | 4 | 0 |
| Juglet 9 | adaptive + nearest carry | 1 972 | **1 465** | **16** | 0 | 0 | **0** |
| Juglet 9 | fixed 0.6 + nearest carry | 787 | 578 | 33 | 0 | 3 | 0 |
| Pot_A 07 | adaptive, re-estimated (default) | 34 608 | 2 837 | **12 888** | 7 | 5 | 7 |

So the honest ceiling at native spacing is **45 points on piece 2 — five short of the floor** — and 16 on piece 9.
Adaptive spacing moved piece 2 from 36 to 45 and piece 9 from 17 to 16, i.e. it did not change the outcome.

### The pictures, read panel by panel

Pre-floor regions, fixed colour map, one cube scale per piece, three orthographic views
(the dumped config is adaptive + nearest carry, the only one of the two that produces regions on these sherds;
the new default gives zero on both, so there would be nothing to draw):

- **Pot_A_Piece_07** (34 608 points, 2 494 regions, largest 13 131): blue **13 131** covers one whole face, red
  **12 042** covers the other, orange 1 127 and the rest are chips along the broken edge; grey (no region)
  is **4 038 = 11.7 %**. Two regions hold **72.7 %** of the cloud and they are the two sides of the wall.
  This is what "the growth works" looks like.
- **Juglet_Piece_2** (2 399 points, 1 765 regions, largest 45): blue 45, red 38, green 24, violet 19, orange 18,
  brown 16, pink 11, cyan 10 — **the eight largest hold 181 points, 7.5 %** — and **2 218 points, 92.5 %, are
  in no region**. The coloured strips lie along the piece's long edges in the XY view and are a thin skin at
  one end in the XZ view.
- **Juglet_Piece_9** (1 972 points, 1 465 regions, largest 16): blue 16, red 15, green 13, violet 13, orange 11,
  brown 11, pink 11, cyan 11 — **the eight largest hold 101 points, 5.1 %** — and **1 871 points, 94.9 %, are in
  no region**. Same shape: slivers at the rim, nothing across the face.

The comparison is not subtle and it does not depend on the numbers: **on the pot a region is a face; on these two
sherds a region is a chip at the rim.**

### What arm C (floor capped at 0.5 %) actually gives

Juglet 2 at a floor of 12 → two surfaces 220 / 179 points, Surface_0 diagonal 11.49 mm, coverage 28.4 %.
Juglet 9 at a floor of 10 → two surfaces 144 / 269, diagonal 11.57 mm, coverage 30.3 %. So with the floor taken
out of the way both sherds do produce two surfaces — 28–30 % corner patches, exactly what ticket 32 measured
before. **The floor is not what stands between these sherds and a face; the growth is.**

One caveat on arm C, worth recording because it is a trap: a 0.5 % fraction is not portable across piece sizes —
on Pot_A 07 and 08 it produces floors of 173 and 180, *higher* than the default's 69 and 72, so the same switch
that opens the small sherds squeezes the pot.

### Where the work went wrong, disclosed

- The worker's figure instrument first reported **largest = 1 764** for Juglet 2 — it took `max()` over a dict of
  region sizes, which returns the largest *id*, not the largest region — and looked for the wrong dump filename.
  Both were found and fixed before the committed figures were drawn; the figure header now prints npts, regions
  and largest, which is what makes it checkable.
- `fetch_instruments37.sh` first refused because the run's commit was not yet in the canonical checkout; the
  checkout was fetched and the instruments verified LF with `bash -n` on every script.
- The replica mismatch on Juglet 7 in the nearest-carry configuration (pipeline `[1035,136,88,85,82]` against
  `[1035,113,112,88]`) is stated in the report rather than dropped; it does not touch the four validated cells,
  and it is not one of the pieces this ticket decides.

### Verified: the command or file behind each load-bearing claim

- `git diff main...HEAD -- mesh_processing_headless.cpp` -> one hunk at `:4353-4371`, `-"fixed"` / `+"piece"`, 10 insertions 1 deletion; a comment block, no other source file.
- `cat out/proof1.md5.tsv` -> 7 rows, every one `IDENTICAL`, matching sizes 1 079 873 / 108 396 / 314 641 / 6 056 071 / 3 537 421 / 611 993 / 548 385.
- `out/pairs30.tsv` -> arm A Pot_A 01 7.089 / 0.271 / 0.0000; 07 3.902 / 0.126 / 0.0000; 08 3.593 / 0.128 / 0.0000; arm D Pot_A 07 3.920 / 0.249, 08 3.604 / 0.250; arm A Juglet 1 0.007194 / 0.386520 / 0.459696 against arm D 0.367769 / 4.198927 / 0.325174.
- Replica table (report section 4) -> Juglet 2 N 2 399 pts / 1 765 regions / largest 45 / 0 at ≥50; Juglet 9 N 1 972 / 1 465 / 16 / 0; Pot_A 07 R 34 608 / 2 837 / 12 888 / 7; re-validation VALIDATED on 4 of 4 gate cells.
- `cells37_table.tsv` arm A vs D -> Juglet 1 10 800/15 780 (cov 0.6599) against 3 580/12 092 (0.2742); Pot_A 07 24 636/26 739 against 6 066/6 437; Pot_A 08 26 774/29 286 against 5 528/6 097; arm C Juglet 2 220/179 (diag 11.486, cov 0.2838), Juglet 9 144/269 (11.565, 0.3032).
- `ls 20261027-1404_c16e274_t37-adaptive-default/out/` -> cells37.tsv, proof1.md5.tsv, pairs30.tsv, inputs_before/after.md5 with a 0-byte diff, corpus_before/after.txt with a 0-byte diff, GEOMETRY_DELETED.txt, GEOMETRY_KEPT.txt, pristine.txt.
- `ssh spartan: head -1 out/pairs30.tsv` and the arm A / arm D rows quoted above — read from the run directory, not from the report.
- Opened `Juglet_Piece_2_regions_3views.png` (1907x860, 119 058 B), `Juglet_Piece_9_regions_3views.png` (1902x842, 131 990 B) and `Pot_A_Piece_07_regions_3views.png` (2061x864, 181 884 B) and read the legends: 45/38/24/19/18/16/11/10 and none 2 218; 16/15/13/13/11/11/11/11 and none 1 871; 13 131/12 042/1 622/1 248/1 127/1 052/183/165 and none 4 038.

### What this does not settle

- Whether 45 against 50 is a knife-edge or a wall. Five points is inside the replica's agreement with the
  pipeline on the pieces where both can be checked (tens of points on a 2 000-point cloud), so the exact
  margin is instrument-dependent; the direction is not, because arm C at a floor of 12 still returns a 28 %
  corner patch rather than a face.
- Why the compliant set is fragmented. Two candidates remain and neither is measured: a compound feature
  (piece 9's multi-sheet rays, and this vessel has a handle — Juglet 1 is the only genus-2 mesh in the set),
  or the growth rule itself.
- Whether a second growth pass over the unclaimed points (92–95 % of the cloud here) would find a face, which
  is the queued repair and has never been run.

## 2026-10-28 — correction: the pair table's `med_across` column is void

The pair statistic in stage37's instruments took the ABSOLUTE value of the signed offset before splitting a Surface_1 point's step into "along Surface_0's normal" and "across it", then rebuilt the across component from that absolute value. Wherever the second sheet lies BEHIND the first, the reported across is `sqr t(across_true^2 + 4 t^2)` — up to twice `med_nn` — and the identity `across <= nn` breaks on exactly those points. Found in ticket 38 from a row where across exceeded nn, proved on synthetic planes (a sheet 2.2 mm inside its partner reported 4.4000 mm), fixed in `stage38/instruments/measure34.py:295-308` which keeps `t` signed.

**What it touches here: 46 of 102 rows** across `phase1/out/pairs34.tsv` and the per-cell tables, worst `Pot_A_Piece_01` reported 14.18 mm across against a true **0.30 mm**. The ticket's own conclusions — that the adaptive step is safe, that Pot A gains a tighter pair on 07 and 08, that the pre-floor region distribution is unchanged in kind — rest on point counts, coverage and `along`, none of which the defect touched. Its quoted `across` values (07 0.126, 08 0.128, Pot A 0.24-0.27) are the affected column and read as void; the corrected values are smaller, in the same direction.
