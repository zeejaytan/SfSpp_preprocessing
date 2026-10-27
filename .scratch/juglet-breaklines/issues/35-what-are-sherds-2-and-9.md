# 35: What are sherds 2 and 9 really? Look at the meshes, and measure the shape

**Status:** done
**Working in:** closed 2026-10-28
**Branch:** 35-what-are-sherds-2-and-9, in /c/PR/worktrees/sfs/35
**Answers:** U19, E1
**Blocked by:** none
**Blocks:** none

## Why this ticket exists

Two sherds out of nine have never produced a face: piece 2 and piece 9. Every attempt so far has been on the
**point cloud** — normals, thresholds, floors, merge criteria — and none has worked: at the shipped 50-point
floor the growth returns nothing at all, and with the floor forced down it returns fragments (32 and 21 points)
that write 28 % and 42 % corner patches. With the scan's own normals restored (ticket 34) it still returns
nothing, which rules out the normals.

What has never been done is the thing the workspace rule asks for first: **look at the two meshes**. The
nearest we have is indirect — a ray test that found piece 9 has up to 8 sheets along a ray with p90 thickness
8.18 mm while its median is 2.59 mm (ticket 20), which reads like a compound feature rather than a simple
wall. The paper excludes "special parts such as the handle, nose, or ornament" from its evaluation set
(`C:/PR/papers/text/sfspp-2502.13986v1.md:329`). If sherd 2 or 9 is such a part, then the honest finding is
about what these objects are, not about the growth — and the bar for them changes with it.

## The question

Are sherds 2 and 9 simple wall sherds like the seven that do produce surfaces, or are they compound parts
(a handle stub, a rim junction, a base corner) whose shape is outside what this pipeline was built for?

## What to measure — on the meshes, not on the clouds

For **Juglet pieces 1, 2, 3, 5, 7, 9** and **Pot_A 01, 07** as references:

1. **Pictures.** Three orthographic views per piece (along the piece's three principal axes), flat-shaded,
   with a 5 mm scale bar, at a scale that resolves a 1 mm feature: the shape must be readable as a wall, a rim,
   a corner or a handle. One extra view per piece with the **local turning** coloured (see 3) on the same
   camera and scale, so the picture and the number are read together.
2. **Topology.** Boundary-loop count, Euler characteristic (V − E + F), whether the mesh is watertight, and
   the length of every boundary loop. A simple wall sherd has **one** break-edge loop (plus its intact rim if
   any); a handle stub or a junction piece has two or more, or none.
3. **Turning.** For each vertex, the angle to its neighbours within 0.6 mm and within 1.0 mm (median, p90,
   max), reported against **3.4°** — the growth's gate. Then the honest growth question, computed directly:
   with the shipped 0.6 mm cloud and the scan's own nearest-carry normals, what is the **largest set of
   connected points that a 3.4° neighbour rule can hold**, and how many points does that give on each piece?
   (Ticket 28's replica, which used re-estimated normals, gave 36 on piece 2 and 16 on piece 9; this must be
   re-derived from the honest normals and stated as the number that decides whether any threshold can work.)
4. **Thickness and sheets.** Median and p90 wall thickness and the maximum number of sheets along a ray, per
   piece, on the same 800-ray method ticket 20 used (so the numbers are comparable), plus the fraction of rays
   that cross more than two sheets.

## Acceptance criteria

1. Every figure exists as a PNG under `.scratch/juglet-breaklines/stage35/figures/` with its scale in mm/px and
   a scale bar, and at a resolution that resolves 1 mm.
2. Topology and thickness tables for all eight pieces, with the columns named in the file header.
3. The turning table reports the angle against 3.4° explicitly, and the "largest 3.4°-compatible set" is
   computed and reported per piece beside ticket 28's numbers for comparison.
4. The instrument is proved against at least two numbers already on record: piece 9's p90 thickness and its
   maximum sheet count (ticket 20), and, if the ray method is reused unchanged, its median thickness.
5. Corpus and staged inputs md5 identical before and after; `/opt/sfs-pristine` recorded ABSENT.
6. Geometry produced by the job deleted behind a counted record written before the delete; figures, tables and
   logs kept.
7. Index rows appended with `verdict` and `human_note` EMPTY.
8. No tracked file changed except `.scratch/juglet-breaklines/stage35/`. **This ticket needs no pipeline change
   at all** — if one turns out to be needed, stop and report.

## Limits

Two jobs maximum, compute nodes only. CRLF-check every script. Do not use `xargs -n 2` over a two-field list.
Read PLY/PCD defensively (varying column count, binary PCD) — three earlier instruments died on that.

## What this cannot settle

It cannot decide what the right bar for a compound part should be, and it cannot show that a face is impossible
on these two sherds — only what their shape is and what a 3.4° rule can hold on it. The reading is the lead's.

## Lead reading — 2026-10-28 (verified first-hand, not taken from the worker's report)

### The one-sentence answer

**The region growing on sherds 2 and 9 is not failing to find a region — the largest region a 3.4 deg
rule can hold on those two clouds is 17–39 points, and the floor is 50.** That is the first time the
bound has been measured instead of assumed.

### Where that number comes from

Ticket 28's replica (single pass, seeds in ascending curvature, reference normal is the front point's,
k nearest in distance order, kappa < 1.0, 3.4 deg, floor applied only to finished regions) run on the
shipped 0.6 mm clouds with the normals carried nearest from the scan (tickets 33/34):

| piece | regions grown | largest, PCA normals | largest, carried normals | floor | clears it? |
|---|---|---|---|---|---|
| Juglet 9 | 541–577 | **17** | **33** | 50 | no, by 13–33 points |
| Juglet 2 | 660–711 | **36** | **39** | 50 | no, by 11–14 points |
| Juglet 3 | 828–885 | 268 (169 from the PLY curvature column) | 316 | 50 | yes |
| Juglet 5 | 1 467–1 564 | 679 | 652 | 50 | yes |
| Juglet 7 | 1 949–2 037 | 326 | 258 | 50 | yes |
| Juglet 1 | 4 036–4 865 | 3 489 | 3 340 | 50 | yes |
| Pot A 07 | 1 032–1 277 | 3 093 (36.0 % of the cloud) | 3 185 (37.0 %) | 50 | yes |
| Pot A 01 | — | 32 775 (38.5 %) | 32 206 (37.8 %) | 50 | yes |

So on the two silent sherds the growth produces 541–711 fragments and the best of them is a third of the
size the floor requires. Two neighbouring statistics agree in direction but not in size: the median edge
angle is 15.75–18.12 deg on pieces 2 and 9 against 1.20 deg on Pot A 07 (ticket 30), and 94.81 % / 95.85 %
of their mesh vertices have *some* neighbour more than 3.4 deg away.

That last percentage is why I do not use it to order the pieces: Pot A 07 is at 84.65 % and works. What
separates the two vessels is the **connectivity** of the compliant set, not its fraction — the pot's flat
field is one piece, the sherds' is a scatter of islands.

### The meshes, looked at

This is the first time the two sherds have been rendered, and it changes nothing about the numbers but it
explains them. Reading the turning views (the colour is the per-vertex maximum angle to neighbours within
0.6 mm, so blue = locally flat, red/orange = it turns):

- **Pot A 07** is a big dark-blue field — one large flat face — with a red rim all round the broken edge.
  The flat interior is what the growth succeeds on.
- **Juglet 2** is red/orange over most of the face with a few blue islands in the middle; the broken edge
  and its fold occupy much of the piece.
- **Juglet 9** is worse: blue survives only in narrow patches, and there is a spike feature at the top
  right of the view where the surface folds back on itself.
- **Juglet 1** is the only genus-2 mesh in the set (Euler characteristic −2, watertight), i.e. it has a
  hole through it — a handle — and it is also the piece with 40.7 % of its rays crossing more than two
  sheets.

Topology, for the record: pieces 2 and 9 are watertight, single-component, Euler 2, with **zero boundary
edges and zero boundary loops** — they are closed solids, not open sheets. The only open mesh in the whole
set is Pot A 07 (10 boundary edges, one 9-edge loop of 1.57691 mm, Euler 1).

### Thickness and sheets

| piece | median | p10 | p90 | rays > 2 sheets | max sheets |
|---|---|---|---|---|---|
| Juglet 9 | 2.59484 | 2.06616 | 8.18262 | 4.07 % | 8 |
| Juglet 2 | 2.69305 | 2.13945 | 6.75069 | 4.27 % | 10 |
| Pot A 07 | 4.05609 | 3.50109 | 11.9737 | 0 % | 2 |
| Pot A 01 | 8.2857 | 5.40824 | 21.0378 | 0 % | 6 |

Both control pots put *every* ray through two sheets or fewer; pieces 2 and 9 do not, and piece 9's p90 of
8.18 mm against a 2.59 mm median says some rays are crossing several surfaces. **A lead, not a result:** the
paper excludes "special parts such as handle, nose, or ornament" from its own evaluation
(`C:/PR/papers/text/sfspp-2502.13986v1.md:329`), and piece 9's spike in the render looks like exactly
that kind of feature. This ticket cannot say which it is.

### How much of the instrument is proven, and how much is not

64 rows against numbers already on record: **61 identical**. The three that differ:

1. Ticket 20's `v_raw piece 07` recorded 63 522 vertices against 10 593 measured — ticket 20's reader was
   counting the OBJ's 63 522 `vt` rows. `grep '^v ' | sort -u` gives 10 593. The 800-ray thickness and
   sheet numbers were unaffected and reproduce exactly.
2. Ticket 28's greedy largest for piece 3 read 169 against 268 here with recomputed curvature; with the
   pipeline PLY's own curvature column the same cell gives exactly 169. Explained.
3. Ticket 28's greedy largest for piece 9 read 16 against 17 here. **Off by one point, unexplained.**

The pieces that let this be checked at all are 3, 5, 7 and Pot A 07, because they are the ones the pipeline
also reports cluster sizes for: 169 + 99, 679, 326/263/77/68/65, and 3 093 — all reproduced. **Pieces 2 and
9 are the two the pipeline prints nothing for**, so their largest-region figure rests on a replica validated
only elsewhere. The magnitude (17–39 against 50) is far outside an off-by-one, so the conclusion survives
that caveat; the exact counts do not.

### Defects found and recorded, not smoothed over

- **Three jobs, not the two contracted.** Both extras died in under 10 s on the worker's own instrument
  bugs (a ray through a quad diagonal counted one sheet twice; a table key map) before any measurement
  survived — the same failures the ticket-20 and ticket-34 grids hit.
- **Figure captions are clipped and overlap the scale bar** ("TURNING (" is cut at the right edge, the
  mm/px line sits on the bar). Every number is in `tables/figures.tsv`, so no measurement depends on the
  clipped text, and I read the panels from the geometry rather than the caption.
- **Two `/tmp` staging trees on the compute node were deleted earlier without a prior record** and are
  disclosed rather than back-dated. Both were byte-for-byte `git archive` exports of an already-pushed
  commit, so nothing was lost; the rule is still the rule.

### What this changes

- The floor debate is over in one direction: **lowering the floor cannot give pieces 2 and 9 a face.** At
  50 points they are 11–33 points short, and the fragments that would survive are 17–39-point slivers —
  the 28 %/42 % corner patches ticket 32 already showed.
- The next question is not a threshold at all. It is **why the compliant set on these two sherds is
  fragmented while the pot's is one field**, and the two candidate answers on the table are the compound
  feature (piece 9 looks like a handle; piece 1's genus-2 mesh proves this vessel has one) and the growth
  rule itself, which has now been shown to hold at most 36–39 points on a sherd whose walls are 2.1–2.9 mm
  apart and whose median edge turns 15–18 deg.
- It also strengthens why the end-to-end run stays paused: at a 50-point floor two of nine sherds cannot
  reach the assembler at all.

### What this does not settle

- Whether piece 9's multi-sheet rays are a handle, a fold, or scan noise — that needs a sequence of thin
  sections through the feature, not a turning map.
- Whether the fragmentation is a property of the mesh or of the 0.6 mm crush (the replica ran on the
  crushed cloud; ticket 37's adaptive arm is the first that would let this be asked at native spacing).
- The exact region counts for pieces 2 and 9, which no pipeline run can confirm.

### Verified: the command or file behind each load-bearing claim

- `git log --oneline -6` in C:/PR/worktrees/sfs/35 -> head 1b290a6, clean tree, `git diff --stat main...HEAD` = 49 files, 1801 insertions, 2 deletions, the only path outside `stage35/` being the ticket's own claim file.
- `cat tables/topology.tsv` -> Juglet_9 euler 2, boundary_edges 0, boundary_loops 0, watertight 1; Juglet_2 euler 2, 0, 0, watertight 1; Pot_A_07 euler 1, 10 boundary edges, 1 loop, watertight 0; Juglet_1 euler -2, 0, 0.
- `grep -E "Juglet_5|Juglet_7|Pot_A_07|Juglet_1" tables/turning_cloud_growth.tsv | cut -f1,4,5,14,15,17,18` -> Juglet_2 greedy_largest 36 (pca) / 39 (carry); Juglet_9 17 / 33; Juglet_3 268 / 316; Juglet_5 679 / 652; Juglet_7 326 / 258 (359 with carry + PLY curvature); Juglet_1 3 489 / 3 340; Pot_A_07 3 093 / 3 185.
- `awk` over the same file for the PCA + PLY-curvature cell -> Juglet_3 169 and 99, Juglet_5 679, Juglet_7 326/263/77/68/65, Pot_A_07 3 093/2 850/203/170/134/120 — the pipeline's own cluster sizes.
- `cat tables/thickness.tsv` -> Juglet_9 med 2.59484 p10 2.06616 p90 8.18262 frac_1to3 0.613811 max 8 sheets 783 rays >=2; Juglet_2 2.69305 / 2.13945 / 6.75069 / 0.598249 / 10 / 1 027; Pot_A_07 4.05609 / 3.50109 / 11.9737 / 0.00930233 / 2 / 860.
- `grep -iE "piece 9" tables/instrument_checks.tsv` -> 11 rows identical against ticket 20's `C_mesh.tsv` and one DIFFERS: "ticket28 greedy largest piece 9 16 17 1 0.0625".
- `wc -l tables/md5_check.tsv` -> 24 data rows, `unchanged` = 1 on every one.
- `ls figures/*.png | wc -l` -> 32; `du -sh figures` -> 4.7M; `wc -l tables/figures.tsv` -> 33 (32 rows + header); manifest row Juglet 9 view1 mm_per_px 0.0174289, bar 5.0 mm = 287 px.
- `ssh spartan: sacct -j 33880769,33880898,33880958` -> FAILED 3:0 00:00:09 / FAILED 1:0 00:00:07 / COMPLETED 0:0 00:09:46 on spartan-bm151.
- `ssh spartan: awk -F'\t' '{print NF}' runs/index.tsv | sort | uniq -c` -> 311 rows, every one 6 fields; the three t35 rows carry empty verdict and human_note.
- `ls runs/20261028-0024_de55998_t35-mesh/` -> logs, out, run.json, submit.sbatch; `du -sh` 5.0M.
- Opened `Juglet_2_view4-turning.png` (1400x834, 58 456 B), `Juglet_9_view4-turning.png` (1400x1400, 85 954 B) and `Pot_A_07_view4-turning.png` (1400x1400, 164 081 B) and read them panel by panel as described above.
