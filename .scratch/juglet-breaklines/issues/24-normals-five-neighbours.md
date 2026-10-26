# 24: the normals are five neighbours, and the count rule is why the walls do not separate

**Answers:** U19 (vessel level), E1 (preprocessing half)
**Blocked by:** 23
**Status:** in-progress
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
