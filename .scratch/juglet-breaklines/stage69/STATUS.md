# stage69 STATUS (ticket 69: axis method + 2x density do not hurt other pots)

Worker state file. LF only. Worker measurements, NOT lead-verified. A later turn resumes from this file alone.

## Ticket
`.scratch/juglet-breaklines/issues/69-axis-density-corpus-check.md`. Answers U19, E1.
Branch `69-axis-density-corpus-check` in `C:/PR/worktrees/sfs/69`. Budget: <= 8 Slurm jobs, <= 24 h wall.
Order of work: **A (corpus GT axes) -> C (seating gate) -> B (density sweep) -> D (code switches)**.

## Plan (as written 2026-11-03, before any measurement)

- **Part A** — for every released piece that has a GT axis (141 of them), compute the folded angle between
  (i) the RELEASED axis in `Axes/` and (ii) each of four fixed estimators, and the GT axis in
  `Ground Truth Axes/`. **No transform on either side** (lead correction 2026-11-03: a rotation preserves
  the angle between two directions, so rotating only one side is meaningless; `_T.txt` answers a different
  question, the pose into the assembled pot frame). Estimators fixed across every pot, no per-piece GT
  selection: `nperp`, `nperpS1`, `pottS1`, `potsac_s0`. Report per pot median + p90 for released and for
  each estimator, and the count of pieces where an estimator is worse than released by more than 10 deg.
  Plus a label-free selection rule from the fit residual and its distance from the GT-optimal choice
  (diagnostic only, labelled).
- **Part C** — Pot A assembly, shipped floor, two arms: (i) shipped; (ii) densified lanes + hybrid axes.
  Gate: 8/8 pieces, 15/15 joins. If it fails, that outranks everything else.
- **Part B** — full chain on the same frozen clouds, arm D18 (sphere 1.8 / resample 1.9) vs D09
  (sphere 0.9 / resample 0.95), on Pot A (8), C (4), D (10), J (11) at minimum. Score every emitted lane
  (Bl0, Bl1) against the authors' own line with `score292.py`; report lanes at bar / measured per arm and
  the per-lane delta.
- **Part D** — `SFS_SPHERE_RADIUS_MM` env switch in `edgeline_extraction_headless.cpp` (range (0.4,5.0),
  default 1.8, unset byte-identical proved by md5); hybrid estimator as a tracked module + CLI
  `sfs_axes/hybrid.py`, default off; both switches off reproduces shipped output byte-for-byte.

## Corpus facts measured this turn (read-only probe, `stage69/probe69a.sh`/`probe69b.sh`/`probe69c.sh`)

`/data/gpfs/projects/punim2657/sfs_main/original_samples/SfS_pp/`:

| dir | n | per pot (A B C D E F G H I J) |
|---|---|---|
| `Ground Truth Axes/` | 141 | 8 9 4 28 31 5 7 11 27 11 |
| `Axes/` (released, what the assembler reads) | 163 | 8 9 6 32 34 7 7 11 30 19 |
| `Surfaces/` | 326 | 16 18 12 64 68 14 14 22 60 38 |
| `Breaklines/` | 326 | 16 18 12 64 68 14 14 22 60 38 |
| `Ground Truth/` | 152 `_T.txt` + 10 `_simple_graph.txt` | |

- 22 released-axis pieces have no GT axis (C 05/06, D 22/30/31/32, E 32/33/34, F 06/07, I 28/29/30,
  J 09/13/14/15/16/17/18/19); no piece has a GT axis without a released one.
- Surface files are 6 columns (x y z nx ny nz), CRLF, ~17-20k points each; 135 MB total.
- Released axis files can carry MORE THAN ONE line (37 of 163; up to 6 lines) — a PotSAC candidate set.
  GT axis files are always exactly one line.
- Both `Axes/` and `Ground Truth Axes/` use zero-padded names (`Pot_J_Piece_02_Axis.xyz`); the Juglet's
  own copies in `Dataset/Axes/Juglet/` are unpadded (`Juglet_Piece_2_Axis.xyz`). Join by pot+piece.
- The Juglet is Pot J. Its released axes live at `Axes/Pot_J_Piece_NN_Axis.xyz`, and Pot J GT exists for
  pieces 1-8, 10-12 (piece 9 has no GT axis).
- Python: login node `python3` is 3.11.15 with numpy 2.4.6 (no scipy check yet);
  `/data/gpfs/projects/punim2657/TORA/envs/tora/bin/python3` is 3.10.20 with numpy 2.2.6 + scipy 1.15.2.

## Lead's verified baseline (message 2026-11-03, no transform, released vs GT)

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

The pots whose baseline is already good and must not regress: A 1.68, B 2.42, D 2.54, E 2.81, G 2.17, I 2.22.

## Steps

- [x] Read ticket 69, ticket 68, stage68 STATUS + fit68/hybrid68/pott68, score292.py, stage67 arm/stage scripts
- [x] Corpus probe (counts, formats, per-pot inventory, python envs)
- [ ] Part A — estimator sweep over all ten pots
- [ ] Part C — Pot A seating control
- [ ] Part B — density sweep
- [ ] Part D — the two switches + defaults proof
- [ ] Results section in the ticket

## Runs

(none yet)
