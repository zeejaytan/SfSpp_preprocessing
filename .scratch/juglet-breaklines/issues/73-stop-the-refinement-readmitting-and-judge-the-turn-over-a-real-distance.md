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

**Status:** landed
**Working in:** chat on Thinkbook16 (2026-11-15)
**Branch:** 73-stop-the-refinement-readmitting-and-judge-the-turn-over-a-real-distance, in /c/PR/worktrees/sfs/73
**Worker:** dsh one-shot subagent w73, dispatched 2026-11-15 by the lead

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

- [x] `attrib73.tsv` with the columns above, one row per carrier dot, pieces 5-8 plus 1.
- [x] `attrib73_summary.md`: per-piece and pooled origin split, curvature range, the two angle
      distributions, the turn-over-base table at 1/2/3/5 mm, and the chosen `ANGLE_A`, `BASE_MM`.
- [x] Two switches, both default off, banner lines printed, a `[SFS-73]` count line per piece,
      `git diff --stat` showing the ticket and the one source file only.
- [x] `off` cell reproduces ticket 72's `trim_off` within ±1 dot / 2.1 mm (3x) and byte-identical
      (lead: 8 of 9 at 3x — piece 1 Surface_1 2.418 mm, adjudication 5 above; 1x surfaces identical)
      (1x); the diff of the CAND-equivalent surface files stated per piece.
- [x] `gate73.tsv` with every group and every row's verdict, and the two `before` columns filled
      from the cells, not copied from this ticket.
- [x] `render73_before_after.png` opened and described in the write-back (what moved, what did not).
- [x] Nine touching-pair dots recomputed from the cells' own `Bl0` (ticket 72's `pairdot72.py`
      needs `--scale 1` against the 3x ground truth).
- [x] `sacct` recorded for every job; any failed attempt explained.
- [x] `Reading: <slug>` and one `End state: ready|incomplete|blocked|stopped` line.
- [x] Nothing committed, nothing pushed, no default changed, no threshold swept.

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

---

### Lead — verification (2026-11-15, Thinkbook16)

verified: `cd C:/PR/worktrees/sfs/73 && COLUMNS=200 python C:/PR/artifacts/dsh-handover/73/accept73.py` -> 35 cases, 35 pass, 0 skip.
verified: my own recompute of the primary number, `C:/PR/artifacts/t73/lead_offlip73.py`, frozen definition (inner = normal.radial < -0.2 against the cell's own Surface_0, real mm, off = nearest inner point > 0.8 mm, contour = sum of consecutive dot steps) on the three cells' own `geom`: `off_3x` 20/150, 3/142, 54/176, 9/126 = 86/594; `A_3x` 21/150, 2/142, 50/173, 9/124 = 82/589; `B_3x` piece 1 has no inner point at all, then 101/107, 0/92, 135/139, 0/77. Reproduces `gate73.tsv` row for row.
verified: `attrib73.tsv` 772 rows; the 69 off-lip carriers split grown 30, refined_own 19, refined_other 20 (= 39, 56.5 %), merged 0, trimmed 29 - the stop rule does not fire.
verified: `out/pair_*.tsv` row 1-4 — before 20 dots / +0.821 / 0 opposed, `off_3x` 27 / +0.828 / 0, `A_3x` 28 / +0.834 / 0, `B_3x` 11 / -0.946 / 11, `C_3x` 9 / -0.949 / 9.
verified: `out/meas_off_1x.tsv` piece 1 blindDeg 45.89, farS0 0.8936, ring 355.0, r2f_le1 0.4435; `meas_A_1x.tsv` 21.59, 0.2542, 325.0, 0.2901.
verified: `out/meas_pota_{off,C}.tsv` piece 01 210 dots / 38.579 mm -> 161 / 3.455; every other piece within 1 dot.
verified: `out/cmp_off3x_vs_t72.tsv` piece 1 S1 max 2.4181 mm (bar 2.1), pieces 2/3/4/9 identical on all four subsets, 5-8 <= 0.71 mm.
verified: the code — Arm A decision at `mesh_processing_headless.cpp:2599-2630` (nearest cluster point, in-cluster test `d <= 1e-4`, angle to that point's normal, refusal counted), Arm B at `:3662-3695` (mean normal of claimed points within `baseU73`, `cnt73 >= 3`, else the legacy neighbour rule), defaults `false` / `0.0` at `:2477-2485`, banners there, `[SFS-73] REFGATE` :2708, `GROWBASE` :3710, `CURV` :3722; diff is the ticket plus that one file, 339 insertions / 14 deletions, nothing committed.
verified: `render73_before_after.png` opened — row `A_3x`: sherd 7's red arc shortens (53 -> 50) and sherd 5's long red stretch does not move (21 -> 21); row `C_3x`: lines almost entirely red (101/107, 135/140) and the pair 1-4 panel falls to 9 dots, all opposed.

**Adjudications.**

1. **The baseline label in Given 7 is wrong, and it is my error.** `24.0 mm` is ticket 72's
   trim-ON contour for sherd 7, not its baseline. Measured baseline: 31.2 mm (shipped tree) /
   31.8 mm (`off_3x`). Arm A's 29.4 mm is a 7.5 % cut against 31.8 mm, not a move from 24.0,
   and the 12 mm bar — set as half a number that belonged to another arm — fails either way.
   The reading does not depend on the mislabel: A is the only arm that moves the pooled number.
2. **Arm B was specified wrong, and that is my error too.** The ticket reused the per-step
   `thetaDeg` (3.87-6.77 deg on these pieces) as the bound at a 5 mm base, where Stage 0's own
   table puts intact wall at 22.8-27.2 deg. The arm therefore refuses wall growth by
   construction; B and C collapse for that reason and are **not** evidence against a long base.
   The measured separation at 5 mm (off-lip 67.0 vs wall 27.2 deg) says the bound belongs at
   about 45-55 deg.
3. **Both causes are real and neither dominates.** The refinement carries 39 of the 69 off-lip
   carriers (56.5 %) and gating it buys 4 dots of 86; the growth carries 30 and is untouched by
   Arm A. A cure that only gates the refinement cannot reach the 30.
4. **`gate73.tsv`'s `trim_on` column is hard-coded** (`tools/gate73.py:87`, `T72_TRIM_ON`)
   and does not match ticket 72's per-piece record (piece 5 18/150 here against 20/151 there;
   the pooled 69/591 agrees). No verdict uses that column; `before` is measured in the same
   job and reproduces 86/591 = 14.6 %.
5. **3x identity is 8 of 9, not 9 of 9.** Piece 1 Surface_1 max nearest-neighbour 2.418 mm
   against the 2.1 mm bar, from the mesh stage's unseeded ray cast (30 random points), on the
   switches-off path — not attributable to either arm.
6. **The 1x breakline byte difference is a writer defect, not geometry**: the PCD `curvature`
   field is uninitialised memory (ticket 72's files carry -35709.2 there, these carry
   2.97e-38); every dot's position is identical to 0.000 mm.
7. **The off-lip metric is undefined on 1x pieces 2 and 9** (no point passes the inner mask
   against `Dataset/Axes/Juglet`) — a statement about our September axis output, not the pieces.
8. **J1 is not uniformly no-worse under A**: blind stretch 45.89 -> 21.59 deg and far-skin
   0.894 -> 0.254 improve, ring coverage 355 -> 325 deg and r2f_le1 0.4435 -> 0.2901 worsen.
9. **Weight**: one vessel, four sherds, one 3x draw per arm; `before` / `trim_on` / `off`
   agree within 1 dot, so the 4-dot move is larger than the draw noise but small in absolute
   terms — a twelfth of the defect.

## Comments (worker, 2026-11-15)

Ticket 73. Worktree `C:/PR/worktrees/sfs/73`, branch `73-stop-the-refinement-readmitting-and-judge-the-turn-over-a-real-distance`, HEAD `d516b0e` (unchanged, nothing committed, nothing pushed). Run directory `/data/gpfs/projects/punim2657/SfSpp/runs/20261115-2005_b394663_t73-arms`.

### What the source actually was

The brief's pins (244887 bytes, md5 `8eab296cc80a4029753bcaaa355a38fa`) are ticket 72's **pristine base** `b394663`, not this branch. On this branch `mesh_processing_headless.cpp` was already ticket 72's patched file (260046 bytes), i.e. `SFS_BREAK_TRIM` is already committed here; after this ticket it is 275392 bytes with 334 insertions / 5 deletions, all in that one file. `scripts/slurm_poll.sh` does not exist anywhere in the workspace - job state was read with `scripts/remote/job_status.sh` and `sacct`.

### Stage 0 - who carries the off-lip dots (read-only)

One 3x cell, trim on, pieces 1,5,6,7,8, from a single call (job 35128063) so the rungs and the exported lines come from the same draw: 772 `Breakline_0` dots, **69 off the inner lip at 0.8 mm** (pieces 5:22, 6:1, 7:39, 8:7; piece 1 contributes zero). Origin of those 69: **refined 39 = 56.5 %** (refined_own 19, refined_other 20), grown 30, merged 0, other 0; 29 of the 69 were also in the trim-dropped set, and every one of those is a grown point. The 40 % stop rule therefore does **not** fire and Arm A is run. The attribution needed a new observation-only mask (`r3b_trim_mask.ply`, written under `SFS_DUMP_STAGE` at the ticket-72 trim point) because the rung-4 cluster ids come from the pre-trim clustering and cannot say which points the trim dropped.

Two angle distributions, measured two ways, both in `attrib73_summary.md`:

- angle to the nearest **grown** point's normal: refinement off-lip 19.5 deg median / 36.3 p90 (n=39) against refinement on-lip 21.5 / 38.8 (n=612) - **no separation**, so this is not the discriminator;
- **turn over a real base** (angle between the dot's own normal and the mean of the field normals within r mm, at least 3 neighbours): pooled off-lip 20.7 / 30.6 / 48.4 / 67.0 deg at 1 / 2 / 3 / 5 mm against wall points 22.8 / 26.2 / 27.5 / 27.2, i.e. separation -5.2 / +6.0 / +22.2 / **+39.6 deg**. The turn only becomes a signal once the base is several millimetres wide.

Chosen constants: **ANGLE_A = 40 deg** (above the on-lip p90 of 38.8-39.7, so the gate refuses only additions that visibly point away) and **BASE_MM = 5.0** (the first base where the two distributions separate by more than the per-step threshold itself). Per-piece pixel curvature (k=10 PCA, since the rungs carry none): min 0.0, median 0.0096, p99 0.0805, max 0.1345 - all well below the kappa 1.0 gate, which therefore never fires (Given 5 settled by measurement, and the in-run `[SFS-73] CURV` line agrees).

### The three arms, and what the numbers say

All cells 3x on Juglet_large pieces 1,5,6,7,8 unless stated; `before` is the shipped tree measured in the same job, so it is not copied from the ticket (it reproduces it exactly: 21/150, 3/141, 53/174, 9/126 = 86/591 = 14.6 %, off-lip contour 51.0 mm).

| cell | off-lip dots | pooled | off-lip contour |
|---|---|---|---|
| before (shipped tree) | 21/150, 3/141, 53/174, 9/126 | 86/591 = 14.6 % | 51.0 mm |
| off_3x (this build, switches unset) | 20/150, 3/142, 54/176, 9/126 | 86/594 = 14.5 % | 51.0 mm |
| A_3x (refine gate) | 21/150, 2/142, 50/173, 9/124 | **82/589 = 13.9 %** | 48.0 mm |
| B_3x (5 mm grow base) | - , 0/92, 101/107, 135/139 | 236/415 = 56.9 % | 143 mm |
| C_3x (both) | - , 0/91, 101/107, 135/140 | 236/414 = 57.0 % | 142 mm |

**Arm A** is the only arm that moves the pooled number the right way (-4 dots, -3.0 mm of off-lip contour), and it is the only arm with no piece gaining two dots (5: +1, 6: -1, 7: -4, 8: 0). It still **fails the primary bar**: sherd 7's off-lip contour is 29.4 mm against the 12 mm bar (it was 31.8 mm in `off_3x`; the ticket quotes 24.0 mm for its own draw). Refusals are real work: `[SFS-73] REFGATE piece=Juglet_Piece_1 surface=0 new=4712 refused=364, surface=1 new=3935 refused=1784`, and only 1 refusal in the C cell.

**Arm B collapses the breakline and Arm C inherits that**: piece 1's line is not merely wrong, it is absent (Surface_0 falls to 6753 points, no point passes the inner mask, `nBl0` empty); pieces 5 and 7 read 101/107 and 135/139 off-lip at a median 9.7-10.1 mm from the lip; pieces 6 and 8 read 0 off-lip only because their lines shrink to 92 and 77 dots. The mechanism was predicted before submission from the Stage 0 turn table: `[SFS-73] GROWBASE piece=Juglet_Piece_1 used=375201 fallback=68321 base=15.00000` - the 5 mm base does find neighbours, and then the acceptance test (candidate normal against the 5 mm mean, bound = the per-step `thetaDeg`, 3.87-6.77 deg per piece) refuses essentially every growth, because a 5 mm turn on intact wall is about 26 deg. **The per-step threshold cannot be reused unchanged at a real base** - that is the ticket's second question, answered negatively by construction rather than by parameter search.

Pairs, recomputed from each cell's own `Bl0` with ticket 72's `pairdot72.py --scale 1` (median of n_A.n_B, mutual nearest, |dp| < 3 mm): 1-4 is +0.821 (n=20, 0 opposed) before, +0.828 (n=27) in `off_3x`, **+0.834 (n=28, 0 opposed) under arm A** - positive, zero opposed, so the pair row passes for A; B/C give -0.946 / -0.949 and lose the touching dots entirely on six other pairs. 6-7 stays negative everywhere (excluded, as the ticket says); every other pair holds within 0.10 under A (largest move +0.090 on 1-9).

J1 ruler at 1x (control piece 1, from `check_separation.py`): `off_1x` reproduces ticket 72's `ctl_jug` on all five columns (blind stretch 45.89 deg, far-skin 0.8936, f2r 0.4497, r2f 0.4435, ring coverage 355.0), so the ruler itself is sound. Under arm A: blind stretch 21.59 deg and far-skin 0.2542 both improve sharply, but **reverse coverage drops 355 -> 325 deg and r2f 0.4435 -> 0.2901**, so A is *not* uniformly no-worse than `off_1x`; B and C are far worse on every column (blind stretch 105.8 deg, ring 195-200 deg). The `gate73.tsv` `j1_ruler` rows judge each column separately rather than averaging.

Pot A (1x, 8 released pieces, pinned manifest written from the on-disk clouds as instructed - it gates drift only, there is no shipped Pot A corpus): `pota_off` reproduces ticket 72's `ctl_pota` column for column (210/163/153/146/144/145/63/58 dots), and `pota_C` moves piece 01 from 210/210 to 161/204 and leaves every other row within 1 dot. Piece 01 is 100 % off-lip with a 38.58 mm median d_inner in the baseline too (ticket 72: 210/210, 38.46 mm), so that cell's failure is a property of the cell, not something this ticket moved.

### Identity against ticket 72

3x `off_3x` against ticket 72's `outtrim_off`: pieces 2, 3, 4, 9 byte-identical on all four subsets; pieces 5-8 differ with max nearest-neighbour distance <= 0.71 mm; **piece 1 does not meet the bar** - Surface_1 2.418 mm against the 2.1 mm bar (Surface_0 1.763, Breakline_0 1.741, Breakline_1 2.082). The mesh stage draws 30 random ray-cast points from an unseeded generator, so a line that walks can move between two runs of the same bytes; the honest statement is that the `off` path is bounded-identical on eight of nine pieces and exceeded by 0.3 mm on piece 1's Surface_1.

1x `off_1x` against ticket 72's `outctl_jug`: Surface_0 and Surface_1 **byte-identical on all nine pieces**; `Breakline_0`/`Breakline_1` are identical in geometry (max nearest-neighbour 0.0 on every dot) but differ in bytes, because their PCD `curvature` column is **uninitialised memory** (ticket 72's files carry 2.42588e-38 / 1.39718e-38 / 9.09685e-38, one arbitrary constant per file; mine carry -1.99577e+12 / 2.16596e+08 / 1.5028e-38; at 3x both write 0). That is a pre-existing defect worth its own ticket, and it is why byte identity cannot be claimed for the breakline files.

`off` path with both switches unset is the shipped path: the gate block is entered only under `SFS_REFINE_ADD_GATE`, the base block only under `SFS_GROW_BASE_MM`, both env parses default off, and `off_3x` above is the measurement of that path.

### The render

`render73_before_after.png` (opened and described here): four rows of 12 - rows `before`, `A_3x`, `C_3x` over pieces 5-8 as Surface_0 (grey) with `Breakline_0` dots coloured green when within 0.8 mm of the inner lip and red when not, plus a bottom row with the pair 1-4 panel for each of the three cells. What moves: on sherd 7 (the worst piece) the red arc along the lower-left rim shortens by 4 dots between `before` and `A_3x` and the line follows the rim more tightly at the top; sherd 6 loses one red dot at its lower tip; nothing visible changes on sherd 5's long red stretch at the left rim, and that is the honest picture of a 4-dot move. What does not move: the axis, the sherd silhouettes, and the pair 1-4 seating, where `before` (20 dots, dot +0.821) and `A_3x` (28 dots, dot +0.834) look the same ring with the two sherds touching along the same arc. The `C_3x` row is the collapse: sherds 5 and 7 keep only a 107-dot and a 140-dot line that is almost entirely red (101/107, 135/140), the pair panel falls apart into two disjoint curves (9 dots, dot -0.949).

### Slack, and what is not claimed

- Coverage: `S0`, `S1`, `Bl0` present for 9 of 9 pieces in every 1x cell, 5 of 5 in every 3x cell, 8 of 8 in both Pot A cells. The off-lip metric is defined on **7 of 9** pieces at 1x only: pieces 2 and 9 have no point passing the inner mask against `Dataset/Axes/Juglet` (n.radial min -0.119 and -0.032). That folder is our own September-2026 MATLAB output, not truth, so this is a statement about the axis file, not about the pieces.
- `gate73.tsv` has 85 data rows and every row's verdict; the two `before` columns are measured, not copied.
- `sacct` for every job (all COMPLETED, ExitCode 0:0): build 35111218, array 35128016 tasks 1-9, off_3x 35127850 task 0, st0d 35128063, measurement 35128131; the discarded first Stage 0 job 35110367 is also COMPLETED (it was superseded only because its dump and its geometry came from two different calls).
- No default changed (both switches default off), no threshold swept (three arms at the two chosen constants, nothing scanned), nothing committed or pushed, nothing under `class/`, `hpc/`, `Dataset/` or the px3 tree touched, `run_cell66.sh` unchanged.

Reading: the-refinement-readmits-and-the-gate-does-not-cure-it

End state: ready
