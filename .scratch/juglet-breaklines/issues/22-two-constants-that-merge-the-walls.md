# 22: the two constants that merge the walls — a 3 mm reassignment and a one-size density step

**Answers:** U19 (vessel level), E1 (preprocessing half)
**Blocked by:** none
**Status:** results-in
**Working in:** chat on Thinkbook16 (2026-10-27)
**Branch:** 22-two-constants-that-merge-the-walls, in /c/PR/worktrees/sfs/22

A ticket on the *method*, not the record. It changes `mesh_processing_headless.cpp` behind
environment switches whose defaults reproduce today's behaviour exactly, and it measures what
each switch does. Judgement stays with the lead: report evidence, do not declare a winner.

## What is already established (lead-measured, not to be re-litigated)

Run `20261027-0300_4cbb2b2_juglet-raw-vs-improved` (job 33838059), notes in that run's
`out/NOTES.md`. The old arm keeps both artefacts, so the clustering and the step after it can be
compared directly:

| piece | clustering dot | gap mm | after the boundary step: dot | share of Surface_1 on Surface_0 |
|---|---|---|---|---|
| 1 | -0.9440 | 2.141 | +0.9727 | 0.705 |
| 2 | +0.4626 | 2.506 | +0.5098 | 0.128 |
| 3 | -0.9831 | 1.898 | +0.9971 | 0.964 |
| 4 | -0.9953 | 2.136 | +0.9993 | 0.842 |
| 5 | -0.8228 | 3.328 | +0.7126 | 0.004 |
| 6 | -0.8724 | 2.547 | +0.9530 | 0.909 |
| 7 | -0.9968 | 3.433 | -0.9877 | 0.000 |
| 8 | +0.6986 | 2.571 | +0.8589 | 0.244 |
| 9 | -0.9895 | 0.750 | +0.6725 | 0.734 |

Read: **the clustering separates the two walls on seven of nine pieces** (dot -0.82 to -0.997,
walls 0.75-3.43 mm apart). Pieces 2 and 8 are fused before that step and are outside this
ticket's reach. The step that collapses the rest is
`improveSurfaceBoundaryByFittingBSplineSurface` (`mesh_processing_headless.cpp:810`): it fits a
NURBS surface to **one** cluster, then iterates **every point of the whole sherd**
(`:911`, first argument `sampledPointCloudNormal` at `:2264`) and admits a point when its
distance to that fitted surface is **< 3 mm** (`:965`, `:976`). The result replaces the cluster
(`:2265-2271`) and is what every downstream stage reads (`:2592`). Against walls 0.75-2.55 mm
apart, a 3 mm radius cannot tell the two walls apart. The only pair that survives intact, piece 7,
is the one whose walls are 3.43 mm apart. Pot A is unharmed because its walls are 3.4-4.06 mm
apart.

Two independent admissions, and the conservator has asked for both to be made adaptive:

1. **The reassignment radius is a length compared against a wall thickness.** A radius is the
   wrong shape of test: a point should belong to the wall it is nearest, not to every wall within
   3 mm.
2. **The 0.6 mm density step is one size for every sherd** (`:2547-2549`, `downsamplePointCloud`
   called with a fixed `0.6F`). On 23-63 mm Juglet sherds it leaves 787-1,467 points for both
   walls; on a 126 mm Pot A piece it is a sensible spacing. The conservator's constraint, which
   the design must keep: **the step stays, and stays a fixed physical spacing within a piece**, so
   the point cloud is uniform and every millimetre threshold downstream keeps its meaning. What
   becomes adaptive is the *value* of that spacing, per piece.

## What to build

All three switches are environment variables. **With none of them set, behaviour must be
identical to today** — that is an acceptance criterion, not a nicety.

1. `SFS_REASSIGN_MODE` = `radius` (default) | `own`.
   `own`: a candidate point may join surface A only if its distance to A's fitted spline is less
   than its distance to the *other* cluster's fitted spline. Keep the existing 3 mm and angle gates
   as outer caps. This needs both clusters' fits available before either is rewritten — the two
   calls at `:2264` and `:2269` are independent today and must not be.
2. `SFS_SPACING_POLICY` = `fixed` (default, 0.6 mm) | `piece`.
   `piece`: choose the spacing so the piece's longest extent spans a fixed number of samples:
   `S = clamp(diag / N, s0, 0.6)` where `diag` is the piece's bounding-box diagonal, `s0` the
   cloud's own median nearest-neighbour spacing (never invent density the scan does not have) and
   `N` from `SFS_SPACING_SAMPLES`. Measure **three** values of N — 100, 200, 400 — and report all
   three; the choice between them is the lead's, on the numbers.
3. `SFS_COUNT_SCALE` = `off` (default) | `auto`.
   Every count threshold is a physical patch size multiplied by the point density, so at a finer
   spacing the same number means a smaller area:

   | constant | where | what it is at 0.6 mm spacing |
   |---|---|---|
   | `minCluster 50` | `:2136`, `:2560` | a patch of 18 mm² |
   | `k1 = 10` | boundary status test, `:1948`, `:1953` | a disc of radius ~1.1 mm |
   | `k2 = 30` | `k2AvgNormal234`, `:1837`, `:1906` | a disc of radius ~1.9 mm |

   `auto` multiplies each of these by `(0.6 / S)^2`. **Measure both**, scaled and unscaled: the
   conservator's expectation is that scaling is enough and the counts "shouldn't matter much", and
   that expectation is a hypothesis for the arms, not a design assumption.
   Distance thresholds (`rhoD 1.0 mm`, `planeDistMM 2.0`) are **not** scaled, and neither is
   anything that defines a *scoring bar* — the assembler's 20.05 deg / 50 mm and the paper's
   parameters stay absolute, because scaling the ruler would make our numbers incomparable with
   the paper's and with every earlier run. Method-internal constants adapt; the ruler does not.

## The arms to measure

For every arm, all nine Juglet pieces plus Pot A pieces 01-08 through the same surface stage:
cluster counts and sizes, whether two surfaces were written, and for each written pair the four
statistics this ticket's table uses (mean-normal dot, median cross distance, share of Surface_1
points coinciding with a Surface_0 point, fraction of the pair's normals pointing opposite).

| arm | switches |
|---|---|
| A baseline | none |
| B ownership only | `SFS_REASSIGN_MODE=own` |
| C spacing only | `SFS_SPACING_POLICY=piece` × N in {100, 200, 400}, counts scaled |
| C2 spacing only, counts unscaled | as C with `SFS_COUNT_SCALE=off` |
| D both | B + C |

A piece counts as **a real wall pair** when dot <= -0.9, median cross distance >= 1.5 mm and share
<= 0.05 — Pot A's own shape, stated here so nobody has to invent a bar.

## Acceptance

1. `git diff --stat main..HEAD` shows the change confined to `mesh_processing_headless.cpp`
   (plus whatever small build/instrument files it needs) — no other tracked source.
2. Defaults proven unchanged: with no switches set, the arm-A run's surfaces are identical to a
   run of the code before the change (md5 per piece, or a stated maximum displacement if byte
   equality is not achievable — say which and why).
3. The arm table above, complete, with the switches and count values used at each cell.
4. Pot A 01-08 under arm D: stated piece by piece as unchanged or changed, with the numbers.
5. Which Juglet pieces reach the wall-pair bar in which arm, and — separately — which pieces were
   already fused before the boundary step (2 and 8 at least) and therefore cannot be helped.
6. One rendered before/after of the same Juglet piece, at a scale that resolves the 2 mm wall gap,
   with the number of pixels per millimetre written on it. `visual-qa/` staging only if the lead
   asks for a conservator's eye; a ticket-local PNG is enough here.
7. Corpus md5 before and after, unchanged; geometry deleted with a counted record; nothing written
   outside the run directory and the ticket; branch pushed.

## Results (2026-10-27) — evidence, no winner

Code: branch `22-two-constants-that-merge-the-walls`, commit `d4f2187` (pushed). Everything
below is measured on Spartan compute nodes; the full tables are the `*.tsv` in the run
directories named under "Where the evidence is".

### What was built

| switch | values | where | what it does |
|---|---|---|---|
| `SFS_REASSIGN_MODE` | `radius` (default) \| `own` | `mesh_processing_headless.cpp:2417-2425` | picks the boundary step: the original, or `improveSurfaceBoundaryByFittingBSplineSurfaceOwn` |
| `SFS_SPACING_POLICY` | `fixed` (default) \| `piece` | `:2714-2735` | `piece`: `S = min(0.6, max(s0, diag/N))` |
| `SFS_SPACING_SAMPLES` | 100 \| 200 (default) \| 400 | `:2716` | the `N` in that formula |
| `SFS_COUNT_SCALE` | `off` (default) \| `auto` | `:2728-2735` | multiplies `minCluster`, `k1`, `k2` by `(0.6/S)^2` |

The fit is now one function, `fitSplineSurfaceToCluster` (`:824`), used by both modes, so the
two arms cannot drift apart in the part that must be shared. The original function keeps its
admission loop verbatim and only calls the fit (`:990`) and the tail (`:1105`,
`finishImprovedSurface` `:880`). `own` mode (`:1114`) fits **both** clusters first, then runs
one loop over the sherd's points computing both distances and both angles, and admits a point
only when `dist[k] < 3` **and** `dist[k] < dist[1-k]`; exact ties join neither (strict `<`).
Count scaling is applied at `:2282-2283` (`minCluster`) and `:2337-2340` (`k1`, `k2`), and the
values actually used are printed per cell as `[COUNT-22]` / `[SPACING-22]` / `[REASSIGN-22]`
lines in each cell's `logs/mesh.log`.

Instruments (all new, all inside the ticket's own `.scratch/juglet-breaklines/stage22/`):
`run_cell.sh`, `submit_22.sbatch.tmpl`, `submit_22_analysis.sbatch`, `measure_arm.py`,
`defaults_proof.py`, `analyse_22.py`, `render_gap.py`.

`git diff --stat main..HEAD` = `mesh_processing_headless.cpp` (+371/-98 lines), this ticket, and
those seven instrument files. No other tracked source.

### Acceptance 2 — defaults proven unchanged

Method: two binaries built from the same push — the new `d4f2187` and the pre-change
`35e38e5` (`main`) — plus a **second pass of the new binary** (`A_new2`) as the run-to-run
yardstick. md5 equality is *not* the proof, because the fit draws `pcl::RandomSample(10000)`
unseeded and the step is stochastic; the yardstick is what that costs.

| pot | piece | surface | points (A / old / new2) | md5 equal | median displacement | max displacement (A→ref / ref→A) |
|---|---|---|---|---|---|---|
| Juglet | 1 | Surface_0 | 3580 / 3580 / 3580 | no | 0.0000 mm | 0.0000 / 0.0000 mm |
| Juglet | 1 | Surface_1 | 12092 / 12092 / 12092 | no | 0.0000 mm | 0.0000 / 0.0000 mm |
| Juglet | 4 | Surface_0 / _1 | 182 / 732 | no | 0.0000 mm | 0.0000 / 0.0000 mm |
| Juglet | 6 | Surface_0 / _1 | 608 / 1016 | no | 0.0000 mm | 0.0000 / 0.0000 mm |
| Juglet | 7 | Surface_0 / _1 | 1012 / 829 | no | 0.0000 mm | 0.0000 / 0.0000 mm |
| Pot A | 01 | Surface_0 | 66758 / 66759 / 66759 | no | 0.0000 mm | 0.3308 / 0.5730 mm |
| Pot A | 01 | Surface_1 | 57293 / 57292 / 57292 | no | 0.0000 mm | 0.6293 / 0.5368 mm |

Juglet pieces 2, 3, 5, 8, 9 write no surface pair in either binary, so they are NA, not equal.

Read: **on the Juglet the point sets are identical** — every piece that writes a pair has zero
displacement in both directions, at the same point count. The files still differ in bytes
(piece 1 Surface_0: 274,974 B new vs 244,984 B old) because the ASCII float text carries digits
further out than the 4-decimal distance can see. **On Pot A the step is stochastic at the
0.3-0.6 mm level** and the count can differ by one, measured between two runs of the *same*
binary; that is the resolution of any "changed" claim on Pot A, not zero.

### The arm grid

Six Slurm jobs, all `COMPLETED` `0:0` (the ticket's budget was six):

| job | run directory | cells | state / elapsed | what it is |
|---|---|---|---|---|
| 33838996 | `20261027-0320_0c28ae2_juglet-armgrid22` | 117 | COMPLETED / 3:54 | superseded: it exposed a regression (below) |
| 33839312 | `20261027-0331_d4f2187_juglet-armgrid22` | 117 | COMPLETED / 2:34 | wasted: instruments uploaded with CRLF, every cell exit 99 |
| 33839313 | `20261027-0331_d4f2187_pota-armgrid22` | 104 | COMPLETED / 1:58 | same |
| 33839377 | `20261027-0336_d4f2187_juglet-armgrid22-rep2` | 117 | COMPLETED / 4:10 | the Juglet grid below |
| 33839378 | `20261027-0336_d4f2187_pota-armgrid22-rep2` | 104 | COMPLETED / 15:30 | the Pot A grid below |
| 33839808 | `20261027-0352_d4f2187_p22-analysis` | — | COMPLETED / 1:02 | statistics, defaults proof, figure |

13 tags per piece: `A`, `B`, `C100`, `C200`, `C400`, `C2_100`, `C2_200`, `C2_400`, `D100`,
`D200`, `D400`, plus the two controls `A_old` (pre-change binary, no switches) and `A_new2`
(new binary, no switches, second pass).

One regression was found and fixed on the way (`d4f2187`): the first version of the refactor
dropped the Cluster1 write-back that `main` has at `35e38e5:2264-2271`, so `Surface_0` never
received its improved cloud (Juglet piece 1: 46,880 B against the old binary's 274,524 B). The
`A_old` control is what caught it; the two write-backs now sit after both calls
(`:2427-2431`), which is safe because the Cluster2 fit reads only Cluster2 and the sherd cloud.

### Counts used at each cell

`S` depends only on the piece and `N`, so one row per (piece, N) covers C, C2 and D alike; the
cell's own log repeats it. `scale = (0.6/S)^2`, applied to `minCluster 50`, `k1 10`, `k2 30`.

| pot | piece | diag mm | s0 mm | N=100: S / minCluster / k1 / k2 | N=200 | N=400 |
|---|---|---|---|---|---|---|
| Juglet | 1 | 63.05 | 0.3380 | 0.6000 / 50 / 10 / 30 | 0.3380 / 158 / 32 / 95 | same as N=200 |
| Juglet | 2 | 28.31 | 0.2109 | 0.2831 / 225 / 45 / 135 | 0.2109 / 405 / 81 / 243 | same as N=200 |
| Juglet | 3 | 33.58 | 0.2153 | 0.3358 / 160 / 32 / 96 | 0.2153 / 388 / 78 / 233 | same as N=200 |
| Juglet | 4 | 32.04 | 0.2156 | 0.3204 / 175 / 35 / 105 | 0.2156 / 387 / 77 / 232 | same as N=200 |
| Juglet | 5 | 42.49 | 0.2386 | 0.4249 / 100 / 20 / 60 | 0.2386 / 316 / 63 / 190 | same as N=200 |
| Juglet | 6 | 39.46 | 0.2237 | 0.3946 / 116 / 23 / 69 | 0.2237 / 360 / 72 / 216 | same as N=200 |
| Juglet | 7 | 44.01 | 0.2580 | 0.4401 / 93 / 19 / 56 | 0.2580 / 270 / 54 / 162 | same as N=200 |
| Juglet | 8 | 34.52 | 0.2216 | 0.3452 / 151 / 30 / 91 | 0.2216 / 367 / 73 / 220 | same as N=200 |
| Juglet | 9 | 23.50 | 0.2035 | 0.2350 / 326 / 65 / 196 | 0.2035 / 435 / 87 / 261 | same as N=200 |
| Pot A | 01 | 172.6 | 0.0755 | 0.6000 / 50 / 10 / 30 | 0.6000 / 50 / 10 / 30 | 0.4315 / 97 / 19 / 58 |
| Pot A | 02 | 137.2 | 0.0558 | 0.6000 / 50 / 10 / 30 | 0.6000 / 50 / 10 / 30 | 0.3430 / 153 / 31 / 92 |
| Pot A | 03 | 132.2 | 0.0519 | 0.6000 / 50 / 10 / 30 | 0.6000 / 50 / 10 / 30 | 0.3306 / 165 / 33 / 99 |
| Pot A | 04 | 116.3 | 0.0484 | 0.6000 / 50 / 10 / 30 | 0.5817 / 53 / 11 / 32 | 0.2909 / 213 / 43 / 128 |
| Pot A | 05 | 120.9 | 0.0484 | 0.6000 / 50 / 10 / 30 | 0.6000 / 50 / 10 / 30 | 0.3022 / 197 / 39 / 118 |
| Pot A | 06 | 132.0 | 0.0418 | 0.6000 / 50 / 10 / 30 | 0.6000 / 50 / 10 / 30 | 0.3300 / 165 / 33 / 99 |
| Pot A | 07 | 58.58 | 0.0212 | 0.5858 / 52 / 10 / 31 | 0.2929 / 210 / 42 / 126 | 0.1464 / 839 / 168 / 504 |
| Pot A | 08 | 54.07 | 0.0203 | 0.5407 / 62 / 12 / 37 | 0.2704 / 246 / 49 / 148 | 0.1352 / 985 / 197 / 591 |

Two consequences worth stating plainly, because they decide how much of the grid is really
distinct: **on every Juglet piece the cloud's own spacing `s0` is the floor**, so N=200 and N=400
are the *same* run and N=100 clamps to 0.6 on only one of nine pieces (piece 1) — the Juglet grid
is effectively three settings, not six. On Pot A, N=400 refines every piece (diagonals are
116-173 mm), which is why the N=400 arms behave differently there.

### Juglet: cluster counts and whether a pair was written

`pre → post` = clusters before and after `mergePaper234`, with the post sizes; `—` = no pair
written (zero or one cluster left, so only `Surface_0` exists).

| piece | A / B / C100 / C2_100 / D100 | C200 / C400 / D200 / D400 | C2_200 / C2_400 |
|---|---|---|---|
| 1 | 22→19 (3489, 626, 411, …, 50) — pair | 7→7 (9032, 4812, 373, 338, 236, 205, 160) — pair | 13→9 — pair |
| 2 | 0→0 — | 0→0 — | 0→0 — |
| 3 | A/B 2→1 (169, 99); C100/C2_100/D100 1→1 (294) — | 0→0 — | 1→1 (289) — |
| 4 | A/B 2→2 (242, 51) — pair; C100/C2_100/D100 1→1 (334) — | 0→0 — | 1→1 (335) — |
| 5 | A/B 1→1 (679) —; C100/C2_100/D100 2→1 (604, 133) — | 1→1 (604) — | 3→2 (604, 136, 51) — pair |
| 6 | A/B 2→2 (365, 213) — pair; C100/D100 2→2 (437, 270) — pair; C2_100 2→1 — | 1→1 (707) — | 1→1 (707) — |
| 7 | A/B 5→4 (326, 263, 77, 68, 65) — pair; C100/D100 3→3 (590, 342, 104) — pair; C2_100 4→3 — | 2→2 (609, 578) — pair | C2_200/C2_400 5→4 — pair |
| 8 | A/B 2→1 (224, 196) —; C100/C2_100/D100 2→2 (254, 206) — pair | 0→0 — | 2→2 (258, 209) — pair |
| 9 | 0→0 — | 0→0 — | 0→0 — |

Pairs written, of nine pieces: A 4 (1, 4, 6, 7), B 4 (1, 4, 6, 7), C100 4 (1, 6, 7, 8),
C2_100 3 (1, 7, 8), D100 4 (1, 6, 7, 8), C200 2 (1, 7), C400 2, D200 2, D400 2, C2_200 4
(1, 5, 7, 8), C2_400 4.

### Juglet: pair statistics (dot / median cross distance / share within 1 µm)

| piece | arm | points S0 / S1 | mean-normal dot | median cross distance | share of S1 on S0 | bar |
|---|---|---|---|---|---|---|
| 1 | A (= A_old = A_new2) | 3580 / 12092 | +0.6183 | 4.3473 mm | 0.3252 | no |
| 1 | B | 1735 / 10920 | +0.2133 | 6.6479 mm | 0.0000 | no |
| 1 | C100 (= C2_100 = D100 = A) | 3580 / 12092 | +0.6183 | 4.3473 mm | 0.3252 | no |
| 1 | C200 (= C400 = C2_200 = C2_400) | 10800 / 15780 | +0.3468 | 0.4716 mm | 0.4597 | no |
| 1 | **D200 (= D400)** | 10044 / 15159 | **-0.9139** | **2.0146 mm** | **0.0351** | **yes** |
| 4 | A | 182 / 732 | -0.9637 | 3.8411 mm | 0.0710 | no |
| 4 | B | 120 / 674 | +0.9785 | 6.1951 mm | 0.0000 | no |
| 5 | C2_200 (= C2_400) | 229 / 2317 | -0.4816 | 11.6280 mm | 0.0147 | no |
| 6 | A | 608 / 1016 | +0.6901 | 4.6015 mm | 0.2402 | no |
| 6 | B | 514 / 930 | +0.5813 | 8.5658 mm | 0.0075 | no |
| 6 | C100 | 820 / 1275 | +0.8612 | 3.7135 mm | 0.2980 | no |
| 6 | D100 | 681 / 1167 | -0.3726 | 9.2604 mm | 0.0017 | no |
| 7 | A | 1012 / 829 | +0.5621 | 4.3393 mm | 0.2630 | no |
| 7 | B | 945 / 743 | +0.4642 | 8.4894 mm | 0.0040 | no |
| 7 | C100 | 1247 / 1660 | +0.6689 | 2.2811 mm | 0.3307 | no |
| 7 | C200 (= C400) | 1753 / 1930 | +0.5099 | 5.3480 mm | 0.2352 | no |
| 7 | C2_100 | 1339 / 1660 | +0.6562 | 2.2969 mm | 0.3151 | no |
| 7 | C2_200 | 1753 / 1997 | +0.5149 | 5.2174 mm | 0.2323 | no |
| 7 | C2_400 | 1753 / 1997 | +0.6479 | 5.2174 mm | 0.2323 | no |
| 7 | D100 | 1055 / 1438 | +0.5163 | 6.2024 mm | 0.0083 | no |
| 7 | D200 | 1567 / 1779 | +0.2875 | 8.4093 mm | 0.0051 | no |
| 7 | D400 | 1567 / 1779 | +0.3945 | 8.4093 mm | 0.0051 | no |
| 8 | C100 (= C2_100) | 840 / 1057 | +0.8725 | 3.8472 mm | 0.1987 | no |
| 8 | C2_200 (= C2_400) | 910 / 1167 | +0.8495 | 4.3406 mm | 0.1714 | no |
| 8 | D100 | 751 / 936 | +0.7725 | 6.3716 mm | 0.0000 | no |

Pieces 2, 3 and 9 write no pair in any arm, so they have no row. Arms not listed for a piece
wrote no pair on it.

Per-arm medians over the pairs that were written (arm_summary.tsv):

| arm | pairs (of 9) | bar | median dot | median cross distance | median share |
|---|---|---|---|---|---|
| A / A_old / A_new2 | 4 | 0 | +0.5902 | 4.343 mm | 0.2516 |
| B | 4 | 0 | +0.5228 | 7.569 mm | 0.0020 |
| C100 | 4 | 0 | +0.7651 | 3.780 mm | 0.3116 |
| C200 / C400 | 2 | 0 | +0.4284 | 2.910 mm | 0.3474 |
| C2_100 | 3 | 0 | +0.6562 | 3.847 mm | 0.3151 |
| C2_200 / C2_400 | 4 | 0 | +0.4309 / +0.4974 | 4.779 mm | 0.2019 |
| D100 | 4 | 0 | +0.3648 | 6.510 mm | 0.0008 |
| **D200 / D400** | 2 | **1** | -0.3132 / -0.2597 | 5.212 mm | 0.0201 |

### Pot A 01-08 under arm D, piece by piece

| piece | A (defaults) | D100 | D200 | D400 |
|---|---|---|---|---|
| 01 | 66758/57293, -0.9995, 7.10 mm, yes | 66763/57297, -0.9995, 7.10, yes | 66763/57297, -0.9995, 7.10, yes | 123430/123806, -0.9994, 7.58, yes |
| 02 | 42200/46327, -0.9993, 3.65, yes | 42200/46324, -0.9993, 3.65, yes | 42200/46332, -0.9993, 3.65, yes | 122412/133495, -0.9992, 3.64, yes |
| 03 | 39773/43576, -0.9995, 3.68, yes | 39771/43570, -0.9995, 3.68, yes | 39771/43574, -0.9995, 3.68, yes | 121848/132108, -0.9993, 3.68, yes |
| 04 | 32683/35787, -0.9996, 3.67, yes | 32684/35788, -0.9996, 3.67, yes | 34728/38009, -0.9996, 3.67, yes | 129691/141125, -0.9995, 3.66, yes |
| 05 | 31579/34139, -0.9994, 3.78, yes | 31575/34139, -0.9994, 3.78, yes | 31574/34141, -0.9994, 3.78, yes | 118615/127594, -0.9993, 3.77, yes |
| 06 | 22572/24920, -0.9997, 3.56, yes | 22571/24918, -0.9997, 3.57, yes | 22574/24919, -0.9997, 3.57, yes | 74368/80217, -0.9992, 3.56, yes |
| 07 | 6066/6437, -0.9990, 3.96, yes | 6369/6760, -0.9991, 3.97, yes | 24635/26743, -0.9988, 3.96, yes | 90430/114064, -0.9811, 3.86, yes |
| 08 | 5528/6097, -0.9994, 3.62, yes | 6795/7465, -0.9995, 3.62, yes | 26771/29286, -0.9993, 3.60, yes | 17961/127619, -0.8080, 11.30, **no** |

Cells are `points S0/S1, mean-normal dot, median cross distance, bar`. Arm B, C100, C200, C2_100
and C2_200 reproduce arm A's *pair statistics* on all eight pieces (dot and cross distance to four
decimals, share 0.0000 on every one); their point counts move by at most 8 points in 57,000, which
is the stochastic spread of Caveat 1. The reassignment switch alone changes nothing measurable on
Pot A, and at N = 100 the spacing policy is clamped at 0.6 on seven of the eight pieces (piece 08
excepted, 0.5407).

Read: **Pot A is unharmed by every arm at N = 100 and 200** — dot stays at -0.999, cross distance
at 3.6-3.7 mm, share at 0.0000 on all eight pieces, i.e. the walls stay apart and the two surfaces
stay clean. Arm D does change *which* points and how many (piece 04: 32,683 under A against
34,728 under D200; piece 07: 6,066 against 24,635; piece 08: 5,528 against 26,771) without
changing the pair statistics. At
**N = 400 piece 08 fails the bar in every arm that refines it** (C400 -0.4709, C2_400 -0.3960,
D400 -0.8080, all with cross distance ~10.7-11.3 mm and `minCluster` 985, i.e. the surfaces are
cut into fragments); pieces 01-07 still pass at N=400 with dot -0.981 to -0.9995.

### Which pieces reach the wall-pair bar (dot <= -0.9, cross distance >= 1.5 mm, share <= 0.05)

- **Juglet, any arm: piece 1 only, under D200 and D400** (-0.9139 / 2.0146 mm / 0.0351). Every
  other Juglet pair in every other arm misses on at least one of the three conditions. Piece 4
  under A already has dot -0.9637 and distance 3.84 mm, and misses on share 0.0710.
- **Pot A: all eight pieces in A, A_old, A_new2, B, C100, C200, C2_100, C2_200, D100, D200**; at
  N=400 (C400, C2_400, D400) seven of eight, piece 08 failing.
- **Already fused before the boundary step, so out of this ticket's reach:** pieces **2 and 9**
  leave zero clusters after `mergePaper234` in every arm, and pieces **3, 5 and 8** leave one in
  arm A. With today's code only four of nine Juglet pieces (1, 4, 6, 7) write a surface pair at
  all, which is why the ticket's nine-piece table cannot be reproduced from this branch: that
  table came from the September bundle (`28e470b`), whose arm wrote pairs on all nine.

### Acceptance 6 — the figure

`20261027-0352_d4f2187_p22-analysis/out/figures/ticket22_wall_gap_Juglet_Piece_1.png` (also
committed beside this ticket as `../stage22/ticket22_wall_gap_Juglet_Piece_1.png`). Juglet piece 1,
arm A before, arm D200 after, both panels sharing one axis, **71.9 px/mm** written in each panel
title, a 2 mm scale bar drawn, and each panel's own share / median distance / dot / bar printed
under it. The projection is an unrolled one — every Surface_1 point is plotted at its signed offset
along the local Surface_0 normal — because a single flat projection smears a 2 mm gap over several
millimetres of a curved sherd. Before: Surface_1 hugs the Surface_0 line (share 0.325, dot +0.618,
bar no). After: Surface_1 sits in a band about 2 mm away (share 0.035, cross distance 2.01 mm,
dot -0.914, bar yes).

### Acceptance 7 — inputs, deletions, where the evidence is

- Corpus unchanged: `out/inputs_before.md5` vs `out/inputs_after.md5`, identical in both grids —
  27 files (Juglet cloud + mesh + boot axes) and 16 files (Pot A cloud + mesh + axis). Nothing was
  written into `original_samples/`, `sfs_main/` or `/opt/sfs-pristine`.
- Geometry deleted with a counted record: Juglet 1,618 files / 382,062,677 B; Pot A 2,046 files /
  8,294,947,344 B, per cell and per extension in each run's `out/cells/geometry_counts.tsv`.
- Kept per cell: `surfaces/<piece>_Surface_{0,1}.ply` and `.xyz`, `logs/stage.log`,
  `logs/mesh.log`, `cell.tsv`. The binary writes no `Breakline_*` file, so BL0/BL1 are not
  produced by this stage; the kept bundle is S0/S1.
- Full tables: `arm_table.tsv` (221 rows, both pots), `arm_summary.tsv`,
  `defaults_proof.tsv` (36 + 32 rows), `measure.tsv` (117 + 104 rows) in the analysis run's
  `out/`; the grids keep their own `out/cells/cells.tsv` and `measure.tsv`.
- One `index.tsv` row per job, `verdict` and `human_note` empty.

### Caveats a reader should carry

1. The boundary step is stochastic (`pcl::RandomSample(10000)`, unseeded). On the Juglet that
   costs nothing measurable; on Pot A it moves points up to ~0.6 mm and can change the count by
   one, so a Pot A difference below that is not a difference.
2. `own` mode removes the coincidence but does not make the normals opposite: share falls to
   0.000-0.008 on all four pieces, while the mean-normal dot stays *positive* on three of them.
   On its own it does not produce a wall pair.
3. On the Juglet, refining the spacing with scaled counts *reduces* the number of pieces that
   write a pair at all (4-5 down to 2 at S = s0), because the finer cloud plus `minCluster` 158-435
   fragments the sherd. Unscaled counts at the same spacing keep 4-5 (C2_200: 4).
4. Only one arm, on one piece, reaches the bar. This ticket reports that; it does not say the arm
   is right, and it does not choose N.
5. `main` rewrote this ticket's scoring-bar paragraph in `35e38e5` (per-sherd seating). That
   paragraph is left untouched on this branch; merging it in is a separate edit.

## What this cannot settle

Whether a two-surface result is *correct* — that needs the breakline and join stages, which stay
paused behind this repair. Whether an adaptive spacing is right for the corpus at large: the
scored corpus pieces are 54-173 mm, so the `piece` policy would move many of them, and no corpus
bar is measured here. Nothing about pieces 2 and 8 beyond reporting them as already fused.
