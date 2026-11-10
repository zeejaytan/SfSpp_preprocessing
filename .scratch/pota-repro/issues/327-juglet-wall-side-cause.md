# Ticket 327 — Bind why three Juglet pieces draw the crack line on the outer wall, and prove the cure direction

**Status:** results-in
**Working in:** C:/PR/worktrees/sfs/327-juglet-wall-side-cause
**Branch:** 327-juglet-wall-side-cause
**Answers:** E1
**Depends on:** none (326's bar-1 diagnosis is input; it lives in the 326 worktree)
**Blocks:** 328 (the cure)
**Worker:** dsh-subagent (first attempt glm-5.3, killed twice by provider rate limit having done nothing; completed by dsh-opencode-go/deepseek-v4.1-flash, agent 4b6566fe)
**Budget:** medium (4 failed acceptance runs; waiting costs none)

> **In one line.** The interior/exterior breakline defect was fixed in the edgeline processing itself
> (tickets 175→182→296: split the dots by parent surface, walk each face, file both slots — interior in
> slot 0 *by construction*, proved 8/8 + 15/15 on a pot). That fixed code regenerated the Juglet bundle on
> 2026-11-03 — and pieces 2, 6 and 9 still carry the **exterior** wall in Surface_0/Breakline_0, so five of
> nine touching joins present breakline normals facing the wrong way and the assembler rejects them at
> correspondence time. Bind which rule in the shipped chain decides the face→slot filing, why it inverts on
> exactly 2/6/9, and prove by a diagnostic swap **on copies** that correcting the slot flips the five
> failing joins' normals positive.

## What is already known (lead-verified 2026-11-10; do not re-derive, reproduce)

**(a) The wall-side split.** Mean radius of each Surface cloud about the piece's own GT axis
(`Dataset/Juglet_GT/Juglet_Piece_N_Axis.xyz` applied with the piece's GT transform; lead script
`C:/PR/worktrees/sfs/325/.scratch/pota-repro/t325/wall_side_check.py` over `artifacts/pota325/juggeom`):

| piece | S0 r_mean (mm) | S1 r_mean (mm) | Surface_0 is |
|---|---|---|---|
| 2 | 5.94 | 5.33 | **outer** |
| 6 | 7.35 | 6.28 | **outer** |
| 9 | 3.74 | 3.36 | **outer** |
| 1,3,4,5,7,8 | — | — | inner |

**(b) The consequence at the assembler** (ticket 326 bar 1; job 34671027, run
`/data/gpfs/projects/punim2657/SfSpp/runs/20261110-1844_6925cb0_t326-diag`, GTPAIR lines): every
**same-wall** touching pair passes the normal-sign test (1-8 +0.97, 1-4 +0.79, 2-9 +0.99, 3-5 +0.99); every
**cross-wall** pair fails (1-2 −0.90, 1-9 −0.94, 2-5 −0.99, 7-9 −0.67, 6-7 +0.11 with 6/16 negative).
18/18 edges explained. The failing gaps equal wall thickness (0.36-2.91 mm): the two lines are the two rims
of one crack.

**(c) The fix line (this is the fix the conservator means — the edgeline processing).**
- **175** (2026-10-20, results-in): user direction "split the dots and let the walk do two walks, one for
  outer, one for inner". Separation by **parent-surface labels** (per-triangle wall label: triangle-normal
  vs mesh-frame radial; fold joins inner). Lead ruling: the **true-face (interior) walk goes in slot 0**
  (assembler opens slot 0 only; slot 0 is interior by design). Note for context: 175's own filing was a
  scratch proof ("installed nowhere"); its stage accounting found the estimator's Surface_0-exclusive
  product is 96% outer-wall.
- **182** (2026-10-20, DONE): the double-walk mechanism traced on the post-176 edgeline.
- **210** (done): Bl0/Bl1 swapped to the author convention on P02-P08.
- **238** (done): "restore working root-edge source to main" — the pristine line was reworked around here.
- **296** (done, merged `0050313` 2026-10-25): **"the interior slot is by construction, not a per-piece
  swap"** (`d19e437`); proved on its pot — interior slot 8/8, both arms seat 8/8 and join 15/15.
- Background (superseded era): the 2026-10-17/18 diagnosis of the same symptom on pots (80: cause bound to
  the size-descending sort in `mesh_processing_headless.cpp:218/:1680`; 81: per-pot slot-exchange surgery)
  was a data-level stopgap before the construction fix landed.
- Open history wrinkle to pin: `e962159` "Split-walk cure on pristine line" (2026-10-21) is **NOT an
  ancestor of fab76f5**, yet 296 (Oct 25) IS. Say what the shipped line at fab76f5 actually carries.

**(d) The regen ran the fixed code.** The Juglet bundle was regenerated 2026-11-03 by the t66 run
(`20261103-1332_fab76f5_t66-admitsign-default`, ticket 66-potc-reorder) at fab76f5, **with 296's
by-construction interior rule in the pipe** — and 3/9 pieces still came out exterior-in-slot-0. So this is
not "the cure never reached the Juglet"; the rule, proven on a pot, **inverts on the Juglet's geometry**
(33 mm vessel; the two walls sit 0.36-2.91 mm apart at the measured gaps). The same one-wall symptom was
also diagnosed on the old (pre-2026-10-31) Juglet bundle in September.

**(e) Slot semantics** (2026-10-17): slot 0 means interior *by convention*
(`Surface_0 -> Breakline_0`, `convert_intermediate_breaklines.py:45`); the assembler reads only slot 0.
"Interior" names the slot, not necessarily the content — which is exactly the defect.

## What to deliver (stop on the first bar that fails and report it)

1. **Nine-piece census, evidence class ≥ ticket 80's.** Re-derive the wall side independently (your own
   script under `.scratch/pota-repro/t327/`, not a copy of the lead's): per piece, mean radius of S0 and S1
   about the GT axis **and** per-wall loop point count / sampling density. Confirm the split is exactly
   2/6/9-outer, and record per-wall densities for the mechanism test in bar 2.
2. **The filing rule + why it inverts.** In the shipped chain at fab76f5 (read the t66 run's
   `submit.sbatch` / stage scripts / logs to see what ran): name **file:line** where the face→slot filing
   is decided (the "interior by construction" of 296 — parent-surface label? walk order? radial sign?), and
   why it inverts on exactly 2/6/9. Test the rule's inputs per piece (e.g. the radial/frame quantity it
   thresholds, evaluated on each Juglet piece) and show the quantity flips sides on 2/6/9 while holding on
   the six. Also pin the e962159-vs-238 history wrinkle from (c).
3. **The old bundle.** If a pre-2026-10-31 Juglet bundle still exists on Spartan, census it the same way —
   were 2/6/9 flipped then too? If it is gone, record that it is gone (nothing is deleted).
4. **Causality proof on COPIES.** Copy the three offending pieces' inputs under your run dir, swap S0↔S1 +
   Bl_0↔Bl_1 on the copies only, run the 326 pair harness
   (`C:/PR/worktrees/structure-from-sherds-pp/326/hpc/tools/diag326_pairs.cpp`, read-only reference; do not
   modify it) at GT on copies + the untouched six, and report dot_med_d3 per touching pair.
   **Bar: all five formerly-failing pairs ≥ +0.7 median; strict-gate inliers > 0 on each.**
5. **Renders.** Per swapped piece, before/after (outer-wall line vs inner-wall line, coloured) into
   `SfSpp_preprocessing/artifacts/pota327/renders/`, as workspace-relative Markdown links in your
   write-back. Eye-check them; the conservator reads pictures.

## Must not

- **No corpus writes.** Diagnostic copies live under your run dir only; the t66 bundle, `Dataset/`,
  `original_samples/` are read-only (list them before/after and paste the listings).
- **No fix in this ticket.** The swap-on-copies is diagnostic; designing or landing the cure is ticket 328.
- **No ORIG/GT points into anything.** GT transforms and axes are the oracle, evidence-only.
- **Never `git worktree add/remove`.** Work only in the pre-created worktree the dispatcher named.
- **No commits, no pushes.** Write-back goes into the ticket's `## Comments (worker, <date>)` section and
  your final-turn output. End with exactly one line:
  `**End state:** ready|waiting: <job ids>|blocked: <reason>|incomplete: <what>`.
- Poll `sacct` directly (never `slurm_poll.sh`); never idle-poll a PENDING job — end the turn `waiting:`.
- Spartan compute only; runs under
  `spartan:/data/gpfs/projects/punim2657/SfSpp/runs/<YYYYMMDD-HHMM>_<git7>_t327<tag>/` with `run.json`,
  `submit.sbatch`, `logs/`, `out/`.

## Inputs

- t66 Juglet bundle: `/data/gpfs/projects/punim2657/SfSpp/runs/20261103-1332_fab76f5_t66-admitsign-default/outU_jug/geom`
  (9x Surface_0/Surface_1 PLY + Breakline_0 PCD) — plus the run's `submit.sbatch`/stage logs for bar 2.
- GT: `/data/gpfs/projects/punim2657/Dataset/Juglet_GT/` (9 T matrices + `Juglet_Piece_N_Axis.xyz`;
  axis .xyz = point+direction, **last 6 numbers, direction = last 3**). Second copy under
  `sfs_preprocessing/Dataset`.
- Lead's measurement (reference, laptop): `C:/PR/worktrees/sfs/325/.scratch/pota-repro/t325/wall_side_check.py`
  over `C:/PR/worktrees/sfs/325/artifacts/pota325/juggeom/`.
- 326 pair harness (reference, laptop): `C:/PR/worktrees/structure-from-sherds-pp/326/hpc/tools/diag326_pairs.cpp`
  + `hpc/scripts/diag326.sh`; its run dir above shows the wiring.
- Touching pairs per the scorer's `Juglet_simple_graph.txt`: 1-2, 1-4, 1-8, 1-9, 2-5, 2-9, 3-5, 6-7, 7-9
  (3-7 is in the graph at 14.19 mm and does not touch; 6-9 is not in the graph).
- Fix-line tickets to read: `.scratch/pota-repro/issues/175-two-walks-two-slots.md`,
  `182-trace-new-edgeline-double-walk.md`, `210-swap-reseat-fresh.md`, `238-restore-good-edge-source.md`,
  `296-seat-a-pot-and-prove-the-interior-slot.md`; background `80-float-cause.md`, `81-swap-cure.md`.

## Comments (worker, 2026-11-10)

### Bar 1 — nine-piece wall-side census (independent, `.scratch/pota-repro/t327/census327.py`)

Instrument: my own script, not a copy of the lead's. It loads the t66 bundle's `S0/S1` PLY (x y z nx ny nz)
and `Bl0/Bl1` PCD, the GT key `Dataset/Juglet_GT`, and measures the radius of every surface point about the
**GT axis line** (point + direction). Frame check first: the t66 clouds are already in the GT frame — about
the GT axis as written, a piece centroid sits 2.4-16.3 mm from the line and surface radii are 11.5-17.2 mm,
which is what a 33 mm vessel requires; applying the T matrices to the axis puts the centroid 100-500 mm off.
Radius is measured to the line itself, not to a centroid-parallel proxy (the lead's script used the latter; it
is sign-equivalent but 3x smaller).

| piece | r_mean S0 | r_mean S1 | Surface_0 | mean(n·r̂) S0 | mean(n·r̂) S1 | S0 pts | S1 pts | Bl0 n | Bl0 mm | Bl0 pts/mm | Bl1 n | Bl1 mm | Bl1 pts/mm | Bl0→S0 | Bl0→S1 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 10.833 | 13.020 | inner | −0.910 | +0.839 | 12,664 | 16,673 | 59 | 106.25 | 0.555 | 64 | 115.16 | 0.556 | 0.618 | 1.826 |
| 2 | 17.015 | 14.749 | **outer** | +0.975 | −0.934 | 1,411 | 1,269 | 32 | 58.11 | 0.551 | 30 | 54.86 | 0.547 | 0.299 | 1.844 |
| 3 | 15.499 | 17.587 | inner | −0.914 | +0.988 | 2,213 | 2,171 | 44 | 81.01 | 0.543 | 41 | 73.68 | 0.556 | 0.290 | 1.904 |
| 4 | 14.636 | 16.914 | inner | −0.958 | +0.981 | 1,861 | 2,191 | 31 | 56.28 | 0.551 | 35 | 63.84 | 0.548 | 0.310 | 2.113 |
| 5 | 13.726 | 15.864 | inner | −0.866 | +0.890 | 3,835 | 5,179 | 43 | 78.45 | 0.548 | 51 | 91.96 | 0.555 | 0.325 | 2.488 |
| 6 | 16.933 | 14.594 | **outer** | +0.025 | −0.042 | 3,805 | 3,157 | 45 | 82.02 | 0.549 | 41 | 74.55 | 0.550 | 0.299 | 2.036 |
| 7 | 9.827 | 11.220 | inner | −0.555 | +0.658 | 5,649 | 7,287 | 54 | 96.47 | 0.560 | 58 | 105.19 | 0.551 | 0.322 | 2.162 |
| 8 | 14.671 | 16.552 | inner | −0.898 | +0.963 | 2,834 | 2,906 | 40 | 71.96 | 0.556 | 42 | 75.43 | 0.557 | 0.338 | 1.527 |
| 9 | 17.205 | 15.221 | **outer** | +0.985 | −0.805 | 1,041 | 1,153 | 22 | 40.40 | 0.545 | 29 | 53.58 | 0.541 | 0.280 | 1.846 |

- **The split is exactly 2/6/9 outer, the other six inner** — the ticket's table reproduced independently.
  `Bl0` rides `S0` on 9/9 (0.28-0.62 mm against 1.5-2.5 mm to `S1`): the slot follows the surface by
  construction, so the defect is upstream of the line — the mesh stage named the outer face `Surface_0`.
- **Per-wall densities are flat across the corpus: 0.541-0.560 pts/mm on every loop of every piece**, and
  `Bl0` is never the sparse one (Bl0 22-59 dots, loop 40-106 mm). Density and loop point count therefore do
  **not** explain 2/6/9; they are recorded here for bar 2's input test.
- **Piece 6 is the odd one on the normal criterion**: mean(n·r̂) is +0.025 / −0.042, i.e. inside ticket 296's
  |Δ| < 0.10 abstain band, while the radius test is decisive (16.93 vs 14.59 mm). Its two faces' normals are
  nearly perpendicular to the radial direction — a base/disc-like fragment, not a wall patch. That makes
  piece 6 the case where the classifier's normal vote has no signal to read, and its tie-break decides.


### Bar 2 — the filing rule, its input per piece, and where it inverts

**The rule (fab76f5 line numbers, `mesh_processing_headless.cpp`).** `classifyAndOrderPaper234` (:3688) runs
inside `paperChain` at :4008, after `mergePaper234` and the size-descending `std::sort(clusters, myobject3)`, i.e.
`clusters[0]` is the larger face by point count, not the interior one. It reads `SFS_AXIS_FILE` (:3693), six
numbers (axis point xyz + direction xyz, :3697-3704; missing/empty/zero-direction is a hard `dieNoAxis`).
For each face it counts `inFrac[f]` (:3705-3718) = the fraction of that face's points whose normal has a
positive dot with `cp - pp`, where `cp` is the point's projection onto the axis line (:3711-3715) — i.e. the
fraction of normals pointing back **toward the axis line**. The vote is

- :3720 `satA = inFrac[0]*n0 + (1 - inFrac[1])*n1`  // [0] is interior
- :3721 `satB = (1 - inFrac[0])*n0 + inFrac[1]*n1`  // [1] is interior
- :3725 `if (satB > satA)` swap `clusters[0]`/`clusters[1]` -> `Surface_0` = interior (:3730); else kept (:3733).

So on a correctly-oriented two-sided wall the **interior** face is the one whose normals point into the cavity,
which is toward the axis: `inFrac` ~ 1 is interior, ~ 0 is exterior. The rule is only as good as (a) which side
of the wall the axis line sits on and (b) the orientation of the estimated normals. Both inputs are wrong on
pieces 2 and 9 for (a), and on piece 6 for (b). Edgelines then inherit the decision mechanically:
`edgeline_extraction_headless.cpp:3516-3520` string-replaces `Surface_0` with `Breakline_0` and :3536 writes it,
which is why bar 1's `Bl0` rides `S0` on 9/9.

**Test of the rule's input, per piece** (`.scratch/pota-repro/t327/classifier327.py`, out `artifacts/pota327/classifier_bar2.json`):
it recomputes the rule's own `inFrac` on the exported `S0/S1` twice — once with the axis line the run actually
staged (`sfs_preprocessing/Dataset/Axes/Juglet/Juglet_Piece_N_Axis.xyz`, our own September MATLAB PotSAC output,
first six numbers) and once with the GT key — and runs the same vote.

| piece | DS-vs-GT axis angle | DS line offset mm | GT line offset mm | inFrac DS S0/S1 -> vote | inFrac GT S0/S1 -> vote |
|---|---|---|---|---|---|
| 1 | 1.5 deg | 3.45 | 3.51 | 0.997 / 0.031 -> S0 | 0.997 / 0.031 -> S0 |
| 2 | **87.8** | 2.09 | 14.60 | 0.403 / 0.001 -> S0 | **0.000 / 0.999 -> S1** |
| 3 | 31.8 | 11.64 | 14.66 | 0.971 / 0.000 -> S0 | 0.993 / 0.000 -> S0 |
| 4 | 10.7 | 14.60 | 15.04 | 0.999 / 0.000 -> S0 | 0.999 / 0.000 -> S0 |
| 5 | 44.5 | 13.16 | 13.08 | 1.000 / 0.000 -> S0 | 1.000 / 0.002 -> S0 |
| 6 | 13.3 | 13.65 | 13.83 | 0.485 / 0.526 -> S1 | 0.485 / 0.526 -> S1 |
| 7 | 24.1 | 6.94 | 4.53 | 0.951 / 0.020 -> S0 | 0.920 / 0.026 -> S0 |
| 8 | 12.8 | 14.87 | 14.01 | 0.993 / 0.000 -> S0 | 0.986 / 0.000 -> S0 |
| 9 | **73.3** | 0.91 | 15.28 | 0.269 / 0.000 -> S0 | **0.001 / 0.951 -> S1** |

(Vote = which face the rule would put in `Surface_0`. The recomputation reproduces the run's own `[PAPER-234]`
numbers on 8/9 pieces after mapping through the recorded swap; piece 6 is the exception, see below.)

**Why 2 and 9 invert: the staged axis line is on the wrong side of the wall.** The DS axis is nearly
perpendicular to the GT axis on exactly these two pieces (87.8 deg and 73.3 deg) and its line point sits on the
**outward** side of the wall — `(cp_ds - centroid)·r_hat_c` = +1.284 mm (P2) and +0.754 mm (P9), against
-14.597 / -15.284 mm for the GT line. With the line outside the wall, the outer face's own outward normals point
back toward it, so `inFrac` inverts and the rule files the outer face as interior. Handed the GT axis, the same
rule on the same clouds votes the physically correct way on both. The two lines are also nearly parallel on the
other seven pieces (1.5-44.5 deg) and there the DS axis happens to be on the usable side, which is why 7/9 were
filed correctly. Note the DS axis is a 6-number file even where our PotSAC wrote two candidate lines: P7's file
holds 12 numbers and the binary reads only the first six (:3697) — silently discarding the alternative.

**Why 6 inverts: the normals fed to the vote were inverted, not the axis.** DS and GT lines agree to 0.6 mm
laterally on piece 6 and both are on the same (inward) side, so no axis choice changes the vote. Its logged vote
is decisive — `face0 interior_frac=1.0000`, `face1 0.0000`, `satA=3340 satB=0`, kept — i.e. the larger face's
normals point at the axis, so the rule calls the larger face interior; bar 1's radius measurement says that
same face (`S0`, r = 16.933 mm) is the **outer** one (inner face 14.594 mm, so the wall is a 2.34 mm shell).
An inverted normal set inverts `inFrac` on both faces and hence the vote. The run agrees that these normals
are inverted: piece 6 is the **only** piece of nine whose mesh log prints `Normals flipped: true` —
`checkNormalsIntersection` (:3144) fires when a normal from the larger face hits the other face within
0.2 mm over 3 mm, i.e. exactly "this face's normals point into the wall". But that check and its global
negation run at :4145-4164, i.e. **after** the classification at :4008. The pipeline therefore repairs the
normals only once the face has already been filed. (Corroboration from the export: `S0/S1` normals on piece 6
have |mean unit n| = 0.017 / 0.041 against 0.32-0.96 on the other eight, so that piece's exported normals
cannot be used to re-derive its vote; the log line is the evidence, and the flip flag is the admission.)

**The history wrinkle, pinned.** `e962159` ("Split-walk cure on pristine line", 2026-10-21) is **not** an
ancestor of `fab76f5` and its blob (`edgeline_extraction_headless.cpp` md5 `21fbb6b5`) never ships: it sits on
the exp-218 branch, whose later commit `885f433` carries the same line plus three unmerged arms (blob
`89ab05b1`). Ticket 238 (2026-10-22, commit `fd01c6f`) restored that blob into main because main's file
(`ce76a872`) built stub lanes. The file fab76f5 actually builds is neither: md5 `f0dbfe70`, introduced by
`8e1e514` (2026-10-24, "Ship the largest-lump walk seed"), after `b289e87` landed the walk fixes the same day.
The face-vs-slot classifier is a separate, later addition: introduced by `7035611` (2026-10-22, ticket 234
paper chain) and hardened by `66d4ad9` (2026-10-25, `dieNoAxis`). So "238's split-walk cure is in the shipped
line" is false in both directions: the cure's content was flattened in on 2026-10-22 and the walk it cured was
rewritten on 2026-10-24; and the classifier that files these faces postdates both.

**Cause, stated once.** `Surface_0` = interior is a hard-coded invariant, and the only thing standing between
it and these clouds is a two-input vote whose inputs are (a) an axis line we supply and (b) normals estimated
upstream. On 2 and 9 input (a) is a wrong-side line from our own September axis fit; on 6 input (b) is inverted.
Nothing in the vote checks its own answer against the geometry (radius, thickness, normal coherence), so a
wrong-side axis or an inverted normal set converts silently into `Surface_0` = outer, and every downstream
artifact (Bl0, Bl1 naming, the assembler's single `Breakline_0`) inherits it.


### Bar 3 — the pre-2026-10-31 bundle: what still exists, and what it said

**What still exists.** The pre-1031 Juglet runs are nine directories under
`/data/gpfs/projects/punim2657/SfSpp/runs/`: `20261027-0055_d8af9d2_p07-juglet-stage1`,
`20261027-0227_4cbb2b2_juglet-two-walls`, `20261027-0300_4cbb2b2_juglet-raw-vs-improved`,
`20261027-0320_0c28ae2_juglet-armgrid22`, `20261027-0331/0336_d4f2187_juglet-armgrid22(-rep2)`,
`20261027-0551_81d76c2_juglet-2x2`, `20261027-0659_cc9c6d9_t30-arm4-control-jug3p4`,
`20261029-0017_bdbd8b8_t41-juglet`, `20261029-0444_835fc1c_t42-juglet`. Per-piece **geometry** survives in
two of them only: `20261027-0659_cc9c6d9_t30-arm4-control-jug3p4/out/arms/t30-arm4-control-jug3p4/Juglet/Juglet_Piece_N/{surfaces,breaklines,logs}`
and `20261029-0017_bdbd8b8_t41-juglet/out/cells-pipeline/Juglet_Piece_N_armA..D/surfaces`. Everything else
was culled to counts and logs (`GEOMETRY_DELETED.txt`, `geometry_counts.tsv`); `t42-juglet` keeps only a
`packed-20261103.tar.gz` + MANIFEST, `juglet-two-walls` only `two_walls.tsv`/`NOTES.md`. The **old input
clouds** are archived at `SfSpp/attic/20261031-juglet-vertex-dumps`, so the pre-1031 clouds exist but the
per-piece surface exports mostly do not.

**What the surviving two say** (my own script `.scratch/pota-repro/t327/census327_old.py`, output
`artifacts/pota327/census_bar3_old.json`, same GT-axis instrument as bar 1; frame confirmed the same way —
centroids 2.8-15.0 mm off the GT line, z spans in −551..−476):

| bundle | piece | r_mean S0 | r_mean S1 | Surface_0 | note |
|---|---|---|---|---|---|
| t30 (2026-10-27) | 1 | 11.349 | 13.510 | inner | mesh log: both faces inFrac 0.0000, decided by size |
| t30 | 4 | 17.369 | 15.299 | **outer** | |
| t30 | 6 | 16.459 | 17.025 | inner | |
| t30 | 7 | 14.454 | 11.128 | **outer** | |
| t41 armA (2026-10-29) | 1 | 10.054 | 12.927 | inner | |
| t41 | 4 | 16.221 | 15.299 | **outer** | |
| t41 | 5 | 10.647 | 15.143 | inner | |
| t41 | 6 | 16.386 | 17.063 | inner | |
| t41 | 7 | 13.703 | 9.114 | **outer** | |
| t41 | 8 | 14.273 | 15.272 | inner | |

- **Pre-1031 the inverted set was {4, 7}; piece 6 was filed correctly then; pieces 2 and 9 could not be
  asked at all** — on the vertex-dump clouds the pipeline produced **zero** surfaces for them
  (`t41` `status_raw.tsv`: P2 "no temp surface; final clusters=0 sizes=none" after 21 merge passes, P9
  clusters=0; `t30`: P2 1031 pts / P9 787 pts, both clusters=0, and P3/P5/P8 collapsed to one cluster).
- So the misfiling set **moved** with the 2026-10-31 cloud regen and the chain change: {4,7} → {2,6,9}. That is
  a bundle-to-bundle comparison, not a controlled cloud-only A/B (old bundles also run a different commit and
  recipe), so it locates the change in time; it does not attribute it.
- The old runs already staged the **same axis file family** the t66 run used — `t41` `inputs.md5` REAL-AXIS
  `6066ab7374d91292403662fa1870f494` for `sfs_preprocessing/Dataset/Axes/Juglet/Juglet_Piece_2_Axis.xyz`,
  byte-identical to t66's P2 row — so the wrong-side axis on pieces 2 and 9 is not new.
- The old mesh logs show the same unguarded vote degenerating: `t30` P6 `face0 n=365 frac=0.0822 / face1
  n=213 frac=0.2207 -> satA=196 satB=382 -> swapped`, and P1/P4 with **both** faces at `frac=0.0000`, where
  the decision falls to the size term alone (P4: `satA=51 satB=242`). P1 also prints
  `Normals flipped: true` — the flip path of bar 2 was already in play on the old clouds.


### Bar 4 — causality proof on copies: the swap moves three of five, not five

**Setup.** Run dir `/data/gpfs/projects/punim2657/SfSpp/runs/20261110-2028_1b131dc_t327-swap`, job
**34687732** (partition sapphire, 24 cpus, 64G, COMPLETED 0:0, 44 s). `work/trees/juglet_GT_ctrl` is a
byte-identical copy of the 326 Juglet GT tree (`20261110-1640_22151d0_t325-juglet/work/trees/juglet_GT_r1`);
`juglet_SWAP` differs from it in **exactly 12 files** — `Surface_0`/`Surface_1`/`Breakline_0`/`Breakline_1`
for pieces 2, 6, 9 — with `Surface_0<->Surface_1` swapped and `Breakline_0` replaced by the t66 `Bl1` (the walk
on the other wall). Source tree untouched (`Surfaces+Breaklines` md5 `2c0c39c37d3311e97d9bb79c08c4c7de` =
ctrl copy; swap tree `4fd20b5ea6babe5aa8eaad6ffe08e682`). Harness shipped byte-identical to what 326 ran
(`diag326_pairs.cpp` `4486b2d31b0194b5f0d3555fd73cfbdd`, `diag326.sh` `fb48c6ef741dacc853827136a4a0e299`),
same SIF (`63a532b9732f84e59e7b1349065f1323`), 20 mm floor, `-DJUGLET_ORIG`, three labels: `jug_GTctrl`,
`jug_SWAPr1`, `jug_SWAPr2` (the last two are the same tree twice — they returned **identical** numbers, so the
harness is deterministic here). Outputs in `artifacts/pota327/swap/`, parser `.scratch/pota-repro/t327/parse_bar4.py`
-> `artifacts/pota327/swap/bar4_pairs.json`.

**The five formerly-failing pairs at GT** (`dot_med_d3` = median n·n over the strict-gate correspondence set,
+1 = the two walls agree; n = that set's size):

| pair | gap mm | ctrl dot / n (neg) | swap dot / n (neg) | strict n_dot07 | verdict |
|---|---|---|---|---|---|
| 1-2 | 1.1030 | −0.896 / 10 (10) | **+0.704 / 13** (0) | 7 | PASS |
| 1-9 | 2.1244 | −0.945 / 8 (8) | **−0.039 / 7** (4) | 0 | **FAIL** |
| 2-5 | 2.9096 | −0.991 / 1 (1) | **+0.948 / 1** (0) | 1 | PASS |
| 6-7 | 0.3570 | +0.106 / 16 (6) | **−0.183 / 15** (10) | 0 | **FAIL** |
| 7-9 | 1.7941 | −0.674 / 4 (4) | **+0.708 / 3** (0) | 2 | PASS |

Same-wall reference pairs, which the swap must not touch: 1-4 +0.786 -> +0.786, 1-8 +0.971 -> +0.971,
2-9 +0.991 -> +0.971, 3-5 +0.987 -> +0.987. Pairs with no correspondence are unchanged (−1.000/0): 1-5, 1-6,
3-7, 4-5, 4-6, 5-9, 7-8, 8-9; the only other move is 6-8, which gains one inlier (−1.000/0 -> +0.637/1).

**The bar is met on 3 of 5, and fails on 1-9 and 6-7.** Bar 4's criterion is all five at ≥ +0.7 with strict-gate
inliers > 0; 1-9 lands at −0.039 with four of seven correspondences negative and no strict inlier, 6-7 at
−0.183 with ten of fifteen negative and no strict inlier. Both are much closer to zero than the control, and
both gaps shrank (1-9 2.124 -> 0.998 mm, 6-7 0.357 -> 0.809 mm), so the swap is doing something on all five —
it is not sufficient on two.

**The swap really took effect (the harness's own per-piece rows, not my bookkeeping).** Columns `bl_r_med`
(radius of the loaded `Breakline_0` about the piece's own aligned axis), `n_radial_pos_frac`, `d_sur0_med`,
`r_sur0_med`, `r_sur1_med`:

| piece | ctrl `bl_r_med / frac / d_sur0 / r_sur0 / r_sur1` | swap |
|---|---|---|
| 2 | 16.777 / 1.00 / 0.329 / 16.897 / 15.184 | 15.253 / 0.00 / 0.313 / 14.992 / 16.957 |
| 6 | 16.654 / 1.00 / 0.294 / 16.795 / 14.531 | 14.506 / 0.00 / 0.314 / 14.498 / 16.846 |
| 9 | 16.798 / 1.00 / 0.289 / 16.858 / 15.230 | 14.905 / 0.17 / 0.302 / 14.778 / 16.919 |

The line moved to the other wall, stayed on its own surface (d_sur0 stays ~0.3 mm), and the loaded line's
radial sign flipped. Untouched pieces 1/5/7 have identical rows in ctrl and swap.

**Why two pairs still fail — the wall side is no longer the residual; the stored normal sign is.**
`.scratch/pota-repro/t327/blnormals327.py` reads the sign of every exported line's stored normals against the GT
radial direction (fraction outward, mean n·r̂): `Bl0` **is exactly the wall side** on 9/9 (all three offenders'
`Bl0` mean n·r̂ = +0.987 P2, +0.973 P6, +0.989 P9 — outward, because they ride the outer wall), but the two walks
do **not** share a per-piece sign convention: `Bl1` is inward on 1, 2, 6, 9 and **outward on 3, 4, 5, 7, 8**
(P7: frac 0.983 outward). The two-walk writer stores whatever sign its surface carried; nothing normalises it
to a slot-0 (interior) convention. A slot swap therefore moves the geometry but cannot guarantee that the two
lines' stored normals agree at every pairing. Locally (`pairprobe327.py`, placement convention verified to
reproduce the harness `gap_min` exactly as `inv(T_y) T_x`): after the swap, piece 1's matched points are clean
inward (−0.93..−1.00) and piece 9's swapped-in line runs −0.74..+0.07 (mixed), while piece 6's matched points
are clean inward and **piece 7's untouched line** swings −0.80..+0.61 across zero at both ends of the matched
run — i.e. in both failing pairs the mixed-sign line is the partner, not the piece I swapped.
Bar 4b tests that directly.


### Bar 4b — the sign probe: the residual is per-point, not a per-piece convention

**Why this probe.** Bar 4's two failures are not on the piece whose wall I swapped. `Bl1`'s stored normal sign is
inward on 1/2/6/9 but outward on 3/4/5/7/8 (`phases` in `blnormals327.py`), so I built three more trees from
`juglet_SWAP` on the same copies — `juglet_SWAPneg` (Bl0 normals negated on 2, 6, 9), `juglet_SWAPneg7`
(negated on 7 only), `juglet_SWAPnegall` (all four) — negating only PCD columns 4-6 and leaving every coordinate
byte-identical (verified: the x y z digest of P6 Bl0 is `40e34751ab7414f45de503bb7a186250` before and after).
Job **34690603** on the same run dir, 18 s, **COMPLETED 0:0** (it finished before the withdrawal I sent landed;
its outputs are the three `out/diag_jug_NEG*.txt` in `artifacts/pota327/swap/`, parser
`.scratch/pota-repro/t327/parse_bar4b.py`).

| pair | ctrl | swap (as is) | NEG (2,6,9) | NEG7 | NEGALL |
|---|---|---|---|---|---|
| 1-2 | −0.896/10 | **+0.704/13** | −0.704/13 | +0.704/13 | −0.704/13 |
| 1-4 | +0.786/9 | +0.786/9 | +0.786/9 | +0.786/9 | +0.786/9 |
| 1-8 | +0.971/19 | +0.971/19 | +0.971/19 | +0.971/19 | +0.971/19 |
| 1-9 | −0.945/8 | **−0.039/7** | +0.039/7 | −0.039/7 | +0.039/7 |
| 2-5 | −0.991/1 | **+0.948/1** | −0.948/1 | +0.948/1 | −0.948/1 |
| 2-9 | +0.991/4 | +0.971/4 | +0.971/4 | +0.971/4 | +0.971/4 |
| 3-5 | +0.987/3 | +0.987/3 | +0.987/3 | +0.987/3 | +0.987/3 |
| 6-7 | +0.106/16 | **−0.183/15** | +0.183/15 | +0.183/15 | −0.183/15 |
| 7-9 | −0.674/4 | **+0.708/3** | −0.708/3 | −0.708/3 | +0.708/3 |

`dot_med_d3/n_d3`. `gap_min` is **identical in all four variants** on every pair (1-2 0.514, 1-9 0.998,
2-5 1.539, 6-7 0.809, 7-9 0.945), which is the control that the negation touched only signs, and it also shows
the correspondence set is geometric (`MakeCorWOBuildTree`, `reconstruction.cpp:341-366`: kd-nearest on points,
normals only read), so a per-piece flip can only mirror the median.

- **No per-piece sign convention can pass 1-9 or 6-7.** Every variant lands on ±0.039 and ±0.183 — the
  reflection of the same mixed set, 3-4 of 7 and 5-10 of 15 correspondences on the wrong side. The three pairs
  that pass pass with the **unnegated** swapped tree, so the swapped-in walks of 2 and 9 already carry the right
  sign for those pairings (negating them breaks 1-2, 2-5 and 7-9 — a useful control, not an improvement).
- So the residual is **spatially varying sign inside one line**, not a convention per piece or per bundle: on
  piece 9's swapped-in walk the section mating with piece 7 is consistently inward, the section mating with
  piece 1 is not (local n·r̂ −0.74..+0.07 across eleven tested points, `pairprobe327.py`), and the same walk is
  17% outward overall. That is what storing the sampled *surface* normal per point does when a walk runs along a
  rim: the normal's relation to the cavity turns along the loop, and nothing in the writer re-signs it against
  the wall it is supposed to face.
- For 6-7 neither piece's sign fixes it (5 of 15 disagree whichever side is flipped), so on that pair the two
  lines' normals differ at the mating section for a reason the wall side no longer explains — the next thing to
  measure there is whether either walk runs on a chamfer/rim rather than the flat of its wall.

**What this means for the fix, stated as narrowly as the evidence allows.** The wall-side filing is confirmed
as a real defect (bars 1-3) and as causally load-bearing (bar 4: 3/5 pairs, all five moved). It is **not
sufficient**: a line whose stored normals are mixed along its own loop will still fail a normal-agreement gate
after the wall is right. Ticket 328 should carry both halves: file by the wall, and re-sign (or re-derive) the
exported line normals per point against that wall instead of storing the sampled surface normal.


### Bar 5 — renders, eye-checked

Three figures, one per mis-filed piece, in `artifacts/pota327/renders/` (script
`.scratch/pota-repro/t327/render327.py`, built only from the t66 exports and the GT axis — no ORIG or GT
geometry is drawn into the diagnostic itself, the key only defines the radial coordinate, same instrument as
bars 1 and 3):

- `artifacts/pota327/renders/juglet_piece_2_wall_side.png`
- `artifacts/pota327/renders/juglet_piece_6_wall_side.png`
- `artifacts/pota327/renders/juglet_piece_9_wall_side.png`

Each is four panels: top row is a 3D view about the GT axis, bottom row is the unrolled radial view
(x = height along the GT axis, y = radius from it) before (left) and after the copy-swap (right). Grey
`Surface_0`, blue `Surface_1`, red `Breakline_0`.

Eye check, piece by piece (the radial row is where a wall-side error is unambiguous):

- **Piece 2** — before, the grey sheet fills r 16.5-17.5 and every red dot sits on it; the blue sheet sits at
  14.3-15.5, ~2 mm in. After, the grey sheet is at 14.3-15.5 and the red line is on it. No red dot is left on
  the outer sheet. Radial range 14.0-17.7 mm, height −532 to −523.
- **Piece 6** — a tall curved patch, −282.5 to −262.5 mm high, inner sheet 13-15, outer 15-17.5; before the red
  line runs along the **top rim of the outer sheet**, after it runs along the top rim of the inner one (r 13.4-15.5).
  This is the piece whose exported normals are incoherent (|mean unit n| = 0.017 / 0.041), and the renders show
  why the vote had to fall back on face size: both faces are nearly edge-on to the radial direction.
- **Piece 9** — before, grey 16.6-17.1 with the red line exactly on it, blue 14.0-15.4. After, grey is the inner
  sheet and the red line rides it — but at both ends the red dots climb to 15.9-16.5 mm, i.e. the outer-fringed
  part that `.scratch/pota-repro/t327/blnormals327.py` counts as 17% of that walk (mean n·r̂ −0.680). That fringe
  is visible, not inferred, and it is the line that fails pair 1-9 after the swap.

So the wall side is visually confirmed on all three: the exported `Surface_0` is the exterior sheet and
`Breakline_0` is drawn on it, and flipping the filing on a copy puts both back on the interior sheet.


### Verdicts, and what is left to the fix

| bar | verdict |
|---|---|
| 1 | **PASS** — the split is exactly 2/6/9 outer; Bl0 rides the foreign wall on 9/9, so the defect is upstream of the line. |
| 2 | **PASS** — the rule is `classifyAndOrderPaper234` (`mesh_processing_headless.cpp:3688`, called :4008), a two-input vote; on 2 and 9 the staged axis line is on the wrong side of the wall, on 6 the normals it reads were inverted (`Normals flipped: true`, the only piece of nine), and nothing checks the answer against geometry. |
| 3 | **ANSWERED** — the pre-1031 geometry survives for t30 and t41 only; the inverted set there was {4,7}, piece 6 was right then, and pieces 2/9 produced no surfaces at all on the vertex-dump clouds. The misfiling set moved with the 1031 regen + chain change. |
| 4 | **FAIL at its criterion** (3 of 5: 1-2 +0.704, 2-5 +0.948, 7-9 +0.708 pass; 1-9 −0.039 and 6-7 −0.183 fail, no strict inlier on either). Every one of the five moved off the control, and the wall side is causally load-bearing — but not sufficient. |
| 4b | **Residual located** — no per-piece sign flip reaches the bar (all variants land on ±0.039 / ±0.183); the failures are sign mixing *inside* one line, so the fix needs both halves: file by the wall, and re-sign the exported line normals per point against that wall. |
| 5 | **PASS** — three before/after renders, eye-checked; the fringe that fails 1-9 is visible on piece 9's swapped-in line. |

**Jobs, sacct-recorded** (`ssh spartan sacct -j <id> --format=JobID,State,ExitCode`):
`34687732` **COMPLETED 0:0** (bar 4, 44 s, partition sapphire);
`34690603` **COMPLETED 0:0** (bar 4b, 18 s — it ran to completion before my withdrawal landed).
Both under `/data/gpfs/projects/punim2657/SfSpp/runs/20261110-2028_1b131dc_t327-swap/` with `run.json`,
`submit.sbatch`, `logs/`, `out/`; the sign-variant trees and `work/setup_neg.sh`, `work/submit_neg.sbatch`
live there too. Nothing outside that run dir was written on Spartan.

**Inputs untouched** (listed before and after; the after-listing is this one, and `find -newermt
"2026-11-10 20:00"` returns nothing under any of the four trees):
t66 bundle `20261103-1332_fab76f5_t66-admitsign-default/outU_jug/geom` = 36 files (`Juglet_Piece_N.{S0,S1}`
PLY + `{Bl0,Bl1}` PCD, N=1..9); `Dataset/Axes/Juglet` = 9 `_Axis.xyz` + `README-not-a-reference.md`;
`Dataset/Juglet_GT` = 9×(`_T.txt`, `_Axis.xyz`) + `Juglet_simple_graph.txt` + `README-axes.md`;
`sfs_main/original_samples/SfS_pp/Point` = `Pot_A..Pot_J` + `MANIFEST_released.tsv`/`MANIFEST_derived.tsv`/`README.md`.
(The Juglet_GT axis files carry mtime 2026-11-10 07:23 from the ticket-322 work recorded in AGENTS.md, i.e.
before this session; nothing in this ticket touched them.) No ORIG or GT points entered any diagnostic input:
the GT key only defines the radial coordinate in bars 1/3/5 and the pair placement in bar 4, and the only
geometry handed to the harness is the t66 export (and its copies).

**Scripts** (all under `.scratch/pota-repro/t327/`): `census327.py`, `census327_old.py`, `classifier327.py`,
`blnormals327.py`, `pairprobe327.py`, `check_radii.py`, `parse_bar4.py`, `parse_bar4b.py`, `render327.py`,
`setup_swap.sh`, `submit_swap.sbatch`, `setup_neg.sh`, `submit_neg.sbatch`.
**Data kept** under `artifacts/pota327/`: `geom/`, `gt/`, `dsaxis/`, `old_t30/`, `old_t41/`, `swap/`,
`renders/`, and the JSONs `census_bar1.json`, `census_bar3_old.json`, `classifier_bar2.json`.

## Comments (lead write-back, 2026-11-10 — verified independently, not taken on report)

**Verdict: the diagnosis landed; bar 4's own bar FAILED by design (3/5), and that failure is the useful
result — swapping the slot alone is not enough, the exported line's normals are also wrong.** Ticket 328 is
amended accordingly.

**Verification (lead, this session) — `verified: <what> -> <value>`:**
- `verified: awk over the run's own GTPAIR lines, GTctrl vs SWAPr1/SWAPr2 ->` 1-2 −0.896→+0.704 (10→13
  correspondences), 1-9 −0.945→−0.039 (8→7; 4 of 7 negative), 2-5 −0.991→+0.948, 6-7 +0.106→−0.183 (10 of
  15 negative), 7-9 −0.674→+0.708; same-wall refs unmoved 1-4 +0.786, 1-8 +0.971, 2-9 +0.991→+0.971,
  3-5 +0.987. So 3 of 5 pass — the worker's table is exactly the file, no rounding drift.
- `verified: awk over NEG7/NEG/NEGALL ->` negating piece 7 alone gives 6-7 +0.183 (5/15 still negative) and
  flips 7-9 to −0.708; negating 2/6/9 flips 1-2 to −0.704, 2-5 to −0.948, 7-9 to −0.708; 1-9 stays
  ±0.039 under every variant. Confirms reflections, i.e. the sign is mixed WITHIN a line, not per piece.
- `verified: mesh_processing_headless.cpp:3688-3730 ->` `classifyAndOrderPaper234` votes
  `satA = inFrac[0]*n0 + (1-inFrac[1])*n1`, `satB = (1-inFrac[0])*n0 + inFrac[1]*n1`, swaps only when
  `satB > satA` strictly; `inFrac` is computed against the ray to the SFS_AXIS_FILE line (:3705-3718).
- `verified: mesh_processing_headless.cpp:4006-4008 ->` the classifier runs after
  `std::sort(clusters.begin(), clusters.end(), myobject3)` — on a degenerate vote (both `inFrac` ~0 or
  equal) nothing swaps, so the denser face stays in slot 0. The filing has no geometric cross-check.
- `verified: artifacts/pota327/classifier_bar2.json ->` piece 2 DS-vs-GT axis angle 87.8°, piece 9 73.3°;
  re-voting with the GT axis gives `interior_gt = face1` on both (piece 2: inFrac_S0 0.0 / inFrac_S1 0.999;
  piece 9: 0.0 / 0.951) — same rule, right answer, wrong axis. Piece 6: axis is fine (13.3°), vote says
  face1, yet the shipped Surface_0 is the outer wall — the vote is inverted because the normals were flipped
  upstream (`Normals flipped: true` is printed for piece 6 only).
- `verified: artifacts/pota327/census_bar1.json ->` side_S0 = outer exactly on 2, 6, 9 (r_mean S0/S1 mm
  17.02/14.75, 16.93/14.59, 17.21/15.22), inner on the other six; `bl0_to_S0` 0.28-0.62 mm against
  `bl0_to_S1` 1.83-2.49 mm on 9/9 — Breakline_0 rides Surface_0, so the choice was made upstream in the mesh
  stage and the edgeline inherits it; per-wall densities 0.543-0.560 pts/mm on every piece, so density does
  not explain the split. Matches the lead's independent September-style measurement (same three pieces).
- `verified: eye-check of artifacts/pota327/renders/ (copied to C:/PR/artifacts/pota327/renders/) ->` piece 2:
  before, the red Bl0 dots sit on the grey Surface_0 sheet at 16.5-17.5 mm; after, they sit on the inner
  sheet at 14.4-15.5 with nothing left outside. Piece 9: same, except the line's two ends climb to
  15.5-17.0 — the fringe that fails 1-9, visible rather than inferred.
- `verified: sacct 34687732, 34690603 ->` both COMPLETED 0:0 (44 s, 18 s).

**What this means, stated plainly.** The slot decision is made by voting on which face's normals point back
at the axis line; the vote trusts that line, and on this 33 mm vessel the line can sit on the wrong side of
the wall (pieces 2, 9) or the normals can already be inverted (piece 6). When the vote degenerates, the
code silently keeps the denser face — no check against geometry. And even with the face filed correctly, the
exported breakline carries a sampled surface normal that flips sign inside one line, so 1-9 and 6-7 still
read as opposing rims. Two independent defects, both upstream of the assembler.

**Scope ruling.** Bars 1-3 and 4b are the ticket; bar 4's 3/5 is recorded as the finding, not as a pass.
Handed to ticket 328 as a four-part cure. The axis half overlaps ticket 325's territory (the axis finder
wrote a wrong-side line for 2 and 9) — noted there, not fixed here.
