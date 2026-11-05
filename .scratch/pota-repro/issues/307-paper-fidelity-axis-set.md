# 307: Match the paper's axis method clause by clause — and emit the candidate set the paper describes

**What to deliver:** a clause-by-clause fidelity audit of `sfs_axes` against paper **§IV-B2** and the
authors' MATLAB, with every remaining difference named at a `file:line` and either **fixed** or
**justified in writing**; the paper's own candidate set actually emitted and measured; and Pot A
seating **8/8 sherds + 15/15 joins with our axes only at 2 of 3 seeds, no best-of-N**. The target is
the paper's method. The released axis files are a scoring reference, never a thing to fit to.

**Answers:** E1

**Blocked by:** none. 302 (per-point cost), 304 (under-5,000 rule, default ON), 305 (sweep), 306 (no
equal-count cut; paper chain default) are all on main.

**Status:** ready-for-agent
**Worker:** unassigned

**Budget:** large 12

**Hand-over:** Claude — Spartan compute, the assembler SIF and the corpus lanes; MATLAB on a compute
node for the parity and `.m`-reading stages.

## Why this ticket exists (measured; do not re-derive)

- **The assembler is not the suspect.** Same binary, same breaklines, only the axis files swapped:
  **MO (authors' axes) 8/8 + 15/15**, **MM (ours) 6/8 + 10/15** — run `20261105-0617_c333dc7_t306-c1c-moom`,
  2/2 repeats each. So the difference lives in our axis set, and the way to close it is to match the
  method that produced theirs. Do not spend time on `sfs_main` in this ticket.
- **Best our axes have ever reached: 7/8 + 12/15** (paper chain, equal-count cut off, seed 1, 3/3
  repeats). Nothing so far has produced 8/8 with our axes.
- **Our chain writes 1-3 axis lines per piece; the released files hold 1-6.** Ticket 305's census,
  which this ticket re-counts: ours fewer lines than the reference on 20 of 163 pieces, more on 19,
  the same on 124.
- **The reason we write 1-3 is one line of our code:** `sfs_axes/potsac.py:145`, `keep = cost <
  cost[0] * 1.1`, applied twice (`:239` after stage-1 refine, `:247` after stage-2). The port's own
  docstring says it is a MATLAB quirk kept deliberately ("first survivor, not the minimum — MATLAB
  quirk, kept"). **The paper's description of the same step contains no such prune.** Paper and code
  therefore disagree, and which one we follow is a decision this ticket has to make with a measurement,
  not a preference.
- **Ticket 306's union is not a test of the paper's set.** It unioned 10 seeds and ranked survivors by
  the worst wall's cost per point. The paper's own output — the **top 10** survivors ranked by the
  robustified residual cost, duplicates at 10 deg removed keeping the cheaper — has **never been
  emitted** by this code. That is the largest single untested divergence from the paper, and it is the
  first thing to test.
- **Two smaller divergences are already known and never settled:** the paper says *MLESAC-based*
  sampling while our search is 1,000 fixed uniform 6-point draws ranked MSAC-style; and the paper says
  *trust-region* optimisation while `refine.py` is a literal Levenberg-Marquardt port of the authors'
  `optimize_using_lm.m`. In both cases the authors' code is the operative reading — settle each by
  reading the `.m`, not by trusting either wording.

## The clauses to audit (quoted; `papers/text/sfspp-2502.13986v1.md`)

1. **:171-173** "MLESAC-based sampling with a minimal 6-point solver that enforces Pottmann's
   constraint — ensuring the offset vector, symmetry axis direction, and the cross product of the
   surface normal lie on the same plane".
2. **:173-175** "an extended Cao and Mumford error, applicable to both interior and exterior
   surfaces ... in the subsequent trust-region-based nonlinear optimization".
3. **:175** "selects the top 10 candidate axes. Then, the angles between each pair of axes are
   evaluated, and those with an angle of 10 degrees or less are considered duplicates, with the axis
   having the higher cost, defined as the robustified residual error, being removed through pruning."
4. **:175** "we initially sample only 10% of the surface points to generate axis candidates, and after
   pruning, all surface points are used for more detailed refinement".
5. **:155** "B-Spline fitting is performed for each cluster to refine surface boundaries and uniformly
   sample the point cloud" — surface generation, not the axis method; do not implement an axis from it.

## Stage A — the audit (no E2E; a laptop and one login-node read)

Build the table the rest of the ticket hangs off. One row per clause and per `.m` file, columns:
**the paper says** (quote + line) / **the `.m` does** (`file:line`, quoted) / **we do** (`file:line`) /
**can this change the emitted set?** / **verdict** (`MATCH`, `DIFFERS-DOCUMENTED`,
`DIFFERS-UNDOCUMENTED`). Files to read in `AxisExtraction/` and wherever they live:
`compute_axis_of_symmetry.m`, `compute_pottmann_axis.m`, `compute_biaxial_cao_error.m`, `run_potsac.m`,
`refine_axis.m`, `optimize_using_lm.m`, `robustifier_gm.m`, `robustifier_huber.m`,
`apply_robustifier.m`, `read_surfaces.m`, `extract_axis.m`.

Three specific questions Stage A must answer with a quote, not an inference:

- **A-Q1 (the big one):** does `run_potsac.m` really contain the `cost < cost[0]*1.1` prune, and does
  the paper's "top 10 survive" describe the same quantity? If the `.m` has it, the authors' own
  released files were made by a chain that can only emit 1-3 lines — so the paper's method and the
  authors' output disagree, and we must say which we follow and why.
- **A-Q2:** is the sampling in `compute_axis_of_symmetry.m` adaptive (MLESAC-style stopping or
  likelihood weighting) or 1,000 fixed uniform draws? Quote the loop and the stop condition.
- **A-Q3:** does `compute_pottmann_axis.m` return one axis per 6-point sample or several valid ones?
  Our `sfs_axes/pottmann.py:26-32` returns the single smallest singular vector of the reduced matrix.
  If the `.m` can return more, our pool is a fraction of theirs — say so with the line.

Also in Stage A, the **output-shape census** (`A2`): for all 163 corpus pieces, lines written by our
chain vs lines in the released file, per pot, with the pieces where we differ named. This is the
cheapest fidelity measurement available and it is free of any E2E.

## Stage B — arms, one variable each, Pot A first

Every arm is measured the same way: Pot A at seeds 0/1/2, report `Sherd accuracy` and the join count
read from `out/<arm>/1. Acc.txt` plus a per-join recompute, **no best-of-N** on the assembler. Any arm
that changes the axis set must also produce the corpus census line (163 pieces, md5 of the released
inputs unchanged) and a Juglet arm for collateral damage.

- **B1 — the paper's candidate set, emitted.** Top 10 survivors ranked by the paper's cost, 10 deg
  dedup keeping the cheaper, **no `cost[0]*1.1` prune**. This is the hypothesis the ticket exists to
  test. Report K per piece and whether Pot A moves.
- **B2 — MLESAC sampling** if A-Q2 finds the `.m` adapts (iterations from the inlier ratio, or
  likelihood weights); otherwise record `MATCH` and skip.
- **B3 — Pottmann completeness** if A-Q3 finds more than one axis per sample: return all of them.
- **B4 — the ranking statistic.** The paper defines the cost as "the robustified residual error"; make
  sure the stage-2 order uses exactly that quantity on all points, and that the order is the paper's
  (cheapest first). Report the row that settled it.
- **B5 — the 10% sample.** Stage A decides whether `run_potsac.m` strides or draws at random; match
  the `.m` and report what the difference does on Pot A Piece 07 and Piece 08 specifically (they are
  the two pieces the last four tickets kept returning to).
- **B6 — any other `DIFFERS-UNDOCUMENTED` row Stage A produces.** One arm each; if a row needs no
  code change, close it in the table instead of an arm.

## Stage C — land the paper-faithful chain

- **C1 — the verdict.** Either Pot A seats **8/8 + 15/15 with our axes only at 2 of 3 seeds, no
  best-of-N**, or the ticket states plainly what still blocks it — which piece, which join, and at
  what angle/offset — with the arm that came closest. A negative verdict is a result; do not tune to
  reach the bar.
- **C2 — parity.** Anything touched must still pass ticket 302's MATLAB unit parity (bar `1e-9`) and
  `python -m pytest tests/ -q`.
- **C3 — the corpus.** 163 pieces to new paths, released md5 unchanged, tier table against 306's
  baseline (**84/163 within 5 deg, median best 4.63 deg**) with the direction, and the `rad_mm` column
  reported separately (anchor reflection is a known, fixed defect — do not compare old rad numbers).
- **C4 — Juglet.** One arm, F20 floor, our axes vs the Dataset axes, counts unchanged in kind
  (currently 0/9 seated for every axis set tried).
- **C5 — renders** of any geometry claim into `artifacts/pota307/`, and the defaults documented in the
  ticket and in `intent/E1`.

## What is admissible (read this before choosing a fix)

**A change is admissible only if a paper clause or a line of the authors' `.m` prescribes it.** If a
change seats Pot A but has no paper or code warrant, it is a finding to report, not a default to ship.
The same rule runs the other way: a paper-faithful change that does **not** seat Pot A is still the
correct code, and the ticket must say so and leave it on.

Never fit to the released axis files. Never use them, or the ground-truth poses, inside a selection
rule; they are for scoring only.

## Acceptance

- [ ] **A1** clause table delivered: every row with the paper quote, the `.m` `file:line`, our
      `file:line`, "can it change the emitted set", and a verdict.
- [ ] **A2** the line-count census (ours vs released, 163 pieces, per pot) with the differing pieces
      named.
- [ ] **A3** A-Q1/A-Q2/A-Q3 answered with quotes, and the paper-vs-`run_potsac.m` conflict on the 1.1
      prune decided in writing with the measurement behind the decision.
- [ ] **A4** every `DIFFERS-UNDOCUMENTED` row is either closed as `MATCH` or assigned to a B arm.
- [ ] **B1** the paper's top-10 set emitted and measured on Pot A, 3 seeds, with K per piece.
- [ ] **B2-B6** each arm run or closed with the reason (one variable, one table).
- [ ] **C1** Pot A verdict: 8/8 + 15/15 with our axes at 2/3 seeds, or the named blocker.
- [ ] **C2** 302 parity (bar `1e-9`) and `pytest` pass for everything touched.
- [ ] **C3** corpus 163 with the released md5 unchanged and the tier table against 306's baseline.
- [ ] **C4** Juglet arm reported.
- [ ] **C5** renders in `artifacts/pota307/` and the defaults documented.

## Rules of the road

- `ssh` must be `/c/Windows/System32/OpenSSH/ssh.exe spartan`; git-bash `ssh` cannot authenticate.
  Single-quote the whole remote command or `$` expands locally.
- Runs go under `/data/gpfs/projects/punim2657/SfSpp/runs/<YYYYMMDD-HHMM>_<git7>_<tag>/` with
  `run.json`, `logs/`, `out/`, and one `index.tsv` row (verdict/human_note empty). Poll every job with
  `sacct -j <id> --format=State,ExitCode` and record State/ExitCode in the ticket.
- Build on the ticket-306 stage scripts in `.scratch/pota-repro/306-stage/` (they already stage the
  Pot A trees, substitute only `Axes/`, and enforce axes-only diffs with `diff -rq`).
- The corpus is read-only: no file under `Dataset/` or the sample trees may change; prove it with an
  md5 diff before and after.
- Heavy work on compute nodes, never the laptop or the login node.
- Edit the ticket's Comments only; commit and push nothing. Hand back: the tables, the run ids, the
  sacct lines, and the diff of anything you would ship.
