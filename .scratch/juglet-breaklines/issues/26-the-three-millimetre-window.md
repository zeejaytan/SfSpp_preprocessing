# 26: the 3 mm window that decides which points become the second surface

**Answers:** U19 (vessel level), E1 (preprocessing half)
**Blocked by:** none
**Blocks:** 25 (same file, and 25 measures the rungs this ticket changes)
**Status:** done
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

## Lead reading — 2026-10-27 (verified first-hand, not taken from the worker's report)

**One sentence.** Shrinking the admission window from the literal 3 mm to the 0.5 mm clamp floor changes which
points land on each surface, but it does not produce a single new genuine Juglet wall pair, and it does not
disturb Pot A — so the window is neither the repair nor the thing that merges the walls.

### What the window does

| cell | window (s0/s1) | points S0/S1 | through mm | across mm | coincidence | a wall pair? |
|---|---|---|---|---|---|---|
| Juglet 1, today (paper chain on) | 3.0 / 3.0 | 3580 / 12092 | 0.368 | 4.199 | 0.325 | no — two patches in different places |
| Juglet 1, other-mode | 0.5 / 0.5 | 11894 / 505 | 1.574 | 4.757 | 0.000 | no — same |
| Juglet 5, paper off, any scheme | 3.0 or 0.5 | 1845 / 300 → 1818 / 174 | 2.276 → 2.200 | 0.361 → 0.334 | 0.013 → 0.000 | **yes**, and it survives every scheme |
| Juglet 7, native, any scheme | 3.0 or 0.5 | 4204 / 2638 → 4141 / 1708 | 3.140 → 3.226 | 0.306 → 0.288 | 0.000 | **yes**, and it survives every scheme |
| Pot A 07, today | 3.0 / 3.0 | 6066 / 6437 | 3.920 | 0.249 | 0.000 | **yes** |
| Pot A 07, residual or both | 0.5 / 0.5 | 6048 / 6423 | 3.927 | 0.247 | 0.000 | **yes**, unchanged |

A pair counts as genuine only when the two surfaces are the two faces of one wall: displaced **through** the
normal by about the wall thickness (2–3 mm here, measured from the meshes) with almost nothing **across** it
and no coincidence. By that test the grid produces exactly the two Juglet pairs ticket 24 found, in the arms
where the paper chain is off, and no others. Every other Juglet row has an across value of 1.7–6.9 mm, which
means the two "surfaces" are patches at different places on the sherd, not the two faces of a wall — the
window moved the patches around without ever cutting a wall in two.

Pot A is the safety check and it holds: **8 of 8 pieces keep a clean wall pair under all three schemes**, with
through 3.55–7.09 mm, across 0.24–0.27 mm and coincidence 0.0000 in every one of the 24 Pot A cells. Point
counts move by a few tens (Pot A 07: 6,066/6,437 → 6,048/6,423). Shrinking the window is safe on the sample.

### Two defects of this experiment, found in its own tables

- **The clamp floor swallowed the alternatives.** Of the 90 non-literal width values the grid computed, **79
  sit exactly on the 0.500000 mm floor** (raw widths 0.02–0.40 mm, because the fitted spline's own residual is
  0.02–0.05 mm on the Juglet). So the six schemes exercised **two** distinct widths — 3.0 mm (48 values) and
  0.5 mm (79) — plus eleven in between. The floor was my choice in the ticket and it sits above the sample's
  own scale. Any future window ticket must lower the floor, or the four alternative rules cannot be told apart.
- **`finishImprovedSurface`'s duplicate removal is dead** (`:1188`–`:1213`): it builds
  `improvedSurfacePointCloudNoDuplicates` and never assigns it back, and its loop stops at `size()-1`. Every
  exported surface therefore carries its own cluster twice: Pot A 01 Surface_0 has **66,759 vertices but
  33,985 distinct positions**, Surface_1 **57,281 / 29,731**, Juglet piece 1 Surface_0 **3,580 / 2,955**. This
  is pre-existing — the branch does not touch those lines — but it means **every surface point count in this
  project counts duplicates**, so a count is an upper bound and the effective surface is about half of it on
  Pot A.

### Corrections to the worker's report

- "33 of the 69 fitted surfaces had `other_copied_over=yes` and 36 no": recounting the two columns over 116
  rows × 2 gives **51 yes, 87 no, 94 empty** — 33 was the Surface_0 column on its own.
- The PLY files are **not byte-identical** between the pre-change binary and the new defaults, because the 7th
  column (curvature) is uninitialised (`3.5126242e-34` and worse). Sorting `x y z nx ny nz` gives an identical
  stream: both files hash to `45078dd2c7c30085b68d75e44c61d666` on Juglet piece 1 Surface_0. The defaults claim
  is **geometric identity, not file identity**, and it is stated that way everywhere below.

### What this changes

- The window is out as the next repair **and** out as the villain. With the paper chain on, the pieces that
  write a pair are 1, 4, 6 and 7 under both 3 mm and 0.5 mm, and none of those pairs is genuine. The walls are
  lost **before** the reassignment step — which is what tickets 23 and 24 already said from the other side.
- Since shrinking is safe on Pot A, the switch could be turned on without harming the sample — but there is
  nothing to gain, so the default stays the literal 3.0 mm until something needs a narrower window.
- The next instrument is not another sweep of this constant. It is the per-rung dump (ticket 25), so the merge
  and the reassignment can be seen rather than inferred, or a direct attack on the growth rule that never
  separates the walls in the first place.

### verified: the command or file:line behind each load-bearing claim

- `sacct -j 33855418,33855584,33855784` → three jobs, all COMPLETED 0:0 (2:27 / 1:51 / 4:16). The first ran
  **0 of 116 cells** (STAGER not exported) and says so in its own out/RUN-FAILED.txt; the smoke run's 4 cells
  preceded the real grid.
- `awk -F'\t' 'NR>1 && NF!=46'` over out/cells/cells26.tsv → 116 rows, 0 bad. Outcomes: Juglet two-surface 46 /
  none 40, Pot A two-surface 30.
- `grep '[WINDOW-26]'` in the run logs → real, e.g. `piece=Pot_A_Piece_07 surface=0 mode=residual k=5.0000
  residual_mm=0.008803 other_mm=0.696321 raw_mm=0.044017 clamped_mm=0.500000 admitted_own=3198 admitted_other=0`.
- Window distribution over the 138 fitted-surface values → 79 at 0.500000 (every one with raw < 0.5), 48 at
  3.000000, 11 between 0.559 and 6.000.
- `cmp out/corpus_before.txt out/corpus_after.txt` → identical, 1,803 rows; inputs identical, 51 rows.
- `find out/cells -name '*.pcd' | wc -l` → 0 and `'*.obj'` → 0; survivors 152 `.ply` + 152 `.xyz` + 348 logs;
  out/GEOMETRY_DELETED.txt totals **1,880 files / 2,321,982,794 B**.
- `awk` over out/defaults_proof26_Juglet.tsv → 16 rows, both displacements **0.000000 mm** everywhere with
  identical point counts. Pot A maxima are 0.33–0.71 mm against the **same-binary** control (A2), so the spread
  is run-to-run; the worker traced it to the 30 unseeded ray casts at `mesh_processing_headless.cpp:1940-1950`,
  and the three "Sampled indices" lines it quoted are in the cells' own mesh.log.
- `git log -1 origin/26-the-three-millimetre-window` → `b803746`; `git diff --stat main..origin/…` → 16 files,
  and the only path outside `.scratch/` is `mesh_processing_headless.cpp` (+384/−9).
- **My own measurement** (new job 33856385, run `20261027-1326_b803746_p26-leadcheck`, instrument
  `.scratch/juglet-breaklines/stage26/leadcheck/lead_paircheck26.py`: own PLY reader, brute-force nearest
  neighbour, no code shared with the worker's scorer) reproduces the worker's corrected-ruler numbers **to six
  decimals** on five cells spanning both pots and both answers: W0T J1 3580/12092, through 0.367769, across
  4.198927, coin 0.325174; W2L J1 11894/505, 1.574492 / 4.756950 / 0.000000; W0L J5 1845/300, 2.275682 /
  0.360592 / 0.013333; W0A A07 6066/6437, 3.919588 / 0.248680 / 0.000000; W3A A07 6048/6423, 3.927241 /
  0.247249 / 0.000000.
- `sort -u` on the xyz of three kept surfaces → 66,759/33,985 and 57,281/29,731 (Pot A 01) and 3,580/2,955
  (Juglet 1).
- `git diff main..origin/… -- mesh_processing_headless.cpp | grep -c NoDuplicates` → **0**: the dead dedupe
  block is untouched by this branch.

### What this does not settle

- **A window below 0.5 mm was never tested.** 79 of 90 alternative widths were clamped up to the floor, so the
  four rules were not really compared — they were tested against one 0.5 mm window. If a narrower window is
  ever wanted, the floor comes down first and the empty-recruitment fallback is re-read.
- **One vessel and one sample**: nine Juglet sherds and eight Pot A pieces, one draw each per cell.
- **The counts are duplicate-inflated**, so the surfaces' effective size is unmeasured. Nothing in this reading
  depends on it — the pair statistic uses nearest points, not counts — but quoted counts should be read as
  upper bounds.
- The genuine-pair test divides at the wall thickness measured from the meshes (2–3 mm). A wall thinner than the
  window can still look like a pair, and a wall thinner than 0.5 mm would look like a non-pair.
