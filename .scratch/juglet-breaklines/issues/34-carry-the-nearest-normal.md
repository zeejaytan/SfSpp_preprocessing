# 34: Carry the nearest normal, not an average — does the growth then grow a face?

**Status:** in-progress
**Working in:** chat on Thinkbook16 (2026-10-27)
**Branch:** 34-carry-the-nearest-normal, in /c/PR/worktrees/sfs/34
**Answers:** U19, E1
**Blocked by:** none
**Blocks:** none

## Why this ticket exists

Ticket 33 built `SFS_NORMAL_SOURCE=input`, which carries the normals the scan already stores through the
sampling step. It made the measurement that matters and it failed on the vessel: at the shipped 0.6 mm
spacing the carried normals sit **3.87-9.95°** from the mesh while the pipeline's own sit **3.39-9.01°** — worse
on all five Juglet pieces. But in the same grid, where the sampling radius shrank to each piece's own spacing
and the carry ball shrank with it, the same carry gave **1.79-3.46°**, better than the pipeline achieves
anywhere. On Pot A the carry was mildly better at both settings (0.71 → 0.69 → 0.59°).

The mechanism is the **averaging ball**, not the source. The carry averages unit normals inside one sampling
radius; on a surface folding over 0.7-5.3 mm (ticket 32), a 0.6 mm ball mixes directions across the fold and
across the broken edge, and the average is smeared. The untested cell is therefore obvious and cheap: carry
each sampled point the normal of its **nearest** source point, with no averaging, at the shipped spacing.

The question it decides is the one ticket 33 could not: with honest normals, does the growth's 3.4° criterion
grow a face on sherd 2 or sherd 9 — the two sherds that give nothing (9) or only two 12 mm patches (2)?

## What to build

One switch, defaulting to today:

- `SFS_NORMAL_CARRY=mean|nearest` (default `mean`), effective only when `SFS_NORMAL_SOURCE=input`. In
  `nearest` mode each sampled point takes the unit normal of its nearest source point verbatim: no averaging,
  no renormalisation other than to unit length, no MST orientation, sign preserved. Points with no source
  neighbour are counted and reported, never silently filled — at the shipped spacing every sampled point lies
  on the source cloud, so **missing must be 0**; if it is not, the nearest lookup is broken and the run says so.
- Extend the existing `[NORMAL-33]` line with `carry=` (mean|nearest) and `source=`. Nothing else about the
  line changes.

No other behaviour may change. `SFS_NORMAL_SOURCE` unset must still give today's output exactly.

## Arms and cells

Pieces: Juglet 1, 3, 5, 7 (controls — 7 is the only piece that writes a pair today, 5 gets two regions under
ticket 33's input arm, 1 is the largest), Juglet 2 and 9 (the target), and all **eight Pot A pieces** (the
control pot, where 8 of 8 two-surface is the standing bar). Three arms:

| arm | normals | notes |
|---|---|---|
| A | reestimate (today) | reference |
| A2 | reestimate, second pass | measures the run's own spread |
| B | input, `SFS_NORMAL_CARRY=nearest` | the cell under test, everything else at the shipped defaults |
| C | as B + `SFS_SINGLE_CLUSTER=write` | so a one-region outcome on 2 or 9 is written and measurable instead of silent |

## The measurement that decides it

Per piece and arm:

- median folded angle of the cloud's normals to the nearest mesh vertex normal — the same instrument ticket 33
  used (`stage33/` carried table), so the numbers are comparable to 8.10 (A) and 9.44 (B, mean carry) on
  piece 2. **This is the first row of the answer**: if nearest carry does not land near the 0.41-1.64° the input
  clouds themselves carry (ticket 32), the carry is not doing what it says and the rest is moot.
- region count, sizes before and after the merge, and every merge line the binary prints.
- for every surface written: point count, bbox diagonal, **2 mm coverage**, median folded angle to the mesh;
  and where two surfaces exist, the corrected pair statistic (nearest-point vector split along / across the
  Surface_0 normal, coincidence at 1 µm). A real pair on Pot A sits at 3.5-7.1 mm along and 0.24-0.27 across;
  every Juglet "pair" so far has been 4-12 mm across, i.e. patches in different places.

## Acceptance criteria

1. The switch exists, defaults to `mean`, and is printed per cell in `run.json` and in the `[NORMAL-33]` line.
2. **Defaults proof**: with the switch unset, `<piece>_SampledWithNormals.ply` is byte-identical and
   sorted-point-set identical to the pre-change binary (12 or more comparisons). Do not ask for byte-identical
   *surface* PLY — ticket 33 showed they differ even between two runs of one binary (uninitialised curvature,
   row order, 1-3 points crossing between surfaces).
3. Nearest mode is proven to be nearest: `missing=0`, `carried=npts`, and the deviation from the pipeline's
   PCA normal is larger than in mean mode on the folding pieces (a nearest carry that matches the mean carry
   to the digit means the switch did nothing).
4. Every arm x piece cell reports exit code, region counts, region sizes, merge lines, and the surface
   measurements above.
5. Pot A keeps **8 of 8** two-surface pieces in every arm, with along 3.5-7.1 mm and across inside
   0.13-0.27 mm, coincidence 0.0000; a piece that loses its pair is reported, not explained away.
6. Corpus and staged inputs md5 identical before and after; `/opt/sfs-pristine` recorded ABSENT.
7. Geometry outside the written surfaces deleted with a counted record written **before** the delete; surfaces,
   logs and tables kept.
8. Index rows appended with `verdict` and `human_note` EMPTY.
9. No verdict, no merge, no write to `intent/`, no tracked file touched except `mesh_processing_headless.cpp`
   and `.scratch/juglet-breaklines/stage34/`.

## Limits

Three jobs maximum, compute nodes only. CRLF-check every script before submitting (two grids have died on
`set: pipefail: invalid option name`, one on a rendered brace expansion). If the pipeline needs any change
beyond this one switch, stop and report.

## What this cannot settle

It cannot show the normals are the whole story even if sherd 2 or 9 gives a face: the growth, the merge and the
write gate all still act on whatever regions appear. It says nothing about pieces 4, 6 and 8, which are not in
the grid, and nothing about whether the same carry helps another vessel. And if the nearest carry lands at
0.4-1.6° and the growth still returns fragments, then the honest conclusion is that the angle test is not the
only thing wrong with these two sherds — which is what the fragment-merge question would then become.
