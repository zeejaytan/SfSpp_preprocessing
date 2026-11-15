# 73 — Stop the refinement re-admitting the break face, and make the growth judge a turn over a real distance

**What to build:** two cures for the same defect, tested one arm at a time, after a read-only
attribution stage that says which one can matter. **Stage 0** records, for every off-lip
surface point on sherds 5-8, how it got into the interior patch — grown, merged, or added back
by the B-spline refinement — and prints the curvature range the gate actually sees. **Arm A**
(`SFS_REFINE_ADD_GATE`) stops the refinement adding a point the growth did not claim unless its
normal agrees with the nearest grown point within an angle measured in Stage 0. **Arm B**
(`SFS_GROW_BASE_MM`) makes the growth judge a candidate's turn against the surface a fixed real
distance back instead of against its immediate neighbour. **Arm C** runs both. A gate table, a
before/after render and five reading slugs close it.

**Why now (2026-11-15, conservator, verbatim):** "The thing putting the break face back is the
B-spline boundary refinement step, not the paper's cluster merge. On sherds 5, 6 and 8 that
step re-added almost every point the trim removed. And yes, staying at 3× is right, as long as
the growth rule measures the angle over a real distance and stops comparing only neighbour to
neighbour." Then: "write this up as ticket 73 and dispatch it using normal subagent".

**Answers:** U19 (does the pipeline put the Juglet back together), E1 (do our breaklines let
SfS find joins)

**Blocked by:** none. Reads ticket 72's cells and ticket 25's dump switch; writes two
default-off switches in the repo-root `mesh_processing_headless.cpp` only.

**Status:** ready-for-agent
**Working in:** to be set at dispatch
**Branch:** to be created at dispatch
**Worker:** unassigned

## Spec

### Given (measured facts this stands on — cite these, do not re-measure)

1. **The refinement re-admits what the trim removed, on three of the four sherds.** Counts from
   the 3x cells of ticket 72 — for each piece, `[ADMIT-SIGN-65] surface=0 admitted_in` minus
   `dup_rows` (the count that reaches the surface) in
   `/data/gpfs/projects/punim2657/SfSpp/runs/20261115-0502_b394663_t72-trim/outtrim_{off,on}/pieces/Juglet_Piece_<n>/mesh.log`:
   piece 5 1 170 -> 2 634 (+1 464 for 1 461 trimmed, ~100 %), piece 6 1 583 -> 3 015 (+1 432
   for 1 529, 94 %), piece 7 3 068 -> 3 656 (+588 for 1 384, 42 %), piece 8 919 -> 1 381 (+462
   for 561, 82 %). **These are counts, not point-matched** — Stage 0 is what matches them.
2. **The refinement tests every point of the sherd, not just the grown patch.** In
   `mesh_processing_headless.cpp`, `improveSurfaceBoundaryByFittingBSplineSurface` (defined
   :2384) loops `meshPointCloud` (:2420), fits the spline to the segmented cluster (:2400-2402),
   and admits at :2474 (`euclideanDistance(ptOnFittedSurface, ptOnOriginalMesh) < windowLenMM &&
   angleDiff > 140`) and :2486 (same window, `angleDiff < 40`). The admitted point always keeps
   its ORIGINAL mesh coordinates (:2478-2483, :2490-2495). A trimmed point is therefore still a
   candidate, and the window is ticket 26's measured one (default 3.0 tree units).
3. **The paper's cluster merge is mostly not involved.** On piece 7 and piece 8 it merged
   nothing; on piece 5 it merged one cluster of 1 190 points; on piece 6 it joined two scraps
   (230 into 766). Stage 0 confirms from rung `r3_after_merge` versus `r2_clusters_premerge`.
4. **The growth compares a candidate with its immediate neighbour.** `growPaper234` (:3355),
   front loop :3386-:3404: curvature gate :3396 `pnormals->points[cand].curvature >= kappaThresh`,
   angle gate :3400 `pcl::getAngle3D(curN4, nn4, true) > thetaDeg` where `curN4` is the CURRENT
   FRONT POINT's normal. Theta default 3.4 (:4227, :5375), 5.6-6.8 on sherds 5-8 at run time.
   At 3x the points are ~0.09 real mm apart, so a 90 deg lip turned over a millimetre shows as
   1-2 deg per step and the growth walks round it.
5. **The curvature gate cannot fire as built.** `paperKappa = 1.0` (:4227, :5375; env
   `SFS_PAPER_KAPPA` :5474) is compared against `pnormals->points[cand].curvature`, which in the
   path traced here is PCL `NormalEstimation` PCA curvature computed at :898-911 and copied back
   at :916 — bounded by 1/3. Whether the 3x radius-normal task (`SFS_NORMAL_MODE=radius`) fills
   the field by the same route is NOT confirmed; Stage 0 prints the range and settles it.
6. **A turn measured over a real distance already separates wall from break face on the four
   defective sherds.** Ticket 59, 5 mm window, per-piece medians wall/fracture in degrees: J1
   20.8/76.8, J5 26.4/68.4, J6 39.8/74.5, J7 24.0/69.9, J8 37.7/79.2; it fails on J2 83.4/79.1,
   J3 72.1/70.7, J9 66.6/74.5 (`.scratch/juglet-breaklines/issues/59-*.md`, decision table row (c),
   pooled 37.98 vs 72.85 deg).
7. **The baseline the gate is scored on (ticket 72, 3x, Fisher's `offlip08.py` rule):** dots more
   than 0.8 mm off the inner wall — piece 5 21/150, piece 6 3/141, piece 7 53/174, piece 8
   9/126 = **86/591 (14.6 %)**, off-lip contour **51.0 mm**, sherd 7 alone 24.0 mm. Trim on:
   69/591 (11.7 %), 40.8 mm. Touching pair 1-4 was clean in both switch-off runs (+0.821,
   +0.829, zero opposed dots) and reads -0.808 after the trim.

### Stage 0 — attribution, read-only, laptop only (a STOP)

For pieces 5, 6, 7, 8 and control 1, for every `Breakline_0` dot, take the surface point of
`Juglet_Piece_<n>_Surface_0.xyz` nearest to it (the carrier, as ticket 72's Part A defined it),
and label it with how it entered the patch:

- **grown** — claimed by `growPaper234` (rung `r2_clusters_premerge`);
- **merged** — claimed by a cluster that was absorbed (rung `r3_after_merge`, reason code
  `DR25_MERGED`);
- **refined-own** / **refined-other** — added by the admission step (:2474 / :2486), reason
  codes `DR25_ADMIT_OWN` / `DR25_ADMIT_OTHER` at rung `r4_after_reassign`; and whether the
  point was in the trimmed set.

Arm the existing dump switch (`SFS_DUMP_STAGE=<dir>`, piece filter `SFS_DUMP_PIECES`) on one 3x
cell with `SFS_BREAK_TRIM=1`; rungs `r1_downsampled`, `r2_clusters_premerge`, `r3_after_merge`,
`r4_after_reassign`, `r5_write` are all there, with `DR25_*` codes. If the rung files are too
large to fetch, join on coordinates on the cluster (they are the same point set apart from rung 1).

Deliver `C:/PR/artifacts/t73/attrib73.tsv` — one row per carrier dot, columns
`piece dot off_lip_08 d_inner_mm carrier_wall grown merged refined_own refined_other
trimmed curvature angle_to_nearest_grown_deg` — plus `attrib73_summary.md` with, per piece, the
count and share of off-lip carriers by origin, the pooled split, and:

- the **curvature range** (min / median / p99 / max) over the surface cloud, to settle Given 5;
- the **angle distribution** between an admitted point's normal and the nearest GROWN point's
  normal, for off-lip carriers and for on-lip carriers separately, plus the same for grown
  wall points near the patch edge — this distribution sets `ANGLE_A` for Arm A (see below);
- the **turn over a base** measured at 1, 2, 3 and 5 real mm on the carriers of pieces 5-8,
  wall-labelled versus off-lip, to choose `BASE_MM` for Arm B.

**Stop rule:** if fewer than 40 % of the off-lip carriers are refinement additions (i.e. the
growth put them there and refinement only kept them), record that with the numbers, read
`the-refinement-is-not-where-they-come-back`, drop Arm A, and run only Arms B and C. If the
attribution cannot be built (the rungs do not join), stop and say so — do not measure a
substitute.

### Part A — Arm A: the refinement may not add back a point the growth refused

One default-off switch `SFS_REFINE_ADD_GATE=1`, banner `refine add gate: on|off`, with
`SFS_REFINE_ADD_ANGLE_DEG` = the Stage 0 value (a single number, not a sweep). In
`improveSurfaceBoundaryByFittingBSplineSurface`, before the admission branches at :2474 / :2486:
a candidate point that is NOT in the segmented cluster is admitted only if the angle between its
normal and the normal of the nearest GROWN point is <= `ANGLE_A`; otherwise it is refused and
counted. Points already in the cluster pass exactly as they do today. Print
`[SFS-73] REFGATE piece=<n> surface=<s> new=<n> refused=<n> angle=<deg>` once per surface.
The off path must be byte-for-byte today's behaviour.

### Part B — Arm B: the growth judges a turn over a real distance

One default-off switch `SFS_GROW_BASE_MM=<real mm>`, banner `grow base: <mm> mm (<u> units)`,
single value from Stage 0 (default 1.0 mm if Stage 0 gives none). Units are tree units:
`u = mm * 3.0` at this scale, printed both ways. In `growPaper234`'s front loop, replace the
neighbour-to-neighbour test at :3400 with: the mean normal of the claimed points within radius
`u` of the candidate (at least 3 points; fewer falls back to the legacy neighbour rule), and
accept if the angle between the candidate's normal and that mean is <= `thetaDeg`. Leave the
curvature gate at :3396 untouched in this arm. Count `[SFS-73] GROWBASE piece=<n> used=<n>
fallback=<n> base=<u>` once per piece. The off path must be byte-for-byte today's behaviour.

### Part C — Arm C

Both switches on, the same values. Nothing else changes.

### Part D — cells and the gate table

Cells (3x unless named), one Slurm array, driver `.scratch/juglet-breaklines/stage66/run_cell66.sh`
as ticket 72 used it, each cell in its own run directory `runs/<YYYYMMDD>-<HHMM>_<git7>_t73-...`:

| cell | scale | switches |
| --- | --- | --- |
| `off` | 3x | none (identity against ticket 72's `trim_off` geom) |
| `A` | 3x | `SFS_REFINE_ADD_GATE=1` |
| `B` | 3x | `SFS_GROW_BASE_MM=<Stage 0 value>` |
| `C` | 3x | both |
| `off_1x`, `A_1x`, `B_1x`, `C_1x` | 1x | same switches (J1's ruler is a 1x measurement) |
| `pota_off`, and one Pot A cell per Juglet arm that improves the pooled number (at least `pota_C`) | 1x | same switches |

Deliver `C:/PR/artifacts/t73/gate73.tsv`, columns
`group metric piece before trim_on arm_A arm_B arm_C ref verdict`, rows:

- **primary** — off-lip share at 0.8 mm and off-lip contour in mm, per piece (5,6,7,8), pooled,
  on 3x: baseline 21/150, 3/141, 53/174, 9/126, 86/591 = 14.6 %, 51.0 mm, sherd 7 24.0 mm.
  **Pass**: pooled share falls, sherd 7's contour falls below 12 mm, and no piece rises by more
  than 2 dots. State the best arm.
- **pairs** — the nine touching-pair median normal dots (ticket 328's values; take the exact
  numbers from ticket 72's `C:/PR/artifacts/t72/gate72.tsv`, group `pairs`). **Pass**: 1-4
  returns to a positive median with at most 2 opposed dots (pre-trim +0.821/+0.829, 0 opposed),
  and no other pair's median moves more than 0.10 toward negative. 6-7 was negative before every
  arm — it is not a regression either way.
- **j1_ruler** — J1's three frozen numbers (blind stretch, far-skin share, reverse coverage) from
  `/data/gpfs/projects/punim2657/SfSpp/runs/20261102-0450_05be12c_t57-sweep/check_separation.py`,
  computed at 1x for `off_1x`, `A_1x`, `B_1x`, `C_1x`. **Pass**: no arm is worse than
  `off_1x`; J1's worn quarter stays the ceiling.
- **pota** — off-lip metric per piece against `pota_off`. **Pass**: within 1 dot, 9 of 9 lines
  written, no crash, and record Pot A's own dot counts.
- **coverage** — 9 of 9 pieces produce S0, S1, Bl0 in every cell.
- **identity** — `off` against ticket 72's `trim_off` geometry: bounded identity, ±1 dot and
  max nearest-neighbour <= 2.1 mm on 3x (no pristine 3x run exists); byte-identical at 1x.
- **render** — `C:/PR/artifacts/t73/render73_before_after.png`: sherds 5-8, rows before / A / C,
  red = off-lip dots, the inner lip drawn in green; plus one panel of pair 1-4's dots before and
  after the winning arm.

Record `sacct` State/ExitCode for every job. `scripts/slurm_poll.sh` **does not exist in any
clone or on Spartan** — use `scripts/remote/job_status.sh` and say so in the write-back.

### Part E — readings (exactly one slug, after a line starting `Reading:`)

- `the-refinement-is-not-where-they-come-back` — Stage 0 stop rule fired; growth-carried only.
- `the-refinement-readmits-and-the-gate-cures-it` — Arm A is the cure: primary passes on A.
- `the-refinement-readmits-and-the-gate-does-not-cure-it` — A moves the number but does not pass.
- `the-growth-crosses-the-lip-and-the-long-base-cures-it` — Arm B is the cure.
- `both-steps-matter-and-only-c-together-cures-it` — only Arm C passes.
- `neither-helps-inconclusive` — no arm passes the primary bar.

Write the reading against the primary gate first, then the pairs and J1 rows; do not average
across sherds to make an arm look better.

### Part F — acceptance

- [ ] `attrib73.tsv` with the columns above, one row per carrier dot, pieces 5-8 plus 1.
- [ ] `attrib73_summary.md`: per-piece and pooled origin split, curvature range, the two angle
      distributions, the turn-over-base table at 1/2/3/5 mm, and the chosen `ANGLE_A`, `BASE_MM`.
- [ ] Two switches, both default off, banner lines printed, a `[SFS-73]` count line per piece,
      `git diff --stat` showing the ticket and the one source file only.
- [ ] `off` cell reproduces ticket 72's `trim_off` within ±1 dot / 2.1 mm (3x) and byte-identical
      (1x); the diff of the CAND-equivalent surface files stated per piece.
- [ ] `gate73.tsv` with every group and every row's verdict, and the two `before` columns filled
      from the cells, not copied from this ticket.
- [ ] `render73_before_after.png` opened and described in the write-back (what moved, what did not).
- [ ] Nine touching-pair dots recomputed from the cells' own `Bl0` (ticket 72's `pairdot72.py`
      needs `--scale 1` against the 3x ground truth).
- [ ] `sacct` recorded for every job; any failed attempt explained.
- [ ] `Reading: <slug>` and one `End state: ready|incomplete|blocked|stopped` line.
- [ ] Nothing committed, nothing pushed, no default changed, no threshold swept.

### Out of scope

- The trace guard (tickets 75/78) — closed by the conservator on 2026-11-15.
- Combining with `SFS_BREAK_TRIM` (ticket 72). The trim stays default off; this ticket measures
  the post-growth and growth cures on their own. If an arm wins, the combination is a later
  ticket.
- Changing the scale, the resolution, or the 3 tree units per mm.
- Pot A threshold work (its pairing machinery degenerates at the primary parameters, ticket 59).

### Notes for the worker (operational, not spec)

- Paths, cell environment and the staging recipe are in
  `C:/PR/artifacts/dsh-handover/73/brief.md`; ticket 72's brief carries the same recipe with its
  own switch.
- The 3x inputs: `CLOUD_DIR=.../runs/20261112-0218_b1e1580_t331-large/cloud_mesh`,
  `MESH_DIR=.../t331-large/mesh_large`, `AXIS_DIR=.../Dataset/Juglet_large`,
  `MANIFEST=.../t331-large/pins/MANIFEST_JUGLET_LARGE.tsv`, `POT_NAME=Juglet_large`,
  `WORNESS=0.7`, `MESH_ENV="SFS_NORMAL_MODE=radius SFS_NORMAL_RADIUS_MM=1.0"`.
- **Pot A has no manifest on the cluster.** Write `$RUN/pins/MANIFEST_POTA_PINNED.tsv` from the
  on-disk clouds (`piece pcd_md5 kept_points spacing_mm`) and say in the write-back that it gates
  the cell against drift only, not against a shipped corpus.
- `wsl rsync` from the laptop to Spartan is the transfer route; base64 over `ssh` is the
  fallback when rsync hangs (it has, twice).
