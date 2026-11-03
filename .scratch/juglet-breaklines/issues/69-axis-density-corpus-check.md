# 69 — Do the axis method and 2x density hurt other pots? Verify, then merge

**What to build:** the evidence that lets the lead merge two Juglet-lane changes without risking the
corpus: (A) the ticket-68 axis method measured against the **released ground-truth axes of all ten
pots** (141 GT files), not just the Juglet; (B) the 2x lane density measured against the **authors'
own breaklines on other pots**, not just the Juglet; (C) an end-to-end seating control proving Pot A
still seats 8/8 and joins 15/15 with both changes on; (D) both changes landed as **opt-in, default-off**
switches so an unset run stays byte-identical, plus the fixes-ledger rows.

**Why now (2026-11-03, conservator):** "verify 1 and 2 doesn't hurt other pots, then merge to main.
use normal agent for this job." — where 1 = the ticket-68 axis method, 2 = the 2x lane density
(`sphereRadius` 0.9 + `RESAMPLE_D_MM` 0.95).

**Answers:** U19 (does the pipeline put the Juglet back together), E1 (do our breaklines let SfS find joins)

**Blocked by:** none (t68 merged bb64811; t66 lanes; the released corpus is read-only)

**Status:** in-progress
**Working in:** chat on Thinkbook16 (2026-11-03)
**Branch:** 69-axis-density-corpus-check, in /c/PR/worktrees/sfs/69
**Worker:** (unset)

## Spec

### Given (measured facts this stands on)

- The released corpus carries, under `/data/gpfs/projects/punim2657/sfs_main/original_samples/SfS_pp/`:
  `Ground Truth Axes/` **141 files** (A 8, B 9, C 4, D 28, E 31, F 5, G 7, H 11, I 27, J 11),
  `Ground Truth/` 152 `_T.txt` + 10 `_simple_graph.txt`, `Surfaces/` 326, `Breaklines/` 326,
  `Axes/` **163** (the released axes the assembler uses — more pieces than GT, because the authors
  also ship the 21 excluded ones). So a per-piece axis error against truth is measurable on every
  released pot, and an edgeline score against the authors' lines is measurable on 163 pieces.
- Axis file format is one line of six numbers: point xyz then direction xyz. `_T.txt` is a 4x4
  row-major R|t (ticket 67 lead verification).
- The Juglet measurement (ticket 68): hybrid estimator brings all nine pieces to 10.5-23.8 deg median
  folded angle, from 18.0-77.3; on the assembler it turns 9/18 true joins into candidates into 12/18.
  **Caveat carried forward: the per-piece estimator CHOICE used the GT gate.** A verification that
  uses GT to select on other pots would repeat that flaw and prove nothing.
- Density (ticket 68): exported spacing is set by the sphere walk
  (`edgeline_extraction_headless.cpp:477`, `double sphereRadius = 1.8;`), not `RESAMPLE_D_MM`
  (:556). Halving both gives ~2.1x dots at 0.90 mm measured spacing on all nine Juglet pieces. It is
  currently a HARDCODED literal with no env switch.
- The corpus bar for an edgeline is the one in `docs/agents` and the ledger: median <= 2.0 mm AND
  coverage >= 90 % against the authors' own line, with the documented exclusions (Pot C 01 interior
  Bl0, Pot J 09 both lines, Pot C 03 Bl1, and the five pieces outside the paper's set).
  Reference scorer: `.scratch/pota-repro/292/score292.py` (`score(ours, author)`, self-tested).
- Pot A is the seating control: 8/8 pieces and 15/15 joins at the shipped settings (t58 PA10, t67
  PACTL, t68 APA all reproduce it). Anything that breaks Pot A is not shippable.

### Task

1. **Part A — axis method against the corpus GT (all ten pots).** For every released piece that has a
   GT axis, compute the folded angle between (i) the RELEASED axis and (ii) each estimator's axis, and
   the GT axis, all mapped into the GT frame by that piece's `_T.txt` rotation.
   - Estimators to evaluate **fixed across every pot** (no per-piece GT selection):
     `nperp`, `nperpS1`, `pottS1`, `potsac_s0` — the four that the Juglet hybrid drew on
     (`stage68/fit68.py`, `stage68/hybrid68.py`).
   - Report per pot: median and p90 folded error for the released axis and for each estimator, and
     the count of pieces where an estimator is WORSE than the released axis by more than 10 deg.
   - State plainly whether any pot regresses. A pot where the released axes are already good (Pot A
     especially) must stay good.
   - Also report a **label-free selection rule** if one is cheap: pick the estimator per piece by the
     fit residual (`hybrid68.py:49 residuals()`: cylindricality + meridional + radius), and show how
     close that blind choice comes to the GT-optimal choice. If it is not cheap, say so and skip it.
2. **Part B — 2x density against the authors' breaklines on other pots.** Full preprocessing chain at
   two settings on the SAME frozen clouds: arm D18 (shipped, sphere 1.8 / resample 1.9) and arm D09
   (sphere 0.9 / resample 0.95). Cover at least Pot A (8), Pot C (4), Pot D (10), Pot J (11) — add
   more pots if the budget allows; state exactly which pieces ran.
   - Score every emitted lane (Bl0 and Bl1) against the authors' corresponding breakline with
     `score292.py`, and report per arm: lanes at bar / lanes measured, plus the median-distance and
     coverage distributions. Apply the documented exclusions; list excluded lanes separately.
   - The question is "does 2x density hurt a lane that is at bar today", so report the per-lane
     DELTA, not only the tallies: how many lanes cross the bar in either direction.
3. **Part C — seating control (the decisive one).** Pot A assembly, shipped floor, two arms:
   (i) shipped settings; (ii) densified lanes + hybrid axes. Arm (ii) must still be 8/8 pieces and
   15/15 joins. If it is not, say so with the numbers — that outranks everything else in this ticket.
4. **Part D — land both changes as opt-in switches (code).**
   - `SFS_SPHERE_RADIUS_MM` in `edgeline_extraction_headless.cpp`: parse at the existing env block
     (near :581-620), valid range (0.4, 5.0), default 1.8, **unset must be byte-identical** (prove it:
     one piece, unset vs explicit 1.8, md5 of Bl0/Bl1).
   - The hybrid axis estimator as a tracked module + CLI (`sfs_axes/hybrid.py`, default off), taking
     the surfaces and writing the six-number file; the released axes are never overwritten in place.
   - Prove the switch defaults: a run with both unset reproduces the shipped output byte-for-byte.
5. **Write `## Results`** with the three tables (axis per pot, density per arm with deltas, seating
   control), the renders for Part C, the sacct table, and the merge recommendation with its risks.

### Acceptance

- Every claim carries file:line or a measured number from a named run dir.
- Part A must NOT select anything by GT when reporting a method; only the diagnostic comparison may
  use GT, and it must be labelled as such.
- Part C is the gate: if Pot A drops below 8/8 or 15/15, the ticket says so and recommends NOT merging.
- Defaults: unset runs byte-identical, proved by md5, both switches.
- Every sbatch polled (sacct directly; `scripts/slurm_poll.sh` has hung before) and the final
  State/ExitCode recorded.
- Budget: <= 8 Slurm jobs, <= 24 h wall.
- Worker measures and implements; the lead verifies and merges.

**Edges:** the released corpus and `sfs_main/original_samples` are read-only; the t66/t68 run dirs are
read-only; no parameter is varied by copying a tree.
