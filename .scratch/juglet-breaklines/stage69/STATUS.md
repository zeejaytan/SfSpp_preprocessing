# stage69 STATUS (ticket 69: axis method + 2x density do not hurt other pots)

Worker state file. LF only. Worker measurements, NOT lead-verified. A later turn resumes from this file alone.

## Ticket
`.scratch/juglet-breaklines/issues/69-axis-density-corpus-check.md`. Answers U19, E1.
Branch `69-axis-density-corpus-check` in `C:/PR/worktrees/sfs/69`. Budget: <= 8 Slurm jobs, <= 24 h wall.
Order of work: **A (corpus GT axes) -> C (seating gate) -> B (density sweep) -> D (code switches)**.
Jobs used: **8 of 8** (final) — 4 Part A (34273111 / 34273167 / 34273237 / 34273319), job 5
the density panel (34274535, in flight), job 6 Part C (34275210, COMPLETED, **superseded — wrong axis dir**),
job 7 Part C corrected (34275406, in flight). Job 5's first attempt 34274349 FAILED 6:0 in 2m24s (a staging
bug, no evidence) and counts against the budget. **One job remains after these.**

## Plan (as written 2026-11-03, before any measurement)

- **Part A** — for every released piece that has a GT axis (141 of them), compute the folded angle between
  (i) the RELEASED axis in `Axes/` and (ii) each of four fixed estimators, and the GT axis in
  `Ground Truth Axes/`. **No transform on either side** (lead correction 2026-11-03: a rotation preserves
  the angle between two directions, so rotating only one side is meaningless; `_T.txt` answers a different
  question, the pose into the assembled pot frame). Estimators fixed across every pot, no per-piece GT
  selection. Plus a label-free selection rule from the fit residual (diagnostic only, labelled).
- **Part C** — Pot A seating, shipped floor 50, control = the already-measured PACTL arm (8/8, 15/15).
  The arm to build is **density only**: Pot A lanes re-traced at sphere 0.9 / resample 0.95, everything
  else shipped. (Lead input 10: the t68 axis method ships no Pot A axes, so "both changes on" is not
  definable for Pot A; Part C reduces to the density question.)
- **Part B** — one mesh stage per piece feeding two edge stages, arm 18 (sphere 1.8 / resample 1.9) vs
  arm 09 (sphere 0.9 / resample 0.95), on Pot A (8), C (4), D (10), J (11). Score every emitted lane
  (Bl0, Bl1) against the authors' own line with `score292.py`; report lanes at bar / measured per arm and
  the per-lane delta direction.
- **Part D** — `SFS_SPHERE_RADIUS_MM` + `SFS_RESAMPLE_D_MM` env switches in
  `edgeline_extraction_headless.cpp` (range (0.4,5.0), defaults 1.8 / 1.9). **The gate is NOT md5** — the
  writer is not bit-stable; see "Part D proof" below for the restated gate (counts + positions + POINTS
  header, normal delta as a number). Hybrid estimator as a tracked module + CLI `sfs_axes/hybrid.py`,
  default off.

## Corpus facts measured (read-only probes)

`/data/gpfs/projects/punim2657/sfs_main/original_samples/SfS_pp/`:

| dir | n | per pot (A B C D E F G H I J) |
|---|---|---|
| `Ground Truth Axes/` | 141 | 8 9 4 28 31 5 7 11 27 11 |
| `Axes/` (released, what the assembler reads) | 163 | 8 9 6 32 34 7 7 11 30 19 |
| `Surfaces/` | 326 | 16 18 12 64 68 14 14 22 60 38 |
| `Breaklines/` | 326 | 16 18 12 64 68 14 14 22 60 38 |
| `Ground Truth/` | 152 `_T.txt` + 10 `_simple_graph.txt` | |

- 22 released-axis pieces have no GT axis (C 05/06, D 22/30/31/32, E 32/33/34, F 06/07, I 28/29/30,
  J 09/13/14/15/16/17/18/19); no piece has a GT axis without a released one. They are excluded from the
  estimator-vs-GT medians **explicitly**, not silently.
- Surface files are 6 columns (x y z nx ny nz), CRLF, ~17-20k points each; 135 MB total.
- Released axis files can carry MORE THAN ONE line (37 of 163; up to 6) — a PotSAC candidate set.
  GT axis files are always exactly one line. `BreakLine::ReadAxis`
  (`structure-from-sherds-pp/class/data_structure.cpp:142-176`) pushes **every** line into
  `axis_point_`/`axis_norm_`, so extra lines are already in the assembler's search space.
- **Our nine-piece Juglet is NOT released Pot J.** Different object: zero shared axis md5, closest fold
  6.1-36.2 deg (median 18.6), different scale and frame. Released Pot J is one more corpus pot (the
  heavy-tail one). Never present a Juglet number as a Pot J number.
- Both corpus dirs use zero-padded names (`Pot_J_Piece_02_Axis.xyz`); `Dataset/Axes/Juglet/` is unpadded.
  Join by pot+piece, never filename.
- `$CORP/Mesh` is FLAT (164 files); `Dataset/Mesh` carries only Juglet, Pot_A, Pot_C, Pot_TEST. Pot C
  02-04, Pot D and Pot J meshes exist only in the corpus.
- Python: login node `python3` 3.11.15 + numpy 2.4.6; `/data/gpfs/projects/punim2657/TORA/envs/tora/bin/python3`
  is 3.10.20 + numpy 2.2.6 + scipy 1.15.2 (what sbatch scripts use).

## Lead's verified baseline (no transform, released vs GT)

| pot | n | median | p90 | max |
|---|---|---|---|---|
| Pot_A | 8 | 1.68 | 30.36 | 58.87 |
| Pot_B | 9 | 2.42 | 15.37 | 23.46 |
| Pot_C | 4 | 11.39 | 47.58 | 59.90 |
| Pot_D | 28 | 2.54 | 72.49 | 80.63 |
| Pot_E | 31 | 2.81 | 14.45 | 82.06 |
| Pot_F | 5 | 4.56 | 9.53 | 9.96 |
| Pot_G | 7 | 2.17 | 2.36 | 2.41 |
| Pot_H | 11 | 29.08 | 80.31 | 89.42 |
| Pot_I | 27 | 2.22 | 7.79 | 62.95 |
| Pot_J | 11 | 25.65 | 59.68 | 89.91 |
| ALL | 141 | 2.78 | 58.28 | 89.91 |

Pots whose baseline is already good and must not regress: A 1.68, B 2.42, D 2.54, E 2.81, G 2.17, I 2.22.

## Part A — DONE (jobs 34273111 / 34273167 / 34273237 / 34273319, all COMPLETED 0:0)

Run dir `/data/gpfs/projects/punim2657/SfSpp/runs/20261103-1733_45ba206_t69-axis-corpus/`; outputs pulled
to `stage69/outA/` (pieces.tsv, dirs.tsv, selection.tsv, per_pot.tsv, per_pot_worse.tsv,
baseline_good.tsv, edge_gate.tsv, crosspiece_gate.tsv). Script `stage69/partA69.py`, gate instrument
`stage69/gatepass69.py`.

**Per-pot MEDIAN folded angle to GT (deg)** — n / rel0 / relbest / nperp / nperpS1 / npar / nparS1 / pottS1 / potsac_s0 / oracle / blind:

| pot | n | rel0 | relbest | nperp | nperpS1 | npar | nparS1 | pottS1 | potsac_s0 | oracle | blind |
|---|---|---|---|---|---|---|---|---|---|---|---|
| A | 8 | 1.68 | 1.68 | 81.07 | 77.41 | - | - | 25.00 | 49.57 | 24.50 | 78.46 |
| B | 9 | 2.42 | 2.42 | 47.85 | 47.91 | 43.93 | 45.66 | 37.31 | 49.30 | 35.54 | 47.85 |
| C | 4 | 11.39 | 3.20 | 53.95 | 52.63 | 66.80 | 66.83 | 53.72 | 61.15 | 25.48 | 52.63 |
| D | 28 | 2.54 | 2.51 | 40.66 | 28.55 | 77.05 | 77.15 | 53.29 | 53.00 | 14.69 | 28.55 |
| E | 31 | 2.81 | 2.50 | 23.18 | 19.77 | 72.21 | 74.45 | 20.52 | 46.34 | 10.03 | 19.93 |
| F | 5 | 4.56 | 4.56 | 83.62 | 71.90 | 50.15 | 54.99 | 36.52 | 65.75 | 36.52 | 83.62 |
| G | 7 | 2.17 | 2.17 | 42.77 | 40.17 | 47.23 | 51.04 | 39.34 | 57.10 | 36.41 | 42.19 |
| H | 11 | 29.08 | 5.71 | 89.58 | 88.82 | 16.33 | 22.38 | 17.04 | 25.84 | 14.48 | 89.63 |
| I | 27 | 2.22 | 2.22 | 21.59 | 21.34 | 74.65 | 74.07 | 39.65 | 58.88 | 11.96 | 21.48 |
| J | 11 | 25.65 | 17.74 | 63.58 | 57.38 | 65.02 | 64.58 | 50.79 | 57.02 | 28.52 | 63.58 |
| ALL | 141 | 2.78 | 2.68 | 47.60 | 42.71 | 66.47 | 67.77 | 27.00 | 51.96 | 17.04 | 44.03 |

`relbest` is an ORACLE (per piece, the line closest to the GT axis) and must never be presented as
deployable. The blind residual rule agrees with the GT-optimal pick on only 32 of 141 pieces.

**Edge gate** (folded angle <= 25 deg between two pieces' axes, `feature_matching.cpp:1715`, each piece's
axis mapped by its GT rotation; 286 corpus edges with both ends GT-axed) — rel0 **217/286 (75.9%)**,
relbest 257/286, pottS1 109/286, nperpS1 98/286, nperp 81/286, npar 59/286, nparS1 52/286,
potsac_s0 36/286. Per pot rel0 / relbest: A 2.6 12/15 / 2.6 15/15; B 3.3 13/15 / 3.3 15/15;
C 60.6 2/5 / 2.3 5/5; D 3.8 49/69 / 3.3 58/69; E 2.9 52/62 / 2.7 62/62; F 3.4 7/7 / 3.4 7/7;
G 2.2 10/10 / 2.2 10/10; H 45.2 6/17 / 8.6 14/17; I 2.6 59/65 / 2.6 59/65; J 40.4 7/21 / 23.8 12/21.

**Conclusion (lead-verified 2026-11-03):** the ticket-68 axis method does NOT transfer to the corpus.
Replacing the released axis with any t68 estimator drops Pot A from 12/15 to 1-6 of 15 on the very gate
that decides seating, and the corpus from 217/286 to 36-109/286. Recommendation: leave the axis method
out of the corpus default (Juglet-only, behind an off-by-default switch).

## Part D — code written and committed (b8fed69)

`edgeline_extraction_headless.cpp`: `SFS_SPHERE_RADIUS_MM` at the sphere walk (`:477`, default literal
kept, range (0.4,5.0), prints `[SPHERE-69]`), `SFS_RESAMPLE_D_MM` at `:556` (default 1.9f, range
(0.4,5.0), prints `[RESAMPLE-69]`). `sfs_axes/hybrid.py` is the default-off hybrid estimator (module +
CLI). The byte-identity proof is job 5's Part D section (below).

## Part B / D — job 5 (the density panel), in flight

Run dir `/data/gpfs/projects/punim2657/SfSpp/runs/20261103-0734_601013e_t69-density-panel`, job **34274535**.
First attempt 34274349 (run `20261103-0729_ae5ad59`) FAILED 6:0 in 2m24s: the Part D proof ran the mesh
stage from the RUN dir instead of the staged tree, and the binaries resolve their inputs relative to the
working directory (`filesystem error: recursive directory iterator cannot open directory: No such file or
directory [Dataset/Point/Pot_A/]`). Fixed in 601013e.

What job 5 does, in one job: build the ticket-69 tree from a git-archive of the pushed commit; assert both
switch literals still occur exactly once; run the Part D proof (one piece, edge stage twice, unset vs
explicit 1.8/1.9); then four density cells (Pot A 8, Pot C 4, Pot D 01-10, Pot J 01-11), each piece
staged ONCE and its post-mesh snapshot copied per arm so the two densities are a paired measurement
(the mesh stage draws 30 unseeded ray-cast points, so two full chains are not the same input).

**Part D proof — the md5 gate is INVALID AS WRITTEN (lead correction, 2026-11-03, job 34275026).**
Job 5 reported "identical no" (unset Bl0 `260e20878d9557cce2556895f888a06e` 203 dots vs explicit
`4d94a2e444c7de99d64d2d0fe5ba077b` 203; Bl1 `abe000137e947d2d3d1d0a02f1744ddc` 210 vs
`20eef04a230e4b6922036ed8f57bd995` 210). That is **not** a switch failure: the writer is not bit-stable.
The lead re-ran it four times on one identical staged tree (job 34275026, run
`runs/20261103-1926_detprobe7_t69d-det`, one mesh stage then the edge stage unset x2 / explicit 1.8+1.9 x2)
and got **different md5 between two runs of the SAME arm**.

**The gate, restated** — (a) identical dot COUNTS, (b) identical POSITION columns to 0.000 mm, (c) identical
header POINTS field; the normal-column delta is reported as a MEASURED NUMBER, never an md5 verdict.
Applied by `geomid69.py` (rewritten 2026-11-03) to the lead's four arms — every number measured by this
worker from `runs/20261103-1926_detprobe7_t69d-det/out/`:

| pair | lane | dots a/b | max position delta | normal median / max deg | POINTS hdr | same counts / positions |
|---|---|---|---|---|---|---|
| unset_a : unset_b (same arm) | Bl0 | 203/203 | 0.000000 mm | 0.208 / 0.898 | 203/203 | yes / yes |
| unset_a : unset_b (same arm) | Bl1 | 210/210 | 0.000000 mm | 0.247 / 0.624 | 210/210 | yes / yes |
| explicit_a : explicit_b (same arm) | Bl0 | 203/203 | 0.000000 mm | 0.187 / 0.540 | 203/203 | yes / yes |
| explicit_a : explicit_b (same arm) | Bl1 | 210/210 | 0.000000 mm | 0.188 / 0.904 | 210/210 | yes / yes |
| unset_a : explicit_a (SWITCH) | Bl0 | 203/203 | 0.000000 mm | 0.136 / 0.498 | 203/203 | yes / yes |
| unset_a : explicit_a (SWITCH) | Bl1 | 210/210 | 0.000000 mm | 0.214 / 0.721 | 210/210 | yes / yes |
| unset_b : explicit_b (SWITCH) | Bl0 | 203/203 | 0.000000 mm | 0.183 / 0.682 | 203/203 | yes / yes |
| unset_b : explicit_b (SWITCH) | Bl1 | 210/210 | 0.000000 mm | 0.347 / 0.816 | 210/210 | yes / yes |

Position md5 identical in all eight pairs (Bl0 `8c6c4dbcc9c5d4d6bb1cfe2e5de5e44a`, Bl1
`bc428262059363fb5210777c04c40e07`), and the same-arm normal jitter (0.19-0.25 deg median) is the same
size as the cross-arm one (0.14-0.35 deg) — i.e. the switches are inert with respect to geometry and the
residual jitter is pre-existing writer non-determinism (the curvature column is denormal dust, 1e-28).
Job 6 (Part C) re-measures the same four-pair table in its own job so the claim is reproduced, not quoted.

**Part B lane counts, job 5 as of the last poll** (bl0_18 / bl1_18 / bl0_09 / bl1_09): Pot A 203/210/415/426,
162/168/331/343, 152/157/311/319, 147/151/298/309, 144/149/294/305, 146/150/298/305, 63/65/130/134,
57/61/119/127 — every piece `ok`, and the 0.9 mm lane is 2.04x the 1.8 mm lane on every piece. Pot C 01
207/226/423/461. Pot C 02-04, Pot D and Pot J were still running.

## Part C — Pot A seating, density only (the gate)

Two runs. The control is already measured read-only: t67 `out/PACTL/'1. Acc.txt'` = 8/8 pieces, 15/15 joins
(Time 433813 Sec); t68 `guard68/out/GPA50` reproduces it (8/8, 15/15, Time 196962 Sec).

**Job 6, 34275210, `runs/20261103-0754_b23aedf_t69-pota-seat` — COMPLETED 0:0 00:15:07. SUPERSEDED, and
its gate is evidence about nothing.** Three arms at floor 50: POTA18 (shipped lanes), POTA09 (densified),
JUG09F50 (Juglet 0.9 mm lanes at the SHIPPED floor 50). POTA18 and POTA09 both returned
**7 / 8 pieces and 12 / 15 joins**, byte-identical gates (the two Acc.txt differ only in the Time line,
184167 vs 653507 Sec), 8 pieces placed and 8 edgelines written in each arm.

The control arm failed too, so this is **not a density effect**. It is a staging error in submit69c:
`--axis-dir "$DS/Axes/Pot_A"` (`Pot_A_Piece_01` d4121141...) instead of the corpus axes
`$CORP/Axes/Pot_A_Piece_01_Axis.xyz` (74086636...) that PACTL and GPA50 read. Measured line-1 fold between
the two files, pieces 01-08: **0.67, 1.00, 0.68, 1.68, 3.28, 24.72, 2.45, 15.57 deg** — pieces 06 and 08 move
by 24.7 and 15.6 deg, the size of change that can cost Pot A a piece and three joins. Proof the controls used
the corpus files: `runs/20261103-1429_3b3efbc_t67-juglet-assembly/trees/pota/Axes/Pot_A_Piece_01_Axis.xyz`
md5 = 74086636... = the corpus file (stager `guard68/instruments/stage67_inputs.py:112-125` hardlinks from
the corpus root).

**JUG09F50 (lead input 5, answered): 0 / 8 pieces, 0 / 13 joins.** 2x density alone at the shipped floor 50
takes the Juglet from 2 of 9 pieces entering to 8 of 9 (P9 is 49 dots, one short) — and seats nothing.
Consistent with ticket 67: lowering the floor is not what is missing.

**Job 7, 34275406, `runs/20261103-0811_08d08b0_t69-pota-axes` — the corrected Part C.** Same two arms,
everything identical to submit69c except `--axis-dir "$CORP/Axes"`; arms renamed POTA18C / POTA09C; the
Juglet arm dropped (already answered). Reading rule written into the job header: if POTA18C is 8/8 + 15/15
the harness matches PACTL and POTA09C answers the ticket; if POTA18C is itself below 8/8 the harness differs
from PACTL in some other way and neither arm says anything about density.

## Steps (final, 2026-11-03)

- [x] Read ticket 69, ticket 68, stage68 STATUS + fit68/hybrid68/pott68, score292.py, stage67 arm/stage scripts
- [x] Corpus probe (counts, formats, per-pot inventory, python envs)
- [x] Part A — estimator sweep over all ten pots (4 jobs) + edge gate + sin-alpha mechanism + any-pair ceiling
- [x] Part D — the two switches written (b8fed69); restated gate measured (counts + positions + POINTS header)
- [x] Part B — density panel (job 5) + all 62 lanes scored with score292.py; 62/62 at bar in both arms
- [x] Part C — Juglet floor-50 question answered (JUG09F50: 8/9 pieces enter, 0/8 seat)
- [x] Part C — Pot A gate PASSES: job 7 POTA18C 8/8 + 15/15, POTA09C 8/8 + 15/15
- [x] Renders (render69.py) for PACTL / POTA18C / POTA09C — bbox and piece counts verified, NOT by eye
- [x] Results section in the ticket (Table 1 axis, Table 2 density, Table 3 seating, Table 4 switches, sacct,
      merge recommendation, risks)
- [ ] Lead verification and merge (lead's job; worker does not merge or push to main)

## Answer in one paragraph

**Density passes, the axis method does not.** Pot A seats **8/8 and 15/15 at 0.9 mm lanes**, identical to
1.8 mm (job 34275406). 62 corpus lanes across Pots A/C/D/J are at bar in BOTH arms with **0 crossed out and
0 crossed in**, 2.04x the dots at the same accuracy. The axis method is a **regression** on the corpus:
replacing the released axis with any t68 estimator drops Pot A from **12/15 to 1-6 of 15** on the
assembler's 25 deg gate and the corpus from **217/286 to 36-109/286**, and an estimator writes one line
where the released files supply several (any-line-pair 262/288 against line-1's 219/288). Merge the density
switch (default off); land the axis method only as a Juglet-lane opt-in never applied to the corpus.

## Runs (final)

| run dir | job | state | what |
|---|---|---|---|
| `runs/20261103-1733_45ba206_t69-axis-corpus` | 34273111 | COMPLETED 0:0 00:00:42 | Part A pass 1 (no npar) |
| same | 34273167 | COMPLETED 0:0 00:00:53 | Part A pass 2 (+npar) |
| same | 34273237 | COMPLETED 0:0 00:00:52 | Part A pass 3 (dirs.tsv writer crashed, fixed) |
| same | 34273319 | COMPLETED 0:0 00:00:46 MaxRSS 424MB | Part A final pass + edge gates |
| `runs/20261103-0729_ae5ad59_t69-density-panel` | 34274349 | **FAILED 6:0** 00:02:24 | job 5 attempt 1: proof stage ran from the run dir, no evidence |
| `runs/20261103-0734_601013e_t69-density-panel` | 34274535 | **FAILED 1:0** 00:42:19 | Part B density panel — rc_any=1 from the Pot C 03 segfault; all four cells' data landed and are used |
| `runs/20261103-0754_b23aedf_t69-pota-seat` | 34275210 | COMPLETED 0:0 00:15:07 | Part C attempt 1: 7/8 + 12/15 in BOTH arms — staged `Dataset/Axes/Pot_A`, **superseded, no evidence**. JUG09F50 0/8 0/13 |
| `runs/20261103-0811_08d08b0_t69-pota-axes` | 34275406 | COMPLETED 0:0 00:12:55 | **Part C corrected: POTA18C 8/8 15/15, POTA09C 8/8 15/15** + the four-run Part D proof |
| `runs/20261103-1926_detprobe7_t69d-det` | 34275026 | COMPLETED 0:0 00:02:10 | the lead's own determinism probe; its `out/` is what `geomid69.py` re-measured |

Run-dir naming wart stated in Results: `20261103-1733_45ba206_t69-axis-corpus` is named for commit 45ba206
but its later passes ran 1e8d07d / 0d31740 from `work/` (md5s in `logs/provenance.log`).

## Next action

None for the worker. Hand to the lead: verify the four tables, merge the density switch to main, and keep
the axis method behind `sfs_axes/hybrid.py` default-off, Juglet-only. Open questions the ticket names:
(i) 2x density with `MINIMUM_NUMBER` 12 (the physical equivalent of 6 at 1.8 mm) — not run;
(ii) the Pot C 03 short-segment segfault at `edgeline_extraction_headless.cpp:3003` — unfixed;
(iii) whether any other pot's seating survives density — only Pot A was assembled.
