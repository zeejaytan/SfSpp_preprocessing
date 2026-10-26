# 24: the normals are five neighbours, and the count rule is why the walls do not separate

**Answers:** U19 (vessel level), E1 (preprocessing half)
**Blocked by:** 23
**Status:** done
**Working in:** chat on Thinkbook16 (2026-10-27)
**Branch:** 24-normals-five-neighbours, in /c/PR/worktrees/sfs/24

A ticket on the *method*. It changes how the surface normals are estimated — behind switches whose
defaults reproduce today's behaviour exactly — and measures whether the two walls of a sherd then
separate. **Report evidence; do not declare a winner.** Judgement stays with the lead.

## The defect, stated as a rule

`mesh_processing_headless.cpp:420`:

```c++
int nb_neighbors = std::max(5, std::min(20, (int)points.size() / 1000));
```

Normal quality is a **function of point count** — one neighbour per thousand points, capped at 20. So a
sherd only gets well-conditioned normals once its whole cloud passes 20 000 points, and a sherd of
20-40 mm at its own spacing (0.20-0.34 mm) holds 800-15 000. Pieces 2 and 9 hold **787** and **1 031**
points after the density step, and **2 565** and **2 094** before it, so they get **five neighbours
whatever the sampling radius is**.

Measured consequence (ticket 20, `D_normal_density.tsv`), scatter of the estimated normal against a
20-neighbour reference on the same cloud:

- Juglet: median **8.40°** (piece 4), **10.98°** (3), **11.14°** (2), up to **12.97°** (9); p90 **22-31°**;
  **14.7 %** of piece 9's normals beyond **30°**.
- Pot A 07: **0.88°** — two orders of magnitude better, on a cloud with 8 598 points.

Region growing decides on a normal-angle test with `paperTheta` 3.4°. A criterion of 3.4° judged on
normals that scatter by 11° is not a measurement; it is a coin toss with a bias. That is the leading
candidate for pieces 2 and 9 producing **zero clusters at all 21 retries**, and it has never been
tested, because `SFS_PAPER_NB` is proven not to reach normal estimation at all (one
segmentation-input md5 across 13 variants).

## What to build

Behind switches whose **defaults leave today's behaviour byte-for-byte alone**:

- `SFS_NORMAL_MODE=count|radius` — `count` is today's `N/1000` rule; `radius` selects neighbours by a
  physical radius instead, so a small sherd is not punished for having few points.
- `SFS_NORMAL_RADIUS_MM=<value|auto>` — the radius. `auto` means a multiple of the piece's own measured
  spacing (the ticket-22 spacing probe already computes `s0` per piece and prints it;
  `[SPACING-22] policy=piece diagMM=... s0MM=...`). `0` keeps today.
- Neighbour floor and cap under `radius` mode (`SFS_NORMAL_MIN_K`, `SFS_NORMAL_MAX_K`) — a radius on a
  very sparse cloud can otherwise pick two neighbours, which is worse than five.
- Print, per piece, the mode, the radius, and the **distribution of neighbours actually used** (min,
  median, max), so a claim that the normals improved can be checked against the count that produced
  them.

Do **not** change: `rhoD` 1.0, `planeDistMM` 2.0, the 3 mm reassignment radius, `paperTheta`,
`paperKappa`, the merge rule, the count constants, the default sampling policy, the mesh stage, or
anything the corpus holds. This ticket moves the normals and nothing else.

## How to measure a normal — not circularly

The reference must not be the same estimator at a different setting. These sherds have **watertight
meshes** (ticket 20 measured all nine: wall thickness medians 2.09-2.90 mm, no holes), so the honest
reference is the **mesh normal at the nearest surface point** to each cloud point, computed in the same
job. Report, per piece and per arm:

- the angle between the estimated normal and the mesh normal: median, p90, and the fraction above 10°
  and above 30°;
- the **sign**: a normal that is 180° from the mesh normal is a flipped normal, which is a different
  defect from a noisy one; report the fraction within 90° of the mesh normal separately;
- how many neighbours each point actually used.

## The arms

All nine Juglet pieces plus Pot A pieces 01-08, same staged inputs as ticket 22's grid, corpus read-only
with md5 before and after. Ticket 23's default path is the baseline (arm A); **23 is merged**
(`b8040fa`), so the switches exist on main with defaults that reproduce today.

| arm | normals | everything else |
|---|---|---|
| A | today (`count`) | today |
| A2 | today, repeat | today (the yardstick: the boundary fit draws `pcl::RandomSample(10000)` unseeded) |
| B | `radius`, auto = 2 × s₀ | today |
| C | `radius`, auto = 3 × s₀ | today |
| D | `radius`, fixed 1.0 mm | today |
| E | whichever `radius` arm wins above | ticket 23's full set: `SFS_SINGLE_CLUSTER=write SFS_SPACING_POLICY=piece SFS_SPACING_SAMPLES=200 SFS_COUNT_SCALE=auto SFS_FLOOR_CEILING=0.01 SFS_REASSIGN_MODE=own` |

**Arm E exists because two repairs interact and neither grid tested the pair.** Under ticket 23's arm C
the finer spacing plus **radius-mode** reassignment made piece 1's two surfaces lie on each other (dot
**+0.3468**, 0.47 mm apart, 46 % of points coincident), while ticket 22's **own-mode** reassignment is
what separated that same piece (dot **−0.9139** at 2.01 mm). So the normals arm that looks best on its
own may behave differently under C's switches. E carries the winners together with `own` mode. It can
ride inside the same job as the normals grid rather than needing a job of its own.

If an arm's radius exceeds the piece's own extent — plausible on a 23 mm sherd — say so and report the
neighbours used rather than letting the arm silently become "the whole piece".

## Evidence to report

1. Per piece per arm: the neighbours-used distribution, the angle statistics against the mesh normal
   (median, p90, fraction >10°, fraction >30°), and the flipped fraction.
2. Per piece per arm: cluster count and sizes at every retry, which of the three outcomes happened under
   ticket 23's rules (two / one / none), with the stage's own log line quoted.
3. Which pieces produce a surface, and which are wall pairs: mean-normal dot, median cross distance,
   share of Surface_1 points coinciding with a Surface_0 point at 0.001 mm, fraction of normals
   pointing opposite — with the A-vs-A2 spread stated.
4. Pot A 01-08 in every arm — Pot A is the control and must not degrade. Give its pair statistics piece
   by piece.
5. The defaults proof in max-displacement form (ticket 22 and 23 both used this shape), against a
   binary built from the pre-change commit.
6. Corpus md5 before and after, both grids, identical.
7. A render for the conservator's eye at a stated mm/px with a drawn scale bar: pieces 2 and 9 (today
   zero clusters) showing the cloud with each point coloured by its normal's angle error against the
   mesh normal, before and after; and Pot A 07 in the same colourmap as the healthy reference. The
   picture must let a non-specialist see whether the normals became coherent or merely different.
8. Geometry deleted with a counted record; the kept bundle is surfaces, logs, the per-piece tables and
   the renders.

## Acceptance criteria

1. `SFS_NORMAL_MODE=count` reproduces today: same pieces, same point counts, same outputs, within the
   A-vs-A2 spread.
2. Every piece reports its neighbours-used distribution and its radius, so each arm can be checked
   against the number that produced it.
3. Angle statistics against the **mesh** normal are given for every piece in every arm, and the method
   of getting them is stated well enough to be repeated.
4. Pot A 01-08 is reported piece by piece in every arm, and any piece that degrades is named with its
   numbers.
5. Which pieces gain a surface, and which gain a *wall pair*, is reported separately — a surface is not
   a pair (ticket 22 measured a piece that separates its walls from 182 points, and pieces that write
   two surfaces of one wall).
6. Corpus md5 identical before and after; nothing outside `.scratch/juglet-breaklines/stage24/` and
   `mesh_processing_headless.cpp` changed on the branch.
7. Renders at a stated scale, opened and described by what they show.

## Budget and constraints

- **At most five Slurm jobs.** Compute nodes only.
- One run directory per job under `/data/gpfs/projects/punim2657/SfSpp/runs/`, with `run.json`,
  `submit.sbatch`, `logs/`, `out/`, and an `index.tsv` row with `verdict` and `human_note` **left
  empty** (the lead fills those).
- Instruments under `.scratch/juglet-breaklines/stage24/` and committed. Check uploaded scripts for CRLF
  — two jobs were lost to that in ticket 22.
- If the pipeline cannot run unmodified apart from these switches, **stop and report**.

## What this cannot settle

Whether coherent normals are enough for the assembler to seat a sherd — that is the stage after the
surfaces. Whether pieces 2 and 9 can ever give two walls: their meshes hold 2 565 and 2 094 vertices, so
if a metric radius does not recover them, the honest conclusion is that **the scan does not carry two
walls** and one surface is the ceiling for those sherds — a different finding, and one that would send
the next ticket at the input data rather than the code.

## Comments (worker, 2026-10-27)

### What was built

The switch set is in `mesh_processing_headless.cpp` (commit `69b6539`, +288/-6, unchanged since):

| switch | default | where it takes effect |
|---|---|---|
| `SFS_NORMAL_MODE`=`count` or `radius` | `count` (today) | `mesh_processing_headless.cpp:625` |
| `SFS_NORMAL_RADIUS_MM`=`<mm>` or `auto` | `0` = today | `:3099-3147` (parse), `:433-526` (resolved per call) |
| `SFS_NORMAL_RADIUS_MULT` | `2` | `mesh_processing_headless.cpp:470` |
| `SFS_NORMAL_MIN_K` / `SFS_NORMAL_MAX_K` | `5` / `20` | `:433-526` (floor and cap) |
| `SFS_NBRS_FILE` | unset | per-point neighbour counts, instrument only |
| `SFS_NORMAL_DUMP_DIR` | unset | the per-call normals PLY, instrument only |

The count rule itself is untouched at `mesh_processing_headless.cpp:621`; radius mode fits its own Eigen PCA over the radius neighbours (CGAL's `pca_estimate_normals` takes a count only, and there is no local CGAL to test another overload against), then hands its median neighbour count to `CGAL::mst_orient_normals` so orientation is still CGAL's. `[ADAPTIVE CGAL] Using N neighbors` keeps printing the count rule's N in every arm: it is **not** evidence of what radius mode used, the `[NORMAL-24]` line is.

### Deviation the ticket should know about: `auto` is resolved per call, not from the raw probe

The ticket defines `auto` as a multiple of "the piece's own measured spacing (the ticket-22 probe's s0)". Measured on this corpus that is 0.021 mm (Pot A 07) to 0.216 mm (Juglet): the **raw scan** spacing, where 2 x 0.216 mm picks about two neighbours and the arm collapses onto the 5-neighbour floor. So `auto` resolves per call from the spacing of the cloud that call is handed (`mesh_processing_headless.cpp:470-472`, `rEff = mult * cloudSpacingMM`). The raw probe's s0 is still measured and printed beside it (`[NORMAL-24] probe`, `[NORMAL-24-SWITCH] s0MM=` / `diagMM=`), so both readings are on the record. Resolved radius: 0.73-0.88 mm on the Juglet pieces, 0.45-0.62 mm on Pot A.

### Jobs

| job | run dir | state | wall | what |
|---|---|---|---|---|
| 33841452 | `20261027-0522_d790f2a_p24-normals-grid` | COMPLETED 0:0 | 5:29 | 102 cells, every angle table empty: `trimesh.proximity` needs `rtree`, absent from the tora env |
| 33841704 | `20261027-0532_1d8fb01_p24-normals-grid` | COMPLETED 0:0 | 4:26 | the grid again, instrument rewritten without trimesh and self-tested in the job |
| 33841866 | `20261027-0537_ba3e41a_p24-normals-arm-e` | COMPLETED 0:0 | 2:02 | arm E, but `EENV` was not exported to the `xargs` child shells, so **no switch reached a cell** (`cells24` shows `envs=none`, `nmode=count`) |
| 33842036 | `20261027-0542_1ec968b_p24-normals-arm-e-rerun` | COMPLETED 0:0 | 2:43 | arm E with the radius env only: `arm_e_env.txt` holds the winning radius setting alone, so this job is arm B repeated |
| 33842148 | `20261027-0546_d3b9f4a_p24-normals-arm-e2` | COMPLETED 0:0 | 2:10 | arm E as defined: radius winner + ticket 23's six switches (17/17 cells report `singleCluster=write floorCeiling=0.010000 countScaleAuto=yes`) |
| 33842352 | `20261027-0552_d30ec2a_p24-renders` | COMPLETED 0:0 | 0:10 | redraw only |

The ticket allows five jobs; the sixth is a **redraw** and makes no new measurement, so every number comes from jobs inside the cap. Jobs 33841866 and 33842036 are wasted quota: their causes (an unexported variable; `arm_e_env.txt` holding only the radius part) are now guarded by a preflight that prints every arm's environment, aborts if arm E's is empty, counts cells whose environment was empty, and counts arm-E cells whose log does not report `singleCluster=write`.

Both grid jobs were green on their own terms: 102 rows of `cells24.tsv` for 102 cells asked; inputs unchanged (51 files byte-identical before/after); frozen corpus and `/opt/sfs-pristine` unchanged (1804 lines); geometry deleted with a counted record (2084 files / 3 491 553 510 bytes, 510 rows = 102 cells x 5 extensions).

### The renderer's colour is the unfolded angle

`angle_points.tsv` stores `ang_deg` in [0, 180] and `dot`; the panel colours `ang_deg` clipped at 45 deg, so a point whose normal is **flipped** (dot < 0) paints red at the same weight as a 45 deg direction error. The folded figure is `med_abs_deg` in `angles24_all.tsv`; the flipped share is 1 - `frac_same_hemisphere`. On Juglet piece 1 arm A the per-point median of the unfolded angle is 11.24 deg against a folded median of 4.34 deg, because 41.7 % of the points sit in the opposite hemisphere; arms B, D and E drive that share to 0.4 %. Read the left-hand colour as "disagrees with the mesh normal, either in direction or in sign".

### Where the numbers live

`out/cells/cells24.tsv` (38 columns: ticket 23's 26 plus calls, nmode, cgalk, radii, nbr_med/min/max, orient_k, floored, capped, cloud_spacing, switch24), `status23.tsv`, `angles24_all.tsv` (370 rows, per call), `measure23.tsv`, `coverage23.tsv`, `defaults_proof_Juglet.tsv` / `defaults_proof_Pot_A.tsv`, `arm_e.txt`, `arm_e_env.txt`, `pick_arm_e.log`, and `out/renders/*.png` (five figures, six rows each) in job 33842352. Per-point angle tables were kept only for Juglet 1, 2, 4, 9 and Pot A 07; everything else died with its stage under the counted record.

## Lead reading — 2026-10-27 (verified first-hand, not taken from the worker's report)

*Corrected the same day: this section first called arm D on piece 7 "a genuine inner/outer pair" and rested
the next step on it. That was my wall-pair bar being wrong, not the geometry being right. The bar, the
correction and what replaces it are all below; the section is rewritten rather than appended so nothing in
it is left standing on the withdrawn number.*

**The neighbour count is not the defect.** Giving the normals 6 to 14 neighbours instead of 5 changes
neither their accuracy nor how many sherds yield two surfaces. What it does change is which regions the
3.4 deg growth test happens to grow — and that is a different problem from the one this ticket set out to
solve.

### The angle to the true surface does not improve with the neighbourhood

| piece | A (count, k=5) | B (radius 2x s, ~6 nbr) | C (3x, ~13 nbr) | D (1.0 mm, ~9 nbr) |
|---|---|---|---|---|
| Juglet 1 | 4.34° | 4.01° | 4.30° | 4.06° |
| Juglet 4 | 6.83° | 6.99° | 8.27° | 7.38° |
| Juglet 7 | 5.78° | 5.80° | 6.59° | 5.99° |
| Juglet 9 | 10.53° | 10.22° | 11.75° | 11.28° |
| Pot A 07 | 0.88° | 0.91° | 0.90° | 0.93° |

(median folded angle per piece against the mesh's own normal, last call = the normals the segmentation
used.) The error is **bias, not variance**: it comes from fitting a plane over a curved patch, and a bigger
patch does not remove it.

Coverage of two surfaces goes the other way: **A 4, A2 4, A_old 4, B 4, C 2, D 2** of nine pieces. Radius
mode *loses* pieces 4 and 6 rather than gaining any.

### The wall-pair bar this ticket was scored against is unsound — proved on its only pass

The bar was **mean-normal dot ≤ -0.9, cross distance ≥ 1.5 mm, coincidence share ≤ 0.05**. It has one pass
in the whole 17-piece x 6-arm grid: arm D on piece 7 (dot -0.9597, cross 4.4852 mm, share 0.0000). A picture
of that cell, asked for so the pair could be seen, killed it. Viewed edge-on along the mean Surface_0
normal, the two sheets' medians differ by **0.230 mm**: they are two patches of **one shell**, side by side
on the same curve. The 4.49 mm is a 3-D cross distance from a 355-point sliver to the 2 366-point
remainder, not a gap between faces. On a curved sherd two patches at different places on the curve have
nearly opposite mean normals while lying in the same shell, so the dot test can be satisfied by nothing at
all. **Piece 7 under D is the same wall written as two patches.**

### The corrected ruler, and what the Juglet actually has

Two faces of one wall lie **one behind the other**: take each Surface_1 point, find its nearest Surface_0
point, and split that vector into the component **along** that Surface_0 point's own normal and the
component **across** it. A real pair has a large along, a small across, and no coincidence.

| | along the normal | across (lateral) | coincidence |
|---|---|---|---|
| Pot A 01 | 7.13 mm | 0.27 mm | 0.0000 |
| Pot A 07 | 3.93 mm | 0.25 mm | 0.0000 |
| Pot A 02-06, 08 | 3.56-3.77 mm | 0.24-0.26 mm | 0.0000 |
| Juglet D piece 7 (the withdrawn pass) | 2.78 mm | **3.73 mm** | 0.0000 |
| Juglet A piece 4 | 2.32 mm | **3.10 mm** | 0.0710 |
| Juglet A piece 7 | 0.64 mm | **4.30 mm** | 0.2630 |

Pot A passes in every arm, comfortably: the two sheets sit on top of each other to a quarter of a
millimetre and are separated by the wall. On the Juglet the lateral offset is as big as the cross
distance, i.e. the "second surface" is beside the first, not behind it.

**Two genuine wall pairs do exist, and both are in arms that turn the paper chain off** (measured on the
2x2 isolation grid's kept surfaces):

- **B1, piece 7** — native cloud, classic PCL region growing: along **3.143 mm**, lateral **0.308 mm**,
  coincidence **0.0000**, 4 204 / 2 638 points. This is Pot A quality (Pot A 07: 3.928 / 0.247 / 0.0000).
- **B0, piece 5** — 0.6 mm cloud, same region growing: along **2.276 mm**, lateral **0.361 mm**,
  coincidence 0.0133, but only 300 points in one surface against 1 845 in the other.

Under the paper-chain arms (A0 and A1) **no** Juglet pair passes in any cell. Two of nine against zero of
nine is a lead, not a proof — one sherd each, one run, no repeat draw.

### What this changes about the order of repairs

- **The normals are still not the repair.** Their accuracy is what it is at every neighbourhood tested, and
  the two genuine pairs were produced by changing the **growth rule**, not the normals.
- **"The 3 mm radius first, because piece 7 shows what the growth can do" is withdrawn.** It rested on the
  false pair. The 3 mm reassignment remains suspect on evidence that does not depend on that bar — the raw
  clusters are opposite-facing on 7 of 9 pieces and the step leaves the surfaces 70-96 % coincident — but
  it is no longer the demonstrated next step.
- **What the two genuine pairs point at instead** is the growth rule: the arms that separate walls are the
  ones where `paperChain` is off and the classic region growing runs. That is also the branch the old
  28e470b binary always used.

### Two defects and one deviation found on the way

- **A whole-piece normal flip under radius mode.** Pot A 08 under B has `frac_same_hemisphere` **0.0009**
  and opposite-facing **0.5256**, against **1.0000** in A / A2 / A_old; Juglet 9 under D sits at **0.1881**.
  The wall statistics happen to be unaffected there, but any logic keyed to the normal **sign** — the
  40°/140° admission window (mesh_processing_headless.cpp:1103, :1114) — would be inverted for that sherd.
  Radius mode is not safe to adopt as a default without a sign check.
- **The normals step is deterministic.** A and A2 agree to 4 decimal places on every angle statistic and
  to **0.0000 mm** surface displacement on every Juglet piece. The run-to-run wobble this project keeps
  meeting lives downstream, in the boundary fit.
- **Deviation from the ticket, documented by the worker:** `SFS_NORMAL_RADIUS_MM=auto` resolves per call
  from the *downsampled* cloud's spacing (0.395 mm x 2 = 0.79 mm) rather than the raw-cloud s0
  (0.021-0.216 mm). The arms therefore test radii of **0.73-1.32 mm**; none tests a radius below the
  0.6 mm density step.

### The figures, looked at

- `C:/PR/worktrees/sfs/24/.scratch/juglet-breaklines/stage24/render24_Piece_1.png` (700x2039,
  0.150 mm/px, 5 mm bar). Under A and A2 the right-hand panel is a **blue Surface_1 covering 83 % of the
  whole sherd** (12 092 of 14 546 points), the red Surface_0 almost hidden under it — what a 32 %
  coincidence looks like. Under B the red becomes a distinct lobe at the lower left. The left-hand panels
  read mostly red under A/A2 because the colour is the **unfolded** angle and 41.7 % of those normals point
  the wrong way; B, D and E drive that to 0.4 %. The picture shows coverage, not separation.
- `.../runs/20261027-0601_062a1c6_p24-p7-figure/out/renders/render24_Juglet_Juglet_Piece_7_lead.png`
  (1040x2039, 0.1058 mm/px). The edge-on column is the one that matters: it is where the 0.230 mm showed up.

### The job count

Six jobs against a cap of five, both overruns named by the worker and re-checked by me: **33841866** ran no
arm at all (EENV not exported to the xargs children, so every cell kept the defaults) and **33842036** was
arm B repeated (arm_e_env.txt carried only the radius part of arm E). Neither contributes a number used
here. The sixth, **33842352**, is a redraw with no new measurement.

### verified: the command or file:line behind each load-bearing claim

- `git diff --stat main..origin/24-normals-five-neighbours` -> 14 files; `mesh_processing_headless.cpp`
  the only path outside `.scratch/juglet-breaklines/stage24/`.
- `sacct -j 33841452,33841704,33841866,33842036,33842148,33842352` -> all six **COMPLETED 0:0**, 05:29 /
  04:26 / 02:02 / 02:43 / 02:10 / 00:10.
- `out/angles24_all.tsv` -> the angle table above; `D Juglet_Piece_9 frac_same_hemisphere 0.1881`;
  `D Juglet_Piece_7 frac_same_hemisphere 0.9932` (so the false pair was not a sign flip).
- `out/cells/measure23.tsv` -> `D Juglet_Piece_7 355 2366 0.0000 -0.9597 4.4852 ... yes`; the pass the
  corrected ruler withdraws.
- **My own recomputation from the kept PLYs** (`stage24/p7_D_S{0,1}.ply`):
  `D npts 355 2366 dot -0.9597 / along S0 mean normal: S0 median 433.531 mm, S1 median 433.301 mm,
  difference 0.230 mm / centroid separation 3.79 mm`.
- **The corrected ruler over every kept pair** (`runs/_lead_pairtest.py` and `_lead_pairtest2.py` on the
  cluster, output `runs/_lead_pairtest.tsv`): Pot A 8/8 pass in every arm (along 3.56-7.13 mm, lateral
  0.24-0.27 mm, share 0.0000); Juglet pairs have lateral 3.1-6.5 mm; `B1 Juglet_Piece_7` along 3.143 /
  lateral 0.308 / share 0.0000; `B0 Juglet_Piece_5` along 2.276 / lateral 0.361 / share 0.0133.
- `cat out/defaults_proof_Juglet.tsv` -> pieces 1, 4, 6, 7: `npts_A == npts_ref` and displacement
  **0.0000 mm** both directions against A_old and A2; pieces 2, 3, 5, 8, 9 `NA` both sides.
- `cmp corpus_before.txt corpus_after.txt` and `cmp inputs_before.md5 inputs_after.md5` -> identical.
- **Mesh units, settled on the cluster:** `Dataset/Juglet/Piece04.obj` diagonal **0.6307** (inches) against
  `Dataset/Mesh/Juglet/Juglet_Piece_4_Mesh.obj` diagonal **32.0374 mm**, both 3 651 vertices. The pipeline
  reads the **mm** mesh; the inches figure applies to the raw source only.

### What this does not settle

- **Two genuine pairs out of nine pieces is a lead.** One sherd each, one arm each, no second draw, and the
  comparison (paper chain off: 2 of 9; paper chain on: 0 of 9) is too small to be a rate.
- Nothing here says the *old* 28e470b binary's piece-7 pair was real: that geometry was deleted under the
  90-day/counted-record policy, and the old bar that called it genuine is the one this ticket has just
  shown to be unsound. Re-testing it needs a re-run, not a re-read.
- The corrected ruler is a geometric criterion, not a seating score. A pair that passes it has not been
  shown to be a *correct* pair under any ground-truth pose.
- Only pieces 1, 2, 4, 9 and Pot A 07 kept per-point tables; pieces 3, 5, 6, 7 and 8 survive as summary rows
  and their kept surfaces.
- Radius mode with a radius **below** the 0.6 mm density step was never tried.
