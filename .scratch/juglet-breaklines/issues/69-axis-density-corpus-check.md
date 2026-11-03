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

**Status:** ready-for-human — lead verified 2026-11-03, merged be5980c (density default-off merged; axis method stays Juglet-lane opt-in, default-off)
**Working in:** chat on Thinkbook16 (2026-11-03)
**Branch:** 69-axis-density-corpus-check, in /c/PR/worktrees/sfs/69
**Worker:** ticket-69 worker session (2026-11-03); lead verified Parts A/B/C/D independently

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


## Results

Worker measurements, 2026-11-03. Every number below is from a named run directory or a named file line;
the sacct table at the end records each job's final state. Budget used: **8 Slurm jobs** (34273111,
34273167, 34273237, 34273319, 34274349, 34274535, 34275210, 34275406), 8 h 41 m wall.

### Table 1 — the axis method against the corpus ground truth (Part A)

For every released piece that has a GT axis (**141 pieces**; the 22 released-axis pieces with no GT axis
are excluded from these medians **explicitly** — C 05/06, D 22/30/31/32, E 32/33/34, F 06/07, I 28/29/30,
J 09/13/14/15/16/17/18/19 — they can be scored only against the released axis), the folded angle between
the GT axis and each estimator. **No transform on either side**: a rotation preserves the angle between two
directions, so rotating one side only is meaningless (`_T.txt` is the pose into the assembled pot frame and
answers a different question). Estimators are **fixed across every pot — nothing is selected per piece by GT**.

Run `runs/20261103-1733_45ba206_t69-axis-corpus/`, job 34273319, `out/per_pot.tsv`:

| pot | n | released line 1 | nperp | nperpS1 | npar | nparS1 | pottS1 | potsac_s0 | blind residual |
|---|---|---|---|---|---|---|---|---|---|
| A | 8 | **1.68** | 81.07 | 77.41 | 37.05 | 37.87 | 25.00 | 49.57 | 78.46 |
| B | 9 | **2.42** | 47.85 | 47.91 | 43.93 | 45.66 | 37.31 | 49.30 | 47.85 |
| C | 4 | 11.39 | 53.95 | 52.63 | 66.80 | 66.83 | 53.72 | 61.15 | 52.63 |
| D | 28 | **2.54** | 40.66 | 28.55 | 77.05 | 77.15 | 53.29 | 53.00 | 28.55 |
| E | 31 | **2.81** | 23.18 | 19.77 | 72.21 | 74.45 | 20.52 | 46.34 | 19.93 |
| F | 5 | **4.56** | 83.62 | 71.90 | 50.15 | 54.99 | 36.52 | 65.75 | 83.62 |
| G | 7 | **2.17** | 42.77 | 40.17 | 47.23 | 51.04 | 39.34 | 57.10 | 42.19 |
| H | 11 | 29.08 | 89.58 | 88.82 | **16.33** | 22.38 | 17.04 | 25.84 | 89.63 |
| I | 27 | **2.22** | 21.59 | 21.34 | 74.65 | 74.07 | 39.65 | 58.88 | 21.48 |
| J | 11 | 25.65 | 63.58 | 57.38 | 65.02 | 64.58 | 50.79 | 57.02 | 63.58 |
| **ALL** | **141** | **2.78** | 47.60 | 42.71 | 66.47 | 67.77 | 27.00 | 51.96 | 44.03 |

Pieces where an estimator is worse than the released line by more than 10 deg (`per_pot_worse.tsv`):
**nperp 116/141, nperpS1 111, npar 114, nparS1 116, pottS1 79, potsac_s0 115.** On the six pots whose
baseline is already good and must not regress (A B D E G I, n = 110): rel0 median 2.34 / p90 39.41,
nperp 42.09 / 84.80, npar 68.81 / 87.96, pottS1 32.40 / 81.30, potsac_s0 51.32 / 86.21.

**No pot improves except H.** Pot H is the single pot where the estimators beat the released axes
(npar 16.33 against 29.08), and it was found by looking at the answer, so it is not acted on.

**Why nperp collapses** (reproduced exactly, `pieces.tsv` columns `sin_alpha_gt` / `nperp`): nperp is the
minimum eigenvector of the wall normals' covariance, which is the pot axis only while
sin(alpha) = mean|n.axis| is below sin(35.26 deg) = 0.577.

| sin(alpha) | n | nperp median deg | within 25 deg |
|---|---|---|---|
| 0.000-0.300 | 45 | 16.71 | 69 % |
| 0.300-0.450 | 32 | 29.19 | 41 % |
| 0.450-0.577 | 5 | 64.93 | 0 % |
| 0.577-0.700 | 22 | 62.55 | 0 % |
| 0.700-0.850 | 16 | 74.63 | 0 % |
| 0.850-1.010 | 21 | 88.80 | 0 % |

It is a specialist for deep steep-walled bodies and it fails exactly where walls flatten — shoulders,
bases, wide bowls. `npar` is the mirror image (right on flat/base fragments, wrong on cylinders).

**A label-free per-piece selection rule does not rescue it.** The blind rule (pick the estimator with the
smallest fit residual, cylindricality + meridional + radius, `hybrid68.py:49`; GT never consulted) agrees
with the GT-optimal pick on **32 of 141 pieces** and its own corpus median is **44.03 deg** against the
released line's 2.78. The GT-optimal per-piece pick ("oracle") reaches 17.04 deg — still 6x worse than the
released axes, because the estimator family itself is wrong here, not merely mis-chosen.
### The column the merge decision turns on: the assembler's own 25 deg axis gate

`feature_matching.cpp:1715` admits an edge only if the folded angle between the two pieces' axes is
<= 25 deg. Each piece's axis is rotated into the assembled frame by its own GT pose. 286 corpus edges
have a GT axis at both ends; `out/edge_gate.tsv`:

| pot | released line 1 (median / pass) | nperp | nperpS1 | pottS1 | potsac_s0 |
|---|---|---|---|---|---|
| A | **2.6 / 12 of 15** | 59.7 / 1 | 59.7 / 1 | 26.2 / 6 | 60.1 / 1 |
| B | **3.3 / 13 of 15** | 59.4 / 1 | 59.1 / 1 | 32.3 / 2 | 45.6 / 6 |
| C | 60.6 / 2 of 5 | 75.3 / 1 | 75.9 / 1 | 52.2 / 0 | 85.2 / 0 |
| D | **3.8 / 49 of 69** | 39.6 / 18 | 33.8 / 21 | 37.7 / 29 | 64.8 / 9 |
| E | **2.9 / 52 of 62** | 27.5 / 28 | 19.8 / 37 | 23.6 / 32 | 55.1 / 8 |
| F | **3.4 / 7 of 7** | 65.5 / 0 | 58.2 / 0 | 33.5 / 1 | 63.9 / 0 |
| G | **2.2 / 10 of 10** | 42.0 / 1 | 34.4 / 2 | 42.4 / 2 | 72.1 / 0 |
| H | 45.2 / 6 of 17 | 32.9 / 7 | 32.3 / 8 | 13.4 / 16 | 62.3 / 6 |
| I | **2.6 / 59 of 65** | 33.9 / 24 | 27.7 / 27 | 46.8 / 21 | 65.5 / 5 |
| J | 40.4 / 7 of 21 | 60.5 / 0 | 62.2 / 0 | 70.4 / 0 | 68.6 / 1 |
| **ALL** | **217 of 286 (75.9 %)** | 81 (28.3 %) | 98 (34.3 %) | 109 (38.1 %) | 36 (12.6 %) |

**Replacing the released axis with any ticket-68 estimator drops Pot A from 12 of 15 to 1-6 of 15 on the
very gate that decides seating, and the corpus from 217/286 to 36-109/286.** Pot A is the seating control
and it passes only 12 of 15 today and still seats 8/8 — a few bad axes are survivable; what is not
survivable is most of them being bad.

**The multi-line search space makes this worse for any estimator, not better.** Released axis files carry
more than one line on 37 of 163 pieces, and `BreakLine::ReadAxis`
(`structure-from-sherds-pp/class/data_structure.cpp:142-176`) pushes **every** line into
`axis_point_`/`axis_norm_`, so the extra lines are already in the assembler's search space. Measured over
all 163 released-axis pieces (288 edges, both ends released-axed), gate <= 25 deg, GT poses:

| pot | line 1 only | any line pair | gain |
|---|---|---|---|
| A | 12/15 | **15/15** | +3 |
| B | 13/15 | **15/15** | +2 |
| C | 2/5 | **5/5** | +3 |
| D | 49/69 | 60/69 | +11 |
| E | 52/62 | **62/62** | +10 |
| F | 9/9 | 9/9 | 0 |
| G | 10/10 | 10/10 | 0 |
| H | 6/17 | 14/17 | +8 |
| I | 59/65 | 59/65 | 0 |
| J | 7/21 | 13/21 | +6 |
| **ALL** | **219/288 (76.0 %)** | **262/288 (91.0 %)** | **+43** |

On the **26** GT-axed pieces that carry more than one released line, the best line beats line 1 by a
median **27.29 deg** (max 80.56), and the good line is **not** index 0 on **23 of 26**. An estimator writes
**one** line per piece, so it forfeits this space — which is why the estimators' regression is larger than
the raw per-piece angles suggest. This is used, not theoretical: in the real t67 Pot A run
(`runs/20261103-1429_3b3efbc_t67-juglet-assembly/out/APA/T67_candidates.tsv`) **44 of 124 candidates
carry `axis_x>0` or `axis_y>0`**, and the three Pot A true edges whose line-1 pair fails (1-7 60.2 deg,
4-7 58.4, 6-7 58.5) all pass only via a later line — which is **why Pot A seats 8/8**. Untested on other
pots.

### The pot-level self-consistency measure — a separate instrument, not the gate above

This is a **different** number from the edge gate and must not be read as one. It rotates each piece's
axis into a common frame by its GT pose and scores each line by its median folded angle to the other
pieces' line 1, keeping each piece's best line (`/c/PR/.scratch/diag65/gatefree2.py`). It is label-free
with respect to the GT **axes** but it **needs the GT poses**, so it is an **acceptance measure** (like
the chamfer bar), not a deployable runtime decision rule; the deployable per-pair version is the 25 deg
gate above. It detects bad files rather than echoing the answer: swapping in GT axes collapses Pot H
37.34 -> 0.04 and Pot J 33.74 -> 0.00.

| pot | n | released line 1 | released best line |
|---|---|---|---|
| A | 8 | 2.97 | 2.97 |
| B | 9 | 3.83 | 3.83 |
| C | 4 | 20.73 | 20.52 |
| D | 28 | 3.99 | 3.99 |
| E | 31 | 3.28 | 3.17 |
| F | 5 | 4.05 | 4.05 |
| G | 7 | 2.11 | 2.11 |
| H | 11 | 40.39 | 37.34 |
| I | 27 | 3.20 | 3.20 |
| J | 11 | 34.17 | 33.74 |

Eight pots sit at 2.1-20.5 deg; H and J are the two heavy-tail pots. Our nine-piece Juglet reads
**27.12 deg** with the shipped axes and **12.31 deg** with the ticket-68 hybrid — improved, and still
short of the 2-4 band the assembling pots occupy. (The Juglet is a separate object, not released Pot J;
see STATUS.md.)

**Part A conclusion.** The ticket-68 axis method **does not transfer to the corpus** — it is a regression
there. It would drop Pot A from 12/15 to 1-6 of 15 on the seating gate and the corpus from 217/286 to
36-109/286, no label-free rule rescues it, and an estimator's single line forfeits the multi-line search
space the released files already provide. Recommendation: **land it as a Juglet-lane opt-in only, never
applied to the released corpus** — behind the off-by-default switch (Part D), documented as never
auto-selected.
### Table 2 — 2x density against the authors' own breaklines (Part B)

One mesh stage per piece feeding two edge stages, so the two arms differ **only** in the lane
densification (`SFS_SPHERE_RADIUS_MM` 1.8 -> 0.9 and `SFS_RESAMPLE_D_MM` 1.9 -> 0.95). Run
`runs/20261103-0734_601013e_t69-density-panel`, job 34274535. Pieces that ran: **Pot A 01-08 (8/8),
Pot C 01-04 (4/4), Pot D 01-10 (10/10), Pot J 01-11 (11/11)** — 33 pieces, 66 lanes, both arms.

**The two arms share one mesh stage, and that is what makes the delta clean.** Verified: `geom18` and
`geom09` carry byte-identical S0/S1 on all 8 Pot A pieces (e.g. 01 S0 `1b27121a` both, 01 S1
`e0327ff7` both, 08 S0 `ece20c07` both), so only the edge stage differs between the arms. Those same
surfaces are **not** the t66 surfaces (01 S0 `1b27121a` against t66's `c2bbf6d1`) — the mesh stage draws
from an unseeded generator (`mesh_processing_headless.cpp:1526-1527`). **No panel lane is compared
against an older run's lane anywhere in this ticket**; such a comparison would be confounded by the draw.

Scored with `.scratch/pota-repro/292/score292.py` (selftest passes). Bar = median <= 2.0 mm **and**
coverage >= 90 %. The lead independently reproduced this table with a separate scorer and got the same
62/62 and the same medians.

| pot | lanes measured | at bar (both arms) | med 1.8 mm | med 0.9 mm | cov 1.8 / 0.9 | dots 1.8 -> 0.9 |
|---|---|---|---|---|---|---|
| Pot_A | 16 | 16 | 0.625 | 0.601 | 100 / 100 | 2185 -> 4464 |
| Pot_C | 6 | 6 | 0.583 | 0.565 | 100 / 99.9 | 1201 -> 2454 |
| Pot_D | 20 | 20 | 0.564 | 0.552 | 100 / 100 | 4976 -> 10103 |
| Pot_J | 20 | 20 | 0.584 | 0.572 | 100 / 100 | 2544 -> 5216 |
| **ALL** | **62** | **62** | **0.581** | **0.565** | **100 / 100** | **10906 -> 22237 (2.04x)** |

Excluded lanes, listed rather than silently dropped: **4** — `Pot_C_Piece_01` lane 0 (corpus gap: the
interior Bl0 measures the input, not the method), `Pot_C_Piece_03` lane 1 (the authors' Bl1 is the rim of
their own small face, not a break edge), `Pot_J_Piece_09` lanes 0 and 1 (their lines on this piece are
wrong, ticket 289).

**The per-lane delta direction, which is the actual question:**

| direction | lanes |
|---|---|
| **CROSSED_OUT** (at bar at 1.8 mm, below bar at 0.9 mm) | **0** |
| **CROSSED_IN** (below bar, rescued by density) | **0** |
| both at bar | **62** |
| both out | 0 |

No lane crosses the bar in either direction. **The per-lane median distance moves both ways — 30 of 62
lanes are farther at 0.9 mm and 32 are closer**, median of the per-lane deltas -0.013 mm, largest
increase **+0.283 mm** (`Pot_A_Piece_07` lane 0), largest decrease **-0.242 mm** (`Pot_J_Piece_03` lane 1).
Those are the numbers a reader needs to check the "re-draw noise" reading: the shift is symmetric and
small against a 2.0 mm bar and against a 0.58 mm baseline, and no lane's coverage falls below 90 %.

Independent check by a different instrument (lead, `/c/PR/.scratch/diag65/`): against the t59 stage-0
face labels, doubling takes the nine Juglet lanes from 370 dots at median 0.270 mm / 90.8 % within 1 mm
to 780 dots at 0.240 mm / 90.6 % — twice the dots, equally well placed.

**One lane failed to produce a 0.9 mm line, and it is a pre-existing hazard, not a switch effect.**
`Pot_C_Piece_03`'s 0.9 mm edge stage **segfaulted** (rc=139) on Surface_1 at segment 19 of 25 while
reading a 3-point segment (`Segments/3.xyz`, `rows=3 cols=6`), after two segments printed
`C1 -nan C2 -nan`. `isBreaklineSegARim` (`edgeline_extraction_headless.cpp:2977`) clips with
`for (size_t i = 3; i < cloud_BreakLineSeg->points.size() - 3; i++)` at `:3003`; with fewer than six
points the unsigned subtraction underflows and the loop runs off the end. The 1.8 mm arm split the same
surface into segments that never got that short, so the crash is surfaced by the different segment split,
not caused by a switch. **Not fixed here** — it is a real latent defect the density change makes easier
to hit, and it belongs in its own ticket.

### Table 3 — the seating control (Part C): Pot A at 0.9 mm lanes

Part C is **density only**. The ticket-68 axis method ships no Pot A axes (`axes68/` holds only the nine
Juglet pieces), so "both changes on" is not definable for Pot A; the question reduces to whether Pot A
still seats when its lanes are densified. Both arms use the **corpus** axes
(`$CORP/Axes/Pot_A_Piece_NN_Axis.xyz`, md5 `74086636...` for piece 01) — the same files the t67 PACTL and
t68 GPA50 controls read — at the **shipped floor 50**, same harness, same patch, same surfaces.

Run `runs/20261103-0811_08d08b0_t69-pota-axes`, job 34275406, COMPLETED 0:0 in 12 m 55 s:

| arm | lanes | sherds seated | joins seated | Acc.txt |
|---|---|---|---|---|
| POTA18C (shipped 1.8 mm) | corpus | **8 / 8 (100 %)** | **15 / 15 (100 %)** | `out/POTA18C/1. Acc.txt` |
| POTA09C (densified 0.9 mm) | corpus, 2.04x dots | **8 / 8 (100 %)** | **15 / 15 (100 %)** | `out/POTA09C/1. Acc.txt` |

Both arms placed 8 pieces and wrote 8 assembled edgelines; both exited 0. Cross-check against the
pre-existing controls: t67 `out/PACTL` = 8/8 + 15/15 (Time 433813 Sec), t68 `guard68/out/GPA50` = 8/8 +
15/15 (Time 196962 Sec) — the corrected control arm reproduces them, so the harness is sound.
**This is the merge gate for density and it passes.**

**A superseded attempt is recorded so it is not mistaken for evidence.** Job 34275210
(`runs/20261103-0754_b23aedf_t69-pota-seat`) returned **7/8 and 12/15 in BOTH arms**, byte-identical
gates. The control failed too, which is the tell: it staged `Dataset/Axes/Pot_A` instead of the corpus
axes, and those files differ by up to 24.7 deg (`Pot_A_Piece_06`) and 15.6 deg (`Pot_A_Piece_08`) on
line 1. That run is **not** evidence about density and its numbers are not used anywhere above.

**A Juglet question rides along and is answered (lead input 5).** Arm JUG09F50 in that same job — the nine
Juglet lanes at 0.9 mm with the **shipped** floor 50 and the shipped old axes, i.e. density alone with no
floor change — gives **0 / 8 sherds and 0 / 13 joins** (`out/JUG09F50/1. Acc.txt`, Time 126899 Sec).
2x density takes the Juglet from **2 of 9 pieces entering to 8 of 9** at the shipped floor and still seats
nothing. Density is not a way of dodging the floor rule.
### Table 4 — the Part D switches, and the gate that actually holds

Both switches are env vars with the shipped literal kept as the default, parsed at the existing env
block, valid range (0.4, 5.0), printing a line only when set:

- `SFS_SPHERE_RADIUS_MM` — `edgeline_extraction_headless.cpp:485` keeps
  `double sphereRadius = 1.8;`, `:486-489` parses the env var and prints `[SPHERE-69] sphereRadius=...`.
- `SFS_RESAMPLE_D_MM` — `:574` keeps `float RESAMPLE_D_MM = 1.9f; // paper constant`, `:575-578` parses
  and prints `[RESAMPLE-69] RESAMPLE_D_MM=...`.
- `sfs_axes/hybrid.py` — the ticket-68 hybrid estimator as a tracked module + CLI, **DEFAULT OFF**
  (`hybrid.py:1`), whose docstring states it must never be a corpus-wide default and must never overwrite
  a released axis in place.

**An md5 comparison of these .pcd files is NOT a valid test, and the reason is measured, not assumed.**
The writer is not bit-stable: two runs of the *same* arm produce different md5s, and the seventh
(curvature) column is uninitialised memory — t68 measured 1.1e+23 against 1.5e-37 on byte-identical
geometry. The gate applied here is **(a) identical dot counts, (b) identical position columns to
0.000 mm, (c) identical header POINTS field**, with the normal-column delta reported as a measured number.

Four edge-stage runs on **one** identical staged tree (unset x2, explicit 1.8/1.9 x2), run
`runs/20261103-0811_08d08b0_t69-pota-axes/proofgeom/`, measured by `geomid69.py`:

| pair | lane | dots a / b | max position delta | normal med / max deg | POINTS hdr | same counts / positions |
|---|---|---|---|---|---|---|
| unset_a : unset_b (same arm) | Bl0 | 203 / 203 | 0.000000 mm | 0.165 / 0.895 | 203 / 203 | yes / yes |
| unset_a : unset_b (same arm) | Bl1 | 210 / 210 | 0.000000 mm | 0.106 / 0.443 | 210 / 210 | yes / yes |
| explicit_a : explicit_b (same arm) | Bl0 | 203 / 203 | 0.000000 mm | 0.142 / 0.533 | 203 / 203 | yes / yes |
| explicit_a : explicit_b (same arm) | Bl1 | 210 / 210 | 0.000000 mm | 0.188 / 0.654 | 210 / 210 | yes / yes |
| **unset_a : explicit_a (the switch)** | Bl0 | 203 / 203 | **0.000000 mm** | 0.166 / 0.639 | 203 / 203 | yes / yes |
| **unset_a : explicit_a (the switch)** | Bl1 | 210 / 210 | **0.000000 mm** | 0.148 / 0.534 | 210 / 210 | yes / yes |
| **unset_b : explicit_b (the switch)** | Bl0 | 203 / 203 | **0.000000 mm** | 0.172 / 0.829 | 203 / 203 | yes / yes |
| **unset_b : explicit_b (the switch)** | Bl1 | 210 / 210 | **0.000000 mm** | 0.145 / 0.547 | 210 / 210 | yes / yes |

The position md5 is identical in all eight pairs (Bl0 `db71e9f1eb2717a7aeae24929b6360b0`, Bl1
`711c502e3c1627603bbb83023f29e96e`). **The same-arm normal jitter (0.11-0.19 deg median) is the same size
as the cross-arm one (0.15-0.17)** — so unset and explicit-defaults are the same geometry, and the
residual jitter is pre-existing writer non-determinism, not a switch effect. The lead re-ran the same
gate independently on these arms and read the same position result (normal median 0.136-0.247 deg,
max 0.898). Switch prints verified: the explicit arm prints both lines, the unset arm prints neither
(grep count 0).

An unset run therefore reproduces the shipped output; the switch changes geometry only when set to a
different value, which the 2.04x dot count in Table 2 demonstrates at 0.9 mm.

### Renders

`render69.py` (new; no assembly-level renderer existed — `t66_render.py` draws one piece over its own
mesh) draws each Result directory in the assembled frame, plan and elevation, equal aspect, 5 mm grid.
Copies under `.scratch/juglet-breaklines/stage69/renders/`; full-size PNGs on Spartan at
`/data/gpfs/projects/punim2657/SfSpp/scratch69/renders/`:

- `POTA18C.png` — Pot A shipped lanes, 8/8 + 15/15, assembled bbox 187.2 x 192.8 x 457.4 mm
- `POTA09C.png` — Pot A densified lanes, 8/8 + 15/15, assembled bbox 187.0 x 191.0 x 476.0 mm
- `PACTL_control.png` — the pre-existing t67 control, same reading

The two Pot A arms draw the same compact body at the same scale, which is what 8/8 + 15/15 looks like; a
failed arm on this object reads as a scattered cluster or a displaced pot. **Caveat: the worker's model
cannot display images**, so the renders were verified by piece count, edge count and bounding box, not
by eye. Someone who can see them should confirm before the merge.

### Jobs (sacct, polled directly)

| job | name | State | ExitCode | Elapsed | what |
|---|---|---|---|---|---|
| 34273111 | t69-partA | COMPLETED | 0:0 | 00:00:42 | Part A pass 1 |
| 34273167 | t69-partA2 | COMPLETED | 0:0 | 00:00:53 | Part A pass 2 (+npar) |
| 34273237 | t69-partA3 | COMPLETED | 0:0 | 00:00:52 | Part A pass 3 (dirs.tsv writer bug, fixed) |
| 34273319 | t69-partA4 | COMPLETED | 0:0 | 00:00:46 | Part A final pass + edge gates |
| 34274349 | t69B-prep | **FAILED** | 6:0 | 00:02:24 | job 5 attempt 1 — proof stage ran from the run dir, no evidence |
| 34274535 | t69B-prep | **FAILED** | 1:0 | 00:42:19 | Part B density panel; `rc_any=1` from the Pot C 03 segfault — all four cells' data landed |
| 34275210 | t69C-pota-seat | COMPLETED | 0:0 | 00:15:07 | Part C attempt 1 — **superseded**, wrong axis dir |
| 34275406 | t69D-pota-axes | COMPLETED | 0:0 | 00:12:55 | Part C corrected + the four-run Part D proof |
| 34275026 | t69D-det6 | COMPLETED | 0:0 | 00:02:10 | the lead's own determinism probe, read-only, re-measured by `geomid69.py` |

The two FAILED rows are both recorded rather than hidden: 34274349 wrote no evidence and was replaced;
34274535 failed only because a per-piece segfault set the job's aggregate return code, and every lane it
produced was used. Run-dir naming wart: `runs/20261103-1733_45ba206_t69-axis-corpus/` is named for commit
45ba206 but its later passes ran 1e8d07d / 0d31740 from `work/` (md5s in `logs/provenance.log`).
### Merge recommendation

**Merge the 2x lane density. Do NOT merge the axis method as a corpus default.**

**1. The axis method is a REGRESSION on the released corpus, not a no-benefit result.** Replacing the
released axis with **any** ticket-68 estimator drops Pot A from **12/15 to 1-6 of 15** on the assembler's
own 25 deg axis gate and the corpus from **217/286 to 36-109/286** (Table 1). Pot A is the seating
control: it passes only 12 of 15 today and still seats 8/8, so a few bad axes are survivable — most of
them being bad is not. The line-1 baseline also **understates** the released files: 26 of the 141
GT-axed pieces carry more than one axis line, the best line beats line 1 by a median **27.29 deg** there
(max 80.56), any-line-pair scores **262/288 against line 1's 219/288**, and the assembler demonstrably
uses the later lines — **44 of 124** Pot A candidates carry `axis_x>0` or `axis_y>0`, and the three Pot A
true edges that fail on line 1 (1-7 60.2 deg, 4-7 58.4, 6-7 58.5) pass **only** via later lines, which is
why Pot A seats 8/8. **An estimator writes ONE line per piece and forfeits that search space.** So: land
the axis method **only as a Juglet-lane opt-in that is never applied to the released corpus**, behind
`sfs_axes/hybrid.py` default-off. Its Juglet result (27.12 -> 12.31 deg self-consistency) is real and
worth keeping for that lane.

**2. The density switch passes its gate and should merge.** Pot A holds **8/8 and 15/15** at 0.9 mm lanes
(Table 3) — the gate that outranks everything else in this ticket. Across **62 corpus lanes on four pots,
62 at bar in both arms, 0 crossed out, 0 crossed in** (Table 2), with 2.04x the dots at the same accuracy,
and the switches proved inert when unset (Table 4). Both switches stay **default off**
(`SFS_SPHERE_RADIUS_MM`, `SFS_RESAMPLE_D_MM`).

### Lead verification (2026-11-03, before merge)

The lead independently verified every part of this ticket before merging.

**Source diff** — read line by line. The non-scratch diff is exactly `edgeline_extraction_headless.cpp`
(25 lines: two env blocks, defaults untouched, ranges (0.4, 5.0), startup prints [SPHERE-69] / [RESAMPLE-69])
plus `sfs_axes/hybrid.py` (201 lines, docstring says DEFAULT OFF, do not enable on the corpus). Everything
else in the branch is stage69 scratch, STATUS, and this ticket.

**Part A reproduced** from the committed `stage69/outA/*.tsv` tables; the corpus regression numbers
(217/286 released vs 36-109/286 estimator on the 25-deg gate; any-line 262/288) were re-read at source
and the multi-line mechanism checked in code (`data_structure.cpp:142-176` pushes every axis line;
44/124 Pot A candidates carry a later line's axis).

**Part B reproduced** with the lead's own scorer (`/c/PR/.scratch/diag65/partB.py`): 62/62 lanes at bar
in both arms, median-of-lane-medians 0.580 -> 0.565 mm, 30/62 farther. Same numbers as the worker.

**Part D restated** via `/c/PR/.scratch/diag65/gateD.py`: positions identical to 0.000000 mm in every
pair including unset-vs-explicit; POINTS identical; normal jitter same-arm == cross-arm. The switches are
inert when unset; md5 is not a valid test (pre-existing writer non-determinism, the ticket-66
uninitialised-curvature class).

**Renders checked by eye** (the worker's open caveat). Both POTA09C and the t67 control render show a
point cloud floating ~300 mm above the assembled edges — but the SPLIT IS IN THE CONTROL TOO, and it is
proved numeric: piece OBJ z 287.5..446.4 vs edgeline z -29.7..2.2, best pure-z alignment still leaves
median 51.97 mm. `Top_1_Edgeline_*.xyz` is written in a different frame from `Top_1_OBJ_*.obj` — a
pre-existing assembler defect (also present in t67's PACTL), NOT a density effect, and it does not touch
seating counts. Honest pieces-only render saved:
`SfSpp_preprocessing/artifacts/69/pota09c_pieces.png` (bbox 143.7 x 166.2 x 158.9 mm). **Piece contact
measured directly, both arms identical**: closest pair gaps 0.06-0.10 mm on six joins, 7 of 28 pairs
within 2 mm, bboxes equal to 0.1 mm — the densified arm seats pieces in exactly the control's
arrangement. Pose files identical between arms; OBJ md5 differs only via filename timestamps.

verified: gateD.py positions 0.000000mm all pairs -> switches inert; partB.py 62/62 both arms;
pieces_only.py gaps 2-3:0.06 3-6:0.06 1-2:0.07 1-4:0.08 2-4:0.08 3-4:0.10 -> seating identical.

**Lead merge decision (conservator order m06808, verify-then-merge):** MERGE the branch. The density
switches pass the gate and are default-off; the axis method is already default-off and marked
Juglet-lane-only, so merging the branch lands exactly the worker's recommendation — density available,
axis method available but never applied to the corpus. The open questions (MINIMUM_NUMBER 12 control,
Pot C 03 underflow segfault, Result-frame mismatch) are ticket material, not merge blockers.

### Risks that travel with this recommendation

- **Density is not a free resampling — it halves the implied match length.** The LCS that decides whether
  two breaklines match needs a run of more than `windowsize` consecutive points
  (`feature_matching.cpp:294`), and `windowsize` is `MINIMUM_NUMBER = 6` (`reconstruction.h:24`, used at
  `ranking_system.cpp:797-801`, `:835-839`, `main.cpp:211`) — a **point** count. At 1.8 mm six dots span
  10.8 mm; at 0.9 mm they span 5.4 mm. Densifying **halves the physical match length**, a real semantic
  change to the matching rule, and it is very likely part of why the t68 D2X arm formed 293 candidates
  against 35. Quantisation is spacing-independent (`Q_size = 0.15/0.15/0.15/0.2`,
  `feature_matching.cpp:1517-1521`), so density moves exactly one of the three matching scales. A post-hoc
  filter to LCS size > 12 on the two t68 candidate tables (an **estimate**, not a run) leaves A20 with 0
  candidates — raising the window at 1.8 mm destroys Pot A — and D2X with 38, 15 on true joins against
  A20's 23/12. The clean control is 2x density with `MINIMUM_NUMBER` at its physical equivalent (12, not
  6); it was **not run** and remains an **open question**.
- **The 50-dot floor is a length threshold in disguise, and that is the honest limit of the density fix.**
  At 1.8 mm the floor is an **88.2 mm** length threshold; **30 of 326** released breaklines are shorter
  than that, and the shortest released line is **48.5 mm**. Our Juglet P9 loop is **40.4 mm** — shorter
  than anything in the corpus. At 0.9 mm **eight of nine** Juglet pieces clear the floor and P9 lands on
  **49 dots, one short**. So density fixes the Juglet's *entry* at the shipped floor (2 of 9 -> 8 of 9) and
  does **not** make the Juglet assemble: arm JUG09F50 seats **0/8 and 0/13**. Merging density does not by
  itself make the Juglet seat, and the floor was not what blocked it once density was on.
- **Part C is Pot A only.** One pot, 8 pieces, 15 joins. Pot A saturates and is the control; it is not a
  corpus result. No other pot's seating was re-run under density.
- **Pot C 03's 0.9 mm segfault** (Table 2) is a latent defect density makes easier to hit, unfixed here.
- **The Part A conclusion is about the corpus, not about the Juglet.** The Juglet lane's improvement
  (ticket 68) stands; it simply does not generalise, and the corpus has no multi-line rescue available to
  an estimator.
- **The renders were not checked by eye** (the worker's model cannot display images); piece counts,
  edge counts and bounding boxes were verified instead.