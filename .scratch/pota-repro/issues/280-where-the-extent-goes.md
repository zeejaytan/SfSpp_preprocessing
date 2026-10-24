# 280 — Where does the extent family lose its coverage: boundary set or walk?

Answers: E1
Status: results-in (Phase 0 reproduces the 272 numbers on a d1b61cb build; class B dominates by the definition, but Phase 2 shows no detector setting recovers the arc — the reference runs through the smooth interior of the surface we kept)
Working in: C:/PR/worktrees/sfs/280
Needs-eye: no

## Why

Tickets 278 and 279 closed the Pot C 03 question (partition mismatch: their second surface is the base
disc, ours an exterior wall that is in neither of their surfaces). The next family still unattributed is
the **extent** one: on Pot H 02 and H 10, Breakline_1 covers only ~69-73% of the reference and ticket 278
showed the uncovered reference dots sit on surfaces we DID keep (34 of 35 on H02, 17 of 21 on H10, rest
within 2 mm of no mesh point). So the geometry is there and the line stops short. Nobody has yet said at
which step it stops short.

This ticket splits that loss into three named causes on four lanes. It changes no defaults and writes no
C++.

## Phase 0 — score the four lanes on the shipped binary

Pot H 02 and H 10, both lanes, on the Phase 3a sheets from ticket 276 (theta 3.4, md5s recorded there),
with SFS_AXIS_FILE set and the classify line confirmed (ticket 277 trap). Defaults only: no SFS_* override.

Build from pushed commit **d1b61cb** with the repo's own script; do not reuse the 67ff3d7 binary (it
predates the 274 neighbour clamp).

Report per lane: n / median / coverage / jumps / maxstep, and author-side coverage. Expected starting
point, from the 272 probe at theta 4: H02 Bl1 0.74 / 73.0, H10 Bl1 0.64 / 72.8. If Phase 0 already clears
both bars, say so and stop — the family would have been a stale-binary artefact.

## Phase 1 — the split (the only new measurement here)

For each lane take the reference dots our line does NOT cover (nearest distance > 2 mm) and put each into
exactly one class:

- **(A) SURFACE EXTENT** — no surface material within 1 mm of that reference dot (test against the
  Surface_0/Surface_1 .xyz the edge stage read).
- **(B) DETECTOR** — surface material is there, but the extracted boundary set has no point within 1 mm.
  Use the pre-walk boundary cloud (the PCD written at edgeline_extraction_headless.cpp:1604-1605), not the
  final line.
- **(C) WALK** — the boundary set does contain a point within 1 mm, so the ordering or the stop rule
  dropped it.

Report counts and the arc length each class accounts for, per lane. Also report where along the rim each
class sits (index range over the reference dots) so the three are not averaged into one number.

## Phase 2 — only if class (B) dominates

On the one worst lane, sweep the boundary detector's two knobs on that sheet — radius 2 / 4 / 6 / 8 mm and
angle 60 / 90 / 108 / 170 deg — and report how many of the uncovered reference dots gain a boundary point
within 1 mm at each setting, with the total boundary-point count so a setting that simply returns
everything is visible as such. Report only; change no default.

## Pre-registered reading

- (C) dominates -> the family is a walk/stop problem; stop and report, a walk ticket is separate.
- (B) dominates -> the family is the boundary detector's operating point; Phase 2 decides whether any
  honest setting exists.
- (A) dominates -> the surface stops short and the family is an extent problem; stop and report.
- A mix -> report the split as measured; do not pick a winner.

Do not retune theta, do not touch the walk defaults, do not build third-surface support.

## Constraints

- Edge stage only; frozen sheets; no mesh rebuild beyond Phase 0's needs.
- Run directory `/data/gpfs/projects/punim2657/SfSpp/runs/<YYYYMMDD-HHMM>_<git7>_p280-extent/` with one
  appended index row (verdict and human_note empty).
- Do not touch C:/PR/worktrees/sfs/275, .../276 or .../279.
- Quote every number from a file.

## Results

**Status: results-in.** Phase 0 does not clear the bar on either Breakline_1 lane on the d1b61cb build, so
the family is not a stale-binary artefact. Phase 1 puts every uncovered dot in class (B) by the ticket's
definition and none in (A), and the pre-registered reading sends that to Phase 2 — where the sweep finds no
honest setting that recovers a single dot. The following probe explains why: the uncovered arc sits in the
smoothest **interior** of the surface we kept, so the reference line there is not a boundary of that surface
at all. The detector is behaving correctly; the difference is which faces the kept region spans.

### Build — and the trap it exposed

- `git archive` of the pushed commit d1b61cb (2531 files) into
  `/data/gpfs/projects/punim2657/sfs-vote-248/build-d1b61cb/src` (job 33742188).
- **The repo's own entry point does not compile the live edge source.** `build.sh --target nurbs` builds
  `original_nurbs_preprocessing/edgeline_extraction_headless.cpp` (build.sh:180 `target_src_dir`), which at
  d1b61cb is md5_lf `3273d87ee09fd2e567cbeaddfa824890`, 3721 lines, `STOP-267`=0 `FULL-263`=0 `VOTE-247`=0 —
  the pre-247 legacy duplicate (last functional commit e31be21, ticket 237; it has no `armFace218` at all).
  The dry run prints it: `source : .../build-d1b61cb/src/original_nurbs_preprocessing`.
  The live source is the root copy (root CMakeLists.txt:38), md5_lf `8264da3647d048e67d983edfe810b59d`,
  3725 lines, `STOP-267`=4 `FULL-263`=3 `VOTE-247`=6 `WALK-275`=0.
- So the build ran **build.sh's own container recipe against the live root project**:
  `apptainer exec --bind /data:/data pcl_191_nurbs.sif bash -c "cmake -S <src> -B <src>/build/edge-release -DCMAKE_BUILD_TYPE=Release -DCMAKE_EXPORT_COMPILE_COMMANDS=ON && make -C <src>/build/edge-release -j8 EdgeLineExtractionHeadless"`
  (Release = `-O3 -DNDEBUG`, per `logs/cmake_facts.txt`). Output binary md5 **62ddd28f4476e9cdf5b27cf0ee01c2f0**;
  `strings` counts `STOP-267`=4, `FULL-263`=3, `VOTE-247`=6, `WALK-275`=0. That md5 is bit-identical to the
  pristine control binary ticket 275's Phase 0 built from the same source, which is a free reproducibility
  check on both builds.

### Phase 0 — the four lanes on the d1b61cb build (job 33742223, four runs, all EXIT=0)

Defaults only (`SFS_STOP_NOFRESH` unset -> R=12 mm, `SFS_FULL_WALK` on, `SFS_VOTE_ORDER` on). Sheets are the
ticket 276 Phase 3a sheets at theta 3.4, unchanged before and after every run (recorded in
`out/<TAG>/sheets_pre.md5` and `sheets_post.md5`).

| piece | lane | n | med | cov (ours->author) | jumps >10 mm | maxstep | acov (author->ours) | 272 probe at theta 4 | bar |
|---|---|---|---|---|---|---|---|---|---|
| Pot H 02 | Bl0 | 152 | 0.582 | 100.00 | 0 | 3.569 | 100.00 | (not in the family) | PASS |
| Pot H 02 | Bl1 | 138 | 0.864 | **73.19** | 0 | 3.736 | 74.45 | 0.74 / 73.0 | **FAIL on cov** |
| Pot H 10 | Bl0 | 98 | 0.661 | 100.00 | 0 | 3.633 | 100.00 | (not in the family) | PASS |
| Pot H 10 | Bl1 | 92 | 0.641 | **72.83** | 0 | 4.571 | 77.27 | 0.64 / 72.8 | **FAIL on cov** |

Both Bl1 lanes reproduce the 272 numbers on a binary built from the pushed commit (median inside the bar by
3x, coverage short by 17 points), so **Phase 0 does not end the ticket**. Bl0 is perfect both ways on both
pieces: the family is only ever Breakline_1.

Sheet md5 (Surface_0 / Surface_1): Pot H 02 `9de492c98873204572919961b7d7dba8` / `638a22194203c6b356e52a066c656ab3`;
Pot H 10 `07ba2430d3ed975b8df20d29569dbe03` / `ee79326ee6c6ef45ca1447b4d3a7699f`. Axis files
`f90e8c18f121ab25f7c2b509624e7b26` (Pot H 02) and `723002c8925cc7bb4ce1705946d1429b` (Pot H 10).

**On the ticket's axis guard:** the edge stage reads the axis from `Dataset/Axes/<stem>_Axis.xyz`
(edgeline_extraction_headless.cpp:1309) and has **no `SFS_AXIS_FILE` string at all** (`grep -c` = 0 in the
d1b61cb source) — that env var belongs to the mesh stage. The guard here is that no run printed
`[LOOP-SELECT] axis missing/unreadable` (0 occurrences over 8 LOOP-SELECT blocks = 4 runs x 2 calls),
plus the axis md5s above.

### The per-pot temp_edge trap, and how lane 0 got its boundary set

`Temp/Temp_edge/<Pot>/` is per pot (data_path.h:84-87), not per surface, so the lane-1 call overwrites lane
0's boundary artifacts. Four runs were made instead of two: per piece a **normal** run and a **dupS0** run
whose `Surface_1.xyz` is a copy of `Surface_0.xyz`, so lane 0's artifacts survive on disk. Validation on both
pieces, comparing positions row by row: lane 0 of the normal run equals lane 0 of the dupS0 run
(n 152 / 98, `max|dxyz|` = **0.000000**), and inside the dupS0 run lane 0 equals lane 1 (`max|dxyz|` = 0.000000).
The lane-0 boundary sets used below are therefore the real ones. PCD files still differ byte-wise in normals
and curvature only, as in ticket 275.

### Phase 1 — the split (35 + 20 uncovered dots, A = 0)

Reference lanes: Pot_H_Piece_02_Breakline_1 n=137 arc 245.168 mm; Pot_H_Piece_10_Breakline_1 n=88 arc
155.505 mm (author dots are resampled on a 1.800 mm grid, so arc length is well defined).

| lane | uncovered | A | B | C | B with a *raw* boundary point <=1 mm | B arc owned | B span | B index range | share of reference |
|---|---|---|---|---|---|---|---|---|---|
| Pot H 02 Bl0 | 0 | 0 | 0 | 0 | - | 0 | 0 | - | - |
| Pot H 02 Bl1 | 35 | **0** | **35** | 0 | **0** | 61.200 mm | 61.200 mm | 32-66 | 24.96% of 245.168 mm |
| Pot H 10 Bl0 | 0 | 0 | 0 | 0 | - | 0 | 0 | - | - |
| Pot H 10 Bl1 | 20 | **0** | **19** | **1** | **0** | 32.400 mm | 32.400 mm | 40-58 | 20.84% of 155.505 mm |

The single (C) dot on Pot H 10 lane 1 is index 74: the walk-input boundary set has a point 0.335 mm away, and
the final line passes 2.277 mm away — the only dot in the whole family where the boundary set carried the
stretch and the line did not.

What class (B) looks like numerically on those dots:

- **Surface is there, and it is the lane's own sheet.** Nearest distance to a surface point: 0.037-0.485 mm
  (H02) and 0.066-0.485 mm (H10). All 35 / all 20 dots are nearer `Surface_1` than `Surface_0`
  (0 dots nearer S0), i.e. the geometry is present on the very sheet lane 1 traces.
- **The boundary set and the final line are the same curve there.** Distance to the walk-input bag
  `boundaryImproved.pcd`: 2.046-6.710 mm (H02), 1.801-5.873 mm (H10); distance to the final line over the
  same dots: 2.046-6.710 mm and 1.801-6.464 mm. So this is not a boundary set that the walk then abandoned
  (that would be class C).
- Nothing in class (A): zero dots anywhere lack material within 1 mm.

By the ticket's definitions **(B) dominates on both failing lanes and (A) is empty**, which per the
pre-registered reading hands the family to Phase 2.

### Phase 2 — the detector sweep (run because (B) dominated)

The detector was reimplemented in numpy (radius neighbours of the sheet, tangent-plane angle of every neighbour
using the sheet's own normals from the `.xyz`, boundary when the largest angular gap exceeds the threshold)
and **validated against the shipped `boundary.pcd`** on the lane's own sheet at the shipped setting r=4 mm /
a=108 deg:

- Pot H 02 lane 1: mine 482 points vs shipped 484; mine->shipped med 0.000 mm max 0.830 mm; shipped->mine
  med 0.000 max 0.695 mm.
- Pot H 10 lane 1: mine 295 vs shipped 298; med 0.000 mm; max 2.515 / 2.469 mm.

That is the shipped detector reproduced, so the sweep is measuring the real thing. Covered uncovered dots
(a dot counts when the reimplemented boundary set of its nearer sheet has a point within 1 mm); the last
column is the total boundary-point count over both sheets, so a setting that simply returns everything is
visible as such.

| setting | Pot H 02 lane 1 | Pot H 10 lane 1 | boundary points, both sheets (H02 / H10) |
|---|---|---|---|
| r=2 mm, a=60 deg | 0/35 | 1/20 | 1659 / 1122 |
| r=2 mm, a=90 deg | 0/35 | 1/20 | 1096 / 790 |
| r=2 mm, a=108 deg | 0/35 | 1/20 | 934 / 690 |
| r=2 mm, a=170 deg | 0/35 | 1/20 | 393 / 242 |
| r=4 mm, a=60 deg | 0/35 | 1/20 | 1648 / 1105 |
| r=4 mm, a=90 deg | 0/35 | 1/20 | 1085 / 775 |
| r=4 mm, a=108 deg (shipped) | 0/35 | 1/20 | 928 / 670 |
| r=4 mm, a=170 deg | 0/35 | 1/20 | 312 / 180 |
| r=6 mm, a=60 deg | 0/35 | 1/20 | 1647 / 1099 |
| r=6 mm, a=90 deg | 0/35 | 1/20 | 1082 / 771 |
| r=6 mm, a=108 deg | 0/35 | 1/20 | 924 / 667 |
| r=6 mm, a=170 deg | 0/35 | **0/20** | 292 / 162 |
| r=8 mm, a=60 deg | 0/35 | 1/20 | 1645 / 1099 |
| r=8 mm, a=90 deg | 0/35 | 1/20 | 1082 / 771 |
| r=8 mm, a=108 deg | 0/35 | 1/20 | 921 / 667 |
| r=8 mm, a=170 deg | 0/35 | **0/20** | 273 / 154 |

**No honest setting exists.** Not one uncovered dot on Pot H 02, and on Pot H 10 only the one dot the shipped
set already carried, gains a boundary point at any of the sixteen settings — including the loose ones
(a=60 deg returns 3-6x more boundary points and still covers nothing). No default was changed, and none
should be.

### Why — the dots are in the smoothest interior of the kept surface

The estimator's own criterion, evaluated at the surface point nearest to each uncovered dot (largest angular
gap; a point is a boundary when it exceeds 108 deg):

| lane | r | median gap | p90 | max | dots under 108 deg |
|---|---|---|---|---|---|
| Pot H 02 Bl1 | 2 mm | 25.4 | 29.9 | 32.9 | 35/35 |
| Pot H 02 Bl1 | 4 mm | 8.9 | 10.4 | 12.1 | 35/35 |
| Pot H 02 Bl1 | 6 mm | 4.8 | 6.9 | 10.4 | 35/35 |
| Pot H 10 Bl1 | 2 mm | 25.5 | 31.9 | 162.4 | 19/20 |
| Pot H 10 Bl1 | 4 mm | 9.9 | 11.8 | 162.4 | 19/20 |
| Pot H 10 Bl1 | 6 mm | 7.1 | 11.2 | 161.1 | 19/20 |

(Angles in degrees. The one Pot H 10 outlier is the single (C) dot.) Every uncovered dot has surface
neighbours all round it at 1 mm: they lie in the **interior** of `Surface_1`, and the detector is right not
to call them boundary points.

And it is not a fold that region growing welded across: the surface normals within 1 mm of the nearest
surface point disagree by

| lane | uncovered dots (median p90 / max) | covered dots (median p90 / max) | neighbours >45 deg off |
|---|---|---|---|
| Pot H 02 Bl1 | 6.42 / 11.44 deg | 18.19 / 25.43 deg | 0.000 of neighbours, both groups |
| Pot H 10 Bl1 | 7.24 / 12.53 deg | 18.46 / 31.88 deg | 0.000 of neighbours, both groups |

— the uncovered stretch is the **smoothest** part of the surface, three times smoother than where our line
does run. Neither a boundary nor a crease: the reference line there follows something the region's own
geometry does not mark.

Mechanism as measured: our `Surface_1` covers the reference rim with a full 1 mm neighbourhood, so the
region spans past that rim and its boundary lies 2-6.7 mm away on a different course. Consistent with that,
our lane-1 line is **longer** than the reference (271.926 mm of chain length, 143 resampled dots, against a
245.168 mm reference on H02; the shipped run never printed `[STOP-267]` on any of the four lanes, so no
stop fired). This is not a line that stops short — it is a different contour of a larger region.

### Per-lane verdict (acceptance)

- **Pot H 02 Breakline_1 — (B) by the definition, but the detector is not the lever.** 35 uncovered dots,
  61.200 mm (24.96%) of the reference, indices 32-66, all with surface within 0.485 mm on `Surface_1` and no
  boundary point within 2.046 mm. Phase 2: 0/35 recoverable at any of 16 detector settings; the arc sits in
  the smooth interior (median max gap 8.9 deg at 4 mm, normals agreeing to 6.42 deg). The loss is decided
  upstream of the detector, in which faces the kept region spans.
- **Pot H 10 Breakline_1 — same class, same conclusion.** 19 (B) + 1 (C) uncovered dots, 32.400 mm (20.84%),
  indices 40-58 and 74; 1/20 recoverable at any setting; median max gap 9.9 deg, normals agreeing to 7.24 deg.
- **Pot H 02 / Pot H 10 Breakline_0 — not in the family.** 0 uncovered dots, 100.00% coverage in both
  directions.

### What would overturn this reading

A detector setting inside the ticket's grid that recovers the arc (none of the sixteen does: 0/35 and 1/20),
or a surface whose boundary passes within 1 mm of the reference arc — which is exactly what "the reference
line is not a boundary of our region here" forbids; equivalently a normal jump at the uncovered dots, where
the measurement is 6.42 / 7.24 deg with no neighbour beyond 45 deg.

### Two corrections to the ticket's own wording

- Class (B) names "the PCD written at edgeline_extraction_headless.cpp:1604-1605". At d1b61cb those lines
  are `writeMatrix_to_XYZ_withNormals`, a writer helper. The pre-walk boundary set is the bag
  `Temp/Temp_edge/<Pot>/boundaryImproved.pcd` (:1282, the raw `boundary.pcd` snapped to unclustered points at
  2.5 mm), and it was used as the primary object with the raw `boundary.pcd` as the diagnostic. The snap
  changes coordinates only (same point count — 462/462, 484/484, 374/374, 298/298; rowwise offset med 0.000,
  max 0.693 mm on H02 and 2.433 mm on H10), and **no (B) dot had a raw boundary point within 1 mm either**,
  so the class does not depend on which of the two files is read.
- The edge stage does not consume `SFS_AXIS_FILE` (see Phase 0): the axis guard is the absence of
  `[LOOP-SELECT] axis missing/unreadable`.

### Job ledger

| job | name | state | exit | what |
|---|---|---|---|---|
| 33742188 | p280build | COMPLETED | 0:0 | archive d1b61cb, build.sh dry run, live root build -> binary 62ddd28f... |
| 33742223 | p280run | COMPLETED | 0:0 | four edge runs (H02/H10 x norm/dupS0), all EDGE_EXIT=0, sheets unchanged |
| 33742273 | p280p2 | COMPLETED | 0:0 | detector reimplementation + sweep + crease probe |

Run directory: `/data/gpfs/projects/punim2657/SfSpp/runs/20261024-1604_d1b61cb_p280-extent/`
(`a280.py`, `a280p2.py`, `a280p3.py`, `manifest.tsv`, `a280_lanes.tsv`, `a280_dots_*.tsv`, `a280p2_*/a280p3_*`
tables and logs, `out/<TAG>/`, `temp_edge/<TAG>/`, `run.json`).

## Acceptance

- Phase 0 table for the four lanes against the 272 numbers.
- Phase 1 split per lane, with counts, arc lengths and index ranges for classes A / B / C.
- One line per lane naming the dominant class, and the Phase 2 table if class (B) dominates.

## Evidence to report

- run directory and index row, commit built, binary md5s, sheet md5s
- the Phase 0 table, the Phase 1 table, the per-lane verdict line
- what would overturn the reading

## Lead verdict (2026-10-24)

**Accepted.** Phase 0 did its job first: a build from main at d1b61cb reproduces the 272 probe
to 0.01 mm (H02 Bl1 138 / 0.864 / 73.19, H10 Bl1 92 / 0.641 / 72.83, both Bl0 lanes 100.00
both ways, zero jumps), so this family is real and not a stale binary. The split is
unanimous and it is not the walk: of 35 uncovered reference dots on H02 Bl1 and 20 on H10
Bl1, class A is 0 and class C is 0 and 1, so the boundary set simply has nothing within 1 mm
of those dots and nothing fuzzy about ordering is at issue. No [STOP-267] line appears in any
of the four logs.

**The important result is the negative in Phase 2.** Sixteen honest detector settings (radius
2-8 mm x angle 60-170 deg, the estimator reimplemented in numpy and validated against the
shipped boundary.pcd at 482 vs 484 and 295 vs 298 points) recover 0 of 35 on H02 and 1 of 20
on H10 — the one recovered being the single C dot. Settings that return 1659 boundary points
recover nothing either. So this is NOT a detector operating point, and the ticket's own class
B label must not be read as "the detector needs tuning". The estimator is not failing; there
is no edge there to find.

**What the surface says instead.** At the nearest surface point the maximum angular gap is
8.9 deg median (max 12.1) on H02 and 9.9 (max 162.4, the C dot) on H10, against the 108 deg
threshold, and neighbour normals agree to 6.42 / 7.24 deg median where the covered dots
disagree by 18.19 / 18.46. The uncovered stretch is the SMOOTHEST part of Surface_1, not a
crease. Our lane-1 line is also LONGER than the reference (271.926 mm against 245.168 mm), so
this is not a line that stops short: it is a different contour, drawn on a region that spans
past the reference rim. That is the same family as ticket 279: **the extent of the kept region
is decided upstream, and the boundary pass traces whatever it is given.** Recorded in the
ledger as such; no default changed, no C++, no retune.

**Two ticket corrections accepted** (they were mine): the pre-walk boundary set that matters
is boundary.pcd (:1232) and the walk-input bag is boundaryImproved.pcd (:1282), not the helper
at :1604-1605; and the edge stage never reads SFS_AXIS_FILE (that variable is mesh-stage
only) — its axis guard is the absence of "[LOOP-SELECT] axis missing/unreadable" at :1317
plus the Dataset/Axes md5.

**Build trap, escalated separately (ticket 282, filed with this verdict).** The build.sh
target called "nurbs" compiles original_nurbs_preprocessing/edgeline_extraction_headless.cpp
— a pre-247 duplicate (3273d87e..., 3721 lines, STOP/FULL/VOTE all 0) — not the live root
source that CMakeLists.txt:38 actually builds. The worker built the live root project instead
and got a binary bit-identical to ticket 275's pristine control. Any earlier binary built
through that target is the wrong program.

**Next step named and cheap:** ticket 281 asks the only question left — at the uncovered arc,
is the reference rim interior to one cluster (region growing welded the rim face to its
neighbour, so growth owns it), or does it sit on a cluster boundary (a cluster was dropped or
merged away, so the merge owns it). Both answers already exist in the 276 Phase 3a dumps.
