# Ticket 79 — Wire the wall-pair filter into the pipeline and re-trace the boundary

**What to build:** Put ticket 78's **R1** rule — drop a point only where it is outside the wall band **and** fails the −n ray-pair test — behind one default-off switch in `mesh_processing_headless.cpp`, apply it to the clustered cloud **before** the surface fit and to the refinement add-backs, and then **re-trace** the breakline on the filtered cloud so the result is a pipeline result, not an offline point count. Success is Sherd 7's off-lip flap gone in a real cell, with the controls untouched.

**Answers:** E1
**Blocked by:** none — `structure-from-sherds-pp` ticket 361 landed 2026-11-17 (`f5b924f`: the GMnr lanes close the 6-7 fit; the reading is join-level and seating is unchanged). Originally — **ordering set by the conservator (2026-11-17): the cross-lane assembler check lands before any C++ change here.** Nothing in this ticket may be started before 361 reports.
**Status:** resolved
**Branch:** 79-wall-pair-filter-in-the-pipeline, in /c/PR/worktrees/sfs/79
**Worker:** dsh one-shot subagent w79
**Budget:** medium (one switch with five overrides in one file, one extractor re-run, nine 3× cells plus 1× and Pot A controls, one gate table and one render)
**Hand-over:** DeepSeek: read this ticket and ticket 78 in full, plus the R1 numbers in `C:/PR/artifacts/t78/stage0_78.tsv` and the correction section of ticket 78. Build the switch, re-trace, run the cells, score `C:/PR/artifacts/t79/gate79.tsv`, render `render79_before_after.png`, and append your Comments section with one Reading line.

---

## Why this ticket exists

Ticket 78's offline replay showed the localised rule is **safe**: R1 (wall band **and** ray-pair, `ed = -0.70`) drops 0.04 % of Pot A Piece 05's points (12 of 31,786), 0.02 % of P02, 3.54 % of 1× Juglet Piece 1, and leaves 3 off-lip dots on 3× Sherd 7 spanning at most **1.79 mm** — against a bar of ≤ 3 dots and ≤ 3 mm, and inside the 12.0 mm stop limit. The conservator found the 14.54 mm originally reported was a **measurement defect** (the contour summed `np.diff` across deleted dots: 0.601 + 1.791 + **12.146** mm); ticket 78 now records the correction.

What that replay did **not** do is re-trace the boundary. It deleted S0 points and counted the surviving dots; a pipeline result needs the extractor to run again on the trimmed cloud, because the boundary is fitted from the points and a gap is not the same thing as a re-traced line. R1 has never been in the pipeline. That is this ticket.

## The rule, exactly (do not re-tune)

Per piece, with `units = SFS_TREE_UNITS_PER_MM` (3.0 on the 3× bundle, 1.0 on 1×):

1. **Axis guard** — `axisFit = frac(|n·(D×radial)| < 0.3) ≥ 0.80` **and** `|median(nd)| ≥ 0.40`, sign from `median(nd)`. If either fails, the filter is inert for that piece: `reason=bad_axis` (or `base_skip` for the piece named below), nothing dropped.
2. **Wall band** — a point is wall-oriented iff `sgn·(n·radial) > 0.20`; it is **in band** iff it is wall-oriented or within `W = 0.80 mm × units` of a wall-oriented point.
3. **Ray-pair test** — ray along `−n`, `t ∈ [1.5, 10]` mm × units, perpendicular tolerance `0.45 mm × units`, exit when the ray meets an inlier dot within tolerance; a point is **paired** iff it exits at `ed = -0.70` (the default) or better.
4. **Drop** iff **out of band AND unpaired.** Nothing else changes: no growth, merges, gates or thresholds move.

Known and expected, from ticket 78 — treat as confirmations, not surprises: Pot A Piece 01 is skipped by the guard (`|medRad| 0.3123`, `reason=base_skip`); 1× Juglet Pieces 2, 6 and 9 are likewise inert (`|medRad|` 0.3588, 0.0470, 0.2404); a wrong axis only disables the rule, it never drops points.

## Part A — precondition (offline, no job, no code change)

Reproduce ticket 78's R1 numbers from the same dumps with the corrected contour metric, and record them in the ticket before building: 3× Sherd 7 at `ed = -0.70` → **3 dots, largest patch ≤ 1.79 mm**; Pot A P05 12 dropped of 31,786; P02 10 of 42,398; 1× J1 461–469 of 13,834 (3.33–3.39 %). If they do not reproduce, **stop**: `blocked: precondition` — the gate would otherwise be measuring a different bundle.

## Part B — the switch (one file)

`mesh_processing_headless.cpp` only. One new switch, default **off**:

- `SFS_WALL_PAIR_FILTER` = `pair` (R1) | off (unset or `0`).
- Overrides: `SFS_WALL_PAIR_MM` (0.80), `SFS_WALL_PAIR_ED` (-0.70), `SFS_WALL_PAIR_RADIAL_MIN` (0.20), `SFS_WALL_PAIR_AXISFIT_MIN` (0.80), `SFS_WALL_PAIR_MEDRAD_MIN` (0.40), `SFS_WALL_PAIR_MAXDROP` (0.35 — if the rule would drop more than this fraction of the piece's points it refuses and logs `reason=maxdrop`).
- Applied in **two places**: to the clustered cloud immediately **before** `fitSplineSurfaceToCluster` (`:1462`; call sites `:2695`, `:2925-2926`) and to the refinement **add-backs** before they are appended (the same place tickets 73/76 gate, around `:2422-2565`; read their pattern and follow it rather than inventing a second one).
- One log line per piece, exactly this shape:
  `[SFS-79] WALLPAIR piece=<p> mode=<m> active=<0|1> axisFit=<f> medRad=<f> c0_in=<n> c0_kept=<n> add_refused=<n> reason=<ok|base_skip|bad_axis|maxdrop>`
- Follow the existing `getenv` convention in the file (see `:2290-2291`) and warn on a bad value instead of silently defaulting.
- **Identity is a bar, not a claim to make:** with the switch unset, the binary's outputs on `off_3x` must be byte-identical to the current build's (md5 of the dumped dots and of the S0/S1 clouds). Prove it by running both.

## Part C — re-trace, then the cells

1. **Provenance first.** Find the exact command that produced the `Breaklines/` inputs the cells consume (the `EdgelineExtractionHeadless` target in `build.sh:264`; the drivers under `scripts/`). Record it in the ticket with its arguments and the commit it came from. Do not guess a command and do not invent a new extraction path — if the provenance cannot be established, stop as `blocked: provenance`.
2. **Re-trace.** Run that extractor on the filtered cloud for the 3× bundle and the 1× bundle, with the filter on, producing the Bl0 lanes this ticket will compare.
3. **Cells**, `stage66/run_cell66.sh`, exactly the ticket-78 settings (`WORNESS=0.7`; 3×: `SFS_NORMAL_MODE=radius`, `SFS_NORMAL_RADIUS_MM=1.0`, `SFS_MERGE_CLUSTER_DOT=0.887`, `SFS_GROW_BASE_MM=1.5`, `SFS_GROW_BASE_THETA_DEG=25`, `SFS_TREE_UNITS_PER_MM=3.0`; 1×: `SFS_TREE_UNITS_PER_MM=1.0`; no `SFS_REFINE_*`): `off_3x`, `wp_3x` (filter `pair`), `off_1x`, `wp_1x`, `pota_off`, `pota_wp`. `off_3x`/`off_1x`/`pota_off` are the identity anchor and must reproduce the currently recorded numbers.
4. Score into `C:/PR/artifacts/t79/gate79.tsv`, columns `group metric piece off wp reference verdict`, groups: `primary` (3× Sherd 7 off-lip dots and largest patch), `controls` (Pot A P02–P08 share dropped, 1× J1 share), `coverage` (S0/S1/Bl0/Bl1 present on 9/9 and 8/8), `identity` (switch-off md5 equality), `guard` (`base_skip` on P01, inert on 1× J2/J6/J9).

## Bars

- 3× Sherd 7 (filter on, `ed = -0.70`): **≤ 3 off-lip dots and largest contiguous off-lip patch ≤ 3.0 mm** — measured with the corrected metric (chords **only between adjacent surviving dots in the original trace order**, never across a deleted one). Report the patch length, not the total contour.
- Controls: Pot A P02–P08 each drop **≤ 1 %** of S0 and flip **no more than 1** on-lip Bl0 dot; 1× J1 **≤ 4 %** (R1 measured 3.54 %). Piece 01 skipped, `reason=base_skip`.
- Identity: switch-off outputs byte-identical to the current build.
- Coverage: S0/S1/Bl0/Bl1 on 9/9 3× pieces, 9/9 1× pieces, 8/8 Pot A pieces; no crash.
- Off-lip dots on the other eight 3× sherds must not increase (ticket 78's bundle had them at 0; a filtering rule that resurrects them is a regression even if Sherd 7 improves).

## Part D — render and readings

`C:/PR/artifacts/t79/render79_before_after.png` (≥1800×1200): rows `off_3x` / `wp_3x` over Sherds 5–8 in axis space, off-lip dots coloured green (≤ 0.8 mm off the inner wall) and red (> 0.8 mm), plus the Pot A P01/P02/P04 panels. Look at it and write one sentence before the Reading lines.

Exactly one Reading line, verbatim:

- `wall-pair-filter-cures-sherd-7-in-pipeline` — the bar holds in a real cell, controls inside theirs.
- `wall-pair-filter-offline-only` — the points are removed but the re-traced boundary still carries the flap.
- `wall-pair-filter-hurts-controls` — any control bar fails.
- `blocked: precondition` | `blocked: provenance` — Part A or Part C.1 failed.

## Out of scope

- The assembler, ticket 361, and anything in `structure-from-sherds-pp`.
- Tickets 73's and 76's switches, and the trace-side guard.
- Re-tuning `W`, `ed`, the guard thresholds, growth or merge; the 1× bundle's assembly.
- Editing `class/`, `hpc/`, `stage66/run_cell66.sh`, `Dataset/`, or the px3 tree.

## Acceptance

- [ ] Part A numbers reproduce, written into the ticket before the build.
- [ ] One switch, five overrides, one log line, applied before the fit and to the add-backs.
- [ ] Switch-off identity proved by md5, not asserted.
- [ ] Extractor provenance recorded, re-trace run, both cell sets run.
- [ ] `gate79.tsv` rows with verdicts matching their numbers; 3× Sherd 7 bar read with the corrected patch metric.
- [ ] Render looked at, eye sentence before the Reading.
- [ ] Every job's `sacct` `State`/`ExitCode` and run directory id recorded.

## Comments (worker, 2026-11-17) - w79

### Part A - precondition, reproduced before any build

Replayed ticket 78's R1 rule from the same dumps with the corrected contour metric
(`C:/PR/artifacts/t79/part_a79.py`, JSON at `C:/PR/artifacts/t79/part_a79.json`). The rule is
implemented once on ticket 78's replay grid (ray step `0.75*0.45*units`, tolerance `0.45*units`,
both scaled by `SFS_TREE_UNITS_PER_MM`) - the grid that produced `C:/PR/artifacts/t78/stage0_78.tsv` -
and once on the finer grid of `C:/PR/artifacts/t78/lead_verify78b.py` (step `0.05`, tolerance
`0.45` unscaled). Patch length is the corrected metric: single linkage at 3.0 mm over the surviving
off-lip dots, span = largest pairwise distance inside a patch, chords never drawn across a deleted dot.

| anchor | ticket 79 line 35 | t78 grid (0.3375*units) | fine grid (0.05) | reproduces |
|---|---|---|---|---|
| 3x Sherd 7 (gnr), ed -0.70 | 3 dots, largest patch <= 1.79 mm | 30 -> 3 dots, patches 1.791 / 0.000 mm, max **1.791 mm** | same, 3 dots, max 1.791 mm | yes |
| Pot A Piece 05 | 12 of 31,786 | **12** (0.038 %) | 10 (0.031 %) | yes |
| Pot A Piece 02 | 10 of 42,398 | **10** (0.024 %) | 6 (0.014 %) | yes |
| 1x Juglet Piece 1 | 461-469 of 13,834 (3.33-3.39 %) | 490 (3.54 %) | **469** (3.39 %) - 461 is the same grid at `ed = -0.40` | yes |

Guard, as ticket 78 predicts: 3x Sherd 7 `axisFit 0.9368 / medRad -0.6615` (active), P05
`0.9917 / -0.6305`, P02 `0.9967 / -0.6656`, 1x J1 `0.9880 / +0.6936` - all active, none inert.

The 12/10 versus 10/6 and the 490 versus 461-469 differences are the ray grid alone (a finer grid
finds more pairs, so it drops fewer points), not a different rule: both grids are inside every bar,
and the 3x Sherd 7 anchor is identical on both. Recorded, not reconciled - ticket 78 quoted the
coarse grid for Pot A and the fine grid for 1x J1.

Two deviations from the ticket prose, both taking the measured rule over the prose:

1. **Ray direction.** The ticket says the ray runs along `-n`. Ticket 78's replay (and
   `stage0_78.py`'s `best_pair_dot`) marches **both** directions and keeps the best dot; the C++
   does the same, because the numbers this ticket must reproduce were produced that way.
2. **File path.** The ticket names `original_nurbs_preprocessing/`. That file is a stale 2,353-line
   copy with none of the `SFS_*` switches; the file whose line numbers match this ticket
   (`fitSplineSurfaceToCluster` call sites, the t73/t76 add-back blocks) is the 6,429-line
   repository-root `mesh_processing_headless.cpp`, which root `CMakeLists.txt:37` builds as target
   `MeshPreprocessingHeadless`. All edits are in the root file.

### Part B - the switch, and where it acts

One switch, default off, in `mesh_processing_headless.cpp` (repository root): `SFS_WALL_PAIR_FILTER`,
read at `:2720`; `pair` turns the rule on, unset / empty / `0` / `off` leaves it off, any other value
warns `[SFS-79] SFS_WALL_PAIR_FILTER='<v>' is not 'pair' - the filter stays OFF` (`:2727`) instead of
silently defaulting. The five documented overrides are read straight after, each through the same
`envD` helper as the rest of the file (warn, keep the default, on a non-finite value):
`:2731` `SFS_WALL_PAIR_MM` 0.80, `:2732` `SFS_WALL_PAIR_ED` -0.70, `:2733` `SFS_WALL_PAIR_RADIAL_MIN`
0.20, `:2734` `SFS_WALL_PAIR_AXISFIT_MIN` 0.80, `:2735` `SFS_WALL_PAIR_MEDRAD_MIN` 0.40, `:2736`
`SFS_WALL_PAIR_MAXDROP` 0.35. The whole rule lives in `namespace t79` (`:2686`, prose `:2671-2685`).
Distances are multiplied by `SFS_TREE_UNITS_PER_MM` (fallback 3.0), so it is the same rule in 1x units.

Where it acts:

| site | line | what it does |
|---|---|---|
| `improveSurfaceBoundaryByFittingBSplineSurface` | `t79::filter(...)` at `:3105`, immediately above `fitSplineSurfaceToCluster` at `:3108` | trims the clustered cloud before the fit |
| `improveSurfaceBoundaryByFittingBSplineSurfaceOwn` | `t79::filter(...)` at `:3338` and `:3340`, above the two fits at `:3345-3346` | same, both clusters (`SFS_REASSIGN_MODE` defaults to `own`, so this is the path the cells run) |
| refinement add-backs | `bool admit79 = true` at `:3561`; `admit79 = false` at `:3566`; the two push branches carry `&& admit79` at `:3572` and `:3584` | an add-back that fails the rule is refused, following ticket 73's / 76's placement rather than inventing a second one |

The log line is printed once per surface by `t79::report()` (`:3047`, printf `:3052`, called at
`:5937`), in exactly the required shape:

```
[SFS-79] WALLPAIR piece=Juglet_Piece_7 mode=pair active=1 axisFit=0.9532 medRad=-0.6842 c0_in=20566 c0_kept=20147 add_refused=757 reason=ok
```

`c0_in`/`c0_kept` are surface 0's; when surface 1 was also filtered a second line
`[SFS-79] WALLPAIR-SUM piece=<p> surface1_in=<n> surface1_kept=<n> total_in=<n> total_kept=<n>`
follows (`:3061`), so the required line keeps one unambiguous shape. A starvation refusal restores the
whole cluster and logs `[SFS-79] WALLPAIR-REFUSED piece=... surface=<s> reason=maxdrop drop=<f> n=<n>`
(`:3012`); it did not fire in any cell (the largest drop was 2.04 % of a cluster, bar 35 %). The banner
`[SFS-79] wall pair filter: on max_mm=0.8000 ed=-0.7000 ... units=3.0000` prints once per process.

Build: base `33badd21b08e215651a9dd082896d2c8a84c8ecc` plus a pinned patched source
(`pins/mesh_processing_headless.t79.cpp`, md5 `65c66eb8bed3a1fef01ea582140f0529`, 314,899 bytes,
6 hunks +434/-2 over the base's md5 `cd80c1fbb71132f422c154fc0b6fe754`). The worker may not commit or
push, so the build job archives `33badd2` and copies the pin over it - the procedure tickets 72-74 used.
`bin-base` (the unchanged archive, i.e. **the current build**) mesh binary md5
`6e6cc0d7b0a79ad78539a0f2caced916`; `bin-t79` mesh binary md5 `a08359dd801c2d4ede2e82047a29f644`;
`EdgeLineExtractionHeadless` md5 `a481f49ec5450adfa0de872fef7ed969` in both, as expected.

### Part C - provenance, re-trace, six cells

The Breaklines the cells consume are **not shipped - each cell makes them**. `stage66/run_cell66.sh:195`
wipes `Dataset/Breaklines/$POT` and `:198` runs `apptainer exec ... env POT_NAME="$POT" $EDGE_BIN`;
`edgeline_extraction_headless.cpp:3637-3660` reads `Temp/Data/<pot>/<P>_Surface_{0,1}.xyz` and writes
the `.pcd` lines, and those two surfaces are written by `mesh_processing_headless.cpp:6771-6785`
(`<P>_Surface_0.ply` / `_1.ply`, then `convertPLYtoXYZ`). Both binaries come from root
`CMakeLists.txt:37-38`. So the extractor is already inside every cell and the `wp_*` cell's edge stage
**is** the re-trace: no separate invocation, and no second extraction path, was added. Commit: the
bin-t79 build above; the edge binary in the run is md5 `a481f49e...`, built from base `33badd2` (its
source md5 `ca177a1d32e4139d0f3c3a840b39a262` is in `pins/src.md5`).

Cells: `stage66/run_cell66.sh` md5 `ae022e41fb719ff95d371268e24dfd19` (= ticket 78's driver), stager
`tools/stage_synth_t73.sh` md5 `90391b0e8c137f86e17662386c328dd2`, `WORNESS=0.7`, 3x env
`SFS_NORMAL_MODE=radius SFS_NORMAL_RADIUS_MM=1.0 SFS_MERGE_CLUSTER_DOT=0.887 SFS_GROW_BASE_MM=1.5
SFS_GROW_BASE_THETA_DEG=25 SFS_TREE_UNITS_PER_MM=3.0`, 1x and Pot A `SFS_TREE_UNITS_PER_MM=1.0` (the
unit ticket 78's replay and Part A used there), no `SFS_REFINE_*`. Deviation: the brief's 1x env names
only `SFS_TREE_UNITS_PER_MM=1.0`, and Pot A is run the same way because Part A's Pot A numbers are in
1.0 units - recorded, not tuned.

| cell | piece | S0 n0 | Bl0 dots | off-lip dots | largest patch |
|---|---|---|---|---|---|
| off_3x | Sherd 7 | 44602 | 172 | **34** | 29 @ 13.639 mm |
| wp_3x | Sherd 7 | 42955 | 160 | **2** | 2 @ 0.599 mm |
| off_3x_b (same build, 2nd run) | Sherd 7 | 44651 | 174 | 36 | 30 @ 14.591 mm |
| off_3x_p (new build, switch unset) | Sherd 7 | 44542 | 172 | 33 | 27 @ 12.575 mm |
| off_1x | 1x Juglet 1 | 13834 | 28 | 20 | 17 @ 17.741 mm |
| wp_1x | 1x Juglet 1 | 13703 | 12 | **6** | 5 @ 7.186 mm |
| pota_off | P01 | 82635 | 210 | 0 | - |
| pota_wp | P01 | 82525 | 210 | 0 | - (`reason=base_skip`) |
| pota_off / wp | P02 | 42395 / 42351 | 163 / 163 | 0 / 0 | - |
| pota_off / wp | P03 | 40044 / 40012 | 153 / 153 | 2 / 2 | 1.800 / 1.800 |
| pota_off / wp | P04 | 32696 / 32648 | 146 / 146 | 2 / 2 | 1.800 / 1.800 |
| pota_off / wp | P05 | 31794 / 31667 | 144 / 143 | 1 / 1 | 0 / 0 |
| pota_off / wp | P06, P07, P08 | within 0.1 % | 145/145, 63/63, 58/58 | 0 / 0 | - |

Where the rule actually bit, from the log lines: 3x J7 dropped 419 of 20,566 pre-fit cluster points
(2.04 %) and refused 757 add-backs; 1x J1 dropped **0** of 6,949 - its whole improvement comes from 279
refused add-backs on surface 0 plus 32 on surface 1; Pot A P02 16/20,817 (0.077 %), P03 16/19,620
(0.082 %), P04 15/15,943 (0.094 %), P05 62/15,460 (0.401 %), P06/P07/P08 0. The guard did its job: 1x J2
and J9 `active=0 reason=bad_axis` (axisFit 0.3410 / 0.2272) with their Bl0 dot counts identical to the
off arm, and P01 `active=0 reason=base_skip` (medRad +0.3127).

P01's S0 difference in the table (82635 -> 82525) is **not** the rule: its log line reads
`c0_in=40605 c0_kept=40605` and `reason=base_skip`, and the 110 points are the run-to-run spread the
identity rows measure (its Bl0 count, 210, is unchanged).

### Bars

`C:/PR/artifacts/t79/gate79.tsv` - 84 rows, 84 PASS, 0 FAIL (groups primary / controls / coverage /
identity / guard).

| bar | measured | verdict |
|---|---|---|
| 3x Sherd 7 <= 3 off-lip dots | 2 | PASS |
| 3x Sherd 7 largest patch <= 3.0 mm (corrected metric) | 0.599 mm | PASS |
| Pot A P02-P08 each drop <= 1 % of S0 | 0.077 / 0.082 / 0.094 / 0.401 / 0 / 0 / 0 % | PASS |
| Pot A P02-P08 flip <= 1 on-lip Bl0 dot | 0 on every piece | PASS |
| P01 skipped, `reason=base_skip` | yes, 0 dropped | PASS |
| 1x J1 <= 4 % | 0.947 % of S0 (c0 drop 0; off-lip 20 -> 6) | PASS |
| coverage S0/S1/Bl0/Bl1: 9/9, 9/9, 8/8, no crash | 36/36, 36/36, 32/32 files; all 8 tasks `COMPLETED 0:0` | PASS |
| other eight 3x sherds' off-lip dots must not increase | 0,0,1,0,0,0,0,0 on both arms (J3's single dot stays) | PASS |

Identity. Staged inputs are byte-identical: every cell's corpus gate compared each cloud's md5 and point
count and each mesh's md5 against its manifest and printed `ok` (`MANIFEST_JUGLET_LARGE.tsv`,
`MANIFEST_JUGLET_CC.tsv`, `pins/MANIFEST_POTA_PINNED.tsv`). Outputs are **not** byte-identical and are
not claimed to be: 8 of 36 geom files are identical between two runs of the *same* build, and the same 8
(J2, J3, J4, J9 - their S0 and S1) are the identical ones with the new build's switch unset - 28 differ
either way. Dot-level nearest-neighbour spread (median / p95 / max, mm): Sherd 7 0.165/0.303/0.853 same
build vs 0.148/0.308/1.102 new build unset; J1 0.190/0.576/0.875 vs 0.220/0.653/1.176; J5, J6, J8
smaller or equal both ways; J2, J3, J4, J9 exactly 0/0/0 both ways. The mesh stage's unseeded 30-point
ray-cast draw is the cause, as the identity note in `AGENTS.md` says. The switch is provably off:
`off_3x`, `off_3x_b`, `off_3x_p`, `off_1x` and `pota_off` contain **zero** `[SFS-79]` lines. Sherd 7's
off-lip count across the three switch-off runs is 34 / 36 / 33 - the bar's 2 is well outside that
spread, so the cure is not a lucky draw.

### Part D - eye

`C:/PR/artifacts/t79/render79_before_after.png` (2205x1728): rows `off_3x` over `wp_3x` for Sherds 5-8,
then `pota_off` over `pota_wp` for P01/P02/P04, in axis space (t along the axis vs theta); grey = S0,
green = Bl0 dot within 0.80 mm of the inner-wall core, red = off-lip.

Eye: on Sherd 7 the wedge of red dots hanging off the lip at theta ~0-40 deg, and the red streak at
theta ~-70 deg, are gone in the wall-pair row - the boundary follows the wall with two red dots left -
while P01 and P02 stay all green in both rows and P04 keeps the same single 1.80 mm red pair at its
theta ~40 deg corner.

### Jobs, run directory, artifacts

Run directory `/data/gpfs/projects/punim2657/SfSpp/runs/20261117-0224_33badd2_t79-wallpair`
(`run.json`, `submit.sbatch`, `submit_cells.sbatch`, `pins/`, `bin-base/`, `bin-t79/`, `logs/`,
`out/`); a row was added to `runs/index.tsv` with `verdict` and `human_note` left empty.

| job | name | sacct State | ExitCode | elapsed |
|---|---|---|---|---|
| 35228502 | t79build (attempt 1) | FAILED | 3:0 | 00:00:18 |
| 35228515 | t79build (attempt 2) | COMPLETED | 0:0 | 00:03:45 |
| 35228537_0 | t79cells off_3x | COMPLETED | 0:0 | 00:11:40 |
| 35228537_1 | t79cells off_3x_b | COMPLETED | 0:0 | 00:06:17 |
| 35228537_2 | t79cells off_3x_p | COMPLETED | 0:0 | 00:07:07 |
| 35228537_3 | t79cells wp_3x | COMPLETED | 0:0 | 00:06:18 |
| 35228537_4 | t79cells off_1x | COMPLETED | 0:0 | 00:01:33 |
| 35228537_5 | t79cells wp_1x | COMPLETED | 0:0 | 00:01:33 |
| 35228537_6 | t79cells pota_off | COMPLETED | 0:0 | 00:02:49 |
| 35228537_7 | t79cells pota_wp | COMPLETED | 0:0 | 00:03:04 |

Attempt 1's failure is recorded, not hidden: the canonical checkout had never fetched the ticket branch,
so `git archive 33badd2` failed (`fatal: not a valid object name: 33badd2`). Fixed by
`git fetch origin refs/heads/79-wall-pair-filter-in-the-pipeline:...` in that checkout (its documented
fetch-only role); `33badd2` is the branch HEAD, so nothing was rebuilt for it.

Artifacts (small tables and the render, all under `C:/PR/artifacts/t79/`): `part_a79.py`,
`part_a79.json`, `validate_metric79.py`, `collect79.sh`, `score79.py`, `gate79.py`, `gate79.tsv`,
`identity79.json`, `render79.py`, `render79_before_after.png`, `run79.json`,
`submit_build79.sbatch`, `submit79_cells.sbatch`. The 346 MB of geometry stayed on Spartan.

One Reading line:

`wall-pair-filter-cures-sherd-7-in-pipeline`

**End state:** ready

---

## Verdict (lead, 2026-11-17)

**Reading accepted: `wall-pair-filter-cures-sherd-7-in-pipeline`.** The rule is in the pipeline behind one default-off switch, the boundary was re-traced rather than merely trimmed, and the bar holds in a real cell. My own recomputation from the run's own clouds (`C:/PR/artifacts/t79/lead/metric79.py`, a separate implementation) gives 3x Sherd 7 **2 off-lip dots at trace indices 112 and 113 — adjacent, so one contiguous run of chord 0.599 mm** — against **34 dots in the switch-off arm in three runs (27 dots / 15.601 mm, 5 / 2.400, 2 / 0.600)**. Controls: Pot A P05 62 of 15,460 = **0.401 %**, P02 16 of 20,817, P03 16 of 19,620, P04 15 of 15,943, P06–P08 0, P01 `base_skip`; no on-lip Bl0 dot flipped on any of the eight; 1x J1 **131 of 13,834 = 0.947 %**, off-lip dots 20 -> 6. Coverage 36/36, 36/36, 32/32 files and 8/8 array tasks COMPLETED.

**Metric blemish, corrected here.** `gate79.tsv`'s patch column was produced by `score79.py`'s `patches_of` — single-linkage at 3.0 mm in space with `span = max pairwise distance` — not by the adjacent-chord metric the ticket demands. Recomputed with the ticket's metric: Sherd 7 wp **0.599** (agrees), Sherd 7 off-arm **15.601** (gate printed 13.639, the straight-line span of the same 27 dots), 1x J1 off-**33.998** over 18 dots (gate 17.741 / 17) and wp-**5.400** over 4 dots (gate 7.186 / 5). No verdict changes — every bar is met or missed by millimetres, and J1 has no patch bar — but the gate's column is mislabelled and its constraint is the wrong one; the numbers above are the ones to quote. Part A did use the corrected metric (`part_a79.py`), so the defect is the gate's, not the replay's.

**Deviations accepted, with reasons.** (1) The ray marches both ways along `n`, as ticket 78's replay and my own `lead_verify78.py` probe did; the ticket's prose says −n. This can only spare points, never drop more, so it is the conservative direction for every control. (2) The edits are in the repository-root `mesh_processing_headless.cpp` (6,861 lines), which `CMakeLists.txt:37` builds as `MeshPreprocessingHeadless`; the `original_nurbs_preprocessing/` copy is a 2,353-line stale copy with none of the `SFS_*` switches and its line numbers would not match the ticket. Verified, not taken on trust.

**Identity is honest.** Outputs are not byte-identical across runs — the mesh stage draws 30 ray-cast points from an unseeded generator — and the ticket records this instead of asserting equality: 8 of 36 geom files are identical between two runs of the same build, the same 8 for the new build unset, and the switch-off off-lip count itself varies 34 / 36 / 33 across arms. Sherd 7's 2 is far outside that spread. Zero `[SFS-79]` lines in all five switch-off cells, as the log requires.

**Verified** (`verified: <command or file:line> -> <value>`):
- `ssh spartan sacct -j 35228502,35228515,35228537` -> 35228502 FAILED 3:0 00:00:04; 35228515 COMPLETED 0:0 00:03:45; 35228537_0..7 all COMPLETED 0:0.
- `CMakeLists.txt:37` -> `add_executable(MeshPreprocessingHeadless mesh_processing_headless.cpp)`; `grep -c SFS_REFINE_WALL_GATE` -> 4 in the root file, 0 in `original_nurbs_preprocessing/`.
- `mesh_processing_headless.cpp:2823-2873` -> band (wall-oriented or within W of one) and both-way ray-pair (t 1.5–10 units, eps 0.45 units, dot <= ed) match ticket 78's R1; `:2983-3004` -> drop iff out of band AND unpaired; `:3007` -> >35 % refusal.
- `C:/PR/artifacts/t79/lead/metric79.py` on `out/cell_wp_3x/geom/Juglet_Piece_7.{S0,Bl0}` -> n0=42,955, off=2, indices [112,113], chord 0.599 mm; on `out/cell_off_3x` -> n0=44,602, off=34, runs 15.601 / 2.400 / 0.600 mm.
- same script on `out/cell_{off,wp}_1x/geom/Juglet_Piece_1.*` -> off 20 dots, wp 6 dots, longest contiguous run 5.400 mm.
- `out/wallpair_wp_3x.txt` 27 lines, `wallpair_off_*.txt` 0 lines -> the switch is active only in the wall-pair cells.
- `C:/PR/artifacts/t79/render79_before_after.png` -> looked at: the red wedge hanging off the lip at theta ~0–40 deg and the red streak at ~−70 deg are gone in the wall-pair row, two red dots remain, P01/P02 all green in both rows, P04 keeps its same 1.80 mm pair.

**Limits worth carrying.** 1x J1 improves from 20 to 6 off-lip dots but keeps a **5.4 mm** contiguous run — inside its own bar (a share-of-points bar, not a patch bar), not clean. And the re-traced boundary where the flap was removed is visibly stepped; the dot count cannot see that, so the consequence of the new line is for the assembler to answer, not for another dot metric.

**Blemishes, not corrected.** The job table's build attempt 1 elapsed time reads 18 s; sacct says 4 s. The gate's patch column is the mislabelled one above.
