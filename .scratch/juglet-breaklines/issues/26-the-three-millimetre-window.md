# 26: the 3 mm window that decides which points become the second surface

**Answers:** U19 (vessel level), E1 (preprocessing half)
**Blocked by:** none
**Blocks:** 25 (same file, and 25 measures the rungs this ticket changes)
**Status:** in-progress
**Working in:** chat on Thinkbook16 (2026-10-27)
**Branch:** 26-the-three-millimetre-window, in /c/PR/worktrees/sfs/26

A ticket on the *method*. It makes the last hardcoded metric distance in the surface chain a **measured,
per-piece** quantity — behind switches whose defaults reproduce today's output exactly — and measures what
the window width does to the surfaces. **Report evidence; do not declare a winner.** Judgement stays with
the lead.

## The constant, stated as a rule

`improveSurfaceBoundaryByFittingBSplineSurface` (`mesh_processing_headless.cpp:1250`) fits one spline to
**one** cluster, then walks **every point of the sherd** and admits it by two tests:

- `:1329` `if (pcl::euclideanDistance(ptOnFittedSurface, ptOnOriginalMesh) < 3 && angleDiff > 140)`
  → the point joins **this** surface;
- `:1340` `... < 3 && angleDiff < 40` → the point joins the **second** surface.

Plus the own-mode twin `improveSurfaceBoundaryByFittingBSplineSurfaceOwn` (`:1387`), whose admission is
`:1451` `if (!(dist[k] < 3)) continue;` after `:1452` `if (!(dist[k] < dist[1 - k])) continue;`.

So the window is measured **from the fitted spline of one cluster** and applied to the whole sherd, and
the **width of that window** — not the clustering — decides how far across the wall a point may be
recruited from. It is the last literal metric distance in the chain, and it is the one the conservator's
rule about hardcoded metrics is about (user rule, 2026-10-27: "any hardcoded metric measurement need to be
adaptive"). Ticket 22 made the **spacing** and the **patch/neighbour counts** adaptive; this one was left.

## What is already known, and what is not

- Wall thickness, measured on the meshes by ray casting (ticket 20): Juglet **2.09–2.90 mm**, Pot A 07
  **4.056 mm**. So 3 mm sits **between** the two: on the Juglet the opposite wall lies *inside* the window,
  on Pot A it lies *outside* it.
- Pot A yields clean wall pairs in every arm; the Juglet yields two, and only with the paper chain off
  (ticket 24, corrected ruler). That is *not* a clean "the window is too wide" story: on the pot where the
  window does reach across the wall the pairs are good at the data level, and on the pot where it does not
  reach they are good in every arm. **The direction of the effect is not known** — which is why this ticket
  measures it rather than asserting it.
- What happens when the recruited set is **empty**, or when it is the same points as the cluster, is decided
  in `finishImprovedSurface` (`:1153`) and has never been read out. It must be, because a narrow window is
  only safe if the empty case falls back cleanly.

## The rules to measure, all per piece, all printed

| id | rule |
|---|---|
| W0 | today: literal **3.0 mm** |
| W1 | `k × r`, where `r` is the fit's **own residual** — median distance from the cluster's own points to the fitted spline. `k` = 3, 5, 8. Self-scaling and not circular: it uses only the cluster being fitted. |
| W2 | `0.45 × d`, where `d` is the distance from the fitted surface to the **nearest point of any other surviving cluster**. The window may not reach into another cluster's territory. |
| W3 | `min(W1 with k = 5, W2)`. |

Every scheme is clamped to **[0.5, 6.0] mm** and the clamped-from value is printed, so a degenerate
residual cannot collapse the window or blow it up into the whole sherd. If the residual is not already
available at the admission site, compute it there from the cluster's own points to the fit — that quantity
is the measurement, not an input.

## Switches (defaults byte-identical to today)

- `SFS_WINDOW_MODE` = `literal` (default) | `residual` | `other` | `both`
- `SFS_WINDOW_K` (default 5, used by `residual` and `both`)
- `SFS_WINDOW_CLAMP_MM` (default `0.5,6.0`)
- `SFS_WINDOW_REPORT` — path for a per-piece TSV, same columns as the log line

One line per piece per fitted surface, verbatim in the log:

`[WINDOW-26] piece=<name> surface=<0|1> mode=<m> k=<k> residual_mm=<...> other_mm=<...> raw_mm=<...> clamped_mm=<...> admitted_own=<n> admitted_other=<n>`

## The grid

Two conditions decide whether a window can act at all: whether the clustering produced **two separated
clusters** to recruit across, and whether the surfaces the window produces are two real faces. So:

- **Juglet, paper chain OFF** (`SFS_PAPER_CHAIN=0` — the only arms where two separated clusters exist
  today): W0, W1(k=3), W1(k=5), W1(k=8), W2, W3 → **6 schemes × 9 pieces**.
- **Juglet, today's default** (paper chain on): W0 and W3 → **2 × 9**. This is the regression row: it says
  what a narrower window does where nothing is recruit-able.
- **Pot A, today's default**: W0, W1(k=5), W3 → **3 × 8**.

**96 cells.** Three jobs maximum: one grid, one analysis, one spare. If the grid needs to be split, split by
pot, not by scheme.

## Evidence required (report these; do not label them)

1. **A per-cell table**, one row per cell: piece, pot, paper chain, scheme, window used (mm), residual (mm),
   other-cluster distance (mm), clusters entering, clusters after merge, Surface_0 / Surface_1 point counts,
   mesh exit code. Cells that produced no pair are rows too, with the reason from the log line.
2. **The pair statistics under the corrected ruler** for every cell that has two surfaces — the step from
   each Surface_1 point to its nearest Surface_0 point, split into the component **along** that Surface_0
   point's normal and the component **across** it, plus the coincidence share at 1 micron. (The older
   mean-normal dot test is retired: it passed two coplanar patches of one shell, 0.230 mm apart.)
3. **The two reference cases**, which any scheme must not lose: Juglet piece 7 at native density and piece 5
   at the 0.6 mm step, both with the paper chain off. Report all four statistics for each, every scheme.
4. **Pot A: 8 of 8 pairs preserved?** Per piece, per scheme. A scheme that breaks Pot A is not a candidate.
5. **Defaults unchanged, proved**: with no `SFS_WINDOW_*` set, the output must be identical to the pre-change
   binary — max displacement 0.0000 mm and identical point counts on the four Juglet pieces that write pairs
   and on three Pot A pieces, as ticket 24 did it.
6. **The fallback, read out**: from `finishImprovedSurface` (`:1153`), what the code does when the recruited
   set is empty, and the counts of `improvedSurfacePointCloud` vs `..._other` per piece. Quote the source
   lines. This is the mechanism the whole ticket rests on.
7. **Inputs and the corpus unchanged**: corpus md5 list before and after (identical), and every switch
   actually in force printed per cell.
8. **Geometry deleted with a counted record** (files, bytes, per extension), surfaces and logs **kept** so the
   lead can re-measure. Three of the last four jobs deleted 664 MB, 1.2 GB and 3.3 GB of stage geometry.
9. **Index rows** appended with `verdict` and `human_note` **empty**.

## Acceptance criteria

- 96 cells present, every one with a status row; any cell that did not run is named with the job id and its
  `sacct` state.
- Nothing outside `.scratch/` changed except `mesh_processing_headless.cpp`, and that file compiles and its
  defaults reproduce today (item 5).
- The corrected-ruler statistics exist for every cell with two surfaces, computed by the script left in the
  ticket branch, not by hand.
- The two reference cases and Pot A's 8 of 8 are answered piece by piece, not as a total.
- Item 6 answered from the source, with line numbers.
- The corpus and the frozen inputs are byte-identical before and after.

## What this cannot settle

- **One vessel.** Nine Juglet sherds and two reference pairs; a scheme that helps there is a lead.
- **It cannot create a pair where the clustering never separated two clusters.** With the paper chain on,
  no arm has two walls to recruit across, so a window change is bounded by that and the report must say so
  rather than reading "still one surface" as "the window is wrong".
- **Wall thickness is a mesh measurement** on millimetre meshes; the window acts on the downsampled cloud, so
  the two are compared as orders of magnitude, not as exact numbers.
- **It does not test a window that varies along the surface.** One width per cluster per piece; a local,
  curvature- or gap-driven width is a later ticket if the fixed-per-piece version shows an effect.
