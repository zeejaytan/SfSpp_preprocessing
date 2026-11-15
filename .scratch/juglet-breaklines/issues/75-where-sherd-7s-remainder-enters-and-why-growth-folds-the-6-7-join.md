# 75 — Where sherd 7's last off-lip dots enter, and why the chord growth turns the 6-7 join into a fold

**What to build:** first a read-only stage that says *how* the 29 dots that still sit off the
inner wall on sherd 7 survived the chord growth, and *what* happened to the 6-7 pair under it;
then exactly **one** default-off arm, chosen by that stage, that closes the leak the stage
found. Ticket 74 established that the growth is the strong lever (sherd 5 21 -> 0, 6 3 -> 0,
7 54 -> 29, 8 9 -> 0 as dot counts, sherd 7's off-lip contour 31.80 -> 17.40 mm) and that it
costs the 6-7 pair its sign. Neither of those is explained yet, and both are cheap to explain
offline before another cell is run.

**Answers:** E1
**Depends on:** 74 (the three doors, landed fad4e5f), 73 (the re-admission path, landed
9ff83e7), 72 (the trim, landed c27284c), 348 (the measured contact set), 328 (the wall side)
**Budget:** small-medium. One read-only stage, one build, three or four 3x cells, two 1x
control cells, one Pot A cell.

**Status:** in-progress
**Working in:** chat on Thinkbook16 (2026-11-16)
**Branch:** 75-where-sherd-7s-remainder-enters-and-why-growth-folds-the-6-7-join, in /c/PR/worktrees/sfs/75
**Worker:** dsh one-shot subagent, dispatched 2026-11-16 by the lead

## Given — what the numbers already say

1. **The growth is where the break face dies on three of the four sherds, and it stops half
   way on sherd 7.** Off-lip dots at the conservator's 0.8 mm cut (`gate74.tsv`, arm G,
   3x Juglet, one draw):

   | arm | sherd 5 | sherd 6 | sherd 7 | sherd 8 |
   |---|---|---|---|---|
   | `off` | 21/150 | 3/141 | 54/173 (31.80 mm) | 9/126 |
   | Arm M (merge gate) | 0/147 | 3/138 | 49/165 (29.56 mm) | 9/124 |
   | Arm G (chord growth) | 0/145 | 0/130 | **29/170 (17.40 mm)** | 0/120 |
   | Arm GM | 0/145 | 0/130 | 28/171 (16.80 mm) | 0/120 |

2. **The same thing with the refinement gate stripped** (the lead's control cells, job
   `35132483` for 3x and Pot A, `35132554` for 1x): `Mnr` 0/146, 3/142, 52/174 (30.60 mm),
   9/125; `Gnr` 0/143, 0/134, **30/171 (17.40 mm)**, 0/123; `ref` (the gate alone, no switch)
   20/149 (12.00 mm), 3/138, 49/165 (29.57 mm), 9/124. So the growth's own effect, with nothing
   else armed, is 5 21->0, 6 3->0, 7 54->30, 8 9->0.

3. **Sherd 7 keeps about 17 mm of line on the outside**, which is 5.4 mm above the 12 mm bar,
   in every arm including GM — so the two doors together do not reach it, and the remaining
   dots are **not** the ones the merge gate refused (the gate fires once on sherd 5 only).

4. **The 6-7 pair changes sign under the growth alone.** Median normal dot over paired dots
   (|dp| < 3 mm): `off` **-0.997** (n=44, 34 opposed), `M` -0.998 (n=46, 39), `G` **+0.551**
   (n=31, 2), `GM` +0.563 (n=32, 2). In the control cells with no refinement gate: `Gnr`
   **+0.657** (0 opposed), `Mnr` -0.997 (42 opposed), `ref` -0.998 (39 opposed). Ticket 328
   recorded -0.786 at this pair, and ticket 348 measured 6-7 as a **real back-to-back join**
   (median normal dot -0.985 there, in the measured contact set). A positive median at a
   back-to-back join means the two lines now face the same way, i.e. one of them has moved to
   the other face or the paired population has changed.

5. **The growth's own test, as it stands after Ticket 74** (`mesh_processing_headless.cpp`,
   ticket-74 file, 279 923 B): the base branch computes the mean normal of the claimed points
   within `baseU73` (1.5 mm x `SFS_TREE_UNITS_PER_MM` = 4.5 tree units) and uses it **only
   when at least 3 claimed points fall in that ball** (`cnt73 >= 3`, `used73`); otherwise it
   falls back to the legacy per-step comparison against the current front point's own normal
   (`fallback73`). Arm G then requires both the chord bound (`candAng73 > g_growBaseTheta`
   refuses) and the legacy per-step test. The refusal path is at `growPaper234` around
   :3662-3694; Arm G's two-test block is :3698-3748; the switch parser (`t74::ensure74`) is
   :2504-2520.

6. **The refinement adds points back after the growth**, and Ticket 73 measured that it
   re-admits 39 of the 69 off-lip dots in a run where the trim was on (Stage 0,
   `attrib73.tsv`). Ticket 74's gate on that step (`SFS_REFINE_ADD_GATE=1`,
   `SFS_REFINE_ADD_ANGLE_DEG=12`) is what moved Pot A (4 of 8 pieces) and sherd 1's ruler in
   ticket 74's armed cells — so **the gate is not the tool to reach for here**: any arm in this
   ticket must be measured against a no-gate cell, and Pot A must be run with no gate.

7. **Where the dots come from is already instrumented.** `SFS_DUMP_STAGE=<dir>` with
   `SFS_DUMP_PIECES=<list>` (armed by `g_dumpOn25`, :1882-1929) writes `r2_clusters_premerge.ply`,
   `r3_after_merge.json`, and the per-rung cloud files used by `attrib73.py`/`attrib74.py`.
   Ticket 73's `attrib74.py` (in this ticket's run or copied from
   `C:/PR/artifacts/t74/attrib74.py`) fixes the branch order that made "merged" unreachable.

## Part A — Stage 0, read-only: how did those dots survive?

No switches, no new cells needed for A1 and A2 if the 3x `off` and `Gnr` geoms and a fresh
dump are available (a dump-armed cell of the `Gnr` arm is acceptable and cheap; run
`SFS_DUMP_STAGE` on it).

**A1 — the remainder census `remainder75.tsv`**, one row per off-lip dot on sherd 7 in the
`Gnr` arm (**29 or 30 dots**), columns:

```
dot_index  x  y  z  chord_turn_1p5_deg  chord_turn_3p0_deg  chord_turn_5p0_deg
d_inner_mm  d_outer_mm  growth_origin  cnt73_at_decision  base_used_flag
refine_added_flag  present_in_off_flag  off_lip_in_off_flag  nn_to_off_mm
```

with `growth_origin` one of `grown`, `grown_fallback`, `refined_added`, `merged`,
`inherited` (present in `off` and still off-lip), and `cnt73_at_decision` read from the
growth's own log line (print it: `[SFS-75] GROWDEC piece dot cnt used fallback angle chord`
for every refused-or-accepted candidate within 1 mm of a surviving off-lip dot, so the table
can be reconstructed rather than guessed).

**A2 — the 6-7 fold `fold75.tsv`**, one row per paired dot of the 6-7 seam in the `off` arm
and in the `Gnr` arm: `piece  dot_id  x y z  nx ny nz  dot_product  dp_mm  matched_off_dot
matched_off_dot_product`. Match **by dot identity against the off arm** (nearest dot within
0.5 mm), so the table shows whether *the same pairs* changed their dot product (the line
moved) or *the population* changed (different dots pair now). Report both medians.

**A3 — the decision table `stage75_summary.md`.** For sherd 7, the share of the 29 dots by
`growth_origin`, and for the fold, the same-pairs vs new-population split, each with a number.
Write one of these slugs and stop there:

- `the-growth-falls-back-and-the-fallback-is-the-leak` — most surviving dots were accepted
  with `cnt73 < 3` / `fallback73` true, so the chord test never judged them;
- `the-refinement-puts-them-back` — most surviving dots are `refined_added` (refused by the
  growth, re-admitted by the refinement);
- `the-turn-is-genuinely-under-the-bound` — most are `grown` with `base_used` and a chord
  turn below 25 deg at 1.5 mm, so the bound is wrong for that stretch, not bypassed;
- `the-fold-is-the-same-dots-moved` / `the-fold-is-a-different-population` — for 6-7;
- `no-single-cause` — **stop rule**: if no origin reaches 50% of the dots, stop here, send the
  shares and do not build Part B.

## Part B — one default-off arm, chosen by A3

Build **only** the arm the A3 slug names. All of them print `[SFS-75] ...` lines with the
counts that justify themselves, and all default to today's path with the switch unset.

- **Arm F (fallback known to be the leak)** — `SFS_GROW_BASE_FALLBACK=refuse|legacy`, default
  `legacy`. With `refuse`, a candidate whose base ball holds fewer than 3 claimed points is
  **refused** instead of being judged by the per-step angle; print `[SFS-75] BASEFALL piece
  dot cnt` per refusal and a `[SFS-75] BASEFALL-SUM piece refusals` line. Same place in
  `growPaper234` as the `cnt73 >= 3` branch.
- **Arm R (the refinement is the leak)** — `SFS_REFINE_LOCAL_GUARD=1`, default off. The
  refinement's add-back decision additionally refuses a point whose **chord turn at 1.5 mm
  about that point** (the same chord the growth uses, on the refined cluster's own normals)
  exceeds 25 deg; print `[SFS-75] REFADD piece point angle refused`. This is **not**
  `SFS_REFINE_ADD_GATE`: that gate compares against the nearest cluster point's normal and is
  the thing that moved Pot A; this one reuses the growth's own geometric test.
- **Arm L (the turn really is under the bound)** — `SFS_GROW_BASE2_MM` (default 0 = off, use
  3.0) and `SFS_GROW_BASE2_THETA_DEG` (default 45.0): a **second, longer** chord test that
  refuses a candidate whose turn at 3.0 mm exceeds 45 deg (the measured wall turn at 3 mm is
  26.7 deg, the off-lip turn 48.9 deg, so 45 separates them), applied **in addition** to the
  existing 1.5 mm / 25 deg test. Print `[SFS-75] CHORD2 piece dot chord2 bound`.

If A3 returns `the-fold-is-the-same-dots-moved`, Part B also runs the same arm and reports the
6-7 median; if it returns `different-population`, no new arm is needed for 6-7 — record that
the pair statistic must be matched by dot identity from now on, and gate on that.

## Part C — cells and gates

Cells (one draw each; the `off` and `Gnr` numbers already exist and may be reused):

| cell | what | why |
|---|---|---|
| `off_3x` | nine 3x sherds, no switch | the baseline (exists) |
| `arm_3x` | nine 3x sherds, the chosen switch | the cure |
| `pota_arm` | eight 1x Pot A pieces, the chosen switch, **no** `SFS_REFINE_ADD_GATE` | no harm |
| `j1_arm` | 1x Juglet piece 1, the chosen switch | the frozen ruler |

Use the ticket-73/74 cell recipe (`stage66/run_cell66.sh` with the ticket-74 `submit_cells.sbatch`
as the model; 3x inputs in run `20261112-0218_b1e1580_t331-large`: `mesh_large/`,
`cloud_mesh/`, `pins/MANIFEST_JUGLET_LARGE.tsv`, `AXIS_DIR Dataset/Juglet_large`,
`WORNESS=0.7`; Pot A pins from its own clouds, no manifest exists).

Gate table `gate75.tsv` with columns `group  metric  piece  off  arm  ref  verdict`, groups
`primary`, `pairs`, `j1_ruler`, `pota`, `coverage`, `identity`. Bars:

- **primary**: sherd 7's off-lip contour < 12 mm; sherds 5, 6 and 8 stay at 0 off-lip dots;
  pooled dots not worse than 29 of 565;
- **pairs**: 1-4 positive with 0 opposed (as in the no-gate cells); **6-7 negative again,
  median <= -0.9 with at least 30 opposed dots** (it is a measured back-to-back join); every
  other pair within 0.10 of `off`;
- **j1_ruler** at 1x: no column worse by more than 10% against the `off` arm
  (`blindDeg`, `farS0`, `ring_cov_deg5`, `f2r_le1`, `r2f_le1`);
- **pota**: 8 of 8 pieces within 1 dot of `pota_off` (this is the bar the ticket-74 gate failed,
  and the reason Pot A runs without it);
- **coverage**: S0/S1/Bl0/Bl1 exported on 9 of 9 pieces;
- **identity**: with the switch unset, the 1x surfaces byte-identical and the 3x surfaces
  within the piece's own run-to-run spread (the unseeded 30-point ray cast moves piece 1's
  Surface_1 by 2.418 mm and 3x has no pristine twin — state the bound you used).

## Part D — readings

Write exactly one, with the numbers that support it:

- `the-fallback-is-the-leak-and-refusing-it-cures-sherd-7`
- `the-refinement-puts-the-line-back-and-guarding-it-cures-sherd-7`
- `the-turn-is-under-the-bound-and-a-longer-chord-cures-sherd-7`
- `the-remainder-survives-every-door` — an honest miss, with the shares;
- `no-single-cause` — the stop rule fired and Part B was not built.

## Part E — acceptance

- [x] Stage 0 runs before any cell, and its slug is quoted verbatim in the ticket
- [x] `remainder75.tsv` has one row per surviving off-lip dot on sherd 7 (29 or 30) and every
      column filled, `NA` only where the quantity is undefined and the reason stated
- [x] `fold75.tsv` reports both medians (same dot identity, current pairing) and the counts
- [x] exactly one Part B switch exists, default-off, with its `[SFS-75]` print lines
- [x] the switch unset reproduces the `off` arm (state the identity bound you got)
- [x] `gate75.tsv` carries every group and every bar above, with PASS/FAIL per row
- [x] Pot A runs **without** `SFS_REFINE_ADD_GATE`, and 8 of 8 pieces are within 1 dot
- [x] every job's `sacct` State/ExitCode is in the ticket, and the run directory holds
      `run.json`, `submit.sbatch`, `logs/`, `out/`
- [x] the render `render75_before_after.png` (sherd 7 before/after, and the 6-7 seam before and
      after under the chosen arm) is written and looked at before the reading is written
- [x] no commit is made by the worker; the lead lands it

## Out of scope

- the trace guard (Pot A tickets 75/78) — closed by the conservator's ruling of 2026-11-15;
- `SFS_REFINE_ADD_GATE` / `SFS_REFINE_ADD_ANGLE_DEG` as the cure: measured in ticket 74 to
  cost Pot A four pieces of eight and sherd 1's `r2f_le1` column;
- sweeping `SFS_GROW_BASE_THETA_DEG` or `SFS_PAPER_RHOINN` as a dial;
- anything under `class/`, `hpc/` or the assembler; any edit to `run_cell66.sh` itself;
  any edit under `Dataset/` or `px3/`.

## Comments (worker, 2026-11-16)

**End state: done — an honest miss.** Part A ran read-only, Part B is one default-off switch, and the
arm that switch implies was built and run against the ticket's bars. Sherd 7 is not cured. Nothing is
committed or pushed; no default is changed; the lead lands it.

### Stage 0 — the slug, quoted verbatim

> **the-turn-is-genuinely-under-the-bound**

Chosen from the growth-side evidence, with the two limits the ticket demands be stated:

* the dots survive mostly **where the walk refused the local point** — at the nearest growth candidate
  the walk accepted 5 of the 30 and refused 25, so no growth-side test can move the line there;
* where the walk did decide, the local chord turn about the dot at 1.5 mm is **median 22.0 deg**, with
  **20 of 30 under the 25 deg bound** — the Stage 0 test has almost nothing to fire on;
* **27 of the 30 dots are the same dot (within 0.5 mm) as in the off arm, and all 27 were off-lip there
  too**, so the growth neither created nor removed this remainder.

Limits stated, not buried: 10 of 30 dots are over 25 deg at 1.5 mm, so the bound is not the only door;
and the ticket-73 rung attribution is **not reproducible in this build** — the ticket-25 dump here
writes r1-r5 and no r3b_trim_mask.ply, and r4_after_reassign.json reports passes 0 with
admitted_own/admitted_other window counts [0,0], so the reason column is cumulative status, not an
event. Under that vocabulary the origin shares read inherited 26 / grown 3 / grown_fallback 1, and the
residual bin has no arm; the census above, not the reason codes, is the primary evidence.

### A1 — remainder75.tsv (170 rows, 22 columns)

30 off-lip dots of 170 on sherd 7 in the Stage 0 Gnr_3x arm (frozen 0.8 mm rule: 30, 16.8 mm of
103.2 mm; the t74 measurer reports 17.4 mm). They form two contiguous runs (dot indices 40-43 and
106-131) whose d_inner ramps 0.85 to 2.73 mm and back — the stretch where the inner field does not
reach the rim. Census at the nearest candidate: 25 of 30 had cnt73 >= 3 (chord branch used), 5 fell
back; walk accepted 5, refused 25. Local chord turn: 1.5 mm median 22.0 deg (10 of 30 over 25, none
over 45), 3.0 mm median 41.5 (5 over 45), 5.0 mm median 58.4. Every column is filled and no row
carries NA; the growth_origin column carries the caveat above (it is the ticket-73 vocabulary applied
to a substitute in_surf0, not a reproduced rung attribution).

### A2 — fold75.tsv (79 rows) and fold75_arm.tsv

| arm | pairs | median dot | opposed (dp <= -0.9) |
|-----|------:|-----------:|---------------------:|
| off_3x | 44 | **-0.997** | 34 |
| G_3x | 31 | +0.551 | 2 |
| Gnr_3x | 35 | +0.596 | 4 |
| GM_3x | 25 | +0.728 | - |
| Arm L | 33 | +0.561 | 3 |

Matched by identity (0.5 mm on both dots): only 5 of the Gnr arm's 35 pairs and 4 of Arm L's 33 pairs
are the same dot pair as in the off arm. The off pairs that leave are the opposed ones (38 pairs,
median -0.998); the pairs that survive were already positive. **The fold is a different population,
not the same dots turned over** — that is a finding in its own right and it is why no chord test
restores the pair.

### Part B — the one switch

Arm L: **SFS_GROW_BASE2_MM** (default 0, off) plus **SFS_GROW_BASE2_THETA_DEG** (default 45.0). A
second chord turn measured over 3.0 mm about the candidate, in addition to the existing 1.5 mm / 25 deg
test, refused when it exceeds its own bound. Prints "[SFS-75] CHORD2 on, base2=... bound2=..." once per
piece and "[SFS-75] CHORD2 piece= dot= cnt2= angle2= bound= refused=" per candidate (the Stage 0 census
adds "[SFS-75] GROWDEC ..." and "[SFS-75] GROWSUM ..."). Source pin 4c051cca35246a4ce6a3d1ac0598cae1,
286 171 B, 5 hunks / 116 added / 4 deleted against the ticket-74 pin 1d748365....
Reach measured in the arm itself: at the 30 surviving dots the new door was tested at 21 (cnt2 >= 3)
and refused **2** — so it could not have moved more than 2 of the 30.

### Part C — cells, jobs, and the bars

Every job, with its sacct State/ExitCode as read from the cluster on 2026-11-16:

| job | name | State | ExitCode | what it was |
|-----|------|-------|----------|-------------|
| 35133731 | t75build | FAILED | 4:0 | Stage 0 build, compile error (t75::dec75) |
| 35133788 | t75build | COMPLETED | 0:0 | Stage 0 build, mesh md5 1653eff99ed262c0d7690d5b63c9db9f |
| 35133833_0 | t75st0 | FAILED | 5:0 | Stage 0 cell, SFS_DUMP_PIECES word-split (mesh_rc=127) |
| 35133851_0 | t75st0 | COMPLETED | 0:0 | Stage 0 cell Gnr_3x, coverage 9/9, census + dump |
| 35134352 | t75armlb | FAILED | 4:0 | Arm L build, compile error (t73::g_unitsPerMM) |
| 35134362 | t75armlb | COMPLETED | 0:0 | Arm L build, mesh md5 51f8e35e0426333613560b3fef559296 |
| 35134404_0 | t75arml | COMPLETED | 0:0 | arm_3x, 3x, 9 pieces |
| 35134404_1 | t75arml | COMPLETED | 0:0 | pota_arm, Pot_A 1x, 8 pieces, no SFS_REFINE_ADD_GATE |
| 35134404_2 | t75arml | COMPLETED | 0:0 | j1_arm, corpus Juglet 1x, 9 pieces |
| 35134417_0 | t75id | COMPLETED | 0:0 | id_1x, every switch unset |
| 35134417_1 | t75id | COMPLETED | 0:0 | id_3x, every switch unset |
| 35134599 | t75meas | FAILED | 3:0 | measurement, md5 cross-check compared full lines not hashes |
| 35134623 | t75meas | COMPLETED | 0:0 | measurement + identity comparison |

Runs: /data/gpfs/projects/punim2657/SfSpp/runs/20261116-0257_742880c_t75-stage0 (Stage 0) and
.../20261116-0330_742880c_t75-arml (Arm L); each holds run.json, submit_build.sbatch,
submit_cells.sbatch (plus submit_id/submit_meas for Arm L), logs/ and out/.

Bars from gate75.tsv (92 rows, columns group metric piece off arm ref verdict):

* **primary — FAIL**: sherd 7 off-lip contour **18.00 mm** against the 12 mm bar (off 31.80, Stage 0
  17.40; 30 of 171 dots); pooled **31 of 571** against a bar of 29 of 565; sherd 5 at **1** off-lip dot
  (off 21). Sherds 6 and 8 stay at 0 — PASS.
* **pairs — 6-7 FAIL**: median **+0.561** with 3 opposed dots, against a bar of <= -0.9 with at least
  30 opposed. Every other pair is within 0.026 of off — PASS.
* **j1_ruler — PASS**: all five columns (blindDeg 45.89, farS0 0.8936, ring_cov_deg5 355.0,
  f2r_le1 0.4497, r2f_le1 0.4435) identical to the off arm, none worse by 10%.
* **pota — PASS**: 8 of 8 pieces within 1 dot of pota_off, run **without** SFS_REFINE_ADD_GATE (the
  ticket-74 trap).
* **coverage — PASS**: S0/S1/Bl0/Bl1 on 9/9 (arm_3x), 9/9 (j1_arm), 8/8 (pota_arm), 9/9 and 9/9 (both
  identity cells).
* **identity — 1x PASS, 3x FAIL**: with every switch unset the same binary reproduces the ticket-74
  off arm at 1x with nearest-neighbour distance 0.000 mm on 9 of 9 pieces (18 of 36 files
  byte-identical; the other 18 differ only in the uninitialised curvature column). At 3x, 8 of 9 pieces
  sit inside the 2.418 mm spread measured for piece 1, but **piece 6 reaches 2.480 mm** — the cited
  bound is exceeded by 0.062 mm, so the 3x identity is **not** claimed, and piece 6's own run-to-run
  spread is not measured here. The Arm L vs off 3x comparison is therefore inside the 3x noise band,
  which is exactly why every bar above is read against the off arm.

### Part D — the reading

> **the-remainder-survives-every-door**

The switch the Stage 0 slug implies was built, run on the same pinned 3x draw, and the line did not
move: 30 dots and 18.00 mm, i.e. the same dot count as Stage 0 and 0.6 mm more contour, against a
12 mm bar; pooled 31 versus a bar of 29; and one added off-lip dot on sherd 5. Its own census says why
— the new door was reached at 21 of the 30 dots and refused 2. The 6-7 pair is not restored either
(median +0.561, 3 opposed), and the fold is a different population (4 of 33 pairs are the same pair),
so no growth-side chord test can bring the opposed pair back. The residue is the boundary of the
surface label: these dots sit where the inner field stops reaching the rim, not where a growth decision
went wrong.

### Artefacts (C:/PR/artifacts/t75/)

remainder75.tsv, fold75.tsv, fold75_arm.tsv, stage75_summary.md, gate75.tsv, render75_before_after.png,
run.json (Arm L), run_stage0.json, plus scripts remainder75.py, fold75.py, arm_check75.py, gate75.py,
render75.py, submit_cells75_stage0.sbatch, submit_cells75_arml.sbatch and the pins/logs they used.
The render was written and looked at before this reading: sherd 7 before/after with the off-lip dots in
red, and the 6-7 seam before/after coloured by each dot's own product.

**Accepted-list status:** Stage 0 ran first and its slug is quoted above; remainder75.tsv and fold75.tsv
are complete with their caveats; exactly one default-off switch exists; the switch-unset identity is
stated at both scales including the 3x failure; gate75.tsv carries every group and bar with PASS/FAIL;
Pot A ran without the gate and is 8 of 8; every job's State/ExitCode is tabled above; the render exists
and was inspected; no commit was made by the worker.

## Lead — verification and adjudication (2026-11-16, Thinkbook16)

**verified** — each line recomputed by me from the arms' own output, not read from the worker's tables:

- `accept75.py` 35/35 (`C:/PR/artifacts/dsh-handover/75/accept75.py`; three of my own cases were
  wrong before it passed — `stage-summary-exists` tested the path string rather than the file,
  the table header test did not skip `#` comment lines, and the row range assumed 30 rows).
- **off-lip recount**, same frozen rule as tickets 72/73 (inner = normal·radial < -0.2, off = nearest
  inner point > 0.8 mm, contour = sum of consecutive steps), on `C:/PR/artifacts/t74/geom_off_3x`,
  `.../geom_Gnr_3x` and `C:/PR/artifacts/t75/geom_armL_3x` with
  `python C:/PR/artifacts/t75/lead_offlip75.py` → every gate row reproduced: off 1: 183/0,
  5: 150/21 (12.60 mm of 90.33), 6: 141/3, 7: 173/54 (31.80 of 104.01), 8: 126/9; Gnr 7: 171/30
  (17.40 of 103.16); arm L 5: 143/1 (0.60), 6: 134/0, 7: 171/30 (18.00 of 102.80), 8: 123/0,
  pooled 571 dots, 31 off, 18.60 mm.
- **the 6-7 pair statistic**, `python C:/PR/artifacts/t72/pairdot72.py --gt C:/PR/artifacts/t75/GT_mm
  --scale 3 --pieces 6,7` → off n=44 median −0.997 with 34 opposed; arm L n=33 median +0.561 with
  3 opposed. The six other pairs on the same run match the gate table.
- **the census**, recounted from the arm's own piece-7 log (`C:/PR/artifacts/t75/arm_p7/mesh.log`,
  `python C:/PR/artifacts/t75/census75b.py`) → 30 off-lip dots, all 30 within 3 tree units (1 mm)
  of a `[SFS-75] GROWDEC` line; chord branch used at 21, fallback at 9; the 3.0 mm door tested at
  21 and refusing 2; walk accepted at 10.
- render opened before the reading: left panels 54 of 173 off (off) against 30 of 171 (arm L), red =
  off-lip; right panels the 6-7 seam coloured by each dot's own product.

**adjudications**

1. **The reading stands, and it is sharper than "the door did not reach".** The door *was* tested —
   at 21 of 30 dots — and refused 2. Nine dots never reached a test at all, because the 3.0 mm ball
   held fewer than three claimed points (the same fallback hole this ticket flagged for the 1.5 mm
   test). A growth-side test can only refuse a point the growth is about to claim; these dots sit on
   the *patch boundary*, which ticket 72 and 73 showed is settled upstream of the growth. Arm L is
   therefore neutral-to-harmful: sherd 7 17.40 → 18.00 mm, one off-lip dot appearing on sherd 5,
   pooled 30 → 31.
2. **The 6-7 bar is wrong, and I withdraw the fold reading — including ticket 74's `+0.657`.**
   Measured at the tight pairs (|dp| < 0.5 mm): the 7-side dot sits median **1.91 mm** off its own
   inner wall in the off arm — i.e. on the break face — and **0.15 mm** in arm L; the 6-side goes
   0.24 → 0.06 mm; the median |n6·radial| goes **0.504 → 0.990** (`C:/PR/artifacts/t75/pairloc75.py`,
   window sweep in `window75.py`; the flip persists at 0.3 mm: off −0.996 over 11 pairs, arm L
   +0.561 over 11). Two mating *walls* have parallel normals; two mating *break faces* have
   anti-parallel ones. So a negative median means the line is still on the break face — the defect —
   and a positive one means it has moved onto the wall. The ticket's bar encoded "keep the line on
   the break face". The pair statistic must from now on be read **with** the wall position of the
   dots, never on its own.
3. **The off-lip count is not the only thing this arm moves.** It shifts the lines by up to 2.4 mm
   (p90 ≈ 2.0 mm) on pieces 5-8 while the off-lip score barely changes, so a future arm should carry
   a line-displacement metric beside the off-lip count.
4. **identity**: 1x byte-exact on all geometry; 3x worst 2.480 mm on piece 6 against the 2.418 mm
   bound — missed by 0.06 mm, the same unseeded ray cast as ticket 73's piece 1, with the banner
   reading off. Not claimed as passing; recorded as bounded-not-byte.
5. **weight**: one vessel, four scored sherds, one 3x draw per arm. Controls pass with the refinement
   gate stripped (Pot A 8 of 8; the J1 ruler's five columns identical), so this arm's failure is not
   the gate's.

**what it leaves** (proposal only — no ticket written): the stretch survives every growth-side door,
so the next lever is the patch boundary itself — either a *crease-aware re-cut* of the interior patch
before its boundary is extracted (ticket 72's trim and ticket 73's refinement gate both act on
membership, not on where the boundary is allowed to sit), or a second trim pass applied to the
*refined* cluster. Sherd 7's 15 mm stretch is the only remainder left, and piece 6 covers only 3 dots
of it.

