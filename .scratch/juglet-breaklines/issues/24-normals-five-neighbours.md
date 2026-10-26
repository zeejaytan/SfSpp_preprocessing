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

**The neighbour count is not the defect. Giving the normals 6 to 14 neighbours instead of 5 changes
neither their accuracy nor how many sherds yield two surfaces — and on the one sherd whose walls the
3 mm reassignment cannot reach, the metric radius turned a failed split into a genuine inner/outer pair.**
That splits this ticket's hypothesis in two, and only the second half survives.

### Where each half stands

**"Normal quality is a function of point count, so more neighbours will separate the walls" — refuted.**
The angle to the mesh normal does not improve when the neighbourhood grows, on any piece:

| piece | A (count, k=5) | B (radius 2x s, ~6 nbr) | C (3x, ~13 nbr) | D (1.0 mm, ~9 nbr) |
|---|---|---|---|---|
| Juglet 1 | 4.34° | 4.01° | 4.30° | 4.06° |
| Juglet 4 | 6.83° | 6.99° | 8.27° | 7.38° |
| Juglet 7 | 5.78° | 5.80° | 6.59° | 5.99° |
| Juglet 9 | 10.53° | 10.22° | 11.75° | 11.28° |
| Pot A 07 | 0.88° | 0.91° | 0.90° | 0.93° |

(median folded angle per piece, last call = the normals the segmentation used.) The error is **bias, not
variance**: it comes from fitting a plane over a curved patch, and a bigger patch does not remove it.

Coverage of two surfaces goes the other way: **A 4, A2 4, A_old 4, B 4, C 2, D 2** of nine pieces. Radius
mode *loses* pieces 4 and 6 rather than gaining any; the only arm that reaches 7 is E, and E is radius
**plus** ticket 23's four switches, so its gain cannot be credited to the normals.

**The segmentation is still sensitive to *which* neighbours — that half survives.** Piece 7 flips from a
failed pair under A (n0 1012 / n1 829, 26.3 % of Surface_1's points sitting on Surface_0, mean dot
+0.5621) to the **only genuine wall pair in the whole 17-piece x 6-arm grid** under D (n0 355 / n1 2366,
share **0.0000**, mean dot **-0.9597**, nearest cross distance **4.4852 mm**, opposite-facing **0.9996**,
offset along the normal **2.8111 mm**) — with the same normal accuracy (5.78° against 5.99°). The
decision is being made by the *neighbourhood a normal was averaged over*, not by whether the normal is
right. That is what a 3.4° growth criterion does when the normals carry 4-11° of error.

### The ordering this implies

Piece 7 is the one sherd whose walls are **3.43 mm** apart, i.e. outside the 3 mm boundary radius, and it
is the only piece where the growth's own quality is visible at all. On the other eight the reassignment
destroys whatever was found, before any normal estimator can show its worth. So the next repair is the
**3 mm radius**, not the normals; and this ticket's result is the evidence for that ordering rather than
a repair in its own right.

### Two defects and one deviation found on the way

- **A whole-piece normal flip under radius mode.** Pot A 08 under B has frac_same_hemisphere **0.0009**
  and opposite-facing **0.5256**, against **1.0000** in A / A2 / A_old; Juglet 9 under D sits at **0.1881**.
  The wall statistics happen to be unaffected there, but any logic keyed to the normal **sign** — the
  40°/140° admission window (mesh_processing_headless.cpp:1103, :1114) — would be inverted for that sherd.
  Radius mode is not safe to adopt as a default without a sign check.
- **The normals step is deterministic.** A and A2 agree to 4 decimal places on every angle statistic and
  to **0.0000 mm** surface displacement on every Juglet piece. The run-to-run wobble this project keeps
  meeting lives downstream, in the boundary fit — a useful narrowing, since it retires "the normals are
  noisy" as an explanation for the wobble.
- **Deviation from the ticket, documented by the worker:** SFS_NORMAL_RADIUS_MM=auto resolves per call
  from the *downsampled* cloud's spacing (0.395 mm x 2 = 0.79 mm) rather than the raw-cloud s0
  (0.021-0.216 mm), which would have picked ~2 neighbours and collapsed onto the floor. The arms therefore
  test radii of **0.73-1.32 mm**, i.e. 1.2-2.2x the density step; no arm tests a radius below the step.

### The figure, looked at

C:/PR/worktrees/sfs/24/.scratch/juglet-breaklines/stage24/render24_Piece_1.png (700x2039, 0.150 mm/px,
5 mm bar, six rows). Under A and A2 the right-hand panel is a **blue Surface_1 covering 83 % of the whole
sherd** (12 092 of 14 546 points) with the red Surface_0 almost hidden under it — that is what a 32 %
coincidence looks like, and it is not two walls. Under B the red becomes a distinct lobe at the lower left
(1 327 points) and under D and E it stays a lobe. The left-hand panels read as mostly red under A and A2
because the colour is the **unfolded** angle and 41.7 % of those normals point the wrong way; B, D and E
drive that to 0.4 % and the panel goes green. **What the figure does not show is wall separation** — it is
a projected view, so two surfaces 2.4 mm apart still paint over one another; separation is the cross
distance in the tables, not this picture.

### The job count

Six jobs against a cap of five, both overruns named by the worker and re-checked by me: **33841866** ran no
arm at all (EENV not exported to the xargs children, so every cell kept the defaults) and **33842036** was
arm B repeated (arm_e_env.txt carried only the radius part of arm E, so ticket 23's switches were absent).
Neither contributes a number used here. The sixth, **33842352**, is a redraw with no new measurement.

### verified: the command or file:line behind each load-bearing claim

- git diff --stat main..origin/24-normals-five-neighbours -> 14 files, 1737 insertions / 138 deletions;
  mesh_processing_headless.cpp is the only path outside .scratch/juglet-breaklines/stage24/.
- sacct -j 33841452,33841704,33841866,33842036,33842148,33842352 -> all six **COMPLETED 0:0**, 05:29 /
  04:26 / 02:02 / 02:43 / 02:10 / 00:10.
- awk over 20261027-0532_1d8fb01_p24-normals-grid/out/measure.log -> bar=yes counts: Pot_A **8** for A,
  A2, A_old, B, C, D; **Juglet 1** (arm D). No other Juglet pass exists in the grid.
- awk over the same run's out/cells/measure23.tsv -> "D Juglet_Piece_7 355 2366 0.0000 -0.9597 4.4852
  0.9996 2.8111 yes"; "A Juglet_Piece_7 1012 829 0.2630 0.5621 4.3393".
- awk over out/angles24_all.tsv -> A Juglet_Piece_1 med_abs 4.3405, B 4.0138, D 4.0615;
  D Juglet_Piece_9 frac_same_hemisphere 0.1881.
- cat out/defaults_proof_Juglet.tsv -> pieces 1, 4, 6, 7: npts_A == npts_ref and med/max displacement
  0.0000 mm in both directions against both A_old and A2; pieces 2, 3, 5, 8, 9 are NA on both sides
  (no surface written by either binary).
- cmp corpus_before.txt corpus_after.txt -> identical; cmp inputs_before.md5 inputs_after.md5 -> identical.
- **Mesh units, settled on the cluster:** Dataset/Juglet/Piece04.obj diagonal **0.6307** (inches) against
  Dataset/Mesh/Juglet/Juglet_Piece_4_Mesh.obj diagonal **32.0374 mm**, both 3 651 vertices. The pipeline
  reads the **mm** mesh; the inches figure applies to the raw source only. The workspace note has been
  corrected to say which file is which.
- awk over arm E's out/measure.log -> Pot_A bar=yes **8**; Juglet rows for pieces 1, 2, 3, 4, 5, 7, 8
  (7 two-surface pieces), piece 6 one surface, piece 9 none.

### What this does not settle

- **One bar pass is a lead, not a conclusion.** It is a single cell out of 102, on one sherd, in one run;
  no second draw was made of arm D on piece 7.
- It says nothing about whether the pair it found is *correct* — a dot of -0.96 and 4.49 mm of separation
  are consistent with an inner and an outer wall, and this project's mesh measurement puts that sherd's
  wall at **3.26 mm**, but no seating was scored and no ground-truth pose was involved.
- Only pieces 1, 2, 4, 9 and Pot A 07 kept per-point tables; pieces 3, 5, 6, 7 and 8 survive as summary
  rows only, their geometry gone with its counted record.
- Radius mode with a radius **below** the 0.6 mm density step was never tried.
