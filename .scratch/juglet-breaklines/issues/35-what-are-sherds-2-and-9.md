# 35: What are sherds 2 and 9 really? Look at the meshes, and measure the shape

**Status:** ready-for-agent
**Working in:** chat on Thinkbook16 (2026-10-27)
**Branch:** —
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
