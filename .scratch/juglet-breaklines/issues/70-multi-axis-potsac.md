# 70 — Make the axis step produce the same multi-line axes as the released sample, then test on the Juglet

**What to build:** the released corpus axis files carry up to six lines per piece because the authors'
modified PotSAC (paper SSIV-B2, `papers/text/sfspp-2502.13986v1.md:173-175`: top-10 MLESAC candidates,
<=10-deg duplicate pruning, 10% candidacy sampling, full-cloud refinement of survivors) keeps multiple
axes. Our `sfs_axes/potsac.py` port already implements that pipeline and `io_axes.py:write_axes` writes
all K lines — but every comparison since ticket 05 has scored and adopted SINGLE-line axes (the t68
hybrid estimators, and t69 Part A's potsac_s0 scored as one line). This ticket closes the gap:

1. **Fidelity audit (local, no cluster):** read `original_nurbs_preprocessing/AxisExtraction/run_potsac.m`
   and `extract_axis.m` against `sfs_axes/potsac.py` + `sfs_axes/cli.py` and list every behavioural
   difference in the MULTI-candidate path (candidate count, refinement stages and which cloud each stage
   uses, cost definition at each stage, both dedup passes, final ordering, how many lines extract_axis.m
   wrote). Nothing is changed in this stage unless a difference is a proven bug.
2. **Corpus match (the acceptance):** run the port's multi-line output on every corpus piece that has
   staged Surface_0/1 clouds (the t69 Part A staging under
   `/data/gpfs/projects/punim2657/SfSpp/scratch69/` and the released axes under the corpus Axes dir),
   compare against the RELEASED multi-line files piece by piece: does our K match theirs, and does each
   released line have a counterpart among ours within 5 deg direction / 2 mm position (the standing
   gate)? Report per-pot match rates for line 1 and for any-line. This is "generate same axes as sample".
3. **Juglet test:** run the port multi-line on the nine Juglet pieces, drop the multi-line files in as
   the axis input, run the assembler on the current Juglet lane (0.9 mm lanes, floor 30), and score
   candidates / axis-gate survival / seating against the t69 JUG09F50 arm and the t68 I20_D2X arm.

**Why now (2026-11-03, conservator m08189):** "let's check the axis step, how the paper claim it is
suppose to be done. what the current matlab step does, why it don't generate up to six axis guesses per
piece? match the gap, so axis step generate same axises as sample and then test on juglet."

**Answers:** U19, E1

**Blocked by:** none (t69 merged be5980c; sfs_axes port landed ticket 05)

**Status:** in-progress
**Working in:** chat on Thinkbook16 (2026-11-03)
**Branch:** 70-multi-axis-potsac from main
**Worker:** (assigned on dispatch)

## Spec

### Stage 1 — fidelity audit (laptop)

Side-by-side of run_potsac.m / extract_axis.m / compute_axis_of_symmetry.m against
sfs_axes/{potsac,refine,cao,pottmann,io_axes}.py. Output a table in the ticket: stage, MATLAB line,
port line, same-or-different. The known ports to respect: randsample without replacement, mean/scale
normalisation over 36 entries, degenerate 0/1 inlier count, dedup keeps cost < cost[0]*1.1 (first
survivor, MATLAB quirk). Flag anything else.

### Stage 2 — corpus match (Spartan)

Inputs: the t69 Part A staged surfaces and the released axes (paths in t69's
stage69/stage69_inputs.py). Run `python -m sfs_axes.cli` (or a thin wrapper) per piece with the
paper-letter settings (step=10, fixed seed set {0,1,2} to measure seed sensitivity), write multi-line
axis files, compare to released. Gate: on the baseline-good pots (A B D E G I, 110 pieces) the
any-line match rate must beat the released line-1 baseline's own 219/288 edge-gate behaviour — the
honest reading is "our multi-line file performs no worse than the released file on the same pieces".
Report K distributions ours vs released.

### Stage 3 — Juglet (Spartan)

Multi-line axes for the nine Juglet pieces; assembler runs on the Juglet lane (0.9 mm lanes, floor 30,
worness 0.7, radius normals 1.0). Compare against: t69 JUG09F50 (0/8, 0/13, old single-line axes) and
t68 I20_D2X (18/18 candidates, best median 53.8 deg). Score: candidates on GT joins, axis-gate
survival, measurable poses, seating, and the any-line self-consistency of the Juglet axis set.

### Gates

- Stage 2 before stage 3; no stage 3 if stage 2 shows the port cannot reproduce released lines on the
  good pots (report and stop instead).
- Every sbatch gets scripts/slurm_poll.sh; final sacct State/ExitCode recorded here.
- Nothing merged by the worker; the lead verifies and merges.

### Budget

- <= 6 Slurm jobs, <= 6 h wall total. Laptop work (audit) does not count.

## Acceptance

- [ ] Audit table in this file
- [ ] Corpus match table: per pot, K ours vs released, line-1 and any-line match rates
- [ ] Seed sensitivity note (3 seeds)
- [ ] Juglet assembler comparison table vs JUG09F50 and I20_D2X
- [ ] All runs in runs/ with index rows; verdict left to the lead
