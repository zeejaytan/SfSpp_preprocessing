# 23: a sherd that keeps one cluster is discarded — write it as one surface, and stop the floor outrunning the piece

**Answers:** U19 (vessel level), E1 (preprocessing half)
**Blocked by:** none
**Status:** done
**Working in:** chat on Thinkbook16 (2026-10-27)
**Branch:** 23-write-one-cluster-as-one-surface, in /c/PR/worktrees/sfs/23

A ticket on the *method*, not the record. It changes `mesh_processing_headless.cpp` behind an
environment switch whose default reproduces today's behaviour exactly, and it measures what the
switch does. **Report evidence; do not declare a winner or a verdict** — judgement stays with the
lead.

## The defect, established and verified

Two things stand between a small sherd and a surface, and neither of them announces itself:

1. **One cluster is written as nothing.** `tmpSurfaceCluster_Improved_0/1.ply` are written only
   inside the two-cluster path (`mesh_processing_headless.cpp` — the two `savePLYFile` calls and
   the `clusters.size() > 1` gates around them); a piece that ends with one cluster prints
   "Proceeding with available clusters", then reads two temp files that were never written, prints
   "Warning: Source file not found" twice, and **exits 0**. Ten such warnings across five pieces in
   run `20261027-0055_d8af9d2_p07-juglet-stage1`.
2. **The scaled patch floor can outrun the piece.** With counts scaled to a finer spacing, the
   minimum cluster size reaches 158-387 points on a Juglet sherd and the sherd falls to **zero**
   clusters: piece 4 goes from 182 points in a written surface (arm A, defaults) to
   `Number of clusters is equal to 0` under `SFS_SPACING_POLICY=piece SFS_COUNT_SCALE=auto`
   at `SFS_SPACING_SAMPLES=200`. That is ticket 22's arm D200, run
   `20261027-0336_d4f2187_juglet-armgrid22-rep2`.

Today the pipeline writes surfaces for **four of nine** Juglet sherds (1, 4, 6, 7). A sherd with no
surface cannot be seated, so the vessel question's ceiling is 4 of 9 until this is fixed.

## What to build

Behind switches whose **defaults leave today's behaviour byte-for-byte alone**:

- `SFS_SINGLE_CLUSTER=off|write` — when exactly one cluster survives, write it as **Surface_0**
  and set a marker that downstream can read (the run's per-piece status, not a comment), instead of
  writing nothing and warning twice. `off` must reproduce today exactly, warnings included.
- `SFS_FLOOR_CEILING=<fraction|off>` — when `SFS_COUNT_SCALE=auto` is on, the effective
  `minCluster` may not exceed that fraction of the piece's own post-downsample point count
  (proposed default `0.01`, i.e. 1 %, so a 23 000-point cloud gets a floor of at most 230). `off`
  must reproduce today exactly. Print the value actually used and the value it was clamped from.
- Whatever happens, the stage must **say per piece which of three things happened**: two surfaces,
  one surface, or none — with the cluster count, the sizes, the floor used, and the reason for
  "none". A machine-readable line per piece plus a summary file. Today's silence is the defect; an
  absence must be an *announced* absence.
- A one-surface piece has **no interior/exterior decision**. Record it as "single surface" rather
  than letting the size argmax (`satA/satB`) manufacture a confident-looking answer — ticket 20
  measured that argmax deciding on no evidence at all (both interior fractions 0.0000) on pieces 1
  and 4, and by 8 points of 668 on piece 7.

Do **not** change: the 3 mm reassignment radius, `rhoD` 1.0, `planeDistMM` 2.0, the default
0.6 mm density step, `paperTheta`, the merge rule, the mesh stage, or anything the corpus holds.

## The arms to measure

All nine Juglet pieces plus Pot A pieces 01-08 through the same surface stage, same staged inputs
as ticket 22's grid (`Dataset/Point/Juglet/*_Point.pcd` + meshes + the boot axes from the stage-1
run; Pot A's cloud, mesh and axis from the frozen corpus — read-only, md5 before and after).

| arm | switches |
|---|---|
| A baseline | none (defaults) |
| A2 baseline repeat | none, a second pass — establishes the run-to-run floor, because the boundary fit draws `pcl::RandomSample(10000)` unseeded |
| B silence fix only | `SFS_SINGLE_CLUSTER=write` |
| C silence + bounded floor | `SFS_SINGLE_CLUSTER=write SFS_SPACING_POLICY=piece SFS_SPACING_SAMPLES=200 SFS_COUNT_SCALE=auto SFS_FLOOR_CEILING=0.01` |

C is the arm that matters for the five silent sherds; B is the arm that matters for the two that
already keep one cluster (3 and 8, whose merge is *correct* — ticket 20 measured them as one wall
split into two patches, so writing one surface gives back one wall, which is what the boundary of
Surface_0 needs).

## Evidence to report, per piece and per arm

1. Cluster counts and sizes at every retry, the floor used and what it was clamped from, and which
   of the three outcomes happened (two / one / none), with the stage's own log line quoted.
2. Surfaces written: how many, their point counts, and — for a single-surface piece — a
   **coverage** figure that shows whether the written surface is a whole wall or a fragment:
   the fraction of that piece's cloud points lying within 2 mm of the written surface, plus the
   surface's bounding-box extent in mm. A fragment and a wall must not read the same.
3. Pot A: per piece, the two-surface pair statistics ticket 22 defined (mean-normal dot, median
   cross distance, share of Surface_1 points coinciding with a Surface_0 point at 0.001 mm,
   fraction of the pair's normals pointing opposite) in arms A, A2, B and C. **A2 is the yardstick**:
   a difference smaller than A-vs-A2 is not a difference.
4. The defaults proof: arm A against the pre-change binary, the same shape ticket 22 used
   (identical point sets counted as max displacement in both directions at equal point counts; md5
   is not usable because the ASCII floats carry digits beyond the 4-decimal distance).
5. Corpus md5 before and after, both grids, identical. Nothing written into `original_samples/`,
   `sfs_main/` or `/opt/sfs-pristine`.
6. A render for the conservator's eye, at a stated mm/px scale with a drawn scale bar, of: piece 3
   (one cluster today -> one surface under B), piece 5 (one cluster today), piece 2 (zero clusters
   today, still none unless C recovers it) and Pot A 07 as the healthy two-wall reference. Show the
   written surface over that piece's cloud, in the same projection, so a fragment is visible as a
   patch rather than a wall.
7. Geometry deleted with a counted record per cell and per extension; the kept bundle is the
   surfaces, the logs and the status summary.

## Acceptance criteria

1. `SFS_SINGLE_CLUSTER=off` and `SFS_FLOOR_CEILING=off` reproduce today's output: the same
   pieces write surfaces, with the same point counts, and the same two "Source file not found"
   warnings appear for a piece that has none.
2. Under B, every piece that keeps one cluster today writes **one** surface instead of none, named
   as Surface_0, with a per-piece status line saying so.
3. Under C, no piece falls to zero clusters for want of a floor larger than its own cluster — if a
   piece still has no surface, the status says why in cluster sizes and floor, in numbers.
4. A per-piece status exists for all nine Juglet pieces and all eight Pot A pieces in every arm, and
   its "none" rows outnumber nothing silently: any absence is announced.
5. Pot A's two-surface results in A, A2, B and C are given piece by piece, with the A-vs-A2 spread
   stated so a change can be told from the wobble.
6. The defaults proof is reported in the max-displacement form, with what it does not cover stated.
7. Corpus md5 identical before and after; nothing outside `.scratch/juglet-breaklines/stage23/` and
   `mesh_processing_headless.cpp` changed on the branch.
8. Renders at a stated scale, opened and described by what they show, not by what they should show.

## Budget and constraints

- **At most five Slurm jobs.** Compute nodes only — a metric, a re-score or a render over meshes is
  compute-node work; the login node is for reading logs and moving files.
- One run directory per job under `/data/gpfs/projects/punim2657/SfSpp/runs/`, with `run.json`,
  `submit.sbatch`, `logs/`, `out/`, and an `index.tsv` row with `verdict` and `human_note`
  **left empty** (the lead fills those).
- Instruments live under `.scratch/juglet-breaklines/stage23/` and are committed. If an instrument
  is uploaded with CRLF line endings it will fail on the node with `set: pipefail: invalid option
  name` — check for that before submitting (ticket 22 lost two jobs to it).
- If the pipeline cannot run unmodified apart from the three switches, **stop and report**.

## What this cannot settle

Whether one surface is enough for the assembler to seat a sherd — that is the next stage's
question, and the end-to-end run stays paused until this lands. Whether the boundary of a
one-surface piece is a usable breakline (it is Surface_0's boundary by construction, so the
assembler will read it). Whether the normals are the deeper cause: ticket 20 left that suspect and
untried, and `SFS_PAPER_NB` is proven not to reach normal estimation, but the switch to fix it is
not in this ticket.

## Lead reading — 2026-10-27 (verified first-hand, not taken from the worker's report)

**The silence is fixed, and the surfacing ceiling is gone.** Every number below I re-read from the run
directories myself; the worker's item (4) had two mis-typed cloud counts and one panel-width guess, which
it withdrew by message, and the table here is the file's.

Outcomes per arm over the nine Juglet pieces (`status23.tsv`, 16-field rows, counted by me):

| arm | two surfaces | one surface | none |
|---|---|---|---|
| A baseline | 4 | 0 | 5 |
| B single-cluster write | 4 | **3** | 2 |
| C0 = B + piece spacing + scaled counts, floor uncapped | 2 | 2 | 5 |
| C = C0 + floor ceiling 0.01 | 4 | **5** | **0** |

Pot A: **8 of 8 two-surface pieces in all five arms**, mean-normal dot −0.9988 to −0.9997, cross distance
3.56-7.10 mm, share 0.0000, bar met every time.

- **B does exactly what the ticket asked.** Pieces 3, 5 and 8 — the three that keep one cluster — each write
  one Surface_0 (740 / 1 677 / 1 236 points) and announce it. Pieces 2 and 9 stay silent, because they have
  zero clusters and this switch cannot invent one; the status line says so in numbers rather than warning
  about a missing file.
- **The floor ceiling is what lifts the ceiling.** Uncapped (C0) the scaled floor empties four pieces
  (piece 4's 335-point cluster against a 387-point floor); capped at 1 % (C) **no Juglet piece is left
  without a surface** — the first time that has been true, and it moves the vessel question's surfacing
  ceiling from 4 of 9 to 9 of 9.
- **But a surface is not a wall pair, and nothing here separates walls.** No Juglet pair passes the wall bar
  in any arm (dot ≤ −0.9, cross ≥ 1.5 mm, share ≤ 0.05). Closest is piece 4 under A: dot **−0.9637**, cross
  **3.84 mm**, share **0.0710** — a real pair that fails only the 7 % overlap.
- **Two of the new surfaces are corner patches, not sherds.** Piece 2 under C: 220 points, extent
  **11.49 mm** on a piece whose cloud diagonal is **28.31 mm**, covering **28 %** of its own cloud. Piece 9:
  277 points, **13.76 / 23.50 mm**, **42 %**. Pieces 3, 4, 6 and 8 reach **86-98 %** of their clouds.
- **Extent alone cannot be trusted, and piece 5 is why.** Under B its single surface spans 41.80 mm of a
  42.49 mm piece yet sits within 2 mm of only **54 %** of the cloud: a surface the size of the sherd that
  is not lying on most of it. Both columns are needed.
- **A cost this grid exposes and did not test.** Under C piece 1's two surfaces **lie on top of each other**
  (dot **+0.3468**, median cross distance **0.47 mm**, 46 % of Surface_1's points coincident): the finer
  spacing plus the 3 mm reassignment claims the whole sherd into both surfaces. Ticket 22's own-mode arm is
  what separated this piece (dot −0.9139 at 2.01 mm), and **this grid runs radius mode only**, so the two
  repairs have an interaction that has not been measured. Ticket 24 carries an arm for it.

**The picture, looked at** (`stage23/ticket23_surfaces_over_cloud.png`, 1 980 × 1 418, nine panels, 0.0583-
0.1136 mm/px, 10 mm bar in each): piece 3 under A is a grey cloud with no coloured point at all; under B the
740 red points are spread thinly over the whole face — a patch lying on the sherd, not a second wall. Piece
5 repeats the pattern; under C its red and blue sit side by side across the face rather than one behind the
other, which is what a dot of −0.54 describes. Piece 2 under C is a small red cluster in one corner. Piece 1
under A is a dense blue mass over red — two surfaces on the same wall. Pot A 07 is the honest reference: red
and blue interleaved point-for-point along one wall.

**What this changes.** The switches merge **off by default**, so nothing already scored moves. C is the
configuration that gives every sherd a surface and should be the one the next stage runs; it must not become
the default on this evidence, because the 1 % ceiling is one number chosen before the fact and because it
costs piece 1 its pair.

**What this does not settle.** Whether a corner patch is enough to seat a sherd (piece 2's 220 points over
28 % of it may be worse than nothing, or may be enough — that is the assembly stage's measurement, not
this one's). Whether one surface's boundary is a usable breakline in practice. Whether the normals are the
deeper cause: still untested, and ticket 24 is where it goes.

## verified — the command or file:line behind each load-bearing claim

- `git diff --stat main..origin/23-write-one-cluster-as-one-surface` → 14 rows: `mesh_processing_headless.cpp`
  +193/−2, the ticket file 3 lines, 11 files under `.scratch/juglet-breaklines/stage23/`. The row removing
  `24-normals-five-neighbours.md` is **main being ahead of the branch** (I pushed ticket 24 after the branch
  was cut), not a deletion on the branch.
- `sacct -j 33840779,33840913,33840987` → all three COMPLETED 0:0 (00:04:48 / 00:00:25 / 00:00:08).
- `awk -F'\t' 'NF==16 && $2=="Juglet" {c[$1" "$11]++}'` over `cells/status23.tsv` → A two 4/none 5; B two
  4/one 3/none 2; C0 two 2/one 2/none 5; C two 4/one 5/none 0; Pot A two 8 in every arm.
- `one_surface_coverage.tsv` → piece 2 (C) n0 220 / diag 11.49 / cov 0.2838 / cloud 2565; piece 9 (C) 277 /
  13.76 / 0.4245 / 2094; piece 3 (B) 740 / 30.58 / 0.8872; piece 3 (C) 1 115 / 31.41 / 0.9264; piece 4 (C)
  1 300 / 27.03 / 0.8641 / cloud 3651; piece 5 (B) 1 677 / 41.80 / 0.5419; piece 5 (C0) 2 050 / 35.00 /
  0.6907; piece 6 (C0 and C) 2 137 / 37.40 / 0.9830; piece 8 (B) 1 236 / 32.93 / 0.9779.
- `measure23.tsv` arm C Pot A → 8 of 8 `bar=yes`, dot −0.9988 to −0.9997, share 0.0000. Juglet: no `bar=yes`
  in any arm; A piece 1 +0.6183/4.347/0.3252; A piece 4 −0.9637/3.841/0.0710; C piece 1 +0.3468/0.472/0.4597;
  C piece 5 −0.5389/8.118/0.0317.
- `defaults_proof23_Juglet.tsv` → the four pieces that write surfaces: `max_mm_A_to_ref` 0.0000 and
  `max_mm_ref_to_A` 0.0000 against **both** the pre-change binary (A_old, 158ddc6) and a second pass (A2),
  point counts identical (3 580/12 092, 182/732, 608/1 016, 1 012/829). Pot A: worst 0.6472 / 0.8170 mm
  (piece 04) with ±10 points, and the A-vs-A2 repeat alone reaches 0.7364 mm — so the binary difference sits
  inside the run-to-run band it is being compared against.
- `diff -q inputs_before.md5 inputs_after.md5` → identical, 51 rows each; `diff -q corpus_before.txt
  corpus_after.txt` → identical (1 804-line listing including `/opt/sfs-pristine`).
- Render opened at 1 980 × 1 418 (456 943 B) and read panel by panel; the panel titles carry each arm's
  `outcome`, `n0`, `n1` and floor, so the picture and the table can be checked against each other.
- The worker's own instruments were caught and re-run twice (ASCII-only PCD reader in `coverage23.py`, one
  output path per pot in `defaults_proof23.py:68`); both re-runs are recorded in the run directories, and no
  number above comes from a truncated file.
