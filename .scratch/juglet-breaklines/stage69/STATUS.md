# stage69 STATUS (ticket 69: axis method + 2x density do not hurt other pots)

Worker state file. LF only. Worker measurements, NOT lead-verified. A later turn resumes from this file alone.

## Ticket
`.scratch/juglet-breaklines/issues/69-axis-density-corpus-check.md`. Answers U19, E1.
Branch `69-axis-density-corpus-check` in `C:/PR/worktrees/sfs/69`. Budget: <= 8 Slurm jobs, <= 24 h wall.
Order of work: **A (corpus GT axes) -> C (seating gate) -> B (density sweep) -> D (code switches)**.
Jobs used so far: **4 of 8** (all four were Part A).

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
  `edgeline_extraction_headless.cpp` (range (0.4,5.0), defaults 1.8 / 1.9, unset byte-identical proved by
  md5); hybrid estimator as a tracked module + CLI `sfs_axes/hybrid.py`, default off.

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

## Steps

- [x] Read ticket 69, ticket 68, stage68 STATUS + fit68/hybrid68/pott68, score292.py, stage67 arm/stage scripts
- [x] Corpus probe (counts, formats, per-pot inventory, python envs)
- [x] Part A — estimator sweep over all ten pots (4 jobs) + edge gate + sin-alpha mechanism
- [x] Part D — the two switches written (commit b8fed69); byte-identity proof pending job 5
- [ ] Part B — density panel (Pot A / C / D / J), lane scoring with score292.py
- [ ] Part C — Pot A density-only seating arm at floor 50 (assembler job, separate from preprocessing)
- [ ] Results section in the ticket

## Runs

| run dir | job | state | what |
|---|---|---|---|
| `runs/20261103-1733_45ba206_t69-axis-corpus` | 34273111 | COMPLETED 0:0 00:00:42 | Part A pass 1 (no npar) |
| same | 34273167 | COMPLETED 0:0 00:00:53 | Part A pass 2 (+npar) |
| same | 34273237 | COMPLETED 0:0 00:00:52 | Part A pass 3 (dirs.tsv writer crashed, fixed) |
| same | 34273319 | COMPLETED 0:0 00:00:46 MaxRSS 424MB | Part A final pass + edge gates |

Run-dir naming wart to state in Results: the directory is named for commit 45ba206 but later passes ran
1e8d07d / 0d31740 from `work/` (md5s in `logs/provenance.log`).

## Next action

Submit job 5 (`submit69b.sbatch`, STAGE=all): build + Part D proof + the four density cells.
